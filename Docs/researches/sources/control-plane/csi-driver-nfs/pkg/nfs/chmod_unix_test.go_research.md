<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix_test.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix_test.go

## Purpose
Tests that Unix chmod behavior preserves special permission bits when `chmodIfPermissionMismatch` adjusts NFS volume directories.

## Important APIs, Types, and Functions
The file is `!windows` only and defines `TestChmodIfPermissionMismatchSpecialBits`. It uses `t.TempDir`, `os.Mkdir`, `syscall.Chmod`, `chmodIfPermissionMismatch`, `os.Lstat`, and `syscall.Stat_t`.

## Control Flow, State, and Persistence
For each table case, the test creates a directory, sets an initial raw mode, calls `chmodIfPermissionMismatch` with the requested mode, then reads raw mode bits via `Stat_t.Mode & 07777` and compares them to the expected requested mode. Temp directories are automatically cleaned up by the test framework.

## Dependencies and Integration Points
It validates the Unix implementation in `chmod_unix.go` and the permission mismatch helper in `utils.go`. It protects controller/node code that applies `mountPermissions` to provisioned directories.

## Risks and Test Signals
Risks include running on filesystems that ignore special bits, OS-specific permission semantics, and test exclusion on Windows. Signals are exact preservation of setgid, sticky, already-set setgid, and setuid cases.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix_test.go -->
