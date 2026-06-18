# sources/distributed-fs/ceph-client/crypto/sha1.c

Purpose: registers library-backed SHA-1 and HMAC-SHA1 shash algorithms with compatible export/import formats.

Important APIs, types, and functions: exports `sha1_zero_message_hash`. SHA-1 wrappers call `sha1_init()`, `sha1_update()`, `sha1_final()`, and `sha1()`. HMAC wrappers call `hmac_sha1_preparekey()`, `hmac_sha1_init()`, `hmac_sha1_update()`, `hmac_sha1_final()`, and `hmac_sha1()`. Export/import helpers append the current partial-block byte count to a block-aligned library context.

Control flow: module init registers `sha1` and `hmac(sha1)`. Hash and HMAC requests delegate to the library. Export subtracts the partial bytes from `bytecount`, copies the context, and stores partial as one byte. Import copies the context and re-adds partial. HMAC import restores the outer state from the tfm key before importing the inner hash context.

State and persistence: per-request shash state lives in descriptor contexts; HMAC key state lives in tfm context. Zero-message hash is static exported data.

Dependencies and integration points: depends on `<crypto/sha1.h>` and crypto shash registration. Used by legacy protocols, HMAC templates, and PKCS#1 signature prefix support.

Risks: SHA-1 is collision-broken for signatures and should be compatibility-only, though HMAC-SHA1 remains different from raw collision resistance. Layout static assertions protect legacy state ABI. Importing HMAC state with a different key would be invalid because outer state comes from current tfm key.

Test signals: SHA-1 and HMAC-SHA1 known-answer vectors, zero-message digest, export/import at partial and block boundaries, algorithm aliases, and PKCS#1 verification with SHA-1.
