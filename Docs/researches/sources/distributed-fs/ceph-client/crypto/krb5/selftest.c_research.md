# sources/distributed-fs/ceph-client/crypto/krb5/selftest.c

Purpose: implements in-kernel selftests for the Kerberos 5 crypto library. It validates PRF output, key derivation, encryption/decryption, and MIC generation/verification against static vectors supplied by `selftest_data.c`.

Important APIs, types, and functions: `krb5_selftest()` is the exported entry point. `prep_buf()`, `load_buf()`, and `clear_buf()` manage decoded test buffers. `krb5_test_one_prf()`, `krb5_test_one_key()`, `krb5_test_one_enc()`, and `krb5_test_one_mic()` drive each vector class. The code uses `struct krb5_buffer`, `struct krb5_enctype`, `struct crypto_aead`, `struct crypto_shash`, and single-entry `scatterlist` objects.

Control flow: `krb5_selftest()` allocates a 4096-byte scratch buffer, iterates null-terminated vector arrays, and skips unsupported enctypes via `-EOPNOTSUPP`. PRF tests decode key/octet/expected PRF and call `calc_PRF`. Key tests derive Kc, Ke, and Ki from a base key. Encryption tests build a confounder-plus-plaintext buffer, prepare either raw base-key or already-derived keys, encrypt, compare ciphertext, then decrypt and verify returned offsets and plaintext. MIC tests prepare checksum keys, generate a MIC at the front of the buffer, then verify it and check payload offsets.

State and persistence: all buffers and crypto transforms are per-test transient allocations. Test state persists only in stack/local heap objects and kernel logs; no filesystem state is written. `VALID()` marks malformed vectors, while `CHECK()` marks implementation mismatches.

Dependencies and integration points: depends on `crypto_krb5_find_enctype()`, Kerberos profile callbacks, `crypto_krb5_prepare_encryption()`, `crypto_krb5_encrypt()`, `crypto_krb5_decrypt()`, `crypto_krb5_get_mic()`, `crypto_krb5_verify_mic()`, `hex2bin()`, and the vector declarations in `internal.h`.

Risks: the 4096-byte scratch buffer assumes all current vectors fit; larger vectors would need sizing changes. The quote-prefixed literal path in `load_buf()` stores `len - 1` bytes including the trailing string content exactly as typed. Tests check deterministic confounder vectors rather than randomness. Error logging exposes vector bytes, which is acceptable for test data but not secret production data.

Test signals: module load/selftest logs should show all supported enctypes running and final success. Good regression cases include zero-length plaintext, sub-block/block/exceed-block CTS paths, both K0 and derived-key inputs, unsupported enctype skipping, checksum verify offset handling, and failure injection for malformed hex or mismatched expected data.
