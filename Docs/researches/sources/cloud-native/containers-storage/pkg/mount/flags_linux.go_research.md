# sources/cloud-native/containers-storage/pkg/mount/flags_linux.go

Purpose: maps package mount constants to Linux `unix.MS_*` and unmount constants.

Important APIs, types, and functions: constants for read-only, nosuid, nodev, noexec, sync, dirsync, remount, mandatory lock, atime, bind/rbind, propagation modes, relatime/strictatime, and `mntDetach`.

Control flow: no runtime control flow; constants feed parsing and syscall wrappers.

State and persistence: no state. Values control kernel mount/unmount behavior when passed to `unix.Mount` or `unix.Unmount`.

Dependencies and integration points: depends on `golang.org/x/sys/unix`; selected for Linux. Used by `flags.go`, `mounter_linux.go`, `sharedsubtree_linux.go`, and unmount helpers.

Risks and edge cases: flag combinations can require multi-step mount calls, handled in `mounter_linux.go`. Future kernel options would require updating this map.

Test signals: Linux mount tests validate many combinations of bind, ro/rw, remount, and propagation flags.
