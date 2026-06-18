# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/Kconfig

Purpose: defines build-time configuration for Linux asymmetric key support, public-key subtype support, X.509/PKCS#8/PKCS#7 parsers, PE signature verification, and optional FIPS signature selftests.

Important APIs/types/functions: `ASYMMETRIC_KEY_TYPE` enables the key type and depends on `KEYS`. `ASYMMETRIC_PUBLIC_KEY_SUBTYPE` selects MPI, hash info, akcipher, sig, and hash support. Parser options include `X509_CERTIFICATE_PARSER`, `PKCS8_PRIVATE_KEY_PARSER`, and `PKCS7_MESSAGE_PARSER`. `PKCS7_WAIVE_AUTHATTRS_REJECTION_FOR_MLDSA` provides a compatibility waiver. `PKCS7_TEST_KEY`, `SIGNED_PE_FILE_VERIFICATION`, and `FIPS_SIGNATURE_SELFTEST*` enable test and verification modules.

Control flow: Kconfig selection controls which objects the Makefile builds and which verification features can be reached by module signing, firmware, kexec, and keyring code. Parser options layer on the public key subtype, and PKCS#7 depends on X.509 parsing.

State and persistence: no runtime state is stored here; it persists only as kernel configuration. Selected options change available key types, parsers, and verification behavior.

Dependencies and integration points: integrates with `crypto/asymmetric_keys/Makefile`, keyrings, ASN.1 decoder generation, OID registry, hash and signature algorithms, module/firmware verification, and FIPS boot requirements.

Risks: missing `select` dependencies can produce runtime `-ENOPKG` failures or build failures. The ML-DSA authattrs waiver is a policy-sensitive compatibility exception and should remain narrowly scoped.

Test signals: build matrices for built-in and modular parsers, configs with only X.509 or PKCS#7 enabled, PE verification configs, and FIPS selftest configs with RSA/ECDSA individually selected.
