# Research: subset-b-006003 Xen public interface headers

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/features.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/features.h

Purpose: defines the `XENFEAT_*` feature-bit numbers returned by `XENVER_get_features`. The file is a public ABI contract between Xen and guests; it has no runtime code, only stable indexes into the feature bitmap.

Important APIs/types/functions: `XENFEAT_writable_page_tables`, `XENFEAT_auto_translated_physmap`, `XENFEAT_hvm_callback_vector`, `XENFEAT_hvm_safe_pvclock`, `XENFEAT_dom0`, `XENFEAT_memory_op_vnode_supported`, `XENFEAT_ARM_SMCCC_supported`, `XENFEAT_linux_rsdp_unrestricted`, and the direct-map pair `XENFEAT_not_direct_mapped`/`XENFEAT_direct_mapped`. `XENFEAT_NR_SUBMAPS` is `1`, so consumers expect one feature submap here.

Control flow: callers issue the Xen version/features hypercall elsewhere, then test these numeric bits to select page-table update rules, callback delivery, PV clock safety, memory-op behavior, direct mapping assumptions, and architecture-specific boot handling. The deprecated grant identity mapping bit remains commented out and should not be consumed.

State and persistence: feature state is hypervisor-provided and effectively immutable for a running domain. The header itself persists no data.

Dependencies and integration points: consumed by guest arch setup, HVM/PVH boot, grant-table mapping, memory hotplug/placement, and ARM SMCCC paths. It intentionally has no includes beyond guards.

Risks: changing bit numbers breaks ABI. Incorrect fallback for older Xen releases can mis-handle direct-mapped vs translated domains. Feature checks must gate behavior that is not universally supported, especially HVM callback vectors and pvclock use.

Test signals: compile-time inclusion in guest drivers, boot tests on old and new Xen, and runtime probes showing expected feature-bit driven branches for PV, HVM/PVH, x86, and ARM guests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/grant_table.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/grant_table.h

Purpose: declares Xen grant table ABI structures, grant entry formats, grant operation command numbers, map/copy/transfer payloads, status codes, and mapping flags. It is the core cross-domain shared-page permission interface used by Xen paravirtual devices.

Important APIs/types/functions: `grant_ref_t`, `grant_handle_t`, `grant_status_t`, `struct grant_entry_v1`, `union grant_entry_v2`, and `struct grant_entry_header` model grant table storage. Operation payloads include `gnttab_map_grant_ref`, `gnttab_unmap_grant_ref`, `gnttab_setup_table`, `gnttab_transfer`, `gnttab_copy`, `gnttab_query_size`, `gnttab_unmap_and_replace`, `gnttab_set_version`, `gnttab_get_status_frames`, `gnttab_get_version`, `gnttab_swap_grant_ref`, and `gnttab_cache_flush`. Flags cover grant types (`GTF_permit_access`, `GTF_accept_transfer`, `GTF_transitive`), access bits (`GTF_readonly`, `GTF_reading`, `GTF_writing`), transfer bits, `GNTMAP_*`, `GNTCOPY_*`, and `GNTTAB_CACHE_*`.

Control flow: guests publish grants by writing `domid` and frame fields, issuing a write barrier, then setting valid flags. Consumers map grants via `GNTTABOP_map_grant_ref`, use returned handles, and release with `GNTTABOP_unmap_grant_ref`. Copies can use grant refs or MFNs, transfers require a receiving grant entry, and version 2 separates status frames for better synchronization.

State and persistence: grant entries are shared pages between Xen and a domain. Some entries are reserved for console and XenStore. Mappings persist until unmapped by handle; transfers have committed/completed handshakes that must be observed.

Dependencies and integration points: includes `xen/interface/xen.h` for domain IDs, PFNs, guest handles, and alignment types. Nearly every Xen IO protocol in this subset depends on grant refs for shared rings or data pages.

Risks: memory ordering and atomic invalidation are security-sensitive. Reusing active grants, unmapping by the wrong handle, leaving stale device mappings, or mishandling version 1 vs 2 frame widths can leak or corrupt cross-domain memory.

Test signals: grant map/unmap stress, concurrent grant invalidation tests, v1/v2 negotiation, copy and transfer error-path coverage, and leak checks showing no outstanding grant handles after frontend/backend disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/grant_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/dm_op.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/hvm/dm_op.h

Purpose: defines the generic buffer descriptor used by Xen HVM device-model operations. The file is deliberately small and supplies ABI layout only.

Important APIs/types/functions: `struct xen_dm_op_buf` contains a guest handle `h` and a `xen_ulong_t size`. `DEFINE_GUEST_HANDLE_STRUCT(xen_dm_op_buf)` exports the type for hypercall argument handling.

Control flow: higher-level HVM device-model hypercalls pass one or more `xen_dm_op_buf` descriptors to describe guest-visible buffers. This header does not define operation numbers; it only defines the payload wrapper.

State and persistence: there is no persistent local state. The buffer points to caller-owned memory for the duration of a device-model operation.

Dependencies and integration points: depends on Xen public handle macros and `xen_ulong_t` being available from already included Xen headers. Integrates with userspace or toolstack device models that marshal buffers into Xen hypercalls.

Risks: ABI width depends on `xen_ulong_t`, so callers must use the ABI selected for the guest/toolstack interface. Bad `size` values can truncate or overrun operation payloads if not validated by the caller and hypervisor.

Test signals: compile tests for both 32-bit and 64-bit ABI consumers, hypercall smoke tests using empty and non-empty buffers, and negative tests for invalid guest handles or sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/dm_op.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_op.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_op.h

Purpose: declares selected HVM operation command numbers and payloads for setting/getting domain parameters, notifying page-table teardown, querying memory type, and configuring x86 event-channel upcall vectors.

Important APIs/types/functions: `HVMOP_set_param`/`HVMOP_get_param` use `struct xen_hvm_param`. `HVMOP_pagetable_dying` uses `struct xen_hvm_pagetable_dying`. `enum hvmmem_type_t` defines `HVMMEM_ram_rw`, `HVMMEM_ram_ro`, and `HVMMEM_mmio_dm`; `HVMOP_get_mem_type` uses `struct xen_hvm_get_mem_type`. On x86, `HVMOP_set_evtchn_upcall_vector` uses `struct xen_hvm_evtchn_upcall_vector`.

Control flow: guests or toolstack components issue HVM hypercalls with these payloads. Parameters are indexed constants from `hvm/params.h`; page-table dying is a hint before destroying top-level page tables; memory type queries classify guest PFNs; x86 vector setup overrides the global callback path for a vCPU.

State and persistence: HVM params and event-channel vectors are domain/vCPU state held by Xen. The header stores none locally.

Dependencies and integration points: includes `xen/interface/xen.h` and is included by `hvm/params.h`. It integrates with HVM/PVH boot, event channels, memory type management, and PV driver page-table lifecycle hints.

Risks: command numbers are ABI. Architecture guards mean non-x86 consumers must not assume vector callback support. `domid` privilege rules are enforced outside this header but must be respected by callers.

Test signals: HVM param set/get round trips, x86 callback vector delivery tests gated by `XENFEAT_hvm_callback_vector`, page-table teardown paths under PV drivers, and memory-type queries for RAM/MMIO pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_op.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_vcpu.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_vcpu.h

Purpose: defines the architecture-specific initial register context used to launch an HVM/PVH vCPU in 32-bit or 64-bit x86 mode.

Important APIs/types/functions: `struct vcpu_hvm_x86_32` contains 32-bit general registers, control registers, EFER, and cached segment base/limit/access-right fields. `struct vcpu_hvm_x86_64` contains 64-bit general registers plus `cr0`, `cr3`, `cr4`, and `efer`. `struct vcpu_hvm_context` selects `VCPU_HVM_MODE_32B` or `VCPU_HVM_MODE_64B` and embeds the corresponding union.

Control flow: a domain builder or control tool prepares this context before vCPU startup. The mode selects which union member Xen consumes. For 64-bit mode, Xen derives segment caches suitable for long mode; compatibility-mode launches use the 32-bit layout.

State and persistence: the structure is a one-time or explicit vCPU state payload. After launch, CPU state lives inside Xen/vCPU execution state.

Dependencies and integration points: includes `../xen.h` for integer and Xen ABI types. Integrates with HVM/PVH domain builders, boot loaders, and vCPU creation paths.

Risks: segment access-right bit layout must match Intel SDM encoding. Incorrect EFER/CR combinations can fail launch or start in the wrong mode. Padding and union layout are ABI and must remain stable across compilers.

Test signals: domain-builder tests launching 32-bit, 64-bit, paging-enabled, and compatibility-mode guests; structure size/offset assertions; and boot smoke tests that validate initial RIP/EIP and control-register state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_vcpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/ioreq.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/hvm/ioreq.h

Purpose: defines the HVM I/O request record shared between Xen and a device model for PIO, MMIO copy, PCI config, time offset, and mapcache invalidation exits.

Important APIs/types/functions: request direction constants `IOREQ_READ` and `IOREQ_WRITE`; states `STATE_IOREQ_NONE`, `STATE_IOREQ_READY`, `STATE_IOREQ_INPROCESS`, `STATE_IORESP_READY`; request types `IOREQ_TYPE_PIO`, `IOREQ_TYPE_COPY`, `IOREQ_TYPE_PCI_CONFIG`, `IOREQ_TYPE_TIMEOFFSET`, and `IOREQ_TYPE_INVALIDATE`; and `struct ioreq`.

Control flow: Xen fills an `ioreq`, sets state ready, and notifies the device model through the `vp_eport` event channel. The device model decodes `addr`, `data`, `count`, `size`, `dir`, `type`, and `data_is_ptr`, services the emulated I/O, writes any response data, and advances state to response ready.

State and persistence: `state` is the synchronization point for each request. The record lives in shared I/O request pages configured by HVM params or newer DMOP paths.

Dependencies and integration points: consumed by QEMU or other Xen HVM device models, HVM param setup (`HVM_PARAM_IOREQ_PFN`, `HVM_PARAM_BUFIOREQ_PFN`), PCI config emulation, MMIO handlers, and mapcache invalidation.

Risks: bitfield layout and endian assumptions are ABI-sensitive. PCI config address encoding packs segment/bus/device/function/offset into `addr`; incorrect decoding targets the wrong device. `data_is_ptr` requires safe guest physical memory access.

Test signals: device-model integration tests for PIO/MMIO reads and writes, PCI config cycles, repeated-string `count` handling, event-channel notification, and state-machine races under concurrent vCPU exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/ioreq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/params.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/hvm/params.h

Purpose: declares the index space and encoded values for `HVMOP_set_param` and `HVMOP_get_param`.

Important APIs/types/functions: `HVM_PARAM_CALLBACK_IRQ` and callback encodings for GSI, PCI INTx, x86 vector, and ARM PPI; `HVM_PARAM_STORE_PFN`, `HVM_PARAM_STORE_EVTCHN`, `HVM_PARAM_PAE_ENABLED`, `HVM_PARAM_IOREQ_PFN`, `HVM_PARAM_BUFIOREQ_PFN`, `HVM_PARAM_TIMER_MODE` with `HVMPTM_*` modes, `HVM_PARAM_HPET_ENABLED`, `HVM_PARAM_IDENT_PT`, `HVM_PARAM_DM_DOMAIN`, `HVM_PARAM_ACPI_S_STATE`, `HVM_PARAM_VM86_TSS`, `HVM_PARAM_VPT_ALIGN`, `HVM_PARAM_CONSOLE_PFN`, `HVM_PARAM_CONSOLE_EVTCHN`, and `HVM_NR_PARAMS`.

Control flow: builders and guests use `xen_hvm_param` from `hvm_op.h` with these indexes to publish shared pages, event channels, callback routing, timer behavior, and device-model ownership.

State and persistence: parameter values are per-domain Xen state and persist until changed or the domain exits. The XenStore page, console page, and IOREQ pages referenced here point to other shared-memory protocols.

Dependencies and integration points: includes `xen/interface/hvm/hvm_op.h`. Integrates with event channels, XenStore, HVM console, virtual timers, HPET, device models, and boot setup.

Risks: callback value packing differs by architecture. `HVM_PARAM_CALLBACK_TYPE_VECTOR` must be gated by `XENFEAT_hvm_callback_vector`. Wrong PFN/event-channel pairing breaks console, XenStore, or device-model I/O.

Test signals: HVM boot with XenStore and console online, timer-mode behavior under vCPU preemption, event-channel interrupt delivery for each supported callback type, and parameter boundary tests up to `HVM_NR_PARAMS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/start_info.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/hvm/start_info.h

Purpose: defines the x86 HVM/PVH start-of-day memory layout passed to guests, including modules, command line, ACPI RSDP, and optional memory map.

Important APIs/types/functions: `XEN_HVM_START_MAGIC_VALUE`, `XEN_HVM_MEMMAP_TYPE_*`, `struct hvm_start_info`, `struct hvm_modlist_entry`, and `struct hvm_memmap_table_entry`.

Control flow: the domain builder places the start info structure in guest physical memory and passes its address in the boot register convention. The guest validates `magic`, checks `version`, reads modules and command line if their physical addresses are nonzero, and for version 1+ reads memory map entries when `memmap_entries` is nonzero.

State and persistence: start info is immutable boot data. Address fields with value zero mean absent. Xen on x86 attempts to place data below 4 GiB.

Dependencies and integration points: used by PVH/HVM guest entry code, boot loaders, ACPI discovery, initrd/module loading, and memory-map initialization. It ties to `XENFEAT_linux_rsdp_unrestricted` for Linux RSDP placement behavior.

Risks: layout is defined by the ASCII diagram and represented by C structs; padding changes would break boot. Version 0 guests must not read version 1 fields. All addresses and sizes are 64-bit little-endian values.

Test signals: PVH/HVM boot tests with no modules, multiple modules, absent/present RSDP, version 0 and 1 structures, and memory maps containing RAM, reserved, ACPI, NVS, unusable, disabled, and PMEM entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/hvm/start_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/9pfs.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/9pfs.h

Purpose: declares the Xen 9PFS transport ring interface for paravirtual 9P filesystem traffic.

Important APIs/types/functions: includes the generic ring helper and invokes `DEFINE_XEN_FLEX_RING_AND_INTF(xen_9pfs)`, producing `xen_9pfs_data_intf`, ring data helpers, read/write packet helpers, mask helpers, and queue accounting helpers.

Control flow: frontend and backend negotiate grant references and event channels outside this header, then exchange byte-stream packets over two flexible rings. The generated helpers handle wraparound copies and byte-queue calculations.

State and persistence: the generated data interface has producer/consumer indexes for in/out rings, a `ring_order`, and a flexible array of grant references backing the ring pages. State persists in shared memory until disconnect.

Dependencies and integration points: depends on `xen/interface/io/ring.h`, which itself requires grant table definitions for flexible rings. The comment points to the Xen 9pfs protocol document for message-level semantics.

Risks: the file only creates transport primitives; incorrect users can overrun the byte rings if they ignore `queued` and ring size. Include path style is `xen/interface/io/ring.h`, so build systems must expose Xen public include roots consistently.

Test signals: compile tests proving generated `xen_9pfs_*` symbols exist, frontend/backend data transfer with packets crossing ring wrap boundaries, and disconnect tests that revoke all grants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/9pfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/blkif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/blkif.h

Purpose: defines the Xen block frontend/backend ring ABI for virtual disks, including request operations, scatter/gather segment layout, indirect descriptors, response statuses, and virtual disk flags.

Important APIs/types/functions: `blkif_vdev_t`, `blkif_sector_t`, operations `BLKIF_OP_READ`, `BLKIF_OP_WRITE`, `BLKIF_OP_WRITE_BARRIER`, `BLKIF_OP_FLUSH_DISKCACHE`, `BLKIF_OP_DISCARD`, and `BLKIF_OP_INDIRECT`; `struct blkif_request_segment`, request variants `blkif_request_rw`, `blkif_request_discard`, `blkif_request_other`, `blkif_request_indirect`, `struct blkif_request`, `struct blkif_response`, `BLKIF_RSP_*`, `DEFINE_RING_TYPES(blkif, ...)`, and `VDISK_*`.

Control flow: the frontend publishes one or more shared rings and event channels in XenStore, optionally using multi-queue and multi-page ring keys. It enqueues read/write/discard/flush/indirect requests with grant refs to data pages. The backend maps grants, performs storage I/O, and returns a response with the echoed `id`, operation, and status.

State and persistence: request state lives in shared rings. `id` is frontend-private correlation state. Grant references for data and indirect pages remain valid until the backend consumes them. XenStore feature keys persist for the device lifetime.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with XenBus, event channels, backend storage drivers, discard/flush/barrier feature discovery, and Linux-style virtual disk numbering.

Risks: packed layout and `CONFIG_X86_32` padding preserve ABI offsets; changing them breaks mixed ABI pairs. Feature nodes are advisory; operations may still return `BLKIF_RSP_EOPNOTSUPP`. Indirect segment counts must be bounded by backend-advertised limits.

Test signals: block I/O read/write integrity, flush/discard/barrier fallback paths, multi-queue setup, indirect I/O above 11 segments, grant leak checks, and ABI size/offset assertions on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/blkif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/console.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/console.h

Purpose: defines the simple Xen console shared-page ring used for guest console input and output.

Important APIs/types/functions: `XENCONS_RING_IDX`, `MASK_XENCONS_IDX(idx, ring)`, `struct xencons_interface`, and connection flags `XENCONSOLE_DISCONNECTED`/`XENCONSOLE_CONNECTED`.

Control flow: producer/consumer indexes track fixed-size byte arrays: backend-to-frontend input in `in[1024]` and frontend-to-backend output in `out[2048]`. Writers place bytes in the ring, advance producer indexes, and notify through the associated event channel configured elsewhere.

State and persistence: the shared page stores in/out buffers, producer/consumer indexes, and a connection flag. It persists as the guest console page for the domain lifetime or until device teardown.

Dependencies and integration points: tied to reserved grant table entry `GNTTAB_RESERVED_CONSOLE` and HVM console params (`HVM_PARAM_CONSOLE_PFN`, `HVM_PARAM_CONSOLE_EVTCHN`). Used by early console, XenBus console backend, and debug paths.

Risks: the mask macro assumes power-of-two ring array sizes. Consumers must avoid overwriting unread bytes and must honor the connection flag, which starts disconnected. No memory barriers are defined here, so implementations must supply appropriate ordering around index updates.

Test signals: boot console output, backend connect/disconnect transitions, input injection, wraparound writes, and stress tests ensuring producer/consumer indexes do not lose bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/console.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/displif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/displif.h

Purpose: defines the Xen paravirtual display protocol, a richer display ABI than `fbif` with multiple connectors, dynamically created display buffers, framebuffer attachment, page flips, EDID retrieval, and asynchronous events.

Important APIs/types/functions: protocol version constants, XenStore field names, operations `XENDISPL_OP_DBUF_CREATE`, `DBUF_DESTROY`, `FB_ATTACH`, `FB_DETACH`, `SET_CONFIG`, `PG_FLIP`, and `GET_EDID`; event `XENDISPL_EVT_PG_FLIP`; request structs such as `xendispl_dbuf_create_req`, `xendispl_page_directory`, `xendispl_fb_attach_req`, `xendispl_set_config_req`, `xendispl_get_edid_req`; `xendispl_req`, `xendispl_resp`, `xendispl_evt`, and `struct xendispl_event_page`.

Control flow: XenBus negotiates backend versions, frontend selected version, connector resolution, request rings, event rings, and backend allocation. Requests go through per-connector control rings, with non-connector-specific operations using connector 0. Backends respond with status and may send page-flip completion events through the separate event page.

State and persistence: display buffers and framebuffers are identified by guest-unique cookies and persist until explicit destroy/detach. Shared buffer page directories hold grant refs. Connector configuration and transport keys persist in XenStore.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with XenBus state transitions, grant sharing, event channels, DRM/KMS style frontends, and optional EDID consumers.

Risks: cookie value zero is invalid and duplicate cookies are protocol errors. Buffer size determines page directory length; mismatches can expose invalid grants. Recovery flow requires frontends to block new clients while reconfiguring after backend failure.

Test signals: multi-connector setup, buffer create/destroy with frontend and backend allocation, framebuffer attach/detach, config reset/set bounds checks, page-flip event delivery, EDID size handling, and protocol version 1 vs 2 behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/displif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/fbif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/fbif.h

Purpose: defines the older Xen virtual framebuffer shared-page protocol for simple display updates and resize notifications.

Important APIs/types/functions: outbound event types `XENFB_TYPE_UPDATE` and `XENFB_TYPE_RESIZE`; `struct xenfb_update`, `struct xenfb_resize`, `union xenfb_out_event`, `union xenfb_in_event`; ring constants and helpers `XENFB_IN_RING_*`, `XENFB_OUT_RING_*`; and `struct xenfb_page` with framebuffer metadata and page directory `pd[256]`.

Control flow: frontend-to-backend out events report updated rectangles or resize changes when negotiated by XenStore features. Backends may define future inbound events, but none are currently defined and frontends should ignore unknown ones.

State and persistence: `xenfb_page` stores ring indexes, visible framebuffer geometry, memory length, depth, and a page directory mapping framebuffer pages. The shared page and backing framebuffer grants persist while the device is connected.

Dependencies and integration points: integrates with Xen virtual keyboard/mouse through shared default resolution definitions under `__KERNEL__`, XenBus feature keys (`feature-update`, `request-update`, `feature-resize`), grant-table mapped framebuffer pages, and event-channel notifications.

Risks: `unsigned long pd[256]` has ABI implications across 32-bit/64-bit domains. The protocol is less expressive than `displif`; using it for modern display workflows can limit multi-output and buffer management. Out events are errors unless requested by the backend.

Test signals: framebuffer update rectangle delivery, resize negotiation, page directory mapping at 32-bit and 64-bit ABI widths, default resolution users, and backend tolerance for unknown inbound event types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/fbif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/kbdif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/kbdif.h

Purpose: defines the Xen virtual keyboard, pointer, and multi-touch shared-page protocol plus XenStore feature negotiation keys.

Important APIs/types/functions: event codes `XENKBD_TYPE_MOTION`, `KEY`, `POS`, and `MTOUCH`; multi-touch subcodes `XENKBD_MT_EV_*`; XenStore field macros for feature and request nodes; event structs `xenkbd_motion`, `xenkbd_key`, `xenkbd_position`, `xenkbd_mtouch`; `union xenkbd_in_event`, `union xenkbd_out_event`; ring helpers; and `struct xenkbd_page`.

Control flow: the backend advertises supported keyboard, pointer, absolute, raw, and multi-touch capabilities. The frontend requests desired features and grants a shared page. Backend-to-frontend events report relative motion, key/button state, absolute position, or multi-touch contact lifecycle; no frontend-to-backend events are currently defined.

State and persistence: shared page state is limited to in/out producer/consumer indexes; device capabilities and dimensions persist in XenStore. Multi-touch contact IDs are reused after UP events.

Dependencies and integration points: integrates with XenBus, event channels, Linux input key codes, framebuffer/display sizing, and guest input stacks. Ring layouts are fixed 40-octet event packets in fixed offsets within one page.

Risks: unknown backend-to-frontend events must be ignored, while unknown frontend-to-backend events are backend errors. Absolute/raw coordinate scaling depends on negotiated dimensions. Reserved fields must be zero to maintain forward compatibility.

Test signals: key press/release, relative and absolute pointer movement, wheel events, raw pointer range checks, multi-touch down/move/shape/orientation/sync/up sequences, and feature negotiation with disabled keyboard or pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/kbdif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/netif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/netif.h

Purpose: defines the Xen virtual network frontend/backend ABI: TX/RX ring records, offload and extra-info descriptors, multi-queue negotiation, control ring messages for hashing, and status codes.

Important APIs/types/functions: `XEN_NETIF_NR_SLOTS_MIN`, `XEN_NETIF_MAX_XDP_HEADROOM`, hash flags/algorithms, optional `xen_netif_toeplitz_hash` helper when `XEN_NETIF_DEFINE_TOEPLITZ` is set, control request/response structs and `DEFINE_RING_TYPES(xen_netif_ctrl, ...)`, TX/RX structs `xen_netif_tx_request`, `xen_netif_tx_response`, `xen_netif_rx_request`, `xen_netif_rx_response`, `xen_netif_extra_info`, `DEFINE_RING_TYPES(xen_netif_tx, ...)`, `DEFINE_RING_TYPES(xen_netif_rx, ...)`, and `XEN_NETIF_RSP_*`.

Control flow: frontends grant TX/RX rings and optional control rings through XenStore. TX packets flow frontend to backend as one or more grant-backed fragments plus optional extra descriptors. RX buffers are posted by the frontend and completed by the backend. Control messages configure hash algorithm, hash flags, key, and queue mapping.

State and persistence: queue topology, split event channels, checksum/GSO/multicast/XDP/hash capabilities, and control-ring grants persist in XenStore. In-flight packet state lives in rings and grant references.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with netfront/netback, event channels, checksum offload, GSO, multicast filtering, XDP headroom, RSS-like queue steering, and legacy Linux slot assumptions.

Risks: TX and RX multi-fragment packet size semantics differ. Extra-info overlays normal ring slots, and legacy Linux RX assumes response slot matching. Feature negotiation defaults are asymmetric for IPv4 and IPv6 checksum offload. Hash grants must remain valid until responses are processed.

Test signals: TX/RX packet integrity, checksum offload matrix, GSO IPv4/IPv6, multicast filter add/delete, split event channels, multi-queue steering, hash control ring operations, XDP headroom, and malformed ring overflow detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/netif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/pciif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/pciif.h

Purpose: defines shared structures and constants for Xen PCI frontend/backend configuration-space access, MSI/MSI-X control, and PCIe AER handling.

Important APIs/types/functions: `XEN_PCI_MAGIC`, flags `XEN_PCIF_active`, `XEN_PCIB_AERHANDLER`, `XEN_PCIB_active`; commands `XEN_PCI_OP_conf_read`, `conf_write`, `enable_msi`, `disable_msi`, `enable_msix`, `disable_msix`, and AER operations; errors `XEN_PCI_ERR_*`; `SH_INFO_MAX_VEC`; `struct xen_msix_entry`, `struct xen_pci_op`, `struct xen_pcie_aer_op`, and `struct xen_pci_sharedinfo`.

Control flow: frontend writes a command into shared info, identifying PCI segment, bus, devfn, config offset/size, value, and optional MSI-X vectors. Backend performs the privileged PCI operation and writes `err` and output values. AER operations use the separate `aer_op` record.

State and persistence: `xen_pci_sharedinfo` persists as the command mailbox with active flags and operation payloads. MSI-X entry arrays persist only for an operation.

Dependencies and integration points: used by Xen pcifront/pciback drivers, PCI config space, MSI/MSI-X setup, PCIe AER recovery, and XenBus versioning via `XEN_PCI_MAGIC`.

Risks: single shared operation slots require external serialization. `SH_INFO_MAX_VEC` bounds MSI-X vectors at 128. Incorrect domain/bus/devfn or config offsets can target wrong hardware; backend permission checks are critical.

Test signals: config read/write round trips, denied access checks, MSI and MSI-X enable/disable with vector counts near limits, AER error/resume/slot reset paths, and protocol magic compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/pciif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/protocols.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/protocols.h

Purpose: declares string constants naming Xen IO protocol ABI layouts and selects a native ABI string for the compiling architecture.

Important APIs/types/functions: `XEN_IO_PROTO_ABI_X86_32`, `XEN_IO_PROTO_ABI_X86_64`, `XEN_IO_PROTO_ABI_POWERPC64`, `XEN_IO_PROTO_ABI_ARM`, and architecture-selected `XEN_IO_PROTO_ABI_NATIVE`.

Control flow: frontend and backend protocol setup code publishes or reads ABI strings, often in XenStore, to know how ring request/response structures are laid out. Preprocessor conditionals select the native string at compile time.

State and persistence: no runtime state is stored here. ABI strings may persist in XenStore device nodes for the connection lifetime.

Dependencies and integration points: included by protocols such as pvUSB that expose a `protocol` XenStore node. It integrates with build architecture macros and mixed frontend/backend ABI negotiation.

Risks: unsupported architectures hit `#error arch fixup needed here`. Native ABI is not always the peer ABI; backends must honor the negotiated string rather than assuming host native layout. String changes are ABI-breaking.

Test signals: compile tests for each supported architecture macro, XenStore protocol node validation, and cross-ABI frontend/backend tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/protocols.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/pvcalls.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/pvcalls.h

Purpose: defines the Xen PV calls socket-like protocol for forwarding socket operations between frontend and backend.

Important APIs/types/functions: `XENBUS_FUNCTIONS_CALLS`, `struct pvcalls_data_intf`, `DEFINE_XEN_FLEX_RING(pvcalls)`, command codes `PVCALLS_SOCKET`, `CONNECT`, `RELEASE`, `BIND`, `LISTEN`, `ACCEPT`, `POLL`, and request/response structs `xen_pvcalls_request` and `xen_pvcalls_response` with `DEFINE_RING_TYPES(xen_pvcalls, ...)`.

Control flow: command requests are placed on a balanced ring and responses echo `req_id` and `cmd` with a return code. Connect and accept can pass grant refs and event channels for per-connection data rings described by `pvcalls_data_intf`, which has separate in/out producer-consumer indexes and error fields.

State and persistence: socket IDs are 64-bit protocol handles. Data rings store stream state, errors, ring order, and grants until the socket is released.

Dependencies and integration points: includes `<linux/net.h>`, generic Xen ring helpers, and grant table types. Integrates with XenBus function discovery, event channels, guest socket APIs, and backend network stack forwarding.

Risks: address storage is fixed at 28 bytes and must match supported socket address families. Dummy union members force cross-architecture size stability; modifying them can break ABI. Data-ring error fields require careful synchronization with producer/consumer indexes.

Test signals: socket/bind/listen/connect/accept/release flows, poll behavior, stream data wraparound over flexible rings, error propagation, and structure size checks across 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/pvcalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/ring.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/ring.h

Purpose: provides the generic shared-memory ring macros used by Xen frontend/backend protocols, plus flexible byte-ring helpers.

Important APIs/types/functions: `RING_IDX`, power-of-two sizing macros, `DEFINE_RING_TYPES`, initialization macros `SHARED_RING_INIT`, `FRONT_RING_INIT`, `BACK_RING_INIT`, accessors `RING_GET_REQUEST`, `RING_GET_RESPONSE`, copy helpers, overflow checks, push/final-check notification macros, `XEN_FLEX_RING_SIZE`, `DEFINE_XEN_FLEX_RING`, and `DEFINE_XEN_FLEX_RING_AND_INTF`.

Control flow: frontends initialize shared rings, enqueue requests, use `RING_PUSH_REQUESTS*`, and consume responses. Backends attach, consume requests, enqueue responses, and use `RING_PUSH_RESPONSES*`. Notification macros combine producer publication with event-index checks. Flexible rings operate as byte queues with wraparound copy helpers.

State and persistence: generated shared rings hold producer indexes, event threshold indexes, padding, and entries. Front/back private structs hold local producer/consumer cursors and ring size. Flexible ring interfaces hold in/out indexes, ring order, and grant refs.

Dependencies and integration points: includes `grant_table.h` and expects integer types plus memory-barrier macros such as `virt_wmb()` and `virt_mb()` from the including environment. It underpins block, net, display, sound, USB, PVCALLS, and 9PFS protocols.

Risks: macros perform no full flow control or locking. Callers must respect `RING_SIZE()-1` outstanding request assumptions, memory barriers, and overflow checks. GNU statement expressions and `typeof` constrain compiler compatibility.

Test signals: unit tests for ring size calculation, wraparound, notification hold-off, overflow detection, local-copy semantics, flexible-ring read/write across boundaries, and protocol integration stress under concurrent frontend/backend activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/ring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/sndif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/sndif.h

Purpose: defines the Xen paravirtual sound protocol for virtual sound cards, PCM devices, streams, command rings, shared audio buffers, and asynchronous position events.

Important APIs/types/functions: `XENSND_PROTOCOL_VERSION`, PCM format constants and string names, XenStore field names, operations `XENSND_OP_OPEN`, `CLOSE`, `READ`, `WRITE`, `SET_VOLUME`, `GET_VOLUME`, `MUTE`, `UNMUTE`, `TRIGGER`, `HW_PARAM_QUERY`, trigger codes, event `XENSND_EVT_CUR_POS`, request structs `xensnd_open_req`, `xensnd_rw_req`, `xensnd_trigger_req`, `xensnd_query_hw_param`, `xensnd_req`, `xensnd_resp`, `xensnd_evt`, `xensnd_page_directory`, and `xensnd_event_page`.

Control flow: XenBus configures card/device/stream hierarchy, sample rates/formats, channels, buffer size, request ring, and event ring. Frontend opens a stream with PCM parameters and a grant-backed buffer directory, issues read/write/control requests by offset/length into that buffer, triggers start/stop/pause/resume, and receives responses plus optional current-position events.

State and persistence: opened stream state includes selected PCM configuration, shared buffer grants, period size, volume/mute data in the shared buffer, and event position state. XenStore configuration persists for the virtual sound device lifetime.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with XenBus, event channels, guest ALSA-like PCM layers, backend mixers/devices, and grant-table buffer sharing.

Risks: lower-layer stream capabilities must be subsets of card/device capabilities. Offset/length requests can address audio or control data in the same buffer, so validation is essential. Recovery from backend failure may require frontend reconfiguration while existing clients drain.

Test signals: stream open parameter validation, read/write playback/capture, trigger transitions, volume/mute round trips, hardware-parameter narrowing, period event delivery, multi-device stream indexing, and grant cleanup on close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/sndif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/tpmif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/tpmif.h

Purpose: defines version 2 Xen virtual TPM shared-page protocol state and packet layout.

Important APIs/types/functions: `enum vtpm_shared_page_state` with `VTPM_STATE_IDLE`, `SUBMIT`, `FINISH`, and `CANCEL`; `struct vtpm_shared_page` with `length`, `state`, `locality`, `nr_extra_pages`, and flexible `extra_pages` grant IDs.

Control flow: XenBus open requires frontend to publish `ring-ref`, `event-channel`, and `feature-protocol-v2`, then both sides transition to connected after backend maps the grant and verifies protocol support. Frontend submits by filling length/locality/extra pages and changing state to `SUBMIT`; backend processes and moves to `FINISH` or `IDLE`. Frontend can request cancellation with `CANCEL`.

State and persistence: the shared page stores the current request/response lifecycle and optional extra page grants for long packets. Backend should only write `IDLE` or `FINISH`; frontend should only write `SUBMIT` or `CANCEL`.

Dependencies and integration points: integrates with XenBus state machine, event channels, grant table pages, and guest TPM/TIS or vTPM drivers.

Risks: state ownership is strict; either side writing the wrong state can race or lose requests. Long-packet `extra_pages` length is controlled by `nr_extra_pages`, so bounds validation is required. The close sequence must unmap grants and events before backend returns to InitWait.

Test signals: vTPM open/close state transitions, request/response exchange, cancel behavior, long request with extra pages, locality propagation, and invalid state transition handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/tpmif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/usbif.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/io/usbif.h

Purpose: defines the Xen pvUSB split-driver ABI, including USB host connector XenStore setup, URB request/response rings, connection event rings, pipe bitfield helpers, speeds, versions, and status codes.

Important APIs/types/functions: `enum xenusb_spec_version`, pipe masks and helpers such as `xenusb_pipeportnum`, `xenusb_pipeunlink`, `xenusb_pipein`, `xenusb_pipedevice`, `xenusb_pipeendpoint`, and `xenusb_pipetype`; constants `XENUSB_MAX_SEGMENTS_PER_REQUEST`, `XENUSB_MAX_PORTNR`, `XENUSB_RING_SIZE`; `struct xenusb_request_segment`, `xenusb_urb_request`, `xenusb_urb_response`, `xenusb_conn_request`, `xenusb_conn_response`; `DEFINE_RING_TYPES(xenusb_urb, ...)` and `DEFINE_RING_TYPES(xenusb_conn, ...)`.

Control flow: frontend publishes `event-channel`, `urb-ring-ref`, `conn-ring-ref`, and optional ABI protocol string. Backend sends plug/unplug events on the connection ring in response to dummy requests. Frontend submits URBs on the URB ring with pipe encoding, transfer flags, type-specific data, and up to 16 grant-backed buffer segments; backend returns status, actual length, start frame, and ISO error count.

State and persistence: ring state persists per virtual USB connector. Backend private XenStore nodes describe number of ports, USB version, and physical port mapping. In-flight URBs are correlated by request `id`; unlink requests cancel earlier IDs.

Dependencies and integration points: includes `ring.h` and `grant_table.h`; integrates with XenStore ABI strings from `protocols.h`, event channels, host USB backends, and guest USB core URB handling.

Risks: pipe bitfields must be encoded exactly; wrong direction, endpoint, or type corrupts USB semantics. Maximum 31 ports and 16 segments are hard ABI limits. Unlink races and ISO frame descriptors require careful backend validation.

Test signals: plug/unplug events, control/interrupt/bulk/iso URB submission, short-transfer flag behavior, unlink cancellation, status mapping for stalls/nodev/shutdown, ring size assertions, and segment-boundary transfer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/io/usbif.h -->
