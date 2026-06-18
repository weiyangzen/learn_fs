# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey.h

## Purpose
Primary public helper header for bkey comparison, packing/unpacking declarations, position arithmetic, bversion comparison, and packed/unpacked key utilities.

## Main Contents
- Copy helpers:
  - `bkey_p_copy()`
  - `bkey_copy()`
  - `bkey_val_copy()`
- Position comparison helpers:
  - `bpos_eq/lt/le/gt/ge/cmp`
  - `bkey_eq/lt/le/gt/ge/cmp`, ignoring snapshot
  - min/max helpers
- Version helpers:
  - `bversion_cmp()`
  - `bversion_eq()`
  - `ZERO_VERSION`
  - `MAX_VERSION`
- Packed/unpacked helpers:
  - `bkey_packed()`
  - `bkey_to_packed()`
  - `packed_to_bkey()`
  - `bkeyp_key_u64s()`
  - `bkeyp_val_u64s()`
  - `bkeyp_val()`
- Position arithmetic:
  - `bpos_successor()`
  - `bpos_predecessor()`
  - no-snapshot successor/predecessor variants
  - `bkey_start_offset()`
  - `bkey_start_pos()`
  - `bpos_with_snapshot()`
- Unpack wrappers:
  - `__bkey_unpack_key_format_checked()`
  - `bkey_unpack_key()`
  - `bkey_unpack_pos()`
  - `bkey_disassemble()`
- Format state:
  - `struct bkey_format_state`
  - `bch2_bkey_format_add_key()`
  - `bch2_bkey_format_field_overflows()`

## Important Types
- `struct bkey_packed_padded` and `struct bkey_i_padded` provide leading padding for stack-local packed keys. This is required because fast unpack paths may read bytes before the packed key address.
- `enum bkey_pack_pos_ret` distinguishes exact pack, smaller/lossy pack, and pack failure.

## Notable Details
- `bkey_cmp()` ignores `snapshot`, while `bpos_cmp()` includes it. This distinction is fundamental to lookup/extent behavior.
- `bkey_packed()` treats `KEY_FORMAT_CURRENT` as unpacked and other formats as packed.
- Endian helpers define `high_word()`, `next_word()`, and `prev_word()` differently for little vs big endian.
- Compiled unpack hooks are declared but disabled by the top-level `#if 0`.

## Risks / Review Notes
- The difference between `bpos_*` and `bkey_*` comparisons is easy to misuse.
- `bpos_successor()` and predecessor helpers `BUG()` on overflow/underflow rather than returning failure.
- Stack-local packed keys should use the padded wrappers when passed to fast unpack/compare paths.
