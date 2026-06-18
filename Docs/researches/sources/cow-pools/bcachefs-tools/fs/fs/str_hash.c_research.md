# File Research: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.c

## Purpose
Implements hash-info initialization and fsck repair for bcachefs string-key hash tables. This shared layer supports hashed dirents and xattrs, including casefold state, snapshot hash consistency, duplicate handling, wrong-offset repair, and whiteout-safe movement.

## Main Contents
- `__bch2_hash_info_init()` builds `struct bch_hash_info` from an inode: snapshot, hash type, 31-bit offset flag, casefold encoding pointer, and hash seed. Old siphash derives the full key by SHA-256 hashing the stored seed.
- `bch2_hash_info_init()` rejects casefolded directories when the filesystem lacks casefold encoding.
- `bch2_dirent_has_target()` checks whether a dirent target still exists, handling subvolume and ordinary inode targets differently.
- `bch2_fsck_rename_dirent()` renames a duplicate dirent to a `.fsck_renamed-N` name and updates backpointers.
- `hash_pick_winner()` decides which duplicate hash key survives, preferring identical values, snapshot ordering, and dirents with valid targets.
- `bch2_repair_inode_hash_info()` repairs per-snapshot inode hash seed/type mismatches by copying root hash info into the bad inode and writing it through fsck.
- `check_inode_hash_info_matches_root()` verifies hash info consistency across snapshot versions before repairing a key.
- `str_hash_dup_entries()`, `bch2_str_hash_repair_key()`, and `str_hash_bad_hash()` handle duplicate or misplaced hash keys by moving keys to their proper hash position, inserting snapshot whiteouts, deleting stale entries, and committing lazy fsck updates.
- `str_hash_check_dirent()` repairs dirent casefold mismatch by rebuilding the dirent under the current hash info.
- `__bch2_str_hash_check_key()` is the main fsck validation path for a single hash-table key.

## Integration Notes
`str_hash.h` provides inline lookup/set/delete primitives; this file provides the slower repair side. `dirent` and `xattr` subsystems provide `bch_hash_desc` instances with hash/cmp functions. Snapshot handling is central: all versions of a directory inode must use identical hash type and seed, or lookup across snapshots can break.

## Risks and Edge Cases
- Repair can move keys to lower positions; callers track `updated_before_k_pos` to know whether iteration must revisit earlier keys.
- Duplicate dirent repair may rename one valid target rather than delete it when both point to valid inodes.
- Hash mismatches may actually be inode hash-info mismatches, so repairs first validate snapshot root hash state before moving keys.
