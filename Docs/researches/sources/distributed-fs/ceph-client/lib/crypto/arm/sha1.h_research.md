# sources/distributed-fs/ceph-client/lib/crypto/arm/sha1.h

## Purpose
This header dispatches ARM32 SHA-1 block compression among scalar, NEON, and crypto-extension implementations.

## Important APIs, Types, And Functions
It declares `sha1_block_data_order`, `sha1_transform_neon`, and `sha1_ce_transform`. It defines static keys `have_neon` and `have_ce`, implements `sha1_blocks`, and defines `sha1_mod_init_arch`.

## Control Flow
At init, NEON enables `have_neon`; SHA-1 crypto extension capability additionally enables `have_ce`. At runtime `sha1_blocks` chooses crypto extensions inside `scoped_ksimd()` when available, otherwise NEON, otherwise scalar ARM.

## State And Persistence
Feature availability persists in jump labels. SHA-1 chaining state is caller-owned and updated by selected compression routines.

## Dependencies And Integration Points
It uses `<asm/simd.h>`, hardware capability variables, kernel-mode NEON configuration, and common SHA-1 block state types. It integrates with the common SHA-1 library through the `sha1_blocks` hook.

## Risks And Edge Cases
Feature detection must prevent crypto-extension instructions on unsupported CPUs. Calls in non-SIMD contexts must fall back to scalar. Build combinations without kernel-mode NEON must still compile.

## Test Signals
SHA-1 selftests should run with static keys forced or observed for scalar, NEON, and CE paths. CPU feature matrix builds and runtime fallback tests are important.
