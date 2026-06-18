# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/main.c

## Purpose
`main.c` is the mlx5 RDMA driver's primary registration and lifecycle implementation. It maps mlx5 core devices into RDMA `ib_device` instances, publishes device and port operations, handles RoCE and InfiniBand port queries, manages user contexts and mmap objects, coordinates events, multiport/LAG, representors, data-direct resources, and staged probe/remove profiles.

## Important APIs, Types, And Functions
Major externally visible functions are `__mlx5_ib_add()`, `__mlx5_ib_remove()`, `mlx5_ib_query_port()`, `mlx5_ib_query_port_speed()`, `set_roce_addr()`, `mlx5_ib_dev_res_cq_init()`, `mlx5_ib_dev_res_srq_init()`, `mlx5_ib_data_direct_bind()`, and `mlx5_ib_data_direct_unbind()`. Module entry/exit are `mlx5_ib_init()` and `mlx5_ib_cleanup()`. Auxiliary probes are `mlx5r_probe()` for RDMA devices and `mlx5r_mp_probe()` for multiport devices.

Key device operation tables are `mlx5_ib_dev_ops`, optional `mlx5_ib_dev_sriov_ops`, `mlx5_ib_dev_mw_ops`, `mlx5_ib_dev_xrc_ops`, `mlx5_ib_dev_common_roce_ops`, representor port ops, and UAPI definitions in `mlx5_ib_defs`. Profiles `pf_profile`, `raw_eth_profile`, and `plane_profile` define ordered init/cleanup stages.

## Control Flow
Module init allocates an emergency translation page, creates the ordered event workqueue, initializes QP event support and ODP, registers representor and data-direct drivers, then registers multiport and RDMA auxiliary drivers. RDMA auxiliary probe allocates `mlx5_ib_dev`, sizes its port array, detects multiplane SMI support for IB, chooses `pf_profile` or `raw_eth_profile`, and calls `__mlx5_ib_add()`.

`__mlx5_ib_add()` runs profile stages in enum order and unwinds already-initialized stages on failure. The normal PF profile initializes base state and special mkeys, flow steering, capabilities and operation tables, non-default port callbacks, RoCE, QP/SRQ tables, device resources, ODP, counters, debugfs, BFREGs, devx whitelist, system-error notifier, RDMA registration, device notifier/MACsec events, UMR pools, delay drop, and restrack. Remove sets `ib_active=false`, runs cleanup in reverse stage order, frees the port array, and deallocates the RDMA device.

Port query flow selects one of three access methods: MAD_IFC for native IB without `ib_virt`, HCA vport access for IB/HCA mode, or NIC vport access for Ethernet/RoCE. RoCE query translates Ethernet PTYS link modes into RDMA width/speed, reflects netdev carrier and MTU, and handles LAG upper netdevs and representors. GID add/delete hooks call MACsec operations and program hardware RoCE address-table entries through `mlx5_core_roce_gid_set()`.

User-context flow validates ABI request versions, optional DevX creation and privileged UID capability, BFREG/UAR allocation strategy, transport-domain allocation, doorbell-page list setup, CQE version negotiation, and response copying. Mmap flow decodes legacy command offsets or RDMA user mmap entries, maps UAR WC/NC pages, core clock pages, MEMIC/VAR/TLP VAR entries, and frees entries through type-specific cleanup.

Event flow converts mlx5 core notifier events into RDMA events on an ordered workqueue. Port changes generate speed, active/error, LID, P_Key, GID, and client-reregister events; P_Key changes schedule GSI QP refresh. System errors walk outstanding QPs and armed CQs to trigger completions, dispatch fatal events, and mark the device inactive. Netdev and LAG notifiers synchronize RoCE port state and RDMA netdev mappings.

Multiport flow maintains global master and unaffiliated-port lists under `mlx5_ib_multiport_mutex`. Masters create a native-port stub, bind matching peer ports by system image GUID, affiliate/unaffiliate NIC vports, track peer netdevs, replay core events, and enable local loopback across master/slave devices. Multiport auxiliary devices either bind to an existing master or wait on the unaffiliated list.

## State And Persistence Behavior
All state is kernel memory and firmware/hardware state. Important in-memory state includes `dev->ib_active`, port arrays, `mlx5_ib_port.roce` netdev tracking, multiport `mpi` pointers and refcounts, `devr` internal PD/CQ/SRQ/XRCD resources, xarrays for ODP and signature MRs, flow DB, data-direct resources, VAR bitmaps, delay-drop debugfs state, and notifier blocks. Firmware state includes PDs, UARs, transport domains, vport RoCE enablement, LAG demux/vport LAG, mkeys, MACsec/RoCE address table entries, and node descriptions. No durable disk state is written.

## Dependencies And Integration Points
`main.c` is the integration point for RDMA core, mlx5 core, eswitch representors, LAG, netdev notifiers, DevX, flow steering, ODP, UMR, memory registration, device memory, counters, congestion debugfs, data-direct, DMAH, MACsec, and auxiliary bus probing. Most other mlx5 RDMA files provide functions installed here into `ib_device_ops` or profile stages.

## Risks
The staged lifecycle must remain strictly symmetric; wrong stage ordering can expose operations before resources exist or free resources while callbacks are live. Several failure paths in `__mlx5_ib_add()` return `-ENOMEM` instead of the original error, which can hide root causes. Mmap offset decoding and RDMA mmap-entry ownership are security-sensitive because they expose PCI BAR pages and device memory to userspace. Multiport refcount/unaffiliate logic depends on correct completion counts under spinlocks. Netdev notifier paths must balance `dev_put()` calls and avoid dispatching events after `ib_active` becomes false. RoCE GID deletion calls `set_roce_addr(..., NULL, attr)`, while `set_roce_addr()` still uses `gid->raw`; this relies on surrounding code/contracts and is a high-value review point.

## Test Signals
Core signals include module load/unload; RDMA auxiliary probe/remove; `ibv_devinfo`, ucontext allocation, DevX contexts, UAR mmap, VAR/UAR uverbs objects; IB and RoCE port query/speed query; RoCE GID add/delete and netdev rescan; LAG active-backup changes; multiport peer hotplug/unplug; representor load/unload; system-error event injection; delay-drop debugfs; ODP/UMR/counter stage init; and failure injection at each profile stage to verify reverse cleanup.
