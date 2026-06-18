# sources/distributed-fs/ceph-client/fs/xfs/scrub/rtb_bitmap.h

## Purpose
`rtb_bitmap.h` provides a type-specific bitmap wrapper for filesystem-wide realtime block numbers (`xfs_rtblock_t`). It gives scrub and repair code a small strongly named abstraction over the generic 64-bit bitmap implementation.

## Important APIs, types, and functions
The file defines `struct xrtb_bitmap`, embedding `struct xbitmap64 rtbitmap`. Inline functions are `xrtb_bitmap_init`, `xrtb_bitmap_destroy`, `xrtb_bitmap_set`, and `xrtb_bitmap_walk`.

## Control flow
Callers initialize the bitmap, add ranges in rtblock units, walk all set ranges with an `xbitmap64_walk_fn`, and destroy the wrapper. All operations forward directly to the underlying `xbitmap64`.

## State and persistence
The wrapper owns only transient in-memory bitmap state. It performs no logging, allocation policy, or disk updates by itself.

## Dependencies and integration points
It depends on XFS realtime block typedefs and scrub bitmap infrastructure. It is suitable for code that needs whole-realtime-volume addressing rather than rtgroup-local `xrgb_bitmap` or data-device `xfsb_bitmap`.

## Risks and test signals
The main risk is unit mismatch at call sites, particularly confusing rtblocks with rt extents, rtgroup blocks, or fsblocks. Tests should check high rtblock values requiring 64-bit coverage, range coalescing, walk ordering, destroy paths, and conversions at callers that cross group boundaries.
