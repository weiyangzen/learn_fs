# sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.h

## Purpose
`jfs_unicode.h` declares filename conversion APIs and provides inline Unicode string utilities for JFS directory names. It bridges JFS component names, little-endian on-disk Unicode arrays, Linux NLS conversion, and uppercase comparisons.

## Important APIs, types, and functions
The header declares `get_UCSname()` and `jfs_strfromUCS_le()`, defines `free_UCSname()`, and provides inline `UniStrcpy()`, `UniStrncpy_le()`, `UniStrncmp_le()`, `UniStrncpy_to_le()`, `UniStrncpy_from_le()`, `UniToupper()`, and `UniStrupr()`. It uses `NlsUniUpperTable` and `NlsUniUpperRange` from the local NLS UCS-2 data.

## Control flow
Callers allocate component names through `get_UCSname()`, free them with `free_UCSname()`, copy names to or from little-endian disk arrays with the `UniStrncpy_*` helpers, compare native and little-endian names with `UniStrncmp_le()`, and uppercase names in place with `UniStrupr()` for case-insensitive behavior where needed.

## State and persistence behavior
The string helpers operate in caller-provided buffers and do not allocate except through the declared C implementation. The little-endian copy helpers are persistence-sensitive because they write on-disk directory/name fields. `UniToupper()` is table-driven and returns the input unchanged when no uppercase mapping is found.

## Dependencies and integration points
The header depends on slab allocation, byteorder helpers, `nls_ucs2_data.h`, and `jfs_types.h`. It is used by directory and name-handling code as well as `jfs_unicode.c`.

## Risks
The copy helpers assume destination buffers are large enough for `n` entries and always pad with NULs after source termination. `UniStrncmp_le()` compares native `wchar_t` to little-endian `__le16`, so wrong pointer types can produce incorrect ordering. Uppercase mapping is limited to the included UCS-2 tables and may not match full modern Unicode case folding.

## Test signals
Tests should validate bounded copies with padding, endian conversions, comparisons at equal/prefix/different names, uppercase conversion for table and range entries, and directory lookup behavior on case-sensitive and non-ASCII names.
