# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey_methods.h

## Purpose
Declares the bkey operation interface and inline dispatch helpers for validation, text rendering, triggers, merges, repair, and compatibility.

## Main Types
- `struct bkey_ops` function table:
  - `key_validate`
  - `val_to_text`
  - `swab`
  - `key_merge`
  - `trigger`
  - `check_repair`
  - `compat`
  - `min_val_size`

## Main Helpers
- `bch2_bkey_type_ops(type)`: returns ops table entry or null ops.
- `bch2_bkey_maybe_mergable(l, r)`: checks type, version, and adjacency.
- `bch2_key_trigger()`: dispatches old/new trigger operation.
- `bch2_key_trigger_old()` and `bch2_key_trigger_new()` synthesize deleted old/new keys for overwrite/insert triggers.
- `bch2_bkey_check_repair()` dispatches optional repair hook.
- `bch2_bkey_compat()` conditionally calls full compatibility conversion only for old metadata, endian mismatch, or debug builds.

## External API
Declares validation, merge, text, swab, renumber, compatibility, and error-key helpers implemented in `bkey_methods.c`.

## Notable Details
- Trigger helpers construct local deleted keys at the same position to represent insertion/deletion transitions.
- Compatibility fast path avoids work when metadata is current and endian matches.
