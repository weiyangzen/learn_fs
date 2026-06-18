# sources/cloud-native/containers-storage/pkg/system/utimes_freebsd.go

Purpose: FreeBSD implementation of symlink timestamp updates without following the link.

Important APIs/types/functions: `LUtimesNano(path string, ts []syscall.Timespec) error`.

Control flow: converts path to a C byte pointer and invokes `SYS_UTIMENSAT` with `AT_FDCWD` and `AT_SYMLINK_NOFOLLOW`. Non-zero errors are returned except `ENOSYS`, which is ignored.

State/persistence: mutates atime/mtime of the symlink itself.

Dependencies/integration: used by archive extraction when preserving symlink timestamps.

Risks: assumes `ts` has at least one element and takes `&ts[0]`; empty slices panic. Ignoring `ENOSYS` makes unsupported kernels look successful.

Test signals: `utimes_unix_test.go` covers symlink timestamp changes and missing-path errors on Linux/FreeBSD.
