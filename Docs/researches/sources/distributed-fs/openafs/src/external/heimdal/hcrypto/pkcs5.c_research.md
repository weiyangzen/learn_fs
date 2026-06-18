# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/pkcs5.c

Purpose: implements PBKDF2-HMAC-SHA1 for PKCS#5 v2 style password-to-key derivation.

Important APIs/types/functions: `PKCS5_PBKDF2_HMAC_SHA1(password, password_len, salt, salt_len, iter, keylen, key)` derives arbitrary-length output using `EVP_sha1()` and `HMAC()`.

Control flow: allocates one buffer holding the current checksum plus `salt || block_index`, loops over derived key blocks, computes U1 as HMAC(password, salt || INT(block)), copies the requested prefix into output, then iteratively computes U2..Uiter and XORs each into the output block. The block counter is encoded big-endian and increments for each output chunk.

State and persistence: only temporary heap storage is used; derived key bytes are written to caller memory. The temporary buffer is freed but not explicitly zeroed before free.

Dependencies and integration points: depends on `evp.h`, `hmac.h`, and `roken`. The API is declared from `evp.h` and used by callers needing OpenSSL-compatible PBKDF2-SHA1.

Risks and test signals: `iter == 0` is not rejected, temporary key material is not scrubbed, and malloc failure is the only explicit error path. Tests should cover RFC 6070 PBKDF2-HMAC-SHA1 vectors, multi-block output, short output, empty salt/password, high iteration counts, and invalid zero-iteration policy.
