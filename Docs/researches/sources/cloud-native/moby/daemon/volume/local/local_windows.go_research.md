# sources/cloud-native/moby/daemon/volume/local/local_windows.go

## Purpose
Windows implementation of local driver platform hooks, where local volume mount options are unsupported.

## Important APIs, Types, And Functions
Defines empty `optsConfig`. Implements no-op or rejecting variants of `validateOpts`, `setOpts`, `needsMount`, `mount`, `unmount`, `postMount`, `restoreIfMounted`, and `CreatedAt` using Windows creation time.

## Control Flow
Any non-empty options map is rejected as invalid parameter. Mount-related methods do nothing and report no mount requirement. `CreatedAt` reads `Win32FileAttributeData.CreationTime` from the volume root.

## State And Persistence
No option state is persisted on Windows. Volume directory state is managed by common local code.

## Dependencies And Integration Points
Completes the local driver interface for Windows builds and integrates with common create/remove/list logic.

## Risks
Callers must not assume option support or mount refcount behavior on Windows. The empty `unmount` function is retained for platform compatibility and should not be mistaken for production unmounting.

## Test Signals
Common local tests run with Windows skips where needed; Windows-specific creation time is not directly tested in this subset.
