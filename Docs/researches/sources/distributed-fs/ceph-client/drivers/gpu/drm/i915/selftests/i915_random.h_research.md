# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/i915_random.h

## Purpose
This header declares and seeds the pseudo-random helper API for i915 selftests. It gives tests a uniform way to use the global `i915_selftest.random_seed` while allowing nested deterministic substates.

## Important APIs, Types, And Functions
- `I915_RND_STATE_INITIALIZER(seed)` initializes `struct rnd_state`.
- `I915_RND_STATE(name)` seeds a state from `i915_selftest.random_seed`.
- `I915_RND_SUBSTATE(name, parent)` derives a child state from a parent PRNG.
- `i915_prandom_u32_max_state()` scales a 32-bit draw to `[0, ep_ro)`.
- Declarations cover `i915_prandom_u64_state`, random order/reorder/shuffle, and `igt_random_offset`.

## Control Flow
Most tests instantiate a local `I915_RND_STATE(prng)` at entry. Loops then call helpers to shuffle placement order or select random offsets. Substates let nested loops reproduce inner random choices while advancing outer choices deterministically.

## State And Persistence
The header does not store state; it defines stack-local PRNG initialization patterns. Persistent reproducibility comes from the global module parameter `st_random_seed` in `i915_selftest.c`.

## Dependencies And Integration Points
It includes Linux `prandom`, `math64`, and `../i915_selftest.h`. It is shared by most stress-oriented selftests in this subset.

## Risks
Changing the scaling helper or seed macros changes reproducibility of existing failures. `i915_prandom_u32_max_state()` assumes callers handle zero/invalid upper bounds appropriately.

## Test Signals
The logged global seed from `__run_selftests()` is the key diagnostic signal. Tests that fail after randomized ordering can be rerun with the same seed.
