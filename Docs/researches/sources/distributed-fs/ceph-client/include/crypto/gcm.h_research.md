# sources/distributed-fs/ceph-client/include/crypto/gcm.h

Purpose: AES-GCM helper constants, auth/tag validation, context, and direct AES-GCM routines.

Important APIs/types/functions: `GCM_AES_IV_SIZE`, RFC4106/RFC4543 IV sizes, `crypto_gcm_check_authsize`, `crypto_rfc4106_check_authsize`, `crypto_ipsec_check_assoclen`, `struct aesgcm_ctx`, `aesgcm_expandkey`, `aesgcm_encrypt`, and `aesgcm_decrypt`.

Control flow: callers validate tag and associated-data sizes, expand AES and GHASH keys into context, then encrypt/decrypt with IV, associated data, ciphertext/plaintext length, and tag. Decrypt returns bool authentication result.

State and persistence: context stores prepared GHASH key, AES encryption key, and auth tag size.

Dependencies and integration points: depends on AES and GF128 hash helpers. Used by direct GCM and IPsec GCM implementations.

Risks: GCM nonce reuse is catastrophic. Tag sizes are constrained and must be validated. Decrypt result must be checked before using plaintext.

Test signals: AES-GCM KATs, RFC4106/RFC4543 assoclen/tag tests, forgery rejection, and nonce/IV size checks at call sites.
