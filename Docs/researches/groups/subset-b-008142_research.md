# subset-b-008142 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpoint.java

## Purpose
Main object-level JAX-RS endpoint for the Ozone S3 gateway. It implements S3-compatible PUT, GET, HEAD, DELETE, copy object, multipart upload initiation, part upload/copy, and multipart completion, while translating Ozone client and OM behavior into S3 response shapes, metrics, and audit events.

## Important APIs, types, and functions
- `ObjectEndpoint extends ObjectOperationHandler` and installs an `AuditingObjectOperationHandler` wrapping a handler chain of object ACL, object tagging, multipart-key, and default object handlers.
- `put`, `get`, `delete`, `initializeMultipartUpload`, and `completeMultipartUpload` are REST entry points; `handlePutRequest`, `handleGetRequest`, and `handleDeleteRequest` are chain delegates.
- `copyObject`, `copy`, `createMultipartKey`, and `openKeyForPut` implement source-copy, datastream fallback, part commits, and conditional create/rewrite.
- `ObjectRequestContext` caches volume/bucket lookup and carries action, timing, and performance strings through the handler chain.

## Control flow
PUT first checks `uploadId` to route to part upload, then `x-amz-copy-source` to route to copy object, then optional FSO directory creation for zero-length keys ending in `/`, and finally normal object creation. Large non-EC writes use `ObjectEndpointStreaming`; smaller or EC writes use `S3ObjectWriteGuard` over `OzoneOutputStream`. GET obtains key metadata, rejects FSO directories as missing when configured, evaluates conditional headers, parses range headers, and returns a streaming entity for full or partial reads. DELETE delegates through the chain and treats missing keys and non-empty directory markers as S3-compatible no-content success. MPU completion converts ordered XML parts to a `LinkedHashMap`, applies write conditions through generation or ETag, and maps OM MPU failures to S3 errors.

## State and persistence behavior
The endpoint persists object bytes, custom metadata, ETags, object tags, multipart upload state, and directory markers through `OzoneBucket` and `ClientProtocol` calls. It records MD5 ETags in key metadata and optionally validates `Content-MD5` and signed SHA-256 just before stream commit. Conditional writes are delegated to Ozone atomic create/rewrite APIs so persistence semantics are enforced server-side.

## Dependencies and integration points
Integrates with `EndpointBase`, Ozone client volume/bucket/key APIs, OM exception result codes, `S3ConditionalRequest`, `RangeHeaderParserUtil`, `S3Utils`, tagging helpers, storage-class/replication config, datastream output, audit logging, and `S3GatewayMetrics`. It also depends on query constants in `S3Consts` and response DTOs for copy and multipart XML.

## Risks and edge cases
Critical risks are incorrect AWS compatibility around conditional headers, ETag quoting, range handling, source/destination bucket-owner verification, copy metadata/tag directives, and FSO directory semantics. Datastream is deliberately disabled for EC writes, so changes to replication detection can change durability or performance. Pre-commit hooks must run before closing the Ozone stream; otherwise bad MD5/SHA-256 or short body writes could commit.

## Test signals
Nearby tests exercise object GET/HEAD/range behavior, object endpoint copy and MPU paths, audit logging, conditional failures, missing bucket/key mappings, and S3 gateway metric deltas. Strong signals are exact status codes, ETag headers, `x-amz-mp-parts-count`, metric increments, and S3 error codes for `NO_SUCH_UPLOAD`, `PRECOND_FAILED`, `INVALID_REQUEST`, and missing keys.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpointStreaming.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpointStreaming.java

## Purpose
Static helper for object and multipart writes that use Ozone datastream output instead of the regular `OzoneOutputStream` path. It supports large non-EC PUTs, copy writes, and MPU part uploads while preserving S3 digest and conditional-write behavior.

## Important APIs, types, and functions
- `put` wraps `putKeyWithStream` and translates selected `OMException` values to S3 errors.
- `putKeyWithStream` opens stream keys, copies bytes through `S3ObjectStreamingWriteGuard`, writes ETag metadata, and installs MD5/SHA-256 validation hooks.
- `copyKeyWithStream` streams source data to destination and computes an MD5 ETag from the `DigestInputStream`.
- `createMultipartKey` writes MPU parts through `createMultipartStreamKey` and returns a quoted ETag response.

## Control flow
The helper opens the appropriate datastream key using `createStreamKey`, `createStreamKeyIfNotExists`, or `rewriteStreamKeyIfMatch` based on parsed write conditions. It then copies exactly the expected length, updates metadata latency, stores the computed ETag, attaches pre-commit validators, closes the stream to commit, and returns byte count plus ETag or a JAX-RS response.

## State and persistence behavior
Persistent effects are stream-created object keys and MPU part metadata in Ozone. Metadata mutations happen through the datastream output's `KeyMetadataAware` map before close-time commit. Failure before commit is recorded by the guard so close cannot silently commit a partial transfer.

## Dependencies and integration points
Depends on `OzoneBucket` datastream APIs, `S3ObjectStreamingWriteGuard`, `MultiDigestInputStream`, `S3Utils.validateSignatureHeader`, `S3GatewayMetrics`, `S3ConditionalRequest.WriteConditions`, and S3 constants for checksum headers.

## Risks and edge cases
The path assumes the caller has already excluded EC writes. Signature validation is split: header presence/shape is checked before copying, but actual SHA-256 comparison is a pre-commit hook. MPU datastream exception mapping only handles no-such-upload and permission-denied specially; other OM exceptions bubble to the caller.

## Test signals
Metric tests cover successful and failed create/copy/MPU writes, while object endpoint tests should detect ETag mismatches, invalid `Content-MD5`, SHA-256 mismatch, no-such-upload, and byte length validation. Datastream-specific risk is best caught by tests that force large payloads above the configured threshold.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectEndpointStreaming.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandler.java

## Purpose
Abstract base for object-operation handlers in the endpoint chain. It gives subresource handlers the same dependency surface as `EndpointBase` and a nullable-response contract for chain-of-responsibility dispatch.

## Important APIs, types, and functions
- Defines package-private `handleDeleteRequest`, `handleGetRequest`, `handleHeadRequest`, and `handlePutRequest` hooks.
- Default hook implementations return `null`, meaning the current handler does not own the request.
- `copyDependenciesFrom` uses `EndpointBase.copyDependenciesTo` so handlers share injected clients, headers, context, metrics, and signature state.

## Control flow
Handlers are called in order by `ObjectOperationHandlerChain`. A handler returns a concrete `Response` when it handles the request; otherwise it returns `null` and the next handler is tried.

## State and persistence behavior
This class stores no request state and performs no persistence. Its main state effect is copying endpoint dependencies into handler instances during endpoint initialization.

## Dependencies and integration points
Integrated by `ObjectEndpoint.init`, object ACL/tagging/multipart handlers, and the auditing wrapper. It depends on `ObjectEndpoint.ObjectRequestContext` to carry request metadata.

## Risks and edge cases
Because `null` means "not handled", a handler that accidentally returns `null` after mutating state could allow a second handler to process the same request. Adding new object subresources must preserve chain order so specific handlers run before the default object handler.

## Test signals
Tests should verify subresource query parameters like `tagging`, `acl`, and multipart parameters route to the intended handler and do not fall through to normal object operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandlerChain.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandlerChain.java

## Purpose
Concrete chain-of-responsibility dispatcher for object operations. It lets object subresource handlers intercept requests before the default `ObjectEndpoint` behavior.

## Important APIs, types, and functions
- Stores ordered `List<ObjectOperationHandler> handlers`.
- Overrides delete/get/head/put hooks and returns the first non-null handler response.
- `newBuilder(ObjectEndpoint)` creates a builder that copies endpoint dependencies into each added handler and the final chain.

## Control flow
Each operation loops through handlers in insertion order. The first handler that recognizes the request, usually by query parameter plus HTTP method, returns a response. If no handler recognizes it, `null` is returned to the caller.

## State and persistence behavior
The chain itself is immutable after construction. Persistence is performed only by downstream handlers. Dependency copying is the stateful initialization step.

## Dependencies and integration points
Constructed by `ObjectEndpoint.init` and wrapped by `AuditingObjectOperationHandler`. It coordinates `ObjectAclHandler`, `ObjectTaggingHandler`, `MultipartKeyHandler`, and `ObjectEndpoint`.

## Risks and edge cases
Incorrect handler ordering changes API behavior. A new handler added after `ObjectEndpoint` may never run because the default endpoint handles broad object operations.

## Test signals
Subresource tests should verify dispatch order by sending ambiguous object requests with query parameters and confirming the expected metrics/action/error path.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectOperationHandlerChain.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectTaggingHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectTaggingHandler.java

## Purpose
Handles S3 object tagging subresource requests, namely `PUT ?tagging`, `GET ?tagging`, and `DELETE ?tagging`.

## Important APIs, types, and functions
- Uses a memoized `MessageUnmarshaller<S3Tagging>` for XML request bodies.
- `handlePutRequest` parses XML, validates required tag fields, then calls `OzoneBucket.putObjectTagging`.
- `handleGetRequest` calls `getObjectTagging` and serializes `S3Tagging.fromMap`.
- `handleDeleteRequest` calls `deleteObjectTagging` and maps missing keys to `NoSuchKey`.
- `getAction` detects supported methods when query parameter `tagging` is present.

## Control flow
The handler first calls `context.ignore(getAction())`; if no tagging action applies it returns `null`. For PUT, XML parsing and semantic validation happen before converting to Ozone tag maps via endpoint tag validators. Success and failure update operation-specific tagging metrics.

## State and persistence behavior
PUT persists the tag map on the object through Ozone bucket metadata. DELETE removes the object's tag set. GET is read-only and returns sorted tag XML through `S3Tagging.fromMap`.

## Dependencies and integration points
Depends on object endpoint context for bucket lookup, `S3Tagging`, `MessageUnmarshaller`, endpoint tag validation helpers, `S3GatewayMetrics`, `S3Consts.QueryParams.TAGGING`, and OM exception result codes.

## Risks and edge cases
Malformed XML is converted to `MalformedXML` with the parser message appended. Delete tagging is intentionally stricter than object deletion: missing keys are errors, not 204. Tag value validation is split between XML structural checks and endpoint-level tag policy validation.

## Test signals
Tests should cover empty/missing `TagSet`, missing key/value fields, duplicate or invalid tags, sorted GET responses, missing-key delete behavior, and metric success/failure counters.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/ObjectTaggingHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/PlainTextMultipartUploadReader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/PlainTextMultipartUploadReader.java

## Purpose
JAX-RS message body reader that accepts `text/plain` multipart-upload completion requests and returns an empty `CompleteMultipartUploadRequest`.

## Important APIs, types, and functions
- Annotated with `@Provider` and `@Consumes("text/plain")`.
- `isReadable` matches only `CompleteMultipartUploadRequest` with `MediaType.TEXT_PLAIN_TYPE`.
- `readFrom` ignores the body and returns a new empty completion request.

## Control flow
JAX-RS provider selection calls `isReadable`; if selected, `readFrom` prevents text/plain parsing failures by supplying an empty object.

## State and persistence behavior
No state is stored and no persistence occurs. It only influences request deserialization before endpoint logic.

## Dependencies and integration points
Integrated with `ObjectEndpoint.completeMultipartUpload`, which expects a `CompleteMultipartUploadRequest` parameter. It exists for AWS CLI behavior where `aws s3 cp` can send multipart requests as `text/plain`.

## Risks and edge cases
Returning an empty request can intentionally drive endpoint-level validation such as "must specify at least one part". A too-broad `isReadable` match would hide real malformed bodies for other resource methods.

## Test signals
Tests should send text/plain MPU completion/initiation style requests and verify the gateway returns S3 validation errors rather than a JAX-RS media parsing failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/PlainTextMultipartUploadReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/RootEndpoint.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/RootEndpoint.java

## Purpose
Top-level S3 gateway endpoint for `GET /`. It lists normal S3 buckets or, when signed for the `s3express` service, lists FSO directory buckets in an S3 Express-compatible response.

## Important APIs, types, and functions
- `get` dispatches between `listAllBuckets` and `listDirectoryBuckets`.
- `isS3ExpressSignedRequest` inspects SigV4 credential scope service segment.
- `listDirectoryBuckets` supports continuation tokens, `max-directory-buckets`, region resolution, ARN construction, and FSO filtering.
- `buildDirectoryBucketArn` formats `arn:aws:s3express:<region>:<account>:bucket/<bucket>`.

## Control flow
Normal listing calls `listS3Buckets` and fills `ListBucketResponse` with owner and bucket metadata. Directory bucket listing decodes optional `continuation-token`, iterates S3 buckets starting after the previous bucket, skips non-FSO layouts, caps the result count, and emits a new continuation token when more buckets remain.

## State and persistence behavior
The endpoint is read-only. It observes bucket metadata and layout state through Ozone client listing. Continuation state is client-visible and encoded by `ContinueToken`.

## Dependencies and integration points
Depends on `EndpointBase.listS3Buckets`, `ListBucketResponse`, `ListDirectoryBucketsResponse`, `DirectoryBucketMetadata`, `ContinueToken`, `S3Owner`, `S3Consts`, audit logging, and list-bucket metrics.

## Risks and edge cases
Continuation only tracks the last emitted bucket name; because non-FSO buckets are skipped after iteration, pagination must not skip later FSO buckets. `max-directory-buckets` is capped at 1000 and rejects negative values. Region comes from credential scope, falling back to `us-east-1`, so malformed or unsigned S3 Express-like requests get default region metadata.

## Test signals
Tests should assert normal bucket XML owner/listing, S3 Express detection from credential scope, max cap and negative-argument failure, continuation token round trip, FSO-only filtering, ARN formatting, and list success/failure metrics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/RootEndpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Acl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Acl.java

## Purpose
Conversion utility between S3 ACL grants and Ozone native ACLs for bucket/object ACL compatibility.

## Important APIs, types, and functions
- Defines S3 grant header names and unsupported canned ACL header.
- `ACLType` models S3 permissions: READ, WRITE, READ_ACP, WRITE_ACP, FULL_CONTROL.
- `ACLIdentityType` maps grantee identity types and currently supports only `CanonicalUser`.
- `ozoneNativeAclToS3Acl` converts Ozone user ACLs to S3 `Grant` values.
- `s3AclToOzoneNativeAcl` converts S3 bucket ACL XML grants into volume and bucket Ozone ACL lists.
- `getOzoneAclOnBucketFromS3Permission` and `getOzoneAclOnVolumeFromS3Permission` implement permission expansion.

## Control flow
Read conversion ignores non-user Ozone ACLs, maps broad ACL sets to the best S3 permission, and logs when no S3 mapping is available. Write conversion iterates grants, validates supported grantee type and permission, creates least-privilege volume ACLs, and creates both default and access bucket ACLs.

## State and persistence behavior
This utility itself is stateless. The produced Ozone ACL lists are later persisted by bucket/object ACL handlers through Ozone APIs.

## Dependencies and integration points
Integrated by ACL handlers and `S3BucketAcl` DTOs. Depends on `OzoneAcl`, `IAccessAuthorizer.ACLType`, S3 error translation, and S3 XML grant objects.

## Risks and edge cases
Only canonical users are supported; S3 groups and email grantees return `NotImplemented`. Mapping Ozone ACL sets back to S3 is lossy and priority based, so mixed ACLs may be logged without a precise S3 equivalent. ACL grant header parsing is not in this class.

## Test signals
ACL tests should assert canonical-user conversions, unsupported grantee failures, invalid permission errors, volume least-privilege mappings, and bucket access/default ACL expansion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Acl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3BucketAcl.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3BucketAcl.java

## Purpose
JAXB model for S3 `AccessControlPolicy` XML used by bucket and object ACL APIs.

## Important APIs, types, and functions
- Root fields are `Owner` and `AccessControlList`.
- Nested `AccessControlList` stores ordered `Grant` objects.
- Nested `Grant` combines a `Grantee` and permission string.
- Nested `Grantee` serializes `DisplayName`, `ID`, `xsi:type`, and `xmlns:xsi`, defaulting to `CanonicalUser`.
- Equality and hash code are implemented on grant and grantee DTOs for tests and comparisons.

## Control flow
The class is passive. JAX-RS/JAXB reads and writes XML directly from the annotated fields. `S3Acl` consumes and produces these DTOs for ACL conversion.

## State and persistence behavior
No persistence occurs in this model. It represents wire-format ACL state that other handlers apply to Ozone ACL storage.

## Dependencies and integration points
Used by ACL endpoint handlers, `S3Acl`, and XML marshalling with the package-level S3 namespace. Depends on `S3Owner` and `S3Consts.S3_XML_NAMESPACE`.

## Risks and edge cases
Null `aclList`, null `grantee`, or invalid permission strings must be handled by callers; this DTO does not validate them. Default `CanonicalUser` XML attributes are important for AWS client compatibility.

## Test signals
Serialization tests should verify namespace, owner fields, default `xsi:type`, grant equality, and round-trip XML consumed by ACL conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3BucketAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ConditionalRequest.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ConditionalRequest.java

## Purpose
Shared conditional-header parsing and evaluation for S3 object reads, source-copy validation, and conditional writes.

## Important APIs, types, and functions
- `PreconditionContext` maps normal read headers and copy-source headers to common evaluation logic.
- `evaluatePreconditions` handles `If-Match`, `If-None-Match`, `If-Modified-Since`, and `If-Unmodified-Since`.
- `checkCopySourceModificationTime` supports the older copy-part modification-time flow.
- `parseWriteConditions` validates conditional PUT headers and returns `WriteConditions`.
- `WriteConditions` exposes `hasIfNoneMatch`, `hasIfMatch`, and parsed expected ETag.

## Control flow
Evaluation checks `If-Match` first, then `If-Unmodified-Since` only when no `If-Match` exists, then `If-None-Match`, then `If-Modified-Since`. READ context can return a 304 response with ETag and Last-Modified; COPY_SOURCE context throws 412 for failed conditions. Write parsing rejects empty values, simultaneous `If-Match` and `If-None-Match`, and any `If-None-Match` value other than `*`.

## State and persistence behavior
No persistent state is modified. The resulting `WriteConditions` drive Ozone create-if-absent or rewrite-if-match APIs in object write paths.

## Dependencies and integration points
Used by GET, HEAD, copy object, PUT, stream PUT, and MPU completion. Depends on Ozone key metadata, `OzoneUtils.formatDate`, `ObjectEndpoint` header helpers, `S3Utils.parseETag`, and `S3ErrorTable`.

## Risks and edge cases
Invalid date headers are ignored as non-matching AWS-style cache validation rather than hard failures. ETag matching supports comma-separated values and wildcard. The `If-Unmodified-Since` precedence differs when `If-Match` is present, so tests should pin compatibility. Write-side support is intentionally narrower than full HTTP semantics.

## Test signals
Tests should cover 304 responses, 412 failures, wildcard and comma ETag values, invalid date strings, copy-source header variants, unsupported conditional PUT combinations, missing keys with `If-Match`, and MPU completion precondition mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ConditionalRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectStreamingWriteGuard.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectStreamingWriteGuard.java

## Purpose
Datastream-specific write guard that adapts `S3ObjectWriteGuard` to `OzoneDataStreamOutput`.

## Important APIs, types, and functions
- Constructor registers inherited pre-commit checks with `OzoneDataStreamOutput`.
- Overrides `write` to send a `ByteBuffer` to datastream output.
- Overrides `getMetadata` through `KeyMetadataAware`.
- Overrides `close` to close the datastream output.

## Control flow
The inherited copy loop tracks bytes and transfer failures. This subclass changes only the sink operation and metadata access path.

## State and persistence behavior
Persistent object or MPU data is committed by `OzoneDataStreamOutput.close` after registered pre-commit hooks pass. Metadata is mutated through the datastream output's key metadata map before close.

## Dependencies and integration points
Used by `ObjectEndpointStreaming` for datastream PUT, copy, and multipart part writes. Depends on `OzoneDataStreamOutput` and `KeyMetadataAware`.

## Risks and edge cases
If a datastream output implementation stops implementing `KeyMetadataAware`, ETag/tag metadata writes fail at runtime. ByteBuffer wrapping must preserve offset and length correctly for partial buffer writes.

## Test signals
Datastream tests should assert content length validation, close-time pre-commit failure behavior, ETag metadata persistence, and correct byte counts for non-zero offsets.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectStreamingWriteGuard.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectWriteGuard.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectWriteGuard.java

## Purpose
Guarded copy/commit helper for S3 object writes. It tracks the number of bytes transferred, records transfer failures, and installs pre-commit checks on Ozone output streams.

## Important APIs, types, and functions
- Constructors accept `OzoneOutputStream` or generic `OutputStream`; the Ozone constructor registers pre-commit hooks immediately.
- `copyFrom` reads up to `expectedLength` into a bounded buffer and writes to the output stream.
- `validateBeforeCommit` rejects prior transfer failures and content-length mismatches.
- `addPreCommit` lets callers add MD5 and SHA-256 validators.
- `getMetadata` exposes `OzoneOutputStream` metadata for ETag and custom metadata mutation.

## Control flow
On construction the guard adds a content-length pre-commit hook. `copyFrom` loops until expected bytes are written or EOF occurs, recording read/write exceptions. `close` closes the stream, triggering Ozone pre-commit hooks before the write is committed.

## State and persistence behavior
The guard itself tracks in-memory `writtenLength` and `transferFailure`. Persistent commit happens only when the underlying output stream closes successfully with all pre-commit validators passing.

## Dependencies and integration points
Used by normal PUT, copy object, multipart part upload, and MPU part copy. Depends on `EndpointBase.validateContentLength`, `OzoneOutputStream.setPreCommits`, and Ratis `CheckedRunnable`.

## Risks and edge cases
The copy loop intentionally stops at `expectedLength`; extra bytes in the request body are not consumed here. EOF before expected length is detected at commit, not at read time. `getMetadata` assumes the generic stream is actually an `OzoneOutputStream` except in subclasses.

## Test signals
Tests should cover short body rejection, read/write exception propagation, custom pre-commit failures, metadata updates before close, and no commit after transfer failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3ObjectWriteGuard.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Owner.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Owner.java

## Purpose
XML DTO and helper for S3 owner identity plus expected bucket-owner condition validation.

## Important APIs, types, and functions
- `DEFAULT_S3OWNER_ID` and `DEFAULT_S3_OWNER` provide canonical Ozone owner identity defaults.
- `of(String displayName)` creates owner DTOs using the default canonical ID and volume owner as display name.
- `hasBucketOwnershipVerificationConditions` detects expected destination/source owner headers.
- `verifyBucketOwnerCondition` and `verifyBucketOwnerConditionOnCopyOperation` enforce owner matches.

## Control flow
Verification reads the relevant header, skips empty headers or null actual owner, and throws `BUCKET_OWNER_MISMATCH` if the expected value differs from the actual owner.

## State and persistence behavior
No persistent state is modified. Owner values are serialized into list/ACL responses and used to gate operations.

## Dependencies and integration points
Used by root listing, object HEAD/PUT/copy/MPU operations, and ACL DTOs. Depends on `S3Consts.EXPECTED_BUCKET_OWNER_HEADER`, `S3Consts.EXPECTED_SOURCE_BUCKET_OWNER_HEADER`, and `S3ErrorTable`.

## Risks and edge cases
Ozone bucket owner strings are compared directly with expected S3 header values, so caller assumptions about canonical ID versus username matter. Copy operations may validate source and destination independently; callers pass nulls when a side was already checked.

## Test signals
Tests should assert matching owner pass-through, mismatched source/destination owner failures, empty header ignored, and correct response XML owner fields.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Owner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3RequestContext.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3RequestContext.java

## Purpose
Per-request context object shared by object operation handlers for timing, action selection, lazy volume lookup, and performance logging.

## Important APIs, types, and functions
- Captures `startNanos` at construction.
- Holds `PerformanceStringBuilder`, `EndpointBase`, mutable `S3GAction`, and cached `OzoneVolume`.
- `getVolume` lazily calls `endpoint.getVolume`.
- `ignore(@Nullable S3GAction)` stores non-null handler actions and tells handlers whether to skip a request.

## Control flow
Endpoint entry points create a context with a best-guess action. Subresource handlers call `ignore` with their detected action; if non-null, the action is updated for audit logging and the handler processes the request.

## State and persistence behavior
Only in-memory per-request state is stored. It does not modify Ozone state directly.

## Dependencies and integration points
Used by `ObjectEndpoint`, `ObjectOperationHandlerChain`, tagging, ACL, multipart, and auditing handlers. Depends on `EndpointBase`, `S3GAction`, and Ozone client volume objects.

## Risks and edge cases
The mutable action is central to audit correctness. If a handler forgets to call `ignore` or sets the wrong action, the operation may be logged and metered incorrectly.

## Test signals
Audit tests should verify operation names for normal objects and subresources. Handler dispatch tests should ensure lazy volume/bucket lookups do not happen for ignored handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3RequestContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Tagging.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Tagging.java

## Purpose
JAXB DTO for S3 object tagging XML and small validation/conversion helper.

## Important APIs, types, and functions
- Root `S3Tagging` contains `TagSet`.
- `TagSet` contains a list of `Tag`.
- `Tag` contains `Key` and `Value`.
- `fromMap` creates sorted tag XML from an Ozone tag map.
- `validate` requires a non-null tag set, at least one tag, and non-null key/value fields.

## Control flow
PUT tagging unmarshalling fills this DTO, then `validate` performs structural checks before endpoint-level tag policy validation. GET tagging uses `fromMap`, sorting entries by key for stable AWS-compatible output.

## State and persistence behavior
No persistence occurs here. It represents tag state exchanged with clients.

## Dependencies and integration points
Used by `ObjectTaggingHandler` and JAXB marshalling with `S3Consts.S3_XML_NAMESPACE`.

## Risks and edge cases
This class does not enforce S3 tag count, character, prefix, or length limits; those are enforced elsewhere. Empty tag sets are rejected, so callers cannot use PUT tagging to clear tags.

## Test signals
Tests should cover XML unmarshalling, missing `TagSet`, empty tags, missing key/value, stable sorted output, and coordination with endpoint tag validators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/S3Tagging.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/XmlNamespaceFilter.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/XmlNamespaceFilter.java

## Purpose
SAX filter that forces all element callbacks into a configured namespace, allowing namespace-insensitive client XML to be read as S3 namespace-qualified XML.

## Important APIs, types, and functions
- Constructor accepts namespace URI.
- `startElement` and `endElement` replace the incoming URI with the configured namespace before delegating.

## Control flow
During SAX parsing, each element start/end event is rewritten with the target namespace while local name, qualified name, and attributes pass through.

## State and persistence behavior
Stores only the configured namespace string. It performs no persistence.

## Dependencies and integration points
Used by XML unmarshalling infrastructure for endpoint DTOs that expect `S3Consts.S3_XML_NAMESPACE`.

## Risks and edge cases
The filter does not rewrite attribute namespaces. If client XML uses namespace-sensitive attributes, callers must handle those separately.

## Test signals
XML parsing tests should include S3 request bodies with and without explicit default namespaces and verify they unmarshal into the same DTOs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/XmlNamespaceFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java

## Purpose
Package-level documentation and JAXB namespace configuration for S3 gateway endpoint DTOs.

## Important APIs, types, and functions
- Declares `@XmlSchema` with namespace `S3Consts.S3_XML_NAMESPACE`.
- Sets `elementFormDefault` to qualified.
- Defines an empty prefix for the S3 XML namespace.

## Control flow
JAXB uses this metadata during marshalling and unmarshalling of endpoint package classes.

## State and persistence behavior
No runtime state or persistence. It controls XML wire format.

## Dependencies and integration points
Applies to response/request classes in `org.apache.hadoop.ozone.s3.endpoint`, including ACL, tagging, listing, and multipart DTOs.

## Risks and edge cases
Changing this namespace would alter client-visible XML and could break AWS SDK compatibility. It must stay aligned with `XmlNamespaceFilter` and `S3Consts`.

## Test signals
XML serialization tests should assert the S3 namespace appears correctly and that unqualified XML request bodies can still be accepted through the namespace filter.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/endpoint/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/BadRequestExceptionMapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/BadRequestExceptionMapper.java

## Purpose
JAX-RS exception mapper for generic `BadRequestException` values not represented as `OS3Exception`.

## Important APIs, types, and functions
- Annotated with `@Provider`.
- Implements `ExceptionMapper<BadRequestException>`.
- `toResponse` returns HTTP 400 with `exception.getMessage()` as the entity.

## Control flow
When JAX-RS raises `BadRequestException`, this mapper logs at debug level and builds a plain bad-request response.

## State and persistence behavior
Stateless; no persistence.

## Dependencies and integration points
Complements `OS3ExceptionMapper` for framework-level request parsing errors such as malformed parameters or body conversion failures.

## Risks and edge cases
The response body is not S3 XML error format, unlike `OS3Exception`. This can leak implementation-specific messages and can be less compatible with AWS clients.

## Test signals
Tests should verify malformed framework-level requests return 400 and decide whether S3 XML formatting is required for compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/BadRequestExceptionMapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3Exception.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3Exception.java

## Purpose
Runtime exception type representing an S3-compatible error response, including error code, message, resource, request ID, HTTP status, and XML serialization.

## Important APIs, types, and functions
- JAXB annotations map fields to S3 `<Error>` XML.
- Package-private constructor accepts `S3ErrorTable`, cause, and resource.
- `toXml` serializes through Jackson `XmlMapper` with JAXB annotations and XML declaration.
- `withMessage` customizes the S3 error message fluently.

## Control flow
`S3ErrorTable.newError` constructs the exception and logs it. `OS3ExceptionMapper` later sets request ID and serializes it as the HTTP entity.

## State and persistence behavior
Only in-memory exception state is held. No persistence occurs.

## Dependencies and integration points
Used throughout endpoint, auth, util, and exception mapping code. Depends on Jackson XML, JAXB annotations, and `S3ErrorTable`.

## Risks and edge cases
Serialization fallback manually formats XML if Jackson fails. `super` message remains the original table message even if `withMessage` or `setErrorMessage` changes the XML message. Request ID is injected later, so logging at construction may show null request ID.

## Test signals
`TestOS3Exceptions` checks XML and code/message behavior. Additional tests should cover customized messages, resource fields, request ID injection, and mapper HTTP status.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3Exception.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3ExceptionMapper.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3ExceptionMapper.java

## Purpose
JAX-RS mapper that turns `OS3Exception` into S3 XML HTTP responses.

## Important APIs, types, and functions
- Annotated with `@Provider`.
- Injects `RequestIdentifier`.
- `toResponse` sets the request ID on the exception, uses its HTTP code, and returns `exception.toXml()` as entity.

## Control flow
Endpoint code throws `OS3Exception`; JAX-RS invokes this mapper; the mapper adds request ID just before serialization.

## State and persistence behavior
Stateless aside from injected request identifier. No persistence.

## Dependencies and integration points
Integrated with all endpoint and auth errors that use `S3ErrorTable`. Depends on request ID infrastructure for AWS-style error tracing.

## Risks and edge cases
The mapper does not set an explicit XML content type. If `requestIdentifier` injection fails, request ID serialization may fail or be null depending on runtime behavior.

## Test signals
Tests should assert status code, XML body, request ID field, and behavior for customized `OS3Exception` messages.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/OS3ExceptionMapper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/S3ErrorTable.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/S3ErrorTable.java

## Purpose
Central table of S3-compatible error codes, messages, and HTTP status codes, plus translation from Ozone Manager exception result codes.

## Important APIs, types, and functions
- Enum values cover bucket/key not found, auth failures, invalid request/argument/range, MPU errors, ACL/tagging errors, quota/storage/digest errors, and conditional conflicts.
- `translateResultCode(OMException)` maps OM result codes to S3 errors.
- `newError` overloads construct `OS3Exception` by table entry, resource, cause, bucket/resource pair, or OM exception.
- `log` emits internal errors at error level and other errors at debug level.

## Control flow
Endpoint code catches `OMException` and calls `newError`, either with generic translation or special-case overrides. Translation maps access and token failures to `AccessDenied`, atomic write conflicts to `ConditionalRequestConflict`, ETag/key-exists failures to `PreconditionFailed`, and unknown results to `InternalError`.

## State and persistence behavior
Static immutable enum metadata only. No persistence.

## Dependencies and integration points
Used by every endpoint package and signature/parser utilities. It is the compatibility bridge between OM errors and S3 XML errors.

## Risks and edge cases
The translation table is a compatibility contract; adding OM result codes without updating it can expose `InternalError` for client errors. `NO_SUCH_BUCKET` uses bucket as resource in the bucket/resource overload, which differs from other errors.

## Test signals
Exception tests should pin every OM result translation used by endpoints, HTTP status codes, XML codes/messages, and special cases like conditional conflicts, digest mismatch, and bucket owner mismatch.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/S3ErrorTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/package-info.java

## Purpose
Package documentation for Ozone S3 exception classes.

## Important APIs, types, and functions
- Declares the `org.apache.hadoop.ozone.s3.exception` package.
- Documents that the package contains Ozone S3 exceptions.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Applies to `OS3Exception`, exception mappers, and `S3ErrorTable`.

## Risks and edge cases
Only documentation. Any package-level annotations added later would affect all exception classes.

## Test signals
No direct tests are needed unless package-level annotations are introduced.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/exception/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/S3GatewayMetrics.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/S3GatewayMetrics.java

## Purpose
Metrics2 source for S3 gateway operation counters, byte counters, list counts, and latency distributions.

## Important APIs, types, and functions
- Singleton lifecycle is managed by `create`, `unRegister`, `getMetrics`, and `close`.
- Counter groups cover bucket endpoints, root listing, object operations, multipart operations, object tagging, object ACL, and byte totals.
- Latency metrics are `PerformanceMetrics` instances initialized from configured percentile intervals.
- `getMetrics(MetricsCollector, boolean)` snapshots every counter and latency metric.
- `update*SuccessStats`, `update*FailureStats`, and `inc*Length` methods mutate counters and latency distributions.

## Control flow
Gateway startup calls `create` to register the source with the default metrics system. Endpoints call update methods at success/failure boundaries using request `startNanos`. Some update methods return elapsed nanoseconds so endpoint audit performance strings can include the same latency.

## State and persistence behavior
Metrics are in-memory process state registered with Hadoop Metrics2. They are not persisted here, but exported to configured metrics sinks/JMX. `close` shuts down percentile resources.

## Dependencies and integration points
Used by `Gateway`, `BucketEndpoint`, `RootEndpoint`, `ObjectEndpoint`, `ObjectEndpointStreaming`, tagging/ACL handlers, and tests. Depends on `DefaultMetricsSystem`, `MutableCounterLong`, `MetricsRegistry`, `PerformanceMetrics`, and S3 gateway config percentile intervals.

## Risks and edge cases
The singleton can be null if endpoints call `getMetrics` before gateway startup. `unRegister` closes the instance and unregisters the source; repeated tests must clean up to avoid stale counters. New endpoint operations require adding fields, snapshot entries, update methods, getters, and tests together.

## Test signals
`TestS3GatewayMetrics` exercises operation success/failure deltas for bucket, object, MPU, tagging, and byte counters. Metrics-source tests should also verify singleton lifecycle, snapshot names, latency increments, and cleanup between tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/S3GatewayMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/package-info.java

## Purpose
Package documentation for S3 gateway metrics classes.

## Important APIs, types, and functions
- Declares the `org.apache.hadoop.ozone.s3.metrics` package.
- Documents that the package contains Ozone S3 metrics.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Applies to `S3GatewayMetrics`.

## Risks and edge cases
Documentation only; future package annotations would affect the metrics source package.

## Test signals
No direct tests needed for the package-info file.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/metrics/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/package-info.java

## Purpose
Package documentation for top-level S3 gateway classes.

## Important APIs, types, and functions
- Declares the `org.apache.hadoop.ozone.s3` package.
- Documents that the package contains top-level generic S3 gateway classes.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Applies to top-level gateway filters, configuration, bootstrap, and shared helper classes outside endpoint-specific packages.

## Risks and edge cases
Documentation only.

## Test signals
No direct tests needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AWSSignatureProcessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AWSSignatureProcessor.java

## Purpose
Request-scoped signature processor that detects and parses AWS S3 authorization formats into `SignatureInfo`.

## Important APIs, types, and functions
- Implements `SignatureProcessor`.
- `parseSignature` tries V4 authorization header, V4 query parameters, then V2 authorization header.
- `LowerCaseKeyStringMap` normalizes request headers, combines duplicates, and restores original content type after header preprocessing.
- `buildAuthFailureMessage` creates S3 auth audit failure records.
- `setContext` supports tests.

## Control flow
Headers are copied to a lowercase map. Parser instances are tried in fixed priority order; malformed parser input is audited and returned as `AuthorizationHeaderMalformed`; null parser results mean "not this auth style". If nothing matches, version `NONE` is returned. The unfiltered request URI path is stored for canonical request construction.

## State and persistence behavior
Holds request context only for the request scope. No persistence.

## Dependencies and integration points
Used by authorization filters and request injection. Depends on JAX-RS `ContainerRequestContext`, `AuthorizationV4HeaderParser`, `AuthorizationV4QueryParser`, `AuthorizationV2HeaderParser`, audit logger, `AuditUtils`, and `HeaderPreprocessor`.

## Risks and edge cases
Parser priority matters when both header and query credentials exist. Duplicate headers are concatenated using only the first value from each map entry, which may diverge from canonical AWS behavior. Content-Type repair is required because header preprocessing can otherwise break signatures.

## Test signals
`TestAWSSignatureProcessor` and authorization filter tests should cover header/query/V2 detection, unsigned requests, malformed audit failures, lowercase lookup, duplicate header combining, and original content-type restoration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AWSSignatureProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthOperation.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthOperation.java

## Purpose
Audit action implementation for authentication and authorization events.

## Important APIs, types, and functions
- Stores request path and HTTP method.
- `fromContext` builds an action from `ContainerRequestContext`.
- `getAction` formats `AUTH(<method> <path>)`.

## Control flow
Used when auth parsing or authorization fails to build a readable audit operation name.

## State and persistence behavior
In-memory audit action only. Persistence is through audit logging infrastructure, not this class.

## Dependencies and integration points
Used by `AWSSignatureProcessor` when building auth failure messages. Implements `AuditAction`.

## Risks and edge cases
Path formatting prepends `/` to `UriInfo.getPath`; changes in JAX-RS path normalization affect audit text.

## Test signals
Auth audit tests should assert formatted action strings for root and nested object paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthOperation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV2HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV2HeaderParser.java

## Purpose
Parser for legacy AWS Signature Version 2 `Authorization` headers.

## Important APIs, types, and functions
- `IDENTIFIER` is `AWS`.
- `parseSignature` accepts headers of form `AWS <accessKey>:<signature>`.
- Returns `SignatureInfo` with version `V2`, access key, and signature.

## Control flow
If the auth header is absent or does not start with `AWS `, it returns null. Otherwise it validates the two-token auth shape, the `accessKey:signature` shape, and nonblank access key/signature.

## State and persistence behavior
No state beyond the constructor-supplied header. No persistence.

## Dependencies and integration points
Used as the final parser fallback in `AWSSignatureProcessor`. The resulting `SignatureInfo` is later consumed by auth code.

## Risks and edge cases
Splitting on spaces and colons is strict; extra spaces or colon-containing signatures will be malformed. V2 canonical string generation is not in this file.

## Test signals
Tests should cover valid V2 auth, absent/non-V2 headers returning null, blank access key/signature, and malformed token counts.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV2HeaderParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4HeaderParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4HeaderParser.java

## Purpose
Parser and validator for AWS Signature Version 4 authorization headers.

## Important APIs, types, and functions
- `parseSignature` parses `AWS4-HMAC-SHA256 Credential=..., SignedHeaders=..., Signature=...`.
- `parseAlgorithm` enforces `AWS4-HMAC-SHA256`.
- `parseCredentials` builds and validates `Credential`.
- `parseSignedHeaders` validates non-empty signed header list.
- `parseSignature` validates non-empty hex signature.
- `validateDateRange` allows credential dates from yesterday through tomorrow.

## Control flow
Non-AWS4 headers return null. AWS4 headers must contain a space separating algorithm and attributes, exactly three comma-separated attributes, valid credential scope, signed headers, and hex signature. Date range and format failures are reported as `MalformedResourceException` carrying the full header as resource.

## State and persistence behavior
Stores only constructor-supplied auth/date headers. No persistence.

## Dependencies and integration points
Used by `AWSSignatureProcessor`. Depends on `Credential`, `SignatureInfo`, `SignatureProcessor.DATE_FORMATTER`, Apache Commons Hex decoding, and Hadoop string collection parsing.

## Risks and edge cases
The parser is strict about attribute order and count. It validates credential date but uses the `x-amz-date` header as `dateTime` without checking it here; canonical request validation handles timestamp range later. Credential service is not limited to `s3`, which enables S3 Express service scopes.

## Test signals
`TestAuthorizationV4HeaderParser` should cover valid parsing, missing fields, invalid algorithm, non-hex signatures, empty signed headers, invalid credential segments, and date range limits.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4HeaderParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4QueryParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4QueryParser.java

## Purpose
Parser and validator for SigV4 presigned URL query parameters.

## Important APIs, types, and functions
- `parseSignature` requires `X-Amz-Signature` and returns version `V4` with `signPayload=false`.
- `validateAlgorithm` enforces `AWS4-HMAC-SHA256`.
- `validateDateAndExpires` enforces `X-Amz-Date`, `X-Amz-Expires`, 1 to 604800 seconds, and not expired.
- `validateCredential`, `validateSignedHeaders`, and `validateSignature` validate credential scope, signed headers, and hex signature.

## Control flow
If no `X-Amz-Signature` is present, returns null. Otherwise it validates algorithm, date/expiry, URL-decodes credential, validates credential fields and date, signed headers, and signature before building `SignatureInfo`.

## State and persistence behavior
Stores query parameter map only. No persistence.

## Dependencies and integration points
Used by `AWSSignatureProcessor` for presigned requests. Depends on `Credential`, `StringToSignProducer.TIME_FORMATTER`, `S3Utils.urlDecode`, and Commons Hex decoding.

## Risks and edge cases
`X-Amz-Expires` is parsed with `Long.parseLong`; nonnumeric values can throw outside the declared `DateTimeParseException` catch in `parseSignature`. Query parameters are single-valued by prior conversion, so repeated params lose all but the first value. Expiry uses local current time at parse time.

## Test signals
Tests should cover valid presigned URLs, missing algorithm/date/expires/signed headers, expired URLs, out-of-range expiry, invalid credential URL encoding, non-hex signature, and nonnumeric expires.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/AuthorizationV4QueryParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/Credential.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/Credential.java

## Purpose
Model and parser for the SigV4 credential scope value.

## Important APIs, types, and functions
- Constructor stores raw credential string and calls `parseCredential`.
- `parseCredential` supports normal five-part credentials and six-part Kerberos-principal access IDs containing `/`.
- Getters expose access key ID, date, AWS region, service, request suffix, and raw credential.
- `createScope` returns `<date>/<region>/<service>/<request>`.

## Control flow
The credential is split on `/`. Five segments map directly. Six segments join the first two as the access key ID to support Kerberos principals. Any other count throws `MalformedResourceException`.

## State and persistence behavior
Only parsed credential fields are stored in memory. No persistence.

## Dependencies and integration points
Used by V4 header and query parsers and later by `StringToSignProducer` via `SignatureInfo.credentialScope`.

## Risks and edge cases
Only one embedded slash in the access key is supported. More complex principal strings or unescaped slashes in access IDs fail parsing. Validation of non-empty fields and date format is left to parser callers.

## Test signals
Tests should cover five-part credentials, Kerberos six-part credentials, malformed segment counts, blank fields, and `createScope` formatting.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/Credential.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/MalformedResourceException.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/MalformedResourceException.java

## Purpose
Checked exception used by signature parsers to report malformed auth resources while preserving the offending header/query value.

## Important APIs, types, and functions
- Stores immutable `resource`.
- Constructors accept resource only or message plus resource.
- `getResource` exposes the value used for S3 error resource and audit logging.

## Control flow
Parsers throw this exception when they recognize their auth style but validation fails. `AWSSignatureProcessor` catches it, audits, and maps it to `AuthorizationHeaderMalformed`.

## State and persistence behavior
In-memory exception state only. No persistence.

## Dependencies and integration points
Used by all signature parsers and `Credential`.

## Risks and edge cases
Some parser paths pass user-supplied full authorization headers as resource; callers should avoid logging sensitive signatures at inappropriate levels.

## Test signals
Tests should assert processor mapping and audit resource selection for malformed auth inputs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/MalformedResourceException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureInfo.java

## Purpose
Request-scoped holder for parsed signature metadata used by authorization and string-to-sign creation.

## Important APIs, types, and functions
- Fields include version, date, dateTime, access ID, signature, signed headers, credential scope, algorithm, sign-payload flag, unfiltered URI, and string-to-sign.
- `initialize(SignatureInfo)` copies another instance, supporting injection/proxy patterns.
- `Version` enum has `NONE`, `V4`, and `V2`.
- Builder constructs immutable-style instances, though the outer object remains mutable for URI/string-to-sign.

## Control flow
Parsers build a `SignatureInfo`; `AWSSignatureProcessor` fills unfiltered URI; authorization code may create and store string-to-sign.

## State and persistence behavior
Request-scoped in-memory state. No persistence.

## Dependencies and integration points
Consumed by `StringToSignProducer`, authorization filters, root endpoint S3 Express detection, and endpoint logic that needs `isSignPayload`.

## Risks and edge cases
Default builder field values are empty strings, which can mask missing values until later validation. Mutability via `setUnfilteredURI` and `setStrToSign` means request scope must be respected.

## Test signals
Tests should assert parser-populated fields, request-scope copying through `initialize`, sign-payload differences between header and query signatures, and S3 Express credential-scope visibility.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureParser.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureParser.java

## Purpose
Small parser contract for extracting signature information from one authorization mechanism.

## Important APIs, types, and functions
- Constant `AUTHORIZATION_HEADER`.
- `parseSignature` returns `SignatureInfo`, null for nonmatching auth style, or throws `MalformedResourceException` for malformed recognized input.

## Control flow
`AWSSignatureProcessor` calls multiple implementations in priority order using the null-versus-exception distinction.

## State and persistence behavior
Interface only; no state or persistence.

## Dependencies and integration points
Implemented by V2 header, V4 header, and V4 query parsers.

## Risks and edge cases
Implementations must return null only when the auth style is absent, not when it is present but invalid, or malformed credentials may fall through to weaker/other auth modes.

## Test signals
Processor tests should ensure each parser obeys null and exception semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureProcessor.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureProcessor.java

## Purpose
Top-level contract for request signature processing plus shared signature constants.

## Important APIs, types, and functions
- Constants include content-type/content-md5 names, AWS4 signing algorithm, host header, and SigV4 date formatter.
- `parseSignature` returns a `SignatureInfo` or throws `OS3Exception`.

## Control flow
Implemented by `AWSSignatureProcessor`, which provides the request-scoped parser orchestration.

## State and persistence behavior
Interface only; no state or persistence.

## Dependencies and integration points
Used by authorization filters and signature parser classes for shared constants.

## Risks and edge cases
Changing constants affects all signature parsing and canonical request generation. Date formatter must remain `yyyyMMdd` for credential scopes.

## Test signals
Signature parser tests indirectly pin these constants through valid AWS examples.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/SignatureProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/StringToSignProducer.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/StringToSignProducer.java

## Purpose
Utility for building SigV4 canonical requests and strings-to-sign for Ozone S3 authorization.

## Important APIs, types, and functions
- `createSignatureBase` builds the SigV4 string-to-sign from `SignatureInfo`, request method, URI, headers, and query parameters.
- `buildCanonicalRequest` canonicalizes URI, query string, signed headers, and payload hash.
- `hash` computes SHA-256 hex.
- `fromMultiValueToSingleValueMap` converts query params to first-value map.
- `validateSignedHeader` checks host/date/content-sha headers.
- `validateCanonicalHeaders` requires host and all `x-amz-*` headers except `x-amz-content-sha256` to be signed.

## Control flow
The string-to-sign is algorithm, request timestamp, credential scope, and hash of canonical request. Canonical request encodes each URI path segment, sorts query parameters except `X-Amz-Signature`, renders signed headers in supplied order, validates signed header presence and timestamp range, and uses `UNSIGNED-PAYLOAD` for presigned requests or the `x-amz-content-sha256` header for signed-payload requests.

## State and persistence behavior
Stateless utility. No persistence.

## Dependencies and integration points
Used by the authorization filter after signature parsing. Depends on `SignatureInfo`, lowercased header maps, `S3Utils.urlEncode`, `S3Consts` payload constants, and S3 auth error creation.

## Risks and edge cases
Canonicalization is security-sensitive. Query parameters are single-valued, header whitespace is not normalized beyond stored values, and signed headers are used in caller-provided order. Missing host or unsigned `x-amz-*` headers fail auth. V4 header signing requires `x-amz-content-sha256`; presigned URLs force unsigned payload.

## Test signals
Authorization tests should use AWS canonical examples, query sorting/encoding cases, path encoding with slash preservation, missing signed headers, timestamp range failures, unsigned payload, and streaming payload constants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/StringToSignProducer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/package-info.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/package-info.java

## Purpose
Package documentation for S3 authorization header and signature classes.

## Important APIs, types, and functions
- Declares the `org.apache.hadoop.ozone.s3.signature` package.
- Documents that the package contains Ozone S3 authorization header support.

## Control flow
No executable control flow.

## State and persistence behavior
No state or persistence.

## Dependencies and integration points
Applies to signature parsers, signature processors, credential parsing, and string-to-sign generation.

## Risks and edge cases
Documentation only.

## Test signals
No direct tests needed.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/signature/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/AuditUtils.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/AuditUtils.java

## Purpose
Shared helper for extracting audit parameters and client IP from JAX-RS request context.

## Important APIs, types, and functions
- `getAuditParameters` copies path and query parameters into a `Map<String, String>`.
- `getClientIpAddress` reads `ClientIpFilter.CLIENT_IP_HEADER`.

## Control flow
If context is non-null, path parameters and query parameters are iterated and their list values are stringified. Client IP lookup is a direct header read.

## State and persistence behavior
Stateless. Audit persistence happens in the audit logger, not here.

## Dependencies and integration points
Used by `AWSSignatureProcessor` for auth failure audit messages and likely by other S3 audit paths. Depends on `ContainerRequestContext` and `ClientIpFilter`.

## Risks and edge cases
Parameter values are stringified lists, not normalized scalars. Null context returns an empty parameter map but `getClientIpAddress` does not null-check context.

## Test signals
Audit tests should check path/query parameter capture, repeated query parameter formatting, and client IP header propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/AuditUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/ContinueToken.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/ContinueToken.java

## Purpose
Encodes and decodes continuation tokens for paginated bucket/key listing using last key and optional last directory.

## Important APIs, types, and functions
- Constructor requires non-null `lastKey` and stores non-empty `lastDir`.
- `encodeToString` serializes key length, key bytes, optional dir bytes, hex-encodes them, and appends a SHA-256 digest separated by `-`.
- `decodeFromString` verifies separator and digest, decodes the hex payload, and reconstructs key/dir.
- `equals`, `hashCode`, and `toString` support tests and diagnostics.

## Control flow
Decoding rejects missing separators, digest mismatches, and bad hex with `InvalidArgument`, customizing the message for incorrect token payloads.

## State and persistence behavior
Tokens are client-visible serialized state but not server-persisted. They carry enough state to resume listing after the last returned entry.

## Dependencies and integration points
Used by root directory bucket listing and list-object responses. Depends on Commons Codec Hex/DigestUtils and `S3ErrorTable`.

## Risks and edge cases
The digest is integrity protection, not a secret or signature. `hashCode` only uses `lastKey` while `equals` also uses `lastDir`. Decoding accepts any remaining bytes as `lastDir`, including empty string.

## Test signals
`TestContinueToken` covers round-trip, Unicode keys/dirs, null dirs, and invalid token errors. Pagination tests should verify decoded `lastKey` resumes iteration correctly.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/ContinueToken.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RFC1123Util.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RFC1123Util.java

## Purpose
Provides a stricter RFC 1123-style date formatter for S3 response headers, especially `Last-Modified`.

## Important APIs, types, and functions
- Static `FORMAT` is a `DateTimeFormatter`.
- Formatter uses English day/month abbreviations, two-digit day of month, four-digit year, optional seconds parsing, and Ozone time zone offset.

## Control flow
The formatter is built once in a static block using `DateTimeFormatterBuilder`.

## State and persistence behavior
Static immutable formatter only. No persistence.

## Dependencies and integration points
Used by `ObjectEndpoint.addLastModifiedDate` and tested by `TestRFC1123Util`. Depends on `OzoneConsts.OZONE_TIME_ZONE`.

## Risks and edge cases
The formatter emits numeric offset based on Ozone timezone rather than a literal `GMT` token. The two-digit day is intentional for Go client compatibility.

## Test signals
Tests should verify single-digit days are formatted with leading zero, month/day abbreviations, timezone suffix, and compatibility with S3 clients.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RFC1123Util.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeader.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeader.java

## Purpose
Simple value object holding parsed S3 byte range offsets and flags for full-read or invalid-range handling.

## Important APIs, types, and functions
- Fields are `startOffset`, `endOffset`, `readFull`, and `inValidRange`.
- Getters expose the parsed values.
- `toString` aids debug logging.

## Control flow
Constructed by `RangeHeaderParserUtil`; consumed by object GET and copy-part range handling.

## State and persistence behavior
In-memory parsed request state only. No persistence.

## Dependencies and integration points
Used by `ObjectEndpoint` and `RangeHeaderParserUtil`.

## Risks and edge cases
The flag name `inValidRange` means invalid range, but the spelling can be read as "in valid range". Consumers must check `isInValidRange` carefully.

## Test signals
Range parser tests should assert exact start/end/full/invalid values for normal, suffix, over-long, and malformed ranges.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeaderParserUtil.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeaderParserUtil.java

## Purpose
Parses S3 `Range` and copy-source range header values into `RangeHeader`.

## Important APIs, types, and functions
- `parseRangeHeader(String rangeHeaderVal, long length)` matches `S3Consts.RANGE_HEADER_MATCH_PATTERN`.
- Supports explicit `bytes=start-end`, open-ended `bytes=start-`, and suffix `bytes=-count` ranges.
- Marks malformed values as full reads and marks start/end beyond length as invalid when appropriate.

## Control flow
If regex matches, start/end groups are parsed. Missing start means suffix range. Missing end means through `length - 1`. Starts beyond length can become invalid if end is also beyond length, otherwise the parser falls back to full read. Nonmatching headers become full-read responses rather than invalid errors.

## State and persistence behavior
Stateless parser. No persistence.

## Dependencies and integration points
Used by object GET and copy-part source range handling. Depends on `S3Consts.RANGE_HEADER_MATCH_PATTERN`.

## Risks and edge cases
Malformed range units such as `mb=...` become full reads instead of 416. Copy-part callers sometimes pass length `0`, so range semantics differ there. Numeric overflow can throw `NumberFormatException`.

## Test signals
`TestRangeHeaderParserUtil` covers normal ranges, single-byte ranges, invalid starts, unsupported units, suffix ranges, overlong suffixes, and large numeric values. Object GET tests should assert HTTP 206/416 behavior on top of parser output.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/RangeHeaderParserUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Consts.java -->
# sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Consts.java

## Purpose
Central constants for S3 gateway headers, query parameters, XML namespace, tagging limits, range parsing, copy directives, payload-signing markers, and S3 Express defaults.

## Important APIs, types, and functions
- Header constants include copy source/range, storage class, content SHA-256, custom metadata, tagging, bucket-owner conditions, checksum, and conditional request headers.
- Payload constants cover unsigned and streaming AWS4 payload marker values.
- Range constants include `RANGE_HEADER_MATCH_PATTERN` and 416 status value.
- Tag limits and regex define S3 tag validation policy.
- `CopyDirective` enum models `COPY` and `REPLACE`.
- `QueryParams` nests all S3 gateway query parameter names.

## Control flow
No executable logic beyond enum/static initialization. Consumers import constants to keep endpoints and utilities aligned.

## State and persistence behavior
Static immutable constants only. No persistence.

## Dependencies and integration points
Used throughout endpoint, signature, util, and exception code. Constants must align with AWS S3 wire names and Ozone endpoint query routing.

## Risks and edge cases
Changing a constant changes public API compatibility. Header casing matters where JAX-RS lookups are case-insensitive in practice but code may compare literal strings. Tag regex and limits define the accepted client surface.

## Test signals
Tests should indirectly pin constants through API behavior: copy directives, conditional headers, tagging validation, range parsing, S3 Express listing, and signature payload modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/s3gateway/src/main/java/org/apache/hadoop/ozone/s3/util/S3Consts.java -->
