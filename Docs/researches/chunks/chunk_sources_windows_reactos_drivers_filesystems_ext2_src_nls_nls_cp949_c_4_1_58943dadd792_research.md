# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp949.c lines 11937-13948

## Scope

This chunk covers the tail of the CP949 Unicode-to-charset mapping data and the only executable conversion/registration logic visible in the file tail. It starts mid-definition inside `u2c_BF` at Unicode page `0xBF` offset `0x1C`, then defines `u2c_C0` through `u2c_D7`, sparse pages `u2c_DC`, `u2c_F9`, `u2c_FA`, and `u2c_FF`, builds `page_uni2charset[256]`, provides ASCII-only case maps, implements `uni2char()` and `char2uni()`, and registers the `cp949`/`euc-kr` NLS table as a kernel module.

## APIs and Entry Points

- `uni2char()` converts one Unicode code point to one or two CP949 bytes using `page_uni2charset`.
- `char2uni()` converts one CP949 byte sequence to one Unicode code point using `page_charset2uni`.
- `table` exposes charset `"cp949"` with alias `"euc-kr"` to the kernel NLS layer.
- `init_nls_cp949()` and `exit_nls_cp949()` register/unregister the table via `register_nls()` and `unregister_nls()`.

## Control Flow and State

`uni2char()` checks output capacity, splits Unicode into high/low bytes, uses a high-byte page lookup, emits two bytes for mapped pages, rejects zero-pair mappings as `-EINVAL`, and falls back to nonzero ASCII only when no page exists.

`char2uni()` checks input length, treats one-byte input as a single character, otherwise uses the first byte as a lead-byte page selector and the second byte as an index. Missing pages or `cl == 0` fall back to single-byte output.

State is static lookup data plus a static `nls_table`. The arrays are mutable by declaration but used as immutable generated tables.

## Dependencies

This chunk depends on earlier file chunks for `page_charset2uni`, `c2u_*`, and many earlier `u2c_*` pages. It also depends on kernel/NLS types and macros: `wchar_t`, `struct nls_table`, `ENAMETOOLONG`, `EINVAL`, `THIS_MODULE`, `__init`, `__exit`, module macros, and NLS registration APIs.

## Risks and Cross-Chunk Notes

- The chunk begins inside `u2c_BF`; previous chunk data is required for the full page.
- Sparse pages rely on implicit zero fill and zero-pair invalidation.
- Dangling CP949 lead bytes with `boundlen == 1` pass through as single-byte Unicode.
- Case folding is ASCII-only.
- The positional table layout is the contract, so hand edits or formatter rewrites are high risk.