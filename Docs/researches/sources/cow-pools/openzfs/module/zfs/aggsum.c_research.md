# File Research: sources/cow-pools/openzfs/module/zfs/aggsum.c

## Scope

Implements aggregate-sum counters: fanned-out, bucketed counters optimized for high-frequency updates and relatively rare exact reads.

## APIs And Behavior

- `aggsum_init()` initializes global bounds, the global lock, bucket fanout based on boot CPU count, and per-bucket locks.
- `aggsum_fini()` destroys bucket locks, frees buckets, and destroys the global lock.
- `aggsum_lower_bound()` and `aggsum_upper_bound()` return approximate atomic bounds without taking locks.
- `aggsum_add()` updates the CPU-selected bucket on the fast path when borrowed capacity covers the delta; otherwise it clears/borrows against the global lower/upper bounds.
- `aggsum_value()` serializes through the global lock, clears all borrowed bucket state, asserts lower and upper bounds converge, and returns the exact value.
- `aggsum_compare()` often answers from bounds alone; otherwise it clears buckets until the target is outside the bounds or the exact value is known.

## State And Dependencies

`aggsum_t` tracks lower/upper bounds, global lock, bucket count/shift, and an array of `aggsum_bucket_t` values containing bucket locks, deltas, and borrowed capacity. It depends on SPL mutexes, atomic load/store helpers, `CPU_SEQID_UNSTABLE`, `boot_ncpus`, and kmem allocation.

## Risks And Invariants

The lower and upper bounds intentionally diverge while buckets hold borrowed capacity. Exact reads and comparisons are expensive because they clear buckets and force future writers to borrow again. CPU hot-add does not expand buckets, so fanout is fixed at initialization. Signed lower-bound arithmetic is mixed with unsigned upper-bound reads; callers must respect the compare/value semantics rather than treating approximate bounds as exact.
