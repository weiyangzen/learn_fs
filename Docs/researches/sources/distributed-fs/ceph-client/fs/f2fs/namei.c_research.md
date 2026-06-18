# sources/distributed-fs/ceph-client/fs/f2fs/namei.c

## Purpose

`namei.c` implements F2FS VFS namespace operations: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, tmpfile, whiteout creation, rename, exchange rename, parent lookup, and inode operation tables. It is the bridge between Linux VFS dentries/inodes and F2FS directory entry, inode allocation, quota, encryption, compression, inline-data, project-quota, orphan, and checkpoint semantics.

## Important APIs and functions

- `f2fs_update_extension_list()` mutates cold/hot extension lists in the raw superblock, preserving ordering between cold and hot extension ranges.
- `set_compress_new_inode()` and `set_file_temperature()` derive new-inode compression and hot/cold file hints from mount options, inherited directory flags, and raw-super extension lists.
- `f2fs_new_inode()` allocates a VFS inode and F2FS nid, initializes ownership, timestamps, generation, project id, encryption state, quota state, inline/xattr flags, compression state, extent tree, and inode flags.
- Namespace creation functions `f2fs_create()`, `f2fs_mkdir()`, `f2fs_mknod()`, `f2fs_symlink()`, and `f2fs_tmpfile()` allocate or initialize inodes and add directory links or orphan/tmpfile state under `f2fs_lock_op()`.
- Lookup and ancestry functions `f2fs_lookup()` and `f2fs_get_parent()` resolve directory entries through F2FS dir helpers and return VFS dentries/aliases.
- Removal and movement functions `f2fs_unlink()`, `f2fs_rmdir()`, `f2fs_rename()`, `f2fs_cross_rename()`, and `f2fs_rename2()` update directory entries, link counts, parent inode numbers, orphan state, whiteouts, and strict-fsync transaction inode tracking.
- Operation tables `f2fs_dir_inode_operations`, `f2fs_symlink_inode_operations`, `f2fs_encrypted_symlink_inode_operations`, and `f2fs_special_inode_operations` register these functions with VFS.

## Control flow and state

Creation paths first reject checkpoint errors and, except mkdir, require checkpoint readiness. They initialize directory quotas, allocate a nid through `f2fs_new_inode()`, assign operation tables and address-space operations, then take the F2FS operation lock and call `f2fs_add_link()`. On success they call `f2fs_alloc_nid_done()`, instantiate the dentry, optionally sync for `dirsync`, and balance the filesystem. On failure after inode allocation, they call `f2fs_handle_failed_inode()`, which must unwind nid, quota, orphan, and inode state while releasing the operation lock context.

`f2fs_new_inode()` is the central initialization funnel. It sets `FI_NEW_INODE`, optional encryption, `FI_EXTRA_ATTR`, inline xattr/dentry/data eligibility, project-inherit flags, compression context, hot/cold file temperature, inode flags, and extent tree state before returning a locked new inode. Failure before insertion calls `make_bad_inode()` and sets `FI_FREE_NID` when a nid was reserved; failure after insertion drops quota, clears nlink, unlocks, and iputs.

Lookup prepares encrypted/casefolded filenames, searches the directory, reads the target inode, rejects zero-link corruption, validates encrypted context compatibility for encrypted directories, and returns `d_splice_alias()`. For Unicode casefolded negative dentries it returns `NULL` to avoid caching a negative dentry that VFS cannot yet safely represent.

Unlink validates quota, finds the entry, rejects zero-link corruption and one-link directory corruption, acquires orphan capacity, deletes the entry, invalidates casefolded dentries, and optionally syncs. Rmdir delegates to unlink only after `f2fs_empty_dir()`.

Rename has two flows. Normal rename handles optional `RENAME_WHITEOUT`, existing-target replacement, parent directory `..` updates, link-count adjustments, orphan accounting for overwritten targets, old-entry deletion, whiteout insertion, strict fsync tracking, and dirsync. Cross rename swaps two existing dentries and, when directories move across parents, swaps their `..` entries and adjusts parent link counts. `f2fs_rename2()` validates flags, runs fscrypt preparation, and dispatches to normal or exchange rename.

## Persistence behavior

The file changes persistent state through inode allocation, NAT/SIT-visible node creation via lower layers, directory entry insertion/deletion, raw superblock extension list mutation, inode flags, link counts, parent inode numbers, inline/compression metadata, symlink data pages, orphan lists, and checkpoint-triggered syncs. It also marks inodes dirty and records transaction directory inode numbers in strict fsync mode to support crash recovery.

Tmpfiles and whiteouts are notable persistence cases. `__f2fs_tmpfile()` creates a non-linked inode, reserves orphan capacity, calls `f2fs_do_tmpfile()`, adds the inode to the orphan list so unused data can be reclaimed after power loss, and marks whiteout tmpfiles linkable for later rename-whiteout insertion.

## Dependencies and integration points

`namei.c` depends on VFS dentry/inode APIs, fscrypt, quota, idmapped ownership, project quota, folios, and F2FS subsystems in `f2fs.h`, `node.h`, `segment.h`, `xattr.h`, and `acl.h`. It integrates with directory helpers such as `f2fs_add_link()`, `f2fs_find_entry()`, `f2fs_delete_entry()`, `f2fs_set_link()`, and filename preparation/freeing. It relies on node-manager nid allocation from `node.c` and on recovery semantics in `recovery.c` for fsync marks, dentry marks, orphan recovery, and strict rename durability.

## Risks and edge cases

- Extension-list mutation writes raw superblock fields in memory; callers must hold the appropriate superblock lock externally when required. Duplicate checks are asymmetric between hot and cold ranges and should be tested carefully.
- Inode allocation has many staged failure paths; missing `FI_FREE_NID`, `clear_nlink()`, quota drop, or `unlock_new_inode()` in a new path can leak nids or expose bad inodes.
- Casefolded negative dentry behavior intentionally avoids caching; changes in VFS support could require revisiting lookup/unlink invalidation.
- Rename-whiteout has a narrow failure window after old-entry deletion and before whiteout link insertion where it invalidates both dentries and exits through shared cleanup.
- Link-count and parent `i_pino` updates must stay consistent for fsck, especially in cross-directory directory renames and exchange renames.
- Symlink creation instantiates the dentry even when writing encrypted/page symlink data fails, then unlinks to unwind; tests should inspect this rollback path.

## Test signals

Important coverage includes create/link/unlink/mkdir/rmdir/mknod/symlink/tmpfile under normal, encrypted, casefolded, inline dentry, inline data, project quota, and compression configurations. Rename tests should cover no-replace, replace-file, replace-directory-empty/non-empty, exchange file-directory across parents, whiteout, strict fsync mode, dirsync parents, and project-id mismatches. Fault injection should target nid allocation, quota initialization, `f2fs_add_link()`, orphan acquisition, encrypted symlink allocation/encryption, and ENOMEM loops in dentry recovery-adjacent paths. Fsck-oriented tests should validate detection of zero-link lookup/unlink corruption and bad directory link counts.
