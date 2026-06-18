# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_ja_unicode_to_jis.h lines 7090-7616

## Scope

This chunk is the final chunk of the kernel-only Japanese Unicode-to-JIS/EUC conversion header. It covers the end of `kiconv_ja_ucs2_to_euc16_block_E7`, all high-byte blocks `F9`, `FA`, and `FF`, the top-level UCS-2 high-byte index table, the EUC-JP-MS/CP932 Unicode override macro, and the header epilogue.

## APIs and Data Exposed

- `kiconv_ja_ucs2_to_euc16_block_F9[]`: static `kiconv_ja_euc16_t` lookup block for Unicode code points `U+F900..U+F9FF`. Almost every entry is `NODEST`; only `U+F929 -> 0xf445` and `U+F9DC -> 0xf472` are mapped.
- `kiconv_ja_ucs2_to_euc16_block_FA[]`: static lookup block for `U+FA00..U+FAFF`. The mapped span is concentrated in compatibility ideographs `U+FA0E..U+FA2D`, producing destination values `0xf434` through `0xf47d` with gaps; the rest of the block is `NODEST`.
- `kiconv_ja_ucs2_to_euc16_block_FF[]`: static lookup block for `U+FF00..U+FFFF`. It maps fullwidth punctuation/digits/Latin letters, halfwidth Katakana-like values `U+FF61..U+FF9F` to `0x00a1..0x00df`, and a few currency/symbol forms near `U+FFE3`/`U+FFE5`.
- `kiconv_ja_ucs2_to_euc16_index[]`: static pointer index from UCS-2 high byte to a 256-entry block. Present blocks point to arrays defined earlier in this header; absent blocks are explicit `NULL` entries.
- `KICONV_JA_CNV_U2_TO_EUCJPMS(id, e, u)`: macro that initializes `e` to `KICONV_JA_NODEST`, then applies EUC-JP-MS/CP932-only remaps for eight selected Unicode values.

## Control Flow

There are no functions in this chunk. Runtime behavior is table selection plus macro expansion: callers split UCS-2 into high/low bytes, index `kiconv_ja_ucs2_to_euc16_index[]`, check for `NULL`, then index the selected block by low byte. `NODEST` means unmapped.

The override macro only assigns a destination when `id` is `KICONV_JA_TBLID_EUCJP_MS` or `KICONV_JA_TBLID_CP932`; otherwise it leaves `e` as unmapped.

## State and Dependencies

All arrays are `static const`, with no mutable state. The chunk depends on `sys/kiconv_ja.h` for `kiconv_ja_euc16_t`, `KICONV_JA_NODEST`, `KICONV_JA_TBLID_EUCJP_MS`, and `KICONV_JA_TBLID_CP932`. The local `NODEST` alias is undefined at the end. The table body is guarded by `_KERNEL`.

## Risks and Edge Cases

- Consumers must check `NULL` index entries before second-level lookup.
- `KICONV_JA_NODEST` is `0xffff`; code must treat it as an output sentinel, not a valid destination.
- Block `FF` mixes two-byte EUC/JIS values with `0x00a1..0x00df` halfwidth values, so downstream encoding must honor this table contract.
- `KICONV_JA_CNV_U2_TO_EUCJPMS` evaluates arguments repeatedly and is not wrapped in `do { } while (0)`, so call sites should use simple expressions and braces in conditional contexts.
- Table correctness is data-sensitive: wrong literals compile cleanly but alter character conversion.

## Cross-Chunk References

Earlier chunks define the blocks referenced by `kiconv_ja_ucs2_to_euc16_index[]`, including `00..04`, `20..26`, `30`, `32..33`, `4E..9F`, and `E0..E7`. This chunk begins at the tail of block `E7`, observing only that final offsets `0x78..0xFF` are unmapped. The reverse-direction header `kiconv_ja_jis_to_unicode.h` contains related MS/CP932 override macros, so bidirectional behavior depends on keeping these exceptions aligned.