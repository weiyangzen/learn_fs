<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc8009_aes2.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc8009_aes2.c

Purpose: Implements the RFC8009 AES CTS HMAC-SHA2 Kerberos profile and defines AES128-SHA256 and AES256-SHA384 enctypes.

Important APIs/types/functions: `rfc8009_calc_KDF_HMAC_SHA2()` builds `0x00000001 || label || 0x00 || context || k`, HMACs it, and truncates to the requested key length. `rfc8009_calc_PRF()`, `rfc8009_calc_Ke()`, and `rfc8009_calc_Ki()` derive PRF, encryption, checksum, and integrity keys using RFC8009 labels/usages. `rfc8009_encrypt()` and `rfc8009_decrypt()` include the starting IV as associated data before delegating to authenc. `rfc8009_crypto_profile` binds these methods with shared key packaging and MIC helpers. The two exported enctype objects define SHA256/128-bit checksum and SHA384/192-bit checksum variants.

Control flow: Key derivation allocates an HMAC shash, verifies digest capacity, constructs the KDF input, computes one HMAC block, and copies the requested prefix. Encryption writes a confounder if needed, chains a synthetic scatterlist containing the IV-sized associated-data buffer before the payload scatterlist, sets AEAD AD length, and encrypts in place. Decryption mirrors this and adjusts output offset/length after authentication succeeds.

State and persistence behavior: Static const profile/enctype metadata persists. Temporary HMAC, AEAD request, IV/AD, and derived-key buffers are allocated per operation and freed sensitively. The encrypted scatterlist is modified in place.

Dependencies and integration points: Uses `authenc(hmac(sha256|sha384),cts(cbc(aes)))`, shared authenc packaging, RFC3961 checksum helpers, and public Kerberos API dispatch. Kconfig selects SHA256, SHA512, HMAC, AES, CBC, CTS, and authenc.

Risks: The `ad` buffer is zero-filled by allocation and represents the starting IV associated data; changing initialization can break RFC8009 authentication. `hash_len` metadata is 20 in both enctype definitions despite SHA2 use, so tests should verify no code relies on that field incorrectly for RFC8009 paths. KDF label/context composition and checksum truncation are interoperability-critical.

Test signals: RFC8009 KDF/PRF/encrypt/checksum vectors, AES128-SHA256 and AES256-SHA384 lookup, bad checksum rejection, associated-data coverage tests that alter the starting IV, scatterlist segmentation, and missing SHA384/authenc provider errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc8009_aes2.c -->
