# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 19891-25440

## Scope

This chunk is part of the generated Unicode text-preparation data used by illumos kernel UTF-8 normalization and case handling. It is in subset A because `sources/os/illumos/illumos-gate` is included by `Docs/research_subset_a.md`.

The chunk contains no executable functions. It spans the end of the 8-bit decomposition fourth-byte index table, the complete 16-bit decomposition fourth-byte index table, and the beginning of the large final decomposition byte table.

## APIs And Exports

- Continues `static const uchar_t u8_decomp_b4_tbl[2][118][257]`, which began before this chunk at line 12228. Lines 19891-20493 cover the tail of the first Unicode-version half: the end of fourth-byte table 100 and full fourth-byte tables 101-117.
- Defines `static const uint16_t u8_decomp_b4_16bit_tbl[2][30][257]` at lines 20495-22600. This table is fully contained in the chunk.
- Defines the start of `static const uchar_t u8_decomp_final_tbl[2][19370]` at line 22602. The first 19,370-byte subarray closes at line 25026; the second subarray starts at line 25027 and continues past line 25440.
- Does not define or export public C functions. Public consumers see this data indirectly through the `u8_textprep.h` APIs, especially `u8_textprep_str()`, `u8_strcmp()`, and normalization/case flags such as `U8_TEXTPREP_NFD`, `U8_TEXTPREP_NFC`, `U8_TEXTPREP_NFKD`, `U8_TEXTPREP_NFKC`, `U8_TEXTPREP_TOUPPER`, and `U8_TEXTPREP_TOLOWER`.

## Data Layout

The file-level comment describes UTF-8 code points as four-byte lookup keys. Earlier b1, b2, and b3 tables select a fourth-byte table, and the fourth-byte value indexes adjacent slots in that selected b4 table. The value at slot `b4` is the start index into `u8_decomp_final_tbl`; the value at slot `b4 + 1` is the end index.

The table choice is split by index width:

- `u8_decomp_b4_tbl` stores byte-sized final-table offsets for ranges whose decomposition payload offsets fit in `uchar_t`.
- `u8_decomp_b4_16bit_tbl` stores 16-bit final-table offsets when the b3 table marks the selected b4 table id with `0x8000`.
- Both b4 table families have `257` entries per fourth-byte table so every possible fourth-byte index can read a `[start, end)` pair without a special last-byte case.

The final table stores raw UTF-8 decomposition bytes. In the visible payload, `0xF6` appears frequently as a generated separator/end marker between decomposition sequences, while `0xF5` appears much less often in multi-result/control encodings. The public filler macro near the top of the file is `0xF7`, but this chunk's visible final-table bytes do not contain `0xF7`.

## Control Flow

There is no local runtime control flow. Runtime lookup follows the data contract documented in the header:

1. Select Unicode data version `[0]` for Unicode 3.2.0 or `[1]` for Unicode 5.0.0.
2. Use prior chunks' `u8_common_b1_tbl`, `u8_decomp_b2_tbl`, and `u8_decomp_b3_tbl` to find a fourth-byte table id and optional displacement/base metadata.
3. If the b4 table id has the high `0x8000` bit set, clear that bit and index `u8_decomp_b4_16bit_tbl`; otherwise index `u8_decomp_b4_tbl`.
4. Use the returned `[start_index, end_index)` range to copy or interpret bytes from `u8_decomp_final_tbl[version]`.

The first version's final decomposition payload is complete in this chunk, while the second version's payload is only partially present here.

## State And Dependencies

All data is immutable `static const` storage in a guarded kernel header. There is no allocation, locking, mutation, or per-call state in this chunk.

Dependencies visible from the surrounding file and public header:

- `<sys/types.h>` supplies `uchar_t` and fixed-width integer types used by the tables.
- `u8_displacement_t`, defined near the top of this file, is used by earlier b3 decomposition tables to decide whether the lookup should use 8-bit or 16-bit b4 offset tables.
- `sys/u8_textprep.h` declares the public Unicode conversion and text-preparation APIs and the version constants `U8_UNICODE_320`, `U8_UNICODE_500`, and `U8_UNICODE_LATEST`.
- Kernel files in ZFS, pcfs, and SMB paths call `u8_textprep_str()` or use the text-prep flags for normalized/case-insensitive name handling; those consumers depend on this generated table data even though the table symbols are header-local.

## Risks

- Manual edits are high risk: adjacent b4 slots form `[start, end)` ranges into the final table, so changing one value can corrupt one or more decompositions.
- The 8-bit and 16-bit b4 tables are selected by high-bit metadata in earlier `u8_decomp_b3_tbl` entries. If those earlier ids and these table dimensions diverge, lookups can read the wrong offset family.
- `u8_decomp_final_tbl[2][19370]` has exact per-version lengths. Inserting or deleting bytes in the first final-table subarray would shift every later offset and can also break the fixed initializer length.
- The chunk boundary is in the middle of the second version's final-table payload at line 25440, so this chunk alone cannot validate closure, final byte count, or trailing table declarations.
- Because ZFS and pcfs use text preparation for filesystem name normalization/case behavior, corrupted decomposition data can surface as lookup mismatches, normalization instability, or incompatible on-disk name comparison semantics.

## Cross-Chunk References

- Earlier chunks define the header guard, constants, `u8_displacement_t`, common b1 tables, decomposition b2/b3 tables, and the start of `u8_decomp_b4_tbl`. This chunk starts inside fourth-byte table 100 and relies on those prior declarations.
- This chunk closes `u8_decomp_b4_tbl` at line 20493 and fully covers `u8_decomp_b4_16bit_tbl`, making it the bridge between earlier decomposition trie selection and the final byte payload.
- Later chunks continue `u8_decomp_final_tbl[1]` after line 25440 and must close the full final table and the header. They are needed for complete Unicode 5.0.0 decomposition coverage and whole-file validation.