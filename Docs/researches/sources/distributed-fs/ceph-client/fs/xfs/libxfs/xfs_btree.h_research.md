# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree.h

## Purpose
This header defines the generic btree ABI used by XFS btree implementations and the shared core in `xfs_btree.c`.  It provides disk-format wrapper unions for keys, records, and pointers; the operation vector that concrete btrees must implement; cursor state; geometry flags; exported core APIs; and inline helpers for key comparisons, cursor allocation, root detection, record counts, and pointer state.

## Important APIs, Types, And Functions
`union xfs_btree_ptr`, `union xfs_btree_key`, `union xfs_btree_rec`, and `union xfs_btree_irec` unify concrete allocbt, inobt, bmbt, rmapbt, and refcountbt formats.  `struct xfs_btree_ops` supplies tree name/type, geometry flags, key/pointer/record sizes, stats and health metadata, cursor hooks, root setter, allocation/free callbacks, min/max record callbacks, key/record initialization, comparison functions, contiguity checks, verifier ops, and optional inode-root reallocation.

`struct xfs_btree_cur` stores transaction and mount pointers, ops, current record, height limits, group reference, root-specific inode/AG/memory state, per-tree private accounting, and a flexible array of per-level `struct xfs_btree_level` slots.  Flags include `XFS_BTREE_STAGING`, bmap conversion/owner flags, and allocbt active state.

## Control Flow And State
Callers allocate cursors with `xfs_btree_alloc_cursor`, populate type-specific state, then call core functions.  The cursor levels array tracks one buffer and 1-based entry pointer per tree level.  For inode-rooted btrees, `xfs_btree_at_iroot` identifies the root level as an in-inode block instead of a buffer.  For staged rebuilds, the cursor redirects AG or inode root state to fake-root structures.

## Dependencies And Integration Points
The header forward-declares major XFS structures and integrates with buffer verifiers, transaction logging, health reporting, concrete btree cursor caches, memory btrees, and online repair staging.

## Risks And Test Signals
The main risk is contract mismatch between a concrete btree's ops and generic core assumptions: wrong key length, pointer length, comparison semantics, min/max geometry, root reallocation size, or verifier pairing can corrupt metadata.  Tests should validate cursor sizing, root detection, record geometry, key ordering, masked comparisons, overlapping high-key behavior, and staging flag behavior for each concrete btree.
