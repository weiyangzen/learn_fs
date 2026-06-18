<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.c

## Purpose
Implements a compact radix-tree-like map from dma-fence context IDs to the latest seqno already synchronized on a timeline, allowing i915 to skip redundant fence waits.

## Important APIs, types, and functions
- Public APIs: `i915_syncmap_init()`, `i915_syncmap_is_later()`, `i915_syncmap_set()`, and `i915_syncmap_free()`.
- Internal `struct i915_syncmap` stores prefix, height, bitmap, parent pointer, and flexible array of either seqnos or child pointers.
- Helpers compute leaf/branch prefixes and indexes, allocate leaves, set seqnos/children, insert join nodes, and recursively free the tree.

## Control flow
The root pointer is treated as a cache for the most recently used leaf. Lookup first checks the cached leaf, otherwise climbs parent pointers until it finds a branch with a matching prefix, then descends toward the target leaf. Set uses the cached leaf fast path when possible; otherwise it climbs to a common ancestor, inserts a join branch where prefixes diverge, allocates missing leaves, stores the seqno, and updates the root cache. Free climbs to the true root and recursively frees bitmap-marked children.

## State and persistence
The syncmap persists per owning timeline until freed. Leaf bitmap bits distinguish valid seqno zero from unset. Parent pointers allow a single cached leaf pointer to reach the whole tree.

## Dependencies and integration points
Depends on kernel flexible-array allocation, bit operations, i915 GEM assertions, and selftests. Used by timeline synchronization code to suppress repeated waits in `i915_request_await_dma_fence()`.

## Risks
Prefix/height math is subtle, especially around 64-bit IDs and `KSYNCMAP` radix assumptions. Sequence comparison uses signed subtraction for wraparound semantics. Allocation failures propagate to request dependency setup. Incorrect root-cache updates could leak subtrees or miss synchronization history.

## Test signals
Selftests under `selftests/i915_syncmap.c`, dense and sparse context-ID insertion, high-bit context IDs, seqno wraparound comparisons, allocation-failure paths, and request dependency squashing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_syncmap.c -->
