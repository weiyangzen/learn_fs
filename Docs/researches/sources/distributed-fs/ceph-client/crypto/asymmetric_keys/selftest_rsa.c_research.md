# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest_rsa.c

Purpose: provides static DER/PKCS#7 test vectors and the RSA-specific entry point for the FIPS certificate verification selftest.

Important APIs/types/functions: `certs_selftest_rsa_keys` contains a 4096-bit RSA X.509 certificate. `certs_selftest_rsa_data` contains detached test data. `certs_selftest_rsa_sig` contains a PKCS#7 signature using RSA PKCS#1 v1.5 with SHA-256. `fips_signature_selftest_rsa()` invokes the shared runner.

Control flow: when enabled, late init calls this function before returning from `fips_signature_selftest_init()`. The generic selftest path exercises X.509 loading, PKCS#7 detached verification, and trust validation.

State and persistence: vectors are `__initconst` and discarded after init. Temporary keyring and parsed message state are owned by the shared runner.

Dependencies and integration points: depends on RSA, PKCS#1 signature encoding, SHA-256, PKCS#7, and X.509 parser support.

Risks: large byte arrays are maintenance-heavy and not self-describing. Missing RSA/PKCS#1/SHA-256 crypto support causes boot panic when selftest is enabled. Any parser policy change may require vector regeneration.

Test signals: boot with RSA selftest enabled, intentional vector mutation, missing crypto algorithm configs, and successful notice logs for the RSA selftest.
