<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.c -->
# sources/distributed-fs/orangefs/src/common/security/security-hash.c

## Purpose
Maintains the key-mode security public-key lookup table, mapping issuer strings to OpenSSL `EVP_PKEY` objects.

## Important APIs, Types, And Functions
Exports `SECURITY_hash_initialize`, `SECURITY_hash_finalize`, `SECURITY_add_pubkey`, and `SECURITY_lookup_pubkey`. Internal `pubkey_entry_t` embeds a qhash link, issuer hash key, and owned public key. Helpers compare issuer strings and free entries.

## Control Flow
Initialization creates a global qhash table under `hash_mutex`. Adding a key allocates an entry, duplicates the issuer string, removes and frees any existing entry for that issuer, and inserts the new entry. Lookup searches by issuer and returns the stored `EVP_PKEY *`. Finalize drains and frees the table.

## State And Persistence
State is global and in memory: `pubkey_table`, initialization flag, and mutex. Public keys are loaded from the configured keystore by `pint-security.c` and freed when removed/finalized.

## Dependencies And Integration Points
Depends on OpenSSL EVP, `quickhash`, `quicklist`, `gen-locks`, and gossip. Used by capability and credential verification in key security mode.

## Risks And Test Signals
`SECURITY_lookup_pubkey` does not take `hash_mutex`, qhash's string hash is mask-based despite the prime table size, `SECURITY_add_pubkey` leaks the entry if `strdup` fails, and returned key pointers have no lifetime protection. Tests should cover initialize idempotence, duplicate replacement, lookup miss/hit, finalize cleanup, concurrent add/lookup, and distribution/collision behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-hash.c -->
