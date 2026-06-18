# Research: subset-b-000488

This grouped report covers the Alluxio S3 proxy authentication/logging utilities, proxy tests, worker process/web surfaces, worker REST API, and selected block-worker synchronization primitives. Each section is source-tree aligned and can be split directly into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestUtils.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestUtils.java

Purpose: `S3RestUtils` is the shared utility layer for Alluxio's S3 REST path. It normalizes bucket paths, wraps endpoint execution into S3 XML/error responses, maps Alluxio exceptions to S3 errors, manages multipart metadata paths, parses headers/query maps, serializes xattrs for content type/tags/ETag, creates per-user file-system views, extracts S3 users from authorization data, and creates optional read rate limiters.

Important APIs include `call`, `toBucketS3Exception`, `toObjectS3Exception`, `checkPathIsAlluxioDirectory`, `checkStatusesForUploadId`, `deleteExistObject`, `getUser`, `getUserFromAuthorization`, `populateContentTypeInXAttr`, `populateTaggingInXAttr`, `setEntityTag`, `getEntityTag`, and `URIStatusNameComparator`. Control flow in `call` first ensures `AuthenticatedClientUser` is initialized when Alluxio security is enabled, invokes a `RestCallable`, converts null/status/POJO results to JAX-RS responses, and funnels thrown exceptions through `S3ErrorResponse`. User extraction switches between pluggable signature authentication and legacy header parsing based on `S3_REST_AUTHENTICATION_ENABLED`.

State and persistence: this class writes metadata into Alluxio inode xattrs using `SetAttributePOptions` with `UNION_REPLACE`, checks multipart metadata consistency by comparing temp-directory file IDs with xattr-encoded upload IDs, and caches bucket-directory existence when a Guava cache is supplied. Dependencies include `FileSystem`, `URIStatus`, `S3Exception`, `TaggingData`, `AwsSignatureProcessor`, `Authenticator`, Jackson XML, protobuf `ByteString`, and Guava `RateLimiter`.

Integration points are broad: S3 handlers call these helpers for endpoint result wrapping, bucket/object error semantics, object overwrite deletion, request identity, metadata preservation, multipart validation, and throttling. Risks include simple authorization-header parsing that assumes v4 `Credential=.../...`, tag header parsing that does not URL-decode keys/values here, `URIStatusNameComparator` throwing on non-numeric part names, and runtime exceptions in multipart edge cases that are later mapped as internal errors. Test signals come from `S3RestServiceHandlerTest.userFromAuthorization`, XML request/response tests, tagging users elsewhere, and rate limiter tests through `createRateLimiter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/TaggingData.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/TaggingData.java

Purpose: `TaggingData` is the Jackson XML model for S3 bucket/object tagging payloads and the serialization format stored in object xattrs. It represents `<Tagging><TagSet><Tag><Key>...` documents while maintaining a transient map view for efficient lookup and mutation.

Important APIs/types are `deserialize(byte[])`, `serialize(TaggingData)`, `getTagMap`, `addTags`, `clear`, and private nested `TagSet`/`TagObject` XML POJOs. Control flow during construction or XML unmarshalling runs `setTagSet`, normalizes null tag sets to an empty `TagSet`, validates constraints, and repopulates the transient map from the XML list. `addTags` updates both list and map, overwriting duplicate keys only for programmatic additions; XML duplicates are rejected during validation.

State and persistence are XML bytes produced by a static `XmlMapper`, wrapped in protobuf `ByteString` by `serialize`, and later stored by `S3RestUtils.populateTaggingInXAttr` under the tagging xattr key. Validation depends on the static configuration snapshot `PROXY_S3_TAGGING_RESTRICTIONS_ENABLED`: when enabled it enforces at most 10 tags, key length <= 128, value length <= 256, and no duplicate keys. All validation failures are wrapped in `IllegalArgumentException` with an `S3Exception` cause to match Jersey/Jackson exception paths.

Dependencies include Alluxio configuration, `S3Exception`/`S3ErrorCode`, Jackson XML annotations, and protobuf. Integration is with Put/Get object and bucket tagging handlers via xattrs. Risks include the static restriction flag not reflecting runtime configuration changes, no character-set validation beyond length/duplicate rules, and `addTag` doing list scans for each inserted tag. Test signals are indirect through S3 handler tests and tag xattr flows; no direct test in this subset covers XML duplicate or length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/TaggingData.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/Authenticator.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/Authenticator.java

Purpose: `Authenticator` defines the S3 proxy's pluggable authentication boundary. It receives parsed AWS authentication material and decides whether a request should be accepted.

Important APIs are the `isAuthenticated(AwsAuthInfo)` method and nested `Factory.create(AlluxioConfiguration)`. The factory uses `CommonUtils.createNewClassInstance` with `PropertyKey.S3_REST_AUTHENTICATOR_CLASSNAME`, allowing deployments to swap in a custom implementation without changing S3 request parsing. Control flow is simple: `S3RestUtils.getUserFromSignature` constructs an `AwsSignatureProcessor`, obtains `AwsAuthInfo`, constructs an authenticator from configuration, and calls `isAuthenticated`; success returns the access ID as the Alluxio user.

State and persistence are absent in this interface. Its behavior is completely determined by the configured class and the provided `AwsAuthInfo`. Dependencies are Alluxio configuration, `PropertyKey`, `CommonUtils`, `AwsAuthInfo`, and `S3Exception`.

Integration points include the legacy Jersey S3 path and the newer servlet-based S3 path, both through `S3RestUtils.getUser` overloads. The main risk is operational: the default authenticator is permissive, so enabling `S3_REST_AUTHENTICATION_ENABLED` without changing `S3_REST_AUTHENTICATOR_CLASSNAME` parses signatures but does not validate secrets. Factory errors also surface at request time if the configured class is missing or incompatible. Test signals include `TestAWSV4Authenticator`, which demonstrates a custom implementation delegating to `AuthorizationV4Validator`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/Authenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/AwsAuthInfo.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/AwsAuthInfo.java

Purpose: `AwsAuthInfo` is a small immutable carrier for the values a configured S3 authenticator needs: access ID, string-to-sign, and request signature.

Important APIs are the constructor, `getStringTosSign`, `getSignature`, `getAccessID`, and `toString`. Control flow is data-only; instances are created by `AwsSignatureProcessor.getAuthInfo` after parsing either header or query authentication. For V4 requests, `mStringToSign` is computed by `StringToSignProducer`; for V2 requests it remains an empty string because only parsing is supported in this code path.

State and persistence are limited to final fields in memory. Dependencies are only Guava `MoreObjects` for diagnostic `toString`. Integration points include `Authenticator.isAuthenticated`, `PassAllAuthenticator`, and `AuthorizationV4Validator` consumers. Risks are mostly naming/API polish: `getStringTosSign` has a typo that is nevertheless part of the local API, and `toString` includes signature material, so logging it on authentication failure can expose sensitive request data. Test signals appear in `TestAWSV4Authenticator`, which constructs `AwsAuthInfo` manually and validates the signature with a dummy authenticator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/AwsAuthInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/PassAllAuthenticator.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/PassAllAuthenticator.java

Purpose: `PassAllAuthenticator` is the default `Authenticator` implementation and always accepts parsed authentication info. It provides compatibility for deployments that want S3 access IDs to map to Alluxio users without enforcing AWS secret validation.

Important API: `isAuthenticated(AwsAuthInfo)` returns `true` unconditionally. The class comment shows the intended pattern for stricter authenticators: call `AuthorizationV4Validator.validateRequest(authInfo.getStringTosSign(), authInfo.getSignature(), secret)`.

State and persistence are absent. Dependencies are only the `Authenticator` interface, `AwsAuthInfo`, and `S3Exception` in the method signature. Integration is through `Authenticator.Factory` when `S3_REST_AUTHENTICATOR_CLASSNAME` points to this class. Risk is direct and security-sensitive: when S3 REST authentication is enabled with this default, malformed requests may be rejected by parsers, but any syntactically valid credential/signature is accepted. Test signals are indirect; `TestAWSV4Authenticator` documents how a non-pass-all validator can be implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/auth/PassAllAuthenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/Logged.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/Logged.java

Purpose: `Logged` is a Jersey name-binding annotation used to attach request logging behavior to S3 proxy resources or methods.

Important API/type: the annotation is marked with `@NameBinding`, retained at runtime, and targets both types and methods. It has no members. Control flow is declarative: Jersey uses the annotation to bind `RequestLoggingFilter`, which is itself annotated with `@Logged`, to matching resources.

State and persistence are absent. Dependencies are JAX-RS name-binding and Java annotation metadata. Integration occurs through `ProxyWebServer`, which registers package scanning for `alluxio.proxy.s3.logging`, allowing Jersey to discover the filter. Risks are low, but because `RequestLoggingFilter` also has `@PreMatching`, behavior depends on Jersey provider binding semantics; annotating too broadly can increase log volume and expose authorization data. No direct tests in this subset assert binding behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/Logged.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/RequestLoggingFilter.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/RequestLoggingFilter.java

Purpose: `RequestLoggingFilter` is a Jersey `ContainerRequestFilter` for S3 proxy debugging. It logs method, URI, authorization header, media type, query parameters, path parameters, and, at debug level, all headers.

Important API: `filter(ContainerRequestContext)` builds a request string when info logging is enabled. It casts the context to Jersey's `ContainerRequest` to obtain the request URI, then chooses `LOG.debug` with full headers if debug is enabled, otherwise `LOG.info` with the shorter message. The filter is annotated with `@Provider`, `@PreMatching`, and `@Logged`.

State and persistence are absent except logs. Dependencies include Jersey server request classes, JAX-RS filter APIs, and SLF4J. Integration comes from proxy Jersey package registration in `ProxyWebServer`. Risks include logging the raw `Authorization` header and all headers in debug mode, which may expose credentials/signatures; the cast to `ContainerRequest` assumes Jersey's implementation; and high request volume can produce large logs. Test signals are absent in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/logging/RequestLoggingFilter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AuthorizationV4Validator.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AuthorizationV4Validator.java

Purpose: `AuthorizationV4Validator` verifies an AWS Signature Version 4 request by deriving the signing key from the string-to-sign credential scope and comparing the computed HMAC-SHA256 signature to the request signature.

Important APIs are `validateRequest(String strToSign, String signature, String userKey)` and private helpers `getSignedKey` and `sign`. Control flow extracts date, region, and service from line 3 of the string-to-sign (`date/region/service/aws4_request`), derives `kDate`, `kRegion`, `kService`, and `kSigning` using the AWS4 key schedule, signs the full string-to-sign, hex-encodes it, and compares it to the supplied signature.

State and persistence are absent. Dependencies include AWS SDK `SigningAlgorithm`, Kerby `Hex`, JCA `Mac`, and S3 authorization charset constants. Integration is expected from custom `Authenticator` implementations; `PassAllAuthenticator` documents this path, and `TestAWSV4Authenticator` uses it directly. Risks include strict dependence on string-to-sign line layout, no constant-time comparison, logging the derived signing key at info level, and no normalization of signature case. Test coverage validates one known signature/secret pair.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AuthorizationV4Validator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AwsCredential.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AwsCredential.java

Purpose: `AwsCredential` parses and stores the credential-scope portion of AWS Signature V4 authentication: access key ID, date, region, service, and terminal request marker.

Important APIs are `create`, getters, `createScope`, and `validateDateRange`. Control flow uses a regex to split credentials shaped like `access/yyyymmdd/region/service/aws4_request`, validates the date, then constructs the immutable credential object. Date validation parses with `S3Constants.DATE_FORMATTER` and only accepts dates from yesterday through tomorrow relative to local system date.

State and persistence are final in-memory fields only. Dependencies include `S3Exception`, `S3ErrorCode`, Java time, regex, and SLF4J. Integration points are `AwsAuthV4HeaderParserUtils` and `AwsAuthV4QueryParserUtils`; `StringToSignProducer` later uses `createScope` via `SignatureInfo`. Risks include a permissive regex (`aws\\S+`) that accepts nonstandard terminal strings beginning with `aws`, local-clock sensitivity, and `LocalDate.parse` exceptions escaping as runtime errors if the date has the wrong numeric shape but matches the regex. Test signals in `TestAuthorizationV4HeaderParser` rely on today's date to avoid the date range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AwsCredential.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AwsSignatureProcessor.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AwsSignatureProcessor.java

Purpose: `AwsSignatureProcessor` extracts AWS authentication information from either Jersey `ContainerRequestContext` or servlet `HttpServletRequest` and converts it into `AwsAuthInfo`.

Important APIs are two constructors, `parseSignature`, and `getAuthInfo`. Control flow reads Authorization, `x-amz-date`, and query parameters from the active request representation. It attempts V4 header parsing first, then V2 header parsing, then V4 query parsing. If parsing succeeds, `getAuthInfo` builds a V4 string-to-sign through `StringToSignProducer`; V2 returns an empty string-to-sign. It requires a non-empty access ID and wraps unexpected failures as internal S3 errors.

State is request-scoped through either `mContext` or `mServletRequest`; no persistence. Dependencies include parser utilities, `S3RestUtils.fromMultiValueToSingleValueMap`, `StringToSignProducer`, `SignatureInfo`, and `AwsAuthInfo`. Integration is via `S3RestUtils.getUserFromSignature` for both proxy architectures. Risks include taking only the first query parameter value in servlet mode, relying on case-insensitive map lookup for headers, accepting V2 parse results though the validator path is V4-oriented, and converting many non-S3 exceptions into internal errors. Test signals cover parser utilities more than this orchestration class directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/AwsSignatureProcessor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/SignatureInfo.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/SignatureInfo.java

Purpose: `SignatureInfo` is an immutable value object holding parsed AWS signature metadata before it is converted to `AwsAuthInfo`.

Important fields/APIs are `Version` (`V4`, `V2`), access ID, signature, credential date, full timestamp, signed headers, credential scope, algorithm, and `signPayload`. Getters expose every field. Control flow is absent; parser utilities construct this object, and `AwsSignatureProcessor`/`StringToSignProducer` consume it.

State and persistence are final in-memory values only. Dependencies are none beyond Java. Integration points include V2/V4 header parsers, V4 query parser, canonical string production, and authentication handoff. The `signPayload` flag distinguishes header-signed payloads from presigned URLs where payload is treated as unsigned. Risks include no internal validation, so downstream code must handle null/empty fields correctly; V2 instances intentionally have empty V4-specific fields. Tests validate selected getters in V2 and V4 parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/SignatureInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/StringToSignProducer.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/StringToSignProducer.java

Purpose: `StringToSignProducer` builds the AWS V4 canonical request and string-to-sign for header-authenticated and presigned S3 requests.

Important APIs are `createSignatureBase` overloads for Jersey and servlet requests, the lower-level `createSignatureBase(SignatureInfo, scheme, method, uri, headers, queryParams)`, `hash`, `buildCanonicalRequest`, and `validateSignedHeader`. Control flow normalizes empty paths to `/`, constructs `algorithm\ndatetime\ncredentialScope\nhash(canonicalRequest)`, and builds the canonical request from method, encoded URI, sorted query string without `X-Amz-Signature`, canonical signed headers, signed-header names, and either `UNSIGNED-PAYLOAD` or `x-amz-content-sha256`.

State and persistence are absent. Dependencies include `S3RestUtils`, request APIs, Kerby `Hex`, Java crypto, URL encoding, DNS/date validation, and S3 constants. Integration is central to `AwsSignatureProcessor.getAuthInfo` and downstream `AuthorizationV4Validator`. Risks include no trimming/collapsing of signed header whitespace, DNS lookup in host validation during request processing, local-clock timestamp validation allowing only one week around now, use of `Collectors.toMap` that would fail duplicate servlet parameters if not already grouped by servlet API, and only first parameter values being signed. Test coverage is indirect through authenticator and parser tests; no direct canonical-request vectors are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/StringToSignProducer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV2HeaderParserUtils.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV2HeaderParserUtils.java

Purpose: `AwsAuthV2HeaderParserUtils` parses legacy AWS Signature V2 Authorization headers of the form `AWS accessKey:signature`.

Important API: `parseSignature(String authHeader)` returns null when the header is absent or does not start with `AWS `, throws `AUTHORIZATION_HEADER_MALFORMED` for malformed V2-looking values, and returns a `SignatureInfo` with version `V2`, access key, signature, and empty V4 fields for valid values. Control flow splits first on a single space and then on `:`, rejecting blank access ID or signature.

State and persistence are absent. Dependencies are `SignatureInfo`, `S3Exception`, `S3ErrorCode`, and Apache `StringUtils`. Integration is the second parser attempted by `AwsSignatureProcessor`. Risks include `String.split(":")` rejecting signatures containing additional colons and no V2 canonical string production or secret validation in the local auth path. Test signals in `TestAuthorizationV2HeaderParser` cover a valid header and a nonmatching prefix returning null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV2HeaderParserUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV4HeaderParserUtils.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV4HeaderParserUtils.java

Purpose: `AwsAuthV4HeaderParserUtils` parses AWS Signature V4 Authorization headers and produces a `SignatureInfo` for canonical request generation.

Important functions are `parseSignature`, `parseSignedHeaders`, `encodeSignature`, `parseCredentials`, and `validateAlgorithm`. Control flow accepts only headers beginning with `AWS4`, locates the first space as the algorithm separator, splits the remaining fields into exactly three comma-separated parts, requires `AWS4-HMAC-SHA256`, parses `Credential=...` via `AwsCredential`, requires nonempty semicolon-tokenized signed headers, validates `Signature=` as nonempty hexadecimal, and returns a V4 `SignatureInfo` with payload signing enabled.

State and persistence are absent. Dependencies include `AwsCredential`, `SignatureInfo`, Apache hex decoding/string utils, S3 exception types, and logging. Integration is the first parser attempted by `AwsSignatureProcessor`. Risks include strict field count/order, current-date validation inherited from `AwsCredential`, no validation that signed header names are lowercase/sorted, and accepting any header that starts with `AWS4` until later algorithm validation. Test signals in `TestAuthorizationV4HeaderParser` cover a current-date valid header and a malformed header missing signed headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV4HeaderParserUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV4QueryParserUtils.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV4QueryParserUtils.java

Purpose: `AwsAuthV4QueryParserUtils` parses AWS V4 presigned URL query parameters into `SignatureInfo`.

Important APIs are `parseSignature(Map<String,String>)` and `validateDateAndExpires`. Control flow returns null if `X-Amz-Signature` is absent. Otherwise it validates expiration when `X-Amz-Expires` is present by parsing `X-Amz-Date`, adding the expiry seconds, and comparing with current time. It URL-decodes `X-Amz-Credential`, parses it through `AwsCredential`, and returns a V4 `SignatureInfo` using query-supplied algorithm, signed headers, date, credential scope, and signature with `signPayload=false`.

State and persistence are absent. Dependencies include S3 signature constants, `AwsCredential`, `SignatureInfo`, URL decoding, and Java time. Integration is the third parser attempted by `AwsSignatureProcessor`, and its `signPayload=false` drives `StringToSignProducer` to use `UNSIGNED-PAYLOAD`. Risks include missing explicit validation for required query keys besides signature/credential, `IllegalArgumentException` for expired URLs or bad expiry escaping as an internal error through some call paths, local-clock sensitivity, and no upper-bound enforcement for `X-Amz-Expires` here. No direct tests in this subset cover presigned URL parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/signature/utils/AwsAuthV4QueryParserUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/web/ProxyWebServer.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/web/ProxyWebServer.java

Purpose: `ProxyWebServer` wires the Alluxio proxy HTTP server, including S3 REST/Jersey or S3 servlet v2 routing, servlet context resources, audit logging, global S3 read rate limiting, and access logging.

Important APIs/types include constructor setup, nested `ProxyListener`, `createLightThreadPool`, `createHeavyThreadPool`, `stop`, and static `logAccess`. Control flow builds a Jersey `ResourceConfig` for `alluxio.proxy`, `alluxio.proxy.s3`, and logging packages, creates a shared `FileSystem`, optionally creates a global Guava `RateLimiter`, starts an async audit log writer and metric gauge, then installs either the newer `S3RequestServlet` path when `PROXY_S3_V2_VERSION_ENABLED` is true or the Jersey servlet plus multipart upload handler otherwise. V2 mode also installs Jetty `HttpChannel.Listener` access logging and configured light/heavy thread pools.

State and persistence include servlet-context attributes for proxy process, file system, stream cache, audit writer, rate limiter, and v2 executor pools. It owns and closes the file system/audit writer in `stop`. Dependencies include Jetty, Jersey, Alluxio metrics/config, `S3Handler`, `S3RequestServlet`, `StreamCache`, and `CompleteMultipartUploadHandler`.

Integration points are every proxy REST/S3 request, audit logs, metrics, and S3 task execution pools. Risks include duplicated access logging in Jersey path, thread-pool rejection behavior controlled only by bounded queues, audit writer always running even if audit logging is disabled at runtime, and sensitive headers emitted in debug access logs. Tests in this subset exercise `StreamCache`, rate limiting, S3 range/auth utilities, not server startup directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/web/ProxyWebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/StreamCacheTest.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/StreamCacheTest.java

Purpose: `StreamCacheTest` verifies the proxy stream cache used to hold open `FileInStream` and `FileOutStream` instances across REST calls.

Important tests are `operations`, `concurrentOperations`, `expiration`, and `size`. Control flow in `operations` adds mocked input/output streams, confirms typed retrieval rejects the wrong stream type, invalidates both streams, verifies repeated invalidation returns null, and verifies both streams are closed. `concurrentOperations` launches 200 threads performing put/get/invalidate cycles across input and output streams and expects final cache size 0. `expiration` uses a zero timeout and verifies streams are closed immediately. `size` checks size transitions.

State and persistence under test are in-memory stream IDs and cache invalidation/expiration side effects; there is no disk persistence. Dependencies include JUnit, Mockito, Alluxio stream classes, and `Constants.HOUR_MS`. Integration signal: `ProxyWebServer` injects a `StreamCache` into servlet context for proxy REST endpoints. Risks covered include type confusion, leaking streams, concurrency races, and expiry cleanup. Remaining gaps include no test for ID wraparound, exception thrown by close, or long-running scheduled eviction behavior beyond zero timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/StreamCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/RateLimitInputStreamTest.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/RateLimitInputStreamTest.java

Purpose: `RateLimitInputStreamTest` validates that S3 download throttling respects both per-stream and global `RateLimiter` limits while preserving bytes.

Important tests are `testSingleThreadRead`, `testMultiThreadReadWithBiggerGlobalRate`, and `testMultiThreadReadWithSmallerGlobalRate`. Setup creates a deterministic 1 MiB byte array from UUID bytes. Single-thread tests copy through `RateLimitInputStream` with two randomly chosen rates and assert elapsed time is at least `size / min(rate1, rate2)` and within one second over that estimate. Multi-thread tests share one global limiter across three streams and assert elapsed time follows `totalSize / min(globalRate, threadNum * perStreamRate)`.

State under test is in-memory stream read position and Guava limiter token consumption. Dependencies are Guava `RateLimiter`, Apache Commons IO, JUnit, executors, and byte streams. Integration signal: `ProxyWebServer` creates a global limiter and S3 handlers wrap reads with per-request/global limiters. Risks covered include global limiter sharing and byte corruption. Risks not fully covered include timing flakiness under overloaded CI, interruption behavior, close propagation, and reads smaller than the copy buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/RateLimitInputStreamTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RangeSpecTest.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RangeSpecTest.java

Purpose: `S3RangeSpecTest` verifies byte-range parsing behavior used by S3 object GET responses.

Important tests cover invalid ranges (`bytes=100`, reversed range, zero suffix), ranges beyond object size, normal inclusive ranges, prefix ranges (`bytes=100-`), and suffix ranges (`bytes=-200`). Control flow constructs range specs through `S3RangeSpec.Factory.create`, then checks `getLength(objectSize)` and `getOffset(objectSize)`. The expected behavior is inclusive end offsets, clipped ranges near EOF, and zero length/offset for unsatisfiable ranges.

State and persistence are absent; this is pure parser/math behavior. Dependencies are JUnit and the production `S3RangeSpec` class. Integration signal: S3 GET/HEAD handlers rely on this math for partial content and range-not-satisfiable behavior. Risks covered include off-by-one errors and suffix/prefix edge cases. Gaps include multiple ranges, whitespace, non-byte units, extremely large values, and explicit HTTP status/header behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RangeSpecTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RestServiceHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RestServiceHandlerTest.java

Purpose: `S3RestServiceHandlerTest` covers selected S3 REST utility and XML model behavior.

Important tests are `userFromAuthorization`, `testDeleteObjectReq`, and `testDeleteObjectResp`. `userFromAuthorization` verifies malformed authorization strings throw `S3Exception` and that `Credential=test/asd` extracts `test`. The XML tests use Jackson `XmlMapper` to deserialize and serialize delete-object request/result bodies, checking quiet mode, object count, deleted/error lists, and request round-trip equality.

State and persistence are absent; the tests exercise parsing and serialization only. Dependencies include Alluxio global configuration, Jackson XML, JUnit, and S3 delete request/result models. Integration signals include legacy non-authenticated user extraction in `S3RestUtils.getUserFromAuthorization` and multi-object delete REST payload compatibility. Risks covered are malformed credential headers and XML shape drift. Gaps include behavior under `AuthType.NOSASL`, v4 parser integration, object delete execution, and detailed delete response serialization equality for response objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/S3RestServiceHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAWSV4Authenticator.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAWSV4Authenticator.java

Purpose: `TestAWSV4Authenticator` demonstrates and validates a custom authenticator that performs real AWS V4 signature validation with a known secret.

Important types/APIs include nested `DummyAWSAuthenticator`, which implements `Authenticator.isAuthenticated` by calling `AuthorizationV4Validator.validateRequest`, and `testAuthenticator`, which supplies a fixed string-to-sign, signature, access ID, and secret. Control flow constructs `AwsAuthInfo`, invokes the dummy authenticator, and asserts true.

State and persistence are absent. Dependencies include `Authenticator`, `AwsAuthInfo`, `AuthorizationV4Validator`, `S3Exception`, and JUnit. Integration signal: this test documents the intended replacement for `PassAllAuthenticator` in secure deployments. Risks covered include HMAC key derivation and signature comparison for one vector. Gaps include negative signatures, malformed string-to-sign scopes, region/service variation, and complete request canonicalization through `StringToSignProducer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAWSV4Authenticator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV2HeaderParser.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV2HeaderParser.java

Purpose: `TestAuthorizationV2HeaderParser` validates the legacy AWS V2 authorization header parser.

Important tests are `testAuthHeaderV2` and `testIncorrectHeader`. The first parses `AWS accessKey:signature` and verifies access key and signature in the returned `SignatureInfo`. The second uses an incorrect prefix and expects a null parser result rather than an exception, allowing `AwsSignatureProcessor` to try the next parser.

State and persistence are absent. Dependencies are JUnit, `AwsAuthV2HeaderParserUtils`, `SignatureInfo`, and `S3Exception`. Integration signal: V2 parsing is part of `AwsSignatureProcessor`'s parser chain. Risks covered include valid splitting and nonmatching prefix behavior. Gaps include malformed V2-looking headers, blank access IDs/signatures, extra spaces, and signatures containing colons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV2HeaderParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV4HeaderParser.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV4HeaderParser.java

Purpose: `TestAuthorizationV4HeaderParser` validates selected AWS V4 Authorization header parser behavior.

Important tests are `testAuthHeaderV4` and `testIncorrectHeader`. Setup formats the current local date with `DATE_FORMATTER` because production `AwsCredential` rejects dates outside yesterday/tomorrow. The valid test constructs a V4 header, parses it, and checks access ID, credential date, signed headers, and signature. The malformed test omits `SignedHeaders` and expects an `AuthorizationHeaderMalformed` S3 error code.

State and persistence are absent. Dependencies are JUnit, Java time, S3 constants, parser utility, and `S3Exception`. Integration signal: these tests protect the first parser in `AwsSignatureProcessor`. Risks covered include current-date credential acceptance and missing-field rejection. Gaps include algorithm rejection, non-hex signatures, malformed credential scopes, date parse failures, query auth, and full string-to-sign generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/test/java/alluxio/proxy/s3/signature/TestAuthorizationV4HeaderParser.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/pom.xml -->
# sources/distributed-fs/alluxio/core/server/worker/pom.xml

Purpose: this Maven POM defines the `alluxio-core-server-worker` jar module, its dependencies, and REST API documentation generation for worker endpoints.

Important elements include parent `alluxio-core-server`, artifact ID, `jar` packaging, module description, local `build.path`, external dependencies for Guava, Commons IO/Lang, Dropwizard metrics, servlet, Jetty, Jersey, and Jackson JSON, plus internal dependencies on client FS, common, transport, server-common, and Fuse integration. Test dependencies include Hamcrest, common test jar, local UFS, and HDFS UFS. The build config adds `swagger-maven-plugin` pointing at `alluxio.worker.AlluxioWorkerRestServiceHandler` and generates worker REST docs under `generated/worker`.

State and persistence are build metadata only. Integration points are compilation/runtime classpaths for worker web, REST, storage, metrics, and UFS behavior. Risks include provided-scope JSON dependency assumptions, test-only UFS dependencies needed by reflection, and generated documentation drifting if REST annotations or paths change. Test signal is indirect: this module's tests and Swagger generation depend on the dependencies declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/underfs/WorkerUfsManager.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/underfs/WorkerUfsManager.java

Purpose: `WorkerUfsManager` is the worker-side `UfsManager` implementation that lazily discovers and caches mount-specific UFS clients from the master.

Important APIs are constructor, `get(long mountId)`, and `connectUfs`. Control flow first delegates `get` to `AbstractUfsManager`; on local miss it asks `FileSystemMasterClient.getUfsInfo`, validates URI/properties, adds the mount with global plus mount-specific configuration, then returns the cached client. `connectUfs` calls `UnderFileSystem.connectFromWorker` with the worker RPC connect host.

State and persistence include the inherited UFS client/mount cache and a closable `FileSystemMasterClient` registered with the manager closer. Dependencies are Alluxio client/master contexts, UFS abstractions, network address utilities, and status exceptions. Integration points are worker services needing UFS access, especially block/file workers. Risks include master unavailability causing `UnavailableException`, stale cached mount properties until manager recreation, and `Preconditions.checkState` for unknown mount IDs surfacing as unchecked failure. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/underfs/WorkerUfsManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/web/WorkerWebServer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/web/WorkerWebServer.java

Purpose: `WorkerWebServer` hosts worker REST endpoints and, when enabled, worker web UI static assets.

Important APIs are the constructor and `stop`. Control flow creates a Jersey `ResourceConfig` scanning `alluxio.worker` and `alluxio.worker.block`, registers protobuf object mapping, creates a file-system client, and installs servlet-context references to the `WorkerProcess` and file-system client. It binds the REST servlet under `Constants.REST_API_PREFIX/*`. If `WEB_UI_ENABLED` is true, it serves `WEB_RESOURCES/worker/build`, sets `index.html` as welcome file, installs a default servlet, and maps 404s to `/` to support client-side routing.

State and persistence include the owned `FileSystem` client and servlet context attributes. Dependencies include Jetty, Jersey, Alluxio configuration, `BlockWorker`, and web utilities. Integration points are `AlluxioWorkerProcess` construction and `AlluxioWorkerRestServiceHandler`, which reads these context attributes. Risks include malformed resource path logging but not failing startup, static UI disabled by config, and REST construction requiring a non-null block worker. No direct tests in this subset cover server startup or UI fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/web/WorkerWebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorker.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorker.java

Purpose: `AlluxioWorker` is the worker process entry point.

Important API: `main(String[] args)`. Control flow rejects command-line arguments, verifies that a master host is configured, marks the process type as worker, creates a `MasterInquireClient`, loads cluster default configuration from the primary master with worker-scoped retry, creates a `WorkerProcess`, registers shutdown handling, and runs the process through `ProcessUtils`.

State and persistence include process-wide `CommonUtils.PROCESS_TYPE` and global configuration loaded from master. Dependencies include configuration utilities, retry utilities, master inquiry, server user state, and process utilities. Integration points are deployment scripts and the `WorkerProcess.Factory`, which returns `AlluxioWorkerProcess`. Risks include fatal exit on missing master/default configuration failure, startup coupling to primary master availability, and broad `Throwable` handling around process creation. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorkerProcess.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorkerProcess.java

Purpose: `AlluxioWorkerProcess` composes and manages the worker's UFS manager, worker registry, web server, data server, optional domain socket server, metrics sinks, JVM pause monitor, lifecycle, and network identity.

Important APIs include constructor, `start`, `stop`, `waitForReady`, address getters, `getWorker`, and `getAddress`. Construction records start time, creates `WorkerUfsManager` and `WorkerRegistry`, loads `WorkerFactory` implementations via `ServiceLoader` under a startup timeout, creates `WorkerWebServer`, resolves RPC bind/connect addresses including port-0 autobind, creates `GrpcDataServer`, and optionally creates a domain-socket `GrpcDataServer` with full file permissions. Start order is metrics sinks, workers, web server, JVM monitor, then blocking data-server termination. Stop closes data/domain servers, UFS manager, web server, metrics, JVM monitor, and workers.

State and persistence include server sockets, network addresses, registry contents, UFS manager cache, metrics sinks, and optional domain socket path. Dependencies include Netty channel detection, `GrpcDataServer`, `WorkerWebServer`, `BlockWorker`, configuration, metrics, and `JvmPauseMonitor`. Integration points are the main worker entry point, REST/web server, block worker registration, and clients using `WorkerNetAddress`. Risks include constructor wrapping all failures as `RuntimeException`, domain socket permission broadening, sensitive lifecycle ordering, and `start` blocking on data server. No direct tests here, but `waitForReady` is designed for tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorkerProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorkerRestServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorkerRestServiceHandler.java

Purpose: `AlluxioWorkerRestServiceHandler` implements worker REST and web-UI JSON endpoints for service info, operations, overview, block info, metrics, logs, configuration, and runtime log-level changes.

Important APIs are JAX-RS endpoints under `/worker`: `info`, `operations`, `webui_init`, `webui_overview`, `webui_blockinfo`, `webui_metrics`, `webui_logs`, `webui_config`, and POST `logLevel`. Construction pulls `WorkerProcess` and `FileSystem` from servlet context, casts the block worker to `DefaultBlockWorker`, and snapshots `BlockStoreMeta`. Control flow wraps endpoint bodies in `RestUtils.call`. Info returns capacity/config/metrics/tier paths/version. Operations reads active operation and RPC queue metrics. Overview summarizes store tiers/dirs. Block info optionally resolves a requested path, then pages file IDs derived from block IDs. Logs either lists log files matching Alluxio's log pattern or reads up to 5 KiB from a sanitized filename. Config returns whitelist and cluster/path configuration data.

State and persistence are read-only views of worker process, block store metadata, metrics registry, local log files, and cluster configuration; `logLevel` mutates runtime logger configuration. Dependencies are broad: worker/block classes, web UI wire DTOs, metrics, configuration, filesystem client, REST utilities, and log utilities. Risks include stale `mStoreMeta` for helper methods, unchecked casts to `DefaultBlockWorker`, pagination edge cases, null gauges causing logged fallback, and log-file exposure limited to filename sanitization and log-pattern listing. No direct tests in this subset exercise these endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/AlluxioWorkerRestServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/DataServer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/DataServer.java

Purpose: `DataServer` defines the minimal lifecycle and address contract for a worker data protocol server.

Important APIs are `getBindAddress`, `isClosed`, `awaitTermination`, and inherited `Closeable.close`. Implementations may bind either an `InetSocketAddress` or Netty `DomainSocketAddress`, as documented by `getBindAddress`. Control flow is implementation-specific; `AlluxioWorkerProcess` uses it to expose data host/port, optional domain socket path, block on server termination during `start`, and close servers during shutdown.

State and persistence are implementation-owned network server resources. Dependencies are Java networking and closeable APIs. Integration points include `GrpcDataServer` and worker lifecycle code. Risks include callers casting bind addresses based on which server is being queried; misuse can cause `ClassCastException`. No direct tests in this subset cover the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/DataServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/SessionCleaner.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/SessionCleaner.java

Purpose: `SessionCleaner` periodically removes timed-out worker sessions and asks registered components to clean their per-session state.

Important APIs are constructor, `run`, and `close`. Control flow tracks `lastCheckMs`, sleeps until `WORKER_BLOCK_HEARTBEAT_INTERVAL_MS` has elapsed, warns if cleanup took longer than the interval, obtains timed-out sessions from `Sessions`, removes each session, and calls `cleanupSession` on each `SessionCleanable`. `close` flips a volatile running flag so the loop exits after wakeup.

State and persistence include the `Sessions` object, a list of cleanable callbacks, check interval, and running flag. Dependencies are Alluxio `Sessions`, configuration, sleep utilities, and `SessionCleanable`. Integration points include block lock cleanup and other worker components with session-scoped resources. Risks include close not interrupting sleep by itself, cleanup callback exceptions escaping the loop, and interval coupling to block heartbeat configuration. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/SessionCleaner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/WorkerProcess.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/WorkerProcess.java

Purpose: `WorkerProcess` defines the public process contract for an Alluxio worker and a factory for constructing the default implementation.

Important APIs include `Factory.create`, `Factory.create(TieredIdentity)`, address getters, UFS manager access, start-time/uptime getters, typed `getWorker`, and inherited `Process` lifecycle methods. Control flow in the factory builds a local tiered identity from global configuration and returns `AlluxioWorkerProcess`.

State and persistence are implementation-defined; the interface exposes worker network identity, data/web ports, optional domain socket path, and registered worker services. Dependencies include Alluxio `Process`, configuration, tiered identity factory, UFS manager, and wire network address. Integration points are `AlluxioWorker`, `WorkerWebServer`, tests, and other server components that need to inspect or control the worker. Risks are mainly contract assumptions: some getters are documented as unit-test-only, and `getWorker` returns null or implementation-specific instances depending on registry contents. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/WorkerProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AbstractBlockStoreEventListener.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AbstractBlockStoreEventListener.java

Purpose: `AbstractBlockStoreEventListener` is a convenience base class for block-store event listeners that only care about a subset of events.

Important APIs are no-op implementations of every `BlockStoreEventListener` callback: access, abort, commit to local/master, move by client/worker, remove by client/worker/general, block lost, and storage lost by tier/path or location. Control flow is intentionally empty; subclasses override only relevant methods.

State and persistence are absent. Dependencies are the block store listener interface and block location types. Integration points include `BlockHeartbeatReporter`, which extends this class and overrides movement/removal/loss callbacks. Risks are low, but missed overrides silently drop events, so listener implementations must be reviewed against required reporting semantics. No direct tests in this subset cover the base class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AbstractBlockStoreEventListener.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AllMasterRegistrationBlockWorker.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AllMasterRegistrationBlockWorker.java

Purpose: `AllMasterRegistrationBlockWorker` is a `DefaultBlockWorker` variant that registers and syncs with all masters instead of only the primary.

Important APIs are constructor, `setupBlockMasterSync`, `start`, and `getBlockSyncMasterGroup`. Control flow delegates most setup to `DefaultBlockWorker`. `setupBlockMasterSync` creates an all-master `BlockSyncMasterGroup`, registers it for close, and starts it on the worker executor service. `start` calls `super.start(address)`, then waits for registration to complete on the primary master address obtained from the file-system master client; standby registration does not block worker startup.

State and persistence include the owned `BlockSyncMasterGroup` and inherited block worker state. Dependencies include `BlockMasterClientPool`, `FileSystemMasterClient`, `Sessions`, `BlockStore`, worker ID reference, and master sync group. Integration points are HA deployments with `WORKER_REGISTER_TO_ALL_MASTERS`. Risks include primary-address cast assumptions and startup waiting only on the primary, leaving standby convergence asynchronous. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AllMasterRegistrationBlockWorker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AsyncBlockRemover.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AsyncBlockRemover.java

Purpose: `AsyncBlockRemover` performs best-effort block deletion in response to master commands without blocking heartbeat handling on all removals.

Important APIs are constructors, `addBlocksToDelete`, `shutDown`, and inner `BlockRemover.run`. Control flow creates a fixed daemon thread pool, starts remover workers, de-duplicates queued/removing block IDs with a concurrent set, and pushes IDs into a blocking queue. Each remover takes a block ID, increments try/remove metrics, calls `BlockWorker.removeBlock` using `MASTER_COMMAND_SESSION_ID`, logs failures as retry-later best effort, and removes the ID from the in-progress set in `finally`. Shutdown sets a flag and interrupts the pool.

State and persistence are in-memory queue/set plus metrics counters/gauges. Dependencies include `BlockWorker`, `Sessions`, metrics system, Java concurrency, and test-visible constructor injection. Integration point is `BlockMasterSync.handleMasterCommand` for `Free` commands. Risks include blocks being dropped from `mRemovingBlocks` after failed removal without automatic requeue, unbounded queue growth, and duplicate check race between `contains` and `add`. No direct tests in this subset are listed, but metrics and visible constructor support targeted tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/AsyncBlockRemover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockHeartbeatReporter.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockHeartbeatReporter.java

Purpose: `BlockHeartbeatReporter` records block-store deltas between worker heartbeats so the block master can be told about removed blocks, moved/added blocks, and lost storage.

Important APIs are `generateReportAndClear`, `clear`, `mergeBack`, and overridden event callbacks for moves, removals, block loss, and storage loss. Control flow stores events under `mLock`. Moves remove the block from any added list and add it at the new location. Removals/loss remove the block from added lists and append to removed blocks if not already present. `generateReportAndClear` hands the current collections to `BlockHeartbeatReport` and clears the reporter. `mergeBack` restores a failed report while avoiding re-adding blocks already removed after the failed report was generated.

State and persistence are in-memory lists/maps cleared on report generation; no disk persistence. Dependencies include block store locations, `BlockHeartbeatReport`, configuration, and Guava list helpers. Integration points include block-store event listeners and `BlockMasterSync` heartbeats. Risks include O(n) duplicate scans/removals for large deltas, report object sharing the same collection instances unless `BlockHeartbeatReport` copies defensively, and the unused `mWorkerRegisterToAllMasters` field indicating drift. Tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockHeartbeatReporter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockLockManager.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockLockManager.java

Purpose: `BlockLockManager` manages per-block read/write locks, lock IDs, lock records, lock pooling, and session cleanup for the worker block store.

Important APIs are `acquireBlockLock`, `tryAcquireBlockLock`, `checkLock`, `cleanupSession`, `getLockedBlocks`, and `validate`. Control flow obtains or creates a `ClientRWLock` from a bounded `ResourcePool`, increments reference counts, acquires the requested read/write lock, creates a unique lock record, and uses a semaphore to prevent new records while session cleanup removes all records for a session. Unlock removes the lock record by lock ID, unlocks the underlying lock, drops the block-lock reference, and returns unused locks to the pool. Write locking rejects attempts by a session already holding any lock on the same block to avoid self-deadlock.

State and persistence are in-memory concurrent maps, an indexed lock-record set, static lock ID generator, pooled locks, and session cleanup semaphore. Dependencies include `ClientRWLock`, `ResourcePool`, `IndexedSet`, `BlockLockType`, and configuration keys for lock counts/readers. Integration points include block read/write/move/remove paths and `SessionCleaner`. Risks include best-effort race noted in the self-lock check, `validate` assuming every `mLocks` entry has a count record and potentially NPE otherwise, indefinite waiting for pooled locks in blocking mode, and stale snapshots from `getLockedBlocks`. No direct tests in this subset, but several methods are test-visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockLockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockLockType.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockLockType.java

Purpose: `BlockLockType` enumerates block lock modes for `BlockLockManager`.

Important API: enum values `READ(0)` and `WRITE(1)` plus `getValue`. Control flow is absent; callers choose the enum to acquire either a read lock or write lock on a block.

State and persistence are enum constants with integer values. Dependencies are only Java enum support and thread-safety annotation. Integration points are block store operations that call `BlockLockManager.acquireBlockLock` or `tryAcquireBlockLock`. Risks are low; the numeric values are not self-validating and should only be used where the local protocol expects them. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockLockType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMapIterator.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMapIterator.java

Purpose: `BlockMapIterator` batches worker block-location maps into gRPC `LocationBlockIdListEntry` groups for streamed worker registration.

Important APIs are constructor, `hasNext`, `next`, and `getBatchCount`. Control flow first merges directory-level `BlockStoreLocation` entries into tier/medium-level `BlockStoreLocationProto` lists because the master expects blocks grouped by tier and medium. Iteration tracks current tier index and global block counter, returning up to `WORKER_REGISTER_STREAM_BATCH_SIZE` block IDs per call, possibly spanning multiple tiers. `getBatchCount` computes total batches from merged block count and batch size.

State and persistence are iterator state over copied/merged block ID lists; no persistence. Dependencies include Alluxio configuration, gRPC block list protos, and block store locations. Integration points include `RegisterStreamer` used by `BlockMasterClient.registerWithStream`. Risks include `hasNext` returning true when `mCurrentBlockLocationIndex == size` because of `||` logic if the current iterator is exhausted, potential empty `LocationBlockIdListEntry` if called in edge cases, and memory copy cost for large block maps. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMapIterator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterClient.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterClient.java

Purpose: `BlockMasterClient` is the worker-side wrapper around the block-master worker gRPC service. It handles commit, heartbeat, registration, registration leases, worker ID acquisition, and all-master worker ID notifications.

Important APIs include constructors for primary or specified master, `commitBlock`, `commitBlockInUfs`, `getId`, `convertBlockListMapToProto`, `heartbeat`, `acquireRegisterLeaseWithBackoff`, `register`, `registerWithStream`, and `notifyWorkerId`. Control flow initializes blocking/async stubs after connection. Commit and ID methods build protobuf requests and call `retryRPC`. Heartbeat converts added/lost block maps into protobuf entries, attaches metrics/capacity/usage/removals, applies a deadline from cluster config, and returns the master's command. Registration builds `RegisterWorkerPRequest` with storage tiers, capacity, current blocks, lost storage, worker config, build version, and CPU count, or delegates streaming to `RegisterStreamer`. Lease acquisition polls `requestRegisterLease` under a caller-supplied retry policy.

State and persistence include gRPC channel stubs inherited from `AbstractMasterClient`; no local durable state. Dependencies are generated gRPC/protobuf classes, master client context/selection, retry policies, worker net address conversion, and block store location models. Integration points are `BlockMasterSync`, `BlockMasterClientPool`, registration streaming, and block worker commit paths. Risks include synchronized heartbeat serializing calls, merging block lists by tier/medium and discarding directory granularity, async stream errors captured through `AtomicReference`, and lease retry exhaustion preventing startup. No direct tests in this subset, but `convertBlockListMapToProto` is visible for testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterClientPool.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterClientPool.java

Purpose: `BlockMasterClientPool` is a bounded resource pool of `BlockMasterClient` instances for worker-to-master communication.

Important APIs are constructors, `createNewResource`, and `close`. Control flow creates a `MasterClientContext` from global configuration and optional specified master address. New resources connect either to the primary master selection policy or the specified address, add the client to a concurrent queue for later close, and return it to the pool. `close` drains all ever-created clients from the queue into a Guava `Closer`.

State and persistence are in-memory pooled clients and the queue of clients to close. Dependencies include `ResourcePool`, `MasterClientContext`, `ClientContext`, optional `InetSocketAddress`, and Guava `Closer`. Integration points include `BlockMasterSync` and all-master registration code that needs clients to primary or standby masters. Risks include the close queue tracking created clients independently of current pool ownership, so callers must still release acquired clients; pool sizing is entirely configuration-driven. No direct tests in this subset, but a visible `Factory` supports testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterClientPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterSync.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterSync.java

Purpose: `BlockMasterSync` is the heartbeat executor that registers a block worker with the master and continuously sends worker block/capacity/metric updates while handling master commands.

Important APIs are constructor, `heartbeat`, `close`, and private `registerWithMaster`/`handleMasterCommand`. Construction acquires a master client from the pool, creates `AsyncBlockRemover` and `BlockMasterSyncHelper`, acquires an optional registration lease, registers the full block store, and records last successful heartbeat time. Each heartbeat sends the worker's report and store metadata through the helper; failures update timeout logic and can fatal-exit outside test mode. Master commands trigger async free, re-registration with a new worker ID, no-op, decommission logging, or error logging.

State and persistence include references to block worker, worker ID, worker address, master client/pool, async remover, helper, and last heartbeat timestamp. Dependencies include heartbeat executor, process utilities, configuration timeouts, `Command`, and sampling logger. Integration points are worker block service startup and periodic heartbeat scheduling. Risks include fatal process exit on registration lease or heartbeat timeout, best-effort async free semantics, re-registration changing worker ID, and retained master client until close. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterSyncHelper.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterSyncHelper.java

Purpose: `BlockMasterSyncHelper` contains retry, registration, and heartbeat helper logic around a `BlockMasterClient`.

Important APIs are constructor, `getDefaultAcquireLeaseRetryPolicy`, `tryAcquireLease`, `registerToMaster`, and `heartbeat`. Control flow builds an exponential time-bounded retry policy from worker register lease configuration. `tryAcquireLease` only contacts the master when `WORKER_REGISTER_LEASE_ENABLED` is true. `registerToMaster` collects worker-scope configuration, then chooses streaming or unary registration based on `WORKER_REGISTER_STREAM_ENABLED`. `heartbeat` reports worker metrics plus block/capacity deltas, invokes the supplied command handler, returns true on success, and logs/disconnects the client on any failure.

State and persistence are limited to the master client reference. Dependencies include configuration, retry utilities, gRPC `Command`/`ConfigProperty`, metrics reporting, and block-store metadata/report types. Integration points are `BlockMasterSync` and registration/heartbeat error handling. Risks include catching all exceptions in heartbeat and reducing them to false, disconnecting the client but relying on retry/reconnect behavior later, and registration mode changes affecting memory/stream behavior. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterSyncHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataAllocatorView.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataAllocatorView.java

Purpose: `BlockMetadataAllocatorView` exposes a narrowed metadata view for block allocation decisions.

Important APIs are constructor and `initializeView`. Control flow delegates common view setup to `BlockMetadataView` through the constructor, then `initializeView` iterates all storage tiers from the metadata manager, creates `StorageTierAllocatorView` for each tier with the configured reserved-space behavior, appends it to `mTierViews`, and indexes it by tier alias.

State and persistence are in-memory view objects over `BlockMetadataManager`; no durable state. Dependencies include block metadata manager/view base classes, storage tier metadata, and allocator-specific tier view classes. Integration points are block allocators that need read-only tier/dir capacity information while placing blocks. Risks are low but view freshness depends on when callers initialize/rebuild it, and reserved-space inclusion changes allocator-visible capacity. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataAllocatorView.java -->
