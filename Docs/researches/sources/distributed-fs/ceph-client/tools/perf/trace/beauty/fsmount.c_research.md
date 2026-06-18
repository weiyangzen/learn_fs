# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.c

## Purpose
This formatter decodes `fsmount`/mount attribute flags, including the special zero-valued relative-atime mode.

## Important APIs, Types, And Functions
It includes generated `fsmount_arrays.c`, defines `strarray__fsmount_attr_flags`, and exposes `syscall_arg__scnprintf_fsmount_attr_flags()`. It defines fallbacks for `MOUNT_ATTR__ATIME` and `MOUNT_ATTR_RELATIME`.

## Control Flow
The helper first prints generated flags only if bits outside the atime mask are set. It then checks whether the atime mask equals `MOUNT_ATTR_RELATIME` and appends `RELATIME`, with optional `MOUNT_ATTR_` prefix. The public function reads `arg->val` and delegates.

## State, Dependencies, And Integration
No persistent state is used. The generated array comes from `fsmount.sh`, and the public formatter is declared as `SCA_FSMOUNT_ATTR_FLAGS` in `beauty.h`.

## Risks And Test Signals
Zero-valued flags are awkward in bitmask printers; this file's explicit `RELATIME` handling is the critical edge. Tests should cover zero/relative-atime, non-atime flags, and combinations with noatime/strictatime if present in generated data.
