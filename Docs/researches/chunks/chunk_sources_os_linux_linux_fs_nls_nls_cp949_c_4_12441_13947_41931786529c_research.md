# Chunk Research: sources/os/linux/linux/fs/nls/nls_cp949.c lines 12441-13947

## Scope

This chunk is the tail of the Linux kernel CP949/EUC-KR NLS module. It covers the end of the generated Unicode-to-charset lookup data, the page index used by Unicode encoding, ASCII-only case tables, the two conversion callbacks exported through `struct nls_table`, and module registration metadata.

## APIs and Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` at lines 13861-13890 is the Unicode-to-CP949 encoder callback assigned to `table.uni2char`.
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` at lines 13892-13921 is the CP949-to-Unicode decoder callback assigned to `table.char2uni`.
- `static struct nls_table table` at lines 13923-13930 publishes charset name `"cp949"`, alias `"euc-kr"`, conversion callbacks, and case tables to the kernel NLS core.
- `init_nls_cp949()` and `exit_nls_cp949()` at lines 13932-13940 register/unregister the table via `register_nls(&table)` and `unregister_nls(&table)`.
- `module_init`, `module_exit`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(euc-kr)` at lines 13942-13947 expose this as a loadable NLS module.

## Data and State

- Lines 12441-12471 finish `u2c_C6`, whose declaration begins before this chunk. This is a cross-chunk continuation and should be merged with chunk 3 data context.
- Lines 12473-13604 define `u2c_C7` through `u2c_D7`, each as `static const unsigned char [512]`.
- Lines 13755-13787 define `page_uni2charset[256]`, the high-byte dispatch table for `uni2char`.
- Lines 13789-13859 define `charset2lower` and `charset2upper`; only ASCII A-Z/a-z fold, while bytes `0x80-0xff` remain identity.
- Runtime state is effectively immutable table data plus the static NLS registration table.

## Control Flow

`uni2char` checks output bounds, dispatches by Unicode high byte into `page_uni2charset`, emits two-byte CP949 mappings, rejects zero-pair invalid entries with `-EINVAL`, and falls back to single-byte non-NUL ASCII when no page exists.

`char2uni` checks input bounds, decodes one-byte buffers as identity, otherwise dispatches by first byte into `page_charset2uni`, rejects zero Unicode entries, and falls back to single-byte identity when no valid two-byte mapping applies.

## Dependencies

- Linux NLS/module APIs: `struct nls_table`, `register_nls`, `unregister_nls`, module macros.
- Error constants: `-ENAMETOOLONG`, `-EINVAL`.
- Earlier chunks define `page_charset2uni`, `c2u_*`, and most `u2c_*` tables referenced here.

## Risks and Cross-Chunk References

- Generated table corruption would silently corrupt CP949 filename/string conversion.
- `0x00,0x00` and `0x0000` are invalid sentinels, so NUL mappings are not representable through these paths.
- `boundlen == 1` in `char2uni` returns single-byte identity, not truncation.
- This chunk starts mid-`u2c_C6` and ends with module registration, so the merge should connect earlier generated tables to the callbacks and NLS registration here.