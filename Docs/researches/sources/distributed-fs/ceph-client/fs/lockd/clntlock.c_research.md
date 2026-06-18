# sources/distributed-fs/ceph-client/fs/lockd/clntlock.c

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/clntlock.c` manages client-side blocking lock waits, GRANTED callbacks, lockd startup/shutdown per NFS mount, and lock reclaim after server reboot. The source was read as a complete 297-line file.

## Important APIs, Types, and Functions

Important functions are `nlmclnt_init`, `nlmclnt_done`, `nlmclnt_prepare_block`, `nlmclnt_rpc_clnt`, `nlmclnt_queue_block`, `nlmclnt_dequeue_block`, `nlmclnt_wait`, `nlmclnt_grant`, `nlmclnt_recovery`, and the `reclaimer` kernel thread. Global blocked waits are tracked in `nlm_blocked` under `nlm_blocked_lock`.

## Control Flow

`nlmclnt_init` starts lockd for the mount, looks up or creates a host, binds an RPC client, and stores optional NLM client callbacks. Blocking lock acquisition queues a stack `nlm_wait` before the LOCK RPC so a GRANTED callback cannot be missed. `nlmclnt_grant` matches callbacks by range, lockowner pseudo-pid, peer address, and NFS file handle, then updates status and wakes the waiter. `nlmclnt_recovery` starts one reclaim thread per host; the reclaimer moves granted locks to a reclaim list, forces rebind, resends reclaim LOCKs, handles repeated reboots, and wakes blocked waiters with grace-period status.

## State and Persistence Behavior

The blocked list is process-local kernel memory. Granted/reclaim lock lists live on `nlm_host` and hold references through file-lock private data. Recovery state uses `host->h_reclaiming`, `h_state`, `h_nsmstate`, and `h_rwsem`; it is not persistent across local reboot.

## Dependencies and Integration Points

The file integrates with `clntproc.c` for reclaim RPCs, `host.c` for host lookup/release/binding, `svc` callbacks for GRANTED RPCs, NFS file handles, SUNRPC address comparison, and `lockd_up`/`lockd_down` service reference management.

## Risks and Edge Cases

Callback matching intentionally does not use cookies, so mismatched ranges or pseudo-pids can lose grants. A server can request blocking even for non-blocking calls, which is rejected. Reclaimer `SIGKILL` can drop unreclaimed locks from future attempts. Polling is needed because some servers lose callbacks.

## Test Signals

Signals include blocking lock tests with GRANTED callbacks arriving before and after LOCK replies, interrupted waits and timeout polling, server reboot recovery with repeated NSM state changes, host shutdown while waits exist, and lockdep/KCSAN over `nlm_blocked_lock`.
