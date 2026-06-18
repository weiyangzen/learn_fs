# sources/distributed-fs/ceph-client/fs/nfs/delegation.h

## Purpose
This header declares NFSv4 delegation data structures, flags, lifecycle APIs, and convenience helpers for checking delegated attributes and times. It is the shared interface between NFS open/I/O paths, callback recall handling, state recovery, and delegation implementation.

## Important APIs, types, and functions
`struct nfs_delegation` contains hash/list links, credential, inode pointer, stateid, type, pagemod limit, change attr, generation, flags, refcount, spinlock, return/LRU list entry, and RCU head. Flag bits cover reclaim, return-on-close, referenced, returning, revoked, test-expired, and delegated-time support.

The header declares delegation install/reclaim/return/evict/find/expire/recover APIs, NFSv4 delegation RPC helpers, stateid copy/refresh helpers, and `nfs4_delegation_hash_alloc()`. Inline helpers include `nfs_have_read_or_write_delegation()`, `nfs_have_write_delegation()`, delegated attribute/time checks, and directory delegation request/status helpers.

## Control flow
Callers use inline checks through `NFS_PROTO(inode)->have_delegation()` on hot paths, while more complex lifecycle events call the exported functions implemented in `delegation.c`. Callback code uses `nfs_delegation_find_inode()` and async return APIs; recovery code uses reclaim/reap/test-expired APIs.

## State and persistence behavior
The header defines in-memory delegation state and module-visible flags. It does not persist data, but its stateid and credential fields are used for protocol RPCs that return, test, or reclaim delegation state on the server.

## Dependencies and integration points
It is enabled for the main delegation structures only under `CONFIG_NFS_V4`, while generic delegated timestamp helper declarations remain available. It integrates with `nfs_fs`, NFS protocol ops, VFS inode mode checks, NFSv4 stateids, and module parameter `directory_delegations`.

## Risks and test signals
Risks include callers assuming delegation APIs exist outside `CONFIG_NFS_V4`, misuse of inline delegation checks for directories, and state structure changes not reflected in locking/refcount rules. Compile tests across NFSv4 enabled/disabled configs and runtime tests of delegated atime/mtime helpers are relevant signals.
