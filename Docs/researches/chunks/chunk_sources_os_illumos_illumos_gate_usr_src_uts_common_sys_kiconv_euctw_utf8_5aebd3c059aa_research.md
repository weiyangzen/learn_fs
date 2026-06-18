# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 39352-46468

## Scope

This report covers lines 39352-46468 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h` for `learn_fs` subset A. The file is generated-style kernel iconv data for EUC-TW/CNS 11643 to UTF-8 conversion. This chunk starts inside the CNS 11643 plane #6 table, closes that table, opens the CNS 11643 plane #7 table, and ends inside plane #7 at key `0xCDBC`.

The slice is table data only. It does not include the file header, include guard, `_KERNEL` guard start, the `KICONV_CNS*_UTF8_MAX` definitions, the start of `kiconv_cns6_utf8`, the end of `kiconv_cns7_utf8`, or the later `kiconv_cns15_utf8` table.

## Public Surface And APIs

The chunk contributes rows to two kernel-only static arrays declared elsewhere in the same header:

- `static kiconv_table_array_t kiconv_cns6_utf8[]` for CNS 11643 plane #6 to UTF-8.
- `static kiconv_table_array_t kiconv_cns7_utf8[]` for CNS 11643 plane #7 to UTF-8.

The relevant maximum constants are outside this chunk but visible in the same file:

- `KICONV_CNS6_UTF8_MAX (6386)`.
- `KICONV_CNS7_UTF8_MAX (6538)`.

The element type is defined in `uts/common/sys/kiconv_cck_common.h`:

- `uint32_t key`
- `uchar_t u8[4]`

Each row maps a CNS/EUC-TW two-byte code value to a UTF-8 byte sequence. Most visible rows use four explicit UTF-8 bytes for supplementary-plane Unicode code points; some use three explicit bytes and rely on zero-initialization for the remaining byte in `u8[4]`.

## Data Layout Visible In This Chunk

This line range contains 7,113 mapping rows total:

- 2,950 rows from the tail of `kiconv_cns6_utf8`, starting at line 39352 with key `0xC5D6` and ending at line 42301 with key `0xE4FA`.
- The closing `};` for `kiconv_cns6_utf8` at line 42302.
- The comment and declaration for `kiconv_cns7_utf8` at lines 42304-42305.
- 4,163 rows from the start of `kiconv_cns7_utf8`, starting at line 42306 with sentinel key `0x0000 -> EF BF BD` and ending at line 46468 with key `0xCDBC`.

Initializer widths in this chunk:

- 6,921 rows with four explicit UTF-8 bytes.
- 192 rows with three explicit UTF-8 bytes.

Within each visible table segment, keys are strictly ascending and no duplicate keys were found. `kiconv_cns6_utf8` as a whole contains 6,386 rows, matching `KICONV_CNS6_UTF8_MAX`; `kiconv_cns7_utf8` as a whole contains 6,538 rows, matching `KICONV_CNS7_UTF8_MAX`.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is supplied by the kernel iconv conversion code that consumes these static tables:

1. EUC-TW input validation is handled by macros in `kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE`, `KICONV_TC_EUCTW_PMASK`, and `KICONV_TC_IS_VALID_EUCTW_SEQ`.
2. The converter identifies the CNS plane and forms the two-byte table key.
3. Generic CCK conversion support can search sorted `kiconv_table_array_t` tables via `kiconv_binsearch()`.
4. On a match, the `u8[4]` bytes are copied to UTF-8 output according to the converter's output-length logic.
5. On invalid input or absent mapping, error/replacement policy is handled by the surrounding kiconv implementation, not by this data table.

The conversion name registry in `uts/common/os/kiconv.c` assigns `"euctw"` code id `16`, tying these CNS tables to the kernel EUC-TW conversion surface.

## State And Dependencies

All state in this chunk is immutable static initializer data compiled into translation units that include the header under `_KERNEL`.

Direct dependencies and adjacent contracts:

- `_KERNEL` gating around the complete table definitions.
- `kiconv_table_array_t` from `kiconv_cck_common.h`.
- `uchar_t` and `uint32_t` from illumos system type headers included before this generated data header.
- EUC-TW byte and plane validation macros in `kiconv_tc.h`.
- Reverse-direction companion data in `kiconv_utf8_euctw.h`.
- Header export listing in `uts/common/sys/Makefile`.

The file-level comment states that the mapping supports Unicode 3.2 and uses `Unihan-3.2.0.txt` as its mapping source. This chunk inherits that version/source constraint.

## Risks And Invariants

Key invariants:

- Table keys must remain sorted for binary-search consumers.
- Per-plane row counts must match `KICONV_CNS6_UTF8_MAX` and `KICONV_CNS7_UTF8_MAX`.
- UTF-8 byte sequences must remain valid and correctly zero-padded in `u8[4]`.
- The sentinel row `0x0000 -> U+FFFD` at the start of `kiconv_cns7_utf8` must remain first in that table.

Risks visible in this chunk:

- Generated-data drift: a single incorrect byte changes character conversion while preserving valid C syntax.
- Cross-chunk count drift: the chunk begins after the start of plane #6 and ends before the end of plane #7, so full-table validation requires adjacent chunks.
- Include-time footprint: arrays are `static` in a header, so each including translation unit gets private table storage.
- Zero-fill dependence: three-byte initializers depend on C zero-initialization for the unused fourth byte.
- Sparse key ranges are intentional; missing CNS code points are not represented by placeholder rows except for each table's `0x0000` replacement sentinel.
- Direct textual consumers of `kiconv_cns6_utf8` and `kiconv_cns7_utf8` were not found outside this header in `usr/src`, suggesting inclusion or generation patterns may be indirect.

## Cross-Chunk References

The preceding chunk must cover the start of `kiconv_cns6_utf8` from line 35915 through key `0xC5D5` at line 39351. Together with this chunk, plane #6 should total 6,386 rows and close at line 42302.

The following chunk must continue `kiconv_cns7_utf8` at line 46469 with key `0xCDBD`, run through the table close at line 48844, and then account for the `kiconv_cns15_utf8` declaration beginning at line 48847. Plane #7 should total 6,538 rows, leaving 2,375 plane #7 rows after this chunk.