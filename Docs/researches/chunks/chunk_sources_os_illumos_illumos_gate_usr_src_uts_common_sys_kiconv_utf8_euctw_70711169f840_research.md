# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euctw.h lines 49827-55539

## Scope

This chunk is the final slice of the kernel-only `kiconv_utf8_euctw[]` mapping table. The table is declared earlier as `static kiconv_table_t kiconv_utf8_euctw[]` and maps UTF-8 byte sequences, encoded as packed `uint32_t` keys, to packed EUC-TW/CNS 11643 output values. The file comment says the table covers UTF-8 to CNS 11643, includes planes 1/2/14, supports CNS11643-86, and is based on Unicode 3.2 / Unihan 3.2.0.

## APIs And Data

- Public symbols visible from this chunk: none newly declared. The chunk completes an existing static array and closes `_KERNEL`, `extern "C"`, and `_SYS_KICONV_UTF8_EUCTW_H` guards.
- Main data contribution: 5,704 `kiconv_table_t` initializer entries from `0xF0A8AB8C -> 0xFE1B5` through `0xF0AFA89D -> 0x7DECD`.
- Table element type comes from `kiconv_cck_common.h`: `kiconv_table_t` has `uint32_t key` and `uint32_t value`.
- The enclosing file defines `KICONV_UTF8_EUCTW_MAX` as `55442`; consumers must use the whole-table count, not this chunk count.

## Control Flow

There is no executable control flow in the chunk. Runtime behavior is indirect: the common UTF-8-to-CCK conversion path can binary-search sorted `kiconv_table_t` arrays and emit the mapped value when a key is found.

## State And Dependencies

- State is compile-time static mapping data under `#ifdef _KERNEL`; no mutable state is introduced.
- The chunk depends on earlier file context for the array declaration, header guard, and table metadata.
- It depends structurally on `kiconv_table_t` and common kiconv conversion helpers declared in `sys/kiconv_cck_common.h`.
- The file is listed by `usr/src/uts/common/sys/Makefile`.

## Risks

- Ordering is critical because the common lookup path expects sorted UTF-8 keys for binary search.
- Count consistency is critical: `KICONV_UTF8_EUCTW_MAX` must match the full array entry count.
- The table is old by design: Unicode 3.2 / Unihan 3.2.0, with CNS11643-92 not supported.
- Raw initializer transcription errors can compile cleanly while producing incorrect character conversion.

## Cross-Chunk References

- Earlier chunks define the header metadata, `KICONV_UTF8_EUCTW_MAX`, the array declaration, the special non-identical conversion entry, and preceding mappings.
- Chunk 4 directly precedes this range and ends at `0xF0A8AB8B -> 0xFE1B9`; this chunk starts at `0xF0A8AB8C -> 0xFE1B5`.
- This is the terminal chunk for the file; it supplies the final entries and closing syntax for the array and guards.

## Verification

- Read `Docs/research_subset_a.md` and confirmed `sources/os/illumos/illumos-gate` is in subset A.
- Read the complete requested range, lines 49827-55539.
- Checked adjacent context around the declaration and closeout.
- Wrote the chunk report to `Docs/researches/chunks/chunk_sources_os_illumos_illumos_gate_usr_src_uts_common_sys_kiconv_utf8_euctw_70711169f840_research.md`.
- Did not create the final per-file merged report.