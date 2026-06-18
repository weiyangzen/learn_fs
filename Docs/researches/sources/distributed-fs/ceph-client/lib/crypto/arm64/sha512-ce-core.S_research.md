# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha512-ce-core.S

## Purpose
ARMv8 SHA512 Crypto Extensions block transform for SHA-384/SHA-512 style 64-bit SHA2 states.

## Important APIs, Types, And Functions
Exports `sha512_ce_transform(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. Uses a `dround` macro, `sha512h`, `sha512h2`, `sha512su0`, `sha512su1`, and the `.Lsha512_rcon` table.

## Control Flow
For each 128-byte block, the transform loads eight 64-bit message vectors, reverses bytes for big-endian SHA words, snapshots the current state, performs 80 rounds while updating the schedule, adds the original chaining state, and loops until all blocks are consumed.

## State, Persistence, And Dependencies
Mutates only the caller's `sha512_block_state`. It requires ARM SHA512 instructions and is expected to be called only from the feature-gated wrapper.

## Integration Points
`sha512.h` dispatches to this implementation when the SHA512 CPU feature is present and SIMD may be used. Generic code otherwise uses `sha512_block_data_order`.

## Risks
State lane ordering, byte swapping, and round constant sequencing are critical. Since SHA-384 and SHA-512 share the block function, digest-specific initialization and finalization must remain in generic code.

## Test Signals
SHA-384 and SHA-512 known-answer vectors, long messages over many blocks, and generic-vs-CE comparisons on CPUs with and without SHA512 instructions should cover this path.
