# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-aes.c

Purpose: defines Heimdal AES Kerberos encryption and checksum descriptors for AES128/AES256 CTS with HMAC-SHA1-96.

Important APIs/types/functions: static `_krb5_key_type` records `keytype_aes128` and `keytype_aes256` specify key sizes, EVP CBC ciphers, AES salts, and schedule cleanup. Exported checksum descriptors `_krb5_checksum_hmac_sha1_aes128` and `_krb5_checksum_hmac_sha1_aes256` use `_krb5_SP_HMAC_SHA1_checksum`. Exported encryption descriptors `_krb5_enctype_aes128_cts_hmac_sha1` and `_krb5_enctype_aes256_cts_hmac_sha1` use `_krb5_evp_encrypt_cts`. `AES_PRF()` implements the RFC3961-style AES PRF.

Control flow: generic crypto code selects these descriptors from `_krb5_etypes`, schedules the key with `_krb5_evp_schedule()`, derives usage-specific keys, computes HMAC-SHA1 checksums, and encrypts with CTS. `AES_PRF()` hashes input with the enctype checksum, derives a `"prf"` key, encrypts the first block of the digest with an all-zero IV, and returns one block.

State and persistence behavior: no module-global mutable state beyond exported descriptor records. Per-context state lives in `krb5_crypto` key schedules and derived-key cache managed by `crypto.c`.

Dependencies and integration points: depends on OpenSSL/hcrypto EVP AES CBC functions, `krb5_derive_key()`, `krb5_data_alloc/free()`, and the generic descriptor tables in `crypto-algs.c`.

Risks: `AES_PRF()` aborts on internal failures after allocation or derivation instead of returning all errors. Correctness depends on `_krb5_evp_encrypt_cts()` handling CTS framing and on checksum truncation to 12 bytes. AES descriptors set padsize 1, so length validation is mostly in CTS code.

Test signals: round-trip AES128/AES256 encryption for one block, partial final block, multi-block CTS, keyed checksum verification, PRF known-answer tests, and derived key tests.
