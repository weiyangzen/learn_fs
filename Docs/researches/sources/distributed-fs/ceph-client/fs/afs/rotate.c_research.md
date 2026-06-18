<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rotate.c -->
# sources/distributed-fs/ceph-client/fs/afs/rotate.c

## Purpose
Selects fileservers and endpoint addresses for a volume operation, handles retry/failover, interprets server aborts, and coordinates volume/server-list refreshes.

## Important APIs, Types, And Functions
Exports `afs_clear_server_states()`, `afs_select_fileserver()`, and `afs_dump_edestaddrreq()`. Internal flow uses `afs_start_fs_iteration()`, `afs_busy()`, and `afs_sleep_and_retry()`. It consumes `afs_operation`, `afs_server_list`, `afs_server_state`, `afs_endpoint_state`, and cumulative error helpers.

## Control Flow
On first iteration it refreshes volume status, snapshots the current server list, records endpoint probe state, and tries to preserve the vnode callback server. Each later call evaluates the previous RPC result. Success may still trigger RO replication checks. Abort handling covers `VNOVOL`, `VMOVED`, `VOFFLINE`, `VBUSY`, quota/full, unsupported op downgrade, and transient network errors. It waits for probes, picks the best-priority responsive address, and returns true when a call should be issued.

## State And Persistence
Mutates operation cursor fields, per-address `last_error`, server-list flags (`VOLUME_BUSY`, `OFFLINE`, `vnovol_mask`), volume update flags, callback server/promise state on the vnode, and preferred address selection. State is transient but affects subsequent retries and volume validation.

## Dependencies And Integration Points
Depends on fs probe waiters, server record update, address preferences, volume status checks, AFS/Vice/UAE abort constants, RxRPC peer metrics, and validation’s `afs_update_volume_state()`.

## Risks And Edge Cases
Failover must not violate file locks (`CUR_ONLY`), regress RO replica data, loop forever on `VMOVED`/`VNOVOL`, or hide state-changing timeout ambiguity. Probe-state supersession and callback server changes are race-prone.

## Test Signals
Exercise multi-server volumes, address failure, busy/offline volumes, VMOVED/VNOVOL refresh, unsupported opcode downgrade, RO release in progress, file lock current-server-only operations, and `CONFIG_AFS_DEBUG_CURSOR` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/rotate.c -->
