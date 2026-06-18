# sources/distributed-fs/ceph-client/lib/crypto/powerpc/gf128hash.h

## Purpose
Provides PowerPC GHASH/GF(2^128) architecture hooks using POWER8 vector crypto when available, with generic POLYVAL/GHASH fallback.

## Important APIs, Types, and Functions
Declares `gcm_init_p8`, `gcm_gmult_p8`, and `gcm_ghash_p8`. Defines `ghash_preparekey_arch`, `ghash_mul_arch`, `ghash_blocks_arch`, and `gf128hash_mod_init_arch`, plus a `have_vec_crypto` static key.

## Control Flow
Key preparation always stores the raw key in generic POLYVAL form. If vector crypto and SIMD are usable, it enters a VSX region and calls `gcm_init_p8` to build the POWER8 table; otherwise it reproduces the table layout in C. Multiplication and block processing convert the internal POLYVAL accumulator into GHASH byte order, run the vector helper inside VSX, convert back, and zero the temporary accumulator. Fallback paths call generic POLYVAL/GHASH routines.

## State and Persistence
The static branch records CPU feature availability after module init. Each `struct ghash_key` persists both generic and POWER8 table material. Temporary GHASH accumulators are explicitly zeroed after use.

## Dependencies and Integration Points
Depends on PowerPC VSX switching, CPU feature bits `CPU_FTR_ARCH_207S` and `PPC_FEATURE2_VEC_CRYPTO`, and generic GHASH/POLYVAL conversion helpers. The generated helpers come from `ghashp8-ppc.pl`.

## Risks
Byte-order conversion between POLYVAL internal state and GHASH helper state is a primary correctness risk. SIMD availability can differ between key setup and use, so the C fallback table generation must match `gcm_init_p8`. Preemption/pagefault control must remain paired around VSX calls.

## Test Signals
Run GHASH and AES-GCM known-answer tests with vector crypto enabled and disabled. Compare `gcm_init_p8` table output to the C fallback table for random keys on BE and LE builds.
