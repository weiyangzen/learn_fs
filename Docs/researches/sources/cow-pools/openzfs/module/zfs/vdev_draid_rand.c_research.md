# File Research: sources/cow-pools/openzfs/module/zfs/vdev_draid_rand.c

## Purpose

Provides the deterministic pseudo-random generator used by dRAID permutation generation. It implements xoroshiro128++ 1.0 directly in-tree so dRAID layout generation does not depend on platform RNG behavior or external libraries.

## APIs And Behavior

- `rotl()` performs a 64-bit rotate-left primitive.
- `vdev_draid_rand(uint64_t *s)` takes a two-word mutable state, returns the next 64-bit value, and advances the state with xoroshiro128++ constants.

## Dependencies And Integration

The only include is `sys/vdev_draid.h`. `vdev_draid_generate_perms()` and `vdev_draid_shuffle_perms()` seed this generator with `VDEV_DRAID_SEED` plus the selected `draid_map_t` seed, then use the generated values for Fisher-Yates shuffles.

## Risks And Invariants

The exact arithmetic, rotations, and state update order are layout-critical. Even small changes would alter generated permutation maps and make dRAID physical placement incompatible with existing pools. The generator is used for deterministic distribution, not cryptographic security.

## Summary

This is a tiny but format-sensitive PRNG implementation that underpins stable dRAID child permutation maps.
