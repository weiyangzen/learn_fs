# sources/distributed-fs/ceph-client/fs/smb/client/unc.c

Read coverage: full file.

## Purpose
`unc.c` provides small helpers for parsing SMB UNC paths into hostname and sharename pieces. These helpers normalize the parts needed by mount/session/tree-connect setup code after UNC delimiters have already been reduced to backslashes.

## Important APIs, types, and functions
`extract_hostname(const char *unc)` validates that the UNC string is long enough, skips leading backslashes, finds the delimiter before the share name, allocates a new NUL-terminated host substring with `kmalloc`, and returns either the allocated string or an `ERR_PTR`.

`extract_sharename(const char *unc)` assumes the UNC starts with two leading characters, finds the next backslash, duplicates the remainder after that delimiter with `kstrdup`, and returns the allocated sharename path or an `ERR_PTR`.

## Control flow
The hostname path rejects too-short strings, all-backslash strings, and strings without a host/share delimiter. It copies only bytes before the delimiter. The sharename path skips the first two characters, locates the delimiter after the host, advances one byte, and duplicates everything after it. Both functions use kernel allocation with `GFP_KERNEL`.

## State and persistence behavior
No global state is changed. The only state produced is caller-owned heap memory that must be freed by the caller. Errors are encoded as `ERR_PTR(-EINVAL)` or `ERR_PTR(-ENOMEM)`.

## Dependencies and integration points
The file includes kernel fs, slab, inet, and ctype headers plus CIFS globals/prototypes. It integrates with mount and connection setup paths that need a server name for socket/session lookup and a share component for tree connect.

## Risks and test signals
`extract_sharename` assumes at least two leading characters and does not repeat the length/all-backslash validation used by `extract_hostname`; callers must pass canonical UNC input. Neither helper handles forward slashes or alternate delimiters. Test cases should cover `\\server\\share`, paths with subdirectories after the share, missing share delimiters, empty host, too-short strings, allocation failure injection, and caller freeing behavior.
