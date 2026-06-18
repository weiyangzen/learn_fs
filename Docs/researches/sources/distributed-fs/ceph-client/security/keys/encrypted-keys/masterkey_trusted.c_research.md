<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/masterkey_trusted.c -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/masterkey_trusted.c

## Purpose
`masterkey_trusted.c` bridges encrypted keys to the trusted key type. It requests a trusted key by description and returns a protected pointer to its raw master key bytes for the encrypted-key crypto derivation path.

## Important APIs, Types, and Functions
The sole exported local API is `request_trusted_key(const char *trusted_desc, const u8 **master_key, size_t *master_keylen)`. It uses `request_key(&key_type_trusted, ...)`, `struct trusted_key_payload`, and the trusted key payload fields `key` and `key_len`.

## Control Flow
The function requests the trusted key, takes the trusted key semaphore for reading, extracts payload pointer and length, and returns the key with the semaphore still held. Callers must release the semaphore with `up_read(&tkey->sem)` and drop the reference with `key_put()` after deriving keys.

## State and Persistence
This file does not own persistent state. It borrows trusted-key payload state under the key semaphore. Trusted keys themselves may be sealed to TPM/PCR metadata and are managed by the trusted key type.

## Dependencies and Integration Points
It depends on `keys/trusted-type.h`, `keys/encrypted-type.h`, and `encrypted.h`. Its contract is consumed by `request_master_key()` in `encrypted.c`, which strips the `trusted:` prefix before calling it.

## Risks
The function deliberately returns with `tkey->sem` held; mismatched caller cleanup would leak a read lock or use payload memory after unlock. A revoked trusted key between lookup and semaphore acquisition must remain handled by trusted-key payload semantics. Error mapping is left to the caller.

## Test Signals
Request encrypted keys backed by valid, missing, revoked, and TPM-unavailable trusted keys. Lockdep should stay quiet around caller cleanup paths, and key reference counts should not leak across failed read/load operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/masterkey_trusted.c -->
