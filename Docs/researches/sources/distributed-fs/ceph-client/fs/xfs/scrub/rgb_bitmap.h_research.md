# sources/distributed-fs/ceph-client/fs/xfs/scrub/rgb_bitmap.h

## Purpose
`rgb_bitmap.h` provides a type-specific bitmap wrapper for realtime group block numbers (`xfs_rgblock_t`). It lets scrub and repair code manipulate ranges in rtgroup-local block units without passing raw integer types directly to the generic 32-bit bitmap API.

## Important APIs, types, and functions
The file defines `struct xrgb_bitmap`, which embeds `struct xbitmap32 rgbitmap`. Inline helpers are `xrgb_bitmap_init`, `xrgb_bitmap_destroy`, `xrgb_bitmap_set`, and `xrgb_bitmap_walk`.

## Control flow
There is no complex control flow. Callers initialize the wrapper, set ranges by `xfs_rgblock_t start` plus `xfs_extlen_t len`, walk set regions with an `xbitmap32_walk_fn`, and destroy the underlying bitmap. The wrapper forwards directly to `xbitmap32` functions.

## State and persistence
State is entirely in memory inside the embedded `xbitmap32`. Nothing is persisted, logged, or tied to a transaction by the wrapper itself.

## Dependencies and integration points
It depends on the scrub bitmap infrastructure and XFS realtime group block typedefs. It is used by realtime repair code, especially rtrmap repair and rtbitmap/rtrmap cross-reference helpers, to represent rtgroup block ranges such as CoW staging gaps or free realtime extents.

## Risks and test signals
The main risk is unit confusion: callers must supply rtgroup block numbers, not rtblocks, fsblocks, or rt extents. Range overflow and missing destroy calls are inherited from the generic bitmap. Tests should exercise large rtgroups, zero-length avoidance by callers, region coalescing, walk callback ordering, and conversions between rtb/rgbno/rtx units at call sites.
