# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.h

This header is the main inline API for bkey and bpos manipulation, packed/unpacked conversions, comparison, packing/unpacking declarations, format accounting, and byte-order helpers.

Key contents:
- Copy helpers: `bkey_p_copy()`, `bkey_copy()`, and `bkey_val_copy()`.
- `bpos_*` comparison helpers compare inode, offset, and snapshot; `bkey_*` comparison helpers compare only inode and offset.
- Version helpers define `ZERO_VERSION`, `MAX_VERSION`, `bversion_cmp()`, and `bversion_eq()`.
- Packed/unpacked detection and casts: `bkey_packed()`, `bkey_to_packed()`, `packed_to_bkey()`, and const variants.
- Position navigation helpers: `bpos_successor()`, `bpos_predecessor()`, no-snapshot variants, `bkey_start_offset()`, and `bkey_start_pos()`.
- Packed-key sizing helpers: `bkeyp_key_u64s()`, `bkeyp_val_u64s()`, `bkeyp_val_bytes()`, and `bkeyp_val()`.
- Public declarations for transform, pack/unpack, lossy position packing, format validation, and format rendering.
- `__bkey_unpack_key_format_checked()` chooses compiled unpack support if enabled, otherwise the normal fast path, with optional debug verification.
- `bkey_disassemble()` and `__bkey_disassemble()` split a packed key into an unpacked key pointer plus value pointer.
- Byte-order macros define `high_word()`, `next_word()`, `prev_word()`, and `high_bit_offset`.
- `bkey_fields()` centralizes the six packable fields: inode, offset, snapshot, size, version high, and version low.

Role:
- This is the hot inline layer used by bset lookup, btree iteration, validation, and mutation paths. It encodes the difference between full key identity including snapshot and extent/range comparisons using only inode/offset.
