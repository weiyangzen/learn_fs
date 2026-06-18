# subset-b-003940 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.c

## Purpose
`ws.c` manages the Intel irdma work-scheduler tree used to map RDMA VSI/user-priority traffic onto hardware scheduling nodes and LAN queue-set handles. It builds a three-level scheduler hierarchy: a device root, per-VSI parent nodes, and traffic-class leaf nodes shared by user priorities with the same traffic class.

## Important APIs, Types, And Functions
The public entry points are `irdma_ws_add()`, `irdma_ws_remove()`, and `irdma_ws_reset()`. Internally, `irdma_alloc_node()` initializes `struct irdma_ws_node` for root/VSI parents or TC leaves, allocating hardware node IDs for non-root nodes. `irdma_ws_cqp_cmd()` converts a software node into `struct irdma_ws_node_info` and posts `IRDMA_OP_WS_ADD_NODE`, `MODIFY_NODE`, or `DELETE_NODE` through `irdma_cqp_ws_node_cmd()`. `ws_find_node()` searches child lists by VSI or traffic class. `irdma_tc_in_use()` guards leaf removal by checking QP lists for the target and same-TC user priorities. `irdma_remove_leaf()` tears down TC, VSI, and root nodes when they become empty.

## Control Flow
`irdma_ws_add()` takes `vsi->dev->ws_mutex`, refuses changes while `tc_change_pending` is set, creates the root if missing, creates or reuses the VSI node, creates or reuses the TC leaf, registers the qset with LAN, enables the leaf with a MODIFY command, then marks every matching user priority valid and copies the RDMA/LAN queue handles. Error paths unwind leaf, VSI, and root nodes in reverse order. `irdma_ws_remove()` serializes on the same mutex, skips deletion if any same-TC QP list is still populated, and otherwise calls `irdma_remove_leaf()`. `irdma_ws_reset()` loops over all user priorities and removes each leaf under the scheduler mutex.

## State And Persistence
The in-memory tree is rooted at `vsi->dev->ws_tree_root` and each node is linked through `siblings` and `child_list_head`. Per-user-priority state in `vsi->qos[]` records `valid`, `traffic_class`, `rel_bw`, `qs_handle`, LAN qset handle, and L2 scheduler node ID. Hardware state is programmed through CQP commands and LAN callbacks; it is not persisted outside driver memory. Reset/removal clears `valid` for every priority sharing the removed traffic class.

## Dependencies And Integration Points
This file depends on irdma CQP scheduler commands, hardware node-id allocation, `struct irdma_sc_vsi`, per-priority QoS mutexes and QP lists, LAN qset registration callbacks, and RDMA core debug logging via `ibdev_dbg()`. It also relies on list APIs and the device-wide scheduler mutex to keep tree mutation serialized.

## Risks
`irdma_tc_in_use()` locks only `vsi->qos[user_pri].qos_mutex` while inspecting all same-TC `qplist` heads, so correctness depends on a broader convention that same-TC list updates are safe under that lock or the outer `ws_mutex`. The add path registers a LAN qset before enabling the leaf; failures after registration must keep LAN and RDMA scheduler state aligned. `irdma_ws_cqp_cmd()` maps any CQP failure to `-ENOMEM`, losing error specificity. Root node index zero is intentionally never freed, so node-index handling must preserve that root special case.

## Test Signals
Exercise first-add root creation, multiple VSIs, multiple user priorities sharing a traffic class, qset registration failure, CQP add/modify/delete failures, removal while QP lists are populated, complete tree teardown, `tc_change_pending` rejection, and repeated reset calls on partially populated trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.h

## Purpose
`ws.h` defines the software representation and public interface for the irdma work-scheduler tree implemented by `ws.c`.

## Important APIs, Types, And Functions
`enum irdma_ws_node_type` distinguishes parent and leaf nodes. `enum irdma_ws_match_type` selects child lookup by VSI or traffic class. `struct irdma_ws_node` stores list linkage, parent pointer, LAN and RDMA queue-set identifiers, hardware node index, VSI index, traffic class, user priority, relative bandwidth, abstraction-layer metadata, priority type, and leaf/enable bits. The exported functions are `irdma_ws_add()`, `irdma_ws_remove()`, and `irdma_ws_reset()`.

## Control Flow
The header has no runtime control flow. It fixes the data contract used by callers that request scheduler nodes and by `ws.c` helpers that allocate, link, program, and free those nodes.

## State And Persistence
All fields in `struct irdma_ws_node` are runtime-only driver state. Handles such as `lan_qs_handle`, `l2_sched_node_id`, and `qs_handle` mirror resources created in LAN or RDMA hardware, but the header does not define persistence.

## Dependencies And Integration Points
The header includes `osdep.h` for kernel/list types, forward-declares `struct irdma_sc_vsi`, and is included by irdma code that needs scheduler add/remove/reset APIs.

## Risks
Bitfields `type_leaf` and `enable` are compact but require all node initialization paths to set sane defaults. Because the struct is shared between RDMA and LAN qset registration callbacks, changes to field names or semantics can break cross-module scheduler integration.

## Test Signals
Build coverage is the primary signal. Runtime tests should indirectly validate the struct by creating parent and leaf nodes, checking propagated handles, and removing all scheduler levels without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ws.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Kconfig

## Purpose
This Kconfig entry exposes `CONFIG_MANA_INFINIBAND`, the RDMA/InfiniBand verbs driver for Microsoft Azure Network Adapter hardware.

## Important APIs, Types, And Functions
`MANA_INFINIBAND` is a tristate option labeled "Microsoft Azure Network Adapter support". It depends on `NETDEVICES`, `ETHERNET`, `PCI`, and `MICROSOFT_MANA`, ensuring the Ethernet/GDMA MANA core is available before the RDMA auxiliary driver can be built.

## Control Flow
There is no runtime flow. The option controls whether the `mana_ib` module is built into the kernel, built as a module, or omitted.

## State And Persistence
The only state is build configuration. No runtime state is created by this file.

## Dependencies And Integration Points
The entry integrates the MANA RDMA driver into the kernel RDMA hardware-driver menu and ties it to the Microsoft MANA network driver stack.

## Risks
Missing dependency coverage would surface as unresolved symbols against MANA core, PCI, Ethernet, or RDMA infrastructure. The help text describes user-mode RDMA workloads such as DPDK and MPI, so packaging should make the dependency on the base MANA net driver clear.

## Test Signals
Validate `allyesconfig`, module build, disabled `MICROSOFT_MANA`, and `MANA_INFINIBAND=m` combinations; confirm `drivers/infiniband/hw/mana/Makefile` produces `mana_ib.o` only when this config is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Makefile

## Purpose
The Makefile defines the object composition for the MANA InfiniBand/RDMA driver.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MANA_INFINIBAND) += mana_ib.o` links the driver when enabled. `mana_ib-y` aggregates `device.o`, `main.o`, `wq.o`, `qp.o`, `cq.o`, `mr.o`, `ah.o`, `wr.o`, and `counters.o`.

## Control Flow
There is no runtime control flow. Build flow collects the listed translation units into one `mana_ib` module or built-in object.

## State And Persistence
No runtime state exists. Build state is determined by `CONFIG_MANA_INFINIBAND`.

## Dependencies And Integration Points
The object list matches the `ib_device_ops` functions registered in `device.c` and prototypes in `mana_ib.h`; omitting any listed object would break verbs, memory, address-handle, work-request, or counter support.

## Risks
Adding new exported operations in `mana_ib.h` without updating `mana_ib-y` can create link failures. Removing objects may compile only if matching device ops are also removed.

## Test Signals
Kernel build with `CONFIG_MANA_INFINIBAND=y` and `m`; inspect `modinfo mana_ib` and link output for all expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/ah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/ah.c

## Purpose
`ah.c` implements MANA RDMA address-handle creation and destruction for RoCE-style UD/GSI sends.

## Important APIs, Types, And Functions
`mana_ib_create_ah()` validates that the requested AH is RoCE and has a GRH, rejects user-data creation, allocates a `struct mana_ib_av` from the device DMA pool, and fills destination/source IP, destination MAC, UDP source port, hop limit, DSCP, and IPv4/IPv6 format bits. `mana_ib_destroy_ah()` frees the AV buffer back to the pool. `copy_in_reverse()` from `mana_ib.h` is used because MANA firmware expects reversed byte order for addresses.

## Control Flow
Create validates the AH type and GRH flag, allocates DMA-coherent AV storage, reads the GRH, derives the network type from `sgid_attr`, copies the destination MAC, derives UDP source port from flow label, and fills IPv6 or IPv4-mapped address fields. Destroy unconditionally returns the pool allocation.

## State And Persistence
Each `struct mana_ib_ah` owns one DMA-pool allocation and DMA address for the AV. State is tied to the RDMA AH lifetime and is not persisted. The AV contents are consumed later by send posting, where the AV DMA address is passed as the first SGE.

## Dependencies And Integration Points
The file integrates with RDMA core AH callbacks, GRH/GID helpers, the MANA AV DMA pool created in `device.c`, and `wr.c` send posting. It expects `grh->sgid_attr` to be valid for network-type and source-GID access.

## Risks
Only kernel-created AHs are supported; unexpected `udata` returns `-EINVAL`. Missing or invalid `sgid_attr` would be unsafe because create dereferences it after validation of GRH only. Endianness is hardware-specific, so address reversal must match firmware ABI. Destroy assumes `ah->av` is initialized.

## Test Signals
Test IPv4 and IPv6 RoCE AH creation, GRH-missing rejection, non-RoCE rejection, udata rejection, DMA-pool allocation failure, address/DSCP/port encoding, and send path use followed by AH destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/counters.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/counters.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/counters.h

## Purpose
`counters.h` defines the MANA RDMA counter enum indexes and prototypes for stat allocation and reading.

## Important APIs, Types, And Functions
`enum mana_ib_port_counters` enumerates requester, responder, NAK, congestion, byte, packet, and request counters. `enum mana_ib_device_counters` enumerates device-wide CNP/ECN/congestion counters. The prototypes expose `mana_ib_alloc_hw_port_stats()`, `mana_ib_alloc_hw_device_stats()`, and `mana_ib_get_hw_stats()`.

## Control Flow
The header has no runtime flow. It provides shared indexes consumed by `counters.c` descriptor arrays and stat population.

## State And Persistence
No state is stored here. Enum values are ABI-significant within the driver because they index `rdma_hw_stats->value`.

## Dependencies And Integration Points
It includes `mana_ib.h`, creating a circular-looking but guarded include relationship because `mana_ib.h` also includes `counters.h`. Header guards avoid duplicate definitions, and `device.c` uses these functions through RDMA ops.

## Risks
Adding, removing, or reordering enum entries requires synchronized changes to descriptors and firmware response mapping. The include relationship should be watched for future type dependencies that could break compilation.

## Test Signals
Build coverage plus runtime stat reads that verify descriptor count equals enum count and user-visible names map to expected firmware values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/cq.c

## Purpose
`cq.c` creates, destroys, arms, services, and polls MANA completion queues, including a kernel shadow-completion path for UD/GSI work requests.

## Important APIs, Types, And Functions
`mana_ib_create_cq()` creates user or kernel CQs, validates CQE limits, creates a queue, optionally creates an RNIC CQ via `mana_ib_gd_create_cq()`, installs a GDMA callback, and returns the CQ ID to userspace. `mana_ib_destroy_cq()` removes the callback, destroys the RNIC CQ, and frees queue resources. `mana_ib_install_cq_cb()` and `mana_ib_remove_cq_cb()` manage `gdma_context->cq_table`. `mana_ib_arm_cq()` rings a kernel CQ arm doorbell. `mana_ib_poll_cq()` polls GDMA completions, calls `mana_handle_cqe()`, and then converts shadow WQEs into `ib_wc` entries.

## Control Flow
Creation branches on `udata`: user CQs pin userspace memory and use the ucontext doorbell; kernel CQs allocate a GDMA queue and use the device doorbell. For RNIC devices, a firmware CQ object and callback entry are installed before optional udata response. Completion callbacks invoke the RDMA CQ handler. Polling holds `cq_lock`, drains up to `num_entries` hardware CQEs, uses queue ID and SQ/RQ bit to find the QP, advances UD shadow queues, then emits completions from send and receive shadow queues.

## State And Persistence
`struct mana_ib_cq` stores queue metadata, a spinlock, lists of send/recv QPs attached to the CQ, CQE count, completion vector, and firmware CQ handle. Callback state is in `gdma_context->cq_table`. Completion state for UD/GSI is stored in per-QP shadow queues, not in the CQ itself. All state is runtime-only.

## Dependencies And Integration Points
The file integrates RDMA core CQ ops, MANA GDMA queue APIs, firmware CQ commands in `main.c`, QP lookup/refcount helpers in `mana_ib.h`, UD shadow queues in `shadow_queue.h`, and QP list management in `qp.c`.

## Risks
`mana_ib_arm_cq()` only supports kernel CQs because user CQs have no `queue.kmem`; callers must not arm unsupported CQs. `mana_ib_remove_cq_cb()` returns early for kernel queues and relies on the MANA core to clean callback table entries, so lifetime coupling is subtle. Shadow queues silently drop hardware completions when `shadow_queue_get_next_to_complete()` returns NULL. Polling assumes `cq->queue.kmem` is valid, which is not true for user CQs in the RNIC path unless userspace polling bypasses this kernel function.

## Test Signals
Test user and kernel CQ creation, RNIC and non-RNIC modes, max CQE validation, callback table collision, udata copy failure unwind, arm on kernel versus user CQs, UD/GSI send and receive completions, shadow-queue empty/full edge cases, CQ destroy with active QPs, and GDMA CQ polling errors or empty polls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/device.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/device.c

## Purpose
`device.c` registers the MANA auxiliary RDMA driver, wires RDMA core operations, probes MANA RDMA/Ethernet auxiliary devices, and tears them down.

## Important APIs, Types, And Functions
`mana_ib_dev_ops` maps RDMA core verbs to MANA implementations for PD, ucontext, AH, CQ, QP, WQ, MR, mmap, query, posting, and notification. `mana_ib_stats_ops`, `mana_ib_device_stats_ops`, and `mana_ib_dev_dm_ops` are optional op sets. `mana_ib_probe()` allocates `struct mana_ib_dev`, queries capabilities, creates RNIC EQs/adapter when applicable, binds net devices to IB ports, creates the AV DMA pool, and registers the IB device. `mana_ib_remove()` drains GSI sends for RNIC, unregisters, destroys pools/adapters/EQs, and deallocates.

## Control Flow
Probe starts with `ib_alloc_device()` and base ops. For RNIC auxiliary devices it sets one initial port, derives node GUID from the primary netdev, queries RNIC caps, installs stats/device-memory ops, creates EQs and adapter, expands to multi-port if firmware supports it, associates each IB port with a primary netdev, configures each MAC in firmware, and registers a netdevice notifier. For Ethernet auxiliary devices it uses all MANA ports and Ethernet capability query. Both paths create an AV pool and call `ib_register_device()`. Unwind labels reverse setup based on RNIC mode.

## State And Persistence
`struct mana_ib_dev` owns `adapter_handle`, EQ pointers, the QP xarray, capability cache, AV DMA pool, netdevice notifier, and netdevice tracker. Port/netdev associations are registered with RDMA core and MAC/IP address state is configured in firmware. No state is persisted across module unload.

## Dependencies And Integration Points
The module imports `NET_MANA`, binds auxiliary IDs `mana.rdma` and `mana.eth`, uses MANA core GDMA and netdev contexts, RDMA core device registration, netdevice notifier handling, and address configuration helpers.

## Risks
Probe unwind after configuring several port MACs calls `mana_ib_gd_destroy_rnic_adapter()` but does not individually remove MACs; firmware adapter teardown must own that cleanup. `mana_ib_netdev_event()` handles only `NETDEV_CHANGEUPPER`; other link/address events rely on RDMA core or other paths. RNIC and Ethernet modes share many ops even though not all operations are meaningful in both modes, so mode checks in individual files are important.

## Test Signals
Test probe/remove for `mana.rdma` and `mana.eth`, capability query failures, EQ/adapter creation failures, multi-port setup, missing netdev on one port, notifier registration failure, AV pool allocation failure, netdev upper changes, device stats feature gating, and removal with outstanding GSI shadow sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/main.c

## Purpose
`main.c` contains core MANA RDMA resource management: protection domains, user contexts and doorbells, queue and DMA-region creation, user mmap, device/port queries, capability queries, EQs, RNIC adapter lifecycle, GID/MAC configuration, and firmware CQ/QP commands.

## Important APIs, Types, And Functions
PD APIs are `mana_ib_alloc_pd()` and `mana_ib_dealloc_pd()`. Ucontext APIs are `mana_ib_alloc_ucontext()`, `mana_ib_dealloc_ucontext()`, and `mana_ib_mmap()`. Queue helpers are `mana_ib_create_kernel_queue()`, `mana_ib_create_queue()`, and `mana_ib_destroy_queue()`. DMA helpers are `mana_ib_create_dma_region()`, `mana_ib_create_zero_offset_dma_region()`, `mana_ib_gd_create_dma_region()`, and `mana_ib_gd_destroy_dma_region()`. Query/config APIs include `mana_ib_query_device()`, `mana_ib_query_port()`, `mana_ib_query_pkey()`, `mana_ib_get_port_immutable()`, `mana_ib_gd_query_adapter_caps()`, `mana_eth_query_adapter_caps()`, `mana_ib_gd_add_gid()`, `mana_ib_gd_del_gid()`, and `mana_ib_gd_config_mac()`. Firmware object APIs cover EQs, adapter, CQ, RC QP, and UD QP create/destroy.

## Control Flow
PD allocation sends `GDMA_CREATE_PD`, allowing GPA MRs for kernel PDs. Ucontext allocation obtains one doorbell page resource and mmap maps that page write-combined. Queue creation either allocates kernel GDMA queues or pins user memory and registers it as a zero-offset DMA region. DMA-region creation chooses the best supported page size, sends an initial create request with as many DMA block addresses as fit, then sends add-pages requests until all pages are registered. Query paths translate firmware caps and netdev state into RDMA attributes. RNIC setup creates one fatal EQ plus per-vector EQs, creates an adapter handle, configures GIDs/MACs through GDMA commands, and passes queue DMA regions to firmware CQ/QP creation commands, which then take ownership of those regions.

## State And Persistence
PDs store firmware handles and vport use counts. Ucontexts store doorbell page indexes. Queues own either user umem or kernel GDMA queue memory plus a DMA-region handle until firmware object creation consumes it. `adapter_caps` caches firmware limits and feature flags. EQs and adapter handles live in `mana_ib_dev`. Firmware owns DMA regions after successful CQ/QP/MR creation, so local handles are set invalid to avoid double free.

## Dependencies And Integration Points
The file is tightly coupled to MANA GDMA command ABI, MANA Ethernet port/vport APIs, RDMA umem/page-size helpers, PCI device attributes, netdev carrier/MTU state, RDMA core port immutable/query callbacks, and QP/CQ/MR setup in other MANA files.

## Risks
DMA-region multi-message creation has several edge cases around request sizing, partial failure, and expected `MORE_ENTRIES` statuses. `mana_ib_uncfg_vport()` assumes `mana_ib_get_netdev()` succeeds. `mana_ib_query_gid()` is a stub that returns success without filling a GID, relying on RDMA core GID table behavior elsewhere. Firmware ownership transitions require every failure path to know whether a DMA region is still locally owned. Doorbell page allocation/deallocation errors are logged but cannot always be recovered.

## Test Signals
Test PD kernel/user flags, vport reference counting, doorbell allocation and mmap offset validation, user and kernel queue creation/destruction, DMA region creation across one and multiple GDMA messages, supported page-size selection, port query under link up/down, RNIC and Ethernet capability translation, EQ creation unwind, adapter create/destroy, GID/MAC add/remove for IPv4/IPv6, and CQ/QP firmware ownership of DMA regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mana_ib.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mana_ib.h

## Purpose
`mana_ib.h` is the central private header for the MANA RDMA driver. It defines driver object wrappers, firmware command structures, queue types, CQE/WQE wire formats, helper functions, constants, and cross-file prototypes.

## Important APIs, Types, And Functions
Key driver objects include `mana_ib_dev`, `mana_ib_pd`, `mana_ib_ucontext`, `mana_ib_queue`, `mana_ib_cq`, `mana_ib_qp`, `mana_ib_wq`, `mana_ib_mr`, `mana_ib_mw`, `mana_ib_dm`, and `mana_ib_ah`. Capability and firmware ABI types include `mana_ib_adapter_caps`, RNIC create/destroy/config requests, CQ/QP create/destroy requests, `mana_rnic_set_qp_state_req`, `mana_rdma_cqe`, and counter responses. Helpers include `mdev_to_gc()`, `mana_get_qp_ref()`, `mana_put_qp_ref()`, `mana_ib_is_rnic()`, `mana_ib_get_netdev()`, and `copy_in_reverse()`.

## Control Flow
The header has no standalone runtime flow, but it defines the contracts followed by every MANA source file. QP lookup uses an xarray keyed by queue ID and `MANA_SENDQ_MASK` for send queues; successful lookup increments a refcount and release completes a `free` completion when the last reference drops.

## State And Persistence
The header describes all runtime state: adapter handle, EQ arrays, QP xarray, AV pool, netdevice notifier, PD vport use count, queue memory/region IDs, firmware handles, shadow queues, and command payloads. None of this is persistent across driver unload; firmware resources are reference-counted through handles and command lifetimes.

## Dependencies And Integration Points
It includes RDMA verbs, MAD, iterator, MANA userspace ABI, uverbs ioctl, DMA pool, MANA net core, `shadow_queue.h`, and `counters.h`. Its prototypes connect build units listed in the Makefile and define the firmware ABI shared by `main.c`, `mr.c`, `qp.c`, `cq.c`, `wr.c`, and `device.c`.

## Risks
Firmware command structures marked as hardware data require stable layout, natural alignment, and endianness expectations; casual refactoring can break the ABI. The header includes `counters.h` while `counters.h` includes this header, so new declarations must avoid circular type requirements. `mana_ib_get_netdev()` returns raw pointers from the MANA context without taking references. `copy_in_reverse()` is used in address commands and AH creation; misuse can silently invert protocol addresses.

## Test Signals
Compile with sparse/struct layout checks where available, exercise QP xarray refcounting under concurrent completions and destroy, verify firmware command sizes against expected ABI, check RNIC-vs-Ethernet mode helpers, and run create/destroy cycles for every object wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mana_ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mr.c

## Purpose
`mr.c` implements MANA memory registration, DMA MRs, memory windows, device memory allocation, and DM-backed MR registration.

## Important APIs, Types, And Functions
`mana_ib_verbs_to_gdma_access_flags()` translates RDMA access flags to GDMA access bits. `mana_ib_reg_user_mr()` pins userspace memory, creates a DMA region, and creates a GVA or zero-based VA MR. `mana_ib_reg_user_mr_dmabuf()` pins a dmabuf umem and creates a GVA MR. `mana_ib_get_dma_mr()` creates a GPA DMA MR. `mana_ib_alloc_mw()` and `mana_ib_dealloc_mw()` create/destroy type 1 or type 2 memory windows. `mana_ib_alloc_dm()`, `mana_ib_dealloc_dm()`, and `mana_ib_reg_dm_mr()` manage device memory and DM MRs. `mana_ib_dereg_mr()` destroys firmware MR state and releases local memory.

## Control Flow
Registration validates access flags and rejects `dmah`, allocates a driver MR, obtains an umem, creates a DMA region using the IOVA or zero-offset helper, fills `gdma_create_mr_params`, and sends `GDMA_CREATE_MR`. On success firmware owns the DMA region lifecycle as part of the MR. Error paths destroy DMA regions, release umems, and free the MR. Deregistration sends `GDMA_DESTROY_MR`, releases the umem if present, then frees the wrapper.

## State And Persistence
`mana_ib_mr` stores the firmware MR handle, lkey/rkey in the embedded `ib_mr`, and optional `umem`. `mana_ib_mw` stores a memory-window handle and rkey. `mana_ib_dm` stores a device-memory handle. All state is runtime-only and backed by firmware handles.

## Dependencies And Integration Points
The file depends on RDMA umem and dmabuf APIs, GDMA MR/DM commands, DMA-region helpers in `main.c`, PD handles, and access flags exposed through RDMA core.

## Risks
`mana_ib_reg_user_mr_dmabuf()` returns `-EOPNOTSUPP` for invalid flags while normal MR registration returns `-EINVAL`, which may matter to userspace. DM MR allocation does not store a `mr_handle` differently from normal MRs but shares deregistration semantics. Firmware ownership of DMA regions after MR creation means local cleanup must not destroy successful regions. The valid flag mask includes remote atomic even though device atomic capability reports none in query_device.

## Test Signals
Test normal, zero-based, dmabuf, GPA DMA, MW type 1/2, DM allocation, DM MR registration, invalid flags, dmah rejection, umem pin failure, DMA-region failure, firmware create/destroy failure, and lkey/rkey propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/qp.c

## Purpose
`qp.c` implements MANA QP creation, modification, destruction, RSS/raw Ethernet queue setup, RNIC RC QPs, and kernel UD/GSI QPs with shadow queues.

## Important APIs, Types, And Functions
`mana_ib_create_qp()` dispatches by QP type to raw packet, RSS, RC, UD, or GSI creation. `mana_ib_create_qp_raw()` configures a vport, creates a userspace SQ, creates a MANA Ethernet WQ object, and returns SQ/CQ IDs. `mana_ib_create_qp_rss()` creates receive WQ objects from an indirection table and configures vport RX steering. `mana_ib_create_rc_qp()` creates user queues and a firmware RNIC RC QP. `mana_ib_create_ud_qp()` creates kernel SQ/RQ queues, shadow queues, and a firmware UD/GSI QP. `mana_ib_modify_qp()` sends RNIC state transitions and AH/path data. `mana_ib_destroy_qp()` dispatches to matching teardown paths. QP table helpers store and remove QPs in an xarray keyed by RC QPN or UD queue IDs.

## Control Flow
Raw/RSS packet QPs are userspace-oriented and use MANA Ethernet vport/WQ APIs. RC QPs read user queue buffers, skip the FMR queue for user-level RC, pass DMA regions to firmware, set QPN from responder RQ ID, return queue IDs to userspace, and insert into the QP table. UD/GSI QPs are kernel-only, allocate hardware queues and shadow queues, create the firmware QP, set kernel queue IDs, store QP references, and add the QP to send/recv CQ lists. Modify QP builds `MANA_IB_SET_QP_STATE`, copies path attributes when `IB_QP_AV` is set, and submits the command.

## State And Persistence
`struct mana_ib_qp` holds firmware handle, raw/RC/UD queues, port, CQ list nodes, shadow queues, refcount, and completion. Packet QPs also configure PD vport use state. RSS state is primarily in WQ objects and vport steering. All state is runtime-only and is removed through destroy paths.

## Dependencies And Integration Points
The file integrates RDMA QP ops, MANA Ethernet WQ/vport steering APIs, GDMA queue creation, firmware RNIC QP commands in `main.c`, CQ callback installation, CQ list polling in `cq.c`, shadow queues, netdev MTU/MAC state, and GID/AV helpers.

## Risks
Error unwinds are complex and must distinguish locally owned DMA regions from firmware-owned regions. `mana_ib_create_qp_rss()` failure after several WQs must remove CQ callbacks and WQ objects consistently. Destroy RSS disables vport RX best-effort because no kernel fence can wait for userspace-polled CQs; failures may leave traffic routing stale. `mana_ib_create_ud_qp()` has a cleanup bug risk: if SQ shadow queue creation fails, the label destroys both shadow queues even though SQ may not have been created. Modify QP assumes GRH `sgid_attr` is present when `IB_QP_AV` is supplied.

## Test Signals
Test raw packet QP creation/destroy, RSS indirection sizes and hash validation, vport config refcounting, RC user queue creation and udata responses, UD/GSI kernel post/poll cycles, QP xarray lookup under completions, modify QP state transitions with IPv4/IPv6 AVs, every error label, and destroy while completions are in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/shadow_queue.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/shadow_queue.h

## Purpose
`shadow_queue.h` provides a small software ring used to remember posted UD/GSI work requests until hardware completions can be converted into RDMA work completions.

## Important APIs, Types, And Functions
`struct shadow_wqe_header` stores opcode, error code, posted WQE size, and `wr_id`. `ud_rq_shadow_wqe` adds receive byte length and source QPN; `ud_sq_shadow_wqe` is send-only. `struct shadow_queue` tracks unmasked producer, consumer, and next-to-complete indexes plus length, stride, and buffer. Inline helpers create/destroy the buffer, check full/empty, get producer/consumer/next-to-complete entries, and advance indexes.

## Control Flow
Post-send/recv writes the producer entry and advances `prod_idx`. CQE handling updates the next-to-complete entry and advances `next_to_complete_idx`. CQ polling consumes completed entries from `cons_idx` up to `next_to_complete_idx`.

## State And Persistence
The queue is memory-only state embedded in `mana_ib_qp`. Indexes are intentionally unmasked and wrap only by integer overflow; element access masks via modulo `length`. No state persists beyond QP lifetime.

## Dependencies And Integration Points
It uses `kvmalloc_array()`/`kvfree()` and is consumed by `wr.c`, `cq.c`, and `qp.c` for kernel UD/GSI completions.

## Risks
`create_shadow_queue()` initializes buffer, length, and stride but does not explicitly zero indexes, relying on the containing QP being zero-initialized by RDMA core. A zero `length` would make modulo invalid; callers must pass nonzero WR counts. There is no locking inside helpers; CQ locks and post serialization must provide safety.

## Test Signals
Test full/empty boundaries, index wrap behavior, create failure, zero length rejection by callers, producer/complete/consumer ordering, and concurrent post versus poll synchronization through the CQ/QP paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/shadow_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wq.c

## Purpose
`wq.c` implements receive work queue and RWQ indirection-table operations used mainly for MANA raw-packet RSS QPs.

## Important APIs, Types, And Functions
`mana_ib_create_wq()` reads userspace WQ buffer attributes, allocates `struct mana_ib_wq`, creates a user queue DMA region, stores max WR and buffer size, and initializes `rx_object` invalid. `mana_ib_modify_wq()` returns `-EOPNOTSUPP`. `mana_ib_destroy_wq()` destroys the queue and frees the wrapper. `mana_ib_create_rwq_ind_table()` and `mana_ib_destroy_rwq_ind_table()` are no-op wrappers because the driver stores no extra indirection-table state.

## Control Flow
Creation validates/copies udata, allocates the WQ, creates a queue over `ucmd.wq_buf_addr`/`wq_buf_size`, and returns the embedded `ib_wq`. Destroy reverses queue creation. RSS QP creation later consumes these WQs to create MANA RQ objects and configure vport steering.

## State And Persistence
Each WQ stores a `mana_ib_queue`, max WQE count, userspace buffer size, and firmware RX object handle once RSS setup creates it. State is runtime-only.

## Dependencies And Integration Points
The file depends on MANA userspace ABI structures, RDMA WQ/RWQ APIs, queue helpers in `main.c`, and RSS setup/destruction in `qp.c`.

## Risks
No kernel WQ creation path exists; `udata` is assumed valid. Modify WQ is unsupported, so userspace must create new WQs for changes. RWQ indirection-table no-ops rely on RDMA core owning the table contents and `qp.c` consuming them directly.

## Test Signals
Test udata validation, queue creation failure, WQ destroy before and after RSS object creation, modify rejection, indirection table create/destroy, and invalid userspace buffer sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wr.c

## Purpose
`wr.c` posts kernel UD/GSI send and receive work requests to MANA queues and records enough shadow state for later CQ polling.

## Important APIs, Types, And Functions
`mana_ib_post_recv()` iterates receive WRs and calls `mana_ib_post_recv_ud()` for UD/GSI. `mana_ib_post_send()` iterates send WRs and calls `mana_ib_post_send_ud()`. The helpers build GDMA SGE arrays, post work with `mana_gd_post_work_request()`, fill `ud_rq_shadow_wqe` or `ud_sq_shadow_wqe`, advance shadow producers, and ring the queue doorbell. Sends prepend the AH AV DMA buffer as an SGE and fill `struct rdma_send_oob`.

## Control Flow
Receive posting checks shadow queue capacity and max two SGEs, converts SGEs to GDMA format, posts the WQE, records `IB_WC_RECV`, `wr_id`, and posted WQE size, then rings. Send posting validates port/netdev, opcode `IB_WR_SEND`, shadow capacity, max two payload SGEs, prepends the address vector, sets OOB fields including fence/signaled/solicited flags, PSN, remote QPN, qkey, and MTU-derived client data unit, posts, increments SQ PSN, records `IB_WC_SEND`, and rings.

## State And Persistence
Posting advances GDMA queue producer state in hardware/core code and software shadow queue `prod_idx`. UD SQ PSN is stored in `qp->ud_qp.sq_psn`. Posted WQE size is used later to advance GDMA queue tails on completion. No state persists beyond QP lifetime.

## Dependencies And Integration Points
The file depends on GDMA work-request APIs, MANA AH objects from `ah.c`, QP queues and shadow queues from `mana_ib.h`, netdev MTU for send sizing, and CQ completion handling in `cq.c`.

## Risks
Only UD/GSI and `IB_WR_SEND` are supported; unsupported QP types or opcodes fail. The maximum SGE count is hard-coded to two payload SGEs. Send requires a valid AH and netdev. Shadow state is written only after hardware post succeeds, so a completion for an unshadowed WQE would be dropped by CQ handling. `err` in `mana_ib_post_send()` is not initialized before the loop but the loop always executes for non-NULL WR; callers should not pass NULL lists expecting a defined local value path beyond return.

## Test Signals
Test multi-WR lists with bad_wr handling, SGE count limits, shadow queue full, unsupported QP/opcode, IPv4/IPv6 AH send, GSI qkey override, PSN increment, doorbell ringing, post failure without shadow advance, and CQ poll conversion after send/recv completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/wr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Kconfig

## Purpose
This Kconfig entry exposes `CONFIG_MLX4_INFINIBAND`, the InfiniBand/RDMA driver for Mellanox ConnectX mlx4 adapters.

## Important APIs, Types, And Functions
`MLX4_INFINIBAND` is a tristate option labeled "Mellanox ConnectX HCA support". It depends on networking, Ethernet, PCI, and INET, and selects `NET_VENDOR_MELLANOX` plus `MLX4_CORE`.

## Control Flow
There is no runtime flow. The option controls whether `mlx4_ib` is built and ensures the core mlx4 PCI driver is selected.

## State And Persistence
Only build configuration state is represented.

## Dependencies And Integration Points
It integrates the mlx4 RDMA hardware driver with Kbuild and the mlx4 core driver. The help text identifies IPoIB and SRP as consumers.

## Risks
Dependency or select mistakes would break builds or allow mlx4_ib without mlx4 core. INET dependency is needed because the driver includes RoCE/IP address handling paths.

## Test Signals
Build with option disabled, built-in, and module; verify `MLX4_CORE` is selected and the Makefile links `mlx4_ib.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Makefile

## Purpose
The Makefile defines the object composition for the mlx4 InfiniBand/RDMA driver.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MLX4_INFINIBAND) += mlx4_ib.o` builds the driver when configured. `mlx4_ib-y` includes address handles, CQs, doorbells, MAD, main, MR, QP, SRQ, multicast groups, CM paravirtualization, alias GUID, and sysfs objects.

## Control Flow
There is no runtime flow. Kbuild links the listed translation units into one mlx4_ib driver.

## State And Persistence
No runtime state exists in this file.

## Dependencies And Integration Points
The object list maps to the RDMA ops and mlx4-specific services declared in `mlx4_ib.h`; subset files here depend on additional objects such as `main.o`, `qp.o`, `srq.o`, and `mad.o`.

## Risks
Object-list drift causes unresolved symbols or missing runtime services, especially for cross-file helpers like AH creation, CQ polling, CM multiplexing, and alias GUID service.

## Test Signals
Run module and built-in builds; verify all listed objects compile and link under `CONFIG_MLX4_INFINIBAND`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/ah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/ah.c

## Purpose
`ah.c` creates and queries mlx4 address vectors for InfiniBand and RoCE address handles, including SR-IOV slave AH creation.

## Important APIs, Types, And Functions
`mlx4_ib_create_ah()` dispatches to `create_ib_ah()` or `create_iboe_ah()` based on AH type. `create_ib_ah()` fills InfiniBand AV fields such as port/PD, SL, path bits, GRH, DLID, and static rate. `create_iboe_ah()` fills Ethernet/RoCE AV fields, resolves source MAC/VLAN from `sgid_attr`, maps GID index to real hardware index, handles multicast DLID requirements, and encodes traffic class/flow label. `mlx4_ib_create_ah_slave()` creates an AH using an explicit slave SGID index/source MAC/VLAN. `mlx4_ib_query_ah()` reconstructs an `rdma_ah_attr`.

## Control Flow
Create rejects RoCE AHs without GRH, then fills the hardware AV. RoCE creation reads L2 fields from the GID attribute unless called through the slave path, where the caller supplies the slave GID index, source MAC, and VLAN. Static rate is reduced until supported by device caps. Query decodes port, SL, DLID, static rate, path bits, and GRH from the stored AV.

## State And Persistence
The AV is stored inside `struct mlx4_ib_ah` for the lifetime of the RDMA AH. It reflects PD number, port, GID index, L2/L3 addressing, VLAN, and rate. There is no persistence beyond AH lifetime.

## Dependencies And Integration Points
The file uses RDMA AH/GID helpers, mlx4 device caps, PD numbers, `mlx4_ib_gid_index_to_real_index()`, `rdma_read_gid_l2_fields()`, and SR-IOV slave AH creation paths.

## Risks
RoCE source L2 resolution may sleep, and the comment notes atomic-context concerns. Querying RoCE AHs returns DLID zero and reconstructs only fields represented in the AV. The slave path clears a force-loopback bit and overwrites VLAN/source MAC; mistakes affect VF packet routing. Static-rate fallback depends on `stat_rate_support` bit numbering.

## Test Signals
Test IB and RoCE AH creation, RoCE missing-GRH rejection, VLAN priority encoding, multicast RoCE DLID placeholder, static-rate fallback, slave AH source MAC/VLAN override, query round-trips, and invalid GID-index mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/ah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/alias_GUID.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/alias_GUID.c

## Purpose
`alias_GUID.c` manages SR-IOV alias GUID assignment for mlx4 master devices. It tracks desired GUIDInfo records, sends SA GUIDInfo set/delete requests, updates caches from SMP responses, and notifies slaves when their GUID state changes.

## Important APIs, Types, And Functions
External entry points include `mlx4_ib_update_cache_on_guid_change()`, `mlx4_ib_notify_slaves_on_guid_change()`, `mlx4_ib_slave_alias_guid_event()`, `mlx4_ib_invalidate_all_guid_record()`, `mlx4_ib_init_alias_guid_work()`, `mlx4_ib_destroy_alias_guid_service()`, and `mlx4_ib_init_alias_guid_service()`. `aliasguid_query_handler()` handles SA responses. `invalidate_guid_record()`, `set_guid_rec()`, `set_required_record()`, `get_low_record_time_index()`, `get_next_record_to_update()`, and `alias_guid_work()` implement scheduling and retry logic.

## Control Flow
Initialization allocates/registers an SA client, initializes per-port records to delete values, optionally clears admin GUIDs for SM assignment, invalidates records, and creates ordered per-port workqueues. Invalidation marks records idle and queues work. Work selects the earliest due record, decides whether to set or delete based on pending GUID values, queries port state, sends an SA GUIDInfo request, and records callback context. The callback compares SM responses with required values, updates admin/cache data, applies exponential retry for declined entries, marks records set when complete, notifies slaves, and reschedules the next record.

## State And Persistence
Per-port alias GUID state lives in `dev->sriov.alias_guid.ports_guid[]`: records, GUID indexes, status, retry schedules, time-to-run, callbacks, state flags, and workqueue. Admin GUIDs stored through `mlx4_set_admin_guid()` provide persistence across subsequent requests as mediated by mlx4 core. The demux GUID cache is updated on GUIDInfo changes and used to decide slave notifications.

## Dependencies And Integration Points
This file depends on mlx4 master/SR-IOV helpers, IB SA GUIDInfo queries, IB MAD/SA data structures, port query state, slave port-state machinery, GUID change EQEs, workqueues, spinlocks, and the module parameter/flag controlling SM GUID assignment.

## Risks
The code has intricate locking across `going_down_lock` and `ag_work_lock`; teardown must cancel SA queries without racing callbacks. Retry scheduling uses seconds and boot-time nanoseconds, so time conversion mistakes can delay records. Slave notification depends on cache matching SM data; stale caches can suppress events. GUID record byte casts must preserve big-endian layout. Ordered per-port workqueues reduce concurrency but make stuck SA requests visible as delayed GUID propagation.

## Test Signals
Test master-only initialization, per-port workqueue creation failure unwind, port inactive rescheduling, SA set/delete success, declined GUID retry backoff, admin GUID persistence, cache update from SMP data, slave init/delete events, GUID invalidation on port management events, teardown with outstanding SA queries, and multi-slave/multi-port notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/alias_GUID.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cm.c

## Purpose
`cm.c` implements mlx4 SR-IOV connection-manager paravirtualization. It rewrites CM communication IDs between slave-visible IDs and physical-function IDs, demultiplexes inbound CM MADs to slaves, and cleans mapping state after disconnect/reject timeouts.

## Important APIs, Types, And Functions
Public functions are `mlx4_ib_multiplex_cm_handler()`, `mlx4_ib_demux_cm_handler()`, `mlx4_ib_cm_paravirt_init()`, `mlx4_ib_cm_paravirt_clean()`, `mlx4_ib_cm_init()`, and `mlx4_ib_cm_destroy()`. `struct id_map_entry` maps `(slave_id, slave_cm_id)` to `pv_cm_id` in both an rb-tree and xarray. `struct rej_tmout_entry` remembers which slave should receive timeout REJ messages. Helpers get/set local and remote comm IDs across normal CM and SIDR MAD formats.

## Control Flow
On outbound slave MADs, multiplexing allocates or finds a mapping for request-like messages, rewrites local comm ID to PF-visible ID, and schedules delayed cleanup on DREQ. On inbound MADs, demux finds the target slave from a REQ/SIDR_REQ SGID or from remote PF CM ID, rewrites remote comm ID back to the slave ID, and schedules cleanup on DREQ/REJ. Timeout REJ handling uses a separate xarray keyed by remote PF CM ID to route timeout rejects when no full ID map exists. Cleanup cancels delayed work, removes rb-tree/xarray/list entries, and frees objects for one slave or all slaves.

## State And Persistence
State is runtime-only in `dev->sriov`: `sl_id_map`, `pv_id_table`, `cm_list`, `pv_id_next`, `xa_rej_tmout`, and delayed cleanup work. Mappings persist for active CM conversations and for `CM_CLEANUP_CACHE_TIMEOUT` after teardown-like MADs.

## Dependencies And Integration Points
The file depends on RDMA CM MAD formats, mlx4 SR-IOV slave/GID lookup helpers, rbtrees, xarrays, delayed workqueues, and module-level `cm_wq` created by `mlx4_ib_cm_init()`.

## Risks
CM MAD field handling is attr-id-specific; SIDR REP/REQ local/remote ID misuse logs errors and returns `-1` cast to `u32`. `sl_id_map_add()` replaces an rb-node without freeing the old entry, so callers must avoid duplicate live mappings or accept leak risk. Cleanup races are mitigated with locks and flushes but remain subtle. REJ timeout routing is best-effort; allocation failure still passes the REQ to a slave but may lose timeout REJ routing.

## Test Signals
Test REQ/REP/MRA/SIDR_REQ mapping allocation, DREQ cleanup scheduling, inbound REQ GID-to-slave routing, timeout REJ fallback, duplicate slave CM IDs, per-slave and all-slave cleanup, workqueue init/destroy, and concurrent demux/multiplex under teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cq.c

## Purpose
`cq.c` implements mlx4 completion queue lifecycle, resizing, polling, arming, CQE decoding, software flush completions, and CQ cleanup for QP teardown.

## Important APIs, Types, And Functions
Creation APIs are `mlx4_ib_create_cq()` and `mlx4_ib_create_user_cq()`. `mlx4_ib_resize_cq()` handles kernel and user CQ resizing. `mlx4_ib_destroy_cq()` frees hardware and memory resources. Runtime APIs include `mlx4_ib_poll_cq()`, `mlx4_ib_arm_cq()`, `mlx4_ib_modify_cq()`, `mlx4_ib_cq_clean()`, and `__mlx4_ib_cq_clean()`. Internal helpers handle CQE ownership (`get_sw_cqe()`), buffer allocation/Mtt setup, outstanding CQE count, resize CQE copying, error syndrome mapping, IPoIB checksum flags, tunnel metadata extraction, and single-CQE translation in `mlx4_ib_poll_one()`.

## Control Flow
CQ creation rounds requested entries to a power-of-two-plus-one ring, initializes locks and QP lists, maps user memory/doorbell or allocates kernel doorbell/buffer, writes MTTs, and calls `mlx4_cq_alloc()`. Resizing allocates a new buffer or user umem, asks hardware to resize, then swaps buffers; kernel resize copies outstanding CQEs after a resize marker. Polling locks the CQ, emits software flush completions if the device is in internal error, otherwise repeatedly checks owner bits, handles resize markers, finds the QP, advances send/recv/SRQ tails, maps errors or opcodes into `ib_wc`, fills addressing/checksum metadata, updates consumer index, and unlocks. Cleanup sweeps unpolled CQEs for a QPN and compacts the ring.

## State And Persistence
`struct mlx4_ib_cq` owns an mlx4 CQ object, buffer/MTT, doorbell, resize buffer/umem, consumer index, lock, resize mutex, and send/recv QP lists. CQE ownership bits and consumer index coordinate hardware/software ring state. No state persists after CQ destruction.

## Dependencies And Integration Points
The file depends on mlx4 core CQ, MTT, buffer, doorbell, QP, and SRQ APIs; RDMA uverbs CQ ABI; mlx4 QP/SRQ driver structures; IPoIB checksum semantics; proxy SQP tunnel headers for SR-IOV; and RDMA core CQ polling/arming callbacks.

## Risks
CQE parsing is highly hardware-specific, especially 64-byte CQE offset handling, owner-bit logic, resize markers, and opcode/status decoding. User CQ creation rejects pre-provided umem when software CQ init is required, which must match userspace ABI expectations. `mlx4_ib_poll_one()` assumes QP lookup succeeds; stale CQEs during teardown depend on CQ locking and cleanup ordering. Internal-error software completions require accurate QP list maintenance. CQ clean ring compaction must preserve owner bits or polling can lose/duplicate CQEs.

## Test Signals
Test kernel and user CQ creation, timestamp flag validation, doorbell mapping failure, MTT write failure, resize up/down with outstanding CQEs, poll of send/recv/SRQ/XRC completions, every error syndrome, immediate/invalidate/atomic/LSO/FMR opcodes, RoCE VLAN/SMAC and IP checksum flags, proxy SQP tunnel completions, internal-error software flush, arm modes, CQ clean during QP reset, and destroy after resize failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/doorbell.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/doorbell.c

## Purpose
`doorbell.c` maps and unmaps userspace doorbell pages for mlx4 user objects.

## Important APIs, Types, And Functions
`struct mlx4_ib_user_db_page` tracks one pinned user page, its virtual page base, refcount, and list node. `mlx4_ib_db_map_user()` finds or pins the page containing a user doorbell address, computes the DMA address for the requested offset, stores the page pointer in `struct mlx4_db`, and increments the page refcount. `mlx4_ib_db_unmap_user()` decrements the refcount and releases the umem/page object when the last mapping is gone.

## Control Flow
Map obtains the ucontext from udata, locks `db_page_mutex`, searches `db_page_list` for `virt & PAGE_MASK`, allocates and pins a new page if missing, links it, computes `db->dma`, stores `db->u.user_page`, increments refcount, and unlocks. Unmap locks, decrements, removes/releases/frees on zero, and unlocks.

## State And Persistence
Pinned doorbell pages are cached per user context in `db_page_list`. Each `struct mlx4_db` references a cached page and DMA offset. State lasts until all CQ/QP/SRQ users of that doorbell page unmap it or the ucontext is destroyed.

## Dependencies And Integration Points
The file uses RDMA udata-to-ucontext helpers, `ib_umem_get()`/`ib_umem_release()`, SG DMA address extraction, and is used by mlx4 user CQ/QP/SRQ creation paths.

## Risks
DMA address uses the first SG entry plus offset, assuming a single pinned page layout. Refcounting depends on every successful map being paired with unmap. The page cache is protected by a mutex, but consumers must not access `db->u.user_page` after unmap.

## Test Signals
Test mapping two doorbells on the same page, mapping different pages, pin failure, allocation failure, exact DMA offset calculation, refcounted unmap, and concurrent map/unmap from one ucontext.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/doorbell.c -->
