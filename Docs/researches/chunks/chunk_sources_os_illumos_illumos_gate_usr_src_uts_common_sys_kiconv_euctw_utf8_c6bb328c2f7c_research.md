# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h lines 8429-16875

## Scope

This report covers only lines 8429-16875 of `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_euctw_utf8.h` for `learn_fs` subset A. The file is a kernel iconv data header for EUC-TW/CNS 11643 to UTF-8 conversion, not filesystem or block-storage executable logic. This chunk starts mid-initializer inside the CNS 11643 plane #2 table, closes that table, opens the CNS 11643 plane #3 table, and ends mid-initializer at plane #3 key `0xC3DB`.

The whole file has 55,578 lines and declares eight CNS-to-UTF-8 tables. This chunk does not include the file license, include guard, `_KERNEL` guard, maximum-count macro definitions, later plane #3 rows, later plane #4/#5/#6/#7/#15 tables, or final preprocessor closure.

## Public Surface And APIs

No callable API is defined in this line range. The chunk contributes static kernel data to two file-scope symbols declared elsewhere in the same header:

- `kiconv_cns2_utf8[]`: this chunk contains the tail of this `static kiconv_table_array_t` table and its closing brace.
- `kiconv_cns3_utf8[]`: this chunk contains the table comment, declaration, sentinel row, and first 3,255 real mappings.

The table element type is defined in `uts/common/sys/kiconv_cck_common.h` as `uint32_t key` plus `uchar_t u8[4]`, large enough for three-byte BMP mappings and four-byte supplementary-plane mappings.

## Data Layout Visible In This Chunk

This line range contains 8,443 initializer rows total:

- Plane #2 tail: 5,187 rows, from `0xBBB4` at line 8429 through `0xF2C4` at line 13615.
- Plane #3 start: 3,256 rows, from the sentinel `0x0000 -> EF BF BD` at line 13620 through `0xC3DB` at line 16875.

The plane #2 rows in this chunk are all three-byte UTF-8 mappings. The visible plane #3 rows include 3,206 three-byte mappings and 50 four-byte mappings, beginning at `0xA1C4` and last seen at `0xC3B3`.

A numeric scan over the chunk found no duplicate keys and no nonascending keys within the visible plane #2 tail or visible plane #3 segment.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is table-driven by conversion code outside this header:

1. EUC-TW byte validation is described in `kiconv_tc.h`.
2. The converter identifies the CNS plane and forms a two-byte CNS key.
3. The selected `kiconv_cnsN_utf8[]` array is searched as sorted `kiconv_table_array_t` data.
4. The matched `u8[]` byte sequence is copied to the UTF-8 output buffer.
5. Generic kiconv code handles buffer accounting, invalid-sequence policy, replacement behavior, and errno values.

The conversion-name registry in `uts/common/os/kiconv.c` maps `"euctw"` to internal code id `16`.

## State And Dependencies

All state visible in this chunk is immutable static initializer data compiled into kernel code that includes this header under `_KERNEL`. There are no locks, allocations, I/O operations, mutable globals, reference counts, or filesystem state transitions.

Direct dependencies include `kiconv_table_array_t` from `kiconv_cck_common.h`, EUC-TW validation macros from `kiconv_tc.h`, and the companion reverse-direction table `kiconv_utf8_euctw.h`.

## Risks And Invariants

Important invariants:

- Full-table row counts must match `KICONV_CNS2_UTF8_MAX` and `KICONV_CNS3_UTF8_MAX` across all chunks.
- Keys must remain sorted within each plane table for binary search.
- CNS plane selection must match the table selected here.
- UTF-8 byte sequences must be copied using their actual encoded length, not by blindly emitting all four storage bytes.

Risks visible in this chunk:

- Generated-data drift can silently corrupt EUC-TW conversion for affected characters.
- This report starts mid-plane #2 and ends mid-plane #3, so whole-array count validation requires adjacent chunks.
- Four-byte UTF-8 handling is required for visible plane #3 rows.
- Plane #3 includes the `0x0000` replacement row in this chunk; plane #2's sentinel is in an earlier chunk.

## Cross-Chunk References

Prior chunk(s) must supply the header guard, `_KERNEL` guard, max-count macros, all of `kiconv_cns1_utf8[]`, and the start of `kiconv_cns2_utf8[]` through `0xBBB3`.

Later chunk(s) must continue `kiconv_cns3_utf8[]` from `0xC3DC` at line 16876 through its close, then cover CNS planes #4, #5, #6, #7, and #15 plus final preprocessor closure.