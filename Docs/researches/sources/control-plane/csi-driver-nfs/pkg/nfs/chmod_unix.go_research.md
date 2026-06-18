<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix.go -->
# sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix.go

## Purpose
Provides the Unix implementation of the package-local `chmod` helper, preserving raw permission bits including setuid, setgid, and sticky bits.

## Important APIs, Types, and Functions
The file is built with `//go:build !windows` and imports `syscall`. Its only function is `chmod(path string, mode uint32) error`, which calls `syscall.Chmod(path, mode)`.

## Control Flow, State, and Persistence
Callers such as `chmodIfPermissionMismatch` delegate final permission changes to this function. The state change is filesystem metadata on the target path.

## Dependencies and Integration Points
It integrates with volume directory creation in `controllerserver.go` and node publish behavior in related helpers. It exists because `os.Chmod` with `os.FileMode` can mishandle special raw Unix bits in this code path.

## Risks and Test Signals
Risks include platform-specific syscall behavior, NFS server permission semantics, and failure under restricted permissions. Signals are tests proving modes such as `02770`, `01777`, and `04755` are applied exactly on Unix.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/pkg/nfs/chmod_unix.go -->
