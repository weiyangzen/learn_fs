# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_hkscs_utf8.h lines 1-8168

## Scope

This chunk covers the first 8,168 lines of `kiconv_hkscs_utf8.h`. It includes the license/header guard, `_KERNEL` gate, `KICONV_HKSCS_UTF8_MAX`, and the prefix of the static BIG5-HKSCS(2004)-to-UTF-8 mapping table. The chunk ends mid-table at key `0xbce1`; later chunks contain the rest of the initializer and closing preprocessor blocks.

## APIs And Data Contracts

- Header guard: `_SYS_KICONV_HKSCS_UTF8_H`.
- Kernel-only declaration: table content is inside `#ifdef _KERNEL`.
- Macro: `KICONV_HKSCS_UTF8_MAX` is `18403`.
- Data object: `static kiconv_table_array_t kiconv_hkscs_utf8[]`.
- Element contract from `kiconv_cck_common.h`: `uint32_t key` plus `uchar_t u8[4]`.

The table is sorted by encoded HKSCS key and stores 2-, 3-, or 4-byte UTF-8 payloads.

## Chunk Contents

- Lines 1-66: CDDL, Sun, and Unicode notices.
- Lines 68-81: guard/opening declarations and table start.
- Lines 82-8168: 8,083 mapping rows.

Structured findings:

- First row: `0x0000 -> { 0xEF, 0xBF, 0xBD }`.
- Last row in chunk: `0xbce1 -> { 0xE6, 0xBE, 0x84 }`.
- No duplicate keys found in this chunk.
- Keys are strictly ascending.
- Row byte lengths: 107 two-byte rows, 6,574 three-byte rows, 1,402 four-byte rows.
- Special sentinel rows: `0x8862`, `0x8864`, `0x88a3`, `0x88a5` map to `0xFF` placeholder sequences, with adjacent comments showing decomposed UTF-8 alternatives.

## Control Flow

No runtime control flow is defined here. Runtime behavior is data-driven: consumers include the header, binary-search or otherwise index the sorted table, infer output size from the first UTF-8 byte, and copy `u8[]` bytes to the output buffer.

## State And Dependencies

The table is effectively immutable conversion data, though not declared `const`. It depends on kernel kiconv types and UTF-8 helper tables from the common kiconv stack, especially `kiconv_table_array_t`, `uchar_t`, and `u8_number_of_bytes`.

Related files visible in the same subsystem include reverse and compatibility tables: `kiconv_utf8_hkscs.h`, `kiconv_cp950hkscs_utf8.h`, and `kiconv_utf8_cp950hkscs.h`.

## Risks And Cross-Chunk Notes

- Full table count must later be reconciled against `KICONV_HKSCS_UTF8_MAX`.
- Binary-search consumers require the complete table to remain sorted.
- `0xFF` sentinel rows need special consumer handling; they are not ordinary UTF-8.
- Because the array is `static` in a header, multiple includes can duplicate a large table.
- This chunk is syntactically incomplete by itself; the next chunk should continue at `0xbce2` and preserve key ordering.