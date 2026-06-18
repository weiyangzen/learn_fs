# sources/cloud-native/containers-storage/pkg/system/umask_windows.go

Purpose: Windows unsupported stub for Unix umask behavior.

Important APIs/types/functions: `Umask(newmask int) (oldmask int, err error)` returns `ErrNotSupportedPlatform`.

Control flow: no state is changed.

State/persistence: none.

Dependencies/integration: allows cross-platform compilation while forcing callers to avoid umask-dependent paths on Windows.

Risks: callers that ignore the error will assume an old mask of zero.

Test signals: Windows tests should assert unsupported behavior where umask paths are reachable.
