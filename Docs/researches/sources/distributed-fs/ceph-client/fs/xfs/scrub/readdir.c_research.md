# sources/distributed-fs/ceph-client/fs/xfs/scrub/readdir.c

## Purpose
`readdir.c` provides scrub-oriented directory iteration, exact directory lookup, and careful lock acquisition for parent-pointer validation. It normalizes shortform, block, leaf, and node directory formats behind one callback API.

## Important APIs, Types, And Functions
Public functions are `xchk_dir_walk`, `xchk_dir_lookup`, and `xchk_dir_trylock_for_pptrs`. Format-specific walkers are `xchk_dir_walk_sf`, `xchk_dir_walk_block`, `xchk_read_leaf_dir_buf`, and `xchk_dir_walk_leaf`. Lock helpers are `xchk_dir_trylock_both` and `xchk_dir_trylock_for_pptrs`.

## Control Flow
`xchk_dir_walk` asserts the target is a locked directory, determines its format with `xfs_dir2_format`, and dispatches. Shortform walking synthesizes `.` and `..` before iterating inline entries. Block walking reads the single block and scans data entries while skipping free regions. Leaf/node walking advances over mapped directory data blocks before `XFS_DIR2_LEAF_OFFSET`, reading buffers as needed and reporting entries.

`xchk_dir_lookup` builds `xfs_da_args` and delegates exact lookup to `xfs_dir_lookup_args`, with special owner handling for temporary repair directories whose block headers are owned by the original scrub target. `xchk_dir_trylock_for_pptrs` repeatedly tries to lock the scrub target and a parent directory without deadlocking on corrupt trees.

## State And Persistence Behavior
The file is read-only except for lock state and transaction buffer references. Buffer reads are released before return. Lock helper state is reflected in `sc->ilock_flags` and returned parent lock modes.

## Dependencies And Integration Points
It depends on XFS directory format internals, scrub transactions, inode locking, and common termination checks. Nlinks, parent, parent repair, and orphanage adoption use these helpers for directory scans and lookups.

## Risks And Edge Cases
The walkers trust callers to hold ILOCK. Leaf walking must handle holes and mapped extents correctly. Buffer cache and verifier errors propagate. Parent-pointer locking intentionally avoids normal two-inode ordering because corrupt trees can create cycles; it can return timeout/incomplete or deadlock retry signals.

## Test Signals
Tests should cover all directory formats, free-space entries, sparse leaf directories, temporary directory lookup owner overrides, shutdown behavior, invalid format errors, and parent-pointer lock contention under `TRY_HARDER`.
