# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent.h

Declares dirent hash operations, validation/text hooks, lookup/create/rename/readdir APIs, and small helpers.

Key elements:
- `bch2_dirent_hash_desc` is the shared hash descriptor for dirents.
- `bch2_bkey_ops_dirent` wires validation, text formatting, and minimum value size into bkey operations.
- Casefold APIs are declared when Unicode support exists; otherwise `bch2_casefold()` returns `no_casefolding_without_utf8`.
- `bch2_maybe_casefold()` returns the original string for non-casefolded directories or the folded lookup name otherwise.
- `dirent_val_u64s()` computes the value size for normal and casefolded names.
- `dirent_get_by_pos()` initializes a dirents iterator and fetches a typed dirent at an exact position.
- Declares create, read target, rename, lookup, empty-dir, readdir, and fsck removal helpers.
- `vfs_d_type()` maps bcachefs `DT_SUBVOL` to VFS `DT_DIR`.

Filesystem relevance:
- This is the shared namespace API used by VFS operations, fsck, subvolume handling, and inode backpointer repair.
