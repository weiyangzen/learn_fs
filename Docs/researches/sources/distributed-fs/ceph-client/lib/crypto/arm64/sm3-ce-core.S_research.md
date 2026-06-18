# sources/distributed-fs/ceph-client/lib/crypto/arm64/sm3-ce-core.S

## Purpose
ARMv8 SM3 Crypto Extensions block transform for the Chinese SM3 hash.

## Important APIs, Types, And Functions
Exports `sm3_ce_transform(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. Uses SM3 instructions such as `sm3ss1`, `sm3tt1a/b`, `sm3tt2a/b`, `sm3partw1`, and `sm3partw2` through `round` and `qround` macros, with constants in `.Lt`.

## Control Flow
The transform loads state, reorders it into vector-friendly form, loads each 64-byte block, byte-swaps words, runs the first and second SM3 round families with schedule expansion, XORs the result with the previous state per SM3 compression, loops for all blocks, and stores state in the C layout.

## State, Persistence, And Dependencies
Only caller state is updated. The code has no persistent storage and depends on ARM SM3 instructions plus wrapper-side feature gating.

## Integration Points
`sm3.h` selects this path when both ASIMD and SM3 features are present; otherwise it may use the NEON assembly or generic C.

## Risks
State reorder around load/store is easy to break. The CE path and NEON path must produce identical compression results. Executing SM3 instructions without the CPU feature would fault.

## Test Signals
SM3 known-answer vectors, multi-block messages, randomized generic-vs-CE comparisons, and CPU feature matrix tests are important.
