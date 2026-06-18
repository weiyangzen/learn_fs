# subset-b-009794 Research

Grouped research for the listed rclone VFS and rpcbind files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/item.go -->
# sources/user-network-fs/rclone/vfs/vfscache/item.go

## Purpose
Implements `vfscache.Item`, the per-file unit of rclone's VFS cache. It owns the sparse local cache file, persisted JSON metadata, downloader coordination, dirty/writeback state, and ENOSPC reset behavior for one VFS path.

## APIs, Flow, And State
Key types are `Item`, persisted `Info`, `Items` sorted by access time, `ResetResult`, and `StoreFn`. `newItem` reconciles cache file and metadata existence, loads `Info`, and estimates size. `Open`/`open` validate remote fingerprints, create cache directories/files, reuse handle-caching grace-period handles when safe, register the item back into `Cache`, and create downloaders for remote-backed files. Reads call `preAccess`, `_ensure` missing ranges, read from `fd`, and retry on no-space errors after kicking the cleaner. Writes update ranges, size, dirty metadata, and cancel pending writebacks when a new modification arrives. `Close` either starts a grace timer for clean handles or `_actualClose`s: it drains missing dirty ranges, closes downloaders and the file descriptor, saves metadata, sets cache-file modtime, and stores immediately or queues asynchronous writeback. `Reset` is the cache cleaner's recovery path, skipping dirty, grace, pending-access, or empty items and otherwise rebuilding clean cache files.

## Dependencies And Integration
Depends on `fs`, `fserrors`, `operations.Copy`, sparse-file helpers, `ranges.Ranges`, `downloaders`, and `writeback`. It is tightly coupled to `Cache` lock ordering, downloader lock ordering, and writeback lock ordering. Persistence is the local cache data file plus `toOSPathMeta` JSON. Remote integration is via `fs.Object`, fingerprints, `fcache.NewObject`, `fremote`, and `Cache.AddVirtual`.

## Risks And Test Signals
Primary risks are lock-order deadlocks, dirty data loss during stale fingerprint handling, writeback cancellation races, grace-period reuse of stale descriptors, and ENOSPC recovery leaving waiters blocked. Tests in `item_test.go` cover existence, metadata reload, dirty/truncate/read/write behavior, large sequential/random/concurrent reads, stale/remote-gone reloads, and handle-caching reset semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/item.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/item_test.go -->
# sources/user-network-fs/rclone/vfs/vfscache/item_test.go

## Purpose
Exercises `vfscache.Item` behavior against a test cache and remote, including dirty state, sparse ranges, metadata reload, writeback, random reads, and handle-caching behavior.

## APIs, Flow, And State
Helpers create a cache with cleaner disabled, synchronous writeback, and usually no handle caching. Tests open cache items, write or read ranges, close to trigger store/writeback, then validate remote object contents. Metadata tests remove items from `Cache.item` and force reload from disk. The large read/write test writes a 50 MiB pattern, removes local cache data, then verifies sequential, random, concurrent, and reverse reads rehydrate ranges correctly. Handle-caching tests configure `HandleCaching`, assert descriptors/downloaders remain alive during grace, are reused on reopen, and eventually close.

## Dependencies And Integration
Uses `fstest`, random/pattern readers, `vfscommon.Opt`, direct cache internals, and the in-memory `avInfos` test hook for `AddVirtual`. It is the main regression suite for `item.go` interactions with remote objects, metadata, downloaders, and writeback.

## Risks And Test Signals
The tests are stateful and depend on timing for grace-period expiry, so sleeps can be flaky under heavy load. They give strong signal for range accounting, stale fingerprint invalidation, remote-deleted recovery, reload of dirty cache entries, and concurrent downloader safety. A FIXME notes async writeback coverage is still missing here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/item_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback.go -->
# sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback.go

## Purpose
Provides the delayed writeback scheduler used by VFS cache items. It queues dirty files, uploads them after `--vfs-write-back`, retries failures with backoff, and allows updates, cancellations, renames, stats, queue inspection, and manual expiry changes.

## APIs, Flow, And State
Public APIs are `New`, `SetID`, `Add`, `Remove`, `Rename`, `Stats`, `Queue`, and `SetExpiry`. `WriteBack` holds a mutex, atomic handle counter, heap of not-yet-uploading `writeBackItem`s, lookup map for queued or uploading items, timer state, and upload count. `Add` either creates an item or updates an existing one; if an upload is active and the file was modified, it cancels and requeues. `processItems` pops expired heap entries until the global transfer limit is reached, starts uploads with cancelable contexts, and stops the timer when the transfer cap blocks progress. `upload` calls the item-supplied `PutFn`, removes successful entries, or requeues failures with exponential delay capped at five minutes. `Rename` cancels active upload, removes duplicate-name queue entries, updates the name, and defers retry.

## Dependencies And Integration
Uses `container/heap`, timers, context cancellation, `fs.GetConfig(...).Transfers`, and `vfscommon.Options.WriteBack`. `vfscache.Item` stores the handle and supplies the `PutFn` that copies local cache data to the remote.

## Risks And Test Signals
Risks include heap index corruption, cancellation deadlocks while waiting for upload goroutines, stale duplicate entries after renames, and stopped timers when transfer capacity becomes available later. Tests cover heap ordering, CRUD helpers, timer state, success/failure retry, modified and unmodified update paths, stats/queue output, expiry mutation, transfer limits, renames, duplicate removal, and explicit upload cancellation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback_test.go -->
# sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback_test.go

## Purpose
Validates the writeback scheduler's priority queue, timer, retry, cancellation, rename, duplicate, and stats behavior with controllable fake upload functions.

## APIs, Flow, And State
`newTestWriteBack` creates a scheduler with 100 ms writeback delay. `putItem` simulates an upload using channels for start, completion, and cancellation. Heap helper assertions check `onHeap`, lookup membership, and index consistency. Tests progress queued items through automatic timers, finish uploads with nil or error, and inspect whether items remain in the heap/lookup map.

## Dependencies And Integration
Uses `fs.GetConfig(ctx).Transfers` to test concurrency caps and `vfscommon.Opt` for scheduler timing. The fake `PutFn` focuses tests on scheduler state rather than remote IO.

## Risks And Test Signals
Timing-driven tests can be sensitive to slow environments, but the channel-based fake upload makes most transitions deterministic. Coverage is strong for scheduler invariants, including failure backoff, cancellation on modified updates, no cancellation for unmodified updates, queue JSON fields, `SetExpiry`, transfer-limit timer stopping, rename requeue, duplicate-name eviction, and explicit `cancelUpload`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscache/writeback/writeback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/cachemode.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/cachemode.go

## Purpose
Defines the typed VFS cache-mode enum used by command-line flags, config, JSON, and VFS behavior selection.

## APIs, Flow, And State
`cacheModeChoices.Choices` maps enum values to `off`, `minimal`, `writes`, and `full`. `CacheMode` is an alias of rclone's generic `fs.Enum`, with constants ordered from least to most caching. `Type` returns `CacheMode` for flag reporting. There is no persistence beyond config serialization by the shared enum machinery.

## Dependencies And Integration
Depends on `github.com/rclone/rclone/fs`. `Options.CacheMode`, VFS open logic, tests, and mount flags use these values to choose cache semantics.

## Risks And Test Signals
The integer order is semantically important because tests and code compare modes with `<`. Adding a mode requires preserving ordering and updating tests/documentation. `cachemode_test.go` verifies string conversion, parsing, JSON unmarshalling, and invalid values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/cachemode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/cachemode_test.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/cachemode_test.go

## Purpose
Tests the `CacheMode` enum's flag and JSON behavior.

## APIs, Flow, And State
Compile-time assertions ensure `*CacheMode` implements `pflag.Value` and `json.Unmarshaler`. Tests verify string names for known and unknown values, parsing of valid and invalid strings, `Type`, JSON string unmarshalling, numeric unmarshalling, and rejection of out-of-range numbers.

## Dependencies And Integration
Uses the generic `fs.Enum` behavior indirectly through `CacheMode`. These tests protect command-line and config compatibility for VFS cache modes.

## Risks And Test Signals
The tests catch broken enum mappings and invalid-value handling. They do not exercise VFS behavior per mode; that is covered in the functional `vfstest` suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/cachemode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/filemode.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/filemode.go

## Purpose
Wraps `os.FileMode` in a flag/config-friendly type for VFS file, directory, link, and umask options.

## APIs, Flow, And State
`FileMode.String` formats permissions as octal, `Set` parses octal text, `Type` identifies the flag type, and `UnmarshalJSON` accepts either string or integer config through `fs.UnmarshalJSONFlag`. No mutable package state is held.

## Dependencies And Integration
Used by `Options` for `DirPerms`, `FilePerms`, `LinkPerms`, and `Umask`. Integrated with rclone's config and flag systems through `fs.Flagger` support.

## Risks And Test Signals
Misparsing modes can produce incorrect mounted permissions or accept invalid octal values. `filemode_test.go` verifies formatting, octal parsing, invalid decimal-like digits, and JSON string/integer handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/filemode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/filemode_test.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/filemode_test.go

## Purpose
Tests `FileMode` formatting, flag parsing, and JSON unmarshalling.

## APIs, Flow, And State
Interface assertions check `fs.Flagger` and non-pointer flag support. Table tests cover zero, standard permissions, high bits such as `02666`, invalid octal `999`, JSON strings, JSON integers, and expected resulting `FileMode` values.

## Dependencies And Integration
Uses `fs` flag interfaces and Go `encoding/json`. The tests support VFS option correctness for permission-related flags.

## Risks And Test Signals
Coverage is narrowly focused on serialization and parsing. It does not validate the later umask masking in `Options.Init`, but it catches the main user-facing parse errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/filemode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/options.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/options.go

## Purpose
Defines the global VFS option schema and the runtime `Options` struct used to configure rclone's VFS and mount behavior.

## APIs, Flow, And State
`OptionsInfo` lists all registered VFS options: modtime/checksum/seek behavior, directory cache and polling, read-only and symlink handling, cache mode and cache limits, read chunking, permissions/uid/gid, case handling, write/read waits, writeback delay, read-ahead, used-size algorithm, fingerprint mode, disk space reporting, handle caching, and metadata extension. `init` registers these global options as `vfs`. `Options` mirrors the config keys. `Init` applies global `--links`, masks permissions by umask, and forces directory and symlink mode bits.

## Dependencies And Integration
Depends on `fs.Options`, `fs.Duration`, `fs.SizeSuffix`, platform-specific `getUmask/getUID/getGID`, `CacheMode`, and `FileMode`. Every VFS, cache, writeback, mount, and functional test path consumes this struct.

## Risks And Test Signals
Defaults are behavioral contract: changing cache/writeback/handle-caching defaults affects IO timing and persistence. Permission normalization is platform-sensitive. Direct tests are light, but broad signal comes from VFS and vfstest suites using `vfscommon.Opt` and calling `Init`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/path.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/path.go

## Purpose
Provides parent-directory helpers for OS-native paths and rclone slash-separated paths.

## APIs, Flow, And State
`OSFindParent` wraps `filepath.Dir` and normalizes `.` or filesystem root to an empty parent. `FindParent` does the same for slash paths with `path.Dir`. There is no state or persistence.

## Dependencies And Integration
Used by VFS path-resolution code that needs a parent path without leaking Go's `.` or `/` root conventions into rclone logic.

## Risks And Test Signals
Root and platform separator handling are the main risks. The helpers are small and not directly tested in this subset; caller tests around stat/open/rename parent behavior provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_non_unix.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_non_unix.go

## Purpose
Supplies default umask, uid, and gid values for platforms outside Linux, Darwin, and FreeBSD.

## APIs, Flow, And State
`getUmask` returns `0000`. `getUID` and `getGID` return all-ones `uint32`, which signals WinFSP-FUSE-style code to use the current user. There is no runtime state.

## Dependencies And Integration
Selected by build tags `!linux && !darwin && !freebsd` and used as defaults in `OptionsInfo`.

## Risks And Test Signals
The sentinel UID/GID semantics are platform-specific. Incorrect defaults can surface as odd ownership on mounted files. Coverage is mostly build-tag compilation and platform-specific mount testing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_non_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_unix.go -->
# sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_unix.go

## Purpose
Supplies Unix-family defaults for VFS umask, uid, and gid options.

## APIs, Flow, And State
`getUmask` temporarily sets umask to zero to read the current value, then restores it. `getUID` and `getGID` return effective user and group IDs. No state is retained, but `getUmask` briefly mutates process-global umask.

## Dependencies And Integration
Selected on Linux, Darwin, and FreeBSD. Uses `golang.org/x/sys/unix` and feeds defaults into `OptionsInfo`.

## Risks And Test Signals
Because umask is process-global, concurrent calls during startup would be sensitive, though option initialization is expected early. Tests indirectly validate permissions through `vfstest` directory/file/link mode checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfscommon/vfsflags_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfsflags/vfsflags.go -->
# sources/user-network-fs/rclone/vfs/vfsflags/vfsflags.go

## Purpose
Registers VFS command-line flags on a provided `pflag.FlagSet`.

## APIs, Flow, And State
`AddFlags` delegates to `flags.AddFlagsFromOptions` with `vfscommon.OptionsInfo`. It has no own state; it projects the shared option schema into CLI flags.

## Dependencies And Integration
Depends on rclone's config flag helper, `vfscommon`, and `spf13/pflag`. Mount commands call this package to expose VFS options.

## Risks And Test Signals
The file is thin, so risks are mostly drift in `OptionsInfo` or wrong prefix use. CLI/config integration tests elsewhere are the meaningful signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfsflags/vfsflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/dir.go -->
# sources/user-network-fs/rclone/vfs/vfstest/dir.go

## Purpose
Contains functional directory tests shared by direct VFS and mounted filesystem runs.

## APIs, Flow, And State
Tests cover directory listing, creating/removing empty and non-empty directories, file creation/removal inside directories, file rename, empty directory rename, full directory rename, directory modtime, explicit directory-cache flush, and cache flush on directory rename. They use the global `run` harness to create local operations, inspect local and remote trees, and call `forget`.

## Dependencies And Integration
Depends on `vfstest.Run`, remote `Mkdir`, and `Run.checkDir`, which compares FUSE/VFS view against remote listing with retry for eventual consistency.

## Risks And Test Signals
These tests detect stale directory caches, missing rename propagation, permission drift, and incorrect non-empty directory removal. They are skipped when FUSE/direct prerequisites are unavailable through harness checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/dir_non_unix.go -->
# sources/user-network-fs/rclone/vfs/vfstest/dir_non_unix.go

## Purpose
Provides the non-Unix fallback for the directory rewind test.

## APIs, Flow, And State
`TestDirRewind` simply skips with the current `runtime.GOOS`. It has no persistent state.

## Dependencies And Integration
Selected outside Linux, Darwin, and FreeBSD so the package still exposes a `TestDirRewind` symbol without raw `getdents` dependencies.

## Risks And Test Signals
The skip means directory stream rewind behavior is untested on these platforms. The useful signal is that unsupported builds compile cleanly and report an explicit skip.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/dir_non_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/dir_unix.go -->
# sources/user-network-fs/rclone/vfs/vfstest/dir_unix.go

## Purpose
Tests that rewinding a mounted directory stream returns the same entries after `lseek(fd, 0, SEEK_SET)`.

## APIs, Flow, And State
`countDirFd` reads raw directory entries from a file descriptor with `syscall.ReadDirent` and parses names. `TestDirRewind` creates a directory with three files, reads once, seeks back to zero, reads again, and compares counts.

## Dependencies And Integration
Unix build-tagged file for Linux, Darwin, and FreeBSD. Exercises the mounted kernel/FUSE path rather than direct VFS and references a regression around go-fuse directory rewind support.

## Risks And Test Signals
The test detects backends that return empty listings after rewind. It is sensitive to platform syscall semantics and skipped for direct VFS mode or missing FUSE.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/dir_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/edge_cases.go -->
# sources/user-network-fs/rclone/vfs/vfstest/edge_cases.go

## Purpose
Holds regression tests for racy VFS/mount edge cases.

## APIs, Flow, And State
`TestTouchAndDelete` creates a zero-byte file and immediately removes it, verifying the tree returns empty. `TestRenameOpenHandle` writes and syncs through an open writer, renames the still-open file, closes it, waits for writers, and verifies the renamed object exists.

## Dependencies And Integration
Uses write helpers from `file.go`, `run.waitForWriters`, and shared directory comparison. Windows skips the open-handle rename case.

## Risks And Test Signals
Targets known race patterns: zero-byte create/delete and renaming before writer close. Failures indicate delayed writeback or directory-cache sequencing issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/edge_cases.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/file.go -->
# sources/user-network-fs/rclone/vfs/vfstest/file.go

## Purpose
Tests file modtime behavior and VFS symlink support across direct VFS and mounted operation.

## APIs, Flow, And State
`TestFileModTime` and `TestFileModTimeWithOpenWriters` set mtimes and verify Unix timestamps after close/writeback. `TestSymlinks` creates real files/directories, then exercises file and directory symlinks, read/write through links, rename/delete of links, mode reporting, and conflict cases where regular files, directories, and link metadata names overlap. Several complex move-conflict cases are marked skipped.

## Dependencies And Integration
Depends on the `run` harness, `vfscommon` permission defaults, `fs.LinkSuffix`, and platform symlink semantics. Link tests only run when `run.vfsOpt.Links` is enabled and skip Windows.

## Risks And Test Signals
Risks include losing mtimes when writers close, incorrect link-file translation, link-vs-regular conflict handling, and divergence between direct VFS and OS-resolved mount symlink behavior. The skipped FIXME cases document remaining unimplemented conflict coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/fs.go -->
# sources/user-network-fs/rclone/vfs/vfstest/fs.go

## Purpose
Provides the shared functional test harness for rclone VFS and mount tests.

## APIs, Flow, And State
`RunTests` iterates cache modes, writeback variants, and symlink variants, then runs the directory, file, read, write, edge-case, and symlink tests. `Run` stores the active `Oser`, VFS options, remote Fs, mount path, cleanup callback, and subprocess pipes. Helpers initialize random remotes, start direct VFS or mount subprocesses, normalize paths, compare local/remote trees, write/read files, create/remove dirs, symlink, check modes, and inspect mount/root.

## Dependencies And Integration
Depends on all rclone backends, `mountlib`, `fstest`, `walk`, VFS options, and the `submount.go` command channel. It is the central integration point for testing VFS behavior against both direct VFS APIs and real mounted filesystems.

## Risks And Test Signals
Global `run` makes tests sequentially coupled, and eventual-consistency retries can mask timing bugs while reducing flakes. The harness gives broad signal over cache mode regressions, permissions, directory listings, remote sync, and mount lifecycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/os.go -->
# sources/user-network-fs/rclone/vfs/vfstest/os.go

## Purpose
Defines the `Oser` abstraction and a real-OS implementation so the same tests can run against either mounted paths or in-process VFS.

## APIs, Flow, And State
`Oser` lists filesystem operations needed by tests. `realOs` delegates to `os` and `lib/file` helpers. `realOsFile` wraps `*os.File` to satisfy `vfs.Handle`, adding no-op `Flush`, `Release` as close, nil `Node`, and invalid lock methods.

## Dependencies And Integration
Used by `Run.startMountSubProcess` for non-direct VFS mode. The interface aligns real OS handles with VFS handles so test code can remain transport-neutral.

## Risks And Test Signals
Adapter methods must preserve close semantics across `Close`, `Flush`, and `Release`. Misalignment can make tests pass in one mode and fail in another. Compile-time interface assertions guard basic compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/os.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/read.go -->
# sources/user-network-fs/rclone/vfs/vfstest/read.go

## Purpose
Contains shared functional read tests for byte-wise reads, checksum behavior, and seeking.

## APIs, Flow, And State
`TestReadByByte` repeatedly opens a file and reads increasing prefixes one byte at a time. `TestReadChecksum` reads a large file fully enough and partially enough to exercise checksum comparison decisions on close. `TestReadSeek` verifies reads after seeks to middle, end, beyond end, and back to start.

## Dependencies And Integration
Uses the `run` harness for file creation, opening, reading, and cleanup. It validates read handle behavior across cache modes and mount/direct VFS operation.

## Risks And Test Signals
Failures point to broken sequential offsets, EOF behavior, seek handling, or checksum-trigger conditions. Tests are intentionally black-box from the mounted/VFS API surface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/read_non_unix.go -->
# sources/user-network-fs/rclone/vfs/vfstest/read_non_unix.go

## Purpose
Provides a non-Unix fallback for the read double-close test.

## APIs, Flow, And State
`TestReadFileDoubleClose` skips with the current operating system. No state is created.

## Dependencies And Integration
Selected outside Linux, Darwin, and FreeBSD where the Unix `dup`/close test is not available.

## Risks And Test Signals
The read-after-dup-close behavior is not validated on these platforms. The file ensures test package build consistency and explicit skip reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/read_non_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/read_unix.go -->
# sources/user-network-fs/rclone/vfs/vfstest/read_unix.go

## Purpose
Tests mounted read handles when file descriptors are duplicated and closed in different orders.

## APIs, Flow, And State
`TestReadFileDoubleClose` opens a file, duplicates the fd twice, closes one duplicate, reads through the original, closes it, reads through the remaining duplicate, then closes that duplicate. It verifies no input/output error after buffered read paths.

## Dependencies And Integration
Unix build-tagged for Linux, Darwin, and FreeBSD. Uses raw `syscall.Dup`, `Close`, and `Read`, and skips direct VFS mode because it needs kernel fd behavior.

## Risks And Test Signals
Detects FUSE/mount implementations that mishandle flush/release on duplicated read descriptors. It is platform-specific and depends on mounted semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/read_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/submount.go -->
# sources/user-network-fs/rclone/vfs/vfstest/submount.go

## Purpose
Implements the subprocess mount orchestration used by functional tests to avoid in-process kernel/FUSE deadlocks.

## APIs, Flow, And State
The `-run-mount` flag carries JSON-encoded `runMountOpt`. `startMountSubProcess` either creates a direct VFS-backed `Oser` or re-execs the test binary, wires stdin/stdout, and waits for a `STARTED` line. `startMount` decodes options, opens the remote from cache, mounts through `mountlib`, serves text commands on stdin, and unmounts on exit. `doMountCommand` handles `waitForWriters`, `forget`, and `exit`. Parent helpers send commands, wait for writer drain, forget directory cache entries, and unmount with retry and VFS cache cleanup.

## Dependencies And Integration
Depends on `mountlib`, `cache.Get`, `fstest`, VFS, and the `Run` harness. It bridges test process control and mounted filesystem lifecycle.

## Risks And Test Signals
Risks include subprocess startup hangs, scanner/protocol desynchronization, mount cleanup failures, and platform-specific mount path selection. Functional test success and cleanup are the main signals; failures are fatal to avoid leaving inconsistent mounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/submount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/vfs.go -->
# sources/user-network-fs/rclone/vfs/vfstest/vfs.go

## Purpose
Adapts `*vfs.VFS` to the `Oser` interface for direct in-process functional testing.

## APIs, Flow, And State
`vfsOs` embeds `*vfs.VFS` and overrides `Stat` to call `VFS.Stat`, returning `os.FileInfo`. Other methods are inherited from `VFS` methods matching `Oser`.

## Dependencies And Integration
Used when `RunTests` is invoked with `useVFS=true`, such as `vfstest_test.go`. It avoids mounting while exercising the same high-level operations.

## Risks And Test Signals
The adapter is minimal; risk is interface drift if `VFS` methods change. Compile-time assertion confirms `vfsOs` satisfies `Oser`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write.go -->
# sources/user-network-fs/rclone/vfs/vfstest/write.go

## Purpose
Contains shared functional write tests for creates, overwrites, fsync, duplicate descriptors, and append mode.

## APIs, Flow, And State
Tests cover closing a created file without writes, writing and reading back data, overwriting, syncing before close, duplicated writer file descriptors, and `O_APPEND` in cache modes that support writes. Dup and append cases are skipped where platform or cache mode cannot support them.

## Dependencies And Integration
Uses `osCreate`, `osAppend`, `writeTestDup`, `run.waitForWriters`, cache-mode options, and mounted/direct filesystem operations from the harness.

## Risks And Test Signals
These tests expose writeback timing, flush/release behavior, cache-mode restrictions, append handling, and duplicate-fd semantics. One open-file listing test is disabled as `FIXME`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write_other.go -->
# sources/user-network-fs/rclone/vfs/vfstest/write_other.go

## Purpose
Provides fallback implementations for write double-close and fd duplication on unsupported non-Unix, non-Windows platforms.

## APIs, Flow, And State
`TestWriteFileDoubleClose` skips with `runtime.GOOS`. `writeTestDup` returns a not-supported error. No persistent state is created.

## Dependencies And Integration
Selected by build tags excluding Unix-like dup support and Windows. It keeps shared write tests buildable.

## Risks And Test Signals
Duplicate-writer behavior is untested on these platforms. The explicit skip/error path avoids false expectations where no fd-dup primitive is available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write_unix.go -->
# sources/user-network-fs/rclone/vfs/vfstest/write_unix.go

## Purpose
Tests write behavior with duplicated file descriptors on Unix-like platforms and provides the Unix implementation of `writeTestDup`.

## APIs, Flow, And State
`TestWriteFileDoubleClose` opens a writer, duplicates its fd twice, closes one duplicate, writes through the original, closes it, then writes through the second duplicate. It expects an error below `CacheModeWrites` and success at write-capable cache modes. `writeTestDup` wraps `unix.Dup`.

## Dependencies And Integration
Build-tagged for Linux, Darwin, FreeBSD, and OpenBSD, though Darwin skips the test. Uses `golang.org/x/sys/unix` and VFS cache-mode options.

## Risks And Test Signals
Detects mount-layer mishandling of flush/release with duplicated writer descriptors. Expected behavior depends on cache mode, so it guards both restriction and success paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write_windows.go -->
# sources/user-network-fs/rclone/vfs/vfstest/write_windows.go

## Purpose
Provides Windows-specific fd duplication support and skips the write double-close behavioral test.

## APIs, Flow, And State
`TestWriteFileDoubleClose` reports an unsupported skip. `writeTestDup` uses `windows.DuplicateHandle` on the current process to duplicate a handle with the same access rights.

## Dependencies And Integration
Selected on Windows and used by shared write tests such as `TestWriteFileDup` when applicable.

## Risks And Test Signals
The duplicate helper can still support mmap-like tests, but the direct double-close write test is skipped. Windows handle semantics and WinFSP behavior remain the key platform risk.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest/write_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest_test.go -->
# sources/user-network-fs/rclone/vfs/vfstest_test.go

## Purpose
Runs the shared `vfstest` functional suite directly against the in-process VFS implementation.

## APIs, Flow, And State
`TestFunctional` skips non-local remotes, then calls `vfstest.RunTests` with `useVFS=true`, minimum cache mode off, cache tests enabled, and a dummy `mountFn` that returns an immediately successful unmount channel.

## Dependencies And Integration
Imports all backends, `fstest`, `mountlib`, `vfs`, `vfscommon`, and `vfstest`. This is the direct-VFS entry point for the broader functional tests.

## Risks And Test Signals
It avoids real mount behavior, so kernel/FUSE-specific bugs are not covered here. It gives broad signal for in-process VFS semantics across cache modes and writeback/link variants on local remotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vfstest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vstate_string.go -->
# sources/user-network-fs/rclone/vfs/vstate_string.go

## Purpose
Generated stringer output for the internal `vState` enum.

## APIs, Flow, And State
The file defines compile-time index checks for `vOK`, `vAddFile`, `vAddDir`, and `vDel`, stores the concatenated names and offsets, and implements `vState.String`. Unknown values format as `vState(<n>)`.

## Dependencies And Integration
Generated by `stringer -type=vState` and used by VFS logging/debugging wherever `vState` is formatted.

## Risks And Test Signals
Manual edits are discouraged; enum changes require regenerating the file. The compiler array-index checks catch changed constant values. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/vstate_string.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/write.go -->
# sources/user-network-fs/rclone/vfs/write.go

## Purpose
Implements `WriteFileHandle`, the non-cache streaming write handle for VFS files. It writes sequential data to the remote via an `io.Pipe` and `operations.Rcat`.

## APIs, Flow, And State
`newWriteFileHandle` creates the handle, adjusts symlink remotes with `fs.LinkSuffix`, initializes condition state, and registers the writer on the `File`. `safeToTruncate` decides whether opening is allowed without cached random-write support. `openPending` lazily starts a goroutine that uploads from a pipe, truncates local VFS size state, and adds the object to the directory. `WriteAt` waits briefly for in-sequence offsets, rejects seeks with `ESPIPE`, lazily opens, writes to the pipe, updates offset and file size, and broadcasts waiters. `Close`, `Flush`, and `Release` converge through `close`, which finalizes the pipe, waits for upload result, updates the VFS object, or removes failed placeholder files. Reads are rejected with `EPERM`; `Truncate` only allows truncating to the current offset.

## Dependencies And Integration
Depends on `operations.Rcat`, `File` writer tracking and size/object updates, VFS `WriteWait`, symlink suffix handling, and error constants from the VFS package. It is used when cache mode does not supply read/write cached handles.

## Risks And Test Signals
Risks are sequential-write enforcement, error propagation from async upload to close/flush, zero-byte creates on remotes that reject empty files, and race behavior for `Flush` versus `Release`. `write_test.go` covers method behavior, readonly remote errors, sequential `WriteAt`, flush/release semantics, open-writer modtime, and reading back zero/nonzero writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/write.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/write_test.go -->
# sources/user-network-fs/rclone/vfs/write_test.go

## Purpose
Tests `WriteFileHandle` behavior for streaming writes, close/flush/release, truncation rules, readonly remotes, modtime, and readback.

## APIs, Flow, And State
`writeHandleCreate` opens `file1` for write and asserts a `*WriteFileHandle`. Tests check `String`, `Node`, offset, stat, rejected read methods, no-op sync, truncate-at-offset, double close, open-existing behavior, O_TRUNC behavior, sequential `WriteAt`, closed-handle errors, unwritten `Flush`, `Release`, open-writer modtime preservation, and `ReadAt` after closing zero or nonzero files. The readonly test changes local remote directory permissions and verifies close returns upload errors and failed placeholders are removed.

## Dependencies And Integration
Uses `newTestVFS`, local `fstest` remotes, `fs.ErrorCantUploadEmptyFiles`, random data, and shared listing helpers. It is the focused unit/regression suite for `write.go`.

## Risks And Test Signals
Some tests skip Windows or non-local remotes, and empty-file behavior depends on backend support. Coverage is strong for sequential streaming semantics and close-time error propagation but does not test high concurrency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/zip.go -->
# sources/user-network-fs/rclone/vfs/zip.go

## Purpose
Creates a ZIP archive stream from a VFS directory tree.

## APIs, Flow, And State
`CreateZip(ctx, dir, w)` constructs a `zip.Writer`, recursively walks `Dir.ReadDirAll`, opens each `File`, creates deflated file headers with VFS modtimes, copies contents, and creates stored directory headers before recursing into child directories. Errors are wrapped with operation context, and `fs.CheckClose` preserves close errors.

## Dependencies And Integration
Depends on `archive/zip`, VFS `Dir`/`File` APIs, file handles from `File.Open`, and `io.Copy`. The passed context is currently only part of the signature and not directly used in this implementation.

## Risks And Test Signals
Directory names use `root + e.Path()`, so nested path construction is the main correctness risk. Large files stream through handles and can surface read/cache issues. `zip_test.go` validates many flat files, nested directories, large-file checksum integrity, and root-directory subdirectories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/zip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/zip_test.go -->
# sources/user-network-fs/rclone/vfs/zip_test.go

## Purpose
Tests ZIP creation from VFS directories for flat files, nested directories, large content, and root children.

## APIs, Flow, And State
Helpers create ZIP buffers, read them with `archive/zip`, and locate file entries by predicate. Tests write objects to a test remote, stat directories through VFS, call `CreateZip`, count file entries, and verify contents or SHA-256 checksum.

## Dependencies And Integration
Uses `newTestVFS`, `fstest`, random data, and VFS directory nodes. A chunker backend skip avoids an overly slow large-file case.

## Risks And Test Signals
The tests are content-oriented and deliberately tolerant of directory-entry naming by matching suffixes. They give signal for recursive traversal and streaming integrity but do not check every ZIP metadata field.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/zip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/Makefile.am -->
# sources/user-network-fs/rpcbind/Makefile.am

## Purpose
Defines the Automake build for rpcbind and rpcinfo.

## APIs, Flow, And State
Sets `AUTOMAKE_OPTIONS`, common preprocessor flags, optional debug/warmstart/libwrap/rmtcalls flags, and program targets. `rpcbind_SOURCES` lists the daemon sources, `rpcbind_LDADD` links libtirpc and optional systemd libraries, and `rpcinfo` is built from `src/rpcinfo.c`. Man pages and optional systemd unit installation are declared.

## Dependencies And Integration
Consumes conditionals and substitutions from `configure.ac`: `DEBUG`, `LIBSETDEBUG`, `WARMSTART`, `LIBWRAP`, `RMTCALLS`, `SYSTEMD`, `TIRPC_*`, `statedir`, `rpcuser`, and `nss_modules`.

## Risks And Test Signals
Build failures can result from conditional drift with `configure.ac` or missing source lists. Test signal is autoreconf/configure/make success across option combinations and installation of expected units/manpages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/autogen.sh -->
# sources/user-network-fs/rpcbind/autogen.sh

## Purpose
Cleans generated autotools files and regenerates the build system.

## APIs, Flow, And State
The shell script removes common generated helper files, `aclocal.m4`, `configure`, `config.h.in`, `autom4te.cache`, `Makefile.in`, and `Makefile`. With argument `clean`, it exits after cleanup. Otherwise it runs `aclocal`, `automake --add-missing --copy --gnu`, and `autoconf`.

## Dependencies And Integration
Requires POSIX shell utilities plus autotools. It is used by developers/packagers before running configure from a source checkout.

## Risks And Test Signals
It destructively removes generated build files in the tree. There is no quoting issue for the fixed filenames, and `find -print0 | xargs -r0` handles paths safely. Test signal is successful regeneration and subsequent configure/make.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/configure.ac -->
# sources/user-network-fs/rpcbind/configure.ac

## Purpose
Defines rpcbind's Autoconf configuration, feature toggles, dependency checks, and output files.

## APIs, Flow, And State
Initializes package `rpcbind` version 1.2.9, checks C compiler, defines enable options for libwrap, debug, warmstarts, and remote calls, defines with-options for state directory, rpc user, NSS module list, and systemd unit dir, checks libtirpc via pkg-config, tests abstract socket support in libtirpc, checks optional libsystemd or libsystemd-daemon, checks libwrap when requested, searches pthread support, checks `nss.h`, computes `_sbindir`, and outputs `Makefile` plus systemd unit files.

## Dependencies And Integration
Feeds Automake conditionals and substitutions consumed by `Makefile.am` and systemd templates. Depends on pkg-config, libtirpc, optional systemd/libwrap, and Autoconf macros.

## Risks And Test Signals
Risks include CPPFLAGS clobbering during the abstract-socket probe, optional dependency detection drift, and systemd default lookup when pkg-config lacks systemd. Test signal is configure success for default and enabled feature matrices.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/check_bound.c -->
# sources/user-network-fs/rpcbind/src/check_bound.c

## Purpose
Tracks transports used by rpcbind and provides address-bound checks, merged universal-address generation, and netconfig lookup by netid.

## APIs, Flow, And State
Static `fdlist` nodes form a linked list of netconfigs. `add_bndlist` clones a netconfig entry and appends it. `check_bound` converts a universal address to a transport address, opens a socket for that netconfig, and attempts bind; success means the service is not currently bound, while bind failure means it is bound. In this version `check_binding` is set false, so checks currently return true. `is_bound` finds the matching netid and delegates. `mergeaddr` validates binding, derives the caller universal address from either supplied `saddr` or `SVCXPRT`, and calls `addrmerge`. `rpcbind_get_conf` returns the stored netconfig.

## Dependencies And Integration
Uses libtirpc netconfig/address conversion and rpcbind helpers such as `addrmerge`. Service lookup paths in pmap/rpcb call `is_bound`, `mergeaddr`, and `rpcbind_get_conf`.

## Risks And Test Signals
Disabled bound checking means stale registrations may persist unless other paths delete them. When enabled, bind-as-probe semantics are subtle and treat conversion/socket errors as bound. Test signal would include service death cleanup, merged address correctness, and netid lookup behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/check_bound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/pmap_svc.c -->
# sources/user-network-fs/rpcbind/src/pmap_svc.c

## Purpose
Implements the legacy version 2 portmapper service interface when `PORTMAP` is enabled.

## APIs, Flow, And State
`pmap_service` dispatches PMAP NULL, SET, UNSET, GETPORT, DUMP, and CALLIT. `find_service_pmap` finds exact or same-program mappings from `list_pml`. `pmapproc_change` decodes `struct pmap`, derives owner from local uid or superuser checks, authorizes, maps protocol to netid, constructs IPv4/IPv6 wildcard universal addresses for SET, calls `map_set`, or unsets TCP and UDP mappings. `pmapproc_getport` authorizes, finds a mapping, validates it with `is_bound`, deletes dead programs, sends the port, and updates stats. `pmapproc_dump` returns `list_pml`. Protocol conversion helpers map TCP/UDP netids and IP protocol numbers.

## Dependencies And Integration
Depends on libtirpc pmap/rpcb XDR, global rpcbind lists, `check_access`, `map_set`, `map_unset`, `delete_prog`, `rpcbs_*` stats, and remote-call common code.

## Risks And Test Signals
Compatibility with legacy PMAP clients is the central risk. Address construction is limited to TCP/UDP wildcard addresses, and stale binding checks depend on `check_bound.c`. Tests should exercise authorization, set/unset/getport/dump, protocol conversion, dead-service deletion, and stats updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/pmap_svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_stat.c -->
# sources/user-network-fs/rpcbind/src/rpcb_stat.c

## Purpose
Maintains in-memory rpcbind statistics returned by the version 4 GETSTAT procedure.

## APIs, Flow, And State
Static `rpcb_stat_byvers inf` stores procedure counts, set/unset counts, address lookup counts, and remote-call counts by rpcbind version index. `rpcbs_procinfo` increments per-procedure counters after validating version/procedure bounds. `rpcbs_set` and `rpcbs_unset` count successful mapping changes. `rpcbs_getaddr` finds or creates an address-list record keyed by program/version/netid and increments success or failure based on returned universal address. `rpcbs_rmtcall` similarly records remote-call success/failure and indirect counts. `rpcbproc_getstat` returns `&inf`.

## Dependencies And Integration
Called by pmap/rpcb service dispatch and common remote-call/address lookup code. Uses `rpcbind_get_conf` for stable netid pointers.

## Risks And Test Signals
State is process-local and not synchronized, so multithreaded dispatch would need external serialization. Allocation failures silently drop new rows. The guard conditions for version indices are important because service code passes version-stat constants. Test signal should verify counters for success/failure paths and GETSTAT output shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_svc.c -->
# sources/user-network-fs/rpcbind/src/rpcb_svc.c

## Purpose
Implements rpcbind version 3 service dispatch and version-3 local wrappers.

## APIs, Flow, And State
`rpcb_service_3` records procedure stats, chooses XDR argument/result routines and a common/local handler for each procedure, decodes arguments, extracts the program number for access checks on SET/UNSET/GETADDR, calls `check_access`, invokes the selected handler, sends replies, and frees arguments. It supports NULL, SET, UNSET, GETADDR, DUMP, CALLIT, GETTIME, UADDR2TADDR, and TADDR2UADDR. `rpcbproc_getaddr_3_local` logs caller address in debug and delegates to `rpcbproc_getaddr_com` with `RPCB_ALLVERS`. `rpcbproc_dump_3_local` returns `list_rbl`.

## Dependencies And Integration
Uses libtirpc XDR and SVC APIs, rpcbind common handlers (`rpcbproc_set_com`, `rpcbproc_unset_com`, conversion/time/getaddr helpers), stats, access checks, and global registration list state.

## Risks And Test Signals
The dispatcher relies on the union field matching selected XDR routines and on freeing decoded arguments exactly once. Authorization and version constants must align with stats and common handlers. Tests should cover each procedure, decode failures, weak-auth failures, dump output, and GETADDR version fallback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_svc_4.c -->
# sources/user-network-fs/rpcbind/src/rpcb_svc_4.c

## Purpose
Implements rpcbind version 4 service dispatch and version-4-only address lookup procedures.

## APIs, Flow, And State
`rpcb_service_4` dispatches NULL, SET, UNSET, GETADDR, GETVERSADDR, DUMP, INDIRECT, BCAST, GETTIME, UADDR2TADDR, TADDR2UADDR, GETADDRLIST, and GETSTAT. Like version 3 it selects XDR handlers, decodes, authorizes, invokes local/common handlers, sends replies, and frees args. `rpcbproc_getaddr_4_local` allows any version via `RPCB_ALLVERS`; `rpcbproc_getversaddr_4_local` requires one version via `RPCB_ONEVERS`. `rpcbproc_getaddrlist_4_local` builds a static response list of merged addresses for all registered mappings with the same program/version and protocol family as the request transport, deleting dead registrations and updating stats. `free_rpcb_entry_list` frees allocated merged-address entries, and dump returns `list_rbl`.

## Dependencies And Integration
Uses rpcbind common service functions, `mergeaddr`, `rpcbind_get_conf`, registration list globals, GETSTAT from `rpcb_stat.c`, and libtirpc XDR/SVC types.

## Risks And Test Signals
`GETADDRLIST` uses static response storage and must free prior allocations before rebuilding. It stores pointers to netconfig fields and allocated merged addresses, making ownership discipline important. Tests should cover address-list filtering by protocol family, dead-service deletion, stat updates, GETVERSADDR strictness, and all dispatch authorization/error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/rpcb_svc_4.c -->
