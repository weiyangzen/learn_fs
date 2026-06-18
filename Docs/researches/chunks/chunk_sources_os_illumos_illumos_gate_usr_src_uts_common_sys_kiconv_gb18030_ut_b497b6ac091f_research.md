# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h lines 8451-16906

## Scope

This report covers lines 8451-16906 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_gb18030_utf8.h` for `learn_fs` subset A. The entire chunk is inside the kernel-only `static kiconv_table_array_t kiconv_gbk_utf8[]` initializer, continuing the two-byte GBK/GB18030-to-UTF-8 mapping table that began in chunk 1. It contains mapping data only: no functions, macros, conditionals, or table boundaries are introduced in this slice.

## Public And Internal APIs Covered

- No callable API is defined in this chunk.
- The chunk contributes 8,456 rows to `kiconv_gbk_utf8[]`, the static table for GB18030 two-byte character input mapped to UTF-8 byte arrays.
- The table element type is `kiconv_table_array_t` from `kiconv_cck_common.h`:
  - `uint32_t key`: packed source character code.
  - `uchar_t u8[4]`: UTF-8 output bytes, with this chunk using three explicit bytes per row and the fourth slot zero-initialized by C.
- The relevant full-table count contract, declared earlier in the file, is `KICONV_GBK_UTF8_MAX (23941)`.

## Data Covered

- First row in this chunk: line 8451, `0xAD46 -> E7 92 85`.
- Last row in this chunk: line 16906, `0xD9A6 -> E4 BD B4`.
- The rows are sorted by ascending GBK/GB18030 key across the chunk.
- Syntax check of the requested range found 8,456 initializer rows, all matching the same `0xKEY, { 0xNN, 0xNN, 0xNN },` shape.
- UTF-8 payload shape check found all rows using valid three-byte UTF-8 byte ranges: lead byte `0xE4` through `0xE9` or private-use lead `0xEE`, followed by continuation bytes.
- The chunk includes both ordinary Unicode mappings and GBK/GB18030 compatibility/private-use mappings. The private-use style entries use `0xEE ...` UTF-8 sequences and appear within the two-byte table.
- A visible transition occurs near the end of the chunk: line 16900 still maps sequential keys into `E8 B4 xx`, while line 16901 begins key `0xD9A1` mapping back to lower Unicode ranges such as `E4 BD 9F`. This is table data, not control flow.

## Control Flow And Behavior

There is no local control flow in this chunk. Runtime behavior is supplied by the kiconv implementation that includes or otherwise compiles this static header table:

1. GB18030/GBK input validation classifies a character as a two-byte sequence using the byte-range macros in `kiconv_sc.h`.
2. The packed two-byte source code is looked up in `kiconv_gbk_utf8[]`.
3. On match, the `u8` array bytes from the table element become the UTF-8 output.
4. On miss or invalid byte sequence, behavior is determined by the caller's kiconv error/replacement policy outside this header.

The sorted ordering visible in this chunk is therefore a behavioral invariant: any binary-search-based lookup depends on the table remaining ordered by `key`.

## State And Data Structures

- The only state represented here is immutable static conversion data.
- No per-conversion state, locks, reference counts, allocations, or mutable globals are present in the chunk.
- Each row is independent, but the table as a whole has global invariants:
  - rows must remain sorted by `key`;
  - row count must stay consistent with `KICONV_GBK_UTF8_MAX`;
  - payload bytes must remain valid UTF-8 byte sequences for the output copy path;
  - the table must remain inside the surrounding `_KERNEL` guard established earlier in the file.

## Dependencies

- `kiconv_table_array_t` and `uchar_t` are provided by the broader illumos kernel/kiconv header environment, specifically `kiconv_cck_common.h` for the table shape.
- `kiconv_sc.h` defines GBK/GB18030 byte validation macros that determine whether runtime input can reach this two-byte table.
- `uts/common/sys/Makefile` lists `kiconv_gb18030_utf8.h` with the exported kiconv headers.
- Companion reverse-direction data lives in `kiconv_utf8_gb18030.h`; this chunk is only for GB18030/GBK to UTF-8.
- `uts/common/os/kiconv.c` registers `"gb18030"` and related Simplified Chinese encoding names in the kernel iconv surface, but direct textual references to `kiconv_gbk_utf8` outside this header were not found in the searched tree, so use may be indirect through kiconv build/include structure.

## Risks And Invariants

- Ordering risk: a misplaced row would break binary search or produce missed mappings.
- Count drift risk: edits in this chunk must preserve the full `KICONV_GBK_UTF8_MAX` table length, even though the macro is declared outside the chunk.
- Boundary risk: this chunk begins and ends mid-table. The previous chunk must end at `0xAD45`; the next chunk must continue at `0xD9A7`.
- Encoding risk: the `u8[4]` field is fixed-width, while rows here initialize only three bytes. Callers must infer/copy the correct UTF-8 length from byte classification or zero termination, not assume all four slots are meaningful payload.
- Data-generation risk: many rows are mechanical mapping constants. Manual edits are easy to get wrong and should be verified against GB18030/GBK source tables and by structural checks over the whole header.
- Private-use compatibility risk: rows using `0xEE ...` are not ordinary CJK scalar mappings; removing or normalizing them could break round-trip behavior expected by legacy GBK/GB18030 consumers.

## Cross-Chunk References

- Chunk 1 (`lines 1-8450`) defines the file guard, C++ wrapper, `_KERNEL` guard, `KICONV_GBK_UTF8_MAX`, `KICONV_GBK4_UTF8_MAX`, and starts `kiconv_gbk_utf8[]`; it ends at key `0xAD45`.
- This chunk continues `kiconv_gbk_utf8[]` from `0xAD46` through `0xD9A6`.
- Chunk 3 (`lines 16907-25455`) continues at key `0xD9A7`, finishes `kiconv_gbk_utf8[]` at `0xFEFE`, closes that table, and starts `kiconv_gbk4_utf8[]`.
- Later chunks cover the four-byte GB18030 table and the closing `_KERNEL`, C++ wrapper, and header guard structure.