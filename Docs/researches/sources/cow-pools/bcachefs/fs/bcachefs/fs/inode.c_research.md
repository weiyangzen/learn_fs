# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.c

Implements bcachefs inode packing/unpacking, validation, lookup, writeback, triggers, allocation, deletion, link counts, inode options, casefold enabling, snapshot cleanup, and deleted-inode processing.

Key entry points:
- `bch2_inode_pack()` and `bch2_inode_unpack()` convert between `bch_inode_unpacked` and on-disk v1/v2/v3 inode keys.
- `bch2_inode_validate()`, v2, and v3 variants validate inode key position, field encoding, checksum/compression options, unlinked/nlink state, subvolume-root mode, string hash, and v3 field start.
- `__bch2_inode_peek()`, `bch2_inode_find_by_inum_snapshot()`, and find helpers load inode records through subvolume snapshot resolution.
- `bch2_inode_write_flags()`, `__bch2_fsck_write_inode()`, and `bch2_fsck_write_inode()` write packed inode keys.
- `bch2_trigger_inode()` updates journal sequence, disk accounting, deleted-inodes bits, and parent `has_child_snapshot` flags.
- `bch2_inode_init_early()`, `bch2_inode_init_late()`, and `bch2_inode_init()` initialize new unpacked inodes.
- `bch2_inode_create()` allocates inode numbers using logged inode allocation cursors.
- `bch2_inode_rm()` deletes inode contents, xattrs, inode record, and eligible ancestor snapshot inodes.
- `bch2_inode_nlink_inc()` / `bch2_inode_nlink_dec()` update encoded link count and unlinked flag.
- `bch2_inode_opts_to_opts()` / `bch2_inode_opts_get_inode()` convert inherited inode options into runtime IO options.
- `bch2_inode_set_casefold()` enables directory casefolding after empty-dir and feature checks.
- `bch2_delete_dead_inodes()` drains the deleted-inodes btree and removes eligible unlinked inode snapshots.
- `bch2_kill_i_generation_keys()` deletes obsolete inode generation keys.

Core mechanics:
- v3 inodes store journal sequence, hash seed, flags, sectors, size, version, mode, and variable-length fields encoded with fast varints.
- Older v1/v2 inode formats are unpacked through slow paths and can be converted to v3 with `bch2_inode_to_v3()`.
- Inode allocation uses per-CPU or 32-bit cursor records in `BTREE_ID_logged_ops`, supports sharded inode spaces, wraps with generation increments, and skips existing inode/generation records visible in the target snapshot.
- Inode triggers maintain `BCH_INODE_has_child_snapshot` on parent snapshot inode versions when child versions are inserted/deleted.
- Deleted inode tracking is buffered in `BTREE_ID_deleted_inodes` for unlinked inodes without child snapshots.
- Inode removal deletes extents for non-directories, dirents/whiteouts for directories, xattrs for all, then removes the inode key and cleans up older unlinked ancestors when safe.
- Casefold is a directory-only inode option; enabling it requires the directory to be empty, requests the metadata incompat feature, and propagates case-insensitive state.

Important invariants:
- Filesystem inode keys must have `k.p.inode == 0` and offsets outside the block-device inode range.
- Inode variable fields must decode without overflow into `bch_inode_unpacked`.
- Unlinked inodes encode zero visible nlink through `BCH_INODE_unlinked`.
- Subvolume roots must be directories.
- Inode writes through fsck use internal snapshot-node flags and may force transaction restarts.
- Directories with casefold enabled cannot already contain entries because dirent hashes would need rehashing.

Filesystem relevance:
- This is bcachefs’s inode metadata core. It defines how inode records are encoded, found, mutated, accounted, linked to snapshots, and eventually deleted.
