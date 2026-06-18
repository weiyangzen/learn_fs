# subset-b-003951 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/verbs.c

Purpose: QLogic/Broadcom `qedr` RDMA verbs implementation for RoCE and iWARP. It supplies the `ib_device_ops` backing for device/port queries, user contexts, mmap, PD/XRCD/CQ/SRQ/QP/AH/MR lifecycles, send/receive posting, SRQ posting, CQ polling, and a minimal MAD path.

Important APIs/functions: query helpers include `qedr_query_device()`, `qedr_query_port()`, `qedr_iw_query_gid()`, `qedr_query_pkey()`, and `qedr_query_srq()`. Object lifecycle is handled by `qedr_alloc_ucontext()`, `qedr_mmap()`, `qedr_alloc_pd()`, `qedr_create_cq()`, `qedr_create_srq()`, `qedr_create_qp()`, `qedr_modify_qp()`, `qedr_query_qp()`, and destroy/dealloc counterparts. Memory registration paths include `qedr_reg_user_mr()`, `qedr_alloc_mr()`, `qedr_map_mr_sg()`, `qedr_get_dma_mr()`, and `qedr_dereg_mr()`. Fast path APIs are `qedr_post_send()`, `qedr_post_recv()`, `qedr_post_srq_recv()`, `qedr_arm_cq()`, and `qedr_poll_cq()`.

Control flow: ucontext allocation asks qed core for a DPI, creates an RDMA mmap entry for the doorbell BAR, and returns DPM/queue limits to userspace. CQ/SRQ/QP creation validates user/kernel parameters, pins user queues or allocates kernel chains, prepares PBLs, calls `dev->ops->rdma_*` ramrods, then records doorbell recovery data. QP modification translates IB attributes and state transitions to qed firmware flags, including RoCE GID/MAC/VLAN/MTU conversion. Posting builds hardware WQEs under `qp->q_lock`, updates shadow WR IDs and producers, uses memory barriers, then rings doorbells. CQ polling checks the toggle bit, classifies requester/responder/SRQ CQEs, advances software queues, translates hardware statuses to `ib_wc`, and re-doorbells the CQ consumer.

State and persistence: durable runtime state is in driver objects embedded in RDMA core objects: `qedr_ucontext` DPI/mmap/db-rec flags, `qedr_pd` IDs, CQ chain/toggle/consumer and db recovery data, QP state/ICID/QP ID/SQ/RQ shadow arrays, SRQ xarray entries, MR TID/PBL state, and iWARP QP xarray/refcount/completions. Hardware-visible state persists in qed core RDMA resources, DMA coherent PBL pages, pinned user memory, mmap entries, and doorbell recovery registrations.

Dependencies and integration: depends on RDMA core/uverbs, `qedr.h`, `qedr_hsi_rdma.h`, `qedr-abi.h`, RoCE/iWARP CM helpers, qed common chain/doorbell APIs, DMA mapping, IOMMU, networking GID/MAC helpers, xarrays, and Linux memory pinning APIs. It is wired into the qedr device ops from the broader qedr driver.

Risks: cleanup and error unwinds are complex and mix user/kernel, RoCE/iWARP, and GSI special cases. PBL sizing/population, mmap offsets, and doorbell recovery must stay ABI-compatible with userspace. `qedr_destroy_cq()` waits for CNQ notification counts and relies on IRQ/event ordering. CQ polling trusts hardware CQE QP handles and must maintain producer/consumer/toggle correctness. State changes to ERR are deliberately made before firmware completion to avoid fast-path races. Memory registration requires correct `pinned`/PBL/TID release on every partial failure.

Test signals: build with RoCE and iWARP enabled; rdma-core verbs smoke tests for context/PD/CQ/QP/MR lifecycle; mmap of doorbells and db-rec pages; RC send/recv/read/write/atomic and immediate/invalidate completions; SRQ and XRC paths; CQ destroy during interrupt activity; QP transitions and error flushes; MR map/invalidate reuse; GSI QP traffic; iWARP connect/disconnect teardown; fault injection in `dev->ops->rdma_*`, `ib_umem_get()`, PBL allocation, and udata copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/verbs.h

Purpose: public verbs declaration header for the qedr RDMA driver. It exposes the function surface implemented in `verbs.c` for registration in qedr `ib_device_ops` and use by adjacent qedr CM/GSI code.

Important APIs/types: declares query APIs, ucontext/mmap/PD/XRCD lifecycle, CQ create/destroy/arm/poll, QP create/modify/query/destroy/post send/post recv, SRQ create/modify/query/destroy/post receive, AH create/destroy, MR registration/allocation/map/deregistration, MAD processing, and `qedr_port_immutable()`.

Control flow: the main qedr device setup includes this header and assigns these callbacks into RDMA core operations. Runtime calls originate from RDMA core/uverbs and land in `verbs.c`; no inline logic or state is stored here.

State and persistence: no state. Persistence is delegated to structures declared in `qedr.h` and allocated/manipulated by the implementation.

Dependencies and integration: relies on RDMA core types such as `ib_device`, `ib_udata`, `uverbs_attr_bundle`, `ib_qp`, `ib_mr`, and `rdma_user_mmap_entry`, plus kernel `scatterlist` and VM types supplied by includers.

Risks: prototypes are the contract between qedr registration and implementation; signature drift with RDMA core APIs will break builds. The header does not encode sequencing constraints, so callers must still respect RDMA core object lifetimes.

Test signals: compile coverage of all `ib_device_ops` assignments, module load, and rdma-core lifecycle tests that exercise each declared callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Kconfig

Purpose: Kconfig entry enabling Cisco VIC usNIC verbs support as `INFINIBAND_USNIC`.

Important symbols: `INFINIBAND_USNIC` is a tristate "Verbs support for Cisco VIC". It depends on networking, Ethernet, INET, PCI, Intel IOMMU, and `INFINIBAND_USER_ACCESS`; it selects Cisco ENIC, Cisco net vendor support, and PCI SR-IOV.

Control flow: when selected, the kernel build includes the usNIC low-level RDMA driver for Cisco VIC 1240/1280-style devices. Without the dependencies, the driver is not offered.

State and persistence: no runtime state; it controls build configuration.

Dependencies and integration: integrates the RDMA driver with the Cisco ENIC netdev stack, PCI IOV, and user-access RDMA infrastructure. The Intel IOMMU dependency matches the driver's explicit IOMMU-domain memory mapping model.

Risks: the hard `INTEL_IOMMU` dependency excludes non-Intel IOMMU platforms even if generic IOMMU APIs could theoretically support them. Missing `INFINIBAND_USER_ACCESS` would break the uverbs-only design.

Test signals: `olddefconfig`, `allyesconfig`/module builds, dependency resolution with ENIC/PCI_IOV, and boot probe on VIC hardware with IOMMU enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Makefile

Purpose: object composition for the usNIC verbs module.

Important entries: adds the Cisco ENIC include path, builds `usnic_verbs.o` for `CONFIG_INFINIBAND_USNIC`, and links forwarding, transport, UIOM, interval tree, vNIC resource management, IB main, QP group, sysfs, verbs, and debugfs objects.

Control flow: Kconfig selects whether `usnic_verbs-y` is compiled as built-in or module objects. The object list defines the integration boundary among ENIC-backed forwarding, RDMA verbs, resource allocation, and observability.

State and persistence: no runtime state.

Dependencies and integration: depends on headers from `drivers/net/ethernet/cisco/enic`; pairs with `Kconfig` and the parent RDMA Makefile to include the driver.

Risks: omitting `usnic_uiom_interval_tree.o` or `usnic_vnic.o` would leave referenced helper APIs unresolved. Include-path coupling to ENIC internal headers is fragile across ENIC reorganizations.

Test signals: module and built-in builds, `modpost` symbol resolution, and compile coverage when `CONFIG_INFINIBAND_USNIC=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic.h

Purpose: small shared identity header for the Cisco usNIC verbs driver.

Important APIs/data: defines `DRV_NAME` as `usnic_verbs`, the Cisco VIC userspace NIC PCI device ID `0x00cf`, and driver version/date strings.

Control flow: included by logging, main, debugfs, and other usNIC files to keep module names, PCI IDs, and build-info output consistent.

State and persistence: no mutable state.

Dependencies and integration: provides the PCI ID used by `usnic_ib_main.c` and strings used by module metadata/debugfs/logging.

Risks: stale version/date strings can mislead operators. Changing `DRV_NAME` affects PCI region request names, debugfs root, and log prefixes.

Test signals: module metadata, debugfs build-info output, PCI probe matching, and log prefix consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_abi.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_abi.h

Purpose: kernel/userspace ABI definitions for usNIC uverbs.

Important APIs/types: defines `USNIC_UVERBS_ABI_VERSION` 4, maximum WQ/RQ/CQ counts returned per QP group, `enum usnic_transport_type`, `struct usnic_transport_spec`, `struct usnic_ib_create_qp_cmd`, and `struct usnic_ib_create_qp_resp`.

Control flow: userspace passes a create-QP command with either a custom RoCE port or UDP socket FD. Kernel responds with VF ID, QP group ID, BAR bus address/length, resource indices, selected transport, and reserved padding.

State and persistence: no kernel state, but this file is a persistent ABI contract with user libraries.

Dependencies and integration: consumed by verbs, QP group, transport, and forwarding code. It determines the uverbs ABI version advertised in `usnic_dev_ops`.

Risks: layout, enum, and version changes can break existing userspace. The response exposes BAR mapping details and fixed-size arrays, so resource-count bounds must match kernel allocation. Reserved fields should remain zeroed for forward compatibility.

Test signals: rdma-core/usNIC user library create-QP compatibility, ABI size checks across 32/64-bit builds, and mmap tests using returned BAR metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_pkt_hdr.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_pkt_hdr.h

Purpose: packet header constants for usNIC custom RoCE-style filtering.

Important data: defines `USNIC_ROCE_GRH_VER`, `USNIC_PROTO_VER`, and `USNIC_ROCE_GRH_VER_SHIFT`.

Control flow: `usnic_fwd_init_usnic_filter()` combines these constants into the filter's protocol-version field when steering custom usNIC/RoCE traffic.

State and persistence: no runtime state; constants encode wire/filter semantics.

Dependencies and integration: included by forwarding code and paired with ENIC `FILTER_USNIC_ID` command formats.

Risks: values must match firmware and userspace packet construction. A protocol-version mismatch would prevent filters from matching traffic.

Test signals: successful custom RoCE QP group creation, ENIC filter installation, and traffic steering to the expected RQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_pkt_hdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_util.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_util.h

Purpose: shared utility helpers for usNIC addressing.

Important APIs: `usnic_mac_ip_to_gid()` builds a link-local style raw GID using `fe80`, the IPv4 address in bytes 4..7, and an EUI-48-derived interface identifier from the MAC address.

Control flow: device add/query paths call this helper to populate node GUID, sys image GUID, and query-GID responses based on the current PF MAC/IP state.

State and persistence: no state; output depends on caller-provided MAC and IPv4 address.

Dependencies and integration: depends on `addrconf_addr_eui48()` from IPv6 addrconf and is used by `usnic_ib_main.c` and `usnic_ib_verbs.c`.

Risks: GID identity changes when MAC/IP changes; notifier code must dispatch GID change events and move active QP groups to error. If no IP exists, the generated GID contains a zero IPv4 field.

Test signals: query-GID output before/after IPv4 address changes, node GUID generation during probe, and GID change event delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_common_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.c

Purpose: debugfs observability for the usNIC driver.

Important APIs/functions: `usnic_debugfs_init()` creates `/sys/kernel/debug/usnic_verbs`, `flows`, and `build-info`; `usnic_debugfs_exit()` removes the tree; `usnic_debugfs_flow_add()` and `usnic_debugfs_flow_remove()` add/remove per-flow files. Read handlers emit version/build date and flow transport metadata.

Control flow: module init creates the debugfs root; QP group flow creation adds a file named by firmware flow ID; flow teardown removes it. Flow reads lock the owning QP group, format QP group ID and transport, and include custom RoCE port or UDP socket address.

State and persistence: global dentries hold debugfs root and flow directory. Per-flow debugfs dentry/name are stored in `struct usnic_ib_qp_grp_flow`. State is transient and removed on flow/module teardown.

Dependencies and integration: depends on Linux debugfs, QP group structures, transport formatting, and driver version macros.

Risks: debugfs flow file private data points at live QP flow objects, so teardown ordering must prevent use-after-free. `flowinfo_read()` uses `count` as remaining buffer size against a fixed 512-byte stack buffer, so very large userspace read counts can make `left` exceed the actual buffer capacity.

Test signals: debugfs tree creation/removal, build-info content, creating/destroying RoCE and UDP QPs while reading flow files, and KASAN/lockdep coverage for concurrent teardown/read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.h

Purpose: debugfs API declarations for usNIC.

Important APIs: declares module-level init/exit and per-flow add/remove helpers accepting `struct usnic_ib_qp_grp_flow`.

Control flow: `usnic_ib_main.c` calls init/exit at module load/unload; `usnic_ib_qp_grp.c` calls flow add/remove around firmware filter lifetime.

State and persistence: no state in the header; implementation owns dentries and per-flow debugfs fields.

Dependencies and integration: includes `usnic_ib_qp_grp.h`, tying debugfs entries to QP group flow objects.

Risks: callers must pair add/remove exactly with QP flow allocation/freeing.

Test signals: compile linkage and debugfs entries appearing and disappearing with QP group flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.c

Purpose: forwarding and filter programming shim between usNIC QP groups and Cisco ENIC firmware devcmds.

Important APIs/functions: `usnic_fwd_dev_alloc/free()`, setters for MAC/IP/carrier/MTU, `usnic_fwd_alloc_flow()`, `usnic_fwd_dealloc_flow()`, `usnic_fwd_enable_qp()`, and `usnic_fwd_disable_qp()`. Internal helpers wrap `enic_api_devcmd_proxy_by_index()`, validate device readiness/filter fields, and build ENIC TLV payloads.

Control flow: PF probe allocates a forwarding device from the PF netdev. Notifiers update link/MAC/IP/MTU. QP group creation builds either a usNIC-ID or UDP 5-tuple filter, validates link and IP/port constraints, DMA-allocates TLVs, sends `CMD_ADD_FILTER`, and records the returned flow ID. QP group state transitions call enable/disable devcmds for the selected RQ/WQ resources; teardown sends `CMD_DEL_FILTER`.

State and persistence: `struct usnic_fwd_dev` caches PF netdev, PCI device, lock, MAC, MTU, link state, IPv4 address, and stable name. `struct usnic_fwd_flow` stores firmware flow ID, VF index, and owner forwarding device.

Dependencies and integration: depends on ENIC internal APIs/types (`enic_api.h`, `vnic_devcmd.h`), Linux netdev/PCI, packet constants, and QP group flow setup.

Risks: filter validity depends on current PF IP/link state and can be invalidated by netdev events. `CMD_DEL_FILTER` errors are logged but converted to success because firmware deletion failure is unrecoverable, which can hide leaked filters. TLV allocation uses `GFP_ATOMIC`; pressure can make QP creation fail. Locking is spinlock-based around firmware proxy commands.

Test signals: add/delete filter devcmds, UDP socket filters matching PF IPv4 address, QP enable/disable transitions, link-down rejection, netdev reboot/down cleanup, and fault injection for ENIC command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.h

Purpose: forwarding data model and helper declarations for usNIC.

Important APIs/types: defines `struct usnic_fwd_dev`, `struct usnic_fwd_flow`, `struct usnic_filter_action`, lifecycle/update APIs, flow allocation/free APIs, QP enable/disable APIs, and inline initializers for custom usNIC and UDP filters.

Control flow: QP group code uses inline filter initializers, then calls `usnic_fwd_alloc_flow()` and QP enable/disable helpers as state changes. Main netdev notifier code updates cached forwarding-device state through setters.

State and persistence: makes explicit the cached PF forwarding state and firmware flow identity that persists across a QP group's lifetime.

Dependencies and integration: includes Linux netdev/PCI/IP headers, usNIC ABI/packet constants, and ENIC `vnic_devcmd` filter/action types.

Risks: header comments require callers to monitor netdev reset/down events and free flows immediately; failure to honor that contract leaves stale firmware steering. Inline filter construction must stay aligned with ENIC firmware expectations.

Test signals: compile coverage, filter field inspection in ENIC devcmd traces, QP traffic steering, and flow cleanup on netdev events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_fwd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib.h

Purpose: central usNIC RDMA object definitions and container helpers.

Important APIs/types: defines one-port/one-completion-vector constants, module parameter `usnic_ib_share_vf`, `struct usnic_ib_ucontext`, `struct usnic_ib_pd`, `struct usnic_ib_cq`, `struct usnic_ib_mr`, `struct usnic_ib_dev`, `struct usnic_ib_vf`, container conversion helpers, `usnic_ib_log_vf()`, and `UPDATE_PTR_LEFT`.

Control flow: RDMA core allocates objects sized through `INIT_RDMA_OBJ_SIZE`; verbs callbacks convert generic IB objects to usNIC-specific containers. PF/VF management and QP group code use these structures for device, context, PD, MR, and VF ownership.

State and persistence: `usnic_ib_dev` holds PF netdev/PCI/forwarding device, VF list, user context list, lock, VF resource counts, kref, and QPN sysfs root. `usnic_ib_vf` tracks one VF vNIC, QP group refcount, bound PD, and lock. Ucontexts own QP group lists; PDs own UIOM protection domains.

Dependencies and integration: depends on RDMA core, IOMMU, netdevice, usNIC ABI, and vNIC resource headers. It is the shared contract among main, verbs, QP group, sysfs, UIOM, and forwarding code.

Risks: locking rules are implicit in comments and code: context/QP group lists are protected by `usdev_lock`, VF bind/refcount by `vf->lock`, and QP group flow state by its spinlock. Violating those rules risks list corruption or IOMMU detach while resources are active.

Test signals: RDMA object allocation/free paths, VF sharing enabled/disabled, context teardown with empty QP group list, and lockdep on QP create/destroy/remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_main.c

Purpose: module, PCI, PF/VF discovery, netdev/inet notifier, and RDMA device registration logic for Cisco usNIC.

Important APIs/functions: module globals `usnic_log_lvl` and `usnic_ib_share_vf`; `usnic_ib_log_vf()`; netdev/inet handlers; `usnic_port_immutable()`; `usnic_get_dev_fw_str()`; `usnic_dev_ops`; PF lifecycle `usnic_ib_device_add/remove()`, `usnic_ib_discover_pf()`, `usnic_ib_undiscover_pf()`; PCI probe/remove; module init/exit.

Control flow: module init registers PCI, netdev, inetaddr notifiers, initializes transport bitmap, and creates debugfs. PCI probe validates IOMMU mapping, enables/request regions for a VF, allocates `usnic_vnic`, discovers or creates the parent PF RDMA device, links the VF, and records per-VF resource counts. PF creation allocates an `ib_device`, forwarding device, netdev binding, sysfs group, initial MAC/MTU/link/IP state, node GUID, and RDMA ops. Netdev/IP events update forwarding state, transition active QP groups to ERR, and dispatch RDMA port/GID events. Remove reverses VF registration and drops the PF kref, unregistering PF when the last VF disappears.

State and persistence: global PF list and lock track registered PF devices. Each PF owns VF list, context list, forwarding state, sysfs QPN root, and kref. Module parameters persist until unload. Notifier-derived MAC/IP/link/MTU state persists in `ufdev`.

Dependencies and integration: ties together RDMA core, PCI, Cisco ENIC/vNIC resources, forwarding, UIOM, transport, debugfs, sysfs, and netdev/inet notifier APIs.

Risks: probe requires `device_iommu_mapped()`; without IOMMU no QPs are allowed. PF removal depends on accurate VF krefs. Netdev notifier uses `ib_device_get_by_netdev()` and must avoid lock inversions with rtnl; `query_port()` explicitly calls `ib_get_eth_speed()` before `usdev_lock` for that reason. Active QP groups are force-moved to ERR on address/link/reset changes.

Test signals: module load/unload ordering, PCI VF probe/remove, PF creation for first VF and destruction after last VF, notifier-driven GID/port events, IOMMU-disabled probe failure, sysfs/debugfs presence, and lockdep during netdev events plus QP churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.c

Purpose: manages usNIC QP groups, the abstraction that maps one userspace UD QP to VF resources, firmware filters, QP enablement, sysfs/debugfs entries, and UIOM PD/VF binding.

Important APIs/functions: `usnic_ib_qp_grp_state_to_string()`, dump helpers, `usnic_ib_qp_grp_create()`, `usnic_ib_qp_grp_modify()`, `usnic_ib_qp_grp_destroy()`, and `usnic_ib_qp_grp_get_chunk()`. Internals allocate/free vNIC resource chunks, create/release custom RoCE and UDP flows, enable/disable QPs, bind/unbind VF to UIOM PD, and derive QP group ID from flow port.

Control flow: create validates the requested resource spec against `min_transport_spec`, allocates WQ/RQ/CQ chunks from the VF vNIC, attaches the VF device to the PD's IOMMU domain on first group, initializes flow list/lock/state, creates the initial transport flow, derives `qp_num`, and registers sysfs. State transitions implement RESET/INIT/RTR/RTS/ERR: INIT creates or adds flows, RTR enables QPs, RTS is currently a no-op from RTR, RESET/ERR disable QPs and release flows as needed, and ERR dispatches `IB_EVENT_QP_FATAL`.

State and persistence: `struct usnic_ib_qp_grp` owns state, group ID/QPN, owner PID, resource chunk list, VF pointer, flow list, sysfs kobject, and forwarding device. Flow objects own firmware flow handles plus reserved RoCE ports or held UDP sockets. VF refcount and PD binding persist while groups are active.

Dependencies and integration: depends on vNIC resource allocation, forwarding devcmds, transport port/socket helpers, UIOM IOMMU attachment, sysfs QPN registration, debugfs flow files, and RDMA QP event callbacks.

Risks: state transition matrix is hand-coded and must keep firmware filters, QP enablement, sysfs/debugfs, socket refs, port reservations, and IOMMU attachment balanced. The code holds `qp_grp->lock` while creating/removing flows and calling forwarding/transport helpers, so blocking assumptions matter. `usnic_ib_qp_grp_destroy()` warns unless the group is already RESET.

Test signals: create/destroy loops for RoCE custom and UDP transports, INIT with additional filters, INIT->RTR->RTS->RESET transitions, ERR transition event delivery, VF sharing/refcount behavior, resource exhaustion, port reservation conflicts, UDP socket lifetime, and sysfs/debugfs cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.h

Purpose: QP group data structures and API declarations for usNIC.

Important APIs/types: defines `struct usnic_ib_qp_grp`, `struct usnic_ib_qp_grp_flow`, external `min_transport_spec`, state/dump helpers, create/destroy/modify/get-chunk APIs, and `to_uqp_grp()`.

Control flow: verbs create/modify/destroy callbacks operate on `struct ib_qp` and convert to QP groups. QP group implementation uses fields declared here to track resources, flows, owner, state, and sysfs/debugfs objects.

State and persistence: header documents the persistent QP group state: IB QP wrapper, state, group ID, forwarding device, user context, flow list, resource chunks, owner PID, VF binding, list node, spinlock, and kobject. Flow state includes firmware flow pointer, transport-specific port/socket, parent group, list node, debugfs dentry, and dentry name.

Dependencies and integration: includes debugfs, RDMA verbs, usNIC IB structures, ABI, forwarding, and vNIC resource definitions.

Risks: object lifetime spans RDMA core, sysfs, debugfs, sockets, transport port bitmap, and vNIC resources; all users must observe the locking and teardown ordering implemented in `usnic_ib_qp_grp.c`.

Test signals: compile coverage, container conversion correctness, QP group sysfs/debugfs lifetime, and resource chunk lookup for WQ/RQ/CQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_qp_grp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.c

Purpose: sysfs reporting for usNIC PF devices and per-QPN/QP-group state.

Important APIs/functions: device attributes `board_id`, `config`, `iface`, `max_vf`, `qp_per_vf`, and `cq_per_vf`; QPN attributes `context` and `summary`; public APIs `usnic_ib_sysfs_register_usdev()`, `usnic_ib_sysfs_unregister_usdev()`, `usnic_ib_sysfs_qpn_add()`, and `usnic_ib_sysfs_qpn_remove()`.

Control flow: RDMA device registration exposes `usnic_attr_group`. PF discovery creates a `qpn` kobject under the RDMA device. QP group creation initializes/adds a kobject named by group ID; removal drops both QP and parent kobject refs. Attribute reads format PF/VF/resource configuration or QP group state/resource indices.

State and persistence: persistent sysfs state is the PF `qpn_kobj` and each QP group's embedded `kobj`. Attribute output reflects live `usnic_ib_dev` and `usnic_ib_qp_grp` state.

Dependencies and integration: depends on RDMA device kobjects, usNIC IB/QP group/vNIC helpers, and sysfs emit APIs. It is called from PF and QP group lifecycle code.

Risks: kobject reference balancing is subtle: register gets the RDMA device kobj, QPN add gets the parent qpn kobj, and remove/unregister put refs. Attribute reads access live QP group pointers; QP teardown must remove sysfs before freeing backing data. `config_show()` iterates resource types starting at EOL and relies on enum ordering.

Test signals: sysfs files under RDMA device, QPN entry create/remove under QP churn, kobject leak checks, and reading attributes during netdev/VF changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.h

Purpose: sysfs API declarations for usNIC RDMA device and QPN reporting.

Important APIs: declares PF sysfs register/unregister, QP group QPN add/remove helpers, and exported `usnic_attr_group`.

Control flow: main PF lifecycle calls register/unregister; QP group lifecycle calls QPN add/remove; `usnic_dev_ops.device_group` points to `usnic_attr_group`.

State and persistence: no state in the header; implementation owns kobject and attribute state.

Dependencies and integration: includes `usnic_ib.h`, tying sysfs callbacks to PF and QP group structures.

Risks: callers must pair register/unregister and add/remove to avoid kobject leaks or dangling sysfs files.

Test signals: build linkage and sysfs lifecycle under module load/unload and QP create/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.c

Purpose: RDMA verbs callbacks for usNIC's userspace-oriented UD QP model.

Important APIs/functions: `min_transport_spec`, link/query callbacks, `usnic_ib_alloc_pd()/dealloc_pd()`, `usnic_ib_create_qp()/destroy_qp()/modify_qp()/query_qp()`, no-op CQ create/destroy, `usnic_ib_reg_mr()/dereg_mr()`, ucontext alloc/dealloc, and `usnic_ib_mmap()`. Helpers fill create-QP responses, choose VFs, and validate user create-QP transport data.

Control flow: query callbacks synthesize capabilities from PF/VF resource counts, forwarding state, firmware string, and MAC/IP-derived GID. PD allocation creates a UIOM IOMMU domain. Create QP accepts only userspace UD QPs, copies a `usnic_ib_create_qp_cmd`, validates transport, computes required CQ resources, finds a used VF in the same PD when sharing is enabled or an unused VF otherwise, creates a QP group, returns BAR/resource indices, and links the group to the ucontext. Modify QP only handles port validation and QP state changes via QP group modify. MR registration pins/maps user memory through UIOM and returns zero lkey/rkey because userspace owns the datapath. Mmap maps the selected VF BAR0 by VF ID in `vm_pgoff`.

State and persistence: PDs hold `usnic_uiom_pd`; MRs hold `usnic_uiom_reg`; ucontexts are linked into PF context lists and own QP group lists; QP groups persist in context lists until destroyed.

Dependencies and integration: depends on RDMA/uverbs, QP group, vNIC resources, forwarding, transport, UIOM, and MAC/IP-to-GID helpers.

Risks: only UD QPs are supported; unsupported CQ operations are accepted as no-ops except flags. Create-QP response exposes BAR bus address/length and fixed resource arrays. VF sharing relies on UIOM device-list snapshots and freeing them in every path; one success path intentionally hands ownership to the QP group. `query_device()` rejects non-empty udata, which can surprise newer userspace probing extensions.

Test signals: uverbs ABI compatibility, QP creation for custom RoCE and UDP transports, VF sharing on/off, BAR mmap by VF ID and length validation, MR pin/map/release, query outputs across link/IP changes, and destroy/modify state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.h

Purpose: declarations for usNIC RDMA verbs callbacks registered in `usnic_dev_ops`.

Important APIs: declares link layer, device/port/QP/GID query, PD lifecycle, QP create/destroy/modify, CQ create/destroy, MR register/deregister, ucontext lifecycle, and mmap callbacks.

Control flow: `usnic_ib_main.c` includes this header and wires each function into RDMA core operations. RDMA core invokes the implementation in `usnic_ib_verbs.c`.

State and persistence: no state here; concrete object state is in `usnic_ib.h` and QP group/UIOM structures.

Dependencies and integration: includes `usnic_ib.h` for object containers and RDMA types.

Risks: callback signatures must track RDMA core API changes. The header does not reveal unsupported operations, so behavior is defined by implementation.

Test signals: compile coverage of `usnic_dev_ops` assignments and uverbs lifecycle tests reaching each callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_ib_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_log.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_log.h

Purpose: lightweight logging macros and log-level declarations for usNIC.

Important APIs/data: declares external `usnic_log_lvl`, level constants NONE/ERR/INFO/DBG, and macros `usnic_printk`, `usnic_dbg`, `usnic_info`, and `usnic_err`.

Control flow: call sites emit messages only when the module parameter `usnic_log_lvl` is high enough. Prefixes include driver name, function, and line number.

State and persistence: the mutable log level is defined in `usnic_ib_main.c` and exposed as a module parameter.

Dependencies and integration: includes `usnic.h` for `DRV_NAME`; used by nearly every usNIC implementation file.

Risks: macros use `printk` directly and can produce noisy logs at debug level. The macro formatting is old-style variadic GNU C and should be kept build-compatible. Line-number prefixes change with edits, which can affect log matching.

Test signals: module parameter read/write, logs at each level, and build coverage with all macro call patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.c

Purpose: transport-specific helper layer for usNIC custom RoCE port allocation and UDP socket inspection.

Important APIs/functions: `usnic_transport_to_str()`, `usnic_transport_sock_to_str()`, `usnic_transport_rsrv_port()`, `usnic_transport_unrsrv_port()`, `usnic_transport_get_socket()`, `usnic_transport_put_socket()`, `usnic_transport_sock_get_addr()`, `usnic_transport_init()`, and `usnic_transport_fini()`.

Control flow: module init allocates a bitmap and reserves port 0. QP group creation reserves a custom RoCE port or gets a referenced socket from a user FD, extracts AF_INET/protocol/address/port, and later releases the port/socket on flow teardown. Port 0 requests auto-allocate from `roce_next_port`.

State and persistence: global `roce_bitmap`, `roce_next_port`, and spinlock track reserved custom RoCE ports for the module lifetime. UDP socket references persist in QP group flow objects.

Dependencies and integration: depends on Linux bitmaps, socket fd lookup, inet socket access, and usNIC ABI transport enums. Integrated by QP group flow creation and debugfs formatting.

Risks: `ROCE_BITMAP_SZ` is expressed as bytes but passed as bit count to bitmap helpers, limiting allocation to 8192 bits rather than all 16-bit ports. Auto-allocation wraps through the low 4096 range via `(port_num & 4095) + 1`. Socket address extraction only supports AF_INET and trusts `sock->ops->getname()`.

Test signals: custom port reserve/free including collisions and port 0 auto-allocation, UDP socket fd reference/release, non-UDP and non-IPv4 rejection, transport debugfs string output, and module unload leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.h

Purpose: public transport helper declarations for usNIC.

Important APIs: declares transport string formatting, socket string/address helpers, RoCE custom port reserve/unreserve, socket get/put, and module init/fini functions.

Control flow: QP group code calls reserve/get helpers during flow creation and unreserve/put helpers during flow release. Debugfs calls string formatting. Main module calls init/fini.

State and persistence: header declares no state; implementation maintains the RoCE bitmap and socket refs.

Dependencies and integration: includes the usNIC ABI transport enum and uses kernel `struct socket` from includers.

Risks: comments define ownership rules: callers must call `usnic_transport_put_socket()` after `get_socket()` and call socket address helpers only after obtaining a reference.

Test signals: compile linkage and QP create/destroy paths for both custom RoCE and UDP transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_transport.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.c

Purpose: userspace I/O memory registration and IOMMU mapping for usNIC protection domains.

Important APIs/functions: `usnic_uiom_reg_get()`, `usnic_uiom_reg_release()`, `usnic_uiom_alloc_pd()`, `usnic_uiom_dealloc_pd()`, `usnic_uiom_attach_dev_to_pd()`, `usnic_uiom_detach_dev_from_pd()`, `usnic_uiom_get_dev_list()`, and `usnic_uiom_free_dev_list()`. Internal helpers pin pages, build SG chunks, compute interval diffs, map/unmap IOMMU ranges, and handle DMA faults.

Control flow: PD allocation creates an IOMMU paging domain with a fault handler. VF binding attaches a device to the domain and records it. MR registration pins long-term user pages under memlock accounting, builds chunks, computes intervals not already mapped in the PD interval tree, maps contiguous physical spans into IOVA equal to userspace VA page addresses, then inserts intervals. Release removes intervals, unmaps pages no longer referenced, unpins dirty writable pages, decrements pinned VM, and drops the owning mm reference.

State and persistence: `usnic_uiom_pd` owns an IOMMU domain, interval tree root, device list/count, and spinlock. `usnic_uiom_reg` owns VA/length/offset/writable state, chunk list, owning mm, and PD pointer. Pinned pages and IOMMU mappings persist until MR deregistration.

Dependencies and integration: depends on Linux GUP/pinning, IOMMU domain APIs, scatterlists, mm accounting, and the usNIC interval tree implementation. Called by PD/MR and QP group VF binding paths.

Risks: long-term page pinning and memlock accounting are delicate; error path subtracts remaining `npages` rather than total pinned count after partial progress. All mappings are forced writable due to Intel IOMMU permission-change behavior. IOVA equals userspace VA, so overlapping registrations rely on interval diff correctness. `usnic_uiom_detach_dev_from_pd()` returns a value from a void function in this source, which is syntactically suspicious in strict builds.

Test signals: MR registration/release with overlapping and non-overlapping ranges, writable/dirty behavior, memlock limit enforcement, IOMMU attach/detach failure paths, DMA fault logging, interval unmap correctness, and stress with VF sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.h

Purpose: UIOM protection-domain, registration, and chunk data model plus public APIs.

Important APIs/types: defines access constants, maximum PD/MR/MR-size/page-size values, `struct usnic_uiom_dev`, `struct usnic_uiom_pd`, `struct usnic_uiom_reg`, `struct usnic_uiom_chunk`, and APIs for PD allocation, device attach/detach/listing, memory registration, and release.

Control flow: verbs PD allocation creates `usnic_uiom_pd`; QP group VF binding attaches VF devices; MR registration creates `usnic_uiom_reg`; MR deregistration releases it.

State and persistence: header shows the persistent IOMMU domain, interval tree, attached device list, VA/length/offset/writable fields, pinned-page chunk list, work item, and owning mm reference.

Dependencies and integration: includes Linux list/scatterlist and the usNIC interval tree header. Used by verbs, QP group, and UIOM implementation.

Risks: public constants advertise very large MR count/size limits; actual behavior is constrained by memlock, IOMMU, and pinned-page availability. The `work_struct` and `page_size` fields are present but unused in the mapped implementation, suggesting legacy design surface.

Test signals: compile coverage, PD attach/detach with multiple VFs, MR registration limits, and release of chunk lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/usnic_uiom.h -->
