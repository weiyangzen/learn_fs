# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/logged_ops_format.h

This header defines the on-disk value formats for logged operations.

Key elements:
- `enum logged_ops_inums` partitions logged-op btree inode namespaces:
  - `LOGGED_OPS_INUM_logged_ops`
  - `LOGGED_OPS_INUM_inode_cursors`
- `struct bch_logged_op_truncate` stores subvolume, inode number, and target size.
- `enum logged_op_finsert_state` tracks insert-range progress:
  - `start`
  - `shift_extents`
  - `finish`
- `struct bch_logged_op_finsert` stores operation state, subvolume, inode, destination/source offsets, and current position.
- `struct bch_logged_op_stripe_update` stores old/new stripe indices plus old block mapping metadata.

Role:
- These structures are persistent recovery records. Field sizes and endianness are fixed with `__le*` types, so compatibility depends on stable layout.
