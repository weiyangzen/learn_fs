<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.h

Purpose: Declares XFS address-space operation tables and the small set of helper functions used outside `xfs_aops.c`.

Important APIs: Exports `xfs_address_space_operations`, `xfs_dax_aops`, `xfs_setfilesize`, and `xfs_end_bio`.

Control flow and integration: Super/inode setup uses the operation tables to wire regular and DAX mapping behavior into VFS. iomap/block completion paths use `xfs_end_bio` to defer ioend processing to XFS workqueues.

State and persistence: The table declarations indirectly control read/writeback persistence behavior; `xfs_setfilesize` is the explicit on-disk file-size persistence helper.

Dependencies: Requires XFS inode/off_t types and kernel `struct bio`/address_space operation declarations from surrounding includes.

Risks: Any signature drift breaks VFS operation wiring or iomap completion callbacks. DAX and non-DAX operation tables must remain behaviorally consistent where they share swap activation semantics.

Test signals: Build/link coverage, mount regular and DAX filesystems, buffered write append tests invoking `xfs_setfilesize`, and read/write bio completion tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_aops.h -->
