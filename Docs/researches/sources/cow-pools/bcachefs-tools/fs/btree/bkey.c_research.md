# File Research: sources/cow-pools/bcachefs-tools/fs/btree/bkey.c

## Purpose
Implements bcachefs bkey packing, unpacking, packed-position comparison support, packed-format synthesis/validation, endian swapping, and optional compiled unpack code.

## Main Areas
- `bch2_bkey_format_current`: current unpacked bkey format.
- Binary/text rendering:
  - `bch2_bkey_packed_to_binary_text()`
  - `bch2_bkey_format_to_text()`
- Packing/unpacking state machines:
  - `pack_state`
  - `unpack_state`
  - `get_inc_field()`
  - `set_inc_field()`
  - `set_inc_field_lossy()`
- Full key transform/pack/unpack:
  - `bch2_bkey_transform()`
  - `__bch2_bkey_unpack_key()`
  - `__bch2_bkey_unpack_key_b()`
  - `bch2_bkey_pack_key()`
  - `bch2_bkey_unpack()`
- Position-only packing:
  - `bch2_bkey_pack_pos()`
  - `bch2_bkey_pack_pos_lossy()`
- Packed-format construction:
  - `bch2_bkey_format_init()`
  - `bch2_bkey_format_add_pos()`
  - `bch2_bkey_format_done()`
  - `bch2_bkey_format_invalid()`
- Packed comparison support:
  - `bch2_bkey_greatest_differing_bit()`
  - `bch2_bkey_ffs()`
  - `bch2_bkey_cmp_packed()`
  - `__bch2_bkey_cmp_left_packed()`
- Byte-order conversion:
  - `bch2_bpos_swab()`
  - `bch2_bkey_swab_key()`

## Fast Paths
- Little-endian byte-aligned formats get precomputed per-field constants in `bch2_compute_bkey_unpack_consts()`.
- `pack_field_fast()` and `unpack_field_fast()` use unaligned 8-byte loads/stores around precomputed byte windows.
- `__bch2_bkey_unpack_key_b()` uses a header trick: a 4-byte unaligned load starting one byte before the packed key, then shifts/adds to construct the unpacked header.
- `__bkey_unpack_pos_b()` avoids full key unpacking for lookup hot paths.
- Exact and lossy position packing both have byte-aligned fast paths.

## Lossy Position Packing
`bch2_bkey_pack_pos_lossy()` packs a search position into the local btree format. If exact packing is impossible:
- field underflow rolls the lower field up by decrementing the higher field and saturating lower fields,
- field overflow clamps the overflowing field and saturates lower fields,
- the result is the greatest representable packed position still less than or equal to the original search key,
- inode underflow fails.

This behavior is used by bset lookup, where a packed approximate key can safely guide auxiliary-tree comparison as long as it is not greater than the real search position.

## Format Generation
`bch2_bkey_format_done()` computes per-field bit widths and offsets from observed min/max values, then rounds fields to byte widths when spare bits permit. That directly enables the fast byte-aligned unpack/pack paths.

## Validation And Debugging
- Debug mode can re-unpack packed keys and compare against expected unpacked keys.
- Format validation rejects field ranges that can represent values outside the current unpacked format.
- `bch2_bkey_pack_test()` exists under debug to sanity-check pack/unpack machinery.

## Optional Compiled Unpack
There is an `#ifdef HAVE_BCACHEFS_COMPILED_UNPACK` implementation that emits x86-64 machine code for unpacking. The header currently disables the feature with `#if 0`, so the normal build path uses C fast paths.

## Risks / Review Notes
- Many helpers rely on carefully controlled unaligned reads, leading padding, and no overflow/carry assumptions. The padded stack wrapper types in `bkey.h` are important when using packed keys outside a bset.
- Big-endian support falls back for several byte-aligned fast paths; performance and coverage differ by endian.
- The compiled-unpack code is dormant but still present; if re-enabled, executable-memory allocation and instruction emission need separate scrutiny.
