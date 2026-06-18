# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp950.c lines 8284-9483

## Scope

This chunk covers the tail of the generated Unicode-to-CP950 table data and the runtime NLS entry points for the Linux `cp950`/`big5` charset module. It is data-heavy: most of the chunk is static reverse-mapping arrays, followed by the page dispatch table, ASCII-only case-folding tables, conversion callbacks, `struct nls_table`, and module registration metadata.

## APIs And Entry Points

- `uni2char()` implements the NLS Unicode-to-charset callback. It returns output length or `-ENAMETOOLONG`/`-EINVAL`.
- `char2uni()` implements the NLS charset-to-Unicode callback. It returns consumed input length or `-ENAMETOOLONG`/`-EINVAL`.
- `table` publishes `.charset = "cp950"`, `.alias = "big5"`, conversion callbacks, and byte case maps.
- `init_nls_cp950()` / `exit_nls_cp950()` register and unregister the table with the kernel NLS core.
- Module macros provide lifecycle and alias metadata.

## Mapping Data

Lines 8287-9289 define reverse Unicode-page tables `u2c_93` through `u2c_9F`, plus `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF`. Each entry stores two CP950 bytes per Unicode low byte; `0x00,0x00` means unmapped.

`page_uni2charset[256]` dispatches Unicode high-byte pages to these and earlier `u2c_*` arrays. `charset2lower` and `charset2upper` are ASCII-only byte case maps; bytes `0x80-0xff` remain identity.

## Control Flow

`uni2char()` splits `wchar_t` into high and low bytes, selects a page via `page_uni2charset`, writes a two-byte CP950 pair, and rejects zero pairs. If Unicode page is zero and low byte is nonzero, it emits a one-byte ASCII value.

`char2uni()` rejects empty input. With one byte available, it returns identity Unicode for that byte. With two bytes, it indexes `page_charset2uni[rawstring[0]]` and then the selected table by `rawstring[1]`; zero Unicode results are invalid. Missing table or zero second byte falls back to one-byte identity.

## State And Dependencies

All tables are `static const`; runtime conversion has no mutable state except module registration. This chunk depends on Linux NLS APIs, module macros, errno values, `wchar_t`, and earlier file definitions, especially `page_charset2uni` and prior `u2c_*` arrays.

## Risks And Edge Cases

- `uni2char()` rejects `U+0000`.
- `char2uni()` treats a single available lead byte as identity rather than incomplete multibyte input.
- Short initializer arrays rely on C zero-fill, intentionally producing unmapped entries.
- Duplicate mappings can make round trips direction-dependent.
- Case folding is byte-wise ASCII-only, not fullwidth or multibyte aware.

## Cross-Chunk References

The chunk begins by closing a table started in the previous chunk. `page_uni2charset` references many earlier reverse tables (`u2c_02`, `u2c_03`, `u2c_20`-`u2c_92`, etc.). `char2uni()` depends on earlier forward `c2u_*` tables through `page_charset2uni`. This chunk completes the file’s runtime module wiring but does not create the merged per-file report.