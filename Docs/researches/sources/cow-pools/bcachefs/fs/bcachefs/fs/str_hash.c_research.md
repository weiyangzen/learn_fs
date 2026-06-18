# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.c

This file implements fsck and repair support for bcachefs string-hash btrees, used by dirents and xattrs.

Hash info:
- `__bch2_hash_info_init()` derives hash type, snapshot, 31-bit offset mode, casefold encoding, and siphash key from an inode.
- Old siphash compatibility hashes the inode seed through SHA-256 before building the key.
- `bch2_hash_info_init()` rejects casefolded directories when Unicode/casefold support is unavailable.

Duplicate and bad-key repair:
- `bch2_dirent_has_target()` checks whether a dirent points to an existing subvolume or inode.
- `hash_pick_winner()` chooses which duplicate key survives; for dirents it prefers entries with valid targets and flags ambiguous valid-vs-valid duplicates.
- `bch2_fsck_rename_dirent()` creates a unique `.fsck_renamed-N` name when both duplicate dirents point to valid objects.
- `str_hash_dup_entries()` reports duplicate hash table keys, optionally renames, deletes the loser, and commits lazily.
- `bch2_str_hash_repair_key()` reinserts a key into its proper hash slot, inserts snapshot whiteouts when needed, updates backpointers, or handles duplicates.
- `str_hash_bad_hash()` checks inode hash metadata against the root snapshot and repairs keys at the wrong offset.

Snapshot hash invariants:
- `bch2_repair_inode_hash_info()` repairs an inode snapshot whose hash type/seed diverges from the oldest/root snapshot.
- `check_inode_hash_info_matches_root()` verifies all snapshot versions of the same inode use compatible hash metadata, because snapshot string lookups depend on consistent hash placement.

Dirent-specific checks:
- `str_hash_check_dirent()` verifies `d_casefold` matches directory hash info and rebuilds/repositions the dirent if needed.
- `__bch2_str_hash_check_key()` checks wrong offsets, duplicates, hash whiteout boundaries, and dirent casefold mismatches.

Role:
- This is primarily consistency-repair logic for hashed metadata btrees.
- It is generic through `bch_hash_desc` but currently has extra behavior for dirents.
