## sources/distributed-fs/orangefs/src/client/usrint/recursive-remove.c

Purpose: Provides recursive directory removal for OrangeFS paths by deleting non-directory entries first, recursing into directories, then removing the now-empty directory.

Important APIs, types, and functions: `recursive_delete_dir(char *dir)` opens, scans, rewinds, recurses, closes, and `rmdir`s a directory. `remove_files_in_dir(char *dir, DIR *dirp)` scans an already-open stream and unlinks non-directories. Both rely on `PINT_merge_paths`, `PINT_is_dot_dir`, and `pvfs_lstat_mask(..., PVFS_ATTR_SYS_TYPE)`.

Control flow: `recursive_delete_dir` opens `dir`, calls `remove_files_in_dir` to unlink files and links, rewinds the stream, walks remaining entries, skips dot entries, builds absolute child paths, stats type, recurses into directories, closes the stream, then calls `rmdir(dir)`. `remove_files_in_dir` rewinds and loops with `readdir`, skipping directories and unlinking everything else.

State and persistence: This code permanently mutates the filesystem by unlinking entries and removing directories. It holds only stack buffers and one `DIR *` at a time per recursion depth.

Dependencies and integration points: Includes usrint POSIX wrappers (`opendir`, `readdir`, `unlink`, `rmdir`) and OrangeFS stat helpers. Debug/error output comes from `recursive-remove.h` macros.

Risks and test signals: Early returns leak `DIR *` because failure paths do not `closedir`. Directory contents can change between the file pass and directory pass. Root removal intentionally removes contents then fails on removing `/`. Fixed `PVFS_PATH_MAX + 1` buffers depend on `PINT_merge_paths` bounds. Test empty trees, mixed files/dirs/symlinks, permission failures, concurrent mutation, root path behavior, long child names, and cleanup after mid-recursion errors.
