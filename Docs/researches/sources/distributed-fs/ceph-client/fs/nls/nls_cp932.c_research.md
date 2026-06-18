# Research: sources/distributed-fs/ceph-client/fs/nls/nls_cp932.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005710`: lines 1-4152, `Docs/researches/chunks/subset-b-005710_research.md`
- `subset-b-005711`: lines 4153-7934, `Docs/researches/chunks/subset-b-005711_research.md`

## Chunk Research

### subset-b-005710: lines 1-4152

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

### subset-b-005711: lines 4153-7934

# sources/distributed-fs/ceph-client/fs/nls/nls_cp932.c lines 4153-7934

## Scope

This chunk covers the tail of the Linux kernel CP932 NLS translation module. It starts in the final rows of the `u2c_6B` Unicode-to-charset page and then contains the remaining Unicode-to-CP932 pages, the `page_uni2charset` dispatch table, ASCII-only case-folding tables, the `uni2char()` and `char2uni()` conversion callbacks, and the module registration boilerplate for the `"cp932"` charset with `"sjis"` as its alias.

The earlier chunk for the same source file defines the reverse CP932-to-Unicode pages (`c2u_*`), `page_charset2uni`, `u2c_00hi`, and the first Unicode-to-charset pages through most of `u2c_6B`. This report therefore focuses on the generated data and executable logic present in lines 4153-7934; the final per-file report should merge it with the earlier table coverage.

## Purpose

`nls_cp932.c` implements a kernel National Language Support table for Microsoft Code Page 932, a Shift-JIS variant used for Japanese filenames and filesystem metadata conversion. Filesystems that request this NLS table can translate between Linux Unicode `wchar_t` code points and on-disk CP932 byte sequences.

The chunk's main purpose is to finish the Unicode-to-CP932 lookup coverage and wire both conversion directions into `struct nls_table`. The static lookup pages encode the generated mapping from selected Unicode high-byte pages to one- or two-byte CP932 sequences. The conversion callbacks are the small runtime layer that validates buffer lengths, handles ASCII and half-width Katakana fast paths, indexes the generated pages, and reports kernel errno-style failures for unmappable or truncated input.

## Important APIs, Types, and Data

Important symbols in this chunk are:

- `u2c_6C` through `u2c_9F`, plus the final rows of `u2c_6B`: generated 512-byte lookup pages for Unicode high bytes `0x6B` through `0x9F`. Each Unicode low byte indexes two adjacent output bytes with `cl * 2` and `cl * 2 + 1`.
- `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`: sparse special pages for compatibility/private-use/full-width mappings. `u2c_FF` includes full-width punctuation, full-width ASCII letters/digits, and half-width Katakana-related values.
- `page_uni2charset[256]`: a high-byte dispatch array that maps a Unicode page number to the corresponding `u2c_*` page pointer, or `NULL` when the page has no generated CP932 mappings in this table.
- `charset2lower[256]` and `charset2upper[256]`: byte-wise case-folding tables used by the NLS layer. They only fold ASCII A-Z/a-z and leave high CP932 bytes unchanged.
- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)`: Unicode-to-CP932 callback installed in `struct nls_table`.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)`: CP932-to-Unicode callback installed in `struct nls_table`.
- `table`: the `struct nls_table` instance with `.charset = "cp932"`, `.alias = "sjis"`, conversion callbacks, and case maps.
- `init_nls_cp932()` / `exit_nls_cp932()`: module lifecycle hooks that register and unregister the table with the kernel NLS registry.
- `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(sjis)`: module metadata and aliasing for autoload/discovery.

The table format is intentionally simple: a missing Unicode mapping is encoded as output bytes `0x00, 0x00`, while a missing CP932-to-Unicode mapping in the earlier `c2u_*` tables is encoded as `0x0000`. Because `uni2char()` checks for a zero pair after lookup and `char2uni()` checks for `0x0000`, the data tables are both payload and validity bitmap.

## Control Flow

`uni2char()` begins by deriving `cl = uni & 0xFF` and `ch = (uni >> 8) & 0xFF`, so it only consults the low 16 bits of the `wchar_t` input. It first rejects zero or negative output capacity with `-ENAMETOOLONG`. It then handles Unicode `U+FF61` through `U+FF9F` as single-byte half-width Katakana by returning `cl + 0x40`, matching CP932 bytes `0xA1` through `0xDF`.

For most non-ASCII characters, `uni2char()` indexes `page_uni2charset[ch]`. When a page exists, the function requires `boundlen >= 2`, copies the two-byte mapping into `out[0]` and `out[1]`, rejects `0x00,0x00` as `-EINVAL`, and otherwise returns `2`. If no generated page exists and the Unicode high byte is zero, it handles `U+0000` through `U+007F` as one-byte ASCII and `U+00A0` and above through the earlier `u2c_00hi` table. Non-ASCII `U+0000` page mappings that are absent or zero pairs return `-EINVAL`.

`char2uni()` is the reverse runtime path. It first rejects `boundlen <= 0` with `-ENAMETOOLONG`. Bytes `0x00` through `0x7F` map directly to the same Unicode scalar and consume one byte. Bytes `0xA1` through `0xDF` map to `U+FF61` through `U+FF9F` by subtracting `0x40` and ORing with `0xFF00`, again consuming one byte. All other non-ASCII bytes require a second byte; if unavailable, the function returns `-ENAMETOOLONG`.

For two-byte candidates, `char2uni()` uses the first byte as a high-byte page index into `page_charset2uni`, which is defined earlier in the file, and the second byte as the offset into that 256-entry `wchar_t` page. If the page pointer is non-NULL and the second byte is nonzero, a nonzero Unicode result is accepted and the function returns `2`. Missing page pointers, zero second bytes, and zero table results return `-EINVAL`.

Module initialization is linear: `module_init(init_nls_cp932)` calls `register_nls(&table)` when the module is loaded or built-in init runs; `module_exit(exit_nls_cp932)` calls `unregister_nls(&table)` during unload. The conversion callbacks are only reachable after successful registration through NLS consumers.

## State and Persistence Behavior

This chunk has no mutable per-file or per-mount state. The generated mapping tables, dispatch tables, and case-folding arrays are `static const` and persist for the lifetime of the module image. They are read-only after load and safe for concurrent callers without locks.

The only global mutable effect is NLS registry membership. `init_nls_cp932()` registers `table` under the `"cp932"` charset name and `"sjis"` alias; `exit_nls_cp932()` unregisters the same table. Consumers that obtain the table through the NLS core use these callbacks without per-conversion allocation.

Output state is caller-provided. `uni2char()` writes one or two bytes into `out` only after sufficient capacity checks for the path being used. `char2uni()` writes one `wchar_t` result through `uni` only after a mapping candidate is found or for direct ASCII/half-width paths. Both callbacks signal problems through negative errno values instead of storing persistent error state.

## Dependencies and Integration Points

The module depends on kernel headers for module metadata, errno constants, and the NLS core: `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`.

The key external integration point is the Linux NLS subsystem. `struct nls_table` defines the ABI expected by filesystem and VFS charset conversion code: `uni2char`, `char2uni`, `charset2lower`, and `charset2upper`. Filesystems that mount with CP932/SJIS conversion can request this table and use it when translating filenames between Unicode-facing kernel paths and CP932-compatible on-disk encodings.

The conversion functions also depend on data defined outside this chunk:

- `page_charset2uni` and the `c2u_*` tables are used by `char2uni()`.
- `u2c_00hi` and `u2c_03` through `u2c_6B` are referenced by `uni2char()` through direct code or `page_uni2charset`.

Because `MODULE_ALIAS_NLS(sjis)` advertises the SJIS alias, module autoloading can satisfy users that request `"sjis"` even though the registered charset string is `"cp932"`.

## Risks

- Table integrity is the highest risk. A single generated byte pair in `u2c_*` or Unicode scalar in `c2u_*` can silently corrupt filename round trips or make valid names unmappable.
- The chunk starts inside `u2c_6B`, so any manual review or regeneration must preserve continuity with the earlier chunk. Dropping or duplicating entries around the line boundary would shift low-byte indexes and break every later entry in that page.
- `uni2char()` always requires a two-byte output buffer before checking whether a generated page entry is valid. That is correct for the table format but means callers must retry with enough capacity even when the ultimate result would be `-EINVAL`.
- `char2uni()` rejects two-byte sequences with a zero trail byte before lookup. That matches the CP932 table model here, but any attempted extension for unusual vendor bytes must preserve this validation intentionally.
- The case-folding tables fold only ASCII. That is expected for a byte-oriented filesystem NLS table, but callers must not assume full Unicode or Japanese-width case normalization.
- `wchar_t` values above `0xFFFF` are effectively truncated to low 16 bits by the `ch`/`cl` extraction. In Linux NLS tables this is conventional for legacy encodings, but it is a risk if callers expect supplementary-plane awareness.
- The data encodes many sparse extension mappings under high Unicode pages and CP932 vendor rows such as `ED`/`EE` byte ranges. Compatibility with Microsoft CP932 depends on preserving those extension values exactly.

## Test and Validation Signals

Useful validation should focus on table consistency, errno behavior, and NLS registration:

- Build the module or kernel configuration that includes `nls_cp932.c`; table-size or initializer mistakes should fail compilation.
- Load and unload the NLS module and confirm `register_nls()`/`unregister_nls()` succeed, including alias lookup through `"sjis"` where the test environment exposes NLS modules.
- Round-trip representative mappings: ASCII, half-width Katakana `U+FF61..U+FF9F`, full-width ASCII and punctuation from `u2c_FF`, common kanji in pages `u2c_6C` through `u2c_9F`, and vendor/private extension values in the `ED`/`EE` byte ranges.
- Exercise negative paths: zero output/input lengths should return `-ENAMETOOLONG`; one-byte output buffers for two-byte Unicode mappings should return `-ENAMETOOLONG`; unmapped Unicode entries that resolve to `0x00,0x00` should return `-EINVAL`; unknown two-byte lead/trail combinations should return `-EINVAL`.
- Compare generated mappings against a known CP932 reference table, especially around sparse pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`.
- Filesystem-level tests should create, lookup, rename, and remove filenames containing ASCII, half-width Katakana, full-width Roman characters, common Japanese characters, and CP932 extension characters on a mount configured to use CP932/SJIS conversion.
