# sources/distributed-fs/ceph-client/lib/crypto/x86/gf128hash.h

Purpose: x86 dispatch for GF(2^128) GHASH and POLYVAL multiplication/block processing using PCLMULQDQ, with AVX POLYVAL support.

Important APIs/types/functions: declares `polyval_mul_pclmul()`, `polyval_mul_pclmul_avx()`, `ghash_blocks_pclmul()`, and `polyval_blocks_pclmul_avx()`. Defines hooks `polyval_preparekey_arch()`, `ghash_mul_arch()`, `polyval_mul_arch()`, `ghash_blocks_arch()`, `polyval_blocks_arch()`, and `gf128hash_mod_init_arch()`.

Control flow: init enables `have_pclmul` and optionally `have_pclmul_avx`. POLYVAL key preparation stores the raw key in the last `h_powers` slot and fills preceding powers by repeated multiplication, using AVX PCLMUL when possible. Single multiply chooses AVX PCLMUL, non-AVX PCLMUL, or generic based on static keys and `irq_fpu_usable()`. GHASH/POLYVAL block processing uses SIMD in 4 KiB chunks, otherwise generic.

State and persistence: static branch state persists after init. Key-preparation mutates caller key schedules; block functions mutate the accumulator.

Dependencies: PCLMULQDQ, AVX, FPU APIs, generic GF128 hash routines, `struct polyval_elem`, `struct polyval_key`, `struct ghash_key`.

Integration points: architecture hooks for GHASH used by GCM and POLYVAL used by AES-GCM-SIV-like constructions.

Risks: GHASH and POLYVAL have different endian conventions; assembly contracts must match key representation. SIMD use in IRQ/FPU-unusable contexts must fall back. Precomputed power count must stay synchronized with `NUM_H_POWERS`.

Test signals: GHASH/POLYVAL known-answer tests, block-count boundaries, fallback comparison, and feature-specific runtime tests.
