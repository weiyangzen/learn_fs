# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp932.c lines 1-4152

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/os/linux/linux` is explicitly in scope.
- Source span read: lines 1-4152 of `fs/nls/nls_cp932.c`.
- This is chunk 1 of 2 for the Linux NLS CP932/Shift-JIS module. It covers the file prologue, kernel includes, all byte-to-Unicode page tables, the byte-to-Unicode page index, the high-ASCII Unicode table, and the first half of Unicode-to-CP932 page tables.
- The chunk ends inside `u2c_6B[512]`; it does not include the remaining Unicode-to-CP932 tables, case tables, conversion callbacks, `struct nls_table`, registration functions, or module metadata.

## APIs and Data Structures

- Header dependencies in this chunk are `linux/module.h`, `linux/kernel.h`, `linux/string.h`, `linux/nls.h`, and `linux/errno.h`.
- `c2u_81` through `c2u_FC`: 45 `static const wchar_t [256]` byte-to-Unicode pages for CP932 lead bytes `0x81..0x9F`, `0xE0..0xEA`, `0xED..0xEE`, and `0xFA..0xFC`. Entries use `0x0000` as the unmapped sentinel.
- `page_charset2uni[256]`: top-level lead-byte index. It maps valid two-byte CP932 lead bytes to `c2u_*` pages and leaves unsupported lead bytes as `NULL`.
- `u2c_00hi[256 - 0xA0][2]`: special Unicode `U+00A0..U+00FF` reverse table for selected punctuation and signs.
- `u2c_03`, `u2c_04`, `u2c_20` through `u2c_26`, `u2c_30`, `u2c_32`, `u2c_33`, and `u2c_4E` through the first part of `u2c_6B`: reverse lookup pages where each Unicode low byte selects a two-byte CP932 pair.
- Visible mapped ranges include Greek, Cyrillic, punctuation, arrows/math symbols, box drawing, CJK symbols, fullwidth forms, Kana-related values, CJK ideographs from `U+4E00`, and CP932/IBM extension byte pairs.

## Control Flow

There are no functions or executable branches in this chunk. Later callbacks consume these tables:

- CP932-to-Unicode conversion uses ASCII/halfwidth fast paths or indexes `page_charset2uni`; `NULL` pages and `0x0000` entries are invalid.
- Unicode-to-CP932 conversion uses Unicode high-byte table selection in chunk 2, then low-byte `* 2` indexing into these `u2c_*` pages.
- ASCII and halfwidth Katakana fast paths are implemented later, but this chunk’s tables are shaped around those rules.

## State and Dependencies

All data here is `static const`; there is no mutable state, locking, allocation, or reference counting. The generated table comment identifies Microsoft Unicode code page data as the source. Types and contracts come from Linux kernel NLS headers, and these internal-linkage arrays become externally reachable only through the `nls_table` callbacks in chunk 2.

## Risks and Edge Cases

- Table data corruption silently changes filename character conversion for filesystems using NLS `cp932`/`sjis`.
- `0x0000` and `{0x00, 0x00}` are sentinels, not valid generated double-byte mappings.
- `page_charset2uni` must stay synchronized with the defined `c2u_*` pages.
- Reverse pages assume exactly two bytes per Unicode low-byte slot.
- The chunk boundary splits `u2c_6B[512]`; lines 4115-4183 must be treated as one table.
- CP932 vendor/compatibility mappings intentionally differ from strict Shift-JIS/JIS behavior.

## Cross-Chunk References

- Chunk 2 continues `u2c_6B[512]`, then defines remaining `u2c_*` tables, `page_uni2charset`, case tables, conversion callbacks, registration, and module metadata.
- `uni2char` consumes `u2c_00hi` and `u2c_*` pages, returning `-EINVAL` for `{0x00, 0x00}`.
- `char2uni` consumes `page_charset2uni` and `c2u_*`, returning `-EINVAL` for `0x0000`.
- `struct nls_table table` exposes these tables as `.charset = "cp932"` and `.alias = "sjis"`.
- Linux-stable and ReactOS CP932 files are useful comparison points for generated-table drift; no final per-file report was created.