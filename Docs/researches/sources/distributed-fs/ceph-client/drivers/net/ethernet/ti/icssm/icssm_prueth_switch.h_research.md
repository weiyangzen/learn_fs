# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssm/icssm_prueth_switch.h

## Purpose
This header exposes the switch-mode service boundary used by the main ICSSM netdev driver and switchdev code. It declares STP accessors, queue info, FDB management, host/port configuration, and dual-PRU firmware lifecycle helpers.

## Important APIs, types, and functions
- `icssm_prueth_sw_set_stp_state()` and `_get_stp_state()` read/write per-port STP state in the shared FDB area.
- `sw_queue_infos` exposes switch queue memory mapping to the TX datapath.
- FDB entry points include init/free, immediate static add/del, deferred learning, deferred purge, and direct purge.
- Configuration entry points include `icssm_prueth_sw_hostconfig()` and `icssm_prueth_sw_emac_config()`.
- Firmware entry points include `icssm_prueth_sw_boot_prus()` and `icssm_prueth_sw_shutdown_prus()`.

## Control flow
The header is invoked from `icssm_prueth.c` during open, stop, TX enqueue, and bridge mode switching; from `icssm_switchdev.c` for STP and FDB events; and from RX processing for source learning.

## State and persistence behavior
The declared functions operate on `struct prueth` and `struct prueth_emac`, mutating PRUSS shared memory, OCMC/DRAM queue context, heap FDB state, and remoteproc firmware state. No persistent state exists beyond active driver lifetime.

## Dependencies and integration points
It includes Linux switchdev and local ICSSM PRU/FDB/switchdev headers. It is the compile-time glue between the generic netdev implementation and switch-specific implementation.

## Risks and edge cases
- `extern const struct prueth_queue_info sw_queue_infos[][4]` hard-codes queue count as 4 rather than `NUM_QUEUES`.
- Callers must only use switch APIs when the device is in switch-capable mode and both required resources exist.
- FDB pointers may be NULL when an interface is down; switchdev callers check for this in implementation.

## Test signals
Build-time coverage for prototypes, runtime bridge enslave/unenslave, switch TX queue selection, STP state update, static FDB add/delete, and clean shutdown after one or both ports stop.
