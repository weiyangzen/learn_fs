# sources/distributed-fs/ceph-client/fs/nls/nls_cp1255.c

## Purpose
`nls_cp1255.c` implements the Windows CP1255 Hebrew NLS table and also exposes an alias for `iso8859-8`. It maps Hebrew letters, Hebrew points/punctuation, and CP1255 symbols to Unicode and provides exact reverse mappings for filesystem charset conversion.

## Important APIs, types, and functions
`charset2uni[256]` maps bytes to Unicode. The high range includes euro and typographic punctuation, Hebrew sheqel sign, Hebrew vowel points in `0x05b0` and related ranges, Hebrew punctuation and ligatures around `0x05f0`, and Hebrew letters `0x05d0` through `0x05ea`. Several bytes are undefined and map to `0x0000`. Reverse mapping uses `page00`, `page01`, `page02`, `page05`, `page20`, and `page21`.

`uni2char()` and `char2uni()` are the conversion callbacks. `charset2lower` and `charset2upper` are effectively identity-like for Hebrew because Hebrew has no upper/lower case, while preserving ASCII case behavior. `table` registers `.charset = "cp1255"` and `.alias = "iso8859-8"`. The file also declares `MODULE_ALIAS_NLS(iso8859-8)` so module autoload can satisfy alias requests. `init_nls_cp1255()` and `exit_nls_cp1255()` manage registration.

## Control flow
Module initialization registers the table. `find_nls()` in `nls_base.c` can match either `"cp1255"` or the alias `"iso8859-8"` and pin the module. Conversion itself is a one-byte lookup. `char2uni()` rejects undefined bytes; `uni2char()` rejects missing reverse pages, zero reverse entries, or insufficient output buffer length.

## State and persistence behavior
The module has immutable static tables and no local mutable state. Alias and charset names are fields in the registered table. Persistence is external to filesystems storing bytes; this module supplies interpretation only while loaded and referenced.

## Dependencies and integration points
It depends on the NLS registry and module alias machinery. Integration points include filesystem charset options that request either CP1255 or ISO-8859-8 naming. The alias behavior is notable because lookup by alias is handled by `nls_base.c` before or after module autoload.

## Risks and test signals
Alias behavior is the unique risk compared with most generated one-byte modules: both `cp1255` and `iso8859-8` requests should resolve to the same table, and autoload metadata must match. Mapping risk includes undefined Hebrew-point positions, sheqel/euro/punctuation mappings, and right-to-left filename test coverage at higher layers. Tests should cover Hebrew letters and vowel points, undefined byte rejection, reverse page `0x05`, alias loading by `iso8859-8`, ASCII case behavior, module unload after both names, and filesystem filename round trips using Hebrew strings.
