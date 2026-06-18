# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode_format.h

Defines the persistent bcachefs inode formats, inode variable fields, inode options, inode flags, bitfield accessors, and inode allocation cursor format.

Key elements:
- `BLOCKDEV_INODE_MAX` reserves low inode numbers; `BCACHEFS_ROOT_INO` is 4096.
- `struct bch_inode`, `bch_inode_v2`, and `bch_inode_v3` define three on-disk inode value layouts.
- `struct bch_inode_generation` stores generation keys.
- `BCH_INODE_FIELDS_v2()` and `BCH_INODE_FIELDS_v3()` enumerate variable-length inode fields such as times, uid/gid, nlink, generation, device, checksum/compression, project, replication/target options, dir backpointers, subvolume IDs, nocow, depth, 32-bit inode selection, and casefold.
- `BCH_INODE_OPTS()` identifies the subset of fields treated as inherited inode options.
- `enum inode_opt_id` indexes inode options.
- `BCH_INODE_FLAGS()` defines inode flags including sync, immutable, append, nodump, noatime, dirty size/sectors, unlinked, backptr untrusted, child snapshot, case-insensitive descendant, and 31-bit dirent offset.
- Bitmask macros define packed string-hash, field-count, v3 field-start, and v3 mode fields.
- `struct bch_inode_alloc_cursor` stores allocation cursor bits, generation, and next index.

Important invariants:
- v3 mode is packed into inode flags bits rather than a standalone `bi_mode` field.
- Bits 20 and above in inode flags are reserved for packed field metadata.
- `bi_subvol` and `bi_parent_subvol` are only for subvolume roots.
- On-disk structs are packed and 8-byte aligned.

Filesystem relevance:
- This file is the persistent inode ABI. Inode parsing, validation, fsck repair, and compatibility migration all depend on these layouts and field lists.
