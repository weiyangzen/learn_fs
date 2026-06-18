# Research: subset-b-008201

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers_test.go -->
## sources/object-store/minio/cmd/object-handlers_test.go

### Purpose
This file is the broad HTTP/S3 compatibility test suite for MinIO object handlers. It drives registered API routes through `httptest` requests and verifies object data, XML error bodies, S3 status codes, auth behavior, anonymous-policy behavior, nil object-layer behavior, multipart flows, copy semantics, checksums, range reads, streaming SigV4 uploads, compression/encryption combinations, and V2/V4 signing parity.

### Important APIs, Types, and Functions
- `type Fault` plus constants `MissingContentLength`, `TooBigObject`, `TooBigDecodedLength`, `BadSignature`, `BadMD5`, and `MissingUploadID` model request mutations used across PUT and multipart tests.
- `TestAPIHeadObjectHandler`, `TestAPIGetObjectHandler`, `TestAPIPutObjectHandler`, `TestAPICopyObjectHandler`, `TestAPIDeleteObjectHandler`, and related helpers exercise single-object HTTP endpoints.
- `TestAPIGetObjectWithMPHandler` and `TestAPIGetObjectWithPartNumberHandler` validate ranged and part-number reads from single-part, multipart, encrypted, and compressed objects.
- Multipart HTTP tests cover `NewMultipart`, `PutObjectPart`, `CopyObjectPart`, `CompleteMultipart`, `AbortMultipart`, and `ListObjectParts` handlers, including presigned list requests.
- The file depends heavily on shared test harnesses such as `ExecObjectLayerAPITest`, `ExecExtendedObjectLayerAPITest`, `ExecObjectLayerAPIAnonTest`, `ExecObjectLayerAPINilTest`, request builders, signing helpers, `uploadTestObject`, `NewDummyDataGen`, and direct `ObjectLayer` methods for setup/verification.

### Control Flow
Each public `Test...` wrapper initializes the object-layer API harness with endpoint names. The paired `test...` helper usually creates prerequisite objects or multipart upload IDs, constructs signed HTTP requests, serves them through `apiRouter`, checks status codes and response bodies, then verifies persistence by reading back through `ObjectLayer`. Most major handlers are checked twice with SigV4 and SigV2 where applicable. Anonymous calls are routed through policy helper tests, while nil-object-layer requests verify early server-not-initialized behavior.

GET and HEAD tests first upload deterministic data, then check normal responses, missing objects, invalid object names, invalid credentials, byte ranges, and encrypted HEAD behavior requiring SSE-C headers. PUT tests mutate content length, MD5, storage class, checksums, copy-source headers, and streaming chunk signatures. Copy tests validate metadata directives, source condition headers, version ID parsing, same-source restrictions, copy-part range validation, and object data preservation. Multipart completion tests build real parts, marshal `CompleteMultipartUpload` XML, and assert ETag/order/part-size/upload-ID failures before a success path.

### State and Persistence Behavior
The tests mutate in-memory or disk-backed test object layers by creating buckets, objects, multipart upload state, uploaded parts, copied objects, and deleted objects. They assert persisted data by calling `GetObjectNInfo`, `GetObjectInfo`, `ListObjectParts`, or direct object reads after handler execution. Extended runs repeatedly execute the same behavior under compression, encryption, and versioning configurations, so state expectations include plaintext length preservation, encrypted-object header requirements, compression metadata presence, multipart ETag formation, and deletion idempotence.

### Dependencies and Integration Points
The file integrates HTTP routing, S3 request signing, XML request/response encoding, bucket policy helpers, MinIO object layer APIs, encryption/compression globals, checksum hashing, multipart metadata, and test data generators. It is a consumer-side validation layer for handlers implemented in object handler files, including `object-multipart-handlers.go`. It also uses package globals such as `globalPolicySys`, `globalIsTLS`, `globalMaxObjectSize`, and compression state, so tests depend on correct setup/teardown discipline.

### Risks and Edge Cases
- Global state such as policy, TLS, compression, encryption, and KMS must be reset carefully or later subtests can inherit unexpected behavior.
- Some branches use direct object-layer calls for setup while only one handler is registered, so failures can reflect setup assumptions as well as handler behavior.
- Large dummy data and extended matrix tests can be expensive; `testing.Short()` reduces some multipart GET cases.
- There is a suspicious switch in copy-part test request creation: `case !testCase.invalidPartNumber || !testCase.maximumPartNumber` is true for most combinations, which can make the invalid/max part-number branches unreachable.
- Error assertions are highly S3-compatibility-sensitive, so changes in API error mapping, resource path normalization, or header casing can break tests.

### Test Signals
This file is itself the signal source. It covers success and failure statuses, XML API error codes, response content equality, checksum headers, ETag headers, anonymous policy authorization, V2/V4 signatures, presigned requests, streaming-chunk signature faults, encrypted HEAD/GET behavior, compression persistence, multipart upload lifecycle, and nil backend handling.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-lambda-handlers.go -->
## sources/object-store/minio/cmd/object-lambda-handlers.go

### Purpose
This file implements S3 Object Lambda GET handling. Instead of returning object bytes directly, it constructs an object-lambda event with a presigned input S3 URL, sends it to a configured lambda/webhook target, validates the target's route/token response, forwards selected headers and status, maps lambda-declared errors into S3 API errors, and streams the transformed body to the client.

### Important APIs, Types, and Functions
- `getLambdaEventData` builds a `levent.Event` containing `GetObjectContext`, the original user request, and user identity. It uses MinIO client presigning with temporary credentials and forwards supported GET/HEAD query parameters plus `partNumber`.
- `fwdHeadersToS3` copies response headers with the `x-amz-fwd-header-` prefix to the client response without the prefix.
- `fwdStatusToAPIError` converts forwarded lambda status and error headers into `APIError` values for status codes >= 400.
- `GetObjectLambdaHandler` is the HTTP handler on `objectAPIHandlers`.

### Control Flow
The handler creates an audit context, checks the object layer is initialized, extracts bucket/object path variables, authorizes `policy.GetObjectAction`, looks up the configured lambda target by `lambdaArn`, builds event data, and sends it to the target. It then validates that `x-amz-request-route` equals the generated route and that `x-amz-request-token` matches the generated token with constant-time comparison. If the target supplies `x-amz-fwd-status`, the handler parses it as the client status. Forwarded headers are copied, forwarded error headers can terminate with an S3 XML error, gzip is disabled when global API config says object gzip is off, and the lambda body is copied to the client.

### State and Persistence Behavior
The handler itself does not persist object data. It relies on presigned access to the underlying object store and on `globalLambdaTargetList`, global endpoint/TLS settings, site region, remote transport, and global API gzip configuration. `getLambdaEventData` derives the output token from access key plus presigned query string, so token validity is tied to the generated URL and credentials.

### Dependencies and Integration Points
It integrates with MinIO auth, policy checks, mux variables, lambda target configuration, MinIO Go client presigning, shortuuid route generation, SHA-256 token generation, response header constants in `internal/http`, audit logging, and gzip middleware behavior. It is reached through the object-lambda router path rather than normal object GET routing.

### Risks and Edge Cases
- The duration clamp in `getLambdaEventData` always sets one hour because the condition is `duration > time.Hour || duration < time.Hour`; only exactly one hour would avoid reassignment.
- `io.Copy` return errors are ignored after headers are written, so downstream write/read failures are not translated into API errors.
- Response trust is centered on route/token validation; any mismatch produces invalid request/token errors before body forwarding.
- Forwarded status parsing can fail and returns a synthetic `LambdaFunctionStatusError`.
- Global mutable `getLambdaEventData` is reassigned in tests and must be restored if future tests share process state.

### Test Signals
The paired test file mocks a lambda target and overrides event generation, checking 200, 206, and 400 paths, forwarded content type, body forwarding on success, request signing, target lookup, and disabled gzip configuration.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-lambda-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-lambda-handlers_test.go -->
## sources/object-store/minio/cmd/object-lambda-handlers_test.go

### Purpose
This file provides focused tests for `GetObjectLambdaHandler`. It verifies that a configured lambda webhook response can drive the final S3 response status, headers, and body through the object-lambda route.

### Important APIs, Types, and Functions
- `TestGetObjectLambdaHandler` defines table cases for `206 Partial Content`, `200 OK`, and `400 Bad Request`.
- `runObjectLambdaTest` sets up the object-layer API test harness, an `httptest.Server` lambda target, configures `globalLambdaTargetList`, overrides `getLambdaEventData`, signs a GET request, invokes `api.GetObjectLambdaHandler`, and asserts response details.

### Control Flow
For each case, the helper creates a lambda server that writes route/token headers, a forwarded content-type header, a forwarded status header, and a test body. It builds MinIO lambda webhook config and API gzip config, fetches enabled targets, replaces event generation with deterministic route/token data, signs a request to `/objectlambda/{bucket}/{object}?lambdaArn=...`, then invokes the handler directly with an object API provider.

### State and Persistence Behavior
The tests mutate package globals `globalLambdaTargetList` and `getLambdaEventData` and rely on the object-layer harness for valid credentials and object API initialization. They do not create or persist an actual source object because the event URL is mocked and the lambda body is synthetic. The mock target is process-local and closed with `defer`.

### Dependencies and Integration Points
The test integrates MinIO config loading for lambda webhook targets, signer V4, auth credentials from the object-layer test harness, `httptest`, lambda event structs, and forwarded header constants. It validates the handler independent of normal router dispatch by directly constructing `objectAPIHandlers`.

### Risks and Edge Cases
- The override of `getLambdaEventData` is not restored inside the helper, so additional tests in the same package could inherit it if ordering changes.
- Negative route/token mismatch cases, target lookup failures, malformed forwarded status, and missing forwarded error code/message paths are not covered.
- Error response body for 400 is not asserted; the test only checks status and content type.

### Test Signals
Signals include status code equality, forwarded `Content-Type`, success-body equality for responses below 400, successful lambda target config fetch, V4 signing, and handler operation with object API present.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-lambda-handlers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object-multipart-handlers.go -->
## sources/object-store/minio/cmd/object-multipart-handlers.go

### Purpose
This file implements MinIO's S3 multipart object HTTP handlers: initiate multipart upload, upload a part, copy a part from an existing object, complete an upload, abort an upload, and list uploaded parts. It is the HTTP adaptation layer between S3 request semantics and the `ObjectLayer` multipart API, including auth, encryption, compression, checksums, object lock, replication, quota, versioning, lifecycle tiering, eventing, and XML responses.

### Important APIs, Types, and Functions
- `NewMultipartUploadHandler` validates authorization and request metadata, applies bucket/default encryption, object lock, tags, storage class, replication metadata, compression metadata, checksum preferences, and calls `ObjectLayer.NewMultipartUpload`.
- `CopyObjectPartHandler` parses `X-Amz-Copy-Source`, version ID, range headers, source/destination encryption options, remote-copy needs, compression and encryption transforms, then calls `ObjectLayer.CopyObjectPart`.
- `PutObjectPartHandler` validates part ID, content length, auth/signature type, checksums, quota, multipart metadata, compression/encryption transforms, and calls `ObjectLayer.PutObjectPart`.
- `CompleteMultipartUploadHandler` decodes completion XML, validates sorted parts and object lock headers, computes multipart ETag metadata, enforces preconditions, calls `ObjectLayer.CompleteMultipartUpload`, then sets headers, schedules replication/events/lifecycle cleanup, and writes XML.
- `AbortMultipartUploadHandler` authorizes abort and calls `ObjectLayer.AbortMultipartUpload`, treating `InvalidUploadID` as non-fatal in this implementation path.
- `ListObjectPartsHandler` validates list markers, calls `ObjectLayer.ListObjectParts`, adjusts encrypted/compressed part sizes and ETags, and writes the XML listing.

### Control Flow
All handlers follow the same outer pattern: create context and audit log, extract mux variables, get `ObjectAPI`, authorize with the appropriate policy action, parse query/header inputs, translate them into `ObjectOptions`, call the object layer, map errors with `toAPIError`, and emit S3 XML or header-only responses.

Initiation is metadata-heavy and establishes persistent multipart state. Put-part and copy-part are stream-heavy: they authenticate, enforce size/part limits, build hash readers, optionally compress, optionally encrypt using a part key derived from object key plus part number, attach compression index callbacks, and write part state. Completion is the commit point: it validates completion XML, records the computed multipart ETag in metadata, commits parts to an object version, emits object-created events, schedules replication, updates replica stats, and handles lifecycle transition cleanup. Abort deletes upload state. List reads upload state and normalizes returned part metadata for S3 clients.

### State and Persistence Behavior
Multipart state is persisted through the object layer: initiate creates an upload ID and metadata, put/copy part persists individual parts, complete atomically creates the final object/version and removes or supersedes upload state, abort removes upload state, and list reads current upload state. Metadata persisted or updated includes encryption metadata, compressed-object markers and indexes, object tags, object lock retention/legal hold, replication timestamps/statuses, checksum algorithm/type, storage class, preserved ETags, and versioning/tiering information.

### Dependencies and Integration Points
The file depends on MinIO's auth and policy systems, mux routing, object-layer interfaces, crypto/SSE helpers, hash/checksum package, compression readers, SIO encryption, bucket encryption/object lock/replication/versioning systems, DNS federation for remote copy, MinIO Go client for remote part upload, lifecycle/tier manager, event notifier, audit logger, XML encoders, and HTTP header constants. It is heavily tested by `object-handlers_test.go` and lower-level object API tests.

### Risks and Edge Cases
- Multipart handlers combine many global subsystems; changes in encryption, compression, replication, object lock, versioning, or lifecycle can subtly alter metadata or response headers.
- Streaming and compressed uploads can have unknown encoded sizes, so checksum validation and hash-reader setup must stay aligned with actual/plain sizes.
- SSE-C/SSE-S3/SSE-KMS compatibility paths are strict; wrong headers can expose invalid decryption behavior or incorrect ETags.
- `CompleteMultipartUploadHandler` writes success before sending events and lifecycle cleanup; failures after response are operational side effects rather than API failures.
- Copy-part has remote-copy, range, version, precondition, compression, and encryption branches that are easy to regress without integration coverage.
- Ignored `io.Copy`-style stream errors are limited here because handlers generally pass readers into object-layer APIs, but response writing still assumes encoder success.

### Test Signals
Coverage comes mainly from `object-handlers_test.go`: initiate success/auth/parallel behavior, put-part signed and streaming faults, copy-part source/range/version cases, complete XML/part-order/ETag/size/upload-ID cases, abort behavior, list parts with V2/V4/presigned auth, encryption and compression matrices, anonymous policy behavior, and nil object-layer behavior. `object_api_suite_test.go` adds direct object-layer multipart creation/abort/complete persistence checks.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object-multipart-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/object_api_suite_test.go -->
## sources/object-store/minio/cmd/object_api_suite_test.go

### Purpose
This file is a direct `ObjectLayer` behavioral suite. It bypasses HTTP routing and checks core bucket/object operations against the object-layer interface across FS/erasure-style harnesses and, for selected tests, compression/encryption/versioning combinations.

### Important APIs, Types, and Functions
- `newTestReaderEOF`, `newTestReaderNoEOF`, `testOneByteReadEOF`, and `testOneByteReadNoEOF` model readers that return data with or without EOF on the first read.
- Bucket/object tests include `testMakeBucket`, `testMultipleObjectCreation`, `testPutObject`, `testPutObjectInSubdir`, `testListBuckets`, `testListBucketsOrder`, `testPaging`, `testObjectOverwriteWorks`, and negative bucket/object cases.
- Multipart tests include `testMultipartObjectCreation` and `testMultipartObjectAbort`.
- `enableCompression`, `enableEncryption`, `resetCompressEncryption`, `execExtended`, and `ExecExtendedObjectLayerTest` manage global compression/encryption/KMS test modes.

### Control Flow
Each public `Test...` delegates to `ExecObjectLayerTest` or `ExecExtendedObjectLayerTest`, which supplies an `ObjectLayer`, instance label, and test error handler. Tests create buckets, write objects or multipart parts, call object-layer APIs, then verify returned errors, sizes, ETags, listing order, object data, and content-type inference. `execExtended` defines a matrix of default, versioned, compressed, compressed+versioned, encrypted, encrypted+versioned, compressed+encrypted, and compressed+encrypted+versioned runs.

### State and Persistence Behavior
The suite creates buckets, object keys, multipart upload IDs, part records, completed multipart objects, aborted uploads, overwritten objects, nested-prefix objects, and bucket lists. It verifies persistence by direct reads through `GetObject`, `GetObjectInfo`, and listing APIs. Compression/encryption helpers mutate package globals (`globalCompressConfig`, `globalAutoEncryption`, `GlobalKMS`) to force object metadata and storage behavior under different configurations.

### Dependencies and Integration Points
The tests exercise the `ObjectLayer` contract directly and therefore validate storage implementations independent of HTTP handlers. They use MinIO KMS secret-key parsing, humanize size constants, context timeouts, object options, bucket options, multipart structs, and shared put-reader helpers. HTTP handler tests rely on the same object-layer behavior for setup and verification.

### Risks and Edge Cases
- Global compression/encryption state must be reset or tests can contaminate each other.
- `ExecExtendedObjectLayerTest` currently accepts an `init` function in `execExtended` but calls `ExecObjectLayerTest` without visibly invoking that `init` in this file, so the effective matrix depends on harness behavior outside this file.
- Paging and ordering assertions encode lexicographic S3 listing behavior; implementation changes in ordering/token logic will break them.
- Tests compare exact error strings in several places, making error wording part of the contract.

### Test Signals
Signals include bucket creation and duplicate-bucket failure, multipart ETag formation and abort success, multiple object creation/readback, list pagination/truncation/prefix/delimiter/marker behavior, overwrite correctness, non-existent bucket/object errors, directory pseudo-object handling, content-type inference, bucket list order, and reader EOF edge cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/object_api_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_fileino.go -->
## sources/object-store/minio/cmd/os-dirent_fileino.go

### Purpose
This platform-specific helper returns an inode-like identifier from `syscall.Dirent` on BSD platforms where the field is named `Fileno`.

### Important APIs, Types, and Functions
- Build tags: `freebsd || openbsd || netbsd`.
- `direntInode(dirent *syscall.Dirent) uint64` returns `uint64(dirent.Fileno)`.

### Control Flow
There is no branching. Callers pass a directory entry and receive the platform's file number as a `uint64`.

### State and Persistence Behavior
The function is pure and reads only the supplied `syscall.Dirent`. It does not mutate state or persist data.

### Dependencies and Integration Points
It depends on Go's `syscall` package and complements `os-dirent_ino.go`, which provides the same function for Linux/Darwin. Higher-level directory walking code can call `direntInode` without build-time field-name conditionals.

### Risks and Edge Cases
The main risk is build-tag coverage: this file must compile only on platforms where `Dirent.Fileno` exists. Null `dirent` would panic, so callers must pass valid entries.

### Test Signals
No direct tests are present in this file. Coverage is expected through platform builds and any directory traversal tests that compile and call `direntInode`.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_fileino.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_ino.go -->
## sources/object-store/minio/cmd/os-dirent_ino.go

### Purpose
This platform-specific helper returns an inode identifier from `syscall.Dirent` on Linux and Darwin platforms where the field is named `Ino`.

### Important APIs, Types, and Functions
- Build tags: `(linux || darwin) && !appengine`.
- `direntInode(dirent *syscall.Dirent) uint64` returns `dirent.Ino`.

### Control Flow
There is no branching. The function directly reads the inode field from the supplied directory entry.

### State and Persistence Behavior
The function is pure and has no persistence side effects.

### Dependencies and Integration Points
It depends on `syscall` and pairs with `os-dirent_fileino.go` for BSD platforms. Callers use `direntInode` as a portable abstraction over platform-specific `Dirent` field names.

### Risks and Edge Cases
The build tag excludes App Engine and assumes `Dirent.Ino` is available on the selected platforms. A nil pointer would panic. Porting to platforms with different field names requires another build-tagged implementation.

### Test Signals
No direct tests are present. Compile success on Linux/Darwin and directory traversal behavior provide indirect validation.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_ino.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_namelen_bsd.go -->
## sources/object-store/minio/cmd/os-dirent_namelen_bsd.go

### Purpose
This platform-specific helper returns the directory-entry name length on Darwin and BSD systems where `syscall.Dirent` exposes `Namlen`.

### Important APIs, Types, and Functions
- Build tags: `darwin || freebsd || openbsd || netbsd`.
- `direntNamlen(dirent *syscall.Dirent) (uint64, error)` returns `uint64(dirent.Namlen), nil`.

### Control Flow
The function performs a direct field read and always returns nil error.

### State and Persistence Behavior
The function is pure and does not mutate global or filesystem state.

### Dependencies and Integration Points
It depends on `syscall` and complements `os-dirent_namelen_linux.go`, which must derive name length from the name buffer. Higher-level directory scanning can call `direntNamlen` uniformly across operating systems.

### Risks and Edge Cases
Build tags must match platforms where `Dirent.Namlen` exists. Nil input would panic. Since it trusts the kernel-provided `Namlen`, malformed entries are not independently checked here.

### Test Signals
No direct tests are present. Platform compilation and directory scanning behavior are the primary signals.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_namelen_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_namelen_linux.go -->
## sources/object-store/minio/cmd/os-dirent_namelen_linux.go

### Purpose
This Linux-specific helper computes the length of a directory-entry name from `syscall.Dirent` by scanning the fixed name buffer up to the record length for a terminating NUL byte.

### Important APIs, Types, and Functions
- Build tags: `linux && !appengine`.
- `direntNamlen(dirent *syscall.Dirent) (uint64, error)` calculates the usable name-buffer limit from `Reclen`, `unsafe.Offsetof(syscall.Dirent{}.Name)`, and the static name buffer size, then uses `bytes.IndexByte` to find the first zero byte.

### Control Flow
The function computes the fixed header size, creates a byte-array view over `dirent.Name` using `unsafe`, caps the scan limit to the smaller of `Reclen - fixedHdr` and the name-buffer length, scans for a zero terminator, returns an error if none is found, and otherwise returns the index as the name length.

### State and Persistence Behavior
The function is pure from the caller's perspective. It reads memory from the supplied `Dirent` and returns either a length or an error. It does not persist or mutate data.

### Dependencies and Integration Points
It depends on `bytes`, `fmt`, `syscall`, and `unsafe`. It is the Linux counterpart to BSD/Darwin `Namlen` field access, allowing directory traversal code to use `direntNamlen` portably.

### Risks and Edge Cases
- The function uses `unsafe.Pointer` into `dirent.Name`; callers must pass a valid `Dirent`.
- `dirent.Reclen - fixedHdr` is unsigned arithmetic. If a malformed record has `Reclen < fixedHdr`, the value can underflow before being capped to name-buffer length.
- Missing NUL terminators return an explicit error to avoid long-name bugs.
- Build tags exclude App Engine and non-Linux platforms.

### Test Signals
No direct tests are present. Indirect signals are Linux builds and any filesystem directory-reading tests that encounter normal and long names.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/os-dirent_namelen_linux.go -->
