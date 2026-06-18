# sources/cloud-native/containers-storage/drivers/aufs/mount.go

## Purpose
`mount.go` provides AUFS unmount cleanup. It flushes AUFS state with `auplink` before invoking the kernel unmount syscall.

## Important APIs, Types, And Functions
`Unmount(target string) error` runs `auplink <target> flush`, logs a warning if that command fails, then calls `unix.Unmount(target, 0)`.

## Control Flow
`Driver.unmount`, `Remove`, `Cleanup`, and error cleanup in `aufsMount` all funnel through this helper. `auplink` failure is non-fatal because the actual unmount remains authoritative.

## State And Persistence
It does not persist Go state. It affects kernel mount state and may flush AUFS branch metadata before unmounting.

## Dependencies And Integration Points
It depends on `os/exec`, `logrus`, and `x/sys/unix`. It assumes `auplink` may be available on AUFS systems.

## Risks
If `auplink` is missing or fails, stale AUFS state may be harder to diagnose, though unmount can still succeed. Busy mountpoints surface as syscall errors to callers that implement retry or logging.

## Test Signals
AUFS mount/unmount tests and cleanup tests exercise this helper indirectly. Real coverage requires a kernel with AUFS and mount privileges.
