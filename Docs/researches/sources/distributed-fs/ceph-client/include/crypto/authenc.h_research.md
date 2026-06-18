# sources/distributed-fs/ceph-client/include/crypto/authenc.h

Purpose: key parsing helpers for authenc-style AEAD wrappers, including IPsec and Kerberos variants.

Important APIs/types/functions: `CRYPTO_AUTHENC_KEYA_*`, `struct crypto_authenc_key_param`, `struct crypto_authenc_keys`, `crypto_authenc_extractkeys`, and `crypto_krb5enc_extractkeys`.

Control flow: callers pass a composite key blob; extraction helpers split it into authentication and encryption key pointers/lengths.

State and persistence: output key struct points into caller-provided key memory, so lifetime follows the original key buffer.

Dependencies and integration points: used by `authenc(hmac(...), cipher)` and related AEAD templates.

Risks: malformed key blobs can produce wrong key boundaries. Because outputs are borrowed pointers, callers must not free or overwrite the backing key prematurely.

Test signals: authenc key decode vectors, invalid length/parameter tests, and IPsec/Kerberos AEAD integration tests.
