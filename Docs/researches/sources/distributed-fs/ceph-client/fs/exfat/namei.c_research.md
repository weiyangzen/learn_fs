# sources/distributed-fs/ceph-client/fs/exfat/namei.c

## Purpose
`namei.c` implements exFAT VFS namespace operations: dentry hashing/comparison/revalidation, empty directory slot search and directory expansion, path/name conversion for lookup and creation, create, lookup, unlink, mkdir, rmdir, rename, and the directory inode operation table. It connects case-insensitive exFAT naming rules to the Linux dcache and directory-entry machinery in `dir.c`.

## Important APIs, types, and functions
Dentry operations are `exfat_d_revalidate()`, `exfat_d_hash()`, `exfat_d_cmp()`, `exfat_utf8_d_hash()`, `exfat_utf8_d_cmp()`, `exfat_dentry_ops`, and `exfat_utf8_dentry_ops`. Slot and path helpers include `exfat_search_empty_slot()`, `exfat_find_empty_entry()`, `exfat_check_max_dentries()`, `__exfat_resolve_path()`, `exfat_resolve_path()`, `exfat_resolve_path_for_lookup()`, and `exfat_make_i_pos()`.

VFS inode operation implementations are `exfat_create()`, `exfat_lookup()`, `exfat_unlink()`, `exfat_mkdir()`, `exfat_rmdir()`, `exfat_rename()`, plus internal `exfat_add_entry()`, `exfat_find()`, `exfat_check_dir_empty()`, `exfat_rename_file()`, `exfat_move_file()`, and `__exfat_rename()`.

## Control flow
Dentry hashing/comparison strips trailing dots unless `keep_last_dots` is enabled and folds case through `exfat_toupper()`. UTF-8 mounts use UTF-8 decoding directly; NLS mounts use the selected `nls_io` table. Negative dentries store the parent directory version and are invalidated on parent version changes or creation/rename-target lookups.

Create/mkdir call `exfat_add_entry()` under `s_lock`: resolve the VFS name to UTF-16, compute entry count, find or allocate an empty entry set, allocate and zero a first cluster for non-zero-size directories, initialize the file/stream/name dentries, write them synchronously when needed, fill `exfat_dir_entry`, build an inode, set creation timestamps, and instantiate the dentry. `exfat_find_empty_entry()` first consumes `hint_femp`, validates actual empty sets, and grows the directory one cluster at a time when no slot exists.

Lookup resolves the search name in lookup-compatible lossy mode, refreshes directory hints when the parent `i_version` changes, scans with `exfat_find_dir_entry()`, reads file and stream entries into `exfat_dir_entry`, clamps invalid size/valid-size/start-cluster states, counts subdirectories for link count, builds or reuses an inode keyed by on-disk position, and handles dcache aliases.

Unlink/rmdir mark entry sets deleted and clear/unhash inodes; rmdir first verifies no file/dir entries remain and leaves cluster freeing to inode eviction/truncate. Rename resolves the target name, optionally verifies target directory emptiness, either rewrites in place, allocates a larger entry set, or moves to a new parent, then deletes a replaced target's entries and frees replaced directory clusters. It updates inode hashes and link counts after moving directory-entry positions.

## State and persistence behavior
Persistent state includes directory entry sets, directory cluster allocation, directory sizes/valid sizes, FAT/bitmap changes for directory growth and replaced-directory cleanup, and deleted-entry markers. Runtime state includes dentry hashes and negative-dentry version tokens, directory hints, inode hash positions, link counts, inode versions, timestamps, and `DIR_DELETED` markers to suppress later writeback of removed entries.

## Dependencies and integration points
This file depends on `dir.c` entry-set operations and directory scanners, `nls.c` conversion and upcase behavior, `fatent.c` cluster allocation/free/zeroing, inode build/hash/write helpers, VFS dcache/namei APIs, idmapped mount signatures for inode operations, and forced-shutdown state from the superblock.

## Risks and test signals
Risks include case-insensitive dcache alias bugs, trailing-dot compatibility mismatches, stale negative dentries, directory growth without inode writeback, rename partial updates, replacement directory cluster leaks, link-count errors, target/source `DIR_DELETED` races, and lossy-name creation. Tests should cover case-only names, UTF-8 and NLS mounts, trailing-dot options, long names requiring many dentries, directory expansion to max dentry count, create/unlink/mkdir/rmdir/rename under `dirsync`, rename over files and empty directories, hard alias/dcache reuse scenarios, and corrupt target/source dentries.
