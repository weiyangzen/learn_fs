# sources/distributed-fs/ceph-client/fs/smb/client/readdir.c

## Purpose
`readdir.c` implements CIFS directory enumeration. It starts and resumes SMB FIND searches, parses multiple directory-information wire formats, converts entries to `cifs_fattr`, primes the dcache, emits VFS dirents, and optionally populates cached directory leases.

## Important APIs, types, and functions
The exported entry point is `cifs_readdir()`. Important helpers are `cifs_prime_dcache()`, `cifs_fill_common_info()`, `cifs_posix_to_fattr()`, `cifs_dir_info_to_fattr()`, `cifs_fulldir_info_to_fattr()`, `cifs_std_info_to_fattr()`, `initiate_cifs_search()`, `find_cifs_entry()`, `nxt_dir_entry()`, `cifs_fill_dirent()`, `cifs_entry_is_dot()`, `cifs_filldir()`, and directory-cache helpers `emit_cached_dirents()`, `add_cached_dirent()`, `update_cached_dirents_count()`, and `finished_cached_dirents_count()`. It supports `SMB_FIND_FILE_POSIX_INFO`, `SMB_FIND_FILE_UNIX`, `SMB_FIND_FILE_DIRECTORY_INFO`, `SMB_FIND_FILE_FULL_DIRECTORY_INFO`, `SMB_FIND_FILE_ID_FULL_DIR_INFO`, `SMB_FIND_FILE_BOTH_DIRECTORY_INFO`, and `SMB_FIND_FILE_INFO_STANDARD`.

## Control flow
`cifs_readdir()` builds the full path, tries `open_cached_dir()` and emits cached dirents when a valid directory lease cache exists. Otherwise it starts `query_dir_first()` if needed, emits dot entries, finds the current entry for `ctx->pos`, optionally performs `query_dir_next()` until the target position is in the current buffer, reopens cached-dir tracking, allocates a Unicode scratch buffer, loops entries, converts names and metadata, primes dcache, emits entries, updates resume keys and cache accounting, and closes cached-dir references before returning.

## State and persistence behavior
Search state is stored in `struct cifsFileInfo->srch_inf`: search handle, info level, Unicode flag, network buffer pointers, entries in buffer, last-entry index, resume name/key, empty/end-of-search flags, and invalid handle state. Directory lease cache state is stored in `struct cached_fid->dirents` with position, validity/failure flags, byte and entry accounting, and copied fattrs. Dcache is updated opportunistically through `cifs_prime_dcache()`, but entries that require immediate revalidation, especially reparse points and POSIX special types, may be skipped or marked stale.

## Dependencies and integration points
This file depends on CIFS path construction, server `query_dir_first/query_dir_next/close_dir/calc_smb_size` operations, cached directory support, Unicode/NLS conversion, `inode.c` fattr conversion and inode instantiation, reparse helpers, backup credential detection, server-inode autodisable, VFS `dir_context`, and dcache lookup/splice APIs.

## Risks
The highest risks are malformed server buffer parsing, invalid `NextEntryOffset`, name length exceeding SMB buffer bounds, Unicode conversion errors, stale dcache priming for reparse points, incorrect resume position after suppressed dot entries, cached-dir accounting mismatches, server inode number collisions, and races when directories change between `seekdir`/`readdir` calls.

## Test signals
Test readdir on empty directories, large directories spanning many FIND buffers, lseek rewind and forward seek, directories changing during enumeration, cached directory lease hits and failures, Unicode and long filenames, malformed or fuzzed FIND buffers, all supported info levels, server-inode enabled/disabled fallback, POSIX special/reparse entries, MF symlink candidates, backup-credential searches, and servers that omit or return late dot entries.
