# sources/distributed-fs/ceph-client/fs/xfs/xfs_rtalloc.h

Purpose: Declares realtime allocation, mount, grow, and geometry-check interfaces, with stubs for kernels built without `CONFIG_XFS_RT`.

Important APIs and functions: With realtime support, exports `xfs_rtmount_readsb`, `xfs_rtmount_freesb`, `xfs_rtmount_init`, `xfs_rtmount_inodes`, `xfs_rtunmount_inodes`, `xfs_growfs_rt`, `xfs_rtalloc_reinit_frextents`, `xfs_growfs_check_rtgeom`, and `xfs_rtallocate_rtgs`. Without realtime support, grow returns `-ENOSYS`, mount initialization returns `-ENOSYS` if the filesystem has realtime blocks, and most cleanup/count functions become no-ops.

Control flow and integration: Mount code calls read/init/inodes to attach realtime metadata. Grow ioctl paths call geometry check and grow. Bmap allocation can call `xfs_rtallocate_rtgs` for realtime block allocation. Unmount paths release metadata inodes and the realtime superblock through declared cleanup functions.

State and persistence: The header has no state, but the APIs manipulate realtime superblocks, rtgroup metadata inodes, bitmap/summary files, free extent counters, and superblock geometry. Stub behavior prevents accidentally mounting realtime filesystems without kernel support.

Dependencies and integration points: Depends on `struct xfs_mount`, `struct xfs_trans`, realtime growfs user input types, and transaction/bmap callers. The exported `xfs_rtallocate_rtgs` remains declared outside the `CONFIG_XFS_RT` block for allocator integration.

Risks and invariants: The non-RT stub macro for `xfs_rtmount_inodes` references `mp` rather than its parameter name `m`, which is notable for compile coverage depending on macro expansion context. Callers must handle `-ENOSYS` for unsupported realtime features and should not assume cleanup stubs perform work.

Test signals: Build with and without `CONFIG_XFS_RT`, mount a realtime filesystem on a non-RT build expecting rejection, growfs ioctl stubs, and compile coverage of the `xfs_rtmount_inodes` macro use sites.
