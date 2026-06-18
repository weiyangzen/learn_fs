# subset-b-009588 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/testing/bucket_tests.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake/testing/bucket_tests.go

## Purpose
This file defines the shared conformance test matrix registered by `RegisterBucketTests` for any implementation of `gcs.Bucket`. It exercises GCS-like behavior for object creation, copy, compose, read, multi-range read, stat, update, delete, list, and cancellation. The tests are written against the public `internal/storage/gcs` request and object model so fake buckets, real buckets, and wrapper buckets can be validated with the same expectations.

## Important APIs, Types, and Helpers
Key helpers include `createEmpty`, `computeCrc32C`, `makeStringPtr`, `interestingNames`, `illegalNames`, `listDifference`, `readMultiple`, `readMultipleUsingMultiRangeDownloader`, and `forEachString`. `init` raises `RLIMIT_NOFILE` to permit high-parallelism integration-style tests. `bucketTest` stores shared dependencies: context, `gcs.Bucket`, clock, cancellation support, and whether create buffers all contents. Test suites embed `bucketTest`: `createTest`, `copyTest`, `composeTest`, `readTest`, `readMultiRangeTest`, `statTest`, `updateTest`, `deleteTest`, `listTest`, and `cancellationTest`.

## Control Flow and Behavior
The file is organized by bucket operation. Create tests cover empty and non-empty objects, overwrites, default and explicit object attributes, partial read failures, legal and illegal object names, CRC32C/MD5 validation, and generation/metageneration preconditions. Copy tests validate source absence, overwriting destination objects, copying to the same name, source generation selection, and source metageneration preconditions. Compose tests cover one, two, repeated, many, and composite sources, explicit destination metadata, destination preconditions, zero/too-many sources, component count limits, and interesting/illegal destination names. Read and multi-range read tests validate missing objects, generation lookup, overwrites, deletes, and byte range edge cases. Stat, update, delete, and list tests assert object metadata transitions, lexicographic ordering, delimiter collapse semantics, prefixes, pagination tokens, and idempotent delete behavior. Cancellation tests run long create/read operations under cancellable contexts and assert fast error return plus no partially created object.

## State, Persistence, and Integration
The tests treat the bucket as persistent state within each test case. They assert generation increments, metageneration increments, updated timestamps, stat/list/read consistency, delete visibility, and that failed precondition/checksum/partial-content operations leave bucket state unchanged. Integration points include `gcs.Bucket`, `gcs.Object`, `gcs.MinObject`, `gcs.ExtendedObjectAttributes`, `gcs.ByteRange`, `storageutil` helpers, `ogletest`, `oglematchers`, `timeutil`, `errgroup`, and OS rlimit APIs.

## Risks and Test Signals
This suite is a high-value compatibility gate but is sensitive to external GCS behavior, error-message wording, clock slop, resource limits, and implementation differences around versioning and multi-range range errors. The tests explicitly tolerate some real-client differences by matching error substrings such as `404`, `googleapi.*412`, or cancellation transport errors. The multi-range tests intentionally differ from single-range reads for ranges beyond EOF, expecting callback errors in several cases. Because the suite uses high parallelism and very broad Unicode inputs, it can expose race conditions, URL-encoding bugs, and fake/real divergence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/testing/bucket_tests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/testing/register_bucket_tests.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake/testing/register_bucket_tests.go

## Purpose
This file registers the shared bucket conformance suites from `bucket_tests.go` with `ogletest`. It turns exported methods on each suite type into test functions, creates fresh suite instances, traces setup/execution with `reqtrace`, and injects a `BucketTestDeps` instance created by a caller-supplied factory.

## Important APIs and Control Flow
`BucketTestDeps` carries the blocking-operation context, initialized `gcs.Bucket`, matching `timeutil.Clock`, cancellation support, and create-buffering behavior. `bucketTestSetUpInterface` is the common setup hook. `getSuiteName`, `isExported`, and `getTestMethods` reflect over suite prototypes in source order and keep only exported methods. `registerTestSuite` constructs an `ogletest.TestSuite`; for each test method it creates an instance, starts a trace in `SetUp`, calls `makeDeps`, stores the traced context in `deps.ctx`, invokes `setUpBucketTest`, calls the reflected method in `Run`, and reports a placeholder error in `TearDown`. `RegisterBucketTests` registers create, copy, compose, read, multi-range read, stat, update, delete, list, and cancellation suites.

## State, Dependencies, and Integration
State is per-test-function: each reflected suite instance holds its bucket dependencies after setup. The file depends on `reflect`, `x/net/context`, `x/text/cases`, `ogletest`, `srcutil`, `reqtrace`, and `timeutil`. It integrates directly with the test suites in the same package and indirectly with any bucket implementation through the `makeDeps` callback.

## Risks and Test Signals
The closure captures `instance` once per method during registration; each `ogletest` function reuses that instance for setup and run. This is normal for ogletest but means parallel execution expectations depend on framework behavior. `TearDown` always reports a TODO error because ogletest failure status is not plumbed into tracing, so trace reports should not be treated as pass/fail truth. Reflection registers only exported methods, so helper methods must remain unexported to avoid becoming tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/testing/register_bucket_tests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake_storage_util.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake_storage_util.go

## Purpose
This file provides a reusable fake-storage fixture for storage-layer tests. It starts `fake-gcs-server` with a fixed bucket/object dataset and returns a `StorageHandle` backed by the fake server's client plus an optional mocked storage control client.

## Important APIs and State
Constants define the default test bucket, object names, folder-like prefixes, generation numbers, metadata keys, and a compressed gzip test object. `FakeStorage` exposes `CreateStorageHandle` and `ShutDown`. `fakeStorage` stores the fake server, optional `MockStorageControlClient`, and selected `cfg.Protocol`. `NewFakeStorage` creates a default fixture; `NewFakeStorageWithMockClient` injects a control-client mock and protocol. `getTestFakeStorageObject` builds the initial object list, including root/subroot folder markers, a regular object with metadata, a subobject, and a gzip-encoded object. `createFakeStorageServer` delegates to `fakestorage.NewServerWithOptions`.

## Control Flow and Integration
`CreateStorageHandle` lazily creates a mock control client if absent and constructs a `storageClient` whose HTTP, gRPC, and bidi-gRPC clients all point at the fake server client. The returned handle uses `storageutil.StorageClientConfig` with the configured protocol and an empty write config. This fixture integrates with tests that expect the production `StorageHandle` interface while avoiding real GCS calls.

## Risks and Test Signals
The fixture panics on fake-server creation failures, which is acceptable for test setup but unsuitable for production. Because one fake server client backs all protocol slots, protocol-specific behavior may not be faithfully represented. The fixed gzip byte string is fragile: changing compressed bytes requires synchronizing the documented decompressed content. `ShutDown` must be called to stop the server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake_storage_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/full_read_closer.go -->
# sources/user-network-fs/gcsfuse/internal/storage/full_read_closer.go

## Purpose
This file defines `gcsFullReadCloser`, a `gcs.StorageReader` wrapper that normalizes short reads by filling the caller's buffer before returning, unless EOF is reached.

## Important APIs and Control Flow
`newGCSFullReadCloser` wraps an existing `gcs.StorageReader`. `Read` calls `io.ReadFull` on the wrapped reader. If the wrapped reader reaches EOF after returning some bytes, `io.ReadFull` reports `io.ErrUnexpectedEOF`; this wrapper converts that to `io.EOF` so callers see the same terminal error shape as ordinary readers. `ReadHandle` and `Close` delegate directly to the wrapped reader.

## State, Dependencies, and Integration
The only state is the wrapped `gcs.StorageReader`. The wrapper depends on `io`, `cloud.google.com/go/storage` for `ReadHandle`, and the local `gcs.StorageReader` interface. It integrates with storage read flows that need full-buffer semantics despite underlying GCS readers returning smaller chunks.

## Risks and Test Signals
`io.ReadFull` changes normal `Read` behavior: callers requesting a large buffer may block until the buffer fills or EOF/error occurs. This is correct for call sites expecting full responses but risky for streaming consumers that rely on partial reads. The EOF conversion is intentional compatibility behavior and is covered by `full_read_closer_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/full_read_closer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/full_read_closer_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/full_read_closer_test.go

## Purpose
This file tests `gcsFullReadCloser` against a deliberately partial reader that returns at most two bytes per `Read` call.

## Important APIs and Control Flow
`twoBytesStorageReader` implements `Read`, `Close`, and `ReadHandle`, using a `bytes.Buffer` while limiting each read to two bytes. `TestFullReaderCloser` runs table-driven parallel subtests for a buffer larger than the data, smaller than the data, and equal to the data. Each case writes data to the fake reader, wraps it with `newGCSFullReadCloser`, reads once, and asserts byte count, error, and output bytes.

## State, Dependencies, and Integration
State is local to each test case via an isolated buffer. Dependencies include `bytes`, `io`, Go `testing`, `cloud.google.com/go/storage`, and `testify/assert`. The test confirms the wrapper preserves `StorageReader` compatibility and fixes short-read behavior.

## Risks and Test Signals
The cases confirm the key invariant: successful reads return exactly the requested buffer length, and short final responses return `io.EOF` rather than `io.ErrUnexpectedEOF`. The fake reader's `ReadHandle` and `Close` are minimal, so delegation behavior is not deeply tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/full_read_closer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/bucket.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/bucket.go

## Purpose
This file defines the central storage abstraction for gcsfuse: the `gcs.Bucket` interface, related writer interface, request-id context key, and bucket capability model.

## Important APIs and Types
`PirloState` distinguishes non-Pirlo buckets from Pirlo buckets with rapid writes enabled or disabled. `BucketType` describes hierarchical namespace, zonal, and Pirlo state. `IsRapid` returns true for zonal or any Pirlo bucket; `RapidWritesEnabled` returns true for zonal or Pirlo rapid-enabled buckets. `Writer` abstracts GCS object writers with `Write`, `Close`, `Flush`, `ObjectName`, and `Attrs`. `Bucket` includes object read, multi-range download, create, chunk/appendable writer creation, upload finalization, flush, copy, compose, stat, list, update, delete, move, folder operations, and `GCSName`.

## Control Flow and Integration
The interface is purely contractual. Implementations in storage backends satisfy it, mocks use it for tests, and higher-level filesystem code consumes it without binding to a particular Google client transport. Methods accept `context.Context` for blocking operations and request structs from `request.go`. Object-returning operations use `Object`, `MinObject`, `ExtendedObjectAttributes`, `Listing`, and `Folder` from the same package.

## State, Persistence, and Risks
No state is stored in this file, but the interface documents persistence guarantees such as create visibility, read availability, and delete semantics. Compatibility risk is high: adding, removing, or changing methods requires updating production bucket handles, fake buckets, and both mock implementations. The rapid-write distinction drives client selection and writer behavior elsewhere, so misclassifying `BucketType` can select the wrong transport or upload semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/bucket_test.go

## Purpose
This file tests `BucketType.IsRapid` and `BucketType.RapidWritesEnabled`.

## Important APIs and Control Flow
`TestBucketType_IsRapid` table-tests combinations of zonal and Pirlo states. It expects non-zonal/non-Pirlo to be false, zonal to be true, Pirlo rapid-enabled to be true, and Pirlo rapid-disabled to still be rapid. `TestBucketType_RapidWritesEnabled` expects rapid writes to be active for zonal and Pirlo rapid-enabled buckets, but inactive for Pirlo rapid-disabled buckets.

## State, Dependencies, and Integration
There is no persistent state. The tests use Go `testing` and `testify/assert`. They are important because `storage_handle.go` uses `IsRapid` to select bidi gRPC and retry behavior, while write paths use `RapidWritesEnabled` to decide append/flush semantics.

## Risks and Test Signals
The test clearly encodes the subtle distinction between a rapid bucket and rapid writes being enabled. Regressions here could cause a Pirlo bucket with rapid writes disabled to be treated as ordinary for client selection or incorrectly enable rapid write behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/errors.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/errors.go

## Purpose
This file normalizes errors from Google storage clients into gcsfuse-specific semantic error types.

## Important APIs and Control Flow
`NotFoundError` wraps errors indicating a missing object name or generation. `PreconditionError` wraps failed preconditions. `GetGCSError` returns nil for nil input, maps `googleapi.Error` HTTP 404 to `NotFoundError`, HTTP 412 to `PreconditionError`, maps gRPC status `codes.NotFound` and `codes.FailedPrecondition`, maps `storage.ErrObjectNotExist` to `NotFoundError`, and otherwise returns the original error.

## State, Dependencies, and Integration
There is no state. Dependencies include `errors`, `fmt`, `net/http`, `cloud.google.com/go/storage`, `googleapi`, and gRPC status/codes. Storage implementations call `GetGCSError` so callers and tests can use `errors.As` or exact type expectations against local error classes instead of transport-specific errors.

## Risks and Test Signals
The function uses `errors.As` for `googleapi.Error` and `status.FromError` for gRPC statuses. Wrapped local `NotFoundError` or `PreconditionError` values are not specially unwrapped and may be returned unchanged or as their wrapper depending on the wrapping shape. Error classification affects retry, cache, and filesystem semantics, so missing a transport-specific error form can leak backend details upward.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/errors_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/errors_test.go

## Purpose
This file table-tests `GetGCSError` across nil, HTTP, gRPC, API error, storage sentinel, local error, and wrapped error cases.

## Important APIs and Control Flow
`TestGetGCSError` creates API errors from gRPC status values using `apierror.FromError`, constructs a matrix of input and expected errors, calls `GetGCSError`, and compares with `assert.Equal`. Cases include `googleapi.Error` 404/412/400, wrapped `googleapi.Error`, gRPC NotFound/FailedPrecondition/Internal, plain errors, wrapped gRPC NotFound, direct local `PreconditionError` and `NotFoundError`, wrapped local errors, `storage.ErrObjectNotExist`, API errors, and wrapped API errors.

## State, Dependencies, and Integration
There is no persistent state. Dependencies include `fmt`, `net/http`, `testing`, `storage`, `apierror`, `testify/assert`, `googleapi`, gRPC codes/status, and `errors`. The tests document exactly which wrapped forms are normalized and which are returned unchanged.

## Risks and Test Signals
The equality checks compare concrete error structs containing constructed error values; this is stricter than type-only assertions and can catch accidental wrapping differences. The TODO around wrapped gRPC status creation references an upstream issue, so this area may need updates when grpc-go behavior changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/folder.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/folder.go

## Purpose
This file defines the internal folder DTO used for hierarchical namespace bucket operations and conversion from Storage Control API folder protos.

## Important APIs and Control Flow
`Folder` contains `Name` and `UpdateTime`. `GCSFolder` converts a `controlpb.Folder` into a `*Folder`, extracting the user-visible folder name through `getFolderName` and converting protobuf update time with `AsTime`. `getFolderName` removes the control API prefix `projects/_/buckets/{bucket}/folders/` using `strings.TrimPrefix`.

## State, Dependencies, and Integration
There is no state. Dependencies include `strings`, `time`, and `cloud.google.com/go/storage/control/apiv2/controlpb`. The conversion is used by bucket folder APIs such as get, create, delete, and rename in HNS flows.

## Risks and Test Signals
`strings.TrimPrefix` silently returns the original string if the expected bucket prefix is absent. That is forgiving but can hide malformed control API names. `GCSFolder` assumes `attrs` is non-nil and would panic if passed nil.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/folder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/folder_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/folder_test.go

## Purpose
This file tests folder name extraction and conversion from Storage Control API protos.

## Important APIs and Control Flow
`TestGetFolderName` builds a full control API folder path and expects `getFolderName` to return the suffix. `TestGCSFolder` builds a `controlpb.Folder` with a timestamp and asserts that `GCSFolder` returns the expected name and update time.

## State, Dependencies, and Integration
The tests are local and stateless. Dependencies include `testing`, `time`, `controlpb`, `testify/assert`, and `timestamppb`. They validate the conversion path used by HNS bucket APIs.

## Risks and Test Signals
The test for `GCSFolder` passes `attrs.Name` as a bare folder name, not the full control API path, so it exercises the permissive `TrimPrefix` behavior rather than strict full-path conversion. There is no nil-proto test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/folder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/multi_range_downloader.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/multi_range_downloader.go

## Purpose
This file defines a narrow interface over the Go storage client's multi-range downloader so gcsfuse code can depend on a mockable abstraction.

## Important APIs and Control Flow
`MultiRangeDownloader` has `Add(output io.Writer, offset, length int64, callback func(int64, int64, error))`, `Close`, `Wait`, `Error`, and `GetHandle`. `Add` schedules range downloads into caller-provided writers, `Wait` blocks for pending ranges, `Close` releases downloader resources, `Error` returns aggregate state, and `GetHandle` exposes a resume/read handle byte slice.

## State, Dependencies, and Integration
The interface stores no state itself. It depends only on `io`. `gcs.Bucket.NewMultiRangeDownloader` returns this interface, fake tests exercise it heavily, and mocks implement it indirectly through bucket mock return values.

## Risks and Test Signals
Because this is an interface, behavior depends entirely on implementations. Callback ordering, concurrent `Add`, when errors surface, and `Close` versus `Wait` semantics must stay aligned with the underlying Go storage client and the expectations in `bucket_tests.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/multi_range_downloader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/object.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/object.go

## Purpose
This file defines gcsfuse's internal object metadata models: full `Object`, compact `MinObject`, and `ExtendedObjectAttributes`.

## Important APIs and State
`ContentEncodingGzip` is the canonical gzip content-encoding string. `Object` represents a full GCS object generation with content headers, owner, size, encoding, checksums, media link, metadata, generation, metageneration, storage class, timestamps, component count, content disposition, custom time, event hold, and ACLs. `MinObject` carries the smaller attribute set used in list/stat paths. `ExtendedObjectAttributes` carries the fields omitted from `MinObject`. `Object.IsUnfinalized` and `MinObject.IsUnfinalized` return true when `Finalized` is zero. `MinObject.HasContentEncodingGzip` checks exact gzip encoding.

## Control Flow and Integration
The file contains simple data types and predicates. It integrates with request/response conversion, bucket operations, storage utilities, tests, and higher filesystem logic that needs generation, checksum, gzip, and finalized-state information. The component-count comment documents a deliberate local synthesis: objects without a GCS component count are treated as component count one.

## Risks and Test Signals
Exact string comparison means `GZIP` is not treated as gzip. Zero `Finalized` means unfinalized, which is important for rapid/appendable object paths. Splitting stat results between `MinObject` and `ExtendedObjectAttributes` requires conversion helpers to keep fields aligned.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/object_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/object_test.go

## Purpose
This file tests simple object predicates with ogletest.

## Important APIs and Control Flow
`TestObject` runs the ogletest suite. `ObjectTest` is registered in `init`. Tests cover positive and negative `MinObject.HasContentEncodingGzip`, finalized and unfinalized `MinObject`, and finalized and unfinalized full `Object`.

## State, Dependencies, and Integration
There is no persistent state. Dependencies include `testing`, `time`, and `ogletest`. The tests guard exact gzip matching and zero-time finalized semantics used by read/write behavior.

## Risks and Test Signals
The tests are intentionally narrow. They do not cover all metadata fields, only predicate semantics. Any future change that treats content encoding case-insensitively would require test and behavior updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/request.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/request.go

## Purpose
This file defines the request and response helper types used by the `gcs.Bucket` interface. It is the shared contract between filesystem code, storage backends, fakes, and mocks.

## Important APIs and Types
`CreateObjectRequest` carries name, object metadata, chunk retry/timeout settings, contents, checksum expectations, generation/metageneration preconditions, and chunk callback. `CopyObjectRequest` defines source/destination names, source generation, source metageneration precondition, and destination generation precondition. `MaxSourcesPerComposeRequest` and `MaxComponentCount` encode GCS compose limits. `ComposeObjectsRequest` and `ComposeSource` define composite object creation. `StorageReader` combines `io.ReadCloser` with `ReadHandle`. `ByteRange` models `[Start, Limit)` and formats as `[start, limit)`. `ReadObjectRequest` and `MultiRangeDownloaderRequest` carry name, generation, compressed-read flag, and read handle. `StatObjectRequest`, `GetFolderRequest`, `ListObjectsRequest`, `Listing`, `UpdateObjectRequest`, `DeleteObjectRequest`, `MoveObjectRequest`, and `CreateObjectChunkWriterRequest` define the remaining bucket operations.

## Control Flow and Semantics
The structs are declarative but encode key behavior: zero generation means latest except in preconditions where zero can mean object must not exist; nil pointer update fields mean untouched; empty pointed strings remove fields; metadata update values of nil delete keys; `FetchOnlyFromCache` controls cache-only lookup in stat/list/folder paths; listing delimiter/prefix fields define collapsed runs and pagination ordering; `Projection.String` maps enum values to JSON API projection strings and defaults to `full`.

## State, Dependencies, and Integration
There is no runtime state. Dependencies include `crypto/md5`, `fmt`, `io`, `cloud.google.com/go/storage`, and `google.golang.org/api/storage/v1`. These types are used by bucket implementations, storage utilities, fake tests, mocks, and higher-level filesystem mutation/read flows.

## Risks and Test Signals
Many fields have subtle zero/nil semantics. Pointer preconditions and pointer update fields are especially easy to misuse. `ByteRange` uses `uint64`, while actual backend APIs often use signed offsets/lengths, so conversions must avoid overflow. Cache-only flags must be respected only by implementations with cache support. Compose limits are tested in `bucket_tests.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/request.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper.go

## Purpose
This file provides a helper for constructing `CreateObjectRequest` values used when creating or overwriting objects while preserving source metadata and setting gcsfuse mtime metadata.

## Important APIs and Control Flow
`MtimeMetadataKey` is `gcsfuse_mtime`, written by sync flows as an RFC3339Nano UTC timestamp. `NewCreateObjectRequest` accepts an optional source `Object`, destination object name, optional mtime, and chunk retry/transfer timeouts. With nil source object, it creates a request for `objectName` with generation precondition zero and an empty metadata map. With a source object, it copies source metadata and object attributes, sets generation and metageneration preconditions from the source, and uses `srcObject.Name` as the request name. If `mtime` is non-nil, it overwrites or inserts `gcsfuse_mtime`.

## State, Dependencies, and Integration
There is no persistent state. The function allocates a fresh metadata map and uses `maps.Copy` to avoid aliasing source metadata. Dependencies are `maps` and `time`. It integrates with sync/write paths that need safe preconditioned object recreation.

## Risks and Test Signals
When `srcObject` is non-nil, `objectName` is ignored and `srcObject.Name` is used. That is likely intentional for overwrite/rewrite flows but can surprise callers expecting rename behavior. Only selected attributes are copied; ACL and content language are not all necessarily carried unless included. Tests cover nil source, existing source, nil mtime, metadata copying, and timeout propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper_test.go

## Purpose
This file tests `NewCreateObjectRequest`.

## Important APIs and Control Flow
`TestCreateObjectRequest` creates a current timestamp and table-drives three scenarios: nil source with mtime, existing source with metadata and object attributes plus mtime, and nil source without mtime. Each case calls `NewCreateObjectRequest` and compares the returned request with the expected struct using `testify/assert`.

## State, Dependencies, and Integration
The test is stateless aside from the local timestamp. Dependencies are `testing`, `time`, and `testify/assert`. The expected requests use slice-backed pointer literals for generation preconditions to compare pointer values by pointed content.

## Risks and Test Signals
The test confirms metadata maps are populated with mtime and copied source metadata. It also locks in the behavior that existing-source requests use the source object's name. It does not mutate source metadata after helper return, so map non-aliasing is not directly verified.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/gcs/request_helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock/mock_writer.go -->
# sources/user-network-fs/gcsfuse/internal/storage/mock/mock_writer.go

## Purpose
This file defines a testify-based mock writer implementing the `gcs.Writer` surface for unit tests.

## Important APIs and Control Flow
`Writer` embeds `io.WriteCloser`, `storage.ObjectAttrs`, and `mock.Mock`. `Write`, `Attrs`, `Close`, `Flush`, and `ObjectName` delegate to `mw.Called(...)` and cast returned arguments into the expected types. This lets tests set expectations on upload writes, flushes, close/finalize behavior, object attributes, and object name.

## State, Dependencies, and Integration
State is held by `testify/mock.Mock`, which records calls and configured returns. Dependencies include `io`, `cloud.google.com/go/storage`, and `testify/mock`. It is used with `mock.TestifyMockBucket` and write-path tests that need controlled writer behavior without real GCS.

## Risks and Test Signals
The methods assume the test configured return values with exact types; missing or nil `Attrs`/`Flush` return values will panic during type assertions. This is normal for strict mocks but makes test failures abrupt.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock/mock_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock/testify_mock_bucket.go -->
# sources/user-network-fs/gcsfuse/internal/storage/mock/testify_mock_bucket.go

## Purpose
This file defines the newer testify-based bucket mock for unit tests. It implements `gcs.Bucket` through `mock.Mock`.

## Important APIs and Control Flow
`TestifyMockBucket` implements all bucket methods by calling `m.Called(...)`, type-asserting return arguments, and returning either typed values or errors. Methods include name/type lookup, readers, object create/copy/compose/stat/list/update/delete/move, chunk and appendable writers, finalize/flush, folder operations, multi-range downloader creation, and `GCSName`.

## State, Dependencies, and Integration
State lives in the embedded testify mock. Dependencies are `context`, local `gcs`, and `testify/mock`. This mock integrates with unit tests that prefer testify expectations over deprecated oglemock code.

## Risks and Test Signals
Several methods use simplified call signatures compared with the real interface: for example `CreateObjectChunkWriter` calls `m.Called(ctx, req)` and ignores `chunkSize` and callback in expectation matching. Many return paths assume non-nil typed values when no error is configured and will panic if tests provide nil. This mock must be updated whenever `gcs.Bucket` changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock/testify_mock_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock_bucket.go -->
# sources/user-network-fs/gcsfuse/internal/storage/mock_bucket.go

## Purpose
This file is an auto-generated, deprecated oglemock implementation of `gcs.Bucket` for legacy tests.

## Important APIs and Control Flow
`MockBucket` combines `gcs.Bucket` and `oglemock.MockObject`. `NewMockBucket` returns a `mockBucket` with controller and description. Each method records caller file/line with `runtime.Caller`, calls `controller.HandleMethodCall` with method name and arguments, validates return count, and type-asserts returned values. Implemented methods include compose, copy, create, chunk/appendable writers, finalize, flush, delete, move, folder operations, list, name, bucket type, reader creation, stat, update, `GCSName`, and multi-range downloader creation.

## State, Dependencies, and Integration
State consists of the oglemock controller and description. Dependencies include `fmt`, `runtime`, `unsafe`, local `gcs`, `oglemock`, and `x/net/context`. Legacy tests use this mock where oglemock matchers and expectations remain in place.

## Risks and Test Signals
The file is generated and marked deprecated in favor of the testify mock; manual edits risk being overwritten. It imports `golang.org/x/net/context` while newer code tends to use standard `context`, though the interfaces are assignment-compatible in current Go. The generated methods panic on invalid return counts or wrong return types. `GCSName` is not mocked through the controller and simply returns `obj.Name`, unlike the testify mock.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock_control_client.go -->
# sources/user-network-fs/gcsfuse/internal/storage/mock_control_client.go

## Purpose
This file defines a testify mock for the storage control client used by HNS folder APIs and bucket storage-layout lookup.

## Important APIs and Control Flow
`MockStorageControlClient` embeds `StorageControlClient` and `mock.Mock`. It implements `GetStorageLayout`, `DeleteFolder`, `GetFolder`, `CreateFolder`, and `RenameFolder`. Each method calls `m.Called(ctx, req, opts)` and returns configured proto/operation values or errors. Folder-returning methods use type assertions to allow nil/error cases.

## State, Dependencies, and Integration
State is in the embedded mock. Dependencies include standard `context`, storage control client/protos, `gax`, and `testify/mock`. `fake_storage_util.go` can inject this mock into a fake `StorageHandle`, and storage-handle tests can assert control-client calls without real Storage Control API traffic.

## Risks and Test Signals
Call expectations include the variadic `opts` slice as a single argument, so tests must match that shape. `GetStorageLayout` assumes a non-error success return is a `*controlpb.StorageLayout`, and will panic if nil or wrong typed. The mock covers only the subset of `StorageControlClient` used by current code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/mock_control_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/object_writer.go -->
# sources/user-network-fs/gcsfuse/internal/storage/object_writer.go

## Purpose
This file adapts the Google Cloud Storage `*storage.Writer` to the local `gcs.Writer` interface.

## Important APIs and Control Flow
`ObjectWriter` embeds `*storage.Writer`. `ObjectName` returns `Writer.Name`, and `Attrs` delegates to `Writer.Attrs()`. `Flush`, `Write`, and `Close` are provided by the embedded storage writer, satisfying the rest of `gcs.Writer`.

## State, Dependencies, and Integration
State is the embedded storage writer and its upload session. The file depends on `cloud.google.com/go/storage`. It integrates with bucket upload flows that need to return a local interface rather than the concrete Google client writer.

## Risks and Test Signals
The file comments note unit tests are absent because fake-storage-server does not support multiple versions of the same object even though versioning APIs exist. Behavior therefore depends on integration tests around chunked/resumable uploads. A nil embedded writer would panic on `ObjectName` or `Attrs`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/object_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storage_handle.go -->
# sources/user-network-fs/gcsfuse/internal/storage/storage_handle.go

## Purpose
This file creates and manages storage clients and bucket handles. It selects HTTP, gRPC, or bidi gRPC transports, configures authentication, retries, DirectPath, metrics, control clients, billing project handling, and bucket type detection.

## Important APIs and Types
`StorageHandle` exposes `BucketHandle(ctx, bucketName, billingProject)`. `storageClient` stores HTTP, gRPC, bidi-gRPC, raw control clients with and without GAX retries, a wrapped control client, and `storageutil.StorageClientConfig`. Constants define hidden read-stall env vars, zonal location type, and DirectPath detection retry parameters.

## Control Flow
`createClientOptionForGRPCClient` builds gRPC/control client options: custom endpoint, anonymous/authenticated credentials, Google library auth or token source, bidi reads, local socket address dialer, tracing stats handler, connection pool, user agent, and metrics settings. `setRetryConfig` applies storage retry options using backoff and `storageutil.ShouldRetryWithMonitoring`. `createGRPCClientHandle` enables DirectPath env, builds a gRPC client with optional bidi config, enforces direct connectivity, verifies connectivity with a dummy stat, then applies production retry config. `verifyDirectPathConnectivity` temporarily disables Go SDK retries and accepts only not-found as a successful DirectPath proof. `createHTTPClientHandle` builds auth and HTTP client options, supports JSON reads, custom endpoints, read-stall retry hidden env vars, creates a storage client, and applies retries.

## State, Persistence, and Integration
`NewStorageHandle` optionally creates Storage Control clients when HNS is enabled and the endpoint is not localhost. It creates raw clients with and without default GAX retries, adds folder API retries, wraps layout calls with billing project and stall retry behavior, and stores config for lazy data-client creation. `lookupBucketType` calls `GetStorageLayout` and infers hierarchical, zonal, and Pirlo state. `getClient` chooses bidi gRPC for rapid buckets, non-bidi gRPC with HTTP fallback for gRPC protocol, or HTTP for HTTP protocols. `BucketHandle` combines bucket type, selected storage client, optional user project, appropriate control-client wrapper, bucket name, billing project, and write config into a `bucketHandle`.

## Dependencies and Risks
Dependencies include Google storage/data/control clients, experimental storage options, gax, cfg, logger, storageutil, local gcs errors, OpenTelemetry, OAuth2, gRPC, direct-path side-effect imports, and OS/env APIs. Major risks include process-wide environment mutation for DirectPath and read-stall knobs, lazy client reuse across bucket/billing-project contexts, DirectPath verification reliability, fallback behavior controlled by `GrpcPathStrategy`, and skipping control clients for localhost endpoints. Misclassification in storage layout affects rapid/zonal behavior, retry wrapping, and transport selection.

## Test Signals
This file is not directly tested in the assigned set, but `fake_storage_util.go` constructs `storageClient` instances for tests, `bucket_test.go` validates bucket type predicates consumed here, and control-client mocks support tests of layout/folder behavior elsewhere. Runtime logs around `GetStorageLayout`, DirectPath verification, fallback, and retry setup are important observability signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/storage_handle.go -->
