<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/file.go -->
# sources/user-network-fs/rclone/vfs/file.go

## Purpose
Defines `File`, the VFS node for regular files and symlink payload files. It bridges directory-cache nodes, backend `fs.Object`s, open handles, writeback cache entries, rename/remove operations, stat metadata, symlink resolution, and modtime/size reporting.

## Important APIs, Types, and Functions
Key members are `File`, `newFile`, `Mode`, `Path`, `CachePath`, `ModTime`, `Size`, `SetModTime`, `Open`, `Truncate`, `Remove`, `rename`, `resolveNode`, `setObject`, `waitForValidObject`, `addWriter`, `delWriter`, and the internal `o_SYMLINK` flag. `File` satisfies the package `Node` interface and returns itself through `Node()`.

## Control Flow
Creation stores parent `Dir`, path, leaf, inode, context, object, and initial size, then detects symlink status from the link suffix. `Open` resolves symlinks unless `o_SYMLINK` is set, rejects `O_RDONLY|O_TRUNC`, derives read/write intent from flags, and chooses `ReadFileHandle`, `WriteFileHandle`, or `RWFileHandle` based on cache mode, append/truncate/create flags, and whether the cache already has the item. Rename updates the VFS node immediately, then either moves the backend object and cache entry immediately or defers the remote rename until writers close. `Truncate` first forwards to open writer handles; if none remain it opens/truncates through the normal handle path.

## State and Persistence Behavior
State is guarded by `mu`, `muRW`, atomics, and lock-ordering comments that make `File` subordinate to `Dir`. Persistent effects include remote object moves/removes, cache renames/removes, delayed writeback via open handles, cached dirty item size/modtime, pending modtime application after object creation, and delayed rename callbacks. `virtualModTime` preserves stable modtimes for remotes without modtime support. Symlinks are represented by backend objects with `fs.LinkSuffix` in cache/remote paths when `--links` is enabled.

## Dependencies and Integration Points
Depends on `fs.Object`, `operations.Move`, `vfscommon.CacheMode`, `vfscache.Cache`, `Dir` methods, VFS options, and handle constructors in `read.go`, `write.go`, and `read_write.go`. `resolveNode` integrates with `VFS.Stat` and handle reading. Mount layers consume `Node`/`Handle` behavior through this file.

## Risks and Edge Cases
Deadlock risk is explicit; methods must not call most `Dir` APIs with `File.mu` held. `setSymlink` and `renameDir` use `RLock` while mutating fields, which is unusual and worth reviewing. `ModTime` writes `virtualModTime` in a deferred closure after releasing the initial read lock, so race safety depends on broader usage. Delayed rename chains can report only through logs if they fail. `waitForValidObject` waits up to roughly five seconds for writers and returns `ENOENT` on timeout. Symlink resolution only follows direct file symlinks, not symlinked intermediate directories, and is capped by `MaxSymlinkIterations`.

## Test Signals
`file_test.go`, `read_write_test.go`, and `vfs_test.go` cover basic metadata, read/write open selection, unknown-size reads, remove/remove-all, pending modtimes, cache-mode rename behavior, writer-delayed rename, size updates, and open flag matrices. Symlink behavior is not strongly represented in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/file_test.go -->
# sources/user-network-fs/rclone/vfs/file_test.go

## Purpose
Tests `File` node metadata, open routing, remote/cache mutation, modtime handling, removal, rename behavior, and structure size.

## Important APIs, Types, and Functions
The helper `fileCreate` builds a test VFS with a chosen cache mode and returns the VFS file node for `dir/file1`. `fileCheckContents` validates read-open contents. Main tests are `TestFileMethods`, `TestFileSetModTime`, `TestFileOpenRead`, `TestFileOpenReadUnknownSize`, `TestFileOpenWrite`, `TestFileRemove`, `TestFileRemoveAll`, `TestFileOpen`, `TestFileRename`, and `TestFileStructSize`.

## Control Flow
Tests create remote objects through `fstest.Run`, obtain nodes through `vfs.Stat`, then exercise direct `File` methods. `TestFileSetModTime` iterates cache mode, open, and write combinations to verify immediate or deferred modtime application. Rename tests cover root/subdirectory moves, cache entry renames, forced cache population, and open-writer rename delay.

## State and Persistence Behavior
The tests observe persistent remote contents with `CheckRemoteItems` and `CheckListingWithPrecision`, and observe cache state with `vfs.cache.Exists`. They also verify read-only mode returns `EROFS` for mutating methods. Unknown-size remote tests verify a `ReadFileHandle` starts at size zero, reads real bytes, and updates handle size after EOF.

## Dependencies and Integration Points
Uses `fstest`, `mockfs`, `mockobject`, `operations.CanServerSideMove`, `vfscommon.CacheMode`, and the test VFS constructors from `vfs_test.go`. It exercises integration among `File`, `Dir.Rename`, remote object operations, and cache writeback.

## Risks and Edge Cases
The rename tests skip remotes lacking server-side move/copy, so coverage is backend-dependent. Unknown-size read coverage uses a mock object with no seek support but does not cover writeback or cache interaction. Symlink and pending rename failure paths are not covered here.

## Test Signals
Strong signal for `File` public methods, size/modtime expectations, read-only protection, cache-aware rename semantics, and writer-close delayed remote rename behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/make_open_tests.go -->
# sources/user-network-fs/rclone/vfs/make_open_tests.go

## Purpose
Generates `open_test.go`, a table of expected VFS open semantics for combinations of read/write mode, append, create, exclusive, sync, and truncation flags. It records Unix-like behavior with an intentional rclone adjustment for `O_RDONLY|O_TRUNC`.

## Important APIs, Types, and Functions
Key functions are `whichError`, `test`, and `main`; `accessModeMask` mirrors the VFS flag mask. The generated table uses `openTest` records with expected open/read/write errors and final contents.

## Control Flow
For each flag combination, `test` opens a nonexistent file, optionally reads/writes/closes it, creates a baseline file containing `hello`, opens it with the same flags, reads/writes/closes, reads final contents, removes the file, normalizes expected errors, and prints a Go struct literal. `main` enumerates all combinations and emits a complete Go source file.

## State and Persistence Behavior
The generator mutates a temporary local OS file and uses the observed local filesystem behavior as the oracle. Generated output persists only when run through `go generate` from `vfs.go`, which pipes the result through `gofmt` into `open_test.go`.

## Dependencies and Integration Points
Depends on `github.com/rclone/rclone/lib/file` wrappers and standard `os` behavior. It integrates with `read_write_test.go`, whose open matrix tests consume `openTests`.

## Risks and Edge Cases
`O_SYNC` is captured in the matrix but VFS largely ignores it. The generator has a hardcoded override for `O_RDONLY|O_TRUNC`, because Linux truncates but VFS chooses `EINVAL`. Error recognition is string-based for several OS errors, so new platform messages could break generation. It is build-tagged `none`, so it is not compiled in normal builds.

## Test Signals
The file is itself a test-data generator. Its signal appears through `open_test.go` and `TestRWFileHandleOpenTests`, not through direct execution in ordinary test runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/make_open_tests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/open_test.go -->
# sources/user-network-fs/rclone/vfs/open_test.go

## Purpose
Provides the generated `openTests` matrix used to validate VFS open/read/write semantics against Unix-like expectations across all combinations of key `os.OpenFile` flags.

## Important APIs, Types, and Functions
Defines `openTest` and `openTests`. Each row specifies `flags`, a display string, expected errors for opening nonexistent/existing files, expected read/write errors after successful open, and expected final file contents.

## Control Flow
This file has no executable control flow beyond table initialization. `read_write_test.go` iterates the table for `CacheModeWrites` and `CacheModeFull`, opening nonexistent and existing files through `VFS.OpenFile`, attempting read/write operations, and comparing final contents.

## State and Persistence Behavior
No runtime state beyond the static table. The matrix encodes persistence expectations such as `O_TRUNC` producing `HEL`, `O_APPEND` producing `helloHEL`, `O_EXCL|O_CREATE` returning `EEXIST` for existing files, and write-only handles returning `EBADF` for reads.

## Dependencies and Integration Points
Imports `io` and `os` for expected sentinel errors and flag constants. Generated by `make_open_tests.go` via `go generate` in `vfs.go`; consumed by `TestRWFileHandleOpenTests`.

## Risks and Edge Cases
Because this is generated data, hand edits would be fragile. The matrix intentionally diverges from Linux for `O_RDONLY|O_TRUNC`, expecting `EINVAL`. It does not cover symlink-specific `o_SYMLINK`, non-cache read handles, or remotes with special upload restrictions beyond what the consuming tests encounter.

## Test Signals
Very strong regression oracle for open flag behavior in cached RW modes. It establishes expected behavior for nonexistent file creation, append/truncate interactions, read/write access errors, and exclusive create semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/open_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc.go -->
# sources/user-network-fs/rclone/vfs/rc.go

## Purpose
Registers remote-control endpoints for selecting active VFS instances, refreshing/forgetting directory cache entries, controlling poll interval, listing active VFSes, reporting stats, and managing the VFS upload queue.

## Important APIs, Types, and Functions
Key functions are `getVFS`, `rcRefresh`, `rcForget`, `getDuration`, `getInterval`, `getTimeout`, `getStatus`, `rcPollInterval`, `rcList`, `rcStats`, `rcQueue`, and `rcQueueSetExpiry`. Multiple `init` functions register `rc.Call`s for `vfs/refresh`, `vfs/forget`, `vfs/poll-interval`, `vfs/list`, `vfs/stats`, `vfs/queue`, and `vfs/queue-set-expiry`.

## Control Flow
`getVFS` selects a VFS by `fs` parameter or, for compatibility, the only active VFS. Refresh resolves requested directories and calls `readDir` or `readDirTree`. Forget calls `ForgetAll` or `ForgetPath` by file/dir parameters. Poll interval parses duration and timeout, sends the new interval over `vfs.pollChan`, and returns status. Queue expiry parses queue `id`, `expiry`, and optional `relative` and delegates to the cache writeback queue.

## State and Persistence Behavior
The endpoints mutate in-memory directory caches, `vfs.Opt.PollInterval`, and writeback queue expiry. They do not directly persist data except by influencing later cache, polling, or upload behavior. `getVFS` deletes a valid `fs` parameter from input before downstream validation.

## Dependencies and Integration Points
Depends on global active VFS registry from `vfs.go`, `fs/cache` canonicalization, `fs/rc` parameter helpers, `Dir` cache methods, `vfscache.Cache`, and `writeback.Handle`. These endpoints are externally visible through rclone rc.

## Risks and Edge Cases
Ambiguous active VFS selection returns errors when no `fs` is supplied. `rcRefresh` only accepts string-valued `recursive` and `dir*` parameters. `rcPollInterval` returns an error if the remote lacks change notification. `rcQueue` returns nil output if no cache exists, while `rcQueueSetExpiry` returns an invalid-parameter error without cache. Timeout behavior may leave `PollInterval` unchanged if the poll goroutine does not receive in time.

## Test Signals
`rc_test.go` validates active VFS selection errors, basic refresh/forget output, list output, stats output, and limited poll-interval behavior. Queue and queue expiry are mainly tested through vfscache/writeback tests outside this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc_test.go -->
# sources/user-network-fs/rclone/vfs/rc_test.go

## Purpose
Tests the VFS remote-control registration and selection behavior for core rc endpoints.

## Important APIs, Types, and Functions
`rcNewRun` creates a test VFS and locates an `rc.Call`. Tests include `TestRcGetVFS`, `TestRcForget`, `TestRcRefresh`, `TestRcPollInterval`, `TestRcList`, and `TestRcStats`.

## Control Flow
Tests set up local-only `fstest` VFS instances, call rc handlers directly, and inspect returned `rc.Params`. `TestRcGetVFS` exercises no-active, implicit single-active, explicit `fs`, wrong `fs`, and ambiguous duplicate-active cases.

## State and Persistence Behavior
The tests create active VFS entries and rely on cleanup to shut them down. `TestRcForget` and `TestRcRefresh` operate on empty/default caches and assert shape of returned results rather than deep cache mutation. `TestRcStats` checks metadata cache counts and options.

## Dependencies and Integration Points
Uses `fs.ConfigString`, `rc.Calls`, `fstest`, `vfscommon.Options`, and the active VFS global registry. Tests skip non-local remotes for determinism.

## Risks and Edge Cases
Several tests contain `FIXME needs more tests`; recursive refresh, path-specific refresh/forget, invalid parameter types, queue endpoints, queue expiry, poll timeout, and unsupported poll interval paths receive little or no coverage here.

## Test Signals
Good signal for `getVFS` compatibility/error behavior and basic rc registration. Limited signal for cache mutation semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read.go -->
# sources/user-network-fs/rclone/vfs/read.go

## Purpose
Implements `ReadFileHandle`, the non-cache read-only handle for VFS files. It wraps backend objects with chunked reading, accounting, optional async buffering, seek/read-at behavior, sequential-read coordination, and optional checksum validation.

## Important APIs, Types, and Functions
Key APIs are `ReadFileHandle`, `newReadFileHandle`, `openPending`, `Seek`, `ReadAt`, `readAt`, `waitSequential`, `checkHash`, `Read`, `Close`, `Flush`, `Release`, `Name`, `Size`, and `Stat`.

## Control Flow
The handle is lazily opened by `openPending`, creating a `chunkedreader` using VFS chunk options and an accounting transfer. `Read` delegates to `readAt` at `roffset`; `ReadAt` calls `readAt` without changing `roffset`. `readAt` optionally waits for nearby in-sequence reads, seeks by range-seek or reopen, retries low-level failures, reads with `io.ReadFull`, handles unknown sizes at EOF, updates offsets, and writes to the hasher. Close closes the accounting reader and validates hashes if a full sequential read occurred.

## State and Persistence Behavior
No writes to the remote. In-memory state tracks object size, whether size is unknown, read and backend offsets, whether opened/closed, no-seek mode, and checksum state. Accounting transfer state is started on open and completed on close.

## Dependencies and Integration Points
Depends on `chunkedreader`, `accounting`, `hash`, global config `LowLevelRetries`, VFS options `NoChecksum`, `NoSeek`, `ReadWait`, `ChunkSize`, `ChunkSizeLimit`, and `ChunkStreams`, and the owning `File`.

## Risks and Edge Cases
`openPending` assumes `fh.file.getObject()` is non-nil. `readAt` checks closed only after opening, so a closed unopened handle may attempt open before returning `ECLOSED`. Hash checking is skipped if seeking invalidates the hasher, if reads did not reach file size, or if source hash is unavailable. Unknown-size reads update size only after EOF. Sequential read waiting launches a goroutine per wait and uses a short timeout to avoid blocking all seeks.

## Test Signals
`read_test.go` covers string/node/size/stat, sequential reads, EOF, seeking, read-at forward/backward/off-end, no-seek errors, close idempotency, flush, and release. `file_test.go` covers unknown-size object reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_test.go -->
# sources/user-network-fs/rclone/vfs/read_test.go

## Purpose
Tests the direct read-only `ReadFileHandle` path used when VFS cache is not providing a RW cache handle.

## Important APIs, Types, and Functions
Helpers are `readHandleCreate` and `readString`. Tests are `TestReadFileHandleMethods`, `TestReadFileHandleSeek`, `TestReadFileHandleReadAt`, `TestReadFileHandleFlush`, and `TestReadFileHandleRelease`.

## Control Flow
The helper writes `dir/file1` with known contents, opens it read-only through `VFS.OpenFile`, asserts the returned handle type, then tests handle methods. Seek tests use start/current/end whence values and delayed read errors for off-end seeks. ReadAt tests exercise forward and backward seeks and reads crossing EOF.

## State and Persistence Behavior
The tests do not mutate remote contents. They validate in-memory offset movement, closed state, EOF behavior, `noSeek` behavior, and that `Flush` does not close the handle while `Release` closes after reading.

## Dependencies and Integration Points
Uses `fstest`, shared test VFS helpers, standard `io` and `os` flags, and testify assertions. It indirectly validates `VFS.OpenFile`, `File.openRead`, and `ReadFileHandle`.

## Risks and Edge Cases
The tests do not exercise checksum mismatch, low-level retry, sequential wait concurrency, chunk stream options, unknown-size objects, or source disappearance during close/hash. Those behaviors remain integration-risk areas.

## Test Signals
Strong signal for normal read handle API compatibility, offset handling, EOF semantics, close/flush/release behavior, and read-after-close error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write.go -->
# sources/user-network-fs/rclone/vfs/read_write.go

## Purpose
Implements `RWFileHandle`, the cache-backed file handle for read/write, write-only with cache, and cache-mode read paths. It uses `vfscache.Item` as the local backing file and schedules writeback on close.

## Important APIs, Types, and Functions
Key APIs are `RWFileHandle`, `newRWFileHandle`, `readOnly`, `writeOnly`, `openPending`, `Read`, `ReadAt`, `Seek`, `Write`, `WriteAt`, `WriteString`, `Truncate`, `Sync`, `Flush`, `Release`, `Close`, `Size`, `Stat`, and unsupported OS-file methods.

## Control Flow
Construction obtains a cache item, determines existence from `File` or unwritten cache state, enforces `O_CREATE|O_EXCL`, truncates immediately for `O_TRUNC` or new create, marks dirty when needed, and registers a writer for non-read-only handles. `openPending` serializes with `File.muRW`, opens the cache item against the current object, sets append or start offset, marks opened, and inserts the object into the directory cache. Reads and writes check closed/access mode, open lazily, then delegate to `Item.ReadAt`/`WriteAt`; writes update size and append offsets. Close updates file size, closes the item with `file.setObject`, applies pending modtime for unopened handles, and deregisters writers.

## State and Persistence Behavior
Persistent writes are local until `Item.Close` and writeback upload. `File.size`, writer count, dirty state, pending modtimes, and directory virtual entries are updated during handle lifetime. `Sync` flushes the local cache item, not necessarily remote upload completion. Close errors intentionally leave cache files around for recovery.

## Dependencies and Integration Points
Depends on `vfscache.Item`, `File` writer tracking, `Dir.addObject`, VFS cache options, and writeback behavior hidden behind `Item.Close`. It is selected by `File.Open` for cache modes and many read/write flag combinations.

## Risks and Edge Cases
`Fd` returns a placeholder `0xdeadbeef`. Locking deliberately releases `fh.mu` around `ReadAt`/`WriteAt` I/O when requested, which requires careful state consistency. `O_SYNC` is not a real remote sync. Unopened handles can close without opening and only apply pending modtime. Append mode modifies `WriteAt` semantics by writing at EOF, matching POSIX append but surprising for positional writes.

## Test Signals
`read_write_test.go` covers method behavior, seeks, read/write/read-at/write-at, truncation, size updates, open flag matrix for writes/full cache modes, modtime with open writers, cache rename, and external update refresh.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write_test.go -->
# sources/user-network-fs/rclone/vfs/read_write_test.go

## Purpose
Tests cache-backed `RWFileHandle` behavior for read-only, write-only, read/write open modes, size tracking, truncation, open flag compatibility, modtime writeback, cache rename, and cache refresh after external remote updates.

## Important APIs, Types, and Functions
Helpers include `rwHandleCreateFlags`, `rwHandleCreateReadOnly`, `rwHandleCreateWriteOnly`, `rwReadString`, `assertSize`, and `testRWFileHandleOpenTest`. Main tests cover methods, seek/read/read-at, flush/release, write/write-at/no-write, size cases, generated open matrix, modtime with open writers, rename, and cache update.

## Control Flow
Most tests create a full-cache VFS with short writeback delay, perform handle operations, close or release, wait for writers, and validate VFS listing plus remote contents. The open matrix creates nonexistent and existing files for each generated `openTest`, probes reads/writes, and compares expected errors and final contents for both `CacheModeWrites` and `CacheModeFull`.

## State and Persistence Behavior
Tests validate local cache state, remote upload state after writer drain, `File.Size` visibility while handles are open, dirty empty-file creation, pending modtime application, and cache item rename after VFS rename. `TestRWCacheUpdate` verifies cache and stat data refresh after external remote content changes and directory cache expiry.

## Dependencies and Integration Points
Uses `open_test.go`, `operations.CanServerSideMove`, `fstest`, VFS cache/writeback options, and shared test helpers. It exercises integration among `VFS.OpenFile`, `File.Open`, `RWFileHandle`, `vfscache.Item`, directory cache, and remote listing.

## Risks and Edge Cases
Coverage is strongest for cache modes, not uncached streaming writes. Some behavior depends on backend support for empty uploads, modtime precision, and server-side move. Concurrent RW handles and writeback failure recovery are not deeply covered here.

## Test Signals
Very strong signal for cached file handle semantics, POSIX-like open flag behavior, size and truncation correctness, and cache coherency after rename/external updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read_write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup.go -->
# sources/user-network-fs/rclone/vfs/sighup.go

## Purpose
Provides supported-platform SIGHUP notification wiring for VFS directory-cache reload.

## Important APIs, Types, and Functions
Defines `NotifyOnSigHup(sighupChan chan os.Signal)` for builds excluding Plan 9 and JavaScript/WASM.

## Control Flow
The function calls `signal.Notify(sighupChan, syscall.SIGHUP)`. `VFS.signalHandler` in `vfs.go` consumes that channel and forgets the root directory cache on signal.

## State and Persistence Behavior
No persisted state. Registers process-level signal delivery for the provided channel until normal signal package semantics are changed elsewhere.

## Dependencies and Integration Points
Depends on `os/signal` and `syscall`. Integrated by `New`, which starts a signal handler goroutine for each VFS instance.

## Risks and Edge Cases
Multiple active VFS instances each register a channel for SIGHUP, so one signal can prompt multiple cache forgets. There is no explicit `signal.Stop` in this helper. Unsupported targets use the no-op file.

## Test Signals
No direct tests in this subset. Behavior is indirectly tied to `VFS.signalHandler`, which is also not directly tested here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup_unsupported.go -->
# sources/user-network-fs/rclone/vfs/sighup_unsupported.go

## Purpose
Provides a no-op SIGHUP notification implementation for Plan 9 and JavaScript/WASM builds where Unix SIGHUP is unavailable.

## Important APIs, Types, and Functions
Defines the same `NotifyOnSigHup(sighupChan chan os.Signal)` API as `sighup.go`, selected by build tags `plan9 || js`.

## Control Flow
The function intentionally does nothing, allowing `VFS.signalHandler` to wait only for context cancellation on unsupported platforms.

## State and Persistence Behavior
No state and no persistence.

## Dependencies and Integration Points
Imports only `os` for the channel type. Integrates with `vfs.go` through build-tag polymorphism.

## Risks and Edge Cases
On unsupported platforms, users cannot trigger directory-cache flush through SIGHUP. The goroutine still exists but receives no signal events.

## Test Signals
No direct tests. Build tag coverage is expected from platform compilation rather than runtime tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/test_vfs/test_vfs.go -->
# sources/user-network-fs/rclone/vfs/test_vfs/test_vfs.go

## Purpose
Standalone stress tool for a mounted VFS directory. It randomly creates, opens, reads, writes, renames, lists, and removes files or directories to expose deadlocks and state inconsistencies.

## Important APIs, Types, and Functions
Defines command-line flags for name length, verbosity, worker count, iterations, and timeout; `Test` state; `NewTest`; operation methods `list`, `rename`, `open`, `close`, `read`, `write`, `remove`, `mkdir`, `rmdir`; `Tidy`; `RandomTests`; and `main`.

## Control Flow
`main` creates the target directory, starts multiple goroutines, and each goroutine creates a `Test` that randomly chooses file or directory operations for a configured number of iterations. A per-test timer is reset before each operation and signals a deadlock if no progress occurs within the timeout.

## State and Persistence Behavior
Mutates the mounted filesystem directly via `os` and `rclone/lib/file`. Each `Test` tracks current name, created state, optional open handle, file-vs-dir mode, and timeout timer. `Tidy` closes and removes any remaining test path.

## Dependencies and Integration Points
Uses standard OS filesystem calls against an already mounted VFS, plus rclone logging, random name generation, and file wrappers. It is not part of normal package tests and is intended as an external harness.

## Risks and Edge Cases
The tool reports errors but generally continues; it is stochastic, so failures may be non-reproducible without logging. Directory and file operations are isolated per random name, so it stresses handle/lifecycle behavior more than shared-path write conflicts. `kick` drains timer channels and must be used carefully to avoid timer races.

## Test Signals
Useful manual signal for deadlocks under concurrent mixed operations on real mounts. It complements unit tests by exercising actual OS/mount interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/test_vfs/test_vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs.go -->
# sources/user-network-fs/rclone/vfs/vfs.go

## Purpose
Defines the top-level VFS abstraction, common node/handle interfaces, active VFS reuse, cache setup/shutdown, directory cache refresh, stat/open helpers, filesystem statistics, file/directory convenience operations, virtual entries, symlink APIs, and metadata-file detection.

## Important APIs, Types, and Functions
Key types are `Node`, `Nodes`, `Noder`, `OsFiler`, `Handle`, `baseHandle`, and `VFS`. Key functions/methods include `Help`, `New`, `Stats`, `activeCacheEntries`, `SetCacheMode`, `Shutdown`, `CleanUp`, `FlushDirCache`, `WaitForWriters`, `Root`, `newInode`, `Stat`, `StatParent`, `decodeOpenFlags`, `OpenFile`, `Open`, `Create`, `Rename`, `Statfs`, `Remove`, `Chtimes`, `Mkdir`, `MkdirAll`, `ReadDir`, `ReadFile`, `WriteFile`, `AddVirtual`, `Readlink`, `CreateSymlink`, `Symlink`, and `isMetadataFile`.

## Control Flow
`New` copies configuration into a non-cancelled context, initializes options, reuses an active VFS with identical options when possible, registers the new VFS globally, creates root `Dir`, starts change notification and SIGHUP handling, optionally refreshes the dir cache, and enables cache mode. `OpenFile` enforces `O_RDONLY|O_TRUNC` invalidity, stats or creates a file, then delegates to node `Open`. Path operations resolve through `Stat` and `StatParent`. `Statfs` uses backend `About` or optional size walk and caches usage for `DirCacheTime`.

## State and Persistence Behavior
Maintains active VFS registry, in-use counts, root directory cache, optional disk cache, usage cache, poll channel, cancellation functions, and inode counter. Persistent effects occur through delegated file/dir operations, cache cleanup, directory creation/removal, write file, symlink creation, and cache virtual entry insertion. `Shutdown` decrements refcount before actually removing active entries and cancelling goroutines.

## Dependencies and Integration Points
Integrates with `fs.Fs` features, `vfscache`, `vfscommon.Options`, `Dir`, `File`, rc stats, filter/config contexts, change notification, `walk.ListR`, and mount-facing `Handle` interfaces. `go:generate` ties this file to generated open tests.

## Risks and Edge Cases
Active VFS reuse depends on full option equality. `WaitForWriters` logs `vfs.cache.Dump()` on timeout even when cache could be nil if writers remain without cache. `AddVirtual` ignores its `isDir` argument and always passes `false` to `Dir.AddVirtual` in this version. SIGHUP handlers are started per VFS. `Statfs` with `UsedIsSize` can be expensive because it walks the whole remote.

## Test Signals
`vfs_test.go` covers base handle defaults, construction/reuse/shutdown, permissions option initialization, root/stat/stat-parent/open/rename/statfs/mkdir/mkdir-all, missing-size filling, and metadata extension. `vfs_case_test.go` covers case-insensitive and Unicode normalization lookups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_case_test.go -->
# sources/user-network-fs/rclone/vfs/vfs_case_test.go

## Purpose
Tests VFS path lookup behavior for case-insensitive mode and Unicode normalization.

## Important APIs, Types, and Functions
Main tests are `TestCaseSensitivity` and `TestUnicodeNormalization`; helpers are `checkFileDataVFS`, `assertFileDataVFS`, and `assertFileAbsentVFS`.

## Control Flow
Case testing creates remote files whose names differ by case, builds case-sensitive and case-insensitive VFS instances, verifies normal lookup, detects whether the backend truly preserves case-sensitive distinct objects, then tests folded lookup and ambiguous folded names. Unicode testing creates NFC and plain-name files, reads them through NFD names, then toggles global `NoUnicodeNormalization` and verifies normalized lookup behavior changes.

## State and Persistence Behavior
Tests persist remote objects through `fstest.Run`; VFS instances maintain their own directory caches. The Unicode test temporarily mutates global config `NoUnicodeNormalization` and restores it with `defer`.

## Dependencies and Integration Points
Uses `fstest`, `vfscommon.Options.CaseInsensitive`, global `fs.GetConfig`, and `golang.org/x/text/unicode/norm`. It depends on `Dir` lookup behavior not present in this subset but validates it through `VFS.OpenFile`.

## Risks and Edge Cases
Case tests skip when backend cannot provide meaningful case-sensitive behavior. Ambiguous case-insensitive lookups only assert an error other than `ENOENT`, not a specific error. Global config mutation can affect parallel tests if not isolated.

## Test Signals
Strong signal for lookup normalization behavior and ambiguous case-folded names. It validates user-visible path compatibility across remotes with different case and Unicode semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_case_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_test.go -->
# sources/user-network-fs/rclone/vfs/vfs_test.go

## Purpose
Provides the core VFS test harness and tests top-level VFS construction, interface defaults, stat/open/rename/statfs/directory operations, missing usage calculations, and metadata extension detection.

## Important APIs, Types, and Functions
Defines shared test times, writeback wait constants, `TestMain`, `cleanupVFS`, `newTestVFSOpt`, and `newTestVFS`. Tests include `TestVFSbaseHandle`, `TestVFSNew`, `TestVFSNewWithOpts`, `TestVFSRoot`, `TestVFSStat`, `TestVFSStatParent`, `TestVFSOpenFile`, `TestVFSRename`, `TestVFSStatfs`, `TestVFSMkdir`, `TestVFSMkdirAll`, `TestFillInMissingSizes`, and `TestVFSIsMetadataFile`.

## Control Flow
Helpers create `fstest` remotes and register cleanup that waits for writers, cleans cache, and shuts down VFS. Tests perform VFS API calls and compare returned nodes, errors, remote listings, usage values, and option-derived permissions.

## State and Persistence Behavior
Tests exercise active VFS cache refcounts, cache cleanup, root directory cache, remote object/directory mutations, usage cache, and metadata-extension option mutation. Directory tests skip when backend cannot have empty directories.

## Dependencies and Integration Points
Uses `fstest`, `vfscommon.Options`, `fs.Features`, and the package's `Dir`, `File`, and `Handle` implementations. Many other tests in this subset depend on its helpers and constants.

## Risks and Edge Cases
`TestVFSStatfs` has conditional expectations based on backend `About` support, so coverage varies. Directory tests skip on remotes without empty directories. Symlink APIs, `ReadDir`, `ReadFile`, `WriteFile`, `Chtimes`, `FlushDirCache`, and `WaitForWriters` failure logging are not fully tested here.

## Test Signals
Strong baseline signal for top-level VFS API compatibility with Go `os`-like behavior and for shared test setup used by the rest of the VFS tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache.go -->
# sources/user-network-fs/rclone/vfs/vfscache/cache.go

## Purpose
Implements the VFS disk cache manager: local data/meta roots, cache item registry, writeback queue access, cache reload, rename/remove, virtual entry callback, quota/age cleanup, out-of-space handling, stats, and background cleaner.

## Important APIs, Types, and Functions
Key type is `Cache`; key APIs are `New`, `Stats`, `Queue`, `QueueSetExpiry`, `Item`, `Exists`, `InUse`, `DirtyItem`, `Rename`, `DirRename`, `Remove`, `SetModTime`, `CleanUp`, `KickCleaner`, `TotalInUse`, `Dump`, and `AddVirtual`. Important internals include path conversion helpers, `reload`, `purgeOld`, `purgeClean`, `purgeOverQuota`, `purgeEmptyDirs`, `updateUsed`, quota checks, and `cleaner`.

## Control Flow
`New` computes encoded cache paths under the rclone cache dir, creates data and metadata roots, creates local backend handles, selects a common hash, initializes maps and writeback queue, reloads existing cache files/meta, purges empty dirs, and starts a cleaner goroutine. Item access normalizes names and lazily creates `Item`s. Cleaner runs immediately and on interval or kick, purging by age, quota, and clean reset eligibility, then updates systemd status.

## State and Persistence Behavior
Persistent cache state lives under `vfs` and `vfsMeta` roots. In-memory state tracks `item`, `errItems`, `used`, `outOfSpace`, cleaner kick status, and writeback queue. Rename moves data/meta files and remaps item keys. Remove deletes item state and local files and reports whether upload was pending. Cleanup removes both root trees.

## Dependencies and Integration Points
Depends on `vfscache.Item` and `writeback`, local backend via `fs/cache`, disk usage checks, `operations.Rmdirs`, `systemd.UpdateStatus`, `vfscommon.Options`, path encoding, and VFS `AddVirtual` callback. `VFS.SetCacheMode`, `RWFileHandle`, and rc queue/stats endpoints use this cache.

## Risks and Edge Cases
Cache and item lock ordering is critical. `KickCleaner` blocks callers until `outOfSpace` clears. `purgeClean` can leave dirty or in-use data and tracks failed resets in `errItems`. `reload` logs per-item reload failures but continues. Path encoding around Windows UNC and drive separators is delicate. Quota behavior relies on local disk usage availability and may treat unsupported disk usage as OK.

## Test Signals
`cache_test.go` covers creation, open counts, mkdir/purge, age purge, quota purge, min-free-space checks, clean reset purge, in-use/dirty/existence/remove/rename, cleaner loop, modtime, total in use, dump, stats, queue, and queue expiry plumbing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache_test.go -->
# sources/user-network-fs/rclone/vfs/vfscache/cache_test.go

## Purpose
Tests the `vfscache.Cache` manager's lifecycle, item registry, local path creation, purging, quota enforcement, rename/remove behavior, cleaner loop, modtime setting, stats, and writeback queue plumbing.

## Important APIs, Types, and Functions
Helpers include `itemAsString`, `itemSpaceAsString`, `itemWrite`, path assertions, `addVirtual`, `newTestCacheOpt`, and `newTestCache`. Tests cover `New`, open counts, mkdir behavior, purge old, purge over quota, min free space, purge clean, in-use, dirty item, exists/remove, rename, cleaner, set modtime, total in use, dump, stats, queue, and queue expiry.

## Control Flow
Each test creates a test remote and cache with cleaner/writeback/handle caching mostly disabled for determinism. Tests create/open/truncate/close cache items, manipulate access times and quota options, call purge/clean methods directly, and assert item maps, local filesystem paths, `used` totals, and returned rc parameters.

## State and Persistence Behavior
Tests validate both in-memory `c.item` and actual files under cache data/meta roots. Cleanup removes cache roots and cancels the context. Some tests directly adjust item metadata such as `ATime` to force eviction order.

## Dependencies and Integration Points
Uses local backend import, `fstest`, `diskusage`, `config.GetCacheDir`, `writeback`, `vfscommon.Options`, and item helpers from other vfscache tests. It exercises cache/item/writeback interactions but usually disables background behavior for deterministic direct calls.

## Risks and Edge Cases
Many tests inspect internal fields, making them sensitive to representation changes. Min-free-space behavior is skipped when disk usage is unsupported and depends on actual host free space. Cleaner timing test uses eventual sleeps and may be timing-sensitive.

## Test Signals
Strong signal for cache eviction, quota accounting, local persistence paths, rename/remove integrity, and rc stats/queue plumbing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders.go -->
# sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders.go

## Purpose
Implements range downloader orchestration for VFS cache items. It starts and reuses background download streams, writes downloaded bytes into cache without overwriting existing ranges, wakes waiters when requested ranges arrive, and handles downloader idle/error shutdown.

## Important APIs, Types, and Functions
Key APIs are `Item`, `Downloaders`, `New`, `Download`, `EnsureDownloader`, `Close`, and internal `_ensureDownloader`, `_dispatchWaiters`, `kickWaiters`, `_newDownloader`, `_countErrors`. The `downloader` type provides `Write`, `open`, `close`, `stopAndClose`, `download`, `setRange`, and `getRange`.

## Control Flow
`Download` creates a waiter for a range, ensures a downloader exists, and blocks for waiter completion. `EnsureDownloader` starts or extends a downloader without waiting. `_ensureDownloader` expands ranges by read-ahead, clips to missing data, reuses a downloader if the desired start is within its current window, or starts a new downloader. Downloader goroutines open a chunked reader at an offset, stream via accounting into `downloader.Write`, and kick waiters as ranges become present. A background ticker periodically kicks waiters to recover from missed events/errors.

## State and Persistence Behavior
State is in-memory downloader lists, waiters, error counts, and per-downloader offsets/ranges. Persistence occurs only through the supplied `Item.WriteAtNoOverwrite`, which writes cache data/range state. `Close` cancels context, stops downloaders, waits for goroutines, and closes pending waiters with an error.

## Dependencies and Integration Points
Depends on `fs.Object`, `chunkedreader`, `accounting`, `asyncreader`, `ranges`, `fserrors`, VFS read-ahead/chunk/buffer options, and the cache item implementation. Used by vfscache items to populate local cache ranges on demand.

## Risks and Edge Cases
Unknown-sized source objects are rejected. `max downloaders` is a FIXME, so many distant reads could create many streams. Error policy closes waiters immediately for no-space and after more than ten errors. Idle downloaders stop after five seconds, and streams stop after skipping too much already-present data. Correctness depends on `Item.FindMissing`, `HasRange`, and `WriteAtNoOverwrite` being race-safe.

## Test Signals
`downloaders_test.go` validates blocking `Download` and asynchronous `EnsureDownloader` against a large pattern file, checking downloaded ranges become present and contents are correct through the fake item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders_test.go -->
# sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders_test.go

## Purpose
Tests the downloader orchestration package with a fake range-tracking item and a real remote test object.

## Important APIs, Types, and Functions
Defines `testItem` implementing downloader `Item` through `HasRange`, `FindMissing`, and `WriteAtNoOverwrite`. `TestDownloaders` contains `Download` and `EnsureDownloader` subtests.

## Control Flow
The test writes a large deterministic pattern object with `operations.RcatSize`, constructs a fresh `Downloaders` for each subtest, and closes it at the end. `Download` requests several sparse ranges and asserts they are present after the call returns. `EnsureDownloader` starts an async downloader and uses `assert.Eventually` until the requested range appears.

## State and Persistence Behavior
The fake item stores downloaded ranges in memory and verifies bytes against `readers.NewPatternReader` before marking ranges present. No cache files are written by this test; the source object is persisted to the `fstest` remote.

## Dependencies and Integration Points
Uses local backend import, `fstest`, `operations.RcatSize`, `ranges`, pattern readers, VFS default options, and the real downloader/chunked reader pipeline.

## Risks and Edge Cases
The fake `WriteAtNoOverwrite` reports no skipped bytes, so skip/stop behavior is not tested. Error handling, no-space handling, unknown-size rejection, downloader reuse windows, read-ahead expansion, and close-with-waiters are not deeply covered.

## Test Signals
Good signal for basic range download completion and byte correctness. Limited signal for failure and resource-management paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/downloaders/downloaders_test.go -->
