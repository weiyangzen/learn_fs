## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/evp-cc.c

Purpose: Apple CommonCrypto-backed EVP provider for hcrypto. The entire implementation is compiled only under `__APPLE__` and returns EVP cipher/digest descriptors backed by CommonCrypto when the relevant CommonCrypto headers/features are available.

Important APIs/functions: exported provider functions include `EVP_cc_des_ede3_cbc`, `EVP_cc_des_cbc`, AES CBC/CFB8 variants, RC2 CBC variants, RC4/RC4-40, MD2/MD4/MD5/SHA1/SHA256 digests, and Camellia stubs. Internal `struct cc_key` owns a `CCCryptorRef`; `init_cc_key()` creates, resets, or releases/recreates cryptors; `cc_do_cipher()` calls `CCCryptorUpdate`; `cc_do_cfb8_cipher()` manually implements CFB8 on top of AES ECB; `cc_cleanup()` releases the cryptor.

Control flow: descriptor-returning functions return pointers to static `EVP_CIPHER` or `hc_evp_md` structs when compile-time support exists, else `NULL`. CBC/stream initialization calls `init_cc_key()` with selected `CCAlgorithm`, options, key length, and IV. CFB8 initialization copies the IV into the EVP context and creates an AES ECB encryptor regardless of encrypt/decrypt direction; per-byte processing encrypts the IV, XORs one byte, then shifts ciphertext into IV.

State and persistence: each EVP context stores provider state in `ctx->cipher_data` as `struct cc_key`. The cryptor reference persists until cleanup or reinitialization. IV is persisted in `ctx->iv`, especially for manual CFB8. Digest descriptors use CommonCrypto digest context sizes but no provider global mutable state.

Dependencies: Apple-only `CommonCrypto/CommonDigest.h` and `CommonCrypto/CommonCryptor.h`, `evp.h`, and `evp-cc.h`. RC2 support is additionally guarded by `COMMONCRYPTO_SUPPORTS_RC2`.

Integration points: selected by hcrypto's EVP layer on Apple platforms as a provider alternative to built-in implementations. `evp-cc.h` declares this provider surface. Camellia functions intentionally return `NULL` because CommonCrypto does not provide Camellia here.

Risks: non-Apple builds compile no code from this file, so callers must tolerate missing provider functions depending on build configuration. Many functions can return `NULL` at runtime based on feature macros. `cc_do_cipher()` copies input to output before `CCCryptorUpdate()` but then passes original input, making the pre-copy unnecessary and potentially misleading. CFB8 descriptor for AES-256 reports block size as `kCCBlockSizeAES128` rather than `1`, unlike AES-128 CFB8; this may affect EVP buffering semantics. No padding options are set, so CommonCrypto behavior must match hcrypto EVP expectations.

Test signals: Apple build tests for non-NULL providers, CommonCrypto CBC/CFB8 vectors, cryptor reset with new IV and null key, cleanup/reinit leak checks, fallback `NULL` behavior with feature macros disabled, digest known-answer vectors, and Camellia provider null expectations.
