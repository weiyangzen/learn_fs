# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-gfid-path.c

## Purpose
`posix-gfid-path.c` implements the POSIX translator side of the virtual gfid-to-path xattr. It identifies internal gfid2path xattrs and resolves stored parent-GFID/basename records into paths returned through `GFID2PATH_VIRT_XATTR_KEY`.

## Important APIs, Types, And Functions
- `posix_is_gfid2path_xattr()` checks for `GFID2PATH_XATTR_KEY_PREFIX`.
- `posix_get_gfid2path()` resolves directory GFIDs directly or scans file xattrs, resolves each parent GFID plus basename, joins paths with `priv->gfid2path_sep`, and stores the result in a dict.
- Uses `MAX_GFID2PATH_LINK_SUP`, `sys_llistxattr()`, `sys_lgetxattr()`, `posix_resolve_dirgfid_to_path()`, and dict dynamic ownership helpers.

## Control Flow
Directories are resolved directly from inode GFID. Non-directories list backend xattrs, retry with exact allocation on `ERANGE`, filter gfid2path keys, fetch values, parse the first 36 bytes as a parent GFID string and offset 37 as basename, resolve each path, and concatenate results. Missing gfid2path metadata returns `ENODATA`.

## State And Persistence Behavior
The file reads persistent xattrs created by entry ops. It synthesizes a virtual xattr response and does not persist new state. It transfers allocated path/value buffers to dict ownership on success and frees temporary allocations on failure.

## Dependencies And Integration Points
Entry operations create/remove the gfid2path records this file consumes. Xattr fill paths call this code when clients request the virtual xattr. It depends on `struct posix_private` for base path and separator state.

## Risks And Edge Cases
The `paths` array has `MAX_GFID2PATH_LINK_SUP` slots but the scan lacks an obvious bounds check before incrementing `i`. Malformed or truncated xattr values can break parent GFID/basename parsing. Large xattr sets rely on the ERANGE fallback. `dict_set_dynptr()` length handling must match caller expectations for NUL-terminated data.

## Test Signals
Cover directory resolution, single and multiple hardlink paths, missing xattrs, unsupported xattrs, ERANGE list fallback, malformed values, custom separators, and records beyond the 500-link support limit.
