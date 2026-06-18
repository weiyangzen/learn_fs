# Group Research: group_593_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__bef929523b7d

Scope: `Docs/research_subset_a.md`; source tree `sources/os/illumos/illumos-gate` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sa_recs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sa_recs.h

This header defines InfiniBand Subnet Administration record wire layouts from IB spec volume 1, release 1.1, chapter 15. It is a pure ABI/header definition file: no executable code, but many structs and component-mask constants used to form SA MAD queries and responses.

Key definitions:
- `ib_sa_hdr_t` is the SA MAD class header with `SM_KEY`, `AttributeOffset`, `Reserved`, and `ComponentMask`.
- Defines SA methods such as `SA_SUBN_ADM_GET`, `SA_SUBN_ADM_SET`, `SA_SUBN_ADM_GET_TABLE`, `SA_SUBN_ADM_GET_MULTI`, `SA_SUBN_ADM_DELETE`, and response variants.
- Defines SA MAD status codes and mask: `SA_STATUS_NO_ERROR`, resource/request/no-records/too-many-records/GID/component errors, and `SA_STATUS_ERROR_MASK`.
- Defines SA class port capability bits for optional records, UD multicast, multipath, and reinit support.
- Defines SA attribute IDs for ClassPortInfo, Notice, NodeRecord, PortInfoRecord, forwarding table records, SMInfo, ServiceRecord, PathRecord, MCMemberRecord, TraceRecord, MultiPathRecord, and ServiceAssociationRecord.

Record layouts:
- Topology and node data: `sa_node_record_t`, `sa_portinfo_record_t`, `sa_SLtoVLmapping_record_t`, `sa_switchinfo_record_t`, `sa_linearft_record_t`, `sa_randomft_record_t`, `sa_multicastft_record_t`, `sa_VLarb_table_record_t`, `sa_sminfo_record_t`, `sa_pkey_table_record_t`, `sa_guidinfo_record_t`, `sa_trace_record_t`.
- Subscription and service data: `sa_informinfo_record_t`, `sa_link_record_t`, `sa_service_record_t`, `sa_service_assn_record_t`.
- Pathing and multicast: `sa_path_record_t`, `sa_mcmember_record_t`, `sa_multipath_record_t`.

Layout/portability notes:
- Several records use endian-sensitive C bitfields guarded by `_BIT_FIELDS_HTOL` and `_BIT_FIELDS_LTOH`, inherited from `sys/isa_defs.h`.
- The file contains compile-time `#error` guards if no bitfield direction macro is defined.
- Component-mask constants map bit positions to every field in each SA record and are critical for SA queries.

Dependencies:
- Includes `sys/ib/ib_types.h` and `sys/ib/mgt/sm_attr.h`.
- Reuses SM attribute structures such as `sm_nodeinfo_t`, `sm_portinfo_t`, forwarding tables, P_Key tables, and GUID info.

Relevance:
- Important for InfiniBand fabric discovery and management, not directly filesystem-specific.
- In this subset it matters as OS/kernel storage-network substrate: InfiniBand/iSER and similar transports can support block/storage paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sa_recs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sm_attr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sm_attr.h

This header defines InfiniBand Subnet Management attributes from IB spec volume 1, release 1.1, chapter 14. It is a wire-layout and constants header for SMP/MAD subnet management.

Key definitions:
- `SM_MAX_DR_PATH` is 64.
- SMP class headers: `sm_lid_class_hdr_t`, `sm_dr_mad_hdr_t`, `sm_dr_class_hdr_t`, `sm_dr_data_t`.
- Directed-route status/direction bits: `SM_DR_SMP_D_OUT`, `SM_DR_SMP_D_IN`, `SM_DR_SMP_D_MASK`, `SM_DR_SMP_STATUS_MASK`.
- Trap numbers for GID service changes, multicast GID creation/destruction, link state, threshold events, capability/sysimage changes, bad M_Key/P_Key/Q_Key, and switch P_Key violations.

Trap payloads:
- `sm_trap_64_t` shared with traps 65/66/67.
- `sm_trap_128_t`, `sm_trap_129_t` shared with 130/131, `sm_trap_144_t`, `sm_trap_145_t`.
- `sm_trap_256_t`, `sm_trap_257_t` shared with 258, and `sm_trap_259_t` include endian-sensitive bitfields.

Subnet management attribute layouts:
- `sm_nodedesc_t`, `sm_nodeinfo_t`, `sm_switchinfo_t`, `sm_guidinfo_t`, `sm_portinfo_t`, `sm_pkey_table_t`, `sm_pkey_block_element_t`, `sm_SLtoVL_mapping_table_t`, `sm_VL_weight_block_t`, `sm_VLarb_table_t`, `sm_linear_forwarding_table_t`, `sm_lid_port_block_t`, `sm_random_forwarding_table_t`, `sm_multicast_forwarding_table_t`, `sm_sminfo_t`, `sm_vendor_diag_t`, `sm_ledinfo_t`.

Constants:
- Node types: CA, switch, router.
- Switch partition/raw-filter enforcement masks.
- Port capability mask bits including SM, notice/trap, reset/APM, NVRAM keys, LED info, CM/SNMP/DM/VM, DR notice, boot management, and client reregistration.
- Port state, physical state, link widths/speeds, M_Key protection levels, MTU values, VL capabilities, operational VLs, partition enforcement, forwarding table sizing, SM state and SMInfo action modifiers.
- Attribute IDs for SM MADs.

Layout/portability notes:
- Many structures use `_BIT_FIELDS_HTOL`/`_BIT_FIELDS_LTOH` conditional definitions for exact wire bit ordering.
- This file is included by SA record definitions and is a foundational InfiniBand management ABI header.

Dependencies:
- Includes `sys/ib/ib_types.h` and `sys/ib/mgt/ib_mad.h`.

Relevance:
- Supports kernel InfiniBand fabric management; relevant to storage transports such as iSER/RDMA even though it is not filesystem code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/sm_attr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ibpart.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ibpart.h

This header defines ioctl ABI structures and commands for InfiniBand partition management.

Key definitions:
- Ioctl commands: `IBD_CREATE_IBPART`, `IBD_DELETE_IBPART`, `IBD_INFO_IBPART`.
- Info subcommands: `IBD_INFO_CMD_IBPART`, `IBD_INFO_CMD_IBPORT`, `IBD_INFO_CMD_PKEYTBLSZ`.
- Error enum `ibd_part_err_t` covers invalid port instance, down port, missing/invalid P_Key, partition exists, no hardware resource, and invalid P_Key table size.

Structures:
- `ibd_ioctl_t` carries common ioctl fields: info command, datalink ID, port instance/number, HCA/port GUIDs, status, and alignment padding.
- `ibpart_ioctl_t` extends common data with partition datalink ID, force-create flag, P_Key, and padding.
- `ibd_create_ioctl_t` and `ibd_delete_ioctl_t` alias `ibpart_ioctl_t`.
- `ibport_ioctl_t` reports P_Key table size and pointer to P_Key array.
- Under `_SYSCALL32`, `ibport_ioctl32_t` provides a 32-bit pointer-compatible form.

ABI notes:
- Comments explicitly warn that structure alignment must remain correct for 32-bit and 64-bit ioctl operation.
- Depends on stable datalink and InfiniBand type sizes.

Dependencies:
- Includes `sys/types.h`, `sys/ib/ib_types.h`, and `sys/dld_ioc.h`.

Relevance:
- Network/storage substrate support: InfiniBand partitioning can affect RDMA-capable storage connectivity.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ibpart.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/id32.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/id32.h

This small kernel-only header declares a 32-bit ID-to-pointer facility.

Key definitions:
- Under `_KERNEL`, declares:
  - `id32_init(void)`
  - `id32_alloc(void *, int)`
  - `id32_free(uint32_t)`
  - `id32_lookup(uint32_t)`

Purpose:
- Provides an opaque 32-bit handle allocation/lookup layer for kernel code that needs to expose or store compact IDs for pointers.

Dependencies:
- Includes `sys/types.h`.

Relevance:
- General kernel utility. It can support device, IPC, or storage subsystems that need stable 32-bit identifiers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/id32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/id_space.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/id_space.h

This header defines a generic ID space allocator API backed by `vmem_t`.

Key definitions:
- `typedef vmem_t id_space_t;`
- API:
  - `id_space_create(const char *, id_t, id_t)`
  - `id_space_destroy(id_space_t *)`
  - `id_space_extend(id_space_t *, id_t, id_t)`
  - `id_alloc`, `id_alloc_nosleep`
  - `id_allocff`, `id_allocff_nosleep`
  - `id_alloc_specific_nosleep`
  - `id_free`

Dependencies:
- Includes `sys/param.h`, `sys/types.h`, `sys/mutex.h`, and `sys/vmem.h`.

Behavioral notes:
- Provides sleeping and non-sleeping allocation variants.
- Provides first-fit variants and specific-ID allocation.
- Used by subsystems that need bounded ID allocation; `ipc_impl.h` uses it for IPC object IDs.

Relevance:
- Common kernel infrastructure for identifiers, relevant to filesystems and storage control planes where stable object IDs are required.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/id_space.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm.h

This is the public umbrella header for the iSCSI Data Mover (IDM) layer. It defines public status codes, callback interfaces, request structures, state-machine audit types, and exported APIs for initiator/target connections, services, buffers, tasks, PDUs, key negotiation, and reference counting.

Key definitions:
- `idm_status_t` covers success, generic failure, no resources, reject, I/O, abort, suspend, header/data digest failures, protocol error, and login failure.
- `idm_client_notify_t` generated from `IDM_CLIENT_NOTIFY_LIST()` includes connection accepted, login failure, login readiness, full-feature phase enabled/disabled, lost/destroyed/failed connection, etc.
- `idm_ffp_disable_t`, `idm_abort_type_t`, `idm_task_state_t`, and `kv_status_t`.
- Forward declarations for IDM connection/service/buffer/PDU/task structures.

Callback types:
- Client notification, PDU receive/error, buffer completion, PDU completion, task completion, header build, StatSN update, and keepalive callbacks.
- `idm_conn_ops_t` groups client callbacks per connection.

Request and address structures:
- `idm_sockaddr_t` union for IPv4/IPv6 socket addresses.
- `SIZEOF_SOCKADDR()` helper.
- `idm_conn_req_t` describes initiator connection creation, including domain/type/protocol, binding, destination, LDI identity, callbacks, and boot-connection flag.
- `idm_svc_req_t` describes target service creation.
- `idm_ipaddr_t`, `idm_addr_t`, and variable-sized `idm_addr_list_t`.

State-machine audit:
- `SM_AUDIT_BUF_MAX_REC`, `sm_audit_record_type_t`, `sm_audit_sm_type_t`, `sm_audit_record_t`, `sm_audit_buf_t`.
- Logging globals and macros: `idm_sm_logging`, `idm_conn_logging`, `idm_svc_logging`, `IDM_SM_LOG`, `IDM_CONN_LOG`, `IDM_SVC_LOG`.
- Audit helper declarations.

Included IDM stack:
- Includes iSCSI protocol, connection state machine, transport, internal IDM structures, text negotiation, and socket transport headers.

Public API groups:
- Initiator: create/connect/disconnect/destroy.
- Target services: create/online/offline/destroy/lookup/hold/release/accept/reject.
- Connection metadata setters for target/initiator names and ISID.
- Data transfer: `idm_buf_tx_to_ini`, `idm_buf_rx_from_ini`, completion calls.
- Key negotiation: negotiate, notice, declare.
- Buffers: allocate/free, bind/unbind, find, buffer-pattern set/check.
- Tasks: allocate/start/abort/cleanup/done/free/find/hold/release.
- PDUs: allocate/init/free/complete/transmit.
- Reference counting: init/destroy/reset/hold/release/wait/async wait/is-held.

Relevance:
- Central kernel iSCSI data movement interface, directly relevant to block storage and virtualization/storage networking in subset A.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_conn_sm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_conn_sm.h

This header defines the IDM connection state machine event/state vocabulary and related helpers.

Key definitions:
- Timeouts: `IDM_LOGIN_SECONDS`, `IDM_LOGOUT_SECONDS`, `IDM_CLEANUP_SECONDS`.
- `IDM_CONN_EVENT_LIST()` enumerates initiator, target, and common connection events.
- `idm_conn_event_t` includes connect/login/logout/async-drop/transport-fail/misc/protocol-error/reinstate/enable-datamover events.
- `CONN_STATE_LIST()` defines connection states from free, transport wait/up, login, logged-in, logout, cleanup, init error, enable datamover, rejected/wait-send-done, complete.
- Optional string tables are emitted under `IDM_CONN_SM_STRINGS`.

Timer safety macros:
- `IDM_SM_TIMER_CHECK(ic)` warns/asserts if an existing timeout is still set before scheduling another.
- `IDM_SM_TIMER_CLEAR(ic)` cancels and clears a state-machine timeout.
- The comment documents a historical panic risk from stale login timeout callbacks after connection close.

PDU event handling:
- `idm_pdu_event_type_t`: none, RX PDU, TX PDU.
- `idm_pdu_event_action_t`: send protocol error, forward, or drop.
- `idm_conn_event_ctx_t` carries event context, PDU event type, and forwarded state.

Functions:
- State machine init/fini, client notification, event dispatch, locked event dispatch, connection reinstatement, TX/RX PDU event helpers, and state string lookup.

Notes:
- The header contains a duplicated declaration of `idm_conn_event`; this is harmless in C headers but notable.
- It is tightly coupled to `idm_conn_t` fields such as `ic_state_timeout`, `ic_state`, and `ic_last_state`.

Relevance:
- Governs iSCSI login/logout/full-feature connection lifecycle, critical for stable block storage sessions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_conn_sm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_impl.h

This header defines private IDM implementation structures and internal routines. It is the concrete layout contract for services, connections, tasks, buffers, PDUs, ID pools, global state, and internal protocol forwarding.

Key definitions:
- Connection flags: `CF_LOGIN_READY`, `CF_INITIAL_LOGIN`, `CF_ERROR`.
- `idm_conn_type_t`: initiator or target.
- Watchdog and idle timeout constants: `IDM_WD_INTERVAL`, `IDM_TRANSPORT_KEEPALIVE_IDLE_TIMEOUT`, `IDM_TRANSPORT_FAIL_IDLE_TIMEOUT`.

Reference counting:
- Audit records and circular audit buffer: `refcnt_audit_record_t`, `refcnt_audit_buf_t`.
- `REFCNT_AUDIT()` captures stack traces with `getpcstack`.
- `idm_refcnt_t` tracks refcount, referenced object, wait mode, mutex/CV, callback, and audit buffer.

Core structures:
- `idm_conn_param_t` stores negotiated connection parameters.
- `idm_svc_t` stores target service state, refcounting, online flag, socket/iSER service-private pointers, and service request.
- `idm_conn_t` stores connection identity, local/remote addresses, target/initiator names, TSIH/ISID strings, connection state/audit/timeout/taskq, login and datamover state, transport ops/type/private data, params, and callbacks.
- `idm_task_t` stores task binding, mutex, client private data/handle, tags, state/refcount, transfer statistics, expected DataSN/R2TSN, input/output buffers, transport header, and phase-collapse flags.
- `idm_buf_t` stores buffer magic, TX/list links, connection binding, buffer pointer/length/offset, expected offset, transport private data, completion callback, task binding, timestamps, socket-specific state, template data header, and status.
- `idm_pdu_t` stores PDU magic, TX/client links, connection, header/data pointers and lengths, transport header/private data, callback, status, iovec receive support, allocation/cache flags, and taskq entry.
- `idm_tx_obj_t` is a generic TX-list discriminator whose first fields match PDU/buffer ordering requirements.
- `idm_idpool_t` is a compact connection-ID pool.
- `idm_global_t` stores global taskqs, watchdog thread, service/connection lists, caches, task ID table, connection ID pool, and socket PDU/buffer caches.

Constants and macros:
- `IDM_CONN_HEADER_DIGEST`, `IDM_CONN_DATA_DIGEST`, `IDM_CONN_USE_SCOREBOARD`.
- `IDM_CONN_ISINI`, `IDM_CONN_ISTGT`.
- Task/buffer/PDU magic values and flags.
- `PDU_MAX_IOVLEN`, `IDM_PDU_OPCODE`.
- AHS cache constants for extended CDB and bidirectional AHS.
- ID pool min/max sizing.

Internal functions:
- Task constructor/destructor.
- ID pool create/destroy/alloc/free.
- PDU RX/TX forwarding and protocol-error paths.
- Login/logout parser helpers.
- Service connection create/destroy; initiator/target finish.
- Common connection create/destroy/close.
- Connection ID allocation/free.
- CRC32C helpers.
- Buffer list insertion and connection lookup by ISID/TSIH/CID.

Dependencies:
- Includes AVL, socket internals, and taskq internals.
- Depends on iSCSI protocol types via inclusion order from `idm.h`.

Relevance:
- Core private kernel data mover state for iSCSI block storage. This is one of the most important files in this group for storage-path behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_so.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_so.h

This header declares the sockets transport implementation pieces for IDM.

Key definitions:
- Socket buffer sizes: `IDM_RCVBUF_SIZE`, `IDM_SNDBUF_SIZE` at 256 KiB.
- Socket buffer cache range: `IDM_SO_BUF_CACHE_LB` 32 KiB and `IDM_SO_BUF_CACHE_UB` 128 KiB.
- `idm_so_svc_t` stores service socket, service thread, thread ID, and running flag.
- `idm_so_conn_t` stores connection socket, TX/RX threads, thread IDs, running flags, TX mutex/CV, and TX PDU list.
- `idm_so_timed_socket_t` stores CV/callback/error state for timed socket connect.

Functions:
- Transport init/fini: `idm_so_init`, `idm_so_fini`.
- Socket lifecycle: `idm_socreate`, `idm_soshutdown`, `idm_sodestroy`.
- Address utilities: sockaddr comparison, IP address list retrieval, IDM address to sockaddr, sockaddr to presentation string.
- I/O helpers: `idm_sorecv`, `idm_sosendto`, `idm_iov_sosend`, `idm_iov_sorecv`.
- TX/RX threads and PDU cache constructors/destructors.
- Service port watcher and timed socket connect.

Dependencies:
- Includes `sys/idm/idm_transport.h` and `sys/ksocket.h`.

Relevance:
- Implements TCP socket data movement for iSCSI when not using iSER/RDMA. Directly relevant to block storage networking.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_so.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_text.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_text.h

This header defines IDM support for iSCSI text key-value negotiation and conversion between text buffers and `nvlist_t`.

Key definitions:
- `iscsikey_id_t` enumerates iSCSI login/text keys:
  - Authentication keys for KRB, SPKM, SRP, CHAP.
  - Operational keys such as HeaderDigest, DataDigest, MaxConnections, SendTargets, TargetName, InitiatorName, aliases, TargetAddress, TPGT, InitialR2T, ImmediateData, segment lengths, burst lengths, timers, outstanding R2T, ordering flags, ErrorRecoveryLevel, markers.
  - iSER keys such as RDMAExtensions and receive segment lengths.
- Comment notes the enum should stay under 64 values because login code uses a bitmask for negotiated key tracking.
- `idmkey_type_t` classifies values as text, iSCSI name, booleans, numerical, ranges, binary, simple, or list-of-values.
- `idm_kv_xlate_t` maps key IDs to names, value types, and declarative status.

Functions:
- Key lookup and ID/name conversion.
- Add key-value pairs to nvlists.
- Convert text buffers to nvlists and nvlists to text buffers.
- Determine first-fragment length.
- Convert nvlist status to `kv_status_t`, and key negotiation status to iSCSI error class/detail.
- Iterate list values and convert nvpair values to text.
- Convert PDU lists to nvlists.
- Create/free internal text buffers and initialize PDU text data.

Dependencies:
- Includes `sys/idm/idm_impl.h`.

Relevance:
- Critical for iSCSI login negotiation, SendTargets, and operational parameter exchange.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_text.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_transport.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_transport.h

This header defines the transport abstraction layer used by IDM. It allows socket and iSER transports to register operation vectors for PDU movement, buffer transfer, key negotiation, and connection/service lifecycle.

Key definitions:
- `IDM_TRANSPORT_PATHLEN` and `IDM_TRANSPORT_HEADER_LENGTH`.
- `idm_transport_type_t`: iSER, sockets, number of types, undefined.
- `idm_transport_caps_t` stores transport capability flags.

Operation typedefs:
- PDU transmit, target buffer TX/RX, initiator Data-In/R2T receive, target Data-Out receive.
- Connection resource allocation/free.
- Target/initiator datamover enable, connection termination.
- Task resource cleanup.
- Key negotiation/notice/declaration.
- Capability probe.
- Buffer allocation/setup/teardown/free.
- Target service create/destroy/online/offline.
- Target connection destroy/connect/disconnect.
- Initiator connection create/destroy/connect/disconnect.

Main structures:
- `idm_transport_ops_t` is the full vtable consumed by IDM.
- `idm_transport_t` stores transport type, device path, LDI handle, ops, and caps.
- `idm_transport_attr_t` is used by transport drivers during registration.

API:
- `idm_transport_register`
- `idm_transport_lookup`
- `idm_transport_setup`
- `idm_transport_teardown`

Dependencies:
- Includes `sys/nvpair.h` and `sys/sunldi.h`.

Relevance:
- Abstraction point between common iSCSI data mover code and concrete transport implementations, including TCP sockets and iSER/RDMA.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idm/idm_transport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idmap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idmap.h

This header defines status codes and reserved identifiers for illumos ID mapping, especially Windows SID to Unix UID/GID mapping.

Key definitions:
- Success/iteration codes: `IDMAP_SUCCESS`, `IDMAP_NEXT`.
- Error code range from `IDMAP_ERR_OTHER` through `IDMAP_ERR_NO_ACTIVEDIRECTORY`, covering internal/memory/no-result/type/rule/cache/db/argument/SID/RPC/client/busy/permission/no-mapping/domain/security/config/network/LDAP/AD errors.
- Reserved well-known GIDs and UIDs for Local System, Creator Group, and Creator Owner.
- Reserved SID authority: `IDMAP_WK_CREATOR_SID_AUTHORITY`.
- Door RPC size cap: `IDMAP_MAX_DOOR_RPC` at 256 KiB.
- `IDMAP_SENTINEL_PID` and `IDMAP_ID_IS_EPHEMERAL(pid)` macro.

Relevance:
- Important to SMB/NFS identity translation and access control around filesystems.
- This file is constants only; no functions or structures are declared.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/idmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ieeefp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ieeefp.h

This header defines Sun/illumos IEEE floating-point enums for rounding, precision, exceptions, trap bits, and FP classes.

Architecture-specific definitions:
- On SPARC:
  - `fp_direction_type`: nearest, tozero, positive, negative.
  - `fp_precision_type`: extended, single, double, precision_3.
  - `fp_exception_type`: inexact, division, underflow, overflow, invalid.
  - `N_IEEE_EXCEPTION` is 5.
  - Trap enum mirrors those five exceptions.
- On i386/amd64:
  - Direction values differ: nearest, negative, positive, tozero.
  - Precision values differ: single, precision_3, double, extended.
  - Exception enum includes denormalized and has 6 entries.
  - `N_IEEE_EXCEPTION` is 6.

Common definition:
- `fp_class_type`: zero, subnormal, normal, infinity, quiet, signaling.

Relevance:
- General ABI/standards header; not directly storage-related.
- Can affect kernel/user ABI compatibility for floating-point state consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ieeefp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ilstr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ilstr.h

This newer illumos header defines a small growable/preallocated string builder interface usable in kernel and user contexts.

Key definitions:
- Includes kernel or user headers depending on `_KERNEL`.
- `ilstr_errno_t`: OK, no memory, overflow, printf error.
- `ilstr_flag_t`: `ILSTR_FLAG_PREALLOC`.
- `ilstr_t` stores data pointer, allocated length, string length, error state, kernel memory flag, and flags.

API:
- Initialization: `ilstr_init`, `ilstr_init_prealloc`.
- Lifecycle: `ilstr_reset`, `ilstr_fini`.
- Mutators: append/prepend string, append/prepend char, printf append via `ilstr_aprintf` and `ilstr_vaprintf`.
- Accessors: error, C string, length, empty check, error string.

Relevance:
- General utility useful for kernel diagnostics, formatting, generated names/paths, and administrative output.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ilstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/instance.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/instance.h

This header defines device instance-number assignment data structures and APIs around `/etc/path_to_inst`.

Key definitions:
- Instance file paths: `INSTANCE_FILE`, `INSTANCE_FILE_SUFFIX`.
- Kernel/kmemuser structures:
  - `in_node_t` represents the fully populated instance tree parallel to the dev_info tree.
  - `in_drv_t` represents a driver binding/instance entry under an instance node.
- Instance states: `IN_PROVISIONAL`, `IN_PERMANENT`, `IN_UNKNOWN`, `IN_BORROWED`.
- `PTI_GUARD` guard text for `path_to_inst`.
- `IN_SEARCHME` special instance value.

Kernel APIs:
- Initialize/assign/keep/free instances.
- Major+instance to path conversion.
- Clean/orphan handling and enter/exit locking.
- Root access and dirty/clean state.
- Platform override hooks: `impl_assign_instance`, `impl_keep_instance`, `impl_free_instance`.
- Instance tree walking and DDI-MP borrow/return helpers.
- Walk callback return values: continue/terminate.

User API:
- `inst_sync(char *pathname, int flags)` when not `_KERNEL`.
- Sync flags: `INST_SYNC_IF_REQUIRED`, `INST_SYNC_ALWAYS`.

Relevance:
- Device instance stability is fundamental for disk, controller, network, and storage device naming.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/instance.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_const.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_const.h

This header implements ISO C integer constant macros for illumos fixed-width integer types.

Key definitions:
- `__CONCAT__(A,B)` token pasting helper.
- `INT8_C`, `INT16_C`, `INT32_C`, `INT64_C`.
- `UINT8_C`, `UINT16_C`, `UINT32_C`, `UINT64_C`.
- `INTMAX_C`, `UINTMAX_C`.

Data model behavior:
- On `_LP64`, 64-bit constants use `l`/`ul` suffixes.
- On `_ILP32` with `_LONGLONG_TYPE`, 64-bit constants use `ll`/`ull`.
- Without long long support, max constants fall back to unsuffixed values for 32-bit max types.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Standards and ABI support for fixed-width constants. Indirectly important across kernel and user headers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_const.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_fmtio.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_fmtio.h

This header implements ISO C99 `<inttypes.h>` printf/scanf format macros for fixed-width integer types, plus illumos non-standard extensions.

Key definitions:
- Print macros for signed and unsigned fixed-width, least, fast, pointer, and max integer types: `PRId*`, `PRIi*`, `PRIo*`, `PRIu*`, `PRIx*`, `PRIX*`.
- Scan macros: `SCNd*`, `SCNi*`, `SCNo*`, `SCNu*`, `SCNx*`, `SCNX*`.
- Pointer formats switch between `l` forms on `_LP64` and plain int forms on ILP32.
- `PRIdMAX`/friends and `SCNdMAX`/friends use `ll` on ILP32 with long long and `l` otherwise.

Kernel/user note:
- `_MODF8` and `_MODF16` suppress `hh`/`h` in `_KERNEL`, while userland gets standard small-width modifiers.

Non-standard extensions:
- Under non-strict symbols, defines private `_PRI*ID`/`_SCN*ID` formats for `id_t`.
- Defines `_PRI*WC`/`_SCN*WC` aliases for `wint_t`/`wchar_t`-like formatting.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Widespread diagnostic and ABI formatting support; important for correct cross-data-model logging and parsing.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_fmtio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_limits.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_limits.h

This header implements integer limit macros for illumos fixed-width and related standard types.

Key definitions:
- Maximums: `INT8_MAX`, `INT16_MAX`, `INT32_MAX`, optionally `INT64_MAX`; unsigned equivalents; `INTMAX_MAX`, `UINTMAX_MAX`.
- Least and fast integer max macros.
- Pointer integer max macros: `INTPTR_MAX`, `UINTPTR_MAX`.
- `PTRDIFF_MAX`, `SIZE_MAX`, `SIG_ATOMIC_MAX`, `WCHAR_MAX`, `WINT_MAX`.
- Minimums are exposed under extensions/non-XOPEN or XPG6 conditions:
  - `INT*_MIN`, `INTMAX_MIN`, least/fast min macros, `INTPTR_MIN`, `PTRDIFF_MIN`, `SIG_ATOMIC_MIN`, `WCHAR_MIN`, `WINT_MIN`.

Data model behavior:
- Uses `L` constants on `_LP64`.
- Uses `LL` constants when `_LONGLONG_TYPE` exists on ILP32.
- `SIZE_MAX` follows LP64/ILP32 `unsigned long` width.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Foundational ABI/standards header used across kernel and user code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_types.h

This header defines illumos fixed-width, max-width, pointer-width, fast, and least integer typedefs.

Key typedefs:
- Fixed signed: `int8_t`, `int16_t`, `int32_t`, optional `int64_t`.
- Fixed unsigned: `uint8_t`, `uint16_t`, `uint32_t`, optional `uint64_t`.
- `intmax_t`, `uintmax_t` map to 64-bit types when available, otherwise 32-bit.
- `intptr_t`, `uintptr_t` map to long/unsigned long on LP64 and int/unsigned int on ILP32.
- Fast types: `int_fast8_t`, `int_fast16_t`, `int_fast32_t`, optional `int_fast64_t`, and unsigned equivalents.
- Least types: `int_least8_t`, `int_least16_t`, `int_least32_t`, optional `int_least64_t`, and unsigned equivalents.

Data model and ABI notes:
- `int8_t` and 8-bit fast/least signed types use `char` if `_CHAR_IS_SIGNED`, otherwise `signed char`.
- On `_LP64`, `int64_t` is `long`; on ILP32 with long long support, it is `long long`.
- Comment warns that `uint_least16_t` and `uint_least32_t` changes must be mirrored for `char16_t` and `char32_t`.

Dependencies:
- Includes `sys/feature_tests.h`.

Relevance:
- Core type foundation for nearly every kernel and user ABI header in this group.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/int_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/inttypes.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/inttypes.h

This is the illumos kernel/driver-facing wrapper for C99 integer facilities.

Key behavior:
- Includes `sys/feature_tests.h` and `sys/int_types.h`.
- Includes `sys/int_limits.h`, `sys/int_const.h`, and `sys/int_fmtio.h` unless constrained by XOPEN namespace rules.
- Comment directs kernel/driver developers to include this file, while applications should use standard `<inttypes.h>`.

Relevance:
- Aggregates fixed-width integer types, limits, constants, and format macros for kernel and driver code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/inttypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioccom.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioccom.h

This header defines BSD-style ioctl command encoding macros.

Key definitions:
- `IOCPARM_MASK` limits encoded parameter size to 255 bytes.
- Direction/status bits: `IOC_VOID`, `IOC_OUT`, `IOC_IN`, `IOC_INOUT`.
- Macros:
  - `_IO(x, y)` for no-parameter ioctl.
  - `_IOR(x, y, t)` and `_IORN(x, y, t)` for copy-out with sizeof or explicit size.
  - `_IOW(x, y, t)` and `_IOWN(x, y, t)` for copy-in.
  - `_IOWR(x, y, t)` and `_IOWRN(x, y, t)` for bidirectional copy.

ABI notes:
- Encodes command in the lower word and size/direction in the upper word.
- Uses `0x20000000` to distinguish newer ioctls from older ones.

Relevance:
- Foundational ioctl ABI support. Used by headers such as `ipmi.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioccom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioctl.h

This header defines legacy System V/BSD ioctl constants and declares `ioctl`.

Key definitions:
- `IOCTYPE`, `LIOC*`, and `DIOC*` legacy command groups.
- Declares `extern int ioctl(int, int, ...);`
- Comment notes POSIX Issue 8 removed the old `<stropts.h>` placement and illumos exposes it here for portability.

BSD compatibility:
- Under `BSD_COMP`, includes `sys/ttychars.h`, `sys/ttydev.h`, and `sys/ttold.h`.
- Defines BSD terminal mode aliases such as `TANDEM`, `CBREAK`, `ECHO`, `RAW`, delay masks, erase modes, modem/control flags, etc.
- Includes `sys/filio.h` and `sys/sockio.h`.

Relevance:
- Core user/kernel control-plane ABI. Storage, filesystems, drivers, and network subsystems all rely on ioctl interfaces.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc.h

This public header defines common System V IPC permission and command constants.

Key definitions:
- `struct ipc_perm` includes owner/creator UID/GID, mode, sequence number, key, and ILP32 padding.
- Mode bits: `IPC_ALLOC`, `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`.
- Key constant: `IPC_PRIVATE`.
- Control commands: `IPC_RMID`, `IPC_SET`, `IPC_STAT`.
- Declares `ftok(const char *, int)` under namespace conditions.

Dependencies:
- Includes `sys/isa_defs.h`, `sys/feature_tests.h`, and `sys/types.h`.

Relevance:
- General OS IPC ABI. Filesystem tools and daemons may use IPC, but this is not filesystem-specific.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_impl.h

This private header defines kernel and cross-data-model implementation details for System V IPC.

Public/cross-model structures:
- `ipc_time_t` is `uint64_t`.
- 64-bit control commands: `IPC_SET64`, `IPC_STAT64`.
- Under `_SYSCALL32`, `struct ipc_perm32` mirrors 32-bit userland layout.
- `ipc_perm64_t` is a stable user/kernel layout for 64-bit IPC control structures.
- `struct shmid_ds64`, `struct semid_ds64`, and `struct msqid_ds64` provide model-independent shared memory, semaphore, and message queue status layouts.

Kernel internals:
- ID encoding macros: sequence bits/mask/shift, index mask, `IPC_SEQ`, `IPC_INDEX`.
- Table sizing and invalid ID constants.
- Resource-control accounting macros: `IPC_PROJ_USAGE`, `IPC_ZONE_USAGE`.
- Lock assertion helper `IPC_LOCKED`.
- `kipc_perm_t` is the kernel IPC permission object with AVL/list links, refcount, credentials, project, IPC ID, zone ID, and zone ref.
- `ipc_slot_t` stores bucket lock, object pointer, sequence, stale-chain pointer, and padding.
- `ipc_service_t` stores global service state: lock, key tree, table, counts, rctl handles/offsets, ID space, object size/destructors, used-ID list, and audit type.

Kernel functions:
- Permission checks/stat/set, service create/destroy/lock/unlock, object lookup/hold/release/get/commit/cleanup/remove/list, and zone cleanup.

Userland fallback:
- When not `_KERNEL`, declares `msgctl64`, `semctl64`, and `shmctl64`.

Dependencies:
- Includes IPC, mutex, resource control, project, zone, sysmacros, AVL, ID space, credentials, and list headers.

Relevance:
- General kernel IPC infrastructure. Not filesystem-specific but important OS substrate.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_rctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_rctl.h

This header defines resource-control quantity storage for System V IPC.

Key definition:
- `ipc_rqty_t` stores:
  - `ipcq_shmmni`
  - `ipcq_semmni`
  - `ipcq_msgmni`

Notes:
- Comments state these quantities are protected by the corresponding IPC service lock.
- Used by `ipc_impl.h` accounting macros through project/zone IPC data.

Dependencies:
- Includes `sys/rctl.h`.

Relevance:
- Resource-control support for IPC object counts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_rctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipd.h

This private header defines the interface between the `ipd` driver and `ipdadm`.

Purpose:
- `ipd` appears to inject IP disruption/perturbation behavior per zone: corrupt, delay, and drop.

Key definitions:
- Device path: `IPD_DEV_PATH` as `/dev/ipd`.
- `IPD_MAX_DELAY` is 10000 microseconds.
- `ipd_ioc_perturb_t` contains zone ID and argument.
- `ipd_ioc_info_t` contains zone ID and current corrupt/drop/delay settings.
- `_KERNEL` 32-bit list form: `ipd_ioc_list32_t`.
- `ipd_ioc_list_t` contains count and pointer to info array.
- Flags: `IPD_CORRUPT`, `IPD_DELAY`, `IPD_DROP`.
- Ioctl command base and commands: `IPDIOC_CORRUPT`, `IPDIOC_DELAY`, `IPDIOC_DROP`, `IPDIOC_LIST`, `IPDIOC_REMOVE`.

Relevance:
- Network fault-injection/control utility. Relevant to testing networked storage behavior but not a filesystem implementation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipmi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipmi.h

This header defines ioctl ABI and message/address structures for IPMI.

Key definitions:
- Limits and defaults: `IPMI_MAX_ADDR_SIZE`, `IPMI_MAX_RX`, BMC slave address/channel, BMC SMS LUN.
- Address types: system interface, IPMB, IPMB broadcast.
- Ioctl magic and commands:
  - Receive message, receive truncated message, send command.
  - Register/unregister command.
  - Set/get event command behavior.
  - Set/get own address and LUN.
- Receive types: response, async event, command.
- IPMI app netfn/command constants for device ID, flags, get/send message, channel info, watchdog reset/set/get.
- Watchdog timer flags/actions.

Structures:
- `ipmi_msg`, `ipmi_req`, `ipmi_recv`, `ipmi_cmdspec`.
- Generic and specific address structures: `ipmi_addr`, `ipmi_system_interface_addr`, `ipmi_ipmb_addr`.
- Under `_KERNEL`, 32-bit ioctl-compatible forms: `ipmi_msg32`, `ipmi_req32`, `ipmi_recv32`, and 32-bit ioctl command variants.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

License note:
- Carries BSD-style copyright from IronPort/FreeBSD plus Joyent copyright.

Relevance:
- Platform management interface. Indirect relevance to storage systems through watchdogs/platform control, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipmi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/isa_defs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/isa_defs.h

This header defines architecture and data-model characteristics used throughout illumos headers.

Purpose:
- Centralizes processor characteristics and Solaris implementation choices for x86, amd64, and SPARC targets.
- Provides macros consumed by layout-sensitive headers such as InfiniBand management records and fixed-width integer headers.

Processor characteristic macros:
- Endianness: `_LITTLE_ENDIAN`, `_BIG_ENDIAN`.
- Stack growth direction.
- Long-long word order.
- Bitfield allocation order: `_BIT_FIELDS_LTOH` on x86/amd64, `_BIT_FIELDS_HTOL` on SPARC.
- IEEE 754 support.
- Char signedness.
- Primitive type alignment macros, `_MAX_ALIGNMENT`, `_MAX_ALIGNMENT_TYPE`, `_ALIGNMENT_REQUIRED`.
- Cache line shift/size.
- `_HAVE_CPUID_INSN` on x86.

Implementation choices:
- Data models: `_ILP32`, `_LP64`, `_MULTI_DATAMODEL`.
- VTOC form: `_SUNOS_VTOC_16` on x86, `_SUNOS_VTOC_8` on SPARC.
- DMA address model: physical on x86, virtual on SPARC.
- Firmware/fdisk/OBP/soft-hostid/platform module flags.
- Compatibility macro `__i386_COMPAT` for 32-bit ABI on amd64.
- Shared `__x86` and `__sparc` family macros.

Architecture branches:
- amd64/x86_64: LP64, little endian, 16-byte max alignment, physical DMA, fdisk, i386 compatibility.
- i386: ILP32, little endian, 4-byte max alignment, physical DMA.
- SPARC: big endian, high-to-low bitfields, virtual DMA, no fdisk, OBP; splits into SPARC V8 ILP32 and SPARC V9 LP64.
- Emits compile-time errors for unsupported ISA or both `_ILP32` and `_LP64`.

Relevance:
- Foundational ABI header. Many wire and ioctl layouts depend on these macros for correct cross-platform representation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/isa_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclient.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclient.h

This header defines the Cisco-derived iSCSI authentication client interface, mainly for CHAP authentication negotiation.

Limits and constants:
- String, string-block, and large-binary maximum lengths.
- Receive-end max count.
- Client signature.
- CHAP response length.
- Key type enum for AuthMethod, CHAP algorithm, username, response, identifier, and challenge.

Enums:
- Authentication options: reject, not present, none, CHAP, MD5 algorithm.
- Negotiation role: originator/responder.
- Version: draft8 or RFC.
- Status: no error, error, pass, fail, continue, in progress.
- Detailed debug status values for success/failure, bad/missing keys, password issues, duplicate keys, string/data limits, T-bit issues, and receive limits.
- Node type: initiator/target.
- Auth phase: configure, negotiate, authenticate, done, error.
- Local and remote CHAP negotiation state machines.

Structures:
- `IscsiAuthClientGlobalStats`.
- Buffer/key descriptors: `IscsiAuthBufferDesc`, `IscsiAuthKey`, `IscsiAuthLargeBinaryKey`, `IscsiAuthKeyBlock`, `IscsiAuthStringBlock`, `IscsiAuthLargeBinary`.
- `IscsiAuthClient` is the main authentication state object, storing config, method/algorithm lists, username/password, version, challenge policy, callbacks, phase/state, debug status, negotiated values, CHAP challenge/response state, and send/receive key blocks.

APIs:
- Init/finish; receive begin/end.
- Key name/type lookup and iteration.
- Receive/send key-value and transit bit handling.
- Set methods, role, algorithms, username/password, remote auth, glue handle, method-list name, IPsec/base64, challenge length, version.
- Query password need, auth phase/status/method/algorithm/username/debug status.
- Send status code and convert debug status to text.
- Platform callback `iscsiAuthClientAuthResponse`.
- Platform-dependent hooks for CHAP auth request/cancel, text-number conversion, random data, MD5 operations, and data encoding/decoding.

Dependencies:
- Includes `sys/iscsi_authclientglue.h`, which provides MD5 context typing.

Relevance:
- Authentication layer for iSCSI sessions. Directly relevant to network block storage security and login behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclient.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclientglue.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclientglue.h

This small header provides platform glue for the iSCSI auth client.

Key definitions:
- Includes `<md5.h>`.
- `typedef MD5_CTX IscsiAuthMd5Context;`
- Declares global handles:
  - `iscsiAuthIscsiServerHandle`
  - `iscsiAuthIscsiClientHandle`

Purpose:
- Decouples the generic auth client from the platform MD5 context type and platform-specific handle storage.

Relevance:
- Support header for iSCSI CHAP authentication.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_authclientglue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_protocol.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_protocol.h

This header defines iSCSI protocol wire constants and PDU header structures.

General constants:
- Name/user lengths, listen port 3260.
- 24-bit network-order helpers `ntoh24` and `hton24`.
- Version constants, min/max PDU length, padding length, max key-value pairs.
- Text constants: separator, `None`, `Reject`, `Irrelevant`, `NotUnderstood`.
- Reserved task tag and key/value length constants.
- Final flag and SendTargets strings.

Common headers and opcodes:
- `iscsi_hdr_t` generic template header and `iscsi_rsp_hdr_t`.
- Opcode bits: retry, immediate, opcode mask.
- Client-to-server opcodes: NOP-Out, SCSI command, task management, login, text, data, logout, SNACK.
- Server-to-client opcodes: NOP-In, SCSI response, task management response, login/text response, data response, logout response, R2T, async event, reject.

PDU structures:
- SCSI command/response: `iscsi_scsi_cmd_hdr_t`, `iscsi_scsi_rsp_hdr_t`, `iscsi_addl_hdr_t`.
- Async event: `iscsi_async_evt_hdr_t`.
- NOP: `iscsi_nop_out_hdr_t`, `iscsi_nop_in_hdr_t`.
- Task management: `iscsi_scsi_task_mgt_hdr_t`, `iscsi_scsi_task_mgt_rsp_hdr_t`.
- R2T: `iscsi_rtt_hdr_t`.
- Data: `iscsi_data_hdr_t`, `iscsi_data_rsp_hdr_t`.
- Text: `iscsi_text_hdr_t`, `iscsi_text_rsp_hdr_t`.
- Login: `iscsi_login_hdr_t`, `iscsi_login_rsp_hdr_t`.
- Logout: `iscsi_logout_hdr_t`, `iscsi_logout_rsp_hdr_t`.
- SNACK: `iscsi_snack_hdr_t`.
- Reject: `iscsi_reject_rsp_hdr_t`.

Protocol constants:
- SCSI command flags and command attributes.
- SCSI response flags and status values.
- Async event codes.
- Task management function and response codes, including backward-compatible aliases.
- Data response flags.
- Text continue flag.
- ISID length and login flag helpers `ISCSI_LOGIN_CURRENT_STAGE` and `ISCSI_LOGIN_NEXT_STAGE`.
- Login stages, status classes, and status details.
- Logout reasons and responses.
- SNACK type mask and reject reasons.
- Default, minimum, and maximum operational parameter values.
- IQN/EUI name prefixes and EUI name length.

Dependencies:
- Includes `sys/types.h` and `sys/isa_defs.h`.

Relevance:
- Core iSCSI wire ABI for block storage networking. IDM, initiator, target, authentication, and user ioctl layers all build on these definitions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsi_protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/chap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/chap.h

This header defines CHAP validation support for the iSCSI target side.

Key definitions:
- `chap_validation_status_type` covers pass, invalid response, duplicate secret, unknown auth method, internal error, RADIUS access error, bad RADIUS secret, and unknown RADIUS code.
- `authentication_method_type`: RADIUS or direct authentication.
- `RADIUS_CONFIG` stores server address, port, shared secret, and shared secret length.

Function:
- `chap_validate(...)` validates a target CHAP response using target and initiator CHAP names, challenge, response, identifier, selected authentication method, and method-specific config data.

Dependencies:
- Includes `netinet/in.h`, `sys/int_types.h`, `sys/iscsit/iscsi_if.h`, and `sys/iscsit/radius_protocol.h`.

Relevance:
- Authentication/security component for iSCSI target sessions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/chap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsi_if.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsi_if.h

This header defines the ioctl/user-kernel interface for the illumos iSCSI initiator stack and related common utilities.

Interface constants:
- `ISCSI_INTERFACE_VERSION` is 3.
- `ISCSI_MAX_NAME_LEN` is 224.
- Login parameter numeric IDs for operational settings such as ordering, immediate data, InitialR2T, digest options, timers, segment lengths, burst lengths, max connections, outstanding R2T, and error recovery.
- Special parameter IDs for persistent DB entries, initiator name, and initiator alias.
- Driver devctl path constants.
- Ioctl command base and commands for OID creation, login/logout, parameter get/set/clear, target lists/properties/address, CHAP, static discovery, discovery settings, RADIUS, DB reload, LUN/connection lists/properties, USCSI, door handle, discovery events, auth settings, SendTargets, iSNS server settings, session config, initiator node name, and debug DB dump.
- Digest preference constants.

Core structs:
- `iscsi_oid_t` creates/returns target OIDs and carries target name and TPGT.
- `iscsi_login_params_t` stores all main session/connection operational parameters.
- `entry_t` describes a login/discovery endpoint with IPv4/IPv6 address, port, and TPGT.
- `node_name_t` stores initiator name/alias.
- Parameter get/set support: `iscsi_int_info_t`, `iscsi_bool_info_t`, `iscsi_get_value_t`, `iscsi_param_get_t`, `iscsi_set_value_t`, `iscsi_param_set_t`.

Authentication structs:
- `iscsi_chap_props_t` stores CHAP retry count, OID, username, and secret.
- `authMethod_t` includes none, CHAP, SRP, KRB5, SPKM1, SPKM2.
- `iscsi_auth_props_t` stores bidirectional-auth and method settings.
- `iscsi_radius_props_t` stores RADIUS address, port, shared secret, access/config flags, and secret length.

Address/discovery/target structs:
- `iscsi_ipaddr_t`, `iscsi_addr_t`, `iscsi_addr_list_t`.
- `iscsi_property_t` reports target name/alias, discovery method, connection status, connection count, last error, configured/negotiated TPGT, and ISID.
- `iscsi_target_list_t` and `iscsi_static_property_t`.
- Discovery enum `iSCSIDiscoveryMethod_t` and mask `ISCSI_ALL_DISCOVERY_METHODS`.

LUN/connection structs:
- `iscsi_lun_status_t`, inquiry ID length constants, `iscsi_lun_props_t`, `iscsi_if_lun_t`, `iscsi_lun_list_t`.
- `iscsi_conn_props_t`, `iscsi_if_conn_t`, `iscsi_conn_list_t`.

iSNS, USCSI, SendTargets:
- `isns_method_t`, `iSCSIDiscoveryProperties_t`.
- `iscsi_uscsi_t` and `_SYSCALL32` `iscsi_uscsi32_t`.
- `iscsi_sendtgts_entry_t`, `iscsi_sendtgts_list_t`, `iscsi_target_entry_t`.
- `isns_portal_group_t`, `isns_portal_group_list_t`, `isns_server_portal_group_list_t`.

Session config and events:
- Config session min/max and variable-sized `iscsi_config_sess_t`.
- `ISCSI_SESSION_CONFIG_SIZE(SIZE)` helper.
- Event class/subclass strings for static, SendTargets, SLP, iSNS, and property changes.

Kernel-only helpers:
- Under `_KERNEL`, declares file and socket utility wrappers used by `iscsid`: open/close/remove/rename/read/write/sendto/recvfrom and `iscsid_errno`.

Common utility prototypes:
- `utils_iqn_create`, `prt_bitmap`, `utils_map_param`, `parse_addr_port_tpgt`.

Dependencies:
- Kernel includes socket and STREAMS support headers.
- Includes `netinet/in.h`, `sys/scsi/impl/uscsi.h`, and `sys/iscsi_protocol.h`.

Relevance:
- Major control-plane ABI for network block storage discovery, login, authentication, target/session/LUN enumeration, and pass-through SCSI operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/iscsit/iscsi_if.h -->