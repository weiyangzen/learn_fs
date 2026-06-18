# File Research: sources/cow-pools/bcachefs-tools/fs/fs/logged_ops_format.h

## Purpose
Defines the on-disk value formats and logical inode namespaces used by logged operation keys.

## Main Contents
- `enum logged_ops_inums` with logical inodes for logged ops and inode cursors.
- `struct bch_logged_op_truncate`, storing subvolume, inode number, and new file size.
- `enum logged_op_finsert_state`, tracking finsert progress through start, extent shifting, and finish states.
- `struct bch_logged_op_finsert`, storing state, subvolume, inode, destination/source offsets, and current position.
- `struct bch_logged_op_stripe_update`, storing old/new stripe indexes plus a compact old block map.

## Integration Notes
These structures are bkey values under `BTREE_ID_logged_ops`. `logged_ops.c` reassembles them generically and dispatches to operation-specific resume functions. The inum enum partitions logged op keys from inode allocation cursor keys.

## Risks and Edge Cases
- These are packed persistent recovery records; field ordering and endian annotations are part of disk compatibility.
- `old_block_map` is fixed at 16 entries for stripe update logging, so code building these keys must respect that capacity.
