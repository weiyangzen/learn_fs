# sources/distributed-fs/ceph-client/fs/nls/nls_cp932.c lines 1-4152

## Scope

This chunk covers the generated CP932/SJIS translation data from the file header through the first half of the Unicode-to-charset lookup tables. It includes all `c2u_*` lead-byte pages, the `page_charset2uni` dispatch table, the `u2c_00hi` Latin-1 supplement table, and Unicode high-byte reverse pages from `u2c_03` through the first 38 lines of `u2c_6B`. The range stops in the middle of `u2c_6B`; conversion callbacks, NLS registration, case folding tables, and the remaining reverse lookup pages are in later chunks.

## Purpose

The data implements the static mapping backbone for the Linux NLS `cp932` module used by filesystems that need Japanese Microsoft Code Page 932, with `sjis` as an alias. CP932 is mostly Shift-JIS but includes Microsoft extensions, vendor/private rows, halfwidth katakana behavior, and compatibility ideographs that ordinary JIS-only Shift-JIS tables may not cover.

The chunk is generated translation data rather than hand-written logic. Its job is to let the later `char2uni()` and `uni2char()` callbacks perform O(1) table lookup for filenames and other filesystem-visible strings when a mount selects this NLS charset.

## Important APIs, Types, and Tables

`static const wchar_t c2u_XX[256]` tables map a two-byte CP932 sequence to Unicode. The first byte selects the table and the second byte indexes it directly. This chunk defines pages for lead bytes `0x81`-`0x84`, `0x87`-`0x9F`, `0xE0`-`0xEA`, `0xED`, `0xEE`, and `0xFA`-`0xFC`. Zero entries mark invalid byte pairs.

The early `c2u_*` pages cover punctuation, fullwidth ASCII, kana, Greek, Cyrillic, box drawing, circled numbers, Japanese common kanji, extended kanji, IBM/NEC extension rows, and Unicode compatibility/private-extension values such as `0xFAxx` and `0xF9DC`.

`page_charset2uni[256]` is the lead-byte dispatch table for `char2uni()`. It contains `NULL` for invalid CP932 lead bytes and pointers to the `c2u_*` page for valid lead bytes. This is the primary integration point from this chunk to the later decode callback.

`u2c_00hi[256 - 0xA0][2]` handles Unicode code points with high byte `0x00` and low byte at least `0xA0`. It maps selected Latin-1 symbols, such as currency, section, degree, division, and overline-like characters, back to two-byte CP932 sequences.

`static const unsigned char u2c_XX[512]` tables map Unicode pages back to CP932. Each Unicode low byte indexes a two-byte pair at `cl * 2` and `cl * 2 + 1`. This chunk includes reverse pages for Unicode high bytes `0x03`, `0x04`, `0x20`-`0x26`, `0x30`, `0x32`, `0x33`, and `0x4E`-`0x6B` up to line 4152.

The reverse pages in this range include Greek and Cyrillic (`u2c_03`, `u2c_04`), punctuation and symbols (`u2c_20`-`u2c_26`), CJK punctuation/kana (`u2c_30`), enclosed/CJK unit symbols (`u2c_32`, `u2c_33`), and a large run of CJK unified ideograph mappings beginning at `u2c_4E`.

## Control Flow

There is no executable control flow in this chunk. The effective lookup flow is determined by table layout:

For CP932-to-Unicode decode, later code treats bytes `0x00`-`0x7F` and halfwidth kana `0xA1`-`0xDF` specially. For other multibyte input, it uses the first byte to fetch `page_charset2uni[first]`, then returns `page[second]` if nonzero. A `NULL` page or zero entry means the byte sequence is invalid.

For Unicode-to-CP932 encode, later code checks ASCII and halfwidth katakana shortcuts first, then uses `page_uni2charset[unicode >> 8]`. The pages defined here are consumed by that dispatch table. If the selected page exists, the low byte indexes a two-byte pair. A `{0x00, 0x00}` pair means the Unicode scalar has no CP932 encoding.

Line 4152 is a chunk boundary inside `u2c_6B[512]`; the table is incomplete in this document and must be reconciled with the next chunk before reasoning about the full Unicode `0x6Bxx` reverse page.

## State and Persistence Behavior

All data in this chunk is `static const` and read-only after module load. It does not allocate memory, mutate state, persist filesystem metadata, perform I/O, or cache runtime results. Persistence effects happen only indirectly: filesystems using the NLS table may encode or decode on-disk filenames through these mappings, so any table change alters filename interoperability for CP932-mounted filesystems.

The generated tables are part of the kernel/module image. Their stability is effectively ABI-like for users with existing on-disk names encoded through this charset.

## Dependencies and Integration Points

The file includes Linux kernel and NLS headers: `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`. In this chunk, the important type dependency is `wchar_t` for Unicode values and `unsigned char` pairs for charset bytes.

The tables are consumed by later symbols in the same file:

- `char2uni()` uses `page_charset2uni` plus ASCII and halfwidth-katakana fast paths.
- `uni2char()` uses `u2c_00hi` and the later `page_uni2charset` dispatcher, which points at `u2c_*` pages defined here and in later chunks.
- The final `struct nls_table` registers those callbacks and case tables under charset `cp932` and alias `sjis`.

Filesystem integration is through the generic Linux NLS layer. Filesystems such as FAT-like or other charset-aware mounts can request `cp932`/`sjis`; the NLS core then calls the registered conversion callbacks. This file is under the imported Ceph client source tree, but the code itself is the Linux NLS CP932 module rather than Ceph-specific logic.

## Risks

Generated table correctness is the main risk. A single wrong entry can silently map a filename character to the wrong Unicode scalar or encode a Unicode name to the wrong CP932 byte sequence.

Zero entries are semantically meaningful invalid markers. Accidentally replacing a zero with a byte pair, or vice versa, changes validation behavior and can permit invalid byte sequences or reject valid CP932 names.

The decode and encode tables must remain reciprocal where CP932 defines a unique mapping. CP932 has compatibility and vendor-extension cases where round-trip behavior is subtle; changes around `0x87`, `0xED`/`0xEE`, and `0xFA`-`0xFC` should be checked especially carefully.

Chunk-local review cannot validate `u2c_6B` fully because the table continues after line 4152. Any generated-table audit must join this chunk with the following range before checking syntax, initializer length, or complete reverse coverage for Unicode page `0x6B`.

The tables are large enough that manual edits are error-prone. Alignment between comments, low-byte offsets, array length, and generated values matters because lookup code indexes directly without searching.

## Test and Validation Signals

Useful validation should include a module build of `nls_cp932.c`, which catches malformed array initializers, incomplete tables after reconciliation, missing symbols, and type mismatches.

Round-trip tests should cover ASCII, halfwidth katakana, fullwidth digits/letters, hiragana, katakana, Greek, Cyrillic, punctuation, box drawing, common kanji in `0x88`-`0x9F`, extended kanji in `0xE0`-`0xEA`, and vendor-extension rows `0xED`/`0xEE`/`0xFA`-`0xFC`.

Negative tests should feed invalid lead bytes, invalid trail bytes, zero-marked table slots, truncated two-byte sequences, and Unicode values whose reverse table entry is `{0x00, 0x00}`. Expected results are `-EINVAL` for unmapped values and `-ENAMETOOLONG` when output/input bounds are insufficient.

Compatibility tests should compare selected mappings against a trusted CP932 reference table, especially duplicate-looking compatibility values such as Roman numerals, fullwidth symbols, NEC selected IBM extensions, and `FAxx` compatibility ideographs.

Filesystem-level signals include creating, listing, unmounting, remounting, and deleting files whose names exercise the table groups above under a CP932/SJIS NLS mount. The observed Unicode names after remount should match the original intended characters.

## Cross-Chunk Notes

The later chunks provide `page_uni2charset`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, `struct nls_table`, and module registration. This chunk should be merged with those callback definitions to describe the complete conversion behavior.

The next chunk must complete `u2c_6B`; do not treat line 4152 as the end of that array during final reconciliation.
