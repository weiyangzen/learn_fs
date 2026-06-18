## sources/distributed-fs/ceph-client/arch/arm64/crypto/ghash-ce-glue.c

### Purpose
Registers AES-GCM and RFC4106 AES-GCM AEAD algorithms using ARMv8 AES/PMULL assembly and handles scatterlist, AAD, tag, and key-table setup.

### Important APIs, Types, And Functions
Defines `struct arm_ghash_key` and `struct gcm_aes_ctx`. Key functions are `ghash_reflect`, `gcm_aes_setkey`, `gcm_update_mac`, `gcm_calculate_auth_mac`, `gcm_encrypt`, `gcm_decrypt`, `rfc4106_setkey`, `rfc4106_encrypt`, `rfc4106_decrypt`, and module init/exit. It calls `pmull_ghash_update_p64`, `pmull_gcm_encrypt`, and `pmull_gcm_decrypt`.

### Control Flow
Setkey prepares AES encryption keys, computes `H = AES_K(0)`, reflects it, and derives `H^1..H^4`. AAD is walked and padded into GHASH. Encrypt/decrypt initialize IV counter block 2, walk payload scatterlists, bounce short final chunks into a 16-byte buffer, call assembly for each segment, and append or compare the authentication tag. RFC4106 prepends the stored nonce and validates IPsec AAD shape.

### State, Persistence, And Dependencies
Transform state contains AES round keys, RFC4106 nonce, and GHASH powers. Request state includes digest, IV, length block, tag buffer, and skcipher walk state. Dependencies include AES, GHASH, GCM, gf128 multiplication, scatterwalk, AEAD/skcipher internals, CPU feature checks, unaligned helpers, and `asm/simd.h`.

### Integration Points
Exports high-priority `gcm(aes)` and `rfc4106(gcm(aes))` drivers to the kernel crypto API when ASIMD and PMULL are present. Ceph or lower network/storage layers can consume these through standard AEAD allocation.

### Risks
AAD buffering and partial payload handling are the highest-risk areas. Incorrect authsize validation, nonce length assumptions, IV counter reuse, failed tag comparison propagation, or missing CPU feature gates would cause security or crash bugs.

### Test Signals
Run crypto selftests for GCM/RFC4106, NIST vectors, malformed tags, all legal auth sizes, AAD lengths around 0/15/16/17/0xff00, fragmented source/destination lists, and CPU-feature-negative module init.
