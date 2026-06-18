## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-ccm-glue.c

### Purpose
Registers `ccm(sm4)` AEAD using ARMv8 SM4 Crypto Extensions and coordinates CCM formatting, AAD authentication, payload walking, and tag handling.

### Important APIs, Types, And Functions
Key functions are `ccm_setkey`, `ccm_setauthsize`, `ccm_format_input`, `ccm_calculate_auth_mac`, `ccm_crypt`, `ccm_encrypt`, `ccm_decrypt`, `sm4_ce_ccm_init`, and `sm4_ce_ccm_exit`. Assembly dependencies are `sm4_ce_expand_key`, `sm4_ce_crypt_block`, `sm4_ce_cbcmac_update`, `sm4_ce_ccm_enc`, `sm4_ce_ccm_dec`, and `sm4_ce_ccm_final`.

### Control Flow
Setkey validates the 128-bit SM4 key and expands CE round keys. Encrypt/decrypt call `ccm_format_input()` to build B0 and encode message length, then initialize a skcipher walk. `ccm_crypt()` preserves CTR0, increments the working counter, optionally authenticates AAD, passes whole walk chunks to assembly while retaining tails for the final segment, finalizes the MAC, and appends or checks the tag.

### State, Persistence, And Dependencies
Per-transform state is `struct sm4_ctx`; per-request state is MAC, CTR0, walk IV, and scatterlist cursor. No persistent storage exists. Dependencies include AEAD/skcipher internals, scatterwalk, `crypto/sm4.h`, `crypto_xor`, and `asm/simd.h`.

### Integration Points
Provides a `cra_priority` 400 `ccm-sm4-ce` AEAD driver gated by `module_cpu_feature_match(SM4)`.

### Risks
CCM has strict length and auth-size rules: bad `L` validation, assoclen encoding, final tail treatment, or non-constant tag comparison would be security-sensitive. All assembly calls require a valid kernel SIMD context.

### Test Signals
Exercise auth sizes 4 through 16, invalid odd/short auth sizes, IV `L` values 2..8 and invalid/out-of-range payload lengths, AAD length transitions at 0xff00, scatterlist fragmentation, and decrypt failures returning `-EBADMSG`.
