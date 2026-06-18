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
