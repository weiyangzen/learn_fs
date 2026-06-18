# File Research: sources/cow-pools/bcachefs-tools/fs/fs/inode.c

## Purpose

Implements bcachefs inode packing/unpacking, validation, lookup, write, creation, deletion, nlink mutation, inode option extraction, casefold enablement, deleted-inode cleanup, inode triggers, and legacy inode-generation cleanup.

## Main Interfaces

- Pack/unpack: `bch2_inode_pack()`, `bch2_inode_unpack()`, `bch2_inode_to_v3()`.
- Lookup/find: `__bch2_inode_peek_snapshot()`, `__bch2_inode_peek()`, `bch2_inode_find_by_inum_snapshot()`, `bch2_inode_find_by_inum_snapshot2()`, `__bch2_inode_find_by_inum_trans()`, `bch2_inode_find_by_inum()`, `bch2_inode_find_oldest_snapshot()`.
- Write: `bch2_inode_write_flags()`, `__bch2_fsck_write_inode()`, `bch2_fsck_write_inode()`.
- Validate/text: inode v1/v2/v3 validators and text formatters; inode generation and alloc cursor validators/formatters.
- Snapshot/trigger: `__bch2_inode_has_child_snapshots()`, `bch2_trigger_inode()`.
- Lifecycle: `bch2_inode_init_early()`, `bch2_inode_init_late()`, `bch2_inode_init()`, `bch2_inode_create()`, `bch2_inode_rm()`, `bch2_inode_rm_snapshot()`, `bch2_delete_dead_inodes()`, `bch2_kill_i_generation_keys()`.
- Link/options: `bch2_inode_nlink_inc()`, `bch2_inode_nlink_dec()`, `bch2_inode_opts_to_opts()`, `bch2_inode_opts_get_inode()`, `bch2_inode_set_casefold()`.

## Behavior

The file supports three inode formats. v3 is the fast path: fixed fields store journal sequence, hash seed, flags, sectors, size, version, and mode; optional fields are varint-packed and truncated after the last nonzero field. v1/v2 unpack through slow paths. Decode errors zero the failed and later fields, count `inode_unpack_error`, and schedule explicit recovery passes when damaged fields affect nlinks, subvolumes, parent subvolumes, or casefolded dirent hashing.

Lookup helpers resolve subvolume snapshots and fetch cached inode keys from `BTREE_ID_inodes`. Write helpers repack unpacked inodes into v3 and update or insert through btree transactions. Validators enforce inode key positions, blockdev-reserved ranges, valid string-hash types, and valid v3 field-start offsets.

`bch2_trigger_inode()` maintains side effects during transactional/gc updates: journal sequence assignment on insert, inode count accounting, deleted-inodes btree bits for unlinked inodes, parent child-snapshot flags, and clearing child flags when a snapshot-local inode is created.

Inode creation obtains a logged inode allocation cursor, supports 32-bit and sharded inode-number ranges, scans for an empty slot or reusable inode-generation key, assigns generation, advances cursor, and positions the caller’s iterator. Inode removal checks whether deletion is valid, deletes extent/dirent/xattr keys, removes the inode, and recursively removes unlinked ancestor snapshot inodes when safe.

Deleted-inode cleanup flushes the write buffer, walks `BTREE_ID_deleted_inodes`, validates each entry, removes bogus deleted-inode bits, and deletes dead inode snapshots while avoiding spin-prone restart behavior.

Inode option helpers convert inode-local option overrides to mount-style option structs, fallback unknown future compression/checksum values to filesystem defaults for new writes, and propagate change cookies. Casefold enablement requires Unicode/casefold support, a directory, an empty directory, and the incompat feature.

## State And Side Effects

This file mutates inode, extent, dirent, xattr, logged-ops, deleted-inodes, and accounting btrees. It also updates filesystem error counters and may trigger recovery passes on unpack failures. Link count helpers manipulate `BCH_INODE_unlinked` semantics rather than only numeric nlinks.

## Dependencies

Depends on accounting, buckets, key cache/write buffer, bkey methods/update, compression/extents/extent update, dirent/namei/str_hash, VFS wrappers, init error/pass machinery, snapshots/subvolumes, varint encoding, random bytes, and unaligned helpers.

## Risks And Notes

Inode format compatibility is central here. Decode error recovery must leave a defined unpacked struct while scheduling enough fsck passes to reconstruct derived state. Snapshot parent/child flag maintenance is delicate because inode creation/deletion in one snapshot affects ancestor visibility and fsck semantics.
