# subset-b-009564 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/datalake_test.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/datalake_test.go

Purpose: `datalake_test.go` is a live Azure Data Lake Storage integration test suite for the BlobFuse2 `azstorage` component. It validates ADLS account configuration, endpoint normalization, container/filesystem reachability, directory and file CRUD, range reads, copy helpers, symlink metadata, ACL/chmod behavior, block-list based writes, truncation, customer-provided keys, prefix-path behavior, listing/filtering, and config updates.

Important APIs, types, and functions: The suite defines `datalakeTestSuite`, `SetupTest`, `setupTestHelper`, `tearDownTestHelper`, and `cleanupTest`. Tests exercise the public `AzStorage` component methods such as `CreateDir`, `DeleteDir`, `ReadDir`, `StreamDir`, `RenameDir`, `CreateFile`, `OpenFile`, `WriteFile`, `ReadFile`, `ReadInBuffer`, `CopyToFile`, `CopyFromFile`, `CreateLink`, `ReadLink`, `GetAttr`, `Chmod`, `Chown`, `GetFileBlockOffsets`, `FlushFile`, `StageData`, `CommitData`, `TruncateFile`, `ListContainers`, and lower-level `Datalake` helpers including `ReadToFile`, `ReadBuffer`, `ReadInBuffer`, `WriteFromFile`, `WriteFromBuffer`, `UpdateConfig`, `SetFilter`, and `List`. Helper functions include `setupHierarchy`, `getACL`, and `createFileWithData`.

Control flow: `SetupTest` initializes file logging, reads `~/azuretest.json` into shared storage test parameters, creates a generated filesystem/container unless a test overrides configuration, starts a test `AzStorage`, and keeps both service and filesystem clients for direct assertions. Most tests perform an operation through BlobFuse2's abstraction and then verify state directly with Azure SDK clients. Several tests tear down and recreate the suite with specialized config for missing containers, FNS-over-HNS validation, list blocking, CPK, ACL preservation, and custom endpoints. Hierarchy tests build overlapping paths like `base`, `baseb`, and `basec` to verify prefix-sensitive recursive behavior.

State and persistence behavior: The suite mutates live Azure storage: it creates and deletes filesystems, directories, files, symlinks, ACLs, metadata, block blobs, and CPK-protected data. It also creates local temp files for copy tests and local files for CPK download/upload verification. Handles retain `Size`, `Path`, ETag, and cache objects; some flush tests manually construct `handlemap.CacheObj` block lists with dirty or truncated `common.Block` entries to simulate block-cache persistence before committing to storage.

Dependencies and integration points: This file depends on Azure SDK ADLS filesystem, directory, file, and service clients, Azure Blob blockblob APIs, shared BlobFuse2 `common`, `internal`, and `handlemap` packages, generated storage test configuration, and Testify suites/assertions. It integrates ADLS storage with the BlockBlob fallback used for block-list operations and with the BlobFuse2 component pipeline through `newTestAzStorage`.

Risks: These tests require live credentials and `~/azuretest.json`; failures can come from account policy, network latency, throttling, container cleanup delays, or CPK/key mismatch rather than local code defects. Many assertions assume service ordering, metadata preservation, and exact Azure error translations. Tests that sleep for mtime changes or move large random buffers can be slow or flaky. The suite sometimes ignores errors from helper calls when setup has already failed, which can obscure root causes.

Test signals: Coverage is broad and behavior-focused. It covers default config, endpoint conversion, missing filesystem errors, HNS validation, directory recursion, prefix path deletion/renaming/listing, file overwrite/append holes with zero filling, block blob conversion, range reads including ETag capture, truncation smaller/equal/larger for simple and chunked files, flush of dirty/truncated cache blocks, CPK download/upload/create/rename, chmod ACL mapping, ignored chown, ACL preservation flags, blob filters, list markers/counts, and config propagation into nested BlockBlob config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/datalake_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/policies.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/policies.go

Purpose: `policies.go` defines custom Azure SDK pipeline policies used by BlobFuse2 storage clients: a telemetry policy, a service API version override policy, and a rate-limiting policy for operations and download bandwidth.

Important APIs, types, and functions: `blobfuseTelemetryPolicy` and `newBlobfuseTelemetryPolicy` prepend BlobFuse2 telemetry to the request `User-Agent`. `serviceVersionPolicy` and `newServiceVersionPolicy` overwrite the `x-ms-version` header. `rateLimitingPolicy` and `newRateLimitingPolicy` create `golang.org/x/time/rate` limiters for read bytes per second and operations per second. `(*rateLimitingPolicy).Do` waits on the ops limiter for every request and waits on the bandwidth limiter only for `GET` requests with a `x-ms-range` or `Range` header parsed by `parseRangeHeader`.

Control flow: Each policy implements `policy.Policy.Do`, mutates or throttles the request, and then calls `req.Next()`. The rate-limiter constructor builds 10-second burst windows and clamps burst sizes to `math.MaxInt` to avoid overflow on small `int` platforms. On request execution, ops limiting occurs first. Bandwidth limiting then inspects range headers for GET downloads and waits for exactly the requested byte count before forwarding the request.

State and persistence behavior: Policies hold in-memory limiter state only. Token buckets persist across requests that share the same client pipeline. No storage state is modified directly, but throttling changes request timing and cancellation behavior because waits use the request context.

Dependencies and integration points: The file depends on Azure SDK `policy`, Go `net/http`, `x/time/rate`, BlobFuse2 `common` headers/logging, and `parseRangeHeader` plus `X_Ms_Range`/`RangeHeader` constants from `utils.go`. `getAzStorageClientOptions` installs telemetry and optional service-version policies as per-call policies and installs rate limiting as a per-retry policy when configured.

Risks: Invalid range headers cause the policy to fail the request before it reaches storage. Bandwidth limiting is skipped for GET requests without range headers, so callers using full-object GETs are not throttled by bytes. The lower-case `x-ms-range` map lookup is intentional for SDK behavior but sensitive to header canonicalization changes. Per-retry placement means retries consume limiter tokens too. Very high configured rates are clamped only at burst size; token limits can still represent extreme values.

Test signals: `policies_test.go` verifies ops delays, range-based bandwidth delays for both `Range` and lower-case `x-ms-range`, no-limit fast path, and skip behavior for non-GET methods. There are no direct tests here for telemetry header concatenation, service version override, context cancellation, malformed range policy errors, or burst clamping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/policies.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/policies_test.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/policies_test.go

Purpose: `policies_test.go` validates the custom Azure SDK rate-limiting policy used by BlobFuse2 azstorage clients.

Important APIs, types, and functions: The file defines `mockTransport`, `policiesTestSuite`, `SetupTest`, `TearDownTest`, and tests for `newRateLimitingPolicy`. Tests construct Azure SDK runtime pipelines with the policy in `PerRetry` and a mock transport returning HTTP 200. Assertions use Testify suite/assert helpers and the BlobFuse2 logger is set to silent debug mode for isolation.

Control flow: Each test creates a pipeline, builds an SDK request, and invokes `pipeline.Do`. The ops and bandwidth tests consume the 10-second burst capacity, then measure the next request and require at least roughly 900 ms of delay for a 1 op/sec or 100 bytes/sec limiter. The no-limit and non-GET tests execute loops expected to remain below 100 ms.

State and persistence behavior: The tests depend on rate limiter token-bucket state across repeated requests in a single pipeline. They do not touch Azure storage or persistent filesystem state. Logger state is initialized and destroyed per test to avoid cross-suite contamination.

Dependencies and integration points: The suite uses Azure SDK `runtime.NewPipeline`/`NewRequest`, BlobFuse2 `common` and `log`, Go `net/http`, `context`, and `time`. It indirectly depends on `parseRangeHeader` from `utils.go` because bandwidth limiting is range-size based.

Risks: Timing assertions can be flaky on overloaded CI hosts or systems with coarse scheduling. Tests reuse the same request object for repeated `pipeline.Do` calls, which matches the policy's needs but may not model all SDK request lifecycles. Coverage focuses on rate limiting only and does not validate telemetry or service-version policies in the same file.

Test signals: Positive signals include explicit coverage for ops limiting, byte limiting with `Range`, byte limiting with lower-case `x-ms-range`, disabled limiters, and non-GET bypass. Missing signals include malformed range error behavior, context cancellation while waiting, burst clamping, and mixed ops-plus-bandwidth limiting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/policies_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/utils.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/utils.go

Purpose: `utils.go` contains shared azstorage support code for Azure SDK client options, logging, HTTP transport configuration, cloud selection, storage error translation, metadata interpretation, content types, access tiers, ACL/mode conversion, path/key sanitization, auth auto-detection, ETag/time mutation, and range parsing.

Important APIs, types, and functions: Client setup flows through `getAzStorageClientOptions`, `getAzBlobServiceClientOptions`, `getAzDatalakeServiceClientOptions`, `getSDKLogOptions`, `setSDKLogListener`, `newBlobfuse2HttpClient`, and `getCloudConfiguration`. Error mapping is handled by `storeBlobErrToErr` and `storeDatalakeErrToErr` with constants like `ErrFileNotFound`, `InvalidRange`, and `ErrPathTooDeep`. Metadata/content helpers include `parseMetadata`, `ContentTypes`, `getContentType`, and `populateContentType`. Access and ACL helpers include `AccessTiers`, `getAccessTierType`, `getACLPermissions`, `getFileModeFromACL`, `getFileMode`, and `writePermission`. Miscellaneous helpers include `removePrefixPath`, `sanitizeSASKey`, `autoDetectAuthMode`, `removeLeadingSlashes`, `modifyLMTandEtag`, `sanitizeEtag`, and `parseRangeHeader`.

Control flow: Client option creation builds retry options, composes BlobFuse telemetry with distro information, adds optional service-version override from `AZURE_STORAGE_SERVICE_API_VERSION`, installs rate-limiting policies from configured read Mbps and IOPS, and creates an HTTP transport using either explicit proxy config or environment proxies. Logging is enabled only for non-silent debug logging unless `BLOBFUSE_DISABLE_SDK_LOG=true`. Metadata parsing marks directories and symlinks based on well-known metadata keys. ACL conversion extracts owner or named-user permissions, applies the mask for named users, appends group/other permissions, and converts the first nine permission characters to `os.FileMode`.

State and persistence behavior: Most helpers are stateless, but `ContentTypes` and `AccessTiers` are package-level maps, and `populateContentType` mutates the global content-type map. SDK log listener setup mutates global Azure SDK logging state. Client options hold reusable transport and limiter state when installed. `modifyLMTandEtag` mutates an `internal.ObjAttr` in place.

Dependencies and integration points: The file integrates Azure SDK core, cloud, log, policy, blob, bloberror, service, datalake service, and datalakeerror packages with BlobFuse2 `common`, `common/log`, and `internal`. Policies from `policies.go` are created here. ACL and metadata helpers feed ADLS object attributes; content type and access tier helpers feed upload/config behavior; error mapping feeds syscall-like behavior in higher storage operations.

Risks: `removePrefixPath` indexes `path[0]` after trimming and can panic if the trim produces an empty string. ACL parsing uses substring indexes after `strings.Index` without validating all keys, so malformed ACL strings can panic. `extractNamedUserACL` computes `idx` after adding `len(key)`, making its `idx == -1` check ineffective if the key is absent. `populateContentType` mutates a global map without synchronization. Debug SDK logging can expose allowed headers/query parameters, so allowlists need care. `parseRangeHeader` rejects open-ended ranges, which is safe for limiter accounting but may reject otherwise valid HTTP range syntax when used by the policy.

Test signals: `utils_test.go` covers content type defaults and overrides, access tiers, mode/ACL conversion, SAS and ETag sanitization, blob/datalake option construction with proxies, endpoint formatting helpers from related files, auth auto-detection priority, leading-slash removal, datalake error mapping, prefix removal, and range parsing. It does not fully cover blob error mapping, malformed ACL panic cases, global map concurrency, SDK listener behavior, service-version env behavior, or proxy parse failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/utils_test.go -->
# sources/user-network-fs/blobfuse2/component/azstorage/utils_test.go

Purpose: `utils_test.go` is the unit test suite for azstorage utility helpers around content types, access tiers, permissions, client options, endpoint formatting, auth-mode detection, error mapping, path manipulation, and range parsing.

Important APIs, types, and functions: The file defines `utilsTestSuite` and table-driven helper structs for content types, access tiers, file modes, endpoints, and protocols. It tests `getContentType`, `populateContentType`, `getAccessTierType`, `getFileMode`, `getFileModeFromACL`, `sanitizeSASKey`, `sanitizeEtag`, `getAzBlobServiceClientOptions`, `getAzDatalakeServiceClientOptions`, `formatEndpointAccountType`, `formatEndpointProtocol`, `autoDetectAuthMode`, `removeLeadingSlashes`, `storeDatalakeErrToErr`, `removePrefixPath`, and `parseRangeHeader`.

Control flow: Tests are grouped as Testify suite methods. Many are table-driven with `s.Run` subtests. Content type tests first validate fallback behavior, then mutate the global map with JSON and re-query. Endpoint tests exercise standard public cloud endpoints, zonal endpoints, China/Germany/Government clouds, private endpoints, protocol insertion, and intentionally malformed endpoint strings. Error mapping tests synthesize `azcore.ResponseError` values with datalake error codes.

State and persistence behavior: The suite mostly avoids external persistence. It mutates package global `ContentTypes` through `populateContentType`, sets a silent logger for permission parsing tests, and constructs client option objects with transport/proxy settings. No live Azure calls are made.

Dependencies and integration points: Tests depend on Azure SDK `azcore`, `to`, blob access tiers, datalake errors, BlobFuse2 `common` and `log`, Testify, and endpoint/auth types defined elsewhere in the azstorage package. They provide safety signals for helpers consumed by both Blob and ADLS storage implementations.

Risks: Because `ContentTypes` is global, test order or parallelization could leak the `.tst` override into other tests. Some endpoint tests assert preservation of malformed strings as false positives, which documents current behavior but can lock in questionable URI formation. The suite does not test concurrent access to global maps or failure branches in HTTP client construction.

Test signals: Coverage is strong for mapping tables and normal parsing behavior: many extensions including case-insensitive paths, all configured access tiers, ACL mask behavior, auth priority order, prefix stripping, datalake error categories, and valid/invalid byte ranges. Missing signals include blob error mapping, cloud configuration detection, SDK log listener options, metadata folder/symlink parsing, `removePrefixPath` empty-trim panic, and ACL strings missing required fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/azstorage/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/block.go

Purpose: `block.go` defines the core in-memory block buffer type used by the BlobFuse2 block cache and helper state for block upload/download tracking.

Important APIs, types, and functions: Block flags include `BlockFlagFresh`, `BlockFlagDownloading`, `BlockFlagUploading`, `BlockFlagDirty`, `BlockFlagSynced`, and `BlockFlagFailed`. Status channel values include `BlockStatusDownloaded`, `BlockStatusUploaded`, `BlockStatusDownloadFailed`, and `BlockStatusUploadFailed`. `Block` stores offset, block id, readiness channel, `common.BitMap64` flags, memory-mapped data, and a list node. `blockInfo` records remote block IDs, commit state, and size. Methods include `AllocateBlock`, `Delete`, `ReUse`, `Uploading`, `Ready`, `Unblock`, `Dirty`, `NoMoreDirty`, `IsDirty`, `Failed`, and `IsFailed`.

Control flow: `AllocateBlock` validates size, uses `syscall.Mmap` to allocate an anonymous private read/write buffer, initializes a fresh block with id `-1`, and deliberately leaves `state` nil until reuse. `ReUse` resets identity, offset, flags, and creates a buffered readiness channel. Download/upload code calls `Ready` once with a status, and the first reader closes the channel through `Unblock` so later readers do not block.

State and persistence behavior: Block data is held in an mmap-backed byte slice and must be released with `Delete`, which calls `syscall.Munmap` and nils the data. Flags encode dirty, synced, failed, and transfer state in memory. The readiness channel coordinates goroutines but is not persisted. `blockInfo` mirrors staged/committed remote block-list state for later commits.

Dependencies and integration points: This file depends on Go `container/list`, `syscall`, and BlobFuse2 `common.BitMap64`. `block_cache.go` uses `Block` instances in handle cooked/cooking lists, block pools, download/upload workers, disk cache reads, and commit-block generation.

Risks: Callers must avoid using a block after `Delete` because `data` is nil and the mmap is gone. Closing `state` more than once would panic, so ownership of `Unblock` matters. `Ready` silently drops a status if the buffered channel is full; the design assumes one status per transfer. `AllocateBlock` converts `uint64` size to `int`, so extremely large sizes can overflow on unsupported configurations before `Mmap`.

Test signals: No direct tests are in this file. Behavior is indirectly covered by block cache tests elsewhere and by integration paths in `datalake_test.go` that exercise block staging/flush semantics. Missing direct coverage includes mmap allocation failure, double `Delete`, double `Unblock`, status drop behavior, and flag transitions in isolation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block_cache.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/block_cache.go

Purpose: `block_cache.go` implements the BlobFuse2 `block_cache` pipeline component, providing memory-backed block caching, optional disk caching, prefetching, background download/upload scheduling, lazy write close behavior, block-list commits, and cache invalidation for filesystem operations.

Important APIs, types, and functions: `BlockCache` embeds `internal.BaseComponent` and implements lifecycle/config methods `Name`, `SetName`, `SetNextComponent`, `Start`, `Stop`, `GenConfig`, and `Configure`. File-operation methods include `CreateFile`, `OpenFile`, `FlushFile`, `ReleaseFile`, `ReadInBuffer`, `WriteFile`, `DeleteDir`, `RenameDir`, `DeleteFile`, `RenameFile`, `SyncFile`, `TruncateFile`, and `StatFs`. Internal coordination helpers include `prepareHandleForBlockCache`, `validateBlockList`, `getBlock`, `startPrefetch`, `refreshBlock`, `lineupDownload`, `download`, `checkBlockConsistency`, `getOrCreateBlock`, `stageBlocks`, `lineupUpload`, `upload`, `commitBlocks`, `getBlockIDList`, `stageZeroBlock`, `diskEvict`, `checkDiskUsage`, and `shouldCommitAndDownload`.

Control flow: `Configure` reads block size, memory size, disk path, disk size, timeout, prefetch count, parallelism, prefetch-on-open, consistency, cleanup, and lazy-write settings, then validates memory and disk constraints. `Start` creates a `BlockPool`, starts a download/upload `ThreadPool`, and starts the disk TLRU policy when disk cache is enabled. Reads lock the file handle, locate or schedule blocks, wait on block readiness, copy bytes to the caller buffer, and optionally continue sequential prefetch. Writes lock the handle, locate or create blocks, download existing committed data when partial overwrite requires it, copy incoming data, mark blocks and handle dirty, and stage old dirty blocks when the per-handle queue grows. Flush commits staged block IDs in order and fills holes with zero blocks when sparse writes require it.

State and persistence behavior: In-memory state includes per-handle cooked and cooking lists, handle value maps keyed by block index, block-list metadata, ETags, random-read counters, a global block pool, thread pool, per-file locks, disk node map, max disk usage state, and lazy close wait group. Disk cache state is stored under `tmpPath` using filenames formed from path and block id, managed by a TLRU policy, and optionally protected with CRC64 xattrs when consistency is enabled. Remote persistence occurs through next-component calls such as `ReadInBuffer`, `StageData`, `CommitData`, `DeleteFile`, `RenameFile`, and `TruncateFile`.

Dependencies and integration points: The component integrates with BlobFuse2's component pipeline via `internal.Component` registration in `init`, with config flags under `block_cache`, with `handlemap.Handle`, with `common` locking/temp-cache/stat helpers, with `tlru` disk eviction, and with downstream storage components implementing block staging, commit, read, rename, delete, and truncate operations. It also has a stream mode integration via `bc.stream.Configure(true)` when `common.IsStream` is set.

Risks: This code is concurrency-sensitive: readiness channels, per-handle locks, per-file locks, cooked/cooking list membership, and background worker retries must stay consistent. `ReleaseFile` waits on in-flight downloads before returning blocks to the pool; failed or stuck workers can delay close. Disk cache filenames combine path and block index and require careful invalidation on rename/delete. Sparse write and partial-block logic stages zero filler blocks and recursively restages blocks, which is complex and sensitive to off-by-one block sizes. Lazy write returns from close before upload finishes, shifting error visibility to background completion. Strong consistency xattrs use the name `user.md5sum` while storing CRC64 bytes, which may confuse diagnostics.

Test signals: Direct tests are not in this subset, but `datalake_test.go` exercises downstream block-list flush, append, truncate, dirty block, zero-fill, and permission preservation behavior that block cache relies on. Expected additional coverage would include block pool exhaustion, random-read prefetch cutoff, disk cache hit/miss and eviction, CRC mismatch recovery, upload/download retry failure, lazy-write shutdown, rename/delete invalidation, and `StatFs` cache accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block_cache.go -->
