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
