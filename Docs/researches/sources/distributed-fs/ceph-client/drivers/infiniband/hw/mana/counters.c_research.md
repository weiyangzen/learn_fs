# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/counters.c

## Purpose
`counters.c` exposes MANA RNIC hardware counters through RDMA core device and port hardware-stat callbacks.

## Important APIs, Types, And Functions
`mana_ib_alloc_hw_device_stats()` and `mana_ib_alloc_hw_port_stats()` allocate RDMA stat arrays from descriptor tables. `mana_ib_get_hw_stats()` dispatches to device stats when `port_num == 0` and VF/port stats otherwise. `mana_ib_get_hw_device_stats()` sends `MANA_IB_QUERY_DEVICE_COUNTERS`; `mana_ib_get_hw_port_stats()` sends `MANA_IB_QUERY_VF_COUNTERS` with GDMA message V2 and copies firmware response fields into RDMA stat slots.

## Control Flow
RDMA core allocates stats using the descriptor arrays. On read, the driver builds a GDMA request with the device ID and adapter handle, submits it with `mana_gd_send_request()`, logs and returns errors, or fills `stats->value[]` and returns the descriptor count.

## State And Persistence
Counters live in hardware/firmware. The driver keeps only static descriptor names and temporary response buffers; no values are cached across reads except RDMA core's own stat object lifespan.

## Dependencies And Integration Points
The file depends on command structures in `mana_ib.h`, `mdev_to_gc()`, `adapter_handle`, RDMA hardware-stat APIs, and RNIC feature gating in `device.c` which installs device-level stats only when supported.

## Risks
Descriptor enum order must match response copy order; any enum/table mismatch corrupts user-visible stats. Port stats ignore `port_num` in the firmware request, suggesting the query is VF-wide or single-port; multi-port semantics should be validated against firmware. The device response uses 32-bit counters while port response uses 64-bit counters, which affects wrap behavior.

## Test Signals
Test stat allocation counts/names, successful device and port queries, GDMA failure propagation, feature-flag gating of device stats, multi-port reads, and exact mapping of each response field to the expected RDMA stat name.
