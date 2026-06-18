# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h lines 11565-23674

## Scope

This report covers only chunk 2 of the oversized illumos kernel header `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb18030.h`, lines 11565-23674, within learn_fs subset A (`Docs/research_subset_a.md`). The range was read completely. Adjacent context was used only to identify the enclosing declaration, shared table type, and kiconv registry context.

The chunk is entirely initializer data inside `static kiconv_table_t kiconv_utf8_gb18030[]`; it starts mid-array at `0xE2B59A -> 0x8138E034` and ends mid-array at `0xE5B2A7 -> 0x8CFD`.

## APIs And Exported Data

No callable API, macro, typedef, or externally linked symbol is defined in this chunk. The exported behavior is data-driven through the enclosing static table:

- The table is declared earlier in the file under `#ifdef _KERNEL`.
- `KICONV_UTF8_GB18030_MAX` is defined earlier as `63361`.
- Each row is a `kiconv_table_t` pair from `sys/kiconv_cck_common.h`: `uint32_t key` and `uint32_t value`.
- `key` is a UTF-8 byte sequence packed into a 32-bit integer.
- `value` is a GB18030 result packed into a 32-bit integer; values with four encoded bytes use eight hex digits, while two-byte GBK/GB18030 compatibility results use four hex digits.

This chunk contributes 12,110 mapping rows. I counted 8,009 four-byte GB18030 mappings and 4,101 two-byte mappings. The first two-byte entry in this chunk is `0xE2BA81 -> 0xFE50` at line 11860; the last four-byte entry in this chunk is `0xE4B7BF -> 0x82358F32` at line 19922; after line 19923 the visible range is the CJK ideograph section represented here by two-byte GB mappings through `0x8CFD`.

## Control Flow

There is no local control flow: no functions, branches, loops, allocations, locking, or error handling appear in the assigned range. Runtime conversion control flow is supplied by kiconv converter code that includes or otherwise compiles this table and searches it.

Rows are sorted by ascending packed UTF-8 key. Discontinuities such as `0xE2B5BF -> 0xE2B680` and `0xE2BFBF -> 0xE38080` are expected UTF-8 byte-boundary and Unicode block transitions, not executable branches.

## State And Data Flow

The chunk contributes immutable kernel conversion state. A caller's decoded/packed UTF-8 input key flows into a table lookup; the corresponding table value becomes the emitted GB18030 byte sequence.

Visible data-flow patterns:

- Lines 11565-11859 continue dense four-byte GB18030 algorithmic mappings in the `0x8138...` region.
- Lines 11860-19922 mix four-byte mappings with selected two-byte compatibility mappings, including `0xFExx`, `0xA1xx`, `0xA2xx`, `0xA4xx`, `0xA5xx`, and other GB ranges.
- Line 19923 enters common CJK ideograph mappings, beginning `0xE4B880 -> 0xD2BB`; from there through line 23674 this chunk's visible entries are two-byte GB values.
- The visible packed UTF-8 key range runs from `0xE2B59A` through `0xE5B2A7`.

No mutable state is updated by the table itself. Because the enclosing array is `static` in a header, storage is internal to each translation unit that includes it with `_KERNEL` enabled.

## Dependencies

Direct dependencies visible from adjacent context are:

- `kiconv_table_t` from `sys/kiconv_cck_common.h`.
- `_KERNEL`, which gates the table declaration.
- Consumers honoring `KICONV_UTF8_GB18030_MAX` and the sorted key invariant.
- Header installation/listing through `uts/common/sys/Makefile`.
- Charset-name registration context in `uts/common/os/kiconv.c`, where `gb18030` is listed as a normalized code name.

The checked tree did not show a direct C source reference to the `kiconv_utf8_gb18030` symbol outside this generated header; the table is likely consumed through generated or build-selected kiconv module include paths.

## Risks And Edge Cases

The main correctness risk is silent data corruption from a bad literal, missing row, duplicate key, or sort-order break. Since conversion is table-driven, a single row error can affect file names or strings converted under GB18030 locales without any local runtime check in this header.

Lookup code must distinguish two-byte and four-byte output values from the packed integer form. Values such as `0xFE50` and `0x8138E034` are both stored in the same `uint32_t value` field, so consumers must already know how to emit the correct number of bytes.

Four-byte GB18030 values in this chunk follow the byte-shape constraints for GB18030 sequences: first byte `0x81`-`0x84`, second byte `0x30`-`0x39`, third byte `0x81`-`0xFE`, fourth byte `0x30`-`0x39`. Two-byte values are interspersed before the ideograph-heavy tail, so code must not assume a single output width over the chunk.

The `static` header table can duplicate a large amount of read-only data if included by multiple kernel translation units. The file-level merge should check whether this is an established pattern across sibling kiconv headers rather than treating it as a local anomaly.

## Cross-Chunk References

This is chunk 2 of 6 for `kiconv_utf8_gb18030.h` according to `Docs/researches/chunk_manifest.tsv`.

- Chunk 1 contains the license/header guards, `KICONV_UTF8_GB18030_MAX`, the `kiconv_utf8_gb18030[]` declaration, the special non-identical conversion entry, and earlier UTF-8-to-GB18030 mappings through line 11564.
- This chunk continues the same array from line 11565 to line 23674 and ends mid-table after `0xE5B2A7 -> 0x8CFD`.
- Chunk 3 begins at line 23675 and should continue the CJK ideograph section.
- Later chunks continue and eventually close the array and preprocessor guards.

The reverse-direction data lives in `kiconv_gb18030_utf8.h`; common table types and helper prototypes live in `kiconv_cck_common.h`; charset registration context is in `uts/common/os/kiconv.c`.