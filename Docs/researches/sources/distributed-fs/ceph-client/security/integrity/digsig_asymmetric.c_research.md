# sources/distributed-fs/ceph-client/security/integrity/digsig_asymmetric.c

Purpose: verifies integrity signatures using asymmetric keys and supports IMA/EVM signature version 3 by hashing file-identity metadata before verification.

Important APIs, types, and functions: public functions are `asymmetric_verify()` and `asymmetric_verify_v3()`. Internal helpers are `request_asymmetric_key()` and `calc_file_id_hash()`. It uses `struct signature_v2_hdr`, `struct public_key_signature`, `struct ima_file_id`, and `struct ima_max_digest_data`.

Control flow: key lookup first checks the IMA blacklist keyring for the key ID, then searches a specific keyring or global asymmetric keys. `asymmetric_verify()` validates signature length, hash algorithm, key ID, public key algorithm, selects encoding (`pkcs1`, `x962`, or `raw`), and calls `verify_signature()`. v3 verification hashes the typed file ID structure and verifies that derived digest.

State and persistence: no persistent state; it acquires and releases key references.

Dependencies and integration: depends on asymmetric key type, public key crypto, hash algorithm tables, IMA blacklist keyring, and integrity xattr signature formats.

Risks and test signals: key lookup errors are intentionally normalized for some cases, while blacklisted keys must reject. Algorithm/encoding selection must match key type. Test signals include unknown key, blacklisted key, unsupported hash/pkey algorithm, malformed signature size, valid RSA/ECDSA/ECRDSA signatures, and v3 hash type validation.
