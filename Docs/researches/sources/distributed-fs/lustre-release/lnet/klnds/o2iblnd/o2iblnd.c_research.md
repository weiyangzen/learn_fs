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
