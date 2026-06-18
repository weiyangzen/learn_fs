<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc6803_camellia.c -->
# sources/distributed-fs/ceph-client/crypto/krb5/rfc6803_camellia.c

Purpose: Implements the RFC6803 Camellia Kerberos profile and defines Camellia128/256 CTS-CMAC enctypes.

Important APIs/types/functions: `rfc6803_calc_KDF_FEEDBACK_CMAC()` implements KDF-FEEDBACK-CMAC with `K(i-1) || i || constant || 0x00 || k`. `rfc6803_calc_PRF()` derives `Kp` using the `prf` constant and CMACs the octet string. `rfc6803_crypto_profile` reuses shared authenc encryption and RFC3961 MIC helpers while using CMAC KDF/PRF methods. `krb5_camellia128_cts_cmac` and `krb5_camellia256_cts_cmac` define the enctype metadata.

Control flow: KDF allocates a CMAC shash, sets the protocol key, constructs the feedback input buffer, iterates until the result buffer is filled, and copies each CMAC segment. PRF derives a PRF key then computes CMAC over the input. Public API paths dispatch here through the enctype profile.

State and persistence behavior: Only static const profile/enctype metadata persists. Temporary CMAC descriptors, feedback buffers, and derived keys are allocated per call and freed sensitively.

Dependencies and integration points: Uses `cmac(camellia)`, `krb5enc(cmac(camellia),cts(cbc(camellia)))`, shared authenc packaging, and RFC3961 encrypt/MIC helpers. Kconfig selects Camellia, CMAC, CTS, CBC, and authenc.

Risks: Feedback KDF buffer layout and bit-length encoding must exactly match RFC6803. The result length is profile-driven; wrong `Kc_len`, `Ke_len`, or `Ki_len` silently produces incompatible keys. Because encryption/MIC helpers are shared with RFC3961, changes there affect Camellia too.

Test signals: RFC6803 Camellia KDF, PRF, encryption, and checksum vectors; 128/256 lookup and transform allocation; scatterlist encrypt/decrypt round trips; and failure tests for missing CMAC/Camellia providers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/krb5/rfc6803_camellia.c -->
