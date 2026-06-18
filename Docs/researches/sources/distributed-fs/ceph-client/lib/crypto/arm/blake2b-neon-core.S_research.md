# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2b-neon-core.S

## Purpose
This ARM NEON assembly file implements the BLAKE2b compression function for ARM systems with NEON.

## Important APIs, Types, and Functions
It defines `ENTRY(blake2b_compress_neon)`. Important data includes rotation tables for 24- and 16-bit byte rotations and the BLAKE2b IV. The core macro is `_blake2b_round`.

## Control Flow
The function aligns a stack spill buffer, loads `h`, `t`, and `f` fields from `struct blake2b_ctx`, increments the counter by `inc` per block, loads the 128-byte message block into NEON registers, executes 12 BLAKE2b rounds with sigma message ordering, folds the final state into the chaining value, stores updated `h`, and loops over `nblocks`.

## State and Persistence
Persistent hash state is caller-owned in `struct blake2b_ctx`: chaining value, counter, and finalization flags. The assembly mutates those fields. Stack spill and NEON registers are transient.

## Dependencies and Integration Points
It depends on ARM NEON and Linux linkage. The wrapper in `arm/blake2b.h` calls it inside SIMD-safe sections when NEON is available.

## Risks and Test Signals
Risks include counter carry handling, stack alignment, NEON register clobbers, final flag handling, and message schedule errors. BLAKE2b known-answer tests and chunked update/final-block cases are key signals.
