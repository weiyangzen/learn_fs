# sources/distributed-fs/ceph-client/crypto/krb5enc.c

Purpose: defines the `krb5enc` AEAD template for Kerberos 5 RFC 3961 simplified profiles. It composes an ahash authentication algorithm and an skcipher encryption algorithm into a crypto API AEAD instance whose checksum is appended after the encrypted payload.

Important APIs, types, and functions: `crypto_krb5enc_extractkeys()` decodes the auth/encryption key blob and is exported. `krb5enc_setkey()`, `krb5enc_encrypt()`, `krb5enc_decrypt()`, `krb5enc_init_tfm()`, `krb5enc_exit_tfm()`, and `krb5enc_create()` implement the template. Key state lives in `struct krb5enc_ctx`; per-instance spawns and request offsets live in `struct krb5enc_instance_ctx`; request-local SG arrays and tail storage live in `struct krb5enc_request_ctx`.

Control flow: instance creation validates AEAD attributes, grabs ahash and skcipher children, names the instance as `krb5enc(auth,enc)`, and sizes request storage for either child request plus two digests. Setkey decodes an `rtattr` key blob with `CRYPTO_AUTHENC_KEYA_PARAM`, then sets the auth key and encryption key. Encryption hashes associated data plus plaintext, writes the digest after the encrypted region, and dispatches the skcipher over data after `assoclen`. Decryption decrypts the ciphertext portion first, hashes associated data plus decrypted plaintext, then compares the stored checksum with `crypto_memneq()`.

State and persistence: transform state contains child `crypto_ahash` and `crypto_skcipher` handles. Per-request state contains forwarded scatterlists, child requests, and digest scratch space. No state persists beyond crypto object lifetime.

Dependencies and integration points: integrates with the crypto template registry as `MODULE_ALIAS_CRYPTO("krb5enc")`. It uses `scatterwalk_ffwd()`, `scatterwalk_map_and_copy()`, `crypto_grab_ahash()`, `crypto_grab_skcipher()`, `aead_register_instance()`, and rtnetlink attribute encoding compatible with `authenc`.

Risks: key blob parsing is sensitive to `rtattr` alignment and CPU-endian versus big-endian fields. `reqoff = 2 * digestsize` must keep `ahreq->result` and copied message hash separate. Length arithmetic around `assoclen`, `cryptlen`, and `authsize` is security-sensitive. Asynchronous completions must complete only after chained hash/cipher work has reached a terminal state.

Test signals: testmgr and Kerberos selftests should cover setkey blob parsing, separate and in-place source/destination buffers, async child algorithms, wrong checksums returning `-EBADMSG`, truncated buffers, zero-length plaintext, and exact instance naming for algorithm lookup.
