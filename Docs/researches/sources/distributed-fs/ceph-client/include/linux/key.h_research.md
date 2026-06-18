# sources/distributed-fs/ceph-client/include/linux/key.h

## Purpose

`key.h` is the internal kernel key-management interface. It defines key serial and permission types, `struct key`, keyring index metadata, possession-carrying `key_ref_t` references, allocation flags, request/search/update/link APIs, RCU payload helpers, and no-op fallbacks when `CONFIG_KEYS` is disabled. The source was read as a complete 520-line file.

## Important APIs, Types, and Functions

Core types include `key_serial_t`, `key_perm_t`, `enum key_need_perm`, `enum key_lookup_flag`, `struct key_tag`, `struct keyring_index_key`, `union key_payload`, `key_ref_t`, `struct key_restriction`, `enum key_state`, and `struct key`. Important APIs are `key_alloc()`, `key_revoke()`, `key_invalidate()`, `key_put()`, `request_key_tag()`, `request_key_rcu()`, `request_key_with_auxdata()`, `wait_for_key_construction()`, `key_validate()`, `key_create()`, `key_create_or_update()`, `key_update()`, `key_link()`, `key_move()`, `key_unlink()`, `keyring_alloc()`, `keyring_search()`, `keyring_restrict()`, `lookup_user_key()`, and `key_set_timeout()`. Inline helpers encode possession in the low bit of `key_ref_t` and use acquire semantics in `key_read_state()`.

## Control Flow

Callers allocate or request keys, optionally wait for construction, validate state and permissions, then link/search/update/unlink keys through keyrings. Payload replacement is protected by the key semaphore and exposed through RCU helpers. Network namespaces can scope searches by using a namespace key domain tag. When keys are disabled, almost every operation compiles into a stub, so callers must tolerate missing key support.

## State and Persistence Behavior

`struct key` persists in kernel memory under refcount control and carries quota, owner UID/GID, permission bits, state, expiry or revocation time, payload pointers, keyring association arrays, and restriction policy. There is no file-backed persistence here; state survives until references, keyrings, quota accounting, and RCU callbacks release it.

## Dependencies and Integration Points

The header integrates credentials, user namespaces, network namespaces, assoc arrays, RCU, rwsems, refcounting, security blobs, key notifications, and the userspace keyctl path. Filesystems, crypto, auth, and networking subsystems use it to request and cache authentication material.

## Risks and Edge Cases

The low-bit `key_ref_t` possession encoding depends on pointer alignment and must never be dereferenced directly. State reads require ordering against instantiation. Payload `datalen` may not match RCU payload internals. Restrictions can be bypassed only with explicit allocation flags. Stubs under `!CONFIG_KEYS` can hide missing feature coverage.

## Test Signals

Useful signals include keyrings selftests, keyctl syscall tests, permission/possession matrix tests, RCU payload replacement stress, namespace-domain request tests, quota and expiry/revocation tests, and `!CONFIG_KEYS` build coverage.
