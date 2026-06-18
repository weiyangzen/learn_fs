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
