# subset-b-007644 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd.c

## Purpose
`o2iblnd.c` is the core implementation for Lustre's OpenIB gen2 LNet network driver. It registers the `O2IBLND` LNet driver, owns module startup/shutdown, creates per-network and per-IB-device state, manages peers and reliable-connected RDMA connections, allocates TX/RX/FMR/FastReg resources, handles IB device/link failover, and exposes control and Netlink tunable hooks.

## Important APIs, types, and functions
- Global state is `struct kib_data kiblnd_data`, declared here and typed in `o2iblnd.h`.
- LNet integration is through `static const struct lnet_lnd the_o2iblnd`, with callbacks for startup, shutdown, ioctl control, send, receive, device priority, tunable defaults, Netlink get/set, timeout, and key metadata.
- Message validation and wire helpers: `kiblnd_cksum()`, `kiblnd_msgtype2str()`, `kiblnd_msgtype2size()`, `kiblnd_unpack_rd()`, `kiblnd_pack_msg()`, and `kiblnd_unpack_msg()`.
- Peer lifecycle: `kiblnd_create_peer()`, `kiblnd_destroy_peer()`, `kiblnd_find_peer_locked()`, `kiblnd_unlink_peer_locked()`, `kiblnd_del_peer()`, and debug/control helpers.
- Connection lifecycle: `kiblnd_create_conn()`, `kiblnd_destroy_conn()`, `kiblnd_close_peer_conns_locked()`, `kiblnd_close_stale_conns_locked()`, and matching close helpers.
- Pooling: `kiblnd_alloc_pages()`, RX descriptor mapping, TX pool creation/destruction, generic poolset allocation, FMR/FastReg pool creation, mapping, unmapping, and idle cleanup.
- Device/failover: `kiblnd_hdev_get_attr()`, `kiblnd_event_handler()`, `kiblnd_dev_need_failover()`, `kiblnd_dev_failover()`, `kiblnd_destroy_dev()`, and notifier handlers for netdev and IP address state.
- Driver lifecycle: `kiblnd_base_startup()`, `kiblnd_startup()`, `kiblnd_shutdown()`, `kiblnd_base_shutdown()`, `ko2iblnd_init()`, and `ko2iblnd_exit()`.

## Control flow
Module init asserts wire constants, initializes default tunables, sets up libcfs, and registers `the_o2iblnd`. The first NI startup initializes base global state, starts the connection daemon, optionally starts the failover thread, and registers netdevice/address notifiers. NI startup then resolves/selects an IPoIB interface, creates or reuses a `kib_dev`, binds an RDMA listener through `kiblnd_dev_failover()`, starts scheduler threads for the NI's CPTs, initializes FMR/FastReg and TX pools, links the `kib_net` into the device, and marks link fatal state when the netdev or IB port is down.

Peer and connection flow begins with `kiblnd_launch_tx()` in `o2iblnd_cb.c`, but peer table and connection objects are allocated here. `kiblnd_create_conn()` binds an RDMA CM id to a peer, selects a scheduler, verifies the CM device matches the current HCA, creates a CQ/QP, allocates and DMA maps RX buffers, posts receives, and initializes connection credits and refcounts. On teardown, closing moves established conns to the connd queue; destruction requires all TX/RX state to be drained and releases QP, CQ, mapped pages, HCA references, peer references, and CM IDs.

Pool flow is split between generic `kib_poolset` logic and RDMA memory registration pools. TX pools hold pre-mapped message buffers and descriptors. FMR/FastReg pools are per-CPT, grow on demand, keep a persistent first pool, and retire failed or idle extra pools after `IBLND_POOL_DEADLINE`. FastReg setup supports regular memory registration and optionally SG gaps.

Failover flow detects HCA changes by rebinding/listening on the IPoIB address, swaps the active `kib_hca_dev`, marks existing TX and FMR pools as failed, and lets future allocations use the new HCA. Netdevice and inetaddr notifiers update LNet fatal link state and ping buffer state based on link up/down, address presence, and IB port events.

## State and persistence behavior
All state is in-kernel runtime state; there is no disk persistence. Important persistent-in-memory structures are the global peer hash, device list, failed-device list, connd queues, reconnection queues, per-CPT schedulers, per-net poolsets, and refcounted peer/conn/HCA objects. Shutdown waits for peer and connection counters to drain, wakes worker threads, and waits for `kib_nthreads` to reach zero. Tunables are copied into per-NI LNet tunable structures during startup and exposed through module parameters and Netlink.

## Dependencies and integration points
This file depends on Linux kernel networking, RDMA CM, IB verbs, libcfs/LNet APIs, Lustre RDMA helpers, `o2iblnd-idl.h`, and the shared declarations in `o2iblnd.h`. It calls hot-path callbacks implemented in `o2iblnd_cb.c`, especially send/recv, CM, scheduler, failover thread, CQ/QP callbacks, TX completion, and RX post helpers. It also integrates with LNet netdev priority, LNet fatal link state, ping-buffer updates, legacy libcfs ioctls, and Netlink tunable export/import.

## Risks and edge cases
- Connection and peer lifetime depend on careful refcount ownership transfer between CM callbacks, peer table refs, RX refs, active TX refs, scheduler refs, and connd zombie cleanup.
- Failover swaps HCA state while connections and pools may still refer to the old HCA; failed-pool marking and refcounts are central to safety.
- Queue depth and WR sizing are adjusted dynamically to satisfy `max_qp_wr`; regressions can underprovision QPs or silently reduce performance.
- FMR/FastReg behavior differs by OFED/kernel capability and device flags; SG gaps and FastReg key invalidation are especially sensitive.
- Wire compatibility is protected by many `BUILD_BUG_ON()` constants; changing IDL structs without updating these checks will fail build or break interoperability.
- Link/address notifier paths must run under appropriate RTNL/RCU assumptions and can incorrectly mark an NI fatal if interface aliases, IPv6 state, or netdev registration transitions are mishandled.

## Test signals
Useful tests include kernel builds across in-kernel and external OFED configurations; module load/unload with leak/refcount checks; LNet NI add/delete for IPv4 and IPv6 IPoIB interfaces; active/passive connect between mixed protocol versions; queue-depth and max-frag negotiation; large PUT/GET RDMA traffic; small immediate traffic; GPU-backed MD mapping if enabled; HCA/link down/up and bonding failover; Netlink tunable dump/set; and fault injection for allocation, CQ/QP creation, RDMA CM rejection, timeout, and device fatal events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd.h

## Purpose
`o2iblnd.h` is the shared internal interface for the o2iblnd driver. It pulls in Linux, RDMA, libcfs, LNet, and Lustre RDMA headers; defines tunable attributes, constants, state objects, descriptor layouts, inline helpers, compatibility wrappers, and cross-file prototypes used by `o2iblnd.c`, `o2iblnd_cb.c`, and `o2iblnd_modparams.c`.

## Important APIs, types, and functions
- Tunables: `enum kiblnd_ni_lnd_tunables_attr`, `struct kib_tunables`, external `kiblnd_tunables`, and `kib_default_tunables`.
- Device state: `struct kib_dev` for IPoIB interface/LNet device state and `struct kib_hca_dev` for active RDMA CM listener, IB device, PD, port, event handler, and HCA refcount.
- Pool state: `struct kib_pages`, `struct kib_poolset`, `struct kib_pool`, `struct kib_tx_poolset`, `struct kib_tx_pool`, `struct kib_fmr_poolset`, `struct kib_fmr_pool`, `struct kib_fmr`, and FastReg descriptors.
- Network/driver state: `struct kib_net`, `struct kib_sched_info`, and global `struct kib_data`.
- Transfer state: `struct kib_rx`, `struct kib_tx`, `struct kib_connvars`, `struct kib_conn`, and `struct kib_peer_ni`.
- Inline helpers cover timeout calculation, connection request timeout, concurrent send clamping, HCA/conn/peer refs, peer state predicates, round-robin conn selection, keepalive/NOOP credit decisions, queue names, WR ID pointer tagging, connection state barriers, message initialization, RDMA descriptor operations, DMA mapping wrappers, SG address wrappers, and RDMA CM compatibility.
- Prototypes expose pool, FMR, tunable, connd/scheduler/failover, page allocation, CM, peer/conn lifecycle, TX/RX, CQ/QP, message pack/unpack, send/recv, and device-priority APIs.

## Control flow
The header does not execute standalone control flow, but it defines the invariants followed by the implementation. Connections move through `INIT`, active or passive handshaking, `ESTABLISHED`, `CLOSING`, and `DISCONNECTED`. TX descriptors move from pool free lists to peer waiting queues, connection queues, active completions, and back to pools. RX descriptors are preposted and returned with explicit credit modes. Peers move between hash membership, active connection attempts, passive accepts, reconnect waits, connection lists, and idle destruction.

## State and persistence behavior
The file defines volatile kernel state only. Refcounted state is explicit: HCAs use `atomic_t ibh_ref`, connections use `ibc_refcount`, and peers use `kref`. The global `kib_data` owns driver-wide mutable lists and locks; each `kib_net` owns per-NI pools and counters; each peer owns connection and waiting-TX lists; each connection owns queues, credits, RX buffers, CM/QP/CQ pointers, and in-progress handshake data. The helper `kiblnd_set_conn_state()` adds a memory barrier after state changes, signaling that state transitions are synchronization-relevant.

## Dependencies and integration points
The header depends on RDMA CM/IB verbs, `lnet_rdma.h`, `lib-lnet.h`, libcfs, and `o2iblnd-idl.h` wire message definitions. It bridges kernel-version and OFED feature differences with compatibility macros for DMA SG access, RDMA connect locking, FMR pool API availability, and external OFED virtual DMA behavior. The prototypes and inline helpers couple all o2iblnd translation units.

## Risks and edge cases
- Many helpers assume locks are already held, especially peer lookup, HCA refs, connection refs, and queue operations; misuse can introduce races or use-after-free.
- WR ID pointer tagging relies on descriptor alignment and the low three bits being unused.
- Credit logic differs for protocol v1 and v2, with OOB NOOP behavior only available after v1.
- DMA mapping has a GPU path using `lnet_rdma_map_sg_attrs()` that must stay aligned with normal IB DMA mapping semantics.
- Conditional FMR/FastReg fields change struct behavior across builds; both code paths require coverage.
- Queue depth, max fragments, and message size constants must remain compatible with `o2iblnd-idl.h` and remote peers.

## Test signals
Compile tests across configurations with and without OFED FMR APIs, external OFED, IPv6, FastReg gaps, and SG DMA compatibility are essential. Runtime tests should stress refcount paths, concurrent sends, v1/v2 peers, NOOP/keepalive credit return, RDMA fragments near `IBLND_MAX_RDMA_FRAGS`, GPU and non-GPU DMA mapping, and all connection state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_cb.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_cb.c

## Purpose
`o2iblnd_cb.c` implements the o2iblnd callback and hot-path logic: LNet send/receive translation, RDMA memory mapping for message payloads, TX/RX completion handling, credit accounting, active/passive RDMA CM negotiation, connection timeout/reconnect processing, CQ scheduling, and failover thread execution.

## Important APIs, types, and functions
- TX completion and allocation: `kiblnd_tx_done()`, `kiblnd_txlist_done()`, `kiblnd_get_idle_tx()`, `kiblnd_unmap_tx()`.
- RX posting and handling: `kiblnd_post_rx()`, `kiblnd_drop_rx()`, `kiblnd_handle_rx()`, `kiblnd_rx_complete()`, `kiblnd_recv()`.
- Message and RDMA setup: `kiblnd_init_tx_msg_payload()`, `kiblnd_init_tx_sge()`, `kiblnd_setup_rd_kiov()`, `kiblnd_map_tx()`, `kiblnd_fmr_map_tx()`, `kiblnd_init_rdma()`.
- Send queueing: `kiblnd_queue_tx_locked()`, `kiblnd_queue_tx()`, `kiblnd_post_tx_locked()`, `kiblnd_check_sends_locked()`, `kiblnd_launch_tx()`, `kiblnd_send()`.
- Completion protocol: `kiblnd_find_waiting_tx_locked()`, `kiblnd_handle_completion()`, `kiblnd_send_completion()`, `kiblnd_reply()`.
- Connection management: privileged port address resolution, `kiblnd_connect_peer()`, `kiblnd_reconnect_peer()`, `kiblnd_close_conn_locked()`, `kiblnd_finalise_conn()`, `kiblnd_connreq_done()`, `kiblnd_passive_connect()`, `kiblnd_active_connect()`, `kiblnd_rejected()`, `kiblnd_check_connreply()`.
- Callback threads/events: `kiblnd_cm_callback()`, `kiblnd_connd()`, `kiblnd_qp_event()`, `kiblnd_cq_completion()`, `kiblnd_scheduler()`, and `kiblnd_failover_thread()`.

## Control flow
For sends, `kiblnd_send()` allocates a TX descriptor, inspects the LNet message type, and chooses immediate send, PUT RDMA, or GET RDMA. Small non-GPU payloads are copied into the message buffer. Large or GPU-backed payloads are converted into scatterlists, DMA mapped, registered through FMR/FastReg, and described in wire RDMA descriptors. `kiblnd_launch_tx()` finds or creates a peer, queues while connection attempts are in progress, or queues on an established connection. `kiblnd_check_sends_locked()` drains nocredit, NOOP, reserved, and normal queues according to credits, concurrent send limits, and keepalive/credit-return needs. `kiblnd_post_tx_locked()` packs final headers, posts IB send WR chains, and handles rollback on post failure.

For receives, CQ completions call `kiblnd_rx_complete()`, which unpacks the message, rejects stale NID/incarnation stamps, records peer liveness, defers early receives until establishment, and then dispatches `kiblnd_handle_rx()`. Immediate messages are passed to `lnet_parse()`. PUT requests cause `kiblnd_recv()` to register a local sink and send `PUT_ACK`; the sender then performs RDMA write and sends `PUT_DONE`. GET requests cause `kiblnd_reply()` to register a source, perform RDMA write, and send `GET_DONE`. Completion messages match waiting TX cookies and finalize LNet messages.

For connection setup, active connects resolve address/route, create a conn, send `CONNREQ`, and validate `CONNACK`. Passive connects validate private data, destination NI, protocol version, queue depth, max fragments, message size, privileged port policy, stale incarnations, and connection races before accepting with `CONNACK`. Rejections can trigger reconnect with downgraded protocol, reduced queue depth, or reduced max fragments.

For background processing, `kiblnd_connd()` destroys zombie conns, disconnects closing conns, schedules reconnects, and periodically checks peer buckets for waiting TX, connection request, and active RDMA timeouts. CQ callbacks schedule connections onto per-CPT scheduler queues; scheduler threads poll CQs, re-arm notifications, dispatch RX/TX/MR/RDMA completion types, and drop refs. The failover thread drains failed-device requests, calls `kiblnd_dev_failover()`, and periodically probes active devices.

## State and persistence behavior
This file mutates only runtime kernel state. It owns TX descriptor transitions, RX repost/drop decisions, peer liveness timestamps, peer connection attempt counters, connection state transitions after CM events, health status propagation into LNet messages, timeout deadlines, reconnect queues, CQ scheduling flags, and failover retry timestamps. LNet messages are finalized exactly when o2iblnd knows local copy/RDMA/control completion status, and health status is preserved through `tx_hstatus`.

## Dependencies and integration points
The file depends on shared definitions from `o2iblnd.h`, LNet message parsing/finalization/reply creation, LNet error simulation, LNet GPU MD detection, RDMA CM, IB verbs CQ/QP/send/recv APIs, Linux credentials for privileged source port binding, and failover/device functions implemented in `o2iblnd.c`. It is the implementation target for many callbacks registered from the LNet driver and RDMA CM listener.

## Risks and edge cases
- Credit accounting is complex: peer credits, reserved credits, outstanding credits, NOOP credits, OOB v2 behavior, and v1 last-credit reservation must remain balanced.
- TX descriptors can be simultaneously affected by send completion, remote completion, timeout, and connection close; the `tx_sending`, `tx_waiting`, and `tx_queued` state machine is delicate.
- FastReg local invalidate/reg WR chains must be posted in the right order and returned to pools exactly once.
- Failure to receive expected IB completions can leave stale connections; the code comments call out this risk during abort handling.
- Passive/active connection races are resolved by NID hash and a race counter, so regressions can cause repeated rejection or duplicate connections.
- Privileged port override temporarily changes credentials; error paths must revert credentials and destroy CM IDs.
- CQ scheduling uses extra connection refs; missed drops or scheduling after refcount zero would be severe.

## Test signals
High-value tests include immediate ACK/PUT/REPLY traffic, RDMA PUT and GET with large and fragmented payloads, GPU-backed MD sends, v1/v2 interoperability, concurrent sends at credit limits, keepalive/NOOP generation, connect race simulations, stale incarnation rejection, CM rejection downgrade paths, privileged source port binding, RDMA timeouts, CQ poll error/fail completions, device fatal/port events, failover retry, and LNet health status assertions for local, remote, network, and timeout failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_cb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_modparams.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_modparams.c

## Purpose
`o2iblnd_modparams.c` defines o2iblnd module parameters, exposes them through `module_param()`, validates selected inputs, initializes the global tunable pointer table, computes default per-NI o2iblnd tunables, and normalizes LNet common tunables for peer credits, router credits, timeouts, FMR/FastReg pools, connection count, and RoCE ToS.

## Important APIs, types, and functions
- Module parameters include `service`, `cksum`, `timeout`, `nscheds`, `conns_per_peer`, `ntx`, `credits`, `peer_credits`, `peer_credits_hiw`, `peer_buffer_credits`, `peer_timeout`, `ipif_name`, `retry_count`, `rnr_retry_count`, `keepalive`, `ib_mtu`, `concurrent_sends`, `use_fastreg_gaps`, `map_on_demand`, `fmr_pool_size`, `fmr_flush_trigger`, `fmr_cache`, `dev_failover`, `require_privileged_port`, `use_privileged_port`, `wrq_sge`, and `tos`.
- `struct kib_tunables kiblnd_tunables` stores pointers to mutable module parameter storage consumed by the rest of the driver.
- `struct lnet_ioctl_config_o2iblnd_tunables kib_default_tunables` stores the exported default tunables snapshot.
- `param_set_tos()` validates ToS as `-1` or an 8-bit value.
- `kiblnd_msg_queue_size()` returns the v1 fixed queue depth, the NI peer TX credits, or module-level peer credits.
- `kiblnd_tunables_setup()` fills and clamps per-NI tunables and common LNet tunables.
- `kiblnd_tunables_init()` initializes the default tunable snapshot during module init.

## Control flow
At module load, static parameter defaults are registered with sysfs/module infrastructure. `ko2iblnd_init()` calls `kiblnd_tunables_init()` to seed `kib_default_tunables`. During NI startup, `kiblnd_tunables_setup()` validates IB MTU, fills unset LNet common tunables from module parameters, clamps peer credits between o2iblnd minimum/maximum and max TX credits, forces obsolete `map_on_demand` to enabled, chooses peer-credit high-water values, bounds `concurrent_sends`, fills FMR/FastReg and TX pool sizing defaults, ensures at least one connection per peer, copies ToS if unset, and records the effective timeout.

## State and persistence behavior
The module parameters are kernel module runtime state exposed through module parameter permissions. Many sizing and policy parameters are read-only after load (`0444`), while operational values such as checksum, timeout, retry counts, keepalive, and privileged port flags can be changed according to their declared permissions. Per-NI tunables get a copy or normalized value at setup time; later module parameter changes do not automatically rewrite already-initialized NI state unless the driver explicitly re-runs setup.

## Dependencies and integration points
The file depends on `o2iblnd.h` for constants, tunable structs, MTU conversion helpers, LNet common tunable types, and logging. Its outputs feed `o2iblnd.c` startup, Netlink default export, queue-depth/QP sizing, FMR/FastReg pool allocation, scheduler thread sizing, connection timeout math, CM retry parameters, keepalive decisions, and send WR SGE limits in `o2iblnd_cb.c`.

## Risks and edge cases
- Invalid `ib_mtu` is rejected only during tunable setup, so configuration failures surface at NI startup.
- `map_on_demand` is obsolete but still accepted and forced to 1; stale configs may appear accepted while behavior is fixed.
- `peer_credits_hiw` and `concurrent_sends` are auto-clamped; very low/high user values may silently change with only warnings.
- `fmr_pool_size < ntx / 4` is not rejected here but later in pool initialization.
- `wrq_sge` and pool sizes strongly influence QP and memory pressure.
- `tos` accepts `-1..255`; other values return `-ERANGE`.

## Test signals
Tests should cover module parameter parsing, ToS validation, invalid MTU rejection, default setup when common tunables are `-1`, clamping of peer credits and concurrent sends, forced `map_on_demand`, `conns_per_peer` zero fallback, FMR pool size interactions with `ntx`, and Netlink/default tunable export matching `kib_default_tunables`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_modparams.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/Makefile

## Purpose
This Makefile defines the kernel module build composition for Lustre's socket LNet network driver (`ksocklnd`). It tells kbuild to produce `ksocklnd.o` as a module and lists the object files that make up the module.

## Important APIs, types, and functions
- `obj-m += ksocklnd.o` declares `ksocklnd` as a loadable kernel module target.
- `ksocklnd-objs := ...` composes the module from `socklnd.o`, `socklnd_cb.o`, `socklnd_lib.o`, `socklnd_modparams.o`, and `socklnd_proto.o`.
- `ifdef CONFIG_GCOV_PROFILE_LNET` sets `GCOV_PROFILE := y` to enable coverage instrumentation when LNet GCOV profiling is enabled.

## Control flow
kbuild reads this file during the kernel/module build. When `ksocklnd.o` is selected as a module, it links the listed objects into one module. If the build configuration defines `CONFIG_GCOV_PROFILE_LNET`, kbuild enables GCOV coverage for this directory/module.

## State and persistence behavior
The Makefile has no runtime state. Its persistent effect is build graph structure: adding, removing, or reordering objects changes which translation units become part of `ksocklnd`.

## Dependencies and integration points
It integrates with the Linux kbuild system and the Lustre LNet build configuration. The object list must match actual socket LND source files in the same directory and must stay aligned with any source split or new required translation units.

## Risks and edge cases
- Missing an object from `ksocklnd-objs` can produce unresolved symbols or silently omit required protocol functionality.
- Adding GCOV profiling changes build flags and can affect timing-sensitive kernel code.
- This file is for `socklnd`, not `o2iblnd`; changes should not be conflated with the RDMA driver researched in the other files.

## Test signals
Build `ksocklnd` as a module with and without `CONFIG_GCOV_PROFILE_LNET`; verify all socket LND objects link and module symbols resolve. Packaging tests should confirm `ksocklnd.ko` is produced when the socket LND is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/socklnd/Makefile -->
