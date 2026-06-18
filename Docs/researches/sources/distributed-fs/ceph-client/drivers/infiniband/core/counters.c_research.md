<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/counters.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/counters.c

## Purpose

`counters.c` implements RDMA core counter management for per-port hardware statistics and QP-bound counters. It supports automatic counter allocation/binding based on QP type and process ID, manual netlink-driven counter allocation/binding/unbinding by QP number and counter ID, optional hardware stat enable/disable, aggregation of live and historical stats, and per-device counter initialization/release.

## Important APIs, types, and functions

The important public/internal entry points are `rdma_counter_set_auto_mode()`, `rdma_counter_modify()`, `rdma_counter_bind_qp_auto()`, `rdma_counter_unbind_qp()`, `rdma_counter_query_stats()`, `rdma_counter_get_hwstat_value()`, `rdma_counter_bind_qpn()`, `rdma_counter_bind_qpn_alloc()`, `rdma_counter_unbind_qpn()`, `rdma_counter_get_mode()`, `rdma_counter_init()`, and `rdma_counter_release()`.

Key helpers include `__counter_set_mode()`, `alloc_and_bind()`, `__rdma_counter_bind_qp()`, `__rdma_counter_unbind_qp()`, `rdma_get_counter_auto_mode()`, `auto_mode_match()`, `counter_history_stat_update()`, `counter_release()`, `rdma_counter_get_qp()`, and `rdma_get_counter_by_id()`. The logic uses `struct rdma_port_counter`, `struct rdma_counter`, `struct rdma_hw_stats`, `struct ib_qp`, resource-tracker roots, xarrays, krefs, and driver counter ops.

## Control flow

Device setup calls `rdma_counter_init()` for each port, initializes port-counter mode and lock, and optionally allocates persistent historical hardware stats through `alloc_hw_port_stats`. Userspace can switch a port into auto mode with a supported mask. In auto mode, QP creation/modification paths call `rdma_counter_bind_qp_auto()`: tracked user QPs either reuse an existing matching counter or allocate a new counter and bind it through the driver. In manual mode, netlink can allocate a counter and bind it to a QP or bind an existing counter to a QP by ID.

Counter allocation creates a driver object, initializes resource tracking, allocates driver stats, updates per-port mode/count, initializes a kref and mutex, calls the device `counter_bind_qp` op, and adds the resource to restrack. Unbind calls the driver unbind op and drops the kref; final release snapshots stats into historical `hstats`, calls driver deallocation, deletes restrack, frees stats, and frees the counter. Query paths call driver `counter_update_stats` under the counter lock. Hardware-stat reads sum live counters plus historical stats from counters that were already freed.

## State and persistence

All state is runtime. Per-port state tracks mode, mask, bind operation count flag, number of counters, lock, and historical stats. Each `rdma_counter` stores device, port, mode, mask parameters, stats, resource tracking, kref, and lock. `qp->counter` is owned by driver bind/unbind behavior and validates whether a QP is already attached. Historical stats preserve values from released counters in memory so sysfs/netlink reads can include past QP activity until device teardown.

## Dependencies and integration points

The file depends on RDMA verbs, RDMA counter UAPI definitions, core private hardware-stat access, restrack, xarray iteration, netlink extack messages, and driver ops: `counter_alloc_stats`, `counter_init`, `counter_bind_qp`, `counter_unbind_qp`, `counter_update_stats`, `counter_dealloc`, `modify_hw_stat`, and `alloc_hw_port_stats`. Integration points include verbs QP setup/destruction, nldev netlink counter commands, sysfs hardware-stat reads, and device registration/release.

## Risks

Mode transitions are sensitive: auto mode rejects unsupported masks and cannot be enabled while counters are bound, while manual mode must fall back to none after the last counter is freed. Kref and restrack interactions must prevent use-after-free during xarray iteration and netlink operations. Manual binding must reject cross-device, cross-port, kernel/user resource mismatches, wrong counter IDs, and raw packet QPs without device raw capability. Stats aggregation can race with live counter updates, so each counter query must hold the counter lock and restrack refs. The failure path in `rdma_counter_init()` should be reviewed carefully because cleanup loops must free the intended per-port hstats.

## Test signals

Tests should cover devices with and without counter ops, auto mode by QP type and PID, automatic counter reuse, manual allocate/bind/unbind, binding errors for wrong QP/counter/port/device/mode, optional stat enable/disable through `rdma_counter_modify()`, counter stats query, historical stat aggregation after QP destroy, netlink extack on busy auto-mode changes, device teardown with live and freed counters, and concurrent QP creation/destruction while netlink enumerates counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/counters.c -->
