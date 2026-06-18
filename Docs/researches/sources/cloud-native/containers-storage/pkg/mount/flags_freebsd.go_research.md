# sources/cloud-native/containers-storage/pkg/mount/flags_freebsd.go

Purpose: maps mount flag constants to FreeBSD `unix.MNT_*` values and zeroes unsupported Linux-style flags.

Important APIs, types, and functions: constants `RDONLY`, `NOSUID`, `NOEXEC`, `SYNCHRONOUS`, `REMOUNT`, `NOATIME`, `mntDetach`, and zero-valued unsupported flags such as `BIND`, `RPRIVATE`, and `RELATIME`.

Control flow: no runtime flow; constants are used by option parsing and mount/unmount wrappers.

State and persistence: no state. The constants influence kernel mount calls on FreeBSD.

Dependencies and integration points: depends on `golang.org/x/sys/unix`; selected for FreeBSD builds. Integrated with `flags.go`, `mounter_freebsd.go`, and `unmount_unix.go`.

Risks and edge cases: Linux-specific options silently become data or no-ops because constants are zero. FreeBSD bind behavior is emulated in `mounter_freebsd.go` via `nullfs`.

Test signals: no FreeBSD-specific tests in the requested files; correctness is mostly compile-time plus platform integration tests elsewhere.
