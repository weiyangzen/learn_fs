# File Research: sources/cow-pools/bcachefs-tools/fs/fs/dirent.h

## Purpose

Declares dirent hash, validation, creation, lookup, rename, readdir, empty-directory, initialization, and fsck removal APIs.

## Main Interfaces

- `bch2_bkey_ops_dirent` defines key validation, text formatting, and minimum value size.
- Casefold helper `bch2_maybe_casefold()` returns original name when no casefold encoding is configured or calls `bch2_casefold()`.
- `dirent_val_u64s()` computes packed value size for plain or casefolded names.
- `dirent_get_by_pos()` fetches a typed dirent at an exact btree position.
- `vfs_d_type()` maps `DT_SUBVOL` to `DT_DIR` for userspace.
- `enum bch_rename_mode`: normal rename, overwrite, exchange.

## Dependencies

Includes `str_hash.h` and forward-declares VFS and bcachefs structs used by the implementation.

## Notes

The header exposes both core metadata operations and the readdir/sysfs-adjacent filldir specialization status hook.
