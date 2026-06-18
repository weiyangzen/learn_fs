# subset-b-003954 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.c

## Purpose

`rxe_net.c` is the RoCEv2 network transport layer for the software RXE driver. It creates per-network-namespace UDP tunnel sockets on the standard RoCEv2 port, wraps RXE packet payloads in UDP/IP headers, routes them over the backing Ethernet netdev, detects local loopback, receives UDP-encapsulated packets, and connects netdev lifecycle events to RXE device registration and port state changes.

## Important APIs, Types, and Functions

- `rxe_prepare()` resolves the address vector to IPv4 or IPv6 routing state and prepends UDP/IP headers.
- `rxe_xmit_packet()` is the common transmit entry point for requester and responder packets; it validates QP state, generates ICRC, then sends or loops back the skb.
- `rxe_init_packet()` allocates and initializes an skb sized for RXE payload plus L2/L3/L4 headers using the GID attribute's netdev.
- `rxe_udp_encap_recv()` is the UDP tunnel receive callback that extracts RXE metadata from a UDP skb and calls `rxe_rcv()`.
- `rxe_net_init()`, `rxe_net_add()`, `rxe_net_del()`, `rxe_net_exit()`, and `rxe_register_notifier()` manage socket setup, RXE device add/remove, and netdevice notifications.
- IPv4/IPv6 route helpers, header builders, and socket setup/release helpers encapsulate kernel networking dependencies.

## Control Flow

Transmit starts in requester/responder code, which calls `rxe_init_packet()` for a packet body, fills BTH/extended headers, then calls `rxe_prepare()` and `rxe_xmit_packet()`. `rxe_prepare()` chooses IPv4 or IPv6 based on the address vector, resolves or refreshes a route, pushes UDP and IP headers, and marks loopback when the destination MAC equals the local device MAC. `rxe_xmit_packet()` checks QP readiness (`RTS` for requests, `RTR` for responses), emits the ICRC, and either calls `rxe_send()` into `ip_local_out()`/`ip6_local_out()` or `rxe_loopback()`, which strips the network headers back to the receive shape and invokes `rxe_rcv()`.

Receive flow is driven by UDP tunnel sockets created lazily per net namespace by `rxe_net_init()`. `rxe_udp_encap_recv()` locates the RXE device from the skb netdev or VLAN real device, linearizes the skb, records RXE packet metadata after the UDP header, pulls the UDP header, and hands the skb to RXE packet validation and dispatch.

## State and Persistence Behavior

Persistent state lives in per-netns IPv4/IPv6 UDP sockets stored through `rxe_ns_*`, per-QP send sockets and route cache (`qp->sk`, `qp->dst_cookie`), per-QP inflight skb reference counts, and RDMA device state attached to netdevs. RXE increments counters for send errors, sent packets, and link-down events. Socket references are carefully balanced: transmit skbs hold QP and socket references until destructor execution; tunnel sockets are reference-counted and released when the last RXE device in a namespace goes away.

## Dependencies and Integration Points

This file depends on Linux networking (`udp_tunnel`, routing, IPv4/IPv6 local output, VLAN, netdev notifier), RDMA address/GID APIs, RXE packet/header helpers, RXE namespace storage, and RDMA core device registration. It is used by requester/responder transmit paths, receive dispatch, module setup/teardown, and netdev event handling.

## Risks and Edge Cases

Route cache validity, netdev lifetime, VLAN device lookup, and socket reference accounting are high-risk areas. IPv6 support is conditional and must degrade cleanly when unavailable. Loopback manipulates skb headers to match tunnel receive shape, so header-length mistakes can corrupt receive parsing. `rxe_init_packet()` notes that the skb does not hold a netdev reference for its lifetime, which is a lifetime-sensitive assumption. Netdev unregister must not race with outstanding QPs or tunnel sockets. Lockdep socket reclassification intentionally adjusts module owner references and can affect unload behavior if changed.

## Test Signals

Useful tests include RXE add/delete over a netdev, IPv4 and IPv6 RC/UD traffic, VLAN-backed RXE devices, loopback sends, net namespace create/delete, netdev MTU change/down/unregister events, module unload after traffic, route invalidation, send error counter increments, and stress with many QPs to exercise inflight skb backpressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.h

## Purpose

`rxe_net.h` declares the public network-facing RXE entry points used by module/device setup and teardown. It is the boundary between RXE core code and the RoCEv2 UDP/IP transport implementation in `rxe_net.c`.

## Important APIs, Types, and Functions

- `rxe_net_add()` allocates/registers an RXE device for a backing `net_device`.
- `rxe_net_del()` releases per-netns tunnel socket references associated with an RXE device.
- `rxe_register_notifier()` registers the netdevice notifier.
- `rxe_net_init()` creates per-netns UDP tunnel sockets needed by a backing netdev.
- `rxe_net_exit()` unregisters notifier state at module teardown.

## Control Flow

Higher-level RXE setup code includes this header to initialize UDP tunnel resources before device registration, add a new RXE instance for a netdev, subscribe to netdev notifications, and unwind resources during remove or module exit. The header itself contains no logic.

## State and Persistence Behavior

No state is owned here. The declarations expose operations that manipulate RXE device objects, per-netns UDP sockets, and netdev notifier registration in `rxe_net.c`.

## Dependencies and Integration Points

The header includes kernel socket, IPv6 interface, and module declarations because the exported functions use `struct net_device`, `struct ib_device`, and socket-backed networking types. It is included by RXE module/device code that needs network lifecycle operations.

## Risks and Edge Cases

The API assumes callers honor ordering: namespace/tunnel setup must happen before traffic, notifier unregister must happen before module teardown finishes, and `rxe_net_del()` must be paired with device unregister. Missing forward declarations mean include order can matter if this header is reused outside the current RXE include graph.

## Test Signals

Build coverage for RXE module init/exit and device add/remove paths is the primary signal. Runtime smoke tests should confirm `rxe_net_init()`, `rxe_net_add()`, `rxe_net_del()`, and `rxe_net_exit()` are called in balanced order during `rdma link add/delete` and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.c

## Purpose

`rxe_ns.c` makes RXE network-namespace aware. It registers a pernet subsystem that stores one IPv4 and, when enabled, one IPv6 UDP tunnel socket pointer per namespace, and it releases those sockets when a namespace exits.

## Important APIs, Types, and Functions

- `struct rxe_ns_sock` stores RCU-protected `rxe_sk4` and `rxe_sk6` socket pointers.
- `rxe_namespace_init()` and `rxe_namespace_exit()` register/unregister `pernet_operations`.
- `rxe_ns_pernet_sk4()`/`rxe_ns_pernet_set_sk4()` get and set the IPv4 socket.
- `rxe_ns_pernet_sk6()`/`rxe_ns_pernet_set_sk6()` provide the IPv6 equivalents under `CONFIG_IPV6`.
- `rxe_ns_exit()` releases remaining UDP tunnel sockets during namespace teardown.

## Control Flow

Module initialization calls `rxe_namespace_init()`, which allocates pernet storage for every existing and future namespace. Socket creation is intentionally deferred to `rxe_net_init()` on first RXE device creation. RXE network setup stores created socket pointers via the setters. Namespace exit reads and clears each pointer under RCU and releases the underlying UDP tunnel socket.

## State and Persistence Behavior

The persistent state is the pernet `struct rxe_ns_sock` instance indexed by `rxe_pernet_id`. Socket pointers are updated with `rcu_assign_pointer()` followed by `synchronize_rcu()` in setters, so readers can dereference under RCU without taking a global lock.

## Dependencies and Integration Points

This file integrates Linux pernet storage, RCU, UDP tunnel sockets, and RXE network setup in `rxe_net.c`. It supplies sockets to IPv6 route lookup and UDP tunnel reference management and is required for namespace cleanup correctness.

## Risks and Edge Cases

Socket lifetime depends on consistent reference handling between `rxe_net.c` and namespace exit. A namespace may exit with sockets still present, so cleanup must clear pointers before releasing sockets. IPv6 code must compile away cleanly when `CONFIG_IPV6` is disabled. RCU readers receive raw socket pointers without taking a reference, so call sites must avoid using them beyond the protected lifetime expectations.

## Test Signals

Tests should create RXE devices inside separate network namespaces, exercise IPv4 and IPv6 traffic, delete namespaces with active or recently removed RXE devices, unload the module after namespace churn, and run with IPv6 disabled in the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.h

## Purpose

`rxe_ns.h` declares RXE per-network-namespace socket accessors and namespace registration hooks. It provides IPv6 stubs when IPv6 support is not built.

## Important APIs, Types, and Functions

- `rxe_ns_pernet_sk4()` and `rxe_ns_pernet_set_sk4()` access the pernet IPv4 UDP tunnel socket.
- `rxe_ns_pernet_sk6()` and `rxe_ns_pernet_set_sk6()` access the IPv6 socket or compile to no-op/null stubs.
- `rxe_namespace_init()` and `rxe_namespace_exit()` manage pernet registration.

## Control Flow

RXE module initialization registers namespace support through this API, and `rxe_net.c` uses the socket accessors when creating, looking up, and releasing tunnel sockets. The header contains no runtime logic beyond IPv6-disabled inline stubs.

## State and Persistence Behavior

No state is stored in the header. The API exposes RCU-managed pernet socket pointers implemented in `rxe_ns.c`.

## Dependencies and Integration Points

The declarations depend on kernel networking types such as `struct net` and `struct sock` through the surrounding RXE include graph. It is a narrow integration layer between RXE transport setup and Linux network namespace lifecycle.

## Risks and Edge Cases

IPv6 stubs silently return no socket and ignore setters, so callers must treat IPv6 setup as optional. If included without prior declarations of `struct net` or `struct sock`, compile errors could appear outside the current include order.

## Test Signals

Build with and without `CONFIG_IPV6`, run net namespace add/delete tests, and verify RXE device setup obtains socket pointers only after namespace registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_ns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_odp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_odp.c

## Purpose

`rxe_odp.c` implements on-demand paging support for RXE memory regions. It registers ODP user MRs, handles MMU invalidations, faults user pages into DMA/HMM mappings on demand, copies to/from ODP-backed memory, supports ODP atomics and atomic write, flushes persistent memory ranges, and implements `advise_mr` prefetch operations.

## Important APIs, Types, and Functions

- `rxe_odp_mr_init_user()` creates an ODP `ib_umem_odp`, initializes RXE MR state, and installs RXE MMU notifier ops.
- `rxe_ib_invalidate_range()` unmaps DMA pages for invalidated virtual ranges.
- `rxe_odp_mr_copy()`, `rxe_odp_atomic_op()`, `rxe_odp_do_atomic_write()`, and `rxe_odp_flush_pmem_iova()` are used by send/receive/RDMA responder paths.
- `rxe_ib_advise_mr()` handles supported prefetch advice synchronously or asynchronously.
- Helper functions map IOVA to ODP page indexes/offsets and fault or snapshot ranges under `umem_mutex`.

## Control Flow

User MR registration with `IB_ACCESS_ON_DEMAND` enters `rxe_odp_mr_init_user()`, obtains an ODP umem from RDMA core, snapshots initial pages, and marks the MR valid. Runtime access calls `rxe_odp_map_range_and_lock()`, which checks PFN validity under `umem_mutex`, faults pages if needed via `ib_umem_odp_map_dma_and_lock()`, and returns with the mutex held. Copy, atomic, and flush operations map pages with `kmap_local_page()`, perform memory operations, and then release the mutex. MMU invalidation unmaps affected pages while blocking invalidations are allowed. `advise_mr` either prefetches inline with `IB_UVERBS_ADVISE_MR_FLAG_FLUSH` or queues best-effort work on `rxe_wq`.

## State and Persistence Behavior

ODP MR state persists in `struct rxe_mr`, its `ib_umem_odp`, PFN list, notifier registration, access flags, IOVA, and MR validity. The PFN list is mutable and invalidated by MMU notifier callbacks. Async prefetch work temporarily holds MR references until work completion. Atomic operations share the global `atomic_ops_lock` for serialized access to mapped memory.

## Dependencies and Integration Points

The file depends on RDMA ODP core (`ib_umem_odp_*`), Linux HMM PFNs, MMU interval notifiers, persistent-memory cache flush helpers, RXE MR lookup/range validation, RXE workqueue, and responder state codes. It integrates with `rxe_verbs.c` user MR registration and `rxe_resp.c` data movement and atomic paths.

## Risks and Edge Cases

Implicit ODP is rejected even though the code recognizes the special full-range form. Pagefault handling is lock-sensitive because `ib_umem_odp_map_dma_and_lock()` returns with `umem_mutex` held on success. Atomic operations must validate alignment and range before mapping page memory. Async prefetch is best-effort, so failures are logged but not returned to the caller. Invalidations require blockable notifier ranges; non-blockable invalidations return false. Persistent flush must iterate correctly across MR page boundaries.

## Test Signals

Test registration and deregistration of ODP MRs, read/write traffic that faults pages lazily, remote atomics and atomic write on ODP memory, misaligned atomic rejection, MMU invalidation during active traffic, synchronous and asynchronous `advise_mr`, prefetch no-fault behavior, persistent flush operations, and builds with `CONFIG_INFINIBAND_ON_DEMAND_PAGING` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_odp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.c

## Purpose

`rxe_opcode.c` is RXE's table-driven opcode contract. It maps RDMA work request opcodes to supported QP-type capabilities and maps InfiniBand packet opcodes to RXE header masks, packet categories, header lengths, and per-header offsets.

## Important APIs, Types, and Functions

- `rxe_wr_opcode_info[]` tells posting code whether an `IB_WR_*` opcode supports inline data, send/write/read/atomic/local/flush/atomic-write behavior for each QP type.
- `rxe_opcode[RXE_NUM_OPCODE]` describes `IB_OPCODE_*` packet layouts for RC, UC, RD, and UD packet families.
- Mask bits drive requester packet construction, responder validation/execution, completion generation, ACK logic, and header accessors.

## Control Flow

This file has no functions. Runtime code indexes these arrays by work request or packet opcode. `rxe_verbs.c` validates posted send WRs with `wr_opcode_mask()`. `rxe_req.c` chooses packet opcodes and uses the packet table to size and populate headers. `rxe_recv.c` and `rxe_resp.c` use masks to validate packet sequencing, permissions, receive WQE consumption, RKEY checks, completion generation, and ACK behavior.

## State and Persistence Behavior

The state is static read-only table data compiled into the driver. It persists for the module lifetime and must remain consistent with `rxe_hdr.h` byte sizes and packet accessor expectations.

## Dependencies and Integration Points

The file depends on RDMA opcode constants, `rxe_opcode.h`, and `rxe_hdr.h` header byte-size definitions. It is central to requester, responder, completer, receive validation, and verbs posting behavior.

## Risks and Edge Cases

Table mistakes are high-impact because they can mis-size skbs, point accessors at wrong offsets, omit required validation, or mark unsupported operations as supported. The table includes RD opcodes even though RXE's QP support is mainly RC/UC/UD/GSI; accidental runtime enablement would need protocol support elsewhere. New operations such as flush and atomic write require coordinated updates across WR masks, packet masks, requester opcode selection, responder execution, and completion handling.

## Test Signals

Test every supported WR on each QP type, including unsupported-op rejection. Exercise RC/UC send/write segmentation, RC read responses, atomics, atomic write, flush, send-with-imm, send-with-invalidate, UD/GSI sends, and malformed packet/header-length cases. Compile-time or runtime assertions comparing offsets to header sizes would be valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.h

## Purpose

`rxe_opcode.h` defines the mask vocabulary and table types used to classify work requests and RXE packet opcodes. It is the shared schema for the opcode tables in `rxe_opcode.c`.

## Important APIs, Types, and Functions

- `enum rxe_wr_mask` classifies verbs work requests as inline-capable, send, write, read, atomic, local op, flush, or atomic write.
- `struct rxe_wr_opcode_info` stores a name and QP-type-specific work request masks.
- `enum rxe_hdr_type` and `enum rxe_hdr_mask` identify packet headers and behavioral categories.
- `struct rxe_opcode_info` stores packet name, masks, total header length, and offsets for each header type.
- `rxe_wr_opcode_info[]` and `rxe_opcode[]` are declared for global RXE use.

## Control Flow

There is no executable control flow. The definitions are consumed by validators, packet builders, packet parsers, and state machines that branch on mask bits rather than open-coding opcode lists.

## State and Persistence Behavior

No mutable state is owned here. The enums and structs define persistent ABI-like internal contracts for packet layout and operation semantics.

## Dependencies and Integration Points

The header integrates with RDMA core opcode constants, RXE header accessors, requester/responder/completer logic, and verbs posting checks. `OPCODE_NONE` and `RXE_NUM_OPCODE` are shared constants for QP state and table sizing.

## Risks and Edge Cases

Mask bits must remain unique and within the enum storage width. Composite masks such as `RXE_RDMA_OP_MASK` and `RXE_READ_OR_ATOMIC_MASK` directly affect access checks and responder resource handling. Adding a new header type requires coordinated changes to all table offsets and accessors.

## Test Signals

Build tests should cover all include users. Runtime tests should exercise each composite mask category and validate that packet accessors read the intended fields for every supported opcode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_opcode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_param.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_param.h

## Purpose

`rxe_param.h` defines RXE default device, port, resource, and protocol limit constants. These values seed RDMA core-visible attributes and constrain pool indexes, queue sizes, MR/MW ranges, atomic depths, packet pacing, and vendor/device identity.

## Important APIs, Types, and Functions

- `rxe_mtu_int_to_enum()` and `eth_mtu_int_to_enum()` convert byte MTUs to IB MTU enums after accounting for RXE header overhead.
- `enum rxe_device_param` defines device capabilities and maximums, including QP/CQ/PD/SRQ/MR/MW limits, supported access flags, atomics, flush, memory windows, inflight skb watermarks, and max task iterations.
- `enum rxe_port_param` and `enum rxe_port_info_param` define single-port default attributes.

## Control Flow

The header provides inline MTU conversion helpers and constants consumed by RXE initialization, capability reporting, QP/SRQ validation, pool setup, requester backpressure, and task scheduling loops.

## State and Persistence Behavior

No mutable state is stored. Constants become persistent device attributes at RXE device initialization and are exposed to users through RDMA query verbs.

## Dependencies and Integration Points

The header includes RXE UAPI definitions and RDMA core enums/flags through the wider include graph. It integrates with `rxe_verbs.c`, `rxe_qp.c`, `rxe_srq.c`, `rxe_pool.c`, network MTU handling, and requester workqueue behavior.

## Risks and Edge Cases

Several maxima use very large default values, so allocation paths must still guard actual memory use. Index ranges distinguish MR from MW by high bits of lkey/rkey, so changing them affects `rkey_is_mw()` and pool lookup. MTU conversion subtracts maximum RXE header length from Ethernet MTU; incorrect header constants can overstate path MTU and produce oversized packets.

## Test Signals

Test RDMA query-device/query-port output, MTU changes on backing netdevs, QP/SRQ/CQ creation near limits, MR/MW lkey/rkey classification, requester inflight skb backpressure, and task loop fairness under high traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.c

## Purpose

`rxe_pool.c` implements indexed, reference-counted object pools for RXE ucontexts, PDs, AHs, SRQs, QPs, CQs, MRs, and MWs. It provides object numbering, xarray lookup by index, kref lifetime management, cleanup callbacks, and final publication after object initialization.

## Important APIs, Types, and Functions

- `rxe_pool_init()` initializes a pool from `rxe_type_info`.
- `__rxe_add_to_pool()` assigns an index and initializes the embedded `rxe_pool_elem`.
- `rxe_pool_get_index()` looks up an object by index and takes a reference.
- `__rxe_get()`/`__rxe_put()` wrap kref access.
- `__rxe_cleanup()` removes an object from lookup, drops the create reference, waits for outstanding references, and calls type-specific cleanup.
- `__rxe_finalize()` stores the initialized element in the xarray so future lookups can find it.

## Control Flow

Object creation adds the embedded pool element to the pool and receives a cyclic index, then object-specific code initializes fields. Only after successful initialization does the caller call `rxe_finalize()`, which publishes the element in the xarray. Lookup runs under RCU and increments the kref unless it is already zero. Cleanup erases the xarray entry first to prevent new lookups, drops the pool's reference, waits for the completion signaled by the last put, then runs the registered cleanup callback.

## State and Persistence Behavior

Each pool persists in `struct rxe_dev`, holding the xarray, limits, next cyclic index, maximum element count, and atomic current element count. Each object persists an embedded pool element with pool pointer, object pointer, kref, completion, list node, and assigned index.

## Dependencies and Integration Points

The implementation depends on Linux xarray, kref, completions, RCU lookup, and RXE object cleanup functions. It underpins all verbs object lifetimes and is used heavily by MR/MW lookup, QP lookup, AH creation, and device cleanup.

## Risks and Edge Cases

The xarray entry is initially allocated with `NULL` and only later finalized; callers must not expose indexes before successful initialization. Non-sleepable AH cleanup spins with `mdelay()` and can timeout if references are held too long. Timeout cleanup still proceeds after warning, so dangling users would be severe. Pool index limits affect user-visible QP numbers and rkey/lkey classification.

## Test Signals

Run create/destroy stress for all object types, lookup-after-destroy races, AH create/destroy in atomic and sleepable contexts, MR/MW/QP index reuse, module unload with outstanding references, and fault injection during object initialization before finalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.h

## Purpose

`rxe_pool.h` defines RXE pool types, embedded object lifetime metadata, pool state, and convenience macros for reference, cleanup, and finalization operations.

## Important APIs, Types, and Functions

- `enum rxe_elem_type` enumerates all pooled RXE object classes.
- `struct rxe_pool_elem` is embedded in pooled objects and stores kref/index/completion metadata.
- `struct rxe_pool` stores pool limits, xarray, cleanup callback, and accounting.
- Macros `rxe_add_to_pool()`, `rxe_get()`, `rxe_put()`, `rxe_cleanup()`, `rxe_read()`, and `rxe_finalize()` wrap the low-level functions around embedded elements.

## Control Flow

Callers allocate an object, add it to the appropriate pool, initialize object-specific fields, finalize it for lookup, and later cleanup or reference-count it through these declarations. The header itself only defines the contract.

## State and Persistence Behavior

Pool metadata persists in the RXE device. Embedded elements persist for the lifetime of each RDMA object and coordinate lookup visibility and final release.

## Dependencies and Integration Points

The header depends on kernel kref, completion, xarray, and list primitives through the RXE include graph. It is included by `rxe_verbs.h` and therefore most RXE modules that manipulate RDMA objects.

## Risks and Edge Cases

Because the macros assume the target object has a field named `elem`, misuse on non-pooled objects is a compile-time or memory-layout hazard. Objects must not be finalized before initialization is complete, and cleanup must not run while code still expects index lookup to succeed.

## Test Signals

Compile coverage and object lifecycle stress tests are the main signals. Reference leak detection and lookup/cleanup races should be exercised with debug refcounting enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_pool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_qp.c

## Purpose

`rxe_qp.c` implements RXE queue pair validation, initialization, modification, reset/error transitions, responder resource allocation, SQ/RQ queue creation, timers, per-QP send socket setup, and final cleanup.

## Important APIs, Types, and Functions

- `rxe_qp_chk_init()` and `rxe_qp_chk_attr()` validate create and modify attributes.
- `rxe_qp_from_init()` creates runtime QP state from `ib_qp_init_attr`.
- `rxe_qp_from_attr()` applies `modify_qp` changes, including state transitions, PSNs, AVs, MTU, access flags, retry counters, and atomic depths.
- `rxe_qp_to_init()`/`rxe_qp_to_attr()` implement query support.
- `rxe_qp_error()`, `rxe_qp_cleanup()`, and `rxe_qp_chk_destroy()` handle error state, final teardown, and destroy eligibility.
- Internal helpers allocate send/receive queues, responder read/atomic resources, per-QP UDP send socket, tasks, and timers.

## Control Flow

QP creation validates type/capabilities, takes references on PD/CQs/SRQ, initializes common fields, creates a kernel UDP socket for sends, allocates the SQ and optional RQ shared queues, initializes send and receive tasks, sets RC timers if needed, and marks the QP valid in RESET. Modification first checks legal RDMA core state transitions, applies side effects for RESET/SQD/ERR, then updates requested attributes. Reset disables tasks, drains sender/receiver, resets queues and protocol state, frees responder resources, and reenables tasks. Cleanup marks the QP invalid, deletes timers, drains tasks and queues, releases queues/references/socket/resources, and runs in process context.

## State and Persistence Behavior

The QP persists PD/CQ/SRQ references, SQ/RQ queue buffers, request/completion/responder protocol state, per-QP socket, source UDP port, path AVs, PSNs, retry counters, timers, skb counters, and task state. RC responder resources are allocated according to `max_dest_rd_atomic` and replay read/atomic/flush responses.

## Dependencies and Integration Points

The file depends on RXE queues, tasks, requester/responder/completer functions, RDMA core QP state validation, socket APIs, timers, AV helpers, MR/MW invalidation paths, and pool cleanup. It is called from `rxe_verbs.c` create/modify/query/destroy operations.

## Risks and Edge Cases

QP state transitions are concurrency-sensitive and protected by `state_lock`; missed locking can race requester/responder tasks. Reset drains work while preventing task execution. RC timers exist only for RC QPs, so cleanup checks timer initialization before deletion. Shared receive queues skip per-QP RQ allocation and alter flush behavior. Resource allocation sizes are rounded to powers of two and must match requester/responder atomic-depth semantics.

## Test Signals

Test QP create/modify/query/destroy across RC, UC, UD, and GSI; invalid transition rejection; reset and error transitions under load; SQD drain events; RC retries/RNR timers; SRQ-backed QPs; MTU/path/access flag changes; max_rd_atomic/max_dest_rd_atomic changes; destroy while attached to multicast; and repeated create/destroy leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.c

## Purpose

`rxe_queue.c` allocates, mmap-prepares, resets, resizes, and destroys RXE circular queue buffers used for SQ, RQ, SRQ, and CQ storage shared between RXE and user or kernel clients.

## Important APIs, Types, and Functions

- `do_mmap_info()` creates mmap metadata and copies it to userspace when a user queue is created or resized.
- `rxe_queue_init()` allocates a power-of-two circular buffer with a management header.
- `rxe_queue_reset()` clears queue element memory while preserving the header.
- `rxe_queue_resize()` allocates a new queue, mmap metadata, locks producer/consumer sides, copies live entries, swaps queue headers, and cleans the old allocation.
- `rxe_queue_cleanup()` drops mmap references or frees the backing vmalloc buffer.

## Control Flow

Queue creation rounds element size up to at least a cache line and a power of two, rounds slot count to a power of two plus one empty slot, allocates `vmalloc_user()` memory, and returns the effective element count. Resize creates a replacement queue, optionally exposes new mmap info, locks queue ends, copies outstanding entries in order, updates indices, swaps queue metadata so existing queue pointers remain valid, and frees the old allocation through the temporary object.

## State and Persistence Behavior

Persistent state includes `struct rxe_queue`, its `rxe_queue_buf`, buffer size, element size/log2, index mask, queue type, private driver index, and optional mmap info object. User-visible queues persist until cleanup or resize, and mmap entries persist through `rxe_mmap_info` reference counting.

## Dependencies and Integration Points

The file depends on vmalloc user memory, RXE mmap helpers, queue inline operations from `rxe_queue.h`, and locks supplied by the owning SQ/RQ/SRQ/CQ. It is called by QP, SRQ, CQ, and verbs code.

## Risks and Edge Cases

Resize must reject shrinking below current occupancy and must preserve order while producer/consumer activity is locked. Element-size rounding changes returned capacities and offsets, so user ABI must consume the returned mmap metadata. `rxe_queue_reset()` clears data but not header indices, so callers must use it only where queue state is otherwise reset consistently.

## Test Signals

Test user and kernel queue creation, mmap metadata delivery, CQ/SRQ resize with active entries, shrink rejection, queue reset on QP reset, mmap release on destroy, and producer/consumer index correctness after wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.h

## Purpose

`rxe_queue.h` defines RXE's lock-free circular queue abstraction shared by driver, userspace clients, and kernel ULPs. It supplies queue types, queue state, and inline producer/consumer/index/address helpers.

## Important APIs, Types, and Functions

- `enum queue_type` distinguishes driver-to-client, client-to-driver, kernel-ULP-to-driver, and driver-to-ULP ownership models.
- `struct rxe_queue` stores queue buffer, mmap info, sizing, type, index mask, and private driver-owned index.
- Inline helpers read producer/consumer indices with acquire semantics where needed, test empty/full/count, advance owned indices with release semantics, and map indices to element addresses.
- Function declarations expose queue creation, resize, reset, mmap info, and cleanup.

## Control Flow

Queue users choose the correct `queue_type` for their perspective. Producer and consumer sides advance only the indices they own; attempts to advance the wrong side warn. Address helpers compute element pointers by masking indices and shifting by `log2_elem_size`.

## State and Persistence Behavior

The shared buffer contains producer and consumer indices plus queue data. For queues shared with userspace, RXE keeps private copies of driver-owned indices and publishes updates to the shared header with release ordering. Clients are not trusted, so reads mask shared indices before use.

## Dependencies and Integration Points

This header is included by QP, CQ, SRQ, requester, responder, and verbs code. It relies on RXE UAPI queue buffer layout and kernel memory-ordering primitives.

## Risks and Edge Cases

Using the wrong queue type can advance the wrong index or misinterpret ownership. The queue capacity is one less than slot count, so callers must use returned `max_wr`/`cqe` values. Lock-free semantics assume each side protects multi-CPU access to its owned end with external locks.

## Test Signals

Unit-style tests should cover wraparound, full/empty boundaries, count calculations, producer/consumer advancement for all queue types, user-supplied out-of-range indices, and concurrent post/poll under SQ/RQ/CQ locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_recv.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_recv.c

## Purpose

`rxe_recv.c` validates received RoCE packets, checks addressing and keys, demultiplexes unicast and multicast traffic, and queues accepted packets to responder QP tasks.

## Important APIs, Types, and Functions

- `rxe_rcv()` is the receive entry from UDP tunnel/loopback transport.
- `hdr_check()` validates BTH opcode, packet type, QP lookup, PKEY/QKEY, address, and checksum/header consistency.
- `rxe_rcv_pkt()` queues unicast packets to `rxe_resp_queue_pkt()`.
- `rxe_rcv_mcast_pkt()` clones multicast packets to attached QPs.
- Helpers update bad PKEY and QKEY violation counters and check DGID matching.

## Control Flow

Transport receive prepares `struct rxe_pkt_info` and calls `rxe_rcv()`. The receive path checks packet format and destination GID, validates QP type/state and keys, resolves the destination QP or multicast group, takes needed references, and either queues the skb to one QP or clones it for each multicast attachment. Queued packets wake the QP receive task, which runs `rxe_receiver()` in `rxe_resp.c`.

## State and Persistence Behavior

The file consumes QP, multicast group, and device references while packets are queued. It increments port counters for bad PKEY/QKEY conditions and global RXE counters for duplicate/out-of-sequence-like receive signals handled elsewhere. Packets persist on `qp->req_pkts` until responder cleanup dequeues them.

## Dependencies and Integration Points

It depends on RXE header parsing, packet opcode tables, QP pools, multicast support, netdev/GID information, and the responder queue entry point. It is downstream of `rxe_net.c` and upstream of `rxe_resp.c`.

## Risks and Edge Cases

Malformed or malicious packets can carry unsupported opcodes, invalid QPNs, bad PKEY/QKEY values, wrong destination GID, or incorrect multicast addressing. Multicast cloning must preserve device/QP references and free skb copies correctly. Packets queued to QPs hold references that responder cleanup must release.

## Test Signals

Exercise valid RC/UC/UD/GSI receive, bad opcode rejection, bad PKEY/QKEY counters, wrong DGID, multicast fanout and detach races, VLAN-backed receives, malformed packet length/header cases, and receive during QP reset/error/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_recv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_req.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_req.c

## Purpose

`rxe_req.c` implements the RXE requester state machine. It consumes send WQEs, chooses packet opcodes, builds RoCE packets, copies payload data, handles local operations, applies fencing and RD atomic limits, manages retry/RNR behavior, and drives the completer.

## Important APIs, Types, and Functions

- `rxe_requester()` processes one unit of send-queue work and returns whether more work remains.
- `rxe_sender()` runs both requester and completer for a QP send task.
- `rnr_nak_timer()` restarts requester retry after RNR wait.
- `req_retry()` rewinds WQE/requester state for retransmission.
- `next_opcode_rc()`, `next_opcode_uc()`, and `next_opcode()` map WR state and MTU fit to packet opcodes.
- `init_req_packet()`, `finish_packet()`, and state update helpers build and transmit packets.

## Control Flow

The send task calls `rxe_sender()`, which invokes `rxe_requester()` then `rxe_completer()`. The requester checks QP validity/state, performs retry rewind if needed, obtains the next WQE, enforces fences and outstanding PSN/RD atomic limits, executes local operations immediately, selects the next opcode, builds an skb and headers, copies inline or MR-backed payload, transmits through `rxe_xmit_packet()`, updates WQE state and PSNs, and arms retransmit timers for RC. Completion processing advances pending WQEs separately.

## State and Persistence Behavior

Requester state persists in `qp->req`: WQE index, current PSN/opcode, atomic credit counters, wait flags, retry flags, and ACK pacing. WQEs hold DMA cursors, first/last PSNs, state, status, and remote IOVA. RC timers and completer state coordinate retransmission and ACK handling.

## Dependencies and Integration Points

The requester depends on queue helpers, opcode tables, header initializers, MR copy/data movement helpers, AV lookup, network transmit, local MR/MW operations, QP state/timers, and the completer function. It is scheduled by `rxe_verbs.c` post-send and by timers/backpressure callbacks.

## Risks and Edge Cases

Retry reconstruction must exactly restore WQE DMA cursors and PSNs, especially after partial write/send or read responses. Fencing and RD atomic credit handling must avoid deadlocks and overcommit. UD oversized messages are completed successfully without sending per spec. Inline payload and MR copy errors map to different WC statuses. Inflight skb high/low watermarks must reschedule correctly.

## Test Signals

Test RC send/write/read/atomic/flush/atomic-write, UC send/write, UD/GSI sends, inline and non-inline data, segmentation across MTU, retransmit and RNR retry, local invalidate/register/bind operations, fence behavior, max unacked PSNs, skb backpressure, and QP error/reset while WQEs are processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_req.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_resp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_resp.c

## Purpose

`rxe_resp.c` implements the RXE responder state machine. It consumes received request packets, validates PSN/opcode/resource/length/rkey state, executes send/write/read/atomic/atomic-write/flush/invalidate operations, posts receive completions, sends ACK/NAK/read responses, replays duplicate requests, and handles responder errors.

## Important APIs, Types, and Functions

- `rxe_resp_queue_pkt()` appends received packets to a QP and schedules the receive task.
- `rxe_receiver()` is the top-level responder state machine.
- Check stages include `check_psn()`, `check_op_seq()`, `check_op_valid()`, `check_resource()`, `rxe_resp_check_length()`, and `check_rkey()`.
- Execution stages include `execute()`, `send_data_in()`, `write_data_in()`, `read_reply()`, `atomic_reply()`, `atomic_write_reply()`, and `process_flush()`.
- Completion/ACK/error stages include `do_complete()`, `acknowledge()`, `duplicate_request()`, `cleanup()`, `flush_recv_queue()`, and QP event helpers.

## Control Flow

`rxe_receiver()` first drains packets and receive WQEs if the QP is invalid, ERR, or RESET. Otherwise it loops through explicit responder states: get packet, validate sequencing and access, acquire RQ/SRQ WQE or responder resource, validate length and rkey/range, execute the operation, complete receive WQEs if needed, acknowledge RC traffic, cleanup packet/MR references, or transition to error states. RDMA reads and replayable operations store `resp_res` entries so duplicates can replay responses. Error states map protocol classes to ACK/NAK, work completion errors, async events, dropped messages, or QP error.

## State and Persistence Behavior

Responder state persists in `qp->resp`: expected PSN, MSN, ACK PSN, current opcode, drop flags, held receive WQE, current MR/rkey/VA/resid, SRQ WQE copy, responder resource ring, and current replay resource. Packet skbs persist in `qp->req_pkts` until cleanup drops QP/device references. RQ/SRQ consumer indices advance only after successful completion or SRQ acquisition.

## Dependencies and Integration Points

The responder depends on RXE packet/header accessors, queue helpers, MR/MW lookup and copying, ODP atomic/copy/flush helpers, CQ posting, requester network transmit for ACK/read responses, QP state management, SRQ events, and RDMA core WC/event semantics. It is downstream of `rxe_recv.c` and scheduled through `rxe_task.c`.

## Risks and Edge Cases

PSN comparison and duplicate replay are correctness-critical for RC reliability. RKEY handling must support zero-length operations, MR vs MW lookup, flush range vs whole-MR semantics, and invalidation. Atomic write must reject non-8-byte or padded payloads before reading payload memory. SRQ limit events and malformed user WQEs need careful locking. Error class mapping differs for RC, UC, UD, SRQ, and non-SRQ QPs. CQ overflow forces QP error.

## Test Signals

Exercise all responder operations, segmented sends/writes, zero-length read/write, duplicate read/atomic/flush replay, PSN NAK/RNR NAK, invalid rkey/access/range, immediate and invalidate completions, SRQ receive and limit events, CQ overflow, ODP-backed atomics, persistent flush, QP reset/error drains, and malformed packet/WQE cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_resp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_srq.c

## Purpose

`rxe_srq.c` implements shared receive queue validation, creation, resize/limit modification, and cleanup for RXE.

## Important APIs, Types, and Functions

- `rxe_srq_chk_init()` validates and normalizes SRQ create attributes.
- `rxe_srq_from_init()` initializes SRQ event fields, queue limits, queue buffer, mmap info, and user response.
- `rxe_srq_chk_attr()` validates resize and limit changes.
- `rxe_srq_from_attr()` applies resize and limit updates.
- `rxe_srq_cleanup()` releases the PD reference and queue.

## Control Flow

SRQ creation validates max WR/SGE against device limits, adds the SRQ to the pool in verbs code, takes the PD reference, creates a receive queue sized for `rxe_recv_wqe` plus SGEs, optionally exposes mmap information to userspace, writes the SRQ number, and returns adjusted capacity. Modification can resize the queue under producer/consumer locks and update the limit used by responder SRQ-limit events.

## State and Persistence Behavior

An SRQ persists its PD reference, receive queue, max WR/SGE, SRQ number, event handler/context, limit, and error flag. Queue contents persist receive WQEs posted by userspace or kernel callers and consumed by responders.

## Dependencies and Integration Points

The file depends on RXE queue allocation/resizing, mmap info, SRQ UAPI commands, device limits from `rxe_param.h`, pool cleanup, and responder SRQ consumption in `rxe_resp.c`.

## Risks and Edge Cases

Resize uses a legacy mmap-info address from input command data, noted as awkward in-code, so user ABI handling is fragile. Limit validation must not allow a limit above current queue capacity. SRQ error state blocks query/modify/consume. Queue resize under active responder consumption must hold both producer and consumer locks.

## Test Signals

Test SRQ create/query/destroy, post_srq_recv, responder consumption from multiple QPs, limit reached events, resize grow/shrink with queued WQEs, invalid max WR/SGE/limit rejection, and cleanup after QPs still reference or have consumed SRQ WQEs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.c

## Purpose

`rxe_task.c` provides RXE's lightweight workqueue task scheduler for QP requester/completer and responder processing. It coalesces schedules, bounds per-run iterations, supports drain/disable/enable transitions, and protects QP lifetime while work is pending or running.

## Important APIs, Types, and Functions

- `rxe_alloc_wq()` and `rxe_destroy_wq()` create/destroy the global unbound RXE workqueue.
- `rxe_init_task()` initializes a task around a QP and callback.
- `rxe_sched_task()` reserves idle tasks and queues work.
- `rxe_disable_task()`, `rxe_enable_task()`, and `rxe_cleanup_task()` control task execution during QP reset and cleanup.
- `do_task()` loops the callback until it returns nonzero or `RXE_MAX_ITERATIONS` is hit.

## Control Flow

Scheduling takes the task lock, moves IDLE to BUSY, takes a QP reference, and queues work. If scheduling happens while BUSY, the task becomes ARMED so the worker makes another pass before going idle. `do_task()` calls the task function repeatedly while it returns zero, yields/reschedules after the iteration cap, honors draining states, updates schedule/done counters, and releases the QP reference. Disable and cleanup move tasks to DRAINING/DRAINED/INVALID and wait with `cond_resched()` until pending work is done.

## State and Persistence Behavior

Global state is `rxe_wq`. Per task state includes work item, state enum, lock, QP pointer, callback, last return value, and schedule/done counters. A scheduled/running task persists an extra QP reference to close the gap between scheduling and completion.

## Dependencies and Integration Points

This file depends on Linux workqueues, spinlocks, QP pool references, and RXE parameter `RXE_MAX_ITERATIONS`. QP setup initializes send and receive tasks; requester/responder functions are callbacks; QP reset/cleanup disables and drains tasks.

## Risks and Edge Cases

Incorrect state transitions can lose a wakeup, run after cleanup, or leak a QP reference. The iteration cap must balance fairness and throughput. Draining waits in process context; calling cleanup from atomic context would be unsafe. Schedule/done counter mismatches are warned and indicate scheduler bugs.

## Test Signals

Stress post-send/receive scheduling, concurrent schedule while running, QP reset during traffic, cleanup with pending work, max-iteration rescheduling under heavy queues, and module unload after task churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.h

## Purpose

`rxe_task.h` defines the RXE task state machine and public task scheduler API used by QPs.

## Important APIs, Types, and Functions

- Task states are `IDLE`, `BUSY`, `ARMED`, `DRAINING`, `DRAINED`, and `INVALID`.
- `struct rxe_task` stores the work item, state, lock, QP, callback, return value, and counters.
- Declarations expose workqueue allocation/destruction, task initialization, scheduling, cleanup, disable, and enable.

## Control Flow

QP setup initializes `rxe_task` objects with requester/responder callbacks. Runtime code schedules tasks when queues receive work, and QP reset/cleanup disables, drains, or invalidates them. The header itself has no executable logic.

## State and Persistence Behavior

State is per task and persists with the QP. The state enum defines legal lifecycle phases that `rxe_task.c` enforces.

## Dependencies and Integration Points

The header depends on Linux workqueue and spinlock types through includes. It is included by `rxe_verbs.h` and QP implementation files.

## Risks and Edge Cases

Callbacks must follow the convention of returning zero while more work remains and nonzero when idle. Misusing task state outside the scheduler can cause lost work or use-after-free.

## Test Signals

Compile coverage and QP task lifecycle tests are the main signals, especially schedule while busy, disable/enable around reset, and cleanup under queued work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.c

## Purpose

`rxe_verbs.c` registers RXE as an RDMA core provider and implements device, port, ucontext, PD, AH, SRQ, QP, CQ, MR, send, receive, and registration verbs. It bridges generic RDMA core operations to RXE pools, queues, memory registration, and requester/responder scheduling.

## Important APIs, Types, and Functions

- Device/port query and modify functions report RXE capabilities, port state, GID/PKEY, immutable RoCE UDP encapsulation, and parent netdev.
- Object verbs allocate/deallocate ucontexts, PDs, AHs, SRQs, QPs, CQs, MRs, and MWs using RXE pools and helper modules.
- `rxe_post_send()` and `rxe_post_recv()` validate state and queue WQEs for user or kernel callers.
- CQ operations create, resize, poll, peek, request notification, and destroy CQs.
- MR operations create DMA/user/ODP/fast MRs, reregister supported fields, deregister, and map SG lists.
- `rxe_register_device()` installs `ib_device_ops`, associates the backing netdev, and calls `ib_register_device()`.

## Control Flow

RDMA core calls the provider methods in `rxe_dev_ops`. Creation methods validate user data and attributes, add objects to pools, initialize object-specific state, then finalize lookup visibility. Posting a kernel send validates each WR, writes WQEs into the SQ, advances producer indices, and schedules the send task; user QPs rely on mmap queues and simply schedule processing. Receive posting writes RQ WQEs and schedules receive flushing if the QP is in error. Registration wires all operations into `ib_device`, sets node attributes, and exposes limited legacy uverbs command masks.

## State and Persistence Behavior

The file creates and destroys persistent RDMA objects stored in `rxe_dev` pools and queue buffers. It updates user-visible capabilities, CQ notification state, WQE contents, MR access/state, parent sysfs attribute, QP source port for GRH flow-label hashing, and queue occupancy. User mmap entries for queues persist via queue/CQ/SRQ helpers.

## Dependencies and Integration Points

It depends on RDMA core ib_device_ops/uverbs, Linux netdev attributes, RXE queues, pools, QP/SRQ/CQ/MR/MW/mcast helpers, ODP support, hardware counters, and UAPI response structures. It is the main integration point between libibverbs/kernel ULPs and RXE protocol engines.

## Risks and Edge Cases

User data length checks must match ABI structures. Post-send validation must reject unsupported opcodes per QP type and enforce inline/SGE/atomic constraints. User QPs trust mmap queues only after requester/responder revalidates WQE fields. CQ destroy must reject associated work queues. MR deregistration must reject bound MWs. Finalizing objects before full initialization would expose partial state.

## Test Signals

Run RDMA core/libibverbs create/query/modify/destroy coverage for all objects, post-send/recv for kernel and user QPs, CQ poll/notify/resize, MR register/reregister/deregister including ODP, AH old/new user provider behavior, invalid udata fault injection, parent sysfs read, and full RXE traffic tests over RC/UC/UD/GSI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.h

## Purpose

`rxe_verbs.h` defines the core RXE RDMA object structures, QP protocol state, responder states, memory object state, access masks, device/port state, and conversion helpers between RDMA core objects and RXE-private containers.

## Important APIs, Types, and Functions

- Inline helpers `pkey_match()`, `psn_compare()`, `rkey_is_mw()`, `mr_page_size()`, `rxe_ib_device_get_netdev()`, and `rxe_counter_inc()`.
- Object containers: `rxe_ucontext`, `rxe_pd`, `rxe_ah`, `rxe_cq`, `rxe_srq`, `rxe_qp`, `rxe_mr`, `rxe_mw`, multicast records, `rxe_port`, and `rxe_dev`.
- QP sub-state structures: `rxe_req_info`, `rxe_comp_info`, `rxe_resp_info`, and `resp_res`.
- `enum resp_states` enumerates responder state-machine and error states.
- `to_r*()` helpers convert RDMA core pointers to RXE types.

## Control Flow

The header has no standalone execution. Its structures are allocated and manipulated by verbs, QP, requester, responder, completer, memory, multicast, and network modules. State-machine enums guide `rxe_resp.c`, while QP and MR structures are shared across most RXE code paths.

## State and Persistence Behavior

Most persistent RXE state is defined here: device pools and counters, port attributes, QP queues/timers/tasks/protocol state, CQ queues and notification state, SRQ queues and limits, MR/MW access and lifetime state, and multicast membership. These structures are embedded in RDMA core objects or RXE device state and persist until pool cleanup.

## Dependencies and Integration Points

The header integrates RDMA core object types with RXE pools, tasks, hardware counters, Linux workqueues/timers/skbs, and memory registration state. Because it is widely included, changes have broad compile and ABI effects inside RXE.

## Risks and Edge Cases

Structure layout and embedded-object assumptions are central to `container_of()` conversions and pool macros. PSN comparison relies on 24-bit wrap semantics via left shift into signed space. `resp_res` replay state must stay consistent with responder duplicate handling. Access masks control which remote operations the driver advertises and enforces.

## Test Signals

Compile all RXE modules after structure changes, run QP/MR/MW/SRQ/CQ lifecycle tests, PSN wraparound tests, responder replay tests, access-flag enforcement tests, multicast attach/detach tests, and refcount leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Kconfig

## Purpose

`Kconfig` declares the `RDMA_SIW` build option for the software iWARP driver, which implements RDMA over TCP/IP using standard Ethernet hardware.

## Important APIs, Types, and Functions

- `config RDMA_SIW` is a tristate option named "Software RDMA over TCP/IP (iWARP) driver".
- It depends on `INET`, `INFINIBAND`, and `INFINIBAND_VIRT_DMA`.
- It selects `CRC32` and `NET_CRC32C`.
- The help text documents kernel/user verbs support, libsiw userspace provider needs, and TCP socket integration.

## Control Flow

There is no runtime flow. Kconfig resolution controls whether Kbuild compiles the SIW module or built-in object. Dependency and select clauses ensure required networking, RDMA, virtual DMA, and checksum helpers are available.

## State and Persistence Behavior

The only state is persistent kernel `.config` selection. It determines whether SIW code is built and whether the resulting module can be loaded.

## Dependencies and Integration Points

The option gates the Makefile target in the same directory. It integrates the RDMA subsystem with INET/TCP and checksum libraries and is conceptually parallel to RXE as another software RDMA transport.

## Risks and Edge Cases

Dependency drift can cause build breakage if SIW begins using symbols not covered here. Help text references `libsiw`; userspace/provider mismatch can make a built driver unusable from libibverbs even when the kernel module loads.

## Test Signals

Build matrix tests with `RDMA_SIW=y`, `=m`, and disabled, plus dependency-disabled configurations for `INET`, `INFINIBAND`, and `INFINIBAND_VIRT_DMA`. Module load and basic iWARP connection smoke tests validate runtime enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Makefile

## Purpose

`Makefile` defines the Kbuild composition of the SIW software iWARP driver.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_RDMA_SIW) += siw.o` builds the composite object when the Kconfig symbol is enabled.
- `siw-y` lists `siw_cm.o`, `siw_cq.o`, `siw_main.o`, `siw_mem.o`, `siw_qp.o`, `siw_qp_tx.o`, `siw_qp_rx.o`, and `siw_verbs.o`.

## Control Flow

Kbuild evaluates `CONFIG_RDMA_SIW`; when enabled, it compiles the listed objects and links them into `siw.o`, which becomes built-in code or a module depending on tristate selection.

## State and Persistence Behavior

The file controls build artifacts only. The object list determines which SIW subsystems are present: connection management, CQ, main registration, memory, QP core, TX/RX protocol, and verbs provider logic.

## Dependencies and Integration Points

It integrates with `Kconfig` via `CONFIG_RDMA_SIW` and with the SIW source files in the same directory. Runtime dependencies are declared in Kconfig rather than the Makefile.

## Risks and Edge Cases

Adding or renaming a SIW source without updating `siw-y` will omit code or break builds. Since the composite target name is stable, external tooling may expect the module/object to be named `siw`.

## Test Signals

Run `make M=drivers/infiniband/sw/siw`, full built-in and module builds, and module load smoke tests after object list changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/iwarp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/iwarp.h

## Purpose

`iwarp.h` defines SIW's protocol-level iWARP wire-format structures, bit masks, inline field accessors, terminate error codes, and RDMAP opcodes for MPA/DDP/RDMAP framing over TCP.

## Important APIs, Types, and Functions

- MPA definitions include revisions, keys, private data length, request/reply flags, enhanced connection setup controls, markers, and trailer CRC layout.
- `struct iwarp_ctrl` and related tagged/untagged control structs define common DDP/RDMAP FPDU headers.
- Inline helpers extract/set DDP version, RDMAP version/opcode, MPA revision, and terminate layer/error fields.
- Packet structs define RDMA write, read request/response, send, send invalidate, and terminate formats.
- Enums define DDP/RDMAP/LLP error layers, error types/codes, untagged queue numbers, and RDMAP opcodes.

## Control Flow

The header has no runtime control flow. SIW connection management, TX, and RX code include it to format outgoing FPDUs, parse incoming frames, negotiate MPA versions/options, validate DDP/RDMAP versions and opcodes, and construct terminate messages.

## State and Persistence Behavior

No mutable state is stored here. The structures describe persistent protocol bytes carried on TCP streams and transient parser/formatter views over skb or buffer memory. Constants become part of SIW's wire compatibility contract.

## Dependencies and Integration Points

It depends on RDMA CM private-data size, Linux fixed-width/endian types, and architecture byte-order bitfield definitions. It integrates with SIW connection management for MPA negotiation and with QP TX/RX code for RDMAP/DDP packet processing.

## Risks and Edge Cases

Wire layout is endian-sensitive. `struct iwarp_terminate` uses bitfields whose order depends on `__LITTLE_ENDIAN_BITFIELD` or `__BIG_ENDIAN_BITFIELD`; layout regressions would break terminate parsing. Several MPA v2 control enum values intentionally overlap depending on request/reply context. CRC, marker, and padding lengths must match framing code exactly.

## Test Signals

Test MPA v1/v2 negotiation, private data length boundaries, CRC enabled/disabled, marker handling if supported, RDMA write/read/send/send-invalidate/terminate formatting and parsing, terminate error-code round trips on little- and big-endian builds, malformed version/opcode rejection, and interop with another SIW or hardware iWARP peer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/sw/siw/iwarp.h -->
