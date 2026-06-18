# Chunk Research: sources/os/linux/linux-stable/fs/nls/nls_cp949.c lines 12441-13947

## Scope

This chunk is the final slice of the Linux NLS CP949/EUC-KR conversion module. It starts inside the tail of a Unicode-to-charset page table from the previous chunk, defines additional Unicode page mapping tables, builds the `page_uni2charset` dispatch table, defines byte-wise case-folding tables, implements both conversion callbacks, and registers the charset as a kernel NLS table.

The file is in subset A through `sources/os/linux/linux-stable`.

## APIs And Data

- Static Unicode-to-charset tables visible here:
  - Tail of the previous `u2c_C6` table at lines 12441-12471.
  - Complete `u2c_C7` through `u2c_D7` tables, each declared as `static const unsigned char ...[512]`, mapping one Unicode high-byte page and 256 low-byte slots to two CP949 output bytes.
  - Sparse/special pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`. These include zero pairs for unmapped Unicode positions.
- `page_uni2charset[256]` maps a Unicode high byte to one of the `u2c_*` tables or `NULL`. This is the main dispatch table for `uni2char()`.
- `charset2lower[256]` and `charset2upper[256]` provide single-byte case mapping. Only ASCII letters are folded; bytes `0x80-0xff` map to themselves.
- `uni2char()` is the NLS Unicode-to-CP949 callback.
- `char2uni()` is the CP949-to-Unicode callback and consumes earlier `page_charset2uni` tables.
- `table` registers charset `"cp949"` with alias `"euc-kr"`.

## Control Flow

`uni2char()` validates output space, splits Unicode into high/low bytes, dispatches through `page_uni2charset[ch]`, emits two CP949 bytes when mapped, rejects `0x00,0x00` mappings with `-EINVAL`, or falls back to one-byte identity for nonzero Unicode page 0 values.

`char2uni()` validates input length, maps one-byte input directly, otherwise dispatches first byte through `page_charset2uni`. If a double-byte page and nonzero second byte exist, it reads the Unicode mapping, rejects zero mappings, and returns 2; otherwise it maps the first byte directly.

Module init/exit simply call `register_nls(&table)` and `unregister_nls(&table)`.

## State And Dependencies

All mapping data is `static const`; there is no mutable conversion state beyond the static `struct nls_table` registration. Dependencies include earlier `u2c_*` tables, earlier `page_charset2uni`/`charset2uni` tables, Linux NLS APIs, module macros, and errno values.

## Risks

- Large generated tables can silently encode wrong character mappings.
- `0x00,0x00` is the invalid sentinel for Unicode-to-charset entries.
- Truncated multibyte input can be accepted as one-byte identity if callers pass `boundlen == 1`.
- Case folding is ASCII-only and byte-wise.
- `page_uni2charset` must stay synchronized with all generated table declarations.

## Cross-Chunk References

This chunk starts inside a table opened earlier, relies on earlier chunks for most `u2c_*` pages and all charset-to-Unicode tables, and is the terminal chunk containing conversion callbacks, NLS registration, module hooks, and metadata.

## Verification

- Read `Docs/research_subset_a.md`.
- Read complete requested range `12441-13947`.
- Wrote the chunk report to `Docs/researches/chunks/chunk_sources_os_linux_linux_stable_fs_nls_nls_cp949_c_4_12441_13947_9a944806100b_research.md`.
- Did not create the final per-file report.