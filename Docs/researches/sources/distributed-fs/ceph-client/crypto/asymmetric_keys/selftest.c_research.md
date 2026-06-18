# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/selftest.c

Purpose: runs late-init FIPS-oriented certificate/PKCS#7 signature verification selftests for configured RSA and ECDSA vectors.

Important APIs/types/functions: `fips_signature_selftest()` creates a temporary keyring, loads DER X.509 certificates with `x509_load_certificate_list()`, parses a PKCS#7 detached signature, supplies test data, verifies it as a module signature, validates trust against the temporary keyring, frees the message, and releases the keyring. `fips_signature_selftest_init()` calls RSA and ECDSA variant hooks.

Control flow: `late_initcall()` runs after core initialization. Failures use `panic()`, making this a hard boot gate when enabled. Variant functions are compiled as real calls or inline no-ops through `selftest.h`.

State and persistence: state is temporary keyring and parsed PKCS#7 memory. No test result is persisted; success is absence of panic.

Dependencies and integration points: depends on X.509 loader, PKCS#7 parser/verifier/trust, current credentials, keyring allocation, and configured selftest vector files.

Risks: enabled selftests can prevent boot if required crypto algorithms are missing. The error message after parse failure prints `ret`, which may not contain the parse error pointer value. The temporary keyring must be released on success; panic paths intentionally stop.

Test signals: boot with RSA-only, ECDSA-only, both, and neither; deliberate malformed vector failure; missing crypto algorithm configs; and successful late-init logs.
