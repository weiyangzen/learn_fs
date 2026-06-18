# Research Report: subset-b-009164

This grouped report covers the requested restic restore, repository, terminal, self-update, test, textfile, and UI files. Each source section is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister.go -->
# sources/sync-backup/restic/internal/restic/lister.go

## Purpose
Implements an in-memory wrapper for a repository/backend lister so a single `List` result can be replayed without re-querying storage.

## Important APIs and Control Flow
`fileInfo`, `memorizedLister.List`, and `MemorizeList` are the important pieces. `MemorizeList` detects an already-memoized lister, otherwise collects `(ID,size)` pairs for exactly one `FileType`. `memorizedLister.List` rejects mismatched file types, iterates the cached slice, forwards each pair to the callback, and stops on callback or context errors.

## State, Persistence, Dependencies, and Integration
State is a process-local slice plus the memoized file type; nothing is persisted. It depends only on `context`, `fmt`, and the repository `Lister`/`FileType` contracts and is used by callers that need stable repeated list iteration.

## Risks and Test Signals
The cache can become stale if the backend changes after memoization, and it is scoped to one file type. Tests verify replay, file-type mismatch errors, idempotent wrapping behavior, and source-list error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister_test.go -->
# sources/sync-backup/restic/internal/restic/lister_test.go

## Purpose
Tests the memoized lister wrapper from the external `restic_test` package to exercise the exported API.

## Important APIs and Control Flow
`ListHelper` implements `restic.Lister`; `TestMemoizeList` builds a fake list source, memoizes snapshot files, verifies mismatched file types fail, and replays the cached IDs/sizes. `TestMemoizeListError` confirms source-list errors abort memoization. Each test uses callbacks to model backend iteration and `internal/test` assertions for equality and error handling.

## State, Persistence, Dependencies, and Integration
State is test-local generated IDs and slices. Dependencies include `backend.FileType`, exported restic APIs, and the shared test helpers.

## Risks and Test Signals
The tests signal correct cache replay and error propagation but do not cover context cancellation or concurrent use of the memoized lister.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/lister_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel.go -->
# sources/sync-backup/restic/internal/restic/parallel.go

## Purpose
Provides concurrency helpers for listing repository files and deleting unpacked repository files.

## Important APIs and Control Flow
`ParallelList` streams `Lister.List` output into worker goroutines under an `errgroup`; `ParallelRemove` uses a generic `RemoverUnpacked` repository, limits goroutines to `repo.Connections()`, reports per-ID results, and advances a `Counter` only on successful removal. Both helpers derive a cancellable context from `errgroup.WithContext`, so the first worker error cancels pending producers/workers. `ParallelRemove` also stops scheduling when cancellation is observed.

## State, Persistence, Dependencies, and Integration
State is transient goroutine, channel, and progress-counter state. Integration points are repository listers/removers, `IDSet`, `FileType` generics, `debug.Log`, and `golang.org/x/sync/errgroup`.

## Risks and Test Signals
Risks are deadlock/cancellation regressions, accidental progress increments on failed deletes, and loop-variable capture in concurrent removal. Tests cover successful removes, remove/report errors, reporting IDs, progress count, and cancellation-sensitive scheduling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel_test.go -->
# sources/sync-backup/restic/internal/restic/parallel_test.go

## Purpose
Tests `ParallelRemove` against a mock unpacked-file remover and an atomic test counter.

## Important APIs and Control Flow
`mockRemoverUnpacked` provides two connections and injectable removal behavior; `NewTestID` creates deterministic IDs; `TestParallelRemove` table-drives successful deletes, remove failures, report failures, expected report IDs, and progress counts. The test collects removed IDs under synchronization where needed and checks that errors stop the errgroup while successful removals advance the counter.

## State, Persistence, Dependencies, and Integration
State is entirely test-local: ID sets, mutex/atomic counters, and error injections. It depends on `internal/errors` and core restic ID helpers.

## Risks and Test Signals
The suite gives useful concurrency-contract coverage but remains timing-light; it does not force high contention or verify exact scheduling order.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/parallel_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress.go -->
# sources/sync-backup/restic/internal/restic/progress.go

## Purpose
Defines the minimal progress counter interfaces used by core repository helpers without depending on UI packages.

## Important APIs and Control Flow
`Counter` exposes `Add`, `SetMax`, `Get`, and `Done`; `noopCounter` and `NoopCounter` implement a safe no-op counter. `noopTerminalCounterFactory` implements `TerminalCounterFactory.NewCounterTerminalOnly` by returning the no-op counter. There is no control flow beyond method dispatch; callers can always install a counter and skip nil checks.

## State, Persistence, Dependencies, and Integration
No state is persisted. The file integrates low-level restic packages with terminal/UI progress implementations through interfaces declared in `repository.go`.

## Risks and Test Signals
The main risk is interface drift between core and UI progress implementations. Tests assert that all no-op methods are callable and return `(0,0)` without panics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress_test.go -->
# sources/sync-backup/restic/internal/restic/progress_test.go

## Purpose
Smoke-tests the no-op progress implementations used by core restic packages.

## Important APIs and Control Flow
`TestNoopCounter` calls `Add`, `SetMax`, `Get`, and `Done` through `NoopCounter` and exercises `NoopTerminalCounterFactory.NewCounterTerminalOnly`. The test verifies no panic and zero-valued progress state rather than formatting or timing behavior.

## State, Persistence, Dependencies, and Integration
There is no persistent state. Integration is with the `Counter` and `TerminalCounterFactory` interfaces used by repository and UI code.

## Risks and Test Signals
The signal is intentionally narrow: it catches interface drift but not real UI counter behavior, which is covered in `internal/ui/progress` tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/progress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/repository.go -->
# sources/sync-backup/restic/internal/restic/repository.go

## Purpose
Defines the central repository interfaces, file type aliases, writable file type constraints, blob loading/saving contracts, warmup contracts, and capability bundles used across restic internals.

## Important APIs and Control Flow
`Repository` is the high-level interface for backend access, config, blob operations, index lookup, warmup, and feature versioning. The file also aliases backend file-type constants, declares `WriteableFileType`, `FileTypes`, `LoaderUnpacked`, `SaverUnpacked`, `RemoverUnpacked`, `Lister`, `BlobLoader`, `BlobSaver`, `BlobSaverAsync`, `WarmupJob`, and set/query interfaces. There is little executable flow beyond `WriteableFileType.ToFileType`; the file is a compile-time contract hub used by repository, restorer, UI, check, prune, and self-test code.

## State, Persistence, Dependencies, and Integration
No runtime state is stored here. Dependencies are `context`, `io`, and internal `backend`, `crypto`, and `errors`; persistence behavior is delegated to implementations that satisfy these interfaces.

## Risks and Test Signals
Risks are broad blast radius from interface changes and generic type-set mistakes. Test signal comes indirectly from all packages that compile against these contracts plus targeted tests for helpers such as parallel removal, listers, config, and blob operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/repository.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/testing.go -->
# sources/sync-backup/restic/internal/restic/testing.go

## Purpose
Provides restic-package helpers intended for tests and fixtures that need deterministic parsing or random IDs.

## Important APIs and Control Flow
`TestParseID` parses an ID string and panics on failure, `TestParseHandle` builds a `BlobHandle` for a parsed ID and blob type, `NewRandomBlobHandle` creates a random data blob handle, and `NewRandomID` fills an `ID` from `crypto/rand`. Control flow is fail-fast: parse or random-reader failures panic so tests can construct fixtures tersely without repetitive error checks.

## State, Persistence, Dependencies, and Integration
State is limited to generated random bytes returned to callers; nothing is persisted. Integration is with tests that need IDs and blob handles without standing up a repository.

## Risks and Test Signals
Risks are panic use outside test contexts and nondeterminism from random IDs. The helper is small and indirectly covered by tests that construct random/mocked repository data.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_unix.go -->
# sources/sync-backup/restic/internal/restic/uid_unix.go

## Purpose
Converts OS user/group information into numeric uid/gid values on Unix-like platforms.

## Important APIs and Control Flow
`UidGidInt` parses `user.User.Uid` and `Gid` with `strconv.ParseUint` and returns `uint32` values. Control flow is a pair of parse operations with early return on invalid uid, then gid parsing.

## State, Persistence, Dependencies, and Integration
No state is persisted. It integrates with restore/backup metadata handling that needs numeric ownership on Unix platforms and depends on Go's `os/user` package.

## Risks and Test Signals
Risks are platform user database oddities and overflow/parse failures, which are surfaced to callers. Windows has a separate stub because uid/gid semantics do not apply.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_windows.go -->
# sources/sync-backup/restic/internal/restic/uid_windows.go

## Purpose
Provides the Windows implementation of uid/gid conversion for code paths that need a cross-platform symbol.

## Important APIs and Control Flow
`UidGidInt` ignores the supplied user and returns zero uid, zero gid, and nil error. Control flow is intentionally trivial because Windows metadata restoration uses different attributes and ACL concepts.

## State, Persistence, Dependencies, and Integration
There is no state or persistence. The file is selected by build tags through filename suffix and keeps shared code compiling on Windows.

## Risks and Test Signals
Risk is accidental use of zero uid/gid as meaningful Windows ownership data; platform-specific restore code should rely on Windows metadata instead.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/uid_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix.go -->
# sources/sync-backup/restic/internal/restic/zeroprefix.go

## Purpose
Computes the number of leading zero bits in a byte slice, used by restic ID/search logic that reasons about hash prefixes.

## Important APIs and Control Flow
`ZeroPrefixLen` walks bytes until a non-zero byte, adds eight bits for each zero byte, then uses `bits.LeadingZeros8` for the first non-zero byte. The function exits early on the first non-zero byte and returns all-bit length for an all-zero slice.

## State, Persistence, Dependencies, and Integration
No state is stored. It depends only on `math/bits` and integrates with ID/hash matching logic.

## Risks and Test Signals
Risks are off-by-one bit counts and empty/all-zero handling. Tests cover representative byte patterns, nil/empty behavior, all-zero input, and benchmarks track the hot-path cost.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix_test.go -->
# sources/sync-backup/restic/internal/restic/zeroprefix_test.go

## Purpose
Validates and benchmarks `ZeroPrefixLen`.

## Important APIs and Control Flow
`TestZeroPrefixLen` runs table cases for empty input, zero bytes, and mixed byte prefixes; `BenchmarkZeroPrefixLen` measures repeated calls on representative byte slices. Control flow is simple table iteration with exact expected leading-zero-bit counts.

## State, Persistence, Dependencies, and Integration
No persistent state. Tests depend on the exported `restic.ZeroPrefixLen` API from the external test package.

## Risks and Test Signals
The coverage is strong for edge cases and regressions in bit accounting, though it does not tie the helper to higher-level ID-search behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restic/zeroprefix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/doc.go -->
# sources/sync-backup/restic/internal/restorer/doc.go

## Purpose
Documents the restorer package and explains the high-level restore architecture.

## Important APIs and Control Flow
The package comment describes the two-pass restore approach: create directories and collect file content first, then restore metadata, hardlinks, and special nodes after file data exists. It has no executable control flow; it is important because it frames how `restorer.go`, `filerestorer.go`, and `fileswriter.go` cooperate.

## State, Persistence, Dependencies, and Integration
No state or dependencies beyond the package declaration. Integration is documentation for callers and maintainers of restore behavior.

## Risks and Test Signals
Risk is documentation drift as restore behavior changes. Tests in the restorer package provide the actual behavioral signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer.go -->
# sources/sync-backup/restic/internal/restorer/filerestorer.go

## Purpose
Restores regular file contents by planning blob downloads per pack and writing downloaded blobs to target files, including sparse-file and partial-overwrite support.

## Important APIs and Control Flow
`fileRestorer`, `fileInfo`, `packInfo`, `fileBlobInfo`, `newFileRestorer`, `addFile`, `restoreFiles`, `downloadPack`, `downloadBlobs`, and `reportBlobProgress` are central. `restoreFiles` maps file blobs to packs, skips matching blobs from `fileState`, tracks sparse eligibility via the zero chunk, optionally warms cold S3 packs, and launches pack download workers. `downloadPack` builds blob-to-file-offset mappings; `downloadBlobs` invokes the repository pack loader and writes every blob to every offset through `filesWriter`, using per-file locks only to ensure first create/preallocation happens once while later writes can run concurrently.

## State, Persistence, Dependencies, and Integration
State includes the pending file list, transient pack maps/order, per-file in-progress/sparse flags, and progress callbacks. It depends on repository index lookup, `LoadBlobsFromPack`, cold-storage warmup, `filesWriter`, feature flags, and restore UI progress.

## Risks and Test Signals
Risks include corrupt restores if sparse handling is wrong for partial overwrites, imprecise error attribution when pack downloads fail, and concurrency races around first file creation. Tests cover basic restore, pack skipping, repeated/frequent blobs, cold-storage warmup, download errors, and per-file error reporting.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer_test.go -->
# sources/sync-backup/restic/internal/restorer/filerestorer_test.go

## Purpose
Unit-tests `fileRestorer` using an in-memory pack/blob repository model.

## Important APIs and Control Flow
The test scaffolding defines `TestBlob`, `TestFile`, `TestRepo`, `testPackBlob`, and `TestWarmupJob` to emulate pack layouts, blob lookup, pack loading order, and cold-storage warmup. Tests exercise basic multi-file restore, selected file restore from shared packs, very frequent blobs, loader failure, and fatal per-blob download errors. Control flow builds synthetic packs from file content, restores into temp dirs, then verifies restored bytes and warmup wait behavior.

## State, Persistence, Dependencies, and Integration
State is temporary filesystem output plus in-memory pack maps and error traces. Dependencies are `feature.S3Restore`, restic IDs/blob handles, and shared test helpers.

## Risks and Test Signals
The suite gives strong coverage of pack planning and error attribution but intentionally bypasses full snapshot traversal and metadata restoration covered in `restorer_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/filerestorer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter.go

## Purpose
Manages concurrent low-level writes to restored files while safely creating, replacing, sizing, caching, and closing file handles.

## Important APIs and Control Flow
`filesWriter`, `filesWriterBucket`, `partialFile`, `newFilesWriter`, `openFile`, `createFile`, `ensureSize`, `writeToFile`, and `flush` are the main APIs. `writeToFile` hashes paths into buckets, reuses active or LRU-cached file handles, writes with `WriteAt`, and releases handles back to cache when no users remain. `createFile` handles read-only targets, symlinks, directories, hardlinked files, recursive deletion policy, no-follow opens, exclusive replacement, preallocation, and sparse truncation.

## State, Persistence, Dependencies, and Integration
State is process-local: bucket maps, reference counts, sparse flags, and an LRU cache. It integrates with `internal/fs`, platform truncate helpers, xxhash, and simplelru; persistence is the target filesystem content and metadata side effects.

## Risks and Test Signals
Risks are TOCTOU/path replacement issues, leaking handles under errors, platform-specific readonly and directory behavior, and corrupting hardlinked existing files. Tests cover basic writes/cache behavior, replacing directories/symlinks/hardlinks, recursive delete policy, sparse sizing, and platform-specific directory-not-empty errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_other_test.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter_other_test.go

## Purpose
Provides the non-Windows expected error helper for `fileswriter_test.go`.

## Important APIs and Control Flow
`notEmptyDirError` returns `syscall.ENOTEMPTY` so recursive overwrite tests can compare portable error values. There is no runtime flow beyond returning the platform constant.

## State, Persistence, Dependencies, and Integration
No state is stored; the file is selected on non-Windows platforms by build tag.

## Risks and Test Signals
The test signal is indirect: it keeps filled-directory overwrite assertions accurate on Unix-like platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_other_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_test.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter_test.go

## Purpose
Tests file creation, replacement, recursive deletion, hardlink safety, and writer cache behavior.

## Important APIs and Control Flow
`TestFilesWriterBasic` writes two files through a one-entry writer and verifies data after `flush`. `TestFilesWriterRecursiveOverwrite`, `TestCreateFile`, and `TestCreateFileRecursiveDelete` exercise regular files, empty/filled directories, symlinks, readonly files, hardlinks, sparse/non-sparse sizing, and recursive delete policy. Control flow creates target fixtures, invokes `writeToFile` or `createFile`, checks resulting file type/size/content, and cleans up.

## State, Persistence, Dependencies, and Integration
State is temporary filesystem data plus writer bucket/cache internals. Dependencies include `internal/fs`, `internal/errors`, syscall constants supplied by OS-specific test files, and shared test helpers.

## Risks and Test Signals
Coverage is strong for replacement edge cases. Remaining risks are high-contention concurrent write races and filesystem-specific preallocation/sparse behavior that unit tests may not fully expose.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_windows_test.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter_windows_test.go

## Purpose
Provides the Windows expected error helper for `fileswriter_test.go`.

## Important APIs and Control Flow
`notEmptyDirError` returns `syscall.ERROR_DIR_NOT_EMPTY` for Windows directory replacement assertions. No control flow beyond returning the platform error constant.

## State, Persistence, Dependencies, and Integration
No state is stored. The file is selected only on Windows by filename/build constraints.

## Risks and Test Signals
Its test signal is indirect but necessary for portable filled-directory overwrite tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index.go -->
# sources/sync-backup/restic/internal/restorer/hardlinks_index.go

## Purpose
Implements a generic hardlink index keyed by inode and device ID so restore can recognize multiple snapshot nodes referring to the same file.

## Important APIs and Control Flow
`HardlinkIndex[T]`, `NewHardlinkIndex`, `Add`, `Has`, `Value`, and `Remove` wrap a map keyed by a small inode/device struct. Restore code adds the first hardlinked file location and later uses `Has`/`Value` to create hardlinks to the already-restored target instead of duplicating content.

## State, Persistence, Dependencies, and Integration
State is an in-memory map for one restore run. It integrates with `Restorer.RestoreTo` hardlink handling and is not persisted.

## Risks and Test Signals
Risks are incorrect inode/device keys causing missed or wrong hardlink reconstruction. Tests verify add, lookup, existence, and removal behavior for generic string values.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index_test.go -->
# sources/sync-backup/restic/internal/restorer/hardlinks_index_test.go

## Purpose
Tests the generic `HardlinkIndex` API from the external `restorer_test` package.

## Important APIs and Control Flow
`TestHardLinks` creates an index, adds two inode/device mappings, verifies values and existence checks, then removes one mapping and verifies it is absent. The control flow is direct API exercise without filesystem interaction.

## State, Persistence, Dependencies, and Integration
State is a test-local map inside the index. It depends on exported `restorer.NewHardlinkIndex` and shared equality helpers.

## Risks and Test Signals
The test catches basic keying regressions but does not cover full restore hardlink creation; platform restore tests cover that integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/hardlinks_index_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer.go -->
# sources/sync-backup/restic/internal/restorer/restorer.go

## Purpose
Coordinates full snapshot restoration: traversal, filtering, overwrite decisions, file-content restore, metadata restore, hardlink recreation, deletion of unexpected files, and verification.

## Important APIs and Control Flow
`Restorer`, `Options`, `OverwriteBehavior`, `NewRestorer`, `traverseTree`, `RestoreTo`, `removeUnexpectedFiles`, `withOverwriteCheck`, `shouldOverwrite`, `VerifyFiles`, and `verifyFile` are the central APIs. `RestoreTo` normalizes the destination, creates the target directory, performs a first tree pass to create directories and collect regular files, delegates file data to `fileRestorer`, then performs a second pass for special nodes, hardlinks, deletion, and metadata. `traverseTreeInner` enforces safe child names and path prefixes, applies select filters, skips sockets, and defers directory metadata until leaving directories. `verifyFile` compares existing/restored files blob-by-blob, optionally trusting mtime for `OverwriteIfChanged`, and feeds partial match state back into incremental restore.

## State, Persistence, Dependencies, and Integration
State includes `fileList` metadata-only flags, options, filters, progress, hardlink index, scratch buffers, and transient verification worker channels. It depends on repository tree/blob APIs, `internal/data`, `internal/fs`, `fileRestorer`, restore UI progress, and errgroup concurrency.

## Risks and Test Signals
High-risk areas are path traversal protection, delete mode, overwrite semantics, metadata-only skips, hardlink handling, partial restore verification, and progress accounting. The large test suite covers basic/relative restore, traversal order, timestamps/permissions, cancellation, sparse files, overwrite modes, dry-run/delete behavior, restore-to-file errors, long paths, Unix hardlinks/permissions, and Windows attributes/case behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_test.go -->
# sources/sync-backup/restic/internal/restorer/restorer_test.go

## Purpose
Provides the main behavioral integration tests for snapshot restoration.

## Important APIs and Control Flow
The file defines synthetic snapshot/node builders, repository save helpers, traversal-check helpers, printer mocks, and many `TestRestorer*`/`TestRestore*` cases. It covers restoring files/dirs/special nodes, relative destinations, traversal ordering, timestamp and permission consistency, cancellation in verification, sparse files and overwrites, overwrite policies, modified-file handling, `if-changed`, dry-run, delete mode, directory overwrite behavior, restore-to-file failures, and long paths. Control flow builds test snapshots in a test repository, restores into temp dirs, mutates destinations for overwrite scenarios, and asserts filesystem state plus progress traces.

## State, Persistence, Dependencies, and Integration
State is temporary repositories/filesystems and in-memory progress/error tracking. Dependencies include `repository.TestRepository`, `internal/data`, `internal/fs`, restore UI progress, and platform helpers.

## Risks and Test Signals
This is the strongest signal for restore correctness, but it is necessarily complex and can be platform-sensitive around filesystem metadata, sparse allocation, and long path behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix.go -->
# sources/sync-backup/restic/internal/restorer/restorer_unix.go

## Purpose
Contains Unix-specific filename comparison behavior for restore delete logic.

## Important APIs and Control Flow
The platform helper keeps filenames comparable using the native case-sensitive representation. Control flow is a small conversion function used when building the keep-set in `removeUnexpectedFiles`.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with `Restorer.removeUnexpectedFiles` and is selected on Unix platforms.

## Risks and Test Signals
Risk is platform mismatch if mounted filesystems have non-standard case behavior. Windows has a separate implementation for case-insensitive comparison.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix_test.go -->
# sources/sync-backup/restic/internal/restorer/restorer_unix_test.go

## Purpose
Covers Unix-specific restore behavior for hardlinks, progress accounting, sparse block counting, and permissions.

## Important APIs and Control Flow
`TestRestorerRestoreEmptyHardlinkedFields` verifies empty hardlinked files share an inode when possible. Progress-bar tests validate hardlink and dry-run accounting. `TestRestorePermissions` checks that `OverwriteIfChanged` and `OverwriteAlways` restore permissions after tampering. Tests create repository snapshots, restore into temp dirs, inspect `os.Stat`/`syscall.Stat_t`, and compare restore UI state.

## State, Persistence, Dependencies, and Integration
State is Unix filesystem metadata and temporary repositories. Dependencies include `repository.TestRepository`, `restoreui.Progress`, and syscall stat data.

## Risks and Test Signals
The signal is strong for Unix metadata integration, but it can vary by filesystem support for sparse blocks and hardlinks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows.go -->
# sources/sync-backup/restic/internal/restorer/restorer_windows.go

## Purpose
Contains Windows-specific filename comparison behavior for restore delete logic.

## Important APIs and Control Flow
The helper normalizes comparable filenames for Windows so delete mode treats names case-insensitively. Control flow is used by `removeUnexpectedFiles` when building expected/actual filename sets.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with restore delete mode and Windows filesystem semantics.

## Risks and Test Signals
Risk is incomplete normalization for unusual Unicode/case-folding behavior; the Windows test suite includes a case-insensitive delete regression test.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows_test.go -->
# sources/sync-backup/restic/internal/restorer/restorer_windows_test.go

## Purpose
Exercises Windows-specific restore behavior for file attributes, directory attributes, overwrites, encrypted files, named streams, and delete case-insensitivity.

## Important APIs and Control Flow
The file defines `FileAttributes`, `NodeInfo`, data-stream helpers, Windows attribute conversion, encrypted-file creation, and verification helpers. Tests generate combinations of readonly/hidden/system/archive/encrypted attributes for files and directories, both fresh and overwritten, then verify restored attributes and content. Control flow builds snapshots with generic Windows attributes, optionally pre-creates destination items with different attributes, restores, and checks Win32 attribute bits via syscall/windows APIs.

## State, Persistence, Dependencies, and Integration
State is Windows filesystem metadata, temporary directories, and synthetic repository snapshots. Dependencies include `data.WindowsAttrsToGenericAttributes`, `golang.org/x/sys/windows`, and restorer snapshot helpers.

## Risks and Test Signals
The suite gives broad Windows metadata coverage. Risks remain around platform privileges, encrypted filesystem support, and combinatorial runtime cost.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/sparsewrite.go -->
# sources/sync-backup/restic/internal/restorer/sparsewrite.go

## Purpose
Overrides `partialFile.WriteAt` to make sparse restore writes skip leading zero data when the file is marked sparse.

## Important APIs and Control Flow
`partialFile.WriteAt` delegates directly to the underlying file for non-sparse files. For sparse files, it computes the longest all-zero prefix with `restic.ZeroPrefixLen`, advances the write offset by that prefix, and writes only the remaining suffix. If the whole buffer is zero, it returns the original length without issuing a write because prior truncation or earlier writes establish the logical zeros.

## State, Persistence, Dependencies, and Integration
Persistent state is the target file's sparse allocation and content. It integrates with `filesWriter.writeToFile`, `truncateSparse`, and the restic zero-prefix helper.

## Risks and Test Signals
Risks are returning a successful byte count without actual writes when file sizing was not prepared correctly, and only skipping leading zeros rather than interior zero ranges. Sparse restore tests validate content and block-count behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/sparsewrite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_other.go -->
# sources/sync-backup/restic/internal/restorer/truncate_other.go

## Purpose
Provides the default sparse truncation implementation for non-Windows platforms.

## Important APIs and Control Flow
`truncateSparse` delegates to file truncation to set logical size while preserving sparseness where the filesystem supports holes. Control flow is a thin platform shim called by `ensureSize` when sparse restore is requested.

## State, Persistence, Dependencies, and Integration
Persistent state is the target file size and sparse allocation. Integration is through `fileswriter.go`.

## Risks and Test Signals
Risks are filesystem-specific sparse behavior and errors from unsupported operations; sparse restore tests provide integration signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_windows.go -->
# sources/sync-backup/restic/internal/restorer/truncate_windows.go

## Purpose
Provides Windows-specific sparse truncation support.

## Important APIs and Control Flow
`truncateSparse` marks the file sparse using Windows control codes before setting the file size. Control flow performs the Windows sparse-file setup, then truncates to the requested logical size.

## State, Persistence, Dependencies, and Integration
Persistent state is the Windows sparse-file attribute and file size. It depends on Windows syscalls and integrates with `fileswriter.go`.

## Risks and Test Signals
Risks are syscall failures on unsupported filesystems or handles; Windows restore tests and cross-platform sparse tests are the relevant signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download.go -->
# sources/sync-backup/restic/internal/selfupdate/download.go

## Purpose
Implements the high-level self-update download, verification, hash checking, archive extraction, and atomic replacement path.

## Important APIs and Control Flow
`findHash`, `extractToFile`, and `DownloadLatestStableRelease` are central. The update flow fetches GitHub latest release metadata, skips if already current, downloads `SHA256SUMS` and its signature, verifies the signature, downloads the platform archive, checks its SHA256, extracts bz2/zip content to a temp file, removes or renames the old binary, atomically renames the new file, and preserves executable mode. Errors abort at every verification or filesystem step. `extractToFile` handles zip archives with exactly one member and bz2/plain data.

## State, Persistence, Dependencies, and Integration
Persistent state is the replaced restic binary and a temporary file in the target directory. Dependencies include GitHub asset helpers, embedded GPG verification, archive readers, SHA256, and platform-specific `removeResticBinary`.

## Risks and Test Signals
Risks are supply-chain critical: signature/hash verification must stay mandatory, zip member assumptions must hold, and binary replacement must be atomic. Tests cover zip extraction and overwrite behavior; GitHub request tests cover auth headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_test.go -->
# sources/sync-backup/restic/internal/selfupdate/download_test.go

## Purpose
Tests archive extraction for self-update on zip input.

## Important APIs and Control Flow
`TestExtractToFileZip` creates an in-memory zip archive with one executable-like file, calls `extractToFile` twice, reads output bytes, and overwrites between runs to verify replacement. Control flow stays local and avoids network/GPG behavior.

## State, Persistence, Dependencies, and Integration
State is a temp directory and generated archive bytes. Dependencies are `archive/zip`, `bytes`, filesystem APIs, and shared test helpers.

## Risks and Test Signals
The test catches extraction and overwrite regressions but does not cover bz2 archives, signature/hash validation, or platform-specific binary removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_unix.go -->
# sources/sync-backup/restic/internal/selfupdate/download_unix.go

## Purpose
Provides Unix self-update removal behavior.

## Important APIs and Control Flow
`removeResticBinary` is a no-op because POSIX systems can rename over an executing binary after the replacement file is ready. Control flow simply returns nil.

## State, Persistence, Dependencies, and Integration
No state is changed in this shim; replacement state is handled by `os.Rename` in `extractToFile`.

## Risks and Test Signals
Risk is platform assumption drift on unusual Unix filesystems, but this is the standard update path for POSIX.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_windows.go -->
# sources/sync-backup/restic/internal/selfupdate/download_windows.go

## Purpose
Provides Windows self-update removal behavior for locked running binaries.

## Important APIs and Control Flow
`removeResticBinary` checks whether the target exists, removes an old `.bak` file if present, then renames the current executable to `<name>.bak` before replacement. Control flow handles missing targets as success and wraps rename failures with a clear error.

## State, Persistence, Dependencies, and Integration
Persistent state may include a `.bak` copy of the previous binary. It integrates with `extractToFile` before final `os.Rename`.

## Risks and Test Signals
Risks are stale backup cleanup failures and locked-file rename behavior. The general extraction test exercises overwrite, while Windows-specific behavior is mainly covered by platform execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github.go -->
# sources/sync-backup/restic/internal/selfupdate/github.go

## Purpose
Implements GitHub release metadata and asset download helpers for self-update.

## Important APIs and Control Flow
`Release`, `Asset`, `newGitHubRequest`, `GitHubLatestRelease`, `getGithubData`, and `getGithubDataFile` are the important APIs. Requests pin Accept headers and optionally add `GITHUB_ACCESS_TOKEN` authorization. `GitHubLatestRelease` uses a 30-second timeout, fetches `/releases/latest`, decodes JSON errors when possible, validates tag names start with `v`, and derives `Version` by trimming the prefix. Asset downloads use octet-stream Accept and suffix matching.

## State, Persistence, Dependencies, and Integration
State is network response data only; no persistence. Dependencies are `net/http`, JSON, environment variables, and GitHub's release API.

## Risks and Test Signals
Risks are API shape/rate-limit changes, leaked or malformed auth headers, missing body close on some non-OK paths, and ambiguous suffix matches. Tests cover request construction with and without tokens.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github_test.go -->
# sources/sync-backup/restic/internal/selfupdate/github_test.go

## Purpose
Tests GitHub request construction for self-update.

## Important APIs and Control Flow
`TestNewGitHubRequest` verifies method, URL, Accept header, and optional Authorization header when `GITHUB_ACCESS_TOKEN` is set or empty. Control flow uses subtests and `t.Setenv` to isolate environment state.

## State, Persistence, Dependencies, and Integration
No persistent state. Dependencies include `net/http` constants and shared test assertions.

## Risks and Test Signals
The test catches auth/header regressions but does not mock full GitHub release or asset download responses.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/verify.go -->
# sources/sync-backup/restic/internal/selfupdate/verify.go

## Purpose
Verifies detached GPG signatures for self-update metadata using an embedded public key.

## Important APIs and Control Flow
The file embeds the restic release signing key and exposes `GPGVerify(data, sig)`, which parses the keyring and signature and checks that the signature was made by a trusted embedded key. Control flow builds OpenPGP entities from the key material, verifies the signature against the supplied data, and returns `(ok,error)` instead of panicking.

## State, Persistence, Dependencies, and Integration
State is static embedded key text plus transient verification objects. It depends on OpenPGP packages and is called by `DownloadLatestStableRelease` before trusting `SHA256SUMS`.

## Risks and Test Signals
Risk is high because update authenticity depends on this path; stale/revoked keys or weakened OpenPGP dependencies would affect updates. Coverage is mostly integration through self-update flow rather than extensive unit tests in this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/verify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix.go -->
# sources/sync-backup/restic/internal/terminal/background_unix.go

## Purpose
Detects whether the current process is running in the background on Unix terminals.

## Important APIs and Control Flow
`IsProcessBackground` wraps `isProcessBackground`; the internal helper compares the terminal foreground process group from `tcgetpgrp(fd)` with `getpgrp()`. Errors are logged and treated as foreground/default behavior to avoid blocking normal operation.

## State, Persistence, Dependencies, and Integration
No persistent state. It depends on terminal process-group syscalls and `debug.Log`, and integrates with terminal prompt/status behavior.

## Risks and Test Signals
Risks are syscall failures in non-interactive sessions and incorrect defaults for background jobs. The Unix test opens `/dev/tty` when available and verifies the helper returns without error.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix_test.go -->
# sources/sync-backup/restic/internal/terminal/background_unix_test.go

## Purpose
Tests Unix background-process detection against the controlling terminal when one exists.

## Important APIs and Control Flow
`TestIsProcessBackground` opens `/dev/tty`, skips if unavailable, calls `isProcessBackground`, and asserts no error. Control flow avoids asserting foreground/background status because that depends on the test runner.

## State, Persistence, Dependencies, and Integration
State is the opened tty descriptor. Dependencies are OS terminal availability and shared test helpers.

## Risks and Test Signals
The test catches syscall integration failures but not actual background-job transitions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_windows.go -->
# sources/sync-backup/restic/internal/terminal/background_windows.go

## Purpose
Provides the Windows implementation of background-process detection.

## Important APIs and Control Flow
`IsProcessBackground` always returns false because Unix process-group foreground/background semantics are not implemented here. There is no control flow beyond returning the safe default.

## State, Persistence, Dependencies, and Integration
No state is stored. It keeps shared terminal code portable on Windows.

## Risks and Test Signals
Risk is that Windows shells with similar concepts are ignored; callers should treat this as best-effort behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground.go -->
# sources/sync-backup/restic/internal/terminal/foreground.go

## Purpose
Provides the public entry point for running an external command in the foreground while scrubbing restic secrets from the environment.

## Important APIs and Control Flow
`StartForeground` removes all `RESTIC_*` variables from `cmd.Env` and delegates to platform-specific `startForeground`. Control flow copies `os.Environ`, filters sensitive variables, then starts foreground handling.

## State, Persistence, Dependencies, and Integration
State mutation is limited to the supplied `exec.Cmd`. Integration points are backend commands that need terminal foreground control and safe environment inheritance.

## Risks and Test Signals
Risks are missed secret environment prefixes and platform-specific foreground failures. Tests verify `RESTIC_PASSWORD` is not visible to a subprocess.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_test.go -->
# sources/sync-backup/restic/internal/terminal/foreground_test.go

## Purpose
Tests that foreground command execution scrubs restic environment variables.

## Important APIs and Control Flow
`TestForeground` sets `RESTIC_PASSWORD`, runs `env` through `StartForeground`, switches back via the returned function, then scans stdout for leaked password variables. Control flow waits for the command and checks scanner output.

## State, Persistence, Dependencies, and Integration
State is process environment and subprocess stdout. The test is non-Windows and depends on shell utilities.

## Risks and Test Signals
The signal is focused on secret hygiene; it does not fully validate process-group behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_unix.go -->
# sources/sync-backup/restic/internal/terminal/foreground_unix.go

## Purpose
Implements Unix foreground process handling for subprocesses.

## Important APIs and Control Flow
`startForeground` sets the child in its own process group, opens `/dev/tty`, checks restic owns the foreground, ignores `SIGTTIN`/`SIGTTOU`, starts the command, moves the child process group to the foreground, and returns a cleanup function that restores the previous process group and signal handling. If `/dev/tty` is unavailable or restic is not foreground, it falls back to plain `cmd.Start`.

## State, Persistence, Dependencies, and Integration
State includes terminal foreground process group and process signal dispositions during the child run. Dependencies are `golang.org/x/sys/unix`, `tcgetpgrp`, `tcsetpgrp`, and `os/signal`.

## Risks and Test Signals
Risks are leaving terminal process groups or signals in a bad state on errors. The foreground environment test covers public behavior; direct process-group behavior is mainly exercised manually/implicitly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_windows.go -->
# sources/sync-backup/restic/internal/terminal/foreground_windows.go

## Purpose
Implements Windows foreground command handling.

## Important APIs and Control Flow
`startForeground` starts the command using Windows process attributes and returns a no-op background restoration function. Control flow is intentionally simpler than Unix because Windows does not use POSIX terminal process groups.

## State, Persistence, Dependencies, and Integration
State is the spawned process configured through `exec.Cmd`/Windows syscall attributes. Integration is through `StartForeground` after environment scrubbing.

## Risks and Test Signals
Risks are Windows console control behavior and command start errors; there is no dedicated Windows foreground test in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/foreground_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_solaris.go -->
# sources/sync-backup/restic/internal/terminal/getpgrp_solaris.go

## Purpose
Provides Solaris-specific process group lookup.

## Important APIs and Control Flow
`getpgrp` calls the Solaris-compatible syscall variant needed by terminal foreground/background code. Control flow is a thin syscall wrapper.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with Unix terminal process-group comparisons.

## Risks and Test Signals
Risk is platform syscall drift; coverage is compile/platform based.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_solaris.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_unix.go -->
# sources/sync-backup/restic/internal/terminal/getpgrp_unix.go

## Purpose
Provides the default Unix process group lookup.

## Important APIs and Control Flow
`getpgrp` returns the current process group using the platform syscall. Control flow is a thin wrapper used by background and foreground terminal code.

## State, Persistence, Dependencies, and Integration
No persistent state. It is selected for Unix platforms except special cases such as Solaris.

## Risks and Test Signals
Risk is limited to platform compatibility; behavior is indirectly tested by terminal Unix tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/getpgrp_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/password.go -->
# sources/sync-backup/restic/internal/terminal/password.go

## Purpose
Implements terminal password reading support.

## Important APIs and Control Flow
The file provides password prompt/read helpers that use raw terminal input where possible and respect context cancellation. Control flow prompts on the terminal, reads without echo through terminal APIs, and returns password text or errors.

## State, Persistence, Dependencies, and Integration
State is transient terminal mode/input data; no password is persisted. Integration is with the `Terminal` abstraction used by commands needing repository passwords.

## Risks and Test Signals
Risks are echo leakage, hanging reads under cancellation, and non-terminal input behavior. Tests for terminal abstractions and UI mocks provide indirect coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/password.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/stdio.go -->
# sources/sync-backup/restic/internal/terminal/stdio.go

## Purpose
Defines standard input/output handles used by terminal implementations.

## Important APIs and Control Flow
The file exposes process stdio variables/wrappers so terminal code can be tested or swapped consistently. Control flow is minimal; these handles are consumed by terminal construction and prompt/status output.

## State, Persistence, Dependencies, and Integration
State is the process stdio descriptors. Integration is with password reading, foreground/background checks, and UI terminal output.

## Risks and Test Signals
Risks are global handle mutation in tests and redirected stdio behavior; platform terminal tests cover update capability separately.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/stdio.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_linux.go -->
# sources/sync-backup/restic/internal/terminal/tcgetpgrp_linux.go

## Purpose
Provides Linux-specific `tcgetpgrp` implementation.

## Important APIs and Control Flow
`tcgetpgrp(fd)` calls the appropriate ioctl/syscall to read the foreground process group for a terminal descriptor. It returns the process group ID or an error to callers in background/foreground logic.

## State, Persistence, Dependencies, and Integration
No persistent state. It integrates with `IsProcessBackground` and Unix `startForeground`.

## Risks and Test Signals
Risks are ioctl portability and descriptor validity. Unix terminal tests exercise the call when `/dev/tty` is available.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_unix.go -->
# sources/sync-backup/restic/internal/terminal/tcgetpgrp_unix.go

## Purpose
Provides the default Unix `tcgetpgrp` implementation for non-Linux Unix platforms.

## Important APIs and Control Flow
`tcgetpgrp` wraps the platform terminal ioctl for foreground process-group lookup. Control flow is a syscall wrapper returning process group ID and errors.

## State, Persistence, Dependencies, and Integration
No persistent state. It supports terminal foreground/background code on BSD-like systems.

## Risks and Test Signals
Risk is platform ioctl incompatibility; coverage is build/platform based.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcgetpgrp_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_aix.go -->
# sources/sync-backup/restic/internal/terminal/tcsetpgrp_aix.go

## Purpose
Provides AIX-specific foreground process-group assignment.

## Important APIs and Control Flow
`tcsetpgrp(fd,pid)` wraps the AIX terminal control operation required by `startForeground`. Control flow is a thin platform syscall adapter.

## State, Persistence, Dependencies, and Integration
No state beyond changing the terminal foreground process group. Integration is Unix foreground command execution.

## Risks and Test Signals
Risks are terminal state restoration failures and platform syscall differences; coverage is platform compile/runtime based.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_aix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_unix.go -->
# sources/sync-backup/restic/internal/terminal/tcsetpgrp_unix.go

## Purpose
Provides the default Unix foreground process-group assignment.

## Important APIs and Control Flow
`tcsetpgrp(fd,pid)` wraps the terminal ioctl/syscall used to move a process group into the foreground. It is called after starting the child and again in the cleanup closure to restore restic's process group.

## State, Persistence, Dependencies, and Integration
The persistent side effect is terminal foreground ownership until restored. It integrates with `foreground_unix.go`.

## Risks and Test Signals
Risks are leaving the terminal attached to the wrong group on error; foreground tests only cover the public path lightly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/tcsetpgrp_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_posix.go -->
# sources/sync-backup/restic/internal/terminal/terminal_posix.go

## Purpose
Implements POSIX escape-sequence helpers for terminal status updates.

## Important APIs and Control Flow
`PosixClearCurrentLine`, cursor-home/up/down constants, and movement helpers write ANSI control sequences to an `io.Writer`. Control flow writes clear/move sequences and can be selected on POSIX terminals or mintty-like Windows pipes.

## State, Persistence, Dependencies, and Integration
State is terminal cursor/display state, not application persistence. It integrates with UI status rendering.

## Risks and Test Signals
Risks are escape sequences going to non-terminal outputs and display corruption if width/cursor assumptions are wrong.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_posix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_unix.go -->
# sources/sync-backup/restic/internal/terminal/terminal_unix.go

## Purpose
Selects terminal status update behavior on Unix.

## Important APIs and Control Flow
Unix implementations use POSIX clear/move helpers and terminal capability checks for whether status can be updated. Control flow is mostly platform dispatch around file descriptors and terminal detection.

## State, Persistence, Dependencies, and Integration
State is terminal display/cursor state. It integrates with UI progress printers that call `SetStatus`.

## Risks and Test Signals
Risks are redirected output and terminal detection mistakes; Windows has more specialized pipe detection tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows.go -->
# sources/sync-backup/restic/internal/terminal/terminal_windows.go

## Purpose
Implements Windows console and mintty-aware terminal status operations.

## Important APIs and Control Flow
`ClearCurrentLine`, `MoveCursorUp`, and `MoveCursorDown` choose native Windows console APIs or POSIX escape functions based on `isWindowsTerminal`. `CanUpdateStatus` returns true for native terminals and mintty/cygwin pty master pipes detected through handle names. Native clear/move functions call `GetConsoleScreenBufferInfo`, `FillConsoleOutput*`, and `SetConsoleCursorPosition`.

## State, Persistence, Dependencies, and Integration
State is terminal cursor and screen buffer contents. Dependencies are `golang.org/x/sys/windows`, `golang.org/x/term`, and kernel32 procedures.

## Risks and Test Signals
Risks are unsafe syscall argument handling, false positives for pipe terminal detection, and output corruption. Tests cover mintty pty-vs-pipe detection.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows_test.go -->
# sources/sync-backup/restic/internal/terminal/terminal_windows_test.go

## Purpose
Tests Windows mintty/cygwin pipe detection for status updates.

## Important APIs and Control Flow
`TestIsMinTTY` creates named pipes with pty-master and ordinary pipe names, then asserts `CanUpdateStatus` returns true only for the pty form. Control flow uses Windows named-pipe creation and closes handles after assertions.

## State, Persistence, Dependencies, and Integration
State is OS pipe handles. Dependencies are Windows syscalls and shared test helpers.

## Risks and Test Signals
The test catches regressions in filename pattern detection but not native console cursor movement.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/terminal_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/test/doc.go -->
# sources/sync-backup/restic/internal/test/doc.go

## Purpose
Documents the shared `internal/test` helper package.

## Important APIs and Control Flow
The package comment states that the package provides helper functions for restic tests. No executable control flow is present.

## State, Persistence, Dependencies, and Integration
No state is stored. It integrates with tests throughout the repository via concise assertion and fixture helpers.

## Risks and Test Signals
Risk is documentation drift only; functional behavior is in `helpers.go` and `vars.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/test/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/test/helpers.go -->
# sources/sync-backup/restic/internal/test/helpers.go

## Purpose
Provides shared test assertions, deterministic random data, fixture extraction, temp directory handling, read-only cleanup, and working-directory helpers.

## Important APIs and Control Flow
`Assert`, `OK`, `OKs`, `Equals`, `Random`, `SetupTarTestFixture`, `Env`, `RemoveAll`, `TempDir`, and `Chdir` are widely used by restic tests. Control flow favors fail-fast `testing.TB` helpers, deterministic pseudo-random generation, tar extraction via external `tar`, and cleanup that resets readonly permissions before removal.

## State, Persistence, Dependencies, and Integration
State includes temporary directories, current working directory changes, and environment-derived settings from `vars.go`; no project data is persisted unless cleanup is disabled.

## Risks and Test Signals
Risks are external `tar` dependency, global cwd mutation, and cleanup behavior on Windows readonly files. The helpers are indirectly tested by broad repository test usage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/test/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/test/vars.go -->
# sources/sync-backup/restic/internal/test/vars.go

## Purpose
Centralizes environment-controlled test configuration.

## Important APIs and Control Flow
Package variables read `RESTIC_TEST_PASSWORD`, cleanup/tempdir flags, integration/FUSE toggles, SFTP path, benchmark directory, and disallow-skip behavior via `getStringVar`/`getBoolVar`. Control flow parses environment values at package initialization, with boolean parsing/fatal behavior handled by helper functions.

## State, Persistence, Dependencies, and Integration
State is process-global test configuration for the test binary. It integrates with repository, backend, FUSE, and integration tests.

## Risks and Test Signals
Risks are surprising global state from environment variables and tests changing behavior across machines. The signal is operational rather than unit-tested: many tests rely on these variables.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/test/vars.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read.go -->
# sources/sync-backup/restic/internal/textfile/read.go

## Purpose
Reads text files while normalizing byte-order marks and UTF-16 encodings to UTF-8 bytes.

## Important APIs and Control Flow
`Decode` detects UTF-16 BOMs and decodes little/big endian content; `Read` loads a file then decodes it. Control flow checks known BOM prefixes, transforms with unicode decoders when needed, and returns original data when no BOM is present.

## State, Persistence, Dependencies, and Integration
State is transient byte slices. Dependencies include text encoding packages and `os.ReadFile`; integration is with config/list files that may come from Windows editors.

## Risks and Test Signals
Risks are unsupported encodings and malformed UTF-16 handling. Tests cover plain UTF-8, BOM variants, invalid data, empty files, and file read behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read_test.go -->
# sources/sync-backup/restic/internal/textfile/read_test.go

## Purpose
Tests textfile decoding and file reading across encodings.

## Important APIs and Control Flow
Helpers create temp files and decode hex fixtures. `TestRead` covers plain text, UTF-8 BOM, UTF-16 little/big endian BOMs, invalid/truncated inputs, and file read paths. Control flow writes fixtures, calls `Decode`/`Read`, and compares bytes or expected errors.

## State, Persistence, Dependencies, and Integration
State is temporary files and test byte slices. Dependencies include shared test helpers and encoding fixtures.

## Risks and Test Signals
The tests provide good coverage for BOM detection and decode errors, though not every possible Unicode normalization edge case.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/textfile/read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json.go -->
# sources/sync-backup/restic/internal/ui/backup/json.go

## Purpose
Implements JSON progress output for the backup command.

## Important APIs and Control Flow
`jsonProgress` embeds a terminal `progress.Printer` and implements `ProgressPrinter`: `Update`, `ScannerError`, `Error`, `CompleteItem`, `ReportTotal`, `Finish`, and `Reset`. It emits JSON `status`, `error`, `verbose_status`, and `summary` objects. Control flow formats status from total/processed counters, sorts current filenames for deterministic output, maps archiver item message types to JSON actions, suppresses verbose item output below verbosity 2, and renders final backup summary including snapshot ID and dry-run flag.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity. Dependencies are archiver stats, restic IDs, UI JSON formatting, and progress terminal printing.

## Risks and Test Signals
Risks are JSON contract drift and incorrect message-type mapping. Tests cover error and scanner-error JSON escaping; broader progress tests cover state feeding.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json_test.go -->
# sources/sync-backup/restic/internal/ui/backup/json_test.go

## Purpose
Tests backup JSON error output.

## Important APIs and Control Flow
`createJSONProgress` builds a `MockTerminal` with verbosity 3. `TestJSONError` and `TestJSONScannerError` verify archival and scan errors are emitted as expected JSON with escaped quotes. Control flow calls printer methods directly and compares captured terminal errors.

## State, Persistence, Dependencies, and Integration
State is mock terminal output. Dependencies include `internal/errors`, `internal/test`, and `ui.MockTerminal`.

## Risks and Test Signals
The tests strongly cover error JSON formatting but do not cover status, verbose item, or summary JSON from this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/json_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress.go -->
# sources/sync-backup/restic/internal/ui/backup/progress.go

## Purpose
Tracks backup progress state and feeds periodic updates to a backup progress printer.

## Important APIs and Control Flow
`ProgressPrinter`, `Counter`, `Progress`, `NewProgress`, `newProgress`, `Error`, `StartFile`, `CompleteBlob`, `CompleteItem`, `ReportTotal`, and `Finish` are central. `Progress` protects state with a mutex and embeds `progress.Updater` for timed/signal updates. Control flow starts updates only after scanning begins, estimates remaining seconds after scan completion using `rateEstimator`, tracks current files, increments processed file/dir/blob counters, maps archiver previous/current nodes to new/unchanged/modified item messages, and stops the updater before final summary.

## State, Persistence, Dependencies, and Integration
State includes start time, rate estimator buckets, scan flags, current file set, counters, error count, and printer. Dependencies include archiver/data node stats and UI progress infrastructure.

## Risks and Test Signals
Risks include races in concurrent archiver callbacks, inaccurate remaining-time estimates, and stale current-file entries after errors. Tests exercise state transitions for files, dirs, blobs, errors, totals, and finish behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress_test.go -->
# sources/sync-backup/restic/internal/ui/backup/progress_test.go

## Purpose
Tests backup progress state transitions with a mock printer.

## Important APIs and Control Flow
`mockPrinter` records selected messages and final snapshot ID. `TestProgress` starts a file, completes blobs/items, reports totals, handles errors, and finishes to verify expected printer calls and state updates. Control flow uses a short update interval and explicit method calls rather than running a full backup.

## State, Persistence, Dependencies, and Integration
State is mock-printer fields protected by a mutex plus progress counters. Dependencies include archiver/data node types and noop progress printer.

## Risks and Test Signals
The test catches callback mapping and finish regressions but does not deeply test periodic timing or JSON/text output.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator.go -->
# sources/sync-backup/restic/internal/ui/backup/rate_estimator.go

## Purpose
Estimates recent backup throughput for remaining-time calculation.

## Important APIs and Control Flow
`rateEstimator` uses a ring/bucket model over time; `newRateEstimator`, `recordBytes`, `rate`, and bucket-width logic track bytes over recent intervals. Control flow advances buckets as time moves forward, adds completed bytes to the current bucket, and computes a bytes-per-second rate over populated buckets.

## State, Persistence, Dependencies, and Integration
State is in-memory time buckets and last-update timestamps. Integration is with `backup.Progress` after scan completion.

## Risks and Test Signals
Risks are responsiveness versus stability tradeoffs and edge cases at bucket boundaries. Tests cover default rate, simple rates, bucket width, and responsiveness to changing throughput.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator_test.go -->
# sources/sync-backup/restic/internal/ui/backup/rate_estimator_test.go

## Purpose
Tests backup throughput estimation behavior.

## Important APIs and Control Flow
The suite defines approximate float comparison and chunk application helpers. Tests cover zero/default rates, simple byte/time examples, bucket-width selection, and estimator responsiveness across bursts and idle periods. Control flow advances synthetic timestamps and records byte chunks into an estimator.

## State, Persistence, Dependencies, and Integration
State is deterministic test time and estimator buckets. Dependencies are standard time/testing only.

## Risks and Test Signals
The tests provide strong deterministic coverage for rate math, but real-world timing jitter is only indirectly represented.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/rate_estimator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text.go -->
# sources/sync-backup/restic/internal/ui/backup/text.go

## Purpose
Implements human-readable backup progress output.

## Important APIs and Control Flow
`textProgress` implements `ProgressPrinter` with terminal status lines, verbose item output, scanner/archive errors, totals, summaries, and reset behavior. Control flow formats bytes, percentages, durations, current files, and summary counts; verbosity controls detailed per-item output through the embedded terminal printer.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity through `progress.NewTerminalPrinter`. It depends on UI formatting helpers, archiver stats, restic IDs, and terminal status capability.

## Risks and Test Signals
Risks are formatting regressions and output that does not fit terminal widths. Tests cover scanner/archive error strings, while progress and formatting tests cover related state/format helpers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text_test.go -->
# sources/sync-backup/restic/internal/ui/backup/text_test.go

## Purpose
Tests text backup error output.

## Important APIs and Control Flow
`createTextProgress` builds a text printer backed by `MockTerminal`. `TestError` and `TestScannerError` verify archival and scan errors are printed in the expected human-readable form. Control flow calls printer methods directly and compares captured mock output.

## State, Persistence, Dependencies, and Integration
State is mock terminal output. Dependencies are shared test helpers and `internal/errors`.

## Risks and Test Signals
Coverage is focused on error text; full status and summary formatting is mainly exercised indirectly and through common UI format tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/text_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format.go -->
# sources/sync-backup/restic/internal/ui/format.go

## Purpose
Provides shared UI formatting/parsing helpers for sizes, percentages, durations, JSON, display widths, quoting, and truncation.

## Important APIs and Control Flow
`FormatBytes`, `FormatPercent`, `FormatDuration`, `FormatSeconds`, `ParseBytes`, `ToJSONString`, `DisplayWidth`, `Quote`, `Truncate`, and `wideRune` are central. The functions format binary units, clamp percentages at 100%, parse B/K/M/G/T suffixes with overflow checks, JSON-encode statuses, and handle terminal cell widths for Unicode. Control flow is deterministic formatting/parsing with early returns for zero denominators, invalid sizes, non-printable strings, and width overflow.

## State, Persistence, Dependencies, and Integration
No persistent state. Dependencies include JSON, `math/bits`, `strconv`, Unicode helpers, and `golang.org/x/text/width`; integration spans backup/restore text and JSON printers.

## Risks and Test Signals
Risks are terminal width ambiguity, overflow parsing, invalid UTF-8 quoting, and truncating within multi-byte runes. Tests cover bytes, percentages, parsing invalid/valid sizes, display width, quote, truncate, and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format_test.go -->
# sources/sync-backup/restic/internal/ui/format_test.go

## Purpose
Tests and benchmarks UI formatting helpers.

## Important APIs and Control Flow
Tests cover byte formatting thresholds, percentage formatting, byte parsing with suffixes and overflow/invalid cases, display width for ASCII/Unicode, quoting of control and invalid text, and truncation across ASCII and wide runes. Benchmarks measure truncate performance. Control flow is table-driven with shared equality assertions.

## State, Persistence, Dependencies, and Integration
State is local test cases only. Dependencies include Unicode fixtures and shared test helpers.

## Risks and Test Signals
The suite is strong for formatting edge cases, though terminal font ambiguity means exact real display width can still vary.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/format_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/mock.go -->
# sources/sync-backup/restic/internal/ui/mock.go

## Purpose
Provides a test/mock implementation of the UI `Terminal` interface.

## Important APIs and Control Flow
`MockTerminal` records `Print`, `Error`, and `SetStatus` output slices and implements terminal input/output capability methods, password reading, and raw writers. Control flow appends strings to fields or returns fixed terminal capability values suitable for unit tests.

## State, Persistence, Dependencies, and Integration
State is in-memory captured output/errors/status. It integrates with backup/restore JSON/text printer tests.

## Risks and Test Signals
Risks are mock behavior diverging from real terminal status behavior; its test signal comes from widespread use in UI unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/mock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter.go -->
# sources/sync-backup/restic/internal/ui/progress/counter.go

## Purpose
Implements a concurrency-safe progress counter backed by the shared updater goroutine.

## Important APIs and Control Flow
`Counter` embeds `Updater`, stores atomic value/max fields, and implements `restic.Counter`. `NewCounter` wires an update callback that reads `Get`; `Add`, `SetMax`, `Get`, and inherited `Done` are safe for concurrent callers. Control flow reports periodically or on signals via `Updater`, and performs a final callback on `Done`.

## State, Persistence, Dependencies, and Integration
State is in-memory atomic counters and updater goroutine state. It integrates core restic counters with UI progress rendering.

## Risks and Test Signals
Risks are goroutine leaks if `Done` is not called and races around final reporting. Tests cover increment/max/report behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter_test.go -->
# sources/sync-backup/restic/internal/ui/progress/counter_test.go

## Purpose
Tests the progress counter implementation.

## Important APIs and Control Flow
`TestCounter` creates a counter with a reporting callback, adds values, changes max, and verifies reported value/max/final state after `Done`. Control flow uses short intervals and direct method calls.

## State, Persistence, Dependencies, and Integration
State is local callback-captured progress. Dependencies are the progress package and testing helpers.

## Risks and Test Signals
The test catches basic counter/update behavior but is intentionally light on timing races.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/counter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/printer.go -->
# sources/sync-backup/restic/internal/ui/progress/printer.go

## Purpose
Defines the generic progress printer interface used by commands and provides a no-op implementation.

## Important APIs and Control Flow
`Printer` includes counter creation and severity/verbosity printing methods; `NewNoopPrinter` returns a `noopPrinter` whose methods discard output and counters use core no-op counters. Control flow is interface dispatch only; no-op methods intentionally do nothing.

## State, Persistence, Dependencies, and Integration
No persistent state. It decouples command code from terminal-specific printers and lets tests disable output.

## Risks and Test Signals
Risks are interface drift and nil/no-op behavior hiding missing output in tests. Compile-time conformance and UI tests provide signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/printer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/terminal.go -->
# sources/sync-backup/restic/internal/ui/progress/terminal.go

## Purpose
Adapts the generic progress printer interface to a real UI terminal.

## Important APIs and Control Flow
`CalculateProgressInterval`, `newProgressMax`, `terminalPrinter`, and `NewTerminalPrinter` handle update cadence, progress counter creation, terminal-only counters, errors/status/print output, and verbosity levels. Control flow disables periodic status for quiet output, uses JSON-aware behavior to avoid mixed terminal status, and routes `E`, `S`, `PT`, `P`, `V`, and `VV` according to verbosity and terminal capabilities.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity. Dependencies include core restic counters, UI terminal abstraction, and `progress.Counter`.

## Risks and Test Signals
Risks are noisy output in JSON mode, incorrect interval choices, and verbosity regressions. Tests for backup/restore printers and updater/counter cover the main integration paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/terminal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater.go -->
# sources/sync-backup/restic/internal/ui/progress/updater.go

## Purpose
Runs periodic and signal-triggered progress callbacks.

## Important APIs and Control Flow
`Updater`, `UpdateFunc`, `NewUpdater`, `Done`, and `run` manage a goroutine, optional ticker, stop/stopped channels, runtime measurement, and SIGUSR1/SIGINFO-triggered reports. Control flow selects between ticker, progress signal channel, and stop; `Done` stops the ticker, closes the stop channel, waits for the final callback, and is idempotent for later calls.

## State, Persistence, Dependencies, and Integration
State is goroutine/channel/ticker state and start time. Dependencies include `internal/ui/signals` and debug logging.

## Risks and Test Signals
Risks are goroutine leaks, double-close panics, and final-update races. Tests cover normal updates, double `Done`, and no-tick operation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater_test.go -->
# sources/sync-backup/restic/internal/ui/progress/updater_test.go

## Purpose
Tests updater lifecycle behavior.

## Important APIs and Control Flow
`TestUpdater` verifies callbacks happen and final reporting occurs; `TestUpdaterStopTwice` checks `Done` idempotence; `TestUpdaterNoTick` verifies an updater with zero interval still reports on final stop. Control flow uses short intervals and callback traces.

## State, Persistence, Dependencies, and Integration
State is local counters/channels in tests. Dependencies are the progress package and testing timeouts.

## Risks and Test Signals
The tests catch lifecycle regressions but cannot exhaustively prove timing behavior under scheduler delays.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/progress/updater_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json.go -->
# sources/sync-backup/restic/internal/ui/restore/json.go

## Purpose
Implements JSON progress output for restore operations.

## Important APIs and Control Flow
`jsonPrinter` implements restore `ProgressPrinter`: `Update`, `Error`, `CompleteItem`, and `Finish`. It emits JSON `status`, `error`, `verbose_status`, and `summary` objects. Control flow maps restore `State` fields to JSON counters, computes percent when total bytes are known, maps `ItemAction` values to actions, suppresses verbose item messages below verbosity 3, and emits restore errors as non-fatal JSON errors.

## State, Persistence, Dependencies, and Integration
State is terminal reference and verbosity. Dependencies are UI JSON formatting and generic progress terminal printing.

## Risks and Test Signals
Risks are JSON schema drift and panics on unknown item actions. Tests cover update, skipped files, summaries, complete-item actions, and error JSON.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json_test.go -->
# sources/sync-backup/restic/internal/ui/restore/json_test.go

## Purpose
Tests restore JSON progress output.

## Important APIs and Control Flow
The tests build a `MockTerminal` JSON printer and assert exact JSON strings for status updates, skipped counters, successful/error summaries, verbose complete-item actions, and error output. Control flow calls printer methods directly with representative `State` values and item actions.

## State, Persistence, Dependencies, and Integration
State is captured mock terminal output and errors. Dependencies are shared test helpers and UI mocks.

## Risks and Test Signals
Coverage is strong for output contract stability, though exact floating-point percent text remains part of the contract.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/json_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress.go -->
# sources/sync-backup/restic/internal/ui/restore/progress.go

## Purpose
Tracks restore progress state and coordinates periodic/final restore progress printing.

## Important APIs and Control Flow
`State`, `Progress`, `ProgressPrinter`, `ItemAction` constants, `NewProgress`, `newProgress`, `update`, `AddFile`, `AddProgress`, `AddSkippedFile`, `ReportDeletion`, `Error`, and `Finish` are central. It records per-file partial progress to avoid double-counting and emits completed item events once total bytes are reached. Control flow creates an updater using UI interval rules, updates state under a mutex, adds skipped/deleted counters immediately, proxies errors to the printer, and stops with a final summary in `Finish`.

## State, Persistence, Dependencies, and Integration
State includes progress map, aggregate counters, start time, printer, and updater goroutine. Integration is with `Restorer` and `fileRestorer` progress callbacks.

## Risks and Test Signals
Risks include double-counting repeated blob updates, missing completion events for zero-size items, and races with concurrent restore workers. Tests cover add/progress/finish/error/skipped/deleted/action behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress_test.go -->
# sources/sync-backup/restic/internal/ui/restore/progress_test.go

## Purpose
Tests restore progress accounting and printer callbacks.

## Important APIs and Control Flow
Mock printer traces updates, completed items, and errors. Tests cover creation, adding files, first/last progress on a file, completion of the last file, success/error summaries, skipped files, action types including deletion, and error forwarding. Control flow drives `Progress` directly and inspects captured traces after optional `Finish`.

## State, Persistence, Dependencies, and Integration
State is in-memory trace slices and progress maps. Dependencies are restore progress types and shared test helpers.

## Risks and Test Signals
The suite strongly guards aggregate counters and item completion semantics, but timing behavior is intentionally controlled rather than real-time.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/progress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text.go -->
# sources/sync-backup/restic/internal/ui/restore/text.go

## Purpose
Implements human-readable restore progress output.

## Important APIs and Control Flow
`textPrinter` implements `Update`, `Error`, `CompleteItem`, and `Finish` using UI formatting helpers and verbosity-aware terminal printing. Control flow builds a single status line with duration, percent, files/dirs, byte totals, skipped and deleted counts; complete-item output maps restore actions to readable verbs; finish clears status and prints success or partial summary.

## State, Persistence, Dependencies, and Integration
State is terminal reference. Dependencies are UI byte/percent/duration formatters and generic terminal printer behavior.

## Risks and Test Signals
Risks are formatting drift and output that is hard to scan for large paths. Tests assert status, summaries, skipped output, complete-item text, and error handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text_test.go -->
# sources/sync-backup/restic/internal/ui/restore/text_test.go

## Purpose
Tests restore text progress output.

## Important APIs and Control Flow
The tests use `MockTerminal` and assert exact output for status updates, skipped counters, success/error summaries, skipped summaries, complete-item action strings, and restore errors. Control flow calls text printer methods directly with representative state and actions.

## State, Persistence, Dependencies, and Integration
State is captured mock terminal output/errors. Dependencies are shared test helpers and UI mocks.

## Risks and Test Signals
Coverage is strong for current text contracts; real terminal width/status behavior is covered indirectly by terminal/progress code.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/restore/text_test.go -->
