# Group Research: subset-b-000081

This grouped report covers the exact source files assigned to work item `subset-b-000081`. Each section is delimited for deterministic reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_test.go -->
# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_test.go

## Purpose
This test file validates the cross-platform raw file-locking primitive exposed by the `internal/rawfilelock` package. It exercises `OpenLock`, `TryLockFile`, `LockFile`, and `UnlockAndCloseHandle` through realistic filesystem paths rather than mocking the platform-specific implementations.

## Important APIs and Behavior Covered
The central tests are `TestOpenLock`, `TestOpenLockNotCreateParentDir`, and `TestTryLockFileAndLockFile`. `TestOpenLock` verifies that `OpenLock` can open an existing lock file in read-write and read-only modes, and can create a new lock file when its parent directory already exists. `TestOpenLockNotCreateParentDir` defines an important boundary: `OpenLock` creates the lock file itself but does not create missing parent directories. `TestTryLockFileAndLockFile` covers both nonblocking and blocking lock acquisition on file handles returned by `OpenLock`.

## Control Flow and State
Each test creates temporary files or paths, calls `OpenLock`, then closes handles through `UnlockAndCloseHandle`. The tests intentionally reopen the same path after unlocking to prove that handle close releases the OS lock and that subsequent opens are usable. Cleanup is done with `os.RemoveAll` or temporary directory lifetime.

## Dependencies and Integration Points
The tests depend on `os`, `filepath`, Go's `testing`, and `testify/require`. They indirectly validate the platform files `rawfilelock_unix.go` and `rawfilelock_windows.go`, plus the shared wrapper in `rawfilelock.go`. Higher-level packages such as `internal/staging_lockfile` depend on this behavior for safe staging/tempdir cleanup.

## Risks and Edge Cases
The tests do not prove multi-process exclusion; that is covered at the `staging_lockfile` layer. They also do not exercise read-lock versus write-lock compatibility, lock reentrancy, or Windows panic behavior for blocking lock failures. The parent-directory test is important because callers must create parent directories before asking rawfilelock to create/open a file.

## Test Signals
Strong signals: open/reopen behavior, read-only mode, no implicit parent creation, and both lock entry points. Missing signals: contention, stale handles, EINTR/retry behavior on Unix, and Windows `LockFileEx` failure modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_unix.go -->
# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_unix.go

## Purpose
This Unix-only implementation provides the OS-specific file descriptor operations backing `internal/rawfilelock`. It wraps `unix.Open`, `unix.FcntlFlock`, and `unix.Close` behind the shared `fileHandle`, `openHandle`, `lockHandle`, `unlockAndCloseHandle`, and `closeHandle` functions.

## Important APIs and Functions
`type fileHandle uintptr` stores a Unix file descriptor. `openHandle(path, mode)` adds `O_CLOEXEC`, opens the path with mode `0644`, and returns the descriptor. `lockHandle(fd, lType, nonblocking)` maps `ReadLock` to `F_RDLCK` and everything else to `F_WRLCK`, prepares a whole-file `Flock_t` with `Len: 0`, and uses `F_SETLK` for nonblocking locks or `F_SETLKW` for blocking locks. `unlockAndCloseHandle` and `closeHandle` both call `unix.Close`.

## Control Flow and State
The blocking path loops until `FcntlFlock` succeeds; if a blocking call returns an error, it sleeps for 10 ms and retries. The nonblocking path returns the first result directly. There is no explicit unlock call before close because POSIX advisory locks are released by closing the descriptor. Persistent state is the lock file itself; active state is entirely in the open descriptor and kernel lock table.

## Dependencies and Integration Points
The file imports `time` and `golang.org/x/sys/unix`. It is called only through the shared rawfilelock API. `staging_lockfile` relies on these fcntl locks to coordinate both in-process and inter-process staging lock ownership.

## Risks and Edge Cases
The blocking retry loop can hide repeated errors other than contention because it retries any non-nil error when `nonblocking` is false. It does not retry `unix.Open` on transient errors. Closing a descriptor always releases locks on Unix, so `CloseHandle` cannot truly close without unlocking; callers must treat it as an error-path escape hatch.

## Test Signals
The paired tests verify open and lock success on Unix. Contention and cross-process behavior are indirectly covered by `staging_lockfile_test.go`, which runs a subprocess against the same lock path.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_windows.go -->
# sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_windows.go

## Purpose
This Windows-only implementation backs `internal/rawfilelock` with Win32 file handles and `LockFileEx`/`UnlockFileEx`. It gives the shared package the same open, lock, unlock, and close concepts as the Unix implementation while using Windows handle semantics.

## Important APIs and Functions
`type fileHandle windows.Handle` aliases a Win32 handle. `openHandle(path, mode)` adds `O_CLOEXEC` and calls `windows.Open` with `S_IWRITE`. `lockHandle` sets `LOCKFILE_EXCLUSIVE_LOCK` for write locks and `LOCKFILE_FAIL_IMMEDIATELY` for nonblocking acquisition, then locks the full byte range using `allBytes` for low and high lengths. `unlockAndCloseHandle` unlocks that full range before calling `closeHandle`; `closeHandle` calls `windows.Close`.

## Control Flow and State
The lock scope is modeled as the entire file. Nonblocking failures are returned to the caller. Blocking failures panic instead of retrying or returning, which is a deliberately sharp difference from Unix. The persistent artifact is still only the lock file; runtime lock state is held by the Windows file handle and kernel.

## Dependencies and Integration Points
The implementation depends on `golang.org/x/sys/windows` and is selected by `//go:build windows`. The shared rawfilelock wrapper passes standard Go open flags into `openHandle`, and `staging_lockfile` consumes the returned handle.

## Risks and Edge Cases
The panic on blocking `LockFileEx` errors makes caller recovery impossible for unexpected blocking failures. The implementation assumes whole-file locking via max uint32 ranges is sufficient. Windows lacks Unix-style close-without-unlock behavior, so the explicit `UnlockFileEx` in `UnlockAndCloseHandle` is important.

## Test Signals
The shared rawfilelock tests exercise open and lock calls on Windows. Windows-specific deep behavior is mostly not isolated here; broader archive tests show several Windows skips and platform-specific path expectations elsewhere in the repository.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/rawfilelock/rawfilelock_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile.go -->
# sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile.go

## Purpose
`staging_lockfile.go` provides a higher-level, process-aware locking abstraction for temporary staging resources. It wraps raw OS file locks with an in-process registry so a single process cannot accidentally create two `StagingLockFile` owners for the same path.

## Important APIs and Types
`StagingLockFile` stores the absolute lock-file path and a `rawfilelock.FileHandle`. `CreateAndLock(dir, pattern)` creates a unique temp file, closes it, then locks it and returns the lock object plus the basename. `TryLockPath(path)` attempts to lock a specific path, creating the file if needed. `UnlockAndDelete()` removes the lock file, unlocks/closes the handle, deletes the registry entry, and invalidates the object by clearing `file`.

## Control Flow
`tryAcquireLockForFile` canonicalizes the path with `filepath.Abs`, takes the package mutex, initializes `stagingLockFiles`, rejects duplicate ownership in the same process, opens the file with `rawfilelock.OpenLock`, and attempts a nonblocking write lock. On lock failure, it closes the raw handle before returning an error. `CreateAndLock` loops up to `maxRetries` if locking a just-created temp file fails, which handles rare name/lock races or external interference.

## State and Persistence
There are two layers of state: the filesystem lock file and the process-global `stagingLockFiles` map protected by `stagingLockFileLock`. The lock file persists until `UnlockAndDelete`, and the map entry exists only while the current process owns the lock. `UnlockAndDelete` deliberately panics on double-unlock because that violates the ownership contract.

## Dependencies and Integration Points
The file depends on `internal/rawfilelock`, `os`, `filepath`, and `sync`. It is the locking foundation for `internal/tempdir`, whose `NewTempDir` creates lock/tempdir pairs and whose stale recovery calls `TryLockPath` to distinguish active from abandoned directories.

## Risks and Edge Cases
If `CreateAndLock` fails after creating a temp file but before locking it, the current implementation retries without removing the failed candidate; later stale cleanup may remove such artifacts. `UnlockAndDelete` holds the package mutex while removing the file, which keeps registry state correct but can serialize slow filesystem operations. Callers must not construct `StagingLockFile` manually and must not use it after unlock.

## Test Signals
The paired tests verify creation, explicit path locking, duplicate lock rejection, panic on double unlock, recreation after deletion, goroutine concurrency, and subprocess contention. Those tests strongly anchor both the in-process registry and OS lock behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile_test.go -->
# sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile_test.go

## Purpose
This test file validates `StagingLockFile` semantics above raw OS locks, including in-process duplicate prevention, file deletion on unlock, concurrency, and real multi-process contention through `reexec`.

## Important APIs and Helpers
`TestMain` initializes reexec. `subTryLockPath` starts a child process registered by `init`, and `subTryLockPathMain` attempts `TryLockPath` on the supplied path, unlocking and deleting on success. The main tests cover `CreateAndLock`, `TryLockPath`, `UnlockAndDelete`, and path reuse.

## Control Flow and State
The tests create temp directories and lock paths, then assert the package-global `stagingLockFiles` map is empty after unlock. `TestCreateAndLockAndTryLock` verifies the same process cannot acquire a second lock for an already-owned path, then can reacquire after release. `TestTryLockPathMultiProcess` holds a lock in the parent process, launches child attempts that must fail, releases the parent lock, and verifies a child can then acquire and clean up.

## Dependencies and Integration Points
The file imports `reexec` to create controlled subprocesses. It uses `testify` assertions and the filesystem to validate deletion. It indirectly tests the rawfilelock platform implementation because subprocess contention depends on kernel-level locking, not just the in-memory map.

## Risks and Edge Cases
The concurrency test creates independent temp dirs in each goroutine, so it stresses map cleanup rather than contention for one path. The subprocess error capture names the stdout reader as `stderrBuf`, but it still checks the child message. Tests do not simulate `os.Remove` failures during `UnlockAndDelete`.

## Test Signals
High-value signals include double-unlock panic, path recreation, and parent/child contention. These are important because `tempdir.RecoverStaleDirs` assumes `TryLockPath` failure means another owner is active.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/staging_lockfile/staging_lockfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/tempdir/tempdir.go -->
# sources/cloud-native/containers-storage/internal/tempdir/tempdir.go

## Purpose
`tempdir.go` manages temporary directories used to stage deletions safely. Each `TempDir` has a paired staging lock file so active directories are distinguishable from stale directories left by crashed or interrupted processes.

## Important APIs and Types
`TempDir` stores `RootDir`, an internal temp directory path, its `StagingLockFile`, the lock path, and a counter for unique staged names. `NewTempDir(rootDir)` creates the root, creates and locks a `lock-*` file, derives the matching `temp-dir-*` directory, and creates it. `StageDeletion(path)` renames a file or directory into the temp directory using `counter-basename`. `Cleanup()` removes the temp directory and unlocks/deletes the lock. `RecoverStaleDirs(rootDir)` scans for `temp-dir-*` and `lock-*` ids and removes entries whose lock can be acquired. `CleanupTemporaryDirectories` joins errors from deferred cleanup functions.

## Control Flow
`listPotentialStaleDirs` reads the root and extracts ids from both tempdir and lock prefixes. `RecoverStaleDirs` loops over those ids, tries `staging_lockfile.TryLockPath`, skips ids that cannot be locked, removes the temp directory for lockable ids, then unlocks and deletes the lock. `NewTempDir` uses `CreateAndLock` first and then creates the paired directory. `StageDeletion` fails if the object was already cleaned up, increments the counter, and uses `os.Rename`, so source and temp dir must be on the same filesystem.

## State and Persistence
Persistent state lives under `RootDir`: `lock-<id>` and `temp-dir-<id>/`. Active ownership is represented by the held staging lock. `Cleanup` resets internal fields so future `StageDeletion` calls fail and repeated `Cleanup` calls are no-ops. Staged deletions are persisted as renamed files until cleanup removes the temp directory.

## Dependencies and Integration Points
The package depends on `internal/staging_lockfile`, `os`, `filepath`, `strings`, `errors.Join`, and `logrus`. `layers.go` uses it during layer deletion: metadata and big-data directories are moved into a tempdir, and cleanup functions are run outside locks where possible. `layerStore.load` also invokes `RecoverStaleDirs` for the layer temp root and driver temp roots.

## Risks and Edge Cases
`StageDeletion` is not concurrency-safe; the file comment warns that a `TempDir` should be used by one goroutine. `os.Rename` can fail across filesystems. If `NewTempDir` successfully locks but fails to create the temp directory, the code returns an error without explicitly unlocking/deleting the lock, creating a potential stale lock that recovery should later handle. `RecoverStaleDirs` treats lock acquisition failure as active use and does not surface those errors.

## Test Signals
Tests cover staging one or many files, cleanup, idempotent cleanup, no reuse after cleanup, stale directory listing, stale recovery, active directory preservation, multiple instances, and filename preservation. They establish the lifecycle assumed by layer deferred deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/tempdir/tempdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/tempdir/tempdir_test.go -->
# sources/cloud-native/containers-storage/internal/tempdir/tempdir_test.go

## Purpose
This test file validates the lifecycle, naming, cleanup, stale recovery, and multi-instance behavior of `internal/tempdir`.

## Important Tests
`TestTempDirAdd` and `TestTempDirAddMultipleFiles` verify `StageDeletion` renames files into the managed tempdir with counter prefixes and removes originals. `TestTempDirCleanup` checks both temp directory and lock file removal and internal field reset. `TestTempDirCleanupNotInit` confirms repeated cleanup is safe. `TestTempDirReInitAfterCleanup` confirms an instance cannot be reused after cleanup. `TestListPotentialStaleDirs`, `TestRecoverStaleDirs`, and `TestRecoverStaleDirsSkipsActiveDirs` define recovery behavior. `TestTempDirMultipleInstances` and `TestTempDirFileNaming` check unique lock/tempdir pairs and basename preservation.

## Control Flow and State
The tests create real files and directories under `t.TempDir`, use `NewTempDir`, then inspect unexported fields because the tests are in the same package. Recovery tests manually create `temp-dir-*` and `lock-*` artifacts and verify `RecoverStaleDirs` removes only lockable stale state while preserving active state owned by a live `TempDir`.

## Dependencies and Integration Points
The tests use `testify/assert` and `require` plus standard filesystem APIs. They indirectly exercise `staging_lockfile.CreateAndLock`, `TryLockPath`, and `UnlockAndDelete`, which means recovery correctness depends on raw lock semantics.

## Risks and Edge Cases
The tests do not cover failed `os.Rename`, cross-device moves, failure to create the actual temp directory after locking, or cleanup errors from permissions. Active-directory recovery is tested in-process, not with a separate process holding the lock.

## Test Signals
The test suite strongly confirms the intended deletion-staging lifecycle and stale cleanup invariant. It is especially relevant to `layers.go`, where these cleanup functions are used to remove layer metadata after the store has removed references.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/internal/tempdir/tempdir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/jsoniter.go -->
# sources/cloud-native/containers-storage/jsoniter.go

## Purpose
This file centralizes JSON encoding/decoding for the `storage` package by assigning package variable `json` to `jsoniter.ConfigCompatibleWithStandardLibrary`.

## Important API
The exported surface is intentionally absent; the package-level variable is used internally as a drop-in replacement for the standard `encoding/json` API. In the researched files, `layers.go` uses `json.Unmarshal`, `json.Marshal`, and `json.NewDecoder` via this variable for layer metadata and additional layer info.

## Control Flow and State
There is no control flow beyond initialization. Runtime behavior depends on jsoniter's standard-library-compatible configuration. Persistent effects show up in files such as `layers.json`, `volatile-layers.json`, `mountpoints.json`, and additional-layer metadata, all written/read through package-level JSON calls.

## Dependencies and Integration Points
The dependency is `github.com/json-iterator/go`. The integration point is broad: all files in package `storage` that refer to `json` bind to this variable, not to an imported standard package.

## Risks and Edge Cases
Because this shadows the conventional package name, maintainers must remember that `json` is a variable. Compatibility with standard JSON is intended, but subtle differences in jsoniter behavior could affect persistent metadata compatibility.

## Test Signals
There is no direct test for this file. Indirect coverage comes from any storage tests that read/write JSON metadata, including the layer location tests and broader store tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/jsoniter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/layers.go -->
# sources/cloud-native/containers-storage/layers.go

## Purpose
`layers.go` implements the containers/storage layer store: in-memory indexing, persistent metadata, graph-driver integration, mount tracking, diff/apply operations, big data, deletion, garbage collection, and digest lookup for container image layers.

## Important Types and APIs
`Layer` is the persistent layer record with ID, names, parent, metadata, SELinux mount label, created time, compressed/uncompressed/TOC digests and sizes, compression type, UID/GID sets, flags, ID maps, read-only status, location, and big-data names. `layerLocations` splits metadata among stable `layers.json`, image-store `layers.json`, and `volatile-layers.json`. `roLayerStore` and `rwLayerStore` define the read/write store interfaces used by the broader storage package. `layerStore` owns locks, JSON paths, layer indexes, digest maps, mount indexes, and the graph `drivers.Driver`.

## Locking and Control Flow
The store uses a process-level `sync.RWMutex` nested under file locks from `pkg/lockfile`. `startWriting` takes the layer lock and in-process write lock, then reloads if needed. `startReading` takes read locks, checks whether on-disk layer or mount state changed, and can temporarily upgrade through a serialized reload path. `multipleLockFile` allows the primary layer directory and optional image store to be locked together.

`load` reads each configured JSON file, assigns layer locations, rebuilds indexes, reserves SELinux labels, loads mountpoints, recovers stale tempdirs, resolves duplicate names by removing conflicting names, and cleans incomplete layers when the store is writable. `saveLayers` records the lockfile write before atomically writing the selected JSON files; volatile layer metadata is written with `NoSync`. `saveMounts` separately records and writes `mountpoints.json`.

## Layer Creation and Persistence
`newLayerStore` creates directories, obtains lockfiles, configures JSON paths, loads metadata, and returns a writable store. `newROLayerStore` uses a read-only lockfile and only stable/volatile metadata under the layer directory. `create` validates ID/name uniqueness, handles template-layer metadata copying, reserves SELinux labels, writes an incomplete layer record before creating driver data, stores big data, creates or clones graph-driver layers, applies a diff or staged directory if supplied, updates digest maps, clears the incomplete flag, and saves final metadata. This incomplete-flag protocol is the crash-recovery anchor.

## Mounts, Deletion, and Cleanup
`Mount`, `unmount`, `Mounted`, and `ParentOwners` maintain mount counts and paths in `mountpoints.json` under `mountsLockfile`. Source comments explicitly identify locking bugs where `Diff` can reach `Mount`/`unmount` while the layer store is only read-locked for btrfs/zfs fallback getters. `internalDelete` marks the layer incomplete, creates a `tempdir.TempDir`, asks the driver for deferred removal, stages tar-split and big-data paths into the tempdir, removes indexes, and returns cleanup functions. `deferredDelete` unmounts first, calls `internalDelete`, saves metadata, and expects callers to run cleanup outside locks. `Wipe` deletes known layers newest-first and then removes driver leftovers.

## Diff, Apply, and Digest Behavior
`Changes` delegates to `driver.Changes` after resolving parent/layer IDs and ID mappings. `Diff` normally delegates to driver diff unless reconstructing a tar stream from tar-split metadata, or returning an additional-layer blob. It can recompress according to requested or recorded compression. `applyDiffWithOptions` peeks compression, computes compressed and uncompressed digests/sizes, captures tar-split metadata, logs UID/GID sets, applies the diff through the driver, writes tar-split data, updates layer fields and digest maps, and saves. Staged-differ paths use `DriverWithDiffer` outputs and can update TOC digest, metadata, flags, tar-split, and big data.

## Dependencies and Integration Points
The file integrates with graph drivers, `archive`, `idtools`, `lockfile`, `mount`, `selinux`, `tar-split`, `pgzip`, `digest`, `tempdir`, `ioutils`, and package-level helpers for names and errors. It is one of the central persistence layers for containers/storage and is consumed through the store APIs elsewhere in the package.

## Risks and Edge Cases
Major risks include the documented read-lock mutation path in `Diff`, metadata consistency across multiple JSON locations, incomplete-layer recovery failures, cleanup functions that must be run even on error, and stale mount information becoming obsolete immediately after load. Volatile metadata trades durability for speed. Digest maps must stay synchronized on update/delete; this file updates compressed and uncompressed maps in several paths but `deleteInDigestMap` only removes compressed and uncompressed entries, leaving TOC-map cleanup as a detail to watch.

## Test Signals
The included `layers_test.go` only validates `layerLocations` bit/index conversion. Most behavior in this file must be covered by broader store and driver tests outside this subset. The code itself contains detailed invariants and comments that serve as strong design signals, especially around lock ordering, incomplete flags, and cleanup obligations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/layers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/layers_test.go -->
# sources/cloud-native/containers-storage/layers_test.go

## Purpose
This test file checks the small `layerLocations` bitmask helpers used by `layers.go` to map stable, image-store, and volatile layer metadata locations.

## Important Tests
`TestLayerLocationFromIndex` asserts exact bit values for indexes 0 through 4. `TestLayerLocationFromIndexAndToIndex` iterates over every bit in the `layerLocations` storage size and verifies `indexFromLayerLocation(layerLocationFromIndex(i)) == i`.

## Control Flow and State
The tests are pure and do not touch filesystem state. They use `unsafe.Sizeof` to cover the full bit width of the `layerLocations` type.

## Dependencies and Integration Points
The file depends on `testify/assert`, `testify/require`, and `unsafe`. These helpers are used by `layers.go` when iterating JSON path arrays and deciding which layer metadata file a layer belongs to.

## Risks and Edge Cases
The tests do not check invalid multi-bit `layerLocations` inputs to `indexFromLayerLocation`; callers should pass one-bit values. They also do not cover the semantic relationship between the first three indexes and the current `numLayerLocationIndex`.

## Test Signals
The tests provide focused confidence that the bit-shift/trailing-zero helpers remain inverses for one-bit values, which protects persistence-location indexing logic in `saveLayers` and `load`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/layers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/lockfile_compat.go -->
# sources/cloud-native/containers-storage/lockfile_compat.go

## Purpose
This compatibility file preserves deprecated storage-package lockfile entry points while delegating to `pkg/lockfile`.

## Important APIs
`type Locker = lockfile.Locker` aliases the deprecated locker type. `GetLockfile(path)` calls `lockfile.GetLockfile(path)`. `GetROLockfile(path)` calls `lockfile.GetROLockfile(path)`. All are marked deprecated in favor of direct `pkg/lockfile` APIs.

## Control Flow and State
There is no local state. Calls pass through to the lockfile package, so persistence and locking semantics are entirely owned by `pkg/lockfile`.

## Dependencies and Integration Points
The only dependency is `github.com/containers/storage/pkg/lockfile`. The file exists for external callers that still import lock helpers from the root storage package.

## Risks and Edge Cases
The file intentionally carries deprecated APIs. Risk is mainly API compatibility: removing or changing it could break downstream users. The staticcheck suppression documents why the deprecated alias is still present.

## Test Signals
No direct tests in this subset. Compatibility is implicitly tested by downstream build coverage and any external users compiling against these symbols.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/lockfile_compat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive.go

## Purpose
`archive.go` is the main tar/archive utility implementation for containers/storage. It detects and applies compression, creates and extracts tar streams, preserves metadata, handles whiteouts, maps IDs, prevents archive breakouts, supports copy helpers, and exposes archiver constructors used by storage and copy code.

## Important Types and APIs
`Compression` supports uncompressed, bzip2, gzip, xz, and zstd detection/handling. `WhiteoutFormat` distinguishes AUFS and overlay whiteouts. `TarOptions` controls include/exclude patterns, compression, ID maps, chown override, whiteout conversion, copy-pass mode, force-mask extraction, source-dir inclusion, rebasing, rootless/userns behavior, and fixed timestamps. `Archiver` packages `Tar`, `Untar`, ID mappings, and chown options. `TarModifierFunc` powers `ReplaceFileTarWrapper`.

## Compression and Tar Creation
`DetectCompression` checks magic bytes. `DecompressStream` wraps a pooled buffered reader and supports gzip, bzip2, xz, zstd, and uncompressed streams, using external `pigz` or `zstd` filters when available. `CompressStream` supports uncompressed, gzip, and zstd output; bzip2 and xz writing return explicit unsupported errors. `TarWithOptions` starts a pipe and writes through `tarWithOptionsTo`, which walks requested include roots, applies exclude patterns, optional rebasing, hardlink tracking, xattrs, file flags, ID mapping, whiteout conversion, and compression.

## Extraction Control Flow and Safety
`Untar` and `UntarUncompressed` call `untarHandler`, which normalizes options and optionally decompresses. `Unpack` iterates tar headers, cleans names, applies excludes, creates parent directories, checks relative path scope, prevents directory/non-directory overwrites when requested, remaps IDs, runs whiteout conversion, and calls `extractTarFileEntry`. `extractTarFileEntry` creates regular files, dirs, devices, fifos, hardlinks, symlinks, or ignores PAX global headers; it rejects hardlink/symlink targets outside the extraction root, applies chown/chmod/timestamps, restores xattrs except ignored SELinux labels, writes override xattrs for force-mask mode, and defers directory flags/times until the end.

## Copy and Temporary Archive Helpers
`Archiver.TarUntar`, `UntarPath`, `CopyWithTar`, and `CopyFileWithTar` compose tar and untar for filesystem copying. `CopyFileWithTar` streams one file through a pipe, enforces `NoOverwriteDirNonDir`, and propagates writer errors. `NewTempArchive` stores a source stream in a temp file and deletes it after the full read. Chown-aware helper factories optionally tee archive data to a hasher. `TarPath` returns an ID-mapped tar producer.

## State and Persistence
Most operations are streaming and avoid persistent state. Persistent effects are extracted files, temp archive files, restored xattrs/file flags, and optional container override xattrs. Pooled buffers must be returned correctly; tar writers/readers and compressors must be closed to flush and surface errors.

## Dependencies and Integration Points
The file depends on Go tar/compression/filepath APIs, `fileutils`, `idtools`, `pools`, `promise`, `system`, `unshare`, `logrus`, `pgzip`, and `xz`. Platform hooks come from `archive_unix.go`, `archive_windows.go`, `archive_linux.go`, `archive_bsd.go`, version-gated files, zstd support, file flags, and filter helpers. `layers.go` uses this package for diff compression/detection, tar-split replay, whiteouts, and layer change export.

## Risks and Edge Cases
Security-sensitive risks include path traversal, symlink/hardlink breakout, xattr restoration under user namespaces, device creation, directory/non-directory overwrite behavior, and races when archiving a concurrently mutating tree. `TarWithOptions` logs and skips transient stat/add failures to keep archives valid, which can omit files. `ReplaceFileTarWrapper` mutates the supplied mods map. `remapIDs` has platform-specific behavior, including Darwin override xattr parsing. `NewTempArchive` only deletes after EOF or read error, so callers that never drain or close may leave temp files until external cleanup.

## Test Signals
The archive tests cover compression detection, unsupported compressors, tar/untar round trips, include/exclude/rebase behavior, overwrite errors, sockets, hardlinks, special devices, xattrs, security breakout attempts, temp archive idempotent close, tar replacement, timestamp determinism, and writer error propagation. Linux/Unix/Windows platform tests add whiteout and path behavior coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_110.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_110.go

## Purpose
This Go-version-specific file is compiled on Go 1.10 and newer. It tunes tar header handling for copy-pass archives and timestamp comparison fidelity.

## Important Functions
`copyPassHeader(hdr)` sets `hdr.Format = tar.FormatPAX`, enabling PAX behavior for copy-pass streams. `maybeTruncateHeaderModTime(hdr)` truncates `ModTime` to seconds only when `hdr.Format` is `tar.FormatUnknown`.

## Control Flow and State
The functions mutate a caller-provided `*tar.Header` and do not store state. They are called from `prepareAddFile` and `CopyFileWithTar` paths in `archive.go`.

## Dependencies and Integration Points
The file depends on `archive/tar` and `time`. It pairs with `archive_19.go`, which compiles on older Go versions and leaves both functions as no-ops.

## Risks and Edge Cases
The timestamp truncation behavior is subtle: it tries to avoid Go tar writer rounding surprises while retaining richer PAX timestamp precision when copy-pass mode has already set a concrete format. Incorrect changes here can cause false positives in directory diff comparisons.

## Test Signals
Round-trip tests in `archive_test.go`, especially no-change comparisons and timestamp determinism, indirectly validate this behavior on modern Go.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_110.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_19.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_19.go

## Purpose
This compatibility file is selected for Go versions older than 1.10. It provides no-op implementations of tar header helpers that modern builds implement in `archive_110.go`.

## Important Functions
`copyPassHeader(hdr)` and `maybeTruncateHeaderModTime(hdr)` are both no-ops under the `!go1.10` build tag.

## Control Flow and State
There is no control flow beyond accepting the header pointer. No persistent or runtime state is modified.

## Dependencies and Integration Points
The file depends only on `archive/tar`. It keeps `archive.go` source-compatible across Go versions by providing the same helper names.

## Risks and Edge Cases
Older Go builds do not force PAX for copy-pass and do not apply the timestamp truncation workaround. This can affect metadata precision and change detection, but only for legacy toolchains.

## Test Signals
Current test runs on Go 1.10+ will not exercise this file. Its main signal is build compatibility for old Go versions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_19.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_bsd.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_bsd.go

## Purpose
This BSD/Darwin platform file implements symlink-aware chmod behavior during tar extraction where `fchmodat` with `AT_SYMLINK_NOFOLLOW` is available.

## Important Function
`handleLChmod(hdr, path, hdrInfo, forceMask)` computes the permissions from the header file info or a forced mask, then calls `unix.Fchmodat(AT_FDCWD, path, mode, AT_SYMLINK_NOFOLLOW)`.

## Control Flow and State
The function directly applies mode bits to an extracted filesystem path. It does not branch on tar type beyond using the supplied mode. The persistent effect is the file mode on disk.

## Dependencies and Integration Points
The file is built on NetBSD, FreeBSD, or Darwin. It depends on `archive/tar`, `os`, and `golang.org/x/sys/unix`. `extractTarFileEntry` in `archive.go` calls `handleLChmod` after chown and before timestamp/xattr restoration.

## Risks and Edge Cases
Because this platform implementation applies `Fchmodat` with no-follow semantics, behavior can differ from Linux's selective chmod of non-symlink entries and hardlinks. Force-mask handling must stay aligned with extraction code and chunked package comments.

## Test Signals
There is no direct BSD test in this subset for `handleLChmod`. BSD-specific file flag tests in `changes_bsd_test.go` exercise adjacent platform metadata handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_linux.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_linux.go

## Purpose
This Linux-specific file implements overlay whiteout conversion and Linux ownership/chmod helpers for archive creation and extraction.

## Important APIs and Types
`GetWhiteoutConverter(format, data)` returns an `overlayWhiteoutConverter` for overlay format, optionally with lower-layer paths. `overlayWhiteoutConverter.ConvertWrite` converts overlay character-device whiteouts and opaque directory xattrs into AUFS-style tar entries. `ConvertReadWithHandler` converts AUFS `.wh.*` and `.wh..wh..opq` entries back into overlay character devices and opaque xattrs. `directHandler` applies xattrs, mknod, and chown directly. `GetFileOwner` returns UID, GID, and mode from `syscall.Stat_t`. Linux `handleLChmod` chmods non-symlink entries and carefully handles hardlinks.

## Control Flow
On write, character devices with major/minor zero become `.wh.<name>` regular tar entries. Opaque directories with overlay opaque xattr may produce an additional AUFS opaque whiteout entry only if lower layers indicate the directory existed and was not already hidden by a parent whiteout. On read, `.wh..wh..opq` sets the overlay opaque xattr on the directory and suppresses writing the marker file; `.wh.<name>` creates a zero-device character node and chowns it, suppressing the marker file.

## State and Persistence
The file reads and writes overlay xattrs, creates character-device whiteouts, applies ownership, and changes permissions. `GetOverlayXattrName` from `archive.go` selects trusted or user overlay xattr namespace based on rootless state.

## Dependencies and Integration Points
Dependencies include `archive/tar`, `os`, `filepath`, `strings`, `syscall`, `idtools`, `system`, and `x/sys/unix`. The code is invoked by `tarWriter.prepareAddFile` and `Unpack` when `TarOptions.WhiteoutFormat` is `OverlayWhiteoutFormat`.

## Risks and Edge Cases
Whiteout conversion is subtle around lower layers, parent-directory whiteouts, and nested whiteout entries. Device creation may fail in restricted environments. `isWhiteOut` assumes `stat.Sys()` is `*syscall.Stat_t`. Incorrect opaque handling can change layer deletion semantics.

## Test Signals
`archive_linux_test.go` validates overlay-to-overlay round trips, overlay-to-AUFS extraction, nested whiteouts, modes, opaque xattrs, and whiteout device preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_linux_test.go

## Purpose
This Linux test file validates overlay whiteout and opaque-directory conversion across tar and untar operations.

## Important Tests and Helpers
`setupOverlayTestDir` creates opaque directories and a character-device whiteout. `setupOverlayLowerDir` creates a lower-layer directory used to decide whether an opaque directory needs an AUFS opaque marker. `TestOverlayTarUntar` tars and untars using overlay whiteout format and checks modes, opaque xattrs, and device whiteouts. `TestOverlayTarAUFSUntar` tars overlay input but extracts as AUFS, checking `.wh..wh..opq` and `.wh.<file>` entries. `TestNestedOverlayWhiteouts` ensures nested whiteouts do not fail when a parent path has already become a whiteout device.

## Control Flow and State
The tests manipulate real xattrs and device nodes using `system.Lsetxattr` and `system.Mknod`, set umask to zero for deterministic modes, stream archives through `TarWithOptions`, and inspect the extracted filesystem state.

## Dependencies and Integration Points
The file depends on Linux-specific `system`, `unix`, `syscall`, and archive whiteout APIs. It validates `archive_linux.go` plus the shared tar/extraction machinery in `archive.go`.

## Risks and Edge Cases
These tests require privileges/filesystem support for xattrs and mknod-like behavior. They focus on a small overlay tree, not all lower-layer combinations. The nested test specifically protects the ENOTDIR case documented in the converter.

## Test Signals
The tests provide strong Linux-specific confidence that overlay whiteouts survive archive round trips and that conversions to AUFS tar markers preserve the expected deletion/opaque semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_other.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_other.go

## Purpose
This non-Linux platform file provides fallback whiteout behavior for archive operations.

## Important APIs
`GetWhiteoutConverter(format, data)` always returns nil on non-Linux builds, meaning no platform-specific whiteout conversion is applied.

## Control Flow and State
There is no state and no conversion. Tar creation and extraction proceed with the generic AUFS-style names or ordinary file entries handled by `archive.go`.

## Dependencies and Integration Points
The file is selected by `//go:build !linux` and shares the same function name as `archive_linux.go`, allowing generic code to call `GetWhiteoutConverter` unconditionally.

## Risks and Edge Cases
Non-Linux platforms do not get overlay whiteout conversion. Callers using overlay-specific formats on non-Linux will effectively get no converter, so tests and features must account for platform capability.

## Test Signals
No direct test in this subset. The behavior is primarily a build-time fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_test.go

## Purpose
This is the broad generic test suite for `pkg/archive`. It validates archive detection, compression, tar/untar copying, include/exclude behavior, metadata preservation, security breakout prevention, temporary archives, archive modification, deterministic timestamps, and error propagation.

## Important Test Areas
Archive detection tests cover invalid files, directories, tar files, and gzip-compressed tar files. Compression tests validate gzip, bzip2, xz decompression and unsupported xz/bzip2 compression. Copy tests cover invalid sources/destinations, file-vs-directory overwrite behavior, destination creation, socket skipping, and metadata preservation. Round-trip tests compare `ChangesDirs` after tar/untar for many files and hardlinks. Include/exclude/rebase tests validate `TarOptions`. Security tests build malicious tar headers for `../`, absolute-like paths, hardlink escapes, symlink escapes, and symlink-in-path writes.

## Control Flow and State
Tests use real temp directories and files, external shell tools for some tar/compression setup, in-memory tar streams for malicious cases, and helper wrappers around `NewDefaultArchiver`. Several tests skip on Windows where platform behavior is unavailable. `TestReplaceFileTarWrapper` streams an archive through modifiers that create, replace, and append entries. `TestTimestamp` compares whole tar byte streams with and without fixed timestamps. `TestTarErrorHandling` uses a failing writer to ensure errors are propagated.

## Dependencies and Integration Points
The tests depend on `archive/tar`, `os/exec`, runtime checks, `idtools`, and `testify`. They exercise `archive.go`, platform hooks for hardlinks/special files/xattrs, `changes.go`, and helper packages for ID mapping and filesystem metadata.

## Risks and Edge Cases
Some tests depend on external commands (`tar`, `gzip`, `bzip2`, `xz`) and platform privileges. Multiple Windows skips mean generic archive behavior is less thoroughly validated on Windows. The security tests are high-value because extraction code is path-sensitive and must reject breakout attempts before creating or removing host files.

## Test Signals
This suite is the primary behavioral safety net for `archive.go`. It signals expected behavior for supported/unsupported compression, safe extraction, copy-pass metadata, hardlink preservation, xattr preservation, replacement streams, deterministic timestamp mode, and write error handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_unix.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_unix.go

## Purpose
This Unix platform file provides tar header stat population, canonical path behavior, special-device extraction, hardlink behavior, and UID/GID extraction for archive operations.

## Important Functions
`init` installs `statUnix` into `sysStatOverride`, so `FileInfoHeader` can populate UID, GID, and device major/minor without extra OS lookups. `fixVolumePathPrefix` is a no-op. `getWalkRoot` preserves trailing include semantics by concatenating paths instead of `filepath.Join`. `CanonicalTarNameForPath` returns Unix-style paths unchanged. `chmodTarEntry` is a no-op. `setHeaderForSpecialDevice`, `getInodeFromStat`, `getFileUIDGID`, `major`, `minor`, `handleTarTypeBlockCharFifo`, and `handleLLink` implement Unix metadata and filesystem operations.

## Control Flow and State
The file mutates tar headers based on `syscall.Stat_t`, creates block/char/fifo filesystem entries through `system.Mknod`, and creates hardlinks via `unix.Linkat` without following symlinks. Its persistent effects occur during extraction when special files and hardlinks are created.

## Dependencies and Integration Points
Dependencies include `archive/tar`, `os`, `filepath`, `syscall`, `idtools`, `system`, and `x/sys/unix`. The functions are called by `archive.go` during tar creation, extraction, and hardlink tracking.

## Risks and Edge Cases
Device creation requires appropriate privileges. Hardlink behavior intentionally avoids symlink following; changing that would weaken breakout protections. `getWalkRoot` has path-cleaning implications for include roots and should remain aligned with tests.

## Test Signals
`archive_unix_test.go` validates canonical names, chmod behavior, hardlink preservation and rebasing, special device/fifo round trips, and xattr preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_unix_test.go

## Purpose
This Unix-only test file validates path canonicalization, chmod behavior, hardlinks, special device/fifo handling, and xattr round trips.

## Important Tests
`TestCanonicalTarNameForPath` and `TestCanonicalTarName` assert Unix names are preserved and directories get trailing slashes. `TestChmodTarEntry` verifies chmod is a no-op on Unix. `TestTarWithHardLink` checks hardlink preservation and ensures tar hardlink entries target a real file entry rather than another hardlink entry. `TestTarWithHardLinkAndRebase` validates hardlinks after archive rebasing. `TestTarWithBlockCharFifo` checks special device/fifo preservation. `TestTarUntarWithXattr` verifies security capability and user xattrs survive tar/untar where supported.

## Control Flow and State
The tests create real Unix filesystem features: hardlinks, block devices, char devices, fifos, and xattrs. They tar to memory, untar to temp directories, and compare inodes or `ChangesDirs` output.

## Dependencies and Integration Points
The file depends on `system`, `unix`, `idtools`, `archive.go`, `archive_unix.go`, and `changes.go`. Some tests skip on platforms such as Solaris or FreeBSD for xattr limitations.

## Risks and Edge Cases
Privilege and filesystem support affect special device and xattr tests. The tests cover preservation, but not all failure branches in extraction. Hardlink tests are especially important for security because link targets must not become symlink-following escapes.

## Test Signals
Strong Unix platform coverage for metadata fidelity and hardlink/device semantics. These tests complement the generic breakout tests in `archive_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_windows.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_windows.go

## Purpose
This Windows platform file adapts archive paths and metadata to Windows filesystem semantics.

## Important Functions
`fixVolumePathPrefix` adds long-path prefixes through `longpath.AddPrefix`. `getWalkRoot` joins source and include paths normally. `CanonicalTarNameForPath` rejects relative paths containing forward slashes and converts Windows separators to POSIX tar slashes. `chmodTarEntry` adds execute bits and clamps permission bits to `0755` while preserving non-permission mode bits. Special-device functions are no-ops because Windows lacks Unix device/inode concepts here. `getFileUIDGID` returns zero IDs. `handleLLink` uses `os.Link`.

## Control Flow and State
The file mostly transforms paths and tar header modes. Extraction of block/char/fifo and chmod are no-ops. Persistent effects are ordinary file creation and hardlinks through generic extraction.

## Dependencies and Integration Points
Dependencies include `archive/tar`, `fmt`, `os`, `filepath`, `strings`, `idtools`, and `longpath`. The functions are invoked from `archive.go` through platform-neutral helper names.

## Risks and Edge Cases
Rejecting forward slashes protects assumptions that Windows input paths use backslashes, but can surprise callers passing POSIX-like relative paths. Permission normalization is lossy by design. No-op device handling means archives containing Unix special files cannot be faithfully restored on Windows.

## Test Signals
`archive_windows_test.go` validates canonical path conversion and directory suffix behavior. One invalid-destination copy test is skipped as currently failing, which marks an unresolved Windows behavior gap.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_windows_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_windows_test.go

## Purpose
This Windows-only test file validates Windows archive path canonicalization and documents a skipped invalid-destination copy case.

## Important Tests
`TestCanonicalTarNameForPath` checks that plain names pass, Unix-style `foo/bar` fails, and Windows-style `foo\bar` converts to `foo/bar`. `TestCanonicalTarName` verifies directory names receive trailing slashes after conversion. `TestCopyFileWithInvalidDest` is skipped with a note that it currently fails and needs investigation.

## Control Flow and State
The active tests are pure path-conversion checks. The skipped copy test would create temp files and attempt a copy to `c:dest`, but it is not executed.

## Dependencies and Integration Points
The file depends on Windows implementation functions in `archive_windows.go` and generic `canonicalTarName` in `archive.go`.

## Risks and Edge Cases
The skipped test is an explicit gap in Windows copy error coverage. The canonicalization tests do not cover long-path prefix behavior or permission normalization.

## Test Signals
The main signal is that Windows relative archive paths must be converted to POSIX tar names and forward slashes in Windows inputs are rejected.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_zstd.go -->
# sources/cloud-native/containers-storage/pkg/archive/archive_zstd.go

## Purpose
This file adds zstd compression and decompression support for archive streams when external `zstd` filtering is unavailable or when writing zstd streams.

## Important APIs
`zstdReader(buf)` creates a `zstd.Decoder`, wraps it with `io.NopCloser`, and returns it. `zstdWriter(dest)` returns a `zstd.Encoder` as an `io.WriteCloser`. Both use `github.com/klauspost/compress/zstd`.

## Control Flow and State
There is no package state. Reader and writer constructors allocate codec instances and return stream wrappers. Callers in `archive.go` own closing returned writers/readers.

## Dependencies and Integration Points
The file depends on `io` and `github.com/klauspost/compress/zstd`. `DecompressStream` calls `zstdReader` if the external filter path is not used. `CompressStream` calls `zstdWriter` for zstd output.

## Risks and Edge Cases
Codec construction errors are propagated. Because `zstdReader` uses `io.NopCloser`, closing the reader does not close an underlying source; `DecompressStream` wraps buffering separately in some paths, so ownership must be understood by callers.

## Test Signals
Generic compression tests in this subset do not explicitly exercise zstd. Coverage may exist elsewhere; within this subset, zstd support is mostly validated by build and integration with `CompressStream`/`DecompressStream`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/archive_zstd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes.go

## Purpose
`changes.go` computes filesystem differences between layers or directories and exports those differences as AUFS-style tar changes. It is used for layer diff generation and size estimation.

## Important Types and APIs
`ChangeType` enumerates modify, add, and delete operations and renders as `C`, `A`, or `D`. `Change` stores path and kind. `Changes(layers, rw)` walks a read-write layer against read-only layers using AUFS whiteout rules. `ChangesDirs(newDir, newMappings, oldDir, oldMappings)` builds `FileInfo` trees and compares them. `ChangesSize` estimates changed payload size without double-counting hardlinks. `ExportChanges` streams a tar archive for a list of changes, writing whiteout entries for deletes.

## Control Flow
`changes` walks the rw directory, rebases paths to absolute-style OS paths, skips metadata, maps `.wh.*` files to deletes, scans lower layers to distinguish adds from modifies, accounts for lower-layer whiteouts, and injects parent directory modify records for adds/deletes. The `FileInfo` comparison path recursively compares stat metadata, capabilities, symlink targets, and xattrs, records adds/modifies/deletes, and inserts directory modify records when children changed.

## State and Persistence
`FileInfo` is an in-memory tree containing parent links, ID mappings, stat data, children, capabilities, xattrs, targets, and an `added` marker. `ExportChanges` persists results only through the returned pipe stream. Delete changes become tar headers named with `WhiteoutPrefix`.

## Dependencies and Integration Points
The file depends on `archive/tar`, filesystem APIs, `fileutils`, `idtools`, `pools`, `system`, and platform helpers from `changes_linux.go`, `changes_unix.go`, `changes_other.go`, or `changes_windows.go`. `layers.go` calls driver-level changes, and drivers/archive flows use these helpers for diff exports and validation.

## Risks and Edge Cases
Filesystem races are expected during live diffing; `ExportChanges` logs and skips some file-add errors to keep streaming. Time comparison allows one side to have zero nanoseconds to account for tar precision. Whiteout and parent-directory logic is subtle and platform-specific. The old-dir empty case creates and removes a temp directory with `os.Remove`, not `RemoveAll`, which is fine for the empty temp dir but worth preserving intentionally.

## Test Signals
Generic archive tests use `ChangesDirs` for round-trip equality. BSD-specific tests validate file flags in changes on supported platforms. Full platform helper coverage is split across other files outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_bsd_test.go -->
# sources/cloud-native/containers-storage/pkg/archive/changes_bsd_test.go

## Purpose
This BSD-only test file validates that file flags are included in change detection on platforms where `chflags`/file flags matter.

## Important Test
`TestChangesWithFileFlags` creates two directories with a file of the same contents, applies a flag such as `UF_NODUMP` to the new file, runs `ChangesDirs`, and expects a single `ChangeModify` entry for `/file`.

## Control Flow and State
The test creates old and new temp directories, writes matching files, changes flags on the new file through `unix.Chflags`, runs the directory comparison, and asserts the exact change list. The persistent state under test is filesystem file flags.

## Dependencies and Integration Points
The file depends on `golang.org/x/sys/unix`, `testify/require`, `idtools`, and `changes.go` plus BSD file-flag helpers. It complements `fflags_bsd.go` and platform-specific stat comparison behavior.

## Risks and Edge Cases
It tests one flag and one file. It does not validate tar header preservation of flags directly; archive round-trip behavior is covered through other platform-specific file flag code.

## Test Signals
The test confirms that metadata-only file flag differences are not ignored by `ChangesDirs`, which is important for faithful layer diffing on BSD-like systems.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/changes_bsd_test.go -->
