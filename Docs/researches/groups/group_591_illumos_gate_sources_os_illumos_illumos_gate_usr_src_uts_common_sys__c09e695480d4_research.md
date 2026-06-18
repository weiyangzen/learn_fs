# Group Research: group_591_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__c09e695480d4

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibci.h

## Purpose

`ibci.h` defines the InfiniBand Channel Interface between IBTF/IBTL and HCA driver implementations. It is the driver-side contract: HCA drivers register their capability data and operation vector with IBTF, while IBTF calls through the vector to allocate, modify, query, post, poll, map, and free transport resources.

## Main Interfaces

The header defines opaque handles for both directions: IBTF-visible CI handles such as `ibc_hca_hdl_t`, `ibc_pd_hdl_t`, `ibc_qp_hdl_t`, `ibc_cq_hdl_t`, `ibc_srq_hdl_t`, memory-region/window handles, and CI-visible IBTF handles such as `ibtl_qp_hdl_t`, `ibtl_eec_hdl_t`, and `ibc_clnt_hdl_t`.

The central type is `ibc_operations_t`, a large HCA driver vtable. It covers HCA and port query/modify operations, protection domains, RDD/EEC legacy reliable datagram objects, address handles, QP allocation/free/query/modify including special and range allocation, CQ allocation/resizing/moderation/scheduling, memory registration and synchronization, memory windows, multicast attach/detach, send/receive posting, CQ polling/notification, CI private data import/export, SRQs, address translation, L_Key allocation, physical and DMA memory registration, FMR pools, IO memory allocation, and XRC placeholders.

`ibc_hca_info_t` packages the CI version, driver HCA handle, operation vector, and static HCA attributes supplied during attach.

## Upcalls

The CI calls into IBTF through `ibc_init()`, `ibc_fini()`, `ibc_attach()`, `ibc_post_attach()`, `ibc_pre_detach()`, `ibc_detach()`, `ibc_cq_handler()`, `ibc_async_handler()`, `ibc_memory_handler()`, and `ibc_get_ci_failure()`.

## Research Notes

This header is central to RDMA storage and network driver behavior because every queue, completion, protection-domain, and memory-registration operation eventually crosses this ABI. Correctness depends on strict handle ownership, persistent `hca_ops`/`hca_attr` storage, and consistent translation between IBTF channel abstractions and HCA-native objects.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti.h

## Purpose

`ibti.h` is the main public InfiniBand Transport Interface header for IBTF clients. It includes `ibti_common.h` and adds client-facing RC and UD channel allocation, query, modify, destination, and helper APIs.

## Main Types

`ibt_chan_alloc_flags_t` describes channel allocation options such as clone, user mapping, deferred allocation, SRQ, RSS, and Fibre Channel variants. `ibt_rc_chan_alloc_args_t`, `ibt_rc_chan_query_attr_t`, and `ibt_rc_chan_modify_attr_t` model RC channel creation, runtime state, path/RDMA parameters, and modifiable attributes. `ibt_ud_chan_alloc_args_t`, `ibt_ud_chan_query_attr_t`, and `ibt_ud_chan_modify_attr_t` do the same for UD channels, including Q_Key, P_Key index, RSS, SRQ, and FC attributes. `ibt_ud_dest_query_attr_t` captures resolved UD destination state.

## Functions

The prototypes cover RC/UD channel allocation, range allocation for consecutive UD QPNs, flush/free, query/modify, UD recovery from SQ error, UD destination allocation/modification/reply/SIDR request/free/query, privileged destination checks, Q_Key updates, channel private data, and channel-to-HCA GUID lookup.

## Research Notes

This is the high-level channel API most kernel consumers would use rather than explicit QP verbs. It hides much of the CI/HCA detail while still exposing RDMA-critical sizing, queue state, path, retry, SRQ, RSS, and Q_Key behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_cm.h

## Purpose

`ibti_cm.h` defines the IBTI Communication Manager event, status, private-data, reject, redirect, and callback contract. It is the public shape of RC connection establishment/teardown and UD SIDR service resolution.

## Main Content

The header defines CM private-data limits for REQ, REP, RTU, MRA, DREQ, DREP, LAP, APR, REJ, SIDR request/reply, and RDMA IP CM private headers. `ibt_cm_reason_t` enumerates standard reject/failure reasons and illumos-specific values such as duplicate requests, aborts, CI failures, invalid passive QP state, and RDMA IP CM rejection.

`ibt_cm_status_t` models client handler decisions: accept, reject, redirect, no channel/resource, default, or defer. SIDR and alternate-path status enums capture UD service resolution and LAP/APR outcomes.

## Event Structures

The header defines redirect data, REP/MRA/LAP/APR/failure event payloads, REQ event payloads, RDMA IP reject information, additional reject unions, connection-closed reason codes, and the top-level `ibt_cm_event_t`. It also defines return structures for accepting, rejecting, redirecting, and proceeding after deferred CM handling.

For UD/SIDR, `ibt_cm_ud_event_t` carries SIDR request/reply events and `ibt_cm_ud_return_args_t` carries service response or redirect data.

## Callbacks

`ibt_cm_handler_t` is the RC CM event callback type. `ibt_cm_ud_handler_t` is the UD CM/SIDR callback type. The comments emphasize that blocking work in CM callbacks can stall CM threads, and that deferred events must later be completed with the proceed APIs declared in `ibti_common.h`.

## Research Notes

This file is the semantic contract for connection lifecycle, private negotiation data, redirect handling, and failure reporting. RDMA storage consumers that use RC or RDMA IP CM rely on these structures to safely establish channels and interpret rejection or teardown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_common.h

## Purpose

`ibti_common.h` defines shared public IBTI types and prototypes used by clients across HCA discovery, path lookup, connection management, service registration, completion queues, memory registration, multicast, protection domains, SRQs, FMR, IP path resolution, and private contract interfaces.

## Main Types

The file defines the IBTI version, client classes, client module registration structure, async and memory callbacks, subnet notice callbacks, service-data masks, path request/response structures, alternate path structures, RC open arguments/returns, UD SIDR destination/return structures, multicast attributes/results, service descriptors/bindings, property update payloads, node information, IP path/source-IP structures, RDMA IP CM private data, address records, and partition attributes.

Client classes distinguish storage, network, generic, user, IBMA, CM, DM, and related management clients. `ibt_clnt_modinfo_t` is the persistent registration descriptor passed to `ibt_attach()`.

## Function Surface

The header declares client attach/detach, HCA listing/open/close/query/port query/private data helpers, path and alternate-path lookup, RC open/close/prime-close/recycle, UD recycle, channel queue and RDMA modification, service registration and binding, CM delay/proceed, CQ allocation/free/notification/handler/poll/query/resize/modification, memory registration/reregistration/shared registration/synchronization, memory windows, L_Key allocation, physical/DMA memory registration, address translation, work request posting, path migration, multicast join/leave/query/attach/detach, subnet notices, PD allocation/free, P_Key conversions, CI private data exchange, node lookup, reprobe, SRQ lifecycle, failure classification, hardware presence check, FMR pool operations, IP path/source-IP lookup, RDMA IP SID formatting/parsing, private Address Record APIs, HCA system-image and port modification, IO memory allocation, partition attribute callbacks, and LID-to-node lookup.

`ibt_get_alt_path()` is declared in both the connection and alternate path sections, reflecting header organization rather than a separate API.

## Research Notes

This is the broadest public IBTF interface header in the group. For filesystem and storage research, the important areas are client classing for `IBT_STORAGE_DEV`, RC channel open/close semantics, memory registration APIs for RDMA buffers, CQ completion delivery, FMR/physical registration, and IP path helpers used by RDMA-aware upper-layer protocols.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_ci_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_ci_types.h

## Purpose

`ibtl_ci_types.h` contains types and compatibility mappings shared by IBTL and the CI/HCA driver interface. It bridges public channel terminology to lower-level QP/AH/EEC terminology and exposes selected structures to avoid data copying in fast paths.

## Main Content

The header maps opaque fields and status names between QP/address-handle language and channel/UD-destination language. It defines CI-specific aliases for address-vector fields, work-completion fields, multicast LID, HCA QP capability names, and CEP timeout storage.

`ibt_ud_dest_t` is shared between IBTL and CI so UD send processing can directly consume address handle, destination QPN, and Q_Key without copying. `ibt_rd_dest_t`, RD transport types, and EEC structures are reserved or legacy-oriented.

The file defines QP types, special QP types, QP allocation flags, `ibt_qp_alloc_attr_t`, QP transport-specific query/modify structures for RC/UC/RD/UD, common `ibt_qp_info_t`, `ibt_qp_query_attr_t`, and EEC query/modify structures.

## Research Notes

This is a compatibility and performance boundary header. It lets CI drivers implement traditional QP verbs while IBTI clients can use the higher-level channel API. The shared `ibt_ud_dest_t` layout is especially important because it is directly referenced by HCA drivers during UD work-request processing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_ci_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_status.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_status.h

## Purpose

`ibtl_status.h` defines global IBTL return codes and work-completion status values.

## Status Families

`ibt_status_t` starts with generic return codes such as success, failure, unsupported, invalid parameter, insufficient resources, CM failure, missing HCA/path/service/MCG/node records, IP-to-GID failures, and no-such-object. It then groups errors by resource/HCA, HCA attributes, UD destinations, channels, completion queues, reserved opaque ranges, memory operations, multicast, P_Key lookup, protection domains, SRQs, and FMR pools.

Opaque status slots are deliberately reused by `ibci.h` and `ibtl_ci_types.h` for legacy or CI-specific meanings such as RDD/EEC and raw datagram errors.

## Completion Status

`ibt_wc_status_t` is a compact `uint8_t`. The file defines success plus local length/protection/channel errors, flushed WRs, memory-management/bind errors, and reliable transport errors such as bad response, local access, remote invalid request/access/op errors, transport timeout, and RNR NAK timeout.

## Research Notes

This is the canonical status vocabulary for IBTF callers and HCA drivers. The numeric grouping is useful when tracing failures across layers: immediate API failures use `ibt_status_t`, while completed work requests report `ibt_wc_status_t`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_status.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_types.h

## Purpose

`ibtl_types.h` defines the common IBTL data types shared by IBTI clients and IBCI/HCA drivers. It is the core ABI/type catalog for handles, endian conversion, HCA and port attributes, channel state, memory registration, work requests, completions, asynchronous events, and RDMA IP addressing.

## Main Types

The header defines opaque handles for clients, HCAs, channels, SRQs, CQs, services, service bindings, FMR pools, memory areas, PDs, CQ schedulers, MRs, MWs, UD destinations, address handles, EEC/RD destinations, IO memory allocations, and memory IOV maps.

It defines endian conversion macros, key and work-request ID types, selector/rate/lifetime request types, channel/SRQ queue sizing, execution modes, allocation flags for MW/PD/UD/SRQ/L_Key, retry/timer enums, HCA capability flags, page-size masks, and `ibt_hca_attr_t`, which is the large static capability descriptor for HCA limits, memory features, CQ moderation, firmware version, XRC, WQE sizing, RSS, FC offload, and device info.

## Port and Channel Data

`ibt_hca_portinfo_t` describes cached/queryable port state including LID, violation counters, SM data, link state, width/speed, SGID/P_Key tables, default P_Key index, virtual lanes, subnet timeout, capabilities, and max message size. `ibt_adds_vect_t` and `ibt_cep_path_t` describe addressing and connected endpoint paths.

Channel-related types include RSS attributes, migration state, transport service IDs, CEP states, attribute flags, CEP control and modify flags, CQ notification/scheduling/attributes, and handler attributes.

## Memory and Work Requests

The memory section defines MR flags, MR query flags, physical buffers, MR/PMR descriptors, MR/PMR/DMR/SMR attributes, IOV mapping attributes, key state, MR/MW query attributes, synchronization ranges, VA translation attributes, and FMR pool attributes.

Work request definitions cover opcodes, completion flags/detail bits, `ibt_wc_t`, WR flags, memory-window bind, SGL data segments, atomic/RDMA/fast-register/local-invalidate operations, raw transport placeholders, RC/UC/RD/UD/LSO send payloads, Fibre Channel over IB WR payloads, `ibt_send_wr_t`, `ibt_recv_wr_t`, and the union `ibt_all_wr_t`.

## Events and Miscellaneous

The file defines asynchronous event codes for channel, CQ, port, HCA attach/detach, SRQ, port-change, client reregister, and FEXCH errors; port-change flags; FC syndromes; CI private data flags; object type identifiers; MR private callback data; memory error payloads; failure classification; and `ibt_ip_addr_t` for IPv4/IPv6 RDMA IP CM support.

## Research Notes

This is the most important structural header in the group. Storage-relevant consumers depend on these exact memory-registration, work-request, CQ, and completion structures for RDMA data paths. The file also exposes several illumos-specific extensions for RSS, LSO, FMR, reserved L_Key, DMA MR, memory-management extensions, and Fibre Channel offload.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibvti.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibvti.h

## Purpose

`ibvti.h` defines private verbs-level transport interface extensions. It exposes explicit QP and AH operations while mapping them onto the channel-oriented IBTI model.

## Main Content

The header provides compatibility aliases for CM reasons, SIDR status, open-channel flags, open arguments, CM event fields, request EEC fields, and address-vector fields. It defines `ibt_qp_hdl_t` as `ibt_channel_hdl_t`, making QPs usable in selected channel APIs.

## Functions

The verbs-style functions cover AH allocation/free/query/modify, QP allocation including special QPs, QP flush/initialize/free/query/modify, QP private data access, QP-to-HCA GUID lookup, UD QP recovery, SIDR destination QPN lookup through `ibt_ud_get_dqpn()`, module-specific failure creation, and OFUV CM request/proceed helper hooks.

## Research Notes

This file exists for lower-level or compatibility consumers that need QP/AH verbs terminology instead of the normal IBTI channel API. It is private, but it reveals how illumos preserves verbs-like behavior while the public interface prefers channels and UD destination handles.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibvti.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl.h

## Purpose

`impl/ibtl.h` is the main private implementation header for IBTL. It defines the internal object graph, async/CQ state, resource accounting, macros for converting IBTL handles to CI objects, and private IBTL initialization/synchronization entry points.

## Main Structures

`ibtl_clnt_t` tracks a registered client, its module info, private pointer, devinfo, service count, HCA list, and subnet notice handler. `ibtl_hca_devinfo_t` represents a CI-registered HCA device with state, portinfo cache, client list, CI handle and ops vector, HCA attributes, devinfo, async state, port async data, FMA data, MultiSM flag, and kstat metadata.

`ibtl_hca_t` is a client’s open HCA handle and tracks links, client/device pointers, closing flag, resource counters for QPs/EECs/CQs/PDs/AHs/MRs/MWs/QPNs/SRQs/FMR pools, and async accounting.

`ibtl_cq_t`, `ibtl_srq_t`, `ibtl_qp_t`, `ibtl_eec_t`, and `ibtl_channel_t` represent internal CQ, SRQ, QP, EEC, and channel objects. Channels embed `ibtl_qp_t` first and add transport-specific RC/RD/UD state, current CEP state, client private data, CM private data, mutex, and condition variable.

## Synchronization and Macros

The header defines async pending/free flags, CQ pending/call-client/free flags, RC QP connection/free-state flags, and `_NOTE` annotations for lock and data-access expectations. Macros convert between channels, QPs, CI HCA handles, CI operation vectors, client handles, module info, HCA GUIDs, port counts, and table sizes.

## Functions and Globals

Private prototypes cover HCA lookup, portinfo init/reinit, CEP state/time/logging/thread initialization and teardown, new-HCA announcement, client detach, QP flow control, async free checks, CQ free synchronization, and HCA close synchronization. Globals include the HCA list, client list/mutex, free-QP mutex, close-HCA condition variable, QP flow-control mutex/CV, well-known async handlers for CM/DM/IBMA, and a fast GID cache validity flag.

## Research Notes

This header is the internal map for IBTL lifetime management. The resource counters and async-free flags are important for detach and free races, especially for storage clients that may hold CQs, channels, and registered memory while asynchronous errors are being delivered.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_cm.h

## Purpose

`impl/ibtl_cm.h` defines the private interface between IBTL and the InfiniBand Communication Manager. It supports CM private data attachment, local port/GID discovery, RC QP lifetime coordination, service-count tracking, cached port queries, active port selection, subnet notice delivery, and node-info callbacks.

## Main Interfaces

The header aliases `ibt_ud_dest_t`’s opaque field as `ud_dest_hca` for CM use. It declares functions to set, get, release, and wait on per-channel CM private data.

`ibtl_cm_hca_port_t` packages HCA GUID, port GUID, base LID, port number, SGID index, LMC, and MTU for a source GID. Lookup functions retrieve HCA/port information, companion GIDs, MultiSM state, first full P_Key index, and cached HCA portinfo.

## RC Lifetime Coordination

The `ibtl_cm_chan_is_*` functions tell IBTL when an RC channel is opening, open, aborted, closing, closed, reused, or already in closing/closed state. These exist to coordinate QPN reuse and TIMEWAIT behavior between CM and client-driven free paths.

## Port Lists and Notices

`ibtl_cm_port_list_t` describes active source ports for path selection, including HCA GUID, SGID, base LID, MTU, SGID index, port number, MultiSM flags, SAA handle, and source IP. The header also declares subnet notice registration/delivery helpers and an initialization-failure payload containing failing SGIDs.

## Research Notes

This header exposes the hidden cooperation needed between path lookup, CM state machines, and IBTL resource lifetime. For RC storage transports, the QPN reuse/TIMEWAIT hooks are the key safety mechanism.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_ibnex.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_ibnex.h

## Purpose

`impl/ibtl_ibnex.h` defines the private interface between IBTL and the InfiniBand nexus driver. It supports nexus callbacks, cfgadm client listing/unconfiguration data, HCA GUID/devinfo translation, verbose HCA data, parent validation, MPxIO pHCI registration, and HCA query by GUID.

## Main Interfaces

The header defines APID/string lengths, child names `ioc` and `ibport`, flags for `list_clients` and `unconfig_clients` style queries, callback argument data, and callback command values for IBC init/fini and reprobe requests.

The callback registration APIs allow IB nexus to provide a routine used by IBTL. Query APIs return packed NVL buffers for clients of a given HCA, translate HCA devinfo pointers to GUIDs and vice versa, collect verbose display data, validate client parents, register/unregister HCA devinfo as an MPxIO pHCI, and query HCA attributes plus driver identity/path.

## Research Notes

This is not a data-path header; it is device-tree and administration plumbing. It matters for hotplug, cfgadm, client unconfiguration, and multipath integration around IB HCAs and child devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_ibnex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_util.h

## Purpose

`impl/ibtl_util.h` declares private IBTF helper routines for timeout conversion and logging/debug output.

## Main Interfaces

`ibt_usec2ib()` converts microseconds to the InfiniBand 6-bit timeout exponent using the protocol formula `time = 4.096us * 2^exp`. `ibt_ib2usec()` converts the exponent back to microseconds.

The logging section defines log levels `IBTF_LOG_L0` through `IBTF_LOG_L5` plus `IBTF_LOG_LINTR`, describing major errors, sysadmin-facing messages, debug traces, and interrupt-context messages. Debug builds expose `ibtl_dprintf_intr()`, `ibtl_dprintf5()`, `ibtl_dprintf4()`, and `ibtl_dprintf3()`; non-debug builds compile these to no-ops. Levels 0 through 2 remain declared through `ibtl_dprintf0()`, `ibtl_dprintf1()`, and `ibtl_dprintf2()`.

## Research Notes

This is a small support header. The timeout conversion functions are used wherever CM/path/channel timers must map between illumos clock values and IB protocol encodings.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_dm_attr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_dm_attr.h

## Purpose

`ib_dm_attr.h` defines InfiniBand Device Management attribute constants and wire-format structures from the IB specification’s device management section.

## Main Content

The header defines Device Management methods, class version, management status bits, and attribute IDs for class port info, notices, IO Unit Info, IOC controller profile, service entries, diagnostic timeout, prepare/test operations, and diagnostic code.

`ib_dm_io_unitinfo_t` describes an IO unit’s change ID, controller slot count, option ROM/diagnostic flags, and packed controller slot list. `ib_dm_ioc_ctrl_profile_t` describes an IOC controller profile with GUID, vendor/device IDs, subsystem IDs, I/O class/subclass, protocol/version, queue depths, message/RDMA sizes, control capability mask, service-entry count, reserved fields, and UTF-8 ID string. `ib_dm_srv_t` describes one service entry with UTF-8 service name and service ID.

## Constants

The file defines IO class values for vendor-specific, none, storage, network, video/multimedia, unknown/multiple, and subclass vendor-specific; controller capability mask values; controller service capability mask values; and service table limits.

## Research Notes

This header is management-plane metadata rather than transport data path. It is storage-relevant because it includes the IB Device Management I/O class value for storage controllers and the IOC service descriptors used to discover services exposed by IB I/O controllers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_dm_attr.h -->