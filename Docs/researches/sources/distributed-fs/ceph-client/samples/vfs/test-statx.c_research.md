# sources/distributed-fs/ceph-client/samples/vfs/test-statx.c

## Purpose
`test-statx.c` exercises the `statx()` syscall and prints returned file metadata in a format close to `/bin/stat`, with optional raw hex dumping.

## APIs, Types, And Functions
It defines a raw `statx()` wrapper, `print_time()` for timestamp formatting, `dump_statx()` for structured metadata, and `dump_hex()` for raw buffer inspection. Command flags are `-F`, `-D`, `-L`, `-O`, `-A`, and `-R`.

## Control Flow
`main()` starts with `STATX_BASIC_STATS | STATX_BTIME` and `AT_SYMLINK_NOFOLLOW`. Options adjust sync behavior, symlink following, automount suppression, basic-stat request masking, and raw output. Each remaining argv path is passed to `statx(AT_FDCWD, ...)`, then optionally dumped as hex before formatted fields are printed.

## State And Persistence
State is transient per invocation: flags, mask, raw flag, and `struct statx`. The program is read-only and does not persist data.

## Dependencies And Integration Points
It depends on Linux `statx` UAPI, raw syscall numbers, libc time formatting, and header workarounds for glibc/kernel macro conflicts. It integrates with filesystem metadata and attribute-mask validation.

## Risks And Test Signals
Risks include unsupported `statx`, filesystem-specific missing mask bits, and local timezone formatting differences. Test signals include expected values for regular files, symlinks with and without `-L`, raw dumps matching structure size, and proper errors for inaccessible paths.
