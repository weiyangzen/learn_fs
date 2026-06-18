# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_types.h

This header defines the basic bkey wrapper model and generates typed wrappers for every bcachefs key value type.

Key contents:
- Documentation explains `struct bpos` as the sortable search key and `struct bkey` as the key header containing u64 count, format, type, version, extent size, and position.
- `bkey_next()`, `bkey_val_u64s()`, `bkey_val_bytes()`, `set_bkey_val_u64s()`, and `set_bkey_val_bytes()` operate on inline key/value sizes.
- Whiteout/deleted helpers distinguish deleted, whiteout, and extent-whiteout key states.
- `struct bkey_s_c` and `struct bkey_s` represent split key/value views, const and mutable.
- Generic conversion helpers create split views from `bkey` and `bkey_i`.
- The `BCH_BKEY_TYPES()` macro expansion generates, for each value type:
  - `bkey_i_<name>` inline key/value type.
  - `bkey_s_<name>` and `bkey_s_c_<name>` split typed views.
  - Conversion helpers that BUG if the runtime key type does not match.
  - Initialization helpers that zero the typed value and set type/value length.
- `enum bch_validate_flags` and `struct bkey_validate_context` define validation context, including source, flags, level, btree id, root flag, and journal location.

Role:
- This file is the type-safe bridge between generic btree storage and individual on-disk value structs such as extents, inodes, dirents, xattrs, allocation keys, and snapshot/subvolume records.
