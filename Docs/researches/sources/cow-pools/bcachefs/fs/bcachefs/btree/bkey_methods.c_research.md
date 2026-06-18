# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.c

This file defines per-key-type operations, generic bkey validation, text rendering, merging, type compatibility translation, and old-format migration.

Key contents:
- `bch2_bkey_types[]` maps key type ids to names.
- Basic ops are defined for deleted, whiteout, extent whiteout, error, cookie, hash whiteout, inline data, and set keys.
- `bch2_bkey_ops[]` is generated from `BCH_BKEY_TYPES()` and dispatches validation, rendering, swabbing, merge, trigger, and compatibility operations.
- `bch2_set_bkey_error()` converts a key to `KEY_TYPE_error`, using the extended key-type-error feature when available.
- `bch2_bkey_val_validate()` checks minimum value size and invokes type-specific validation.
- `__bch2_bkey_validate()` performs generic structural checks: key u64 count, allowed key type for btree/node type, extent size rules, snapshot field rules, and `POS_MAX` exclusion.
- `bch2_bpos_to_text()`, `bch2_bkey_to_text()`, `bch2_val_to_text()`, and `bch2_bkey_val_to_text()` provide common diagnostic rendering.
- `bch2_bkey_merge()` checks mergeability and calls the type-specific merge function when enabled.
- `bch2_bkey_renumber()` maps pre-renumbering key type ids to current ids for old metadata.
- `__bch2_bkey_compat()` performs read/write compatibility transforms: endian swab, type renumbering, old inode btree field swap, old snapshot encoding, value swab, and type-specific compatibility.

Important interactions:
- Validation is sensitive to `BCH_FS_no_invalid_checks`.
- Strict key-type enforcement depends on commit context, internal btree nodes, and key type flags.
- Compatibility transformations run in reverse order on write.
