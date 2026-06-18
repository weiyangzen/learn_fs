<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.h -->
# sources/distributed-fs/orangefs/src/common/security/security-hash.h

## Purpose
Declares the issuer-to-public-key hash API used by key-based OrangeFS security.

## Important APIs, Types, And Functions
Declares `SECURITY_hash_initialize`, `SECURITY_hash_finalize`, `SECURITY_add_pubkey`, and `SECURITY_lookup_pubkey` over OpenSSL `EVP_PKEY` pointers.

## Control Flow
Security initialization creates the table, loads keystore entries with `SECURITY_add_pubkey`, verification paths call `SECURITY_lookup_pubkey`, and finalization frees all keys.

## State And Persistence
The header declares no state, but the implementation owns global in-memory key table state.

## Dependencies And Integration Points
Includes OpenSSL `evp.h`; used by `pint-security.c`.

## Risks And Test Signals
Risks are ownership ambiguity for `EVP_PKEY *` passed to add and returned from lookup. Link and lifecycle tests around keystore loading validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.h -->
