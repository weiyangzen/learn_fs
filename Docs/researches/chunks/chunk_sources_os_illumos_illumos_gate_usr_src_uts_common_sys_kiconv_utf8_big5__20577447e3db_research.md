# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_big5.h lines 1-13699

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/illumos/illumos-gate` is explicitly in scope.
- Source span read completely: lines 1-13699 of `usr/src/uts/common/sys/kiconv_utf8_big5.h`.
- This is chunk 1 of an oversized kernel header. It covers the license block, include/C++/kernel guards, `KICONV_UTF8_BIG5_MAX`, and the first 13,618 entries of the `kiconv_utf8_big5[]` UTF-8 to BIG5 mapping table.
- The chunk ends inside the table at line 13699; it does not include the final table entries, closing `};`, or closing preprocessor guards.

## APIs and Data Structures

- The header is protected by `_SYS_KICONV_UTF8_BIG5_H` and exposes content only under `_KERNEL`.
- `KICONV_UTF8_BIG5_MAX` is defined as `13711`, matching the full table row count observed in adjacent context.
- The only declared symbol in this chunk is `static kiconv_table_t kiconv_utf8_big5[]`.
- `kiconv_table_t` comes from `usr/src/uts/common/sys/kiconv_cck_common.h` and stores `uint32_t key` plus `uint32_t value`.
- In this table, `key` is a packed UTF-8 byte sequence and `value` is a packed BIG5 two-byte code, except the first sentinel row.

## Mapping Content

- Chunk row count: 13,618 mapping rows.
- First row: `0x0000 -> 0x003f`, documented as the special hold entry for non-identical conversion.
- First real mapping: `0xC2A2 -> 0xa246`.
- Last row in this chunk: `0xEFB9A4 -> 0xa1e0`.
- Key distribution is dominated by three-byte UTF-8: 1 sentinel/ASCII-range key, 118 two-byte packed keys, 13,499 three-byte packed keys, and 13,068 keys in the CJK Unified Ideographs UTF-8 byte range.
- Value validation found one sentinel value and no malformed BIG5 byte pairs by visible BIG5 byte rules.

## Control Flow

- There is no executable control flow in this chunk. It is compile-time data consumed by conversion code.
- The sorted ascending `key` order is the important behavioral property: common conversion code and CCK wrappers use binary-search-style lookup over mapping tables.
- Mechanical checks over lines 1-13699 found no non-ascending keys, no duplicate keys, and no invalid BIG5 byte pairs among non-sentinel values.

## State and Dependencies

- State is static kernel data emitted into each translation unit that includes this header because the table is declared `static` in a header.
- Direct visible dependencies: `_KERNEL`, `kiconv_table_t` from `kiconv_cck_common.h`, and kernel integer typedefs such as `uint32_t`.
- `usr/src/uts/common/sys/Makefile` lists `kiconv_utf8_big5.h` in the common sys header set.
- A direct reference search under `usr/src` found only this header and the sys header makefile entry for `kiconv_utf8_big5`; no direct include or consumer symbol reference was visible in the checked tree.

## Risks

- Data integrity is the main risk. A single wrong literal silently corrupts UTF-8 to BIG5 conversion for that character.
- `KICONV_UTF8_BIG5_MAX` must remain synchronized with the full table length. The full file has 13,711 table rows; this chunk owns 13,618 of them.
- Binary search requires the packed UTF-8 keys to stay strictly ascending.
- The initial `0x0000 -> 0x003f` sentinel is not a normal BIG5 mapping and should not be removed or counted as a Unicode character mapping without checking converter logic.
- Because this is a `static` table in a header, broad inclusion can duplicate the table in multiple objects.

## Cross-Chunk References

- The next chunk/tail starts at line 13700 with `0xEFB9A5 -> 0xa1e1`.
- Adjacent context shows 93 remaining rows after this chunk, ending at `0xEFBDA4 -> 0xa14e`, followed by the table close and `_KERNEL`, C++, and header guard closures.
- Any final per-file merge should combine this chunk with the tail so the report can state the full `KICONV_UTF8_BIG5_MAX == 13711` invariant and final closure ownership.
- No final per-file report was created.