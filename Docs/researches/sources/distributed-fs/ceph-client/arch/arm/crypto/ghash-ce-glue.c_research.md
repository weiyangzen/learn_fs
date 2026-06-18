<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-glue.c -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-glue.c

## Purpose
C CryptoAPI AEAD glue for ARM PMULL AES-GCM and RFC4106(GCM(AES)) providers.

## Important APIs/types/functions
- Context `struct gcm_key` stores hash powers, AES round keys, round count, and RFC4106 nonce tail.
- Key/auth setup: `gcm_aes_setkey()`, `gcm_aes_setauthsize()`, `rfc4106_setkey()`, `rfc4106_setauthsize()`.
- MAC helpers: `ghash_reflect()`, `gcm_update_mac()`, `gcm_calculate_auth_mac()`.
- AEAD handlers: `gcm_encrypt()`, `gcm_decrypt()`, `rfc4106_encrypt()`, `rfc4106_decrypt()`.
- Registered drivers: `gcm-aes-ce` and `rfc4106-gcm-aes-ce`.

## Control flow
Key setup builds an AES encrypt key, encrypts the zero block to get GHASH H, precomputes reflected powers H through H^4, and stores round keys. Encryption walks AEAD data, authenticates AAD with GHASH, encrypts plaintext blocks while updating digest, finalizes tail/length/tag, writes the tag after ciphertext, and completes the walk. Decryption copies the received tag, authenticates/decrypts ciphertext, finalizes and verifies the tag, and returns `-EBADMSG` on failure. RFC4106 prepends the fixed nonce to request IV and excludes the explicit IV from authenticated payload length.

## State and persistence behavior
Per-tfm state stores AES and GHASH precomputation; per-request state stores digest, counter, stack buffers, and copied tag. Module registration persists providers until unload.

## Dependencies and integration points
Depends on CryptoAPI AEAD/skcipher walking, ARM NEON, HWCAP_NEON and HWCAP2_PMULL checks, AES library key layout, GF128 multiplication helpers, GCM/RFC4106 validation helpers, and `ghash-ce-core.S`.

## Risks and edge cases
Auth failure must not expose unauthenticated plaintext semantics to callers beyond CryptoAPI norms. The source as read contains a stray duplicated block-comment terminator in the encrypt tail comment area, which is a compile-risk signal if present. Scatterwalk page-boundary handling restarts NEON sections and must stay balanced. RFC4106 associated-data length validation is mandatory.

## Test signals
Run CryptoAPI AEAD vectors for valid/invalid tags, all allowed tag sizes, zero/nonzero AAD, partial tails, RFC4106 nonce/IV layouts, in-place buffers, scatterlist splits, and CPUs without PMULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/ghash-ce-glue.c -->
