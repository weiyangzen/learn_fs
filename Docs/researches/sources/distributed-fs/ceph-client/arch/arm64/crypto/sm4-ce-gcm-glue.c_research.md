## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-glue.c

### Purpose
Registers ARMv8 CE/PMULL accelerated `gcm(sm4)` AEAD and handles SM4 key expansion, GHASH table setup, AAD hashing, scatterlist walking, and tag verification.

### Important APIs, Types, And Functions
Defines `struct sm4_gcm_ctx`, `gcm_setkey`, `gcm_setauthsize`, `gcm_calculate_auth_mac`, `gcm_crypt`, `gcm_encrypt`, `gcm_decrypt`, `sm4_ce_gcm_init`, and `sm4_ce_gcm_exit`. Assembly calls are `sm4_ce_pmull_ghash_setup`, `pmull_ghash_update`, `sm4_ce_pmull_gcm_enc`, and `sm4_ce_pmull_gcm_dec`.

### Control Flow
Setkey expands SM4 keys and computes the GHASH table in one SIMD section. AAD is scatterwalked, buffered to 16-byte blocks, and padded. `gcm_crypt()` zeroes GHASH, builds IV with counter 2, computes lengths, runs each skcipher walk segment through the assembly worker, and passes the length block on the final segment. Encrypt appends the computed tag; decrypt maps the stored tag and compares with `crypto_memneq()`.

### State, Persistence, And Dependencies
Transform state is SM4 key material plus a 64-byte GHASH table. Request state is IV, GHASH accumulator, length block, authtag, and skcipher walk cursor. Dependencies include AEAD/skcipher internals, scatterwalk, b128 operations, `crypto/sm4.h`, `asm/simd.h`, and CPU feature tables for SM4 and PMULL.

### Integration Points
Provides `gcm-sm4-ce` with priority 400 via the kernel crypto API and depends on base CE key helpers from `sm4-ce.h`.

### Risks
Risks include ignoring an initial skcipher walk error before `gcm_crypt()`, AAD buffer edge cases, final-segment length signaling, tag compare coverage for short auth sizes, and CPU feature combinations where SM4 exists without PMULL.

### Test Signals
Run GCM vectors across auth sizes, AAD lengths around block boundaries, payload lengths 0/1/15/16/17/64, fragmented walks, in-place decrypt with bad tags, and module auto-load on CPUs advertising both SM4 and PMULL.
