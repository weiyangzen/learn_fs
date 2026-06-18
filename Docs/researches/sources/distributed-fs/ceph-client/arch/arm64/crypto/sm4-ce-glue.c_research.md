## sources/distributed-fs/ceph-client/arch/arm64/crypto/sm4-ce-glue.c

### Purpose
Registers ARMv8 Crypto Extension SM4 skcipher and shash algorithms for ECB, CBC, CBC-CTS, CTR, XTS, CMAC, XCBC, and CBC-MAC.

### Important APIs, Types, And Functions
Context types include `struct sm4_xts_ctx`, `struct sm4_mac_tfm_ctx`, and `struct sm4_mac_desc_ctx`. Major functions include `sm4_setkey`, `sm4_xts_setkey`, `sm4_ecb_do_crypt`, CBC/CTS/CTR/XTS crypt helpers, `sm4_cbcmac_setkey`, `sm4_cmac_setkey`, `sm4_xcbc_setkey`, `sm4_mac_init`, `sm4_mac_update`, `sm4_cmac_finup`, and `sm4_cbcmac_finup`. It exports `sm4_ce_expand_key`, `sm4_ce_crypt_block`, and `sm4_ce_cbc_enc`.

### Control Flow
Setkey expands SM4 CE keys. Skcipher helpers walk virtual scatterlists, pass whole-block work to assembly, and handle CTR tails with generic block encryption. XTS validates two keys and performs tweak handling in assembly. MAC setup derives subkeys for CMAC/XCBC; update accumulates full blocks through assembly and finup handles padding/final encryption before returning digests.

### State, Persistence, And Dependencies
State is per-transform expanded keys and per-request IV/digest buffers. No filesystem persistence exists. Dependencies include skcipher/hash internals, `crypto/sm4.h`, `crypto/xts.h`, `crypto/utils.h`, `crypto/b128ops.h`, scatterwalk, CPU features, and `asm/simd.h`.

### Integration Points
Provides high-priority `sm4-ce` mode drivers and exported helpers used by CCM/GCM modules. These drivers are consumed through the generic kernel crypto API.

### Risks
High-risk areas are CTS/XTS tail semantics, CMAC/XCBC subkey generation and padding, update/finup block retention, IV persistence, and correct cleanup if registering shash algorithms fails after skciphers succeeded.

### Test Signals
Run SM4 mode vectors for every registered algorithm, XTS weak-key rejection, CTS partial final lengths, CTR non-block tails, MAC incremental updates with every split point, module init failure injection, and selftests comparing against generic SM4.
