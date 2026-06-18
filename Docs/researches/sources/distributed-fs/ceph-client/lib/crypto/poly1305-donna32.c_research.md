# sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna32.c

## Purpose
Implements the 32-bit Donna Poly1305 core: key clamping/precomputation, block accumulation, and tag emission.

## Important APIs, Types, and Functions
- Exports `poly1305_core_setkey()`, `poly1305_core_blocks()`, and `poly1305_core_emit()`.
- Uses 5 limbs of 26 bits for the accumulator/key and precomputes `5*r[1..4]`.

## Control Flow and State
Key setup extracts and clamps `r` from the first 16 key bytes. Block processing loads each 16-byte block into 26-bit limbs, applies `hibit`, multiplies accumulator by `r` modulo `2^130-5`, partially carries after every block, and stores accumulator limbs. Emit fully carries, conditionally subtracts the modulus through mask selection, packs the low 128 bits, optionally adds a 128-bit nonce, and writes the tag little-endian.

## Dependencies and Integration Points
Used by generic Poly1305 internals on 32-bit-oriented builds. Depends on unaligned little-endian helpers and `struct poly1305_state`/`struct poly1305_core_key`.

## Risks and Test Signals
Constant-time final conditional subtraction and carry bounds are important. Tests should cover RFC 8439 vectors, empty input, multi-block input, all tail lengths through `poly1305.c`, nonce null/non-null emit behavior if used internally, and comparison with 64-bit/arch implementations.
