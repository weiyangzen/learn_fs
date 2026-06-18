# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp936.c lines 3985-8212

## Scope

This chunk is static lookup data for the Linux NLS CP936/GB2312 charset module. It contains no executable functions or exported symbols. The visible content is split between:

- The tail of charset-to-Unicode `c2u_*` tables, including the end of `c2u_F1` and full/partial pages `c2u_F2` through `c2u_FE`.
- The dispatch table `page_charset2uni[256]`.
- The beginning and large middle of Unicode-to-charset `u2c_*` tables, from `u2c_00` through a partial `u2c_7A`.

## APIs And Data Structures

The chunk defines internal `static const` data only:

- `static const wchar_t c2u_F2[256]` through `c2u_FE[256]`, plus the tail of `c2u_F1`, map CP936 lead-byte pages to Unicode code points. Each table is indexed by the second byte of a two-byte CP936 sequence.
- `static const wchar_t *page_charset2uni[256]` maps a CP936 first byte to the corresponding `c2u_*` table. Entries for unmapped lead bytes are `NULL`; entries `0x81` through `0xFE` point to the corresponding page tables.
- `static const unsigned char u2c_00[512]` through `u2c_7A[512]` begin the reverse mapping. Each Unicode high-byte page table stores 256 pairs of bytes, so index `low_byte * 2` gives the first CP936 byte and `low_byte * 2 + 1` gives the second. `0x00, 0x00` means no reverse mapping for that Unicode scalar in that page.

Adjacent code outside this chunk shows how these data structures are consumed:

- `char2uni()` uses `page_charset2uni[ch]` and then indexes `[cl]`.
- `uni2char()` uses `u2c_00` specially for Unicode page `0x00`, otherwise uses the later `page_uni2charset[ch]` dispatcher.
- The Euro sign is a special case outside this chunk: CP936 byte `0x80` maps to Unicode `0x20ac`.

## Control Flow

There is no runtime control flow in this chunk. The only control relationship is table-driven:

- For CP936-to-Unicode conversion, the first input byte selects a `c2u_*` page through `page_charset2uni`; the second input byte indexes the selected page.
- For Unicode-to-CP936 conversion, later code selects a `u2c_*` page by the high byte of the Unicode value and indexes a two-byte pair by the low byte.
- `NULL` dispatch entries and `0x0000`/`0x00,0x00` cells are sentinel states interpreted by later conversion routines as unmappable or invalid.

## State And Dependencies

All state here is immutable module-local lookup state:

- The `c2u_*` tables depend on definitions from earlier chunks: `page_charset2uni` references `c2u_81` through `c2u_F0` that are defined before this line range.
- This chunk also begins the `u2c_*` table family but does not complete it. Later chunks define `u2c_7B` and beyond, the `page_uni2charset[256]` dispatcher, case-fold tables, NLS callbacks, and module registration.
- The file depends on Linux kernel NLS infrastructure outside this chunk through later `struct nls_table` registration, but this chunk itself has no direct include or function dependency.

## Notable Table Coverage

Visible `c2u_*` coverage:

- `c2u_F1` tail at the beginning of the chunk.
- Full `c2u_F2` to `c2u_F7`.
- Shorter terminal pages `c2u_F8` to `c2u_FE`, where many high second-byte positions are `0x0000`.

Visible `u2c_*` coverage:

- Low Unicode pages: `u2c_00`, `u2c_01`, `u2c_02`, `u2c_03`, `u2c_04`.
- Symbol/punctuation pages: `u2c_20` through `u2c_26`.
- CJK compatibility and kana-like ranges: `u2c_30` through `u2c_33`.
- Main CJK Unified Ideographs pages: `u2c_4E` through the partial `u2c_7A`.

## Risks And Edge Cases

- Table integrity is the primary risk. A single misplaced byte pair or `wchar_t` value silently changes filename transcoding behavior.
- Sentinel ambiguity is intentional but fragile: `0x0000` and `0x00,0x00` mean unmapped in table cells, while adjacent code treats Unicode `U+0000` specially through `u2c_00`.
- The chunk boundary splits both logical table families: it starts mid-`c2u_F1` and ends mid-`u2c_7A`. Review or regeneration must include adjacent chunks to validate initializer completeness.
- Reverse mappings are not guaranteed to be visually obvious inverses of the forward mappings; correctness depends on generated table consistency across the whole file.
- `page_charset2uni` depends on all `c2u_*` page symbols being present and ordered correctly. A wrong pointer affects an entire lead-byte page.

## Cross-Chunk References

- Previous chunk: defines earlier `c2u_81` through `c2u_F1` content used by `page_charset2uni`.
- Next chunk: continues `u2c_7A`, defines later `u2c_*` pages, then defines `page_uni2charset`, `charset2lower`, `charset2upper`, `uni2char()`, `char2uni()`, and module registration.
- Final merge should describe this file as a generated/static NLS mapping module whose behavior is almost entirely determined by these table families plus the small conversion callbacks later in the file.