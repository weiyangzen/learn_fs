# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_ecdsa.c

Purpose: provides static DER/PKCS#7 test vectors and the ECDSA-specific entry point for the FIPS certificate verification selftest.

Important APIs/types/functions: `certs_selftest_ecdsa_keys` contains a P-256 ECDSA certificate. `certs_selftest_ecdsa_data` contains detached test data. `certs_selftest_ecdsa_sig` contains a PKCS#7 ECDSA/SHA-256 signature. `fips_signature_selftest_ecdsa()` passes these buffers to `fips_signature_selftest()`.

Control flow: when compiled, late init in `selftest.c` calls this function. The shared runner loads the certificate, parses the PKCS#7 signature, supplies data, verifies, and validates trust.

State and persistence: test vectors are `__initconst`, so they can be discarded after init. No persistent state remains after successful selftest.

Dependencies and integration points: depends on ECDSA P-256 public-key verification, SHA-256 hashing, PKCS#7 parser/verifier, and X.509 parser support.

Risks: DER byte arrays are opaque and easy to corrupt. Algorithm availability must match vector choices. The certificate validity dates are intentionally far future; changes to time validation policy could affect selftest assumptions.

Test signals: boot success with ECDSA selftest enabled, failure when ECDSA or SHA-256 support is absent, and vector corruption causing panic.
