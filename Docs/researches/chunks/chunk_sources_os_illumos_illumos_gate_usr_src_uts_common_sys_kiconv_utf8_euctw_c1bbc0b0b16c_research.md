# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 25997-37911

## Scope

This chunk is a contiguous middle slice of the illumos kernel UTF-8-to-EUC-TW mapping header. It sits entirely inside:

- `static kiconv_table_t kiconv_utf8_euctw[] = { ... }`

The range contains 11,915 initializer rows and no executable functions, macros, typedefs, conditionals, or closing braces. Runtime behavior is therefore fully data-driven by common kiconv conversion code that packs validated UTF-8 input into table keys, searches this sorted table, and emits the stored EUC-TW/CNS value.

## APIs And Data Structures

- This chunk contributes rows to `kiconv_utf8_euctw[]`, declared earlier in the file under `_KERNEL`.
- The file-level table count contract is `KICONV_UTF8_EUCTW_MAX (55442)`.
- Each row uses `kiconv_table_t` from `sys/kiconv_cck_common.h`:
  - `uint32_t key`: packed UTF-8 byte sequence.
  - `uint32_t value`: packed EUC-TW destination encoding.
- Visible key range in this chunk:
  - first row: `0xF0A09B8E -> 0x4A3C1`
  - last row: `0xF0A4AD90 -> 0x5BAB4`
- All keys in this range are 4-byte UTF-8 packed values with lead byte `0xF0`, covering supplementary-plane Unicode mappings.

## Control Flow

There is no direct control flow in the chunk. The relevant runtime flow is outside this header:

1. Common UTF-8-to-CCK conversion logic determines the UTF-8 sequence length with `u8_number_of_bytes[]`.
2. It validates continuation bytes and second-byte bounds with `u8_valid_min_2nd_byte[]` and `u8_valid_max_2nd_byte[]`.
3. It packs the UTF-8 bytes into a `uint32_t` key.
4. It binary-searches the selected sorted table.
5. On match, it writes the mapped target bytes; on miss or invalid input, surrounding conversion code handles replacement, `EILSEQ`, `EINVAL`, or `E2BIG`.

The chunk’s sort order is part of that binary-search contract. A read-only check over the line range found no descending keys and no duplicate keys inside the chunk.

## State

The chunk is immutable static initializer data. It does not allocate memory, mutate state, perform locking, or maintain per-conversion state. Conversion state such as BOM handling, buffer pointers, non-identical conversion counts, null handling, and replacement policy lives in the kiconv driver code rather than in this header.

## Data Shape

- Rows in this chunk: 11,915.
- Key ordering: ascending, unique within the chunk.
- Key gaps: expected; the table only includes mapped Unicode scalar values.
- Destination value range seen in this chunk: `0x3A3D9` through `0xFEDB4`.
- Destination value high-nibble/plane distribution visible in this chunk:
  - `0x3....`: 14 rows
  - `0x4....`: 1,216 rows
  - `0x5....`: 2,832 rows
  - `0x6....`: 3,031 rows
  - `0x7....`: 1,684 rows
  - `0xF....`: 3,138 rows
- The `0xF....` destination values correspond to EUC-TW/private-use/UDA-style encoded values, consistent with `kiconv_tc.h` documenting EUC-TW planes 12/13/14/16 in the Unicode private-use range.

## Dependencies

- `_KERNEL` guard and `_SYS_KICONV_UTF8_EUCTW_H` include guard declared outside this chunk.
- `kiconv_table_t` from `sys/kiconv_cck_common.h`.
- UTF-8 validation tables declared in `sys/kiconv_cck_common.h` and provided by common Unicode textprep code.
- Traditional Chinese/EUC-TW constants in `sys/kiconv_tc.h`, including `KICONV_TC_EUCTW_MBYTE`, `KICONV_TC_EUCTW_PMASK`, and UDA range constants.
- The reverse-direction mapping is in `sys/kiconv_euctw_utf8.h`.
- `usr/src/uts/common/sys/Makefile` exports `kiconv_utf8_euctw.h` as an illumos kernel/system header.

## Risks And Cross-Chunk References

- Count drift risk: changes to this data must keep the full-file `KICONV_UTF8_EUCTW_MAX` aligned with the complete initializer length.
- Sort-order risk: common conversion code relies on sorted keys for binary search. Insertions must preserve ascending key order across chunk boundaries.
- Boundary continuity:
  - The previous chunk ends before this range at `0xF0A09B8D -> 0x6A3E6`; this chunk continues at `0xF0A09B8E`.
  - The next chunk should continue after this range at `0xF0A4AD91 -> 0x5BAB3`.
- Generated-data risk: this file appears to be a generated Unicode/CNS mapping table. Manual edits can introduce asymmetric mappings with `kiconv_euctw_utf8.h`, wrong EUC-TW plane encodings, or missing supplementary-plane entries.
- Error-handling risk is external: this table has no invalid-entry sentinel in the chunk, so unmapped input depends on the caller’s search-miss and replacement policy.