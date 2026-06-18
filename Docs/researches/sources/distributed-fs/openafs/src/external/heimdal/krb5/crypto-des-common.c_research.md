# sources/distributed-fs/openafs/src/external/heimdal/krb5/crypto-des-common.c

Purpose: provides helper routines shared by single-DES and triple-DES checksum/encryption implementations.

Important APIs/types/functions: `_krb5_xor()` XORs an 8-byte DES block in place. `_krb5_des_checksum()` builds DES-encrypted keyed MD4/MD5-style checksums when DES3 old enctypes or weak crypto are enabled. `_krb5_des_verify()` decrypts and verifies those checksums. `_krb5_checksum_rsa_md5` exports the unkeyed RSA-MD5 checksum descriptor.

Control flow: keyed checksum generation writes an 8-byte random confounder, hashes confounder plus data, then CBC-encrypts the 24-byte checksum field with zero IV. Verification decrypts the 24-byte field, recomputes the digest over the recovered confounder and input data, and constant-time compares the digest portion.

State and persistence behavior: stateless except for use of the caller's scheduled EVP contexts. Temporary decrypted checksum and digest buffers are zeroed before return.

Dependencies and integration points: depends on DES block types, EVP digest/cipher contexts, `krb5_generate_random_block()`, and `ct_memcmp()`. Called by `crypto-des.c` and `crypto-des3.c`.

Risks: legacy DES checksum formats are only conditionally built and are cryptographically weak. EVP cipher contexts are reused from the key schedule, so correct IV reset is essential. Digest failure paths abort rather than returning recoverable errors.

Test signals: keyed checksum known-answer or round-trip verification tests for MD5-DES and MD5-DES3, bad checksum rejection, and weak-crypto build coverage.
