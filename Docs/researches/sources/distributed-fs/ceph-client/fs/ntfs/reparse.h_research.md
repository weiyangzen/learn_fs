# sources/distributed-fs/ceph-client/fs/ntfs/reparse.h

## Purpose
`reparse.h` exposes NTFS reparse point operations used by inode setup, namespace deletion, and directory type reporting.

## Important APIs
The header declares `reparse_index_name[]`, `ntfs_make_symlink()`, `ntfs_reparse_tag_dt_types()`, `ntfs_reparse_set_wsl_symlink()`, `ntfs_reparse_set_wsl_not_symlink()`, `ntfs_delete_reparse_index()`, and `ntfs_remove_ntfs_reparse_data()`.

## Control Flow and State
The API separates reading/interpreting reparse data, writing WSL reparse data, and removing index state. Callers are expected to pass NTFS inodes with appropriate MFT/attribute state and to persist dirty records after changes.

## Dependencies and Integration
`namei.c` uses the setters for new symlinks and special files and `ntfs_delete_reparse_index()` during deletion. Directory code can use `ntfs_reparse_tag_dt_types()` for dirent type mapping.

## Risks
`ntfs_remove_ntfs_reparse_data()` is declared but not found in the paired implementation, making it a stale or missing symbol risk. The header relies on externally visible `struct ntfs_inode` and `struct ntfs_volume` declarations.

## Test Signals
Build/link tests should ensure every declaration has an implementation or no references. VFS tests should cover symlink and special-file creation and deletion through this interface.
