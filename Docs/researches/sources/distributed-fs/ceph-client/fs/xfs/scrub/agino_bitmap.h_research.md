# sources/distributed-fs/ceph-client/fs/xfs/scrub/agino_bitmap.h

## Purpose
This header provides a type-checked bitmap wrapper for per-AG inode numbers (`xfs_agino_t`). It narrows the generic 32-bit sparse bitmap API to AG inode number use sites, mostly repair code that tracks sets of inodes inside one allocation group.

## Important APIs, types, and functions
`struct xagino_bitmap` embeds `struct xbitmap32 aginobitmap`. Inline functions mirror the generic bitmap operations: `xagino_bitmap_init`, `xagino_bitmap_destroy`, `xagino_bitmap_clear`, `xagino_bitmap_set`, `xagino_bitmap_test`, and `xagino_bitmap_walk`. The walk callback type is inherited from `xbitmap32_walk_fn`.

## Control flow and state
There is no independent control flow; all functions immediately delegate to `xbitmap32`. State is the interval tree maintained by the underlying bitmap. Callers pass AG inode start and length values, and the wrapper preserves those types at the interface boundary.

## Persistence and integration
The structure is in-memory only and must be initialized and destroyed by the caller. It integrates with AGI repair, especially iunlink reconstruction, where sets of unlinked, missing, or already-processed AG inode numbers are tracked compactly.

## Risks and test signals
The header relies on the underlying `xbitmap32` semantics, including interval merging, splitting, and walk immutability. Tests should focus on callers: setting, clearing, and walking sparse AG inode ranges; ensuring no full inode numbers are accidentally passed; and verifying cleanup on repair abort paths.
