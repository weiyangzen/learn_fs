# sources/distributed-fs/ceph-client/crypto/asymmetric_keys/public_key.c

Purpose: implements the in-software public-key asymmetric subtype, translating kernel key payloads into akcipher or sig algorithm instances for query, encryption, decryption, signing, and verification.

Important APIs/types/functions: `public_key_free()` releases key material and parameters. `software_key_determine_akcipher()` maps key algorithm, encoding, hash, and operation to Crypto API algorithm names such as `pkcs1(rsa,sha256)`, `pkcs1pad(rsa)`, `x962(ecdsa-...)`, or raw ML-DSA/ECRDSA names. `software_key_query()` reports key sizes and supported operations. `software_key_eds_op()` performs encrypt/decrypt/sign. `public_key_verify_signature()` verifies signatures and checks key/signature algorithm compatibility. `public_key_subtype` exports subtype callbacks.

Control flow: subtype callbacks pack public/private key bytes with algorithm id and parameters, allocate either `crypto_sig` or `crypto_akcipher`, set public/private keys, run the requested operation, and free all temporary material. Verification rejects mismatched pkey algorithms except the accepted ECDSA key/algorithm naming difference.

State and persistence: persistent state is `struct public_key` in an asymmetric key payload, including key bytes, parameters, key length, algorithm names, flags, and private/public bit. Temporary packed key buffers are freed with `kfree_sensitive()`.

Dependencies and integration points: depends on `crypto_sig`, `crypto_akcipher`, public-key structures, keyctl pkey params, and parser-produced payloads from X.509 and PKCS#8.

Risks: algorithm-name construction is policy-critical because it controls padding and hash semantics. Supported hash lists for ECDSA/ECRDSA/ML-DSA must track available algorithms and standards. Positive returns from verify are warned and normalized. Private-key paths must avoid leaking temporary packed keys.

Test signals: RSA pkcs1 verify/sign and pkcs1pad encrypt/decrypt, raw RSA restrictions, ECDSA x962/p1363 with allowed and disallowed hashes, ECRDSA Streebog hashes, ML-DSA raw/sha512 handling, query supported-op bits, and mismatched pkey algorithm rejection.
