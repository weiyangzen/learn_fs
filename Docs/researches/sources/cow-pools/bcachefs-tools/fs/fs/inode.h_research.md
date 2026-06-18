# File Research: sources/cow-pools/bcachefs-tools/fs/fs/inode.h

## Purpose
Public inode helper header for bcachefs. It declares inode bkey validation/text/trigger operations, the normalized in-memory inode representation, inode lookup/write/create/remove helpers, inode option helpers, link-count helpers, and snapshot/subvolume identity utilities.

## Main Contents
- Bkey operation descriptors for `KEY_TYPE_inode`, `KEY_TYPE_inode_v2`, `KEY_TYPE_inode_v3`, inode generation keys, and inode allocation cursor keys.
- `struct bch_inode_unpacked`, the canonical unpacked inode view with inode number, snapshot, journal sequence, hash seed, size, sectors, version, flags, mode, and all v3 variable fields.
- `struct bkey_inode_buf`, a padded buffer large enough to pack an unpacked inode into a v3 key.
- Pack/unpack and format conversion declarations: `bch2_inode_pack()`, `bch2_inode_unpack()`, and `bch2_inode_to_v3()`.
- Lookup helpers that distinguish snapshot-specific lookup, subvolume-aware lookup, and nowarn variants.
- Inode write, fsck write, initialization, creation, removal, snapshot removal, and dead-inode cleanup declarations.
- Inline helpers for inode options, `d_type` derivation, format-specific flags/mode extraction, casefold inheritance, backpointer presence, biased nlink encoding, and root subvolume inum constants.

## Integration Notes
This header is a central dependency for namespace, xattr, quota, fsck, snapshot, and reconcile code. `namei.c` mutates `bch_inode_unpacked` values for create/link/unlink/rename; `str_hash.c` uses inode hash seed/type/casefold state; `quota.h` derives quota ids from uid/gid/project fields; `xattr.c` exposes inode options through synthetic xattrs. The link-count helpers encode bcachefs' on-disk convention where stored `bi_nlink` is biased by file type and `BCH_INODE_unlinked` represents zero visible links.

## Risks and Edge Cases
- Inode options use a +1 bias: zero means "inherit/default". Callers must use the provided helpers or can accidentally confuse unset with explicit value zero.
- `bch2_inode_nlink_set()` and `bch2_inode_nlink_get()` rely on mode-derived bias; changing mode and nlink ordering incorrectly can corrupt visible link counts.
- Snapshot-aware inode lookup is subtle: some helpers use subvolume snapshots while others accept explicit snapshot ids.
