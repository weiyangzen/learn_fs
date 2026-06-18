<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.h

Purpose: Declares kernel-only higher-level XFS bmap utility interfaces used by file operations, writeback, ioctl, and maintenance paths.

Important APIs and types: Declares realtime allocation hook `xfs_bmap_rtalloc`, delalloc punch, `struct kgetbmap`, `xfs_getbmap`, extent alignment helpers from bmap core, preallocation/hole-punch/collapse/insert interfaces, EOF block cleanup, `xfs_swap_extents`, block address conversion, extent counting, and `xfs_flush_unmap_range`.

Control flow and integration: This header connects many subsystems to bmap utility behavior: address-space error cleanup uses delalloc punching, ioctl paths use getbmap and swapext, file space operations use alloc/free/collapse/insert, and inode cleanup uses EOF block helpers.

State and persistence: Declared functions can mutate persistent extent maps and inode metadata; the header itself stores no state.

Dependencies: Forward-declares bmap, inode, mount, transaction, and zoned allocation types. Provides an inline `xfs_bmap_rtalloc` returning `-EFSCORRUPTED` when realtime support is disabled.

Risks: The disabled realtime inline intentionally treats RT allocation attempts as corruption, so callers must feature-gate RT paths. Function contracts generally assume caller-held locks that are documented in implementation rather than type signatures.

Test signals: Compile matrix with/without `CONFIG_XFS_RT`, call sites meeting locking assumptions, and public file-operation paths invoking each declared mutator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_bmap_util.h -->
