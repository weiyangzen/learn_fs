# sources/distributed-fs/lizardfs/src/master/itree.cc

Purpose: implements a simple interval tree mapping inclusive `uint32_t` ranges to nonzero ids, with id zero used as deletion.

Important APIs/types/functions: internal `itnode` stores `from`, `to`, `id`, left, and right; `itree_add_interval()` adds or deletes a normalized interval; `itree_find()` returns id for a point or zero; `itree_rebalance()` converts tree to list, simplifies adjacent same-id intervals, and rebuilds a more balanced tree; `itree_freeall()` frees all nodes. Helpers split, overwrite, delete, and remove tree nodes.

Control flow: adding overlaps recursively splits existing ranges, deletes covered subranges, or overwrites ids. Deleting removes or trims intervals. Rebalance performs in-order flattening using `left` as next pointer, merges adjacent same-id intervals, then recursively chooses midpoints.

State and persistence behavior: state is caller-owned opaque tree pointer. No direct persistence; callers must serialize their interval meanings elsewhere.

Dependencies/integration: C-style module using `malloc/free` and `passert`. It is likely used for mapping numeric ranges in master configuration or metadata helpers.

Risks and test signals: deletion/addition use inclusive endpoints and swap reversed inputs; off-by-one at `from-1`/`to+1` can overflow around 0 or `UINT32_MAX`. The rebalance is documented as square-time and not a production-grade balanced tree. Tests should cover overlapping replaces, deletes that split intervals, reversed inputs, adjacent merge, endpoint extremes, and repeated rebalance.
