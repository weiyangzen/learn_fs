# sources/distributed-fs/ceph-client/fs/ufs/dir.c

## Purpose
`dir.c` implements UFS directory pagecache handling, validation, lookup, add/delete/set-link operations, `.`/`..` initialization, emptiness checks, readdir, and directory file operations.

## Important APIs, types, and functions
Public functions include `ufs_inode_by_name`, `ufs_set_link`, `ufs_dotdot`, `ufs_find_entry`, `ufs_add_link`, `ufs_delete_entry`, `ufs_make_empty`, and `ufs_empty_dir`. Exported `ufs_dir_operations` supplies open/release/read/iterate/fsync/llseek/setlease. Important internals are `ufs_match`, `ufs_commit_chunk`, `ufs_handle_dirsync`, `ufs_check_folio`, `ufs_get_folio`, `ufs_last_byte`, `ufs_next_entry`, `ufs_validate_entry`, and `ufs_readdir`.

## Control flow
Directory reads map folios through `ufs_get_folio`, validate record lengths, alignment, chunk boundaries, names, and inode ranges once per folio, then iterate records. Lookup begins at a cached page index and wraps around. Adding a link scans existing and one-past-end folios, splits reusable records when needed, prepares block-backed chunks, writes the new dirent, commits size/version changes, updates times, and syncs if required. Deletion merges with the previous record when possible and clears the inode number. Readdir revalidates offsets after directory version changes.

## State and persistence
Persistent state includes directory entry records, `d_ino`, record lengths, name length/type fields, directory size, ctime/mtime, and block contents. Runtime state includes folio checked bits, per-open i_version cookie, and `i_dir_start_lookup`.

## Dependencies and integration points
It depends on `ufs_prepare_chunk` from `inode.c`, endian/name helpers in `util.h`, VFS folio and dir_context APIs, and namei operations in `ufs/namei.c`.

## Risks and test signals
Risks include accepting corrupt directories, record splitting/merging bugs, offset revalidation errors after mutation, missing kmap release on error paths, and old versus 4.4BSD dirent format differences. Test signals include fsck-corrupted dirents, create/delete/rename loops, readdir during mutation, directory sync mounts, max-length names, old UFS dir format and 44BSD d_type format.
