<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.h -->
# sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.h

Purpose: Declares shared DIAG 204/224 hypfs helpers and config-gated filesystem formatting hooks.

Important APIs/types/functions: Declares `diag204_get_info_type()`, `diag204_get_buffer()`, `diag204_store()`, `__hypfs_diag_fs_init()`, and `__hypfs_diag_fs_exit()`. Inline wrappers `hypfs_diag_fs_init()` and `hypfs_diag_fs_exit()` call the filesystem hooks only when `CONFIG_S390_HYPFS_FS` is enabled.

Control flow: Header-only config gating; no local runtime logic beyond inline wrappers.

State and persistence: No local state; shared state is in `hypfs_diag.c`.

Dependencies and integration points: Included by DIAG 204 raw and filesystem formatting files. Depends on `asm/diag.h` for `enum diag204_format`.

Risks: Incorrect config gating can create unresolved references or skip required init. Function signature drift breaks diag consumers.

Test signals: Build matrix for `CONFIG_S390_HYPFS_FS` and DIAG formatting initialization/exit.

Source read size: 35 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/hypfs/hypfs_diag.h -->
