# sources/distributed-fs/ceph-client/fs/nls/nls_cp1251.c

## Purpose
`nls_cp1251.c` provides the Windows CP1251 NLS table for Cyrillic-script languages. It maps CP1251 bytes to Unicode Cyrillic code points, punctuation, and symbols, and encodes exact Unicode matches back to one-byte CP1251.

## Important APIs, types, and functions
`charset2uni[256]` maps byte values to Unicode. The upper half contains Cyrillic letters in pages `0x04`, including Ukrainian/Belarusian/Serbian/Macedonian variants, plus punctuation such as smart quotes, dashes, `0x20ac`, `0x2116`, and `0x2122`. Reverse mapping uses `page00`, `page04`, `page20`, and `page21`.

The generated callback pair is `uni2char()`/`char2uni()`. `charset2lower` and `charset2upper` provide byte-level Cyrillic case folding. `table` registers `.charset = "cp1251"`, and the module entry/exit functions are `init_nls_cp1251()` and `exit_nls_cp1251()`.

## Control flow
Initialization registers the NLS table. Runtime conversion is exact and table driven. `char2uni()` turns a byte into a Unicode value and returns `-EINVAL` for undefined entries. `uni2char()` looks up the reverse page for the Unicode high byte and emits one byte if present. Empty output buffers return `-ENAMETOOLONG`; missing mappings return `-EINVAL`.

## State and persistence behavior
No mutable local state is kept. All mapping and case data is static constant data. The only runtime state is the NLS registry linkage and module owner reference managed by `nls_base.c`.

## Dependencies and integration points
The module integrates with Linux filesystems through `struct nls_table`. It is loaded by charset name `"cp1251"` and can be used for on-disk or I/O filename translation. The comments identify the generated Unicode table source, and the module description notes Bulgarian and Belarusian but the table covers the CP1251 Cyrillic repertoire more broadly.

## Risks and test signals
Risks include incorrect Cyrillic case folding, undefined byte handling, and mixups with KOI8 or ISO Cyrillic tables. Because Cyrillic upper/lower pairs span byte ranges, case-table regressions can break case-insensitive lookup. Tests should cover basic Russian Cyrillic letters, Ukrainian/Belarusian-specific letters, punctuation/euro mappings, undefined byte `0x98`, reverse page `0x04`, case folding, module load/unload, and filesystem name round trips.
