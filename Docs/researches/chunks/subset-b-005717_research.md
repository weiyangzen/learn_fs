# sources/distributed-fs/ceph-client/fs/nls/nls_cp949.c lines 8201-12440

## Scope

This chunk covers the middle of the generated CP949 Unicode-to-charset mapping tables in `nls_cp949.c`. It starts inside the tail of `u2c_7A`, then defines complete `static const unsigned char u2c_*[512]` pages for Unicode high bytes `0x7B` through `0xC5`, and ends partway through `u2c_C6`.

There is no executable function body in this range. The important behavior is data-driven: later code indexes these arrays through `page_uni2charset[]` and `uni2char()` to encode Unicode code points as one- or two-byte CP949/EUC-KR sequences.

## Purpose

The arrays in this range provide reverse conversion from Unicode to CP949. Each `u2c_XX` table corresponds to a Unicode page where `XX` is the high byte of a `wchar_t` value. The low byte of the Unicode code point selects a two-byte output pair inside the 512-byte table.

The chunk includes two major kinds of mapping data:

- Sparse mappings for Unicode pages such as `0x7A` through `0x9F`, where many entries are `0x00, 0x00` and only selected characters have CP949 encodings.
- Dense Hangul syllable mappings for pages `0xAC` through the visible part of `0xC6`, where most entries map to CP949 lead/trail byte pairs. These pages cover a large part of the modern Hangul syllable block beginning at Unicode `U+AC00`.

Together with earlier and later `u2c_*` pages, this data lets the Linux NLS layer encode Korean filenames and other filesystem-facing strings into the CP949 charset.

## Important APIs, Types, and Data

`static const unsigned char u2c_7A[512]` is already open before this chunk begins. Lines in this chunk finish the latter part of that Unicode page, then close it. Because the chunk starts mid-table, the complete table ownership is cross-chunk.

`u2c_7B` through `u2c_9F` are sparse reverse lookup pages. They contain explicit two-byte CP949 pairs for Unicode values in those high-byte pages and `0x00, 0x00` sentinels for unmappable characters.

`u2c_AC` through `u2c_C5` are dense Hangul reverse lookup pages. The visible data mostly maps Unicode Hangul syllables to CP949 byte pairs in the `0xB0` through `0xBF` range and CP949 extension byte ranges such as `0x99`, `0x9A`, `0x9B`, `0x9C`, and `0x9D`.

`u2c_C6` begins at line 12405 and continues beyond this chunk. Lines through 12440 include mappings for low-byte offsets `0x00` through roughly `0x9B`; the rest of this page belongs to the following chunk.

The relevant consumer, outside this line range, is `uni2char(const wchar_t uni, unsigned char *out, int boundlen)`. It computes `ch = (uni >> 8) & 0xFF` and `cl = uni & 0xFF`, selects `page_uni2charset[ch]`, reads `uni2charset[cl * 2]` and `uni2charset[cl * 2 + 1]`, and returns two output bytes unless the pair is `0x00, 0x00`.

`page_uni2charset[256]`, also outside this chunk, is the dispatch table that makes these arrays reachable. It assigns entries such as `page_uni2charset[0x7B] = u2c_7B`, `page_uni2charset[0xAC] = u2c_AC`, and so on.

## Control Flow

This range contributes no direct branches, loops, callbacks, allocation, or registration logic. Runtime control flow reaches it indirectly:

1. A caller in the VFS/NLS path asks the registered CP949 NLS table to convert one Unicode code point to charset bytes.
2. `uni2char()` validates `boundlen`. It needs at least one byte for ASCII fallback and at least two bytes when a Unicode page table exists.
3. `uni2char()` indexes `page_uni2charset` by the Unicode high byte.
4. For high-byte pages covered here, `page_uni2charset[ch]` points at one of these `u2c_*` arrays.
5. The Unicode low byte is multiplied by two to fetch the CP949 byte pair.
6. A nonzero pair is written to `out[0]` and `out[1]`, returning `2`; `0x00, 0x00` returns `-EINVAL`.
7. If there is no page table and the Unicode value is nonzero ASCII, `uni2char()` emits one byte instead. That fallback is outside this chunk and does not apply to the high-byte pages represented here.

The comments at the end of each table row, such as `/* 0x40-0x43 */`, document the low-byte offset range for that row. They are important for maintaining the generated layout because the index math assumes every page has exactly 256 two-byte entries.

## State and Persistence Behavior

All data in this chunk is `static const`, so it is immutable module text/rodata after compilation. The tables do not allocate memory, hold references, perform I/O, update counters, or persist state to disk.

Persistence is behavioral rather than mutable: the compiled module permanently fixes the CP949 encoding results for the represented Unicode pages until the module is replaced. Any incorrect entry becomes a deterministic conversion bug for every filesystem and user path that relies on this NLS table.

The `0x00, 0x00` entries are meaningful state in the table. They encode "no mapping" and are interpreted by `uni2char()` as `-EINVAL`, not as a NUL character output.

## Dependencies and Integration Points

The file depends on Linux kernel NLS interfaces from `<linux/nls.h>`, module registration from `<linux/module.h>`, and error codes from `<linux/errno.h>`. This chunk itself only supplies lookup data consumed by those interfaces.

The direct integration point is the later `page_uni2charset[]` array. If a `u2c_*` table is present but omitted from `page_uni2charset[]`, it is dead data. If a `page_uni2charset[]` entry points to the wrong table, Unicode high-byte pages encode as the wrong CP949 byte ranges.

The external API exposed by the full file is `struct nls_table table` with `.charset = "cp949"`, `.alias = "euc-kr"`, `.uni2char = uni2char`, and `.char2uni = char2uni`. The module registers this table with `register_nls()` during init and unregisters it on exit.

The data is paired with earlier `c2u_*` tables and `page_charset2uni[]`, which implement the opposite CP949-to-Unicode direction. Correct round-trip behavior depends on these reverse `u2c_*` tables agreeing with the forward `c2u_*` tables for all intended mappings.

## Risks

- Table shape is fragile. Every `u2c_*` page must contain exactly 512 bytes representing 256 two-byte mappings. Missing, extra, or shifted bytes would corrupt all later entries in that page.
- The chunk begins and ends inside table definitions. Merge/reconciliation must preserve continuity with adjacent chunks for `u2c_7A` and `u2c_C6`; reviewing this chunk alone cannot prove those two arrays are complete.
- `0x00, 0x00` is a sentinel for unmappable Unicode. Accidentally replacing a real mapping with zero causes `uni2char()` to return `-EINVAL`; accidentally replacing a zero pair with nonzero bytes allows an invalid or unsupported Unicode code point to encode.
- Dense Hangul pages include long monotonic-looking byte sequences. They are easy to damage with mechanical edits because many entries differ only by one byte.
- CP949 includes Microsoft extensions beyond strict EUC-KR. Mistaking alias behavior for strict EUC-KR behavior can lead to compatibility regressions when filenames use extension characters.
- The tables are generated data without local validation logic. Compile success only proves the C syntax and array sizes, not semantic correctness against the authoritative CP949 mapping.
- `uni2char()` trusts `page_uni2charset[]` and table dimensions. A wrong dispatch pointer can produce valid-looking two-byte output for the wrong Unicode page, making failures subtle.

## Test and Validation Signals

Good validation for this chunk is table-driven rather than branch-driven:

- Compile the module or full kernel tree with warnings enabled to catch malformed array syntax or size drift.
- Run NLS conversion tests for representative Unicode points in every page covered here: sparse pages `U+7Axx` through `U+9Fxx`, dense Hangul pages `U+ACxx` through `U+C5xx`, and the visible prefix of `U+C6xx`.
- Include negative tests for known `0x00, 0x00` entries and verify `uni2char()` returns `-EINVAL`.
- Validate round trips through `uni2char()` and `char2uni()` for sampled mappings from this range, especially Hangul syllables whose CP949 byte pairs use extension lead bytes such as `0x99` through `0x9E`.
- Compare generated table entries against an authoritative CP949 mapping source or an independent converter for the exact same Unicode points.
- Exercise filesystem filename conversion with Korean names containing Hangul syllables from `U+AC00` through `U+C6xx`, plus unmappable characters adjacent to valid ones, to verify caller-visible errors and successful encodings.
- Boundary tests should cover first and last low-byte entries of complete tables in this chunk, and cross-chunk boundaries around `u2c_7A` and `u2c_C6`.

## Cross-Chunk Notes

The preceding chunk owns the start of `u2c_7A`; this chunk only sees its tail and close brace. The following chunk owns the remainder of `u2c_C6`, the later `u2c_C7` and subsequent pages, `page_uni2charset[]`, case tables, conversion functions, and module registration.

The final per-file research document should synthesize this chunk as part of the Unicode-to-CP949 reverse mapping section, not as an independent feature. The executable semantics for this data come from `uni2char()` and `page_uni2charset[]` later in the file.
