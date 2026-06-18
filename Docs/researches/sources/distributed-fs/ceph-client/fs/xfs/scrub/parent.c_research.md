# sources/distributed-fs/ceph-client/fs/xfs/scrub/parent.c

## Purpose
`parent.c` validates parent relationships. Without parent pointers, it verifies a directory's `..` entry and the alleged parent directory's forward link. With parent pointers, it validates each parent-pointer xattr against a directory entry, checks dotdot consistency for directories, and compares parent-pointer counts with link counts.

## Important APIs, Types, And Functions
`xchk_setup_parent` and `xchk_parent` are public. Traditional validation uses `xchk_parent_validate`, `xchk_parent_actor`, and `xchk_parent_ilock_dir`. Parent-pointer validation uses `struct xchk_pptr`, `struct xchk_pptrs`, `xchk_parent_scan_attr`, `xchk_parent_dirent`, `xchk_parent_iget`, `xchk_parent_finish_slow_pptrs`, `xchk_parent_pptr_and_dotdot`, and `xchk_parent_count_pptrs`. `xchk_pptr_looks_zapped` identifies attr forks that repair intentionally cleared and that should defer parent-pointer checks.

## Control Flow
Setup optionally prepares parent repair state, then sets up inode contents scrub. On parent-pointer filesystems, scrub allocates scratch `xfarray` and `xfblob` storage for deferred parent pointers. It walks the target's xattrs; each parent pointer is decoded, checked for self-reference, and resolved to a parent directory. If locks can be acquired immediately, it looks up the named child in the parent. If not, it stores the record and name for a slow pass that can cycle locks and revalidate the xattr.

For directories, it also looks up `..` and ensures it matches one of the parent pointers unless the directory is a root or currently unlinked. It then counts parent pointers and compares them to link-count expectations. Without parent pointers, the code loops on `..` lookup and parent validation, retrying when lock ordering required revalidation.

## State And Persistence Behavior
Scrub is read-only. It records only transient deferred parent-pointer names and records in xfile-backed structures, sets scrub corruption/xref/incomplete flags, and releases all scratch state at exit.

## Dependencies And Integration Points
It depends on directory walking and lookup helpers, xattr walking, parent-pointer decoding, xfarray/xfblob, temporary-file detection, and repair setup in `parent_repair.c`. It integrates with directory and xattr scrub health by deferring if those structures look zapped.

## Risks And Edge Cases
Key edge cases include root and metadata root self-parenting, unlinked directories with meaningless dotdot, parent inodes that are missing or not directories, generation mismatches, metadata/non-metadata tree crossing, lock contention requiring slow revalidation, hardlinked non-directories, and superblock-rooted metadata inodes without ordinary parent xattrs.

## Test Signals
Tests should cover corrupt dotdot, parent pointer with missing forward dirent, wrong parent generation, multiple parent pointers on directories, non-directory hardlinks, zapped attr fork deferral, VFS lock contention, and parent pointers crossing metadata tree boundaries.
