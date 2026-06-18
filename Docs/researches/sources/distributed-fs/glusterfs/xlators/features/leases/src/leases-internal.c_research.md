# sources/distributed-fs/glusterfs/xlators/features/leases/src/leases-internal.c

## Purpose
Contains the internal lease-management engine for the leases translator: per-inode lease state, per-client cleanup lists, conflict detection, recall upcalls, timer expiry, blocked fop replay, and disconnect cleanup.

## Important APIs, Types, and Functions
- `is_leases_enabled()` and `get_recall_lease_timeout()` read translator private options.
- `lease_ctx_get()` creates/fetches a `lease_inode_ctx_t` in inode ctx.
- `process_lease_req()` handles `GF_GET_LEASE`, `GF_SET_LEASE`, and `GF_UNLK_LEASE`.
- `check_lease_conflict()` decides whether an fop winds, blocks, or fails with `EAGAIN`.
- `__recall_lease()` sends `GF_UPCALL_RECALL_LEASE` notifications and arms a timer.
- `do_blocked_fops()` resumes fops queued while a conflicting lease was recalled.
- `cleanup_client_leases()` removes all leases for a disconnected client.
- `expired_recall_cleanup()` consumes recall-expiry work and forcefully removes stale leases.

## Control Flow
A set-lease request validates the lease ID, locks the inode lease ctx, checks open fd and existing lease compatibility, and either records the lease or sends recall notifications and rejects the request. A normal data or metadata fop calls `check_lease_conflict()` with flags indicating write/blocking behavior; conflicts trigger recall. Blocking fops are queued in the inode ctx, while nonblocking fops fail with `EAGAIN`.

Unlock removes counts from both the lease-id entry and aggregate inode state. When the last lease disappears, `blocked_fops_resuming` is set and blocked stubs are resumed outside the lease lock. If clients do not unlock after recall, the timer handler adds the inode to `priv->recall_list`; the cleanup thread later removes all leases on that inode and resumes blocked fops.

## State and Persistence
All lease state is in memory: inode ctx contains lease-id entries, aggregate lease counts, blocked stubs, timer pointer, and recall flags; private state contains client cleanup and recall lists plus timer wheel/thread synchronization. There is no on-disk lease persistence. Client disconnect cleanup relies on the client-to-inode list populated when the first lease for a client is added.

## Dependencies and Integration Points
Depends on GlusterFS upcall utilities, timer wheel, inode/fd ctx, call stubs, list APIs, pthread synchronization, and client UID/lease ID helpers. It integrates with the rest of the translator through `process_lease_req()`, `check_lease_conflict()`, and `cleanup_client_leases()`.

## Risks and Edge Cases
Lock ordering is documented at the top and must be preserved to avoid deadlock. `__is_same_lease_id()` uses `strlen(k1)` on lease IDs that are copied as fixed-size byte arrays, so callers rely on valid string-like lease IDs. Client cleanup list removal has a TODO to remove empty client entries. Timer callbacks free the timer but timer data allocation/freeing is delicate. Open fd conflict checking fails closed if fd ctx is missing. Forceful recall cleanup intentionally revokes leases after timeout, which can surprise slow clients.

## Test Signals
Cover RD/RW lease compatibility, same lease ID reentrancy, open-fd conflicts, blocking and nonblocking fop behavior, recall upcall emission, timer-expiry forced cleanup, client disconnect cleanup, and concurrent unlock while blocked fops are queued.
