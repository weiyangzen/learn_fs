# Research: subset-b-000085

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/meminfo_windows.go

Purpose: Windows implementation of host memory probing for the `system` package. It backs the cross-platform `ReadMemInfo` API by calling `kernel32!GlobalMemoryStatusEx`.

Important APIs/types/functions: defines the local `memorystatusex` struct matching the Win32 `MEMORYSTATUSEX` layout, lazy DLL/proc handles for `kernel32.dll`, and `ReadMemInfo() (*MemInfo, error)`. `ReadMemInfo` fills `MemTotal`, `MemFree`, `SwapTotal`, and `SwapFree` from physical and pagefile counters.

Control flow: allocate a struct with `dwLength` set to 64, invoke the syscall through `procGlobalMemoryStatusEx.Call`, and return an empty `MemInfo` on failure rather than surfacing the Win32 error. On success it converts unsigned byte counts to signed `int64`.

State/persistence: no persistent state. Lazy procedure handles are package-level process state and memory values are a point-in-time host snapshot.

Dependencies/integration: depends on `golang.org/x/sys/windows` and `unsafe`. It integrates with generic storage resource reporting wherever `system.ReadMemInfo` is used on Windows.

Risks: the hard-coded `dwLength` must continue to match the struct layout; if the syscall fails, callers cannot distinguish zero-memory results from failure because nil error is returned with an empty struct. Large pagefile values are cast to `int64`.

Test signals: Windows tests should mock or run on real hosts to verify non-zero memory counters, syscall failure behavior, and ABI layout if the struct changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/meminfo_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/mknod.go -->
# sources/cloud-native/containers-storage/pkg/system/mknod.go

Purpose: default Unix implementation of filesystem node creation and device-number packing for platforms other than Windows and FreeBSD.

Important APIs/types/functions: exports `Mknod(path string, mode uint32, dev uint32) error`, a thin wrapper over `unix.Mknod`, and `Mkdev(major, minor int64) uint32`, which encodes Linux-style major/minor device numbers.

Control flow: `Mknod` delegates directly to the kernel through `x/sys/unix`. `Mkdev` masks and shifts major/minor fields into the historical Linux device encoding.

State/persistence: `Mknod` creates persistent filesystem nodes. `Mkdev` is pure computation.

Dependencies/integration: used by archive extraction and layer application paths that need to recreate device nodes from tar metadata. Depends on `golang.org/x/sys/unix`.

Risks: creating device nodes requires privileges and correct mode bits; errors are not wrapped with path context here. The Linux device encoding is intentionally used on several non-Windows/non-FreeBSD targets, so portability depends on build tags matching syscall expectations.

Test signals: integration tests should cover major/minor round trips, permission-denied behavior, and archive extraction of character/block devices on supported Unix platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/mknod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/mknod_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/system/mknod_freebsd.go

Purpose: FreeBSD-specific variant of node creation where the `unix.Mknod` device argument is `uint64`.

Important APIs/types/functions: exports `Mknod(path string, mode uint32, dev uint64) error` and `Mkdev(major, minor int64) uint64`.

Control flow: `Mknod` delegates to `unix.Mknod` without conversion to `int`; `Mkdev` uses the same bit layout as the default implementation but returns a wider integer.

State/persistence: creates filesystem device/FIFO nodes; no in-memory state.

Dependencies/integration: selected by the `freebsd` build tag and used by the same layer/archive code as the generic Unix variant.

Risks: comments still describe Linux device-node encoding, so FreeBSD behavior depends on compatibility of that encoding with callers and kernel expectations. Privilege and filesystem restrictions can surface as raw syscall errors.

Test signals: FreeBSD archive/device tests should validate node type, major/minor values, and error handling for unprivileged callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/mknod_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/mknod_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/mknod_windows.go

Purpose: Windows stub for Unix `mknod` functionality.

Important APIs/types/functions: `Mknod` returns `ErrNotSupportedPlatform`; `Mkdev` panics because Windows has no compatible device-node encoding in this package.

Control flow: no syscall is attempted. `Mkdev` is deliberately fail-fast if a caller reaches it on Windows.

State/persistence: none.

Dependencies/integration: protects cross-platform callers from compiling Unix-only node creation on Windows.

Risks: `Mkdev` panics rather than returning an error, so callers must guard platform-specific device handling. `Mknod` signature differs from FreeBSD/default variants in the type of `dev`, which is safe by build tag but relevant to cross-platform code.

Test signals: Windows tests should assert unsupported errors for device creation and avoid executing `Mkdev` except in panic-specific tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/mknod_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path.go -->
# sources/cloud-native/containers-storage/pkg/system/path.go

Purpose: exposes the default executable search path used by containers/storage callers when constructing container environments.

Important APIs/types/functions: `defaultUnixPathEnv` constant and `DefaultPathEnv(platform string) string`.

Control flow: non-Windows hosts always return the Unix default. On Windows, Linux containers on Windows can receive the Unix default when `platform` differs from `runtime.GOOS` and `LCOWSupported()` is true; Windows containers return an empty default so the container supplies its own path.

State/persistence: no persistence; result depends on the host runtime and LCOW capability.

Dependencies/integration: integrates with container environment setup code and platform selection. Depends on `runtime` and the package's Windows LCOW helper.

Risks: empty Windows default is intentional but can surprise callers that assume a non-empty PATH. LCOW support detection controls whether Linux-style paths are injected on Windows.

Test signals: platform tests should cover Linux/Unix defaults, Windows-container empty defaults, and LCOW Linux-platform behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path_unix.go -->
# sources/cloud-native/containers-storage/pkg/system/path_unix.go

Purpose: Unix no-op implementation of Windows system-drive path normalization.

Important APIs/types/functions: `CheckSystemDriveAndRemoveDriveLetter(path string) (string, error)`.

Control flow: returns the input path unchanged with nil error.

State/persistence: none.

Dependencies/integration: lets shared code call the path-normalization API without build-tag branching.

Risks: Unix callers get no validation or slash conversion, which is correct only because drive-letter checks are Windows-specific.

Test signals: compile coverage on non-Windows platforms and cross-platform tests that expect no-op behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/path_windows.go

Purpose: validates Windows paths used by operations such as copying files into or out of containers, removing an optional system-drive prefix and converting slashes to Windows semantics.

Important APIs/types/functions: `CheckSystemDriveAndRemoveDriveLetter` rejects bare drive-relative forms like `C:`, rejects absolute paths on non-system drives, strips `C:` from absolute paths, and applies `filepath.FromSlash`.

Control flow: two-character drive-only paths fail as relative paths. Non-absolute or short paths are slash-normalized and returned. Absolute drive-letter paths must use `C:` case-insensitively, then the drive prefix is removed before slash normalization.

State/persistence: no persistent state; returns normalized path strings.

Dependencies/integration: depends on `filepath`, `strings`, and `fmt`. Used by Windows path validation in user-facing copy/extract code and by tests in `path_windows_test.go`.

Risks: system drive is hard-coded to `C:`. Error text currently uses lower-case messages in implementation, while the test file expects older capitalized messages, so test drift is a signal. UNC and extended-length path behavior is not explicitly handled here.

Test signals: tests cover non-system drive rejection, relative paths, slash conversion, system-drive stripping, and bare-drive failures; they should be kept in sync with exact error strings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path_windows_test.go -->
# sources/cloud-native/containers-storage/pkg/system/path_windows_test.go

Purpose: Windows unit tests for `CheckSystemDriveAndRemoveDriveLetter`.

Important APIs/types/functions: `TestCheckSystemDriveAndRemoveDriveLetter` exercises `d:\`, single-character and two-character relative paths, drive-less absolute paths, Linux-style slash input, `c:\`/`c:/`, and bare `c:`/`d:` failures.

Control flow: each case calls the helper and compares either returned path or exact error string.

State/persistence: none beyond temporary test state.

Dependencies/integration: validates Windows path normalization behavior expected by higher-level copy and extraction code.

Risks: the expected error strings differ in capitalization from the current implementation (`The/No` versus `specified/relative`), which would fail exact-string assertions on Windows. Exact error string checks are brittle for user-message changes.

Test signals: strong coverage for common drive-letter cases; missing coverage for UNC paths, extended-length paths, and non-`C:` system drives.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/path_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/process_unix.go -->
# sources/cloud-native/containers-storage/pkg/system/process_unix.go

Purpose: Unix process liveness and forced termination helpers.

Important APIs/types/functions: `IsProcessAlive(pid int) bool` and `KillProcess(pid int)`.

Control flow: liveness calls `unix.Kill(pid, 0)` and treats nil and `EPERM` as alive. Killing sends `SIGKILL` and ignores the result.

State/persistence: affects live process state when `KillProcess` succeeds; no stored metadata.

Dependencies/integration: selected for Linux, FreeBSD, Solaris, and Darwin; used by cleanup or process-management paths that need coarse liveness checks.

Risks: PID reuse can make liveness checks stale immediately. Ignoring kill errors hides permission, non-existent PID, and race failures.

Test signals: tests should cover current process liveness, missing PID false results, and permission behavior where feasible.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/process_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm.go -->
# sources/cloud-native/containers-storage/pkg/system/rm.go

Purpose: robust recursive removal helper that tries harder than `os.RemoveAll` for storage directories, especially when mounts, races, or immutable flags are involved.

Important APIs/types/functions: `EnsureRemoveAll(dir string) error`.

Control flow: first tries `os.RemoveAll`. On failure it runs `mount.RecursiveUnmount`, then loops up to per-path retry limits. It retries benign missing-child races, treats missing top-level dir as success, resets file flags on `EPERM`, unmounts `EBUSY` paths, sleeps briefly, and eventually returns unrecoverable errors.

State/persistence: removes filesystem trees and may unmount mounts under the target. Tracks transient retry maps in memory.

Dependencies/integration: depends on `pkg/mount`, `logrus`, `syscall`, and platform `resetFileFlags`/`IsEBUSY`. Used by store deletion and garbage cleanup for container/userdata directories.

Risks: aggressive unmount/removal is intentionally destructive for the target tree. Non-`PathError` failures are returned immediately. Race handling for repeated missing paths returns the error after seeing the same child twice. It can loop for about 10 seconds per busy path at the max retry setting.

Test signals: `rm_test.go` covers missing paths, files, directories, and bind mounts. FreeBSD immutable-flag behavior depends on `rm_freebsd.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm_common.go -->
# sources/cloud-native/containers-storage/pkg/system/rm_common.go

Purpose: default implementation of file-flag reset for platforms that do not need FreeBSD `chflags` cleanup.

Important APIs/types/functions: `resetFileFlags(dir string) error` returns nil.

Control flow: no traversal or syscall is performed.

State/persistence: none.

Dependencies/integration: called by `EnsureRemoveAll` after `EPERM`; on non-FreeBSD it assumes immutable flags are not handled here.

Risks: if a non-FreeBSD platform supports immutable flags that block removal, this no-op leaves the original `RemoveAll` failure unresolved.

Test signals: `EnsureRemoveAll` tests on non-FreeBSD confirm ordinary deletion paths; platform-specific immutable tests belong elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/system/rm_freebsd.go

Purpose: FreeBSD implementation of immutable/file flag reset used before retrying recursive deletion.

Important APIs/types/functions: `resetFileFlags(dir string) error` walks the tree with `filepath.WalkDir` and calls `Lchflags(path, 0)` on each entry.

Control flow: every visited path has flags cleared; any `Lchflags` error aborts the walk and propagates to `EnsureRemoveAll`.

State/persistence: mutates filesystem flags, enabling later deletion of files that were append-only or immutable.

Dependencies/integration: integrates with FreeBSD `chflags` helpers and `EnsureRemoveAll` EPERM recovery.

Risks: the callback ignores the `err` argument from `WalkDir`; if traversal reports an access error, the code still tries `Lchflags` on that path. Clearing all flags is broad and should only happen in removal paths.

Test signals: FreeBSD tests should combine immutable files with `EnsureRemoveAll`; `stat_freebsd_test.go` checks flag preservation through stat helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm_test.go -->
# sources/cloud-native/containers-storage/pkg/system/rm_test.go

Purpose: unit/integration tests for `EnsureRemoveAll`.

Important APIs/types/functions: tests cover non-existent paths, temporary directories, temporary files, and bind-mounted subdirectories.

Control flow: the mount test creates two temp dirs, bind-mounts one into the other, runs `EnsureRemoveAll` in a goroutine, and fails if it does not complete within five seconds.

State/persistence: creates and removes temporary filesystem objects; the mount test performs a real bind mount on non-Windows systems.

Dependencies/integration: depends on `pkg/mount`, `runtime`, and host mount permissions.

Risks: mount test requires privileges/capabilities and skips only Windows; unprivileged Unix test environments may fail during `mount.Mount`. Timeout detects hangs in busy-unmount retry logic.

Test signals: good regression signal for `EBUSY` unmount cleanup and no-error behavior for missing paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/rm_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_common.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_common.go

Purpose: common non-FreeBSD fallback for file flags in `StatT`.

Important APIs/types/functions: defines empty `platformStatT` and `StatT.Flags() uint32`, returning zero.

Control flow: `Flags` references the embedded field only to silence unused warnings and returns zero.

State/persistence: none.

Dependencies/integration: embedded by `StatT` on non-FreeBSD platforms so callers can use a uniform `Flags` method.

Risks: callers must treat zero as either no flags or unsupported flags depending on platform.

Test signals: compile coverage across all non-FreeBSD platforms; behavior is intentionally trivial.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_darwin.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_darwin.go

Purpose: Darwin conversion from `syscall.Stat_t` to the package-neutral `StatT`.

Important APIs/types/functions: `fromStatT(s *syscall.Stat_t) (*StatT, error)`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtimespec` into `StatT`.

State/persistence: no mutation; captures a filesystem stat snapshot.

Dependencies/integration: called by Unix `Stat`/`Fstat` on Darwin.

Risks: does not populate `dev`, so `StatT.Dev()` remains zero on Darwin. Platform field names and integer widths must match Go's Darwin syscall definitions.

Test signals: Darwin stat tests should verify mode/time/ownership and whether missing `dev` is acceptable for callers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_freebsd.go

Purpose: FreeBSD conversion from `syscall.Stat_t` to `StatT`, including filesystem flags.

Important APIs/types/functions: `platformStatT{flags uint32}`, `StatT.Flags()`, and `fromStatT`.

Control flow: builds a `StatT` with size, mode, uid, gid, rdev, mtime, dev, then stores `s.Flags`.

State/persistence: read-only conversion of syscall stat data.

Dependencies/integration: supports FreeBSD deletion flag reset and caller visibility into file flags.

Risks: assigns `dev` twice, harmless but redundant. FreeBSD-specific `Flags` behavior is not available on other platforms.

Test signals: `stat_freebsd_test.go` validates mode/time and file flags after `Lchflags`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_freebsd_test.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_freebsd_test.go

Purpose: FreeBSD tests for `fromStatT` and file flag reporting.

Important APIs/types/functions: `platformTestFromStatT` compares mode and mtime; `TestFileFlags` writes a file, sets `UF_READONLY` with `Lchflags`, and checks `Stat(file).Flags()`.

Control flow: creates temporary files, applies flags, reads stat metadata, and uses fatal assertions on mismatch.

State/persistence: mutates temporary file flags and relies on cleanup of temp directories.

Dependencies/integration: exercises FreeBSD `Lchflags`, `Stat`, and `StatT.Flags`.

Risks: requires filesystem support and permissions for `chflags`; failures may be environmental rather than logical.

Test signals: strong platform signal that FreeBSD-specific flag plumbing remains wired into stat and removal support.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_freebsd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_linux.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_linux.go

Purpose: Linux conversion from `syscall.Stat_t` to the package's stable `StatT`, plus an exported converter for archive change code.

Important APIs/types/functions: `fromStatT` and exported `FromStatT`.

Control flow: copies size, mode, uid, gid, rdev, `Mtim`, and device ID to `StatT`; `FromStatT` delegates to the unexported converter.

State/persistence: no mutation; represents a stat snapshot.

Dependencies/integration: used by `Stat`, `Fstat`, and `pkg/archive/changes` on Linux.

Risks: `Rdev` and `Dev` conversions are intentionally marked with `nolint:unconvert`, so type changes in syscall definitions should be checked carefully.

Test signals: `stat_linux_test.go` and `stat_unix_test.go` verify mode, mtime, uid/gid, and rdev mapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_linux_test.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_linux_test.go

Purpose: Linux-specific assertion helper for common stat conversion tests.

Important APIs/types/functions: `platformTestFromStatT(t, stat, s)` compares raw `Mode` and `Mtim` against `StatT`.

Control flow: called by `TestFromStatT` in `stat_unix_test.go`.

State/persistence: none.

Dependencies/integration: ties Linux syscall field names to the shared stat test.

Risks: narrowly checks only mode/time; size/dev coverage would need additional tests.

Test signals: catches regressions in Linux `fromStatT` time and mode field selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_netbsd.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_netbsd.go

Purpose: NetBSD `syscall.Stat_t` conversion for the shared `StatT` abstraction.

Important APIs/types/functions: `fromStatT`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtimespec`.

State/persistence: read-only stat conversion.

Dependencies/integration: used by Unix `Stat` and `Fstat` on NetBSD.

Risks: does not populate `dev`, so callers needing filesystem identity get zero. Platform fields must stay aligned with Go's NetBSD syscall struct.

Test signals: NetBSD compile and stat behavior tests should confirm expected metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_openbsd.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_openbsd.go

Purpose: OpenBSD conversion from `syscall.Stat_t` into `StatT`.

Important APIs/types/functions: `fromStatT`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtim`.

State/persistence: no mutation.

Dependencies/integration: selected by OpenBSD build constraints for shared stat APIs.

Risks: `dev` is not populated. Cross-platform code using `Dev()` must handle zero on this platform.

Test signals: OpenBSD stat tests should validate mode, mtime, owner, and device expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_openbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_solaris.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_solaris.go

Purpose: Solaris conversion from syscall stat structures into the package's `StatT`.

Important APIs/types/functions: `fromStatT`.

Control flow: copies size, mode, uid, gid, rdev, and `Mtim`.

State/persistence: no mutation.

Dependencies/integration: selected for Solaris builds of shared stat helpers.

Risks: `dev` is not populated. Solaris field widths and semantics should be checked when updating Go versions.

Test signals: Solaris compile and stat tests should confirm metadata accessors remain correct.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_solaris.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_unix.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_unix.go

Purpose: Unix implementation of the package-neutral file stat abstraction.

Important APIs/types/functions: defines `StatT` with mode, uid, gid, rdev, size, mtime, dev, and embedded `platformStatT`; accessors `Mode`, `UID`, `GID`, `Rdev`, `Size`, `Mtim`, `Dev`, `IsDir`; and functions `Stat` and `Fstat`.

Control flow: `Stat` and `Fstat` call `syscall.Stat`/`Fstat`, wrap syscall failures in `os.PathError`, and delegate platform-specific field conversion to `fromStatT`.

State/persistence: read-only filesystem metadata snapshots.

Dependencies/integration: used across storage for ownership, size, device, and directory checks; platform conversion files supply syscall field mapping.

Risks: `Stat` follows symlinks rather than using `Lstat`. The abstraction has platform-dependent completeness, especially `Dev` and `Flags`.

Test signals: shared tests cover conversion of UID, GID, Rdev and platform mode/time; callers should also test symlink-specific needs separately.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_unix_test.go

Purpose: shared Linux/FreeBSD stat conversion test.

Important APIs/types/functions: `TestFromStatT` uses `prepareFiles`, raw `syscall.Lstat`, `fromStatT`, and platform-specific assertions.

Control flow: creates a temp file, reads syscall stat data, converts it, compares UID/GID/Rdev, then calls `platformTestFromStatT`.

State/persistence: temporary filesystem state only.

Dependencies/integration: shares `prepareFiles` with utime tests and validates platform converters.

Risks: covers Linux and FreeBSD only; other Unix converters rely mainly on compile coverage unless separate tests exist.

Test signals: catches accidental field mixups in common ownership/device metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/stat_windows.go

Purpose: Windows implementation of the `StatT` abstraction using `os.FileInfo`.

Important APIs/types/functions: defines Windows `StatT` with mode, size, mtime, embedded platform fields; accessors for `Size`, `Mode`, `Mtim`, `UID`, `GID`, `Dev`, `IsDir`; `Stat`; and `fromStatT(*os.FileInfo)`.

Control flow: `Stat` calls `os.Stat` and converts the returned file info. UID, GID, and Dev are hard-coded to zero because Windows does not expose Unix-style IDs here.

State/persistence: read-only filesystem metadata snapshot.

Dependencies/integration: lets cross-platform storage code ask for size/mode/time on Windows while tolerating missing ownership/device data.

Risks: no `Fstat` equivalent is provided in this file. Symlinks are followed via `os.Stat`. Ownership/device consumers must not treat zero as meaningful Unix ownership.

Test signals: Windows stat tests should cover file/dir mode, size, mtime, missing path errors, and zero ownership semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/stat_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/syscall_unix.go -->
# sources/cloud-native/containers-storage/pkg/system/syscall_unix.go

Purpose: Unix syscall convenience wrappers used by shared storage code.

Important APIs/types/functions: `Unmount(dest string) error`, `CommandLineToArgv(commandLine string) ([]string, error)`, and `IsEBUSY(err error) bool`.

Control flow: `Unmount` calls `unix.Unmount(dest, 0)`. `CommandLineToArgv` returns the whole string as a single element because Unix command-line parsing belongs to shells/callers. `IsEBUSY` uses `errors.Is`.

State/persistence: `Unmount` mutates mount state; the others are pure.

Dependencies/integration: `EnsureRemoveAll` uses `IsEBUSY` and mount cleanup uses `Unmount`; command-line parsing gives cross-platform callers a compile-compatible helper.

Risks: no unmount flags are exposed. The Unix `CommandLineToArgv` behavior is intentionally not shell-like and should not be used for parsing shell commands.

Test signals: tests should verify busy error recognition and unmount behavior through higher-level removal tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/syscall_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/syscall_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/syscall_windows.go

Purpose: Windows syscall helpers for OS/SKU detection, command-line parsing, win32k support, and cross-platform stubs.

Important APIs/types/functions: `OSVersion`, `GetOSVersion`, `IsWindowsClient`, `IsIoTCore`, `Unmount`, `CommandLineToArgv`, `HasWin32KSupport`, and `IsEBUSY`.

Control flow: version/SKU functions call `GetVersion`, `GetVersionExW`, and `GetProductInfo`, logging warnings and returning conservative false values on failures. `CommandLineToArgv` converts a UTF-16 command line through the Windows API and frees the returned buffer. `HasWin32KSupport` probes a lazy DLL load.

State/persistence: no persistent storage; lazy DLL handles are process state. `Unmount` is a no-op on Windows.

Dependencies/integration: used by Windows container platform checks, licensing/SKU gates, LCOW/path logic, and tests.

Risks: Windows version APIs can be manifest-sensitive. `IsWindowsClient` and `IsIoTCore` are marked as licensing-sensitive and should not be casually changed. `IsEBUSY` always false, so removal retry behavior differs from Unix.

Test signals: `syscall_windows_test.go` verifies `HasWin32KSupport` does not panic; broader Windows CI should cover command-line parsing and SKU helper behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/syscall_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/syscall_windows_test.go -->
# sources/cloud-native/containers-storage/pkg/system/syscall_windows_test.go

Purpose: smoke test for Windows win32k capability probing.

Important APIs/types/functions: `TestHasWin32KSupport`.

Control flow: calls `HasWin32KSupport` and logs the result without asserting a fixed value because host support varies.

State/persistence: none.

Dependencies/integration: exercises lazy API-set loading on Windows test hosts.

Risks: only verifies non-panic behavior, not semantic correctness.

Test signals: useful as a host-compatibility smoke test when Windows API-set availability changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/syscall_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/umask.go -->
# sources/cloud-native/containers-storage/pkg/system/umask.go

Purpose: Unix wrapper for setting the process file mode creation mask.

Important APIs/types/functions: `Umask(newmask int) (oldmask int, err error)`.

Control flow: calls `unix.Umask(newmask)` and returns the previous mask with nil error.

State/persistence: changes process-global umask, affecting future file creation in the current process.

Dependencies/integration: used by CLI or storage setup paths that need controlled file permissions.

Risks: umask is process-global and not goroutine-local; changing it in concurrent programs can affect unrelated file creation.

Test signals: tests should save/restore the original mask and avoid parallel execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/umask.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/umask_windows.go -->
# sources/cloud-native/containers-storage/pkg/system/umask_windows.go

Purpose: Windows unsupported stub for Unix umask behavior.

Important APIs/types/functions: `Umask(newmask int) (oldmask int, err error)` returns `ErrNotSupportedPlatform`.

Control flow: no state is changed.

State/persistence: none.

Dependencies/integration: allows cross-platform compilation while forcing callers to avoid umask-dependent paths on Windows.

Risks: callers that ignore the error will assume an old mask of zero.

Test signals: Windows tests should assert unsupported behavior where umask paths are reachable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/umask_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/system/utimes_freebsd.go

Purpose: FreeBSD implementation of symlink timestamp updates without following the link.

Important APIs/types/functions: `LUtimesNano(path string, ts []syscall.Timespec) error`.

Control flow: converts path to a C byte pointer and invokes `SYS_UTIMENSAT` with `AT_FDCWD` and `AT_SYMLINK_NOFOLLOW`. Non-zero errors are returned except `ENOSYS`, which is ignored.

State/persistence: mutates atime/mtime of the symlink itself.

Dependencies/integration: used by archive extraction when preserving symlink timestamps.

Risks: assumes `ts` has at least one element and takes `&ts[0]`; empty slices panic. Ignoring `ENOSYS` makes unsupported kernels look successful.

Test signals: `utimes_unix_test.go` covers symlink timestamp changes and missing-path errors on Linux/FreeBSD.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_linux.go -->
# sources/cloud-native/containers-storage/pkg/system/utimes_linux.go

Purpose: Linux implementation of no-follow nanosecond timestamp updates.

Important APIs/types/functions: `LUtimesNano(path string, ts []syscall.Timespec) error`.

Control flow: uses `unix.BytePtrFromString` and raw `SYS_UTIMENSAT` with `AT_SYMLINK_NOFOLLOW`, returning syscall errors except `ENOSYS`.

State/persistence: updates symlink metadata rather than target file metadata.

Dependencies/integration: archive extraction and layer unpacking use it to preserve symlink times.

Risks: empty `ts` slices panic; `ENOSYS` is treated as success; raw syscall use must track kernel ABI expectations.

Test signals: symlink test verifies the link mtime changes while target file mtime stays unchanged.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_unix_test.go -->
# sources/cloud-native/containers-storage/pkg/system/utimes_unix_test.go

Purpose: Linux/FreeBSD test coverage for `LUtimesNano`.

Important APIs/types/functions: `prepareFiles` creates a temp file, invalid path, and symlink; `TestLUtimesNano` updates symlink times and verifies target preservation.

Control flow: captures file mtime, sets symlink times to epoch, checks `os.Lstat` on symlink changed, checks `os.Stat` on target did not change, and expects an error for a missing path.

State/persistence: creates temporary files/symlinks and mutates symlink timestamps.

Dependencies/integration: supports both utime and stat tests.

Risks: compares seconds via `Unix()`, so subsecond precision issues are not covered. Filesystems with unusual symlink timestamp semantics may affect results.

Test signals: strong regression signal that `AT_SYMLINK_NOFOLLOW` is used and missing paths are not silently ignored.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/system/utimes_unsupported.go

Purpose: unsupported-platform stub for symlink timestamp updates.

Important APIs/types/functions: `LUtimesNano(path string, ts []syscall.Timespec) error` returns `ErrNotSupportedPlatform`.

Control flow: no syscall is attempted.

State/persistence: none.

Dependencies/integration: selected on platforms other than Linux and FreeBSD, letting callers compile and handle unsupported symlink timestamp preservation.

Risks: archive extraction on unsupported platforms may lose symlink timestamp fidelity.

Test signals: platform tests should assert unsupported errors where callers expose this behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/utimes_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_darwin.go -->
# sources/cloud-native/containers-storage/pkg/system/xattrs_darwin.go

Purpose: Darwin extended-attribute helpers for no-follow get, set, and list operations.

Important APIs/types/functions: constants `E2BIG` and `ENOTSUP`; `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: get/list start with a 128-byte buffer and retry on `ERANGE` after querying the required size. Missing attributes (`ENOATTR`) return nil data. Attribute lists are split on NUL bytes.

State/persistence: `Lsetxattr` writes filesystem xattrs; get/list read them.

Dependencies/integration: archive/layer metadata preservation and SELinux/security metadata paths use these helpers through a common API.

Risks: buffer growth depends on zero-size size queries; error wrapping preserves path but not attribute key. Darwin only defines a subset of Linux-like errno constants here.

Test signals: xattr round-trip tests should cover missing attrs, large attrs causing `ERANGE`, and symlink no-follow behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/system/xattrs_freebsd.go

Purpose: FreeBSD adapter between Linux-style xattr names and FreeBSD extattr namespaces.

Important APIs/types/functions: constants `E2BIG`, `ENOTSUP`, `EOVERFLOW`; `namespaceMap`; `xattrToExtattr`; `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: xattr names must contain a namespace prefix such as `user.` or `system.`. Get/set map the prefix to FreeBSD namespace constants and call `Extattr*Link`. List iterates namespaces and prefixes returned names.

State/persistence: set mutates extattrs; get/list read them.

Dependencies/integration: integrates common storage xattr APIs with FreeBSD extattr syscalls.

Risks: unsupported namespaces and names without dots return `ENOTSUP`. `Lsetxattr` does not implement Linux flags and rejects any non-zero flag. Map iteration order makes list order nondeterministic.

Test signals: tests should cover namespace parsing, non-zero flag rejection, list prefixing, and symlink no-follow extattr behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_linux.go -->
# sources/cloud-native/containers-storage/pkg/system/xattrs_linux.go

Purpose: Linux extended-attribute helpers for symlink-safe metadata preservation.

Important APIs/types/functions: errno aliases `E2BIG`, `ENOTSUP`, `EOVERFLOW`; `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: get/list allocate a small buffer, retry on `ERANGE` after size query, return nil for missing data (`ENODATA`), and split NUL-separated names. Set delegates to `unix.Lsetxattr` with caller-supplied flags.

State/persistence: reads and writes filesystem xattrs without following symlinks.

Dependencies/integration: used during layer unpack/diff, SELinux label handling, and metadata copy paths.

Risks: large xattrs require retry logic; unsupported filesystems surface wrapped path errors. Attribute key is not included in wrapped errors, so diagnostics may require caller context.

Test signals: xattr tests should include missing attr, large attr/list, create/replace flags, unsupported filesystem behavior, and symlink handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/system/xattrs_unsupported.go

Purpose: fallback xattr implementation for platforms without Linux/Darwin/FreeBSD support.

Important APIs/types/functions: zero-valued errno aliases and unsupported `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: all operations immediately return `ErrNotSupportedPlatform`.

State/persistence: none.

Dependencies/integration: keeps common xattr callers buildable on unsupported targets.

Risks: zero-valued errno constants are placeholders; code comparing them directly on unsupported platforms can behave unexpectedly. Metadata fidelity is lost where callers ignore unsupported errors.

Test signals: platform tests should assert unsupported return values and caller tolerance for missing xattrs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/system/xattrs_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/tarlog/tarlogger.go -->
# sources/cloud-native/containers-storage/pkg/tarlog/tarlogger.go

Purpose: provides an `io.WriteCloser` that observes a tar stream and invokes a callback for each tar header while preserving write behavior for callers.

Important APIs/types/functions: unexported `tarLogger` with pipe writer, close mutex, and closed flag; exported `NewLogger(logger func(*tar.Header)) (io.WriteCloser, error)`; methods `Write` and `Close`.

Control flow: `NewLogger` creates an `io.Pipe`, starts a goroutine with a tar reader, calls the logger for each header until `Next` errors, closes the reader, and unlocks a mutex so `Close` waits for completion. `Write` forwards bytes to the pipe and treats closed-pipe errors as successful full writes to avoid changing tar digest behavior.

State/persistence: holds in-memory pipe state and logs headers through caller-provided side effects; no persistent data.

Dependencies/integration: uses `github.com/vbatts/tar-split/archive/tar` and `logrus`. It integrates with archive/diff pipelines that want progress or audit logging while streaming tar bytes.

Risks: `closed` is accessed without synchronization between `Write` and the reader goroutine. Tar parse errors stop logging silently except reader close errors. `Close` locks the mutex but does not unlock it afterward, relying on object finality.

Test signals: `tarlogger_test.go` verifies all header names are observed for a generated archive.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/tarlog/tarlogger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/tarlog/tarlogger_test.go -->
# sources/cloud-native/containers-storage/pkg/tarlog/tarlogger_test.go

Purpose: verifies that `tarlog.NewLogger` observes tar headers in stream order.

Important APIs/types/functions: `TestTarLogger` builds 32 test files with increasing names and sizes, writes them through a tar writer backed by the logger, closes both writers, and compares logged names.

Control flow: every test case writes a header and payload; callback appends names; final assertions check count and order.

State/persistence: in-memory buffers and pipe goroutine only.

Dependencies/integration: depends on `stretchr/testify/require` and `tar-split` tar writer/reader.

Risks: does not cover malformed tar streams, concurrent writes, early close, or callback panics.

Test signals: confirms happy-path header logging without corrupting tar writer behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/tarlog/tarlogger_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/truncindex/truncindex.go -->
# sources/cloud-native/containers-storage/pkg/truncindex/truncindex.go

Purpose: maintains an index of full string IDs that can be looked up by any unique prefix, used for Docker/container-style shortened IDs.

Important APIs/types/functions: errors `ErrEmptyPrefix`, `ErrIllegalChar`, `ErrNotExist`, and `ErrAmbiguousPrefix`; type `TruncIndex` with mutex, Patricia trie, and ID set; `NewTruncIndex`, `Add`, `Delete`, `Get`, and `Iterate`.

Control flow: construction silently ignores invalid/duplicate input IDs via `addID`. `Add` validates spaces/empty/duplicates, stores the ID in a map, and inserts into the trie. `Get` visits the prefix subtree, returns the sole match, returns `ErrAmbiguousPrefix` for multiple matches, and `ErrNotExist` for none. `Delete` requires exact ID membership. `Iterate` walks all trie entries under a write lock.

State/persistence: in-memory only. The trie and map are protected by `sync.RWMutex`.

Dependencies/integration: depends on `github.com/tchap/go-patricia/v2/patricia`. Used by storage indexes where human-facing IDs can be abbreviated.

Risks: `NewTruncIndex` silently drops invalid IDs, which can hide corrupt inputs. `Iterate` uses an exclusive lock and warns handlers not to call public methods, though the test demonstrates concurrent calls block rather than panic. Error for ambiguity reports the second visited prefix, not necessarily the queried prefix.

Test signals: tests cover add/get/delete, ambiguity, illegal/empty IDs, iteration, and benchmarks for add/get/delete/new combined workloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/truncindex/truncindex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/truncindex/truncindex_test.go -->
# sources/cloud-native/containers-storage/pkg/truncindex/truncindex_test.go

Purpose: behavioral and performance tests for the truncated ID index.

Important APIs/types/functions: `TestTruncIndex`, helper assertions for get and iteration, and benchmarks for add, get, delete, construct, and add+get at 100/250/500-size labels.

Control flow: the main test creates an index, exercises empty/nonexistent/illegal IDs, verifies exact and prefix lookups, introduces a conflicting ID, checks ambiguity, deletes the conflict, and checks iteration. Benchmarks generate random non-crypto IDs and measure core operations.

State/persistence: in-memory test indexes only.

Dependencies/integration: uses `pkg/stringid`, `math/rand/v2`, `slices`, and `testify/require`.

Risks: benchmark names for `BenchmarkTruncIndexAddGet100/250/500` all generate 500 IDs, so labels do not match workload size. Iteration concurrency test only asserts no panic/error, not timing or absence of deadlock beyond the test's natural completion.

Test signals: strong coverage for prefix uniqueness semantics and basic lock behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/truncindex/truncindex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_cgo.go -->
# sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_cgo.go

Purpose: cgo-backed environment lookup for Linux builds using cgo.

Important APIs/types/functions: `getenv(name string) string`, calling C `getenv`.

Control flow: converts the Go string to a C string, defers `free`, calls `C.getenv`, and converts the returned pointer to a Go string.

State/persistence: reads process environment; no mutation.

Dependencies/integration: used by Linux rootless/unshare helpers to read environment variables that may be set before Go runtime initialization or by C constructor code.

Risks: `C.GoString(nil)` returns an empty string, matching expected missing variable behavior. cgo availability changes which file supplies `getenv`, so behavior should remain aligned with the non-cgo implementation.

Test signals: rootless environment tests should cover `_CONTAINERS_ROOTLESS_UID/GID` and `_CONTAINERS_USERNS_CONFIGURED` under cgo builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_nocgo.go -->
# sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_nocgo.go

Purpose: non-cgo Linux implementation of unshare package environment lookup.

Important APIs/types/functions: `getenv(name string) string` delegates to `os.Getenv`.

Control flow: direct return of the Go runtime environment value.

State/persistence: reads process environment.

Dependencies/integration: keeps rootless/unshare logic available in `CGO_ENABLED=0` builds.

Risks: must remain semantically aligned with the cgo C `getenv` variant.

Test signals: non-cgo builds should exercise rootless environment parsing and namespace reexec decisions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/getenv_linux_nocgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare.c -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare.c

Purpose: Linux C constructor implementation that performs early namespace unshare and reexec before Go code starts.

Important APIs/types/functions: `_containers_unshare`, `_containers_unshare_parse_envint`, `_check_proc_sys_file`, `parse_proc_stringlist`, `try_bindfd`, `copy_self_proc_exe`, and `containers_reexec`.

Control flow: constructor reads `_Containers-unshare`; if absent it returns. It unshares user namespace first, writes child PID to the parent pipe, waits on the continue pipe for parent UID/GID map setup, optionally calls `setsid`, `setpgrp`, and `TIOCSCTTY`, sets uid/gid to 0 inside new userns, unshares remaining namespace flags, then reexecs the current binary via a protected bind-mounted fd or sealed memfd copy.

State/persistence: mutates process namespaces, uid/gid, session/process group, controlling terminal, environment variables, and can temporarily create a `/tmp/containers.XXXXXX` mount point/file.

Dependencies/integration: driven by environment and file descriptors set in `unshare_linux.go` `Cmd.Start`. Integrates with `/proc`, Linux clone flags, memfd sealing, mount APIs, and reexec behavior.

Risks: this is security-sensitive process bootstrap code. It exits the process on parse/syscall/setup errors. Reexec fallback must avoid writable executable fds; failure to detach temporary bind mounts is treated as unrecoverable. It prints diagnostics to stderr and checks kernel userns sysctls only after unshare failure.

Test signals: `unshare_test.go` validates namespace changes and ID mappings from the Go side; lower-level C paths are indirectly covered by successful reexec and synchronization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare.go

Purpose: shared unshare package helper for resolving the current user's home directory.

Important APIs/types/functions: package-level `homeDirOnce`, `homeDirErr`, `homeDir`; `HomeDir() (string, error)`.

Control flow: `HomeDir` caches the first result. It prefers `$HOME`; if unset, it looks up the user by `GetRootlessUID()` and returns that user's home directory.

State/persistence: process-local cached home directory and error via `sync.Once`.

Dependencies/integration: used by rootless storage configuration paths that need a stable home directory. Depends on platform `GetRootlessUID`.

Risks: cache does not update if `$HOME` or rootless UID changes later in process lifetime. User lookup can fail in minimal containers or NSS-restricted environments.

Test signals: tests should cover `$HOME` set, `$HOME` missing with user lookup, and lookup failure/caching behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_cgo.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_cgo.go

Purpose: cgo link hook for Linux and FreeBSD unshare C constructors.

Important APIs/types/functions: C constructor `init` calling external `_containers_unshare`.

Control flow: when the package is linked, the C constructor runs before Go initialization and delegates to platform `_containers_unshare`.

State/persistence: may trigger early namespace/session setup through the C implementation based on environment variables.

Dependencies/integration: selected for Linux cgo non-gccgo and FreeBSD cgo builds; paired with `unshare.c` or `unshare_freebsd.c`.

Risks: constructor side effects happen before normal Go code, so environment variables and file descriptors must be correct. Build tags are critical to avoid compiling the wrong C implementation.

Test signals: unshare command tests indirectly verify the constructor runs and synchronizes with Go parent code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_darwin.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_darwin.go

Purpose: Darwin rootless/unshare compatibility implementation for an OS without Linux user namespaces.

Important APIs/types/functions: `UsernsEnvName`, `IsRootless`, `GetRootlessUID`, `GetRootlessGID`, `RootlessEnv`, `MaybeReexecUsingUserNamespace`, `GetHostIDMappings`, and `ParseIDMappings`.

Control flow: Darwin always reports rootless true, returns host uid/gid, appends an empty userns marker to env, makes reexec a no-op, returns nil host mappings, and delegates explicit mapping parsing to `idtools.ParseIDMap`.

State/persistence: reads environment and uid/gid; no namespace mutation.

Dependencies/integration: lets higher-level rootless storage paths compile and run on macOS while avoiding Linux namespace operations.

Risks: always-rootless behavior may affect feature gating. `RootlessEnv` sets `_CONTAINERS_USERNS_CONFIGURED=` with an empty value, unlike Linux's `done`.

Test signals: Darwin tests should cover mapping parsing and rootless env expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.c -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.c

Purpose: FreeBSD C constructor support for parent/child startup synchronization and session/process-group setup.

Important APIs/types/functions: `_containers_unshare_parse_envint` and `_containers_unshare`.

Control flow: reads pipe fd environment values, writes child PID to the parent, waits on the continue pipe, optionally calls `setsid`, `setpgrp(0,0)`, and `TIOCSCTTY`.

State/persistence: mutates session, process group, controlling terminal, and consumes environment variables. It does not create Linux-style namespaces.

Dependencies/integration: coordinated by `unshare_freebsd.go` `Cmd.Start` through extra files and environment.

Risks: exits the process on malformed env or setup failures. It shares the early-constructor risks of the Linux C path but with fewer features.

Test signals: FreeBSD command tests should verify PID synchronization, `Setsid`, `Setpgrp`, and controlling terminal behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.go

Purpose: FreeBSD Go wrapper for starting reexec commands with early C-side synchronization and optional session/process group setup.

Important APIs/types/functions: `Cmd` struct, `Command`, `Start`, `Run`, unsupported `CombinedOutput`/`Output`, `Runnable`, and `ExecRunnable`.

Control flow: `Start` locks the OS thread, sets environment instructions, creates PID and continue pipes, starts the reexec command, reads the child's C-reported PID, runs an optional hook, and returns so closing the continue pipe lets the child proceed. `Run` waits, and `ExecRunnable` exits with the child status or signal-derived status.

State/persistence: starts child processes, manipulates environment/extra files, and may change child session/process group/controlling terminal through C code.

Dependencies/integration: uses `pkg/reexec`, `logrus`, and the FreeBSD C constructor. Provides an API parallel to Linux for callers that do not need user namespace mappings.

Risks: if hook fails, the error is written to the child continue pipe but cleanup/kill behavior is less defensive than Linux. Output capture methods are intentionally unimplemented.

Test signals: FreeBSD tests should cover hook failure propagation, PID parsing, session and pgrp options, and exit-code preservation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_gccgo.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_gccgo.go

Purpose: gccgo-specific cgo hook ensuring the C constructor for Linux unshare is linked.

Important APIs/types/functions: imports C constructor and defines exported `AlwaysFalse` used in `init`.

Control flow: the ordinary C constructor calls `_containers_unshare`; additionally, `init` contains an unreachable reference to `C.init()` behind `AlwaysFalse` so gccgo links the symbol despite optimizer behavior.

State/persistence: same early constructor side effects as `unshare_cgo.go` when environment requests unshare.

Dependencies/integration: selected for `linux && cgo && gccgo`; works around a gccgo linker issue noted in comments.

Risks: subtle build-toolchain compatibility file; removing the dead-looking reference can break gccgo builds.

Test signals: gccgo build/namespace smoke tests are the key signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_gccgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_linux.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_linux.go

Purpose: Linux process wrapper and rootless/user-namespace support for containers/storage.

Important APIs/types/functions: `Cmd` with namespace flags, newuidmap/newgidmap controls, UID/GID mappings, session options, OOM score, and hook; `Command`, `Start`, `Run`, `MaybeReexecUsingUserNamespace`, `ExecRunnable`, `GetHostIDMappings`, `GetSubIDMappings`, `ParseIDMappings`, `IsRootless`, `HasCapSysAdmin`, and `IsSetID`.

Control flow: `Cmd.Start` locks the OS thread, encodes namespace instructions in env vars, starts a reexec child, reads the child PID from the C constructor, writes setgroups/uid_map/gid_map through `/proc` or `newuidmap/newgidmap`, writes `oom_score_adj`, runs a hook, and releases the continue pipe. `MaybeReexecUsingUserNamespace` decides whether a new userns is needed, constructs mappings from `/etc/subuid`/`subgid` or current maps, sets rootless environment, forwards signals, sets `Pdeathsig`, and exits with the child status through `ExecRunnable`.

State/persistence: starts and controls child processes, mutates `/proc/<pid>` mapping files and OOM score, changes process environment, caches rootless/capability checks, and uses subuid/subgid configuration.

Dependencies/integration: tightly integrated with `pkg/reexec`, the C constructor in `unshare.c`, `idtools`, OCI `LinuxIDMapping`, Linux capabilities, `/proc`, and rootless Buildah/Podman environment conventions.

Risks: security-sensitive and race-sensitive. Mapping setup must happen while the child is paused; failures kill/wait the child. Fallback from `newuidmap/newgidmap` to single mapping can reduce namespace range. `IsRootless`/`HasCapSysAdmin` cache results and may not reflect later environment/capability changes. Some warnings are logged rather than returned in rootless reexec setup.

Test signals: `unshare_test.go` exercises namespace changes, process group/session changes, OOM score, and UID/GID map round trips under Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_test.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_test.go

Purpose: Linux integration tests for the unshare command wrapper and C constructor path.

Important APIs/types/functions: `TestMain`, reexec handler `report`, `CloneFlags`, `Report`, and tests `TestUnshareNamespaces`, `TestUnsharePgrp`, `TestUnshareSid`, `TestUnshareOOMScoreAdj`, and `TestUnshareIDMappings`.

Control flow: registers a child command that reports namespace symlink targets, uid/gid maps, pgrp, sid, and OOM score as JSON. Tests run that command through `Command`, configure flags/options, decode JSON, and compare child state to parent expectations.

State/persistence: creates child processes and user namespaces; reads `/proc/self/ns`, `/proc/self/oom_score_adj`, and uid/gid maps.

Dependencies/integration: validates Go `Cmd.Start`, C early unshare, reexec, Linux `/proc`, and capability-dependent namespace behavior.

Risks: tests require kernel support for user namespaces and relevant clone flags; unprivileged CI may fail if userns is disabled. The tests are Linux-only.

Test signals: strong end-to-end signal for synchronization, namespace creation, ID mapping, session/pgrp, and OOM score setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported.go

Purpose: generic non-Linux/non-Darwin unshare compatibility layer.

Important APIs/types/functions: `UsernsEnvName`, `IsRootless`, `GetRootlessUID`, `GetRootlessGID`, `RootlessEnv`, `MaybeReexecUsingUserNamespace`, `GetHostIDMappings`, `ParseIDMappings`, and `HasCapSysAdmin`.

Control flow: reports rootless as `os.Getuid() != 0`, returns current uid/gid, appends an empty userns env marker, no-ops reexec, returns nil host mappings and parsed mappings, and treats euid 0 as CAP_SYS_ADMIN.

State/persistence: reads uid/gid and environment; no namespace mutation.

Dependencies/integration: lets unsupported Unix-like targets compile shared rootless code.

Risks: `ParseIDMappings` ignores inputs and errors, unlike Linux/Darwin, so callers may believe unsupported mappings were accepted. CAP_SYS_ADMIN semantics are approximated by euid.

Test signals: unsupported-platform tests should assert no-op behavior and ensure callers do not rely on actual userns mappings.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported_cgo.go -->
# sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported_cgo.go

Purpose: cgo placeholder for platforms that have C files in the package but no usable unshare C implementation.

Important APIs/types/functions: imports C with `CPPFLAGS: -DUNSHARE_NO_CODE_AT_ALL`.

Control flow: no operational C code is compiled; the import satisfies Go's cgo package requirements.

State/persistence: none.

Dependencies/integration: selected for cgo builds outside Linux/FreeBSD.

Risks: build plumbing only; changing tags can accidentally expose Linux/FreeBSD C code to unsupported platforms.

Test signals: cgo compile tests on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported_cgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/storage.conf -->
# sources/cloud-native/containers-storage/storage.conf

Purpose: sample/default containers/storage configuration file documenting storage roots, driver selection, read-only image stores, pull behavior, auto-userns settings, and overlay driver options.

Important APIs/types/functions: TOML tables `[storage]`, `[storage.options]`, `[storage.options.pull_options]`, and `[storage.options.overlay]`. Active defaults include `driver = "overlay"`, `runroot = "/run/containers/storage"`, `graphroot = "/var/lib/containers/storage"`, empty `additionalimagestores`, and overlay `mountopt = "nodev"`.

Control flow: configuration precedence is documented in comments; actual parsing is handled by the `types` package and exposed through helpers in `store.go`.

State/persistence: defines persistent storage locations and behavior for engines using the library. Options can affect image/layer contents, metadata persistence, and mount behavior.

Dependencies/integration: consumed by containers/storage users such as Podman/Buildah through `types.Options`/config reload. Pull options integrate with zstd:chunked, hard links, ostree repos, and integrity policy.

Risks: comments warn that `force_mask` can expose files like `/etc/shadow` when set to shared permissions, and that `insecure_allow_unpredictable_image_contents` should almost never be enabled. Changing graphroot on SELinux systems requires relabeling.

Test signals: config parser tests should verify string-bool handling, precedence, overlay mount option extraction, rootless path expansion, and defaults matching this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/storage.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/store.go -->
# sources/cloud-native/containers-storage/store.go

Purpose: central public façade for containers/storage, coordinating graph drivers, layer/image/container metadata stores, big-data blobs, mounts, diffs, deletion, configuration helpers, additional image stores, and deduplication.

Important APIs/types/functions: defines the large `Store` interface; option/result types such as `LayerOptions`, `ImageOptions`, `ContainerOptions`, `ApplyStagedLayerOptions`, `MultiListOptions`, `DedupArgs`, and `AdditionalLayer`; singleton creation via `GetStore`; core methods for create/delete/list/lookup/mount/diff/apply/size/big-data/name updates; config helpers `DefaultConfigFile`, `ReloadConfigurationFile`, `GetMountOptions`; lifecycle methods `Shutdown`, `Free`, `GarbageCollect`, `MultiList`, and `Dedup`.

Control flow: `GetStore` normalizes/defaults options, reuses matching existing stores, creates roots/locks, constructs graph driver, and initializes image/container/digest lock stores. Most operations go through locking helpers that open layer/image/container stores in a documented hierarchy. Layer creation resolves parents across writable and read-only stores, inherits or applies ID mappings, optionally uses shifting, and delegates to layer store creation. Image/container creation validates references, copies options defensively, supports mapped top layers for ID mapping, initializes SELinux labels, and rolls back created layers on container-record failures. Delete paths check references and use deferred cleanup. Mount/diff paths hold graph locks because graph driver state can be reinitialized and naive diff can mount. Size and lookup methods traverse layers and big-data stores. Shutdown optionally unmounts layers, records graph lock writes, and runs driver cleanup.

State/persistence: manages persistent graphroot metadata, optional imagestore metadata, runroot runtime metadata, lock files, digest locks, layer contents, image/container JSON, big-data files, user data directories, mount counts, and transient-store behavior. Package-level `stores` caches store singletons.

Dependencies/integration: imports built-in graph drivers for registration; depends on driver interfaces, layer/image/container store implementations in the same package, `idtools`, `archive`, `directory`, `lockfile`, `tempdir`, `system.EnsureRemoveAll`, SELinux labels, OCI digests, and the `types` configuration package. Integrates with reexec-driven diff/mount paths and additional layer store drivers.

Risks: high-concurrency code depends on strict lock ordering and several comments identify locking bugs or FIXME areas. `Free` modifies the global `stores` slice without taking `storesLock`. Generic read helpers defer unlocks inside loops, holding all previously opened stores until return. Deletion APIs are intentionally powerful and `Delete` skips some safety checks. ID-mapped layer creation and read-only image-store pull-up are subtle. Mount-count return values are explicitly stale-prone.

Test signals: `store_test.go` covers broad interface error behavior, split image store setup, `MultiList`, and deletion cleanup. More targeted tests should cover concurrency, read-only additional stores, mapped top layers, transient stores, staged layers, dedup, and config parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/store_test.go -->
# sources/cloud-native/containers-storage/store_test.go

Purpose: broad smoke and regression tests for the public `Store` façade.

Important APIs/types/functions: `newTestStore`, `TestStore`, `TestWithSplitStore`, `TestStoreMultiList`, and `TestStoreDelete`.

Control flow: `newTestStore` creates temp run/graph roots, defaults to `vfs`, and supplies single-ID uid/gid maps. `TestStore` and `TestWithSplitStore` call most public methods against missing IDs to assert expected errors or empty success paths. `TestStoreMultiList` creates a layer/image/container and verifies selective listing counts. `TestStoreDelete` creates two images/containers and an unused layer, deletes them, and verifies the store returns to the initial state.

State/persistence: uses temporary storage roots and the vfs driver; creates and deletes real storage metadata and layer directories. Calls `Shutdown` and `Free` to release store state.

Dependencies/integration: depends on `pkg/reexec`, `idtools`, OCI digest, and testify. Exercises top-level integration with graph drivers and store metadata implementations.

Risks: many assertions are smoke-level and only check error presence, not specific error types. `reexec.Init()` is called inside some tests rather than `TestMain`, which is adequate for these paths but less comprehensive than unshare tests. Concurrency and additional read-only stores are not deeply covered.

Test signals: useful guard that the public API remains callable, split image stores initialize, `MultiList` is consistent, and delete operations clean up created objects.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/store_test.go -->
