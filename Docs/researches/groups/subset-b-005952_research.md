# subset-b-005952 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_verbs.h -->
# sources/distributed-fs/ceph-client/include/rdma/ib_verbs.h

Purpose: This is the central kernel RDMA verbs contract for the Ceph client source snapshot. It defines InfiniBand/RoCE/iWARP/OPA core object types, capabilities, event types, work request/completion formats, provider callbacks, and wrappers used by upper-layer protocols and low-level drivers.

Important APIs/types/functions: The file exports `union ib_gid`, `struct ib_gid_attr`, transport/network/link-layer enums, device and port capability flags, `struct ib_device_attr`, `struct ib_port_attr`, `struct ib_event`, `struct rdma_ah_attr`, completion and work-request types (`ib_wc`, `ib_send_wr`, `ib_recv_wr`, RDMA/atomic/UD/reg wrappers), access flags, and resource objects (`ib_ucontext`, `ib_pd`, `ib_ah`, `ib_cq`, `ib_srq`, `ib_wq`, `ib_qp`, `ib_mr`, `ib_mw`, `ib_flow`, `ib_device`). `struct ib_device_ops` is the provider vtable: post send/recv, CQ polling/notification, MAD processing, device/port query and modify, GID/P_Key management, user mmap, PD/AH/SRQ/QP/CQ/MR/MW/XRCD/flow/WQ/DM/counter lifecycle, hardware stats, iWARP CM callbacks, and sub-device operations. Core wrappers include `ib_register_device`, `ib_register_client`, `ib_alloc_pd`, `rdma_create_ah`, `ib_create_srq`, `ib_create_qp`, `ib_post_send`, `ib_post_recv`, `ib_poll_cq`, `ib_req_notify_cq`, DMA mapping helpers, MR registration/mapping helpers, multicast attach/detach, `ib_modify_qp_is_ok`, port capability predicates, and address-handle accessors.

Control flow: Most functions declared here are call-through contracts. Consumers allocate core objects, fill init attributes, then call wrappers that validate common state and dispatch into `ib_device->ops`. Fast paths are direct: `ib_post_send` and `ib_post_recv` call provider queue-post callbacks; `ib_poll_cq` and `ib_req_notify_cq` call CQ ops; DMA helpers choose normal DMA API behavior or virtual-DMA behavior based on `dev->dma_device`. QP control follows the IB state machine (`RESET`, `INIT`, `RTR`, `RTS`, `SQD`, `SQE`, `ERR`) with attribute masks checked by `ib_modify_qp_is_ok`.

State and persistence behavior: This header defines in-memory kernel state, not durable storage. Persistence is by object lifetime and reference ownership: `ib_device` has registration refcounts, event handler lists, client data, port caches, CQ pools, netdev compatibility state, subdevice lists, and resource tracking; PD/CQ/SRQ/QP/MR/MW objects carry use counts, uobject links, and restrack entries. User ABI compatibility is handled through `ib_udata` length/zero-fill rules and mmap entries in an xarray.

Dependencies and integration points: It depends on Linux device, DMA, netdevice, xarray, cgroup, net namespace, uverbs, MAD, SA, cache, signature, and restrack facilities. It integrates with RDMA CM (`rdma_cm_id`), iWARP CM (`iw_cm_id`), netlink resource reporting, sysfs hardware stats, IPoIB/RDMA netdevs, RoCE GID rescans, OPA address handling, and provider modules.

Risks: Misstated provider callbacks or capability flags can expose unsupported verbs. QP state transitions and attribute masks are security and correctness sensitive. `IB_PD_UNSAFE_GLOBAL_RKEY` deliberately bypasses dynamic MR protection and must stay restricted. DMA helper misuse can leak mappings or skip required syncs. `ib_udata` size handling is an ABI boundary; new fields require strict zero/comp-mask validation. GID, P_Key, netdev, and event-handler lifetimes are RCU/refcount sensitive.

Test signals: Build coverage must catch provider vtable signature drift and enum/uapi mismatches. Runtime tests should cover QP create/modify/destroy, CQ poll/notify races, MR access validation, DMA map/unmap paths including virtual DMA, RoCE GID add/delete, netdev association, multicast attach/detach, device unregister while objects exist, and uverbs input/output length compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ib_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iba.h -->
# sources/distributed-fs/ceph-client/include/rdma/iba.h

Purpose: Provides generic InfiniBand Architecture field access helpers for packed big-endian management datagram layouts. It lets generated field macros describe byte offsets, bit offsets, masks, widths, and memory blocks, then uses common `IBA_GET`, `IBA_SET`, `IBA_GET_MEM`, and `IBA_SET_MEM` accessors.

Important APIs/types/functions: `_iba_get8/16/32/64` and `_iba_set8/16/32/64` load and update big-endian fields in CPU order; 64-bit accesses use unaligned helpers because MAD layouts can align larger fields only to four bytes. `IBA_FIELD_BLOC`, `IBA_FIELD8_LOC`, `IBA_FIELD16_LOC`, `IBA_FIELD32_LOC`, `IBA_FIELD64_LOC`, and `IBA_FIELD_MLOC` encode field metadata. `IBA_GET` and `IBA_SET` wrap `FIELD_GET` and `FIELD_PREP`; memory helpers copy raw byte fields.

Control flow: Callers define a field macro with a struct type, offset, mask, and width. `IBA_GET(field, ptr)` casts the pointer to that struct, advances by the field offset, reads the native unit, extracts masked bits, and returns the typed value. `IBA_SET` reads the existing unit, clears the mask, ORs the prepared value, and writes it back in big-endian format. Memory fields skip bit extraction and copy bytes after a size warning.

State and persistence behavior: No persistent state is owned. The helpers mutate caller-provided wire buffers in place and preserve bits outside the target mask.

Dependencies and integration points: It depends on Linux `bitfield.h`, endian conversions, `get_unaligned`/`put_unaligned`, `WARN_ON`, and `memcpy`. It is used by generated IBTA and CM message declarations, including `ibta_vol1_c12.h`.

Risks: Field metadata must match the wire specification exactly; an incorrect byte offset or bit numbering silently corrupts management messages. `_IBA_SET_MEM` has a FIXME noting that trailing bytes are not zeroed when setting a shorter memory field, so stale data can remain unless callers clear buffers first. Pointer arithmetic on `void *` is a kernel extension and assumes kernel build semantics.

Test signals: Compile-time use of `GENMASK` catches some invalid widths. Protocol tests should round-trip set/get for boundary bit fields, unaligned 64-bit fields, and memory fields with short lengths, and compare encoded MAD bytes against specification examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iba.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ibta_vol1_c12.h -->
# sources/distributed-fs/ceph-client/include/rdma/ibta_vol1_c12.h

Purpose: Declares packed Communication Management message field layouts from IBTA Volume 1, Chapter 12. It maps CM request, reply, reject, ready, disconnect, alternate path, and SIDR messages into `IBA_*` field descriptors.

Important APIs/types/functions: `CM_FIELD_BLOC`, `CM_FIELD8_LOC`, `CM_FIELD16_LOC`, `CM_FIELD32_LOC`, `CM_FIELD64_LOC`, and `CM_FIELD_MLOC` offset field locations past `struct ib_mad_hdr`. `CM_STRUCT` creates concrete message structs with a MAD header and opaque data words sized by the table. Exported field macros cover `cm_req_msg`, `cm_mra_msg`, `cm_rej_msg`, `cm_rep_msg`, `cm_rtu_msg`, `cm_dreq_msg`, `cm_drep_msg`, `cm_lap_msg`, `cm_apr_msg`, `cm_sidr_req_msg`, and `cm_sidr_rep_msg`.

Control flow: The file has no executable control flow beyond macro expansion. CM code uses a field macro with `IBA_GET`, `IBA_SET`, or memory-copy helpers to read/write the correct bit range within the CM MAD payload. The macro layer ensures every table offset is relative to the payload start while the generated struct still includes the MAD header.

State and persistence behavior: It defines transient wire message layouts only. State is serialized into management datagram buffers by callers and transmitted by the CM/MAD layers.

Dependencies and integration points: It depends on `rdma/iba.h`, `struct ib_mad_hdr`, and RDMA GID types. It integrates with InfiniBand CM code that constructs REQ/REP/RTU/DREQ/DREP/LAP/APR/SIDR messages and with the MAD transport.

Risks: This is specification-coupled code. Any offset, width, or total-length mismatch breaks interoperability. Private-data field sizes are large memory regions where callers must validate lengths. Vendor ID fields in REP are split across bytes, which is easy to mishandle in consumers.

Test signals: CM encode/decode tests should verify byte-for-byte layouts for every message type, especially bit-packed timeout/retry/service fields, primary/alternate path GIDs, and private-data length boundaries. Build tests catch missing `union ib_gid` or `ib_mad_hdr` dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/ibta_vol1_c12.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iter.h -->
# sources/distributed-fs/ceph-client/include/rdma/iter.h

Purpose: Defines RDMA block DMA iterators for walking DMA-mapped scatterlists in hardware-supported page-size aligned blocks, including a convenience iterator for `ib_umem` memory.

Important APIs/types/functions: `struct ib_block_iter` stores the current scatterlist entry, unaligned DMA address, block count, entry count, next advance, and page-bit alignment. External helpers `__rdma_block_iter_start` and `__rdma_block_iter_next` drive generic scatterlist iteration. `rdma_block_iter_dma_address` returns the current aligned DMA address. `rdma_for_each_block` and `rdma_umem_for_each_dma_block` provide loop macros. `__rdma_umem_block_iter_start` seeds the iterator from `umem->sgt_append.sgt`, `ib_umem_offset`, and `ib_umem_num_dma_blocks`.

Control flow: Callers start an iterator with an SGL and page size, then loop while the internal next function advances to a block. The umem variant adjusts the initial advance for user-memory offset alignment and decrements the expected block count so the macro performs exactly `ib_umem_num_dma_blocks()` iterations.

State and persistence behavior: Iterator state is stack/local caller state. It does not own mappings or persist anything; the underlying SGL must already be DMA mapped and remain valid during iteration.

Dependencies and integration points: It depends on Linux scatterlists, RDMA user memory (`ib_umem`), DMA address types, and page-size helpers. It integrates with MR registration and page list programming paths that need page-aligned DMA chunks.

Risks: The page size must be a supported power-of-two alignment and must match the mapping requirements of the target hardware. Incorrect `nents`, unmapped SGLs, or stale umem state can generate invalid DMA addresses. The umem macro assumes the caller follows `ib_umem_find_best_pgsz()`/`ib_umem_num_dma_blocks()` semantics.

Test signals: Tests should exercise multi-entry SGLs, unaligned user addresses, page-size boundaries, contiguous DMA coalescing, and exact iteration counts for zero-offset and nonzero-offset umems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iw_cm.h -->
# sources/distributed-fs/ceph-client/include/rdma/iw_cm.h

Purpose: Declares the kernel iWARP Connection Manager API. It supplies connection identifiers, event formats, connection parameters, and client/provider callback contracts for RDMA over TCP/iWARP.

Important APIs/types/functions: `enum iw_cm_event_type` covers connect request, connect reply, established, disconnect, and close. `struct iw_cm_event` carries status, local/remote socket addresses, private/provider data, private-data length, ORD, and IRD. `struct iw_cm_id` stores client handler/context, IB device, local/remote and mapped addresses, provider data, provider event callback, provider ref hooks, TOS, and mapping flags. Public APIs include `iw_create_cm_id`, `iw_destroy_cm_id`, `iw_cm_listen`, `iw_cm_accept`, `iw_cm_reject`, `iw_cm_connect`, `iw_cm_disconnect`, `iw_cm_init_qp_attr`, and `iwcm_reject_msg`.

Control flow: Clients create an IW CM ID with a callback, bind addresses through the ID, then either listen/accept/reject passive requests or initiate `iw_cm_connect`. Providers deliver asynchronous events through `event_handler`; the CM delivers client-visible events through `cm_handler`. Destroy and failed accept/reject/connect paths promise no further events for the ID after return except the documented close lifecycle.

State and persistence behavior: The ID is an in-memory connection state object. It stores address translation state (`mapped`, mapped local/remote addresses), QoS state (`tos`, `tos_set`), address-family restriction (`afonly`), and provider-private state. Reference hooks let providers keep IDs alive during asynchronous work.

Dependencies and integration points: It depends on Linux socket address types and `ib_cm.h`/verbs objects. It integrates with `ib_device_ops` iWARP callbacks, RDMA CM iWARP adaptation, and IW port mapping.

Risks: Event ordering is subtle: events can arrive before connect/accept returns. Destroying an ID from callbacks or failing to respect provider references can cause use-after-free. Address mapping state must stay consistent with the port mapper and socket namespace. Private-data lengths are one-byte in events and reject API.

Test signals: Exercise active and passive connection setup, rejection with private data, abrupt and graceful disconnect, close event delivery, provider reference balancing, QP attribute initialization, TOS/AF-only behavior, and races where events arrive immediately during connect or accept.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iw_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iw_portmap.h -->
# sources/distributed-fs/ceph-client/include/rdma/iw_portmap.h

Purpose: Declares the iWARP port mapper kernel interface used to coordinate real and mapped socket addresses between kernel iWARP CM code and a userspace port mapping daemon/library.

Important APIs/types/functions: Constants define user library, device, interface, and IP address name sizes. Error enums describe invalid netlink messages, create/duplicate/unknown mapping failures, device/user-library info errors, and remote query rejection. `struct iwpm_dev_data` names the RDMA device and interface. `struct iwpm_sa_data` carries local, mapped local, remote, mapped remote addresses, and flags. APIs include init/exit, PID validation/registration, add/query/remove mapping, mapinfo creation/removal, remote info lookup, and netlink callback handlers such as `iwpm_register_pid_cb`, `iwpm_add_mapping_cb`, `iwpm_remote_info_cb`, and `iwpm_hello_cb`.

Control flow: An iWARP client initializes the port mapper for a netlink client, registers the userspace daemon PID and device info, creates or queries address mappings, then removes mapping state when the listener or connection is torn down. Incoming netlink callbacks update kernel mapping tables or report errors.

State and persistence behavior: This header defines in-kernel mapping records indirectly through API contracts. Mapping state is runtime-only and tied to sockaddr tuples, daemon PID validity, netlink client identity, and flags.

Dependencies and integration points: It depends on Linux socket and netlink structures. It integrates with `iw_cm.h` address mapping fields and iWARP CM connection setup, plus userspace iwpmd-style coordination.

Risks: PID validation, duplicate mapping, and removal paths are race-prone. Incorrect sockaddr family/length handling can corrupt mappings across IPv4/IPv6. If the daemon is absent or stale, connection setup may hang or fail. The `IW_F_NO_PORT_MAP` mode in `iw_cm.h` changes semantics by advertising mappings without reserving a socket port.

Test signals: Cover daemon register/unregister, duplicate add, unknown remove, remote query success/reject, IPv4/IPv6 sockaddr round trips, stale PID handling, concurrent mapping updates, and no-port-map behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/iw_portmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/lag.h -->
# sources/distributed-fs/ceph-client/include/rdma/lag.h

Purpose: Declares RDMA link aggregation helper hooks for selecting and releasing RoCE transmit slave netdevices associated with an address handle.

Important APIs/types/functions: `enum rdma_lag_flags` currently defines `RDMA_LAG_FLAGS_HASH_ALL_SLAVES`. `rdma_lag_get_ah_roce_slave` selects a transmit slave for an `ib_device` and `rdma_ah_attr`, with allocation flags. `rdma_lag_put_ah_roce_slave` releases the selected `net_device`.

Control flow: Address-handle creation or send-path setup can request a RoCE LAG slave based on destination attributes. The returned netdevice must later be passed to the put helper. Selection policy is implemented outside this header, likely using Linux bonding/LAG state.

State and persistence behavior: This header owns no state, but the get/put API implies a referenced runtime netdevice object. `ib_device->lag_flags` in `ib_verbs.h` is the likely persisted in-memory policy field.

Dependencies and integration points: It depends on `<net/lag.h>`, `struct ib_device`, and `struct rdma_ah_attr`. It integrates with RoCE address handle creation and provider transmission paths where slave selection matters.

Risks: Missing a put leaks netdevice references. Using a slave after bond state changes or unregister requires correct reference and RCU handling in implementation. Hash policy changes can affect flow ordering and packet distribution.

Test signals: Validate get/put reference balance, slave selection under bond membership changes, behavior with no usable slaves, and `RDMA_LAG_FLAGS_HASH_ALL_SLAVES` policy coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/lag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/mr_pool.h -->
# sources/distributed-fs/ceph-client/include/rdma/mr_pool.h

Purpose: Declares a small memory-region pool API for queue-pair scoped reusable MRs, used by kernel RDMA consumers to avoid repeated allocation costs.

Important APIs/types/functions: `ib_mr_pool_init` preallocates a list of MRs for a QP with a requested MR type and data/metadata SGE limits. `ib_mr_pool_get` obtains an MR from the list. `ib_mr_pool_put` returns an MR to the list. `ib_mr_pool_destroy` tears down the pool.

Control flow: A user initializes a pool after QP creation, gets an MR when a transfer needs registration, maps/registers it through normal verbs paths, returns it when done, and destroys the pool before or during QP teardown. The list is caller-provided, making ownership explicit.

State and persistence behavior: Runtime state is stored in the caller's `list_head` and in each pooled `ib_mr` list entry. There is no durable persistence. Lifetime is tied to the QP and must end before the QP resources backing the MRs are invalid.

Dependencies and integration points: It depends on `ib_verbs.h` for `struct ib_qp`, `struct ib_mr`, and `enum ib_mr_type`. It integrates with fast registration and integrity MR workflows.

Risks: Pool users must serialize list access or use it from a context with known concurrency. Returning an MR still visible to hardware or failing to invalidate/remap keys can expose stale access. Destroying while outstanding MRs are checked out can leak or use after free.

Test signals: Cover init failure unwind, get/put balance, destroy with empty pool, behavior under exhausted pools, integrity MR parameters, and QP teardown ordering with outstanding transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/mr_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/opa_addr.h -->
# sources/distributed-fs/ceph-client/include/rdma/opa_addr.h

Purpose: Provides Omni-Path Architecture address helpers for encoding extended LID information in special GIDs and validating OPA/IB unicast LIDs.

Important APIs/types/functions: `OPA_SPECIAL_OUI`, `OPA_MAKE_ID`, `OPA_TO_IB_UCAST_LID`, `OPA_GID_INDEX`, multicast/collective top-bit constants, `ib_is_opa_gid`, `opa_get_lid_from_gid`, `opa_is_extended_lid`, `opa_get_mcast_base`, and `rdma_is_valid_unicast_lid`. The helpers distinguish 16-bit IB LID space from OPA's wider LID space.

Control flow: `ib_is_opa_gid` checks the upper 24 bits of a GID interface ID for the OPA OUI. `opa_get_lid_from_gid` extracts the lower 32 bits as a LID. `opa_is_extended_lid` flags source or destination LIDs beyond the IB multicast base. `rdma_is_valid_unicast_lid` validates address-handle DLIDs differently for IB and OPA.

State and persistence behavior: No state is stored. These are pure conversions and validators over caller-provided GIDs, LIDs, and address attributes.

Dependencies and integration points: It depends on `opa_smi.h`, `ib_verbs.h` address-handle accessors, endian helpers, and IB multicast LID constants. It integrates with OPA AH creation, path validation, and MAD/SMI code.

Risks: Mixing host and big-endian LID values can cause false validation results. `OPA_TO_IB_UCAST_LID` truncates/invalidates extended values for IB consumers. Multicast base calculations depend on the top-bit constants matching fabric width assumptions.

Test signals: Validate OPA GID detection, LID extraction, extended-LID detection, multicast boundary behavior, and `rdma_is_valid_unicast_lid` for IB, OPA, zero LID, unicast boundary, and multicast/collective ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/opa_addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/opa_port_info.h -->
# sources/distributed-fs/ceph-client/include/rdma/opa_port_info.h

Purpose: Defines OPA PortInfo constants, masks, enums, and packed wire layout used by OPA subnet management code to read and configure port state, link mode, link speed/width, error action, capabilities, and neighbor information.

Important APIs/types/functions: Constants cover OPA link modes, packet formats, LTP CRC modes, link-down reasons, link-init reasons, speeds, widths, and capability mask bits. `enum port_info_field_masks` defines bit masks for packed fields across `struct opa_port_info`. `struct opa_port_states`, `struct opa_port_state_info`, and packed `struct opa_port_info` model the OPA PortInfo payload, including LID, flow control, VL config, port states, P_Key/Q_Key violation counters, link speed/width, packet format, flit/preemption control, error actions, pass-through, mkey lease, buffer units, SM LID, subnet prefix, neighbor MTU, per-VL transmit queue parameters, IP addresses, neighbor GUID, capability masks, diagnostics, replay depth, neighbor mode, MTU cap, response time, and local port.

Control flow: The header is declarative. Consumers receive an OPA SMP PortInfo payload, cast or copy it into `struct opa_port_info`, then use masks and endian conversions to extract or update fields.

State and persistence behavior: The struct mirrors management-plane state of an OPA port as transmitted in MAD/SMP payloads. Kernel code treats it as transient serialized fabric state, while the actual durable state lives in hardware/fabric manager configuration.

Dependencies and integration points: It depends on `opa_smi.h` for OPA sizes and management context. It integrates with OPA subnet management agents, port query/modify paths, and conversion to generic `ib_port_attr`/capability reporting.

Risks: The packed structure must match hardware wire layout; compiler padding is suppressed but endian conversion remains caller responsibility. Mask names document removed/reserved fields, so consumers must not revive obsolete bits. Some values are policy-sensitive, such as link-down reasons, partition enforcement, pass-through, and error actions.

Test signals: Validate struct size/layout against OPA spec, mask extraction for every packed byte/word, endian conversions, PortInfo query/modify round trips, link-state reason decoding, and handling of reserved/unsupported packet format or speed bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/opa_port_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/opa_smi.h -->
# sources/distributed-fs/ceph-client/include/rdma/opa_smi.h

Purpose: Defines OPA Subnet Management Packet structures, attribute IDs, node descriptors/info, and helper functions for accessing LID-routed versus directed-route SMP payloads.

Important APIs/types/functions: Constants define LID and directed-route SMP data sizes, max path hops, max VL/SL/SC counts, and permissive LID. `struct opa_smp` is a packed OPA SMP header with route union for LID data or directed route fields (`dr_slid`, `dr_dlid`, initial/return paths, data). Attribute IDs include node description/info, port info, partition table, SL/SC/VL maps, SM info, cable info, aggregate, port state info, and buffer control table. `struct opa_node_description` and `struct opa_node_info` model basic node payloads. Helpers include `opa_get_smp_direction`, `opa_get_smp_data`, `opa_get_smp_data_size`, and `opa_get_smp_header_size`.

Control flow: Helper functions branch on `smp->mgmt_class == IB_MGMT_CLASS_SUBN_DIRECTED_ROUTE`. Directed-route packets use the `route.dr` path/data layout and smaller data size; LID-routed packets use `route.lid.data`. Direction delegates to the IB SMP helper by casting to `struct ib_smp`.

State and persistence behavior: The file defines transient management packet state. SMP data may represent hardware/fabric configuration, but the header itself only models messages in memory or on wire.

Dependencies and integration points: It depends on RDMA MAD and IB SMI headers. It integrates with OPA PortInfo, OPA address helpers, subnet manager/agent logic, and MAD processing paths in providers.

Risks: `struct opa_smp` is cast-compatible enough for `ib_get_smp_direction`; changes to common header layout could break that assumption. Payload size and header-size helpers must be used to avoid overrunning directed-route payloads. Attribute IDs are big-endian constants, so comparisons must respect endian format.

Test signals: Validate directed-route and LID-routed data pointer/size/header-size outputs, packed struct sizes, path hop limits, attribute ID comparisons, and compatibility of direction extraction with IB SMP helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/opa_smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_cm.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdma_cm.h

Purpose: Declares the RDMA Connection Manager kernel API for resolving addresses/routes, creating QPs, connecting/listening/accepting/rejecting, disconnecting, and multicast membership over IB, RoCE, and iWARP transports.

Important APIs/types/functions: `enum rdma_cm_event_type` models asynchronous CM progress and failure states from address resolved through disconnect, device removal, multicast, address change, and internal/user events. `struct rdma_addr`, `struct rdma_route`, `struct rdma_conn_param`, `struct rdma_ud_param`, `struct rdma_cm_event`, and `struct rdma_cm_id` carry address, route, connection, UD, event, and ID state. APIs include `rdma_create_id`, `rdma_destroy_id`, `rdma_restrict_node_type`, `rdma_bind_addr`, `rdma_resolve_addr`, `rdma_resolve_route`, `rdma_resolve_ib_service`, `rdma_create_qp`, `rdma_destroy_qp`, `rdma_init_qp_attr`, `rdma_connect`, `rdma_connect_ece`, `rdma_listen`, `rdma_accept`, `rdma_accept_ece`, `rdma_notify`, `rdma_reject`, `rdma_disconnect`, multicast join/leave, option setters, service ID and reject helpers, `rdma_read_gids`, and `rdma_iw_cm_id`.

Control flow: Active clients create an ID, optionally restrict node type, resolve address, optionally resolve IB service, resolve route or set an IB path, create/associate a QP, then connect. Passive listeners bind, listen, receive connect request events, create/associate QPs as needed, and accept or reject. Event callbacks serialize on the ID mutex and may sleep, but cannot directly destroy the passed ID; nonzero callback return destroys it.

State and persistence behavior: `rdma_cm_id` holds runtime association to device, context, QP, route records, port space, QP type, port, and net work. Destroying the ID cancels in-flight async operations. Device removal events require users to destroy IDs and release device resources.

Dependencies and integration points: It depends on Linux sockets, IPv6, RDMA address resolution, IB SA, uapi CM definitions, verbs QPs, and iWARP CM. It integrates directly with ULPs such as storage/network protocols that use RDMA CM for setup.

Risks: Event lifetime and callback restrictions are critical. Users must destroy QPs before IDs, handle device removal, and not assume route/address resolution is synchronous. Private-data lengths are small fixed fields. `rdma_read_gids` is compatibility-only and new code should use path records.

Test signals: Cover active/passive connection flows, route resolution failure, ECE negotiation, user callback destruction behavior, QP auto-transition, multicast join/leave, reject data extraction, device removal cleanup, and option ordering for reuseaddr/afonly/TOS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_cm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_cm_ib.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdma_cm_ib.h

Purpose: Provides InfiniBand-specific extensions to RDMA CM, primarily manual path-record injection for clients that bypass normal route resolution.

Important APIs/types/functions: `rdma_set_ib_path` binds a `struct sa_path_rec` to an `rdma_cm_id` on the client side and replaces `rdma_resolve_route`. `RDMA_UDP_QKEY` defines the global Q_Key used for UDP QPs and multicast groups.

Control flow: After address resolution, a client may call `rdma_set_ib_path` with a path record instead of asking CM to resolve the route. Subsequent connection setup uses the supplied path to initialize QP attributes and CM messages.

State and persistence behavior: The path record becomes runtime route state inside `rdma_cm_id->route`. The qkey constant is protocol configuration, not mutable state.

Dependencies and integration points: It includes `rdma_cm.h` and uses IB SA path records. It integrates with IB-specific ULPs and test setups that already have path information.

Risks: A stale or mismatched path record can produce unreachable connections or wrong MTU/P_Key/GID/SL behavior. Call ordering matters; this is client-side and substitutes for route resolution, not address binding.

Test signals: Validate manual-path connection setup, invalid path rejection, path MTU/P_Key propagation into `rdma_init_qp_attr`, and multicast/UDP QP use of `RDMA_UDP_QKEY`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_cm_ib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_counter.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdma_counter.h

Purpose: Declares RDMA counter management structures and APIs for binding QPs to hardware counters, configuring automatic counter modes, querying stats, and exposing counter state through RDMA netlink/restrack.

Important APIs/types/functions: `struct auto_mode_param` currently captures QP type. `struct rdma_counter_mode` combines netlink mode, mask, auto parameters, and bind-operation counter flag. `struct rdma_port_counter` stores per-port mode, hardware stats, counter count, and lock. `struct rdma_counter` stores restrack entry, device, counter ID, kref, mode, lock, stats, and port. APIs include `rdma_counter_init`, `rdma_counter_release`, `rdma_counter_set_auto_mode`, auto bind/unbind, query stats, get hardware stat value, bind/unbind by QPN, allocate-and-bind, get mode, and modify counter enablement.

Control flow: Device registration initializes per-port counter state. Admin/netlink operations set auto mode or bind specific QPNs. QP creation or transition can call auto-bind based on port mode; teardown unbinds. Query paths update the associated `rdma_hw_stats` through provider callbacks and expose values.

State and persistence behavior: Counter state is in-memory per device, per port, and per counter. `kref` protects counter object lifetime, locks serialize mode/stat changes, and restrack records make counters discoverable. There is no durable persistence across driver reload.

Dependencies and integration points: It depends on mutexes, PID namespace types, RDMA restrack, RDMA netlink enums, `ib_device`, `ib_qp`, and provider counter callbacks in `ib_device_ops`.

Risks: QP-to-counter binding must remain consistent across QP destroy, counter dealloc, and automatic mode changes. Incorrect kref or lock ordering can race stats queries with unbind/release. Hardware may not support all modes or masks.

Test signals: Cover device init/release, auto mode set/get, auto bind by QP type, explicit QPN bind/unbind, allocated counter ID return, concurrent stats query/unbind, counter modify enable/disable, unsupported provider callbacks, and restrack/netlink dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_counter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_netlink.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdma_netlink.h

Purpose: Declares kernel RDMA netlink registration, message construction, unicast/multicast delivery, event notification, and RDMA link operation registration.

Important APIs/types/functions: `struct rdma_nl_cbs` holds `doit` and `dump` callbacks plus flags. `enum rdma_nl_flags` includes `RDMA_NL_ADMIN_PERM`. `MODULE_ALIAS_RDMA_NETLINK` validates subsystem indexes against uapi constants and emits module aliases. APIs include `rdma_nl_register`, `rdma_nl_unregister`, `ibnl_put_msg`, `ibnl_put_attr`, `rdma_nl_unicast`, `rdma_nl_unicast_wait`, `rdma_nl_multicast`, `rdma_nl_chk_listeners`, and `rdma_nl_notify_event`. `struct rdma_link_ops` and register/unregister functions support dynamic RDMA link creation/deletion by type.

Control flow: RDMA subsystems register callback tables by netlink index. Request handling dispatches to `doit` or `dump`. Producers allocate messages in skbs, append attributes, then send to a PID or multicast group. Device events call `rdma_nl_notify_event`. Link providers register `newlink`/`dellink` handlers and module aliases.

State and persistence behavior: Netlink callback and link-op registrations are runtime kernel registry state. Messages are transient skbs. The API does not persist configuration; userspace can reconstruct state by dumps.

Dependencies and integration points: It depends on Linux netlink, RDMA uapi netlink definitions, and `ib_verbs.h`. It integrates with `rdma` userspace tooling, resource tracking, counter control, device notifications, and soft/link drivers.

Risks: Callback flags must enforce admin permissions for mutating operations. Netlink attribute lengths and types must match uapi. Module alias index checks prevent some registration mismatch, but wrong client/op values can still break userspace. Multicast notification should handle absent listeners.

Test signals: Cover callback registration/unregistration, admin-permission enforcement, dump and doit dispatch, malformed attributes, unicast wait retry behavior, multicast with/without listeners, event notification payloads, and link new/delete module autoload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_vt.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdma_vt.h

Purpose: Declares the rdmavt software verbs transport abstraction used by low-level drivers such as hfi1/qib to share RDMA verbs object management while providing hardware-specific packet scheduling, QP behavior, port state, and memory-key validation.

Important APIs/types/functions: `struct rvt_ibport` stores per-port special QPs, MAD agent, multicast tree, locks, M_Key/trap timers, GID prefix, counters, per-CPU hot counters, P_Key table, SM AH, and trap lists. `struct rvt_driver_params` carries device properties and driver tuning such as lkey/QP table sizes, SGE copy mode, QPN ranges, port count, P_Key count, PSN masks, capabilities, MAD size, and RDMA atomic limits. `struct rvt_ucontext`, `rvt_pd`, `rvt_ah`, `rvt_mmap_info`, and `rvt_wss` wrap core objects. `struct rvt_driver_provided` is the low-level callback table for send scheduling, WQE setup, QP private data, reset/error/flush/quiesce notifications, MTU/GUID/port queries, AH validation, QPN allocation, MAD-agent notices, mmap/ucontext hooks, and optional cleanup. `struct rvt_dev_info` embeds `ib_device` first and stores params, opcode tables, lkey table, allocation counters, ports, QP/CQ/mcast/mmap state, and WSS state.

Control flow: A driver allocates `rvt_dev_info`, fills `dparms` and `driver_f`, initializes ports with P_Key tables, registers with rdmavt, and rdmavt exposes standard verbs through the embedded `ib_device`. Send paths call driver scheduling/setup callbacks; QP transitions call driver validation/notification hooks; port/MAD/mcast operations coordinate through `rvt_ibport`.

State and persistence behavior: All state is runtime kernel memory. Locks protect allocation counters, port state, mmap offsets, pending mappings, multicast groups, and QP counts. Timers manage M_Key lease/trap resend behavior. Driver params should not be modified after registration because they are reported to ULPs.

Dependencies and integration points: It depends on Linux locks/lists/hash, `ib_verbs.h`, `ib_mad.h`, and `rdmavt_mr.h`. It integrates with rdmavt QP, CQ, MR, multicast, MAD, and provider registration code.

Risks: Callback completeness depends on which verbs rdmavt provides versus the driver overrides. Incorrect lock use around port/QP/mmap state can corrupt shared data. P_Key table ownership remains with the driver but is consumed by rdmavt. Timers and trap lists need teardown discipline.

Test signals: Cover device register/unregister, port init with P_Key table, AH validation, QP create/modify/reset/error paths, send scheduling callbacks, MR key validation, multicast lookup, trap timer behavior, mmap offset validation, and driver callback NULL handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdma_vt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdmavt_cq.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdmavt_cq.h

Purpose: Defines rdmavt completion queue data structures and memory-ordering helpers for kernel and mmaped userspace CQ rings.

Important APIs/types/functions: `RVT_CQ_NONE` is a sentinel notify value outside normal `ib_cq_notify` values. `RDMA_READ_UAPI_ATOMIC` and `RDMA_WRITE_UAPI_ATOMIC` apply acquire/release barriers to indices shared with userspace. `struct rvt_k_cq_wc` stores head, tail, and a flexible array of kernel `ib_wc` entries. `struct rvt_cq` embeds `ib_cq`, completion work, a spinlock, notify/triggered/full state, completion-vector CPU, rdmavt device pointer, userspace queue pointer, mmap info pointer, and kernel queue pointer. `ibcq_to_rvtcq` casts from core CQ to rdmavt CQ. `rvt_cq_enter` inserts a completion and handles notification.

Control flow: Providers or rdmavt QP processing call `rvt_cq_enter` with a work completion. The CQ lock protects queue state, head/tail movement, notification arming, and full/triggered flags. Completion work can be scheduled on the chosen CPU/vector.

State and persistence behavior: CQ state is runtime ring-buffer state. Head/tail are shared with userspace for mmaped CQs and require explicit acquire/release ordering. `rvt_mmap_info` tracks the mapping lifetime.

Dependencies and integration points: It depends on kernel threads/workqueues, uverbs CQ ABI, core verbs, and `rvt-abi.h`. It integrates with rdmavt QP completion generation and user/kernel CQ polling paths.

Risks: Ring index memory ordering is critical; missing barriers can make userspace see stale or torn completions. Full-queue handling must avoid overwriting unpolled CQEs. Notification arming races are common CQ bugs.

Test signals: Cover CQE insertion, solicited notification, notify sentinel behavior, full queue handling, mmaped userspace poll with memory barriers, completion-vector CPU selection, and concurrent producer/consumer stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdmavt_cq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdmavt_mr.h -->
# sources/distributed-fs/ceph-client/include/rdma/rdmavt_mr.h

Purpose: Defines rdmavt memory region, L_Key/R_Key table, segment, and SGE progress structures plus inline helpers for reference management and SGE advancement.

Important APIs/types/functions: `struct rvt_seg` represents a linear low-memory segment; `RVT_SEGSZ` and `struct rvt_segarray` group segments by page. `struct rvt_mregion` stores PD, user base, IOVA, length, lkey, offset, access flags, segment counts, invalid/published flags, page shift, percpu refcount, completion, and segment map. `struct rvt_lkey_table` stores max/shift/table and write-side lock/next/generation. `struct rvt_sge` and `struct rvt_sge_state` track copy progress across SGEs and MR segments. Helpers include `rvt_put_mr`, `rvt_get_mr`, `rvt_put_ss`, `rvt_get_sge_length`, `rvt_update_sge`, `rvt_skip_sge`, `rvt_ss_has_lkey`, and `rvt_mr_has_lkey`.

Control flow: RDMA receive/send copy code validates an lkey/rkey, seeds an SGE state, copies or skips bounded chunks computed by `rvt_get_sge_length`, then advances with `rvt_update_sge`. When an SGE is consumed, optional release drops the MR ref and loads the next SGE. Segment boundaries advance through `map[m]->segs[n]`.

State and persistence behavior: MR state is runtime memory-registration state. Per-CPU refs allow fast access while `comp` signals final ref teardown. `lkey_invalid` and `lkey_published` track key validity and table exposure. SGE state is per-operation progress.

Dependencies and integration points: It depends on Linux percpu refcounts and RDMA core PD/MR concepts. It integrates with `rdma_vt.h`, rdmavt QP data movement, fast registration, invalidation, and key lookup.

Risks: SGE advancement must not run past `mapsz` or consume zero-length chunks; the code warns on zero length but callers must avoid malformed states. MR refs must be acquired before use and released on every exit path. Lkey invalidation races can expose stale access if lookup/ref ordering is wrong.

Test signals: Cover lkey/rkey lookup, MR get/put and completion, SGE copy across segment-array boundaries, skip/update with release true/false, zero-length safeguards, invalidation during in-flight access, and max lkey table sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/rdma/rdmavt_mr.h -->
