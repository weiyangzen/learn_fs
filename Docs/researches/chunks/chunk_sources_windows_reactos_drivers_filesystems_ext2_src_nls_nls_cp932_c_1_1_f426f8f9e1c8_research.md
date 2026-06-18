# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp932.c lines 1-3983

## Scope

- Repository subset: `Docs/research_subset_a.md`; `sources/windows/reactos` is explicitly in scope.
- Source span read: lines 1-3983 of `sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp932.c`.
- This is chunk 1 of a chunked CP932/Shift-JIS NLS table source. It covers the file prologue, Linux-style NLS includes, all byte-to-Unicode page tables, the byte-to-Unicode page index, the high-ASCII reverse table, and Unicode-to-CP932 reverse pages through most of `u2c_68`.
- The chunk ends inside `u2c_68[512]`; lines 3984-3989 complete that table and line 3991 starts `u2c_69[512]`.

## APIs and Data Structures

- Header dependencies in this chunk are `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>`. Although this lives under the ReactOS Ext2 source tree, this file is structurally a Linux NLS module copy/generator output.
- The generated prologue says the CP932 translation tables were generated from Microsoft Unicode code page data.
- `c2u_81` through `c2u_FC`: 45 `static wchar_t [256]` byte-to-Unicode pages for valid CP932 lead bytes: `0x81..0x84`, `0x87..0x9F`, `0xE0..0xEA`, `0xED..0xEE`, and `0xFA..0xFC`.
- `page_charset2uni[256]` maps a lead byte to one of the `c2u_*` pages, or `NULL` when the lead byte is not a valid two-byte CP932 page.
- `u2c_00hi[256 - 0xA0][2]` maps selected Unicode `U+00A0..U+00FF` characters back to two-byte CP932 values; `{0x00, 0x00}` marks unmapped entries.
- `u2c_03`, `u2c_04`, `u2c_20` through `u2c_26`, `u2c_30`, `u2c_32`, `u2c_33`, and `u2c_4E` through the visible portion of `u2c_68` are reverse lookup pages. Each `u2c_*[512]` stores two bytes per Unicode low-byte slot.

## Control Flow

- There is no executable control flow in this chunk. It is table data only.
- Later conversion callbacks use these data structures: CP932-to-Unicode indexes `page_charset2uni[lead]` then `c2u_*[trail]`; Unicode-to-CP932 chooses a reverse page from `page_uni2charset`, then indexes `low_byte * 2` into a `u2c_*[512]` page.
- ASCII and halfwidth single-byte cases are not implemented in this chunk, but the tables are arranged around those later fast paths.

## State and Dependencies

- All visible symbols have internal linkage via `static`; this chunk introduces no mutable runtime state, locks, allocation, I/O, registration, or teardown.
- The arrays are not declared `const` in this ReactOS copy, so they are writable in C type terms even though they are intended as immutable generated tables.
- The tables depend on Linux NLS type/contracts (`wchar_t`, `struct nls_table`, callback signatures, `-EINVAL`) that appear later in the file.

## Risks and Edge Cases

- Any table drift or transcription error silently changes filename encoding behavior for filesystems using CP932/SJIS NLS conversion.
- `0x0000` in `c2u_*` and `{0x00, 0x00}` / byte pair `0x00,0x00` in `u2c_*` are unmapped sentinels.
- `page_charset2uni` must stay synchronized with the available `c2u_*` arrays.
- Reverse pages depend on the exact two-byte-per-Unicode-low-byte layout.
- CP932 intentionally includes vendor and compatibility mappings that differ from strict JIS/Shift-JIS expectations.
- The chunk boundary splits `u2c_68[512]`: line 3983 ends at low-byte range `0xE4-0xE7`, while lines 3984-3989 contain the remaining entries and closing brace.

## Cross-Chunk References

- Chunk 2 must continue with the remainder of `u2c_68[512]`, then `u2c_69` onward through the remaining reverse tables.
- `page_uni2charset[256]`, `charset2lower[256]`, `charset2upper[256]`, `uni2char`, `char2uni`, `struct nls_table table`, init/exit registration, module metadata, and the `sjis` alias are all outside this chunk.
- Later `uni2char` should be checked against this chunk for special handling of `u2c_00hi` and reverse-page sentinel pairs.
- Later `char2uni` should be checked against this chunk for how it treats single-byte input, lead-byte bounds, `page_charset2uni`, and `0x0000` table entries.