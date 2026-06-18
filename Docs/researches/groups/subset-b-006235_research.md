# subset-b-006235 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/llsec.c -->
# sources/distributed-fs/ceph-client/net/mac802154/llsec.c

Purpose: implements IEEE 802.15.4 MAC link-layer security for mac802154: PIB parameter storage, key/device/security-level tables, AES-CCM/AES-CTR transforms, transmit encryption, receive decryption, and frame-counter replay protection.

Important APIs and functions: `mac802154_llsec_init/destroy()` initialize and tear down parameters, lists, hashes, locks, crypto refs, and sensitive memory. `mac802154_llsec_get_params/set_params()` expose protected parameter updates. `mac802154_llsec_key_add/del()`, `mac802154_llsec_dev_add/del()`, `mac802154_llsec_devkey_add/del()`, and `mac802154_llsec_seclevel_add/del()` maintain the security table. `mac802154_llsec_encrypt()` and `mac802154_llsec_decrypt()` are the packet data path.

Control flow and state: keys are deduplicated by raw AES key and held by `kref`; each key owns CCM AEAD transforms for 4/8/16-byte auth tags plus CTR for unauthenticated encryption. Devices are indexed by extended address and optional `(short_addr, pan_id)` hashes, with RCU list visibility and per-device spinlock for frame counters and key records. TX pulls the header, validates supported frame types, resolves the key, increments the global frame counter under `sec->lock`, pushes the header back, and encrypts/authenticates payload and associated MAC header. RX peeks the header, verifies security is enabled, resolves key/device/security-level, checks and advances per-device or per-device-key counters, then decrypts and trims the auth tag.

Dependencies and integration: called from `tx.c` before packet transmit and from `rx.c` before frame delivery. It depends on kernel crypto (`ccm(aes)`, `ctr(aes)`), IEEE 802.15.4 header helpers, RCU list/hash traversal, and the cfg802154/mac802154 LLSEC operations exposed through `mib.c` and `mac_cmd.c`.

Risks and test signals: replay prevention depends on correct endian handling and monotonically advancing frame counters. RCU readers and table mutation require the outer `sec_mtx` users in `mib.c`; direct callers must not bypass locking. `mac802154_llsec_decrypt()` looks up security level with command id `0`, so MAC command policy granularity should be checked if command-specific levels are expected. No local KUnit tests are present; test signals are integration-level encrypted TX/RX, key table mutation, counter overflow (`-EOVERFLOW`), missing keys, and replayed frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/llsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/llsec.h -->
# sources/distributed-fs/ceph-client/net/mac802154/llsec.h

Purpose: declares the private mac802154 link-layer security model used by `llsec.c` and the public entry points used by the rest of mac802154.

Important types and APIs: `struct mac802154_llsec_key` wraps the generic IEEE key with AEAD/CTR transform handles and a `kref`. `struct mac802154_llsec_device` wraps per-peer state, hash nodes, an RCU head, and a spinlock for frame-counter/key-list mutation. `struct mac802154_llsec` owns current parameters, the exported table, short/long-address hash tables, and an rwlock for parameters. The function declarations cover parameter, key, device, device-key, security-level, encrypt, and decrypt operations.

Control flow and state: the header makes ownership boundaries explicit: table lists are visible through `ieee802154_llsec_table`, while implementation-only wrappers carry locks, hashes, crypto transforms, and RCU lifetime fields. Persistent runtime state is in memory only and scoped to an `ieee802154_sub_if_data` security object.

Dependencies and integration: includes Linux hash/kref/spinlock facilities and IEEE 802.15.4 netdev types. `mib.c` and `mac_cmd.c` call these APIs; `tx.c`/`rx.c` call encrypt/decrypt.

Risks and test signals: callers need to respect the locking implied by `struct mac802154_llsec` because most table walkers are RCU-aware but not globally serialized in the header contract. Tests should verify exported APIs keep generic table pointers valid while preserving hidden wrapper lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/llsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/mac_cmd.c -->
# sources/distributed-fs/ceph-client/net/mac802154/mac_cmd.c

Purpose: wires mac802154 MLME operations to cfg802154/netdev callbacks for PAN start, MAC parameter get/set, and LLSEC table manipulation.

Important APIs and functions: `mac802154_mlme_start_req()` programs PAN ID, short address, channel/page, and LLSEC coordinator/local addressing. `mac802154_set_mac_params()` updates transmit power, CCA mode/level, CSMA retries, frame retries, and listen-before-talk, invoking driver operations only for supported PHY flags. `mac802154_get_mac_params()` snapshots current parameters. `mac802154_mlme_wpan` publishes the ops table.

Control flow and state: all functions assert RTNL. Start request mutates `dev->ieee802154_ptr`, calls `mac802154_dev_set_page_channel()`, and pushes LLSEC parameter changes through `mac802154_set_params()`. Parameter setting updates local `wpan_dev`/`wpan_phy` state first, then programs hardware.

Dependencies and integration: depends on `driver-ops.h`, `mib.c` wrappers, cfg802154 MLME interfaces, and netdevice state. It is the bridge between userspace/configuration requests and lower driver hooks.

Risks and test signals: partial hardware programming can leave software-updated values after a later driver operation fails. Test by setting combinations of PHY flags and checking error propagation and retained state. PAN start assumes short-address mode and uses `BUG_ON` for invalid callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/mac_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/main.c -->
# sources/distributed-fs/ceph-client/net/mac802154/main.c

Purpose: provides mac802154 subsystem allocation, registration, default PHY setup, RX tasklet dispatch, and module init/exit.

Important APIs and functions: `ieee802154_alloc_hw()` allocates a `wpan_phy` with aligned `ieee802154_local` and driver-private memory, initializes queues, work items, tasklet, completion, supported ranges, and interface types. `ieee802154_configure_durations()` derives symbol/SIFS/LIFS durations from page/channel. `ieee802154_register_hw()` creates workqueues, registers the PHY, and creates default `wpan%d` node interface. `ieee802154_unregister_hw()` tears down tasklet, workqueues, interfaces, and phy registration.

Control flow and state: RX interrupt-safe packets are queued into `local->skb_queue`; `ieee802154_tasklet_handler()` drains only `IEEE802154_RX_MSG` packets to `ieee802154_rx()`. Registration establishes `local->workqueue` for TX, `local->mac_wq` for MAC-command/scan/beacon work, `ifs_timer`, and advertised capabilities based on hardware flags.

Dependencies and integration: integrates with `cfg.h`, cfg802154 `wpan_phy`, `ieee802154_if_add/remove`, tasklets, workqueues, RTNL, and exported driver API symbols.

Risks and test signals: registration has multi-step unwind paths; allocation requires valid driver ops. Tests should exercise failure injection for workqueue/PHY/interface creation, RX tasklet handling of invalid packet types, and duration calculation for supported channel pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/mib.c -->
# sources/distributed-fs/ceph-client/net/mac802154/mib.c

Purpose: exposes MAC PIB and LLSEC management operations for netdevices, adding netdevice validation and interface-level serialization around `llsec.c`.

Important APIs and functions: `mac802154_dev_set_page_channel()` calls the driver channel setter and updates current PHY page/channel. `mac802154_get_params/set_params()`, key/device/device-key/security-level add/delete helpers, and table lock/get/unlock wrap the corresponding LLSEC functions with `sdata->sec_mtx`.

Control flow and state: every LLSEC mutation or table exposure locks `sec_mtx`, checks `ARPHRD_IEEE802154`, then delegates to `llsec.c`. Channel setting is RTNL-only and updates software state only after successful hardware programming.

Dependencies and integration: consumed by `mac_cmd.c` LLSEC ops table and cfg802154/mac802154 control paths. It depends on netdevice-to-subinterface conversion and driver ops.

Risks and test signals: table exposure gives callers a live pointer while holding `sec_mtx`; callers must pair lock/unlock. Channel set failure leaves old channel values intact. Tests should verify serialized concurrent add/delete and table iteration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/mib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/rx.c -->
# sources/distributed-fs/ceph-client/net/mac802154/rx.c

Purpose: implements the mac802154 receive path from driver-provided skb to monitor delivery, per-interface filtering, LLSEC decrypt, MAC-command/beacon work dispatch, and data-frame delivery.

Important APIs and functions: `ieee802154_rx_irqsafe()` queues RX skbs from interrupt context. `ieee802154_rx()` handles suspension, optional FCS synthesis/checking, monitor clones, CRC removal, and interface fanout. `ieee802154_subif_frame()` applies destination/PAN filtering, decrypts, updates stats, and dispatches beacon/MAC/data frames. `mac802154_rx_beacon_worker()` and `mac802154_rx_mac_cmd_worker()` process queued management frames.

Control flow and state: packets are parsed into `mac_cb`, cloned per running non-monitor interface under RCU, filtered against required hardware/software levels, decrypted with per-interface LLSEC state, then either delivered to the network stack or queued to `local->rx_beacon_list`/`rx_mac_cmd_list` for `mac_wq`. Monitor interfaces receive full frames before CRC stripping.

Dependencies and integration: depends on CRC helpers, IEEE header parsing, LLSEC, scan/association handlers in `scan.c`, netif receive, tasklets, RCU interface lists, and workqueues initialized by `main.c`.

Risks and test signals: queued beacon/MAC lists are manipulated without an explicit local lock in this file, so single-threaded `mac_wq` assumptions matter. Decryption occurs before monitor-safe header rewriting, noted by TODO. Test signals include bad FCS drop, filtering by PAN/address, scan-only beacon acceptance, MAC command dispatch, and stats increments only on accepted frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/scan.c -->
# sources/distributed-fs/ceph-client/net/mac802154/scan.c

Purpose: implements IEEE 802.15.4 scanning, beacon transmission, association, association response handling, and disassociation management.

Important APIs and functions: `mac802154_trigger_scan_locked()`, `mac802154_abort_scan_locked()`, and `mac802154_scan_worker()` manage active/passive scans. `mac802154_process_beacon()` reports scan events. `mac802154_send_beacons_locked()`/`mac802154_stop_beacons_locked()` and `mac802154_beacon_worker()` handle coordinator beaconing. Association functions include `mac802154_perform_association()`, `mac802154_process_association_resp()`, `mac802154_process_association_req()`, `mac802154_send_disassociation_notif()`, and `mac802154_process_disassociation_notif()`.

Control flow and state: scans store an RCU `scan_req`, set `IEEE802154_IS_SCANNING`, hold/sync the TX queue, switch channels with receiver stopped, optionally transmit beacon requests, wait per-channel duration, then cleanup restores channel, filtering, driver state, and queue. Beaconing stores an RCU `beacon_req`, builds a beacon template, sends once or periodically depending on interval. Association blocks on `assoc_done`, uses `local->assoc_dev/status/addr`, and mutates `wpan_dev->parent`/children under `association_lock`.

Dependencies and integration: driven by cfg802154 ops, RX beacon/MAC-command workers in `rx.c`, MLME TX helpers in `tx.c`, driver channel/start/stop hooks, nl802154 notifications, and cfg802154 address allocation/relationship helpers.

Risks and test signals: scan cleanup interleaves delayed work cancellation, RCU pointer replacement, driver restart, and queue release; abort/completion races are important. Association code contains a likely bug pattern: after an unsuccessful association response, it sets `ret = 0` unconditionally before returning, which can mask PAN-at-capacity/access-denied errors. Tests should cover scan abort during channel switch, active scan beacon request failures, beacon request response behavior, association timeout/negative status, retransmitted association requests, and disassociation of parent vs child.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/trace.c -->
# sources/distributed-fs/ceph-client/net/mac802154/trace.c

Purpose: instantiates mac802154 tracepoints defined in `trace.h`.

Important APIs and functions: defines `CREATE_TRACE_POINTS` after including cfg802154 and driver ops headers, causing tracepoint storage and registration code to be emitted for the header declarations.

Control flow and state: no runtime logic beyond tracepoint instantiation; guarded by `#ifndef __CHECKER__`.

Dependencies and integration: depends on `trace.h`, `driver-ops.h`, and kernel ftrace/tracepoint infrastructure. Build placement must ensure this file is compiled exactly once for the trace system.

Risks and test signals: duplicate inclusion or missing compilation would break tracepoint symbols. Build/link tests and enabling mac802154 trace events are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/trace.h -->
# sources/distributed-fs/ceph-client/net/mac802154/trace.h

Purpose: declares trace events for mac802154 driver callbacks and scan notifications.

Important APIs and functions: event classes and events include driver return traces, start/stop, channel, CCA, TX power, LBT, short/PAN/extended address, PAN coordinator, CSMA params, frame retries, promiscuous mode, and `802154_scan_event`.

Control flow and state: trace macros capture `wpan_phy_name`, driver parameters, CCA fields, booleans, addresses, and scan coordinator descriptors into trace buffers. It ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` integration.

Dependencies and integration: consumed by driver operation wrappers and `scan.c` (`trace_802154_scan_event`). It depends on kernel tracepoint macros, `net/mac802154.h`, and internal local structures.

Risks and test signals: trace format strings must match captured field types, especially endian-converted addresses. Validation is compile-time trace generation plus runtime ftrace/perf event availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/tx.c -->
# sources/distributed-fs/ceph-client/net/mac802154/tx.c

Purpose: implements mac802154 transmit path, including FCS append, queue serialization, async/sync driver handoff, MLME synchronous transmission helpers, and monitor/subinterface start_xmit functions.

Important APIs and functions: `ieee802154_tx()` is the core transmit helper. `ieee802154_xmit_sync_worker()` handles drivers without async transmit. `ieee802154_sync_queue()`, `ieee802154_sync_and_hold_queue()`, `ieee802154_mlme_tx_locked()`, `ieee802154_mlme_tx()`, and `ieee802154_mlme_tx_one_locked()` provide management-frame synchronization. `ieee802154_subif_start_xmit()` encrypts through LLSEC then transmits.

Control flow and state: TX optionally appends CRC, holds all interface queues, increments `ongoing_txs`, and calls `drv_xmit_async()` or queues sync work. Completion paths in `util.c` release queue/ongoing counters. MLME helpers stop user traffic, wait for outstanding TX, and send control frames under RTNL.

Dependencies and integration: depends on driver ops, LLSEC, netdevice stats, CRC helpers, `util.c` queue primitives, and workqueue setup from `main.c`.

Risks and test signals: queue hold/release and `ongoing_txs` must stay balanced on all driver success/failure paths. Sync fallback uses `local->tx_skb` single storage, so serialization is required. Test async failure, sync failure, encrypted TX failure, tailroom expansion failure, and MLME sends while interface is down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/util.c -->
# sources/distributed-fs/ceph-client/net/mac802154/util.c

Purpose: provides mac802154 queue control, inter-frame-spacing timer completion, transmit completion/error callbacks exported to drivers, device stop, and the private `wpan_phy` identity token.

Important APIs and functions: `ieee802154_hold_queue()`, `ieee802154_release_queue()`, and `ieee802154_disable_queue()` stop/wake/disable all interface queues. `ieee802154_xmit_ifs_timer()` releases queues after SIFS/LIFS. `ieee802154_xmit_complete()`, `ieee802154_xmit_error()`, and `ieee802154_xmit_hw_error()` finish driver TX. `ieee802154_stop_device()` flushes work, cancels timer, and stops the driver.

Control flow and state: `hold_txs` is an atomic nesting counter protected by `queue_lock`; only the transition to/from zero stops or wakes netdev queues. Completion records `local->tx_result`, optionally delays release based on skb length and PHY SIFS/LIFS periods, consumes/frees skb, decrements `ongoing_txs`, and wakes synchronous waiters.

Dependencies and integration: used by `tx.c`, scan/MLME paths, and drivers through exported completion symbols. Requires RCU access to `local->interfaces` and hrtimer support.

Risks and test signals: incorrect completion use by drivers can leak queue holds or wake too early. IFS timing depends on symbol durations configured in `main.c`. Tests should check nested holds, IFS delayed release, error completion, and stop behavior with pending work/timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac802154/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/Kconfig -->
# sources/distributed-fs/ceph-client/net/mctp/Kconfig

Purpose: defines kernel configuration for MCTP core, tests, and optional flow tracking.

Important symbols: `MCTP` is a bool under `NET`. `MCTP_TEST` depends on built-in MCTP and KUnit, defaults with `KUNIT_ALL_TESTS`, and selects `MCTP_FLOWS`. `MCTP_FLOWS` depends on MCTP and selects `SKB_EXTENSIONS`.

Control flow and state: configuration controls whether AF_MCTP core, KUnit tests, and skb extension-backed flow tracking are compiled.

Dependencies and integration: pairs with `net/mctp/Makefile`; tests are included into core C files under `CONFIG_MCTP_TEST`.

Risks and test signals: tests require built-in MCTP (`MCTP=y`) rather than module. `MCTP_FLOWS` changes runtime behavior by attaching key refs to skb extensions, so both enabled and disabled configurations should compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/Makefile -->
# sources/distributed-fs/ceph-client/net/mctp/Makefile

Purpose: builds the MCTP core object and optional test utility object.

Important entries: `obj-$(CONFIG_MCTP) += mctp.o`; `mctp-objs := af_mctp.o device.o route.o neigh.o`; `obj-$(CONFIG_MCTP_TEST) += test/utils.o`.

Control flow and state: links socket, device, route, and neighbour implementation into one MCTP object. Route and socket test sources are included from their production C files when configured, while shared test utilities are separate.

Dependencies and integration: driven by Kconfig. Build correctness depends on include-style KUnit tests resolving static symbols in `af_mctp.c` and `route.c`.

Risks and test signals: changing object composition can break static test access. Build with `CONFIG_MCTP`, `CONFIG_MCTP_TEST`, and module/built-in variants where allowed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/af_mctp.c -->
# sources/distributed-fs/ceph-client/net/mctp/af_mctp.c

Purpose: implements the AF_MCTP datagram socket family, including bind/connect, sendmsg/recvmsg, tag allocation ioctls, socket option for extended addressing, socket hash/unhash, key expiry, and module init/exit.

Important APIs and functions: `mctp_bind()`, `mctp_connect()`, `mctp_sendmsg()`, `mctp_recvmsg()`, `mctp_setsockopt()/getsockopt()`, `mctp_ioctl_alloctag()/droptag()`, `mctp_sk_hash()/unhash()`, `mctp_sk_expire_keys()`, and `mctp_pf_create()`. Module init registers socket family, proto, routes, neighbours, and devices.

Control flow and state: bind records local EID/net/type and optional connected peer, then hashes into per-net bind buckets. Send validates sockaddr/tag bits and capabilities, resolves a route or direct extended address, builds an skb with type byte payload prefix, stores network in `mctp_cb`, and calls `mctp_local_output()`. Recv pulls the type byte and returns base or extended sockaddr metadata. Tag ioctls allocate/drop manual `mctp_sk_key` entries; timers expire automatic keys. Unhash removes binds and all socket keys under net key lock.

Dependencies and integration: depends on route/device/neighbour subsystems, net namespace MCTP state, Linux socket/proto APIs, trace events, capabilities, and KUnit socket tests included when enabled.

Risks and test signals: tag lifetimes involve socket refs, key refs, timers, and device flow refs; cleanup must avoid use-after-free. `sendmsg()` mutates `addr->smctp_network` in the user-provided kernel sockaddr copy. Test signals include bind conflict matrix, connect/bind mismatch, direct extended addressing send/recv, ioctl error paths, key expiry, and module init unwind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/af_mctp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/device.c -->
# sources/distributed-fs/ceph-client/net/mctp/device.c

Purpose: manages MCTP per-netdevice state, local EID addresses, RTNL address operations, link AF attributes, netdevice registration/unregistration, and driver-facing MCTP netdev registration helpers.

Important APIs and functions: `__mctp_dev_get()`, `mctp_dev_get_rtnl()`, `mctp_rtm_newaddr()/deladdr()`, `mctp_dev_hold()/put()`, `mctp_dev_set_key()/release_key()`, `mctp_register_netdev()/unregister_netdev()`, and init/exit for notifier, RTNL AF ops, and address message handlers.

Control flow and state: `mctp_add_dev()` allocates `mctp_dev`, initializes address lock and default net, attaches it to `dev->mctp_ptr` with RCU, and holds the netdevice. Address add/delete updates `mdev->addrs` under spinlock, sends RTNL notifications, and adds/removes local routes. Netdevice notifier auto-registers supported ARPHRD types and unregister removes routes/neighbours before dropping refs.

Dependencies and integration: used by route lookup/output, socket direct addressing, neighbour tables, and physical MCTP drivers. Integrates with RTNL, netdevice notifier, rtnl AF ops (`IFLA_MCTP_NET`, physical binding), and local route management.

Risks and test signals: address array replacement/removal must be safe for readers using `addrs_lock`; `mctp_rtm_deladdr()` memmoves the live array without reallocating. Device unregister relies on RTNL plus RCU/refcounts to protect readers. Tests should cover address add/delete notifications, local route synchronization, device unregister cleanup, and flow release callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/neigh.c -->
# sources/distributed-fs/ceph-client/net/mctp/neigh.c

Purpose: implements the MCTP neighbour table: static EID-to-link-layer-address mappings, RTNL new/delete/get neighbour handlers, lookup for packet output, and per-net namespace initialization.

Important APIs and functions: `mctp_neigh_add()`, `mctp_neigh_remove_dev()`, `mctp_neigh_remove()`, `mctp_rtm_newneigh()/delneigh()/getneigh()`, `mctp_fill_neigh()`, and `mctp_neigh_lookup()`.

Control flow and state: neighbours are stored in `net->mctp.neighbours`, protected by `neigh_lock` for mutation and RCU for lookup/dump. Entries hold an `mctp_dev` ref and are freed by RCU callback. Netlink add validates EID, lladdr presence and length; delete matches device/EID/static source; lookup returns copied hardware address or `-EHOSTUNREACH`.

Dependencies and integration: used by `route.c` output when a route does not carry direct hardware address. Integrates with RTNL neighbour messages and `device.c` unregister cleanup.

Risks and test signals: there are TODOs for immediate RTM_DELNEIGH notifications and richer state. `mctp_neigh_net_exit()` schedules frees without list deletion but net namespace teardown owns the list lifetime. Tests should cover duplicate add, wrong lladdr length, output next-hop lookup, dump filtering, and device unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/neigh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/route.c -->
# sources/distributed-fs/ceph-client/net/mctp/route.c

Purpose: implements MCTP routing, packet receive dispatch, socket bind lookup, tag key management, fragmentation/reassembly, route netlink operations, packet-type registration, and per-net namespace route/key/bind state.

Important APIs and functions: packet input/output centers on `mctp_pkttype_receive()`, `mctp_route_lookup()`, `mctp_dst_input()`, `mctp_dst_output()`, `mctp_local_output()`, and `mctp_do_fragment_route()`. Tag/key functions include `mctp_alloc_local_tag()`, `mctp_lookup_key()`, `mctp_key_add()`, `mctp_key_unref()`, `__mctp_key_done_in()`, and preallocated tag lookup. Route management includes `mctp_route_add/remove`, local route add/remove, netlink parse/populate, and dump helpers.

Control flow and state: input validates MCTP version and source/destination EID classes, sets `mctp_cb` network/interface metadata, resolves local or forwarded route, and dispatches to input/output dst handlers. Socket delivery uses tag keys first, then bind lookup ordered by specificity. Fragmented responses are queued on `key->reasm_head` with sequence validation and 64 KiB max; EOM queues the assembled skb and invalidates automatic keys. Output allocates or reuses local tags, pushes MCTP header, fragments by MTU, copies skb extensions, resolves neighbours/direct hardware addresses, and transmits. Routes are simple per-net RCU lists with direct or gateway entries; gateway lookup follows up to 32 hops while clamping MTU and requiring a source EID for non-first-hop gatewaying.

Dependencies and integration: interacts with AF_MCTP sockets, `device.c` local EIDs and dev refs, `neigh.c` link-layer resolution, netlink route APIs, packet type registration, skb extensions when `CONFIG_MCTP_FLOWS`, and KUnit static stubs/tests.

Risks and test signals: key locking order (`keys_lock` before key lock) and ref accounting are critical. Reassembly must unshare cloned starts and clean all fragments on errors. Gateway loops rely on depth cap rather than visited-set detection. Net namespace exit iterates routes under RCU and releases refs. Existing KUnit tests cover fragmentation boundaries, invalid RX, socket delivery/reassembly/key matching, multiple networks, delivery failure cleanup, cloned fragments, null EID receive, flow extensions, key creation, extended address metadata, gateway lookup/loop/MTU, neighbour-based output, bind lookup precedence, and no-local-EID output cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/route-test.c -->
# sources/distributed-fs/ceph-client/net/mctp/test/route-test.c

Purpose: KUnit suite for `route.c`, compiled into the route implementation to exercise static helpers and packet lifecycle behavior.

Important tests and helpers: parameterized tests cover `mctp_do_fragment_route()`, packet type RX routing, socket input matching, reassembly sequences, key lookup, gateway MTU, and bind lookup. Direct tests cover delivery failure cleanup, cloned fragment reassembly, null-EID input, flow extension propagation, output key creation, extended-address input metadata, gateway lookup/loop/output, and output without local EIDs.

Control flow and state: tests create synthetic MCTP netdevices/routes/sockets through `utils.c`, construct skbs with specific headers, feed them to static route functions, then inspect socket queues, device TX queues, skb refs, flow extensions, route lookup results, and generated link-layer headers.

Dependencies and integration: included from `route.c` under `CONFIG_MCTP_TEST`, uses KUnit, static stubs, shared `utils.h`, and init-net MCTP state. `CONFIG_MCTP_TEST` selects flows, but the file still provides skip stubs when flow support is absent.

Risks and test signals: tests assume prior cases clean global key lists and bind tables; failures can cascade. They are strong behavioral signals for route/tag/reassembly regressions, especially memory ownership and network namespace matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/route-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/sock-test.c -->
# sources/distributed-fs/ceph-client/net/mctp/test/sock-test.c

Purpose: KUnit suite for AF_MCTP socket behavior, compiled into `af_mctp.c` to reach static socket functions.

Important tests and helpers: `mctp_test_sock_sendmsg_extaddr()` stubs `mctp_local_output()` and verifies direct hardware addressing from `sockaddr_mctp_ext`. `mctp_test_sock_recvmsg_extaddr()` verifies extended receive sockaddr metadata. Parameterized bind tests assert conflict rules across local address, network, type, and connected peer. `mctp_test_bind_invalid()` checks bind/connect network mismatch.

Control flow and state: tests create kernel sockets, configure test devices/routes, manipulate `mctp_sock.addr_ext`, call `mctp_sendmsg()`/`mctp_recvmsg()` or `kernel_bind()`, and assert returned lengths/errors and socket address fields.

Dependencies and integration: included from `af_mctp.c` under `CONFIG_MCTP_TEST`; uses `utils.c`, KUnit static stubs, kernel socket APIs, and init-net default network.

Risks and test signals: bind tests rely on cleanup through `sock_release()` and default net being 1. They provide direct coverage for user-visible socket ABI validation and conflict behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/sock-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/utils.c -->
# sources/distributed-fs/ceph-client/net/mctp/test/utils.c

Purpose: shared KUnit infrastructure for MCTP route and socket tests, creating synthetic netdevices, routes, destinations, skbs, and bind scenarios.

Important APIs and functions: `mctp_test_create_dev*()` register ARPHRD_MCTP netdevices and retrieve `mctp_dev`. `mctp_test_destroy_dev()` unregisters and frees queued packets. `mctp_test_create_route_direct/gw()` insert test routes. `mctp_test_dst_setup()` builds a referenced `mctp_dst`. `mctp_test_create_skb*()` build packets. `mctp_test_bind_run()` creates sockets, optional connects, and binds.

Control flow and state: test netdev transmit queues outgoing skbs to `dev->pkts`. Routes are inserted directly into `net->mctp.routes` with test output that calls `dev_direct_xmit()`. Device setup can assign local EIDs and link-layer addresses. Destroy helpers assert route ref balance.

Dependencies and integration: used by both KUnit suites; relies on real MCTP device notifier registration, netdevice registration, RTNL, KUnit assertions, and init-net state.

Risks and test signals: helpers manipulate global route lists directly and require disciplined cleanup. They are not production code, but failures often indicate lifetime/refcount regressions in MCTP core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/utils.h -->
# sources/distributed-fs/ceph-client/net/mctp/test/utils.h

Purpose: declares shared MCTP KUnit test fixtures, constants, setup descriptors, and helper APIs.

Important types and APIs: `MCTP_DEV_TEST_MTU`, `struct mctp_test_dev`, `struct mctp_test_route`, and `struct mctp_test_bind_setup` describe test devices/routes/binds. Function declarations cover device creation/destruction, route creation/destruction, destination setup, skb creation, skb device tagging, and bind execution.

Control flow and state: the header defines the common state contract used by `route-test.c` and `sock-test.c`; test devices hold a real `net_device`, referenced `mctp_dev`, optional lladdr, and TX skb queue.

Dependencies and integration: includes MCTP core/device headers and KUnit. It is test-only and compiled with `CONFIG_MCTP_TEST`.

Risks and test signals: helper contracts must match production struct visibility. Changes to `mctp_route`, `mctp_dst`, or socket bind semantics often require synchronized test utility updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mctp/test/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/Kconfig -->
# sources/distributed-fs/ceph-client/net/mpls/Kconfig

Purpose: defines configuration options for MPLS core support, GSO helper, routing, and IP-over-MPLS tunnel support.

Important symbols: `MPLS` is the top-level bool. `NET_MPLS_GSO` enables segmentation support for MPLS-stacked GSO packets. `MPLS_ROUTING` depends on `PROC_SYSCTL` and compatible IP tunnel configuration. `MPLS_IPTUNNEL` depends on `LWTUNNEL` and `MPLS_ROUTING`.

Control flow and state: options gate compilation of MPLS data-plane and sysctl/netlink components in the Makefile.

Dependencies and integration: pairs with `net/mpls/Makefile`, routing implementation, GSO helper, and lightweight tunnel integration.

Risks and test signals: dependency expressions control valid build matrices; test modular and built-in combinations for routing/tunnel/GSO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/Makefile -->
# sources/distributed-fs/ceph-client/net/mpls/Makefile

Purpose: maps MPLS Kconfig symbols to build objects.

Important entries: `obj-$(CONFIG_NET_MPLS_GSO) += mpls_gso.o`, `obj-$(CONFIG_MPLS_ROUTING) += mpls_router.o`, `obj-$(CONFIG_MPLS_IPTUNNEL) += mpls_iptunnel.o`, and `mpls_router-y := af_mpls.o`.

Control flow and state: when routing is enabled, `af_mpls.o` is linked as `mpls_router`. Optional tunnel and GSO helpers build independently according to their symbols.

Dependencies and integration: driven by `Kconfig`; integrates with kernel net build system and module naming.

Risks and test signals: object naming affects module load names and symbol ownership. Build tests should cover each Kconfig symbol combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mpls/Makefile -->
