# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cm.c

## Purpose
`cm.c` implements mlx4 SR-IOV connection-manager paravirtualization. It rewrites CM communication IDs between slave-visible IDs and physical-function IDs, demultiplexes inbound CM MADs to slaves, and cleans mapping state after disconnect/reject timeouts.

## Important APIs, Types, And Functions
Public functions are `mlx4_ib_multiplex_cm_handler()`, `mlx4_ib_demux_cm_handler()`, `mlx4_ib_cm_paravirt_init()`, `mlx4_ib_cm_paravirt_clean()`, `mlx4_ib_cm_init()`, and `mlx4_ib_cm_destroy()`. `struct id_map_entry` maps `(slave_id, slave_cm_id)` to `pv_cm_id` in both an rb-tree and xarray. `struct rej_tmout_entry` remembers which slave should receive timeout REJ messages. Helpers get/set local and remote comm IDs across normal CM and SIDR MAD formats.

## Control Flow
On outbound slave MADs, multiplexing allocates or finds a mapping for request-like messages, rewrites local comm ID to PF-visible ID, and schedules delayed cleanup on DREQ. On inbound MADs, demux finds the target slave from a REQ/SIDR_REQ SGID or from remote PF CM ID, rewrites remote comm ID back to the slave ID, and schedules cleanup on DREQ/REJ. Timeout REJ handling uses a separate xarray keyed by remote PF CM ID to route timeout rejects when no full ID map exists. Cleanup cancels delayed work, removes rb-tree/xarray/list entries, and frees objects for one slave or all slaves.

## State And Persistence
State is runtime-only in `dev->sriov`: `sl_id_map`, `pv_id_table`, `cm_list`, `pv_id_next`, `xa_rej_tmout`, and delayed cleanup work. Mappings persist for active CM conversations and for `CM_CLEANUP_CACHE_TIMEOUT` after teardown-like MADs.

## Dependencies And Integration Points
The file depends on RDMA CM MAD formats, mlx4 SR-IOV slave/GID lookup helpers, rbtrees, xarrays, delayed workqueues, and module-level `cm_wq` created by `mlx4_ib_cm_init()`.

## Risks
CM MAD field handling is attr-id-specific; SIDR REP/REQ local/remote ID misuse logs errors and returns `-1` cast to `u32`. `sl_id_map_add()` replaces an rb-node without freeing the old entry, so callers must avoid duplicate live mappings or accept leak risk. Cleanup races are mitigated with locks and flushes but remain subtle. REJ timeout routing is best-effort; allocation failure still passes the REQ to a slave but may lose timeout REJ routing.

## Test Signals
Test REQ/REP/MRA/SIDR_REQ mapping allocation, DREQ cleanup scheduling, inbound REQ GID-to-slave routing, timeout REJ fallback, duplicate slave CM IDs, per-slave and all-slave cleanup, workqueue init/destroy, and concurrent demux/multiplex under teardown.
