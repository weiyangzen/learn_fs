# sources/distributed-fs/ceph-client/fs/nls/mac-greek.c

## Purpose
`mac-greek.c` implements the Linux NLS module for the classic Macintosh Greek single-byte code page. It translates between 8-bit on-disk or user-facing bytes and Unicode `wchar_t` code points for filesystems that select the `macgreek` charset. The file is almost entirely generated lookup data plus the standard NLS adapter functions and module registration hooks.

## Important APIs, types, and functions
The core data is `charset2uni[256]`, which maps each byte value to Unicode. The upper half includes Greek capital and lowercase letters, Greek tonos/dialytika variants, mathematical symbols, punctuation, `0x20ac`, and compatibility characters; zero entries mark unmappable bytes. Reverse conversion uses page tables `page00`, `page01`, `page03`, `page20`, `page21`, and `page22`, referenced through `page_uni2charset[256]` by Unicode high byte.

`uni2char()` validates `boundlen`, selects the relevant page table from the Unicode high byte, and returns either one output byte or `-EINVAL`/`-ENAMETOOLONG`. `char2uni()` indexes `charset2uni` and rejects mappings whose result is `0x0000`. `charset2lower` and `charset2upper` provide byte-level case folding for consumers using `nls_tolower()`/`nls_toupper()`. `table` is a `struct nls_table` with `.charset = "macgreek"`, the conversion callbacks, and case tables. `init_nls_macgreek()` and `exit_nls_macgreek()` register and unregister the table.

## Control flow
Module load calls `register_nls(&table)` from `init_nls_macgreek()`. Filesystem code later resolves `"macgreek"` through `load_nls()` in `nls_base.c` and calls the table callbacks. Byte-to-Unicode conversion is direct: the input byte indexes `charset2uni`, and a zero Unicode result is treated as invalid. Unicode-to-byte conversion splits the `wchar_t` into high and low bytes, uses the high byte to find a reverse page, then uses the low byte to fetch the output byte. The reverse page value `0x00` is also treated as unmapped, so Unicode NUL is not convertible through this table.

## State and persistence behavior
The module has no persistent or mutable runtime data beyond the `struct nls_table` linkage maintained by the NLS registry. All translation tables are `static const`; conversion calls are stateless and deterministic. Loading pins the module through the registry owner reference, and unloading removes the table from the global list.

## Dependencies and integration points
This file depends on Linux module, kernel, string, errno, and NLS headers. It integrates with the common NLS registry provided by `nls_base.c` and with filesystem clients such as FAT/VFAT that translate filenames through `struct nls_table`. The Unicode data license block indicates generated source from Unicode charset tables, so regeneration must preserve exact mapping semantics and license text.

## Risks and test signals
The main risks are table accuracy, especially for Greek-specific bytes, reverse mapping collisions, and the convention that `0x0000`/`0x00` means invalid rather than a valid NUL mapping. Case-folding tables must match Macintosh Greek expectations or case-insensitive filename lookup can regress. Useful tests load `nls_macgreek`, round-trip representative Greek letters and accented forms, verify invalid bytes or missing Unicode mappings return `-EINVAL`, confirm `boundlen == 0` returns `-ENAMETOOLONG`, and exercise case-insensitive VFAT lookup using Greek names.
