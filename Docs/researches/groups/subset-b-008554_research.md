<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/dsl.go -->
# sources/storage-engines/pebble/vfs/errorfs/dsl.go

## Purpose
Provides the public predicate helpers and parser for `errorfs`'s Lisp-like error-injection DSL. It lets tests express when to inject an error or latency by operation class, path glob, operation offset, call stack, logical invocation index, boolean composition, or deterministic randomness.

## Important APIs, Types, and Functions
`Predicate` aliases `dsl.Predicate[Op]`. `And`, `Not`, `PathMatch`, `CallStackIncludes`, `OpKindIn`, `Randomly`, and `ParseDSL` are the main construction/parsing entry points. `NewParser` wires constants like `Reads`, `Writes`, `OpFileWrite`, functions like `PathMatch`, `OpFileReadAt`, `Randomly`, and the default `ErrInjected` labelled error. `Parser.AddError` allows tests to register additional `LabelledError` values. `LabelledError` implements both `error` and `Injector`, returning a stack-wrapped error if its optional predicate matches.

## Control Flow
Programmatic helpers construct predicate objects whose `Evaluate` methods inspect an `Op`. `ParseDSL` delegates to the package-level parser. During parser construction, predicate grammar and injector grammar are registered separately; a labelled error is both a constant injector and a function that parses a trailing predicate. `parseRandomly` validates probability and optional seed, while `parseFileReadAtOp` parses an exact read offset.

## State and Persistence Behavior
The DSL has no filesystem persistence. Stateful behavior is limited to deterministic pseudo-random predicates: `Randomly` embeds a `keyedPrng` so each path has its own PRNG sequence derived from a root seed. Parser instances keep grammar tables and may be extended with labelled errors.

## Dependencies and Integration Points
Depends on `internal/dsl` for generic scanners, parsers, predicates, boolean composition, call-stack predicates, and `OnIndex`. It integrates with `errorfs.Op`/`OpKind` from `errorfs.go` and `RandomLatency` parsing from `latency.go`. Tests in WAL failover and VFS failure paths feed DSL strings through `errorfs.ParseDSL`.

## Risks and Edge Cases
Invalid path globs panic during evaluation, so test DSL mistakes fail hard. `Randomly` rejects probabilities greater than 1 but negative values are syntactically impossible under the current scanner behavior. Call-stack matching is intentionally fragile under renames. `LabelledError.MaybeError` stack-wraps itself, so consumers should use `errors.Is` rather than string matching.

## Test Signals
`errorfs_test.go` drives the DSL parser through datadriven `parse-dsl` cases. Failover manager/writer tests also parse injected-error DSL strings, giving integration coverage for path, operation, and error predicates.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/dsl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs.go -->
# sources/storage-engines/pebble/vfs/errorfs/errorfs.go

## Purpose
Implements a `vfs.FS` and `vfs.File` wrapper that injects artificial errors before filesystem operations. It is a test utility for forcing Pebble code through rare IO error paths without modifying production VFS implementations.

## Important APIs, Types, and Functions
`ErrInjected` is the default labelled error. `Op`, `OpKind`, `OpKinds`, `ReadOps`, and `WriteOps` classify VFS and file operations. `OnIndex`, `Injector`, `InjectorFunc`, `Any`, `Counter`, and `Toggle` compose injection behavior. `Wrap` wraps an FS, and `WrapFile` wraps a single file. `FS` implements `vfs.FS`; `errorFile` implements `vfs.File`.

## Control Flow
Every wrapped FS method constructs an `Op` and calls `inj.MaybeError` before delegating to the underlying FS. Methods that return opened files wrap those files with `errorFile` so subsequent reads, writes, stats, syncs, and preallocations are also injectable. `Any` scans injectors in order and returns the first error. `Counter` records injected count and last error under a mutex, and `Toggle` gates an injector through an atomic boolean.

## State and Persistence Behavior
The wrapper does not persist state or alter the underlying filesystem when injection fires; it returns the injected error before the delegated operation runs. `Counter` stores counters in memory, and `Toggle` stores the enabled flag atomically. File close intentionally does not inject errors because close failures are not expected in Pebble's modeled error paths.

## Dependencies and Integration Points
Integrates with `vfs.FS`/`vfs.File`, the DSL predicates in `dsl.go`, and the generic `internal/dsl.OnIndex` implementation. WAL failover tests and other Pebble tests wrap `vfs.NewMem` or disk-backed VFSs to exercise IO failure handling.

## Risks and Edge Cases
`OpFileClose` is classified as a write op but `errorFile.Close` bypasses injection, so close-error testing must use other wrappers. `Prefetch` also does not inject errors. For two-path operations like link and rename, the source path is used for predicate matching, which can surprise tests that want to target the destination path. The `init` invariant panics if new op kinds are added without updating read/write classification.

## Test Signals
`errorfs_test.go` covers DSL parsing. Broader integration is visible in `failover_manager_test.go` and `failover_writer_test.go`, where injected create/write/sync/open-dir errors drive failover and close paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs_test.go -->
# sources/storage-engines/pebble/vfs/errorfs/errorfs_test.go

## Purpose
Provides datadriven coverage for the `errorfs` DSL parser and string rendering. It verifies that DSL snippets used by other tests parse into the expected injector descriptions or produce stable parse errors.

## Important APIs, Types, and Functions
`TestErrorFS` is the only test entry point. It uses `datadriven.RunTest`, `crstrings.LinesSeq`, `ParseDSL`, and `Injector.String` to process `testdata/errorfs` commands.

## Control Flow
For each datadriven `parse-dsl` command, the test iterates over input lines, parses each line independently, and writes either `parsing err: ...` or the parsed injector's string representation. Unknown commands return a diagnostic string.

## State and Persistence Behavior
The test maintains only a reusable `strings.Builder`; no filesystem state is mutated except reading datadriven fixtures.

## Dependencies and Integration Points
Depends on the parser in `dsl.go`, injector string methods in `errorfs.go` and `latency.go`, and the `datadriven` fixture framework. The output format becomes a regression signal for DSL compatibility.

## Risks and Edge Cases
This file validates parser shape but not actual operation injection against a real wrapped FS. It also does not directly exercise `Counter`, `Toggle`, `Any`, or file-method injection; those are covered indirectly elsewhere.

## Test Signals
The test itself is the signal: expected fixture output catches parser regressions, missing grammar registrations, malformed string rendering, and parse-error changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/errorfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/latency.go -->
# sources/storage-engines/pebble/vfs/errorfs/latency.go

## Purpose
Adds latency injection to `errorfs` without returning errors. It is used to deterministically simulate slow IO operations, especially in WAL failover monitoring tests.

## Important APIs, Types, and Functions
`RandomLatency` constructs an `Injector` that sleeps for an exponentially distributed duration when an optional predicate matches. `parseRandomLatency` registers the DSL form. `randomLatency.MaybeError` performs the sleep and always returns nil. `keyedPrng` provides path-keyed deterministic PRNG state shared with random predicates.

## Control Flow
`RandomLatency` initializes a `randomLatency` with predicate, mean, optional total limit, and seeded `keyedPrng`. `MaybeError` checks the predicate, derives a per-path random duration capped at 20 times the mean, optionally caps aggregate injected latency with an atomic counter, sleeps, and returns nil. `parseRandomLatency` consumes a duration string, seed, optional predicate, and closing parenthesis.

## State and Persistence Behavior
State is entirely in memory. `randomLatency.agg` tracks total injected sleep time if a limit is configured. `keyedPrng` lazily creates and caches a `rand.Rand` per key under a mutex; this makes results deterministic per file path across interleavings that touch different paths.

## Dependencies and Integration Points
Depends on `internal/dsl`, `math/rand/v2`, `hash/maphash`, and `time`. Registered from `NewParser` in `dsl.go` as `RandomLatency`. WAL failover tests wrap VFSs with random latency injectors to make monitor/prober switching paths observable.

## Risks and Edge Cases
The path-keyed PRNG serializes access under a mutex, which is fine for tests but not intended as a hot production path. Latency is capped to avoid extreme test timeouts, changing the tail of the exponential distribution. Aggregate limit accounting can overshoot then cap the final sleep, but once already over limit it injects nothing.

## Test Signals
`errorfs_test.go` covers parsing and string rendering. `failover_manager_test.go` uses `RandomLatency` with `Randomly` to drive quiesce and all-files-deletable tests under delayed operations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errorfs/latency.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix.go -->
# sources/storage-engines/pebble/vfs/errors_unix.go

## Purpose
Defines Unix-specific filesystem error helpers for Pebble's VFS layer.

## Important APIs, Types, and Functions
`errNotEmpty` aliases `unix.ENOTEMPTY` for directory removal semantics. `IsNoSpaceError` returns true when an error wraps `unix.ENOSPC`.

## Control Flow
`IsNoSpaceError` delegates to `cockroachdb/errors.Is`, allowing wrapped errors from VFS calls to match the Unix errno.

## State and Persistence Behavior
No state or persistence. It only supplies platform constants and classification logic.

## Dependencies and Integration Points
Used by VFS and MemFS removal/error handling. Depends on `golang.org/x/sys/unix` and CockroachDB errors wrapping. Built only on Darwin, DragonFly, FreeBSD, Linux, OpenBSD, and NetBSD.

## Risks and Edge Cases
It only recognizes `ENOSPC`; other quota or inode exhaustion errors are not classified as no-space here. The build tag excludes Solaris despite Unix lock code including Solaris in a separate file.

## Test Signals
`errors_unix_test.go` verifies that a stack-wrapped `unix.ENOSPC` is recognized.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix_test.go -->
# sources/storage-engines/pebble/vfs/errors_unix_test.go

## Purpose
Tests Unix no-space error classification.

## Important APIs, Types, and Functions
`TestIsNoSpaceError` wraps `unix.ENOSPC` with CockroachDB stack context and asserts `IsNoSpaceError` returns true.

## Control Flow
The test constructs one wrapped errno and checks it through `require.True`.

## State and Persistence Behavior
No filesystem state is created; the test is purely error-classification logic.

## Dependencies and Integration Points
Covers `errors_unix.go` and relies on `errors.WithStack` preserving `errors.Is` matching. Built on the same Unix-like platforms as the implementation.

## Risks and Edge Cases
The test only covers the positive `ENOSPC` case, not false positives or related errors like quota exhaustion.

## Test Signals
Passing confirms wrapped errno matching remains compatible with the VFS helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_windows.go -->
# sources/storage-engines/pebble/vfs/errors_windows.go

## Purpose
Defines Windows-specific filesystem error helpers for Pebble's VFS layer.

## Important APIs, Types, and Functions
`errNotEmpty` aliases `windows.ERROR_DIR_NOT_EMPTY`. `IsNoSpaceError` recognizes `windows.ERROR_DISK_FULL` and `windows.ERROR_HANDLE_DISK_FULL` through CockroachDB error wrapping.

## Control Flow
`IsNoSpaceError` performs two `errors.Is` checks and returns true if either Windows error code is in the error chain.

## State and Persistence Behavior
No state or persistence. It only supplies platform-specific constants and classification.

## Dependencies and Integration Points
Used by VFS callers that need portable disk-full detection and by MemFS removal behavior through `errNotEmpty`. Built only on Windows.

## Risks and Edge Cases
The helper intentionally recognizes disk-full conditions, not every storage-related Windows error. There is no local Windows-specific test in this shard.

## Test Signals
No direct test file is listed for Windows. Unix coverage in `errors_unix_test.go` provides analogous expectations for wrapped-error matching.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_generic.go -->
# sources/storage-engines/pebble/vfs/fadvise_generic.go

## Purpose
Provides no-op advisory read hint functions on non-Linux platforms.

## Important APIs, Types, and Functions
`fadviseRandom` and `fadviseSequential` accept a file descriptor and return nil.

## Control Flow
Both functions immediately return nil. `vfs.RandomReadsOption` and `vfs.SequentialReadsOption` can call them without platform checks.

## State and Persistence Behavior
No state or persistence; no OS calls are made.

## Dependencies and Integration Points
Used by `vfs.go` open options on platforms where `unix.Fadvise` is unavailable or not used. Built under `!linux`.

## Risks and Edge Cases
Read-hint options silently do nothing, so performance behavior differs from Linux. Callers must treat these hints as best-effort.

## Test Signals
No direct tests. `vfs_test.go` and broader VFS tests exercise open options structurally, while Linux-specific behavior is implemented in `fadvise_linux.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_generic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_linux.go -->
# sources/storage-engines/pebble/vfs/fadvise_linux.go

## Purpose
Implements Linux advisory read hints used by VFS open options.

## Important APIs, Types, and Functions
`fadviseRandom` calls `unix.Fadvise` with `FADV_RANDOM`; `fadviseSequential` calls it with `FADV_SEQUENTIAL`.

## Control Flow
When `RandomReadsOption` or `SequentialReadsOption` is applied to a file with a valid descriptor, the corresponding helper sends a whole-file advisory hint to the kernel. The caller ignores the returned error.

## State and Persistence Behavior
No Pebble state or durable data is changed. The kernel may adjust readahead behavior for the descriptor.

## Dependencies and Integration Points
Depends on `golang.org/x/sys/unix` and is called from `vfs.go` open options. It is Linux-only.

## Risks and Edge Cases
Errors are intentionally ignored by open-option callers, so unsupported filesystems/descriptors silently proceed without the hint. The hint uses offset and length zero to mean the whole file.

## Test Signals
No direct test in this shard. `fd_test.go` verifies wrappers preserve file descriptors so open options can reach descriptor-backed implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fadvise_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fd_test.go -->
# sources/storage-engines/pebble/vfs/fd_test.go

## Purpose
Verifies VFS file wrappers preserve access to underlying OS file descriptors through `Fd`.

## Important APIs, Types, and Functions
`TestFileWrappersHaveFd` creates a real temporary file, wraps `vfs.Default` with disk health checks, opens a file, then wraps it with `NewSyncingFile` and asserts `Fd()` is nonzero and not `InvalidFd`.

## Control Flow
The test uses the default filesystem because `MemFS` returns `InvalidFd`. It checks the health-checking wrapper first, then the syncing wrapper stacked on top.

## State and Persistence Behavior
Creates and removes one temporary file. No durable Pebble data is involved.

## Dependencies and Integration Points
Covers wrapper compatibility with features that need descriptors, including fadvise and syncing-file range sync/preallocation. It relies on `WithDiskHealthChecks`, `Default.Open`, and `NewSyncingFile`.

## Risks and Edge Cases
Only checks descriptor availability, not descriptor correctness or behavior after close. It is sensitive to wrappers forgetting to forward `Fd`.

## Test Signals
Passing indicates descriptor-backed files remain usable through wrapper stacks.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/fd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_generic.go -->
# sources/storage-engines/pebble/vfs/file_lock_generic.go

## Purpose
Provides the fallback `Lock` implementation for platforms without explicit Unix or Windows file locking support.

## Important APIs, Types, and Functions
The fallback `Lock` method returns an error saying file locking is not implemented on the current `GOOS/GOARCH`.

## Control Flow
A call to `Lock` immediately returns nil closer and a formatted error with safe runtime values.

## State and Persistence Behavior
No file is created or modified because locking is unsupported in this fallback.

## Dependencies and Integration Points
Completes the `defaultFS` implementation of `vfs.FS` for unsupported platforms. Built when none of the Unix or Windows lock build tags apply.

## Risks and Edge Cases
The code spells the receiver as `defFS`, while the main type is `defaultFS`; if this build tag is selected, that mismatch would fail compilation unless another type alias exists outside this shard. Supported Pebble platforms likely use the Unix or Windows implementations.

## Test Signals
`file_lock_test.go` exercises lock behavior on supported platforms. There is no fallback-platform test here.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_generic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_test.go -->
# sources/storage-engines/pebble/vfs/file_lock_test.go

## Purpose
Tests exclusive lock behavior for `vfs.Default.Lock` across processes and within one process.

## Important APIs, Types, and Functions
`TestLock` uses a `-lockfile` flag to run as parent or child process. `spawn` reinvokes the test binary. `TestLockSameProcess` checks that re-locking the same file in one process fails.

## Control Flow
The parent creates an empty temp file, locks it, spawns a child that should fail to lock it, closes the lock, then spawns another child that should succeed. The child path simply tries to lock the provided file and exits through test success/failure. The same-process test locks once, attempts a second lock, expects an error, and releases the first lock.

## State and Persistence Behavior
Temporary lock files are created, truncated by platform lock implementations, and removed by the parent. The tests enforce that non-empty files are not accidentally used as lock files.

## Dependencies and Integration Points
Covers `file_lock_unix.go` and `file_lock_windows.go` through the public `vfs.Default` FS interface. It validates behavior relied on by Pebble DB directory locking.

## Risks and Edge Cases
The test depends on subprocess execution and platform-specific lock semantics. On Windows, files must be closed before locking; the test explicitly closes the temp file before calling `Lock`.

## Test Signals
Passing confirms interprocess exclusion, lock release on `Close`, and same-process duplicate lock rejection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_unix.go -->
# sources/storage-engines/pebble/vfs/file_lock_unix.go

## Purpose
Implements `vfs.Default.Lock` on Unix-like platforms using advisory `fcntl` write locks plus process-local duplicate-lock tracking.

## Important APIs, Types, and Functions
`lockedFiles` is a global map protected by a mutex. `lockCloser` wraps the lock file and releases the map entry on close. `defaultFS.Lock` creates/truncates the file, attempts `unix.FcntlFlock` with `F_SETLK`, and returns a closer.

## Control Flow
`Lock` first rejects paths already locked by this process. It creates the lock file, constructs a whole-file write lock, and attempts a non-blocking `F_SETLK`. On OS lock failure it closes the file and returns the errno. On success it records the name in `lockedFiles` and returns a `lockCloser`. `Close` checks the map, deletes the entry, and closes the file, releasing the advisory lock.

## State and Persistence Behavior
The lock file is created/truncated and remains on disk. Lock state is partly OS-managed and partly tracked in the process-local map to avoid fcntl's same-process semantics accidentally replacing/releasing locks.

## Dependencies and Integration Points
Used by `vfs.Default.Lock` and tested by `file_lock_test.go`. Pebble uses this to coordinate DB ownership across processes.

## Risks and Edge Cases
Unix advisory locks can be released by closing another descriptor for the same file, which the interface comment warns about. Path keys are raw strings, so aliases/symlinks may bypass the same-process map. `Close` panics if called on a lock not marked held.

## Test Signals
`file_lock_test.go` verifies subprocess exclusion, release, and duplicate same-process detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_windows.go -->
# sources/storage-engines/pebble/vfs/file_lock_windows.go

## Purpose
Implements `vfs.Default.Lock` on Windows using exclusive `CreateFile` access.

## Important APIs, Types, and Functions
`lockCloser` wraps a Windows handle and closes it with `windows.Close`. `defaultFS.Lock` creates/truncates the file with read/write access and share mode zero.

## Control Flow
The path is converted to UTF-16. `windows.CreateFile` is called with `GENERIC_READ|GENERIC_WRITE`, no sharing, and `CREATE_ALWAYS`. A successful handle represents the lock until closed.

## State and Persistence Behavior
The lock file is created or truncated. The OS handle enforces exclusivity, including against the same process if the file is already open.

## Dependencies and Integration Points
Used by `vfs.Default.Lock` under Windows and covered by the cross-platform locking tests. It supports Pebble DB directory locking on Windows.

## Risks and Edge Cases
Because `CREATE_ALWAYS` truncates, callers must only use empty lock files. The test file explicitly rejects non-empty targets. Windows locking fails if the current process already has the file open, so callers must close temp handles before locking.

## Test Signals
`file_lock_test.go` validates the public lock contract on Windows as part of the same tests used for Unix.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/file_lock_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/logging_fs.go -->
# sources/storage-engines/pebble/vfs/logging_fs.go

## Purpose
Provides a lightweight VFS wrapper that logs filesystem and file operations. It is useful for tests and diagnostics that need to observe VFS behavior without changing the underlying filesystem.

## Important APIs, Types, and Functions
`WithLogging` wraps an `FS` with a `LogFn`. `loggingFS` implements selected `FS` methods with log lines. `loggingFile` wraps opened files and logs close, sync, sync-to, read-at, write-at, and prefetch operations.

## Control Flow
Each logging FS method emits a formatted message before delegating. Methods that return files wrap them in `loggingFile`. Open logs include option type names when options are present. `Unwrap` exposes the underlying FS for `vfs.Root`.

## State and Persistence Behavior
The wrapper stores only the log callback and file name. It does not alter persistence semantics; all durable behavior is delegated to the wrapped FS and file.

## Dependencies and Integration Points
Integrates with the `vfs.FS`/`vfs.File` interfaces and root-unwrapping behavior. It complements datadriven VFS tests and other wrappers such as error injection and syncing.

## Risks and Edge Cases
It logs before the operation, so logs may show attempted operations that later fail. It does not log every file method, such as sequential `Read`, `Write`, `Stat`, `Preallocate`, `Flush`, or `Fd`, so it is not a complete audit trail.

## Test Signals
No direct test file in this shard, but similar logging behavior is embedded in `vfs_test.go`'s `vfsTestFS` harness.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/logging_fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs.go -->
# sources/storage-engines/pebble/vfs/mem_fs.go

## Purpose
Implements Pebble's in-memory `vfs.FS` and `vfs.File` for tests, including hard links, directory operations, file locks, optional Windows-like removal semantics, and crash-clone simulation for durability testing.

## Important APIs, Types, and Functions
`NewMem`, `NewCrashableMem`, and `NewMemFile` construct memory-backed filesystems/files. `MemFS` implements `FS` methods including `Create`, `Link`, `Open`, `OpenReadWrite`, `OpenDir`, `Remove`, `RemoveAll`, `Rename`, `ReuseForWrite`, `MkdirAll`, `Lock`, `List`, `Stat`, path helpers, disk usage stubbing, `CrashClone`, and `UnsafeGetFileDataBuffer`. `CrashCloneCfg`, `memNode`, `memFile`, `memFileInfo`, and `memFileLock` hold the backing tree, file handles, metadata, and lock state.

## Control Flow
All path operations route through `walk`, which strips leading slashes and traverses `memNode.children` under `MemFS.mu`. Mutations on crashable filesystems take `cloneMu.RLock`, while `CrashClone` takes `cloneMu.Lock` to block concurrent writes. Create replaces the final child with a new node. Link points a new directory entry at an existing node. Rename removes the old entry and inserts it at the new path. ReuseForWrite renames then opens the file write-only. File reads/writes lock the node's data mutex, update positions, grow buffers as needed, and optionally mutate input buffers when invariants are enabled.

## State and Persistence Behavior
Filesystem state is an in-memory tree. Directories store `children` and, when synced in crashable mode, `syncedChildren`. Files store `data`, `syncedData`, and `modTime`. `memFile.Sync` copies current file data or directory children into synced state; `CrashClone` returns a possible post-crash tree with all synced state plus optional random unsynced directory entries and 4 KiB data blocks. Open files increment node refs and close decrements them; Windows semantics reject removal of referenced nodes. `SyncTo` intentionally returns `(false, nil)` without durability to expose incorrect reliance on range sync.

## Dependencies and Integration Points
Implements the core `vfs.FS` contract used throughout Pebble tests. `Clone` and VFS datadriven tests use MemFS as a portable filesystem. WAL failover tests use `NewCrashableMem` to inspect durable log records after simulated crashes. `errNotEmpty` comes from platform error files.

## Risks and Edge Cases
`Rename` deletes the source before walking the destination; if destination parent traversal fails, the source has already been removed. This mirrors existing test utility assumptions but is not fully atomic. `Link` does not increment a link count; nodes persist as long as referenced by directory entries or open handles. `UnsafeGetFileDataBuffer` can race or corrupt state if misused. `f.readat` in the test harness appears to parse offset from the first argument rather than a second one, but that is test code, not MemFS itself.

## Test Signals
`mem_fs_test.go` covers datadriven basics, listing, crash-clone semantics, standalone mem files, crash clone concurrency against `ReuseForWrite`/`Link`/`Lock`, and lock behavior. `vfs_test.go` compares MemFS behavior with disk VFS for common operations and link/create semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs_test.go -->
# sources/storage-engines/pebble/vfs/mem_fs_test.go

## Purpose
Tests MemFS behavior through datadriven scenarios, crash-clone equivalence, standalone memory files, concurrency around crash cloning, and MemFS lock semantics.

## Important APIs, Types, and Functions
`runMemFSDataDriven` interprets commands for file and filesystem operations. `checkClonedIsEquivalent` checks `Clone` round trips. `TestMemFSBasics`, `TestMemFSList`, `TestMemFSCrashable`, `TestMemFile`, `TestMemFSCrashCloneConcurrency`, and `TestMemFSLock` are the main test entry points.

## Control Flow
Datadriven commands create/open/link/rename/reuse/remove files, write/read/sync/close handles, list directories, crash-clone filesystems, and switch active FS handles. After each datadriven run, the test clones the filesystem through `Clone` using both empty and slash root paths and compares string dumps. The concurrency test runs crash cloning alongside reuse, link, and lock workers for a fixed duration. The lock datadriven test manages multiple named MemFS instances and lock handles.

## State and Persistence Behavior
Tests exercise synced versus unsynced state in `NewCrashableMem`, including random retention of unsynced data. The concurrency test stresses `cloneMu` ordering to catch deadlocks from recursive read locks when a crash clone is waiting. Lock tests validate per-MemFS lock maps and close-based release.

## Dependencies and Integration Points
Covers `mem_fs.go`, `Clone`, the VFS `File` interface, datadriven fixtures, and test randomness from `math/rand/v2`. These tests protect behavior used by broader Pebble DB and WAL tests.

## Risks and Edge Cases
The fixed five-second concurrency test is heavier than typical unit tests and may be sensitive to slow CI, but it targets a real deadlock class. The datadriven `f.readat` command appears to reuse the first command argument for both byte count and offset, limiting offset coverage.

## Test Signals
Passing demonstrates MemFS compatibility with the VFS contract, crashable sync modeling, root clone behavior, lock isolation, and absence of the known crash-clone deadlock.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/mem_fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file.go -->
# sources/storage-engines/pebble/vfs/syncing_file.go

## Purpose
Wraps writable files so large sequential writes periodically issue range syncs and optionally preallocate storage, reducing latency spikes from dirty page writeback while preserving full durability on close unless configured otherwise.

## Important APIs, Types, and Functions
`SyncingFileOptions` configures `NoSyncOnClose`, `BytesPerSync`, and `PreallocateSize`. `NewSyncingFile` wraps a `File`. `syncingFile.Write`, `preallocate`, `maybeSync`, `Sync`, and `Close` implement the behavior. `NewSyncingFS` wraps an FS so new files are syncing files.

## Control Flow
`Write` preallocates based on current offset, delegates to the underlying file, advances an atomic offset, then calls `maybeSync`. `maybeSync` ignores the last 1 MiB of dirty data, aligns the sync target to 4 KiB, checks `BytesPerSync`, and either calls `SyncTo` on descriptor-backed files or full `Sync` when no descriptor exists. `Sync` ratchets the sync offset to current file offset and calls `SyncData`. `Close` performs a full sync for remaining dirty data unless `NoSyncOnClose` is set, in which case it attempts `SyncTo` and closes.

## State and Persistence Behavior
`offset` and `syncOffset` are atomic so concurrent `Sync` can observe write progress, but `Write` itself is explicitly not safe for concurrent use. `preallocatedBlocks` tracks allocation progress. Range syncs may not provide durability; full `Sync`/`SyncData` on close provides the persistence guarantee unless `NoSyncOnClose` is enabled.

## Dependencies and Integration Points
Wraps `vfs.File` and is used by WAL failover writer creation. It relies on platform-specific file `SyncTo` behavior and `Fd` support. `NewSyncingFS` supports FS-level wrapping for created files; `ReuseForWrite` is intentionally unimplemented and panics.

## Risks and Edge Cases
`NoSyncOnClose` trades durability for latency and must only be used when the caller has other guarantees. If a file lacks a descriptor, periodic sync falls back to full `Sync`, which may be expensive. Preallocation errors are ignored in `Write` because the return value of `preallocate` is discarded. `syncingFS.ReuseForWrite` panics if called.

## Test Signals
`syncing_file_test.go` covers range-sync thresholds, close behavior with full versus partial syncs, `NoSyncOnClose`, and write benchmarks. `syncing_file_linux_test.go` covers Linux sync-range smoke behavior and direct-IO benchmark paths. `fd_test.go` verifies wrapper `Fd` forwarding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_linux_test.go -->
# sources/storage-engines/pebble/vfs/syncing_file_linux_test.go

## Purpose
Provides Linux-specific tests and benchmarks for range syncing and direct IO write behavior.

## Important APIs, Types, and Functions
`TestSyncRangeSmokeTest` exercises `syncRangeSmokeTest` with injected syscall outcomes. `BenchmarkDirectIOWrite` measures aligned `O_DIRECT` writes across write sizes.

## Control Flow
The smoke test passes a fake sync-range function that validates the fd and returns nil, `EINVAL`, or `ENOSYS`; expected support is true for nil and `EINVAL`, false for `ENOSYS`. The benchmark creates a temp file, aligns a buffer to 4096 bytes, opens with `O_DIRECT`, writes at offsets until a target size, and cycles files.

## State and Persistence Behavior
The test itself does not persist Pebble data. The benchmark writes temporary files and syncs them to measure IO behavior.

## Dependencies and Integration Points
Covers Linux-only `SyncTo` support used by `syncing_file.go`. Depends on `syscall`, `unsafe`, and Linux `O_DIRECT`; build tag excludes ARM.

## Risks and Edge Cases
Benchmarks require filesystem support for `O_DIRECT` and alignment-sensitive behavior. The smoke test treats `EINVAL` as support because some kernels/filesystems may reject specific arguments while still supporting the syscall.

## Test Signals
Passing confirms the sync-range feature probe classifies common syscall responses as expected.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_test.go -->
# sources/storage-engines/pebble/vfs/syncing_file_test.go

## Purpose
Tests `syncingFile` range-sync thresholds, close-time durability behavior, `NoSyncOnClose`, and provides sync write benchmarks.

## Important APIs, Types, and Functions
`TestSyncingFile`, `TestSyncingFileClose`, `mockSyncToFile`, `TestSyncingFileNoSyncOnClose`, and `BenchmarkSyncWrite` are the main elements. `mockSyncToFile` lets tests force partial `SyncTo` behavior or full-sync fallback behavior.

## Control Flow
`TestSyncingFile` writes increasing amounts and checks expected `syncOffset` values after the 1 MiB buffer and 8 KiB threshold. `TestSyncingFileClose` logs sync/close calls through `vfsTestFSFile` and compares expected output for partial versus full-syncing files. `TestSyncingFileNoSyncOnClose` verifies close ratchets sync offset without blocking full sync when configured. The benchmark compares no preallocation, 4 MiB preallocation, and reuse scenarios.

## State and Persistence Behavior
Tests create temporary OS files and remove them afterward. They inspect in-memory offsets and logged sync calls rather than reopening files for durable content. Benchmarks perform real syncs and optional preallocation/reuse on temp files.

## Dependencies and Integration Points
Covers `syncing_file.go`, the default VFS file wrapper, and the VFS logging test wrapper. It also documents expectations for callers such as WAL writing.

## Risks and Edge Cases
The tests assert internal `syncingFile` state, so implementation refactors must preserve thresholds or adjust tests. Benchmarks are performance-only and not correctness gates.

## Test Signals
Passing confirms periodic range-sync decisions, close-time full sync when needed, and `NoSyncOnClose` behavior match the intended contract.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/syncing_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs.go -->
# sources/storage-engines/pebble/vfs/vfs.go

## Purpose
Defines Pebble's filesystem abstraction and the default OS-backed implementation, plus portable helper functions for copying, link-or-copy fallback, read-hint open options, disk usage metadata, and wrapper unwrapping.

## Important APIs, Types, and Functions
`File`, `FS`, `OpenOption`, `DeviceID`, `FileInfo`, `DiskUsage`, `Default`, and `ErrUnsupported` form the public VFS contract. `defaultFS` implements filesystem operations through `os` and `filepath`. `RandomReadsOption` and `SequentialReadsOption` apply fadvise hints when possible. `Copy`, `CopyAcrossFS`, `LimitedCopy`, `LinkOrCopy`, and `Root` are utility functions.

## Control Flow
`defaultFS.Create` opens with `O_EXCL`; if a file exists, it removes and retries so hard-linked old inodes are not truncated. Open methods apply `OpenOption`s after wrapping OS files. Copy helpers open source and destination, stream bytes, and sync the destination. `LinkOrCopy` first tries a hard link, returns immediately for existence/not-existence/permission errors, and falls back to copy for other link failures. `Root` repeatedly calls `Unwrap` until it reaches the base FS.

## State and Persistence Behavior
The default FS delegates durability to OS file operations. Copy helpers call destination `Sync`; directory sync is left to callers. `Create` intentionally changes inode identity by removing existing files. `ReuseForWrite` renames an old file and opens it without truncation, enabling WAL recycling and similar reuse patterns.

## Dependencies and Integration Points
This interface underpins Pebble storage code, `MemFS`, `errorfs`, logging wrappers, syncing wrappers, WAL managers, and tests. Platform-specific files provide OS file wrapping, locking, errors, fadvise, sync range, and disk usage.

## Risks and Edge Cases
`Create` remove-then-create is not atomic, though it loops to handle races. `LinkOrCopy` chooses portability over precise cross-device detection, so unexpected link errors may trigger a copy attempt. `CopyAcrossFS` does not sync parent directories. `File.Write` explicitly allows mutation of input buffers, so callers must not assume buffer immutability.

## Test Signals
`vfs_test.go` exercises common operations on MemFS and disk FS, link/create semantics, disk usage, root opening, and operation string coverage. `fd_test.go`, lock tests, syncing tests, and MemFS tests cover related contract pieces.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs_test.go -->
# sources/storage-engines/pebble/vfs/vfs_test.go

## Purpose
Provides datadriven and targeted tests for the VFS abstraction across MemFS and the default disk filesystem.

## Important APIs, Types, and Functions
`normalizeError`, `vfsTestFS`, `vfsTestFSFile`, `runTestVFS`, `TestVFS`, `TestVFSGetDiskUsage`, `TestVFSCreateLinkSemantics`, `TestVFSRootDirName`, and `TestOpType` are the main components.

## Control Flow
`runTestVFS` wraps an FS with logging and interprets fixture commands for clone, create, link, link-or-copy, reuse-for-write, list, mkdir, remove, and remove-all. It can inject a link error to test fallback behavior. Targeted tests check disk usage on a real temp dir, hard-link behavior when `Create` replaces a linked path, opening root directories, and string coverage for operation types.

## State and Persistence Behavior
Tests create temporary directories/files for disk VFS and use MemFS for in-memory runs. They verify `Create` on one hard link does not truncate the other link and that clone operations produce expected logs and content.

## Dependencies and Integration Points
Covers `vfs.go`, `MemFS`, clone helpers, path helpers, and error normalization through `oserror`. It serves as a cross-implementation contract test.

## Risks and Edge Cases
Disk tests are skipped on Windows for the main datadriven VFS run, so some disk behavior is only covered on non-Windows platforms. Logging wrappers in the test are specialized and not the same as `logging_fs.go`.

## Test Signals
Passing confirms MemFS and default FS share core semantics, `LinkOrCopy` behaves under injected link errors, disk usage can be queried, root directories open, and operation string coverage stays complete.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files.go -->
# sources/storage-engines/pebble/vfs/vfstest/open_files.go

## Purpose
Provides a test wrapper that tracks currently open files and can dump the stack traces that opened them. It helps diagnose leaked VFS file handles in tests.

## Important APIs, Types, and Functions
`WithOpenFileTracking` wraps an inner `vfs.FS` and returns the wrapped FS plus a dump function. `openFilesFS` implements `vfs.FS`. `openFile` wraps `vfs.File`, stores caller PCs, dumps stack frames, and removes itself from tracking on `Close`.

## Control Flow
All FS methods that open or create files call `wrapOpenFile`. If the open succeeds, `runtime.Callers` captures the call stack, the file is inserted into the `files` map under mutex, and the wrapper is returned. `dumpStacks` prints a count and each open file's captured stack. Closing an `openFile` delegates close then removes it from the map.

## State and Persistence Behavior
State is in-memory tracking metadata only: a mutex-protected map of open wrapper pointers and captured PCs. Underlying filesystem state is delegated unchanged.

## Dependencies and Integration Points
Part of package `vfstest`, used by tests that need leak diagnostics around any `vfs.FS`. It implements `Unwrap` so root unwrapping still works.

## Risks and Edge Cases
If the underlying `Close` returns an error, the file is still removed from tracking. Lock handles are not tracked because `Lock` returns `io.Closer`, not `vfs.File`. Stack depth is capped at 20 PCs.

## Test Signals
`open_files_test.go` verifies every file-opening method reports a leak before close and reports nothing after close.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files_test.go -->
# sources/storage-engines/pebble/vfs/vfstest/open_files_test.go

## Purpose
Tests the open-file tracking VFS wrapper.

## Important APIs, Types, and Functions
`TestOpenFiles` uses `WithOpenFileTracking`, a MemFS, and a table of file-opening operations: `OpenDir`, `Create`, `Open`, `OpenReadWrite`, and `ReuseForWrite`.

## Control Flow
The test prepares a directory and file operations, then runs two subtests. In `leaks`, each operation opens a file, dumps stacks, asserts output exists, closes the file, and asserts the dump is empty. In `noleaks`, it opens and closes before dumping and expects no output.

## State and Persistence Behavior
State is an in-memory MemFS plus tracking map. `ReuseForWrite` renames `foo` to `bar`, so the operation sequence relies on the surrounding setup and subtest order.

## Dependencies and Integration Points
Covers `open_files.go` and the VFS file-opening methods. It validates the wrapper as a reusable test diagnostic.

## Risks and Edge Cases
The test only asserts non-empty dump output, not exact stack contents. It does not cover open failures or lock handles.

## Test Signals
Passing confirms tracked files are registered on open/create/reuse and unregistered on close.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/open_files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/vfstest.go -->
# sources/storage-engines/pebble/vfs/vfstest/vfstest.go

## Purpose
Defines small test helpers for VFS consumers.

## Important APIs, Types, and Functions
`DiscardFile` is a `vfs.File` implementation backed by `discardFile`. It accepts writes, returns requested byte counts for reads, and no-ops sync, preallocation, close, and prefetch.

## Control Flow
Every method on `discardFile` returns immediately with success-like values. `Read` and `ReadAt` report `len(p)` without filling the buffer. `Fd` returns 0 rather than `vfs.InvalidFd`.

## State and Persistence Behavior
No state is stored and no bytes are persisted. It is a sink/source stub for tests and benchmarks.

## Dependencies and Integration Points
Lives in `vfstest` for tests that need a cheap file-like object satisfying the full `vfs.File` interface.

## Risks and Edge Cases
`Fd` returning 0 can look like a real descriptor on Unix stdin, so callers that use `Fd` should not use `DiscardFile` unless that behavior is acceptable. `Stat` returns nil info and nil error, which may surprise callers expecting metadata.

## Test Signals
No direct test in this file. Compile-time interface satisfaction comes from assigning `DiscardFile` as `vfs.File`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/vfstest/vfstest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager.go -->
# sources/storage-engines/pebble/wal/failover_manager.go

## Purpose
Implements the WAL manager for failover mode, where a logical WAL may be written across primary and secondary directories and the active directory can switch on write errors or unhealthy latency. It also manages secondary directory identity, probing for failback, WAL listing/obsolete accounting, recycling, stats, and goroutine lifecycle.

## Important APIs, Types, and Functions
`dirProber` probes primary health. `ValidateOrInitWALDir`, `readSecondaryIdentifier`, and `writeSecondaryIdentifier` manage stable secondary IDs. `failoverMonitor` watches a `switchableWriter` and switches directories. `failoverManager` implements `Manager` through `init`, `List`, `Obsolete`, `Create`, `ElevateWriteStallThresholdForFailover`, `Stats`, `Close`, and `Opts`. `logCreator` creates or reuses WAL segment files. `stopper`, `timeSource`, and ticker types coordinate background work and tests.

## Control Flow
Initialization ensures the secondary is writable by writing `failover_source`, opens both WAL directories, starts a stopper, creates a monitor/prober, initializes the recycler, and converts initial scanned logs into obsolete records while ratcheting minimum recyclable numbers. `failoverMonitor.monitorLoop` samples current writer latency/error; it switches immediately on errors, switches on latency above thresholds, enables primary probing when on secondary, and fails back when probe mean/max are healthy. `Create` constructs failover-writer options and asks the monitor to create a writer in the current directory. Closed writer/segment callbacks merge physical segments into sorted logical WAL records.

## State and Persistence Behavior
Persistent effects include secondary identity files, `failover_source`, WAL segment files, directory syncs, and recycled WAL renames. In memory, the manager tracks initial obsolete logs, closed logical WALs and their physical segments, current writer, recycler state, directory handles, failover stats, and monitor/prober state. `writeSecondaryIdentifier` syncs the file and containing directory to make the identifier durable. `Obsolete` either returns physical logs for deletion or adds eligible primary synchronously closed single-segment WALs to the recycler.

## Dependencies and Integration Points
Integrates with WAL `Options`, `Dir`, `Manager`, `Writer`, `Scan`, `LogicalLog`, `DeletableLog`, record log writers through `failover_writer.go`, `LogRecycler`, VFS APIs, event listeners, histograms, CockroachDB time/error helpers, and Pebble format/options code that stores secondary IDs.

## Risks and Edge Cases
`generateStableIdentifier` ignores the error return from `crypto/rand.Read`, so entropy failure would not be reported. Failover heuristics are intentionally arbitrary and may need tuning; high secondary error counts suppress switching from primary to a likely misconfigured secondary. `RecyclerForTesting` returns nil despite the manager having a recycler. If a recycled-file reuse fails after `Pop`, cleanup of old/new files is left to restart-era cleanup. Segment creation is asynchronous, so `writerClosed` may not know all segments; `segmentClosed` repairs that later.

## Test Signals
`failover_manager_test.go` covers prober sampling, monitor switching/failback, failover manager datadriven behavior, quiesce under latency injection, secondary writability validation, and randomized all-files-deletable accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager_test.go -->
# sources/storage-engines/pebble/wal/failover_manager_test.go

## Purpose
Tests the WAL failover manager, primary prober, monitor switching logic, secondary writability validation, graceful quiescence, and eventual deletion accounting for all physical WAL files.

## Important APIs, Types, and Functions
`manualTime` and `manualTicker` provide deterministic time. `TestDirProber`, `TestManagerFailover`, `TestFailoverManager_Quiesce`, `TestFailoverManager_SecondaryIsWritable`, and `TestFailoverManager_AllFilesDeletable` are the primary tests. Helper methods print prober and monitor state for datadriven outputs.

## Control Flow
`TestDirProber` initializes a prober with optional `errorfs` injectors and a blocking FS, enables/disables probing, advances manual time, blocks/unblocks IO, and queries mean/max samples. `TestManagerFailover` initializes a failover manager with manual thresholds, creates/writes/closes writers, blocks operations, advances monitor/prober time, lists stats, checks elevation state, and exercises obsolete behavior. The quiesce test uses `synctest` with random latency. The all-files-deletable test repeatedly creates WALs under latency, advances min-unflushed, calls `Obsolete`, deletes returned files, and eventually asserts no old logs remain.

## State and Persistence Behavior
Tests use MemFS directories for primary/secondary WALs and wrap them with error/latency/blocking layers. They create real in-memory WAL segments, secondary metadata, probe files, recycler state, and failover stats. Manual time makes background monitor/prober state deterministic.

## Dependencies and Integration Points
Covers `failover_manager.go`, `failover_writer.go`, `errorfs`, `vfs.MemFS`, WAL scanning/file accumulation, prometheus histograms, and the blocking FS helper defined in `failover_writer_test.go`.

## Risks and Edge Cases
Datadriven tests expose implementation details through channels to wait for goroutine iterations. The randomized all-files-deletable test can depend on timing but uses `Eventually` to absorb asynchronous segment callbacks. TODOs note missing prober history wraparound tests.

## Test Signals
Passing confirms switching/failback heuristics, stats updates, secondary preflight errors, goroutine shutdown, and physical WAL cleanup accounting remain functional.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer.go -->
# sources/storage-engines/pebble/wal/failover_writer.go

## Purpose
Implements the failover-mode WAL writer. It writes records to the current physical `record.LogWriter`, retains unsynced records in a replay queue, asynchronously creates replacement segment writers on directory switches, and closes only when all queued records are durably written or a latest-writer creation/close error is known.

## Important APIs, Types, and Functions
`recordQueue`, `recordQueueEntry`, `poppedEntry`, `failoverWriter`, `failoverWriterOpts`, `logWriterAndRecorder`, `newFailoverWriter`, `WriteRecord`, `switchToNewDir`, `doneSyncCallback`, `Close`, `getLog`, and `latencyAndErrorRecorder` are central. Constants include `initialBufferLen` and `maxPhysicalLogs`.

## Control Flow
`WriteRecord` refs the caller's buffer, pushes the record into `recordQueue`, and if a current `record.LogWriter` exists, calls `SyncRecordGeneralized` with a pending sync index. `recordQueue` tracks `[tail, head)` with an atomic packed head/tail, grows as needed, snapshots outstanding records on writer switch, and pops records when a sync callback confirms durability. `switchToNewDir` reserves a physical log index, asynchronously creates/syncs the file and directory, wraps it in `SyncingFile` and `latencyAndErrorRecorder`, creates a `record.LogWriter`, and snapshots queued records into it if it is still latest. `Close` loops over created and creating writers, closes latest writers with the last queued record index, handles switches racing with close, pops any remaining entries with close error, and invokes manager callbacks.

## State and Persistence Behavior
Persistent state is physical WAL segment files named by logical WAL number and segment index in primary or secondary dirs. Queue state holds unsynced byte slices until a sync callback pops them and unrefs. Logical offsets are best-effort during periods before a writer exists or across failover replay. `getLog` exposes known segments with approximate sizes and whether they closed synchronously, enabling recycling only for safe segments.

## Dependencies and Integration Points
Integrates with `record.LogWriter`, WAL manager callbacks, `vfs.NewSyncingFile`, directory handles, metrics histograms, queue semaphores used by sync concurrency, failover monitor through `switchableWriter`, and `latencyAndErrorRecorder` for health sampling.

## Risks and Edge Cases
The queue can grow to the unsynced memtable-sized workload if callers do not request syncs. Logical offsets are approximate in some failover/no-writer cases, as comments document. Switching is capped at ten physical logs. Asynchronous segment creation means late-created unused files must be reported via `segmentClosed`. Close has complex races with monitor-triggered switches and stuck writers; errors from latest writer close/creation are fatal to callers.

## Test Signals
`failover_writer_test.go` covers datadriven switching, blocked IO, close modes, segment metadata, queue semaphore behavior, many-record queue growth, concurrent writer switches, and record continuity across physical segments.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer_test.go -->
# sources/storage-engines/pebble/wal/failover_writer_test.go

## Purpose
Tests failover writer behavior under switching, blocked IO, injected errors, close races, queue growth, and large record counts.

## Important APIs, Types, and Functions
`TestFailoverWriter` is a datadriven harness over crashable MemFS. `blockingFS` and `blockingFile` provide controllable blocking for create/write/sync/close/open-dir. `TestConcurrentWritersWithManyRecords` stresses queue resizing and multi-writer replay. `TestFailoverWriterManyRecords` writes four times the initial queue length. `randStr` and `seed` support randomized data generation.

## Control Flow
The datadriven harness initializes dirs, creates failover writers with optional injected errors or delayed writer creation, writes records with optional syncs, waits for queue length, switches dirs, closes synchronously or asynchronously, dumps logs after crash cloning, and inspects segment metadata. The concurrent test blocks all physical writers, writes thousands of unique records while periodically switching dirs, unblocks writes, closes, waits for syncs, and verifies each physical log contains a contiguous prefix interval and the final writer contains all records.

## State and Persistence Behavior
Tests use crashable MemFS and sync root/directories so printed log files reflect durable post-crash state. Queue semaphores model outstanding sync capacity. Blocking configuration is in-memory and released by closing channels. WAL segment files are read back through `record.Reader` to validate replay and sync behavior.

## Dependencies and Integration Points
Covers `failover_writer.go`, `record.LogWriter`, `vfs.NewCrashableMem`, `errorfs`, `LogNameIndex` naming, prometheus histograms, and the `stopper` lifecycle. `blockingFS` is also reused by manager tests.

## Risks and Edge Cases
The datadriven harness relies on sleeps and wait channels for async behavior. The concurrent test uses many records and may be relatively expensive, but it covers queue resize and pop races. TODO notes missing randomized error and delay injection tests.

## Test Signals
Passing indicates records are replayed correctly across switches, close propagates sync errors and metadata correctly, queue semaphores drain, and large queues do not lose or reorder synced records.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/failover_writer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler.go -->
# sources/storage-engines/pebble/wal/log_recycler.go

## Purpose
Maintains a bounded FIFO set of obsolete WAL files that may be reused instead of deleted. Recycling improves WAL creation/sync performance by avoiding some filesystem metadata work.

## Important APIs, Types, and Functions
`LogRecycler` stores a limit, minimum recyclable log number, queued `base.FileInfo` entries, and max log number seen. `Init`, `RatchetMinRecycleLogNum`, `Add`, `Peek`, `Stats`, `Pop`, `LogNumsForTesting`, and `maxLogNumForTesting` are the main methods.

## Control Flow
`Init` sets the queue limit. `RatchetMinRecycleLogNum` monotonically increases the minimum accepted file number. `Add` rejects logs below the minimum, ignores already-considered log numbers, updates `maxLogNum`, and appends if under the limit. `Peek` returns the head entry. `Pop` requires the requested file number to match the head, then removes it. `Stats` sums current queued sizes.

## State and Persistence Behavior
State is in memory only. The actual filesystem rename/reuse happens in the WAL manager's `logCreator`; this type only decides which obsolete files are eligible and in which order.

## Dependencies and Integration Points
Used by standalone and failover WAL managers to recycle safe obsolete WALs. It stores `base.FileInfo` so callers can reuse file numbers and sizes. Failover mode protects `Peek`/`Pop` pairs with an additional mutex because async segment creation can race.

## Risks and Edge Cases
Once a file number is considered and rejected due to queue limit, later `Add` for that number returns true without enqueuing because `maxLogNum` already advanced; callers must not delete such a file twice. `Pop` enforces FIFO head matching, so callers must coordinate `Peek` and `Pop` correctly.

## Test Signals
`log_recycler_test.go` covers min-number filtering, limit behavior, duplicate/previously considered numbers, stats-visible queue order, invalid pop errors, and empty pop errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler_test.go -->
# sources/storage-engines/pebble/wal/log_recycler_test.go

## Purpose
Tests `LogRecycler` queue admission, ordering, duplicate handling, and pop validation.

## Important APIs, Types, and Functions
`TestLogRecycler` constructs a recycler with limit 3 and min recyclable log 4, then exercises `Add`, `Peek`, `Pop`, `LogNumsForTesting`, and `maxLogNumForTesting`.

## Control Flow
The test rejects logs below the minimum, adds logs up to the limit, verifies the queue and max number, rejects a past-limit log while advancing max, confirms re-adding an already considered log leaves state unchanged, checks invalid pop errors, pops in order, verifies a previously considered log is not newly recycled, then drains the queue and checks empty pop error text.

## State and Persistence Behavior
All state is in-memory recycler metadata; no files are created.

## Dependencies and Integration Points
Covers `log_recycler.go` and `base.FileInfo`/`DiskFileNum` formatting. It protects behavior expected by WAL manager recycling paths.

## Risks and Edge Cases
The test uses zero file sizes, so `Stats` size accumulation is not directly asserted. It focuses on queue membership and ordering.

## Test Signals
Passing confirms the recycler's bounded FIFO and max-number semantics are stable.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/wal/log_recycler_test.go -->
