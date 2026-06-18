# sources/distributed-fs/ceph-client/lib/crypto/arm/ghash-neon-core.S

## Purpose
This ARM32 NEON assembly file implements GHASH block update using `vmull.p8` byte polynomial multiplication. It accelerates AES-GCM style GF(2^128) accumulation without requiring ARMv8 PMULL.

## Important APIs, Types, And Functions
The exported routine is `pmull_ghash_update_p8(size_t blocks, struct polyval_elem *dg, const u8 *src, const struct polyval_elem *h)`. Core macros are `__pmull_p8` for 64x64 polynomial multiply built from 8x8 operations, `__pmull_reduce_p8` for reduction by the GHASH polynomial, `vrev64_if_be` for endian handling, and `ghash_update` for the per-block loop.

## Control Flow
The function loads the hash subkey, precomputes shifted variants for Karatsuba-style multiplication, initializes masks, loads the accumulator, then loops over blocks. Each block reverses input byte order, xors it into the accumulator, computes low/high/cross polynomial products, reduces the 256-bit product, and continues until `blocks` reaches zero. It stores the updated accumulator and returns.

## State And Persistence
All vector temporaries live in NEON registers. Persistent state is the caller's accumulator buffer, updated in place. No global state is touched.

## Dependencies And Integration Points
It uses `<linux/linkage.h>`, `<asm/assembler.h>`, `.fpu neon`, and is called by `arm/gf128hash.h` inside a SIMD-safe section. It integrates with common GHASH key/accumulator layout represented as `struct polyval_elem`.

## Risks And Edge Cases
Endian conversions must match common GHASH formatting. The routine assumes valid block count and 16-byte readable inputs. Register aliasing in macros is subtle, and incorrect overlap could corrupt the product. As assembly, it needs architecture-specific build and unwind scrutiny.

## Test Signals
AES-GCM vectors, random differential tests against `ghash_blocks_generic`, big-endian build coverage, unaligned input tests if callers permit them, and PMULL-free NEON ARM32 hardware tests are useful signals.
