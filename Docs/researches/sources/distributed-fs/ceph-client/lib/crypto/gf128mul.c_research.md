# sources/distributed-fs/ceph-client/lib/crypto/gf128mul.c

## Purpose
Provides legacy GF(2^128) multiplication helpers used by crypto modes such as GHASH/GCM. It supports byte-oriented multiply-by-x^8 helpers, a direct constant-time-ish `lle` multiplier, and a large precomputed 64 KiB table implementation for the `bbe` representation.

## Important APIs, Types, and Functions
- Exports `gf128mul_x8_ble()`, `gf128mul_lle()`, `gf128mul_init_64k_bbe()`, `gf128mul_free_64k()`, and `gf128mul_64k_bbe()`.
- Uses `be128`, `le128`, `struct gf128mul_64k`, and `be128_xor()`/`gf128mul_x_lle()`/`gf128mul_x_bbe()` from `<crypto/gf128mul.h>`.
- `gf128mul_table_be` and `xda_le()`/`xda_be()` encode reduction constants for the polynomial `x^128 + x^7 + x^2 + x + 1`.

## Control Flow and State
`gf128mul_lle()` builds a small stack table of powers of the current multiplicand, with odd elements zeroed and even elements holding powers. It XORs both cacheline-adjacent possibilities for each bit to reduce timing variance, then advances the accumulator by x^8 between input bytes. The 64 KiB path allocates sixteen 256-entry tables, fills powers and XOR combinations for each byte position, then multiplies by table lookup and XOR accumulation. `gf128mul_free_64k()` clears table memory through `kfree_sensitive()`.

## Dependencies and Integration Points
Uses kernel allocation (`kzalloc_obj`, `kfree_sensitive`), endian helpers, and crypto GF128 types. The table API is integrated by callers that can afford per-key memory for faster repeated multiplication.

## Risks and Test Signals
Table lookups indexed by data/key material may be side-channel sensitive depending on caller use; the direct `lle` path has explicit alignment/cacheline mitigation. Allocation failure during 64 KiB table setup must clean partial state, which this file handles by calling `gf128mul_free_64k()`. Test signals include multiplication identity/zero cases, representation-specific known vectors, allocation-failure injection, and cross-checks against a simple reference multiplier.
