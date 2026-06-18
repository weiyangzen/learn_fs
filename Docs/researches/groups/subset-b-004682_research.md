# subset-b-004682 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_core.c

Purpose: Implements the IPvlan data plane shared by normal `ipvlan` and `ipvtap` links. It hashes L3 addresses, dispatches inbound frames from the lower device, handles local slave-to-slave forwarding, routes L3/L3S outbound packets through the lower device namespace, and defers multicast/broadcast fanout through a bounded workqueue backlog.

Important APIs and functions: Exported helpers include `ipvlan_init_secret()`, `ipvlan_count_rx()`, `ipvlan_ht_addr_add()`, `ipvlan_ht_addr_del()`, `ipvlan_find_addr()`, `ipvlan_addr_busy()`, `ipvlan_get_L3_hdr()`, `ipvlan_addr_lookup()`, `ipvlan_queue_xmit()`, and `ipvlan_handle_frame()`. Internal paths split into address hashing (`ipvlan_get_v4_hash()`, IPv6 hash when enabled), L3 header parsing for ARP/IPv4/IPv6/ICMPv6 neighbor solicitation, multicast processing (`ipvlan_multicast_enqueue()`, `ipvlan_process_multicast()`), L2 transmit (`ipvlan_xmit_mode_l2()`), L3 transmit (`ipvlan_xmit_mode_l3()`), and lower-device receive handlers for L2/L3.

Control flow: transmit starts in `ipvlan_queue_xmit()` and switches on port mode. L2 mode can deliver locally when source and destination MAC indicate another local IPvlan, enqueue multicast for fanout and lower-device transmit, or send directly on the physical device. L3/L3S mode parses the L3 header, optionally delivers to a local IPvlan unless private/VEPA rules block it, then strips pseudo-L2 framing and calls IPv4 or IPv6 local output with a fresh route lookup. Receive starts in `ipvlan_handle_frame()` under the lower device RX handler. L2 mode passes loopback/nonlocal traffic, performs L3 lookup for unicast, and clones external multicast into the deferred backlog; L3 mode only looks up by destination L3 address.

State and persistence: `ipvlan_jhash_secret` salts address and multicast filter hashes. Persistent runtime state lives in `struct ipvl_port`: the RCU-protected address hash table, slave list, multicast backlog, mode/flags, and lower-device reference. Per-device counters use `struct ipvl_pcpu_stats` with `u64_stats_sync`. Address entries are added/removed by `ipvlan_main.c` notifiers and freed through RCU.

Dependencies and integration: Depends on Linux netdevice RX handlers, RCU lists, workqueues, skb cloning/scrubbing, IPv4/IPv6 route output, ARP/ND parsing, per-CPU stats, and constants/types from `ipvlan.h`. It integrates with `ipvlan_main.c` lifecycle and with `ipvlan_l3s.c` for L3S local-input redirection.

Risks and test signals: High-risk paths are skb lifetime during local forwarding, namespace crossing via `skb_scrub_packet()`, multicast backlog overflow, IPv6 DAD neighbor-solicitation lookup, and route-output error accounting. Useful tests include L2 bridge/private/VEPA behavior, L3 local and external IPv4/IPv6 forwarding, ARP and IPv6 DAD delivery, multicast subscription filtering, backlog limit drops, lower-device namespace moves, and CONFIG_IPV6 on/off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_l3s.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_l3s.c

Purpose: Adds IPvlan L3S support, which makes an IPvlan port act as an L3 master device and rewrites local-input packets to the matched IPvlan slave late in netfilter input processing. This mode lets routed traffic arrive on the lower device but be accounted and delivered as the correct IPvlan device.

Important APIs and functions: Public lifecycle hooks are `ipvlan_l3s_init()`, `ipvlan_l3s_cleanup()`, `ipvlan_l3s_register()`, `ipvlan_l3s_unregister()`, and `ipvlan_migrate_l3s_hook()`. Internal helpers are `ipvlan_skb_to_addr()`, `ipvlan_l3_rcv()`, `ipvlan_nf_input()`, `ipvlan_register_nf_hook()`, `ipvlan_unregister_nf_hook()`, and `ipvlan_ns_exit()`. `ipvl_l3mdev_ops` supplies `.l3mdev_l3_rcv`.

Control flow: `ipvlan_l3s_register()` increments a per-netns netfilter hook reference count, installs `l3mdev_ops` on the lower device, and marks `IFF_L3MDEV_RX_HANDLER`. The l3mdev receive callback performs IPv4 or IPv6 input route lookup using the matched IPvlan device. The netfilter hooks run at `NF_INET_LOCAL_IN` with `INT_MAX` priority; when an skb maps to a configured IPvlan address, `ipvlan_nf_input()` changes `skb->dev`, `skb_iif`, and IPv6 control-block input interface, then records successful RX accounting.

State and persistence: State is per network namespace in `struct ipvlan_netns`, storing only `ipvl_nf_hook_refcnt`. The hook is registered once per namespace no matter how many L3S ports exist, and unregistered when the refcount reaches zero. `ipvlan_ns_exit()` defensively warns and unregisters if namespace teardown finds leaked references.

Dependencies and integration: Depends on `ipvlan_core.c` address parsing/lookup and RX accounting, l3mdev operations, IPv4/IPv6 route input helpers, netfilter hook registration, and pernet subsystem registration. `ipvlan_main.c` calls this when mode changes to or from `IPVLAN_MODE_L3S` and when the lower device moves network namespaces.

Risks and test signals: Risks include hook refcount imbalance across mode changes and namespace moves, stale `l3mdev_ops`, incorrect skb input-interface rewrites, and IPv6 conditional build behavior. Test L3S registration/unregistration cycles, multiple ports in one netns, netns migration, local IPv4/IPv6 delivery, IPv6 disabled builds, and namespace exit with active devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_l3s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_main.c

Purpose: Provides IPvlan control-plane and netdevice lifecycle support. It registers the `ipvlan` rtnetlink kind, creates/destroys shared lower-device ports, configures modes and flags, tracks assigned IPv4/IPv6 addresses, mirrors lower-device state, and exposes netdevice, header, ethtool, and notifier operations.

Important APIs and functions: Exported helpers are `ipvlan_link_new()`, `ipvlan_link_delete()`, `ipvlan_link_setup()`, and `ipvlan_link_register()` for reuse by `ipvtap.c`. Core lifecycle routines include `ipvlan_port_create()`, `ipvlan_port_destroy()`, `ipvlan_init()`, `ipvlan_uninit()`, `ipvlan_open()`, `ipvlan_stop()`, `ipvlan_start_xmit()`, `ipvlan_fix_features()`, `ipvlan_nl_changelink()`, `ipvlan_nl_validate()`, `ipvlan_device_event()`, and address notifier handlers for IPv4 and IPv6. `ipvlan_set_port_mode()` coordinates L2/L3/L3S transitions.

Control flow: newlink resolves `IFLA_LINK`, unwraps nested IPvlan devices to the real lower device, rejects loopback/non-Ethernet or busy RX-handler devices, registers the virtual netdevice, allocates a unique `dev_id`, links the IPvlan as an upper, applies mode/flags, and appends it to the port's RCU slave list. Device open publishes already-known addresses into the shared hash; stop removes them and unsyncs multicast/unicast filters. Address notifiers validate duplicate assignments and add/delete `struct ipvl_addr` records under `addrs_lock`. Lower-device notifiers propagate carrier/features/MTU/MAC changes, kill slaves on lower unregister, and migrate L3S hooks on namespace moves.

State and persistence: `struct ipvl_port` is allocated per lower device and persists while `port->count` is nonzero. It holds mode, private/VEPA flags, the address hash, slave list, multicast backlog, IDA for slave `dev_id`s, and lower-device netns pointer. Each `struct ipvl_dev` stores physical device, virtual device, feature mask, address list, and per-CPU stats. State is runtime-only and rebuilt from netlink/address configuration.

Dependencies and integration: Uses rtnetlink link ops, netdevice upper/lower relationships, RX-handler registration from `ipvlan_core.c`, inet/inet6 address notifier chains, VLAN filter forwarding, ethtool delegation, and optional L3S hooks. `ipvtap.c` calls the common setup/newlink/delete/register helpers.

Risks and test signals: Key risks are rollback after partially registered devices, mode-change flag rollback, duplicate address validation under RCU/spinlock, lower-device unregister ordering, IDA reuse, and feature inheritance with tap-updated software features. Test create/delete chains, invalid lower links, nested IPvlan creation, mode and flag changes, L3S transitions, IPv4/IPv6 duplicate address rejection, MTU/features/MAC propagation, and module init error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvlan_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvtap.c -->
# sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvtap.c

Purpose: Implements `ipvtap`, a tap character-device frontend layered on IPvlan. It creates rtnetlink `ipvtap` netdevices that use IPvlan forwarding semantics while exposing `/dev` tap queues for userspace packet I/O.

Important APIs and functions: `struct ipvtap_dev` embeds `struct ipvl_dev` and `struct tap_dev`, so the same private allocation supports both IPvlan and tap state. `ipvtap_newlink()` initializes tap queues and callbacks, registers `tap_handle_frame()` as the device RX handler, then delegates link creation to `ipvlan_link_new()`. `ipvtap_dellink()` unregisters the tap RX handler, deletes tap queues, and calls `ipvlan_link_delete()`. `ipvtap_device_event()` creates/destroys tap class devices and sysfs links and resizes queues. Module init/exit uses `tap_create_cdev()`, `class_register()`, netdevice notifiers, and `ipvlan_link_register()`.

Control flow: newlink sets `tap_features` to common tun offloads, wires drop-accounting and feature-update callbacks back into the embedded IPvlan stats/features, and ensures no failing operation is performed after `ipvlan_link_new()` succeeds. On `NETDEV_REGISTER`, the notifier allocates a tap minor, creates a namespaced class device named `tap<ifindex>`, and links it under the netdevice kobject. On unregister it removes the sysfs link, destroys the class device, and frees the minor. Queue length changes call `tap_queue_resize()`.

State and persistence: Persistent runtime state is the embedded `tap_dev` queue list, minor number, and tap feature mask plus the IPvlan state managed by `ipvlan_main.c`. Global module state includes `ipvtap_major`, `ipvtap_cdev`, and the `ipvtap_class`. Device nodes and sysfs links exist only while the netdevice is registered.

Dependencies and integration: Depends on the tap core (`if_tap.h`), IPvlan exported link helpers, netdevice notifier chain, class/cdev infrastructure, network namespace class support, and tun/virtio offload flags.

Risks and test signals: Risks include leaked tap minors if sysfs link creation fails after `device_create()`, RX-handler ordering with IPvlan setup, queue resize failures reported as notifier errors, and callback accounting correctness. Test module init rollback, link create/delete, `/dev/tapX` creation in netns, queue open/close and resize, tap feature updates changing IPvlan features, and traffic/drop stats through userspace tap queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ipvlan/ipvtap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/loopback.c -->
# sources/distributed-fs/ceph-client/drivers/net/loopback.c

Purpose: Implements the per-network-namespace loopback netdevice and the global `blackhole_netdev` used for expired or discard destinations. Loopback reinjects transmitted packets into receive processing with local statistics, while blackhole drops packets through transmit and neighbor output paths.

Important APIs and functions: `loopback_xmit()` timestamps, scrubs, forces dst references, converts Ethernet protocol metadata, and calls `__netif_rx()`. `dev_lstats_read()` is exported for reading per-CPU lightweight stats. `loopback_get_stats64()` mirrors loopback RX and TX counters from the same local stats. `gen_lo_setup()` initializes common loopback-like device fields and is reused for `blackhole_netdev_setup()`. `loopback_net_init()` allocates and registers one `lo` device per net namespace. `blackhole_netdev_init()` allocates and activates the global dummy discard device.

Control flow: pernet init allocates `lo` with predictable name, binds it to the namespace, registers it, verifies `LOOPBACK_IFINDEX`, and stores it as `net->loopback_dev`; init-net failure panics because networking cannot proceed without loopback. Transmit uses `NETDEV_TX_OK` regardless of upper-layer reinjection result, with stats incremented only on successful receive enqueue. The blackhole device is initialized at `device_initcall`, scheduler-activated under the init-net RTNL lock, and marked up/running without normal registration.

State and persistence: Loopback stats use `NETDEV_PCPU_STAT_LSTATS` and are read with `u64_stats_fetch_begin/retry`. `loopback_dev_free()` clears the namespace's loopback pointer. `blackhole_netdev` is a global exported pointer, not per namespace, and intentionally persists for the boot lifetime.

Dependencies and integration: Uses core netdevice allocation/registration, pernet operations registered from `net/core/dev.c`, skb timestamp/dst helpers, Ethernet header ops, ethtool timestamp info, scheduler activation, and neighbor output hooks.

Risks and test signals: Risks are fundamental networking boot failure, incorrect skb timestamp/dst handling before reinjection, stats races, and the unusual manually activated blackhole device lifecycle. Test namespace creation/destruction, loopback traffic counters, packet timestamp clearing, dst ref behavior, init-net failure handling where injectable, and blackhole route/neighbour drops with ratelimited warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/loopback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/macsec.c -->
# sources/distributed-fs/ceph-client/drivers/net/macsec.c

Purpose: Implements the software and offload control plane for IEEE 802.1AE MACsec netdevices. It creates MACsec upper devices over Ethernet lower devices, encrypts/protects transmit frames, validates/decrypts receive frames, manages SecY/Secure Channel/Secure Association state via rtnetlink and generic netlink, exposes statistics, and coordinates MAC/PHY hardware offload callbacks.

Important APIs and types: Private state is `struct macsec_dev`, embedding `struct macsec_secy`, lower `real_dev`, per-CPU SecY stats, GRO cells, offload mode, and TX-tag requirements. `struct macsec_rxh_data` hangs a list of SecYs off the lower device RX handler. Packet helpers include `macsec_fill_sectag()`, `macsec_validate_skb()`, IV builders for normal and XPN ciphers, `macsec_encrypt()`, `macsec_decrypt()`, `macsec_post_decrypt()`, and `macsec_handle_frame()`. Control-plane functions add/delete/update RXSC, RXSA, TXSA, offload mode, and SecY settings. Exported helpers are `macsec_pn_wrapped()`, `macsec_get_real_dev()`, and `macsec_netdev_is_offloaded()`.

Control flow: transmit enters `macsec_start_xmit()`. Offloaded devices attach MACsec metadata and optionally insert a PHY TX tag before sending on the lower device. Software devices either pass unprotected frames when `protect_frames` is false, drop when not operational, or add SecTAG/ICV space, reserve/update PN, build AEAD scatterlists, encrypt or authenticate, and queue to the lower device. Receive is installed as the lower device RX handler. Plaintext frames are delivered or dropped based on validation/offload metadata. MACsec frames are parsed for SecTAG/SCI/AN, matched to RXSC/RXSA under RCU, replay-checked before and after AEAD validation, stripped back to the original Ethernet frame, and delivered through GRO cells.

State and persistence: Runtime state is in SecY configuration, TX/RX SC lists, per-association SAs with AEAD transforms, key IDs, salts/SSCI, next PN counters, active flags, RCU/refcounts, and per-CPU stats. `macsec_generation` tracks dump consistency. Keys are not persisted by this file; they live in kernel memory until SA deletion/device teardown, then crypto transforms and per-CPU stats are freed via RCU work on `macsec_wq`.

Dependencies and integration: Depends on AEAD `gcm(aes)`, rtnetlink `macsec` link ops, generic-netlink `MACSEC_GENL_NAME`, netdevice upper/lower links, RX handlers, GRO cells, metadata dst for offload, VLAN filter synchronization, PHY and MAC `macsec_ops`, notifier propagation from lower devices, and UAPI definitions in `if_macsec.h`.

Risks and test signals: High-risk areas are PN wrap and XPN half recovery, replay-window checks, async crypto lifetime and skb ownership, offload rollback, lower-device unregister teardown, duplicate SCI detection, SecTAG length validation, and stats consistency. Test software encrypt/authenticate and validate-only modes, strict/check/disabled validation, no-SCI and unknown-SCI behavior, RX/TX SA add/update/delete with active restrictions, PN wrap disabling operational state, XPN salt/SSCI handling, offload enable/disable refusal when running or configured, lower MTU/feature changes, and MAC/PHY offload callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/macsec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/macvlan.c -->
# sources/distributed-fs/ceph-client/drivers/net/macvlan.c

Purpose: Implements MAC address based virtual Ethernet devices over a lower Ethernet device. It provides L2 forwarding for private, VEPA, bridge, passthru, and source modes; multicast/broadcast filtering and deferred fanout; source-MAC filters; netdevice operations; rtnetlink configuration; and lower-device notifier integration.

Important APIs and functions: Shared exports for `macvtap` are `macvlan_common_setup()`, `macvlan_common_newlink()`, `macvlan_dellink()`, and `macvlan_link_register()`. Core data types are `struct macvlan_port`, `struct macvlan_source_entry`, and embedded `struct macvlan_dev` from headers. Major functions include `macvlan_handle_frame()`, `macvlan_queue_xmit()`, `macvlan_broadcast_enqueue()`, `macvlan_process_broadcast()`, `macvlan_open()`, `macvlan_stop()`, `macvlan_sync_address()`, `macvlan_changelink_sources()`, `macvlan_changelink()`, and `macvlan_device_event()`.

Control flow: RX handler first handles multicast/broadcast: defrag when needed, source-mode forwarding, source lookup, deferred broadcast queue, or immediate multicast fanout based on filters. Unicast can be diverted by source-mode entries, delivered to the passthru device, looked up by destination MAC, or passed to the lower stack. TX in bridge mode can deliver local bridge peers directly or broadcast to local bridge peers, then otherwise sends via the lower device with possible accelerated station context. Newlink resolves the lower device, creates a port/RX handler if needed, enforces passthru exclusivity, configures source-mode MAC lists and broadcast queue settings, registers the netdevice, links upper/lower devices, and adds the vlan to the port list.

State and persistence: `struct macvlan_port` persists per lower device while children exist and holds MAC hash tables, source hash table, child list, broadcast queue/work, filter bitmaps, passthru/address-change flags, lower permanent address, and child count. Per-MACVLAN state includes mode, flags, lowerdev pointer, per-CPU stats, requested broadcast queue length, source address count, and optional direct-forward/offload or netpoll state. All state is runtime and configured through rtnetlink/FDB operations.

Dependencies and integration: Uses netdevice RX handlers, RCU hash/list traversal, lower-device unicast/multicast/promisc synchronization, VLAN filter forwarding, ethtool and timestamp delegation, netpoll, direct forwarding offload hooks, rtnetlink policies, and notifier chains. `macvtap.c` reuses the common setup/newlink/delete/register path.

Risks and test signals: Risks include RCU lifetime around broadcast/source entries, passthru lower-MAC restoration, multicast queue overflow, source-mode `NODST` consumption, FDB restrictions, lower-device unregister ordering, and hardware L2 forwarding fallback. Test all modes, passthru exclusivity and MAC changes, source MAC add/delete/flush/set, broadcast queue length/cutoff filters, multicast subscriptions, lower MTU/features/MAC changes, netpoll builds, FDB operations, and error rollback from newlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/macvlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/macvtap.c -->
# sources/distributed-fs/ceph-client/drivers/net/macvtap.c

Purpose: Implements `macvtap`, a tap character-device frontend for MACVLAN. It lets userspace open tap queues for a MACVLAN-like virtual device while preserving MACVLAN forwarding modes and lower-device integration.

Important APIs and functions: `struct macvtap_dev` embeds `struct macvlan_dev` and `struct tap_dev`. `macvtap_newlink()` initializes the tap queue list, offload feature mask, and accounting/feature callbacks, registers `tap_handle_frame()` as the MACVTAP device RX handler, and delegates creation to `macvlan_common_newlink()`. `macvtap_dellink()` unregisters the tap RX handler, deletes tap queues, and calls `macvlan_dellink()`. `macvtap_device_event()` owns tap minor allocation, class device creation/destruction, sysfs links, and queue resizing.

Control flow: module init creates the tap cdev, registers the namespaced class, registers the netdevice notifier, then registers a `macvtap` rtnetlink kind through `macvlan_link_register()` so it inherits MACVLAN validation/fill/changelink behavior. Netdevice registration events create `/dev` nodes named `tap<ifindex>` before register_netdevice completes. Unregister events reverse sysfs/device/minor state, and TX queue length changes resize tap queues.

State and persistence: Global state is `macvtap_major`, `macvtap_cdev`, and `macvtap_class`. Per-device state is the embedded tap queue/minor state plus embedded MACVLAN state. The character device and sysfs link are runtime artifacts tied to the netdevice lifetime.

Dependencies and integration: Depends on the tap core, MACVLAN exported helpers, network namespace class support, cdev/class/device APIs, netdevice notifier chain, tun/virtio offload flags, and rtnetlink.

Risks and test signals: Risks are minor/class-device leaks on partial notifier failures, ordering between tap RX handler and MACVLAN creation, feature update propagation to `vlan->set_features`, and queue resize errors. Test module init rollback, create/delete in multiple namespaces, device-node/sysfs lifetime, userspace tap queue open/close and traffic, feature negotiation, and lower MACVLAN mode behavior through macvtap links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/macvtap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/Kconfig

Purpose: Defines Kconfig options for MCTP transport device drivers under the `if MCTP` menu. It exposes serial, SMBus/I2C, I3C, and USB transports plus a KUnit test option for the serial binding.

Important options: `MCTP_SERIAL` is a tristate line-discipline transport depending on `TTY` and selecting `CRC_CCITT`; its module name is `mctp-serial`. `MCTP_SERIAL_TEST` is a bool enabled by `KUNIT_ALL_TESTS` when serial is built-in with KUnit. `MCTP_TRANSPORT_I2C` is a tristate SMBus/I2C binding depending on `I2C`, `I2C_SLAVE`, and `I2C_MUX || !I2C_MUX`, and selects `MCTP_FLOWS`. `MCTP_TRANSPORT_I3C` depends on `I3C`. `MCTP_TRANSPORT_USB` depends on `USB`.

Control flow and integration: Kconfig does not execute runtime code; it controls which transport objects the Makefile builds. The outer `if MCTP` ensures the menu is visible only when the MCTP core is enabled. Help text documents the DMTF binding specifications and expected netdevice creation model for each bus.

State and persistence: The file contributes build-time configuration state only. Selected tristates determine built-in versus module artifacts, and dependencies prevent impossible combinations such as I2C transport without I2C slave support.

Dependencies and risks: The I2C mux dependency is intentionally shaped so the transport cannot be built-in when `i2c-mux` is modular. Risks are dependency drift with core bus APIs, stale help text/module names, and missing test coverage for modular/built-in combinations.

Test signals: Build matrix coverage should include MCTP disabled, each transport as built-in/module where legal, `MCTP_SERIAL_TEST` under KUnit, I2C mux built-in/module permutations, and all transports together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/Makefile

Purpose: Maps MCTP transport Kconfig symbols to object files for kbuild.

Important entries: `CONFIG_MCTP_SERIAL` builds `mctp-serial.o`, `CONFIG_MCTP_TRANSPORT_I2C` builds `mctp-i2c.o`, `CONFIG_MCTP_TRANSPORT_I3C` builds `mctp-i3c.o`, and `CONFIG_MCTP_TRANSPORT_USB` builds `mctp-usb.o`.

Control flow and integration: kbuild evaluates each `obj-$(CONFIG_...)` line and links the object into the kernel when the symbol is `y` or builds a module when the symbol is `m`. The symbols are defined in the adjacent `Kconfig`, so this file is the final build integration for the transport drivers.

State and persistence: There is no runtime state. The Makefile only persists the source-to-object mapping used by kernel builds.

Risks and test signals: Risks are symbol/object name drift, missing objects after adding Kconfig options, or module naming surprises. Test by building each transport as built-in and module where dependencies permit and confirming the expected object/module names are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/Makefile -->
