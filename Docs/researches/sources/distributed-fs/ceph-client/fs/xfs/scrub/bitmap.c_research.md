# sources/distributed-fs/ceph-client/fs/xfs/scrub/bitmap.c

## Purpose
This file implements sparse interval bitmaps for 64-bit and 32-bit address spaces using Linux interval-tree/rbtree infrastructure. Scrub and repair use these structures to collect ranges of filesystem blocks, AG blocks, inode numbers, or other dense numeric spaces without allocating full bit arrays.

## Important APIs, types, and functions
For 64-bit ranges, `struct xbitmap64_node` stores start, last, and subtree-last fields, and public operations are `xbitmap64_init`, `destroy`, `set`, `clear`, `disunion`, `hweight`, `walk`, `empty`, and `test`. The 32-bit implementation mirrors the same API with `struct xbitmap32_node`, plus `xbitmap32_count_set_regions`. Both use `INTERVAL_TREE_DEFINE` to generate tree operations.

## Control flow and state
`set` first checks if a range is already covered, clears overlapping intervals, then merges with left and/or right adjacent intervals or inserts a new node. `clear` removes or splits overlapping intervals depending on whether the clear range covers the middle, left, right, or whole interval. `disunion` iterates all ranges in the subtracting bitmap and clears them from the target. `walk` calls the caller callback for every set interval and stops on any nonzero return. `test` reports whether the requested start is set and adjusts length to the contiguous state run.

## Persistence and integration
The bitmaps are in-memory only and require explicit destruction. They are foundational for repair paths that compute stale metadata blocks, free-space gaps, AGFL candidates, iunlink inode sets, and bmap old-block sets through typed wrappers such as `xagb_bitmap`, `xfsb_bitmap`, and `xagino_bitmap`.

## Risks and test signals
Critical risks are integer overflow in `start + len - 1`, adjacency around zero or max values, split allocation failure leaving partial state, and modifying a bitmap during walk. Tests should cover set/clear inside, outside, and across intervals; merging both neighbors; disunion of overlapping and empty sets; hweight overflow boundaries; early walk cancellation with `-ECANCELED`; and `test` length adjustment for set and clear runs.
