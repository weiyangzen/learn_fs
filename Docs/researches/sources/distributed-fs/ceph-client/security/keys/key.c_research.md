<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/key.c -->
# sources/distributed-fs/ceph-client/security/keys/key.c

## Purpose
`key.c` is the core object lifecycle implementation for Linux keys. It allocates keys, assigns serial numbers, tracks per-user quotas, instantiates or rejects keys, updates payloads, handles revocation and invalidation, registers key types, and initializes global key subsystem state.

## Important APIs, Types, and Functions
Key exported APIs include `key_alloc()`, `key_payload_reserve()`, `key_instantiate_and_link()`, `key_reject_and_link()`, `key_put()`, `key_lookup()`, `key_set_timeout()`, `key_create_or_update()`, `key_create()`, `key_update()`, `key_revoke()`, `key_invalidate()`, `generic_key_instantiate()`, `register_key_type()`, and `unregister_key_type()`. `key_user_lookup()` and `key_user_put()` manage per-UID accounting records. `key_alloc_serial()` inserts random positive serials into `key_serial_tree`.

## Control Flow
Allocation validates description/type, reserves quota unless bypassed, allocates a slab object and description, initializes permissions and flags, calls `security_key_alloc()`, references the domain tag, increments user counts, and publishes the key by serial. Instantiation serializes through `key_construction_mutex`, calls type-specific instantiate, marks state with release ordering, notifies watchers, links into an optional keyring, invalidates an authorization key, and sets expiry. Create-or-update preparses payload, checks keyring restrictions and write permission, updates a matching key when allowed, or allocates and instantiates a new key.

## State and Persistence
Global state includes `key_jar`, `key_serial_tree`, `key_user_tree`, quota limits, key type list, and `key_construction_mutex`. Each key carries quota length, data length, owner/group, permissions, flags, expiry, type, payload, domain tag, and optional keyring restriction. Persistence is in kernel memory only; final reference release schedules GC rather than destroying synchronously.

## Dependencies and Integration Points
This file integrates with LSM hooks, keyring link primitives, request-key construction waiting, GC scheduling, key notifications, RCU payload assignment, and key type modules. It is the central API used by keyctl syscalls, process keyring management, request-key upcalls, and specialized key types such as encrypted keys.

## Risks
Quota transfer and rollback paths must remain exact or `/proc/key-users` will drift. State transitions for uninstantiated, positive, and negative keys rely on memory ordering with `key_read_state()`. Register/unregister holds `key_types_sem` and invokes GC; racing key allocation with module unload is explicitly a caller concern. Keep flags prevent destructive operations and must be respected by syscall wrappers.

## Test Signals
Run keyutils tests for add/update/revoke/invalidate/timeout under quota pressure. Add races between request construction, update, revoke, and GC. Verify duplicate key serial avoidance, negative key updates, type unregister with live keys, LSM denials, and quota rollback on allocation/preparse/link failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/key.c -->
