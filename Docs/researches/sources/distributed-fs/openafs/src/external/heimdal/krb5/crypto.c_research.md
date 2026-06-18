# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto.c

Purpose: implements the generic Heimdal krb5 crypto API: enctype/checksum lookup, key scheduling, checksums, encryption/decryption, IOV crypto, key derivation, crypto context lifecycle, PRF, weak-crypto toggles, and length/overhead helpers.

Important APIs/types/functions: key lifecycle includes `krb5_generate_random_keyblock()`, `krb5_random_to_key()`, `krb5_crypto_init()`, `krb5_crypto_destroy()`, `_krb5_free_key_data()`, `_key_schedule()`, `_get_derived_key()`, and `krb5_derive_key()`. Checksum APIs include `_krb5_internal_hmac()`, `_krb5_SP_HMAC_SHA1_checksum()`, `krb5_create_checksum()`, `krb5_verify_checksum()`, and IOV checksum helpers. Encryption APIs include `krb5_encrypt_ivec()`, `krb5_decrypt_ivec()`, `krb5_encrypt_iov_ivec()`, `krb5_decrypt_iov_ivec()`, and `EncryptedData` wrappers.

Control flow: public APIs find descriptor records from `crypto-algs.c` and dispatch by flags. Derived enctypes build confounder plus plaintext, checksum with integrity usage, encrypt with encryption usage, and append trailer. Old enctypes put checksum inside encrypted data. Special RC4 delegates framing to the RC4 algorithm. Decryption reverses each format and verifies integrity before returning plaintext.

State and persistence behavior: `krb5_crypto` stores the selected enctype, copied base key, optional key schedule, and an expandable cache of derived keys by usage. Global descriptor flags can be mutated by enable/disable APIs, affecting later callers process-wide.

Dependencies and integration points: integrates all algorithm descriptors, ASN.1 `Checksum`/`EncryptedData` types, EVP helpers, n-fold, store-int, random generation, `ct_memcmp`, and krb5 error-message APIs.

Risks: this is security-critical code with many size and padding invariants. Some allocation paths use `ENOMEM` directly, some internal failures abort, and `_get_derived_key()` does not check every copy/derive return before publishing a cache entry. Descriptor flag mutation is global and not synchronized. IOV code copies buffers into temporary contiguous memory and must preserve data/sign-only ordering.

Test signals: known-answer vectors for each enctype, round-trip encrypt/decrypt with bad-integrity cases, IOV header/padding/trailer sizing, checksum type mismatch handling, derived-key cache reuse, weak-crypto toggles, PRF/CF2 tests, and malformed ciphertext size rejection.
