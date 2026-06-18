# Research Report: subset-b-009567

This grouped report covers the exact source files assigned to `subset-b-009567`. Each file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test_wrapper.go -->
## sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test_wrapper.go

Purpose: Go/cgo test support for the non-`fuse2` libfuse handler. It creates a `libfuseTestSuite`, configures a `Libfuse` component over a gomock `internal.Component`, and calls exported cgo callback functions directly to validate FUSE-to-component behavior without mounting a live filesystem.

Important APIs and flow: `newTestLibfuse` loads YAML config, constructs `NewLibfuseComponent`, wires the next component, and stores it in global `fuseFS`. Individual helper tests exercise `libfuse_mkdir`, `rmdir`, `create`, `open`, `truncate`, `unlink`, `symlink`, `readlink`, `fsync`, `fsyncdir`, `chmod`, `chown`, `utimens`, and `statfs`. The file also models the C native file object as `fileHandle` so tests can reinterpret `fi.fh` back into a Go `handlemap.Handle`.

State and dependencies: Tests depend on global `fuseFS`, cgo `libfuse_wrapper.h`, gomock expectations against `internal.MockComponent`, and handle allocation through `handlemap`. Configuration flags such as `disable-writeback-cache` and `ignore-open-flags` materially change open-flag normalization.

Risks: The helpers are sensitive to global state and call `cleanupTest` manually; double cleanup patterns make ordering fragile. The unsafe pointer casts must match `native_file_io.h` layout. Test coverage is broad for errno mapping and flag policy but has TODO gaps for `ReadDir` and rename paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_handler_test_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_wrapper.h -->
## sources/user-network-fs/blobfuse2/component/libfuse/libfuse_wrapper.h

Purpose: C shim that adapts blobfuse2's Go-exported libfuse handlers to the `fuse_operations` table for either FUSE2 or FUSE3. It centralizes callback registration and small native helpers required by the Go cgo layer.

Important APIs and flow: `populate_callbacks` assigns destroy, statfs, directory, file, link, sync, attribute, and rename callbacks. Read, write, and flush are wired to `native_read_file`, `native_write_file`, and `native_flush_file` for fast FD-based I/O; commented alternatives show the pure Go handlers. FUSE2 and FUSE3 signatures are selected with `__FUSE2__`. `start_fuse` calls `fuse_main`, `populate_statfs` uses host `/` stats, `populate_uid_gid` lazily captures FUSE context uid/gid, `get_root_properties` synthesizes root stat data, and `fill_dir_entry` adapts `fuse_fill_dir_t` flags.

State and dependencies: Depends on libfuse headers, Linux/POSIX headers, `libfuse_defs.h`, and `native_file_io.h`. It keeps process-global `fuse_opts` and `context_populated`.

Risks: Function pointer casts suppress type checking, so ABI drift between FUSE versions can break at runtime. Root attributes are static and time-based. `populate_uid_gid` is global and not reset across mounts/tests. Test signal comes indirectly from libfuse cgo tests and native I/O behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/libfuse_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/native_file_io.h -->
## sources/user-network-fs/blobfuse2/component/libfuse/native_file_io.h

Purpose: Native C fast path for FUSE read/write/flush operations when a blobfuse handle exposes a Unix file descriptor. This avoids crossing into Go for cached/local file data.

Important APIs and flow: `file_handle_t` stores the Unix fd, the Go `handlemap.Handle` pointer encoded as an integer, operation count, and dirty flag. `allocate_native_file_object` allocates and zeroes this object for `fi->fh`; `release_native_file_object` frees it. `native_read_file` falls back to `libfuse_read` when fd is zero, otherwise calls `native_pread`. `native_write_file` similarly chooses `libfuse_write` or `native_pwrite`, marks dirty, increments a counter, and invokes `blobfuse_cache_update` every `CACHE_UPDATE_COUNTER` writes. `native_flush_file` calls Go `libfuse_flush` and clears dirty on success.

State and dependencies: The file owns malloc/free lifecycle for `fi->fh` and depends on `pread`, `pwrite`, `errno`, and Go-exported functions declared in `libfuse_defs.h`. Optional `ENABLE_READ_AHEAD` code defines a read-ahead handler but relies on fields not present in the visible `file_handle_t`.

Risks: No null check before dereferencing `fi` or `handle_obj` in native callbacks. Layout must match Go tests' unsafe casts. Dirty state is native-only and cache-update behavior is write-count based. Test coverage validates allocation/free and handler integration indirectly through libfuse tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/libfuse/native_file_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/loopback/loopback_fs.go -->
## sources/user-network-fs/blobfuse2/component/loopback/loopback_fs.go

Purpose: Implements `internal.Component` against the local filesystem. It is a consumer component useful for tests, local backends, and xload remote simulation.

Important APIs and flow: `Configure` reads `loopbackfs.path`, creates it if missing, and stores the root path. Directory methods map to `os.Mkdir`, `os.Remove`, `os.ReadDir`, `os.Rename`, and optional MD5 calculation in `StreamDir` when consistency mode is enabled. File methods create/open local files, wrap them in `handlemap.Handle`, lock handles for read/write, support `ReadInBuffer` both with and without an open handle, and expose copy, truncate, chmod, chown, symlink, readlink, stat-like `GetAttr`, staged block writes, and commit assembly.

State and persistence: Persistent state is the host directory tree under `lfs.path`. `consistency` toggles MD5 population for streamed files. `StageData` writes temporary files named from object plus sanitized block id; `CommitData` assembles staged data at block offsets and removes stage files.

Dependencies and integration: Uses `internal` option structs, `handlemap`, `common.GetMD5`, and POSIX file operations. It registers as `loopbackfs`.

Risks: Path joining does not guard against traversal. `ReadInBuffer` returns `(0,nil)` for open errors without a handle. `CommitData` defaults `BlockSize` to zero unless caller sets it, making offsets collapse. Tests cover core filesystem paths and block commit basics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/loopback/loopback_fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/loopback/loopback_fs_test.go -->
## sources/user-network-fs/blobfuse2/component/loopback/loopback_fs_test.go

Purpose: Test suite for the loopback component's local filesystem implementation.

Important APIs and flow: `SetupTest` constructs a `LoopbackFS`, creates `/tmp/blobfuse2lfstests` with directories and seed files, writes lorem content, and starts the component. Tests validate directory creation/deletion/listing/rename, file creation/deletion/open/read/write/truncate/release, buffered reads with offsets, `GetAttr`, staged block data plus commit, and committing an empty block list to truncate an existing file.

State and persistence: The suite uses a fixed `/tmp/blobfuse2lfstests` path and a separate expanded `~/blocklfstest` path for block tests; cleanup removes these directories. Tests assert actual file metadata and content on disk.

Dependencies and integration: Uses `internal` option structs, `common.ExpandPath`, `stretchr/testify` suite/assert, and the real OS filesystem rather than mocks.

Risks and test signals: The fixed temp path can collide under concurrent runs. There is no explicit test for `Configure`, symlinks, `StreamDir` MD5 mode, `ReadInBuffer` no-handle branch, copy operations, chmod/chown, or error handling. The positive path coverage is strong enough to prove loopback can back xload tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/loopback/loopback_fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/block.go -->
## sources/user-network-fs/blobfuse2/component/xload/block.go

Purpose: Defines the reusable memory block used by xload to stage chunk data during parallel downloads.

Important APIs and flow: `Block` records pool index, file offset, valid length, storage block id, and a byte slice backed by memory mapping. `AllocateBlock` rejects zero size, creates anonymous private read/write memory with `syscall.Mmap`, and returns a `Block` whose `Data` points at that mapping. `Delete` unmaps `Data` with `syscall.Munmap` and nils the slice. `ReUse` resets metadata before returning the block to active use.

State and dependencies: State is in the mmap allocation and metadata fields. It depends directly on Linux/POSIX mmap semantics through `syscall`.

Risks: Manual mmap lifecycle means double-free, deleting non-mmap byte slices, or forgetting `Delete` can leak or fail. `ReUse` does not clear the actual data bytes, so consumers must respect `Length`/transfer counts and not read stale content. Tests cover zero, normal, large, huge allocation failure, invalid delete, and metadata reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/block_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/block_test.go

Purpose: Unit tests for xload `Block` mmap allocation, deletion, and reuse.

Important APIs and flow: `TestBlockAllocate` checks zero-size rejection and a successful small allocation/delete. `TestBlockAllocateBig` confirms a 100 MiB allocation exposes the expected capacity. `TestBlockAllocateHuge` expects a 50 GiB mmap to fail. `TestBlockFreeNilData` and `TestBlockFreeInvalidData` verify delete error behavior for nil or non-mmap data. `TestBlockResuse` validates metadata reset.

State and dependencies: Tests exercise actual mmap/munmap behavior through `syscall`, so behavior is OS and overcommit dependent.

Risks and test signals: The huge allocation expectation can be environment-sensitive on systems with aggressive overcommit. Invalid-data munmap error text is platform-specific. The tests do not verify stale byte clearing, concurrent access, or integration with `BlockPool`, but they do catch the main allocation lifecycle contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/block_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/blockpool.go -->
## sources/user-network-fs/blobfuse2/component/xload/blockpool.go

Purpose: Provides a bounded pool of preallocated mmap `Block` objects for xload, split into regular and high-priority capacity.

Important APIs and flow: `NewBlockPool` validates nonzero block size/count, reserves 10% of blocks for `priorityCh`, preallocates every block via `AllocateBlock`, and returns nil on allocation failure. `GetBlock(priority)` tracks waiters and delegates to `mustGet` for priority requests or `tryGet` for regular requests. `tryGet` waits only on regular blocks; `mustGet` can consume priority or regular blocks. Both honor context cancellation and call `ReUse`. `Release` preferentially fills `priorityCh`, then regular, then deletes overflow blocks. `Terminate` closes channels and drains them through `releaseBlocks`.

State and dependencies: State lives in buffered channels, `waitLength`, `blockSize`, `maxBlocks`, and cancellation context. It integrates with splitter scheduling and stats usage reporting.

Risks: `releaseBlocks` reads until channel closure returns nil; this assumes no nil block values. Closing while other goroutines call `GetBlock`/`Release` can panic. For small pool sizes, 10% priority truncates to zero. Tests cover allocation, usage, exhaustion, release, and termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/blockpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/blockpool_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/blockpool_test.go

Purpose: Tests block pool sizing, block checkout/release, usage accounting, and full exhaustion.

Important APIs and flow: `TestBlockPoolAllocate` validates invalid inputs and a single-block pool. `TestBlockPoolGetRelease` checks priority and regular checkout/release on a five-block pool. `TestBlockPoolUsage` verifies usage percentages after one and two checkouts in a ten-block pool. `TestBlockPoolBufferExhaution` checks that ten priority checkouts consume the full pool and return to empty usage after release.

State and dependencies: Tests use `context.TODO()` and real mmap-backed blocks; each pool is terminated to unmap buffers.

Risks and test signals: Tests do not cover context cancellation, concurrent waiters, release after terminate, or regular checkout when only priority capacity exists. They establish basic invariants but not race safety under xload's live pipeline.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/blockpool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/data_manager.go -->
## sources/user-network-fs/blobfuse2/component/xload/data_manager.go

Purpose: Defines xload's remote data manager stage, responsible for moving chunk data between the remote `internal.Component` and splitter-owned blocks. Current implementation supports downloads only.

Important APIs and flow: `newRemoteDataManager` validates worker count, remote component, and stats manager, then initializes a `ThreadPool` with `Process`. `Start` and `Stop` manage that pool. `Process` respects item cancellation; when `Download` is true it calls `ReadData`, otherwise returns an unsupported-upload error. `ReadData` calls `remote.ReadInBuffer` with the work item's path, offset, destination buffer, and data length, then reports a `DATA_MANAGER` stats item.

State and dependencies: It embeds `XBase` for name, remote, stats, worker count, and thread pool. It depends on `internal.ReadInBufferOptions` and `StatsManager`.

Risks: Upload/sync modes are intentionally unsupported. `ReadData` passes the whole block buffer and file size as `Size`; remote implementations must use offset and buffer length correctly. Cancellation only prevents starting work; an in-flight `ReadInBuffer` is not interrupted. Tests cover construction validation and unsupported/cancelled process errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/data_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/data_manager_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/data_manager_test.go

Purpose: Unit tests for remote data manager construction and error branches.

Important APIs and flow: `TestNewRemoteDataManager` asserts nil and incomplete option structs are rejected, then constructs a valid manager with a loopback remote and stats manager. `TestProcessErrors` creates a `WorkItem` with `Download=false` and confirms unsupported upload returns an error, then cancels the context and confirms cancellation is also surfaced.

State and dependencies: Uses `loopback.NewLoopbackFSComponent`, `NewStatsManager`, and context cancellation.

Risks and test signals: There is no positive `ReadData` test validating bytes copied from a real remote component or stats increments. There is no test for thread-pool start/stop behavior. The tests are useful for parameter validation and upload-disabled behavior but leave the main download path covered only through splitter/xload integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/data_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/lister.go -->
## sources/user-network-fs/blobfuse2/component/xload/lister.go

Purpose: Implements the xload directory enumeration stage. It lists the remote namespace, creates matching local directories, and schedules files for the splitter.

Important APIs and flow: `newRemoteLister` validates path, workers, remote, and stats, initializes a thread pool, and stores default permissions. `Start` begins workers and schedules an initial empty-path list. `Process` optionally waits for `azstorage.block-list-on-mount-sec` once, then repeatedly calls `remote.StreamDir` with continuation tokens. Directory entries trigger asynchronous `mkdir` plus recursive schedule; file entries schedule `WorkItem`s on the next component with size, mode, timestamps, and MD5. `mkdir` uses `os.MkdirAll` and reports lister stats.

State and dependencies: Uses `listBlocked` to ensure the configured initial list delay runs once, and uses the downstream `XComponent` chain for file processing. It depends on `config`, `internal.StreamDirOptions`, stats, and local filesystem permissions.

Risks: Directory creation goroutines capture and assign `err` from the outer scope, which is race-prone. Recursive scheduling can continue after `Stop` if goroutines are still running. Tests cover construction, start/stop listing against loopback, and mkdir.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/lister.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/lister_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/lister_test.go

Purpose: Integration-style tests for remote lister behavior using loopback as the remote namespace.

Important APIs and flow: Suite setup creates a random `/tmp/xload_*` remote tree with ten files and ten directories containing five files each, configures loopback, and starts silent logging. `testComponent` counts scheduled file work items through an `XBase` thread pool. `TestNewRemoteLister` validates option failures and success. `TestListerStartStop` chains lister to the counting component, starts it, sleeps five seconds, stops it, expects 60 file schedules, and verifies ten local directories. `TestListerMkdir` directly tests directory creation.

State and dependencies: Uses real temporary directories, loopback, global `lb` and `lb_path`, stats manager, and wall-clock sleeps.

Risks and test signals: Sleep-based synchronization can be flaky on slow systems. The expected count depends on full recursive listing completion. Error paths from `StreamDir`, downstream `Schedule`, and initial list-delay config are not deeply covered.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/lister_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/splitter.go -->
## sources/user-network-fs/blobfuse2/component/xload/splitter.go

Purpose: Splits remote files into block-sized download work items, writes completed chunks to a local cache file, and optionally validates MD5 consistency.

Important APIs and flow: `newDownloadSplitter` validates dependencies, stores the block pool, local path, file locks, and MD5 flag, and initializes a thread pool. `Process` locks non-priority file requests, skips existing same-size files, opens/creates the local file, handles zero-byte files, truncates to target size, schedules one `WorkItem` per block on the data manager, and collects responses on a channel. A collector goroutine writes each block to the correct offset, releases blocks, cancels remaining work on error, and records stats. After success it applies atime/mtime and calls `checkConsistency` when enabled.

State and persistence: Writes cache files under `ds.path`; failed downloads are deleted. Uses `BlockPool` for transient buffers and `common.LockMap` to coordinate lister and on-demand open paths.

Dependencies and integration: Requires a next `XComponent` data manager and remote metadata from lister/xload. Uses `common.GetMD5` and OS file operations.

Risks: Disk I/O stats mark `Success:false` for disk writes, likely skewing metrics. No retry on block failure or MD5 mismatch. Existing same-size files are trusted unless MD5 validation is reached through a fresh download. Tests cover present-file handling, full chained download, and MD5 comparison.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/splitter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/splitter_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/splitter_test.go

Purpose: Tests splitter creation, skip behavior, end-to-end file downloads, and MD5 consistency through a lister-splitter-data-manager chain.

Important APIs and flow: Suite setup creates a random loopback remote tree with root and nested files. `setupTestSplitter` creates local cache path, small block pool, lock map, and stats manager. `TestNewDownloadSplitter` checks validation and successful construction. `TestProcessFilePresent` verifies directory conflict error and same-size local file skip. `TestSplitterStartStop` wires lister, splitter, and remote data manager, starts all stages, sleeps, stops lister, and validates recursive MD5 equality. `TestSplitterConsistency` enables loopback MD5 publication and splitter validation.

State and dependencies: Uses real temp directories, loopback, `exec.Command("cp")`, small mmap blocks, stats manager, and sleep-based completion.

Risks and test signals: Failure cases are explicitly left as TODO. Tests do not stop all components in `TestSplitterStartStop`, relying on cleanup side effects. Sleep timing may be flaky. Positive integration coverage is strong for the download pipeline.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/splitter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/stats_manager.go -->
## sources/user-network-fs/blobfuse2/component/xload/stats_manager.go

Purpose: Aggregates and periodically exports xload progress, throughput, directory, transfer, and disk I/O statistics.

Important APIs and flow: `NewStatsManager` creates a buffered stats channel and optional JSON output file under the default work directory. `Start` initializes JSON with an array skeleton and launches `statsProcessor` plus `statsExporter`. `AddStats` sends `StatsItem`s. `statsProcessor` updates counters by component: lister increments total and directory counts, splitter updates success/failure or disk bytes, data manager tracks downloaded/uploaded bytes, and stats-manager items trigger `calculateBandwidth`. `statsExporter` ticks every four seconds. `calculateBandwidth` logs completion, pending files, Mbps, disk speed, and block pool details, and appends JSON samples.

State and persistence: State is in in-memory counters and optional `xload_stats_{PID}.json`. `Stop` closes channels and waits for the processor.

Dependencies and integration: Receives stats from lister, splitter, data manager, and block pool. Uses JSON append-by-seeking before the final `]`.

Risks: `AddStats` after `Stop` will panic on closed channel. Sending `done` from both `Stop` and `calculateBandwidth` can race. Counters are not atomic but are confined to processor goroutine. Tests cover export and mixed stats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/stats_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/stats_manager_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/stats_manager_test.go

Purpose: Unit/integration tests for stats manager construction, JSON file export, processing, and stop behavior.

Important APIs and flow: `TestNewStatsManager` confirms non-export mode leaves `fileHandle` nil and export mode creates a file, then removes it. `TestStatsManagerStartStop` starts an exporting stats manager, sends lister, directory, stats-manager, invalid component, data-manager, and splitter events, sleeps to allow exporter ticks, stops the manager, and asserts directory count, total processed count, and positive transfer counters.

State and dependencies: Uses the default blobfuse work directory for JSON output and real time sleeps. Logging is silenced.

Risks and test signals: The test depends on ticker timing and can run for roughly 15 seconds. It validates aggregate counters but does not inspect JSON validity or bandwidth values. Race cases around `Stop`, closed channels, and automatic `done` signaling are not covered.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/stats_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/threadpool.go -->
## sources/user-network-fs/blobfuse2/component/xload/threadpool.go

Purpose: Generic xload worker pool with separate priority and regular queues for lister, splitter, and data manager stages.

Important APIs and flow: `NewThreadPool` validates worker count and callback, then creates buffered priority and regular channels. `Start` stores the context and launches workers, reserving 10% for priority-only reads. `Schedule` checks context cancellation and sends priority items to `priorityItems`, otherwise regular work to `workItems`. `Do` loops until context cancellation or channel closure; regular workers select from both queues. `process` invokes the callback, logs errors, and returns the item with error/data length on a response channel when one is configured.

State and dependencies: State is worker count, wait group, queues, callback, and context. It integrates into every `XComponent`.

Risks: `cap(item.ResponseChannel)` panics if `ResponseChannel` is nil; current callers appear to provide it for response paths and omit it for fire-and-forget, making this a latent bug because nil channel cap is allowed in Go, but sending would block only when cap > 0. Scheduling after channel close can panic. Tests cover creation, start/stop, schedule, and priority throughput.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/threadpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/threadpool_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/threadpool_test.go

Purpose: Tests xload thread pool creation, lifecycle, scheduling, and priority handling.

Important APIs and flow: `TestThreadPoolCreate` validates nil returns for invalid constructor arguments and successful creation with a callback. `TestThreadPoolStartStop` starts a two-worker pool and stops it. `TestThreadPoolSchedule` schedules one priority and one regular item. `TestPrioritySchedule` schedules 20 priority and 80 regular items on ten workers, sleeps, then asserts the callback ran 100 times.

State and dependencies: Uses context TODO, atomic callback counters, and real goroutines/channels.

Risks and test signals: Tests are sleep-based and do not cover context cancellation, scheduling after stop, backpressure, callback errors, response channels, or priority ordering guarantees. They demonstrate that workers drain both queues under normal conditions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/threadpool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/utils.go -->
## sources/user-network-fs/blobfuse2/component/xload/utils.go

Purpose: Shared constants, work item schema, mode enum, rounding helper, and local file presence probe for xload.

Important APIs and flow: Constants define maximum workers, lister/splitter caps, `MB`, and component names. `WorkItem` carries all data passed between lister, splitter, and data manager: path, size, mode, timestamps, block, file handle, response channel, direction, priority, cancellation context, and MD5. `Mode` uses `JeffreyRichter/enum` to parse and stringify `PRELOAD`, `UPLOAD`, `SYNC`, and `INVALID_MODE`. `RoundFloat` rounds to a fixed precision. `isFilePresent` wraps `os.Stat` and returns presence, directory flag, and size.

State and dependencies: No persistent state. Depends on `os`, `time`, `context`, `math`, enum reflection, and logging.

Risks: `WorkItem` is a broad mutable transport object shared across goroutines; correctness depends on stage conventions. Unsupported modes parse successfully but later fail in xload start. `isFilePresent` logs all stat failures as debug, including permission errors. Tests cover mode parsing/stringing, rounding, and file presence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/utils_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/utils_test.go

Purpose: Unit tests for xload utility functions and mode enum behavior.

Important APIs and flow: `TestModeParse` checks case-insensitive parsing for valid modes plus errors for invalid values. `TestModeString` validates enum string names. `TestRoundFloat` checks several precision cases. `TestIsFilePresent` validates missing path, current directory detection, empty file detection, and size after truncate.

State and dependencies: Creates a temporary file in the current working directory and removes it with defer. Uses testify suite/assert and real filesystem metadata.

Risks and test signals: The temporary filename is fixed (`testFile1234`) inside the package working directory, so parallel package tests could collide. Rounding test expectations include `5.20`, which is numerically equal to `5.2`. Coverage is focused and adequate for utility contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/xcomponent.go -->
## sources/user-network-fs/blobfuse2/component/xload/xcomponent.go

Purpose: Defines the internal xload stage interface and base implementation used by lister, splitter, and data manager.

Important APIs and flow: `XComponent` requires lifecycle (`Init`, `Start`, `Stop`), scheduling/processing, next-stage linkage, thread pool access, remote component access, name, and stats manager access. `XBase` stores those fields plus worker count. Its `Schedule` sends to the thread pool when present, otherwise calls `Process` synchronously. Default `Process` is a no-op returning zero.

State and dependencies: `XBase` holds mutable pipeline links and references to `ThreadPool`, `internal.Component`, and `StatsManager`. It logs synchronous process errors.

Risks: Default no-op behavior can hide miswired components; tests intentionally rely on it. `Schedule(nil)` is tolerated when no pool exists, but real pools expect non-nil work items. There is no synchronization around setting next/remote/stats fields, so setup must complete before workers start. Coverage appears through xload tests and direct default behavior tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/xcomponent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/xload.go -->
## sources/user-network-fs/blobfuse2/component/xload/xload.go

Purpose: Blobfuse2 component that preloads a remote read-only filesystem into a local cache path and serves subsequent opens from that cache.

Important APIs and flow: `Configure` enforces global `read-only`, reads xload config, resolves block size from xload or stream config, resolves cache path from xload or file cache config, rejects path equal to mount path, creates empty path, parses mode, sets permissions, worker count, pool size, and cancellation context. `Start` creates a block pool and stats manager, supports only `PRELOAD`, builds downloader stages, starts stats, chains lister -> splitter -> data manager, and starts components in reverse. `Stop` cancels context, stops stages/stats/pool with timeout, then cleans local cache. `OpenFile` locks a per-file lock, downloads on priority if missing, opens the cached file, marks the handle cached, and stores Unix FD. `ReleaseFile` decrements the lock count.

State and persistence: Local cache files live under `xl.path` during mount and are removed on stop. Runtime state includes block pool, stats, stage list, file locks, and context.

Risks: Upload/sync unsupported. Stop timeout may leave goroutines running. `ReleaseFile` does not close the underlying file handle, relying on upstream/native release semantics. Empty-directory requirement can reject reuse. Tests cover config, start/stop, chain, open-on-demand, and unsupported modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/xload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/xload_test.go -->
## sources/user-network-fs/blobfuse2/component/xload/xload_test.go

Purpose: Main test suite for xload configuration, downloader construction, lifecycle, and cached open behavior.

Important APIs and flow: Setup creates random local cache and fake storage directories, reads a minimal read-only xload+loopback config, and constructs xload over loopback. Tests cover defaults, read-only enforcement, block size from component and CLI stream config, path fallback from file cache, missing/same-as-mount/nonempty path errors, mode parsing, allow-other permissions, unsupported modes, priority, block pool start failure, default `XBase`, downloader/chain creation, download error paths, start/stop preloading, opening already downloaded files, and on-demand downloads after remote data appears.

State and dependencies: Uses loopback as fake storage, real temp directories, config global state, small block sizes to force chunking, wall-clock sleeps, and recursive MD5 validation.

Risks and test signals: Tests reset global config frequently and rely on sleeps for async preloading. They cover many user-facing config failures and integration behavior but do not stress concurrent opens, stop races, or file handle closure semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/component/xload/xload_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/copyright_fix.sh -->
## sources/user-network-fs/blobfuse2/copyright_fix.sh

Purpose: Maintenance script for adding or replacing Go source copyright/license headers and updating copyright years from `LICENSE`.

Important flow: It derives `currYear` from `date`, extracts the license line containing `Copyright ©`, and scans `find -name *.go`. With argument `replace`, it replaces fixed line ranges using `sed` depending on whether `+build` appears. Without `replace`, it adds a header to Go files missing the copyright marker, or updates the marker line when the current year is absent.

State and persistence: Mutates Go files in place and uses a temporary file named `__temp__` in the current directory. Reads the repository `LICENSE`.

Dependencies and integration: Uses Bash, `find`, `grep`, `sed`, `tail`, `cat`, and `mv`. Intended for repository-wide maintenance rather than runtime.

Risks: The line-range edits assume stable header lengths and can damage files with unusual build tags or comments. Unquoted variables break on spaces. The temp filename can collide. Search is repository-wide and not scoped to tracked files. No tests are present; validation would require diff inspection after running.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/copyright_fix.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/Dockerfile -->
## sources/user-network-fs/blobfuse2/docker/Dockerfile

Purpose: Builds an Ubuntu 22.04 container image containing blobfuse2, sample config, FUSE3, syslog/logrotate config, and mount/unmount helper scripts.

Important flow: Starts from Microsoft mirror Ubuntu 22.04, creates `/usr/share/blobfuse2`, copies `blobfuse2` and `config.yaml`, installs `ca-certificates`, `vim`, `rsyslog`, and `fuse3`, enables `user_allow_other`, copies rsyslog and logrotate snippets, creates `/mnt/blobfuse_mnt` and `/tmp/blobfuse_temp` with broad permissions, writes shell scripts for mount and unmount, symlinks them as `fuse` and `unfuse`, and enters via `bash fuse`.

State and persistence: Runtime mount point and temp cache are inside the container. Credentials are expected via environment variables referenced by config or storage component.

Dependencies and integration: Requires a prebuilt local `blobfuse2` binary and support files copied by build scripts.

Risks: Runs with FUSE privileges when launched. Scripts are generated with `echo`, permissions are `777`, and entrypoint mounts in foreground. No health checks or non-root hardening. Docker scripts provide the main test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/buildandruncontainer.sh -->
## sources/user-network-fs/blobfuse2/docker/buildandruncontainer.sh

Purpose: Convenience script that builds the blobfuse2 Docker image and runs it interactively when the image appears.

Important flow: Reads the blobfuse2 version from `../blobfuse2 --version`, derives tag `azure-blobfuse2.$ver`, calls `./buildcontainer.sh Dockerfile x86_64`, checks `docker images` for the tag, and runs `docker run -it --rm` with `SYS_ADMIN`, `/dev/fuse`, apparmor unconfined, and Azure storage environment variables. It documents `fuse` and `unfuse` commands inside the container.

State and dependencies: Depends on a built `../blobfuse2`, Docker, environment credentials, and the build script. It creates/runs a privileged container but does not persist container state due to `--rm`.

Risks: Tag format differs from `buildcontainer.sh` (`azure-blobfuse2-$2.$ver`), so the image lookup may fail. Uses unquoted variables and broad privileges. No tests; validation is manual via build/run success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/buildandruncontainer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/buildcontainer.sh -->
## sources/user-network-fs/blobfuse2/docker/buildcontainer.sh

Purpose: Builds a blobfuse2 Docker image from the repository source and local Dockerfile context.

Important flow: Moves to repo root, runs `./build.sh`, lists the generated binary, returns to docker directory, copies the binary plus rsyslog/logrotate files into the Docker build context, computes version and tag `azure-blobfuse2-$2.$ver`, removes any existing image, runs `sudo docker build -t $tag -f $1 .`, lists images, removes copied build-context artifacts, and prints matching image status.

State and dependencies: Mutates the docker directory temporarily with copied binary/config files and mutates local Docker image cache. Depends on `build.sh`, Docker daemon, sudo, and setup files.

Risks: No `set -e`, so failed commands can cascade. Unquoted args and variables can break. Image removal is unconditional for the computed tag. Cleanup removes known copied files only. Test signal is manual image listing and downstream run script.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/buildcontainer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/config.yaml -->
## sources/user-network-fs/blobfuse2/docker/config.yaml

Purpose: Sample container configuration for mounting Azure Blob Storage with blobfuse2.

Important content: Enables `allow-other`, syslog logging, and the component chain `libfuse`, `file_cache`, `attr_cache`, `azstorage`. `libfuse` cache expirations are set for attributes, entries, and negative entries. `file_cache` uses `/tmp/blobfuse_temp`, disables timeout eviction with `timeout-sec: 0`, permits non-empty temp path, and cleans on start. `attr_cache` timeout is 7200 seconds.

State and dependencies: Runtime state is in `/tmp/blobfuse_temp` and whatever Azure storage config is supplied through environment variables or other mechanisms. It depends on the Dockerfile's directories and FUSE setup.

Risks: This is not a complete standalone config because Azure account/container credentials are absent. `allow-non-empty-temp` and `cleanup-on-start` can delete cached data on container start. Long attr cache timeout may hide remote changes. No direct tests; exercised by container mount workflow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/dockerinstall.sh -->
## sources/user-network-fs/blobfuse2/docker/dockerinstall.sh

Purpose: Host setup helper to remove Docker Desktop remnants, install Docker Engine on Ubuntu, adjust permissions, prune old images, and start Docker.

Important flow: Removes/purges Docker Desktop, updates apt, installs certificates and prerequisites, creates Docker apt keyring/source, installs Docker CE packages, creates `docker` group, adds current user, adjusts docker socket and `~/.docker` ownership/permissions, removes blobfuse images, prunes Docker system, starts service, and lists images/containers.

State and dependencies: Mutates system packages, apt sources, user groups, docker socket permissions, images, and service state. Requires sudo and network access to Docker repositories.

Risks: Highly privileged and destructive for Docker state. Backtick `docker rmi` can fail or remove unintended images if grep/cut output is broad. Group membership changes may require re-login. No `set -e`, so partial installs are possible. No automated tests; validation is command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/dockerinstall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/publishcontainer.sh -->
## sources/user-network-fs/blobfuse2/docker/publishcontainer.sh

Purpose: Tags and pushes a built blobfuse2 Docker image to `blobfuse2containers.azurecr.io`.

Important flow: Reads blobfuse version, builds image name `azure-blobfuse2-$3.$ver`, logs into Azure Container Registry with username `$1` and password `$2`, tags local `$image:latest` to the registry path, pushes it, and logs out.

State and dependencies: Mutates Docker local tags and remote registry state. Depends on a previously built image, Docker CLI, network, and valid ACR credentials.

Risks: Password is passed on the command line and can be visible in process history. No `set -e`, so push/tag errors can be missed. Image naming must match build script output. No tests; success is registry push completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/docker/publishcontainer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/error_search.sh -->
## sources/user-network-fs/blobfuse2/error_search.sh

Purpose: Lightweight static-analysis helper to find Go error assignments that may lack nearby log statements.

Important flow: Removes previous `tmp.lst` and `missing_log.lst`, scans non-test Go files excluding `manual_scripts`, captures seven lines after each `err :=`-style assignment into `tmp.lst`, counts error assignments and `log.` occurrences, and appends files with mismatches plus context to `missing_log.lst`.

State and persistence: Writes and removes `tmp.lst`; writes `missing_log.lst` in the current directory.

Dependencies and integration: Uses Bash, `find`, `grep`, and shell arithmetic. It is a repository maintenance aid, not part of runtime.

Risks: The regex is narrow and can miss or miscount errors. Counting any `log.` in the next seven lines is imprecise. Unquoted file paths break on spaces. It ignores tests and manual scripts by design. No tests; output requires human review.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/error_search.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/exported/exported.go -->
## sources/user-network-fs/blobfuse2/exported/exported.go

Purpose: Public wrapper package exposing selected `internal` blobfuse2 types and helpers for custom component authors without importing internal packages directly.

Important APIs: Re-exports property flag constants, aliases `BaseComponent`, `Component`, `ComponentPriority`, `ObjAttr`, every component option struct in this subset, committed block types, and `handlemap.Handle`. `NewHandle` wraps `handlemap.NewHandle`. `ComponentPriorityWrapper` exposes priority constructors. `TruncateDirName` and `ExtendDirName` forward internal directory name helpers.

State and dependencies: Contains no state. Depends on `internal` and `internal/handlemap`; because aliases preserve identity, consumers interact with the same underlying types.

Integration points: This is the external extension boundary for pipeline components. It mirrors `internal` contracts used by loopback, xload, libfuse, and storage components.

Risks: Alias coverage must stay synchronized with `internal`; missing aliases can block plugin/custom component use. Exported constants use `uint16`-style iota while internal flags are currently `uint64`, so type assumptions can diverge. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/exported/exported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/go_installer.sh -->
## sources/user-network-fs/blobfuse2/go_installer.sh

Purpose: Installs a pinned Microsoft build of Go, intended for FIPS-capable builds using `systemcrypto`.

Important flow: Uses `set -euo pipefail`, trims the work directory argument, chooses `GO_VERSION` default `1.26.3`, detects architecture, downloads the tarball and SHA256 sidecar from `aka.ms`, verifies checksum, stages extraction in `/usr/local/go.new`, validates `go version`, requires `MICROSOFT_REVISION`, atomically swaps `/usr/local/go`, symlinks `go` and `gofmt` into `/usr/bin`, and removes the tarball.

State and dependencies: Mutates `/usr/local/go`, `/usr/bin/go`, `/usr/bin/gofmt`, and downloads into the provided work dir. Requires sudo, wget, tar, sha256sum, awk, and network.

Risks: It assumes Microsoft aka.ms sidecar availability and the version naming convention. Existing Go is moved aside then deleted after successful swap. Architecture detection uses `hostnamectl`, which may not exist in minimal containers. Strong checksum and staging behavior reduce partial-install risk.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/go_installer.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/attribute.go -->
## sources/user-network-fs/blobfuse2/internal/attribute.go

Purpose: Defines the common object attribute model and property flags used across blobfuse2 components.

Important APIs: `NewDirBitMap`, `NewSymlinkBitMap`, and `NewFileBitMap` construct `common.BitMap64` values for object type flags. Property constants represent unknown, not-exists, directory, empty directory, symlink, and default-mode states. `ObjAttr` carries timestamps, size, mode, flags, path/name, MD5, ETag, and metadata. Methods `IsDir`, `IsSymlink`, and `IsModeDefault` query flags.

State and dependencies: Attribute instances are passed through component APIs, lister/splitter metadata flow, libfuse stat conversion, and external exported aliases. Depends on `common.BitMap64`, `os.FileMode`, and `time`.

Risks: Flags are a shared protocol; mismatched flag constants in external wrappers or components can create subtle behavior changes. `PropFlagEmptyDir` exists but is not exercised in this subset. MD5/ETag are optional and consumers must handle nil values. Tests are indirect through loopback, xload, and component option behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/attribute.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/base_component.go -->
## sources/user-network-fs/blobfuse2/internal/base_component.go

Purpose: Provides default forwarding implementations for the `Component` interface so components can embed `BaseComponent` and override only relevant operations.

Important APIs and flow: Holds component name and next component. Pipeline methods expose name, config, priority, next linkage, start, and stop. Directory, file, symlink, filesystem, block, and stat methods check `base.next` and forward to it, otherwise return neutral zero values. `SetNextComponent` panics if called more than once.

State and dependencies: State is the next-component pointer and component name. It depends on all internal option structs, `handlemap.Handle`, `common.BlockOffsetList`, and `syscall.Statfs_t`.

Integration points: Every concrete component can embed this to participate in a chain. Xload and loopback both use internal component conventions; libfuse calls into the top component and expects errors/attributes to propagate.

Risks: Neutral nil success defaults can hide missing implementations when no next component exists. Single-assignment next pointer prevents dynamic rewiring. No direct tests here; behavior is exercised by xload `XBase` tests separately and by components embedding `BaseComponent`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/base_component.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/component.go -->
## sources/user-network-fs/blobfuse2/internal/component.go

Purpose: Defines the central blobfuse2 component interface and component priority values.

Important APIs: `ComponentPriority` constructors define ordering levels: producer, level one, mid, level two, and consumer. `Component` requires pipeline metadata/config/lifecycle, next-component linkage, directory operations, file operations, flush/release semantics, symlink operations, attribute/setattr operations, block offset retrieval, file-use notification, statfs, committed block list, stage data, and commit data.

State and dependencies: This file has no runtime state except exported priority sentinel `EComponentPriority`. It imports `context`, `syscall`, `common`, and `handlemap`.

Integration points: It is the contract implemented by loopback, xload, libfuse-facing components, storage backends, caches, and exported wrapper aliases. Comments document important expectations such as `ReadDir`/`GetAttr` returning not-exist errors and `CreateFile` returning exists errors.

Risks: Interface breadth means all components must either implement or inherit many methods; neutral defaults can mask missing behavior. Contract comments are not compiler-enforced. Tests are indirect through concrete component suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/component.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/component_options.go -->
## sources/user-network-fs/blobfuse2/internal/component_options.go

Purpose: Defines typed option payloads passed through the `Component` interface, plus directory-name helper functions.

Important APIs: Option structs cover directory creation/deletion/listing/renaming, file create/open/read/write/truncate/copy/flush/release/rename, symlink create/read, attributes, chmod/chown, sync, staged block upload, commit, and committed block metadata. `ReadInBufferOptions` supports both handle-based and path/size-based reads, used by xload. `CommitDataOptions` carries block id order, block size, and optional new ETag. `TruncateDirName` removes one trailing slash; `ExtendDirName` adds one trailing slash or returns `/` for empty input.

State and dependencies: The file has no mutable state. It imports `os` and `handlemap`.

Integration points: These structs are the shared ABI between libfuse, xload, loopback, storage backends, and external aliases.

Risks: Option semantics are implicit; for example `BlockSize` zero in `CommitDataOptions` can be harmful if implementations do not default it. Tests cover only `TruncateDirName` and `ExtendDirName`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/component_options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/component_options_test.go -->
## sources/user-network-fs/blobfuse2/internal/component_options_test.go

Purpose: Unit tests for the directory name helper functions in `component_options.go`.

Important APIs and flow: `TestExtendDirName` validates adding a slash to `dir`, preserving `dir/`, and converting empty string to `/`. `TestTruncateDirName` validates removing a trailing slash from `dir/`, preserving `dir`, and converting `/` to empty string.

State and dependencies: No filesystem state. Uses testify suite/assert.

Risks and test signals: Coverage is narrow but directly verifies the edge cases likely to affect directory marker naming. The many option structs in the same source file are data-only and receive no direct tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/component_options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/handlemap/handle_map.go -->
## sources/user-network-fs/blobfuse2/internal/handlemap/handle_map.go

Purpose: Defines blobfuse2 file handle state and a global concurrent handle map from blobfuse handle IDs to `Handle` objects.

Important APIs and flow: `Handle` embeds `sync.RWMutex` and stores an OS file, optional stream cache, buffers, ID, size, mtime, Unix FD, operation count, flags, path, and arbitrary key/value data. Methods expose dirty/fsynced/cached flag queries, file object get/set, FD, value set/get/remove, and cleanup. Global `Add` allocates a unique ID with atomic increment and stores the handle in `sync.Map`; `Load`, `Delete`, and `GetHandles` access the map. `CreateCacheObject` attaches an LRU block cache. `Store` is a test utility.

State and dependencies: Persistent runtime state is global `defaultHandleMap` and `nextHandleID`; per-handle state coordinates libfuse, caches, xload, and storage components. Depends on `common.BitMap64`, cache policy LRU, `os.File`, `sync`, and atomic counters.

Risks: Global map can leak handles if releases do not delete them. `values` map is not separately synchronized beyond caller use of the handle lock. Native cgo paths store raw `Handle` pointers, so lifetime matters. Tests in this subset exercise handle use indirectly through loopback, xload, and libfuse wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/handlemap/handle_map.go -->
