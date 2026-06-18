# sources/distributed-fs/ceph-client/lib/crypto/arm64/sha3-ce-core.S

## Purpose
ARMv8.2 SHA3 Crypto Extensions implementation of Keccak absorb and permutation.

## Important APIs, Types, And Functions
Exports `sha3_ce_transform(struct sha3_state *state, const u8 *data, size_t nblocks, size_t block_size)`. Defines instruction macros `eor3`, `rax1`, `bcax`, and `xar`, plus the 24-round constant table `.Lsha3_rcon`.

## Control Flow
The function loads the 25-lane Keccak state into vector registers. For each block it XORs input lanes according to `block_size` branches for SHA3-512, SHA3-384, SHA3-256/SHAKE256, SHA3-224, and SHAKE128, then runs 24 rounds using SHA3 CE ternary XOR, rotate-XOR, Chi, and round constant operations. After all blocks it stores the state.

## State, Persistence, And Dependencies
State is the caller's `sha3_state`. The assembly has no persistent storage. It depends on ARMv8.2 SHA3 instructions encoded with `.inst` and on the wrapper to gate CPU features and SIMD context.

## Integration Points
Called by `sha3.h` for both absorbing data blocks and for `sha3_keccakf()` by passing a zero block.

## Risks
Only specific rate values are supported by control-flow assumptions. A bad `block_size` from the caller could absorb the wrong number of lanes. Encoded instruction macros are less self-checking than mnemonic assembly and require assembler/CPU compatibility.

## Test Signals
SHA3-224/256/384/512 and SHAKE128/256 vectors, direct Keccak-f tests through finalization, and generic-vs-CE comparisons for every rate value are needed.
