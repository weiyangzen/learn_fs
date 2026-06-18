<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyring.c -->
# sources/distributed-fs/ceph-client/security/keys/keyring.c

## Purpose
`keyring.c` implements the `keyring` key type and the indexed container used to link, search, restrict, move, clear, revoke, and garbage-collect keyring contents. Keyrings are ordinary keys plus an associative-array payload of links to other keys.

## Important APIs, Types, and Functions
The exported key type is `key_type_keyring`. Core APIs include `keyring_alloc()`, `keyring_search_rcu()`, `keyring_search()`, `keyring_restrict()`, `find_key_to_update()`, `find_keyring_by_name()`, `key_link()`, `key_unlink()`, `key_move()`, `keyring_clear()`, `keyring_gc()`, `keyring_restriction_gc()`, `key_set_index_key()`, `key_put_tag()`, and `key_remove_domain()`. Associative-array callbacks build and compare `struct keyring_index_key` chunks.

## Control Flow
Instantiation initializes the assoc-array and publishes non-hidden names in the current user namespace. Search finalizes the index key, checks the root keyring, then walks keyring contents and nested keyrings up to `KEYRING_SEARCH_MAX_DEPTH`, applying state, permission, match, negative-key, and timestamp rules. Link/move operations use staged `assoc_array_edit` scripts: lock, preallocate, check restriction and cycles, apply edit, notify, and release locks. Unlink/clear apply delete/clear edits and adjust link quota.

## State and Persistence
Keyring contents persist in memory as assoc-array leaves holding referenced keys, with a pointer tag distinguishing child keyrings. Named keyrings live on per-namespace name lists protected by `keyring_name_lock`. Domain tags partition keys for network namespaces and can be marked removed. Restrictions are heap-allocated `struct key_restriction` objects stored on keyrings.

## Dependencies and Integration Points
This file integrates with key allocation, quotas, permission checks, process keyrings, user namespaces, network namespace key domains, assoc-array internals, LSM hooks through callers, notifications, RCU searches, and GC.

## Risks
Nested keyring traversal is RCU-sensitive and deliberately depth-limited. Link and move locking must prevent cycles and deadlocks, especially when linking keyrings to keyrings. Restrictions can hold key references, so cycle detection and restriction GC are required to avoid leaks or opening a restricted keyring after key type unregister. The hash/index layout is part of lookup correctness.

## Test Signals
Exercise direct and recursive search, negative/revoked/expired results, link replacement, move with `KEYCTL_MOVE_EXCL`, cycle rejection, depth overflow, named keyring lookup across user namespaces, restriction setup and keytype unregister, domain removal, and concurrent search while linking/unlinking under RCU debug and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyring.c -->
