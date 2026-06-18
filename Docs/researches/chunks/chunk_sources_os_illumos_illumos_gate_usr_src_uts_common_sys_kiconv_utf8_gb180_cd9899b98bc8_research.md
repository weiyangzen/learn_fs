# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 37472-49451

## Scope

This report covers only `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h` lines 37472-49451 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the enclosing declaration, table type, guards, and registration context. This chunk is generated/static kernel character-conversion data, not executable filesystem or VFS logic.

## APIs And Exported Data

The chunk is a middle slice of the `_KERNEL`-only `static kiconv_table_t kiconv_utf8_gb18030[]` initializer declared near the top of the file. Adjacent context defines `KICONV_UTF8_GB18030_MAX` as `63361`; this chunk contributes 11,980 table entries.

Each entry is a `kiconv_table_t` pair:

- `key`: a UTF-8 byte sequence packed into a `uint32_t`.
- `value`: the GB18030 output sequence packed into a `uint32_t`; values in this chunk are either two-byte GBK/GB18030 compatibility values or four-byte GB18030 sequences.

The exact requested range starts at `0xE98A8D -> 0xE387` and ends at `0xEC8598 -> 0x8331F939`. Lines 37472-40824 contain 3,353 two-byte destination mappings, ending with `0xE9BEA5 -> 0xFD9B`. Lines 40825-49451 contain 8,627 four-byte destination mappings, starting at `0xE9BEA6 -> 0x82358F33`.

## Control Flow

There are no functions, branches, loops, lock operations, allocations, or direct runtime side effects in this line range. Runtime behavior is indirect: common kiconv conversion code can binary-search or otherwise consult this sorted table when converting packed UTF-8 input to GB18030 bytes.

The only control-affecting structure is outside this chunk: the whole array is under `_KERNEL`, with C++ linkage guards and include guards around the header. Because the table is declared `static`, including translation units receive internal-linkage table storage rather than an exported global symbol.

## State And Dependencies

This chunk contributes immutable lookup-table state to the UTF-8-to-GB18030 converter. It depends on `kiconv_table_t` from `sys/kiconv_cck_common.h`, defined as two `uint32_t` fields (`key` and `value`). Adjacent common declarations also expose `kiconv_utf8tocck_t`, UTF-8-to-CCK wrapper prototypes, and `kiconv_binsearch()`, which explains why sorted packed keys matter.

The source file is listed for installation in `usr/src/uts/common/sys/Makefile`, and `usr/src/uts/common/os/kiconv.c` registers `gb18030` as a known code name. A repository-wide search in the checked-in tree found no direct `.c` reference to `kiconv_utf8_gb18030` or `KICONV_UTF8_GB18030_MAX` outside this header, so the concrete include/generator path is not visible in this chunk alone.

## Risks

The main correctness risks are data risks: an incorrect literal can silently corrupt GB18030 conversion for affected Unicode code points; an unsorted key, duplicate key, or missing key can break binary-search-based lookup; and a mismatch between the actual table size and `KICONV_UTF8_GB18030_MAX` can cause incomplete searches or out-of-bounds reads in consumers.

The two-byte to four-byte transition at lines 40824-40825 is a useful audit boundary. Any regeneration or hand edit should preserve ascending UTF-8 keys across that boundary and maintain GB18030 sequence legality, especially the four-byte byte-class constraints encoded by values such as `0x82358F33` through `0x8331F939`.

## Cross-Chunk References

This chunk continues the same array from earlier chunks and ends mid-array. The next chunk begins at line 49452 with `0xEC8599 -> 0x8331FA30`, continuing the four-byte GB18030 sequence run. The prior chunk should end at line 37471 with `0xE98A8C -> 0xE386`, immediately before this chunk's first key.

Related files visible from adjacent context are `kiconv_cck_common.h` for the shared table type and wrapper contracts, `kiconv_gb18030_utf8.h` for the reverse-direction mapping table, `uts/common/os/kiconv.c` for charset-name registration, and `uts/common/sys/Makefile` for header listing.