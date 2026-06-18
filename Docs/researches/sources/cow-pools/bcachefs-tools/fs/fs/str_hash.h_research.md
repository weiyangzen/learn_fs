# File Research: sources/cow-pools/bcachefs-tools/fs/fs/str_hash.h

## Purpose
Generic inline framework for bcachefs string-key hash tables. It abstracts hash type selection, hash computation state, btree lookup, collision probing, insert/replace semantics, whiteout-aware delete, and fsck check dispatch.

## Main Contents
- `bch2_str_hash_opt_to_type()`, mapping mount/inode hash options to concrete hash type, including old/new siphash feature selection.
- `struct bch_hash_info`, carrying inode snapshot, hash type, 31-bit truncation flag, casefold encoding, and keyed hash seed.
- Hash context helpers:
  - `bch2_str_hash_init()`
  - `bch2_str_hash_update()`
  - `__bch2_str_hash_end()`
  - `bch2_str_hash_end()`
- `struct bch_hash_desc`, the per-table descriptor containing btree id, key type, hash functions, comparison functions, and optional visibility predicate.
- `is_visible_key()`, which filters keys by type and snapshot/subvolume visibility.
- Lookup helpers:
  - `bch2_hash_lookup_in_snapshot()`
  - `bch2_hash_lookup()`
  - `bch2_hash_hole()`
- Collision/whiteout helpers:
  - `bch2_hash_needs_whiteout()` scans forward to decide whether deleting a slot needs a whiteout.
  - `bch2_hash_set_or_get_in_snapshot()` probes from the hash offset, detects duplicates/collisions, records first reusable slot, supports must-create and must-replace flags, and either updates or returns the existing key.
  - `bch2_hash_set_in_snapshot()` and `bch2_hash_set()` wrap insertion.
  - `bch2_hash_delete_at()` and `bch2_hash_delete()` delete by position or key, emitting whiteouts when needed.
- Fsck repair declarations and fast-path `str_hash_key_needs_check()` / `bch2_str_hash_check_key()`.

## Integration Notes
Dirents and xattrs use this file by supplying `bch_hash_desc` instances. The btree key position offset is the computed hash, but collisions are resolved by linear probing through slots in the same inode range. Snapshot-aware visibility and whiteouts are required so deletions do not expose hidden older entries.

## Risks and Edge Cases
- `cmp_key` and `cmp_bkey` return true for inequality; this convention is easy to misread.
- `STR_HASH_must_create` returns the found existing key to signal EEXIST in wrappers; callers must handle the returned bkey correctly.
- 31-bit hashing applies only when the caller allows it and the inode has the 31-bit dirent offset flag.
- Whiteout decisions depend on forward scanning; incorrect hash functions or comparison callbacks can corrupt lookup semantics.
