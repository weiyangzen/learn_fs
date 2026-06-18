# Group Research: group_590_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__4af506d1aae2

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`. All 41 requested source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_verbs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_verbs.h

This OFED-derived public/kernel compatibility header defines the illumos OpenFabrics verbs-facing model over IBTF. It supplies the basic RDMA/IB types, object structs, enum values, and function prototypes used by kernel OFED clients.

Core definitions:
- RDMA node and transport types, GIDs, device/port attributes, capabilities, port states, rates, AH attributes, events, completions, CQ notification flags, QP/SRQ attributes, QP states, work request opcodes, and access flags.
- Kernel object wrappers for protection domains, completion queues, shared receive queues, queue pairs, IB devices, and IB clients.
- `ib_device_t` bridges OFED client-visible device identity to IBTF HCA handles, GUIDs, local DMA lkey, port count, registration state, client data, and OFS client handles.
- API declarations cover client register/unregister, client data access, device query, PD allocation, QP lifecycle, CQ lifecycle, polling, notification, and IBTF handle extraction.

Risk-sensitive invariants:
- This is ABI/API compatibility glue; enum values and struct layout must remain aligned with OFED consumers.
- `IB_QPT_SMI` and `IB_QPT_GSI` must remain the first two QP types because MAD code uses them as table indexes.
- CQ notification uses the standard missed-event race protocol: positive return from `ib_req_notify_cq()` means consumers must poll again.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_verbs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_cm.h

This OFED-derived header declares the kernel RDMA Connection Manager API exposed to OpenFabrics-style clients on illumos.

Core definitions:
- CM event types for address/route resolution, connection requests/responses, rejects, establishment, disconnect, device removal, multicast, and address change.
- RDMA port spaces for SDP, IPoIB, TCP, UDP, and SCTP.
- `rdma_addr`, `rdma_route`, connected and UD connection parameter structs, and `rdma_cm_event`.
- `rdma_cm_id`, which binds a device, caller context, optional QP, event handler, route, port space, and port number.

API surface:
- ID creation/destruction, address binding/resolution, route resolution, QP attribute initialization, active connect, listen, accept, reject, disconnect, event notification, multicast join/leave, service type selection, and RDMA-CM-owned QP create/destroy.
- illumos-specific mapping helpers attach IBTF/iWARP client handles and QP handles to an RDMA-CM ID.

Important semantics:
- Destroying an ID cancels in-flight async operations.
- Event callbacks must not directly call `rdma_destroy_id()` on the same ID; returning nonzero requests destruction.
- RDMA-CM-owned QPs are automatically transitioned by CMA.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_user_cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_user_cm.h

This OFED-derived packed ABI header defines the user/kernel command protocol for the RDMA user CM device.

Core definitions:
- ABI version `RDMA_USER_CM_ABI_VERSION` is `4`; private connection data is capped at `RDMA_MAX_PRIVATE_DATA` bytes.
- Command numbers cover create/destroy ID, bind/resolve/query route, connect/listen/accept/reject/disconnect, init QP attr, get/set option, notify, multicast join/leave, and event retrieval.
- Packed request/response structs encode user handles, response addresses, IDs, socket addresses, timeouts, route records, connection parameters, UD parameters, event responses, and options.

Risk-sensitive invariants:
- `#pragma pack(1)` makes this a strict binary ABI; padding/reserved fields are deliberate.
- Many structures carry user pointers or response addresses, so compat conversion and copyin/copyout code must preserve 32/64-bit layout.
- Route query response supports two IB paths and embeds IPv6-sized source/destination socket addresses.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/rdma_user_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_cma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_cma.h

This Solaris-specific CMA private header defines the in-kernel state behind `rdma_cm_id` for the illumos OpenFabrics RDMA-CM implementation.

Core definitions:
- Macros classify UDP/IPoIB IDs and valid IPv4/IPv6 socket addresses.
- Global listen records track service IDs, client/service handles, and CMID channel lists.
- `cma_chan_state_t` models RDMA-CM ID progression through idle, bound, address/route query, resolved, event-notified, connect/listen/disconnect/accept/reject, destroying, HCA down, and port down states.
- Listen metadata distinguishes root listener CMIDs from endpoint CMIDs and stores root/endpoint list entries plus IBTF service/bind handles.
- Client/server role state is tracked separately through `sol_cma_connect_flag_t` and `cma_req_cmid_state_t`.

Main structure:
- `sol_cma_chan_t` embeds `struct rdma_cm_id` first, then adds request/accepted AVL trees, counters, state, mutex/CV, transport type, IB/iWARP client handles, QP handle, listen metadata, connection params, session/QP metadata, and transport-specific `ibcma_chan_t`.

Important helpers:
- `sol_cma_any_addr()` recognizes wildcard IPv4/IPv6 addresses.
- `cma_create_new_id()` clones route/address/device/listen-root state for derived IDs.
- `cma_get_req_idp()` and `cma_get_acpt_idp()` search listener AVL trees and require the root channel mutex.

Risk-sensitive invariants:
- `struct rdma_cm_id` must remain the first field of `sol_cma_chan_t` for casting.
- Request and accepted CMID AVL trees are protected by the root channel mutex.
- Destroy/event/API progress bits coordinate caller-facing destruction with async callbacks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_cma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ib_cma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ib_cma.h

This transport-specific CMA header holds the InfiniBand-side state used by Solaris RDMA-CM.

Core definitions:
- Defines the global UDP QKey as `RDMA_UDP_QKEY`.
- `ibcma_dev_t` records selected local device information: node GUID, port, pkey index/value, SGID, and IP address.
- Address flags track whether local/remote addresses were set and whether the local address was wildcard.
- `ibcma_chan_t` stores path info, local/remote IBT IP addresses, port, service ID, RC request data, QP modify status, selected device, multicast list, and multicast count.
- `ibcma_mcast_t` records multicast membership context: CMID, caller context, socket address, and multicast GID.

Risk-sensitive invariants:
- `ibcma_chan_t` is embedded in the generic CMA channel union and is the IB transport’s private state.
- Address flags determine whether source/destination binding and wildcard handling are complete.
- Multicast list ownership and count must stay synchronized with join/leave handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ib_cma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_kverb_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_kverb_impl.h

This private Solaris OFS kernel-verbs header defines event-firing macros, OFED-to-IBTF conversion macros, and OFS client state.

Core definitions:
- `FIRE_QP_EVENT` and `FIRE_CQ_EVENT` acquire the OFS client reader lock, check that the object and event handler exist and the device is open, fill `ib_event`, call the OFED event handler, then release the lock.
- Conversion macros map OFED page size, QP state, static rate, path migration state, and path MTU values to IBTF forms.
- `gfp_t` is typedefed for OFED compatibility.
- `ofs_client_t` maps an OFED `ib_client_t` to IBTF module/client handles, HCA counts, device/client lists, a lock, and initialization state.

Risk-sensitive invariants:
- Async events are discarded when the device registration state is `IB_DEV_CLOSE`.
- Event callbacks run while the client lock is held as reader, so callback behavior must avoid deadlocking with client teardown.
- Conversion macros assume enum compatibility between OFED-visible and IBTF-visible values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_kverb_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ofs_common.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ofs_common.h

This common Solaris OFS utility header provides user-object tables, small linked-list abstractions, generic resource lists, and debug printf entry points shared by OpenFabrics kernel drivers.

Core definitions:
- User object types cover sol_uverbs contexts, PDs, AHs, MRs, CQs, SRQs, QPs, event files, and sol_ucma event files, CM IDs, and multicast objects.
- `sol_ofs_uobj_t` carries a user handle, object type, rwlock, table ID, ref lock/refcount, live flag, and object size.
- `sol_ofs_uobj_table_t` is a growable block table mapping integer IDs to user objects.
- Table/object APIs initialize/finalize tables, initialize/ref/deref/put/free objects, add/remove objects, and acquire objects for read or write.
- `llist_head_t` is a Linux-style circular doubly linked list with explicit payload pointer.
- `genlist_t` is a separate doubly linked list of generic entries with helpers to add/delete/remove/insert/flush/test empty.
- Debug routines expose levels L0-L5.

Risk-sensitive invariants:
- Object lifetime combines rwlocks with explicit refcounts; callers must pair object gets/puts correctly.
- `llist_head_t` and `genlist_t` do not self-synchronize; external locking is required.
- Object table block sizing and IDs are shared by uverbs and ucma, so type correctness matters at lookup boundaries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_ofs_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_rdma_user_cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_rdma_user_cm.h

This Solaris UCMA compatibility header aliases OFED `rdma_user_cm.h` ABI structures into Solaris-specific names and defines 32/64-bit variants for structures whose native layout differs.

Core definitions:
- Typedefs map all RDMA UCM command and response structs to `sol_ucma_*` names.
- Packed 32-bit and 64-bit versions are provided for bind-address and join-multicast commands.
- The 64-bit variants add reserved padding where needed to preserve expected alignment and structure size.

Risk-sensitive invariants:
- This file is part of user/kernel ABI adaptation for sol_ucma.
- The compat variants are necessary because `rdma_user_cm.h` carries user response pointers and socket-address payloads.
- Any change must preserve the packed wire/control ABI used by user-space RDMA CM libraries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_rdma_user_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_ucma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_ucma.h

This Solaris user-CMA driver header defines sol_ucma file, channel, multicast, event, and global driver state.

Core definitions:
- Limits define two supported paths and up to 128 listens.
- Event-file close flags track no close, event in progress, and disabled state.
- `sol_ucma_file_t` embeds a user object and tracks all CM IDs for an open file, poll support, blocking event CVs, pending event list/count, and close coordination.
- `sol_ucma_chan_t` embeds a user object for each RDMA CM ID and tracks file membership, channel/user IDs, event count, underlying `rdma_cm_id`, QP number/handle, QP flush state, listen backlog, and flags.
- `sol_ucma_mcast_t` tracks multicast user objects, UID/ID, owning channel, address, and event count.
- `sol_ucma_event_t` binds an event response to its channel and optional multicast object.
- `sol_ucma_t` stores global driver synchronization, devinfo, open count, LDI/module handles, IB/iWARP client handles, and initialization state.

Risk-sensitive invariants:
- Event delivery requires synchronization between file event lists, poll wakeups, blocking `GET_EVENT`, and close disablement.
- Channel objects tie user-visible IDs to kernel `rdma_cm_id` lifetime.
- QP flush state coordinates UCMA with sol_uverbs when connection teardown must flush user QPs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ucma/sol_ucma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_umad/sol_umad.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_umad/sol_umad.h

This Solaris UMAD driver header defines user MAD contexts, agents, HCA/port state, IBMF registration records, message wrappers, and driver entry points.

Core definitions:
- Minor-number macros encode node, port, ISSM status, and user context number.
- Only one UMAD instance is supported; up to 16 user contexts are tracked.
- `umad_uctx_t` represents an open file context with registered agents, receive queue, pollhead, and CV.
- `umad_agent_t` records MAD registration request, IBMF registration, owning user context, outstanding messages, lock/CV, and unregister/async flags.
- `umad_hca_info_t` and `umad_port_info_t` describe HCA GUIDs/handles/attributes and per-port minor nodes, GUID/LID, ISSM open count, and IBMF registrations.
- `umad_info_t` is global driver state: devinfo, mutex, IBT client handle, HCA GUID/info arrays, and open contexts.
- `ib_umad_msg_t`, `umad_send`, and `ibmf_reg_info` bridge user MAD buffers to IBMF messages and registrations.

Risk-sensitive invariants:
- Agent unregister must wait for outstanding messages and async handling to drain.
- Receive queues and agent lists have separate locks.
- Minor encoding leaves room for 16 boards and 16 ports, with ISSM marked by a high bit.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_umad/sol_umad.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs.h

This Solaris user-verbs kernel-agent header defines the main sol_uverbs module context and all user resource objects exposed to OFED user verbs.

Core definitions:
- Minor layout supports up to 16 HCA minors plus event and max minor constants.
- `uverbs_event_t` wraps async/completion event descriptors, event-file linkage, object linkage, and an event counter.
- `uverbs_module_context_t` stores global IBT client registration, HCA GUID/list state, HCA records, device info, and event device node.
- `uverbs_ufile_uobj_t` represents async/completion event files with refcount, poll state, owning context, event list, CQ notification control, and CQ count.
- `uverbs_uctxt_uobj_t` tracks an opened HCA/user context and all owned PD/MR/CQ/QP/SRQ/AH lists plus async/completion event files.
- Resource objects wrap PDs, MRs, CQs, SRQs, AHs, and QPs with IBTF handles, context list entries, event tracking, dependency counts, and free-pending state.
- Extern user-object tables provide global ID lookup for each resource class.

API surface:
- Command handlers for context, PD, AH, device/port/GID/PKey query, MR registration, completion channel creation, and status/capability conversions.
- Free helpers for PD/QP/SRQ/CQ and inline typed lookup helpers for read/write access.

Risk-sensitive invariants:
- User context lists are cleanup ownership lists; object tables are the authoritative lookup path.
- QP objects retain dependency handles for PD/CQ/SRQ and coordinate with UCMA through QP free state and CQ notification control.
- Event counters and object event lists must be drained on resource destruction.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs2ucma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs2ucma.h

This small inter-driver contract header declares the sol_uverbs symbols that sol_ucma dynamically uses.

Core definitions:
- `SOL_UCMA_UVERBS_PATH` names the UCMA access path through sol_uverbs.
- Named symbol strings and function pointer typedefs expose:
  - IB/iWARP client handle retrieval.
  - QP-number to QP-handle lookup.
  - Disabling user QP modification.
  - Enabling/disabling CQ notification for CQs associated with a QP.
  - Setting QP free state.
  - Flushing a QP.
- `sol_uverbs_cq_ctrl_t` models CQ notification not-set/enable/disable.
- `sol_uverbs_qp_free_state_t` models enable free, disable free, and free pending.

Risk-sensitive invariants:
- This is a runtime symbol ABI between two kernel drivers; names and signatures must stay stable.
- CQ notification gating exists to ensure the first user completion is delivered only after connection establishment.
- QP free-state control prevents UCMA and uverbs from racing connection teardown against user QP destruction.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs2ucma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_comp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_comp.h

This sol_uverbs completion-queue header declares command handlers and event callback support for user CQ operations.

API surface:
- User command handlers for create, destroy, resize, request-notify, and poll CQ.
- `sol_uverbs_comp_event_handler()` handles IBTF CQ completion callbacks for a CQ.

Risk-sensitive invariants:
- CQ command handlers consume user ABI buffers with explicit input/output lengths.
- Completion delivery integrates with sol_uverbs event files and CQ event counters defined in `sol_uverbs.h`.
- CQ destruction must coordinate with active QPs and pending completion events.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_comp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_event.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_event.h

This sol_uverbs event header declares async/completion event-file lifecycle, event cleanup, async HCA event handling, and event-file read/poll operations.

API surface:
- Allocate and release event files.
- Handle asynchronous IBT HCA events.
- Release CQ completion-channel association.
- Release queued user events for CQs, QPs, and SRQs.
- Close, read, and poll event files.

Risk-sensitive invariants:
- Event files back both async and completion channels and must wake pollers/blocking readers correctly.
- Resource destruction must remove object-specific pending events to avoid dangling pointers.
- Async events interact with HCA callbacks and user-visible event descriptors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_hca.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_hca.h

This sol_uverbs HCA-management header defines the shared HCA list and common client/event-handler API used by OFA kernel agents.

Core definitions:
- `sol_uverbs_hca_t` tracks one IBT HCA: list entries, event handler list/lock, client data list/lock, IBT client/HCA handles, GUID, HCA attributes, port count, port info pointer, and port info size.
- `sol_uverbs_ib_client_t` registers add/remove callbacks for HCA availability.
- `sol_uverbs_ib_event_handler_t` registers per-HCA async event callbacks.
- `SOL_UVERBS_INIT_IB_EVENT_HANDLER` initializes event handlers.

API surface:
- Common HCA init/fini, handle-to-HCA lookup, client register/unregister, client data get/set, event handler register/unregister, user-QP-ID to IBT handle lookup, and disabling/enabling user QP modify.

Risk-sensitive invariants:
- sol_uverbs owns the shared IBT client handle used by multiple OFA user-kernel agents.
- HCA client and event-handler lists require their matching locks.
- HCA add/remove callbacks define availability ordering for dependent OFED compatibility modules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_hca.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_qp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_qp.h

This sol_uverbs QP/SRQ command header declares queue-pair and shared-receive-queue handlers plus multicast attach/detach support.

Core definitions:
- `IBT_TO_OFA_QP_STATE()` maps IBTF states into OFA QP states, collapsing SQ-drain variants to `IB_QPS_SQD`.

API surface:
- Create, destroy, modify, and query QP.
- Create, modify, query, and destroy SRQ.
- Attach and detach multicast.
- Detach all multicast entries owned by a user QP.

Risk-sensitive invariants:
- QP modification may be disabled by UCMA while connection manager owns transitions.
- Multicast memberships attached to a QP must be detached during QP cleanup.
- QP state translation assumes OFA and IBTF state ordering up to SQ-drain.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_qp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds.h

This legacy RDS socket/STREAMS header defines the main socket-side RDS state and bind fanout interfaces.

Core definitions:
- `rds_t` stores reference synchronization, TPI state, flags, socket family, credentials, bound port/source address, upper-layer private data, bind-hash linkage, port quota, and zone ID.
- `RDS_CLOSING` marks close state.
- Refcount macros increment/decrement under `rds_lock`; final decrement calls `rds_free()`.
- Bind fanout entries contain an RDS chain head and lock, padded for cache layout.
- Bind hash is based on network-order local port and a power-of-two fanout size.
- `AF_INET_OFFLOAD` is defined as `30`.

API surface:
- Hash init, create/free, bind hash insert/remove/fanout lookup, message delivery entry point, bind-address/local-interface checks, and module init/fini.

Risk-sensitive invariants:
- Refcount macro frees while holding `rds_lock`, so `rds_free()` must match that expectation.
- Bind fanout and port quota are zone-aware.
- This is socket-facing RDS, separate from the IB transport implementation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_kstat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_kstat.h

This header defines legacy RDS kstats and convenience macros for updating them.

Core definitions:
- `struct rds_kstat_s` exposes counters/gauges for ports, sessions, TX/RX bytes and packets, errors, pending RX packets, ACKs, post-receive calls, stall/unstall events, ignored stalls, ENOBUFS, EWOULDBLOCK, failovers, port quota, and quota adjustments.
- Generic helpers increment, decrement, set, and get `kstat_named_t` values with a boolean likely indicating whether the value is a mutable gauge.
- Macros wrap every named statistic update.

Risk-sensitive invariants:
- Pending packet and port count stats are decremented as gauges; traffic/error stats are monotonic counters.
- Correct flow-control diagnosis depends on stall/unstall and pending-packet stats being updated in all paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_kstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_transport.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_transport.h

This small legacy RDS header defines the transport operations vector used by the socket layer to call the IB transport.

Core definitions:
- `rds_transport_ops_t` provides hooks to open/close IB, send a message, resume a port, and look up an interface by name.
- Global `rds_transport_ops` points to the active transport implementation.
- Extern tunables include user buffer size and RX pending packet high-water mark.

Risk-sensitive invariants:
- The socket layer depends on the transport vector being installed before send/open paths.
- Send hook carries source/destination IPs, ports, and zone ID, so transport must preserve zone isolation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_transport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_buf.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_buf.h

This legacy RDS-over-IB buffer header defines send/receive buffer states, buffer objects, buffer pools, and pool-management APIs.

Core definitions:
- Send buffer states: free, pending, error.
- Receive buffer states: free, posted, on socket queue.
- `rds_buf_t` links buffers to endpoints, SGL data segments, state, and receive free callbacks.
- `rds_bufpool_t` tracks lock-protected buffer-pool sizing, busy/free counts, free list head/tail, memory backing, CV waiters, and polling state used when interrupts are disabled.
- Global data/control receive pools are declared.

API surface:
- Initialize/free receive caches and per-endpoint send/receive pools.
- Allocate/free generic buffers, send buffers, and receive buffers.
- Test whether endpoint send/receive queues are empty.

Risk-sensitive invariants:
- Pool counts, free lists, and busy counts must stay consistent under `pool_lock`.
- `pool_cv`, waiter count, and `pool_sqpoll_pending` are only used in polling/no-interrupt mode.
- Receive buffers use `frtn_t` for STREAMS `esballoc()` ownership.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_cm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_cm.h

This small legacy RDS-over-IB CM header defines connection-management tuning constants.

Core definitions:
- `RDS_IB_PATH_RETRY` sets CM path retry count to 7.
- `RDS_IB_RNR_RETRY` uses infinite RNR retry.
- `RDS_IB_MAX_SGL` limits work requests to one SGL entry.
- `RDS_IB_PKT_LT` uses the packet lifetime from the path record.

Risk-sensitive invariants:
- These constants shape RC channel establishment and retry behavior.
- Single-SGL assumptions must match buffer construction in send/receive paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_cm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_debug.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_debug.h

This legacy RDS debug header defines logging levels and debug print entry points.

Core definitions:
- Label is `"RDS"`.
- Levels L0-L5 distinguish major errors, admin-facing info, progressively verbose debug, and excessive trace.
- `RDS_LOG_LINTR` is reserved for interrupt/softint/taskq/timeout-context messages.
- In DEBUG builds, high-volume macros map to real functions; otherwise L3-L5/intr debug macros compile out.
- L0-L2 functions are always declared and mapped.

Risk-sensitive invariants:
- Non-DEBUG builds still retain lower-level logging.
- Interrupt-context logging has a separate macro to avoid misuse of normal debug paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ep.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ep.h

This legacy RDS-over-IB endpoint/session header defines the RC endpoint model, session state machine, QP accounting, and endpoint/session APIs.

Core definitions:
- Endpoint types distinguish control and data RC channels.
- Endpoint states cover unconnected, active/passive pending, connected, closing, closed, and error.
- Session states cover created, failed, init, connected, HCA closing, error, active/passive closing, closed, fini, and destroy.
- `RDS_SESSION_TRANSITION` changes session state under writer lock.
- `rds_qp_t` tracks queue-pair depth, level, low-water mark, and pending refill task state.
- `rds_ep_t` contains endpoint identity, HCA/send memory registration info, endpoint lock/state, IB channel/CQ handles, send/receive pools, receive QP state, segmentation tracking, failover buffer IDs, and RDMA ACK memory.
- `rds_session_t` owns active/passive identity, remote/local IP/GIDs, lock/state, data/control endpoints, failover flag, local/remote port maps, and path info.

API surface:
- Session create/init/reinit/open/close/lookup/recycle/fini paths.
- Endpoint RC channel allocation/free, posting receives, polling send completions.
- RC channel open/close, message receive/control handling, send-error handling, and service-console path lookup.

Risk-sensitive invariants:
- Session list membership is protected by global session lock; per-session state by `session_lock`.
- Local and remote port maps are separate congestion/stall bitmaps.
- Failover uses endpoint last-local/remote-buffer IDs and ACK memory fields.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ep.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ib.h

This legacy RDS-over-IB header declares global tunables, HCA state, soft state, and IB initialization/service APIs.

Core definitions:
- Global configuration covers node count, buffer sizes, packet size, send/receive buffer counts, low-water marks, pending RX high-water mark, RNR retry, path retry, and packet lifetime.
- Performance tunables cover interrupt disabling, polling fullness threshold, work-completion signaling, and wait time.
- Loopback port map is a fixed bitmap of 8192 bytes protected by rwlock.
- `rds_hca_t` tracks HCA list state, GUID, port count, IBT handles, PD/MR/lkey/rkey, service-bind handles, attributes, and port info.
- `rds_state_t` is singleton soft state: session list/lock, IB client handle, HCA list/lock, service handle, and service ID.

API surface:
- Service register/bind, receive CQ handler, GID/GUID-to-HCA lookup, IB initialize/deinitialize, and logging lifecycle.

Risk-sensitive invariants:
- HCA state transitions are attach/detach oriented and separate from session state.
- Registered receive-pool memory keys are stored per HCA and used by endpoint receive buffers.
- The driver uses one global soft state rather than per-instance state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_ib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_protocol.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_protocol.h

This legacy RDS-over-IB wire-protocol header defines versioning, default sizing, CM private data, data headers, and control packets.

Core definitions:
- RDS version is 4 and service ID is Sun-OUI-based `0x1000144F00000001`.
- Defaults include max nodes, 4K user data buffer size, per-session send/receive buffer counts, receive low-water marks, and pending RX high-water percentage.
- `RDS_THIS_ARCH` permits only homogeneous Solaris architecture interoperability across sparcv9, amd64, and i386.
- `rds_cm_private_data_t` carries IBT IP CM private data, version, architecture, endpoint type, failover flag, last buffer ID, user buffer size, ACK rkey, and ACK address.
- `rds_data_hdr_t` carries buffer ID, payload length, packet count, packet sequence number, source port, and destination port.
- Control packet codes cover stall, unstall, all-ports stall/unstall, heartbeat, and close session.
- `rds_ctrl_pkt_t` carries port and control code.

Risk-sensitive invariants:
- Wire structs contain native-width pointer-sized fields; the header explicitly limits interoperability to homogeneous Solaris architectures.
- Packet segmentation relies on `dh_npkts` and `dh_psn`.
- Failover recovery depends on private-data last buffer IDs and ACK memory registration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_protocol.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_sc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_sc.h

This legacy RDS service-console header defines path endpoint records and path notification hooks.

Core definitions:
- `rds_path_endpoint_t` records interface type, IP address, node IP address, and interface name.
- `rds_path_t` pairs local and remote endpoints.
- Hooks declare cluster interface naming and path up/down notifications.

Risk-sensitive invariants:
- Path lookup and path notifications connect RDS IB sessions to external cluster/service-console topology.
- Interface names are stored as pointers, so ownership/lifetime is external.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rdsib_sc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/ib.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/ib.h

This OFED-derived RDSv3 InfiniBand transport header defines the RDSv3-over-IB connection, device, send/receive ring, ACK, credit, MR, and statistics interfaces.

Core definitions:
- Defaults cover FMR size/pool, max SGE, receive SGE count, send/receive WR counts, retry count, supported minor protocols, max receive allocation, and CQ poll size.
- Page fragments represent fixed `RDSV3_FRAG_SIZE` receive fragments with DMA mapping metadata.
- `rdsv3_ib_incoming` wraps generic incoming messages with IB fragment lists and pool/device ownership.
- `rdsv3_ib_connect_private` is versioned CM private data containing addresses, protocol version/mask, ACK sequence, and credit.
- Send/receive work records tie messages/RDMA ops/fragments to work rings.
- `rdsv3_ib_work_ring` tracks alloc/free positions and counters plus an empty wait queue.
- `rdsv3_ib_connection` stores CM ID, PD, MR, CQs, send and receive rings, soft-CQ threads, receive assembly state, ACK state, flow-control credits, batching counters, and receive allocation limit.
- `rdsv3_ib_device` stores per-HCA IPs, connections, OFED device/PD, fragment/incoming/FMR pools, limits, HCA attributes, soft-CQ workers, IBT HCA handle, and AF group.
- Stats cover connection races, CQ/tasklet activity, TX/RX ring pressure, credits, ACKs, and MR pool behavior.

Risk-sensitive invariants:
- Credit packing assumes `atomic_t` is at least 32 bits.
- ACK work requests use magic WR ID `~0ULL`; sends set high bit `RDSV3_IB_SEND_OP`.
- Device connection lists are protected by either global nodev lock or per-device spinlock.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/ib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/info.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/info.h

This OFED-derived RDSv3 info header defines the generic snapshot/copy interface used by RDSv3 diagnostic ioctls.

Core definitions:
- `rdsv3_info_iterator` carries a user destination address and current byte offset.
- `rdsv3_info_lengths` reports number of records and bytes per record.
- `rdsv3_info_func` callbacks describe available snapshot size and copy data when the user buffer is large enough.
- `rdsv3_info_copy` wraps `ddi_copyout()` and advances the iterator offset.
- Register/deregister functions attach info callbacks to option names; `rdsv3_info_ioctl()` serves user info requests.

Risk-sensitive invariants:
- Callers infer whether a snapshot was copied by comparing requested lengths to available lengths.
- `rdsv3_info_copy` ignores the `ddi_copyout()` return value in the macro, so caller-side size validation is important.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/info.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/loop.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/loop.h

This OFED-derived RDSv3 loopback transport header declares loop transport state.

Core definitions:
- Extern `rdsv3_loop_transport` exposes the loopback transport operations vector.
- `rdsv3_loop_exit()` tears down loopback transport state.

Risk-sensitive invariants:
- Loopback transport must integrate with generic RDSv3 transport registration and socket receive paths.
- Loopback can pass messages directly back into receive logic, as described by the message structure comments in `rdsv3.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/loop.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma.h

This OFED-derived RDSv3 RDMA header defines memory-region and RDMA operation state used by socket options and control messages.

Core definitions:
- `rdsv3_mr` stores AVL linkage, refcount, key, use-once/invalidate/write flags, dead-state bit, owning socket, transport, and transport-private MR data.
- `RDSV3_MR_DEAD` marks a memory region dead using bit operations.
- `rdsv3_rdma_sg` binds a user memory cookie, RDS iovec, send WR, memory-IO handle, and HCA handle.
- `rdsv3_rdma_op` stores remote key/address, write/fence/notify/error/mapped flags, notifier, byte/entry counts, generic scatterlist pointer, and inline RDMA SG array.
- Cookie helpers pack/unpack a 32-bit rkey and 32-bit offset into `rds_rdma_cookie_t`.

API surface:
- Get/free MR socket options, destination-specific MR lookup, key drop, control-message parsing for RDMA args/destination/map, RDMA op free, send complete, and final MR release.

Risk-sensitive invariants:
- MR release is refcounted and finalizes through `__rdsv3_put_mr_final()`.
- Cookie layout is externally visible through RDS RDMA APIs.
- Dead-state bit prevents reuse while outstanding references drain.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma_transport.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma_transport.h

This small RDSv3 RDMA transport header declares RDMA transport initialization and RDMA-CM integration.

Core definitions:
- `RDSV3_RDMA_RESOLVE_TIMEOUT_MS` is 5000 ms.
- `rdsv3_rdma_cm_event_handler()` is the RDMA-CM event callback.
- `rdsv3_rdma_init()` and `rdsv3_rdma_exit()` manage RDMA transport layer state.
- IB transport init/exit and `rdsv3_ib_transport` are declared.

Risk-sensitive invariants:
- RDMA-CM route/address resolution timeout is part of connection behavior.
- RDMA transport lifecycle must coordinate with IB transport registration and shutdown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdma_transport.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3.h

This OFED-derived main RDSv3 header defines the protocol version, core connection/message/socket structures, transport operations, statistics, and subsystem APIs.

Core definitions:
- Protocol version is RDS 3.1, with port `18634`.
- Congestion maps are per-address bitmaps covering 65536 ports.
- Connection states are atomically tracked: down, connecting, disconnecting, up, error.
- `rdsv3_connection` stores local/remote addresses, congestion maps, send lock/generation/senders, in-flight transmit offsets, send/retrans queues, RX sequence, transport hooks/data, atomic state, reconnect timing, work items, CM lock, congestion map transfer state, unacked counters, and protocol version.
- `rdsv3_header` carries sequence, ACK, length, source/destination ports, flags, credit, checksum, and extension header space.
- Extension headers support version, RDMA completion key, and RDMA destination key/offset.
- `rdsv3_incoming`, `rdsv3_message`, and `rdsv3_notifier` define receive objects, send/receive messages, RDMA notifier delivery, refcounts, list ownership flags, and RDMA metadata.
- `rdsv3_transport` is the transport ops vector for connection allocation, connect/shutdown, transmit, congestion map transmit, RDMA transmit/MR handling, receive, CM callbacks, stats, and exit.
- `rdsv3_sock` stores socket linkage, bound/connected addresses/ports, preferred transport, cached connection, congestion state, send/receive queues, notifier queue, RDMA keys, options, credentials, and zone.

API surface:
- Bind, connection lifecycle, receive/send, congestion, stats/sysctl, threads, transport registration, message construction/extensions/checksum, RDMA, and service-console helpers.

Risk-sensitive invariants:
- Message list flags avoid lock nesting between socket and connection lists.
- Connection state transitions use atomic compare-and-swap and imply memory ordering.
- Checksum covers the RDSv3 header and treats zero checksum as acceptable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr.h

This Solaris-only RDSv3 header declares asynchronous/soft-CQ thread and HCA affinity group APIs.

Core definitions:
- Opaque `rdsv3_af_grp_t` and `rdsv3_af_thr_t` represent HCA affinity groups and async worker threads.
- Drain callbacks take a single private data pointer.
- Creation flags can bind HCA, interrupt, or worker execution to CPUs.
- APIs initialize the AF subsystem, create/destroy/draw HCA groups, retrieve an IBT scheduler handle, create normal or interrupt-backed AF threads, destroy threads, and fire threads.

Risk-sensitive invariants:
- CPU binding flags influence CQ and worker placement for performance.
- Interrupt-backed thread creation receives an IBT CQ handle, tying affinity to completion delivery.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr_impl.h

This Solaris-only private RDSv3 AF-thread header defines the implementation structures for CPU/MSI-X affinity and worker state.

Core definitions:
- `ddi_intr_set_affinity` is mapped to `set_intr_affinity`.
- Combined `SCQ_BIND_CPU` binds HCA and worker CPUs.
- Constants define maximum connections per HCA group, per-connection CPU count, CPU/MSI-X pool sizes, and CPU flag bits.
- Static CPU and MSI-X pools track available binding candidates.
- `rdsv3_af_grp_s` stores HCA handle, scheduler handle, assigned HCA CPU, per-connection CPU pool, and next index.
- `rdsv3_af_thr_s` stores lock/CV, worker thread, callback data, CPU binding, state flags, creation flags, drain callback, group pointer, and interrupt handle.
- State flags track processing, bound, armed, and condemned states.

Risk-sensitive invariants:
- Worker state is protected by `aft_lock`.
- Condemned state coordinates teardown with worker wakeups.
- CPU pool sizing caps affinity assignment at 128 CPUs/MSI-X entries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_af_thr_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_debug.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_debug.h

This RDSv3 debug header defines logging levels, debug print macros/functions, trace hooks, and logging lifecycle.

Core definitions:
- Label is `"RDSV3"`.
- Levels L0-L5 and LINTR mirror legacy RDS logging semantics.
- DEBUG builds enable L3-L5 and interrupt debug macros; non-DEBUG builds compile them out.
- L0-L2 print functions remain declared for all builds.
- `rdsv3_trace()`, `rdsv3_vprintk()`, logging initialization/destruction, and printk rate limiting are declared.

Risk-sensitive invariants:
- Interrupt/taskq logging is separated through LINTR.
- Rate limiting is available for high-volume paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_debug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_impl.h

This Solaris-only RDSv3 implementation header provides Linux-compatibility primitives and illumos helper declarations used by the OFED-derived RDSv3 code.

Core definitions:
- Big-endian typedefs map to native integer types.
- Atomic compatibility maps Linux-style `atomic_t`, compare/exchange, decrement-test, bit operations, and little-endian bit operations onto illumos atomics.
- Timing/page constants emulate Linux-style `jiffies`, `HZ`, `PAGE_SIZE`, and bit widths.
- Error-pointer macros emulate Linux `ERR_PTR`, `IS_ERR`, and `PTR_ERR`.
- List macros add remove/splice and safe iteration helpers over illumos lists.
- `rdsv3_wait_queue_t` emulates Linux wait queues with mutex/CV/waiter count and wait/wake macros.
- `rsock_t` is an internal socket shim with upper handle/upcalls, lock, flags, sleep wait queue, send/receive buffers, refcount, and protocol info.
- Workqueue and delayed-work structs emulate Linux work items using illumos locks, timeouts, and list queues.
- `rdsv3_scatterlist` maps a virtual address/length to IBT SGL and mapping handle.
- Control-message macros provide CMSG alignment/traversal without depending on XPG guard exposure.
- OFUV-to-IB helper macros extract IBTF handles from OFED wrapper objects.
- `rdsv3_hdrs_mr` describes registered header memory.

API surface:
- Transport init, interface/IP ioctl helpers, delayed work/workqueue operations, socket allocation/init/exit, connection constructors/comparators, loop init, MR compare, cmsg put, bind verification, checksum, DMA map/unmap, and socket ref/flag helpers.

Risk-sensitive invariants:
- `PAGE_SIZE` is hardcoded to 4096 with a comment noting this is a workaround.
- Wait macros increment/decrement waiter counts around CV waits and require condition predicates to be stable under the wait queue mutex.
- Linux compatibility bit operations differ for SPARC little-endian bitmap indexing through `LE_BIT_XOR`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_sc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_sc.h

This RDSv3 service-console header mirrors the legacy RDS service-console path structures and hooks.

Core definitions:
- `rds_path_endpoint_t` records interface type, IP address, node IP address, and interface name.
- `rds_path_t` pairs local and remote endpoints.
- Path hooks declare cluster interface naming and path up/down notifications.

Risk-sensitive invariants:
- RDSv3 service-console integration shares struct names with legacy RDS, so include ordering and namespace expectations matter.
- Path notification callbacks are external integration points for link/topology changes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rdsv3/rdsv3_sc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_pkt_hdrs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_pkt_hdrs.h

This core IB header defines wire-layout structs and masks for InfiniBand packet headers.

Core definitions:
- `ib_lrh_hdr_t` models the Local Route Header with VL/version, service level/next header, DLID, packet length, and SLID.
- LRH masks extract virtual lane, link version, service level, next-header type, and packet length; next-header values include raw, IPv6, BTH, and GRH.
- `ib_grh_t` models the Global Route Header with IP version/traffic class/flow label, payload length, next header, hop limit, SGID, and DGID.
- GRH masks extract IP version, traffic class, flow label, and BTH next-header value.
- `ib_bth_hdr_t` models Base Transport Header fields: opcode, solicited/migration/pad/version byte, P_Key, destination QP, ACK/PSN.
- BTH masks extract solicited event, migration request, pad count, transport version, destination QP, ACK request, and PSN.
- `ib_deth_hdr_t` models Datagram Extended Transport Header Q_Key and source QP.

Risk-sensitive invariants:
- These structs describe on-wire IB headers; consumers must handle endian conversion externally as needed.
- QP and PSN fields are 24-bit values masked from 32-bit fields.
- `IB_DETH_SRC_QP_MASK` is defined twice with the same value.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_pkt_hdrs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_types.h

This core IBTA primitive-types header defines GUID/GID/LID/PKey/QKey/service-ID and MTU types and constants.

Core definitions:
- EUI-64 masks/shifts, LID ranges, permissive LID, GUID/subnet-prefix typedefs.
- Unicast and multicast GID structs are wrapped in `ib_gid_t`, with convenience macros for unicast and multicast fields.
- GID prefix constants cover default/subnet-local/site-local and multicast prefix/transient flag/scope values.
- Multicast join states, multicast QPN, and IPoIB multicast GID prefixes are defined.
- LID/path-bits, default/invalid PKeys, GSI QKey, privileged QKey bit, PKey/QKey counter types, SM key, ethertype, QPN/EECN, message length, memory virtual address/length, and service ID types are declared.
- `ib_mtu_t` enumerates unspecified, 256, 512, 1K, 2K, and 4K MTUs.
- `ib_time_t` is a timeout exponent with a 6-bit mask.
- Service ID AGN masks and IP-address-derived service ID masks are defined.

Risk-sensitive invariants:
- These are foundational ABI types used across IBTL, OFED compatibility, nexus, and clients.
- Multicast and service-ID constants encode IBTA/IPoIB conventions and must remain stable.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ib_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex.h

This private IB nexus header defines child-node metadata, cfgadm/configuration states, reprobe coordination state, and global nexus instance state.

Core definitions:
- Internal return codes distinguish success, failure, offline failure, busy, and invalid node.
- IOC node data records IOU/IOC GUIDs, ID string, GID count, optional disconnected IOC profile, stringified IOC GUID, and PHCI GUID.
- Port node data records port number, communication-service index, port/HCA GUIDs, PKey, and parent dip.
- Pseudo-node data records node address, unit address/length, driver name, and merge-node flag.
- Node types include port, VPPA, HCA service, IOC, and pseudo nodes; HCA child mask groups port/VPPA/HCA service nodes.
- Node states track cfgadm configured/unconfigured/configuring/unconfiguring.
- Reprobe/AP flags track property-update notification behavior, always-notify behavior, IOC wait, and AP configured/unconfigured/configuring state.
- `ibnex_node_data_t` stores per-child devinfo private data plus typed node payload, list links, node type/state, reprobe state, and AP state.
- `ibnex_t` is the singleton IB nexus instance: dip, mutex, communication service name lists, child-node lists, NDI event handle/cookie, reprobe CV/state, disconnected IOC count, pseudo init flag, shared IOC list/CV/state, and taskq.
- Defines compatibility-name limits, enumeration source flags, node address size, GUID formatting, invalid PKey test, DDI event tag, and devtree status values.

Risk-sensitive invariants:
- Node type values are shared with the cfgadm IB plugin and must remain synchronized.
- Reprobe logic is designed to serialize reprobe-all with IOC-specific reprobes while allowing distinct IOC reprobes in parallel.
- Node payload structs are treated as stable read-only data after creation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex_devctl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex_devctl.h

This IB nexus devctl ABI header defines cfgadm attachment-point commands, user/kernel ioctl payloads, and HCA/port query structures.

Core definitions:
- APID types distinguish base, HCA, dynamic IOC/DLPI, and unknown attachment points.
- Dynamic APIDs use `"::"` as separator; strings name fabric, VPPA, port, and HCA service nodes.
- Service parser enum covers `name`, `class`, port service list, VPPA service list, HCA service list, and none.
- nvlist key strings identify node info, APID, type, receptacle/occupant state, and condition.
- Devctl subcommands cover node counts, snapshot size/get, dynamic device path size/get, HCA client list size/info, unconfigure client size/info, PKey table update, config-file service add/delete, verbose HCA info size/data, and IOC config update.
- `ibnex_ioctl_data_t` and `_32_t` carry command, buffer, buffer size, AP ID pointer/length, and misc arg for `DEVCTL_AP_CONTROL`.
- General ioctl codes expose API version, HCA GUID list, HCA query, and HCA port query through `/devices/ib:devctl`.
- API version is `1`.

HCA query ABI:
- `ibnex_ctl_hca_info_t` and 32-bit variant expose node/system-image GUIDs, port count, driver identity, device path pointer/length, capability flags, vendor/device/version IDs, channel/CQ/SGL/memory/window/RDMA/multicast/partition/PD/SRQ/FMR/LSO/inline/CQ moderation limits, firmware version, and detailed WQE sizes.
- Query wrapper supplies target HCA GUID and user-allocated device-path buffer.

Port query ABI:
- `ibnex_ctl_hca_port_info_t` and 32-bit variant expose LID, violation counters, SM SL/LID, physical/link state, port number, width/speed support/enabled/active, MTU, LMC, SGID/PKey table pointers and sizes, default PKey index, max VL, init type reply, subnet timeout, port capabilities, and max message size.
- Query wrapper supplies target HCA GUID/port plus user-allocated SGID and PKey tables.

Risk-sensitive invariants:
- Pointer-bearing structures have explicit 32-bit variants for 32-bit apps on a 64-bit kernel.
- User buffers are size-negotiated; insufficient buffers return lengths and/or NULL pointers rather than full data.
- The ioctl namespace deliberately avoids collision with generic devctl AP commands.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibnex/ibnex_devctl.h -->