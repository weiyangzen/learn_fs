# sources/cloud-native/containers-storage/pkg/system/utimes_linux.go

Purpose: Linux implementation of no-follow nanosecond timestamp updates.

Important APIs/types/functions: `LUtimesNano(path string, ts []syscall.Timespec) error`.

Control flow: uses `unix.BytePtrFromString` and raw `SYS_UTIMENSAT` with `AT_SYMLINK_NOFOLLOW`, returning syscall errors except `ENOSYS`.

State/persistence: updates symlink metadata rather than target file metadata.

Dependencies/integration: archive extraction and layer unpacking use it to preserve symlink times.

Risks: empty `ts` slices panic; `ENOSYS` is treated as success; raw syscall use must track kernel ABI expectations.

Test signals: symlink test verifies the link mtime changes while target file mtime stays unchanged.
