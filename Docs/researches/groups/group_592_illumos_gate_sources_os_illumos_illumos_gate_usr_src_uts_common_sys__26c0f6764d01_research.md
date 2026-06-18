# Group Research: group_592_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__26c0f6764d01

Scope: subset A from `Docs/research_subset_a.md`, covering the listed illumos InfiniBand management headers under `sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_mad.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_mad.h

## Scope

Defines common InfiniBand Management Datagram (MAD) wire-format constants and base structures used by multiple management classes.

## APIs And Structures

- `MAD_SIZE_IN_BYTES` sets the standard MAD size to 256 bytes.
- `ib_mad_hdr_t` defines the common 24-byte MAD header: base/class versions, class, method/response bit, status, class-specific field, transaction ID, attribute ID, and attribute modifier.
- Management class constants cover subnet management, subnet administration, performance, baseboard/device/communication management, SNMP, vendor, and application class ranges.
- Method/status constants define GET, SET, SEND, TRAP, REPORT, trap repress, response methods, and common MAD error statuses.
- Attribute IDs include ClassPortInfo, Notice, and InformInfo.
- `ib_mad_classportinfo_t`, `ib_mad_notice_t`, and `ib_mad_informinfo_t` model IB specification tables for class port info, notices/traps, and trap subscription info.

## Format Details

- Bitfield layouts are defined separately for `_BIT_FIELDS_HTOL` and `_BIT_FIELDS_LTOH`, with a compile-time error if neither endian bitfield convention is selected.
- ClassPortInfo stores redirect/trap GID, LID, P_Key, QP, Q_Key, SL, traffic class, flow label, and hop-limit details.
- Notice encodes generic/vendor notices, producer type or vendor ID, trap/device IDs, issuer identity, notice count/toggle, detail bytes, and issuer GID.
- InformInfo encodes GID/LID ranges, subscription mode, generic/vendor forwarding, trap type/number, destination QPN, response time, and producer type/vendor ID.

## Dependencies

- Includes `sys/ib/ib_types.h` for InfiniBand scalar and address types such as `ib_gid_t`, `ib_lid_t`, `ib_pkey_t`, and `ib_qkey_t`.
- Consumed by IBMF, IBCM, IBDM, IBDMA, and SA-related code that builds or parses management datagrams.

## Risks And Invariants

- These structures mirror on-wire formats; field order, widths, and endian-specific bitfields must remain ABI-compatible with the InfiniBand specification.
- MAD payload users must treat multi-byte fields as wire-format data where required by the surrounding protocol.
- The header intentionally uses C bitfields for packed protocol fields, so all builds must define the correct illumos bitfield ordering macro.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ib_mad.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_arp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_arp.h

## Scope

Defines private IBCM ARP/IP-to-InfiniBand address resolution data structures and prototypes.

## APIs And Structures

- `IBCM_ARP_MAX_IFNAME_LEN` caps interface names at 24 bytes.
- `IBCM_H2N_GID(gid)` converts the two 64-bit halves of an `ib_gid_t` from host to network ordering using 32-bit `ntohl()` pieces.
- Path-record wait queue flags:
  - `IBCM_ARP_PR_RT_PENDING`
  - `IBCM_ARP_PR_RESOLVE_PENDING`
- `ibcm_arp_prwqn_t` tracks an address-resolution wait node, including stream state, user/source/destination/gateway/netmask IP addresses, interface name/protocol, IPoIB source/destination MACs, source/destination GIDs, and `ip2mac_id_t`.
- `ibcm_arp_streams_t` provides a mutex, condition variable, status, done flag, and current wait queue node.
- `ibcm_arp_ip_t` represents an IP-over-IB interface instance with datalink ID, P_Key, HCA GUID, port GID, address family, IPv4/IPv6 socket address, and zone ID.
- `ibcm_arp_ibd_insts_t` stores an allocated array of IPoIB instances.

## Functions

- `ibcm_arp_get_ibaddr()` resolves source/destination IP addresses to source/destination IB GIDs and returns the resolved source IP.
- `ibcm_arp_get_ibds()` discovers IPoIB instances for an address family.
- `ibcm_arp_free_ibds()` releases instance arrays returned by discovery.

## Dependencies

- Includes `ibcm_impl.h`, IPoIB client definitions, `inet/ip2mac.h`, and IPv6 definitions.
- Bridges IBCM connection setup with IP routing, ARP/neighbor resolution, IPoIB MAC addresses, zones, and datalinks.

## Risks And Invariants

- `IBCM_H2N_GID` mutates its argument and assumes the GID halves can be addressed as two 32-bit words.
- Resolution state is synchronized through `ibcm_arp_streams_t` mutex/CV and must keep the wait node valid while asynchronous routing or IP-to-MAC resolution is pending.
- Zone, family, P_Key, and HCA/port GID must match the intended IPoIB interface, or path records may be built for the wrong fabric endpoint.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_arp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_impl.h

## Scope

Private implementation header for the InfiniBand Connection Manager (IBCM). It defines CM state machines, connection and SIDR state records, service registration records, per-HCA/port/QP registries, CM MAD wire structures, timeout/list helpers, global state, and internal function prototypes.

## State Machines And Constants

- `ibcm_conn_state_t` models RC connection establishment, failure, established, teardown, UD SIDR, and delete states.
- `ibcm_ap_state_t` models LAP/APR alternate-path state.
- `ibcm_event_type_t` maps incoming and outgoing CM protocol messages, including stale lookup cases, to internal event values.
- CM attribute IDs are derived from `IBCM_ATTR_BASE_ID` plus the first 11 event values.
- Defines retry, ID allocation, RNR retry, MAD size, MAD header size, and maximum ComID/ReqID/service ID ranges.
- `ibcm_mode_t` distinguishes active and passive CM sides.
- `ibcm_status_t` communicates lookup results, response actions such as send REJ/REP/RTU/APR/SIDR_REP, defer, success, and failure.

## Core Data Structures

- `ibcm_mad_addr_t` records IBMF local/global addressing for received or outgoing CM MADs, including GRH presence, IBMF handle, port number, and CM QP entry.
- `ibcm_state_data_t` is the main RC connection state object. It stores AVL links, local/remote IDs and QPNs, mode/state/AP state, channel, refcount, service ID, client handler, HCA pointer, stored MADs, timeout data, retry counters, QP/path attributes, flow flags, client private data, service info, condition variables, API return pointers, queued open/close links, trace data, request message pointer, and RNR retry count.
- `ibcm_ud_state_data_t` tracks UD SIDR state: request ID, service ID, handler, HCA, stored reply, timeout/retry data, request source address, server-provided QPN/Q_Key, client private data, condition variables, and return data.
- `ibcm_svc_info_t` and `ibcm_svc_bind_t` represent service ID registrations and their bound GID/P_Key/port/service data/name records.
- `ibcm_ar_t` tracks alternate route or address-resolution style service-record state, waiters, rewrite state, owning IBT handles, SA handle, and HCA.
- `ibcm_qp_list_t`, `ibcm_port_info_t`, and `ibcm_hca_info_t` model per-P_Key CM QPs, per-port IBMF/SAA handles, and per-HCA CM state including AVL trees, SIDR list, ID arenas, counters, and port array.

## Wire Formats

Defines on-wire CM message payload structures:

- `ibcm_req_msg_t` for REQ, including service ID, local CA GUID/Q_Key/QPN/EECN, responder/initiator resources, timeout/retry fields, P_Key, MTU/RNR/SRQ bits, primary and alternate path data, and private data.
- `ibcm_mra_msg_t`, `ibcm_rej_msg_t`, `ibcm_rep_msg_t`, `ibcm_rtu_msg_t`, `ibcm_dreq_msg_t`, `ibcm_drep_msg_t`.
- `ibcm_lap_msg_t` and `ibcm_apr_msg_t` for alternate path migration.
- `ibcm_sidr_req_msg_t` and `ibcm_sidr_rep_msg_t` for UD service-ID resolution.
- `ibcm_classportinfo_msg_t` for CM ClassPortInfo response data.
- `ibcm_ip_pvtdata_t` for RDMA CM IP private data, with endian-specific bitfields and IPv4 aliases into IPv6 addresses.

## Internal APIs

- IBMF receive callback: `ibcm_recv_cb()`.
- Per-message state handlers: `ibcm_process_req_msg()`, `rep`, `rtu`, `dreq`, `drep`, `rej`, `mra`, `apr`, `lap`, `sidr_req`, and `sidr_rep`.
- CEP/QP transition helpers process REQ/REP/RTU/REJ/LAP/APR/DREQ and client callback results.
- MAD posting helpers build reply addresses and post/resend REJ, REP, RTU, DREQ, DREP, LAP, APR, MRA, SIDR_REQ, and SIDR_REP messages through IBMF.
- Lookup/lifetime helpers manage RC state AVL entries, SIDR list entries, service entries, ComIDs, ReqIDs, local/IP service IDs, transaction IDs, HCA references/resources/services, and timeout-list processing.
- SA and path helpers include SA access throttling/contact, node info lookup, path cache init/fini/purge, service-data swizzling, AR init/fini, and IP debug printing.

## Synchronization

- `state_mutex` protects RC state, refcounts, timers, retry counters, callback proceed flags, and MRA/abort fields.
- `ud_state_mutex` protects SIDR state, refcount, timer, retry, send flags, and blocking state.
- HCA AVL trees are protected by `hca_state_rwlock`; SIDR lists by `hca_sidr_list_lock`.
- Service rewrite and unbind paths coordinate through `ibcm_svc_info_lock` and `ibcm_svc_info_cv`.
- Global locks cover HCA list/counters, QP list, multicast group list, receive path, and timeout list.
- Lock order annotations document state-lock to timeout-list ordering and HCA-tree/SIDR-list locks before state locks.

## Dependencies

- Relies on IBTL private CM interfaces, IBMF, IBMF SAA, kernel AVL/vmem/taskq/timeout primitives, IP definitions, and CM public data from IBT.
- Stores IBMF messages directly and reuses IBMF callbacks for asynchronous send completion and receive dispatch.
- Uses SA records for service registration rewrite and path/service lookup behavior.

## Risks And Invariants

- State object lifetime depends on refcounts plus delayed timeout-list deletion; `delete_state_data` and `ud_delete_state_data` defer freeing until references drain.
- Timers store expected CM/AP states to validate callbacks against current state before retransmitting or failing a connection.
- AVL lookup keys differ by active/passive path and message type; incorrect tree choice can misidentify duplicate, stale, or valid messages.
- Stored MADs and send flags must remain synchronized with IBMF completions and timeout retransmits.
- Service record rewrite state must prevent unbind from freeing records while SA rewrite is in progress.
- CM MAD structures are wire contracts; packed bit fields and byte-array GIDs/SIDs exist to handle non-aligned protocol fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_trace.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_trace.h

## Scope

Defines internal per-connection tracing support for IBCM RC connection state processing.

## APIs And Structures

- `ibcm_state_rc_trace_qualifier_t` enumerates trace event qualifiers for:
  - Initial displayed identifiers such as SID, channel, local/remote ComID, QPN, and timestamp.
  - Incoming CM MADs: REQ, REP, RTU, COMEST, MRA, REJ, LAP, APR, DREQ, DREP.
  - Outgoing CM MADs: REQ, REP, RTU, LAP, APR, MRA, REJ, DREQ, DREP.
  - IBMF send completions for corresponding messages.
  - REP timeout, client callback entry/return events, QP state transitions, error/set-alt transitions, stale detection, and retry events.
- `IBCM_MAX_CONN_TRCNT` defaults per-connection trace chunks to 40 events.
- `IBCM_DEBUG_BUF_SIZE` defines a 4096-byte debug buffer.
- `tm_diff_type` is `uint32_t`, with `TM_DIFF_MAX` as `UINT32_MAX`.
- `ibcm_conn_trace_t` stores base time, event array, event time deltas, current index, and allocated trace count.

## Functions And Globals

- `ibcm_insert_trace()` records a trace event for a connection state object.
- `ibcm_dump_conn_trace()` dumps the trace into `ibtf_debug_buf`.
- Extern globals include `ibcm_debug_buf`, trace mutexes, maximum trace count, trace enable flags, and `event_str[]`.

## Dependencies

- Referenced by `ibcm_state_data_t` in `ibcm_impl.h`.
- Uses kernel time (`hrtime_t`) and mutex primitives.

## Risks And Invariants

- Trace arrays are dynamically sized per connection and indexed by an 8-bit `conn_trace_ind`, so configured trace counts must fit intended indexing behavior.
- Timing deltas are limited to `uint32_t`; overflow needs to be tolerated or clamped by implementation.
- Trace control is global through `ibcm_enable_trace`, with separate mutexes for trace state and print serialization.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_ibnex.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_ibnex.h

## Scope

Private interface between the InfiniBand Device Manager (IBDM) and the IB nexus driver. It exposes discovery status, HCA/port/IOC/IOU data structures, event callbacks, and query/free routines used by the nexus.

## APIs And Structures

- `ibdm_status_t` returns `IBDM_SUCCESS` or `IBDM_FAILURE`.
- `ibdm_events_t` reports HCA add/remove, IOC property update, port up, and port P_Key change events to IB nexus.
- `ibdm_ibnex_get_ioclist_mtd_t` controls IOC list behavior: normal probe, no probe, or reprobe all.
- `ibdm_timeout_cb_args_t` carries timeout callback context for GID, request type, IOC number, retry count, and service-entry range.
- `ibdm_srvents_info_t` stores service-entry state, attributes, timeout ID, and callback args.
- `ibdm_ioc_info_t` stores IOC controller profile, service entries, GID list, IOU GUID, timeout IDs, diagnostic-code state, previous reprobe data, update payload, and reachable HCA list.
- `ibdm_iou_info_t` stores IOUnitInfo, IOC array, IOU GUID, diagnostic code, and probe progress count.
- `ibdm_pkey_tbl_t`, `ibdm_port_attr_t`, and `ibdm_hca_list_t` describe P_Key/QP mappings, port attributes, and HCA list entries.
- `ibdm_callback_t` is the IB nexus notification function type.

## Functions

- Callback registration: `ibdm_ibnex_register_callback()` and `ibdm_ibnex_unregister_callback()`.
- Port probing/query/free: `ibdm_ibnex_probe_hcaport()`, `ibdm_ibnex_get_port_attrs()`, `ibdm_ibnex_free_port_attr()`.
- IOC probing/list/query/free: `ibdm_ibnex_probe_ioc()`, `ibdm_ibnex_get_ioc_count()`, `ibdm_ibnex_get_ioc_list()`, `ibdm_ibnex_get_ioc_info()`, `ibdm_ibnex_free_ioc_list()`.
- HCA list/query/free: `ibdm_ibnex_get_hca_list()`, `ibdm_ibnex_get_hca_info_by_guid()`, `ibdm_ibnex_free_hca_list()`.
- Maintenance: `ibdm_ibnex_update_pkey_tbls()` and `ibdm_ibnex_port_settle_wait()`.

## Dependencies

- Includes IBTL common types, IBMF client interface, and IB Device Management attributes.
- Uses timeout IDs, IBTF handles, SAA handles, IBMF handles, and property update payload types.

## Risks And Invariants

- Many returned objects are allocated copies and must be freed through the matching `ibdm_ibnex_free_*()` routine.
- Several structures are annotated as serialized by condition variables, not by embedded locks; callers must respect the implementation’s serialization contract.
- IOC reprobe state preserves previous service/GID data and update payload masks, so copy/free paths must retain both current and previous views until consumers finish comparing them.
- Port/HCA reachability affects nexus-visible IOC property updates; stale HCA lists can make devices appear or disappear incorrectly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_ibnex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_impl.h

## Scope

Private implementation header for IBDM. It defines Device Management request types, GID probe state, global module state, transaction-ID layout, DM MAD sizing, timeout defaults, message access macros, debug hooks, and helper types.

## APIs And Structures

- Request type flags identify ClassPortInfo, IOUnitInfo, IOCInfo, service entries, IOU diagnostic code, and IOC diagnostic code requests.
- `ibdm_taskq_args_t` carries IBMF handle, message, and opaque args into taskq processing.
- GID probe state flags model discovery progress from not-done through ClassPortInfo, IOUnitInfo, IOC details, completion, skipped, failed, and Cisco set-ClassPortInfo activation.
- Cisco FC gateway constants identify a special vendor/device combination and define OUI extraction from GUIDs.
- `ibdm_gid_t` is a linked-list node containing destination GID high/low halves.
- `ibdm_dp_gidinfo_t` is the per-Device-Protocol-GID probe object: mutex, state, reprobe flag, IOU pointer, pending command count, QP handle, transaction ID bounds, LIDs/GIDs/GUIDs/P_Key, redirect info, IBMF/SAA handles, timeouts, GID list, response timeout, IOC count, HCA list, previous IOU, Cisco probe CV/flags, and SL fields.
- `ibdm_t` is global IBDM state: global mutexes, HCA list, GID probe list, CVs, probe/busy counters, transaction ID counter, IBT client handle, registered ibnex callback, and previous-IOU flag.
- `ibdm_saa_event_arg_t` packages SAA event callback information for taskq use.

## Constants And Macros

- Transaction IDs are split into upper 32 bits per GID and lower 32 bits per MAD using `IBDM_GID_TRANSACTIONID_SHIFT` and mask.
- DM MAD size is 256 bytes, with a 40-byte Device Management MAD header after the common MAD/RMPP/access-key fields.
- Defaults include 4-second timeout and 3 retries.
- `IBDM_TIMEOUT_VALUE(t)` converts seconds to ticks.
- `IBDM_OUT_IBMFMSG_MADHDR`, `IBDM_IN_IBMFMSG_MADHDR`, status/attr/attrmod, and payload-cast macros simplify IBMF message parsing.
- `IBDM_GIDINFO2IOCINFO()` indexes IOU IOC arrays.
- `IBDM_IS_IOC_NUM_INVALID()` validates IOC slot numbers.
- `IBDM_INVALID_PKEY()` recognizes invalid full or limited P_Key values.

## Dependencies

- Includes `ibdm_ibnex.h` and IBTL implementation utility headers.
- Depends on IBMF message layout, SAA handles/events, IB DM attributes, and byte-order helpers such as `b2h16()` and `b2h32()`.

## Risks And Invariants

- `gl_mutex` protects GID probe state, timeout ID, pending commands, and nested IOC/service timeout IDs.
- Global `ibdm_mutex`, HCA-list mutex, and ibnex callback mutex protect distinct parts of module state; lock-order annotation requires global state before GID state.
- Transaction-ID uniqueness depends on bounded practical assumptions for GID count and per-GID MAD count.
- Redirect fields must be honored after ClassPortInfo redirect, or subsequent DM MADs may be sent to the wrong destination.
- Debug dump functions compile to no-ops outside DEBUG builds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma.h

## Scope

Public client API for the InfiniBand Device Management Agent (IBDMA), used by protocol transports that provide I/O Controller profiles and services.

## APIs

- `ibdma_status_t` reports success, duplicate IOC GUID, full IOU, bad IOC profile, or bad parameter.
- `ibdma_hdl_t` is an opaque provider handle returned when an IOC registers.
- `ibdma_ioc_register()` registers an IOC GUID, IOC controller profile, and service entries, returning a handle.
- `ibdma_ioc_unregister()` removes a registered IOC.
- `ibdma_ioc_update()` updates a registered IOC profile and services.

## Behavior

- IBDMA manages an I/O Unit per IB HCA and responds to Device Management requests on all fabric ports.
- By default the IOUnit has no IOCs. Transport protocols register their IOCs and service entries, and IBDMA assigns IOUnit slots.
- Protocol transports call back into IBDMA as profile or service data changes.

## Dependencies

- Includes IBMF and IB Device Management attribute definitions.
- The profile and service records are IB DM wire/domain structures.

## Risks And Invariants

- IOC GUIDs must be unique; duplicates return `IBDMA_IOC_DUPLICATE`.
- The IOUnit has a finite slot count enforced by the implementation.
- Consumers must retain and use only valid `ibdma_hdl_t` handles returned from registration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma_impl.h

## Scope

Private IBDMA implementation header defining HCA, port, IOC slot, provider handle, and module state structures.

## APIs And Structures

- Constants define MAD size, DM MAD header size, response time, and `IBDMA_MAX_IOC` of 16.
- `ibdma_hdl_impl_t` maps a consumer handle to IOU GUID and IOC slot index.
- `ibdma_ioc_t` represents one IOC slot: in-use flag, slot number, owning HCA pointer, network-order IOC profile, and service-entry pointer.
- `ibdma_port_t` stores per-port IBMF handle, registration info, implementation capabilities, and parent HCA pointer.
- `ibdma_hca_t` stores list linkage, IBT HCA handle, registered consumer handle list, IOU GUID, network-order IOUnitInfo, IOC slot array, port count, and flexible per-port array.
- `ibdma_mod_state_t` stores the IBT client handle, HCA list lock/list, and HCA count.
- `ibdma_ioc_state_t` defines IOC slot states plus `IBDMA_HDL_MAGIC`.
- Static helpers `ibdma_set_ioc_state()` and `ibdma_get_ioc_state()` manipulate IOC state in an HCA slot.

## Dependencies

- Includes IB verbs transport interface, IB DM attributes, and common MAD definitions.
- Uses kernel `list_t`, `list_node_t`, `kmutex_t`, and `krwlock_t`.

## Risks And Invariants

- The HCA list lock is explicitly used instead of per-HCA reference counts to keep HCA objects alive during consumer operations.
- IOC profiles are stored in network order; update and response code must avoid mixing host-order and wire-order fields.
- `ih_iou_rwlock` protects IOUnit and IOC slot state exposed to fabric requests.
- The header has `#ifdef __cpluplus`, likely a typo for `__cplusplus`; this only affects C++ linkage guards.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf.h

## Scope

Public IBMF client interface for registering InfiniBand management clients, sending/receiving MADs or UD traffic, managing asynchronous callbacks, allocating messages, and allocating/modifying/freeing alternate QPs.

## Public Types And Constants

- Defines IBMF status codes from `IBMF_SUCCESS` through transport, timeout, validation, callback, and transaction-ID errors.
- `IBMF_VERSION` is 1.
- `ibmf_handle_t` and `ibmf_qp_handle_t` are opaque handles; `IBMF_QP_HANDLE_DEFAULT` is the default special QP handle.
- `ibmf_client_type_t` enumerates management class/client role combinations: subnet agent/manager, SA, performance, baseboard, device, communication, SNMP, vendor ranges, application ranges, and universal class.
- `ibmf_retrans_t` defines retries, response time, round-trip time, and transaction timeout parameters.
- `ibmf_register_info_t` identifies HCA/port and client class.
- `ibmf_impl_caps_t` advertises whether default and non-default QP handles support arbitrary P_Key/Q_Key use.
- `ibmf_async_event_t` currently defines `IBMF_CI_OFFLINE`.
- `ibmf_async_event_cb_t` and `ibmf_msg_cb_t` define asynchronous interface and message callbacks.

## Main APIs

- `ibmf_register()` registers one management class on one port, with RMPP/offload flags and an async event callback.
- `ibmf_unregister()` unregisters a client and invalidates the handle.
- `ibmf_setup_async_cb()` installs an unsolicited receive callback for a handle/QP pair.
- `ibmf_tear_down_async_cb()` removes that callback.
- `ibmf_msg_transport()` sends a message synchronously or asynchronously, optionally sequenced and/or RMPP.
- `ibmf_alloc_msg()` and `ibmf_free_msg()` allocate and release IBMF message contexts.
- `ibmf_alloc_qp()`, `ibmf_query_qp()`, `ibmf_modify_qp()`, and `ibmf_free_qp()` manage alternate QPs.

## Behavioral Contracts

- Clients must register before sending or receiving management packets.
- A class can generally be registered once per port, except `UNIVERSAL_CLASS`, which permits multiple clients and should use alternate QPs only.
- Clients whose classes include an RMPP header must register with `IBMF_REG_FLAG_RMPP`.
- Callbacks may be invoked before setup/register/transport calls return; clients must tolerate early callback ordering.
- Message receive buffers supplied by IBMF must be freed with `ibmf_free_msg()`.
- Reusing receive buffers for send is only allowed for non-sequenced operations; sequenced reuse returns `IBMF_REQ_INVALID`.
- Default QP usage is constrained by registered MAD class and implementation P_Key/Q_Key capabilities.

## Flags

- Registration flags: `IBMF_REG_FLAG_RMPP`, `IBMF_REG_FLAG_NO_OFFLOAD`, `IBMF_REG_FLAG_SINGLE_OFFLOAD`.
- Transport flags: `IBMF_MSG_TRANS_FLAG_RMPP`, `IBMF_MSG_TRANS_FLAG_SEQ`.
- Alternate QP allocation flags: `IBMF_ALT_QP_MAD_NO_RMPP`, `IBMF_ALT_QP_MAD_RMPP`, `IBMF_ALT_QP_RAW_ONLY`.

## Dependencies

- Includes IB types, packet headers, common MAD definitions, IBMF message structures, SAA API, and utilities.
- Public API is used by CM, DM, DMA, SAA, and management agents/managers.

## Risks And Invariants

- `ibmf_unregister()` fails with `IBMF_BUSY` while messages, callbacks, or QPs remain active.
- Callback functions are expected not to block in unsolicited message callbacks, though IBMF does not enforce it.
- Alternate QP P_Key/Q_Key may be modified concurrently by another thread, so query/transport validation can race with caller behavior.
- Buffer ownership is split: clients own send buffers; IBMF owns receive buffers.
- Raw UD traffic has separate size and buffer-layout requirements from MAD traffic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_impl.h

## Scope

Private IBMF implementation header defining internal QP, message, client, channel interface, WQE, UD destination, RMPP, taskq, kstat, state, and helper function contracts.

## Core Structures

- `ibmf_wqe_mgt_t` tracks WQE memory allocation, registered IB memory, lkey, MR handle, and mutex.
- `ibmf_qp_t` tracks special QPs: IBT QP handle, port/QP number, reference count, flags, posted receive WQEs, and mutex.
- `ibmf_alt_qp_t` tracks alternate QPs: IBT QP, sizes, owning client, receive callback, teardown CV, state flags, active send/receive counters, QPN, P_Key/Q_Key, port, RMPP support, SQD CV, WQE counts, WQE caches, vmem arena, and WQE management list.
- `ibmf_msg_impl_t` extends public `ibmf_msg_t` with list links, client/QP/UD destination, callback, TID, management class, mutex, state flags, RMPP context, retransmission data, timeout IDs, refcount, unsolicited flag, and pending send completions.
- `ibmf_client_t` tracks a registered client, taskqs, message lists, async event callback, unsolicited receive callback, client class info, special QP, CI handle, flags, registration flags, stats, base LID, and kstat pointer.
- `ibmf_send_wqe_t` and `ibmf_recv_wqe_t` wrap IBT send/receive work requests with memory registration, QP, port, message, status, and RMPP segment metadata.
- `ibmf_ci_t` represents one channel interface/HCA context with clients, QPs, CQs, PD, UD dest pool, WQE caches, HCA identity, refcount/state, wait CVs, WQE cleanup coordination, and port kstats.
- `ibmf_state_t` is global IBMF state: CI list, IBT handle, CQ handler, global mutex, module info, and fallback taskq.

## Macros And State Flags

- Defines queue sizes, WQE memory size, management Q_Key, default P_Key values, P_Key masks, and taskq sizing.
- Work request IDs mark receive completions with bit 0.
- Message flags track queued/done/blocking, sequenced, send/receive RMPP, busy/free/on-list, and termination.
- Transaction flags track uninitialized/init/wait/done/signaled/timeout/recv/send completion states.
- Client flags track active receive/send callbacks and callback teardown.
- CI flags and states track initialization, validation, invalidation, uninitialization, present/inited/gone states, and waiters.
- Callback setup/cleanup macros update active callback counts and kstats and signal teardown CVs when active callbacks drain.

## Internal APIs

- CI validation/acquire/release, client allocation/add/delete/lookup, QP allocation/query/modify/free and P_Key mapping.
- Packet send, UD destination allocation/free/pooling, WQE allocation/free/posting, completion handling, loopback detection, status conversion.
- Message initialization, client message list management, allocation/free, transport, refcount decrement, send/receive completion, and error receive-buffer setup.
- Transaction termination, client notification, sequence notification, timer set/unset/timeout callbacks.
- RMPP detection, message lookup, RMPP receive handling, RMPP send/window/termination setup.
- Alternate QP WQE cache constructors/destructors and WQE-cache extension.
- Receive callback setup/cleanup and UD destination population task dispatch.

## Dependencies

- Includes kernel module/DDI/taskq/synchronization headers, IBT verbs transport, public IBMF, RMPP, kstat, and trace headers.
- Uses IBT CQs, QPs, PDs, memory registration, UD destinations, work completions, and async HCA events.

## Risks And Invariants

- `im_mutex` protects transaction state, receive buffers, status, flags, and RMPP context.
- Client message lists are separately protected by `ic_msg_mutex`; callback and allocation state by `ic_mutex`.
- CI state and client/QP lists have distinct locks and CVs; teardown must drain active callbacks, WQEs, messages, QPs, and references in order.
- UD destination pool high/low watermarks are tuned to avoid long refill stalls while preserving stress capacity.
- WQE memory is registered with IBT and tracked by both kernel virtual allocation and IB virtual memory arenas; leaks or premature free would corrupt transport operations.
- RMPP message matching must use TID, class, method, LID/GID, and RMPP header state to distinguish transactions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_kstat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_kstat.h

## Scope

Defines IBMF kstat data structures and convenience macros for updating client and port statistics.

## Structures

- `ibmf_port_kstat_t` tracks clients registered, registration failures, allocated send/receive WQEs, and WQE allocation failures.
- `ibmf_kstat_t` tracks allocated/active/sent/received messages, active sends/receives, allocated UD destinations and alternate QPs, active callbacks, receive buffers, allocation failures, send packet failures, and RMPP errors.

## Macros

- `IBMF_ADD32_KSTATS()` and `IBMF_SUB32_KSTATS()` adjust a 32-bit client kstat field if client and kstat pointer are valid.
- `IBMF_ADD32_PORT_KSTATS()` and `IBMF_SUB32_PORT_KSTATS()` adjust a 32-bit port kstat field if CI/port kstat pointer is valid.

## Dependencies

- Assumes `kstat_named_t` and illumos kstat structures.
- Macros expect client objects with `ic_kstatp` and CI/port objects with `ci_port_kstatp`.

## Risks And Invariants

- Macros do not acquire locks; callers must hold the relevant kstat mutex where required.
- Counters are plain 32-bit kstat fields and can wrap under sustained long-running activity.
- Field names are macro parameters, so incorrect names fail at compile time but wrong counter choice is a caller responsibility.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_kstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_msg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_msg.h

## Scope

Defines the public IBMF message, local/global address, and message buffer structures used by `ibmf_msg_transport()` and receive callbacks.

## Structures

- `IBMF_MAD_SIZE` is 256 bytes.
- `ibmf_addr_info_t` stores local LID, remote LID, remote QPN, P_Key, Q_Key, and 4-bit service level.
- `ibmf_global_addr_info_t` stores sender/receiver GIDs, flow label, traffic class, and hop limit.
- `ibmf_msg_bufs_t` splits a message into MAD header, class header, and class data buffers with lengths.
- `ibmf_msg_t` contains local/global address info, completion status, message flags, message size limit, send buffers, and receive buffers.

## Buffer Contracts

- The MAD header is normally 24 bytes and may be NULL only for raw UD traffic over an appropriately allocated non-special QP.
- The class header may be separate or combined with class data by leaving `im_bufs_cl_hdr` NULL.
- For raw UD sends, the entire packet is supplied as class data and MAD/class header pointers should be NULL.
- MAD header, class header, and class data buffers contain IB wire-format big-endian data.
- Other fields in `ibmf_msg_t` are host-format.

## Dependencies

- Uses `ib_mad_hdr_t` from `ib_mad.h` and IB addressing scalar types.
- Included by public IBMF API and private implementation.

## Risks And Invariants

- Send buffers are client-owned; receive buffers are IBMF-owned.
- `im_msg_flags` must include `IBMF_MSG_FLAGS_GLOBAL_ADDRESS` when global address data is valid.
- Local/remote LID semantics reverse depending on send path versus receive callback context.
- Class-header offset/length must match the specific management class, especially for RMPP-capable classes where the RMPP header is not part of the class header buffer.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_rmpp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_rmpp.h

## Scope

Defines private IBMF Reliable Multi-Packet Protocol (RMPP) context, header, states, packet types, flags, and status values.

## Structures And Constants

- `ibmf_rmpp_ctx_t` tracks send window first/last/next, expected receive segment, direction switch, new window last, payload length, state, retry count, packet data sizes, number of packets, data offset, cached header words, packet type, response time, flags, and status.
- RMPP states include undefined, sender active, sender switch, receiver active, receiver terminate, abort, and done.
- `IBMF_CTX_RMPP_FLAGS_DYN_PYLD` marks dynamic payload.
- Default response time values and method response bit constants are defined.
- `ibmf_rmpp_hdr_t` models the IB RMPP header with version, type, response time/flags bitfields, status, segment number, and payload-length/new-window-last field.
- Header bitfield order changes for `_BIT_FIELDS_HTOL` versus the default low-to-high layout.

## Protocol Values

- Types: none, data, ACK, STOP, ABORT.
- Flags: active, first packet, last packet.
- Statuses: normal, resources exhausted, total time too long, inconsistent last/payload length, inconsistent first/segment number, bad type, window too small, segment too big, illegal status, unsupported version, too many retries, unspecified error.
- `IBMF_RMPP_VERSION` is 1 and default window size is 5.

## Dependencies

- Embedded in `ibmf_msg_impl_t`.
- Used by IBMF RMPP send/receive helpers declared in `ibmf_impl.h`.

## Risks And Invariants

- Window and expected-segment fields drive retransmission and ACK behavior; off-by-one errors can stall or corrupt multi-packet transfers.
- Header status/type/flag values are wire protocol constants and must stay spec-compatible.
- Payload lengths and last-packet sizes must be consistent with segmented buffer offsets.
- Bitfield ordering must match target architecture conventions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_rmpp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa.h

## Scope

Public IBMF Subnet Administration Access (SAA) interface for opening SA sessions, issuing SA queries/updates/deletes, subscribing to subnet events, and using helper query functions.

## Public Types

- `IBMF_SAA_PKEY_WC` and `IBMF_SAA_MTU_WC` are wildcard values for P_Key and MTU.
- `ibmf_saa_access_type_t` selects retrieve, update, or delete.
- `ibmf_saa_handle_t` is an opaque SAA session handle.
- `ibmf_saa_cb_t` is the asynchronous SA access callback, returning length, host-endian unpacked result, and IBMF status.
- `ibmf_saa_access_args_t` contains SA attribute ID, access type, component mask, template pointer/length, callback, and callback arg.
- `ibmf_saa_subnet_event_t` enumerates GID available/unavailable, multicast group create/delete, capability mask change, system image GUID change, and subscription status change.
- `ibmf_saa_event_details_t` carries event-specific GID, system image GUID, capability mask, LID, or producer status mask.
- `ibmf_saa_subnet_event_cb_t` and `ibmf_saa_subnet_event_args_t` define event callback registration.

## Main APIs

- `ibmf_sa_session_open()` registers an SAA consumer on a port GUID, optionally with subnet event subscription and SM key.
- `ibmf_sa_session_close()` unregisters a consumer and cancels outstanding callbacks before returning.
- `ibmf_sa_access()` performs generic SA retrieve/update/delete operations, synchronously if no callback is supplied.
- Helpers:
  - `ibmf_saa_gid_to_pathrecords()`
  - `ibmf_saa_paths_from_gid()`
  - `ibmf_saa_name_to_service_record()`
  - `ibmf_saa_id_to_service_record()`
  - `ibmf_saa_update_service_record()`

## Event Behavior

- SAA subscribes with the SA for CA, switch, router, and subnet-management trap producer types.
- Subscription failures are reported as `IBMF_SAA_EVENT_SUBSCRIBER_STATUS_CHG` with a producer status mask.
- Event callbacks may occur before `ibmf_sa_session_open()` returns.
- Event callbacks are dispatched on separate threads, may be out of order, and may not be generated under heavy load.

## Dependencies

- Includes IB types and SA record definitions.
- Returns unpacked, host-endian SA record structures from `sa_recs.h`.

## Risks And Invariants

- Successful query results allocate buffers that the consumer must free.
- `ibmf_sa_access()` returns zero length on failure or no records.
- Callback ordering is intentionally weak; consumers must not infer strict event order.
- Session close must synchronize with outstanding asynchronous callbacks before invalidating the handle.
- Unknown SA attributes require caller-provided wire-format template length because SAA cannot pack unknown records.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_impl.h

## Scope

Private SAA implementation header defining per-port/client state, kstats, transaction context, event taskq arguments, constants, and implementation function prototypes.

## Structures And State

- Constants define max clients per port, MAD base/class versions, retry/time limits, busy retry count, and wait times.
- `saa_port_state_t` tracks registering, ready, invalid, and purging port states.
- `saa_port_t` stores list linkage, mutex/CV, state/reference count, port GUID, IBMF registration info/handle/caps/QP, timeout/class capability data, IBMF address/global address/message flags, redirect state, retransmission settings, current TID, outstanding transaction count, kstats, event-subscription masks/client list, node GUID/port number, and latest SA uptime.
- `ibmf_saa_kstat_t` tracks clients registered, failed registrations, outstanding/total/failed/timed-out requests.
- `saa_client_state_t` tracks active, waiting, and closed clients.
- `saa_client_data_t` stores handle signature, port pointer, mutex, pending transaction count, state CV/state, SM key, active event callback count/CV, and event callback info.
- `saa_state_t` stores global port list, lock, and event taskq.
- `saa_impl_trans_info_t` groups all fields for an SA transaction: client/port, request attribute/mask/template/method, async callback, sync result storage, InformInfo subscription metadata, unsubscribe sequencing, saved transport flags, busy retry count, and send time.
- `ibmf_saa_event_taskq_args_t` packages event callback dispatch.

## Functions

- Init/fini/purge and validation: `ibmf_saa_impl_init()`, `ibmf_saa_impl_fini()`, `ibmf_saa_is_valid()`, `ibmf_saa_impl_purge()`.
- Port/client setup: add client, create port, init kstats, mark registration failed, register port, get ClassPortInfo.
- Transaction send: `ibmf_saa_impl_send_request()` and `ibmf_saa_async_cb()`.
- Event subscription and notification: add subscriber, subscribe/unsubscribe events, subscribe SM events, notify clients, and `ibmf_saa_report_cb()` for report handling.

## Dependencies

- Includes public SAA API and IBMF private implementation.
- Uses IBMF handles/QPs/retransmission, kstats, taskqs, mutexes/CVs, and MAD notice structures.

## Risks And Invariants

- `saa_pt_mutex` protects port reference count, retransmission/address/redirect/TID/outstanding state.
- Registration synchronization allows only one client to perform IBMF registration for a shared port.
- Event subscription masks track arrivals and successes per producer type; status-change events depend on comparing masks over time.
- `saa_impl_trans_info_t` lifetime differs between sync and async transactions: sync freed by `ibmf_access_sa()`, async by the IBMF transport callback.
- Busy SA responses are retried with a bounded counter and sleep interval.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_utils.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_utils.h

## Scope

Declares SAA utility functions for packing/unpacking SA headers and payloads and parsing selected subnet-management trap buffers.

## APIs

- `ibmf_saa_utils_pack_sa_hdr()` packs an `ib_sa_hdr_t` into a wire-format class header buffer.
- `ibmf_saa_utils_unpack_sa_hdr()` unpacks a wire-format class header buffer into an `ib_sa_hdr_t`.
- `ibmf_saa_utils_unpack_payload()` converts wire-format SA payload bytes into host-format record structures for a given attribute ID, attribute offset, and response type.
- `ibmf_saa_utils_pack_payload()` converts host-format payload structures into wire-format SA payload bytes.
- Trap parsers:
  - `ibmf_saa_gid_trap_parse_buffer()`
  - `ibmf_saa_capmask_chg_trap_parse_buffer()`
  - `ibmf_saa_sysimg_guid_chg_trap_parse_buffer()`

## Dependencies

- Includes `sys/ib/mgt/sa_recs.h`.
- The header states the packing definitions are based on InfiniBand specification version 1.1 and must be updated with spec changes.

## Risks And Invariants

- Correct packing depends on attribute ID and known SA record layout; unknown or changed attributes require utility updates.
- Callers control allocation behavior through `km_sleep_flag`.
- Trap parsers assume buffers contain the expected trap record format.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_saa_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_trace.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_trace.h

## Scope

Defines IBMF trace/debug print levels and trace macros.

## APIs And Macros

- Trace levels:
  - `DPRINT_L0`: no messages
  - `DPRINT_L1`: major errors
  - `DPRINT_L2`: minor errors
  - `DPRINT_L3`: general debug
  - `DPRINT_L4`: general trace
- `IBMF_TRACE_0` through `IBMF_TRACE_5` conditionally call `ibmf_dprintf()` when `ibmf_trace_level > 0`.
- `ibmf_dprintf(int l, const char *fmt, ...)` is the underlying debug print function.

## Dependencies

- Relies on an external `ibmf_trace_level` variable defined elsewhere.
- Used by IBMF implementation code for compile-time consistent probe-style trace calls.

## Risks And Invariants

- The first macro arguments preserve a probe-like calling convention, but only format string and selected values are passed to `ibmf_dprintf()`.
- Macros do not wrap bodies in `do { } while (0)`, so use in conditional statements requires care.
- Trace cost is gated only by `ibmf_trace_level > 0`; level filtering is performed by `ibmf_dprintf()` or below.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_utils.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_utils.h

## Scope

Declares generic IBMF helper functions for packing and unpacking management datagram data.

## APIs

- `ibmf_utils_unpack_data()` unpacks raw MAD bytes into a host structure according to a format string, with source data and destination structure lengths.
- `ibmf_utils_pack_data()` packs a host structure into raw MAD bytes according to a format string, with structure and destination data lengths.

## Dependencies

- Used by IBMF/SAA code that needs structured conversion between host data and IB wire-format buffers.
- Format-string semantics are implemented in the corresponding source file, not this header.

## Risks And Invariants

- Callers must pass correct format strings and matching buffer sizes.
- These helpers are a central boundary between host-endian structures and MAD wire-format byte arrays.
- Incorrect lengths or format descriptors can corrupt protocol buffers or truncate decoded data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_utils.h -->