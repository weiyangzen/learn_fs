<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist.c -->
# sources/distributed-fs/ceph-client/certs/blacklist.c

## Purpose

`blacklist.c` implements the system blacklist keyring used to reject blacklisted certificate hashes, binary hashes, and optional revocation certificates. It defines a custom `blacklist` key type whose description is the hash identifier and loads compiled-in blacklist material at boot.

## Important APIs, Types, And Functions

Exported functions include `mark_hash_blacklisted()`, `is_hash_blacklisted()`, and `is_binary_blacklisted()`. With revocation support, it also provides `add_key_to_revocation_list()` and `is_key_on_revocation_list()`. Key type operations are `blacklist_vet_description()`, `blacklist_key_instantiate()`, `blacklist_key_update()`, and `blacklist_describe()`.

Initialization is split between `blacklist_init()` as a `device_initcall()` and `load_revocation_certificate_list()` as a `late_initcall()` when configured.

## Control Flow

`blacklist_init()` registers the `blacklist` key type, allocates `.blacklist` with a link restriction that accepts only blacklist keys, then iterates `blacklist_hashes` to add built-in hash descriptions. Built-in hashes bypass PKCS#7 authentication by using `KEY_ALLOC_BUILT_IN`.

Runtime hash checks use `get_raw_hash()` to format binary hashes as `tbs:<hex>` or `bin:<hex>`, then search `.blacklist`. A match returns rejection. Authenticated userspace updates, when enabled, verify a PKCS#7 signature over the description against the builtin trusted keyring before instantiating a new blacklist key. Revocation certificates are stored as asymmetric keys in the same keyring and checked by validating PKCS#7 trust against `.blacklist`.

## State And Persistence Behavior

The persistent runtime state is the global `.blacklist` keyring and its keys. Built-in hashes and revocation certificates originate from build-time embedded data. Blacklist keys cannot be updated or removed through this type; additions are monotonic for the running kernel.

## Dependencies And Integration Points

The file depends on kernel keyrings, asymmetric keys, PKCS#7 verification, X.509 certificate loading, `blacklist.h`, and `keys/system_keyring.h`. It integrates with module signature verification and other callers that use exported blacklist checks.

## Risks And Edge Cases

Description validation is security-critical. It permits only `tbs:` or `bin:` prefixes, lowercase even-length hex, and at most 128 hex characters. Initialization panics on keyring/key-type allocation failure because silent blacklist absence would weaken signature enforcement. Authenticated update mode must ensure the payload signature covers the exact description.

## Test Signals

Tests should cover valid and invalid descriptions, duplicate built-in hashes, binary and X.509 TBS hash lookups, authenticated update success/failure, revocation certificate loading, PKCS#7 messages signed by revoked keys, and init failure injection. Expected rejection codes are `-EKEYREJECTED` for hash matches and `-EPERM` from `is_binary_blacklisted()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/blacklist.c -->
