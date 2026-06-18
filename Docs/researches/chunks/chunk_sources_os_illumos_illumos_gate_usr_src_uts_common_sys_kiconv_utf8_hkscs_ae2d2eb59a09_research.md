# Chunk Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_hkscs.h lines 13703-18512

## Scope

This chunk covers lines 13703-18512 of `kiconv_utf8_hkscs.h` for `learn_fs` subset A. It is the final ordered segment of the kernel UTF-8-to-BIG5-HKSCS(2004) mapping table. The range starts mid-initializer at UTF-8 key `0xE8BA98`, continues through the end of the mapping data, and includes the closing table brace plus `_KERNEL`, C++ wrapper, and header-guard closures.

This chunk is data-only. It does not create the final per-file report.

## Public Surface And APIs

No new callable APIs, typedefs, or exported functions are introduced in this range. The chunk contributes rows to the file-level static table declared earlier:

- Header guard: `_SYS_KICONV_UTF8_HKSCS_H`.
- Kernel gate: table data is only compiled under `_KERNEL`.
- Macro declared earlier: `KICONV_UTF8_HKSCS_MAX (18420)`.
- Data object declared earlier: `static kiconv_table_t kiconv_utf8_hkscs[]`.
- Table element contract from `kiconv_cck_common.h`: `uint32_t key` and `uint32_t value`.

Each row stores a UTF-8 byte sequence packed as a hexadecimal integer key and a destination BIG5-HKSCS code value in the low 16 bits of `value`.

## Chunk Contents

The chunk contains 4,801 mapping rows:

- First row in chunk: `0xE8BA98 -> 0xf846`.
- Last row in chunk: `0xF0AFA794 -> 0x8ff0`.
- Key ordering in this chunk is ascending with no duplicate keys found by a local scan.
- Key sizes visible in this chunk: 3,108 three-byte UTF-8 keys and 1,693 four-byte UTF-8 keys.
- The table initializer closes at line 18504, followed by `_KERNEL`, `extern "C"`, and `_SYS_KICONV_UTF8_HKSCS_H` closeout lines.

## Control Flow

There is no executable control flow in this chunk. Runtime behavior is controlled by kernel kiconv code that includes this header, packs UTF-8 input bytes into a `uint32_t` key, searches `kiconv_utf8_hkscs[]`, and emits the mapped HKSCS value.

## State And Dependencies

State in this range is static initializer data. It is not declared `const`, but consumers should treat it as immutable conversion metadata.

Dependencies include `_KERNEL`, `kiconv_table_t`, the sorted-table search contract, and sibling kiconv tables such as `kiconv_hkscs_utf8.h`, `kiconv_utf8_cp950hkscs.h`, and `kiconv_cp950hkscs_utf8.h`.

## Risks And Cross-Chunk References

- Earlier chunk(s) contain the license, macro, table declaration, sentinel/default row, and mappings before `0xE8BA98`.
- Full-file merge should reconcile row count against `KICONV_UTF8_HKSCS_MAX`; a simple local pair-line count sees 18,418 rows while the macro says 18,420.
- Consumers likely rely on ascending keys for binary search.
- The large `static` header table can duplicate storage across translation units.
- `0xF0...` keys are packed UTF-8 bytes, not Unicode scalar values.