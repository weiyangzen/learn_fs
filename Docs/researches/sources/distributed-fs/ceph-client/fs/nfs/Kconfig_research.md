<!-- Source: sources/distributed-fs/ceph-client/fs/nfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/nfs/Kconfig

## Purpose
Defines kernel configuration options for the NFS client, supported protocol versions/features, pNFS layout modules, local caching, root-over-NFS, DNS behavior, debugging, UDP disabling, and NFSv4.2 READ_PLUS.

## Important APIs, Types, And Functions
This is Kconfig data, not C code. Important symbols include `NFS_FS`, `NFS_V2`, `NFS_V3`, `NFS_V3_ACL`, `NFS_V4`, `NFS_SWAP`, `NFS_V4_0`, `NFS_V4_2`, `PNFS_FILE_LAYOUT`, `PNFS_BLOCK`, `PNFS_FLEXFILE_LAYOUT`, `NFS_FSCACHE`, `ROOT_NFS`, `NFS_USE_LEGACY_DNS`, `NFS_USE_KERNEL_DNS`, `NFS_DEBUG`, `NFS_DISABLE_UDP_SUPPORT`, and `NFS_V4_2_READ_PLUS`.

## Control Flow
Kconfig dependencies and selects drive build inclusion. `NFS_FS` selects core RPC/lock/common support. Protocol version options depend on NFS core. pNFS layouts depend on NFSv4, with block layout also requiring device mapper. `NFS_FSCACHE` selects `NETFS_SUPPORT` and `FSCACHE`. Kernel DNS is default when NFSv4 is enabled and legacy DNS is not selected.

## State And Persistence
The file persists build-time choices in kernel config. It does not manage runtime state.

## Dependencies And Integration Points
Integrated by the kernel Kconfig system and consumed by NFS Makefiles and `#ifdef` code. It gates whether the netfs/FS-Cache files in this group can be used by NFS caching and whether blocklayout code is built.

## Risks
Incorrect dependencies cause link failures or unsupported runtime combinations. `NFS_DISABLE_UDP_SUPPORT` defaults on due to fragmentation/data corruption risk called out in help. `ROOT_NFS` requires built-in NFS and IP autoconfiguration.

## Test Signals
Build matrix across NFSv3/v4, pNFS layouts, `NFS_FSCACHE`, root NFS, legacy/kernel DNS, and debug/stat configurations. Verify `PNFS_BLOCK` is unavailable without `BLK_DEV_DM`.
