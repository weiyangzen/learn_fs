# sources/distributed-fs/ceph-client/lib/crypto/poly1305-donna64.c

## Purpose
Implements the 64-bit Donna Poly1305 core optimized around 44/44/42-bit limbs and `u128` intermediates.

## Important APIs, Types, and Functions
- Exports `poly1305_core_setkey()`, `poly1305_core_blocks()`, and `poly1305_core_emit()`.
- Uses three accumulator/key limbs and precomputes `20*r[1..2]`.

## Control Flow and State
Key setup clamps the 128-bit `r` into three limbs. Block processing adds message limbs plus `hibit`, multiplies with `u128` intermediate products, partially reduces carries modulo `2^130-5`, and stores state. Emit fully carries, computes `h + -p`, mask-selects canonical `h`, optionally adds the nonce as two 64-bit chunks, reduces to 128 bits, and writes little-endian tag words.

## Dependencies and Integration Points
Used by Poly1305 builds where 128-bit integer support is available and preferred. Depends on `u128`, unaligned helpers, and internal Poly1305 types.

## Risks and Test Signals
Risks include `u128` availability, carry range assumptions, and constant-time canonical selection. Tests should compare to Donna32 and MIPS arch implementations, include RFC vectors, large multi-block messages, boundary accumulator values, and split-update wrapper tests.
