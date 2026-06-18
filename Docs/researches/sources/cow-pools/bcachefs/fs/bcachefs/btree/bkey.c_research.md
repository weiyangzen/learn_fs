# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/bkey.c

This file implements packed bkey format handling: packing, unpacking, lossy position packing, format construction/validation, byte swapping, packed comparisons, and optional compiled-unpack support.

Key contents:
- `bch2_bkey_format_current` defines the current unpacked key format.
- Packing/unpacking is built around `pack_state` and `unpack_state`, with `get_inc_field()`, `set_inc_field()`, and `set_inc_field_lossy()`.
- `bch2_bkey_transform()` converts a packed key/value from one packed format to another.
- `__bch2_bkey_unpack_key()` and `__bch2_bkey_unpack_key_b()` unpack packed keys; the latter has a little-endian fast path using precomputed byte-aligned load constants from `bch2_compute_bkey_unpack_consts()`.
- `bch2_bkey_pack_key()` and `bch2_bkey_pack()` pack key-only and key-plus-value forms.
- `bch2_bkey_pack_pos_lossy()` creates a packed search position that is exact, smaller than the requested position, or impossible; bset lookup relies on this to search auxiliary trees efficiently.
- `bch2_bkey_format_init()`, `bch2_bkey_format_add_pos()`, and `bch2_bkey_format_done()` derive compact local formats from observed key ranges.
- `bch2_bkey_format_invalid()` validates packed format metadata against current field widths and computed `key_u64s`.
- `bch2_bkey_greatest_differing_bit()` and `bch2_bkey_ffs()` support auxiliary search tree compression.
- The disabled `HAVE_BCACHEFS_COMPILED_UNPACK` block contains x86 instruction emission for runtime unpack functions.
- `bch2_bpos_swab()` and `bch2_bkey_swab_key()` handle endian conversion of positions/keys.

Important invariants:
- Packed keys use per-field offsets plus bit widths and must not represent values larger than the unpacked format.
- Extent start-position invariants are explicitly not preserved by the generic transform helper.
- Debug branches verify pack/unpack equivalence and packed comparison correctness.
