# sources/distributed-fs/ceph-client/fs/nfs/delegation.c

## Purpose
This file implements NFSv4 delegation lifecycle management. It installs and updates delegations on inodes, checks and copies delegation stateids for I/O, returns delegations synchronously or asynchronously, handles recalls/revocation/reclaim after recovery, expires unused delegations, and maintains per-server delegation hash/LRU/return lists.

## Important APIs, types, and functions
Important external APIs include `nfs_inode_set_delegation()`, `nfs_inode_reclaim_delegation()`, `nfs4_have_delegation()`, `nfs4_get_valid_delegation()`, `nfs4_copy_delegation_stateid()`, `nfs4_refresh_delegation_stateid()`, `nfs_async_inode_return_delegation()`, `nfs4_inode_return_delegation()`, `nfs4_inode_return_delegation_on_close()`, `nfs_inode_evict_delegation()`, `nfs_delegation_find_inode()`, `nfs_client_return_marked_delegations()`, `nfs_expire_all_delegations()`, `nfs_expire_unused_delegation_types()`, `nfs_expire_unreferenced_delegations()`, `nfs_delegation_mark_reclaim()`, `nfs_delegation_reap_unclaimed()`, `nfs_test_expired_all_delegations()`, `nfs_reap_expired_delegations()`, and `nfs4_delegation_hash_alloc()`.

## Control flow
Setting a delegation allocates and initializes `struct nfs_delegation`, then under `cl_lock` either attaches it to the inode/server hash/list, updates an existing matching delegation, or handles duplicate delegations by allowing write-upgrades and returning/revoking the old delegation. Reclaim updates existing delegation state after recovery and clears reclaim/revoked markers.

Return begins by marking `NFS_DELEGATION_RETURNING`, clearing delegated verifiers, breaking leases, flushing writeback when synchronous, reclaiming delegated opens and locks, and sending `nfs4_proc_delegreturn()`. Async returns move delegations to `server->delegations_return` and set client state-manager bits. Close paths either return immediately when no opens remain or place delegations on LRU for later pressure-based return.

Revocation and bad delegation handling mark stateids invalid, decrement active counts, detach from inode/hash/list when appropriate, and schedule state recovery. Expired delegation handling marks candidates, calls minor-version `test_and_free_expired()`, and restarts if server reboot/session-reset state appears.

## State and persistence behavior
Delegation state is stored in `struct nfs_delegation` under RCU plus per-delegation spinlock: stateid, cred, inode pointer, type, pagemod limit, change attr, flags, refcount, and list/hash membership. Per-server state includes delegation hash table, `delegations`, `delegations_return`, `delegations_lru`, `delegations_delayed`, active count, generation, and delegation flags. Durable protocol effects are delegation return/free-stateid/test-expired RPCs and state recovery scheduling.

## Dependencies and integration points
The file depends on NFSv4 state/open/lock recovery, inode cache validity, writeback, leases, state manager scheduling, minor-version ops, server lists from `client.c`, and callback recall paths from `callback_proc.c`. Directory delegation behavior is controlled by the `directory_delegations` module parameter; pressure is controlled by `delegation_watermark`.

## Risks and test signals
Risks include RCU/refcount/list lifetime bugs, deadlocks while reclaiming opens/locks, duplicate delegation server behavior, forgetting to clear RETURNING after delayed failure, active-count imbalance on revoke/reclaim, and recovery loops during server reboot. Tests should cover read/write delegation grant, upgrade, recall, close-triggered return, LRU pressure return, expired/revoked stateids, recovery reclaim/reap, directory delegation disablement, and lock/open reclaim under delegation recall.
