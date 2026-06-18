# Research: subset-b-003941

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mad.c

## Purpose
`mad.c` implements the mlx4 InfiniBand management datagram path. It bridges ib_core MAD processing to mlx4 firmware through `MAD_IFC`, tracks subnet manager addressing, synthesizes port-management events, and implements SR-IOV paravirtualized QP0/QP1 tunneling so a master PF can multiplex management traffic for VFs. It is a central integration point for subnet management, performance management, SA multicast management, CM paravirtualization, alias GUID updates, P_Key propagation, and tunnel QP lifecycle.

## Important APIs, types, and functions
- Wire/tunnel buffer formats: `struct mlx4_mad_rcv_buf`, `struct mlx4_mad_snd_buf`, `struct mlx4_tunnel_mad`, and `struct mlx4_rcv_tunnel_mad` define DMA-backed receive/send payloads for real special QPs and paravirtual tunnel QPs.
- `mlx4_ib_gen_node_guid()` generates synthetic VF node GUIDs using the OpenIB OUI plus random low bits.
- `mlx4_ib_get_new_demux_tid()` allocates per-port demux transaction IDs with a high-byte marker.
- `mlx4_MAD_IFC()` wraps the firmware `MLX4_CMD_MAD_IFC` command. It prepares command mailboxes, optionally appends work-completion/GRH metadata, sets ignore-key and network-view flags, and copies the 256-byte response MAD back to callers.
- `mlx4_ib_process_mad()` is the ib_device `process_mad` entry. It routes IB-link traffic to `ib_process_mad()` and RoCE/PMA traffic to `iboe_process_mad()`.
- `smp_snoop()`, `handle_port_mgmt_change_event()`, `handle_lid_change_event()`, `handle_client_rereg_event()`, and `handle_slaves_guid_change()` update cached SM AH, SL2VL, GUID, and P_Key state and dispatch ib_core or slave-management events.
- `mlx4_ib_send_to_slave()` demultiplexes ingress wire MADs into a VF tunnel QP. `mlx4_ib_send_to_wire()` multiplexes VF-origin tunnel MADs back onto real QP0/QP1.
- `mlx4_ib_demux_mad()` and `mlx4_ib_multiplex_mad()` classify management classes, rewrite TIDs, resolve slaves by GID or encoded TID, call multicast/CM paravirtual handlers, and enforce SMI policy for VFs.
- `mlx4_ib_alloc_pv_bufs()`, `create_pv_sqp()`, `create_pv_resources()`, `destroy_pv_resources()`, `mlx4_ib_alloc_demux_ctx()`, `mlx4_ib_free_demux_ctx()`, `mlx4_ib_init_sriov()`, and `mlx4_ib_close_sriov()` allocate and tear down per-port/per-slave tunnel resources, CQs, PDs, QPs, DMA buffers, and workqueues.

## Control flow
Normal host MAD processing enters `mlx4_ib_process_mad()`. IB ports pass valid SMP, PMA, vendor, and congestion-management GET/SET requests through `ib_process_mad()`, which may record the previous LID, calls `mlx4_MAD_IFC()`, snoops successful SMP SETs, overrides node description responses for the master, adjusts directed-route status, and replies or consumes as ib_core expects. Ethernet/RoCE ports use `iboe_process_mad()` for PMA counters, synthesizing class-port-info and counter responses from mlx4 flow counters.

For ingress SR-IOV management traffic, real SQP receive completions are handled by `mlx4_ib_sqp_comp_worker()`. It extracts the MAD and GRH, calls `mlx4_ib_demux_mad()`, then reposts the receive buffer. Demux identifies the target slave using RoCE destination GID, IB GRH interface ID, SA well-known GUID, or encoded response TID. It drops unsupported unsolicited VF SMI traffic, delegates SA MCMember traffic to `mlx4_ib_mcg_demux_handler()`, delegates CM to `mlx4_ib_demux_cm_handler()`, and finally calls `mlx4_ib_send_to_slave()` to build a tunnel receive record and post a send to the VF proxy SQP.

For VF-origin management traffic, tunnel receive completions are handled by `mlx4_ib_tunnel_comp_worker()`. `mlx4_ib_multiplex_mad()` validates that the source QP belongs to the expected slave/port, encodes the slave ID into request TIDs, rejects disallowed management classes, gives SA multicast and CM handlers first chance to consume requests, reconstructs an address handle from the tunneled mlx4 AV, maps VF SGID and P_Key indexes into real indexes, applies default VLAN/QoS policy, and calls `mlx4_ib_send_to_wire()`.

Resource lifecycle starts from `mlx4_ib_init_sriov()`. Slaves only initialize CM paravirt state and operate in QP1 tunnel mode. Masters generate slave node GUIDs, initialize alias GUID and sysfs support, create demux contexts per port, initialize multicast-group state, allocate master SQP contexts, and bring up master tunnels. Runtime slave init/shutdown events call `mlx4_ib_tunnels_update_work()`, which creates or destroys tunnel QPs. Teardown marks `is_going_down`, flushes workqueues, destroys SQP/tunnel resources, closes MCG state, and cleans alias GUID/sysfs/CM paravirt services.

## State and persistence behavior
State is in memory and hardware/FW tables; there is no filesystem persistence. Important state includes `dev->send_agent`, `dev->sm_ah`, `dev->sl2vl`, P_Key physical caches and VF mappings, demux `subnet_prefix`, `guid_cache`, `tid`, per-slave tunnel contexts, QP ring indices, and `is_going_down`. DMA buffers persist only for active tunnel/SQP resources and are synchronized around CPU/device access. Transaction IDs and encoded slave IDs are transient correlation mechanisms. SM AH and SL2VL caches are rebuilt from SMP snooping or port-management events.

## Dependencies and integration points
This file depends on ib_core MAD, AH, QP, CQ, PD, DMA, P_Key, GID, and port-event APIs; mlx4 core command, EQE, capability, P_Key, VLAN, flow-counter, and SR-IOV helpers; and local `mlx4_ib.h` declarations for device/QP/demux structures. It integrates directly with `mcg.c` via multicast SA demux/multiplex handlers, CM paravirtual code via `mlx4_ib_demux_cm_handler()`/`mlx4_ib_multiplex_cm_handler()`, alias GUID code via GUID update callbacks, and `main.c` event/probe paths via `mlx4_ib_init_sriov()`, `mlx4_ib_close_sriov()`, and `handle_port_mgmt_change_event()`.

## Risks and edge cases
- Tunnel ring accounting is protected by spinlocks, but correctness depends on send completions always advancing tails and destroying AHs; error paths must keep head/tail and AH ownership balanced.
- Many paths run from workqueues or completion context while teardown may set `is_going_down`; missed flushing or state checks could race QP/CQ destruction.
- VF demux relies on TID high-byte rewriting and GID/P_Key mapping. Bugs can misroute management responses or expose unauthorized SMI/P_Key views.
- `mlx4_MAD_IFC()` uses raw mailbox layouts and offset-based MAD parsing, so ABI or firmware layout drift would be high impact.
- RoCE demux requires GRH parsing and slave lookup; absent/malformed GRH or bonded-port fallback can cause drops.
- `update_sm_ah()` replaces AHs under `sm_lock`, but callers sometimes query or copy AH-derived attributes after lock release; lifetime assumptions must remain valid.

## Test signals
- Build coverage with mlx4 IB/RDMA configs enabled should catch signature drift in ib_core and mlx4 core APIs.
- Runtime tests should include MAD GET/SET on IB ports, directed-route responses, trap forwarding, node-description modify/query, PMA queries on IB and RoCE ports, and port-management EQEs for LID/GID/P_Key/SL2VL changes.
- SR-IOV tests should exercise VF QP0/QP1 tunnel creation/destruction, VF init/shutdown, encoded TID request/response routing, SMI disabled/enabled policy, P_Key remapping, RoCE GID-based demux, bonded ports, and teardown under outstanding completions.
- Multicast and CM tests should verify that SA/CM handlers consume or forward traffic as expected without leaking tunnel buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/main.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mcg.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mcg.c

## Purpose
`mcg.c` implements SR-IOV multicast group paravirtualization for SA MCMember records. The master PF tracks multicast groups per demux port, consolidates VF join/leave requests into real SA requests, rewrites Port_GID to the master's real GID on the wire, fans responses back to the requesting VF with the VF's Port_GID restored, exposes group state through sysfs, and cleans VF memberships on shutdown.

## Important APIs, types, and functions
- `struct ib_sa_mcmember_data` is the packed MCMember record payload used in SA MAD data.
- `struct mcast_group` stores the group record, RB-tree node, mgid0 relocation list entry, per-VF membership and pending queues, state machine, last wire TID, response MAD, sysfs attribute, refcount, timeout work, and cleanup list.
- `struct mcast_member` stores each VF's join state, membership state, pending count, and request list.
- `struct mcast_req` stores queued VF SA MADs plus group/function list links and a cleanup marker.
- `mlx4_ib_mcg_multiplex_handler()` handles VF-origin MCMember SET/DELETE requests.
- `mlx4_ib_mcg_demux_handler()` handles wire-origin MCMember GET_RESP/DELETE_RESP responses.
- `mlx4_ib_mcg_work_handler()` is the central group state-machine worker.
- `mlx4_ib_mcg_timeout_handler()` handles SA response timeouts.
- `mlx4_ib_mcg_port_init()`, `mlx4_ib_mcg_port_cleanup()`, `clean_vf_mcast()`, `mlx4_ib_mcg_init()`, and `mlx4_ib_mcg_destroy()` manage per-port and global workqueues/state.

## Control flow
On a VF MCMember SET or DELETE, `mlx4_ib_mcg_multiplex_handler()` rejects requests while flushing, allocates a `mcast_req`, acquires or creates a group under `ctx->mcg_table_lock`, checks the per-VF pending limit, increments counters/refcounts, queues the request on both the group and VF lists, and schedules `mlx4_ib_mcg_work_handler()`.

The worker first processes any waiting SA response (`MCAST_RESP_READY`), validates the TID, cancels timeout work, updates the group record on success, reports failure status to the waiting VF when needed, and returns the group to `MCAST_IDLE`. It then processes pending requests while idle. Leave requests are validated against the VF's current join bits, immediately acknowledged to the VF, and update local membership counters. Join requests either complete locally if the PF is already a member for all requested bits and the record matches, or send a real SA join using `send_join_to_wire()` and transition to `MCAST_JOIN_SENT`. After pending requests, if local membership counters show the PF no longer needs some join bits, it sends a real SA leave and transitions to `MCAST_LEAVE_SENT`.

Wire responses enter `mlx4_ib_mcg_demux_handler()`. For normal MGIDs it finds the group by RB-tree lookup. For MGID zero joins, where the SM may allocate the MGID, it uses `search_relocate_mgid0_group()` to match by TID, update the group MGID, move the group from the temporary list into the RB-tree, and add sysfs exposure. The response is copied into the group, state becomes `MCAST_RESP_READY`, and the worker is queued.

Timeouts remove or fail the outstanding request depending on `MCAST_JOIN_SENT` or `MCAST_LEAVE_SENT`, potentially clear membership bits, release groups, reset state to idle, and reschedule the worker. Cleanup calls `clean_vf_mcast()` for each VF, queues synthetic clean leave requests for joined groups, waits briefly for the RB-tree to drain, flushes the MCG workqueue, then force-frees any remaining groups.

## State and persistence behavior
All state is runtime memory. Each demux context has an RB-tree keyed by MGID, a special list for MGID zero groups, and an ordered workqueue. Group membership is tracked as three membership counters plus per-VF join-state bitmasks. `refcount` intentionally represents queued requests, worker invocations, and real SA membership; release logic deletes sysfs attributes and removes RB-tree/list entries when it reaches zero. `last_req_tid` correlates wire responses and timeouts. Sysfs group files are transient diagnostics under the per-port MCG sysfs parent.

## Dependencies and integration points
`mcg.c` depends on ib_mad, ib_sa, ib_cache, rbtrees, workqueues, and mlx4_ib demux state. It sends wire MADs through `mlx4_ib_send_to_wire()` and VF replies through `mlx4_ib_send_to_slave()`, uses `dev->sm_ah` from `mad.c` to address the subnet manager, reads `demux->guid_cache[0]` for the real port GID, uses sysfs helpers declared in `mlx4_ib.h`, and is initialized/cleaned by SR-IOV demux setup in `mad.c` and module init in `main.c`.

## Risks and edge cases
- The group state machine is concurrency-sensitive: `mcg_table_lock`, per-group `lock`, delayed timeout work, normal work, cleanup work, and refcount releases must stay ordered.
- MGID zero relocation races with existing groups; collision handling silently drops the new temporary request and releases the group.
- `MAX_PEND_REQS_PER_FUNC` limits VF pressure, but note the condition uses `> MAX_PEND_REQS_PER_FUNC`, allowing one more than the literal maximum before rejecting.
- Cleanup may force-free groups after timeout if refcounts do not drain; this is defensive but can hide a leaked reference or queued work bug.
- TID rewriting and validation are required to avoid applying an SA response to the wrong group.
- `send_mad_to_slave()` assumes `sm_ah` is valid for `rdma_query_ah()` after only checking the send agent; callers rely on port-active ordering.
- Membership counters cover three low join-state bits; if protocol semantics expand, counter logic would need review.

## Test signals
- SR-IOV multicast tests should include VF joins/leaves for full, non-member, send-only, and overlapping join-state bits across multiple VFs.
- Exercise MGID zero allocation, SM failure statuses, wrong-TID responses, timeouts, and duplicate MGID collision during relocation.
- Verify per-VF pending limit behavior and cleanup of pending requests on VF shutdown.
- Confirm sysfs group attributes appear/disappear for nonzero MGIDs and show expected members/refcount/state.
- Run teardown tests with pending joins/leaves, delayed timeout work active, and `ctx->flushing` set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mcg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mlx4_ib.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mlx4_ib.h

## Purpose
`mlx4_ib.h` is the private shared header for the mlx4 RDMA driver. It defines driver constants, object wrappers around ib_core and mlx4 core resources, SR-IOV demux/tunnel structures, RoCE/GID/P_Key/counter state, the top-level `struct mlx4_ib_dev`, container conversion helpers, and cross-file prototypes for the mlx4_ib subsystem.

## Important APIs, types, and functions
- Constants and flags: `MLX4_IB_DRV_NAME`, SQ headroom constants, steering QPN constants, `MLX4_MR_PAGES_ALIGN`, tunnel buffer counts, alias GUID limits, `MLX4_PAGE_SIZE_SUPPORTED`, and QP create flags.
- Object wrappers: `mlx4_ib_ucontext`, `mlx4_ib_pd`, `mlx4_ib_xrcd`, `mlx4_ib_cq`, `mlx4_ib_mr`, `mlx4_ib_mw`, `mlx4_ib_qp`, `mlx4_ib_srq`, `mlx4_ib_ah`, `mlx4_ib_wq`, and `mlx4_ib_rwq_ind_table`.
- Flow and steering: `mlx4_ib_flow`, `mlx4_flow_reg_id`, `mlx4_ib_steering`, and `mlx4_wqn_range`.
- SR-IOV and MAD tunneling: `mlx4_ib_tunnel_header`, `mlx4_rcv_tunnel_hdr`, `mlx4_ib_proxy_sqp_hdr`, `mlx4_ib_demux_pv_qp`, `mlx4_ib_demux_pv_ctx`, `mlx4_ib_demux_ctx`, and `mlx4_ib_sriov`.
- Alias GUID state: `mlx4_sriov_alias_guid_info_rec_det`, `mlx4_sriov_alias_guid_port_rec_det`, and `mlx4_sriov_alias_guid`.
- RoCE state: `gid_cache_context`, `gid_entry`, `mlx4_port_gid_table`, and `mlx4_ib_iboe`.
- Top-level device: `struct mlx4_ib_dev` contains the embedded `ib_device`, mlx4 core device pointer, private UAR/PD, MAD agents, SM AHs, SL2VL cache, SR-IOV state, RoCE netdev/GID state, P_Key maps, counters, sysfs objects, steering resources, QP list, diagnostic counters, and mlx4 event notifier.
- Inline helpers: `to_mdev()`, `to_mpd()`, `to_mmr()`, `to_mqp()`, and similar container conversions; `mlx4_ib_bond_next_port()`; `mlx4_ib_ah_grh_present()`; and `mlx4_ib_umem_calc_optimal_mtt_size()`.

## Control flow
The header does not contain runtime control flow beyond inline helpers. Its declarations define the contract across implementation files. `main.c` populates `mlx4_ib_dev` and installs ops using the object sizes declared here. `mad.c` uses demux, tunnel, alias GUID, SL2VL, and P_Key structures. `mcg.c` uses `mlx4_ib_demux_ctx` and send helpers. `mr.c` uses MR/MW wrappers and the optimal MTT-size helper. QP/CQ/SRQ/AH implementation files use the shared wrapper structs and prototypes.

## State and persistence behavior
All structures describe in-memory driver state, with embedded handles to mlx4 hardware resources such as MPTs, MTTs, QPs, CQs, PDs, UARs, counters, and EQs. The header records which state is protected by locks in comments or member names: CQ locks and resize mutexes, QP mutexes, ucontext doorbell/WQN range mutexes, SR-IOV going-down spinlock, MCG table mutex, RoCE spinlock, counter mutexes, and reset-flow resource lock. Persistent effects occur only through implementation files that program hardware or expose sysfs/ib_device objects.

## Dependencies and integration points
The header includes Linux list/mutex/idr/notifier primitives, RDMA verbs, umem, MAD, SA APIs, and mlx4 device/doorbell/QP/CQ headers. It is the coupling layer for the whole mlx4_ib driver: prototypes span MR, CQ, AH, SRQ, QP, MAD, MCG, CM paravirt, alias GUID, sysfs, steering, WQ/RSS, and event subsystems. Any structure change can impact multiple C files and ib_core object layout registration.

## Risks and edge cases
- Embedded ib_core objects plus `container_of` helpers require object allocation sizes in `main.c` to match these structures exactly.
- Several arrays are dimensioned by mlx4 constants such as `MLX4_MAX_PORTS`, `MLX4_MFUNC_MAX`, `MLX4_MAX_PORT_GIDS`, and fixed alias GUID counts; capability mismatches can cause out-of-range bugs if callers do not validate indexes.
- SR-IOV demux state mixes workqueues, QP resources, DMA rings, atomic TIDs, GUID cache, and MCG table locks; lifecycle must follow the structure ownership model.
- Header-level inline `mlx4_ib_umem_calc_optimal_mtt_size()` determines MR page size behavior and returns `order_base_2(pg_sz)`; callers must treat negative values as errors and shift values as page orders.
- `mlx4_ib_ah_grh_present()` infers GRH presence differently for Ethernet and IB, which affects send-path header construction.

## Test signals
- Full-driver build is the primary signal for prototype/object-layout consistency.
- KASAN/lockdep tests around QP/CQ/MR/SR-IOV operations can expose misuse of shared structures and locks.
- ABI-sensitive tests should cover uverbs object allocation for all wrappers whose sizes are registered in `main.c`.
- Capability matrix tests should vary number of ports, VFs, GID/P_Key table lengths, RoCE v1/v2, RSS, XRC, memory windows, and flow steering to exercise array and optional-op assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mlx4_ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mr.c

## Purpose
`mr.c` implements mlx4 memory registration verbs: DMA MRs, user MRs, reregistration, deregistration, memory windows, fast-registration MRs, and scatterlist mapping into fast-reg page lists. It translates ib_core access flags and memory objects into mlx4 MPT/MTT resources and keeps user memory pinning synchronized with hardware memory translation state.

## Important APIs, types, and functions
- `convert_access()` maps `IB_ACCESS_*` bits to mlx4 `MLX4_PERM_*` flags and always grants local read.
- `to_mlx4_type()` maps ib_core MW type 1/2 to mlx4 MW type values.
- `mlx4_ib_get_dma_mr()` allocates and enables a whole-address-space DMA MR for a PD.
- `mlx4_ib_umem_write_mtt()` iterates DMA blocks in an `ib_umem` and writes them into an mlx4 MTT.
- `mlx4_get_umem_mr()` pins user memory, upgrading to local write when the VMA is writable so later reregistration can add write access without repinning.
- `mlx4_ib_reg_user_mr()` pins user memory, chooses an optimal MTT page shift, allocates an MPT/MTT, writes MTT entries, enables the MR, and returns lkey/rkey/page size.
- `mlx4_ib_rereg_user_mr()` updates PD, access flags, and/or translation for an existing MR using hardware MPT get/change/write helpers.
- `mlx4_alloc_priv_pages()` and `mlx4_free_priv_pages()` allocate a DMA-mapped private page list for fast-reg MRs.
- `mlx4_ib_dereg_mr()` frees private pages, mlx4 MR hardware resources, user memory, and wrapper memory.
- `mlx4_ib_alloc_mw()` and `mlx4_ib_dealloc_mw()` manage mlx4 memory windows.
- `mlx4_ib_alloc_mr()` creates fast-reg memory MRs with private page lists.
- `mlx4_ib_map_mr_sg()` maps a scatterlist into a fast-reg MR page array through `ib_sg_to_pages()` and `mlx4_set_page()`.

## Control flow
DMA MR allocation creates a zeroed wrapper, allocates an mlx4 MR with base zero and size `~0ull`, enables it, mirrors the hardware key into lkey/rkey, and returns the embedded `ib_mr`. Failure paths free the partially created mlx4 MR and wrapper.

User MR registration rejects DMA handles, allocates a wrapper, pins memory with `mlx4_get_umem_mr()`, computes best page size through `mlx4_ib_umem_calc_optimal_mtt_size()`, allocates an mlx4 MR with the requested IOVA/length/access and number of MTTs, writes each DMA block to the MTT, enables the MR, sets keys and `ibmr.page_size`, and unwinds in reverse on error.

Reregistration first obtains the hardware MPT entry and assumes uverbs serializes deregistration against reregistration. It optionally changes PD, validates access upgrades against `umem->writable`, changes access permissions, and for translation changes cleans old memory translation, releases old umem, pins the new region, rewrites MPT memory parameters and MTT entries, updates cached IOVA/size, then writes the MPT back. On failure it returns `ERR_PTR(err)` and leaves deregistration responsible for cleanup when hardware transfer could not be completed.

Fast-reg MR allocation validates `IB_MR_TYPE_MEM_REG` and `MLX4_MAX_FAST_REG_PAGES`, allocates an MR with empty translation, allocates a single page for the DMA-visible page list aligned to `MLX4_MR_PAGES_ALIGN`, enables the MR, and records max pages. Mapping resets `npages`, syncs the page list for CPU, uses `ib_sg_to_pages()` to append present-bit physical addresses, then syncs back for device.

## State and persistence behavior
MR/MW state is per-object and persists until deregistration/deallocation. User MRs own an `ib_umem` pin and mlx4 `struct mlx4_mr`; fast-reg MRs own a DMA-mapped private page list plus mlx4 MR; MWs own mlx4 MW resources. Keys are hardware-generated and copied into ib_core objects. There is no disk persistence. Hardware translation state persists in MPT/MTT tables until explicitly freed or rewritten.

## Dependencies and integration points
`mr.c` depends on ib_core verbs, `ib_umem`, RDMA DMA block iterators, scatterlist-to-pages helpers, Linux MM VMA locking, DMA mapping APIs, and mlx4 core MR/MW/MPT/MTT helpers. It is wired into ib_device ops by `main.c` through `get_dma_mr`, `reg_user_mr`, `rereg_user_mr`, `dereg_mr`, `alloc_mr`, `map_mr_sg`, `alloc_mw`, and `dealloc_mw`. It relies on wrapper definitions and page-size helper from `mlx4_ib.h`.

## Risks and edge cases
- `mlx4_get_umem_mr()` only checks a single VMA for read-only registration optimization; multi-VMA registrations conservatively become writable, but behavior depends on current MM layout.
- Reregistration translation failure after releasing the old umem can leave the MR partially updated; callers rely on later deregistration cleanup and the explicit `umem = NULL` guard for failed repinning.
- Access upgrade is rejected if the existing umem is not writable, but correctness depends on `umem->writable` accurately reflecting the original pin.
- Fast-reg private page allocation uses one page and assumes `max_pages <= MLX4_MAX_FAST_REG_PAGES` keeps the aligned map within that page.
- `mlx4_set_page()` fails with `-ENOMEM` when scatterlist expansion exceeds `max_pages`; callers must respect partial mapping failures.
- DMA sync direction and page-list lifetime must remain paired with QP fast-reg use to avoid stale device-visible page addresses.

## Test signals
- User MR tests should cover read-only and writable mappings, multi-VMA ranges, access flag combinations, invalid DMA handle use, large page-size selection, and MTT write failures.
- Reregistration tests should cover PD-only, access-only, translation-only, combined changes, access upgrade rejection, repin failure, MPT write failure, and deregistration after failed reregistration.
- Fast-reg tests should cover max page boundary, scatterlist offsets, too many SG pages, DMA sync correctness, and deregistration after mapping.
- MW tests should cover type 1/type 2 allocation, invalid type rejection through core setup, enable failure unwind, and deallocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mr.c -->
