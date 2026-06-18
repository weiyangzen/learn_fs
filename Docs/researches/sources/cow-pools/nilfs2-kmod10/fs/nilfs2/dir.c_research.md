# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dir.c

Directory entry implementation, derived from ext2-style directory handling and adapted for NILFS page/folio and transaction helpers.

Key behavior:
- Converts directory record lengths between disk and memory, including large page-size handling.
- Validates directory folios for record length, alignment, name length, block-boundary crossing, and private inode numbers.
- Reads directory entries via `nilfs_readdir`.
- Finds entries by name with a cached start folio in `i_dir_start_lookup`.
- Reads `".."`, resolves inode numbers by name, and updates existing links.
- Adds links by finding deleted/expandable records or extending the directory.
- Deletes entries by merging record length into the previous entry.
- Creates empty directories with `"."` and `".."`.
- Checks whether a directory is empty for rmdir.
- Exports `nilfs_dir_operations`.

Integration: writes are routed through `nilfs_prepare_chunk`, `nilfs_commit_chunk`, `nilfs_get_block`, `nilfs_set_file_dirty`, and inode dirty/ctime/mtime updates.

Risk/notes: directory corruption is surfaced with `nilfs_error` and `-EIO`. The code relies on folio kmap lifetime correctness; several paths pass adjusted pointers to `folio_release_kmap`, making pointer handling worth testing carefully.
