# File Research: sources/cow-pools/bcachefs-tools/fs/bcachefs_format.h

Central on-disk format header for bcachefs. It defines common bitfield helpers, btree key layout, bkey types, superblock fields, btree IDs, metadata versions, superblock layout, feature/option enums, journal formats, and btree node formats.

Major sections:
- Overview comments for superblock, journal, btree, and btree key structure.
- Generic native-endian and little-endian bitfield accessor macros.
- `struct bkey_format`, `struct bpos`, `struct bversion`, `struct bkey`, `struct bkey_packed`, and `struct bkey_i`.
- Position/key construction helpers: `SPOS`, `POS`, `POS_MIN`, `POS_MAX`, `KEY`, `POS_KEY`, `bkey_init()`, and `bkey_bytes()`.
- Bkey type definitions in `BCH_BKEY_TYPES()`, including deleted/whiteout/error/cookie/hash entries, btree pointers, extents, inodes, alloc formats, stripes, reflink, inline data, snapshots, LRU, backpointers, bucket gens, logged ops, accounting, and extent whiteouts.
- Key error types such as `device_removed`, `double_allocation`, and `no_valid_pointers_repair`.
- Core small value structs: deleted/whiteout/error/cookie/hash/set/csum/backpointer.
- Backpointer flags, including reconcile-physical linkage and erasure/stripe pointer flags.
- Superblock field base type and all `BCH_SB_FIELDS()`.
- Btree flags and all `BCH_BTREE_IDS()`.
- Includes for all subordinate format headers, including allocation, replicas, LRU, members, accounting, extents, EC, inode, dirent, quota, snapshots, and journal blacklist formats.
- Journal bucket, crypt, clean-shutdown, and extended superblock field structures.
- Full metadata version list through current format evolution, including alloc v4, freespace, backpointers, LRU changes, disk accounting, casefolding, reconcile, erasure coding, and need-discard-by-journal-seq.
- `struct bch_sb_layout` and `struct bch_sb`.
- Superblock flags and option bitfields for checksum, compression, replicas, targets, journal tuning, write buffer, version upgrade, degraded action, casefolding, scrub journal, EC limits, and related options.
- Feature and compatibility bit enums.
- Error/degraded action enums.
- String hash, checksum, compression, and scrub-journal option enums.
- Magic numbers for bcache/bcachefs superblocks, journal sets, and bsets.
- Journal entry types and journal entry structures.
- Btree reconstruction helpers and btree node/bset formats.

Important format relationships:
- `struct bkey` is the common key header used across btrees; values are type-specific and inline.
- `BCH_BKEY_TYPES()` and `BCH_BTREE_IDS()` define which key types are valid in each btree.
- `BTREE_ID_need_discard`, `BTREE_ID_freespace`, `BTREE_ID_lru`, `BTREE_ID_alloc`, backpointers, bucket gens, and accounting are the allocator-relevant btrees.
- `BCH_SB_FIELD_disk_groups`, `BCH_SB_FIELD_replicas_v0`, and `BCH_SB_FIELD_replicas` are the superblock fields implemented by files in this group.
- `btree_id_is_alloc()` classifies allocator/reconstructable metadata btrees.
- `btree_id_can_reconstruct()` and `btree_id_recovers_from_scan()` describe recovery expectations for reconstructable metadata.
- Journal rewind entries and rewind limit entries connect to discard safety and journal rewind behavior.
- `struct btree_node` and `struct btree_node_entry` define the COW btree node log format.

Role:
- This file is the authoritative shared wire-format contract for bcachefs-tools and kernel-compatible metadata parsing/writing.
