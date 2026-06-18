<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/adfs/Kconfig

## Purpose
This Kconfig fragment exposes Acorn Disc Filing System support and optional experimental write support.

## Important APIs, types, and functions
It defines `CONFIG_ADFS_FS` and `CONFIG_ADFS_FS_RW`. `ADFS_FS` depends on `BLOCK` and selects `BUFFER_HEAD`; write support depends on `ADFS_FS`.

## Control flow
At configuration time, enabling `ADFS_FS` includes the adfs module/built-in objects. Enabling `ADFS_FS_RW` allows directory update paths that otherwise return `-EINVAL`.

## State and persistence
Only `.config` state is persisted. Runtime write behavior is gated by compiled config checks.

## Dependencies and integration points
It integrates ADFS with block devices, buffer heads, and the miscellaneous filesystem menu.

## Risks and test signals
Risks include users enabling experimental writes on fragile media and blockless configs exposing ADFS. Test signals include read-only and RW builds, module builds, and write path gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/adfs/Kconfig -->
