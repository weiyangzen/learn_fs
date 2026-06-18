# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_hkscs_utf8.h lines 8169-16638

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is in scope.
- Source span read completely: lines 8169-16638 of `usr/src/uts/common/sys/kiconv_hkscs_utf8.h`.
- This is chunk 2 of an oversized generated-style conversion header. It is wholly inside the `static kiconv_table_array_t kiconv_hkscs_utf8[]` initializer and does not include the declaration or closing brace.

## APIs and Data Structures

- No callable API, macro, typedef, or function body is defined in this chunk.
- The chunk contributes rows to `kiconv_hkscs_utf8[]`, the HKSCS-2004 to UTF-8 mapping table declared earlier in the file under `_KERNEL`.
- Adjacent context shows the associated constant `KICONV_HKSCS_UTF8_MAX` is declared before the table with value `18403`.
- `kiconv_table_array_t` is defined in `kiconv_cck_common.h` as:
  - `uint32_t key`
  - `uchar_t u8[4]`
- Each entry in this chunk maps a packed two-byte BIG5-HKSCS code value to a UTF-8 byte sequence stored inline in `u8`.

## Mapping Coverage

- The chunk contains 8,470 table rows.
- First row: `0xbce2 -> { 0xE6, 0xBD, 0x91 }`.
- Last row: `0xf34b -> { 0xE8, 0xB6, 0xAC }`.
- It starts immediately after prior-chunk key `0xbce1` and ends immediately before next-chunk key `0xf34c`.
- Keys are strictly increasing within the chunk and all visible trail bytes are in valid BIG5 trail-byte ranges (`0x40-0x7e` or `0xa1-0xfe`).
- UTF-8 byte widths in this chunk:
  - 8,389 rows use three bytes.
  - 78 rows use two bytes.
  - 3 rows use four bytes: `0xc87a`, `0xc87c`, and `0xc8a4`.
- No duplicate keys or duplicate UTF-8 byte sequences were found within this chunk.

## Control Flow

- There is no local executable control flow. Runtime behavior depends on converter code that includes this static table and searches it.
- The strict key ordering is a functional contract for binary-search style lookup code. `kiconv_cck_common.h` declares `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)`.
- The table rows do not carry explicit UTF-8 lengths. Consumers must infer or otherwise know how many bytes in `uchar_t u8[4]` are payload for each result.

## State and Dependencies

- State is compile-time static mapping data. Because the array is declared `static` in a header, every translation unit that includes the header can receive its own private copy.
- Dependencies include `_KERNEL` guarding, `kiconv_table_array_t`, `uint32_t`, `uchar_t`, and BIG5/HKSCS byte validity rules from nearby kiconv headers such as `kiconv_tc.h`.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_hkscs_utf8.h` among exported/common sys headers.

## Risks and Edge Cases

- Data integrity is the main risk: a wrong byte literal or missing row silently changes conversion behavior for one HKSCS character.
- The mix of two-, three-, and four-byte UTF-8 payloads means lookup consumers must not assume uniform sequence length.
- The `uchar_t u8[4]` field has no separate length member; shorter sequences rely on consistent consumer handling.
- Gaps are normal for invalid or unmapped BIG5 byte slots. Consumers must rely on lookup failure handling rather than assuming contiguous keys.
- `KICONV_HKSCS_UTF8_MAX` is outside this chunk; full-table row-count validation must reconcile all chunks, including sentinel or non-mapping rows.

## Cross-Chunk References

- Chunk 1 owns the file preamble, guards, `KICONV_HKSCS_UTF8_MAX`, the table declaration, the `0x0000` replacement entry, and mappings up through `0xbce1`.
- This chunk continues the same array from `0xbce2` through `0xf34b` without opening or closing syntax.
- Chunk 3 resumes at `0xf34c`, finishes the table at `0xfefe`, and closes the array and file guards.
- The final per-file report should merge this with adjacent chunk reports; it was not created here.