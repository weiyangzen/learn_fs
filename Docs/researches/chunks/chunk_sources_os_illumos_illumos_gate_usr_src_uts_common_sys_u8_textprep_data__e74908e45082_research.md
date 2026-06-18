# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/u8_textprep_data.h lines 31357-35374

## Scope

This chunk is the final ordered slice of `u8_textprep_data.h`, a generated Unicode text-preparation data header in the illumos kernel tree. It is in subset A because `sources/os/illumos/illumos-gate` is included by `Docs/research_subset_a.md`.

The chunk contains no executable functions. It closes the `u8_tolower_final_tbl` data started before this range, then defines the complete uppercase conversion lookup tables and closes the header guard.

## APIs And Exports

- Completes the tail of `static const uchar_t u8_tolower_final_tbl[2][2299]` at lines 31357-31374. The visible tail maps lower-case outputs for fullwidth Latin lower-case letters and Deseret lower-case code points.
- Defines `static const u8_displacement_t u8_toupper_b3_tbl[2][5][256]` at lines 31376-32041. This is the third-byte dispatch table for uppercase conversion for two Unicode data versions: index `0` is Unicode 3.2.0 and index `1` is Unicode 5.0.0, as described in the file header.
- Defines `static const uchar_t u8_toupper_b4_tbl[2][39][257]` at lines 32043-34778. Each fourth-byte table has 257 entries so consumers can read adjacent start/end offsets for a fourth-byte value and the next value.
- Defines `static const uchar_t u8_toupper_final_tbl[2][2318]` at lines 34780-35365. This byte pool stores the UTF-8 uppercase replacement sequences addressed by the `b4` offset tables.
- Undefines the local shorthand macros `N_` and `FIL_`, closes the optional C++ linkage block, and closes `_SYS_U8_TEXTPREP_DATA_H` at lines 35367-35374.

All data symbols are `static const`, so this header provides compile-unit-local data to files that include it rather than exporting linker-visible symbols.

## Data Layout

The lookup structure follows the multi-level scheme documented near the top of the file:

- The shared `u8_common_b1_tbl` and `u8_case_common_b2_tbl`, defined in earlier chunks, select a case-conversion third-byte table.
- `u8_toupper_b3_tbl` stores `u8_displacement_t` entries with a `tbl_id` and `base`. `N_` (`0xff`) marks undefined/non-mapping entries.
- `u8_toupper_b4_tbl` stores offsets relative to the selected `base`. Consumers use the current and next fourth-byte entries as `[start, end)` bounds into the final byte table.
- `u8_toupper_final_tbl` stores packed UTF-8 output bytes. Entries can be one or more UTF-8 characters depending on the Unicode uppercase mapping.

The uppercase final table includes mappings across Latin, Greek, Cyrillic, Armenian, Latin Extended Additional, Greek Extended, Roman numerals, circled letters, Glagolitic, Coptic, Georgian, fullwidth Latin, and Deseret ranges. The two outer version slots differ: Unicode 5.0.0 includes mappings not present in the Unicode 3.2.0 slot, for example later-script additions visible in the second final-table block.

## Control Flow

There is no direct control flow in this chunk. Runtime control flow is table-driven:

1. A caller requests uppercase preparation or comparison through public APIs such as `u8_textprep_str()` or `u8_strcmp()` with `U8_TEXTPREP_TOUPPER` / `U8_STRCMP_CI_UPPER`.
2. The implementation validates and parses a UTF-8 character as a four-byte lookup key.
3. Earlier `b1`/`b2` tables select the `u8_toupper_b3_tbl` row for the first and second UTF-8 bytes.
4. The third byte selects a `u8_displacement_t` entry. If it is not `N_`, its `tbl_id` selects a `u8_toupper_b4_tbl` row and its `base` contributes to the final-table offset calculation.
5. The fourth byte selects adjacent offset entries in the `b4` row; the byte span in `u8_toupper_final_tbl` is emitted as the uppercase mapping.

The 257-entry `b4` rows are important to this control flow because they allow `end_index = row[fourth_byte + 1]` without a special case for most values.

## State And Dependencies

All state in the chunk is immutable static storage. There is no allocation, locking, mutation, I/O, or error handling in the chunk itself.

Dependencies visible in this slice and adjacent header context:

- `uchar_t`, `uint16_t`, and related base types come from `<sys/types.h>`.
- `u8_displacement_t` is defined earlier in this header as `{ uint16_t tbl_id; uint16_t base; }`.
- `N_` is the local alias for `U8_TBL_ELEMENT_NOT_DEF` (`0xff`), defined earlier and undefined at the end of this chunk.
- `FIL_` is the local alias for `U8_TBL_ELEMENT_FILLER` (`0xf7`), although this final uppercase slice mainly uses raw UTF-8 bytes and zero padding.
- Public flags and entry points are declared in `u8_textprep.h`: `U8_TEXTPREP_TOUPPER`, `U8_TEXTPREP_TOLOWER`, `U8_UNICODE_320`, `U8_UNICODE_500`, `U8_UNICODE_LATEST`, `u8_validate()`, `u8_strcmp()`, and `u8_textprep_str()`.

Visible kernel consumers include ZFS name normalization, pcfs long filename case folding, and SMB client string comparisons. For example, ZFS documents `U8_TEXTPREP_TOUPPER` as a valid normalization flag for normalized ZAP names, while pcfs uses `u8_textprep_str(..., U8_TEXTPREP_TOLOWER, U8_UNICODE_LATEST, ...)` for foldcase paths.

## Risks

- The data is generated and offset-coupled. Manual edits to any `b3`, `b4`, or final-table byte can silently corrupt case-insensitive filesystem lookup semantics.
- `u8_toupper_b3_tbl` references `u8_toupper_b4_tbl` rows by small integer IDs and final-table bases. A mismatched table ID or base can redirect a code point to unrelated UTF-8 bytes.
- `u8_toupper_b4_tbl` uses adjacent offsets, so every row must preserve exactly 257 entries. Missing or extra values shift later offsets and can cause wrong spans or out-of-bounds reads in consumers.
- Unicode version indexing must stay aligned across all tables. Callers using `U8_UNICODE_LATEST` rely on slot `1` consistently meaning Unicode 5.0.0 across the common, lower, upper, decomposition, and composition tables.
- Filesystem name normalization depends on stable mappings. Regenerating these tables with a different Unicode version or changed case mapping rules can alter on-disk name hashes or case-insensitive comparison behavior.

## Cross-Chunk References

- Earlier chunks define the common first-byte table, case common second-byte table, and the full `u8_tolower_b3_tbl`, `u8_tolower_b4_tbl`, and most of `u8_tolower_final_tbl`.
- This chunk starts in the middle of `u8_tolower_final_tbl`; the declaration and most lower-case mapping payload are in the previous chunk.
- This chunk completes the file, so there is no later chunk for `u8_textprep_data.h`. The final per-file report should merge this chunk with prior chunks rather than being created here.