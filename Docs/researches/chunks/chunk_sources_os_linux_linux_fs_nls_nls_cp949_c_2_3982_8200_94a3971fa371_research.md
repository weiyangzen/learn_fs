# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 3982-8200

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/linux/linux` is explicitly in scope.
- Source span read: lines 3982-8200 of `fs/nls/nls_cp949.c`.
- This is chunk 2 of a chunked Linux NLS CP949/UHC module. It begins inside the byte-to-Unicode table for lead byte `0xF1`, completes byte-to-Unicode pages through `0xFD`, defines the byte-to-Unicode lead-byte index, and defines the first large block of Unicode-to-CP949 reverse lookup pages.
- The chunk ends inside `u2c_7A[512]`; it does not include the rest of the reverse Unicode pages, `page_uni2charset`, case tables, conversion callbacks, `struct nls_table`, registration functions, or module metadata.

## APIs and Data Structures

- `c2u_F1[256]` tail plus complete `c2u_F2` through `c2u_FD`: `static const wchar_t` byte-to-Unicode pages for high CP949 lead bytes. Entries before the valid trail-byte area are mostly `0x0000`; populated positions map CP949 two-byte sequences to Unicode scalar values, including ordinary CJK ideographs and compatibility/private-use style values such as `U+F9FC..U+FA0B`.
- `page_charset2uni[256]`: top-level lead-byte dispatch table for the later CP949 byte decoder. It maps lead bytes `0x81..0xC8`, skips `0xC9`, then maps `0xCA..0xFD`; all other entries are `NULL`. This table references `c2u_81` through `c2u_FD`, many of which are defined in earlier chunks.
- `u2c_01`, `u2c_02`, `u2c_03`, `u2c_04`, `u2c_11`, `u2c_20` through `u2c_26`, `u2c_30` through `u2c_33`, and `u2c_4E` through the first part of `u2c_7A`: `static const unsigned char [512]` reverse lookup pages. Each Unicode low byte consumes two array bytes at offsets `low * 2` and `low * 2 + 1`; `{0x00, 0x00}` means unmapped.
- The reverse pages cover Latin Extended and spacing marks (`U+0100..U+02FF`), Greek (`U+03xx`), Cyrillic (`U+04xx`), Hangul Jamo (`U+11xx`), punctuation/currency/symbol/box-drawing blocks (`U+20xx..U+26xx`), CJK symbols and Hangul compatibility jamo (`U+30xx..U+33xx`), and a dense run of CJK ideograph pages from `U+4E00` through `U+7Axx`.

## Control Flow

There are no functions, loops, or conditional branches in this chunk. Runtime behavior is implicit in how later callbacks consume these tables:

- CP949-to-Unicode conversion will use the first byte as an index into `page_charset2uni`. If the selected page pointer is `NULL`, or the selected trail-byte slot contains `0x0000`, the later decoder rejects the sequence.
- Unicode-to-CP949 conversion will use the Unicode high byte to select one of the `u2c_*` pages through `page_uni2charset` in a later chunk. Once a page is selected, the Unicode low byte indexes a two-byte output pair.
- Sparse reverse pages rely on zero pairs as the invalid sentinel. Single-byte ASCII and any special non-table paths are necessarily handled outside this chunk by the later conversion functions.

## State and Dependencies

- All visible state is immutable `static const` lookup data. There is no allocation, locking, reference counting, I/O, or module lifecycle code in this span.
- The arrays depend on kernel types and NLS contracts introduced earlier in the file, especially `wchar_t` and the later `struct nls_table` callback signatures from Linux NLS headers.
- `page_charset2uni` depends on byte-to-Unicode page arrays defined outside this chunk (`c2u_81` through `c2u_F0`) as well as the pages completed here.
- The reverse `u2c_*` pages depend on a later `page_uni2charset` index table to be reachable. Pages defined here but omitted from that later index would be dead data.

## Risks and Edge Cases

- Data integrity is the primary risk. These generated constants are the conversion behavior; an incorrect literal silently corrupts filename encoding/decoding for filesystems using NLS `cp949`.
- Chunk boundaries split logical declarations. The chunk starts after `c2u_F1` has already been declared and ends before `u2c_7A` closes, so merge validation must combine adjacent chunks before checking table completeness.
- `0x0000` in `c2u_*` and `{0x00, 0x00}` in `u2c_*` are sentinels, not mappings.
- The lead-byte index deliberately leaves `0xC9`, `0xFE`, and `0xFF` unmapped while allowing broad `0x81..0xFD` coverage.
- CP949/UHC contains compatibility and vendor-extension mappings. Values in the `U+F9xx` and `U+FAxx` areas and extended byte pairs in `0xCA..0xFD` are intentional compatibility behavior.

## Cross-Chunk References

- Earlier chunk(s) define the file prologue, kernel includes, generated-table comment, `c2u_81` through most of `c2u_F1`, and any special high-ASCII reverse table used by `uni2char`.
- This chunk's `page_charset2uni` references `c2u_81..c2u_F0` from earlier chunk(s) and `c2u_F1..c2u_FD` from the boundary/current span.
- Later chunk(s) continue and close `u2c_7A[512]`, define additional reverse pages beyond `U+7Axx`, build `page_uni2charset[256]`, and define case tables plus `uni2char`, `char2uni`, the `nls_table`, init/exit registration, and module metadata.
- The final per-file report must be produced only after all chunks for `sources/os/linux/linux/fs/nls/nls_cp949.c` are available; this chunk report intentionally does not create that merged artifact.