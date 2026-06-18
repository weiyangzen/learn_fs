# sources/distributed-fs/ceph-client/lib/crypto/arm/poly1305-armv4.pl

## Purpose
This Perl generator emits ARMv4-compatible and ARMv7 NEON Poly1305 assembly for the kernel. It is Cryptogams/OpenSSL-derived code adapted to expose Linux symbols for Poly1305 block initialization, block processing, and tag emission.

## Important APIs, Types, And Functions
Generated exported symbols are `poly1305_block_init` (via `poly1305_init` macro), `poly1305_blocks_arm`, `poly1305_blocks_neon`, and `poly1305_emit`. Internal generator/body regions include scalar `poly1305_blocks`, scalar `poly1305_emit`, `poly1305_init_neon`, and the long NEON loop with `.Lbase2_26_neon`, `.Loop_neon`, `.Long_tail`, and `.Lshort_tail`.

## Control Flow
The generator prints assembly after substituting register and syntax helpers. `poly1305_init` clears the accumulator, clamps the key, records scalar key limbs, and for non-kernel OpenSSL builds may choose function pointers by ARM capability. The scalar block routine processes 16-byte blocks in base 2^32-like limbs with multiplication by the clamped key and modular reduction. The NEON path requires at least 64 bytes, converts state to base 2^26, precomputes powers of `r`, processes up to four blocks per vectorized iteration, handles long/short tails, lazily reduces, and stores the hash. `poly1305_emit` finalizes and adds the nonce.

## State And Persistence
Persistent algorithm state is the caller's `struct poly1305_block_state` and final `struct poly1305_state`. The NEON path stores an `is_base2_26` marker in the state so scalar and vector code can convert formats safely. The generator itself has no runtime state after build.

## Dependencies And Integration Points
It depends on Perl at build time and kernel ARM assembler support at output time. `arm/poly1305.h` declares the generated symbols and selects scalar vs NEON through static keys and `may_use_simd()`.

## Risks And Edge Cases
Risks include generator drift, state radix conversion bugs, tail handling for non-64-byte multiples, endian handling, and clamping/final reduction mistakes. The scalar routine must remain ARMv4-compatible while the NEON routine must preserve VFP/NEON ABI registers. Mixing scalar and NEON updates relies on the state marker.

## Test Signals
Poly1305 RFC vectors, randomized split-update tests that alternate scalar and NEON paths, tail lengths from 0 to 127 bytes, big-endian build checks, ABI register preservation tests, and differential comparison with the generic implementation are relevant.
