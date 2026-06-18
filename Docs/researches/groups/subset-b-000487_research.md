# subset-b-000487 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RangeFileInStream.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RangeFileInStream.java

## Purpose
`RangeFileInStream` adapts an Alluxio `FileInStream` into a bounded Java `InputStream` for S3 byte-range reads. It is used when object GET and copy operations need to expose only a requested range from a larger Alluxio file.

## Important APIs and control flow
The public surface is `read()`, `read(byte[])`, `read(byte[], int, int)`, `read(ByteBuffer, int, int)`, `close()`, and `Factory.create(FileInStream, long, S3RangeSpec)`. Factory construction calls private `seek`, which uses `S3RangeSpec.getOffset(objectLength)` to position the underlying stream and `S3RangeSpec.getLength(objectLength)` to cap the number of bytes exposed. The byte-array reads stop at `mUnderlyingLength` and shrink the requested length when a caller asks beyond the allowed range.

## State and persistence behavior
The class stores only stream-local state: the wrapped `FileInStream`, the allowed range length, and bytes already returned. It does not persist metadata. Closing delegates to the Alluxio stream. The `ByteBuffer` overload delegates directly to the underlying stream and does not update `mReadBytes` or enforce the range cap, which is a notable behavioral difference from the normal `InputStream` methods.

## Dependencies and integration points
It depends on Alluxio client `FileInStream` and `S3RangeSpec`. `S3ObjectTask` and `S3RestServiceHandler` use it for GET range streaming and copy/copy-part operations. Correctness depends on `S3RangeSpec` resolving invalid or suffix ranges before `seek`.

## Risks and test signals
Tests should cover full-object reads, open-ended ranges, suffix ranges, out-of-object ranges, EOF behavior, and close propagation. The `read(ByteBuffer, int, int)` method is a risk because it bypasses the range accounting; callers using that overload could read outside the requested range. Another edge signal is `FileInStream.read(byte[], off, 0)`, because the wrapper only checks `mReadBytes` and delegates zero-length reads rather than returning `0` explicitly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RangeFileInStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RateLimitInputStream.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RateLimitInputStream.java

## Purpose
`RateLimitInputStream` wraps another `InputStream` and applies one or more Guava `RateLimiter` instances before each read. In the S3 proxy it throttles object download streams with both global and per-connection limits.

## Important APIs and control flow
The constructor accepts the source stream and varargs rate limiters. `read()` acquires one permit, then reads one byte. `read(byte[])` delegates to `read(byte[], int, int)`. The ranged array read acquires permits for `Math.min(b.length - off, len)` before calling the wrapped stream. `close()` closes the wrapped stream. `acquire(int)` skips null limiters, allowing optional global or local limiters.

## State and persistence behavior
State is limited to the wrapped stream and limiter references. There is no persistence or shared mutable state. The limiter instances themselves can be shared by servlet context or per request, so blocking behavior can reflect global S3 proxy pressure.

## Dependencies and integration points
It depends on `com.google.common.util.concurrent.RateLimiter`. `S3ObjectTask.GetObjectTask` and `S3RestServiceHandler.getObject` wrap response streams when `ProxyWebServer.GLOBAL_RATE_LIMITER_SERVLET_RESOURCE_KEY` or `PROXY_S3_SINGLE_CONNECTION_READ_RATE_LIMIT_MB` yields a limiter.

## Risks and test signals
The implementation acquires permits before knowing how many bytes the wrapped stream will actually return, so EOF and short reads can over-consume permits. `read(byte[], off, len)` does not validate offsets itself and uses requested length rather than actual read length. Tests should use fake limiters or timing-tolerant checks around single-byte reads, bulk reads, null limiters, close behavior, EOF, and short reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/RateLimitInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3AuditContext.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3AuditContext.java

## Purpose
`S3AuditContext` is the audit record object used by the S3 proxy. It implements Alluxio `AuditContext` and collects request outcome, identity, source IP, command, bucket, object, and elapsed time for asynchronous audit logging.

## Important APIs and control flow
The class exposes fluent setters for `ugi`, command, IP, creation time, bucket, object, allowed, and succeeded flags. It is normally created by `S3Handler.createAuditContext` or `S3RestServiceHandler.createAuditContext` in a try-with-resources block. `close()` computes elapsed nanoseconds from `System.nanoTime()` and appends the context to `AsyncUserAccessAuditLogWriter` when logging is enabled. `toString()` formats the record as tab-separated fields.

## State and persistence behavior
The context itself is per request. Persistence is delegated to `AsyncUserAccessAuditLogWriter.append(this)`, which consumes `toString()`. When no writer is provided, `close()` is a no-op, allowing callers to keep a uniform try-with-resources pattern even when audit logging is disabled.

## Dependencies and integration points
It depends on `alluxio.master.audit.AsyncUserAccessAuditLogWriter` and `AuditContext`. S3 bucket/object tasks mark denied or failed operations by mutating the context before throwing translated `S3Exception`s. User/group enrichment is performed outside this class before setters are called.

## Risks and test signals
If `setCreationTimeNs` is not called, execution time is computed from zero and becomes meaningless. Tests should verify disabled logging no-op behavior, writer append on close, formatting fields, fluent return values, and failed/denied mutation paths. Since `toString()` emits raw bucket/object/user strings, tests or review should consider escaping expectations for tabs or newlines in names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3AuditContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3AuthenticationFilter.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3AuthenticationFilter.java

## Purpose
`S3AuthenticationFilter` is a JAX-RS pre-matching request filter for the S3 service path. It converts AWS authorization information into the internal Alluxio user header consumed by the older Jersey S3 resource.

## Important APIs and control flow
The single `filter(ContainerRequestContext)` method exits unless the URI path starts with `S3RestServiceHandler.SERVICE_PREFIX`. For S3 requests, it reads the `Authorization` header, calls `S3RestUtils.getUser(authorization, requestContext)`, and replaces/sets `S3RestUtils.ALLUXIO_USER_HEADER` with the resolved user. Any exception aborts the request with `S3ErrorResponse.createErrorResponse(e, "Authorization")`.

## State and persistence behavior
The filter has no persistent state. It mutates only the in-flight JAX-RS request headers.

## Dependencies and integration points
It integrates JAX-RS `ContainerRequestFilter`, `@PreMatching`, and `@Provider` registration with S3 auth utilities. It is tied to the Jersey service prefix, while the newer servlet handler performs equivalent authentication inside `S3Handler.doAuthentication`.

## Risks and test signals
Prefix checking is simple string matching; paths such as `s3foo` would satisfy `startsWith("s3")` depending on how the URI path is represented. Tests should cover non-S3 bypass, valid Authorization translation, missing/malformed auth, abort response shape, and header replacement. Logging includes the original Authorization header at debug level, which is operationally sensitive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3AuthenticationFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BaseTask.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BaseTask.java

## Purpose
`S3BaseTask` is the abstract command object for the newer servlet-based S3 proxy path. It binds an `S3Handler` to a classified S3 operation and provides the common interface used by `S3RequestServlet`.

## Important APIs and control flow
Constructors store `mHandler` and `mOPType`. `getOPType()` exposes the operation enum. Subclasses implement `continueTask()` to return a JAX-RS `Response`. `handleTaskAsync()` is a no-op hook overridden by `CompleteMultipartUploadTask` for long-running multipart completion. `OpType` enumerates supported object and bucket APIs, and each value carries an `OpTag` of `LIGHT` or `HEAVY` for executor routing.

## State and persistence behavior
There is no persistence here. State is per request and consists of the handler and operation type. Persistence decisions happen in concrete tasks through Alluxio `FileSystem` calls and xattrs.

## Dependencies and integration points
`S3RequestServlet` calls `getS3Task().mOPType.getOpTag()` to pick the light or heavy executor and then invokes `continueTask()` or `handleTaskAsync()`. `S3ObjectTask.Factory` and `S3BucketTask.Factory` instantiate concrete subclasses mapped to `OpType`.

## Risks and test signals
The servlet directly accesses protected `mOPType`, so package-level coupling is intentional but brittle if visibility changes. Tests should validate verb/query/header routing creates the expected `OpType` and that heavy operations route to heavy executor pools. Multipart completion should verify the async hook is used instead of normal `continueTask()` processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BaseTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BucketTask.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BucketTask.java

## Purpose
`S3BucketTask` contains bucket-level task implementations for the servlet-based S3 API: list buckets, bucket tagging, multipart upload listing, object listing, create bucket, bulk delete, head bucket, delete bucket tags, and delete bucket.

## Important APIs and control flow
`Factory.create(S3Handler)` dispatches by HTTP verb and query parameters. GET with no bucket lists owned buckets; GET with `tagging`, `uploads`, or neither maps to bucket tags, multipart uploads, or objects. PUT maps to bucket tagging or creation. POST `delete` maps to bulk object deletion. HEAD checks bucket existence. DELETE maps to tag deletion or bucket deletion. The base `continueTask()` returns NOT_IMPLEMENTED for unsupported routes.

## State and persistence behavior
Bucket state is represented as Alluxio directories. Creation calls `createDirectory` and then sets the owner to the S3 user. Bucket tags are stored in xattrs under `S3Constants.TAGGING_XATTR_KEY`. Delete behavior honors `PROXY_S3_DELETE_TYPE` for Alluxio-only deletes. Bucket existence is cached in `S3Handler.BUCKET_PATH_CACHE`, populated on list/create/head checks and invalidated by delete.

## Dependencies and integration points
The tasks use `S3RestUtils` for path parsing, user-scoped filesystem creation, bucket validation, tag serialization, and exception translation. They use Alluxio `FileSystem`, `URIStatus`, gRPC option builders, Jackson XML request parsing, and result DTOs such as `ListAllMyBucketsResult`, `ListBucketResult`, `ListMultipartUploadsResult`, and `DeleteObjectsResult`.

## Risks and test signals
ListObjects only supports `/` delimiters and normalizes prefixes to the last delimiter boundary. `max-keys` parsing can throw unchecked `NumberFormatException` if invalid. Bulk delete sorts longest keys first and treats missing files and non-empty directories as success, matching S3 semantics but needing regression coverage. Bucket naming restriction paths should test adjacent dot/dash patterns, IP-address names, `xn--` prefixes, and `-s3alias` suffixes. Tagging tests should verify malformed XML, xattr replacement, and delete semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3BucketTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Constants.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Constants.java

## Purpose
`S3Constants` centralizes string constants, xattr keys, charset choices, date formatters, metadata directory names, and copy/tagging directives for the S3 proxy implementation.

## Important APIs and control flow
The class is non-instantiable and annotated thread-safe because it contains only constants. It defines HTTP headers such as `Content-Length`, `Content-Range`, `x-amz-copy-source`, `x-amz-tagging`, and signing query/header names. It defines Alluxio xattr keys for content type, ETag, tags, multipart bucket/object/file-id metadata, and metadata root/upload directories. The `Directive` enum captures `COPY` and `REPLACE` behavior for metadata and tagging during copy operations.

## State and persistence behavior
The constants drive persisted xattr names and hidden Alluxio metadata paths, especially `.alluxio_s3_api_metadata/uploads`. Changing these values would affect compatibility with existing stored objects and multipart upload metadata.

## Dependencies and integration points
The class is used throughout `S3ObjectTask`, `S3BucketTask`, `S3RestServiceHandler`, `S3RestUtils`, and result serializers. Charset constants standardize UTF-8 conversions for auth headers, tagging data, and xattr strings. Date formatters are UTC and used for S3-style date handling elsewhere in the package.

## Risks and test signals
The largest risk is accidental compatibility breakage if xattr keys or metadata directories change. Tests should exercise object put/get/copy, tagging, multipart initiation/completion, and auth signing with these constants. Header casing is also a signal because S3 clients can be strict around returned names such as `ETAG` versus conventional `ETag`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Constants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Error.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Error.java

## Purpose
`S3Error` is the XML-serializable response body for S3 error responses. It mirrors the AWS-style `<Error>` structure with code, message, request ID, and resource fields.

## Important APIs and control flow
Jackson XML annotations set the root element to `Error` and map getters/setters to `Code`, `Message`, `RequestId`, and `Resource`. The default constructor initializes fields to empty strings for XML serialization. The `S3Error(String resource, S3ErrorCode code)` constructor copies code and description from `S3ErrorCode` and leaves request ID empty.

## State and persistence behavior
It is a transient DTO only. No state is persisted, though its serialized XML is sent to clients by `S3ErrorResponse`.

## Dependencies and integration points
It depends on Jackson XML annotations and `S3ErrorCode`. `S3ErrorResponse` instantiates it and serializes it using `XmlMapper`. Multipart completion keepalive error handling uses `CompleteMultipartUploadResult` rather than this class for embedded errors.

## Risks and test signals
Tests should validate exact XML element names, default constructor serialization, custom message overrides in `S3ErrorResponse`, and empty request ID behavior. Because request ID is always blank here, compatibility tests with clients that expect non-empty request identifiers may be useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Error.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorCode.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorCode.java

## Purpose
`S3ErrorCode` models S3 error names, default messages, and HTTP statuses used by the proxy's exception translation layer. It includes AWS-compatible names plus Alluxio-specific/customized cases.

## Important APIs and control flow
The nested `Name` class holds string identifiers. Static constants instantiate known codes such as `NO_SUCH_BUCKET`, `NO_SUCH_KEY`, `INVALID_ARGUMENT`, `ACCESS_DENIED_ERROR`, `MALFORMED_XML`, and `NOT_IMPLEMENTED`. Each instance exposes `getCode()`, `getDescription()`, and `getStatus()`. Some callers create new `S3ErrorCode` instances dynamically to preserve an AWS code/status while overriding the message.

## State and persistence behavior
The class has immutable per-instance fields and no persistence. It indirectly affects client-visible XML error bodies and status codes. The values are part of the S3 API contract exposed by the proxy.

## Dependencies and integration points
It depends on `javax.ws.rs.core.Response.Status`. `S3Exception` wraps these codes, and `S3ErrorResponse` converts them to XML responses. Bucket and object tasks use constants to report invalid names, missing uploads, bad digests, entity-too-small multipart parts, unsupported APIs, and access denial.

## Risks and test signals
Regression tests should verify status-code mappings and code names for common client behaviors, especially S3A and AWS SDK compatibility. `INVALID_NESTED_BUCKET_NAME` reuses the `BucketAlreadyExists` code with a bad-request status, which is custom and should be covered if nested bucket semantics matter. Message spelling and exact code strings are externally visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorCode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorResponse.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorResponse.java

## Purpose
`S3ErrorResponse` converts internal exceptions into HTTP `Response` objects shaped like S3 errors. It is the central bridge from Alluxio, IO, and S3 exception types to client-visible status codes and XML bodies.

## Important APIs and control flow
`createErrorResponse(Throwable, String)` dispatches by exception type: `AlluxioStatusException`, `AlluxioRuntimeException`, `S3Exception`, `IOException`, or generic fallback. S3 exceptions are mapped by their embedded `S3ErrorCode`. Alluxio status exceptions map not found to `NO_SUCH_KEY`, invalid argument to `INVALID_ARGUMENT`, permission denied to `ACCESS_DENIED_ERROR`, failed precondition to `PRECONDITION_FAILED`, and otherwise internal error. IO file-not-found maps to `NO_SUCH_KEY`; other IO and runtime cases mostly map to internal error.

## State and persistence behavior
The class is stateless. It creates a fresh `XmlMapper` for each response and returns a JAX-RS `Response`. It logs mappings in `finally` blocks for non-S3 typed conversions.

## Dependencies and integration points
It depends on Alluxio exception classes, Jackson XML, SLF4J, `S3Error`, `S3ErrorCode`, and `S3Exception`. It is used by `S3AuthenticationFilter`, `S3RestExceptionMapper`, `S3RequestServlet` handler-creation failures, and servlet stream-copy error handling.

## Risks and test signals
Mapping granularity is limited and may turn many storage failures into `InternalError`. For generic exceptions it returns plain text, not XML, which may surprise S3 clients. Tests should cover every dispatch branch, XML serialization failure fallback, message overriding for Alluxio/IO exceptions, and resource field propagation. Servlet streaming errors are risky because `processResponse` may attempt to write an error after response output has begun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ErrorResponse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Exception.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Exception.java

## Purpose
`S3Exception` is the checked exception type for S3 proxy request failures. It carries an `S3ErrorCode` and optional resource string so error mappers can generate S3-compatible responses.

## Important APIs and control flow
Constructors support an error code only, resource plus code, wrapping an existing exception with resource/code, and custom message/resource/code. The wrapping constructors create a new `S3ErrorCode` with the original code and status but with the exception or supplied message as the description. `getErrorCode()`, `getResource()`, and `setResource()` expose mutable resource data.

## State and persistence behavior
The exception is transient request state. Its error code affects serialized response XML. It does not persist any data.

## Dependencies and integration points
It depends on `S3ErrorCode` and is consumed by `S3ErrorResponse`, `S3RestUtils` translation helpers, and bucket/object tasks. It is also used as a nested cause in XML parsing and tag validation paths.

## Risks and test signals
The custom-message constructor does not call a superclass constructor with the message, so `getMessage()` can be null even though `getErrorCode().getDescription()` is set. Tests should verify response mapping uses the embedded error description, resource mutation, cause preservation in wrapping constructor, and behavior when code-only exceptions lack a resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Exception.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Handler.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Handler.java

## Purpose
`S3Handler` is the per-request coordinator for the newer servlet-based S3 proxy path. It parses bucket/object names, authenticates, initializes common resources, rejects unsupported subresources, creates the correct task, and writes task responses back to the servlet response.

## Important APIs and control flow
`createHandler(path, request, response)` matches bucket/object URL patterns under `S3RequestServlet.S3_V2_SERVICE_PATH_PREFIX`, URL-decodes components, constructs and initializes the handler, then delegates to `S3ObjectTask.Factory` or `S3BucketTask.Factory`. `init()` authenticates, extracts headers, rejects unsupported query subresources, obtains `FileSystem` and audit writer from servlet context, and creates the multipart metadata directory if needed. `processResponse` copies status, headers, and entity data from a JAX-RS `Response` to `HttpServletResponse`; `InputStream` entities are streamed with a thread-local 8 KiB buffer.

## State and persistence behavior
The handler stores bucket/object/user/request/response/context/task and `mMetaFS`. It creates persistent `.alluxio_s3_api_metadata/uploads` metadata storage with restricted permission bits if absent. `BUCKET_PATH_CACHE` is a static expiring Guava cache shared by handlers to speed bucket existence checks.

## Dependencies and integration points
It integrates servlet APIs, Jetty request types, Alluxio `FileSystem`, configuration, audit logging, bucket/object task factories, `S3RestUtils`, `S3ErrorResponse`, and `ProxyWebServer` context attributes. `S3RequestServlet` uses it as the unit of work and stores it as a request attribute.

## Risks and test signals
`extractAMZHeaders` currently records all headers, not only `x-amz-*`, despite the comment. `processResponse` can recursively attempt to emit an error after partial stream output and uses default platform encoding for string entities. Unsupported-subresource rejection is broad and may reject unsupported parameters before operation-specific validation. Tests should cover URL decoding, bucket/object path matching, authentication failure, unsupported query names, metadata directory creation, stream response copying, duplicate headers, and task factory selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Handler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ObjectTask.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ObjectTask.java

## Purpose
`S3ObjectTask` contains object-level task implementations for the servlet-based S3 API: object get/head/put/copy/delete, object tagging, multipart initiation/list/upload/copy/complete/abort, and shared helpers for object creation, directory creation, and copy.

## Important APIs and control flow
`Factory.create(S3Handler)` routes by HTTP verb, query parameters, and copy headers. GET can list parts, get tags, or download. PUT can put tags, upload a multipart part, upload a copy part, copy an object, or put an object. POST initiates or completes multipart upload. DELETE aborts multipart, deletes tags, or deletes an object. `PutObjectTask.createObject` reads either normal or AWS chunked request bodies, writes to Alluxio through `FileOutStream`, computes MD5, validates `Content-MD5`, persists ETag xattr, and returns `ETAG`. `GetObjectTask` supports `Range`, small-positioned reads, rate-limited streaming, content type, ETag, and tag count headers. `CompleteMultipartUploadTask` parses requested parts, validates part existence and minimum sizes, merges parts into a temp object, stores ETag and upload id xattrs, atomically renames with S3 syntax overwrite semantics, and cleans metadata.

## State and persistence behavior
Objects are Alluxio files or convenience directories. Content type, ETag, tags, and multipart metadata are stored in xattrs. Multipart uploads create temporary part directories under the target bucket/object naming scheme and metadata files under `S3RestUtils.MULTIPART_UPLOADS_METADATA_DIR`; completion deletes both after successful rename. Delete operations honor configured Alluxio-only versus underlying-storage delete behavior.

## Dependencies and integration points
The class depends heavily on Alluxio `FileSystem`, `URIStatus`, stream classes, gRPC option builders, `S3RestUtils`, `S3RangeSpec`, `RangeFileInStream`, `RateLimitInputStream`, Jackson XML DTOs, Guava byte utilities/rate limiters, metrics timers, `MultipartUploadCleaner`, and servlet context executors for async complete multipart upload.

## Risks and test signals
Multipart completion returns all uploaded parts after validation rather than filtering to requested parts, so extra uploaded parts may be merged; this deserves focused testing. Upload-part validation has a duplicated `Preconditions.checkNotNull(partNumber, "required 'uploadId'...")`, so missing uploadId may be reported late. `CompleteMultipartUploadTask.handleTaskAsync` writes keepalive whitespace and then XML, making committed status handling subtle. Range reads, positioned reads, copy range, self-copy rejection, MD5 mismatch cleanup, chunked encoding, xattr propagation, idempotent retry completion, and cleanup of temp paths are all high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3ObjectTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RangeSpec.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RangeSpec.java

## Purpose
`S3RangeSpec` parses and resolves HTTP `Range` headers for S3 object reads and copy-source reads. It supports standard byte ranges, open-ended ranges, suffix ranges, and an invalid sentinel used to mean full-object access.

## Important APIs and control flow
`Factory.create(String)` matches `^bytes=(\\d*)-(\\d*)$`, parses optional start/end values, rejects start greater than end, rejects `bytes=-0`, and returns either a valid spec or `INVALID_S3_RANGE_SPEC`. `getOffset(objectSize)` resolves the actual starting offset, including suffix ranges. `getLength(objectSize)` resolves bytes to expose and returns zero if the start is beyond object size. `getRealRange(objectSize)` formats the `Content-Range` value.

## State and persistence behavior
The object is immutable and request-local. It does not persist data. Its computed values drive stream seeking, content-length headers, partial content status, and copy range behavior.

## Dependencies and integration points
It depends on Apache Commons `StringUtils`. It is used by `RangeFileInStream`, `S3ObjectTask.GetObjectTask`, `S3ObjectTask.copyObject`, and equivalent methods in `S3RestServiceHandler`.

## Risks and test signals
Invalid ranges are treated as full-object reads rather than an S3 `InvalidRange` style error. A start beyond object size produces length zero and offset zero, yielding `bytes 0-0/size` for response range formatting. Tests should cover empty/malformed headers, `bytes=0-0`, `bytes=10-`, `bytes=-10`, `bytes=-0`, `bytes=20-10`, suffix larger than object, start equal to size, and very large numeric values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RangeSpec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RequestServlet.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RequestServlet.java

## Purpose
`S3RequestServlet` is the newer servlet entry point for S3 v2 requests. It replaces the JAX-RS resource path when enabled and dispatches each request through `S3Handler` and task objects.

## Important APIs and control flow
`service(request, response)` ignores requests outside `/api/v1/s3` style `S3_V2_SERVICE_PATH_PREFIX`. It creates an `S3Handler`, writes handler creation errors immediately, stores the handler on the request, and either submits work to an async executor or handles it in the current thread. Async routing uses the task `OpTag` to select light or heavy executor services from servlet context. `serveRequest(S3Handler)` invokes `handleTaskAsync()` for complete multipart upload, otherwise calls `continueTask()` and `S3Handler.processResponse()`.

## State and persistence behavior
The servlet is stateless apart from static configuration-derived flags and executor context attributes. It does not persist application state itself. It influences request processing lifetime via servlet async context timeout.

## Dependencies and integration points
It depends on Alluxio configuration keys for v2 async processing and timeout, `ProxyWebServer` request attributes/context executors, servlet async APIs, `S3Handler`, `S3BaseTask`, and `S3ErrorResponse`.

## Risks and test signals
If async mode is enabled but executor context attributes are missing, requests can fail with null executor behavior. Complete multipart upload has a specialized async path that can itself submit to the heavy pool, so tests should cover nested executor behavior and timeout. Non-target paths return without setting a response, which is only safe when servlet mapping ensures this servlet sees matching paths. Tests should cover handler creation failures, sync and async execution, light/heavy routing, and response completion on thrown task errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RequestServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestExceptionMapper.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestExceptionMapper.java

## Purpose
`S3RestExceptionMapper` is the Jersey exception mapper for the older JAX-RS S3 service. It converts uncaught throwables to S3-style HTTP responses.

## Important APIs and control flow
The single `toResponse(Throwable)` method delegates to `S3ErrorResponse.createErrorResponse(e, "")`. It deliberately leaves the resource empty because generic exception mapping lacks request-specific bucket/object context.

## State and persistence behavior
The mapper is stateless and does not persist data.

## Dependencies and integration points
It depends on JAX-RS `ExceptionMapper` and `@Provider`, plus `S3ErrorResponse`. It acts as a safety net around `S3RestServiceHandler` methods and other Jersey providers in the S3 proxy.

## Risks and test signals
Because resource is empty, client-visible XML cannot identify the failed bucket or object in this fallback path. Generic exception branches in `S3ErrorResponse` may return plain text rather than XML. Tests should verify mapper registration, mapping of `S3Exception`, mapping of Alluxio exceptions, and empty resource behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestExceptionMapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestServiceHandler.java

## Purpose
`S3RestServiceHandler` is the older JAX-RS resource implementation of the Alluxio S3 API. It exposes bucket, object, tagging, copy, delete, multipart upload, range GET, and listing operations directly as annotated resource methods.

## Important APIs and control flow
The constructor pulls `FileSystem`, configuration, audit writer, rate limiter, and multipart metadata directory setup from servlet context. Bucket methods include `listAllMyBuckets`, `headBucket`, `getBucket`, `postBucket`, `createBucket`, and `deleteBucket`. Object methods include `createObjectOrUploadPart`, `initiateMultipartUpload`, `getObjectMetadata`, `getObjectOrListParts`, and `deleteObjectOrAbortMultipartUpload`, with private helpers for list parts, get object, tag operations, abort, delete, delimiter path parsing, and audit context creation. The large PUT method multiplexes PutObject, PutObjectTagging, CopyObject, UploadPart, and UploadPartCopy based on query parameters and headers.

## State and persistence behavior
The class is `@NotThreadSafe` and request/resource scoped by Jersey. Bucket state is Alluxio directories; object state is Alluxio files/directories; ETag, content type, tags, multipart upload IDs, bucket/object names, and temporary file IDs are stored in xattrs. Multipart metadata lives under `.alluxio_s3_api_metadata/uploads`, and part data lives in temporary directories. A static bucket path cache mirrors the newer handler cache.

## Dependencies and integration points
It integrates JAX-RS annotations, servlet request context, Alluxio filesystem and gRPC option builders, `S3AuthenticationFilter` user header injection, `S3RestUtils`, DTO classes, Jackson XML, Guava utilities/rate limiters, `RangeFileInStream`, `RateLimitInputStream`, `MultipartUploadCleaner`, and audit logging. Much of its logic is mirrored in `S3BucketTask` and `S3ObjectTask` for the servlet v2 architecture.

## Risks and test signals
The monolithic PUT path has many mutually exclusive combinations and should be tested for invalid parameter/header mixes. Multipart completion is not implemented in this file despite initiation/upload/list/abort support; in v2 it lives in `S3ObjectTask`. Copy metadata/tagging directive behavior, self-copy rejection, MD5 mismatch cleanup, range and suffix reads, delimiter-only `/` support, unsupported ACL/policy/location branches, and cache invalidation are key tests. Because this class duplicates newer task logic, drift between old and v2 behavior is a long-term compatibility risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestServiceHandler.java -->
