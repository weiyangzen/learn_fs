# sources/distributed-fs/ceph-client/lib/crypto/gf128hash.c

## Purpose
Implements library GHASH and POLYVAL over GF(2^128), including generic constant-time multiplication and dispatch to architecture-specific accelerated hooks. It is intended for AEAD and disk-encryption constructions that need these almost-universal polynomial hashes, not as a standalone cryptographic hash.

## Important APIs, Types, and Functions
- Exports `ghash_preparekey()`, `ghash_update()`, `ghash_final()`, `polyval_preparekey()`, `polyval_update()`, and `polyval_final()`.
- Uses public context/key types from `<crypto/gf128hash.h>`: `struct ghash_key`, `struct ghash_ctx`, `struct polyval_key`, `struct polyval_ctx`, and `struct polyval_elem`.
- `clmul64()` and, on non-`CONFIG_ARCH_SUPPORTS_INT128`, `clmul32()` emulate carryless multiply with "holes" in normal integer multiplication.
- `polyval_mul_generic()` performs Karatsuba 128x128 carryless multiplication followed by reduction in the POLYVAL field.
- `ghash_key_to_polyval()`, `ghash_acc_to_polyval()`, and `polyval_acc_to_ghash()` bridge GHASH's big-endian bit mapping to POLYVAL's little-endian representation.

## Control Flow and State
Key preparation either calls `*_preparekey_arch` or stores the converted/raw key. Updates first complete a buffered partial block, then process full blocks via `*_blocks_arch` or generic loops, then XOR any tail into the accumulator and remember `partial`. GHASH stores partial bytes in reverse block order to preserve the GHASH convention; POLYVAL stores partial bytes in natural order. Finalization multiplies a final partial block when present, serializes the accumulator, and zeroes the whole context with `memzero_explicit()`.

## Dependencies and Integration Points
Depends on kernel unaligned helpers, endian conversion, export/module infrastructure, and optional `$(SRCARCH)/gf128hash.h` hooks selected by `CONFIG_CRYPTO_LIB_GF128HASH_ARCH`. Consumers are expected to initialize contexts with a prepared key and stream input using block-size-neutral update calls.

## Risks and Test Signals
The main correctness risks are representation conversion between GHASH and POLYVAL, reduction constants, and partial-block byte ordering. The generic multiplication is designed to avoid secret-dependent lookup tables; architecture hooks must preserve constant-time behavior and equivalent accumulator/key formats. Tests should include NIST GCM GHASH vectors, RFC 8452 POLYVAL vectors, split-update equivalence, empty and partial inputs, and generic-vs-arch comparison on supported architectures.
