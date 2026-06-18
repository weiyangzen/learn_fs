# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_uhc_utf8.h lines 8454-16909

## Scope

This chunk is part of subset A (`Docs/research_subset_a.md`) under `sources/os/illumos/illumos-gate`. I read the requested range completely: lines 8454-16909 of `usr/src/uts/common/sys/kiconv_uhc_utf8.h`. Adjacent context was used only to identify the surrounding declaration, the shared table type, the UHC byte validity macros, and the table closure.

The file is a generated/static Korean code-conversion table. This chunk contains only initializer rows inside `static kiconv_table_array_t kiconv_uhc_utf8[]`; it has no functions or local control-flow statements.

## APIs And Exported Data

The surrounding header defines, under `_KERNEL`, the UHC-to-UTF-8 table:

- `KICONV_UHC_UTF8_MAX` is defined earlier in the file as `17047`.
- `kiconv_uhc_utf8[]` is a `static kiconv_table_array_t` declared before this chunk. `kiconv_table_array_t` comes from `kiconv_cck_common.h` and has `uint32_t key` plus `uchar_t u8[4]`.
- Each visible row maps one two-byte UHC code, stored as a 16-bit-looking integer key such as `0xB297`, to a three-byte UTF-8 sequence stored as `{ 0x.., 0x.., 0x.. }`.

This chunk contributes 8456 initializer rows. The first visible row is `0xB297 -> { 0xEC, 0xBF, 0x81 }`; the last visible row is `0xFBE0 -> { 0xE9, 0x8E, 0xAC }`.

## Control Flow

There is no executable control flow in the chunk. Runtime behavior is data-driven: a caller validates UHC input bytes, combines two bytes into the table key, and looks up the key in `kiconv_uhc_utf8[]`. The sorted key order matters because common CCK code declares `kiconv_binsearch(uint32_t key, void *tbl, size_t nitems)`.

The chunk itself does not branch, allocate, lock, mutate state, or perform conversion.

## State And Invariants

All state here is immutable compile-time table data.

- 8456 rows matched the expected initializer shape.
- No malformed rows were visible.
- The key sequence is strictly increasing.
- Each row uses a UHC key and exactly three UTF-8 bytes.
- UHC trail-byte gaps such as `0x5B-0x60` and `0x7B-0x80` are structural, matching `kiconv_ko.h` validity rules.

Lead-byte coverage: partial `0xB2`, full `0xB3-0xC5`, partial `0xC6`, EUC-style `0xC7-0xC8` and `0xCA-0xFA`, and partial `0xFB`.

## Dependencies

Direct dependencies visible from context:

- `_KERNEL` guards the table definition.
- `kiconv_table_array_t` is defined in `sys/kiconv_cck_common.h`.
- UHC byte validity and Korean UDA constants are in `sys/kiconv_ko.h`.
- The reverse mapping table is `sys/kiconv_utf8_uhc.h`.
- `usr/src/uts/common/sys/Makefile` lists both UHC conversion headers.

## Risks

Manual row edits are high risk: one wrong key or UTF-8 byte silently corrupts Korean conversion. The table must remain sorted for binary-search users. `KICONV_UHC_UTF8_MAX` must match the complete table length, not this chunk length. Apparent numeric holes should not be filled automatically because they reflect invalid UHC byte ranges or separately handled ranges.

## Cross-Chunk References

Previous chunk contains the declaration and rows through `0xB296 -> { 0xEC, 0xBF, 0x80 }`; this chunk starts at `0xB297`. Next chunk continues at `0xFBE1 -> { 0xE9, 0xA0, 0x80 }` and closes the array and guards. Whole-file validation requires merging all chunks before checking the full `KICONV_UHC_UTF8_MAX == 17047` table length and sortedness.