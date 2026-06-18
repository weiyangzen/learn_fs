# sources/distributed-fs/ceph-client/fs/jfs/jfs_unicode.c

## Purpose
`jfs_unicode.c` implements filename conversion between JFS's internal UCS-2-ish `wchar_t`/little-endian Unicode names and Linux dentry byte strings using an optional NLS table. It allocates converted component names for lookup/create paths and converts on-disk Unicode names back to user-visible strings.

## Important APIs, types, and functions
Public functions are `jfs_strfromUCS_le()` and `get_UCSname()`. The private helper `jfs_strtoUCS()` converts byte strings to `wchar_t`. The code uses `struct nls_table` callbacks `uni2char()` and `char2uni()`, `struct component_name`, dentry names, `JFS_NAME_MAX`, and the mount's `JFS_SBI(sb)->nls_tab`.

## Control flow
`jfs_strfromUCS_le()` iterates over a little-endian Unicode input until `len` or NUL. With a codepage, it calls `uni2char()` and substitutes `?` on conversion failure. Without a codepage, it accepts only Latin-1 range characters, substitutes `?` for higher values, and rate-limits a warning to five total strings. `get_UCSname()` checks the dentry length, allocates a `wchar_t` buffer with `GFP_NOFS`, calls `jfs_strtoUCS()`, frees the buffer on conversion failure, and leaves `uniName->namlen` set on success.

## State and persistence behavior
The conversion functions do not persist data directly, but their output feeds directory operations and therefore determines on-disk name encoding. Returned UCS names are heap-owned and must be freed with `free_UCSname()`. The static `warn_again` counter persists across calls to limit log spam when mounted without an appropriate charset.

## Dependencies and integration points
The file depends on Linux slab allocation, NLS tables, JFS incore mount options, filesystem name length constants, unicode helpers in `jfs_unicode.h`, and debug logging. Directory lookup, create, rename, and readdir paths use these conversions around directory-tree keys and on-disk names.

## Risks
Without `iocharset`, non-Latin-1 names degrade to `?`, which can make names inaccessible or ambiguous. `jfs_strtoUCS()` returns negative NLS errors directly; callers must stop and free partial state. `get_UCSname()` uses byte length for allocation, which is safe for multibyte-to-UCS conversion when each input sequence produces at most one `wchar_t`, but malformed input can fail mid-string. Conversion behavior depends on the mounted NLS table and must match lookup/readdir symmetrically.

## Test signals
Tests should cover ASCII, Latin-1 without NLS, UTF-8 or other NLS mounts, invalid multibyte sequences, maximum-name boundary, embedded NUL behavior from dentries, high Unicode values warning/substitution, and round-trip lookup/readdir for non-ASCII filenames.
