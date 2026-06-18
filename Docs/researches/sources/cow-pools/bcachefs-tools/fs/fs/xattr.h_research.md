# File Research: sources/cow-pools/bcachefs-tools/fs/fs/xattr.h

## Purpose
Public xattr header defining bcachefs xattr bkey operations, xattr value layout helpers, search keys, exported transaction setter, list function, and VFS handler array.

## Main Contents
- Declaration of `bch2_xattr_hash_desc`.
- Bkey validation/text declarations and `bch2_bkey_ops_xattr` with minimum value size 8 bytes.
- `xattr_val_u64s()`, computing the number of u64s needed for name+value payload.
- `xattr_val()` macro, returning a pointer to the value bytes after the name.
- `struct xattr_search_key` and `X_SEARCH()` initializer for hash lookups.
- Forward declarations for VFS and bcachefs inode/hash types.
- `bch2_xattr_set()`, exported for both filesystem code and migration tooling.
- `bch2_xattr_list()` and `bch2_xattr_handlers[]`.

## Integration Notes
`xattr.c` implements the hash descriptor and handlers declared here. `acl.c` and migration/tooling paths can call `bch2_xattr_set()` without going through VFS xattr handlers. The value helpers encode the packed `struct bch_xattr` flexible-array layout from `xattr_format.h`.

## Risks and Edge Cases
- `xattr_val()` relies on `x_name_len`; callers must validate bounds before dereferencing arbitrary on-disk values.
- `xattr_val_u64s()` must stay synchronized with `struct bch_xattr` layout.
