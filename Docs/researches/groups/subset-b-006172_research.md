# subset-b-006172 Research

Grouped code research for PF_CAN core, CAN BCM, CAN gateway, ISO-TP, and SAE J1939 socket/network-management files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/af_can.c -->
# sources/distributed-fs/ceph-client/net/can/af_can.c

## Purpose
This file implements the PF_CAN core protocol family. It registers the CAN socket family, dispatches incoming Classic CAN, CAN FD, and CAN XL sk_buffs to protocol subscribers, manages receive-filter lists per network namespace and per CAN device, exports the common CAN transmit helper, and provides protocol registration for CAN transport modules such as BCM, ISO-TP, and J1939.

## Important APIs, Types, And Functions
The external API surface is `can_send()`, `can_rx_register()`, `can_rx_unregister()`, `can_set_skb_uid()`, `can_proto_register()`, `can_proto_unregister()`, and `can_sock_destruct()`. Protocol modules use `can_proto_register()` with a `struct can_proto` containing socket type, protocol number, `proto_ops`, and `struct proto`, and use the receive registration helpers to subscribe callbacks to CAN identifiers and masks.

The core state includes the global RCU `proto_tab[CAN_NPROTO]`, `proto_tab_lock`, a `kmem_cache` for `struct receiver`, per-net `net->can.rx_alldev_list`, `net->can.pkg_stats`, `net->can.rcv_lists_stats`, and each CAN netdevice's `can_ml_priv.dev_rcv_lists`.

Receive-list selection is performed by `can_rcv_list_find()`. It normalizes filters into error, all, inverted, general masked, exact standard ID, or hashed extended ID lists. `effhash()` reduces 29-bit extended identifiers into `rx_eff[]` buckets.

## Control Flow
Socket creation enters through `can_create()`. It validates the protocol number, looks up a registered `can_proto` under RCU, optionally triggers `request_module("can-proto-%d")`, checks socket type, allocates the protocol socket with `sk_alloc()`, attaches `sock_init_data()`, installs `can_sock_destruct()`, and calls the protocol-specific `init()` hook.

Transmit callers provide a fully formed skb to `can_send()`. The helper validates the frame type with `can_is_can_skb()`, `can_is_canfd_skb()`, or `can_is_canxl_skb()`, assigns the Ethernet protocol, enforces device MTU, CAN ARP type, and `IFF_UP`, resets packet headers, optionally prepares local loopback or driver echo behavior, submits to `dev_queue_xmit()`, injects a software-loopback clone with `netif_rx()` when needed, and updates per-net TX statistics.

Receive registration allocates a `receiver`, canonicalizes the filter, and adds it to an RCU hlist under `net->can.rcvlists_lock`. Receive delivery comes from packet handlers `can_rcv()`, `canfd_rcv()`, and `canxl_rcv()`, which reject malformed skbs and then call `can_receive()`. `can_receive()` stamps a nonzero skb hash, runs `can_rcv_filter()` first on the namespace all-device list and then on the device list, consumes the driver skb, and updates RX/match counters.

Module init builds the `can_receiver` slab cache, registers per-net state, registers `PF_CAN`, and attaches packet handlers for `ETH_P_CAN`, `ETH_P_CANFD`, and `ETH_P_CANXL`. Exit removes packet handlers, unregisters PF_CAN, tears down per-net state, waits for RCU callbacks, and destroys the cache.

## State And Persistence
All state is kernel-resident and scoped to module lifetime, net namespace lifetime, or socket/protocol lifetime. Protocol registrations are global but RCU-protected. Receive subscriptions persist until the owning protocol or socket unregisters them. Per-net stats are reset on namespace init and optionally surfaced/updated through proc support. There is no disk persistence.

Receiver deletion is deferred with `call_rcu()`. If a receiver is associated with a socket, the unregister path takes a temporary socket reference before the RCU callback so callbacks cannot race a final free.

## Dependencies And Integration Points
This core depends on the Linux networking stack (`sock_register()`, `dev_add_pack()`, per-net operations, `dev_queue_xmit()`), CAN skb validation helpers from `linux/can/skb.h`, CAN multi-layer device private state from `linux/can/can-ml.h`, and optional proc helpers declared in `af_can.h`.

It is the central integration point for CAN protocol modules. BCM, ISO-TP, J1939, raw CAN, and gateway code all depend on its transmit helper, protocol registry, and receive filter dispatcher.

## Risks And Edge Cases
`can_rx_unregister()` warns rather than failing when no matching receiver is found. That is intentional for races with device removal, but it can hide protocol-layer reference bugs.

Filter canonicalization mutates the caller-provided `can_id` and `mask` locals before storage and before unregister matching. Callers must pass the same logical filter values to unregister, relying on the same normalization to find the same hlist.

`can_send()` consumes the skb on validation failures and on normal transmission. Callers must not reuse the skb after calling it, including on errors.

Receive callbacks run under an RCU read-side section and receive a borrowed skb that is consumed after dispatch. Protocol callbacks must clone if they retain data beyond the callback.

The receive hot path depends on valid CAN skb extensions; malformed or hand-crafted skbs are dropped with a one-time warning.

## Test Signals
Likely test signals are kernel CAN selftests and protocol-specific tests that exercise PF_CAN sockets, local loopback, CAN FD/XL validation, and net namespace teardown. Important coverage includes register/unregister races, software loopback when `IFF_ECHO` is absent, exact SFF/EFF filter fast paths, inverted/error filters, and module autoload through `can-proto-*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/af_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/af_can.h -->
# sources/distributed-fs/ceph-client/net/can/af_can.h

## Purpose
This private header defines the receive-dispatch and statistics structures shared by the PF_CAN core and CAN procfs/statistics code. It is not a user ABI header; it supports in-kernel organization around `af_can.c` and companion proc code.

## Important APIs, Types, And Functions
`struct receiver` represents one CAN receive subscription. It stores the normalized `can_id`/`mask`, callback function and callback data, optional identifier string, optional owning socket, match counter, hlist node, and RCU head for deferred freeing.

`struct can_pkg_stats` tracks per-net RX/TX frame counts, match counts, current/total/max rates and match ratios, plus delta counters used by periodic stat updates.

`struct can_rcv_lists_stats` tracks receive-list reset timestamps and current/max receiver entry counts.

The function declarations `can_init_proc()`, `can_remove_proc()`, and `can_stat_update()` connect the core to procfs/stat timer support.

## Control Flow
`af_can.c` allocates `struct receiver` objects from its slab cache, fills them during `can_rx_register()`, links them into chosen receive lists, and eventually frees them through an RCU callback. Proc/stat code initializes procfs files per net namespace, removes them during namespace teardown, and updates `can_pkg_stats` through the declared timer callback.

## State And Persistence
The header only declares memory layouts. Runtime instances are stored in per-net CAN state, per-device CAN receive lists, or transient receiver allocations. Counters persist until net namespace teardown or explicit stat reset by the proc/stat layer.

## Dependencies And Integration Points
The header depends on `sk_buff`, `net_device`, hlist/list support, RCU support, and CAN identifier definitions. It is included by the PF_CAN core and procfs implementation. The callback signature in `struct receiver` is the contract consumed by protocol modules registered through `can_rx_register()`.

## Risks And Edge Cases
Because `struct receiver` carries both callback data and an optional socket reference, unregister paths must coordinate RCU and socket lifetime correctly. Statistics use atomic counters for hot-path updates but aggregate fields are plain unsigned longs, so readers need to tolerate approximate snapshots.

The header is internal to this source tree. Changing field layout affects `af_can.c`, procfs output, and any in-tree code that inspects receiver/stat structures.

## Test Signals
Compile coverage is the main signal for this header. Runtime signals come from PF_CAN receive-filter tests, procfs CAN statistics tests, and namespace teardown tests that verify receiver and stat state is allocated and freed correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/af_can.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/bcm.c -->
# sources/distributed-fs/ceph-client/net/can/bcm.c

## Purpose
This file implements the PF_CAN Broadcast Manager protocol (`CAN_BCM`). It lets user space configure cyclic CAN/CAN FD transmissions, one-shot sends, receive filters, receive-change notifications, timeout notifications, multiplexed content comparisons, RTR replies, and optional procfs introspection.

## Important APIs, Types, And Functions
`struct bcm_sock` is the protocol socket state: bound ifindex, notifier list entry, RX/TX operation lists, procfs entry name, and dropped-user-message counter. `struct bcm_op` represents one BCM operation with CAN ID, flags, timers, frame arrays, last-frame arrays, counters, current TX frame index, owning socket, and registered RX device.

Core command handlers are `bcm_sendmsg()`, `bcm_tx_setup()`, `bcm_rx_setup()`, `bcm_tx_send()`, `bcm_delete_rx_op()`, `bcm_delete_tx_op()`, and `bcm_read_op()`. Delivery and timer functions include `bcm_can_tx()`, `bcm_tx_timeout_handler()`, `bcm_rx_handler()`, `bcm_rx_timeout_handler()`, `bcm_rx_thr_handler()`, and `bcm_send_to_user()`.

The socket operations table exposes `connect()` as the binding operation, `sendmsg()` for BCM opcodes, `recvmsg()` for notifications/status replies, `poll`, timestamp retrieval, and release.

## Control Flow
Socket initialization sets up RX/TX operation lists and adds the socket to a global notifier list. `bcm_connect()` binds the BCM socket to a CAN interface or ifindex zero ("any"), verifies CAN devices, creates a procfs entry when available, and marks the socket bound.

`bcm_sendmsg()` reads a `struct bcm_msg_head`, validates payload size against Classic CAN or CAN FD frame size, resolves an alternative sendto ifindex when the socket is bound to any, locks the socket, and dispatches by opcode. `TX_SETUP` creates or updates a TX op, copies frame payloads, configures count and timers, optionally announces immediately, and starts cyclic transmission. `RX_SETUP` creates or updates an RX op, allocates comparison and last-frame storage, configures timeout/throttle timers, and registers a CAN receive filter. `TX_SEND` sends exactly one frame without storing an op.

RX callbacks arrive through `can_rx_register()`. `bcm_rx_handler()` filters by frame type and CAN ID, cancels receive timeout, records timestamp and source ifindex, handles RTR auto-reply, computes local/own traffic flags, performs direct or multiplexed content comparison, reports `RX_CHANGED` immediately or through throttle handling, and restarts timeout monitoring.

Release removes the socket from the notifier list, tears down procfs entries, unregisters RX filters, waits for RCU readers, cancels timers, frees operations via RCU, orphans the socket, and drops protocol usage.

## State And Persistence
All BCM state is per socket and per net namespace. Operation configuration persists while the socket is open. Timers hold runtime scheduling state for cyclic TX, RX timeout, and throttled RX notifications. Procfs entries under `/proc/net/can-bcm` are live views only and disappear on socket release, net namespace exit, or device unregister.

TX and RX operation lists are protected primarily by socket locking. Individual cyclic TX fields that can change while timers run are protected by `bcm_tx_lock`. Operation memory is freed with `call_rcu()` because receive callbacks can observe operations after list removal.

## Dependencies And Integration Points
BCM depends on PF_CAN core protocol registration, `can_send()`, `can_rx_register()`, and `can_rx_unregister()`. It uses CAN UAPI types from `linux/can/bcm.h`, CAN skb extensions, high-resolution timers, netdevice notifiers, procfs/seq_file, and per-net operations.

Netdevice notifier integration removes receive registrations and reports `ENODEV` or `ENETDOWN` to affected sockets. Per-net init/exit owns the procfs directory.

## Risks And Edge Cases
The message format is compact and user-controlled; length checks must stay aligned with `CAN_FD_FRAME` and frame count flags. `MAX_NFRAMES` limits most operations to 256 frames, with RX multiplex setup allowing `MAX_NFRAMES + 1` because index zero is the mux mask.

Existing TX/RX operations cannot grow their frame arrays; updates with more frames than originally allocated return `-E2BIG`.

Receive callbacks run asynchronously with socket close and device unregister. Correctness depends on unregistering filters, `synchronize_rcu()`, and RCU-delayed operation free.

Timer callbacks can send frames and queue user notifications. Tests need to cover cancellation paths, especially release during active TX/RX timers and notifier callbacks.

`bcm_notify()` sets socket errors but does not necessarily remove all configured ops on `NETDEV_DOWN`; user space must handle errors and potentially reconfigure after link changes.

## Test Signals
Useful tests include `can-utils` BCM exercises, kernel CAN selftests, and fault-injection around invalid opcodes, invalid frame lengths, timer values beyond `BCM_TIMER_SEC_MAX`, CAN FD/classic mismatches, multiplex filters, RTR reply setup, `RX_CHECK_DLC`, throttle flush behavior, and netdevice unregister while operations are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/bcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/gw.c -->
# sources/distributed-fs/ceph-client/net/can/gw.c

## Purpose
This file implements the CAN gateway/router/bridge facility exposed through rtnetlink route messages for `PF_CAN`. It creates CAN-to-CAN forwarding jobs between interfaces, optionally modifies CAN/CAN FD frames, updates checksums, limits routing hops, records counters, and removes jobs on request, namespace exit, or device unregister.

## Important APIs, Types, And Functions
`struct cgw_job` is one gateway job. It stores source/destination devices, CAN filter, flags, hop limit, handled/dropped/deleted counters, and an RCU-protected `struct cf_mod`. `struct cf_mod` stores AND/OR/XOR/SET modification frames, precomputed function pointers, checksum definitions, checksum function pointers, and optional UID.

The hot-path callback is `can_can_gw_rcv()`. Netlink operations are `cgw_create_job()`, `cgw_remove_job()`, and `cgw_dump_jobs()`, registered as `RTM_NEWROUTE`, `RTM_DELROUTE`, and `RTM_GETROUTE` handlers for `PF_CAN`. Parsing and serialization are handled by `cgw_parse_attr()` and `cgw_put_job()`.

Modification helpers cover CAN ID, length/DLC, flags, Classic CAN data, CAN FD data, and DLC conversion through `mod_retrieve_ccdlc()`/`mod_store_ccdlc()`. Checksum helpers support XOR and CRC8 over absolute or length-relative data ranges.

## Control Flow
Module init clamps the `max_hops` parameter, registers per-net state, creates a job slab cache, registers a netdevice notifier, and registers rtnetlink handlers.

Creating a route requires `CAP_NET_ADMIN`, an `AF_CAN` route message, and currently `CGW_TYPE_CAN_CAN`. `cgw_parse_attr()` validates and normalizes attributes, precomputes modification/checksum function arrays, reads source/destination ifindices, and rejects incomplete interface combinations. `cgw_create_job()` supports UID-based in-place modification updates when UID, interfaces, and filters match. Otherwise it allocates a new job, resolves source/destination CAN devices under RTNL, rejects same-interface routing unless explicitly allowed, registers the source CAN filter, and adds the job to the per-net hlist under RCU.

When a matching CAN frame arrives, `can_can_gw_rcv()` verifies Classic CAN versus CAN FD mode, finds CAN skb extension state, enforces global/private hop limits, checks destination link up, rejects loop-back-to-incoming-interface unless allowed, clones or copies the skb depending on whether modifications are configured, copies the CAN skb extension to increment hop count, applies modification function pointers, validates the modified length against available frame storage, updates configured checksums, optionally clears timestamps, and sends through `can_send()`.

Removal parses the same attributes, removes all jobs when both ifindices are zero, or finds the first job matching flags, hop limit, UID or full modification content, and CAN gateway tuple. Device unregister removes any job using that source or destination device.

## State And Persistence
Jobs live in `net->can.cgw_list` for the network namespace and persist until deletion, namespace exit, module exit, or device unregister. The counters are in memory and exported through route dumps. `cf_mod` is replaced under RTNL with RCU assignment for UID updates; old modification data is freed after an RCU grace period.

There is no persistence outside kernel memory. The module-level `max_hops` parameter is read-only after load and bounds routing-loop protection.

## Dependencies And Integration Points
The gateway integrates with PF_CAN receive filters and `can_send()`, rtnetlink message dispatch, net namespace lifecycle, netdevice notifiers, CAN skb extensions, and CAN gateway UAPI attributes from `linux/can/gw.h`.

It assumes RTNL protection for route creation/removal and RCU read protection for hot-path job traversal and modification access.

## Risks And Edge Cases
The receive path is a hot path with user-configured transformations. Length/DLC modifications can delete frames if they produce a length larger than the backing skb frame capacity. Checksum parameter validation only constrains configured indices to possible CAN/CAN FD ranges; runtime relative indices can still become negative for short received frames and then skip checksum writes.

Routing-loop protection depends on CAN skb extension hop counters. Frames without a CAN skb extension are ignored by the gateway.

UID updates replace only modification data, not interfaces or filters. Attempts to reuse a UID with a different gateway tuple return `-EINVAL`.

Gateway creation accepts same source and destination only with `CGW_FLAGS_CAN_IIF_TX_OK`; otherwise it rejects self-routing to avoid immediate loops.

`cgw_put_job()` dumps counters only when nonzero, so user-space readers must treat missing stats attributes as zero.

## Test Signals
Strong test signals are rtnetlink route create/delete/dump tests with `CAP_NET_ADMIN`, vcan interface pairs, Classic CAN and CAN FD forwarding, every modification type, checksum profiles, UID update behavior, route loop hop limits, timestamp preservation flags, same-interface rejection/allowance, and device unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/gw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/isotp.c -->
# sources/distributed-fs/ceph-client/net/can/isotp.c

## Purpose
This file implements the PF_CAN ISO 15765-2 transport protocol (`CAN_ISOTP`). It exposes datagram sockets that segment larger protocol data units over Classic CAN or CAN FD, handle flow control, enforce padding and STmin options, support broadcast modes, and reassemble incoming ISO-TP PDUs for user space.

## Important APIs, Types, And Functions
`struct isotp_sock` is the socket state. It stores bind state, ifindex, TX/RX CAN IDs, timers, ISO-TP options, flow-control options, link-layer options, forced STmin settings, echo tracking, RX/TX `struct tpcon` state machines, notifier list node, wait queue, and RX state lock.

`struct tpcon` tracks one RX or TX PDU: buffer pointer, buffer length, PDU length, current index, state, block size counter, sequence number, link-layer data length, and default static buffer.

Important functions include `isotp_bind()`, `isotp_sendmsg()`, `isotp_recvmsg()`, `isotp_rcv()`, `isotp_rcv_sf()`, `isotp_rcv_ff()`, `isotp_rcv_cf()`, `isotp_rcv_fc()`, `isotp_send_fc()`, `isotp_send_cframe()`, `isotp_rcv_echo()`, `isotp_setsockopt_locked()`, and netdevice notifier helpers.

## Control Flow
Socket initialization fills default ISO-TP options, initializes RX/TX state to idle, points RX/TX buffers at static 8300-byte arrays, sets up three high-resolution timers, adds the socket to the global notifier list, and installs `isotp_sock_destruct()`.

Before binding, user space may set options. `isotp_bind()` validates AF_CAN, ifindex, sanitized CAN IDs, CAN/CAN FD MTU compatibility, and distinct TX/RX IDs for normal unicast mode. It registers the RX ID for data/flow-control frames unless a broadcast mode is active, always registers the TX ID for local echo tracking, then marks the socket bound.

`isotp_sendmsg()` serializes one PDU at a time using `cmpxchg()` on `tx.state`. It may grow the static TX buffer up to the module `max_pdu_size`, validates broadcast constraints, copies user payload, builds a single frame when possible, otherwise builds a first frame and either waits for flow control or enters CF-broadcast mode. Consecutive frames are paced by local echo (`isotp_rcv_echo()`), flow-control block size, and `tx_gap`/`txfrtimer`.

The receive callback `isotp_rcv()` enforces the configured MTU, optional extended address, and half-duplex constraints under `rx_lock`. It dispatches N_PCI types to flow-control, single-frame, first-frame, or consecutive-frame handlers. Multi-frame RX sends FC CTS/OVFLW frames unless listen mode is active, tracks sequence numbers, enforces block size and padding options, and queues a completed PDU as a datagram skb.

Release waits for TX idle where possible, moves TX to shutdown, unregisters CAN filters, cancels timers, removes notifier state, and frees any dynamically grown RX/TX buffers in the socket destructor.

## State And Persistence
State is per socket and in memory only. Options must be set before bind because `isotp_setsockopt_locked()` rejects changes after binding. RX/TX state machines persist across callbacks and timers until completion, timeout, error, release, or netdevice unregister.

The default static buffers avoid allocation for common PDUs. Larger buffers are lazily allocated up to `max_pdu_size` and freed on socket destruction. Wait queues coordinate blocking writers and release behavior.

## Dependencies And Integration Points
ISO-TP depends on PF_CAN protocol registration, `can_send()`, CAN receive filters, CAN skb extensions, CAN ISO-TP UAPI options from `linux/can/isotp.h`, high-resolution timers, datagram socket queues, and netdevice notifiers.

It relies on local echo delivery through PF_CAN to know when a single/consecutive frame has left the local stack and when to schedule the next consecutive frame.

## Risks And Edge Cases
Only one TX PDU can be active per socket. Blocking sends wait for idle; nonblocking sends return `-EAGAIN`.

Padding and length validation are subtle across Classic CAN and CAN FD because optimized lengths, mandatory CAN FD padding, extended addressing, and SF_DL/FF_DL escape encodings interact.

Half-duplex mode suppresses conflicting RX/TX progress but depends on correct N_PCI classification under `rx_lock`.

The bind path calls `can_rx_register()` but does not check the return value in the visible code; registration failures could leave partial state if allocation fails in the CAN core.

Some error paths call `netdev_put(dev, NULL)` after `dev_get_by_index()` while most paths call `dev_put()`. That warrants review against the kernel version's netdevice reference API expectations.

Timeouts surface as socket errors: RX data timeout `ETIMEDOUT`, TX flow-control/echo timeout `ECOMM`, malformed padding/layout `EBADMSG`, sequence mismatch `EILSEQ`, and receiver overflow `EMSGSIZE`.

## Test Signals
Test with vcan pairs and ISO-TP user-space tools should cover single-frame and multi-frame send/receive, Classic CAN versus CAN FD MTUs, 12-bit and 32-bit FF_DL lengths, STmin and forced STmin, dynamic flow-control parameters, padding length/data checks, listen mode, half-duplex, SF/CF broadcast modes, local echo timeouts, netdevice down/unregister, and max PDU size boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/isotp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/Kconfig -->
# sources/distributed-fs/ceph-client/net/can/j1939/Kconfig

## Purpose
This Kconfig file declares the `CAN_J1939` build option for in-kernel SAE J1939 protocol support over PF_CAN.

## Important APIs, Types, And Functions
The single symbol is `config CAN_J1939`, a tristate option named "SAE J1939". It depends on `CAN` and enables the J1939 socket type and protocol implementation.

The help text identifies the relevant standard areas: SAE J1939-21 for datalink/transport protocol and SAE J1939-81 for network management.

## Control Flow
Kconfig selection controls whether the J1939 objects in the sibling Makefile are omitted, built in, or built as a module. When enabled as a module, `main.c` advertises `MODULE_ALIAS("can-proto-" __stringify(CAN_J1939))`, allowing PF_CAN protocol autoload.

## State And Persistence
The file does not define runtime state. It controls compile-time availability and module/built-in linkage.

## Dependencies And Integration Points
The option depends on the broader CAN subsystem. It integrates with the net/can build hierarchy through the J1939 Makefile and with PF_CAN protocol registration at runtime.

## Risks And Edge Cases
Because this is a protocol-family extension, disabling it removes the `CAN_J1939` socket protocol even if user-space tools exist. As a module, correct aliasing and module autoload are important for `socket(PF_CAN, SOCK_DGRAM, CAN_J1939)`.

## Test Signals
Configuration tests should verify `CAN_J1939=n` omits the module, `m` builds `can-j1939.ko` with the expected alias, and `y` links the protocol into the kernel when `CAN` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/Makefile -->
# sources/distributed-fs/ceph-client/net/can/j1939/Makefile

## Purpose
This Makefile defines how the SAE J1939 protocol implementation is built.

## Important APIs, Types, And Functions
`obj-$(CONFIG_CAN_J1939) += can-j1939.o` builds one composite object controlled by the Kconfig symbol. `can-j1939-objs` is composed from `address-claim.o`, `bus.o`, `main.o`, `socket.o`, and `transport.o`.

## Control Flow
When `CONFIG_CAN_J1939` is built in or modular, kbuild compiles the listed objects and links them into the `can-j1939` module or built-in object. `transport.o` is not in this research subset but is part of the final linked protocol.

## State And Persistence
The Makefile has no runtime state. It defines object composition, which determines which internal symbols from `j1939-priv.h` are available within the composite module.

## Dependencies And Integration Points
It integrates with the parent CAN networking build and the Kconfig symbol from `Kconfig`. Runtime integration is provided by `main.o` registering the protocol and netdevice notifier.

## Risks And Edge Cases
The private header declares transport functions implemented by `transport.o`; omitting that object would break J1939 send/receive. Any source-file addition must be reflected here to participate in the composite module.

## Test Signals
Build tests for `CONFIG_CAN_J1939=y` and `m` are sufficient for this file, with link coverage ensuring all private cross-file symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/address-claim.c -->
# sources/distributed-fs/ceph-client/net/can/j1939/address-claim.c

## Purpose
This file implements J1939 address-claim processing and NAME-to-source-address fixup. It tracks observed address-claimed messages, resolves source/destination names into current addresses for outgoing traffic, annotates incoming skbs with source/destination names, and enforces J1939 address-claim message validity.

## Important APIs, Types, And Functions
Exported internal functions are `j1939_ac_fixup()` for TX-time address/name resolution and `j1939_ac_recv()` for RX-time address-claim and name annotation.

Important helpers include `j1939_skb_to_name()`, `j1939_ac_msg_is_request()`, `j1939_ac_verify_outgoing()`, and `j1939_ac_process()`. They operate on `struct j1939_priv`, `struct j1939_sk_buff_cb`, `struct j1939_ecu`, and the ECU mapping APIs from `bus.c`.

## Control Flow
On transmit, `j1939_send_one()` calls `j1939_ac_fixup()`. Address-claimed PGNs are validated for 8-byte NAME payload, matching source name, non-broadcast source address, and broadcast destination. If a claimed ECU's address differs from the outgoing source address, the old mapping is removed so the later looped-back address-claim receive path can establish the new mapping. Non-address-claim traffic with a source or destination name is resolved through `j1939_name_to_addr()` and rejected with `-EADDRNOTAVAIL` when no unicast mapping exists, except for address-claim request messages.

On receive, `j1939_ac_recv()` handles address-claimed PGNs through `j1939_ac_process()`. That function validates DLC/name/source address, finds or creates the ECU by NAME, cancels pending claim timers, handles idle-address unmapping, applies J1939 NAME priority when two ECUs contend for the same address, and starts the ECU's 250 ms claim timer. For other received traffic, it looks up current source and destination names by address and stores them in the skb control block.

## State And Persistence
Address-claim state is stored in `struct j1939_priv`: the ECU list and 256-entry address map maintained by `bus.c`. Mappings are not committed immediately on address-claimed reception; they become active after the ECU timer expires, matching the J1939 contention window. State lasts while the J1939 per-device private object exists and is cleared on netdevice down/unregister.

## Dependencies And Integration Points
The file depends on `j1939-priv.h`, ECU map helpers from `bus.c`, and send/receive orchestration in `main.c`. It relies on CAN echo: locally sent address-claim frames are processed in the receive path so local and remote claims are ordered consistently.

## Risks And Edge Cases
Address-claim correctness depends on receiving local echo. If echo is absent or delayed, local ECU mappings may not become active when user space expects.

The code intentionally does not send address-claim responses itself; user space must implement policy daemons. Kernel state only observes and resolves claims.

NAME priority conflict handling unmaps the losing ECU and starts/restarts timers under `priv->lock`; missed refcount or timer cancellation bugs here would affect all name/address resolution.

Outgoing named traffic can fail until the 250 ms address-claim timer maps the ECU, even if an address-claimed frame was just seen.

## Test Signals
Tests should inject address-claimed frames with valid, idle, duplicate, and malformed payloads; verify 250 ms delayed mapping; verify lower NAME wins address contention; verify outgoing named traffic fails before claim and succeeds after mapping; and verify local echo address claims update mappings in transmit order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/address-claim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/bus.c -->
# sources/distributed-fs/ceph-client/net/can/j1939/bus.c

## Purpose
This file manages J1939 ECU objects and the in-memory bus address map for one CAN netdevice. It tracks NAME-address associations, local socket user counts, delayed address-claim activation, and ECU object lifetimes.

## Important APIs, Types, And Functions
The main APIs are `j1939_ecu_create_locked()`, `j1939_ecu_put()`, `j1939_ecu_unmap_locked()`, `j1939_ecu_unmap()`, `j1939_ecu_unmap_all()`, `j1939_ecu_timer_start()`, `j1939_ecu_timer_cancel()`, `j1939_ecu_get_by_addr()`, `j1939_ecu_get_by_name()`, `j1939_name_to_addr()`, `j1939_local_ecu_get()`, and `j1939_local_ecu_put()`.

`struct j1939_ecu` instances are linked in `priv->ecus`, keyed by NAME for lookup, optionally mapped into `priv->ents[addr].ecu`, and refcounted with `kref`.

## Control Flow
ECU creation initializes the object with idle address, NAME, timer, refcount, and a reference to `j1939_priv`, then appends it to the ECU list. Mapping requires a unicast address and an empty address slot; it takes an ECU reference and adds the ECU's local-user count to the address entry. Unmapping clears the address entry, subtracts local users, and drops the map-held ECU reference.

Address-claim processing starts `j1939_ecu_timer_start()`, which holds the ECU and schedules a 250 ms soft hrtimer. The timer handler maps the ECU under `priv->lock` and drops the timer-held reference. Cancellation drops that reference if the timer was pending.

Socket bind/rebind uses `j1939_local_ecu_get()` to increment local user counts for source address and/or NAME, creating an ECU for a named local user if needed. Release/rebind uses `j1939_local_ecu_put()` to decrement those counts and drop the ECU reference.

## State And Persistence
All state is per `j1939_priv` and lasts until netdevice stop/unregister or all references are released. ECU objects are reference-counted by list ownership, active address map slots, timers, local users, and transient lookups. No state persists outside memory.

`priv->lock` protects both the ECU list and address-entry table. Some lookups return referenced ECUs, while `_find_` helpers return borrowed pointers and require the lock to remain held.

## Dependencies And Integration Points
`address-claim.c` uses these APIs to resolve and update J1939 network-management state. `socket.c` uses local ECU get/put to mark local source identities and help transport logic identify local endpoints. `main.c` calls `j1939_ecu_unmap_all()` on netdevice events and releases `j1939_priv` references after ECU cleanup.

## Risks And Edge Cases
Mapping and local-user accounting share `priv->ents[addr].nusers`. Bugs in bind/release balance can underflow counts or mislabel received frames as local/not local.

`j1939_ecu_map_locked()` warns and skips if a slot is already mapped. Address-claim conflict logic must unmap previous occupants first to avoid silently losing mappings.

Timers hold ECU references. Every timer start must be paired with either timer handler completion or successful cancellation.

`j1939_name_to_addr()` returns idle or no-address sentinel values when no active mapping exists; callers must distinguish unclaimed names from broadcast/no-name behavior.

## Test Signals
Test address-claim timer activation/cancel, duplicate NAME lookup, address contention, local user count increments/decrements for named and address-only binds, netdevice down unmapping, and final release assertions that ECU and priv lists are empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/j1939-priv.h -->
# sources/distributed-fs/ceph-client/net/can/j1939/j1939-priv.h

## Purpose
This private header defines the internal SAE J1939 protocol data model and cross-file function contracts. It ties together socket handling, CAN receive/transmit glue, address claiming, ECU bus state, and transport protocol sessions.

## Important APIs, Types, And Functions
Key types include `struct j1939_ecu`, `struct j1939_priv`, `struct j1939_addr`, `struct j1939_sk_buff_cb`, `struct j1939_session`, and `struct j1939_sock`.

`struct j1939_priv` is the per-CAN-device protocol object. It owns the ECU list, address-entry table, netdevice pointer, active transport session list, max packet size, socket list, receive-side refcount, and timestamp key counter.

`struct j1939_sk_buff_cb` is stored in `skb->cb` and carries J1939 address metadata, message flags, transport offset, timestamp key, local source/destination flags, and priority.

`struct j1939_session` describes simple/TP/ETP transfer state, packet counters, timers, queued skbs, socket association, session state, and identifying address tuple.

`struct j1939_sock` embeds `struct sock`, bind/connect state, filters, PGN receive filter, wait queue, pending skb count, and queued sessions.

The header declares internal APIs for ECU mapping, address claim, socket receive/error queues, transport send/receive/session management, netdevice start/stop, and notifier reactions.

## Control Flow
Files in this module share state through this header. `main.c` creates `j1939_priv` and converts CAN frames to/from `j1939_sk_buff_cb`; `address-claim.c` resolves NAME/address state; `bus.c` owns ECU objects; `socket.c` owns user-visible sockets and session queues; `transport.c` implements the session machinery declared here.

Inline helpers classify addresses and PDU1 PGNs and provide `j1939_skb_to_cb()` with a build-time size check against `skb->cb`.

## State And Persistence
The header defines in-memory state only. Lifetimes are controlled by krefs, socket references, RCU-deferred socket destruction, hrtimers, list ownership, and netdevice references in the implementation files.

## Dependencies And Integration Points
It depends on public J1939 CAN UAPI (`linux/can/j1939.h`) and networking socket internals. It is included by all J1939 implementation units and is the internal ABI between them.

## Risks And Edge Cases
Because this header defines `skb->cb` layout, any size growth in `struct j1939_sk_buff_cb` can break receive/transmit paths; the build-time assertion in `j1939_skb_to_cb()` is the guard.

The session struct has multiple lock domains: active session list lock, socket session queue lock, and timer-owned TX fields. Changes need careful lock-order review.

`struct j1939_sock` embeds `struct sock` as the first member; `j1939_sk_init()` relies on this to memset the protocol-private tail only.

## Test Signals
Build coverage catches many header contract breaks. Runtime signals should come from J1939 socket tests covering bind/connect, filters, transport sessions, session cancellation, error queue reporting, and netdevice teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/j1939-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/main.c -->
# sources/distributed-fs/ceph-client/net/can/j1939/main.c

## Purpose
This file is the J1939 core glue between PF_CAN and the internal J1939 stack. It registers the CAN_J1939 protocol, manages one `j1939_priv` object per CAN netdevice, registers receive filters, parses incoming CAN EFF frames into J1939 metadata, sends J1939 skbs as CAN frames, and reacts to netdevice state changes.

## Important APIs, Types, And Functions
Externally visible internal functions are `j1939_netdev_start()`, `j1939_netdev_stop()`, `j1939_send_one()`, `j1939_priv_get()`, and `j1939_priv_put()`.

Important internal helpers include `j1939_can_recv()`, `j1939_priv_create()`, `j1939_priv_set()`, `j1939_can_rx_register()`, `j1939_can_rx_unregister()`, `j1939_priv_get_by_ndev()`, and `j1939_netdev_notify()`.

The module registers `j1939_can_proto`, implemented in `socket.c`, and a netdevice notifier.

## Control Flow
`j1939_netdev_start()` is called when a socket binds to a CAN device. It looks for an existing `j1939_priv` under `j1939_netdev_lock`, increments the receive refcount if present, or creates a new object, initializes transport and socket lists, installs it into `can_ml_priv`, registers a broad extended-frame receive filter, and returns the referenced private object.

`j1939_can_recv()` receives borrowed CAN skbs from PF_CAN, accepts only Classical CAN, clones the skb, takes a `j1939_priv` reference, pulls the CAN header so the skb payload is just J1939 data bytes, fills `j1939_sk_buff_cb` from the 29-bit CAN ID, normalizes PDU1 PGNs and destination addresses, annotates local source/destination flags from the address table, then runs address-claim receive, transport receive, simple receive, and socket delivery. It releases the private reference and cloned skb afterward.

`j1939_send_one()` performs TX sanity normalization, calls address-claim fixup, pushes a CAN header back onto the skb, pads to an 8-byte CAN frame, constructs the EFF CAN ID from priority, PGN, destination, and source address, then sends with local loopback through `can_send()`.

The netdevice notifier cancels active sessions, reports errors to sockets, and unmaps ECUs on down/unregister. Module init registers the notifier first and then the PF_CAN protocol; exit unregisters both.

## State And Persistence
`j1939_priv` is stored in `can_ml_priv->j1939_priv` for the CAN netdevice. It is protected by `j1939_netdev_lock` for creation/removal and by krefs for receive, socket, ECU, and transient users. The receive filter's lifetime is counted by `rx_kref`; the final unregister path clears the netdevice pointer and unmaps ECUs.

State persists while at least one socket/session/receive user holds references. It is not persisted across module unload or device unregister.

## Dependencies And Integration Points
This file depends on PF_CAN core receive registration and `can_send()`, CAN skb extensions, CAN multi-layer device private state, the J1939 socket protocol from `socket.c`, ECU/address claim from `address-claim.c` and `bus.c`, and transport/simple receive functions from `transport.c`.

## Risks And Edge Cases
The code relies on local loopback for address-claim ordering and transmit completion behavior. Devices or configurations that disturb echo semantics can affect J1939 state.

`j1939_can_recv()` clones and mutates the skb layout; downstream layers expect skb data to start at J1939 payload, while `j1939_send_one()` expects enough headroom to push the CAN header back.

Per-device private creation handles a race where another binder creates `priv` first, but this path must keep netdevice and kref accounting balanced.

Only Classical CAN frames are accepted in this receive path; CAN FD frames are ignored for J1939 here.

## Test Signals
Tests should cover concurrent binds to the same vcan device, bind/release reference balance, receive parsing for PDU1/PDU2 PGNs, transmit CAN ID construction, netdevice down/unregister behavior, and module autoload through `can-proto-CAN_J1939`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/socket.c -->
# sources/distributed-fs/ceph-client/net/can/j1939/socket.c

## Purpose
This file implements the user-visible SAE J1939 datagram socket protocol. It handles bind/connect, address and PGN filtering, receive delivery, send queueing into J1939 transport sessions, ancillary data, timestamp/error queue reporting, socket options, release, and netdevice event cleanup.

## Important APIs, Types, And Functions
The `proto_ops` table exposes release, bind, connect, getname, poll, setsockopt, getsockopt, sendmsg, recvmsg, and ioctl fallback. `j1939_can_proto` registers this as a `SOCK_DGRAM` PF_CAN protocol.

Important functions include `j1939_sk_bind()`, `j1939_sk_connect()`, `j1939_sk_sendmsg()`, `j1939_sk_send_loop()`, `j1939_sk_recvmsg()`, `j1939_sk_recv()`, `j1939_sk_recv_match()`, `j1939_sk_setsockopt()`, `j1939_sk_errqueue()`, `j1939_sk_queue_activate_next()`, `j1939_sk_netdev_event_netdown()`, and `j1939_sk_netdev_event_unregister()`.

Socket options include `SO_J1939_FILTER`, `SO_J1939_PROMISC`, `SO_J1939_ERRQUEUE`, and `SO_J1939_SEND_PRIO`.

## Control Flow
Initialization clears the protocol-private tail of `struct j1939_sock`, sets default priority and reuse behavior, initializes filters, queues, and wait queue, enables RCU socket free, and installs the J1939 destructor.

Bind validates `sockaddr_can`, requires an ifindex and clean PDU1 PGN, resolves and validates the CAN device, starts or references the per-device `j1939_priv`, records local NAME/source address/PGN receive filter, increments local ECU accounting, and adds the socket to `priv->j1939_socks`. Rebinding to the same interface drops old local references and installs new ones; rebinding to a different interface is rejected.

Connect requires a prior bind to the same interface, validates destination name/address and broadcast permissions, stores peer NAME/address and optional PGN, and marks the socket connected.

Receive delivery walks `priv->j1939_socks`. `j1939_sk_recv_one()` rejects own-origin skbs, applies bound/connected destination-source matching, PGN and filter matching, clones matching skbs, sets message flags such as `MSG_DONTROUTE`, and queues to the socket receive queue. `recvmsg()` returns payload, source sockaddr, destination ancillary data, priority ancillary data, timestamp cmsgs, and message flags.

Send validates bound state, source identity, destination and broadcast permissions, allocates one or more skbs, fills J1939 control metadata, creates or extends a transport session via `j1939_tp_send()` and `j1939_session_skb_queue()`, queues the session on the socket, activates the first non-conflicting session, and schedules transport timers. Release waits for pending skbs, cancels sessions on interruption, removes the socket from the device list, decrements local ECU accounting, stops the netdevice private, frees filters, and drops the socket.

## State And Persistence
Socket state persists for the life of the socket. It includes bind/connect flags, local/remote J1939 addresses, filters, a PGN receive filter, pending skb count, and queued transport sessions. Per-device socket membership is protected by `priv->j1939_socks_lock`; per-socket session queue is protected by `sk_session_queue_lock`.

Error queue state is optional and controlled by `SO_J1939_ERRQUEUE`. When disabled, abort errors are reported through `sk_err` and `sk_error_report()` instead of queued timestamp/error skbs.

## Dependencies And Integration Points
This file depends on `main.c` for netdevice private start/stop and sending, `bus.c` for local ECU accounting, `transport.c` for session creation/activation/cancellation/timers, Linux error queue/timestamping support, CAN J1939 UAPI structures, and datagram socket queue helpers.

Netdevice event callbacks from `main.c` call into this file to report `ENETDOWN`, drop queues, unbind sockets on unregister, and synchronize RCU before clearing private pointers.

## Risks And Edge Cases
The send loop can split large writes into multiple TP-sized skbs and requires later writes that complete an existing incomplete session to match the originally declared total size. Mismatches return `-EIO`.

Release waits for `skb_pending` to reach zero. If interrupted, it cancels active sessions and drops queued sessions, so callers can observe shutdown errors for in-flight sends.

Filtering combines bind destination matching, connected source matching, PGN receive filter, and arbitrary user filters. Broadcast receive requires `SO_BROADCAST` unless promiscuous mode is enabled.

Priority values below 2 require `CAP_NET_ADMIN`. Conversion between socket priority and J1939 priority is inverted (`7 - prio`), which is easy to mishandle in tests.

Netdevice unregister manually detaches bound sockets and nulls `jsk->priv` to avoid a later destructor put. This path is race-prone and depends on socket locks plus `synchronize_rcu()`.

## Test Signals
Tests should cover bind/rebind/release, connect permissions, broadcast send/receive with and without `SO_BROADCAST`, NAME and address-based matching, PGN filters, `SO_J1939_FILTER`, promiscuous mode, send priority permission checks, multi-packet TP queueing, interrupted release, error queue notifications, and netdevice down/unregister while sockets and sessions are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/can/j1939/socket.c -->
