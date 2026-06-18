# subset-b-003942 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/qp.c

## Purpose
This file implements the mlx4 InfiniBand queue pair, receive work queue, RSS indirection, work request posting, state transition, query, destroy, and drain paths. It is the main mlx4 verbs bridge between RDMA core QP/WQ objects and mlx4 firmware resources: QPN ranges, QP contexts, MTTs, doorbells, CQ linkage, SRQ linkage, steering state, RoCE MAC/VLAN state, and SR-IOV proxy/tunnel special QPs.

## Important APIs, types, and functions
- Public verbs entry points: `mlx4_ib_create_qp`, `mlx4_ib_destroy_qp`, `mlx4_ib_modify_qp`, `mlx4_ib_query_qp`, `mlx4_ib_post_send`, `mlx4_ib_post_recv`, `mlx4_ib_create_wq`, `mlx4_ib_modify_wq`, `mlx4_ib_destroy_wq`, `mlx4_ib_create_rwq_ind_table`, `mlx4_ib_drain_sq`, `mlx4_ib_drain_rq`, `mlx4_ib_qp_event_init`, and `mlx4_ib_qp_event_cleanup`.
- Core lifecycle helpers: `create_qp_common`, `destroy_qp_common`, `_mlx4_ib_modify_qp`, `__mlx4_ib_modify_qp`, `create_rq`, `create_qp_rss`, `destroy_qp_rss`, `bringup_rss_rwqs`, and `bring_down_rss_rwqs`.
- Posting helpers: `_mlx4_ib_post_send`, `_mlx4_ib_post_recv`, `mlx4_wq_overflow`, `set_data_seg`, `set_datagram_seg`, `set_tunnel_datagram_seg`, `build_mlx_header`, `build_sriov_qp0_header`, `build_tunnel_header`, `build_lso_seg`, and memory-registration segment builders.
- State and transport helpers: `to_mlx4_state`, `to_ib_qp_state`, `to_mlx4_st`, `to_mlx4_access_flags`, `_mlx4_set_path`, `handle_eth_ud_smac_index`, `create_qp_lb_counter`, and RoCE mode conversion.

## Control flow
QP creation validates type, flags, user command ABI, and capabilities, then sizes RQ/SQ rings, maps user memory or allocates kernel buffers, builds MTTs, maps/allocates doorbells, reserves a QPN, allocates the mlx4 QP, precomputes the doorbell QPN, links the QP into device and CQ reset-flow lists, and sets software state to RESET. Special paths exist for SMI/GSI proxy and tunnel QPs, RoCEv2 GSI shadow QPs, raw-packet WQs, XRC targets/initiators, netif steering QPs, and RSS QPs. Destruction reverses the state to RESET when needed, unregisters MAC/VLAN candidates, cleans kernel CQs, removes reset-flow links, frees QPN ranges, MTTs, buffers, WRID arrays, proxy buffers, and gid entries.

Modification is guarded by `qp->mutex` and RDMA-core transition validation. The low-level `__mlx4_ib_modify_qp` allocates a QP context, fills flags, state, service type, path MTU, queue sizes, CQs, PD, access bits, PSNs, retry timers, P_Key, Q_Key, SRQ number, RoCE mode, RSS context, counters, steering, MAC/VLAN indexes, and user UAR index, then calls `mlx4_qp_modify`. On success it updates cached state and side-effect ownership; on failure it unregisters candidates and rolls back steering/counters. QP0 state transitions also call `mlx4_INIT_PORT` or `mlx4_CLOSE_PORT`.

Posting sends locks `sq.lock`, rejects device internal error unless draining, checks overflow and SGE count, builds type-specific WQE segments, writes data segments in reverse order, uses write barriers before ownership and doorbell writes, rings the UAR doorbell, stamps prefetched WQEs invalid, and advances SQ head/next indices. Posting receives locks `rq.lock`, checks overflow and SGE count, writes scatter segments and proxy receive header entries, updates WRID, advances RQ head, and updates the doorbell record. Drain paths move the QP to ERR, post a synthetic WR, and wait for the CQ completion with special handling for direct polling and reset/internal-error CQ processing.

## State and persistence behavior
All persistent state is in kernel memory and firmware resources: `mlx4_ib_qp` caches queue heads/tails, SQ/RQ layout, flags, state, port, counters, MAC/VLAN registrations, RSS use counts, WQ ranges, and gid/steering lists. User QPs persist their queue memory in user umem and user doorbell mappings; kernel QPs own mlx4 buffers, WRID arrays, and doorbell pages. Firmware state is represented by allocated QPNs, QP contexts, MTTs, counters, steering registrations, and MAC/VLAN table entries. There is no disk persistence.

## Dependencies and integration points
The file integrates with RDMA core verbs, mlx4 core firmware commands/resource allocators, CQ cleanup, SRQ handling, XRC, RoCE GID/cache helpers, netdevice addressing, steering, multicast, counter tables, reset-flow lists, and SR-IOV special QP plumbing. It depends on `mlx4_ib.h`, `rdma/ib_cache.h`, `rdma/ib_pack.h`, `rdma/ib_addr.h`, `rdma/uverbs_ioctl.h`, and mlx4 kernel headers.

## Risks
The highest-risk areas are WQE layout and barriers, queue overflow accounting, QP state transition side effects, RoCE MAC/VLAN candidate rollback, SR-IOV proxy/tunnel header construction, GSI RoCEv2 shadow QP synchronization, RSS WQ use-count rollback, reset/internal-error races, and lock ordering between CQs and reset-flow lists. Bugs here can leak firmware resources, corrupt queues, misroute packets, hang drains, or expose invalid user ABI behavior.

## Test signals
Useful signals include RDMA CM/ibverbs QP lifecycle tests across RC/UC/UD/raw-packet/XRC, user and kernel QP creation with boundary capabilities, post-send/receive overflow and bad-SGE tests, RoCE v1/v2 GSI traffic, SR-IOV QP0/QP1 proxy traffic, RSS indirection table validation, QP query after transitions, reset/internal-error drain behavior, CQ cleanup after reset, MAC/VLAN registration leak checks, and lockdep/KASAN/KCSAN runs around concurrent modify/destroy/post paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/srq.c

## Purpose
This file implements mlx4 shared receive queue verbs. It creates, modifies, queries, destroys, posts receives to, and recycles WQEs for basic and XRC SRQs while translating mlx4 SRQ events to RDMA core events.

## Important APIs, types, and functions
The public functions are `mlx4_ib_create_srq`, `mlx4_ib_modify_srq`, `mlx4_ib_query_srq`, `mlx4_ib_destroy_srq`, `mlx4_ib_free_srq_wqe`, and `mlx4_ib_post_srq_recv`. Internally, `get_wqe` computes WQE addresses in either a kernel mlx4 buffer or user-backed MTT address space, and `mlx4_ib_srq_event` maps `MLX4_EVENT_TYPE_SRQ_LIMIT` and `MLX4_EVENT_TYPE_SRQ_CATAS_ERROR` to `IB_EVENT_SRQ_LIMIT_REACHED` and `IB_EVENT_SRQ_ERR`.

## Control flow
Creation rejects unsupported SRQ types and oversized capabilities, initializes mutex/spinlock state, rounds the WQE count to a power of two with one reserved entry, computes descriptor size, then chooses a user or kernel allocation path. User SRQs copy the create command, pin user memory, build an MTT, and map the user doorbell. Kernel SRQs allocate a doorbell, buffer, initialize the WQE free-list through next-index segments, invalidate unused data segments, build an MTT, and allocate the WRID array. Both paths call `mlx4_srq_alloc` with PD, optional CQ number, XRC domain, MTT, and doorbell DMA, then return the SRQN to userspace when requested.

Modification only supports arming the limit watermark with `mlx4_srq_arm`; resizing is rejected. Query calls `mlx4_srq_query` and returns limit, max WR, and max SGE. Destroy frees the firmware SRQ, MTT, user or kernel backing resources, doorbell, and umem.

Posting receives is serialized by `srq->lock`. It rejects internal-error devices, validates SGE count and free-list availability, records WRIDs, pops WQEs from the free-list, fills data segments, invalidates the first unused segment, increments the producer counter, uses a write barrier, and updates the doorbell record. Completed WQEs are returned through `mlx4_ib_free_srq_wqe`, which pushes the index onto the tail of the free-list.

## State and persistence behavior
The SRQ state is runtime-only: `msrq.max`, `max_gs`, WQE shift, head/tail free-list pointers, WQE counter, WRID array, umem/buffer, MTT, and doorbell record. Firmware persists the SRQ until `mlx4_srq_free`; no state survives driver teardown.

## Dependencies and integration points
The file depends on mlx4 SRQ/QP core APIs, mlx4 buffer/MTT helpers, RDMA uverbs ABI copy helpers, XRC objects, CQs for XRC/event delivery, PDs, DMA/umem memory pinning, and RDMA event callbacks.

## Risks
Important risks are free-list corruption under concurrent post/complete, incorrect WQE descriptor sizing, missing invalid LKEY termination, user umem/doorbell cleanup leaks on partial creation failure, unsupported resize expectations, and incorrect behavior during `MLX4_DEVICE_STATE_INTERNAL_ERROR`.

## Test signals
Exercise basic and XRC SRQ create/destroy, boundary max WR/SGE, user and kernel SRQ posting, limit arming and event delivery, free-WQE recycling under completion load, invalid SGE rejection, no-resize rejection, and fault-injection cleanup for MTT, doorbell, umem, and firmware allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/sysfs.c

## Purpose
This file builds the mlx4 InfiniBand SR-IOV sysfs surface. It exposes master-only IOV port trees for administrative alias GUIDs, operational GIDs, physical P_Keys, multicast group attributes, per-VF virtual-to-physical P_Key mappings, GID index views, and SMI enablement controls.

## Important APIs, types, and functions
Public entry points are `mlx4_ib_device_register_sysfs`, `mlx4_ib_device_unregister_sysfs`, `add_sysfs_port_mcg_attr`, and `del_sysfs_port_mcg_attr`. Key helpers include `show_admin_alias_guid`, `store_admin_alias_guid`, `show_port_gid`, `show_phys_port_pkey`, `add_port_entries`, `register_pkey_tree`, `unregister_pkey_tree`, `add_port`, `add_vf_smi_entries`, and `remove_vf_smi_entries`. The local `struct mlx4_port` wraps a kobject plus attribute groups for per-slave/port P_Key and GID mappings.

## Control flow
Registration only runs on master devices. It creates an `iov` kobject under the IB device, a physical `ports` subtree, and for each RDMA port creates `admin_guids`, `gids`, `pkeys`, and `mcgs` subdirectories. Each admin GUID file can be read and written; writes update the cached alias GUID record under `ag_work_lock`, mark the record idle/pending, set the admin GUID in mlx4 core, update the component mask, and queue alias GUID work. GID and physical P_Key entries are read-only views backed by mlx4 query helpers.

The P_Key tree creates one device directory per PF/VF and a `ports/<port>/pkey_idx` group for active ports. Dom0/master mappings are read-only; VF mappings can be written on InfiniBand ports, update `virt2phys_pkey`, synchronize the hardware P_Key table, and generate a P_Key event. The `gid_idx` group exposes the slave id. Non-Ethernet non-master VF ports also receive `smi_enabled` and `enable_smi_admin` files.

Unregistration tears down alias GUID trees, P_Key trees, sysfs groups, optional SMI files, and kobject references.

## State and persistence behavior
The sysfs tree reflects runtime driver state. Writes mutate in-memory SR-IOV structures and hardware/admin-guid state through mlx4 core, but this file does not persist configuration to disk. Kobject lifetimes and reference counts are the main persistence concern across register/unregister.

## Dependencies and integration points
This code integrates with Linux sysfs/kobject APIs, mlx4 SR-IOV alias GUID and P_Key management, RDMA port/GID/P_Key query helpers, active port discovery, VF SMI controls, and the driver's multicast group sysfs hooks.

## Risks
Risks include kobject reference-count imbalance, partial-registration cleanup ordering, fixed-length sysfs attribute names, unchecked `sscanf` conversions for admin GUID writes, concurrent alias GUID updates, exposing writes on unsupported transport modes, and cleanup assumptions around multiple `kobject_put` calls. Incorrect P_Key mapping can disrupt VF isolation and traffic authorization.

## Test signals
Validate master versus non-master behavior, full sysfs tree creation/removal with kmemleak/refcount diagnostics, admin GUID read/write including reserved GUID 0 behavior, P_Key VF remap and event generation, SMI toggles on IB but not Ethernet ports, MCG attribute add/remove, failure injection at every kobject allocation step, and concurrent sysfs access during device unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Kconfig

## Purpose
This Kconfig entry defines `MLX5_INFINIBAND`, the tristate option enabling the mlx5 RDMA/InfiniBand driver for Mellanox fifth-generation ConnectX-family adapters.

## Important APIs, types, and functions
There are no C APIs in this file. The important symbol is `CONFIG_MLX5_INFINIBAND`. Its dependency expression is `NETDEVICES && ETHERNET && PCI && MLX5_CORE`, and the user-visible prompt is "Mellanox 5th generation network adapters (ConnectX series) support".

## Control flow
At kernel configuration time this symbol determines whether the mlx5 IB module is not built, built in, or built as a module. The help text states that it provides low-level InfiniBand support required for protocols such as IP-over-IB and SRP on Mellanox Connect-IB PCIe HCAs.

## State and persistence behavior
The selected value persists only in the kernel build configuration, normally `.config`, and controls compilation/linkage. It has no runtime state.

## Dependencies and integration points
The option depends on the networking, Ethernet, PCI, and mlx5 core driver stacks. The corresponding Makefile consumes the symbol via `obj-$(CONFIG_MLX5_INFINIBAND)`.

## Risks
Risk is mostly configuration-level: missing dependencies hide the driver, and enabling mlx5 IB without mlx5 core is impossible by design. Help text is narrow compared with the broader mlx5 RDMA feature set but does not affect behavior.

## Test signals
Check all three tristate modes, ensure `mlx5_ib.o` appears only when expected, verify dependency visibility in menuconfig/allmodconfig, and boot/module-load test with `CONFIG_MLX5_CORE` enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Makefile

## Purpose
This Makefile declares how the mlx5 InfiniBand/RDMA driver object is built and which feature-specific source files are conditionally included.

## Important APIs, types, and functions
The primary build target is `mlx5_ib.o`, selected by `obj-$(CONFIG_MLX5_INFINIBAND)`. The base object list includes address handles, command wrappers, congestion, counters, CQ, data-direct, device memory, DMAH, doorbell, flow steering, GSI, virtualization, MAD, main, memory, MR, QP/QPC, restrack, SRQ/SRQ commands, UMR, and WR logic. Conditional additions include `odp.o`, `ib_rep.o`, `devx.o`, `qos.o`, `std_types.o`, and `macsec.o`.

## Control flow
Kbuild assembles all `mlx5_ib-y` objects into one driver object when `CONFIG_MLX5_INFINIBAND` is enabled. Optional objects are appended when their feature symbols are enabled: on-demand paging, eswitch representors, user access/devx, and MACsec.

## State and persistence behavior
This file has no runtime state. Its only persistent effect is the compiled module or built-in object composition.

## Dependencies and integration points
It integrates with the Kconfig symbol and the Linux kernel kbuild system. It also documents feature boundaries in the mlx5 IB driver by mapping config symbols to compilation units.

## Risks
Build risks include missing an object for a feature registration path, stale conditional dependencies, and unintentionally compiling user-access or eswitch code without the required core support. Because many files register `ib_device_ops`, omitted objects can create link failures or missing runtime features.

## Test signals
Run build matrix coverage for baseline, ODP, eswitch, user access/devx, and MACsec configurations. Verify module link symbols and smoke-test load/unload for built-in and modular builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ah.c

## Purpose
This file implements mlx5 address-handle creation and query. It converts RDMA core `rdma_ah_attr` values into an mlx5 address vector used by UD/RoCE send paths and returns selected AH data to userspace.

## Important APIs, types, and functions
The public functions are `mlx5_ib_create_ah` and `mlx5_ib_query_ah`. Internal helpers are `mlx5_ah_get_udp_sport`, which selects a RoCEv2 UDP source port from the GRH flow label or device minimum, and `create_ib_ah`, which fills `struct mlx5_ib_ah` address-vector fields.

## Control flow
Creation first rejects RoCE AHs without GRH. For userspace RoCE AH creation, it validates the response length and copies the resolved destination MAC back through udata. The helper then copies GRH destination GID, flow label, SGID index, hop limit, and traffic class when present; translates static rate; and diverges by AH type. RoCE AHs set optional LAG transmit port, destination MAC, UDP source port, SL bits, and ECN enablement for RoCEv2. InfiniBand AHs set DLID, path bits, and SL.

Query clears the output attribute, restores type, checks whether the AV has GRH-present state, populates GRH and DGID, then sets DLID, static rate, and SL from the stored AV fields.

## State and persistence behavior
The AH state is the in-memory `mlx5_ib_ah` address vector. It is stable until the AH is destroyed by RDMA core. No firmware object is allocated here and there is no disk persistence.

## Dependencies and integration points
The file depends on RDMA AH helpers, GID type semantics, RoCE UDP port helpers, rate translation via `mlx5r_ib_rate`, LAG slave selection, user ABI response structures, and mlx5 send-path AV consumers.

## Risks
Risks include incorrect GRH requirement enforcement for RoCE, wrong SL bit packing for RoCE versus IB, stale assumptions about `sgid_attr`, UDP source-port entropy mismatch, ECN bit behavior, and query not reconstructing all RoCE-specific attributes such as MAC fields.

## Test signals
Create/query IB, RoCEv1, and RoCEv2 AHs; validate udata DMAC response length handling; test flow-label-derived UDP sport; verify LAG transmit slave mapping; send UD traffic across SL/rate settings; and run negative tests for RoCE without GRH and invalid static rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.c

## Purpose
This file provides mlx5 IB-facing wrappers for common mlx5 firmware commands. It keeps command input/output packing local to the driver and exposes concise helpers for special mkeys, congestion query, transport objects, multicast groups, XRC domains, MAD IFC, UARs, and VUID query.

## Important APIs, types, and functions
Functions exported through `cmd.h` include `mlx5r_cmd_query_special_mkeys`, `mlx5_cmd_query_cong_params`, `mlx5_cmd_destroy_tir`, `mlx5_cmd_destroy_tis`, `mlx5_cmd_destroy_rqt`, `mlx5_cmd_alloc_transport_domain`, `mlx5_cmd_dealloc_transport_domain`, `mlx5_cmd_dealloc_pd`, `mlx5_cmd_attach_mcg`, `mlx5_cmd_detach_mcg`, `mlx5_cmd_xrcd_alloc`, `mlx5_cmd_xrcd_dealloc`, `mlx5_cmd_mad_ifc`, `mlx5_cmd_uar_alloc`, `mlx5_cmd_uar_dealloc`, and `mlx5_cmd_query_vuid`.

## Control flow
Each wrapper builds a firmware input mailbox with `MLX5_SET`, sets opcode and identifiers, calls the appropriate `mlx5_cmd_exec*` helper, and extracts output fields with `MLX5_GET` when needed. Allocation helpers return ids only after successful commands. Destroy/dealloc helpers mostly ignore returned firmware status when declared `void`. `mlx5_cmd_mad_ifc` allocates dynamic input/output buffers, handles SMI device port-plane translation, copies the MAD request into the command buffer, executes, and copies the response MAD back out. `mlx5r_cmd_query_special_mkeys` first checks capabilities and then fills cached null, dump-fill, and terminate-scatter-list mkeys.

## State and persistence behavior
State changes happen in firmware and in the driver's in-memory caches. Allocated TDNs, XRCDs, UARs, MCG attachments, and special mkeys persist only while the device context and firmware resources exist. There is no file persistence.

## Dependencies and integration points
The file depends on `mlx5_ib.h`, `cmd.h`, mlx5 command layout macros, core command execution, SMI native-port translation, multicast GID data, and RDMA MAD/XRC/UAR consumers in other mlx5 IB files.

## Risks
Risks include opcode/field mismatches, endian mistakes for cached mkeys, silent failures in `void` destroy helpers, incorrect SMI port translation, memory allocation failure paths in MAD IFC, and callers forgetting to pair allocations and deallocations. VUID query uses a stack buffer sized for a large variable field and must remain aligned with firmware layout definitions.

## Test signals
Firmware command selftests or fault injection should verify allocation/deallocation pairing, MCG attach/detach, MAD IFC on normal and SMI devices, special mkey capability combinations, UAR allocation failure cleanup, XRC domain lifecycle, and VUID query output sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.h

## Purpose
This header declares the mlx5 IB command-wrapper interface implemented in `cmd.c` and consumed by mlx5 RDMA subsystems.

## Important APIs, types, and functions
The declarations cover special mkey query, congestion parameter query, PD/TIR/TIS/RQT/transport-domain lifecycle, multicast group attach/detach, XRCD lifecycle, MAD IFC execution, UAR lifecycle, and VUID query. It includes `mlx5_ib.h` and `<linux/mlx5/driver.h>` so callers share the core device and mlx5 IB device types.

## Control flow
There is no executable control flow. Build-time inclusion makes command wrappers available to files such as congestion, QP, multicast, resource allocation, MAD, and user-context handling code.

## State and persistence behavior
The header owns no state. It defines function contracts for operations that mutate firmware resources or driver caches elsewhere.

## Dependencies and integration points
This is an internal interface boundary between mlx5 IB logic and mlx5 core command mailboxes. Changes here require matching implementation changes in `cmd.c` and caller updates across the mlx5 IB driver.

## Risks
Risks are ABI-internal: prototype drift, uid parameter misuse, ownership ambiguity for returned ids, and adding wrappers without clear allocation/deallocation pairing. Because it is included by multiple driver files, incorrect declarations can cause build failures or subtle call-site mismatches.

## Test signals
Compile coverage with all mlx5 optional features enabled is the primary signal. Runtime coverage comes from the command users: MAD, UAR, MCG, congestion, XRCD, and transport-domain lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cong.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cong.c

## Purpose
This file creates a debugfs interface for querying and modifying mlx5 RoCE congestion-control parameters. It exposes RP, NP, and general RRoCE ECN fields as per-port files when firmware permits congestion query and modification.

## Important APIs, types, and functions
Public lifecycle functions are `mlx5_ib_init_cong_debugfs` and `mlx5_ib_cleanup_cong_debugfs`. Internal mapping helpers include `mlx5_ib_param_to_node`, `mlx5_get_cc_param_val`, and `mlx5_ib_set_cc_param_mask_val`. Firmware command helpers are `mlx5_ib_get_cc_params` and `mlx5_ib_set_cc_params`, backed by `mlx5_cmd_query_cong_params` and `MLX5_CMD_OP_MODIFY_CONG_PARAMS`. Debugfs operations are `set_param`, `get_param`, and `dbg_cc_fops`.

## Control flow
Initialization checks the global mlx5 debugfs root, obtains the native port mdev, validates `cc_query_allowed` and `cc_modify_allowed`, allocates `mlx5_ib_dbg_cc_params`, creates a `cc_params` directory under the mlx5 device debugfs root, and creates one 0600 file per supported parameter. General RTT response DSCP fields are skipped unless RoCE and general RoCE congestion-control capabilities are present.

Reads allocate a query output mailbox, select the RP/NP/general congestion node from the parameter offset, execute a query command, extract the field, and copy a decimal value to userspace. Writes copy a short numeric string from userspace, parse a `u32`, allocate a modify input mailbox, set opcode and protocol, set the target field and field-select mask, and execute the firmware modify command.

Cleanup removes the debugfs subtree recursively, frees the parameter container, and nulls the pointer.

## State and persistence behavior
The debugfs files are runtime-only. Values read and written are firmware congestion parameters for the native port mdev. The driver stores only debugfs dentries and small parameter descriptors; no disk persistence is provided.

## Dependencies and integration points
This code depends on debugfs, mlx5 command mailbox layouts, native-port lookup for multiport/LAG setups, firmware congestion capabilities, and `cmd.c` query support.

## Risks
Risks include exposing powerful tuning knobs through debugfs, wrong field-select masks for NP/general fields, port number off-by-one handling, stale native-port devices during teardown, partial debugfs creation, and accepting syntactically valid but semantically out-of-range values without driver-side validation.

## Test signals
Test capability-gated creation, read/write of every RP/NP/general parameter on supported firmware, absence of RTT DSCP files when capabilities are missing, cleanup after partial allocation failure, invalid user input lengths and nonnumeric writes, multiport native-port routing, and verification that firmware values change as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/cong.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.c

## Purpose
This file implements mlx5 RDMA statistics and counters support. It allocates device/port Q counters, builds RDMA hw stats descriptors, reads queue, congestion, PPCNT, vport, and optional operational flow counters, implements RDMA per-QP counter binding, and supports user flow counters attached to flow steering.

## Important APIs, types, and functions
Public functions are `mlx5_ib_counters_init`, `mlx5_ib_counters_cleanup`, `mlx5_ib_counters_clear_description`, `mlx5_ib_flow_counters_set_data`, `mlx5_ib_get_counters_id`, and `mlx5r_is_opfc_shared_and_in_use`. Important local types include `struct mlx5_ib_counter` descriptor templates and `struct mlx5_rdma_counter`, which extends `rdma_counter` with operational flow counters and a QPN xarray. Major helpers include `mlx5_ib_read_counters`, `mlx5_ib_query_q_counters`, `mlx5_ib_query_q_counters_vport`, `mlx5_ib_query_ext_ppcnt_counters`, `do_get_hw_stats`, `do_get_op_stat`, `do_per_qp_get_op_stat`, `mlx5_ib_counter_bind_qp`, `mlx5_ib_counter_unbind_qp`, `mlx5_ib_modify_stat`, `mlx5_ib_alloc_counters`, and `mlx5_ib_dealloc_counters`.

## Control flow
Initialization always registers generic ib counters ops, then, if firmware supports QP counters, registers hw stats ops for normal or switchdev mode and allocates per-port counter sets. Allocation computes descriptor counts based on capabilities, allocates descriptor/offset arrays, fills names and offsets, then allocates firmware Q counter sets. Switchdev allocates a real device counter set and an optional vport helper set.

Stats reads select the correct counter set through `get_counters`. Q counters are read with `QUERY_Q_COUNTER`; vport representors use `other_vport` and aggregation; extended PPCNT uses `mlx5_core_access_reg` on `MLX5_REG_PPCNT`; congestion counters use `mlx5_lag_query_cong_counters` from the native port mdev. Optional operational counters are flow counters created on demand by `modify_hw_stat`; packet and byte pairs may share the same flow counter object. Per-QP RDMA counters allocate a Q counter lazily during bind, set the QP counter id, optionally bind operational flow counters to the QP through flow steering, update stats by querying both Q counters and per-QP flow counters, and undo bindings on unbind/dealloc.

User flow counters are created through `mlx5_ib_flow_counters_set_data`: optional userspace descriptions map packet/byte hardware slots to user buffer indices, a flow counter object is created if needed, and read operations query packet/byte values and place them by description index.

## State and persistence behavior
Driver state includes per-port `mlx5_ib_counters` arrays of stat descriptors, offsets, firmware Q counter ids, and operational flow-counter handles/rules. Per-QP state includes an RDMA counter id, stats buffer, optional flow counters, and a QPN xarray. User flow counters store descriptions and a hardware flow counter handle. All state is runtime firmware/kernel state and is destroyed during cleanup, dealloc, or flow counter destruction.

## Dependencies and integration points
This file integrates with RDMA core `ib_device_ops`, `rdma_hw_stats`, `rdma_counter`, mlx5 firmware Q counters, PPCNT registers, LAG congestion counter queries, eswitch representors/vports, flow steering operational counters, QP counter assignment, uverbs flow counter ABI data, and capability macros.

## Risks
Risk areas include descriptor count/offset mismatches, switchdev port-index selection, optional stat enable/disable sharing semantics, QP bind rollback when flow-counter binding fails, per-QP xarray cleanup, flow counter description lifetime under `usecnt`, counter id leaks on partial allocation, and inconsistent handling of byte versus packet counters. Capability-conditioned arrays must remain aligned with descriptor counts or stats indices will be wrong.

## Test signals
Cover normal and switchdev stats allocation, stats reads with each capability combination, vport representor aggregation, congestion and PPCNT counters, optional stat enable/disable including shared packet/byte counters, per-QP counter bind/unbind/update/dealloc, user flow counters with valid and invalid descriptions, failure injection for Q counter and flow counter allocation, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.h

## Purpose
This header declares the mlx5 IB counters subsystem interface used by the rest of the mlx5 RDMA driver.

## Important APIs, types, and functions
Declared functions include `mlx5_ib_counters_init`, `mlx5_ib_counters_cleanup`, `mlx5_ib_counters_clear_description`, `mlx5_ib_flow_counters_set_data`, `mlx5_ib_get_counters_id`, and `mlx5r_is_opfc_shared_and_in_use`. The header includes `mlx5_ib.h` for device, counter, and flow-counter types.

## Control flow
There is no executable flow. Callers use this interface during device initialization/cleanup, QP setup requiring a counter id, flow creation with user counters, and optional operational flow counter sharing.

## State and persistence behavior
The header owns no state. It defines access to runtime state managed by `counters.c`: firmware Q counter ids, descriptor arrays, flow counters, per-QP counter bindings, and user flow-counter descriptions.

## Dependencies and integration points
It is the internal boundary between general mlx5 IB code and the counters implementation. It ties flow creation, QP configuration, and device lifecycle to the stats subsystem.

## Risks
The main risks are prototype drift with `counters.c`, exposing helper semantics that depend on shared operational flow-counter lifetime, and callers assuming a valid counter id before `mlx5_ib_counters_init` has allocated one.

## Test signals
Compile all mlx5 IB configurations and exercise device init/cleanup, QP counter id retrieval, flow counter setup, and operational counter sharing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/counters.h -->
