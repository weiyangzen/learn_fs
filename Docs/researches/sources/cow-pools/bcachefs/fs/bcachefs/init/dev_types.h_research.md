# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/dev_types.h

This header defines lightweight device/init types.

Key elements:
- `struct bch_sb_handle_holder` stores a backpointer to `struct bch_fs` for block holder callbacks.
- `struct bch_sb_handle` owns a read/open superblock context: superblock pointer, backing file/block device, name, bio, holder, buffer size, open mode, layout/bio/fs-superblock flags, and sequence.
- `struct bch_devs_mask` is a bitmap over possible superblock members.
- `struct bch_devs_list` is a compact list of device indexes sized to max bkey pointers.

Role:
- These types connect superblock IO, device membership, and allocator/read-write device masks.
