# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/provider.c

## Purpose

`provider.c` is the RDMA core provider registration layer for the Chelsio cxgb4 iWARP driver. It binds Chelsio's low-level `c4iw_rdev` resources to `struct ib_device_ops`, exposes device/port attributes and sysfs attributes, manages user contexts and protection domains, implements user mmap dispatch for queues/status pages/BAR mappings, and registers/unregisters the RNIC with the RDMA subsystem.

## Important APIs, Types, and Functions

- `fastreg_support`: module parameter controlling whether `IB_DEVICE_MEM_MGT_EXTENSIONS` is advertised.
- `c4iw_alloc_ucontext` / `c4iw_dealloc_ucontext`: initialize per-process `c4iw_dev_ucontext`, maintain mmap key lists, expose the status page to modern user libraries, and release queued mmap metadata.
- `c4iw_mmap`: consumes a one-shot `c4iw_mm_entry` by key and maps BAR, write-combining BAR, contiguous DMA, or non-contiguous coherent DMA memory into userspace.
- `c4iw_allocate_pd` / `c4iw_deallocate_pd`: allocate and free PD IDs through the resource ID table and update PD statistics.
- `c4iw_query_device`, `c4iw_query_port`, `c4iw_query_gid`: fill RDMA core capability, port, and GID data from the lower-layer cxgb4 device and netdevs.
- Sysfs/stat helpers: `hw_rev_show`, `hca_type_show`, `board_id_show`, `c4iw_alloc_device_stats`, and `c4iw_get_mib`.
- `c4iw_dev_ops`: the central verbs operation table connecting CQ/QP/SRQ/MR/CM/resource-tracking callbacks from the rest of the driver.
- `c4iw_register_device` / `c4iw_unregister_device`: final RDMA device setup, netdev association, and registration lifecycle.

## Control Flow

Registration work sets node GUID/type, port count, completion vectors, parent PCI device, and iWARP interface name, installs `c4iw_dev_ops`, associates each RDMA port with its Ethernet netdev, raises the PCI DMA segment limit, then calls `ib_register_device`. Failure after setup calls `c4iw_dealloc(ctx)` to unwind the Chelsio device context.

User context creation initializes queue-ID sharing lists and mmap state. If userspace is old and cannot receive the status page response, the driver disables status-page support globally; otherwise it allocates an mmap entry, reserves a key, copies the response, and queues a mapping to the physical status page. `c4iw_mmap` later removes exactly one matching mapping and dispatches by `mmap_flag`, so mmap entries are consumed when mapped.

Capability queries are mostly read-only projections of `rdev->lldi`, hardware queue limits, firmware version, and module parameters. PD allocation uses the generic resource table and writes the PDID to userspace when requested.

## State and Persistence Behavior

Persistent state lives in `struct c4iw_dev`, `struct c4iw_rdev`, per-ucontext mmap lists, RDMA core object wrappers, and the low-level driver information (`lldi`). Mmap keys monotonically advance per user context. PD/current/max counters are protected by `rdev->stats.lock`; mmap list operations use `ucontext->mmap_lock`. The file does not persist data beyond kernel memory, but it defines the ABI-visible uverbs response fields and sysfs/stat output.

## Dependencies and Integration Points

This file integrates Linux RDMA core (`ib_device_ops`, uverbs, resource tracking, iWARP CM), netdev/ethtool helpers, cxgb4 lower-layer APIs (`cxgb4_get_tcp_stats`, `ib_get_eth_speed`, BAR mappings), and driver-local helpers from `iw_cxgb4.h`. It depends on `resource.c` for PD/QID allocation, `qp.c`/CQ/MR/CM files for operation callbacks, and the user ABI structs consumed by libcxgb4.

## Risks and Edge Cases

- `c4iw_alloc_ucontext` sets `T4_STATUS_PAGE_DISABLED` on the shared rdev when one old userspace process connects, affecting later contexts.
- `c4iw_mmap` frees the mmap entry before the actual remap call; failed mmap attempts cannot be retried with the same key.
- `c4iw_query_gid` rejects port zero but otherwise trusts the caller-provided port index when indexing `ports[port - 1]`.
- Device stats are marked with a FIXME because TCP MIB counters look port-scoped but are exported through device stats.
- The `rhp = (struct c4iw_dev *)ibdev` cast in PD allocation assumes `struct c4iw_dev` embeds `ib_device` at offset zero or matches historical layout; most other code uses `to_c4iw_dev`.

## Test Signals

Build coverage should verify every callback in `c4iw_dev_ops` matches the RDMA core signatures. Runtime smoke tests should cover device registration/unregistration, `ibv_query_device`, `ibv_query_port`, PD alloc/dealloc, old and new ucontext responses, mmap of queue/status/BAR entries, and sysfs/stat reads. Negative tests should exercise malformed mmap keys, undersized udata, invalid ports, and registration failure after netdev association.
