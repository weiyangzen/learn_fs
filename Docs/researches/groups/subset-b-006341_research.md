# Research Group: subset-b-006341

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.c -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.c

## Purpose
`encrypted.c` implements the Linux `encrypted` key type. It stores secret key material in kernel memory as decrypted bytes but exports/imports it as a text datablob encrypted with a derived AES-CBC key and authenticated with an HMAC derived from a trusted or user master key. The file supports `new`, `load`, and `update` commands plus `default`, `ecryptfs`, and `enc32` payload formats.

## Important APIs, Types, and Functions
The public integration point is `struct key_type key_type_encrypted`, registered by `init_encrypted()` and removed by `cleanup_encrypted()`. Key type methods are `encrypted_instantiate()`, `encrypted_update()`, `encrypted_read()`, and `encrypted_destroy()`. Parsing and validation are handled by `datablob_parse()`, `valid_master_desc()`, and `valid_ecryptfs_desc()`. Payload sizing and layout are handled by `encrypted_key_alloc()` and `__ekey_init()`. Crypto work flows through `get_derived_key()`, `init_skcipher_req()`, `derived_key_encrypt()`, `derived_key_decrypt()`, `datablob_hmac_append()`, and `datablob_hmac_verify()`.

## Control Flow
Instantiation copies the user datablob, tokenizes it, allocates a single `encrypted_key_payload` allocation sized for clear payload, text datablob, encrypted bytes, and HMAC, then either decrypts a loaded blob, decodes caller-supplied cleartext when `user_decrypted_data` permits it, or fills decrypted bytes and IV from the RNG. Read obtains the master key, derives an encryption key, encrypts the in-memory payload, appends an HMAC over the formatted datablob, formats bytes as hex, and copies the result to the keyctl caller. Update is intentionally narrow: it validates that only the master-key description changes within the same `trusted:` or `user:` family, clones the old payload and IV, publishes the new payload with RCU, and frees the old one after grace period.

## State and Persistence
All state is kernel-resident key payload state. `epayload->payload_data` holds decrypted material or an eCryptfs auth token, while `format`, `master_desc`, `datalen`, `iv`, and `encrypted_data` point inside the same allocation. The encrypted export is not stored durably by this file; userspace receives it through `read` and may later pass it to `load`. Master key semaphores are held while using trusted/user key payload pointers, and sensitive buffers are zeroed through `kfree_sensitive()` or `memzero_explicit()`.

## Dependencies and Integration Points
This file depends on the key subsystem, `trusted` and `user` key types, eCryptfs format helpers, kernel RNG, SHA-256/HMAC helpers, and the skcipher API for `cbc(aes)`. It integrates with key quotas through `key_payload_reserve()`, with RCU through `rcu_assign_keypointer()` and `call_rcu()`, and with module/key-type registration.

## Risks
The load path is format-sensitive: IV, separator byte, encrypted data, and HMAC lengths must match exactly. The datablob uses pointers into one allocation, so size and offset calculations are security critical. CBC padding is implemented through scatterlists with zero-page or throwaway padding; off-by-one errors can corrupt adjacent payload state. Debug dump helpers can expose key material if enabled. Allowing user-supplied decrypted data is gated by config/module parameter and must remain disabled unless the deployment accepts that trust boundary.

## Test Signals
Exercise `keyctl add encrypted ... new`, `load`, `read`, and `update` for `trusted:` and `user:` masters. Include bad prefixes, empty descriptions, bad eCryptfs descriptions, malformed hex, wrong HMAC, mismatched lengths, revoked master keys, missing crypto transform, quota failures, `enc32` length boundaries, and update attempts that change master type. Crypto self-tests should verify read-then-load round trips and that HMAC failures occur before decryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.h -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.h

## Purpose
`encrypted.h` is the private header for encrypted-key support. It exposes the trusted-master-key accessor when trusted keys are available and defines no-op or active key-material dump helpers depending on `ENCRYPTED_DEBUG`.

## Important APIs, Types, and Functions
`request_trusted_key()` is declared when trusted keys can be linked with encrypted keys; otherwise an inline stub returns `-EOPNOTSUPP`. Debug helpers are `dump_master_key()`, `dump_decrypted_data()`, `dump_encrypted_data()`, and `dump_hmac()`.

## Control Flow
Compile-time configuration controls whether encrypted keys can ask the trusted key type for a master key. Debug helpers either call `print_hex_dump()`/`pr_info()` or compile to empty inline functions, so callers in `encrypted.c` do not need local `#ifdef` blocks.

## State and Persistence
The header stores no state. It only provides function declarations and inline wrappers. When debugging is enabled, helper calls expose transient key material to kernel logs; otherwise they have no runtime effect.

## Dependencies and Integration Points
The trusted-key declaration matches `masterkey_trusted.c` and depends on `CONFIG_TRUSTED_KEYS` or the module combination where both trusted and encrypted keys are modules. The dump helpers rely on `struct encrypted_key_payload` from public encrypted-key headers included by the C file.

## Risks
The main risk is accidental key disclosure if `ENCRYPTED_DEBUG` is changed from zero. The trusted-key stub must preserve the same signature as the real function so `encrypted.c` cleanly handles unavailable trusted-key support.

## Test Signals
Build encrypted keys with trusted keys built-in, as modules, and disabled. Verify `trusted:` master descriptions fail with `-EOPNOTSUPP` when unsupported, while `user:` masters still work. Audit debug builds to confirm logs contain expected dumps only when deliberately enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/gc.c -->
# sources/distributed-fs/ceph-client/security/keys/gc.c

## Purpose
`gc.c` implements deferred garbage collection for keys, keyring links, expired keys, invalidated keys, and keys whose key type is being unregistered. It lets non-sleeping paths such as `key_put()` schedule cleanup in process context.

## Important APIs, Types, and Functions
Public/internal entry points are `key_schedule_gc()`, `key_set_expiry()`, `key_schedule_gc_links()`, and `key_gc_keytype()`. `key_type_dead` is the replacement type for referenced keys after their real key type unregisters. `key_garbage_collector()` is the workqueue body, `key_gc_timer_func()` schedules expiry-link cleanup, and `key_gc_unused_keys()` destroys unreferenced keys from the graveyard list.

## Control Flow
`key_set_expiry()` records an expiry and schedules GC after the expiry plus `key_gc_delay`, except instant-reap key types. The workqueue scans `key_serial_tree` under `key_serial_lock`, removes unreferenced keys to a graveyard, calls `keyring_gc()` to prune dead links, updates keyring restrictions for unregistering key types, and on the final keytype reap cycle changes still-referenced keys to `.dead` after destroying their payload. Keytype unregister uses three observed GC cycles: mark dead, reap links, then reap keys.

## State and Persistence
GC state is in static `key_gc_next_run`, `key_gc_dead_keytype`, `key_gc_flags`, and persistent local `gc_state`. Keys move from the serial tree to the static graveyard list before destruction. User quota counters, instantiated-key counters, domain tags, LSM state, watch lists, descriptions, and slab allocations are released only after final reference death and required RCU synchronization.

## Dependencies and Integration Points
This file coordinates with `key.c` reference dropping, `keyring.c` link cleanup, LSM hooks, key notifications, the timer API, workqueues, RCU, and key type unregister paths under `key_types_sem`.

## Risks
The reaper relies on lock ordering, memory barriers, and the `KEY_FLAG_USER_ALIVE` handoff from `key_put()`. Keytype unregister is multi-pass by design; shortening it can leave links to destroyed payloads. Timer calculation uses coarse real time and `key_gc_delay`, so tests must not assume immediate removal for non-instant key types.

## Test Signals
Validate expiry, revoke, invalidate, final `key_put()`, and key-type unregister under concurrent keyring search/link workloads. Use lockdep/KASAN/KCSAN with nested keyrings, active watches, removed network key domains, and restricted keyrings. Check `/proc/key-users` quota counters return to baseline after GC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/internal.h -->
# sources/distributed-fs/ceph-client/security/keys/internal.h

## Purpose
`internal.h` is the private contract shared by the kernel key-management implementation. It declares key user accounting, keyring search context, construction, GC, permission, request-key, keyctl, DH, pkey, notification, and debugging interfaces.

## Important APIs, Types, and Functions
Important types are `struct key_user` and `struct keyring_search_context`. Search flags include `KEYRING_SEARCH_NO_STATE_CHECK`, `DO_STATE_CHECK`, `NO_UPDATE_TIME`, `NO_CHECK_PERM`, `DETECT_TOO_DEEP`, `SKIP_EXPIRED`, and `RECURSE`. The header declares core objects such as `key_serial_tree`, `key_user_tree`, `key_construction_mutex`, `request_key_conswq`, `key_type_dead`, `key_type_user`, `key_type_logon`, and `key_type_request_key_auth`. Inline helpers include `notify_key()`, `key_permission()`, `key_is_dead()`, and debug `key_check()`.

## Control Flow
Most source files include this header to compose the subsystem: key allocation and type registration in `key.c`, keyring search/link operations in `keyring.c`, credential keyring lookup in `process_keys.c`, usermode construction in `request_key.c`, syscall dispatch in `keyctl.c`, and cleanup in `gc.c`.

## State and Persistence
The header describes in-memory persistent kernel state rather than owning it. `struct key_user` tracks per-UID references, construction lock, instantiated and total key counts, and quota bytes. `struct keyring_search_context` carries caller credentials, match data, flags, iterator, possession state, search result, and timestamp across nested keyring traversals.

## Dependencies and Integration Points
It includes scheduler, wait-bit, credentials, key type, task work, keyctl, refcount, watch queue, compat, memory, and vmalloc headers. Optional declarations are gated by `CONFIG_PERSISTENT_KEYRINGS`, `CONFIG_KEY_DH_OPERATIONS`, `CONFIG_ASYMMETRIC_KEY_TYPE`, and `CONFIG_KEY_NOTIFICATIONS`.

## Risks
Because this header defines cross-file locking and search contracts, mismatched flag combinations or caller assumptions can break permission checks or RCU safety. The inline `key_is_dead()` must stay aligned with GC and search expiry semantics. Optional stubs must return stable errors for disabled features.

## Test Signals
Build all relevant config matrices, especially without persistent, DH, asymmetric, notifications, and with key debugging. Static analysis should verify all `__acquires`/`__releases` contracts. Runtime tests should cover search flags, notification delivery, and disabled keyctl operations returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/internal.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyctl.c -->
# sources/distributed-fs/ceph-client/security/keys/keyctl.c

## Purpose
`keyctl.c` implements the userspace syscall surface for key management: `add_key(2)`, `request_key(2)`, and the multiplexed `keyctl(2)` operations. It copies user arguments, resolves key references, enforces permissions, and delegates to core key/keyring/process/request helpers.

## Important APIs, Types, and Functions
Important functions include `keyctl_get_keyring_ID()`, `keyctl_join_session_keyring()`, `keyctl_update_key()`, `keyctl_revoke_key()`, `keyctl_invalidate_key()`, clear/link/unlink/move/search/read operations, `keyctl_chown_key()`, `keyctl_setperm_key()`, instantiate/negate/reject helpers, `keyctl_set_reqkey_keyring()`, `keyctl_set_timeout()`, `keyctl_assume_authority()`, `keyctl_get_security()`, `keyctl_session_to_parent()`, `keyctl_restrict_keyring()`, `keyctl_watch_key()`, and `keyctl_capabilities()`. `key_get_type_from_user()` guards type names and rejects hidden dot-prefixed types from userspace.

## Control Flow
Syscall handlers first copy bounded strings and payloads from userspace, then call `lookup_user_key()` with operation-specific lookup flags and permission needs. Add creates or updates a key in a writable keyring. Request searches process keyrings and may trigger request-key construction. Read defers permission until it knows whether direct read or possessor search access is available, then uses a temporary kernel buffer to avoid page-fault deadlocks while key semaphores are held. Instantiation verifies the caller has assumed the matching request-key auth token before linking or rejecting the target key.

## State and Persistence
The file does not own key payload state; it mutates existing key, keyring, and credential state. It can change ownership, group, permissions, expiry, request-key default destination, current instantiation authority, parent session keyring via task work, watch lists, and keyring restrictions.

## Dependencies and Integration Points
It depends on user copy APIs, credentials, capabilities, task work, LSM security labels, watch queues, request-key auth keys, process keyring helpers, keyring link/move/search primitives, persistent keyrings, DH operations, public-key operations, and feature capability bits.

## Risks
Every operation is a user/kernel trust boundary. Length caps differ by operation and must remain enforced. Partial lookup and auth-token override paths intentionally permit operations on under-construction keys; mistakes can bypass normal validity checks. Parent-session transfer has strict parent/thread/credential constraints. Feature-gated keyctl cases must match `keyrings_capabilities` and internal stubs.

## Test Signals
Use keyutils syscall tests for every `KEYCTL_*` option, including invalid pointers, oversized payloads, hidden key type names, permission denial, keep-flag behavior, partial construction auth, parent session transfer constraints, watch add/remove, capability buffers, and disabled optional features. Fuzz keyctl arguments with KASAN/KMSAN enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyctl_pkey.c -->
# sources/distributed-fs/ceph-client/security/keys/keyctl_pkey.c

## Purpose
`keyctl_pkey.c` implements asymmetric public-key `keyctl` operations for query, encrypt, decrypt, sign, and verify. It is a syscall adapter around key-type-provided asymmetric callbacks.

## Important APIs, Types, and Functions
Entry points are `keyctl_pkey_query()`, `keyctl_pkey_e_d_s()`, and `keyctl_pkey_verify()`. Helpers include `keyctl_pkey_params_get()`, `keyctl_pkey_params_get_2()`, `keyctl_pkey_params_parse()`, and `keyctl_pkey_params_free()`. It parses `enc=<encoding>` and `hash=<digest>` into `struct kernel_pkey_params`.

## Control Flow
The query path copies the info string, parses unique options, looks up the key with search permission, requires `asym_query`, and copies `struct keyctl_pkey_query` back to userspace. Encrypt/decrypt/sign/verify copy user parameter lengths, call `asym_query` to validate them against maximum sizes, allocate input/output buffers, map the requested operation enum, and invoke the relevant key-type callback.

## State and Persistence
No durable state is owned here. Per-call state consists of copied info text, a referenced key, parsed parameter pointers into the info buffer, and temporary input/output buffers. `keyctl_pkey_params_free()` releases both the info buffer and key reference.

## Dependencies and Integration Points
This file integrates with asymmetric key types through `asym_query`, `asym_eds_op`, and `asym_verify_signature`. It depends on `lookup_user_key()`, user copy helpers, parser match tables, and the `KEYCTL_PKEY_*` syscall cases in `keyctl.c`.

## Risks
The parser rejects duplicate or empty options; relaxing that could make algorithm selection ambiguous. Length validation depends on key-type query results and must precede allocation/copy. A callback returning more bytes than `out_len` would break the copy contract, so key-type implementations must obey `kernel_pkey_params`.

## Test Signals
Test RSA/ECDSA or available asymmetric key types for raw and encoded operations, duplicate/unknown info options, oversized input/output lengths, missing callback support, invalid user buffers, verify failure, and disabled `CONFIG_ASYMMETRIC_KEY_TYPE` returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/keyctl_pkey.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/permission.c -->
# sources/distributed-fs/ceph-client/security/keys/permission.c

## Purpose
`permission.c` centralizes permission and validity checks for keys. It converts requested key operations into permission-bit masks, applies owner/group/other/possessor permissions, then delegates final policy to the LSM layer.

## Important APIs, Types, and Functions
`key_task_permission()` checks a `key_ref_t` against a supplied `cred` and `enum key_need_perm`. `key_validate()` checks invalidated, revoked, dead, and expired state. Both are exported to other key subsystem and kernel consumers.

## Control Flow
Permission checks select the user, group, or other permission byte based on `fsuid`, `fsgid`, and supplementary groups. Possessor permissions from the top permission byte are ORed in when the key reference carries possession. Special needs such as unlink, sysadmin override, auth-token override, and deferred permission skip normal bit masks and go directly to `security_key_permission()`.

## State and Persistence
The file owns no state. It reads immutable or lock-protected fields from `struct key`: UID, GID, permission mask, flags, and expiry. Validation compares expiry against real time.

## Dependencies and Integration Points
It is used by keyring search, lookup, keyctl operations, request-key destination selection, and persistent keyring linking. LSM integration is mandatory through `security_key_permission()`.

## Risks
Possessor semantics are additive and easy to misapply if callers construct `key_ref_t` incorrectly. Special permission modes deliberately bypass bit checks but not LSM checks; new call sites must choose them narrowly. Expiry checks must match GC and search behavior.

## Test Signals
Test every permission class: possessor, owner, group by fsgid, group by supplementary groups, other, LSM denial, and special override modes. Validate expired, revoked, dead, and invalidated keys return the expected errno across read/search/link/update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/permission.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/persistent.c -->
# sources/distributed-fs/ceph-client/security/keys/persistent.c

## Purpose
`persistent.c` implements per-UID persistent keyrings. These keyrings are stored under a per-user-namespace hidden register and can be linked into a caller-selected destination keyring for long-lived user caches.

## Important APIs, Types, and Functions
The keyctl entry is `keyctl_get_persistent()`. Internal helpers are `key_create_persistent_register()`, `key_create_persistent()`, and `key_get_persistent()`. `persistent_keyring_expiry` controls the idle timeout, defaulting to three days.

## Control Flow
`keyctl_get_persistent()` resolves the target UID, enforcing `CAP_SETUID` for other users, then looks up a writable destination keyring. `key_get_persistent()` builds the `_persistent.<uid>` index key, searches the namespace register under read lock, creates the register and/or persistent keyring under write lock if absent, checks link permission on the persistent keyring, links it to the destination, refreshes its timeout, and returns its serial.

## State and Persistence
Persistent keyrings persist only in kernel key memory, not on disk. The namespace owns `persistent_keyring_register`, which holds links to per-UID persistent keyrings. The keyrings are allocated outside normal quota and have an expiry refreshed on successful retrieval.

## Dependencies and Integration Points
This file depends on user namespaces, namespace `keyring_sem`, keyring allocation/search/link, permission checks, UID mapping, capabilities, and key timeouts. It is exposed through `KEYCTL_GET_PERSISTENT` when `CONFIG_PERSISTENT_KEYRINGS` is enabled.

## Risks
The read-then-write creation flow must recheck under write lock to avoid duplicate persistent keyrings. UID mapping and privilege checks are security boundaries. Because keys are not in quota, expiry and GC behavior matter for resource control.

## Test Signals
Test current-user and other-user retrieval with and without `CAP_SETUID`, invalid mapped UIDs, non-keyring destinations, repeated lookup returning the same serial, timeout refresh, namespace isolation, and disabled config returning `-EOPNOTSUPP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/persistent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/proc.c -->
# sources/distributed-fs/ceph-client/security/keys/proc.c

## Purpose
`proc.c` exposes key subsystem diagnostics through `/proc/keys` and `/proc/key-users`. The views are filtered by user namespace mappings and key view permissions.

## Important APIs, Types, and Functions
Initialization is `key_proc_init()`, registered with `__initcall`. Sequence operations are `proc_keys_ops` and `proc_key_users_ops`. Helpers include `find_ge_key()`, `key_serial_next()`, `proc_keys_show()`, `key_user_first()`, `key_user_next()`, and `proc_key_users_show()`.

## Control Flow
`/proc/keys` iterates the global `key_serial_tree` under `key_serial_lock`, starting at the requested serial position. For each key, it checks namespace UID mapping, determines whether the reading process possesses the key by searching credential keyrings when possessor view might apply, then calls `key_task_permission(..., KEY_NEED_VIEW)`. Visible rows include serial, flags, usage, timeout, permissions, UID/GID, type, and type-specific description. `/proc/key-users` iterates `key_user_tree` and prints usage and quota counters.

## State and Persistence
The file is read-only diagnostic state. It reads global key trees and counters but does not mutate them. Sequence position for `/proc/keys` is the key serial, not a dense row number, to support ordered rb-tree traversal.

## Dependencies and Integration Points
It depends on procfs, seq_file, key serial and user rb-trees, namespace mapping helpers, process keyring search, permission checks, and type `describe` callbacks.

## Risks
The output must not leak keys that lack view permission or whose owner UID is unmapped in the reader namespace. Iteration holds spinlocks while formatting setup is limited, so expensive work must be controlled. Possessor detection is subtle because it affects permission bits.

## Test Signals
Read `/proc/keys` and `/proc/key-users` from different user namespaces, with keys visible by owner, group, possessor, and not visible. Validate flags for instantiated, revoked, dead, quota, constructing, negative, and invalidated keys. Check quota counters during create/update/revoke/GC cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/process_keys.c -->
# sources/distributed-fs/ceph-client/security/keys/process_keys.c

## Purpose
`process_keys.c` manages keyrings attached to credentials: thread, process, session, user, user-session, requestor, and request-key authorization keyrings. It also implements lookup of user-supplied key serials and special key IDs.

## Important APIs, Types, and Functions
Important APIs are `look_up_user_keyrings()`, `get_user_session_keyring_rcu()`, `install_thread_keyring_to_cred()`, `install_process_keyring_to_cred()`, `install_session_keyring_to_cred()`, `key_fsuid_changed()`, `key_fsgid_changed()`, `search_cred_keyrings_rcu()`, `search_process_keyrings_rcu()`, `lookup_user_key_possessed()`, `lookup_user_key()`, `join_session_keyring()`, and `key_change_session_keyring()`.

## Control Flow
User keyrings are found or created under the current user namespace register. Thread/process/session install functions prepare new credentials and commit them. Lookup handles special negative IDs by creating keyrings when allowed, falling back from session to user-session keyring, resolving request-key auth/requestor keyrings, or looking up positive serials in `key_serial_tree`. It then waits for construction unless partial lookup is requested, validates state, checks permission, marks last-used time, and returns a possessed reference when reachable from process keyrings.

## State and Persistence
Credential objects hold keyring references. User namespaces pin the hidden `.user_reg` register. `root_key_user` seeds root accounting. Named sessions can outlive a process while referenced. Session-to-parent replacement is stored as a prepared credential in task work until the parent resumes userspace.

## Dependencies and Integration Points
This file integrates with credentials, user namespaces, user_struct, keyring allocation/search, request-key auth payloads, permission checks, LSM credential transfer, and late init creation of root keyrings.

## Risks
Credential replacement must never mutate live creds directly; helper functions operate on prepared creds or commit new ones. `lookup_user_key()` combines many special cases and must preserve construction/partial/auth override semantics. User namespace register creation and named session joins use locks to avoid duplicate keyrings and disappearing names.

## Test Signals
Test all `KEY_SPEC_*` IDs with and without create flags, setuid/fsuid/fsgid changes, named and anonymous session joins, user-session fallback, requestor keyring during upcalls, lookup of under-construction and negative keys, possessor detection, and parent session replacement constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/process_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/request_key.c -->
# sources/distributed-fs/ceph-client/security/keys/request_key.c

## Purpose
`request_key.c` implements the kernel request-key mechanism. It searches process keyrings for a key and, if missing and allowed, allocates an under-construction key and asks a key-type actor or `/sbin/request-key` to instantiate it.

## Important APIs, Types, and Functions
Public APIs are `complete_request_key()`, `request_key_and_link()`, `wait_for_key_construction()`, `request_key_tag()`, `request_key_with_auxdata()`, and `request_key_rcu()`. Internal helpers include `check_cached_key()`, `cache_requested_key()`, `call_sbin_request_key()`, `construct_key()`, `construct_get_dest_keyring()`, `construct_alloc_key()`, and `construct_key_and_link()`.

## Control Flow
`request_key_and_link()` preparses match data, checks the per-task requested-key cache, searches process keyrings, optionally links a found key to the destination, or starts construction on `-EAGAIN` when callout info is supplied. Construction selects a destination keyring based on explicit input or the caller's `jit_keyring`, allocates a key under the per-user construction lock, links it early to avoid duplicate races, creates a request-key auth key, and invokes the actor. The default actor builds a temporary `_req.<serial>` session keyring containing the auth key and executes `/sbin/request-key`.

## State and Persistence
Under-construction keys carry `KEY_FLAG_USER_CONSTRUCT` until instantiated or rejected. Negative construction results use a default 60-second timeout. Optional `CONFIG_KEYS_REQUEST_CACHE` stores the last successful requested key on the task until resume cleanup. The temporary request session keyring and auth key are reference-counted and cleaned after the upcall completes.

## Dependencies and Integration Points
This file depends on process keyring search, key allocation/linking, request-key auth key type, usermode helper execution, credentials, current task flags, namespace-aware user keyrings, and optional key type `request_key` callbacks.

## Risks
The duplicate construction race is handled by re-searching under `key_construction_mutex`; changes there can create multiple simultaneous upcalls for the same key. The usermode helper receives key serials and default keyring serials as ABI. Destination keyring permission is skipped only for requestor-keyring reuse, which is a deliberate upcall exception.

## Test Signals
Test successful usermode construction, custom key-type actor construction, negative construction, interrupted waits, duplicate concurrent requests, destination default selection for every `jit_keyring` value, request-key cache hits, RCU non-sleeping requests, and failure paths where the actor does not instantiate the key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/request_key.c -->
