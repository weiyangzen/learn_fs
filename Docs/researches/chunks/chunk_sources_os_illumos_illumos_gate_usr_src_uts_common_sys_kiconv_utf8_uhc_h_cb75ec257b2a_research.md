# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_uhc.h lines 1-13706

## Scope

This chunk is in learn_fs subset A because `sources/os/illumos/illumos-gate` is listed in `Docs/research_subset_a.md`. I read the requested source range completely: lines 1-13706 of `usr/src/uts/common/sys/kiconv_utf8_uhc.h`. Adjacent context was used only to confirm that line 13707 continues the same initializer and that the full file later closes the table and guards.

The file is a generated-style illumos kernel Korean code-conversion header. This chunk contains the file prologue, include/C++/kernel guards, the UTF-8-to-UHC table-size macro, and the first 13,625 rows of the `kiconv_utf8_uhc[]` initializer. It ends inside the table body.

## APIs and Data Surface

- Header guard: `_SYS_KICONV_UTF8_UHC_H`.
- C++ wrapper: `extern "C"` around kernel declarations.
- Kernel-only section: all conversion data is under `#ifdef _KERNEL`.
- Macro introduced in this chunk: `KICONV_UTF8_UHC_MAX (17047)`.
- Main object introduced in this chunk: `static kiconv_table_t kiconv_utf8_uhc[] = { ... }`.
- Table element type: `kiconv_table_t` from `sys/kiconv_cck_common.h`, with `uint32_t key` and `uint32_t value`.

Verified chunk statistics:

- 13,625 mapping rows in lines 1-13706.
- First row: line 82, `0x0000 -> 0x003F`, the hold entry for non-identical conversion.
- Last row in this chunk: line 13706, `0xECAEB5 -> 0xA892`.
- No duplicate keys or non-ascending keys detected.
- Key shapes: 1 sentinel row, 170 two-byte UTF-8 keys, and 13,454 three-byte UTF-8 keys.
- 8,118 keys fall in the Hangul syllable UTF-8 range.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is data-driven: shared UTF-8-to-CCK code packs input UTF-8 into a `uint32_t`, searches the sorted `kiconv_utf8_uhc[]` table via common lookup logic such as `kiconv_binsearch`, and emits the packed UHC value on a hit. Invalid-input, replacement, output-space, and errno handling live outside this header.

## State and Dependencies

All state is compile-time static table data. Because the table is `static` in a header, each translation unit including it under `_KERNEL` can receive a private copy.

Visible and related dependencies:

- `sys/kiconv_cck_common.h`: `kiconv_table_t`, `kiconv_utf8tocck_t`, `kiconv_binsearch`, `kiconv_utf8_to_cck`, `kiconvstr_utf8_to_cck`.
- `sys/kiconv_ko.h`: UHC byte validity macros.
- `sys/kiconv_uhc_utf8.h`: reverse UHC-to-UTF-8 companion table.
- `usr/src/uts/common/sys/Makefile`: exports this header and the reverse header.
- `usr/src/uts/common/os/kiconv.c`: broader kernel iconv registration and replacement handling.

## Risks and Invariants

- `KICONV_UTF8_UHC_MAX` must match the complete table length across all chunks; the full file has 17,047 rows.
- The table must remain sorted by packed UTF-8 key for binary-search consumers.
- The sentinel `0x0000 -> 0x003F` is part of non-identical conversion behavior.
- Gaps are expected because not every Unicode scalar maps to UHC.
- The table is not `const`; accidental writes by including code could mutate local conversion behavior.
- This chunk is syntactically incomplete by design: it opens the header and array but does not close the initializer or guards.

## Cross-Chunk References

- This first chunk owns the prologue, guards, `KICONV_UTF8_UHC_MAX`, and the start of `kiconv_utf8_uhc[]`.
- The chunk ends at line 13706 with `0xECAEB5 -> 0xA892`; line 13707 continues with `0xECAEB6 -> 0xA893`.
- Later chunk(s) must preserve ascending order, close the table initializer, and close `_KERNEL`, `extern "C"`, and the include guard.
- Per-file merge should reconcile this chunk with the remaining chunk(s), verify `17047` total rows, and compare consistency with `kiconv_uhc_utf8.h`.