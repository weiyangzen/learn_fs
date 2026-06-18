<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3961_simplified.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc3961_simplified.c

Purpose: Implements the RFC3961 simplified Kerberos crypto profile: n-fold, DK/DR derivation, PRF, authenc key packaging, AEAD encrypt/decrypt wrappers, and checksum MIC helpers.

Important APIs/types/functions: `crypto_shash_update_sg()` hashes a scatterlist range. `rfc3961_nfold()` implements the RFC n-fold operation. `rfc3961_calc_DK()` derives keys by repeated encryption of folded constants and optional random-to-key conversion. `rfc3961_calc_PRF()` hashes input, derives a `prf` key, and encrypts the truncated hash. `authenc_derive_encrypt_keys()` and `authenc_load_encrypt_keys()` package Ke/Ki for `authenc`. `rfc3961_derive_checksum_key()` and `rfc3961_load_checksum_key()` prepare Kc. `krb5_aead_encrypt/decrypt()` perform confounder insertion, AEAD processing, and boundary adjustment. `rfc3961_get_mic()` and `rfc3961_verify_mic()` calculate/verify keyed checksums.

Control flow: Key derivation folds the constant to block size, repeatedly encrypts blocks with the base key until enough raw key bytes exist, then either copies or random-to-key converts the result. Encryption expects data immediately after the confounder, optionally writes a random confounder, zero-pads if needed, then encrypts/checksums the secure region through AEAD. MIC generation hashes optional metadata plus data and writes the checksum immediately before data; verification recomputes and compares against the stored checksum.

State and persistence behavior: No global mutable state. Sensitive key, digest, request, and confounder buffers are temporary and freed with sensitive zeroing. Scatterlist data is modified in place for encryption/MIC insertion and offsets/lengths are updated on successful decrypt/verify.

Dependencies and integration points: Uses kernel random bytes, scatterlist helpers, sync skcipher, shash, authenc key parameter format, and the Kerberos profile table. It backs AES-SHA1 and also provides shared encrypt/MIC helpers for Camellia and AES-SHA2 profiles.

Risks: Scatterlist offset arithmetic must not authenticate or copy outside the intended buffer. `memcmp()` is used for MIC comparison, which is acceptable only if timing side channels are not relevant in the calling context; crypto constant-time comparison would be safer. Error paths in `authenc_derive_encrypt_keys()` currently return after allocation on a failed Ke derivation without freeing `setkey->data`, relying on caller cleanup behavior. Exact RFC n-fold behavior is easy to break.

Test signals: RFC3961/RFC3962 known-answer vectors, n-fold vectors, DK/PRF/Kc/Ke/Ki derivation tests, encryption/decryption with and without preconfounded input, MIC metadata tests, short/invalid buffer rejection, scatterlist segmentation tests, and KMSAN/KASAN checks for temporary buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc3961_simplified.c -->
