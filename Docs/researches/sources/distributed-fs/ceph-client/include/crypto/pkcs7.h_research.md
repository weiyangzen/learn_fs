# sources/distributed-fs/ceph-client/include/crypto/pkcs7.h

Purpose: declares the kernel PKCS#7 message parsing and verification interface.

Important APIs, types, and flow: `pkcs7_parse_message()` decodes DER data to a `pkcs7_message`; `pkcs7_free_message()` releases it. Accessors retrieve content data or message digest. Verification APIs supply detached data, verify signatures at a given usage time, and validate trust against a keyring.

State and persistence: parsed messages hold allocated decoded ASN.1/signature/content state until freed. Trust decisions use keyring state but this header declares no persistence.

Dependencies and integration: depends on kernel keyrings, public-key verification, ASN.1/PKCS#7 parser implementation, and consumers such as module signing, firmware signing, and IMA.

Risks and test signals: risks include DER parser robustness, detached-content lifetime, certificate-chain policy, time validity, and digest mismatch handling. Signals include PKCS#7 signature vectors, malformed ASN.1 fuzzing, keyring trust tests, detached data tests, expired/not-yet-valid certificate tests, and digest extraction tests.
