# sources/cloud-native/containerd/internal/fsview/overlay_linux.go

## Purpose
Provides Linux-specific xattr and whiteout detection used by the userspace overlay filesystem.

## Important APIs, Types, And Functions
`getxattr` reads xattrs from `*os.File` using `unix.Fgetxattr` or delegates to registered handlers. `isOpaque` checks overlay opaque xattrs for value `y`. `isWhiteout` detects character device entries with `Rdev == 0` or delegates to handlers.

## Control Flow
Overlay code calls these helpers while scanning layers. Native Linux files use syscalls first; non-native fs implementations can participate through registered handlers.

## State And Persistence
No state beyond global registered handlers maintained in `register.go`.

## Dependencies And Integration Points
Uses `io/fs`, `os`, `syscall`, `golang.org/x/sys/unix`, and fsview plugin registration.

## Risks
Fixed 256-byte xattr buffer is sufficient for opaque marker values but not general xattr reads. Whiteout detection relies on `syscall.Stat_t` for native files.

## Test Signals
Linux overlay tests exercise `user.overlay.opaque` and whiteout behavior.
