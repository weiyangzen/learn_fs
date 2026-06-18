<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/hmac_s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/crypto/hmac_s390.c

Purpose: Implements CPACF-accelerated clear-key HMAC-SHA224/256/384/512 for the synchronous hash API.

Important APIs/types/functions: Defines `struct s390_hmac_ctx`, `union s390_kmac_gr0`, and `struct s390_kmac_sha2_ctx`. Key functions are `hash_data()`, `hash_key()`, `s390_hmac_sha2_setkey()`, `s390_hmac_sha2_init()`, `s390_hmac_sha2_update()`, `s390_hmac_sha2_finup()`, `s390_hmac_sha2_digest()`, export/import helpers, and module init/exit over `s390_hmac_algs[]`.

Control flow: Init requires KLMD SHA-256 and SHA-512 support for selftest/hash-key support, then registers only HMAC variants with matching KMAC function codes. Setkey hashes overlong keys, creates inner/outer padded key blocks, and stores them in transform context. Init seeds descriptor state from ipad, update streams data through KMAC state, and final/finup produces the digest using opad state.

State and persistence: Per-transform context stores ipad/opad-derived state and digest metadata. Per-request descriptor state holds partial SHA2/KMAC state across update/final. Registered flags track cleanup ordering.

Dependencies and integration points: Integrates with `crypto_shash`, CPACF KMAC/KLMD wrappers, SHA2 state sizes, module CPU feature matching, and crypto selftests.

Risks: Export/import compatibility must preserve in-progress HMAC state exactly. Key normalization and block-size handling differ across SHA256-family and SHA512-family variants. Registration requires both KLMD families even if only some HMAC variants are used.

Test signals: Crypto manager HMAC vectors for SHA224/256/384/512, incremental update/export/import tests, overlong and zero-length keys, partial CPU feature masks, and module unload tests.

Source read size: 426 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/crypto/hmac_s390.c -->
