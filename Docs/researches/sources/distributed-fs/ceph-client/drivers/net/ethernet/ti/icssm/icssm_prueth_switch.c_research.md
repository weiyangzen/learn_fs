# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.c

## Purpose
This file implements ICSSM switch-mode support layered under the main PRU Ethernet netdev driver. It defines switch queue layouts, initializes switch host/port memory tables, manages the firmware-shared FDB, schedules asynchronous FDB learning/purge work, and boots/shuts down both PRUs with switch firmware.

## Important APIs, types, and functions
- `sw_queue_infos` is exported and maps host/MII queues to OCMC and descriptor offsets for switch mode.
- `rx_queue_infos` maps RX contexts for host and physical ports.
- `icssm_prueth_sw_fdb_tbl_init()`, `icssm_prueth_sw_init_fdb_table()`, and `icssm_prueth_sw_free_fdb_table()` allocate/map/free host FDB state.
- `icssm_prueth_sw_fdb_spin_lock()` and `_unlock()` implement host/PRU arbitration over shared RAM lock bytes.
- FDB helpers implement hash, search, open-slot discovery, insertion point selection, slot shifting, index-table repair, insert, delete, and purge.
- `icssm_prueth_sw_fdb_add()`, `_del()`, `_learn_fdb()`, and `_purge_fdb()` are called from switchdev and RX datapath paths.
- `icssm_prueth_sw_hostconfig()`, `icssm_prueth_sw_port_config()`, and `icssm_prueth_sw_emac_config()` program firmware memory for switch operation.
- `icssm_prueth_sw_boot_prus()` and `icssm_prueth_sw_shutdown_prus()` manage dual-PRU switch firmware lifetime.

## Control flow
When switch mode opens, the main driver initializes host memory with `icssm_prueth_sw_hostconfig()`, then `icssm_prueth_sw_emac_config()` configures physical port contexts. The first switch-mode open maps PRU constant tables C28/C30 to shared RAM and OCMC. `icssm_prueth_sw_init_fdb_table()` allocates the host FDB object and points each subtable at fixed shared-RAM offsets; flood-to-host and flood-to-ports bits are enabled.

FDB insert locks against firmware, rejects local port MAC addresses, hashes the MAC, establishes a bucket if empty, finds sorted insertion point, shifts neighboring entries when necessary, writes MAC/age/port/static/active flags, increments bucket and total counts, and unlocks. Delete locks, searches the hash bucket, shifts remaining bucket entries left, clears active on the bucket tail, decrements counts, and unlocks. Learning and purge are deferred through `system_long_wq` using held netdev references; RX schedules learning when firmware reports source lookup failure.

Firmware boot is all-or-nothing for switch mode: PRU0 firmware is set/booted first, PRU1 second, and PRU0 is shut down if PRU1 setup fails. Shutdown only runs once all ports are no longer configured.

## State and persistence behavior
Switch state is volatile. Queue tables and FDB tables live in PRUSS DRAM/shared RAM and OCMC. `prueth->fdb_tbl` is heap state pointing into shared RAM; `total_entries` is maintained by host code. Deferred FDB work owns a held netdev reference and a copy of the MAC/event until the work item completes.

## Dependencies and integration points
The file integrates with `icssm_prueth.c` for open/stop, TX/RX queue selection, RX learning, firmware lifecycle, and mode changes. It integrates with `icssm_switchdev.c` for static FDB and STP events. It depends on Linux remoteproc, etherdevice helpers, switchdev notifier structs, workqueues, and local firmware ABI constants.

## Risks and edge cases
- FDB table manipulation is complex: sorted buckets are stored in one global MAC array, so left/right shifts must update affected bucket indexes exactly.
- `icssm_prueth_sw_do_purge_fdb()` clears dynamic entries without compacting buckets, which may leave inactive holes.
- Lock timeout is only 10 microseconds worth of polling; busy firmware can cause transient offload failure.
- Atomic allocation for learning work can fail under pressure, losing learned entries.
- Switch mode requires both PRUs; single-port configurations with switch requested are risky.

## Test signals
Run bridge offload with learning traffic, static FDB add/delete, duplicate MAC on same and different ports, full 256-entry table, hash collisions, purge after STP state change, PRU lock timeout injection, PRU1 firmware boot failure unwind, and traffic validation after repeated EMAC/switch mode transitions.
