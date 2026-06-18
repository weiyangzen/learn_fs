# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/xattr.h

This header declares xattr hash descriptors, bkey ops, search helpers, and VFS list/set entry points.

Key elements:
- Exposes `bch2_xattr_hash_desc`.
- Registers xattr bkey operations with validate/to-text handlers and `min_val_size = 8`.
- `xattr_val_u64s()` computes required value u64s from name and value lengths.
- `xattr_val()` returns the value pointer after the name bytes.
- `struct xattr_search_key` and `X_SEARCH()` package type/name lookup keys.
- Declares `bch2_xattr_set()` for use by migration/tools paths, `bch2_xattr_list()`, and the global handler table.

Role:
- Used by VFS xattr code, ACL code, metadata validation, and migration tooling.
