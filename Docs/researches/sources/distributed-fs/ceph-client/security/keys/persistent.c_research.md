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
