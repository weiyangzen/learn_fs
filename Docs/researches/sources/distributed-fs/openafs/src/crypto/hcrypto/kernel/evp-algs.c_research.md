# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/evp-algs.c

This file provides a deliberately small EVP provider for kernel hcrypto. It implements AES-128-CBC, AES-256-CBC, and SHA1, and returns `NULL` for many unsupported digest and cipher algorithms.

Important functions are `aes_init`, `aes_do_cipher`, `EVP_hckernel_aes_128_cbc`, `EVP_hckernel_aes_256_cbc`, `EVP_hckernel_sha1`, unsupported stubs such as `EVP_hckernel_sha256`, `EVP_hckernel_rc4`, `EVP_hckernel_des_cbc`, and `hcrypto_validate`. `aes_init` sets an AES encrypt/decrypt key based on `ctx->encrypt`; `aes_do_cipher` uses CFB8 if the flag is set, otherwise CBC, updating `ctx->iv`.

State is per-`EVP_CIPHER_CTX` cipher data and IV mutation; provider descriptors are static const. Dependencies are kernel `config.h`, hcrypto EVP/AES/SHA headers. Integration is RFC3961 kernel algorithm selection, primarily AES CTS/HMAC-SHA1 paths. Risks are unsupported algorithms causing NULL dereference if callers do not check, no AES-192 or CFB8 provider despite code support in `aes_do_cipher`, and reliance on hcrypto struct layouts. Test signals are AES128/AES256 Kerberos crypto vectors and SHA1 checksum vectors in kernel mode.
