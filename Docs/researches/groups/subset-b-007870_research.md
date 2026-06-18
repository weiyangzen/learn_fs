# subset-b-007870 Research

Grouped research for SeaweedFS S3 API files. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_v4_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_v4_test.go

Purpose: regression tests for STS-aware SigV4 authorization paths. The file does not implement request authorization, but documents the expected token extraction contract for `authorizeWithIAM` and the STS temporary credential generator.

Important APIs and fixtures: `TestAuthorizeWithIAMSessionTokenExtraction`, `TestSTSSessionTokenIntoCredentials`, and `TestActionConstantsForV4Auth`. The tests use `s3_constants.SeaweedFSSessionTokenHeader`, `SeaweedFSPrincipalHeader`, raw `X-Amz-Security-Token`, URL query parameters, and `sts.NewCredentialGenerator`.

Control flow and behavior signals: session token discovery must prefer SeaweedFS JWT headers, then fall back to `X-Amz-Security-Token` header, then presigned query token. Principal extraction is only expected for JWT-style requests. STS credential generation must emit non-empty access key, secret key, and session token, be deterministic for the same session ID, and differ for different sessions.

State and persistence: test state is in-memory only. It validates deterministic credential derivation from session ID and expiry, not any persisted credential store.

Dependencies and integration points: integrates S3 auth constants, IAM STS credential generation, and action constants used by authorization checks. These tests protect S3, IAM, and presigned URL interoperability.

Risks: if `authorizeWithIAM` changes token precedence, temporary STS credentials may fail under SigV4 despite valid signatures. Missing `X-Amz-Security-Token` query extraction breaks presigned STS URLs. Test signals are focused on extraction logic and constants rather than full end-to-end authorization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auth_sts_v4_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auto_signature_v4_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/auto_signature_v4_test.go

Purpose: broad regression suite for S3/IAM/STS Signature V4 authentication helpers, canonical request construction, proxy header handling, presigned URLs, payload hashing, and streaming-body limits.

Important APIs and helpers: tests cover `isRequestPresignedSignatureV4`, `reqSignatureV4Verify`, `authRequest`, `doesSignatureMatch`, `doesPresignedSignatureMatch`, `extractHostHeader`, `getStringToSign`, `EncodePath`, `streamHashRequestBody`, and helpers `signRequestV4`, `signV4WithPath`, `preSignV4`, `preSignV4WithPath`, and `newTestIAM`.

Control flow signals: unsigned requests should be denied unless an anonymous identity permits the requested action. Header-signed and presigned requests build canonical requests from method, canonical URI, query, selected headers, signed header list, and payload hash. Reverse-proxy tests require `X-Forwarded-Prefix`, `X-Forwarded-Host`, `X-Forwarded-Port`, and `X-Forwarded-Proto` to reconstruct the externally signed host/path, preserving trailing slashes and normalizing default ports, including IPv6 forms. Presigned URLs must reject missing `X-Amz-Expires`.

State and persistence: IAM identities and credential maps are built in-memory. Body hashing preserves or truncates request bodies after reading so downstream handlers can still consume them.

Dependencies and integration points: depends on mux URL vars, IAM protobuf config loading, S3 constants, SigV4 helper functions in the auth implementation, and AWS canonicalization rules.

Risks: signature verification is highly sensitive to path cleaning, port normalization, service names, and payload hash source. The suite specifically guards GitHub issue #7080 by requiring IAM/STS service scopes, not hardcoded `s3`, and enforcing a 10 MiB body hash limit for DoS resistance. Benchmarks compare signing and streaming hash approaches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/auto_signature_v4_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata.go

Purpose: maintains cached S3 bucket metadata derived from filer bucket directory entries, including ownership controls, ACL grants, owner identity, and table-bucket classification.

Important APIs/types: `BucketMetaData`, `BucketRegistry`, `NewBucketRegistry`, `init`, `LoadBucketMetadata`, `buildBucketMetadata`, `RemoveBucketMetadata`, `GetBucketMetadata`, `LoadBucketMetadataFromFiler`, `setMetadataCache`, `removeMetadataCache`, and `unMarkNotFound`. `loadBucketMetadataFromFiler` is a package variable to allow testing and indirection.

Control flow: registry initialization lists `option.BucketsPath`, skips hidden names, loads metadata for each entry, and warms bucket config cache. `buildBucketMetadata` starts with bucket-owner-enforced object ownership and AccountAdmin owner defaults, then validates extended ownership, resolves owner account IDs through `AccountManager`, and unmarshals ACL grants. `GetBucketMetadata` checks the positive cache, then a negative not-found cache, then serializes filer loading under `notFoundLock` to avoid duplicate concurrent loads.

State and persistence: persistent state is stored in filer entry `Extended` metadata keys such as ownership, owner, ACL, and table-bucket markers. Runtime state is split between `metadataCache` and `notFound`, protected by separate RW mutexes.

Dependencies and integration points: uses `filer_pb.List`, `S3ApiServer.getBucketEntry`, bucket config cache updates, AWS `s3.Owner`/`s3.Grant`, `s3_constants`, `s3err`, and `s3tables`.

Risks: stale positive cache can misrepresent changed ACL/ownership until invalidated. Stale negative cache is cleared only on load/remove paths. Invalid extended metadata falls back silently with warnings, which preserves availability but can mask configuration drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata_test.go

Purpose: tests bucket metadata construction from filer entries and concurrent registry loading behavior.

Important APIs and fixtures: `BucketMetadataTestCase`, multiple filer entry fixtures with valid and invalid `Extended` metadata, `TestBuildBucketMetadata`, and `TestGetBucketMetadata`. The test overrides `loadBucketMetadataFromFiler` and uses `loadFilerBucket` to count loads.

Control flow signals: `TestBuildBucketMetadata` runs table-driven comparisons over malformed entries, valid ACL entries, empty ownership, valid ownership, empty owner, unknown owner, and empty grants. Expected defaults are AccountAdmin owner, default object ownership, and nil or empty ACL according to the input. `TestGetBucketMetadata` starts 40 goroutines repeatedly reading five bucket names; the overridden loader sleeps one second so duplicate load races are visible.

State and persistence: all state is in memory. The test deliberately mutates the package-level loader and global load-count map, so it is not safe to parallelize without isolation.

Dependencies and integration points: exercises `IdentityAccessManagement.loadS3ApiConfiguration`, `filer_pb.Entry`, AWS S3 grant/owner structs, S3 metadata constants, and `BucketRegistry.GetBucketMetadata`.

Risks and test signals: the concurrency test proves `notFoundLock` also serializes cache-miss loads. It does not restore the overridden loader, so later tests in the same package can be affected if they depend on the default loader. The expected owner fixture uses `AccountAdmin.DisplayName` as stored owner bytes, relying on IAM lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_metadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_paths.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/bucket_paths.go

Purpose: centralizes bucket path calculation, bucket existence lookup, and table-bucket object path validation for the S3 API.

Important APIs: `isTableBucket`, `bucketRoot`, `bucketDir`, `validateTableBucketObjectPath`, `bucketPrefix`, `bucketExists`, and `getBucketEntry`. The package-level `tableBucketFileValidator` is built from `s3tables.NewTableBucketFileValidator`.

Control flow: `isTableBucket` first checks `bucketRegistry.metadataCache`, then loads the bucket entry from the filer and refreshes registry metadata if possible. Lookup errors other than not-found are logged at low verbosity and treated as non-table. `bucketRoot` returns the unified `BucketsPath`; `bucketDir` and `bucketPrefix` append bucket names. `validateTableBucketObjectPath` is a no-op for ordinary buckets. For table buckets it trims leading slash, requires a non-empty object, validates the full path through the table bucket validator, and requires at least four path segments matching namespace/table/data-or-metadata style layout.

State and persistence: no direct persistence beyond `getEntry` reads and optional registry cache warming.

Dependencies and integration points: depends on `S3ApiServer.option.BucketsPath`, filer entries, bucket registry metadata, glog, and `s3tables.IcebergLayoutError`.

Risks: treating transient lookup errors as non-table can allow paths to bypass table-bucket validation during filer trouble. Validation combines full-path validator checks with a local segment-count check; changes to Iceberg table layout rules must stay aligned with `s3tables`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_paths.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics.go

Purpose: periodically collects per-bucket logical size, physical size, object counts, and quota state from master topology and filer bucket entries, then updates Prometheus metrics and bucket read-only quota enforcement.

Important APIs/types: `CollectionInfo`, `volumeKey`, `startBucketSizeMetricsLoop`, `collectAndUpdateBucketSizeMetrics`, `enforceBucketQuotas`, `collectCollectionInfoFromMaster`, `listBuckets`, `ecVolumeAgg`, and `collectCollectionInfoFromTopology`.

Control flow: the loop waits ten seconds, acquires a long-lived distributed lock named `s3.leader`, and runs once per minute only while locked. Collection pulls `VolumeList` topology from any master, lists bucket directories in pages of 1000, maps bucket names to collections, updates stats, and calls quota enforcement. Quota enforcement reads `filer.conf`, applies bucket quota read-only decisions per bucket prefix, updates quota metrics, and writes `filer.conf` only if a flag changed.

State and persistence: persistent writes occur only when quota enforcement saves `filer.conf` inside filer. Metrics state is external Prometheus gauge state. Collection aggregation is in-memory.

Dependencies and integration points: uses cluster lock client, master/filer protobuf clients, `filer.ReadFilerConfFromFilers`, `stats.UpdateBucketSizeMetrics`, `stats.UpdateBucketQuotaMetrics`, and erasure coding size helpers.

Risks: topology aggregation must dedupe replicated regular volumes by collection and volume ID while summing physical replicas. EC shards are node-local: physical includes all shards, logical includes data shards, file count uses max across reporters, delete count sums. Lock failure or missing filers disables collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics_test.go

Purpose: unit tests for topology aggregation of erasure-coded and mixed regular/EC volumes used by bucket size metrics and quota enforcement.

Important tests: `TestCollectCollectionInfoFromTopologyEC`, `TestCollectCollectionInfoFromTopologyMixed`, and `TestCollectCollectionInfoFromTopologyECFileCountMaxDedupe`.

Control flow signals: tests construct `master_pb.TopologyInfo` trees with data centers, racks, data nodes, disks, regular `VolumeInfos`, and `EcShardInfos`. The EC-only test models one 10+4 EC volume across two nodes, requiring physical size to sum all shards, logical size to sum data shards, file count to be max across shard reporters, delete count to be summed, and volume count to be one. The mixed test requires regular and EC data in the same collection to accumulate rather than overwrite. The slow `.ecx` test requires max file count to avoid a zero reporter pinning the result.

State and persistence: in-memory only; no master or filer clients are used.

Dependencies and integration points: exercises `collectCollectionInfoFromTopology`, `CollectionInfo`, and `master_pb` topology messages.

Risks and test signals: these tests guard a production-observable regression where converting a volume to EC made bucket metrics drop to zero. They focus on aggregation math, not the outer lock, gRPC fetch, bucket listing, Prometheus updates, or quota writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/bucket_size_metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/chunked_bug_reproduction_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/chunked_bug_reproduction_test.go

Purpose: narrow regression reproduction for GitHub issue #6847 involving AWS SDKs that send unsigned streaming headers but signed-looking chunk extensions.

Important APIs: `TestChunkedEncodingMixedFormat` and local `setupTestIAM`. The test drives `IdentityAccessManagement.newChunkedReader`.

Control flow signals: the request advertises `x-amz-content-sha256: STREAMING-UNSIGNED-PAYLOAD-TRAILER` and `x-amz-trailer: x-amz-checksum-crc32`, but the body chunks include `;chunk-signature=` extensions. The reader must parse the chunk framing, ignore signatures because there are no credentials/seed signature for unsigned streaming, validate the CRC32 trailer, and return only `hello world\n`.

State and persistence: no persistent state. The IAM object is intentionally empty to reproduce the nil-credential path.

Dependencies and integration points: integrates chunked reader state machine, S3 error codes, and checksum trailer parsing.

Risks and test signals: this protects against nil pointer dereferences and over-strict interpretation of mixed-format clients from newer AWS SDKs. It does not validate signed streaming, invalid checksum behavior, or full authorization; those are covered in the broader chunked reader tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/chunked_bug_reproduction_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4.go

Purpose: implements an AWS SigV4 `aws-chunked` decoding reader for signed streaming, unsigned streaming with trailers, checksum validation, and chunk signature chaining.

Important APIs/types: `calculateSeedSignature`, `newChunkedReader`, `extractChecksumAlgorithm`, `s3ChunkedReader`, `chunkState`, `Read`, `getChunkSignature`, `readCRLF`, `peekCRLF`, `readChunkLine`, `parseS3ChunkExtension`, `parseChunkChecksum`, `parseHexUint`, `ChecksumAlgorithm`, and `getCheckSumWriter`.

Control flow: `newChunkedReader` inspects `X-Amz-Content-Sha256`. Signed streaming modes verify the seed signature and retain credential, region, service, date, and seed signature. Unsigned streaming skips seed verification unless the request itself has SigV4 headers. The `Read` method is a state machine: read chunk header, read data while hashing, consume CRLF, optionally verify chunk signature, parse trailer checksum after the zero chunk, and return EOF. Last-chunk CRLF handling intentionally accepts clients that omit an optional final CRLF.

State and persistence: all state is per-reader: remaining chunk bytes, last signature, checksum hash, chunk SHA256 hash, trailer flag, and error. It does not persist metadata; callers receive a decoded body stream.

Dependencies and integration points: relies on IAM SigV4 verification helpers, `s3err`, glog, SHA/CRC hash implementations, and `crc64nvme`.

Risks: malformed chunk extensions can panic if `parseChunkSignature` receives an unexpected format after the marker. Trailer signatures are parsed as ordinary ignored trailer headers and not verified. Checksum mismatch and algorithm mismatch are surfaced as read errors after payload bytes may already have been streamed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4_test.go

Purpose: tests SigV4 chunked reader behavior for unsigned trailer uploads, signed chunk chains, checksum trailers, invalid chunk signatures, and service-scope handling.

Important helpers/tests: `setupIam`, `NewRequestStreamingUnsignedPayloadTrailer`, `generateStreamingUnsignedPayloadTrailerPayload`, `TestNewSignV4ChunkedReaderStreamingUnsignedPayloadTrailer`, `TestSignedStreamingUpload`, `createTrailerStreamingRequest`, `TestSignedStreamingUploadWithTrailer`, `TestSignedStreamingUploadWithTrailerInvalidSignature`, and `TestSignedStreamingUploadInvalidSignature`.

Control flow signals: unsigned trailer tests build AWS documentation-style chunked payloads with CRC32 trailer and both final-CRLF variants. Signed tests dynamically compute seed signatures, per-chunk signatures, and final zero-chunk signatures, then require `newChunkedReader` to return concatenated chunk data. Invalid chunk signature tests flip one signature byte and require a read error containing chunk signature mismatch. Trailer signature invalidity is currently permissive: content may still be returned unless future validation is implemented.

State and persistence: test IAM state is in-memory credentials and action maps. Request bodies are synthetic `bytes.Reader` streams.

Dependencies and integration points: uses SigV4 helper functions, checksum writers, default test credentials, `s3err`, and testify assertions.

Risks and test signals: tests validate checksum algorithm extraction is case-insensitive and signed chunk verification works with dynamic dates. They intentionally document a current gap: trailer signature validation is not enforced, so future tightening will need test updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/copy_source_decode_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/copy_source_decode_test.go

Purpose: regression tests for S3 `X-Amz-Copy-Source` parsing, special-character decoding, same-source/destination detection, and traversal rejection.

Important tests: `TestCopySourceWithExclamationMark`, `TestCopySourceDecodingPlusSign`, `TestCopySourceRejectsTraversal`, and `TestCopySourceRoutingWithSpecialChars`.

Control flow signals: copy source parsing must use `url.PathUnescape`, not query unescape, so literal `+` remains plus rather than space. Encoded and unencoded `!`, encoded slashes, lowercase `%2f`, and version IDs should produce the same bucket/object/version semantics. Traversal validation must reject dot and dot-dot path segments after decoding, including encoded slashes, backslashes, dot-dot buckets, and traversal embedded in `versionId`.

State and persistence: tests are in-memory request and router simulations only.

Dependencies and integration points: exercises `pathToBucketObjectAndVersion`, `validateCopySource`, `s3_constants.GetBucketAndObject`, and Gorilla mux routing with `SkipClean(true)`. It mirrors handler behavior that returns `ErrInvalidCopyDest` when source and destination identify the same key.

Risks and test signals: this guards security-sensitive path traversal and correctness for object keys containing reserved characters. It also protects routing behavior where mux decoding and header decoding must agree. The tests do not perform actual filer copy operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/copy_source_decode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/cors.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/cors/cors.go

Purpose: implements bucket CORS configuration validation, request parsing, rule matching, response construction, wildcard handling, and HTTP response header application.

Important APIs/types: `CORSRule`, `CORSConfiguration`, `CORSRequest`, `CORSResponse`, `ValidateConfiguration`, `ParseRequest`, `EvaluateRequest`, `ApplyHeaders`, plus internal `validateRule`, `validateOrigin`, `buildPreflightResponse`, `buildResponse`, `matchesOrigin`, `matchWildcard`, `matchesHeader`, and `containsString`.

Control flow: validation rejects nil/empty configs, more than 100 rules, unsupported methods, empty origins, invalid wildcard origins, and negative max age. `ParseRequest` extracts `Origin`, method, and preflight request method/headers for OPTIONS. `EvaluateRequest` finds the first origin-matching rule. Preflight responses include allowed methods/headers only when the requested method and all requested headers are allowed; actual requests also require method match.

State and persistence: pure in-memory logic; XML/JSON tags define persistence/transport shape when configs are marshaled elsewhere.

Dependencies and integration points: uses standard `net/http`, string operations, and S3 middleware/storage code that supplies configs.

Risks: `AllowedOrigins: "*"` returns the caller origin rather than literal `*`, which is credential-friendly but differs from some simple CORS implementations. Header matching treats an empty `AllowedHeaders` list as all headers allowed. Origin wildcard matching is intentionally simple and only supports protocol-prefixed leading `*` subdomain patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/cors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/cors_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/cors/cors_test.go

Purpose: unit tests for pure CORS validation, parsing, matching, evaluation, and header application.

Important tests: `TestValidateConfiguration`, `TestValidateOrigin`, `TestParseRequest`, `TestMatchesOrigin`, `TestMatchesHeader`, `TestEvaluateRequest`, and `TestApplyHeaders`.

Control flow signals: tests verify nil/empty configs fail, valid single rules pass, rule count cap is 100, invalid methods and origins fail, and negative max age fails. Parsing must identify OPTIONS preflight and split comma-separated requested headers with trimming. Origin matching covers wildcard, exact HTTP/HTTPS, subdomain wildcard, base-domain non-match, multi-origin lists, and protocol mismatch. Header matching is case-insensitive, supports `*`, exact names, and prefix wildcards such as `x-amz-*`.

State and persistence: no persistence. Tests compare plain structs and httptest response headers.

Dependencies and integration points: exercises `cors.go` only, using `httptest` for `ApplyHeaders`.

Risks and test signals: preflight with forbidden headers still returns a `CORSResponse` containing only `AllowOrigin`, leaving middleware behavior to decide whether this is acceptable. The tests document current behavior rather than strict browser acceptance. There is no coverage for XML/JSON marshaling of CORS configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/cors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware.go

Purpose: HTTP middleware that applies bucket or fallback CORS policy to S3 API requests and short-circuits preflight requests.

Important APIs/types: `BucketChecker`, `CORSConfigGetter`, `Middleware`, `NewMiddleware`, `getCORSConfig`, `Handler`, `HandleOptionsRequest`, and `processCORS`.

Control flow: `processCORS` parses request CORS fields and extracts the bucket from S3 route constants. Requests without a bucket bypass CORS. Config lookup prefers bucket-specific CORS and falls back to global config only for no config, nil config, or no-such-bucket cases. Other errors prevent fallback. If any config exists, `Vary: Origin` is added even for non-CORS requests. Non-CORS requests then continue. Preflight without config or failed evaluation gets S3 access denied. Successful preflight applies CORS headers and returns 200; successful actual requests apply headers then call the next handler.

State and persistence: middleware holds references to config providers and optional fallback config. It does not persist state.

Dependencies and integration points: integrates `cors.go`, route parsing in `s3_constants.GetBucketAndObject`, S3 error response writing, and glog.

Risks: `BucketChecker` is injected but not used in current control flow; bucket existence is inferred from config getter errors. Fallback on `ErrNoSuchBucket` intentionally avoids CORS-based bucket-existence leaks but means global CORS may decorate 404 responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_nonexistent_bucket_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_nonexistent_bucket_test.go

Purpose: tests CORS behavior for non-existent buckets, especially global fallback policy and non-disclosure of bucket existence through CORS response differences.

Important tests: `TestMiddlewareNonExistentBucket` and `TestMiddlewareConsistentBehavior`.

Control flow signals: preflight to a missing bucket with wildcard or matching fallback config should return 200 with `Access-Control-Allow-Origin`. Actual requests to missing buckets should let the downstream handler return 404 while still applying CORS headers. Non-matching origins and no fallback config should make preflight return forbidden without origin headers. Existing and non-existing bucket cases should produce consistent preflight CORS headers/status under a fallback wildcard config.

State and persistence: in-memory mocks and httptest recorders only.

Dependencies and integration points: uses mock bucket checker/config getter types from the middleware test package, Gorilla mux URL vars, fallback `CORSConfiguration`, and S3 error codes.

Risks and test signals: these tests document a deliberate security tradeoff: fallback CORS applies even when the bucket does not exist so browsers cannot infer existence by CORS preflight behavior. Coverage uses mocks where `GetCORSConfiguration` returns nil/ErrNone, so real S3 server integration still depends on production config getter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_nonexistent_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_test.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_test.go

Purpose: tests CORS middleware fallback precedence, error handling, multi-origin matching, and `Vary: Origin` behavior.

Important fixtures/tests: `mockBucketChecker`, `mockCORSConfigGetter`, `TestMiddlewareFallbackConfig`, `TestMiddlewareFallbackConfigWithMultipleOrigins`, `TestMiddlewareFallbackWithError`, `TestMiddlewareVaryHeader`, `TestHandleOptionsRequestVaryHeader`, and helper `hasVaryOrigin`.

Control flow signals: no bucket-level config should use global fallback; bucket config must override fallback both for allow and deny outcomes. No config on actual requests yields normal downstream status without CORS headers, while OPTIONS without config returns forbidden. Only `ErrNoSuchBucket` and `ErrNoSuchCORSConfiguration` trigger fallback; access denied and internal errors do not. `Vary: Origin` must be present whenever a CORS config exists, including OPTIONS handling and non-CORS requests.

State and persistence: tests use in-memory mocks and mux route vars.

Dependencies and integration points: validates `Middleware.Handler`, `HandleOptionsRequest`, `getCORSConfig`, and response headers under httptest.

Risks and test signals: the middleware adds `Vary` by `Header().Add`, so multiple middleware layers could create multiple values; `hasVaryOrigin` allows comma-separated or repeated forms. The injected `BucketChecker` is not asserted because production logic currently relies on config getter outcomes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/credential_iam_errors.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/credential_iam_errors.go

Purpose: maps credential-store errors to AWS IAM error code strings for embedded S3 IAM handling and the standalone IAM API.

Important API: `CredentialErrToIamErrCode(err error) string`.

Control flow: uses `errors.Is` to preserve wrapped error semantics. `credential.ErrUserAlreadyExists` maps to `iam.ErrCodeEntityAlreadyExistsException`. `credential.ErrUserNotFound` and `credential.ErrAccessKeyNotFound` map to `iam.ErrCodeNoSuchEntityException`. All other errors map to `iam.ErrCodeServiceFailureException`.

State and persistence: no state or persistence; this is pure error translation.

Dependencies and integration points: depends on AWS IAM SDK error constants and SeaweedFS credential package sentinel errors. Shared use keeps IAM error granularity consistent across `weed/iamapi` and embedded `weed/s3api`.

Risks and test signals: the default to service failure ensures unexpected backend errors become HTTP 500-style IAM failures rather than accidental success or misleading client errors. New credential sentinel errors need explicit mapping if they should surface as specific IAM client errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/credential_iam_errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/custom_types.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/custom_types.go

Purpose: defines small shared S3 API types/constants that do not belong to larger feature files.

Important API/type: `s3TimeFormat` and `ConditionalHeaderResult`.

Control flow: no functions are implemented. `ConditionalHeaderResult` is a data carrier for conditional header evaluation, bundling an S3 error code, an ETag used for 304 responses, and the fetched filer entry if one was loaded during precondition checks.

State and persistence: no persistence. The `Entry` pointer can carry filer metadata/chunks fetched by calling code, so consumers must treat nil as either not fetched or object missing according to caller context.

Dependencies and integration points: imports `filer_pb.Entry` and `s3err.ErrorCode`. The result type integrates conditional GET/HEAD/PUT logic with object fetch paths and error response generation elsewhere in the S3 API.

Risks: because `Entry` is optional and overloaded, downstream code must not assume a nil entry always means not found. `s3TimeFormat` with millisecond precision is shared formatting surface; changing it can affect wire-compatible timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/custom_types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart.go -->
## sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart.go

Purpose: implements S3 multipart upload lifecycle on top of SeaweedFS filer entries: initiate, complete, abort, list uploads, list parts, encryption metadata propagation, multipart ETag, composite checksums, versioning behavior, and cleanup.

Important APIs/types: `createMultipartUpload`, `CompleteMultipartUploadResult`, `copySSEHeadersFromFirstPart`, `multipartCompletionState`, `completeMultipartResult`, `extractMultipartSSES3Info`, `completedMultipartChunk`, `applyMultipartSSES3HeadersFromUploadEntry`, `prepareMultipartCompletionState`, `completeMultipartUpload`, `abortMultipartUpload`, `listMultipartUploads`, `listObjectParts`, `MultipartEncryptionConfig`, `prepareMultipartEncryptionConfig`, `applyMultipartEncryptionConfig`, `calculateMultipartETag`, `computeCompositeChecksum`, `getEtagFromEntry`, and `validateCompletePartETag`.

Control flow: initiation creates an upload directory under bucket uploads, stores target key/owner/metadata/content type/object-lock metadata, validates requested checksum algorithm, and prepares explicit or bucket-default SSE-KMS/SSE-S3 metadata before persisting the directory. Completion validates non-empty ordered parts, lists upload entries, matches requested ETags, rejects too-small non-final parts, builds final chunk offsets, records part boundaries, computes multipart ETag and optional composite checksum, then writes either a new version file, a suspended-version null object, or a normal object. It routes writes through object ownership/ring helpers when available, otherwise uses an object write lock. Cleanup removes unused part entries and upload directories.

State and persistence: persistent state is filer directory/file entries, extended metadata for upload ID, object key, owner, ETag, version ID, multipart part count/boundaries, checksum algorithm/value, object lock, TTL expiry, and SSE metadata. Versioned buckets store content under `.versions` and update latest-version pointers; rollback removes a just-created version if finalization fails.

Dependencies and integration points: depends on AWS S3 SDK structs, filer client operations, versioning helpers, conditional header checks, object routing locks, stats counters, S3 encryption helpers, checksum mappings, and `s3_constants`.

Risks: multipart completion is a dense persistence transaction spread across list, write, version-pointer update, and cleanup; partial failures can leave stale upload data. SSE-S3 IV backfill intentionally trusts existing per-chunk metadata and only fills missing metadata, avoiding decryption corruption. Composite checksum requires every completed part to have matching stored checksum metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/filer_multipart.go -->
