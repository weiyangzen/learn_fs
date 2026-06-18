# sources/distributed-fs/ceph-client/net/can/af_can.h

## Purpose
This private header defines the receive-dispatch and statistics structures shared by the PF_CAN core and CAN procfs/statistics code. It is not a user ABI header; it supports in-kernel organization around `af_can.c` and companion proc code.

## Important APIs, Types, And Functions
`struct receiver` represents one CAN receive subscription. It stores the normalized `can_id`/`mask`, callback function and callback data, optional identifier string, optional owning socket, match counter, hlist node, and RCU head for deferred freeing.

`struct can_pkg_stats` tracks per-net RX/TX frame counts, match counts, current/total/max rates and match ratios, plus delta counters used by periodic stat updates.

`struct can_rcv_lists_stats` tracks receive-list reset timestamps and current/max receiver entry counts.

The function declarations `can_init_proc()`, `can_remove_proc()`, and `can_stat_update()` connect the core to procfs/stat timer support.

## Control Flow
`af_can.c` allocates `struct receiver` objects from its slab cache, fills them during `can_rx_register()`, links them into chosen receive lists, and eventually frees them through an RCU callback. Proc/stat code initializes procfs files per net namespace, removes them during namespace teardown, and updates `can_pkg_stats` through the declared timer callback.

## State And Persistence
The header only declares memory layouts. Runtime instances are stored in per-net CAN state, per-device CAN receive lists, or transient receiver allocations. Counters persist until net namespace teardown or explicit stat reset by the proc/stat layer.

## Dependencies And Integration Points
The header depends on `sk_buff`, `net_device`, hlist/list support, RCU support, and CAN identifier definitions. It is included by the PF_CAN core and procfs implementation. The callback signature in `struct receiver` is the contract consumed by protocol modules registered through `can_rx_register()`.

## Risks And Edge Cases
Because `struct receiver` carries both callback data and an optional socket reference, unregister paths must coordinate RCU and socket lifetime correctly. Statistics use atomic counters for hot-path updates but aggregate fields are plain unsigned longs, so readers need to tolerate approximate snapshots.

The header is internal to this source tree. Changing field layout affects `af_can.c`, procfs output, and any in-tree code that inspects receiver/stat structures.

## Test Signals
Compile coverage is the main signal for this header. Runtime signals come from PF_CAN receive-filter tests, procfs CAN statistics tests, and namespace teardown tests that verify receiver and stat state is allocated and freed correctly.
