# sources/distributed-fs/ceph-client/fs/nls/nls_cp936.c lines 3985-8212

## Scope

This chunk covers the middle of the generated CP936/GB2312 NLS translation table source. It starts inside the tail of `c2u_F1`, includes the remaining high-byte character-to-Unicode pages `c2u_F2` through `c2u_FE`, defines the `page_charset2uni` dispatch table, and then defines Unicode-to-CP936 pages from `u2c_00` through the first part of `u2c_7A`. The chunk ends mid-`u2c_7A` at Unicode page offset `0xE7`; `u2c_7A` continues in the next chunk.

## Purpose

The file is the Linux NLS implementation for CP936, also aliased as GB2312. This chunk supplies the static lookup data used by the module's two conversion callbacks:

- CP936 byte sequence to Unicode code point via `page_charset2uni`.
- Unicode code point to CP936 byte sequence via `u2c_*` page tables, later reached through `page_uni2charset`.

The data is generated from Microsoft's Unicode code page mapping source, so the important behavior is exact table fidelity rather than algorithmic logic.

## Important Data Structures

- `static const wchar_t c2u_F2[256]` through `c2u_FE[256]`: byte-second-indexed tables for CP936 lead bytes `0xF2` through `0xFE`. The chunk also contains the final entries of `c2u_F1`. Each entry maps the trailing byte value directly to a Unicode code point. `0x0000` marks invalid or unmapped byte positions.
- `static const wchar_t *page_charset2uni[256]`: dispatch array keyed by CP936 lead byte. Entries below `0x81` are `NULL`, entries `0x81` through `0xFE` point at the corresponding `c2u_*` tables, and the final `0xFF` entry is `NULL`. This chunk is the integration point that makes all earlier and current `c2u_*` tables reachable by `char2uni`.
- `static const unsigned char u2c_00[512]` through partial `u2c_7A[512]`: reverse lookup tables keyed by Unicode high byte. Each Unicode low byte index consumes two bytes, so offset `cl * 2` stores the CP936 first byte and `cl * 2 + 1` stores the second byte. A pair of `0x00, 0x00` marks no CP936 mapping, except `u2c_00` also relies on later fallback logic for ordinary ASCII.

## Covered Mapping Ranges

The `c2u_F*` tables cover the upper CP936 lead-byte range. They include many CJK Unified Ideographs, compatibility ideographs, and private/generated-looking sequential ranges in the `0x99AA` through `0x9DFF` area, mixed with explicit mappings such as `0xFA0C` through `0xFA29` near `c2u_FE`.

The reverse tables in this chunk cover these Unicode high-byte pages:

- `u2c_00` through `u2c_04`: low Unicode planes, including ASCII/control-adjacent entries, Latin-derived symbols, and non-ASCII page-zero mappings.
- `u2c_20` through `u2c_26`: punctuation, currency/symbol, and miscellaneous symbol ranges.
- `u2c_30` through `u2c_33`: CJK punctuation and related compatibility ranges.
- `u2c_4E` through `u2c_7A` offset `0xE7`: the main CJK Unified Ideographs range used by Simplified Chinese filenames and text.

## Control Flow And Integration

There is no executable control flow inside this chunk; it is all static data. Runtime lookup is provided later in the file:

- `char2uni(rawstring, boundlen, uni)` reads `rawstring[0]` as the CP936 lead byte and `rawstring[1]` as the trail byte when at least two bytes are available. It then indexes `page_charset2uni[ch]` and returns `charset2uni[cl]` if present and nonzero. The `c2u_F1` tail and `c2u_F2`-`c2u_FE` arrays in this chunk are used through that path for high lead bytes.
- `uni2char(uni, out, boundlen)` splits a Unicode code point into high byte `ch` and low byte `cl`, later indexes `page_uni2charset[ch]`, then reads the two-byte CP936 result from `u2c_*[cl * 2]` and `u2c_*[cl * 2 + 1]`. The `u2c_00`-`u2c_7A` data in this chunk supplies many of those reverse mappings.
- The `page_charset2uni` table defined here links together character-to-Unicode arrays declared both before and within this chunk. The reverse dispatch table `page_uni2charset` is later in the file, so this chunk contains many reverse pages before the final reverse-page pointer table is assembled.

## State And Persistence Behavior

All tables in this chunk are `static const`, so they are read-only module data after load and have no runtime mutation, locking, allocation, or persistence side effects. The effective state is the byte-for-byte mapping embedded in the module image. Persistence is therefore build-time persistence: changing any literal table value changes filesystem charset conversion behavior for every caller that loads this NLS module.

## Dependencies

This chunk depends on kernel NLS conventions and types from the top of the file:

- `wchar_t` for Unicode code point storage in `c2u_*`.
- `unsigned char` for byte-oriented CP936 output in `u2c_*`.
- Sentinel convention: `0x0000` in `c2u_*` and `0x00, 0x00` in `u2c_*` mean unmapped unless later conversion code has a special-case fallback.

It has no direct dependency on Ceph-specific logic despite the repository path. Its integration surface is the generic Linux `struct nls_table` registered later by the module.

## Risks And Edge Cases

- Table corruption is the main behavioral risk. A single wrong literal creates a silent, deterministic filename/text conversion mismatch.
- The `0x0000` sentinel makes Unicode NUL special. The later code explicitly permits `U+0000` in CP936 for `uni2char`, so page-zero behavior must be checked against the conversion callback rather than inferred only from table zeros.
- `page_charset2uni` deliberately leaves lead bytes outside `0x81`-`0xFE` as `NULL`. If future generated tables add lead-byte ranges, this pointer table must be updated with the data arrays.
- This research chunk ends in the middle of `u2c_7A`. Any validation of the complete `u2c_7A` table must include the next chunk.
- Since the source is generated, manual edits are high risk. Regeneration from the authoritative mapping source is safer than hand-editing individual entries.

## Test Signals

Useful tests should exercise both table directions rather than only compile coverage:

- Build/module compile confirms table syntax and symbol references, especially that `page_charset2uni` points at declared `c2u_*` arrays.
- Round-trip tests for representative high lead bytes from `0xF1` through `0xFE` catch issues in the `c2u_F*` tables and reverse `u2c_*` coverage.
- Negative tests for unmapped `0x0000` entries should verify `char2uni` returns `-EINVAL` for invalid two-byte CP936 sequences.
- Boundary tests should cover ASCII/page-zero fallback, the Euro special case handled outside this chunk, and the chunk boundary around Unicode page `0x7A` offsets `0xE4` through `0xFF`.
