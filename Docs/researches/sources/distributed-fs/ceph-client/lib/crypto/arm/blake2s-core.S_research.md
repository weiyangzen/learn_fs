# sources/distributed-fs/ceph-client/lib/crypto/arm/blake2s-core.S

## Purpose
This ARM scalar assembly file implements BLAKE2s compression faster than the generic C path on ARM without relying on NEON.

## Important APIs, Types, and Functions
It defines `ENTRY(blake2s_compress)` and macros for loading/storing words, endian swaps, quarter rounds, rounds, and the permutation. It embeds the BLAKE2s IV.

## Control Flow
For each block, the function loads the hash state and message words, sets up the BLAKE2s state with counters and flags, runs the required rounds with message schedule permutations, folds the result into the chaining value, updates counters, advances input, and loops until `nblocks` is exhausted.

## State and Persistence
The caller-owned `struct blake2s_ctx` state is updated across blocks. Temporary message/state words live in ARM registers and stack spill slots.

## Dependencies and Integration Points
It depends on ARM assembler helpers and is built when `CRYPTO_LIB_BLAKE2S_ARCH` selects ARM. `arm/blake2s.h` declares the function for the generic BLAKE2s code.

## Risks and Test Signals
Risks include endian conversion on ARM big-endian, delayed rotation bookkeeping, stack spill correctness, and counter/final flag handling. Known-answer BLAKE2s tests and incremental update tests validate it.
