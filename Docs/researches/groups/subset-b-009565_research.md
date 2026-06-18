# Research Group subset-b-009565

This grouped report covers Blobfuse2 component code and tests for block cache support, custom plugin loading, entry list caching, and file cache behavior. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block_cache_test.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/block_cache_test.go

## Purpose

`block_cache_test.go` is the main integration-style unit suite for the Blobfuse2 block cache component. It exercises configuration, read prefetching, disk-cache spillover, block-list validation, write-back upload, sparse writes, overwrite races, committed and uncommitted block handling, lazy write, stream-to-block-cache compatibility, and strong consistency metadata.

## Important APIs, Types, and Functions

The suite defines `blockCacheTestSuite`, `testObj`, `setupPipeline`, `cleanupPipeline`, `randomString`, `getFakeStoragePath`, `getTestFileName`, and `computeMD5`. Tests construct a loopback-backed pipeline using `loopback.NewLoopbackFSComponent`, `NewBlockCacheComponent`, and the component lifecycle methods `Configure`, `Start`, and `Stop`. Most assertions target `BlockCache` methods including `CreateFile`, `OpenFile`, `ReadInBuffer`, `WriteFile`, `FlushFile`, `ReleaseFile`, `SyncFile`, `RenameFile`, `DeleteFile`, `RenameDir`, `DeleteDir`, `StatFs`, `validateBlockList`, `stageBlocks`, and `checkDiskUsage`.

## Control Flow

Each test builds a temporary fake storage root and disk cache root, loads YAML-like config through `config.ReadConfigFromReader`, wires block cache above loopback storage, and starts both components. Read tests create files directly in fake storage, open them through block cache, then read sequential or random offsets to drive `getBlock`, prefetch, and disk/memory eviction paths. Write tests create or open handles through block cache, write byte ranges at aligned and unaligned offsets, flush or release the handle, and compare storage size or MD5 output to a reference local file. Race-focused tests deliberately stage blocks, rewrite already staged blocks, read blocks while writes are pending, and validate that the cooked/cooking lists settle correctly.

## State and Persistence Behavior

The test suite validates state held in temporary directories, handle buffer lists, handle dirty flags, block maps, disk cache files named with block suffixes, xattrs for strong consistency, and global `common.IsStream`. Cleanup stops components and removes temporary directories. Several tests rely on asynchronous cleanup or upload behavior and use sleeps, polling, or release operations to wait for state transitions.

## Dependencies and Integration Points

Dependencies include `common`, `config`, `log`, `loopback`, `internal`, `memory`, `testify`, and operating-system tools such as `nproc`, `free`, and `df`. The tests integrate block cache with the loopback component rather than a cloud backend, giving broad component-level signal without Azure service calls.

## Risks and Edge Cases

The suite is environment-sensitive: free memory, disk size, permissions, xattr support, external shell command output, and timing can affect results. The 50 GiB mmap failure test and long sleeps can be brittle on constrained systems. The tests cover many high-risk cases: invalid prefetch/memory/disk config, temp-path conflicts, disk-threshold decisions, sparse file holes, partial block overwrites, block index limits, failed block downloads, reads of staged blocks, uncommitted block validation, prefetch-disabled behavior, lazy write deferral, and strong consistency xattr refresh.

## Test Signals

Passing this suite gives strong confidence that block cache preserves data across reads, random writes, sparse writes, flush/release sequences, and local disk cache interactions. It also signals that read prefetch does not overgrow handle block lists, that write-back can recover from staged or committed block overlap, and that block cache still interoperates with stream component compatibility settings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block_test.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/block_test.go

## Purpose

`block_test.go` verifies the low-level `Block` abstraction used by block cache for mmap-backed block buffers and per-block state signaling.

## Important APIs, Types, and Functions

The suite defines `blockTestSuite` and tests `AllocateBlock`, `Delete`, `ReUse`, `Ready`, `Unblock`, `Uploading`, `Dirty`, `NoMoreDirty`, and `IsDirty`. It checks block status constants through calls using `BlockStatusDownloaded` and `BlockStatusUploaded`.

## Control Flow

Allocation tests request invalid, small, large, and huge block sizes. State tests allocate a block, call `ReUse` to reset id, offset, flags, and state channel, then send status through `Ready`, consume it from the channel, close channels with `Unblock`, and toggle dirty/failed/uploading state.

## State and Persistence Behavior

The file focuses on transient in-memory state. It checks that mmap data exists for valid allocations, that `Delete` clears `data`, that `ReUse` recreates a buffered channel, and that dirty flags survive failed/upload transitions until cleared.

## Dependencies and Integration Points

It uses `testify` suite/assert and directly targets `block.go`. These tests protect assumptions used by `BlockPool`, `ThreadPool`, and `BlockCache` when blocks move between downloading, writing, uploading, and free-list states.

## Risks and Edge Cases

Tests include nil data and non-mmap data passed to `Delete`, which should return errors instead of silently corrupting allocator state. The huge allocation test depends on system mmap behavior and may be sensitive to overcommit policy.

## Test Signals

Passing tests show that blocks fail fast for invalid sizes, can allocate large buffers, reject invalid frees, and maintain channel/dirty semantics required by readers and uploaders.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/blockpool.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/blockpool.go

## Purpose

`blockpool.go` implements a bounded pool of preallocated `Block` objects for the block cache. It limits memory consumption, separates priority and normal block availability, and asynchronously zeroes released buffers before reuse.

## Important APIs, Types, and Functions

`BlockPool` owns `blocksCh`, `priorityCh`, `zeroBlock`, `resetBlockCh`, `wg`, `blockSize`, and `maxBlocks`. Public functions are `NewBlockPool`, `Terminate`, `Usage`, `MustGet`, `TryGet`, and `Release`; helper functions are `releaseBlock` and the background method `resetBlock`.

## Control Flow

`NewBlockPool` validates `blockSize` and `memSize`, computes `blockCount`, reserves 10 percent of blocks for `priorityCh`, keeps the final block as a zero-filled template, and starts the reset goroutine. `MustGet` waits up to five seconds for either priority or normal blocks, preferring the select cases as written, then calls `ReUse`. `TryGet` only takes from `blocksCh` and returns nil if normal capacity is empty. `Release` sends blocks to the reset channel or deletes them if reset backlog is full. `resetBlock` copies `zeroBlock.data` into each released block and returns it first to `priorityCh`, then to `blocksCh`, deleting it if both are full.

## State and Persistence Behavior

All state is process-local and channel-backed. Memory is mmap-backed through `AllocateBlock`; `Terminate` closes reset processing, waits for the goroutine, closes free channels, deletes the zero block, and drains/deletes remaining pooled blocks. `Usage` counts blocks missing from free and reset channels, so the reserved zero block contributes to usage.

## Dependencies and Integration Points

The pool depends on `Block` allocation/deletion from `block.go`, `sync.WaitGroup`, `time`, and Blobfuse logging. `BlockCache` uses the pool to bound memory for read/write blocks.

## Risks and Edge Cases

`releaseBlock` reads from closed channels until it receives nil, which works for closed channels but would block if called on an open empty channel. `MustGet` can wait five seconds in tests or callers when exhausted. `TryGet` ignores priority blocks, so priority capacity is not available to nonblocking normal callers. `Release` accepts any `*Block`; nil or already deleted blocks would panic later in `resetBlock`.

## Test Signals

`blockpool_test.go` covers invalid config, allocation layout, usage percentages, exhaustion behavior, zeroing after release, and cleanup after `Terminate`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/blockpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/blockpool_test.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/blockpool_test.go

## Purpose

`blockpool_test.go` validates `BlockPool` allocation, channel sizing, usage reporting, buffer exhaustion, reset-to-zero behavior, and termination cleanup.

## Important APIs, Types, and Functions

The suite defines `blockpoolTestSuite`, `validateNullData`, `getBlocks`, and `releaseBlocks`. It exercises `NewBlockPool`, `MustGet`, `TryGet`, `Release`, `Usage`, and `Terminate`.

## Control Flow

Tests allocate pools with invalid and valid sizes, check channel lengths and zero block state, get blocks through blocking and nonblocking APIs, release blocks, wait for the reset goroutine, and re-check pool size. Exhaustion tests drain available blocks, assert `TryGet` returns nil and `MustGet` eventually errors, then release all blocks. Reset tests dirty bytes before release, wait for reset, and assert reissued blocks are zero-filled.

## State and Persistence Behavior

The file observes channel-backed state (`blocksCh`, `priorityCh`, `resetBlockCh`), mmap buffer content, and `zeroBlock.data`. Tests use sleeps to allow asynchronous `resetBlock` to finish.

## Dependencies and Integration Points

It depends on `math/rand`, `time`, `testify`, and the local block pool implementation. It indirectly validates `Block.ReUse` and `Block.Delete` through pool operations.

## Risks and Edge Cases

The tests are timing-sensitive because reset completion is assumed after one or two seconds. They also encode exact capacity assumptions, including that a five-block pool has four usable normal blocks and a reserved zero block.

## Test Signals

Passing tests confirm that the pool respects memory limits, does not hand out stale data after release, reports usage consistently, and frees mmap data during termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/blockpool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/stream.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/stream.go

## Purpose

`stream.go` implements the legacy/config-compatibility `stream` component facade that translates streaming configuration into `block_cache` configuration. It does not perform I/O itself; it maps stream cache knobs into block cache block size, prefetch, and memory size settings.

## Important APIs, Types, and Functions

The file defines `Stream`, `StreamOptions`, constants `compStream` and `mb`, methods `Name` and `Configure`, and an `init` function that registers command-line flags. `StreamOptions` includes `block-size-mb`, `buffer-size-mb`, `max-buffers`, `file-caching`, `read-only`, and v1 compatibility fields `stream-cache-mb` and `max-blocks-per-file`.

## Control Flow

`Configure` unmarshals `stream` config plus global `read-only`. If `max-blocks-per-file` is set, it derives `BufferSize` from block size times max blocks. If `stream-cache-mb` is set with a buffer size, it derives `CachedObjLimit`, clamping to at least one. It checks whether requested memory exceeds `memory.FreeMemory`, logs the final settings, and writes translated values into `block_cache.block-size-mb`, `block_cache.prefetch`, and `block_cache.mem-size-mb`.

## State and Persistence Behavior

The component stores only parsed sizing fields on `Stream`; the significant state mutation is writing into the process-wide config registry before block cache configuration consumes those keys.

## Dependencies and Integration Points

It depends on Blobfuse `config`, `log`, `internal.BaseComponent`, and `pbnjay/memory`. It integrates with `BlockCache` through `config.Set` and with CLI registration through `config.AddFloat64Flag`, `AddIntFlag`, and `AddUint64Flag`.

## Risks and Edge Cases

The memory check multiplies `BufferSize * CachedObjLimit * mb`; overflow or unset values can hide bad config. `FileCaching` and `readOnly` are logged but not otherwise enforced here. This compatibility shim depends on block cache using the translated config keys later in startup.

## Test Signals

`block_cache_test.go` includes `TestZZZZZStreamToBlockCacheConfig`, which sets stream config, enables `common.IsStream`, and checks that block cache receives the expected block size and memory size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/threadpool.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/threadpool.go

## Purpose

`threadpool.go` provides a small worker pool used by block cache to execute asynchronous block downloads and uploads with separate priority and normal queues.

## Important APIs, Types, and Functions

`ThreadPool` holds worker count, close channel, wait group, priority and normal work channels, and reader/writer callbacks. `workItem` carries the handle, block, prefetch flag, failure count, upload flag, block id, and ETag. Functions are `newThreadPool`, `Start`, `Stop`, `Schedule`, and worker method `Do`.

## Control Flow

`newThreadPool` rejects zero workers or nil reader callbacks, then sizes `priorityCh` to `count*2` and `normalCh` to `count*5000`. `Start` launches all workers and marks roughly 10 percent as priority-only workers. `Schedule` sends urgent items to `priorityCh` and normal items to `normalCh`. `Do` loops on channel selects until `close` receives a value; priority-only workers ignore `normalCh`, while normal workers service both queues. Items with `upload=true` call `writer`, otherwise `reader`.

## State and Persistence Behavior

State is in goroutines and buffered channels only. `Stop` sends one close token per worker, waits for all workers, and closes channels. No durable state is written.

## Dependencies and Integration Points

The pool depends on `sync` and `handlemap.Handle`. It is integrated by `BlockCache` for `download` and `upload` scheduling, with work item fields avoiding handle-lock deadlocks when ETags are needed inside worker callbacks.

## Risks and Edge Cases

If `writer` is nil and an upload item is scheduled, workers will panic. `Schedule` can block when queues are full. Worker select reads from closed work channels may receive nil work items if channels close before workers stop, though `Stop` sends close tokens before closing queues.

## Test Signals

`threadpool_test.go` verifies constructor validation, start/stop, urgent and normal scheduling, priority throughput, and writer callback routing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/threadpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/threadpool_test.go -->
# sources/user-network-fs/blobfuse2/component/block_cache/threadpool_test.go

## Purpose

`threadpool_test.go` validates construction and scheduling behavior of the block cache worker pool.

## Important APIs, Types, and Functions

The suite defines `threadPoolTestSuite` and tests `newThreadPool`, `Start`, `Stop`, and `Schedule` using inline reader and writer callbacks. It uses atomic counters to count callback invocations.

## Control Flow

Constructor tests reject zero-worker and nil-reader configurations, then accept a valid one-worker pool. Start/stop tests launch workers and close them cleanly. Scheduling tests enqueue normal and urgent work items, sleep to allow workers to process, and assert callback counts. Writer-specific tests schedule upload work and assert only the writer callback runs.

## State and Persistence Behavior

The file observes in-memory worker goroutines, buffered channels, and atomic counters. It does not touch filesystem state.

## Dependencies and Integration Points

It depends on `sync/atomic`, `time`, `testify`, and the local thread pool implementation. It protects the scheduling layer used by block cache read prefetch and write upload paths.

## Risks and Edge Cases

The tests rely on one-second sleeps rather than explicit synchronization for all scheduled items, so heavily loaded systems could make them flaky. They do not cover nil writer with upload items or queue saturation.

## Test Signals

Passing tests confirm that workers start, exit, route urgent/normal work, and dispatch upload work to writer callbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/block_cache/threadpool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/custom/custom.go -->
# sources/user-network-fs/blobfuse2/component/custom/custom.go

## Purpose

`custom.go` loads external Blobfuse components from Go plugins listed in `BLOBFUSE_PLUGIN_PATH` and registers them with the internal component registry.

## Important APIs, Types, and Functions

The main function is `initializePlugins`; package `init` calls it and exits the process on failure. Plugins must export `GetExternalComponent` with the exact signature `func() (string, func() exported.Component)`.

## Control Flow

`initializePlugins` reads `BLOBFUSE_PLUGIN_PATH`, returns nil when empty, splits a colon-separated path list, skips non-`.so` entries with an error log, opens each `.so` with `plugin.Open`, looks up `GetExternalComponent`, type-asserts the symbol to the expected function signature, calls it to obtain component name and constructor, and registers the component via `internal.AddComponent`.

## State and Persistence Behavior

State changes are process-global: loaded plugins remain in the Go plugin runtime and successful components are added to the Blobfuse component registry. On init failure the package logs, prints a message, and terminates the process with `os.Exit(1)`.

## Dependencies and Integration Points

The file depends on standard `plugin`, `os`, `strings`, `time`, and Blobfuse `log`, `exported`, and `internal` packages. It is the dynamic extension point for out-of-tree components.

## Risks and Edge Cases

Go plugins are version- and build-configuration-sensitive. Any invalid `.so`, missing symbol, or wrong signature aborts startup through package init. Non-`.so` entries are skipped rather than returned as errors. `strings.SplitSeq` means empty segments may be iterated depending on environment string shape.

## Test Signals

`custom_test.go` covers empty plugin path and invalid `.so` path. The disabled valid-plugin test documents known Go plugin package-version issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/custom/custom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/custom/custom_test.go -->
# sources/user-network-fs/blobfuse2/component/custom/custom_test.go

## Purpose

`custom_test.go` validates basic plugin-loader behavior for the custom component integration path.

## Important APIs, Types, and Functions

The suite defines `customTestSuite` and directly calls `initializePlugins`. Active tests are `TestInitializePluginsInvalidPath` and `TestInitializePluginsEmptyPath`; a valid-plugin build/load test is present but commented out.

## Control Flow

The invalid-path test sets `BLOBFUSE_PLUGIN_PATH` to a nonexistent `.so` path and expects `initializePlugins` to return an error from `plugin.Open`. The empty-path test clears the variable and expects no error.

## State and Persistence Behavior

Tests mutate process environment with `os.Setenv`. The disabled test would have created `.so` files and registered external components, but active tests do not persist files.

## Dependencies and Integration Points

The file depends on `os`, `testing`, and `testify`. It exercises `custom.go` directly rather than through Blobfuse startup so package `init` process exit behavior is not under test.

## Risks and Edge Cases

Environment variables are global to the process; if tests run in parallel with other plugin-loading tests, state could leak. The most important success path, loading a valid plugin and registering its component, is intentionally disabled because Go plugins can report package-version mismatches when built under test.

## Test Signals

Passing tests show that no plugin configuration is accepted and invalid plugin paths are surfaced as errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/custom/custom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache.go -->
# sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache.go

## Purpose

`entry_cache.go` implements a read-only directory listing cache for `StreamDir` results. It stores paged directory entries keyed by path and continuation token, with TLRU expiration.

## Important APIs, Types, and Functions

`EntryCache` embeds `internal.BaseComponent` and holds `cacheTimeout`, `pathLocks`, `pathLRU`, and `pathMap`. `pathCacheItem` stores children and next token. Public component methods include `Name`, `SetName`, `SetNextComponent`, `Start`, `Stop`, `Configure`, and `StreamDir`; internal helpers include `pathEvict`, `NewEntryCacheComponent`, and package `init`.

## Control Flow

`Configure` requires global `read-only` to be true, loads `entry_cache.timeout-sec`, constructs a TLRU with capacity 1000 and the configured timeout, and initializes path locks. `Start` starts the TLRU worker, and `Stop` stops it. `StreamDir` builds a key as `name##token`, locks that key, returns cached children if present, otherwise calls `NextComponent().StreamDir`, stores non-empty successful results, and adds the key to the TLRU. `pathEvict` locks the same key and deletes the map entry when TLRU expires it.

## State and Persistence Behavior

Cached entries live in `sync.Map`; expiration state lives in the external `tlru.TLRU`. Per-key locks prevent duplicate fetch/store/evict races for the same path token. No filesystem persistence is used.

## Dependencies and Integration Points

The component depends on Blobfuse `common.LockMap`, `config`, `log`, `internal`, and `github.com/vibhansa-msft/tlru`. It sits in the component pipeline above storage components and only intercepts `StreamDir`.

## Risks and Edge Cases

It only caches non-empty successful listings, so empty directories and errors are never cached. Cache invalidation is purely timeout-based and requires read-only mode, so using it in mutable mounts is rejected. Key construction with `##` is simple but assumes path/token combinations cannot collide semantically.

## Test Signals

`entry_cache_test.go` verifies read-only configuration through loopback, non-caching of empty/error listings, cache hits that hide newly created files until expiration, and TLRU eviction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache_test.go -->
# sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache_test.go

## Purpose

`entry_cache_test.go` tests the `EntryCache` component against a loopback backend, focusing on caching, cache miss behavior, and TTL expiration.

## Important APIs, Types, and Functions

The suite defines `entryCacheTestSuite`, `newLoopbackFS`, `newEntryCache`, `randomString`, `setupTestHelper`, and `cleanupTest`. It exercises `EntryCache.Configure`, `Start`, `Stop`, and `StreamDir`.

## Control Flow

`SetupTest` creates a temporary loopback storage directory and configures `read-only: true` with a seven-second entry-cache timeout. Tests call `StreamDir` on empty, missing, and populated directories. One test creates an additional file after the initial listing, verifies that the cached listing still has the first result, sleeps long enough for eviction, and then verifies that a fresh listing sees both files.

## State and Persistence Behavior

The suite creates and removes temporary directories under the user's home directory. It inspects `entryCache.pathMap` directly for the `##` root key and relies on the TLRU expiration worker to remove entries.

## Dependencies and Integration Points

It depends on `loopback`, Blobfuse `config`, `log`, `common`, `internal`, `testify`, and filesystem operations. It validates that the cache composes with a real component rather than a mock.

## Risks and Edge Cases

`TestCachedEntry` sleeps 40 seconds for a seven-second timeout, making the suite slow. The direct `pathMap` inspection couples tests to internal key formatting. The tests do not cover paginated non-empty tokens beyond the root empty token key.

## Test Signals

Passing tests show that non-empty listings are cached, empty or failed listings are not cached, and expiration eventually allows new storage entries to appear.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/entry_cache/entry_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/cache_policy.go -->
# sources/user-network-fs/blobfuse2/component/file_cache/cache_policy.go

## Purpose

`cache_policy.go` defines the policy interface and shared helpers for file cache eviction policies.

## Important APIs, Types, and Functions

`cachePolicyConfig` carries temp path, timeout, max eviction count, size thresholds, lock map, and trace flag. `cachePolicy` defines lifecycle, config update, validity/invalidation/purge notifications, cache membership, and policy name methods. `getUsagePercentage` computes current cache usage relative to configured maximum, and `deleteFile` removes a file with permission and missing-file handling.

## Control Flow

`getUsagePercentage` rejects invalid max size by logging and returning zero, calls `common.GetUsage`, converts usage to a percentage, updates the file cache stats collector with current MB and percent, and returns the value. `deleteFile` attempts `os.Remove`; permission errors trigger chmod to `0666` and retry, not-found errors are treated as success, and other errors are returned.

## State and Persistence Behavior

The file has no durable state of its own. `getUsagePercentage` mutates metrics in `fileCacheStatsCollector`; `deleteFile` mutates the local filesystem and may change permissions before removal.

## Dependencies and Integration Points

It depends on Blobfuse `common`, `log`, and `stats_manager`, plus `os`. `lru_policy.go` implements `cachePolicy`, and `file_cache.go` constructs policy configs and calls policy methods around file operations.

## Risks and Edge Cases

`fileCacheStatsCollector` must be initialized before `getUsagePercentage` updates stats. Usage is directory-size based and can be expensive on large caches. `deleteFile` broadens permissions to remove files, which is intentional for cache cleanup but security-sensitive if paths escape the cache root.

## Test Signals

`cache_policy_test.go` covers usage measurement, percentage calculation including zero max size, and deleting a missing path without error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/cache_policy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/cache_policy_test.go -->
# sources/user-network-fs/blobfuse2/component/file_cache/cache_policy_test.go

## Purpose

`cache_policy_test.go` validates shared file-cache policy helpers for directory usage and file deletion behavior.

## Important APIs, Types, and Functions

The suite defines `cachePolicyTestSuite`, `SetupTest`, `cleanupTest`, and tests `common.GetUsage`, `getUsagePercentage`, and `deleteFile`.

## Control Flow

Setup initializes a silent logger and creates `cache_path`. Usage tests create a 1 MiB file and assert measured usage is near one MiB or about 25 to 30 percent of a four-MiB max. The zero-max test calls `getUsagePercentage("/", 0)` and asserts it returns a bounded nonnegative value. Deletion tests call `deleteFile` on a deliberately nonexistent suffix and expect no error.

## State and Persistence Behavior

Tests create and remove a local cache directory and a temporary file. They rely on package-level `cache_path` from other file-cache tests.

## Dependencies and Integration Points

It uses `testify`, Blobfuse `common` and `log`, and standard filesystem packages. It indirectly requires the file cache stats collector behavior to be safe in the test environment.

## Risks and Edge Cases

The measured size can vary by filesystem block accounting, so assertions use ranges. The test relies on a shared `cache_path` symbol and could be affected by test order or parallelism.

## Test Signals

Passing tests show usage helpers produce plausible numbers and cache deletion treats missing files idempotently.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/cache_policy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/file_cache.go -->
# sources/user-network-fs/blobfuse2/component/file_cache/file_cache.go

## Purpose

`file_cache.go` implements Blobfuse2's local file cache component. It downloads remote files into a local temp path, serves reads and writes through local file descriptors, flushes dirty handles back to storage, merges local and remote directory/attribute views, and coordinates eviction policy state.

## Important APIs, Types, and Functions

`FileCache` stores temp path, file locks, cache policy, config flags (`createEmptyFile`, `allowNonEmpty`, `offloadIO`, `syncToFlush`, `syncToDelete`, `lazyWrite`, `hardLimit`), size/time settings, missed chmod tracking, and async close wait group. `FileCacheOptions` defines all config keys. Major methods include `Start`, `Stop`, `GenConfig`, `Configure`, `OnConfigChange`, `StatFs`, `GetPolicyConfig`, `ReadDir`, `StreamDir`, `IsDirEmpty`, `CreateFile`, `OpenFile`, `ReleaseFile`, `ReadFile`, `ReadInBuffer`, `WriteFile`, `SyncFile`, `FlushFile`, `GetAttr`, `RenameFile`, `TruncateFile`, `Chmod`, `Chown`, `DeleteFile`, `DeleteDir`, `RenameDir`, and `FileUsed`.

## Control Flow

Configuration expands and validates the temp path, rejects mount-path conflicts and disallowed non-empty temp directories, derives max cache size from filesystem free space unless configured, sets default permissions from `allow-other`, builds an LRU policy config, and records hard-limit watermarks. Opens check policy membership and local file freshness through `isDownloadRequired`; if a download is required, they optionally delete stale local files, create directories, enforce hard-limit capacity, copy from the next component, set local mode and timestamps, update stats, then open the local file and return a handle. Writes use `syscall.Pwrite`, mark handles dirty, and periodically refresh policy validity. Reads use `syscall.Pread` or full-file reads from the local descriptor. Flush serializes dirty uploads with a per-file lock, duplicates and closes the fd to flush kernel buffers, opens a read handle, calls `CopyFromFile`, clears dirty state, and applies missed chmods. Release flushes, closes the file, decrements lock counts, and invalidates or purges local cache depending on fsync state.

## State and Persistence Behavior

The component persists cached file bytes and directories under `tmpPath`. It tracks cache policy state in the selected policy, per-path open/download locks in `common.LockMap`, missed chmods in `sync.Map`, dirty/fsynced/cached bits on handles, and file-cache metrics through `stats_manager`. Storage state changes are delegated to the next pipeline component through create/delete/rename/truncate/chmod/chown/copy calls.

## Dependencies and Integration Points

It integrates deeply with Blobfuse pipeline interfaces in `internal.Component`, handle state in `handlemap`, common helpers for locks, temp cleanup, usage, and permissions, config change listeners, stats collection, and the LRU policy implementation. The next component supplies storage operations and transfer primitives `CopyToFile` and `CopyFromFile`.

## Risks and Edge Cases

High-risk areas are local/remote divergence when `createEmptyFile` is false, recoverability of storage 404s, path safety under `tmpPath`, permission changes needed for uploads, concurrent flush/release/sync operations, hard-limit accounting based on directory usage, cache invalidation timing, and stale local entries after rename/delete failures. `isLocalDirEmpty` ignores `os.Open` errors before deferring close, which can panic if called on an invalid path. Some async invalidation calls can race with later opens if not protected by file locks.

## Test Signals

`file_cache_test.go` is broad: config defaults and errors, directory merging, create/open/read/write/flush/release, sync modes, rename/delete/truncate/chmod/chown, symlink cache paths, lazy write, StatFS, refresh, hard limits, empty-directory cleanup, concurrent flush serialization, and download-failure cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/file_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/file_cache_constants.go -->
# sources/user-network-fs/blobfuse2/component/file_cache/file_cache_constants.go

## Purpose

`file_cache_constants.go` centralizes the metric names used by the file cache stats collector.

## Important APIs, Types, and Functions

It defines four package constants: `cacheUsage`, `usgPer`, `dlFiles`, and `cacheServed`.

## Control Flow

There is no executable control flow. Other file-cache code passes these constants to `fileCacheStatsCollector.UpdateStats`.

## State and Persistence Behavior

The constants themselves are immutable. They affect the labels under which runtime file-cache statistics are recorded.

## Dependencies and Integration Points

The constants are consumed by `cache_policy.go` for cache usage and usage percent, and by `file_cache.go` for files downloaded and files served from cache.

## Risks and Edge Cases

Changing these strings can break monitoring, dashboards, tests, or users that depend on stable stat names. Keeping them in one file reduces the risk of spelling drift.

## Test Signals

There are no direct tests for this file. Indirect coverage comes from file-cache tests that call paths updating stats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/file_cache/file_cache_constants.go -->
