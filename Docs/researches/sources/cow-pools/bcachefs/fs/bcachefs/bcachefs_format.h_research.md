# File Research: sources/cow-pools/bcachefs/fs/bcachefs/bcachefs_format.h

Primary on-disk format header for bcachefs.

Major responsibilities:
- Define bitmask helper macros for native and little-endian packed fields.
- Define core btree key primitives: `bpos`, `bversion`, `bkey`, `bkey_packed`, `bkey_i`, and key construction helpers.
- Enumerate bkey types and their semantic descriptions.
- Define common simple key values such as deleted, whiteout, error, cookie, set, checksum, and backpointer values.
- Define superblock field header, superblock field types, and single-device field mask.
- Enumerate btree IDs, flags, allowed key types, and descriptions.
- Include all subsystem format headers, including alloc, disk groups, LRU, replicas, accounting, extents, EC, inode, quota, journal, members, and snapshots.
- Define journal superblock fields, encryption key/KDF formats, clean shutdown field, extended superblock field, metadata versions, superblock layout, and core superblock.
- Define superblock option bitfields, features, compat flags, checksum/compression/hash options, magic constants, journal entry types, journal entry payloads, journal set format, and btree node formats.

Allocator-related format details:
- `BTREE_ID_alloc`, `freespace`, `need_discard`, `backpointers`, `bucket_gens`, `lru`, `accounting`, and reconcile btrees are all declared here.
- `BTREE_ID_need_discard` is a write-buffer btree of `KEY_TYPE_set` entries for buckets waiting for discard/TRIM.
- Metadata version `need_discard_by_journal_seq` documents reindexing `need_discard` by journal sequence for efficient discard eligibility.
- `BCH_SB_FIELD_disk_groups`, `replicas_v0`, and `replicas` connect allocator targeting and replica accounting to superblock metadata.
- `btree_id_is_alloc()` classifies allocation/accounting/reconcile btrees for recovery/reconstruction handling.
- `btree_id_can_reconstruct()` and `btree_id_recovers_from_scan()` encode which btrees can be rebuilt from other metadata.

Important on-disk structures:
- `struct bch_sb_layout` records backup superblock layout.
- `struct bch_sb` stores versioning, UUIDs, label, device count/index, block size, flags, feature/compat masks, layout, and variable fields.
- `struct jset` stores journal entries with sequence, version, checksum, no-flush/overwrite flags, and oldest dirty sequence.
- `struct bset`, `struct btree_node`, and `struct btree_node_entry` describe btree node write sets and node metadata.

Versioning:
- `BCH_METADATA_VERSIONS()` lists format evolution from early bkey renumbering through current versions, including recent allocator-relevant changes such as `bucket_stripe_index`, `no_sb_user_data_replicas`, `erasure_coding`, and `need_discard_by_journal_seq`.
- `bcachefs_metadata_version_current` is derived from `bcachefs_metadata_version_max - 1`.

Role:
- All files in this group depend on this header directly or indirectly for data type IDs, btree IDs, key/value formats, superblock field IDs, and metadata version gates.
