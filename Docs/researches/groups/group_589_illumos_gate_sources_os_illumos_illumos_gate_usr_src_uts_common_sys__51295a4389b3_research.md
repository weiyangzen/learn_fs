# Group Research: group_589_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__51295a4389b3

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_qp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_qp.h

## Purpose

Defines the Tavor InfiniBand adapter driver's Queue Pair resource constants, QP software handle layout, QPN tracking entries, allocation options, and cross-file QP management prototypes.

## Main Definitions

- QP sizing/configuration defaults for 128 MB and 256 MB adapter DDR profiles, minimum profile values, and minimum QP depth.
- `TAVOR_QP_IS_SYNC_REQ()` decides whether work queue memory needs `ddi_dma_sync()` based on config profile and queue location.
- QPC, extended QPC, RDB sizing, RDMA read/atomic limits, maximum WQE SGL count, QP number mask, schedule queue mapping, AckReq frequency, and max message size constants.
- `TAVOR_QP_WQ_ALIGN()` computes combined work-queue alignment to avoid hardware 32-bit boundary restrictions.
- `TAVOR_QP_TYPE_VALID()` maps IBTF transport service types to Tavor QP service types.
- `tavor_qp_wq_type_t` and WQE header overhead constants used to calculate WQE sizes and SGL capacity.
- `tavor_qp_info_t`: internal input/output bundle for normal and special QP allocation.
- `tavor_qpn_entry_t`: AVL-tracked QPN allocation/refcount entry, with release/free flags.
- `struct tavor_sw_qp_s`: the main QP handle, containing lock-protected state, PD/MR/CQ handles, SQ/RQ buffers and WRID headers, QPC/RDB resources, SRQ association, multicast refcount, saved MTU/static rate, user mapping details, and embedded hardware QPC shadow.
- `tavor_qp_options_t`: currently controls work queue memory placement.
- Prototypes for QP alloc/free/query, special QP allocation, QPN AVL management, QP lookup by number, QP modify, and reset transition.

## Integration Notes

This header is consumed by the Tavor CI/IBTF implementation and by lower-level work request and completion paths. It depends on common Tavor typedefs, IBTF allocation/query/modify types, `tavor_qalloc_info_s`, `tavor_hw_qpc_s`, and related resource handles.

`struct tavor_sw_qp_s` is the central software object tying together hardware context, queue memory, protection domain, CQs, optional SRQ, and completion WRID tracking.

## Risks and Gotchas

- QP memory alignment and sync behavior are hardware-sensitive; changing sizing or queue-location logic can break DMA correctness.
- The SQ/RQ fields have explicit lock annotations; posting, completion, reset, and free paths must preserve those lock boundaries.
- QPNs are 24-bit and additionally tracked in an AVL tree with refcounts; release semantics differ for normal release vs free-only paths.
- Special QPs carry port and P_Key state in the same handle structure as ordinary QPs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_qp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_rsrc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_rsrc.h

## Purpose

Defines the Tavor resource manager interface: sleep policy, resource pool names, resource type enumeration, initialization cleanup levels, per-resource initialization descriptors, resource pool metadata, mailbox-private metadata, resource allocation handles, and public alloc/free/init/fini prototypes.

## Main Definitions

- `TAVOR_SLEEP`, `TAVOR_NOSLEEP`, and `TAVOR_SLEEPFLAG_FOR_CONTEXT()` map interrupt/panic context to non-sleeping allocation behavior.
- Named kmem caches and vmem arenas for software handles, DDR tables, mailbox pools, UAR space, and PD handles.
- `TAVOR_RSRC_NAME()` appends the driver instance to resource names; `TAVOR_RSRC_NAME_MAXLEN` bounds names.
- `tavor_rsrc_type_t`: all managed resources, including QPC, CQC, SRQC, EQC, EQPC, RDB, MCG, MPT, MTT, UAR scratch, UDAV, mailboxes, software handles, refcounts, UAR pages, and interrupt mailboxes.
- `tavor_rsrc_cleanup_level_t`: staged cleanup markers for attach/detach rollback.
- `tavor_rsrc_mbox_info_t`, `tavor_rsrc_hw_entry_info_t`, and `tavor_rsrc_sw_hdl_info_t`: initialization descriptors for mailbox, hardware-table, and software-handle resources.
- `struct tavor_rsrc_pool_info_s`: pool metadata for location, size, alignment, quantum, shift, start/DDR offset, vmem arena, soft state, and private data.
- `tavor_rsrc_priv_mbox_t`: DMA/access metadata needed to bind mailbox resources.
- `struct tavor_rsrc_s`: allocation result handle with type, address, length, index, access handle, and DMA handle.
- Prototypes for `tavor_rsrc_alloc()`, `tavor_rsrc_free()`, two-phase initialization, and cleanup.

## Integration Notes

This header underpins almost every Tavor object allocator: QPs, CQs, SRQs, EQs, memory translation tables, mailboxes, and user access regions. Consumers receive `tavor_rsrc_t` objects whose fields are only meaningful for specific resource types.

## Risks and Gotchas

- `TAVOR_SLEEPFLAG_FOR_CONTEXT()` must stay compatible with command-layer sleep flags referenced in comments.
- `TAVOR_NUM_RESOURCES` and `TAVOR_RSRC_CLEANUP_ALL` are sentinel values; new enum entries must be inserted before them.
- Resource locations distinguish DDR, system memory, and UAR memory. Misclassifying a resource affects DMA mapping, synchronization, and access-handle expectations.
- `TAVOR_RSRC_NAME()` assumes a `state` variable is in scope.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_rsrc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_srq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_srq.h

## Purpose

Defines Shared Receive Queue sizing, sync policy, SRQ state constants, the SRQ software handle, SRQ allocation options, and the Tavor SRQ public interface.

## Main Definitions

- Default SRQ count and size shifts for 128 MB and 256 MB profiles, minimum SRQ profile values, and minimum SRQ depth.
- `TAVOR_SRQ_MAX_SGL` caps SRQ SGLs at 15 due to documented firmware problems with larger SRQ WQEs.
- `TAVOR_SRQ_IS_SYNC_REQ()` mirrors QP sync policy for SRQ WQE memory based on config profile and queue placement.
- SRQC size constants and SRQ hardware/software ownership states.
- `struct tavor_sw_srq_s`: SRQ handle with lock, PD/MR handles, SRQ number, limit, sync flag, refcount, state, user mapping details, real sizes, context/handle resources, WQ buffer metadata, WRID lock/list, zero-based descriptor offset, and queue allocation info.
- Lock annotations distinguish read-only fields, data readable without lock, and `srq_lock`-protected mutable queue and size state.
- `tavor_srq_info_t`: allocation input/output bundle.
- `tavor_srq_options_t`: currently controls normal vs adapter DDR work queue allocation.
- Prototypes for SRQ allocate/free/modify/post, refcount inc/dec, and lookup by SRQ number.

## Integration Notes

SRQs are shared by QPs through `tavor_sw_qp_s::qp_srqhdl` and are posted through the work request path. The WRID and queue-lock types come from `tavor_wr.h`.

## Risks and Gotchas

- Firmware SGL limitations are encoded as a driver policy constant; increasing it can expose known hardware/firmware failure modes.
- SRQ WQE index/address macros live in `tavor_wr.h`, so SRQ buffer layout must remain compatible there.
- Refcounting is explicit because QPs can attach to a shared SRQ; free paths must coordinate with QP ownership.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_srq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_typedef.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_typedef.h

## Purpose

Provides forward typedefs for common Tavor driver structures and opaque handle aliases, allowing other Tavor headers to refer to shared objects before their full definitions are included.

## Main Definitions

- Forward typedefs for driver-global and resource infrastructure: `tavor_state_t`, agent lists, queue allocation info, resource pools, resources, WRID entries/lists, work queue headers, and work queue locks.
- Forward typedefs for hardware command/context/layout structures: HCR, query results, init/query HCA/IB structures, MPT/MTT, EQ/CQ/SRQ/UAR/CQE/QPC/MCG objects, address paths, UD address vectors, performance counters, and WQE segments.
- Opaque handle typedefs:
  - `tavor_mrhdl_t` and `tavor_mwhdl_t`
  - `tavor_pdhdl_t`
  - `tavor_eqhdl_t`
  - `tavor_cqhdl_t`
  - `tavor_srqhdl_t`
  - `tavor_ahhdl_t`
  - `tavor_qphdl_t`
  - `tavor_mcghdl_t`

## Integration Notes

The file is intended to be included early through `tavor.h`, before the rest of the Tavor driver headers. It prevents include cycles among hardware layout, resource, QP, CQ, MR, AH, MCG, and WR processing headers.

## Risks and Gotchas

- These are only forward declarations. Any file dereferencing the pointed-to handles must include the corresponding full-definition header.
- Opaque handle aliases all use pointer-to-struct forms; mixing handles is type-safe only to the extent the compiler sees distinct pointed-to struct tags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_typedef.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_wr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_wr.h

## Purpose

Defines work request and WRID tracking support for Tavor QP/SRQ posting and completion processing, including WQE address macros, special-QP MAD helpers, WRID list/work queue structures, lock ordering, and posting/WRID function prototypes.

## Main Definitions

- `TAVOR_QP_WQEADDRSZ()` packs a WQE address and size into the CQE-compatible WRID tracking value.
- `TAVOR_QP_SQ_ENTRY()`, `TAVOR_QP_RQ_ENTRY()`, and `TAVOR_SRQ_WQ_ENTRY()` compute WQE addresses from queue base and tail index.
- `TAVOR_SRQ_WQE_INDEX()` and `TAVOR_SRQ_WQE_ADDR()` convert between SRQ WQE address and index.
- Directed-route MAD helper macros extract management class, hop pointer, and hop count from fragmented buffers and adjust hop pointer for management class `0x81`.
- `struct tavor_wrid_entry_s`: stores application WRID, packed WQE address/size, and signaled/doorbelled flags.
- `tavor_sw_wqe_dbinfo_t`: returns doorbell opcode/fence information from WQE builders.
- `struct tavor_wq_lock_s`: refcounted mutex shared by work queues and SRQs for WRID list manipulation.
- `struct tavor_wrid_list_hdr_s`: WRID queue/list state, including active/retired lists and SRQ-specific buffer metadata.
- `struct tavor_workq_hdr_s`: CQ-associated work queue tracking header keyed by QPN and queue type.
- Lock annotations define ordering: CQ lock, CQ WRID header lock, then WQ lock.
- Queue type constants for receive, send, and SRQ.
- Prototypes for posting send/receive/SRQ WRs and for WRID reset handling, add/get operations, WRID list allocation, SRQ WRID init, CQ reap/force reap, WQ lock refcounts, and SRQ CQE matching.

## Integration Notes

This header links the QP/SRQ posting path to completion processing. Work queue headers live with CQs rather than QPs so completions can still be resolved after a QP is reset or destroyed.

## Risks and Gotchas

- WRID lists can outlive the active QP incarnation; reset and reap paths must avoid mixing old and new queue state.
- Special-QP directed-route MAD macros assume exact packet offsets.
- The packed address/size value depends on `TAVOR_WQE_NDS_MASK`, defined elsewhere, and must match CQE hardware encoding.
- Lock order is explicitly documented and should not be inverted in posting/completion/reset code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_wr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt.h

## Purpose

Defines the kernel-side state and resource objects for the `daplt` uDAPL kernel agent: HCA inventory, per-instance state, generic hash tables, IA/PD/EVD/EP/MR/MW/SP/CNO/SRQ resources, connection event bookkeeping, shared MR tracking, and a resource table.

## Main Definitions

- Driver version, taskq size, and attached/detached status constants.
- `daplka_hca_t`: HCA GUID/handle/attributes/ports, resource counters, refcount, and linked-list membership.
- `daplka_t`: per-device instance state with mutex, devinfo, IBT client handle, HCA list, and status.
- Generic hash table types with table and key locks plus optional free/lookup callbacks.
- `daplka_resource_t`: common header for all resources, including type, resource number, refcount, charge flag, and free callback.
- Hash table sizes for EP, MR, MW, PD, SP, EVD, global SP, timers, CNO, and SRQ.
- IA state machine for races between MW allocation and MR cleanup callbacks.
- Resource structs for:
  - IA with per-IA resource hash tables and async EVD list.
  - PD with HCA and IBT PD handle.
  - EVD with CQ handle, event queues, waiters, cookie, and optional CNO.
  - SRQ with PD/HCA association and real size.
  - EP with channel handle, EVDs, PD/SRQ, state, timer, passive cookie, private data, and GIDs.
  - MR/MW with IBT handles and locking.
  - SP with service/bind handles and connection backlog.
  - CNO with wait condition and EVD cookie.
  - Shared MR AVL entries.
- Resource table block/root structures for minor-resource mapping.

## Integration Notes

This is the private kernel representation behind the ioctl ABI in `daplt_if.h`. It maps user-visible hash keys and cookies to IBT resources and tracks ownership/refcounts inside the kernel driver.

## Risks and Gotchas

- Many objects are documented as scheme-protected rather than solely lock-protected; correctness depends on higher-level DAPL lifecycle rules.
- IA MW freeze states handle a specific race between MR cleanup and MW allocation.
- Passive connection cookies encode timestamp plus backlog index; consumers must validate backlog state, not just decode the index.
- EVD event queues mix asynchronous, connection-request, and connection events under one lock.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt_if.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt_if.h

## Purpose

Defines the user/kernel ioctl ABI for the `daplt` uDAPL kernel agent, including command numbers, driver naming, packed data structures, connection private data format, HCA-specific opaque return buffers, and ioctl payloads for IA, EP, EVD, MR, MW, PD, SP, CNO, and SRQ operations.

## Main Definitions

- `DAPL_IF_VERSION` and ioctl command namespaces by object type.
- Commands for IA creation/query, EP create/free/connect/modify/disconnect/reinit, EVD create/free/poll/wakeup/CQ resize/CNO modify, MR register/deregister/sync, MW alloc/free, CNO alloc/free/wait, PD alloc/free, service register/deregister, CR accept/reject/handoff, and SRQ create/free/resize.
- Driver name, minor name, default path, and event poll limits.
- `DAT_EVD_FLAGS` fallback definitions when DAT headers are not present.
- `#pragma pack(4)` around ioctl structures when 64-bit kernel long-long alignment differs from 32-bit ABI alignment.
- `dapl_ia_addr_t`, `DAPL_HELLO_MSG`, and `DAPL_PRIVATE`: DAPL private data/hello message format carrying IPv4, IPv6, or SA-address data.
- Opaque HCA-specific output arrays for CQ, QP, and SRQ creation/resize.
- EP ioctl structs for create, modify, connect, disconnect, reinit, and free.
- EVD event-family definitions and event return structures for async and CM events, plus 64-bit and 32-bit event-poll payloads.
- MR registration variants: direct, shared, LMR-based, deregister, and RDMA sync vectors.
- IA creation/query/enum structures and a stable copy of selected HCA attributes.
- PD, MW, SP, CR, CNO, and SRQ ioctl payload definitions.

## Integration Notes

This header is ABI-sensitive. It deliberately avoids direct kernel pointer fields in ioctl payloads except where a 32-bit shadow form is provided, and it uses fixed-width hash keys/cookies as user-visible handles.

## Risks and Gotchas

- Structure packing and padding are part of the ABI; changing field order or alignment breaks 32-bit userland on 64-bit kernels.
- `dapl_cq_data_out_t` and `dapl_qp_data_out_t` typedef names appear swapped in their array-size macros, but both sizes are currently 24 so behavior is unaffected.
- Private data length limits must stay consistent with IBT private-data limits.
- Event polling allocates kernel memory, hence `DAPL_EVD_MAX_EVENTS` bounds user requests.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt_if.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib.h

## Purpose

Defines public EoIB encapsulation constants, vNIC ID packing helpers, vHUB ID construction, nexus-to-leaf event names and properties, gateway information passed to EoIB instances, and soft interrupt priorities.

## Main Definitions

- EoIB encapsulation header size and bit masks/shifts for signature, version, TCP/IP checksum state, FCS bit, multi-segment bit, segment offset, and segment ID.
- Encapsulation field values for signature/version/checksum states and shortcuts for common TX/RX encapsulation words.
- Driver name `eoib`.
- vNIC/device instance packing constants:
  - 6 bits for Solaris vNIC instance.
  - 9 bits for EoIB pseudo-device instance.
  - Macros to extract and build the combined vNIC ID.
- `EIB_VHUB_ID()` builds a vHUB ID from gateway port ID and VLAN.
- NDI event names for gateway availability, vNIC login acknowledgements, and gateway-info updates.
- Device properties used on EoIB child nodes, including HCA, port, gateway identity, keepalive periods, control QPN, LID, port ID, availability, host-managed vNIC flag, SL, RSS QPN count, names, and vendor ID.
- `eib_gw_info_t`: gateway information delivered by the nexus, with string buffers sized one byte larger than FIP source fields.
- Soft interrupt priorities for data, control, and admin CQ handling.

## Integration Notes

This is shared between the EoIB leaf driver and EoIB nexus driver. It exposes the contract by which `eibnx` creates/configures `eoib` instances and signals gateway/login state.

## Risks and Gotchas

- The 15-bit vNIC ID split caps vNICs at 64 per EoIB device and pseudo-devices at 512; comments note this is a gateway-response workaround.
- Property names are string contracts with devinfo/NDI consumers.
- Encapsulation checksum shortcut constants assume exact bit layout of the 32-bit EoIB header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib_impl.h

## Purpose

Defines the private implementation surface for the EoIB leaf driver: constants, debug controls, service-thread names, WQE pools, LSO buffers, admin/control/data channel sizing, multicast GID layouts, gateway and port properties, vNIC/vHUB tables, per-instance state, and cross-file function prototypes.

## Main Definitions

- Driver return codes, max line/SGL/posting/payload constants, copy threshold, max vNICs, timeouts, retry limits, and GRH size.
- Debug flag masks and logging macros, with debug categories compiled out unless `EIB_DEBUG` is set.
- Service-thread names for event handling, receive-WQE refill, vNIC creation, TX-WQE monitoring, and LSO-buffer monitoring.
- `EIB_FIND_LSB_SET()` lookup macro used by bitmap WQE allocation.
- LSO buffer bucket structures and status flags.
- Admin, control, and data QP sizing constants and CQ moderation defaults.
- WQE `qe_info` bit packing for block, index, type, and flags.
- `eib_wqe_t`: send/receive WQE wrapper with copy buffers, payload header, UD destination, free routine, mblk, memory I/O handle, IBT WR, SGLs, post chain, and channel pointer.
- Two-level bitmap WQE pool model: 64 WQEs per block, 64 blocks per pool.
- WQE low/high-water marks and priority constants.
- `eib_mgid_spec_t`/`eib_mgid_t`: multicast GID layout for vHUB data/update/table groups.
- Gateway, port, HCA capability, multicast group, channel, login-data, vHUB map/table/update, Ethernet header, vNIC, node state, stats, address-vector cache, event, vNIC request, keepalive, and main `eib_t` state structures.
- Function prototypes for FIP, service threads, admin/control/data QPs, resources, IBT, channels, MAC layer, vNIC handling, logging, properties, globals, and hardware workarounds.

## Integration Notes

`eib_t` is the leaf driver's main soft state and ties together IBT handles, MAC registration, gateway properties, admin QP, shared WQE pools, LSO buffers, vNIC slots, event queues, refiller/creator/monitor/keepalive threads, and address-vector cache.

## Risks and Gotchas

- Many structures use multiple mutex/condition-variable pairs; vNIC creation/deletion is serialized separately from active/zombie/rejoin bitmaps.
- WQE allocation depends on 64-bit bitmap invariants; constants say `EIB_WQES_PER_BLK` must not change.
- Data path uses large SGL arrays and LSO copy buffers to work around HCA SGL limits.
- Several runtime workaround globals disable descriptor length, checksum offload, LSO, multicast entries, AV discovery, VP flag, or vHUB checksum assumptions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/eib_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/enx_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/enx_impl.h

## Purpose

Defines the private implementation surface for the EoIB nexus driver (`eibnx`), which discovers EoIB gateways through FIP solicitation/advertisement, manages per-HCA-port monitor threads, tracks gateway state, and creates/configures `eoib` child nodes.

## Main Definitions

- Nexus return codes, debug flags/macros, default log size, monitor/node-creator thread names, and default unicast solicitation period.
- HCA/port inventory structures: `eibnx_port_t` and `eibnx_hca_t`.
- Port-monitor WQE sizing for solicitation/advertisement handling and CQ size.
- WQE type/flag constants and `eibnx_wqe_t` containing type, buffer size, SGL, IBT WR, lock, and state flags.
- TX/RX descriptors with MR handles, lkeys, and fixed WQE arrays.
- `eibnx_gw_addr_t`: address vector, GID, QPN, QKey, and P_Key for discovered gateways.
- Gateway state constants and `eibnx_gw_info_t`: advertisement status, address, GUIDs, keepalive periods, control QPN, LID, port ID, vNIC counts, flags, SL/RSS count, and gateway strings.
- Gateway packet type enum and message wrapper.
- Child-node tracking with devinfo pointer, gateway pointer, and node name.
- Port-monitor event bitmasks, multicast group status flags, and `eibnx_thr_info_t` for one HCA port monitor.
- Node-creation queue entries and bus configuration flags.
- `eibnx_t`: nexus global/per-instance state with IBT handle, HCA list, monitor list, node queue thread state, and bus operation state.
- Event tags delivered to child EoIB instances.
- Prototypes for monitor/event handlers, IBT setup/rollback, FIP solicit/parse, WQE queue helpers, gateway/child list management, logging, node creation/configuration, bus operations, devctl entry points, and globals.

## Integration Notes

The nexus sits above IBT and below child `eoib` instances. It joins well-known FIP multicast groups, discovers gateways, prepares devinfo properties/events, and handles gateway login ACK packets that may arrive at the nexus due to gateway behavior documented in `eib.h`.

## Risks and Gotchas

- Send WQEs for unicast solicitations are preallocated during receive processing constraints; acquisition cannot always sleep.
- Gateway liveness has separate unavailable/available/ready-to-login states plus advertisement heartbeat flags.
- Bus operation flags are partly protected by `nx_busop_lock` and partly by the in-progress bit itself.
- Child node creation is asynchronous through a node queue thread.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/enx_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/fip.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/fip.h

## Purpose

Defines EoIB FIP wire protocol constants and packed descriptor/message structures for solicitation, gateway advertisement, vNIC login/login ACK/logout-related data, keepalive, vHUB table, and vHUB update messages.

## Main Definitions

- Fixed lengths for vendor IDs, GUIDs, gateway system/port names, multicast GID prefix, vNIC name, and vHUB ID.
- EoIB admin P_Key, FIP/data QKeys, advertise/solicit multicast GUID prefixes.
- FIP protocol version and EoIB opcode/subcodes.
- Basic header flags for gateway availability and solicited messages.
- `fip_proto_t` and `fip_basic_hdr_t`.
- InfiniBand address descriptor with masks for QPN, port ID, and SL.
- Solicitation message: protocol version, basic header, and IB address descriptor.
- Gateway information, gateway identifier, and keepalive descriptors.
- Advertisement message combining IB address, gateway info, gateway ID, and keepalive parameters.
- vNIC login descriptor with MTU, vNIC ID, VLAN/flags, MAC, multicast GID prefix, RSS/MAC multicast counts, syndrome/control QPN, and vNIC name.
- Masks and syndrome codes for vNIC login success/failure.
- Partition descriptor and login/login-ACK message structures.
- vNIC identity descriptor and keepalive message.
- vHUB table entry format and entry type/valid/RSS/QPN/SL masks.
- vHUB update and vHUB table descriptors, including eport state, VP flag, vHUB ID, TUSN, table-size, chunk header flags, and trailing checksum convention.
- vHUB update/table packet wrappers.

## Integration Notes

This is a wire-format header used by both `eoib` and `eibnx`. Parsing/building code must apply endian conversion where appropriate; the structures describe protocol layout and constants but do not enforce conversion.

## Risks and Gotchas

- Some descriptors are variable length or have trailing entries/checksum after the fixed struct; bounds checks must live in parser code.
- Login descriptor bitfields are represented as masks over integer fields, not C bitfields.
- vHUB table fragmentation uses FIRST/MIDDLE/LAST/ONLY flags and TUSN/checksum state; partial table handling is external.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/eoib/fip.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/ibd/ibd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/ibd/ibd.h

## Purpose

Defines the private IP-over-InfiniBand (`ibd`) driver interface and state. It covers UD and Reliable Connected modes, driver lifecycle flags, tunables, multicast/address-handle cache rules, IPoIB wire headers, work queue objects, LSO/copy buffers, per-port state, RC connection/channel state, global service registration state, and cross-file prototypes.

## Main Definitions

- CQ polling flags, maximum receive mblk chain length, send batching limit, resource reap masks, async request opcodes, and attach/start state flags.
- Tunable defaults and bounds for UD/RC link mode, LSO policy, copy thresholds, WQE counts, AH/hash sizes, completion coalescing, SRQ enablement, SRQ sizes, and RC thresholds.
- Thresholds for LSO buffers, SWQEs, and TX CQ polling.
- Extensive multicast/AH cache design comments covering active/free list transitions, multicast disable, MCG delete/create traps, promiscuous rejoin, unreliable traps, and sendonly/fullmember behavior.
- Atomic AH reference/recycle-bit macros using high bits in `ac_ref`.
- Active/free address-handle cache list/hash macros.
- `IBD_PAD_NSNA()` adjusts IPv6 Neighbor Solicitation/Advertisement link-layer address padding between Solaris IP expectations and IPoIB alignment.
- IPoIB header/address/pseudo-TX-header and pseudo-GRH structures.
- RC mode service IDs, including legacy OFED interop ID.
- Kernel-only definitions:
  - RC channel state enum.
  - Async request, multicast cache, address cache, WQE, SWQE/RWQE, generic list, LSO bucket, RX post queue, and large-buffer structures.
  - `ibd_state_t`: main per-interface state with IBT/MAC handles, TX/RX lists, CQs, UD channel, multicast group info, MAC addresses/GIDs, async request thread, AH/multicast caches, trap/link/MAC state, counters, checksum/LSO capabilities, RC mode configuration, RC listeners, channel lists, SRQ, large TX buffers, chained receive state, timeout state, RC statistics, device identity, and all UD/RC tunables.
  - Global IBTF state and service list structures.
  - RC hello message and `ibd_rc_chan_t` with channel handle, state, ACE, TX/RX WQE lists, CQs, soft interrupts, chained send/receive, channel role, timeout/use markers, and close synchronization.
- Prototypes shared between `ibd.c` and `ibd_cm.c` for warnings, memory unmapping, async work queueing, AH cache lookup/recycle/refcount, RC listen/connect/close, SRQ handling, RC send/receive resources, config, and stats.

## Integration Notes

This header is central to the illumos IPoIB MAC driver. It bridges MAC provider APIs, IBT channels/CQs/MRs, multicast SA membership, address resolution, and optional RC connections.

## Risks and Gotchas

- The address-handle cache deliberately avoids locking active-list operations except via async-thread ownership and atomic refcounts; changing caller context can break this model.
- Multicast trap handling is conservative because SA traps are unreliable and out of order.
- RC mode has separate active/passive channel states, two service IDs, optional SRQ, timeout reaping, and large-copy-buffer fallback.
- Tunables interact with HCA limits and CQ sizes; comments call out catastrophic errors if SRQ buffers exceed RWQE constraints.
- `RX_QUEUE_CACHE_LINE` depends on exact struct size and may need revision if fields change.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/ibd/ibd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser.h

## Purpose

Defines core iSER driver state, operational parameters, iSCSI negotiation keys, service bindings, connection type/stage/state, negotiated operation parameters, connection objects, and top-level iSER public routines.

## Main Definitions

- Includes core DDI, socket, IBT, IDM, and iSER component headers.
- `iser_logging` and `ISER_LOG` conditional logging macro.
- Taskq thread count, iSER header length, and half-second delay constant.
- Operational min/max/implementation/default values for target/initiator receive data segment length and max outstanding unexpected PDUs.
- iSCSI key names relevant to iSER negotiation: RDMA extensions, OF/IF markers, segment lengths, and max outstanding unexpected PDUs.
- `iser_sbind_t`: one service bind handle with GID/GUID.
- `iser_svc_t`: iSER-specific IDM service state with refcount, service ID, server handle, and service-bind list.
- `iser_conn_type_t`: initiator or target connection.
- `iser_conn_stage_t`: staged transition into iSER-assisted mode, including allocation, IDM connected, hello/helloreply send/receive states and failures, logged-in, disconnected, freed, closing, and closed.
- `iser_op_params_t`: negotiated digest, RDMA extension, marker, segment length, and unexpected-PDU parameters.
- `iser_conn_t`: connection lock/stage CV, type, channel, stage, op params, IDM connection, and IDM service.
- `iser_state_t`: driver soft state with devinfo, instance, open refcount, IBT client handle, HCA list, connection list, and global WR cache.
- Status enum and prototypes for IDM registration, service registration/binding/unbinding/deregistration, path lookup, channel allocation/open/close/free, connection destruction, and target service refcount helpers.

## Integration Notes

This is the top-level private iSER header and aggregates the IB, resource, CM, and transfer subheaders. It connects IDM/iSCSI lifecycle to IBT Reliable Connected channels and iSER protocol negotiation.

## Risks and Gotchas

- Connection stages explicitly model failure points during hello exchange; callers should not collapse these states.
- Segment-length defaults reuse iSCSI defaults but iSER imposes larger protocol min/max constraints.
- Service binding is per HCA port through `iser_sbind_t` list entries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_cm.h

## Purpose

Declares the iSER Communications Manager event handler used with IBT CM events.

## Main Definitions

- Includes IBT and iSCSI protocol headers.
- Declares `iser_ib_cm_handler()`, taking CM private data, an IBT CM event, return arguments, return private-data buffer, and maximum return private-data length.

## Integration Notes

This is the narrow interface between iSER and the IBT communication manager. The handler is expected to translate IB CM events into iSER/IDM connection state transitions and optional private-data replies.

## Risks and Gotchas

- Return private data length is caller-provided; handler implementations must respect `ret_len_max`.
- CM handler behavior is tightly coupled to connection-stage values in `iser.h` and private-data layout in `iser_xfer.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_ib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_ib.h

## Purpose

Defines iSER's InfiniBand transport state and IBT-facing routines: HCA inventory, queue pair sizing/depth tracking, RC channel state, address conversion/path lookup, channel allocation/open/close, receive posting, CQ handlers, and async handler entry points.

## Main Definitions

- External globals: `iser_state` and `iser_taskq`.
- `iser_hca_t`: list node, failure flag, IBT client/HCA/PD handles, HCA attributes, GUID, port info, and per-HCA message/data memory pools and kmem caches.
- Receive queue low-water percentage, receive-post batching limit, and send-CQ poll limit.
- Queue sizing constants:
  - 64-bit kernels use larger receive queue default than 32-bit kernels.
  - Send queue size is 2000.
  - SGL size is 1.
  - Default IRD/ORD values.
- `iser_qp_t`: QP lock, SQ/RQ sizes, RQ depth/current level/min post level/low-water mark, and pending taskq flag.
- `iser_chan_t`: RC channel lock, IBT channel handle, local/remote IP and ports, IBT path info, HCA pointer, send/recv CQs and sizes, QP tracking, SQ post lock/count/max count, and back-pointer to iSER connection.
- Prototypes for IB init/fini, service register/bind/unbind/deregister, sockaddr/IBT address conversion, path lookup, channel allocation with or without path lookup, RC channel open/close/free, receive posting, CQ handlers, and IB async handling.

## Integration Notes

`iser_chan_t` is the IB transport object referenced by `iser_conn_t`. It owns the IBT channel/CQs and tracks both RQ refill pressure and SQ outstanding posts.

## Risks and Gotchas

- Receive queue sizes are intentionally below power-of-two boundaries so HCA drivers can round up while leaving headroom.
- 32-bit kernels use much smaller receive queues due to memory pressure.
- RQ refill uses low-water and taskq-pending state; double scheduling must be avoided.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_ib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_idm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_idm.h

## Purpose

Defines the iSER transport hooks visible to IDM, especially the target service creation routine and the copy-vs-registration threshold for small transfers.

## Main Definitions

- Includes IDM core and text interfaces.
- Documents that most transport functions are called through the IDM transport ops vector, while `iser_tgt_svc_create()` is also called from an async handler.
- `ISER_BCOPY_THRESHOLD` is `0x20000` bytes, selecting bcopy into pre-registered memory for transfers where memory registration would be too expensive.
- Declares `iser_tgt_svc_create(idm_svc_req_t *, struct idm_svc_s *)`.

## Integration Notes

This header is the IDM-facing glue point for iSER target service setup. It complements the broader service registration functions in `iser.h`.

## Risks and Gotchas

- The bcopy threshold is a performance policy: changing it shifts CPU cost vs RDMA registration overhead.
- `iser_tgt_svc_create()` may be invoked from more than one path, so implementation must handle async and ULP contexts safely.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_idm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_resource.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_resource.h

## Purpose

Defines iSER memory-region pools, registered message/data buffer objects, work request tracking objects, cache constructors/destructors, and routines for allocating registered memory and registering in-place IDM buffers.

## Main Definitions

- Cache name length and default control/text PDU and data buffer lengths.
- `iser_mr_t`: IBT MR handle, virtual address, length, lkey/rkey, and AVL node.
- `iser_vmem_mr_pool_t`: HCA-bound vmem pool with MR flags, chunk sizing, total/max size, AVL MR list, and mutex.
- MR quantum/minimum chunk sizes and architecture-dependent chunk/max pool sizes for data and message memory.
- MR flags:
  - Data buffers enable local write, remote read, and remote write.
  - Message buffers enable local write.
- Vmem pool create/destroy/alloc/free/MR lookup prototypes.
- `iser_wr_type_t`: send, RDMA write, RDMA read, or undefined.
- `iser_wr_t`: send completion context referencing an iSER message, IDM buffer, or IDM PDU.
- WR cache constructor/destructor/get/free prototypes.
- `iser_msg_t`: registered control PDU/text message handle with back-pointer cache, SGE, and two MR handles.
- Message cache constructor/destructor/get/free prototypes.
- `iser_buf_t`: data buffer object with cache, buffer, length, MR, SGE, debug copies of WR/WC, and construction/destruction timestamps.
- Buffer cache constructor/destructor and HCA cache init/fini prototypes.
- In-place RDMA memory registration/deregistration routines for existing IDM buffers.

## Integration Notes

This header manages the registered-memory substrate used by iSER transfer code. Per-HCA caches are referenced from `iser_hca_t` in `iser_ib.h`.

## Risks and Gotchas

- Pool sizes differ sharply between 32-bit and 64-bit kernels.
- Registered-memory pools track MR chunks in an AVL tree; alloc/free and MR lookup must stay synchronized with vmem lifetime.
- Work request completion depends on `iser_wr_t` preserving the correct associated object type.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_resource.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_xfer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_xfer.h

## Purpose

Defines iSER wire headers and transfer routines for connection private data, Hello/HelloReply exchange, iSCSI control PDUs, and RDMA data movement over an RC channel.

## Main Definitions

- `iser_private_data_t`: packed CM REQ private data containing IBT IP header private data plus SIE/ZBVA flags and reserved bytes, with endian-specific bitfield ordering.
- iSER opcode constants for control-type PDU, Hello, and HelloReply.
- `iser_ctrl_hdr_t`: expanded iSER control header used when ZBVA is not supported, including opcode, RStag/WStag valid flags, write stag/VA, and read stag/VA.
- `iser_hello_hdr_t`: Hello message with opcode, min/max version, and IRD.
- `iser_helloreply_hdr_t`: HelloReply with opcode, flag, current/max version, and ORD.
- `#pragma pack(1)` ensures these protocol headers are byte-packed.
- Transfer prototypes:
  - `iser_xfer_hello_msg()`
  - `iser_xfer_helloreply_msg()`
  - `iser_xfer_ctrlpdu()`
  - `iser_xfer_buf_to_ini()`
  - `iser_xfer_buf_from_ini()`

## Integration Notes

The structures are protocol ABI, not just internal state. They are used alongside connection-stage tracking in `iser.h` and channel/WR resources in `iser_ib.h` and `iser_resource.h`.

## Risks and Gotchas

- Requires one of `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`; incorrect endian macro selection changes wire bit positions.
- The header is packed to one-byte alignment; adding fields must preserve protocol layout.
- Control header use depends on ZBVA negotiation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_xfer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofa_solaris.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofa_solaris.h

## Purpose

Provides a small Solaris kernel wrapper type used by OFED-style user/kernel interfaces to pass response addresses in a way compatible with 32-bit and 64-bit layouts.

## Main Definitions

- Kernel-only include of basic types and byteorder.
- `ofv_resp_addr_t`: union of a 64-bit response address and two 32-bit words.
- Macros:
  - `r_laddr` accesses the full 64-bit value.
  - `r_addr` and `r_notused` select the correct 32-bit word depending on `_LONG_LONG_HTOL`.

## Integration Notes

Included by `ofed_kernel.h` and `ib_user_verbs.h` to model OFED uverbs response pointer/address fields without direct pointer types.

## Risks and Gotchas

- Word selection depends on long-long byte ordering, not ordinary integer byte order.
- Only active under `_KERNEL`; userland consumers need matching ABI definitions elsewhere.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofa_solaris.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofed_kernel.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofed_kernel.h

## Purpose

Collects Solaris OFED compatibility definitions imported from OpenIB headers, including MAD size constants, CM SIDR status values, and SA path record layout.

## Main Definitions

- License/comment block documents imported content from `ib_mad.h`, `ib_cm.h`, and `ib_sa.h` under OpenIB BSD terms.
- Includes Solaris OFA wrapper, OFED verbs, user verbs, and user MAD headers.
- MAD management header/data size enum:
  - General MAD, RMPP, vendor, SA, device, and SNMP header/data sizes.
- `enum ib_cm_sidr_status`: SIDR result codes for success, unsupported, reject, no QP, redirect, and unsupported version.
- `struct ib_sa_path_rec`: SA path record with service ID, DGID/SGID, LID fields, raw traffic, flow label, hop limit, traffic class, reversibility, number of paths, P_Key, QoS class, SL, MTU/rate/lifetime selectors and values, and preference.

## Integration Notes

This is a compatibility aggregation header for OFED-derived kernel interfaces in illumos. It bridges local Solaris headers with imported OFED user/kernel ABI definitions.

## Risks and Gotchas

- The imported definitions must remain ABI-compatible with the OFED consumers they emulate.
- `struct ib_sa_path_rec` uses OFED types from `ib_verbs.h`, including `union ib_gid`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/ofed_kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_addr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_addr.h

## Purpose

Defines OFED-compatible RDMA device address helpers for IPoIB/InfiniBand address data embedded in hardware address buffers.

## Main Definitions

- Imported-license comment for OFED `ib_addr.h`.
- `MAX_ADDR_LEN` set to 32 bytes.
- `struct rdma_dev_addr`: source device address, destination device address, broadcast address, and RDMA node type.
- `ip_addr_size()` returns IPv4 or IPv6 sockaddr size based on `sa_family`.
- Inline helpers to get/set P_Key from `broadcast[8..9]`.
- Inline helpers to get multicast GID from `broadcast + 4`.
- Inline helpers to get/set SGID from `src_dev_addr + 4`.
- Inline helpers to get/set DGID from `dst_dev_addr + 4`.

## Integration Notes

This header is used by OFED-compatible RDMA code that expects Linux-style device-address packing. It depends on `ib_verbs.h` for `enum rdma_node_type` and `union ib_gid`.

## Risks and Gotchas

- Offsets are protocol/ABI assumptions. The helpers blindly copy at fixed offsets inside 32-byte arrays.
- `ip_addr_size()` treats anything other than `AF_INET6` as IPv4.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_addr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_mad.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_mad.h

## Purpose

Defines the OFED user MAD ABI structures and ioctl command constants for registering agents, sending/receiving MAD packets, and enabling P_Key-index support.

## Main Definitions

- `IB_USER_MAD_ABI_VERSION` set to 5.
- ABI comment requiring identical struct layout on 32-bit and 64-bit architectures.
- `struct ib_user_mad_hdr`: packet metadata including agent ID, status, timeout, retries, MAD length, QPN, QKey, LID, SL, path bits, GRH presence, GID index, hop limit, traffic class, remote GID, flow label, P_Key index, and reserved bytes.
- `struct ib_user_mad`: header plus flexible `uint64_t data[]` payload.
- `struct ib_user_mad_reg_req`: agent registration request with returned ID, method mask, QPN, management class/version, OUI, and RMPP version.
- `IB_IOCTL_MAGIC` and ioctl constants:
  - `IB_USER_MAD_REGISTER_AGENT`
  - `IB_USER_MAD_UNREGISTER_AGENT`
  - `IB_USER_MAD_ENABLE_PKEY`

## Integration Notes

This is a user/kernel ABI header. It mirrors OFED definitions and is included by `ofed_kernel.h`.

## Risks and Gotchas

- Layout is explicitly ABI-sensitive across 32-bit userland and 64-bit kernels.
- Flexible payload is `uint64_t` aligned; command handlers must use the length field for bounds.
- P_Key index is only meaningful after enabling it on the user MAD file handle.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_mad.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_sa.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_sa.h

## Purpose

Defines the OFED-compatible user SA path record structure.

## Main Definitions

- Imported-license comment for OFED `ib_user_sa.h`.
- `struct ib_user_path_rec` containing:
  - DGID and SGID byte arrays.
  - Destination/source LIDs.
  - Raw traffic, flow label, reversibility, MTU, P_Key.
  - Hop limit, traffic class, number of paths, service level.
  - MTU/rate/packet lifetime selectors and values.
  - Preference.

## Integration Notes

This is a compact user ABI counterpart to the kernel `ib_sa_path_rec` in `ofed_kernel.h`.

## Risks and Gotchas

- Uses fixed byte arrays for GIDs rather than `union ib_gid`, preserving user ABI layout.
- Field sizes/order must remain compatible with OFED userland.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_sa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_verbs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_verbs.h

## Purpose

Defines the OFED user verbs ABI for illumos, including command IDs and request/response structures for contexts, device/port/GID/P_Key queries, PD/MR/CQ/QP/AH/SRQ lifecycle, posting send/receive work requests, polling completions, and multicast attach/detach.

## Main Definitions

- `IB_USER_VERBS_ABI_VERSION` set to 6.
- `IB_USER_VERBS_CMD_*` enum covering context, device/port queries, PD, AH, MR/MW, completion channel/CQ, QP, send/recv posting, multicast, SRQ, XRC-related commands, GID query, and P_Key query.
- ABI rules: no pointer types in structs, use `uint64_t` for addresses, and pad larger structures to 8-byte multiples.
- Event descriptors for async and completion events.
- Common `ib_uverbs_cmd_hdr`.
- Context and device/port/GID/P_Key query request/response structures.
- PD allocation/deallocation, with Solaris opaque PD driver output buffer.
- MR registration/deregistration.
- Completion channel creation.
- CQ create/resize/poll/notify/destroy, with WC and opaque CQ driver output buffer.
- Address vector structures: global route, AH attributes, create/destroy AH payloads.
- QP attribute, create/query/modify/destroy request/response structures, QP destination layout, and opaque QP driver output buffer.
- SGE documentation struct and send/receive WR formats.
- Post send/recv/SRQ recv payloads and bad-WR responses.
- Multicast attach/detach structures.
- SRQ create/modify/query/destroy structures and opaque SRQ driver output buffer.

## Integration Notes

This is a large ABI header used by OFED-compatible uverbs code on illumos. `ofv_resp_addr_t` from `ofa_solaris.h` models response addresses. Opaque driver output arrays are deliberately sized at 24 `uint64_t` words for PD/CQ/QP/SRQ responses.

## Risks and Gotchas

- Every field order, width, and padding choice is ABI-sensitive for 32-bit and 64-bit compatibility.
- Several command payloads contain flexible trailing arrays or driver data; handlers must validate `in_words`, `out_words`, counts, and `wqe_size`.
- XRC command IDs are listed even though this header does not define all XRC payloads here.
- The file assumes `ib_sge` packs the same across kernel/user and documents that with `ib_uverbs_sge`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_verbs.h -->