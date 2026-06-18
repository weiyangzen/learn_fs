# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h lines 1-8439

## Scope

This report covers lines 1-8439 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_cp950hkscs_utf8.h` for `learn_fs` subset A. The file is a kernel-only generated/static conversion table, not executable filesystem logic. This chunk starts at the CDDL/Unicode license block and header guard, defines the table metadata, opens the `kiconv_cp950hkscs_utf8[]` initializer, and continues through CP950HKSCS key `0xbf4c`. The closing initializer and header guard are outside this chunk; the whole source file has 18,412 lines.

## Public Surface And APIs

This chunk contributes two kernel-visible symbols when `_KERNEL` is defined:

- `KICONV_CP950HKSCS_UTF8_MAX` is defined as `18322`, the advertised maximum mapping count for CP950HKSCS-to-UTF-8 conversion.
- `static kiconv_table_array_t kiconv_cp950hkscs_utf8[]` starts the mapping table from CP950HKSCS code units to UTF-8 byte arrays.

The include guard is `_SYS_KICONV_CP950HKSCS_UTF8_H`, with `extern "C"` wrapping for C++ consumers. Because the table is declared `static` in a header, each translation unit that includes it gets its own internal-linkage copy. The table element type comes from `kiconv_cck_common.h`: `kiconv_table_array_t` contains a `uint32_t key` and `uchar_t u8[4]` for CCK-encoding-to-UTF-8 mappings.

## Data Layout Visible In This Chunk

The initializer begins with a sentinel/default-style mapping:

- `0x0000 -> { 0xEF, 0xBF, 0xBD }`, which is UTF-8 for U+FFFD replacement character.

After that, keys are CP950HKSCS double-byte values in ascending numeric order. This chunk contains 8,358 initializer rows total: the `0x0000` row plus 8,357 high-byte rows from `0x8840` through `0xbf4c`. A numeric scan found no non-monotonic keys in this line range, which is important because the shared kiconv layer exposes binary-search table lookup.

Visible key coverage by leading byte is:

- `0x88`: 73 rows, `0x8840`-`0x88aa`.
- `0x89` through `0xa2`: mostly dense Big5-style lead-byte ranges using valid trail bytes `0x40`-`0x7e` and `0xa1`-`0xfe`, with gaps where CP950HKSCS has no mapping.
- `0xa3`: 95 rows, ending at `0xa3e1`.
- `0xa4` through `0xbe`: full 157-row lead-byte ranges, `xx40`-`xxfe` over valid Big5 trail-byte slots.
- `0xbf`: starts in this chunk with 13 rows, `0xbf40`-`0xbf4c`; continuation begins in the next chunk.

UTF-8 output byte lengths visible here are either 2-byte or 3-byte sequences. A scan counted 102 two-byte outputs and 8,256 three-byte outputs in this chunk. The table stores outputs in a four-byte fixed field, so shorter sequences rely on zero-initialization of the unused trailing bytes in C aggregate initialization.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is table-driven:

1. Higher-level kiconv code recognizes the normalized code name `cp950hkscs` as code id `17` in `uts/common/os/kiconv.c`.
2. Traditional Chinese conversion logic validates Big5-family byte sequences using macros such as `KICONV_TC_IS_BIG5_1st_BYTE()` and `KICONV_TC_IS_BIG5_2nd_BYTE()` from `kiconv_tc.h`.
3. The CP950HKSCS double-byte value is used as a lookup key in a `kiconv_table_array_t` table.
4. Shared CCK helpers, including `kiconv_binsearch()`, are the visible dependency for sorted-table lookup.
5. The matched `u8[]` bytes are emitted to the UTF-8 output buffer by conversion code outside this header.

Because this chunk only defines data, all buffer accounting, invalid-sequence handling, replacement behavior, and errno decisions are delegated to the including conversion implementation and common kiconv helpers.

## State And Dependencies

State is immutable static table data after compilation. There are no locks, counters, mutable globals, allocation paths, I/O paths, or filesystem-facing state transitions in this chunk.

Direct dependencies visible or implied by this chunk are:

- `_KERNEL`: the table is only exposed for kernel builds.
- `kiconv_table_array_t`, `uchar_t`, and integer typedefs from the common kiconv/sys type headers.
- `kiconv_cck_common.h` for the CCK table shape and binary-search helper contract.
- `kiconv_tc.h` for Big5-family byte validity rules used by Traditional Chinese conversion code.
- `uts/common/os/kiconv.c` for public code-name registration; `cp950hkscs` maps to internal code id `17`.
- Companion reverse mapping header `kiconv_utf8_cp950hkscs.h` for UTF-8-to-CP950HKSCS conversion, outside this chunk.

## Risks And Invariants

The key invariants are table completeness, strict ascending key order, output byte correctness, and agreement between `KICONV_CP950HKSCS_UTF8_MAX` and the complete table size across all chunks. This chunk alone cannot verify the final count because it ends mid-initializer.

Important risks:

- Generated-data drift: a single wrong byte sequence silently corrupts filename/text conversion for affected CP950HKSCS characters.
- Binary-search fragility: any out-of-order row would make lookup unreliable; this chunk is sorted, but later chunks must preserve that invariant.
- Fixed-width UTF-8 storage: two-byte entries depend on implicit zero fill in `u8[4]`; consumers must stop output at the intended UTF-8 length rather than blindly copying four bytes.
- Header-level `static` data can duplicate a large table in every including object if included broadly.
- This file maps many characters into Unicode private-use-looking ranges such as `EF 8C..EF 95` early in the table; compatibility with external CP950HKSCS expectations depends on the exact Unicode data version and Sun modifications noted in the header comments.
- The chunk is unrelated to filesystem/block semantics except as kernel text conversion infrastructure that can affect path/name encoding when used by filesystems or kernel consumers.

## Cross-Chunk References

The next chunk must continue the open `kiconv_cp950hkscs_utf8[]` initializer at key `0xbf4d`, confirm that key ordering remains ascending, and eventually verify the closing brace, `_KERNEL`/C++ guard closure, and total mapping count against `KICONV_CP950HKSCS_UTF8_MAX`. Later chunks also need to identify the final key range and whether any four-byte UTF-8 outputs appear after line 8439.