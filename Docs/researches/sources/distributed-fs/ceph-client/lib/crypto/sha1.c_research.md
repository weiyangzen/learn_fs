# sources/distributed-fs/ceph-client/lib/crypto/sha1.c

## Purpose

This file implements generic SHA-1 and HMAC-SHA1 library functions with optional architecture block acceleration and FIPS self-testing. It was read as a complete 336-line file.

## Important APIs, Types, and Functions

Exports include `sha1_init`, `sha1_update`, `sha1_final`, `sha1`, `hmac_sha1_preparekey`, `hmac_sha1_init`, `hmac_sha1_init_usingrawkey`, `hmac_sha1_final`, `hmac_sha1`, and `hmac_sha1_usingrawkey`. Internal pieces include `sha1_block_generic`, `sha1_blocks_generic`, `__sha1_final`, and `__hmac_sha1_preparekey`.

## Control Flow

`sha1_update` accumulates bytes in a partial block buffer, processes full blocks through `sha1_blocks`, and stores any remainder. Finalization adds SHA padding and a 64-bit bit count, processes the final block, emits big-endian digest words, then zeroizes the public context. HMAC preparation hashes overlong keys, builds ipad and opad derived blocks, and precomputes inner and outer SHA-1 states.

## State and Persistence Behavior

`struct sha1_ctx` stores block state, byte count, and a partial buffer. HMAC key structs persist precomputed inner and outer states. Temporary derived keys and contexts are zeroized explicitly.

## Dependencies and Integration Points

It depends on crypto HMAC constants, SHA-1 public headers, unaligned big-endian helpers, optional `$(SRCARCH)/sha1.h`, and `fips.h`. It exports GPL symbols to other kernel crypto users.

## Risks and Edge Cases

SHA-1 is cryptographically weak for collision resistance. Implementation risks include bytecount overflow semantics, padding boundary cases around 56 bytes, architecture hook correctness, and HMAC outer padding length assumptions.

## Test Signals

SHA-1/HMAC-SHA1 KUnit vectors, incremental update split tests from `hash-test-template.h`, FIPS HMAC-SHA1 self-test, and architecture fallback comparison validate behavior.
