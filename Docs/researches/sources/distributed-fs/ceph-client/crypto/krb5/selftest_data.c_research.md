# sources/distributed-fs/ceph-client/crypto/krb5/selftest_data.c

Purpose: provides the static Kerberos 5 test-vector tables consumed by `selftest.c`. The vectors cover RFC 8009 AES-SHA2, RFC 6803 Camellia, key derivation, encryption layouts, and MIC calculation.

Important APIs, types, and data: exports four null-terminated arrays: `krb5_prf_tests[]`, `krb5_key_tests[]`, `krb5_enc_tests[]`, and `krb5_mic_tests[]`. Entries use `struct krb5_prf_test`, `struct krb5_key_test`, `struct krb5_enc_test`, and `struct krb5_mic_test` fields from `internal.h`, including `.etype`, `.name`, `.key`, `.Kc`, `.Ke`, `.Ki`, `.K0`, `.usage`, `.plain`, `.conf`, `.ct`, and `.mic`.

Control flow: this file has no executable control flow. Runtime behavior is produced when `krb5_selftest()` walks each array until it sees an entry with no `.name`. Hex strings are decoded by `load_buf()`; strings whose first byte is a single quote are treated as literal byte data after the quote.

State and persistence: all vectors are read-only static kernel data. There is no mutable state or persistence. The sentinel `{/* END */}` entries are part of the API contract with the test runner.

Dependencies and integration points: depends on Kerberos enctype constants such as `KRB5_ENCTYPE_AES128_CTS_HMAC_SHA256_128`, `KRB5_ENCTYPE_AES256_CTS_HMAC_SHA384_192`, `KRB5_ENCTYPE_CAMELLIA128_CTS_CMAC`, and `KRB5_ENCTYPE_CAMELLIA256_CTS_CMAC`. The content is tied to expected behavior in `krb5_kdf.c`, RFC 3961 simplified profiles, AES2, and Camellia Kerberos implementations.

Risks: a typo in any vector can look like a crypto regression. Literal string entries are easy to misread because the leading quote is a marker, not data. The vectors exercise selected RFC examples, not exhaustive key usages, message sizes, or all Kerberos enctypes.

Test signals: selftest coverage should detect format drift in vector structs, missing sentinels, incorrect enctype registration, and changed output lengths. Adding new enctypes should include PRF, derivation, encryption, and MIC vectors here so `selftest.c` can validate the whole profile.
