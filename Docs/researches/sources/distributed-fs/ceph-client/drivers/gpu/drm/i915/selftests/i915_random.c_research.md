# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.c

## Purpose
This file provides deterministic pseudo-random helpers used by many i915 selftests. It centralizes 64-bit random generation, array shuffling, random order allocation, and aligned random offset selection using the global selftest seed.

## Important APIs, Types, And Functions
- `i915_prandom_u64_state()` combines two 32-bit PRNG draws.
- `i915_prandom_shuffle()` implements Fisher-Yates shuffle for small element sizes.
- `i915_random_reorder()` shuffles an array of unsigned indices.
- `i915_random_order()` allocates and shuffles an index array from `0..count-1`.
- `igt_random_offset()` chooses an aligned address in `[start, end)` that can contain `len`.

## Control Flow
Callers create an `rnd_state` with macros from `i915_random.h`, then request shuffled order or offsets. `i915_random_order()` fills the array sequentially, shuffles it, and returns ownership to the caller. `igt_random_offset()` validates the requested range with `BUG_ON`, computes the aligned range, uses modulo reduction on a 64-bit random number, and returns the rounded-up aligned result.

## State And Persistence
No global state is mutated directly. Determinism is controlled by the caller-provided `struct rnd_state`, usually seeded from `i915_selftest.random_seed`. Allocated order arrays are caller-owned.

## Dependencies And Integration Points
It depends on Linux PRNG helpers, allocation APIs, math64 helpers, and i915 utility overflow checks. It is used by GTT, request, memory-region, VMA, and syncmap selftests for reproducible randomized stress paths.

## Risks
`i915_prandom_shuffle()` refuses elements larger than its 128-byte stack buffer and warns on oversized count. `igt_random_offset()` assumes valid non-overflowing ranges and will `BUG_ON` invalid inputs, so callers must pre-check size/alignment.

## Test Signals
The helper itself has no selftest entry. Its signals appear in dependent randomized tests: repeatability from a logged seed, shuffled coverage of holes/engines/objects, and deterministic reproduction of failures.
