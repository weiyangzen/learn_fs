# File Research: sources/cow-pools/bcachefs/fs/bcachefs/vfs/types.h

Defines the per-filesystem VFS state container embedded in `struct bch_fs`.

Key fields:
- `inodes_list` and `inodes_lock` track all live bcachefs VFS inodes for subvolume eviction and lifecycle operations.
- `inodes_table` maps full `(subvol, inum)` identities to cached VFS inodes.
- `inodes_by_inum_table` maps inode numbers across subvolumes for snapshot/open-descendent checks.
- `writepage_bioset`, `dio_write_bioset`, `dio_read_bioset`, and `nocow_flush_bioset` back specialized bio allocations.
- `writepage_buf_pool` reserves memory for writepage folio-sector snapshots.
- `writeback_wq` runs delayed inode writeback work.

Filesystem relevance:
- This structure groups the shared VFS resources that are initialized during filesystem startup and torn down during VFS exit.
