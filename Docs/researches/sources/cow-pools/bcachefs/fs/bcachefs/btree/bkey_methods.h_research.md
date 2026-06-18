# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey_methods.h

This header declares the bkey operation table and helpers for validation, rendering, merging, triggers, and metadata compatibility.

Key contents:
- `struct bkey_ops` contains callbacks for `key_validate`, `val_to_text`, `swab`, `key_merge`, `trigger`, and `compat`, plus `min_val_size`.
- `bch2_bkey_type_ops()` safely maps a key type to its operations or null ops.
- Validation/rendering declarations cover whole key validation, value validation, bpos/bkey text, and key-value text.
- `bch2_bkey_maybe_mergable()` checks same type, same version, and contiguous positions.
- `bch2_key_trigger()`, `bch2_key_trigger_old()`, and `bch2_key_trigger_new()` wrap trigger calls for overwrite/delete/insert cases using synthetic deleted keys.
- Compatibility and error helpers are declared: `bch2_bkey_renumber()`, `bch2_bkey_compat()`, and `bch2_set_bkey_error()`.

Role:
- This is the shared interface between generic btree code and individual bkey value-type implementations.
