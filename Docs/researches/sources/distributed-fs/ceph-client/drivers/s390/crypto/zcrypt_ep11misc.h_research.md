# sources/distributed-fs/ceph-client/drivers/s390/crypto/zcrypt_ep11misc.h

## Purpose
`zcrypt_ep11misc.h` defines the local public interface for EP11 helper functionality. It exposes API ordinal constants, EP11 key-blob version constants, key-blob layouts, card/domain info structs, validation routines, key generation/import/conversion functions, APQN discovery, and lifecycle hooks.

## Important APIs, Types, And Functions
Important constants are `EP11_API_V1`, `EP11_API_V4`, `EP11_API_V6`, `EP11_STRUCT_MAGIC`, `EP11_BLOB_PKEY_EXTRACTABLE`, `TOKVER_EP11_AES`, `TOKVER_EP11_AES_WITH_HEADER`, and `TOKVER_EP11_ECC_WITH_HEADER`. `struct ep11keyblob` describes the firmware key blob payload with a union for old-style session/header overlay, WKVNP/WKVP, attributes, mode, magic, IV, encrypted key data, and MAC. `struct ep11_card_info` and `struct ep11_domain_info` are query result contracts.

## Control Flow
The inline `is_ep11_keyblob()` checks the magic value and is used by decode logic in the implementation. Other declarations form call paths for checking blobs, querying cards/domains, generating AES blobs, importing clear keys, finding matching APQNs, and deriving protected keys.

## State And Persistence
The header defines transient in-memory views of EP11 key blobs and hardware info. It does not own storage or persistent state.

## Dependencies And Integration Points
It includes `asm/zcrypt.h` and `asm/pkey.h`, connecting EP11 helpers to zcrypt request types and pkey protected-key typing. CEX4 sysfs and pkey code are natural consumers.

## Risks And Test Signals
Risks include packed-layout drift, old-style header overlay confusion, and callers treating `is_ep11_keyblob()` as sufficient validation without length checks. Tests should cover all accepted token versions, extractability-flag enforcement, and query result formatting in CEX4 sysfs attributes.
