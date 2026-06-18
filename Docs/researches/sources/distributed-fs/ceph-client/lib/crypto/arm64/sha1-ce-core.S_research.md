# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha1-ce-core.S

## Purpose
ARMv8 SHA1 Crypto Extensions block transform for the kernel SHA1 block API.

## Important APIs, Types, And Functions
Exports `sha1_ce_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`. Uses macros `loadrc`, `add_only`, and `add_update` around `sha1h`, `sha1c`, `sha1p`, `sha1m`, `sha1su0`, and `sha1su1`.

## Control Flow
The function loads SHA1 round constants and the 160-bit state, then loops over 64-byte blocks. Each block is loaded big-endian via `rev32`, expanded with SHA1 schedule instructions, run through all rounds, added back to the chaining state, and stored after `nblocks` reaches zero.

## State, Persistence, And Dependencies
Only the caller-provided block state is mutated. There is no persistent global state in assembly. It depends on ARMv8 SHA1 instructions and is only called by the dispatch header after CPU feature and SIMD-context gating.

## Integration Points
`sha1.h` routes generic SHA1 block processing to this function when `have_ce` is enabled and SIMD is allowed.

## Risks
SHA1 is legacy and collision-broken for new designs, so integration must remain for compatibility only. Implementation risks are endian conversion, state layout at five 32-bit words, and incomplete feature gating before executing CE opcodes.

## Test Signals
SHA1 known-answer vectors, multi-block messages, incremental messages crossing 64-byte boundaries, and forced generic-vs-CE comparisons are the core signals.
