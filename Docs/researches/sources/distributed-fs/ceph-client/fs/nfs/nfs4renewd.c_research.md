# sources/distributed-fs/ceph-client/fs/nfs/nfs4renewd.c

## Purpose
`nfs4renewd.c` implements the NFSv4 client lease renewal worker. The worker is a delayed work item stored on `struct nfs_client` (`cl_renewd`) and runs in the system workqueue rather than as a persistent thread. Its job is to keep server-side NFSv4 state alive by scheduling protocol-specific renewal operations before the lease expires, and by expiring delegations when renewal credentials are unavailable or stale.

## Important APIs and Functions
- `nfs4_renew_state(struct work_struct *work)`: delayed-work callback that decides whether a lease renewal or delegation callback renewal is needed.
- `nfs4_schedule_state_renewal(struct nfs_client *clp)`: computes the next renewal deadline and requeues `cl_renewd` on `system_percpu_wq`.
- `nfs4_kill_renewd(struct nfs_client *clp)`: synchronously cancels the delayed worker during teardown.
- `nfs4_set_lease_period(struct nfs_client *clp, u32 period)`: stores the server lease period, caps it at one hour, and updates the RPC reconnect timeout to half the lease.

## Control Flow
`nfs4_renew_state()` obtains the minor-version maintenance operations from `clp->cl_mvops->state_renewal_ops`. It exits immediately if `NFS_CS_STOP_RENEW` is set. It compares `jiffies` against `cl_last_renewal + cl_lease_time / 3` and sets `NFS4_RENEW_TIMEOUT` when the client is sufficiently far into the lease. If delegations are present, it also sets `NFS4_RENEW_DELEGATION_CB`.

When a renewal is needed, it asks the ops table for a renewal credential. A missing credential is fatal for ordinary lease renewal and sets `NFS4CLNT_LEASE_EXPIRED`; for delegation-only renewal it expires all delegations instead. With a credential, it calls `sched_state_renewal()` asynchronously and tolerates `-EAGAIN` and `-ENOMEM` as retryable queueing failures. Successful or retryable paths reschedule the delayed work and expire unreferenced delegations.

## State and Persistence
The file mutates transient in-memory `nfs_client` state: `cl_lease_time`, `cl_last_renewal`, `cl_res_state`, and `cl_state` bits. There is no disk persistence. Correctness depends on `cl_lock` protecting lease period updates and delayed-work scheduling state. Lease timing is expressed in `jiffies`.

## Dependencies and Integration Points
This file integrates with minor-version state maintenance ops, SUNRPC delayed work and reconnect timeout APIs, and delegation helpers from `delegation.h`. It is called after clientid/session setup by `nfs4state.c`, and its expiration decisions feed the state manager via `NFS4CLNT_LEASE_EXPIRED`.

## Risks
Renewal timing is sensitive to stale `cl_last_renewal`, missing machine/user credentials, and work cancellation races at teardown. If a non-delegation renewal cannot obtain credentials, the client deliberately marks the lease expired, which pushes recovery to the state manager. If `sched_state_renewal()` returns an unexpected error, this worker does not reschedule immediately and relies on expiration handling.

## Test Signals
Useful signals are lease-renew tracepoints (`nfs4_renew`, `nfs4_renew_async`), `NFSDBG_STATE` debug output, observed delayed-work requeue intervals, delegation expiration behavior, and recovery triggered by `NFS4CLNT_LEASE_EXPIRED`. Tests should cover no-delegation/no-credential, delegation-only/no-credential, transient async allocation failures, lease cap behavior, and cancellation during client teardown.
