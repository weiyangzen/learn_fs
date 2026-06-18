# sources/distributed-fs/ceph-client/lib/crypto/sha3.c

## Purpose

This file implements generic SHA-3 and SHAKE sponge functions, with optional architecture absorb, permutation, and one-shot hooks. It was read as a complete 411-line file.

## Important APIs, Types, and Functions

Exports include `__sha3_update`, `sha3_final`, `shake_squeeze`, `sha3_224`, `sha3_256`, `sha3_384`, `sha3_512`, `shake128`, and `shake256`. Internal pieces include `sha3_keccakf_one_round_generic`, `sha3_keccakf_generic`, and `sha3_absorb_blocks_generic`. Architecture one-shot hooks default to false when not provided.

## Control Flow

Update XORs input into the sponge rate area, runs the Keccak permutation on full blocks, and tracks absorb offset. SHA3 final applies the `0x06` domain suffix and `0x80` pad bit, permutes, copies the fixed digest, and zeroizes. SHAKE squeeze applies the `0x1f` suffix on first squeeze, marks absorb complete by setting offset to block size, then repeatedly permutes and copies output chunks.

## State and Persistence Behavior

`__sha3_ctx` stores the 1600-bit state, block size, digest size, absorb offset, and squeeze offset. SHA3 final and one-shot SHAKE zeroize contexts after use. Streaming SHAKE contexts persist across multiple squeezes until the caller zeroizes them.

## Dependencies and Integration Points

It depends on `crypto/sha3.h`, `crypto_xor`, unaligned little-endian helpers, optional `$(SRCARCH)/sha3.h`, and FIPS test data. Architecture hooks can override block absorb, permutation, and fixed-length one-shot SHA3 calls.

## Risks and Edge Cases

The main risks are domain separation suffixes, absorb-after-squeeze misuse, endian conversion on non-little-endian systems, output-length handling for SHAKE, and architecture one-shot equivalence with streaming behavior.

## Test Signals

SHA3 and SHAKE KUnit vectors, NIST SHAKE tests, multiple-squeeze tests, guarded buffer tests, FIPS SHA3-256 self-test, and architecture fallback comparison validate behavior.
