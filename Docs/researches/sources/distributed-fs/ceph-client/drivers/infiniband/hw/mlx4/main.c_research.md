# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/main.c

## Purpose
`main.c` is the mlx4 InfiniBand/RoCE driver entry point. It registers the auxiliary mlx4 IB driver, creates and registers the `ib_device`, installs verbs operations, exposes device attributes and hardware stats, initializes ports, GID/P_Key/counter state, handles netdevice and mlx4 core events, and coordinates probe/remove lifecycle for MAD, SR-IOV, flow steering, XRC, memory windows, RSS/WQ, and diagnostic counters.

## Important APIs, types, and functions
- Module and driver registration: `mlx4_ib_init()`, `mlx4_ib_cleanup()`, `mlx4_ib_adrv`, and `mlx4_ib_id_table`.
- Probe/remove: `mlx4_ib_probe()` allocates `struct mlx4_ib_dev`, private PD/UAR/EQs/counters, sets `ib_device_ops`, initializes node data and SL2VL, registers RDMA device, MAD/SR-IOV/netdevice/event services, and active VF tunnels. `mlx4_ib_remove()` reverses these resources.
- Device/port query APIs: `mlx4_ib_query_device()`, `ib_link_query_port()`, `eth_link_query_port()`, `__mlx4_ib_query_port()`, `__mlx4_ib_query_gid()`, `__mlx4_ib_query_pkey()`, and `mlx4_port_immutable()`.
- Uverbs context and resource APIs: `mlx4_ib_alloc_ucontext()`, `mlx4_ib_mmap()`, `mlx4_ib_alloc_pd()`, `mlx4_ib_alloc_xrcd()`, and related deallocation paths.
- RoCE GID table management: `mlx4_ib_add_gid()`, `mlx4_ib_del_gid()`, `mlx4_ib_update_gids_v1()`, `mlx4_ib_update_gids_v1_v2()`, and `mlx4_ib_gid_index_to_real_index()`.
- Flow steering: `parse_flow_attr()`, `__mlx4_ib_create_flow()`, `mlx4_ib_create_flow()`, `mlx4_ib_destroy_flow()`, `mlx4_ib_steer_qp_alloc()`, `mlx4_ib_steer_qp_reg()`, and helpers for default/dont-trap/tunnel rules.
- Multicast attach/detach: `mlx4_ib_mcg_attach()`, `mlx4_ib_mcg_detach()`, `add_gid_entry()`, and `mlx4_ib_add_mc()`.
- Event handling: `mlx4_ib_event()`, `do_slave_init()`, `mlx4_ib_handle_catas_error()`, `handle_bonded_port_state_event()`, `mlx4_sched_ib_sl2vl_update_work()`, and netdev notifier functions.

## Control flow
Module load creates the ordered global workqueue, initializes QP event, CM, and MCG subsystems, then registers the auxiliary driver. Probe starts only when mlx4 exposes IB transport ports. It allocates an RDMA device wrapper, reserves a private PD and UAR, maps the UAR page, sets base ib_device metadata, layers optional ops based on hardware capabilities, allocates completion EQ mappings, queries node data through `MAD_IFC`, initializes SL2VL and counter tables, reserves flow-steering QPN ranges when supported, initializes RoCE MAC defaults, diagnostic counters, and then registers the RDMA device. After registration it starts MAD agents, SR-IOV services, netdevice notifier, RoCE v2 UDP port config, devlink IB port type, P_Key mappings, active VF tunnels, and mlx4 core event notifications.

`ib_device_ops` callbacks feed most user and kernel verbs activity. Device and port queries use either firmware MADs for IB or mlx4 port/netdev state for Ethernet. Ucontext allocation reserves a UAR and returns ABI-specific capabilities; mmap exposes UAR, BlueFlame, or HCA clock pages. PD/XRCD/flow/multicast callbacks allocate mlx4 core resources and maintain local lists/caches for cleanup and detach.

RoCE GID add/delete is reference-counted under `iboe.lock`. A new GID chooses a free hardware slot, allocates a `gid_cache_context`, snapshots the table, and programs firmware using either legacy GID table or RoCE v1/v2 address format. Delete decrements the context refcount and reprograms hardware when the last reference is removed. Bonded mode maps application-visible port indexes to hardware port 1/2 as needed.

Flow creation validates flags and flow specs, maps ib_core flow specs to mlx4 hardware rule IDs, adds default IB L2 rules for certain IPv4-over-IB patterns, handles dont-trap sniffer cases, optionally mirrors bonded rules on port 2, and adds tunnel steering for VXLAN offload. Destroy walks registered IDs and detaches each hardware rule.

Event handling receives mlx4 core events. Port up/down events dispatch ib_core port events, update alias GUID/SL2VL as needed, and coalesce bonded state. Port-management-change events are queued to `handle_port_mgmt_change_event()` from `mad.c` for masters or processed inline for non-masters. Slave init/shutdown schedules per-port tunnel creation/destruction and alias GUID notifications. Catastrophic error marks `ib_active=false`, dispatches device fatal, and notifies CQs with outstanding QP work.

## State and persistence behavior
Driver state is memory-backed and tied to the lifetime of `struct mlx4_ib_dev`. Persistent-like hardware state includes programmed GID tables, flow rules, counters, P_Key mappings, EQ assignments, UAR/PD allocations, and devlink port type. In-memory state includes RoCE netdev pointers/MACs/GID slots, counters lists, flow-steering QPN bitmap, QP list for reset handling, diagnostic counter descriptors, SR-IOV demux state, and active flags. The module parameter `sm_guid_assign` is read-only at runtime and controls alias GUID assignment behavior elsewhere.

## Dependencies and integration points
`main.c` integrates mlx4 core auxiliary devices, mlx4 command/resource APIs, ib_core device registration and verbs, uverbs ABI structures, RDMA netdev/port cache helpers, devlink, Linux netdevice notifier infrastructure, bonding, and local mlx4_ib subsystems (`mad.c`, `mcg.c`, CM, QP, CQ, SRQ, AH, WQ, sysfs, alias GUID). Probe ordering is important: ib_device ops and node data are prepared before registration; MAD and SR-IOV services start after registration; event notifier starts after active VF tunnel setup.

## Risks and edge cases
- Probe has many staged allocations and labels; cleanup ordering must match resource ownership exactly, especially around registered devices, netdevice notifiers, SR-IOV workqueues, flow-steering ranges, and counters.
- `ib_active` gates ucontext allocation and is cleared on remove/catastrophic errors, but existing resources still rely on lower-level teardown synchronization.
- RoCE GID add/delete snapshots the table outside the spinlock for firmware programming; rollback paths must preserve refcounts and table contents under failures.
- Bonded mode rewrites ports for queries, flows, counters, and netdev lookups; missing mirrored cleanup can leave hardware rules or counters inconsistent.
- Flow spec parsing uses size/offset arithmetic on user-provided ib_flow_attr layouts; validation coverage is important for unsupported fields and malformed sizes.
- Netdev callbacks store raw `net_device *` pointers under lock and use `dev_hold()`/`dev_put()` in selected paths; NULL handling and lifetime around unregister are sensitive.
- Catastrophic error CQ notification walks QPs and CQs under multiple locks and invokes completion callbacks; lock ordering must avoid deadlocks with QP/CQ destroy.

## Test signals
- Build with mlx4, RDMA core, RoCE v2, SR-IOV, XRC, memory-window, RSS, and flow-steering configurations.
- Probe/remove tests should cover no-IB-port devices, IB-only, RoCE-only, mixed ports, bonded devices, multifunction master, and VF/slave devices.
- Uverbs tests should cover query_device ABI variants, mmap offsets 0/1/3, PD/XRCD allocation, MR/MW ops, WQ/RSS availability, and `ib_active` behavior during remove.
- RoCE tests should add/delete duplicate GIDs, VLAN-tagged GIDs, full-table failure, rollback on firmware update failure, netdev register/unregister/changeaddr/up/down, and bonded active-slave changes.
- Flow tests should exercise normal, default, sniffer, dont-trap, invalid flags, unsupported fields, bonded mirror cleanup, and VXLAN tunnel steering.
- Event tests should inject port up/down, port-management changes, slave init/shutdown, and catastrophic error while QPs have outstanding send/receive work.
