# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 1-6876

## Scope

This chunk covers the first 6,876 lines of `u8_textprep_data.h`, a generated/static Unicode UTF-8 text preparation data header in illumos. The full header is 35,374 lines; this chunk ends mid-definition of `u8_composition_b4_tbl`, so composition table coverage continues in later chunks.

Read verification: lines 1-6876 were read completely; SHA-256 over the exact chunk text is `af98d1202f0c756e9a1ebc1f526b8a50284904456d6743e1a3f6bed933829766`.

## File Role

`u8_textprep_data.h` supplies private lookup data for illumos UTF-8 validation/text preparation, normalization, composition/decomposition, combining-class lookup, and case conversion. This chunk defines the shared lookup-table contract and the complete combining-class lookup tables, then begins canonical composition lookup tables.

The companion public header `u8_textprep.h` exposes APIs and flags that depend on these tables: `u8_validate`, `u8_strcmp`, `u8_textprep_str`, Unicode version selectors `U8_UNICODE_320`/`U8_UNICODE_500`, and normalization/case flags.

## Declarations And Data

- Lines 1-67: CDDL and Unicode permission notices.
- Lines 68-75: include guard, `<sys/types.h>`, C++ wrapping.
- Lines 77-124: table traversal scheme. UTF-8 chars are treated as 4-byte keys; shorter encodings are left-padded.
- Lines 126-130: `u8_displacement_t { uint16_t tbl_id; uint16_t base; }`.
- Lines 132-141: sentinels `N_ == 0xff` for undefined entries and `FIL_ == 0xf7` for final-table character boundaries.
- Lines 143-216: `u8_common_b1_tbl[2][256]`.
- Lines 218-362: `u8_combining_class_b2_tbl[2][2][256]`.
- Lines 364-981: `u8_combining_class_b3_tbl[2][9][256]`.
- Lines 983-4732: `u8_combining_class_b4_tbl[2][55][256]`, storing direct canonical combining class values.
- Lines 4734-4803: `u8_composition_b1_tbl[2][256]`.
- Lines 4805-4881: `u8_composition_b2_tbl[2][1][256]`.
- Lines 4883-5768: `u8_composition_b3_tbl[2][5][256]`, including `0x8000`-tagged entries for later 16-bit fourth-byte tables.
- Lines 5770-6876: beginning of `u8_composition_b4_tbl[2][41][257]`.

## Control Flow

There is no executable code. Consumers perform data-driven trie lookup:

1. Convert each UTF-8 character into a 4-byte lookup key.
2. Use byte 1 in a `b1` table.
3. Use byte 2 in the selected `b2` table.
4. Use byte 3 in the selected `b3` table.
5. Use byte 4 in a `b4` table.

Combining-class lookup returns the class directly from `u8_combining_class_b4_tbl`. Composition/decomposition/case mappings use fourth-byte table entries as start/end offsets into final byte tables. Entries with `tbl_id >= 0x8000` select 16-bit fourth-byte tables defined later.

## State And Dependencies

All data in this chunk is `static const`; there is no mutable state. The outer `[2]` dimension represents Unicode 3.2.0 and Unicode 5.0.0.

Dependencies visible here:

- `<sys/types.h>` for `uchar_t` and `uint16_t`.
- `u8_textprep.h` for public APIs/flags.
- `usr/src/uts/common/sys/Makefile`, which exports `u8_textprep.h` and `u8_textprep_data.h`.
- Generated Unicode data from tools referenced as `PSARC/2007/149/materials/tools.tar.gz`.

## Risks

- This chunk ends inside `u8_composition_b4_tbl`; later chunks are required for complete composition behavior.
- `N_ == 0xff` must never be treated as a real table id.
- `0x8000` dispatch to 16-bit tables is required to avoid truncating final-table offsets.
- `[257]` fourth-byte tables rely on `index` and `index + 1` range lookup.
- Unicode version selection affects filesystem name normalization semantics, especially for ZFS-style normalized comparisons.
- Large `static const` tables can duplicate object data if broadly included.
- License notices combine CDDL and Unicode terms and must be preserved.

## Cross-Chunk References

- `u8_composition_b4_tbl` continues through line 8645.
- `u8_composition_b4_16bit_tbl` starts at line 8647.
- `u8_composition_final_tbl` starts at line 9004.
- Decomposition tables start at line 10667.
- Case-conversion tables start at line 27453.
- Macro cleanup and include guard closure occur at lines 35367-35374.

## Summary

Lines 1-6876 establish the Unicode textprep lookup format, provide complete combining-class data for Unicode 3.2.0 and 5.0.0, and begin canonical composition data. The encoded lookup path is central to UTF-8 normalization and filesystem name comparison through `u8_textprep.h`; main risks are sentinel handling, 8-bit versus 16-bit table dispatch, version consistency, and the mid-table chunk boundary.