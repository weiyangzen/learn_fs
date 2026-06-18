# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 61209-63451

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` lines 61209-63451 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing table declaration, type definition, preprocessor guards, and nearby kiconv registration context. This chunk is static kernel character-conversion data, not executable control logic.

## APIs And Exported Data

The chunk is the final portion of the `static kiconv_table_t kiconv_utf8_gb18030[]` initializer declared at line 81 under `#ifdef _KERNEL`. Adjacent context defines `KICONV_UTF8_GB18030_MAX` as `63361`; this slice contributes 2,234 mapping entries and then closes the table and header guards at lines 63443-63451.

Each entry is a two-field `kiconv_table_t` pair:

- `key`: a UTF-8 byte sequence packed into a `uint32_t`, such as `0xEF9D86`.
- `value`: the GB18030 result packed into a `uint32_t`; most entries here are four-byte GB18030 sequences, with selected two-byte GBK/GB18030 compatibility values.

The exact chunk boundary starts at `0xEF9D86 -> 0x8339D239` and ends at `0xEFBFBF -> 0x8431A439`. Notable embedded two-byte mapping runs include `0xFD9C`-`0xFDA0`, `0xFE40`-`0xFE4F`, CJK punctuation-style values in the `0xA6xx` and `0xA9xx` ranges, fullwidth ASCII mappings `0xEFBC81`-`0xEFBD9E` mostly to `0xA3A1`-`0xA3FD`, and final special mappings around `0xEFBFA0`-`0xEFBFA5`.

## Control Flow

There are no functions, branches, loops, allocations, locks, or runtime side effects in this chunk. The only control-affecting syntax is preprocessor structure: the array is compiled only for `_KERNEL`, and the file closes its C++ `extern "C"` and include guards after the initializer.

Runtime conversion behavior is indirect. Adjacent common kiconv declarations define `kiconv_table_t`, `kiconv_binsearch()`, and UTF-8-to-CCK wrapper functions that operate on mapping tables of this shape. `kiconv.c` registers `gb18030` as a normalized code name with code id `9`, but this checked-in tree does not show a direct C include of this specific generated header outside the header list in `uts/common/sys/Makefile`.

## State And Dependencies

The chunk contributes immutable static table state in every kernel translation unit that includes the header with `_KERNEL` set. Because the symbol is `static`, linkage is internal to the including translation unit rather than a shared exported object.

Direct dependencies are:

- `kiconv_table_t` from `sys/kiconv_cck_common.h`, a `{ uint32_t key; uint32_t value; }` pair.
- The `_KERNEL` preprocessor gate surrounding the table.
- Header installation/listing through `uts/common/sys/Makefile`.
- Unicode/GB18030 mapping data provenance noted in the file header.

The table is sorted by ascending packed UTF-8 key in this chunk, matching binary-search expectations visible in common kiconv declarations.

## Risks And Cross-Chunk References

A single wrong literal can silently produce incorrect filename or string conversion for GB18030 locales. The main risks are table drift from the authoritative mapping source, broken sort order, duplicate or missing UTF-8 keys, and mismatches between `KICONV_UTF8_GB18030_MAX` and the actual table size used by converter glue.

This is a continuation from previous chunks of the same oversized header: it starts mid-array after earlier UTF-8-to-GB18030 mappings and closes the array and file. There is no later chunk for this file after line 63451. Cross-file context for the reverse direction is `kiconv_gb18030_utf8.h`; common table semantics and conversion wrappers are in `kiconv_cck_common.h`, while charset-name registration is visible in `uts/common/os/kiconv.c`.