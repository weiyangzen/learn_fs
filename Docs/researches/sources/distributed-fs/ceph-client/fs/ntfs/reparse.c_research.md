# sources/distributed-fs/ceph-client/fs/ntfs/reparse.c

## Purpose
`reparse.c` handles NTFS reparse point validation, type interpretation, `$Extend/$Reparse` index updates, WSL symlink target extraction, and creation of WSL reparse data for symlinks and special files.

## Important APIs and Types
It defines `reparse_index_name` as `$R`, WSL link payload structure, packed reparse index entry, and exports `ntfs_make_symlink()`, `ntfs_reparse_tag_dt_types()`, `ntfs_delete_reparse_index()`, `ntfs_reparse_set_wsl_symlink()`, and `ntfs_reparse_set_wsl_not_symlink()`. The header also declares `ntfs_remove_ntfs_reparse_data()`, but no implementation appears in this file.

## Control Flow and State
Validation checks total buffer size against `reparse_data_length`, rejects reserved zero tags, accounts for non-Microsoft GUID headers, verifies WSL symlink type `2`, and requires recall-on-open for WSL special-file tags. `ntfs_make_symlink()` reads `AT_REPARSE_POINT`, validates it, maps tags to Unix file types, and for LX symlinks allocates `ni->target` from the stored byte link. Directory-entry type probing opens the inode by MFT reference and maps known tags to `DT_*`.

Index maintenance opens `$Extend/$Reparse` by Unicode lookup, obtains `$R`, and uses `(reparse_tag, file_id)` as key. Setting reparse data creates `AT_REPARSE_POINT` if needed, sets `FILE_ATTR_REPARSE_POINT`, removes old index entries, overwrites the attribute, adds the new index entry, and dirties affected MFT records. Deletion removes the index entry, clears the reparse flag, marks filename dirty, and dirties the inode record.

## Dependencies and Integration
`namei.c` calls WSL setters during symlink and special-file creation and calls deletion during final unlink. The code depends on attribute read/write/add/remove, index APIs, MFT dirtying, Unicode conversion, `$Extend` lookup, and NTFS layout tag definitions.

## Risks
The missing implementation for `ntfs_remove_ntfs_reparse_data()` is a stale declaration/build risk if referenced. If index insertion fails after writing data, the code attempts to remove the attribute but can leave inconsistency. Validation accepts only a subset of tags. `ntfs_reparse_tag_dt_types()` returns `PTR_ERR()` as unsigned int on `ntfs_iget()` failure, which can look like a large directory type value. Some flag handling assigns `ni->flags` rather than ORing in create paths outside this file.

## Test Signals
Test valid/invalid WSL symlink buffers, AF_UNIX/FIFO/CHR/BLK tags, missing `$Reparse`, index add/remove failures, reparse replacement, deletion clearing flags and filename dirty state, directory `DT_*` reporting, and link-target lifetime through `ni->target`.
