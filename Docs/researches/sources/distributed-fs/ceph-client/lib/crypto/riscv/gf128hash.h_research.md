# sources/distributed-fs/ceph-client/lib/crypto/riscv/gf128hash.h

## Purpose
Provides RISC-V GHASH architecture hooks using the Zvkg vector GCM/GMAC extension when available.

## Important APIs, Types, and Functions
Declares `ghash_zvkg`. Defines `ghash_preparekey_arch`, `ghash_blocks_arch`, `gf128hash_mod_init_arch`, and static key `have_zvkg`.

## Control Flow
Key preparation stores the key both as generic POLYVAL form and raw GHASH bytes for Zvkg. Block processing checks `have_zvkg` and `may_use_simd()`. Accelerated processing converts the internal accumulator to GHASH byte order, enters a vector region, calls `ghash_zvkg`, exits, converts back to POLYVAL, and zeros the temporary. Fallback calls `ghash_blocks_generic`.

## State and Persistence
The `struct ghash_key` persists generic and raw key forms. The accumulator is mutated in place after conversion back. The temporary GHASH accumulator is explicitly zeroed.

## Dependencies and Integration Points
Depends on RISC-V vector/SIMD headers, generic GHASH/POLYVAL conversion helpers, and `ghash-riscv64-zvkg.S`. Module init checks `ZVKG` plus VLEN at least 128.

## Risks
No `ghash_mul_arch` single-block hook is defined here, so callers use block processing or generic multiply depending on higher-level selection. Conversion between POLYVAL and GHASH representations is correctness-critical.

## Test Signals
GHASH and AES-GCM test vectors with Zvkg enabled/disabled, plus randomized generic-vs-arch differential tests over several block counts.
