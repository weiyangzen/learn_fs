# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb/sge.h

## Purpose
`sge.h` is the public header for the first-generation Chelsio `cxgb` scatter-gather engine. It defines the minimal statistics structures and entry points that the adapter core, interrupt layer, NAPI poller, and netdev transmit path use to manage DMA queues.

## Important APIs, Types, And Functions
- `struct sge_intr_counts` exposes software-maintained interrupt/error counters: receive allocation drops, pure responses, spurious interrupts, response/free-list queue empty or overflow conditions, oversized packets, packet mismatches, and command queue full/restart counts for three command queues.
- `struct sge_port_stats` exposes per-port data-path offload counters: RX checksum successes, TX checksum and TSO requests, VLAN extraction/insertion, and SKBs requiring additional header room.
- Lifecycle/configuration APIs are `t1_sge_create`, `t1_sge_configure`, `t1_sge_set_coalesce_params`, and `t1_sge_destroy`.
- Interrupt and polling APIs are `t1_interrupt`, `t1_interrupt_thread`, `t1_poll`, `t1_sge_intr_enable`, `t1_sge_intr_disable`, `t1_sge_intr_clear`, and `t1_sge_intr_error_handler`.
- Data-path APIs are `t1_start_xmit`, `t1_vlan_mode`, `t1_sge_start`, `t1_sge_stop`, and `t1_sched_update_parms`.
- Readout APIs are `t1_sge_get_intr_counts` and `t1_sge_get_port_stats`.

## Control Flow And State
This header does not implement control flow; it defines the SGE contract consumed by `cxgb` board setup and interrupt code. `subr.c` calls SGE creation during software module initialization, calls `t1_sge_configure` during hardware initialization, clears/enables/disables SGE interrupts as part of global interrupt transitions, and asks `t1_sge_intr_error_handler` whether an SGE error needs threaded handling.

## Dependencies And Integration Points
The header depends on Linux interrupt, type, byte-order, NAPI, `sk_buff`, `net_device`, and `netdev_features_t` definitions. It is intentionally opaque around `struct sge`; callers hold only pointers. It integrates with the `adapter` object, netdev transmit path, VLAN feature toggling, interrupt threading, and per-port statistics collection.

## Risks And Edge Cases
SGE errors include fatal conditions such as response queue overflow and packets too large. The interrupt counters mix hardware IRQ events and host-side command queue backpressure, so callers must interpret them as operational diagnostics rather than pure hardware MIBs. The API assumes implementation-side locking around queues and register access; this header alone gives no ownership rules.

## Test Signals
Useful signals include successful adapter probe/remove without SGE allocation leaks, NAPI receive/transmit traffic, checksum/TSO/VLAN offload counters changing under matching workloads, command queue restart behavior under TX pressure, and fatal SGE error paths waking the threaded interrupt handler.
