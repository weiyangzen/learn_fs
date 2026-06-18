<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/wrappers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/wrappers.h

## Purpose
This header supplies thin syscall wrappers and fallback constants for newer mount API operations used by filesystem selftests on systems whose libc/kernel headers may be older.

## Important APIs, Types, And Functions
The exported inline wrappers are `sys_fsopen()`, `sys_fsconfig()`, `sys_fsmount()`, `sys_mount()`, `sys_move_mount()`, and `sys_open_tree()`. It also defines compatibility values for `STATX_MNT_ID_UNIQUE`, `MOVE_MOUNT_F_EMPTY_PATH`, `MOVE_MOUNT_T_EMPTY_PATH`, `OPEN_TREE_CLONE`, `OPEN_TREE_CLOEXEC`, `AT_RECURSIVE`, and architecture-specific syscall numbers for `move_mount` and `open_tree`.

## Control Flow
Each wrapper forwards directly to `syscall()` with the appropriate `__NR_*` number. There is no branching beyond compile-time architecture fallback selection.

## State And Persistence
The header has no state. State changes occur only when callers invoke mount syscalls that create fs contexts, configure mounts, clone/open mount trees, or move mounts.

## Dependencies And Integration Points
It integrates tests with Linux's new mount API and raw syscall ABI. It depends on `<linux/mount.h>`, `<sys/syscall.h>`, and architecture preprocessor definitions such as `_MIPS_SIM`.

## Risks
Hard-coded syscall numbers must stay aligned with architecture ABIs. Because wrappers return raw syscall results, callers must handle `-1` and `errno` themselves.

## Test Signals
Build success on architectures with and without libc definitions and runtime mount API tests that either succeed or fail with expected `ENOSYS`/permission errors validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/wrappers.h -->
