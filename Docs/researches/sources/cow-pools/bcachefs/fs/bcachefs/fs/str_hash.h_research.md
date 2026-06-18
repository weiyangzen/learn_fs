# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/str_hash.h

This header defines the generic string-hash engine used by dirents and xattrs.

Hash support:
- `bch2_str_hash_opt_to_type()` maps filesystem options to crc32c, crc64, new siphash, or old siphash based on feature bits.
- `struct bch_hash_info` stores snapshot, hash type, 31-bit offset mode, casefold encoding, and key material.
- `bch2_str_hash_init/update/end()` abstract crc32c, crc64, and siphash. crc64/siphash return shifted values to avoid signed offset issues, and `bch2_str_hash_end()` can mask to 31 bits for old directory-offset mode.

Generic hash descriptor:
- `struct bch_hash_desc` supplies btree id, key type, hash/cmp callbacks, and optional visibility predicate.
- `is_visible_key()` filters by key type and snapshot/subvolume visibility.

Lookup/create/delete helpers:
- `bch2_hash_lookup_in_snapshot()` scans from the computed hash offset until it finds a matching visible key or reaches a hole.
- `bch2_hash_lookup()` resolves the subvolume snapshot then calls the snapshot-specific lookup.
- `bch2_hash_hole()` finds an insertion hole for a key.
- `bch2_hash_needs_whiteout()` determines whether deletion must leave a hash whiteout to preserve collision-chain lookup semantics.
- `bch2_hash_set_or_get_in_snapshot()` implements insert/replace/create semantics while handling collisions and whiteout reuse.
- `bch2_hash_set_in_snapshot()` and `bch2_hash_set()` are wrappers for insertion.
- `bch2_hash_delete_at()` writes either `KEY_TYPE_hash_whiteout` or `KEY_TYPE_deleted`.
- `bch2_hash_delete()` looks up then deletes by search key.

Fsck integration:
- Declares inode hash-info repair and slow-path key checking.
- `str_hash_key_needs_check()` fast-filters keys with wrong offsets or dirent casefold mismatch.
- `bch2_str_hash_check_key()` calls the heavy checker only when needed.

Role:
- This header carries most of the generic string-hash algorithm inline for performance and reuse by dirents/xattrs.
