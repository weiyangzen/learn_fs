## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-gcm-core.S

### Purpose
Implements SM4-GCM assembly using ARMv8 SM4 Crypto Extensions and PMULL GHASH acceleration.

### Important APIs, Types, And Functions
Exports `sm4_ce_pmull_ghash_setup`, `pmull_ghash_update`, `sm4_ce_pmull_gcm_enc`, and `sm4_ce_pmull_gcm_dec`. Important macro groups include `PMUL_128x128`, `PMUL_128x128_4x`, `REDUCTION`, `SM4_CRYPT_PMUL_128x128_BLK`, `SM4_CRYPT_PMUL_128x128_BLK3`, `inc32_le128`, and `GTAG_HASH_LENGTHS`.

### Control Flow
GHASH setup encrypts zero to derive H and stores H through H^4 in bit-reflected form. Standalone GHASH consumes four blocks at a time then single blocks. GCM encrypt processes four full blocks, then one-block and byte-tail paths, hashes ciphertext, finalizes optional length block and tag, and updates counter/MAC when not final. Decrypt hashes ciphertext before XORing keystream and uses a three-block fused loop to fit register pressure.

### State, Persistence, And Dependencies
Caller-owned state includes round keys, IV/counter, GHASH accumulator, GHASH table, source, destination, and optional length block. Dependencies include `sm4-ce-asm.h`, PMULL, SM4 CE instructions, and C glue that wraps the assembly in `scoped_ksimd()`.

### Integration Points
Used by `sm4-ce-gcm-glue.c` to implement `gcm(sm4)`. It shares `sm4_ce_expand_key` key material with other SM4 CE modes.

### Risks
GCM is sensitive to counter construction, GHASH bit reflection, reduction constants, partial-block padding, and final length block handling. Any mismatch between assembly finalization and C tag comparison is security-critical.

### Test Signals
Run RFC8998 SM4-GCM vectors with auth sizes 4, 8, and 12-16; test zero-length payload, AAD-only, short tails 1-15 bytes, counter carry cases, fragmented scatterlists, bad tags, and PMULL/SM4 CPU-feature module gates.
