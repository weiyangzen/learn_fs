# Research: subset-b-006195

Grouped research for the HSR/PRP, IEEE 802.15.4, and IEEE 802.15.4 6LoWPAN files listed in work item `subset-b-006195`. Each section preserves the source path in its title and is bounded for reconciliation into the source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_main.h -->
## sources/distributed-fs/ceph-client/net/hsr/hsr_main.h

Purpose: private shared definitions for the HSR/PRP driver. It defines IEC 62439-3 timing constants, HSR/PRP wire structures, core private state, port iteration helpers, protocol-operation hooks, and inline helpers used by frame forwarding, supervision, node registration, netlink, and slave setup code.

Important APIs/types/functions: `struct hsr_priv` is the central per-master object, carrying the RCU-protected port list, node databases, proxy node database, self-node pointer, announce/prune timers, HSR/PRP version, sequence counters, locks, protocol operations, PRP net id, offload and RedBox state, supervision multicast address, and optional debugfs root. `struct hsr_port` links a netdev into an HSR master as master/slave/interlink and stores the original MAC for restoration. `struct hsr_proto_ops` abstracts HSRv0, HSRv1, and PRPv1 differences for supervision, duplicate-drop, tagging, ingress validation, and frame registration. Wire helpers include `set_hsr_tag_path`, `set_hsr_tag_LSDU_size`, `set_hsr_stag_path`, `set_hsr_stag_HSR_ver`, `set_prp_lan_id`, `set_prp_LSDU_size`, `hsr_get_skb_sequence_nr`, `skb_get_PRP_rct`, `prp_get_skb_sequence_nr`, and `prp_check_lsdu_size`.

Control flow and state: this header does not execute large flows itself, but it establishes the data passed between RX handlers, forwarding, frame registration, timers, and netlink. Sequence number state is protected by `seqnr_lock`; node and port lists are RCU/list based with `list_lock` for node mutations. PRP frame validation relies on the trailer at `skb_tail_pointer(skb) - HSR_HLEN` and checks the suffix against `ETH_P_PRP`.

Dependencies and integration points: depends on Linux netdevice, VLAN, list, if_hsr UAPI, skb, RCU, timers, debugfs, and endian helpers. Its structs are consumed by `hsr_slave.c`, `hsr_netlink.c`, device setup, forwarding, frame registry, and debugfs modules.

Risks: most inline wire helpers assume callers have already validated skb layout and protocol. Miscomputed LSDU size or path bits can break duplicate detection or interop. `skb_get_PRP_rct()` trusts tailroom size; callers must ensure PRP-suffixed skbs are long enough. RCU callers must use the matching port iteration/read-side locking pattern.

Test signals: KUnit PRP duplicate-discard tests exercise sequence-related state derived from these definitions. Runtime validation comes from HSR/PRP link creation, supervision frames, duplicate handling, RedBox/proxy handling, and debugfs/node netlink visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.c -->
## sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.c

Purpose: implements the rtnetlink link type `hsr` and a generic-netlink family named `HSR`. It creates and destroys HSR/PRP master devices, exposes configured slave/interlink/protocol metadata, emits ring/node notifications, and serves node status/list queries from userspace.

Important APIs/types/functions: `hsr_policy` validates rtnl attributes such as `IFLA_HSR_SLAVE1`, `IFLA_HSR_SLAVE2`, `IFLA_HSR_INTERLINK`, `IFLA_HSR_VERSION`, and `IFLA_HSR_PROTOCOL`. `hsr_newlink()` resolves slave devices in the target namespace, validates they differ, handles optional interlink, maps `HSR_PROTOCOL_PRP` to `PRP_V1`, rejects PRP+interlink, and calls `hsr_dev_finalize()`. `hsr_dellink()` synchronously deletes timers, tears down debugfs, ports, self-node, node tables, and queues unregister. `hsr_fill_info()` reports slave/interlink ifindexes, supervision address, sequence number, version, and protocol. Generic-netlink operations include `hsr_nl_ringerror()`, `hsr_nl_nodedown()`, `hsr_get_node_status()`, and `hsr_get_node_list()`.

Control flow and state: link creation is RTNL-driven and depends on already allocated netdev private storage. Deletion stops timers before freeing state that timer callbacks may reference. Node queries take `rcu_read_lock()`, find the master by ifindex, allocate a reply skb, pull data from `hsr_get_node_data()` or `hsr_get_next_node()`, then unicast replies. Node-list dump restarts with a preserved position when an skb fills.

Dependencies and integration points: integrates with `rtnl_link_ops`, `genl_family`, `hsr_device`, `hsr_framereg`, debugfs helpers, node database helpers, and UAPI `hsr_netlink.h`. Notifications use multicast group `hsr-network`.

Risks: several notification paths allocate with `GFP_ATOMIC` and only warn on failure, so userspace observability is best-effort. `hsr_get_node_status()` and `hsr_get_node_list()` return netlink acks with `-EINVAL` but otherwise often return `0`, matching legacy generic-netlink behavior but making caller-side diagnostics coarse. Correct RCU lifetime depends on keeping all netdev/node lookups inside the read-side section.

Test signals: create/delete `ip link add type hsr` variants, PRP creation rejection cases, `ip -d link show`, and generic-netlink node status/list queries. Ring-error/node-down paths need fault or topology tests because they are asynchronous notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.h -->
## sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.h

Purpose: public-in-driver declarations for the HSR/PRP netlink integration. It keeps module init/exit and asynchronous node notification APIs visible to the rest of the HSR code without exposing netlink implementation details.

Important APIs/types/functions: declares `hsr_netlink_init()` and `hsr_netlink_exit()` for module registration/unregistration of rtnl and generic-netlink families. Declares `hsr_nl_ringerror(struct hsr_priv *hsr, unsigned char addr[ETH_ALEN], struct hsr_port *port)` for notifying userspace when traffic for a node is seen only through one slave, and `hsr_nl_nodedown(struct hsr_priv *hsr, unsigned char addr[ETH_ALEN])` for notifying when a node ages out. Forward declarations of `struct hsr_priv` and `struct hsr_port` avoid heavy include coupling.

Control flow and state: this header carries no state and has no runtime control flow. Its functions operate on live `hsr_priv`/`hsr_port` objects owned by the HSR master and node database. Callers are expected to respect the locking context of the notification emitters; the implementation allocates atomic skbs and performs RCU lookup of the master for warning paths.

Dependencies and integration points: includes `linux/if_ether.h` for `ETH_ALEN`, `linux/module.h`, and UAPI `linux/hsr_netlink.h` for command/attribute constants. It is included by `hsr_netlink.c` and by HSR code that emits topology notifications.

Risks: the notification APIs take raw MAC buffers and object pointers, so stale object lifetime or wrong locking in callers can produce invalid reports. No compile-time constraint says the passed `port` belongs to `hsr`, so callers must maintain that invariant.

Test signals: build coverage checks prototypes and UAPI availability. Runtime signals are userspace reception of ring error and node-down multicast events during HSR topology failure/aging tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_slave.c -->
## sources/distributed-fs/ceph-client/net/hsr/hsr_slave.c

Purpose: manages HSR/PRP slave/interlink ports and the RX handler installed on lower devices. It validates candidate netdevices, registers/unregisters the receive hook, links slaves under the HSR master, updates MTU/features, and forwards accepted frames into the HSR forwarding engine.

Important APIs/types/functions: `hsr_handle_frame()` is the registered `rx_handler`. It drops loopback/self-originated frames, rejects invalid DAN ingress protocols through `proto_ops->invalid_dan_ingress_frame`, prepares MAC/network headers for HSR/PRP, then calls `hsr_forward_skb()`, with `seqnr_lock` held for interlink ingress. `hsr_invalid_dan_ingress_frame()` accepts only HSR/PRP protocols for DAN ingress. `hsr_port_exists()`, `hsr_add_port()`, and `hsr_del_port()` are the external port-management API. Internals include `hsr_check_dev_ok()` and `hsr_portdev_setup()`.

Control flow and state: add-port allocates `struct hsr_port`, records original MAC, appends to the RCU port list, then for non-master ports sets promiscuity when forwarding is not offloaded, links the lower device as an upper/lower relationship, installs the RX handler, disables LRO, and updates master features/MTU. Deletion removes the RCU list entry, unregisters RX handler, reverses promiscuity and upper links, restores PRP slave B MAC when needed, and frees by `kfree_rcu()`.

Dependencies and integration points: depends on netdevice RX handlers, RTNL upper-device links, LAG upper info, VLAN checks, `hsr_device`, `hsr_forward`, and frame registry helpers. Offload is signaled by `NETIF_F_HW_HSR_TAG_RM` and `hsr->fwd_offloaded`.

Risks: skb manipulation assumes MAC header validity after explicit checks; malformed or short packets must be rejected before HSR tag access. Promiscuity and upper-device rollback must stay balanced across setup failures. Interlink forwarding serializes sequence allocation with a spinlock, making deadlock and lock ordering important around forwarding paths.

Test signals: enslave rejection tests for loopback, VLAN, existing HSR slaves, HSR masters, and non-bridgeable devices; RX tests for self-frame drop, invalid protocol pass-through, hardware tag removal, PRP SAN frames, and interlink sequence handling; teardown tests for promiscuity and MAC restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_slave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_slave.h -->
## sources/distributed-fs/ceph-client/net/hsr/hsr_slave.h

Purpose: declares the HSR/PRP port-management API and inline helpers for recovering `struct hsr_port` from a slave netdevice under RTNL or RCU protection.

Important APIs/types/functions: declares `hsr_add_port()`, `hsr_del_port()`, `hsr_port_exists()`, and `hsr_invalid_dan_ingress_frame()`. `hsr_port_get_rtnl()` asserts RTNL and returns `rtnl_dereference(dev->rx_handler_data)` only when the device has the HSR RX handler. `hsr_port_get_rcu()` similarly returns `rcu_dereference(dev->rx_handler_data)` for RCU read-side callers. Both helpers rely on `hsr_port_exists()` comparing the registered RX handler to the HSR handler.

Control flow and state: the header does not mutate state. It encodes the core lifetime contract: `rx_handler_data` is meaningful only while the HSR RX handler is installed, and dereference mode must match the caller's lock context.

Dependencies and integration points: includes skb/netdevice/rtnetlink headers and `hsr_main.h`. Used by `hsr_slave.c` and other HSR modules needing to identify slave ownership.

Risks: callers that use `hsr_port_get_rcu()` outside an RCU read-side critical section can race with `hsr_del_port()` and `kfree_rcu()`. `hsr_port_get_rtnl()` must not be called without RTNL. The helper returns `NULL` for non-HSR devices and must be checked.

Test signals: lockdep coverage around RTNL/RCU callers, port add/delete races, and negative lookups on non-HSR netdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_slave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/prp_dup_discard_test.c -->
## sources/distributed-fs/ceph-client/net/hsr/prp_dup_discard_test.c

Purpose: KUnit suite for PRP duplicate-discard behavior implemented in the HSR frame registry. It builds minimal in-memory `hsr_port`, `hsr_frame_info`, and `hsr_node` objects and verifies sequence bitmap behavior for forwarding, duplicates, timeouts, and out-of-order frames.

Important APIs/types/functions: `build_prp_test_data()` allocates test data, configures `node.seq_port_cnt`, allocates `node.block_buf` based on `hsr_seq_block_size()`, initializes the xarray `seq_blocks` and `seq_out_lock`, connects the frame to source node and receive port, and defaults receive port to `HSR_PT_SLAVE_A`. `check_prp_frame_seen()` and `check_prp_frame_unseen()` inspect sequence blocks and bits. Test cases call exported `prp_register_frame_out()`.

Control flow and state: each test constructs isolated state through KUnit allocators. The duplicate-discard state is maintained in per-node sequence blocks indexed by sequence number. Accepted frames set the appropriate bit; duplicate frames on the opposite LAN should return `1`; expired blocks are aged by manually setting `block->time` before a repeat call.

Dependencies and integration points: depends on KUnit and HSR frame registry internals exported for KUnit via `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`. It exercises `hsr_framereg` behavior using definitions from `hsr_main.h`.

Risks: the tests create synthetic objects rather than full netdevices, so they verify frame registry sequencing, not RX handler integration, skb parsing, netlink, or real PRP trailer validation. The timeout test mutates internal block time directly, which is useful but tied to implementation details.

Test signals: suite name `prp_duplicate_discard`; cases cover normal forward, exact duplicate drop, entry timeout clearing old state, out-of-sequence acceptance followed by duplicate drop, and LAN B late duplicate drops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/prp_dup_discard_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/6lowpan_i.h -->
## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/6lowpan_i.h

Purpose: internal header for the IEEE 802.15.4 6LoWPAN module. It shares RX handler result codes, fragmentation dispatch constants, fragment queue key structures, and internal function prototypes across core, RX, TX, and reassembly files.

Important APIs/types/functions: `lowpan_rx_result` is a bitwise result enum with `RX_CONTINUE`, `RX_DROP_UNUSABLE`, `RX_DROP`, and `RX_QUEUED`. `LOWPAN_DISPATCH_FRAG1` and `LOWPAN_DISPATCH_FRAGN` define 6LoWPAN fragment dispatch high bits. `struct frag_lowpan_compare_key` keys reassembly by datagram tag, datagram size, source address, and destination address. `struct lowpan_frag_queue` wraps `struct inet_frag_queue`. Prototypes include `lowpan_frag_rcv()`, frag init/exit, RX init/exit, `lowpan_header_create()`, `lowpan_xmit()`, `lowpan_iphc_decompress()`, and `lowpan_rx_h_ipv6()`.

Control flow and state: this header has no runtime flow but defines the contract between the packet receive path and fragment reassembly. A fragment receiver can return `1` to mean a complete skb is ready, while intermediate fragments are consumed into inet-frag queues.

Dependencies and integration points: includes IEEE 802.15.4 netdevice types, inet fragment infrastructure, and generic 6LoWPAN helpers. It binds the module to the Linux IPv6/6LoWPAN compression stack and per-net frag directories.

Risks: fragment key equality copies full `ieee802154_addr` structs, so address initialization must be deterministic before lookup. Result-code misuse can leak or double-free skbs because each return value encodes ownership.

Test signals: compile-time type checking across all 6LoWPAN files, RX tests for each dispatch path, fragmentation/reassembly tests keyed by tag/addresses, and module load/unload tests for init/exit prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/6lowpan_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Kconfig -->
## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Kconfig

Purpose: Kconfig entry for IPv6 compression over IEEE 802.15.4. It defines `IEEE802154_6LOWPAN` as the configuration switch for building the 802.15.4-specific 6LoWPAN module.

Important APIs/types/functions: the `config IEEE802154_6LOWPAN` symbol is `tristate`, has prompt `6lowpan support over IEEE 802.15.4`, and depends on the generic `6LOWPAN` subsystem. Its help text states that it provides IPv6 compression over IEEE 802.15.4.

Control flow and state: no runtime state. Build selection controls whether `core.o`, `rx.o`, `reassembly.o`, and `tx.o` are linked into `ieee802154_6lowpan.o`.

Dependencies and integration points: sourced by `net/ieee802154/Kconfig` inside the parent `IEEE802154` menu. Requires generic 6LoWPAN support so compression/decompression helpers and lowpan netdevice support are available.

Risks: a missing `6LOWPAN` dependency would cause unresolved symbols; the current dependency prevents that. Because this is a tristate, module/built-in combinations with parent IEEE802154 and generic 6LOWPAN must remain compatible.

Test signals: Kconfig build matrix for disabled, module, and built-in combinations; `make oldconfig` visibility under `IEEE802154`; symbol-driven inclusion of `ieee802154_6lowpan.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Makefile -->
## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Makefile

Purpose: build recipe for the IEEE 802.15.4 6LoWPAN implementation.

Important APIs/types/functions: `obj-$(CONFIG_IEEE802154_6LOWPAN) += ieee802154_6lowpan.o` selects the composite object. `ieee802154_6lowpan-y := core.o rx.o reassembly.o tx.o` declares the constituent source files.

Control flow and state: no runtime behavior. The object composition maps directly to module responsibilities: netdevice/rtnl integration in `core.o`, packet receive in `rx.o`, inet-frag reassembly in `reassembly.o`, and transmit compression/fragmentation in `tx.o`.

Dependencies and integration points: controlled by the Kconfig symbol from `Kconfig` and included through the parent IEEE 802.15.4 Makefile's `obj-y += 6lowpan/` recursion.

Risks: omissions here silently remove functionality at link time. All four objects are required because `core.c` references RX and frag init/exit, netdev ops reference TX/header functions, and RX references reassembly.

Test signals: build with `CONFIG_IEEE802154_6LOWPAN=m/y`; modpost symbol resolution; module load proving `module_init()` and `module_exit()` are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/core.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/core.c

Purpose: rtnetlink and netdevice integration for `lowpan` interfaces backed by IEEE 802.15.4 WPAN devices. It creates/deletes virtual lowpan netdevices, registers packet receive support and fragment infrastructure, and tears lowpan devices down when the underlying WPAN device is unregistered.

Important APIs/types/functions: `lowpan_setup()` initializes broadcast address, hard header length, flags, no-queue private flag, netdev/header ops, free-on-unregister, and netns immutability. `lowpan_newlink()` validates `IFLA_LINK`, resolves an `ARPHRD_IEEE802154` backing device, rejects duplicate lowpan attachment, copies hardware address, calculates headroom/tailroom, sets neighbor private size, registers through `lowpan_register_netdevice()`, and stores the reverse pointer in `wdev->ieee802154_ptr->lowpan_dev`. `lowpan_dellink()` clears that pointer, unregisters, and drops the held backing dev reference. `lowpan_open()` and `lowpan_stop()` maintain global `open_count` and install/remove packet handlers through `lowpan_rx_init()`/`lowpan_rx_exit()`.

Control flow and state: module init first initializes fragment infrastructure, then registers rtnl link ops, then netdevice notifier. On lower WPAN `NETDEV_UNREGISTER`, the notifier deletes the attached lowpan interface if present. Open lowpan interfaces share one packet_type registration tracked by `open_count`.

Dependencies and integration points: integrates with rtnl link kind `lowpan`, generic lowpan registration, IEEE 802.15.4 netdevice private state, IPv6 header size, netdevice notifier chain, and 6LoWPAN fragment subsystem.

Risks: `open_count` is global and not visibly locked in this file; open/stop are serialized by netdevice core but changes must preserve that assumption. `lowpan_dellink()` can be called from notifier context with `head == NULL`; any unregister behavior changes must preserve safe deletion. The lowpan device is netns immutable because the backing phy/device relationship is fixed.

Test signals: `ip link add link wpanX name lowpanX type lowpan`, duplicate lowpan rejection, deletion, backing-device unregister auto-cleanup, open/close packet handler registration, and module load/unload under active/inactive devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/reassembly.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/reassembly.c

Purpose: 6LoWPAN fragment reassembly for IEEE 802.15.4, built on Linux inet-frag infrastructure. It parses FRAG1/FRAGN headers, queues fragments by tag/size/source/destination, reassembles complete IPv6 datagrams, decompresses or accepts the restored network payload, and exposes per-net sysctls for fragment thresholds/timeouts.

Important APIs/types/functions: `lowpan_frag_rcv()` is the RX entry. It peeks IEEE 802.15.4 addresses, parses fragment metadata with `lowpan_get_cb()`, handles FRAG1 payload dispatch through `lowpan_invoke_frag_rx_handlers()`, rejects oversized datagrams, finds the queue with `fq_find()`, and queues the skb. `lowpan_frag_queue()` computes byte offsets, validates last/length consistency, inserts via `inet_frag_queue_insert()`, tracks meat/memory, and calls `lowpan_frag_reasm()` when first and last fragments cover the full datagram. `lowpan_frag_expire()` kills incomplete queues. `lowpan_net_frag_init()` initializes `inet_frags`, sysctl, and pernet operations.

Control flow and state: per-net state lives in `net_ieee802154_lowpan(net)->fqdir`. Queue keys combine `d_tag`, `d_size`, source, and destination. Fragment payload offsets are `d_offset << 3`. Reassembly clears fragment tree pointers, restores skb dev and timestamps, and returns `1` to the caller when a complete skb is available.

Dependencies and integration points: depends on `inet_frag`, IPv6 fragment thresholds/timeouts, jhash/rhashtable params, sysctl, IEEE 802.15.4 header parsing, lowpan IPHC decompression, and the RX file's IPv6 dispatch helper.

Risks: ownership is subtle: queued or errored fragments are consumed, while a `1` return hands a complete skb back to the caller. The code contains `BUILD_BUG_ON()` checks because inet-frag reuses `skb->cb`, so callback area size changes are critical. Hashing assumes the compare key size is a multiple of `u32`.

Test signals: fragmented IPv6 over 802.15.4, duplicate/overlap/corrupt-end rejection, timeout cleanup, sysctl threshold changes, per-net namespace creation/destruction, FRAG1 IPHC and uncompressed IPv6 payloads, and MTU rejection above `IPV6_MIN_MTU`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/reassembly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/rx.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/rx.c

Purpose: receive path for IEEE 802.15.4 6LoWPAN packets. It registers an `ETH_P_IEEE802154` packet handler, validates candidate MAC frames, maps the skb to the associated lowpan netdevice, dispatches 6LoWPAN headers, performs IPHC decompression or fragment handling, and queues resulting IPv6 packets to the network stack.

Important APIs/types/functions: `lowpan_rcv()` is the packet_type callback. `lowpan_rx_h_check()` verifies data frame type, intra-PAN addressing, dispatch availability, and excludes NALP/reserved dispatch values. Dispatch handlers include `lowpan_rx_h_iphc()`, `lowpan_rx_h_frag()`, `lowpan_rx_h_ipv6()`, and unsupported ESC/HC1/DFF/BC0/MESH handlers. `lowpan_iphc_decompress()` peeks 802.15.4 addresses and calls `lowpan_header_decompress()`. `lowpan_give_skb_to_device()` sets `ETH_P_IPV6`, updates lowpan RX stats, and calls `netif_rx()`.

Control flow and state: the handler drops non-802.15.4, other-host, invalid, unbound, or down-lowpan packets. It share-checks the skb, swaps `skb->dev` to the lowpan device, unshares skbs for FRAG1/IPHC paths that mutate data, then runs handlers in likely order: IPHC, fragment, uncompressed IPv6, unsupported dispatches. Result codes determine whether skb is delivered, dropped, or already consumed.

Dependencies and integration points: depends on mac802154 helpers, `ieee802154_hdr_peek_addrs()`, generic lowpan dispatch helpers, fragment reassembly, and lowpan netdevice private linkage from `core.c`.

Risks: dispatch byte access is only safe after `lowpan_rx_h_check()` validates `skb->len`. Result-code fallthrough intentionally frees for `RX_DROP_UNUSABLE` and returns `NET_RX_DROP`; altering switch flow can leak/double-free. Unsupported dispatches are rate-limited warnings but still drops.

Test signals: receive compressed IPHC, uncompressed IPv6, fragmented datagrams, reserved dispatch drops, unsupported dispatch warnings, missing/down lowpan device drops, shared skb unshare behavior, and lowpan RX stats increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/tx.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/tx.c

Purpose: transmit path for IPv6 over IEEE 802.15.4 6LoWPAN. It builds address metadata during header creation, compresses IPv6 headers, emits IEEE 802.15.4 MAC headers, chooses single-frame or fragmented transmission, and updates lowpan TX statistics.

Important APIs/types/functions: `lowpan_header_create()` stores source/destination IEEE 802.15.4 addresses in private headroom, selecting broadcast, neighbor short address, or extended EUI-64 address. `lowpan_header()` copies that metadata, calls `lowpan_header_compress()`, computes datagram size and offset, initializes `mac_cb`, sets ack request based on broadcast/default policy, and calls `wpan_dev_hard_header()`. `lowpan_xmit()` ensures headroom/tailroom and skb exclusivity, invokes `lowpan_header()`, peeks the resulting WPAN header, compares payload to `ieee802154_max_payload()`, then either queues the skb directly to the WPAN device or calls `lowpan_xmit_fragmented()`. Fragment helpers build FRAG1/FRAGN headers and allocate per-fragment skbs.

Control flow and state: per-lowpan `fragment_tag` increments for each fragmented datagram. Fragmentation sends FRAG1 with the MAC header copied from the master skb, then FRAGN skbs with fresh WPAN headers and 8-byte aligned offsets. On full success the original skb is consumed; on error it is freed.

Dependencies and integration points: depends on IPv6/NDISC neighbor table, lowpan compression, IEEE 802.15.4 header generation and max payload calculation, mac802154 control block, and backing WPAN device head/tailroom.

Risks: `lowpan_skb_priv()` assumes sufficient headroom reserved for `struct lowpan_addr_info`; callers outside normal header creation can trip `WARN_ON_ONCE`. Fragment size math depends on `ieee802154_max_payload()` and network header length; underflow would be severe if payload capacity were smaller than required headers. Neighbor short-address reads require locking around `n->lock`.

Test signals: IPv6 unicast via extended address, broadcast via short broadcast, neighbor short-address optimization, single-frame transmit, multi-fragment transmit/reassembly peer tests, headroom expansion path, and TX stats/tag increments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/6lowpan/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/Kconfig -->
## sources/distributed-fs/ceph-client/net/ieee802154/Kconfig

Purpose: top-level Kconfig menu for IEEE 802.15.4 low-rate wireless PAN support.

Important APIs/types/functions: `menuconfig IEEE802154` is a tristate symbol controlling the core LR-WPAN subsystem. `IEEE802154_NL802154_EXPERIMENTAL` gates experimental nl802154 low-level security support. `IEEE802154_SOCKET` controls the socket interface and defaults to `y` when the parent is enabled. The file also sources `net/ieee802154/6lowpan/Kconfig`.

Control flow and state: no runtime behavior. The selected symbols determine whether core cfg802154/nl802154/sysfs/pan/header code, socket support, experimental LLSEC netlink blocks, and 6LoWPAN support are compiled.

Dependencies and integration points: integrates with the kernel networking Kconfig tree and child 6LoWPAN configuration. Its options are referenced by Makefiles and C preprocessor conditionals such as `CONFIG_IEEE802154_NL802154_EXPERIMENTAL`.

Risks: enabling experimental netlink changes ABI surface and exposes security table manipulation code guarded by compile-time conditionals. Defaulting socket support to enabled increases build/runtime surface whenever IEEE802154 is selected.

Test signals: config matrix for core built-in/module, socket disabled/enabled, experimental disabled/enabled, and 6LoWPAN dependency behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/Makefile -->
## sources/distributed-fs/ceph-client/net/ieee802154/Makefile

Purpose: build recipe for the IEEE 802.15.4 networking subsystem and socket interface.

Important APIs/types/functions: `obj-$(CONFIG_IEEE802154) += ieee802154.o` builds the composite core. `obj-$(CONFIG_IEEE802154_SOCKET) += ieee802154_socket.o` builds socket support. `obj-y += 6lowpan/` always descends into the 6LoWPAN subdirectory, where its own Kconfig symbol selects objects. `ieee802154-y` includes `netlink.o`, `nl-mac.o`, `nl-phy.o`, `nl_policy.o`, `core.o`, `header_ops.o`, `sysfs.o`, `nl802154.o`, `trace.o`, and `pan.o`; `ieee802154_socket-y := socket.o`. `CFLAGS_trace.o := -I$(src)` supports trace header include generation.

Control flow and state: no runtime flow, but object composition defines module init coverage. `core.o` calls both legacy `ieee802154_nl_init()` and modern `nl802154_init()`, so corresponding objects must be linked.

Dependencies and integration points: driven by Kconfig symbols and kernel kbuild. Exposes trace support and subdirectory recursion to 6LoWPAN.

Risks: removing an object can create unresolved symbols or silently drop netlink/sysfs/PAN functionality. The unconditional subdirectory recursion is safe because child Makefile selection is symbol-gated.

Test signals: all relevant config builds, especially experimental nl802154, socket, and 6LoWPAN combinations; modpost and link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/core.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/core.c

Purpose: cfg802154 core lifecycle and registry for `wpan_phy` objects and their associated WPAN netdevices. It creates/registers/unregisters PHYs, tracks registered devices, handles netdevice notifier state, moves PHY/device groups across net namespaces, initializes subsystem services, and frees PAN association state.

Important APIs/types/functions: exports `wpan_phy_find()`, `wpan_phy_for_each()`, `wpan_phy_new()`, `wpan_phy_register()`, `wpan_phy_unregister()`, and `wpan_phy_free()`. Internal lookup helpers include `cfg802154_rdev_by_wpan_phy_idx()` and `wpan_phy_idx_to_wpan_phy()`. `cfg802154_switch_netns()` moves all netdevices under a registered device and rolls back on failure. `cfg802154_netdev_notifier_call()` handles register/up/down/unregister for WPAN netdevices, maintaining `wpan_dev_list`, generation counters, opencount, running interface count, association locks/lists, and netns immutability.

Control flow and state: `cfg802154_rdev_list` is RCU-protected with RTNL for writers. Registration calls `device_add()`, appends to the global list, and increments generation. Unregistration waits for `opencount == 0`, removes from the list, synchronizes RCU, increments generation, and deletes the device. Netdev up/down changes opencount and wakes waiters; unregister frees parent/children PAN structures and removes the wpan_dev once even under repeated unregister events.

Dependencies and integration points: depends on sysfs class support, rtnetlink, generic and modern netlink init, netdevice notifier chain, pernet operations, and PAN helpers. Module init order registers pernet, sysfs, notifier, legacy netlink, then nl802154.

Risks: global registry and per-device lists require strict RTNL/RCU discipline. Namespace switching has a rollback loop that must preserve netns immutability flags. `wpan_phy_unregister()` warns if interfaces remain, so drivers must delete virtual interfaces first.

Test signals: PHY register/unregister, open interface blocking unregister, netdev up/down opencount accounting, namespace move success and rollback, repeated unregister events, and module init failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/core.h -->
## sources/distributed-fs/ceph-client/net/ieee802154/core.h

Purpose: private core definitions for cfg802154 registered-device management.

Important APIs/types/functions: `struct cfg802154_registered_device` wraps driver `cfg802154_ops`, global list linkage, internal PHY index, open-count wait queue, running-interface count, WPAN device list, generation counters, per-rdev WPAN device ID allocator, and the embedded `struct wpan_phy`. `wpan_phy_to_rdev()` converts from public `wpan_phy` to the private wrapper. Externs declare the global rdev list and generation, namespace switching, free helper, index lookup, and phy lookup.

Control flow and state: this header defines layout and invariants. The embedded `wpan_phy` must remain last and aligned because private driver data is derived relative to it by public APIs. `opencount`, `dev_wait`, and `wpan_dev_list` are managed in `core.c`; list readers/writers rely on RTNL/RCU as documented in comments.

Dependencies and integration points: includes `net/cfg802154.h`; used by nl802154, legacy netlink, rdev op wrappers, and core lifecycle code.

Risks: changing struct layout, especially moving `wpan_phy`, can break `wpan_phy_priv()` assumptions. The comments specify lock domains; violating them in users of the struct risks use-after-free or stale generation data.

Test signals: build-time layout users, PHY allocation/free with private data, nl802154 lookups by PHY index and WPAN dev ID, lockdep around RTNL-protected access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/header_ops.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/header_ops.c

Purpose: IEEE 802.15.4 MAC header serialization, parsing, peeking, and payload-size calculation. It is shared by mac802154, 6LoWPAN, socket, and management paths needing to build or inspect frame control/address/security headers.

Important APIs/types/functions: exported functions include `ieee802154_hdr_push()`, `ieee802154_mac_cmd_push()`, `ieee802154_beacon_push()`, `ieee802154_hdr_pull()`, `ieee802154_mac_cmd_pl_pull()`, `ieee802154_hdr_peek_addrs()`, `ieee802154_hdr_peek()`, and `ieee802154_max_payload()`. Internal helpers push/pull addresses and security headers, compute address lengths, minimum header length, security header length, and intra-PAN source PAN elision.

Control flow and state: push builds a temporary header buffer from frame control, sequence, destination, source, and optional security header, then prepends it to the skb. Pull validates minimum data with `pskb_may_pull()`, copies frame control/seq, parses addresses, optionally parses security header, and advances skb data. Peek variants inspect from `skb_mac_header()` without pulling. `ieee802154_max_payload()` subtracts header, auth tag, and FCS sizes from `IEEE802154_MTU`.

Dependencies and integration points: depends on `linux/ieee802154.h`, mac802154, IEEE 802.15.4 netdev types, skb APIs, and security-control helpers. 6LoWPAN uses `peek_addrs()` for decompression and `max_payload()` for fragmentation.

Risks: packed bitfield/frame-control layout and memcpy use must match on-wire endian expectations. Security header indexing trusts key-id modes after validation; out-of-range modes could index length arrays if callers bypass normal parsing. Beacon push does not support pending address lists and returns `-EOPNOTSUPP` after appending the fixed beacon header.

Test signals: round-trip push/pull for short/long/no addresses, intra-PAN elision, all security key-id modes, truncated skb rejection, peek without pull, max-payload calculations with security auth tags, MAC command and beacon construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/header_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/ieee802154.h -->
## sources/distributed-fs/ceph-client/net/ieee802154/ieee802154.h

Purpose: private header for the legacy IEEE 802.15.4 generic-netlink interface and shared declarations for legacy management commands.

Important APIs/types/functions: declares legacy netlink init/exit, message allocation/reply/multicast helpers, and command handlers in `nl-phy.c` and `nl-mac.c`. `IEEE802154_OP()` and `IEEE802154_DUMP()` macros build `genl_small_ops` entries, with `IEEE802154_OP` granting `GENL_ADMIN_PERM` for mutating operations. Declares multicast group IDs `IEEE802154_COORD_MCGRP` and `IEEE802154_BEACON_MCGRP`. Externs the legacy `nl802154_family` object from `netlink.c`.

Control flow and state: no direct runtime flow. It binds the legacy operation table to functions for PHY listing, interface add/delete/list, MLME association/scan/start/macparams, and LLSEC parameter/table manipulation.

Dependencies and integration points: consumed by `netlink.c`, `nl-phy.c`, and `nl-mac.c`; uses `linux/nl802154.h` UAPI constants and generic-netlink types.

Risks: this header predates the modern `net/nl802154.h` family and shares similar naming, so confusion between legacy `nl802154_family` and modern `nl802154_fam` is possible. Most legacy lookup helpers use `init_net` in implementation, so namespace behavior differs from newer code.

Test signals: legacy generic-netlink command registration, multicast group creation, and each declared handler resolving at link time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/ieee802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/netlink.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/netlink.c

Purpose: legacy generic-netlink family implementation for IEEE 802.15.4 management. It provides helpers for constructing replies/events and registers a large operation table implemented mostly by `nl-phy.c` and `nl-mac.c`.

Important APIs/types/functions: `ieee802154_nl_create()` creates an event skb with an atomic sequence number protected by `ieee802154_seq_lock`. `ieee802154_nl_mcast()` ends the genl message and multicasts to a legacy group. `ieee802154_nl_new_reply()` and `ieee802154_nl_reply()` build and finalize replies. The `ieee802154_ops` table registers PHY/interface commands, MLME commands, MAC parameter setting, and LLSEC key/device/devkey/seclevel commands. `nl802154_family` is the legacy family named by `IEEE802154_NL_NAME`.

Control flow and state: init registers the family; exit unregisters it. Event creation increments a global sequence under spinlock with IRQ save/restore. Each reply helper expects the caller to have put attributes before finalization.

Dependencies and integration points: uses `ieee802154_policy` from `nl_policy.c`, group names from UAPI, and command handlers from `ieee802154.h`. Core module init calls `ieee802154_nl_init()` before modern `nl802154_init()`.

Risks: legacy ops use `GENL_DONT_VALIDATE` style through macros only indirectly; policy coverage exists but many handlers still perform manual checks. `ieee802154_nl_mcast()` extracts the genl header from the skb; callers must pass an skb created by the matching helper. Global sequence state is process-wide, not per-net.

Test signals: family registration, command enumeration, multicast delivery for start/beacon/coord events, reply generation under attribute-fill failures, and legacy userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl-mac.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/nl-mac.c

Purpose: legacy generic-netlink handlers for IEEE 802.15.4 MAC/MLME management and low-level security table management. It parses legacy attributes, resolves WPAN netdevices, invokes `ieee802154_mlme_ops`, formats interface information, and dumps/mutates LLSEC keys/devices/devkeys/security levels.

Important APIs/types/functions: address helpers convert netlink hardware/short addresses. `ieee802154_nl_fill_iface()` reports device name/index, phy name, hardware address, short address, PAN ID, and optional MAC params. `ieee802154_nl_get_dev()` resolves by device name or index in `init_net` and enforces `ARPHRD_IEEE802154`. MLME handlers include `ieee802154_associate_req()`, `ieee802154_associate_resp()`, `ieee802154_disassociate_req()`, `ieee802154_start_req()`, `ieee802154_scan_req()`, `ieee802154_list_iface()`, `ieee802154_dump_iface()`, and `ieee802154_set_macparams()`. LLSEC handlers parse/fill key IDs, get/set params, add/delete/dump keys, devices, device keys, and security levels.

Control flow and state: most requests validate required attrs, get a dev reference, check operation availability, call the MLME/LLSEC callback, and `dev_put()`. MAC params are read/modified under RTNL and rejected while the netdev is running. LLSEC dumps iterate netdevices and tables using `cb->args[]` as cursors, locking each LLSEC table around list traversal.

Dependencies and integration points: depends on legacy `netlink.c`, UAPI attributes, `ieee802154_mlme_ops`, netdevice lookup, RTNL, LLSEC table callbacks, and IEEE address helpers.

Risks: use of `init_net` in `ieee802154_nl_get_dev()` limits namespace awareness relative to modern nl802154. Attribute validation is manual and some returns use `-ENOBUFS` for parse-like failures. LLSEC dump cursor handling is coarse; nested devkey iteration uses two indices and must avoid repeating/skipping under table mutation.

Test signals: legacy association/start/scan requests, interface dumps, set-macparams rejection while running, LLSEC parameter round trips, add/delete/list for each LLSEC object type, malformed attr rejection, and netns behavior expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl-mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl-phy.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/nl-phy.c

Purpose: legacy generic-netlink handlers for IEEE 802.15.4 PHY listing and deprecated virtual-interface creation/deletion.

Important APIs/types/functions: `ieee802154_nl_fill_phy()` formats PHY name, current page/channel, and supported channel/page list into a genl message. `ieee802154_list_phy()` resolves a PHY by null-terminated name and replies with a single PHY. `ieee802154_dump_phy()` iterates all PHYs using `wpan_phy_for_each()` and callback cursor state. `ieee802154_add_iface()` creates a deprecated virtual interface through `rdev_add_virtual_intf_deprecated()`, optionally sets hardware address with RTNL, and replies with phy/device names. `ieee802154_del_iface()` resolves an IEEE802154 netdev by name, optionally verifies PHY name, and deletes through `rdev_del_virtual_intf_deprecated()`.

Control flow and state: list/dump build skbs and manage `wpan_phy` references. Add-interface validates strings, type, and optional hardware address length, creates the device, holds it while configuring, and unregisters on MAC-address failure. Delete-interface obtains a netdev reference, obtains a phy reference, and releases both on all paths.

Dependencies and integration points: uses core `wpan_phy_find()`/`wpan_phy_for_each()`, rdev deprecated ops, RTNL for MAC address and deletion, and legacy netlink helpers.

Risks: deprecated ops depend on driver support and older userspace semantics. String null-termination and `IFNAMSIZ` checks are manual. Some cleanup paths must balance `dev_hold`, `dev_put`, and `wpan_phy_put()` exactly.

Test signals: legacy PHY list/dump with multiple PHYs, interface add/delete success and invalid type/name/address cases, MAC address set failure rollback, and PHY-name mismatch rejection on delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl-phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl802154.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/nl802154.c

Purpose: modern generic-netlink `nl802154` configuration interface, modeled after nl80211. It exposes PHY and interface discovery, interface creation/deletion, PHY/channel/CCA/power settings, WPAN interface address/MAC behavior settings, netns moves, scan/beacon/association operations, association listing, scan multicast events, and optional experimental LLSEC management.

Important APIs/types/functions: object lookup helpers `__cfg802154_rdev_from_attrs()` and `__cfg802154_wpan_dev_from_attrs()` resolve PHYs/devices from ifindex, WPAN PHY index, or WPAN device ID under RTNL. `nl802154_policy` defines core attr validation/ranges. `nl802154_send_wpan_phy()` and `nl802154_send_iface()` format dump/get replies with generation counters, capabilities, supported commands, and current PIB/interface state. Setter handlers validate support flags and ranges before calling traced `rdev_*` wrappers. Scan and beacon handlers allocate `cfg802154_scan_request`/`cfg802154_beacon_request` and dispatch to drivers. Association handlers lock `wpan_dev->association_lock` around driver calls. `nl802154_pre_doit()` and `nl802154_post_doit()` centralize RTNL locking, object lookup, netdev hold/release, up checks, and user pointers. `nl802154_ops` registers the command table.

Control flow and state: most commands enter through pre_doit, which may lock RTNL, resolve `rdev`, `net_device`, or `wpan_dev`, and hold netdev references. Dumps store cursors in `cb->args[]`; PHY dump allocates a small state object and frees it in `.done`. Address changes are blocked while the netdev or attached lowpan device is running and while associations exist. Scan events are multicast to the `scan` group with coordinator details. Namespace moves use `cfg802154_switch_netns()`.

Dependencies and integration points: depends on cfg802154 core registry, `rdev-ops.h`, generic netlink, mac802154, PAN helpers, net namespace APIs, and UAPI `net/nl802154.h`. Optional LLSEC code depends on driver LLSEC table ops.

Risks: lifetime correctness depends on pre/post flags matching each command. `NL802154_FLAG_NEED_WPAN_DEV` post-release assumes a netdev exists unless deletion clears `user_ptr[1]` for netdev-less devices. Experimental LLSEC code contains TODOs and some suspicious command constants in dump helpers, so ABI consumers need targeted tests. Request structs are freed by drivers/notification path on success, so ownership must remain consistent.

Test signals: get/dump PHY/interface, create/delete interface, all setters with unsupported/out-of-range/running-device cases, netns move rollback, trigger/abort scan with multicast events, beacon start/stop constraints, associate/disassociate/list associations, and experimental LLSEC add/delete/dump coverage when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl802154.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl802154.h -->
## sources/distributed-fs/ceph-client/net/ieee802154/nl802154.h

Purpose: private declarations for the modern nl802154 generic-netlink interface.

Important APIs/types/functions: declares `nl802154_init()` and `nl802154_exit()` for family registration/unregistration. Declares event helpers `nl802154_scan_event()`, `nl802154_scan_started()`, `nl802154_scan_done()`, and `nl802154_beaconing_done()` used by cfg802154/mac802154 drivers or core logic to notify userspace.

Control flow and state: no local state. The event functions expect live `wpan_phy` and `wpan_dev` objects; implementation maps `wpan_phy` to `cfg802154_registered_device`, constructs netlink messages, and multicasts in the PHY net namespace. `scan_done` carries an enum reason.

Dependencies and integration points: this header is included by `core.c` for init/exit and by providers of scan/beacon notifications. It references `struct wpan_phy`, `struct wpan_dev`, and `struct ieee802154_coord_desc` through external declarations from included kernel headers in users.

Risks: event callers must ensure object lifetime across notification construction. Beaconing done is currently a no-op but exported, so callers should not rely on cleanup side effects in this implementation.

Test signals: nl802154 family registration, scan event/start/done multicast delivery, no-listener `-ESRCH` handling in implementation, and build coverage for event callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl802154.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl_policy.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/nl_policy.c

Purpose: legacy IEEE 802.15.4 generic-netlink attribute policy table.

Important APIs/types/functions: defines `const struct nla_policy ieee802154_policy[IEEE802154_ATTR_MAX + 1]`. It assigns types and lengths for device/PHY names, indices, status, short/hardware addresses, PAN IDs, channel/page, coordinator/source/destination addresses, capability/reason/scan fields, ED/channel-page lists, MAC params, and low-level security attributes. `NLA_HW_ADDR` is defined as `NLA_U64`.

Control flow and state: no runtime control flow beyond generic-netlink validation. The table is referenced by the legacy `nl802154_family` in `netlink.c` and constrains messages before per-command parsing.

Dependencies and integration points: uses `linux/nl802154.h` legacy UAPI constants and netlink policy types. Works with `nl-mac.c` and `nl-phy.c`, which still perform required-attribute and semantic validation.

Risks: policy type/length mismatches can reject valid legacy userspace or admit malformed data that command handlers do not expect. Hardware address as U64 differs from raw byte-array handling in some handlers, so endian conversion helpers must stay consistent.

Test signals: malformed netlink fuzzing for each attr type/length, LLSEC fixed-length key and command arrays, channel-page/ED list lengths, and compatibility with legacy userspace tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/nl_policy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/pan.c -->
## sources/distributed-fs/ceph-client/net/ieee802154/pan.c

Purpose: PAN association bookkeeping helpers for cfg802154. It answers parent/child association queries, allocates free short addresses, reports whether a device has active associations, and changes maximum association limits.

Important APIs/types/functions: `cfg802154_device_is_associated()` locks `association_lock` and checks for any parent or child entries. `cfg802154_device_is_parent()` and `cfg802154_device_is_child()` require the lock held and compare target extended addresses against parent/children. `cfg802154_get_free_short_addr()` randomly chooses a short address avoiding broadcast, unspecified, the device's own short address, parent, and children. `cfg802154_set_max_associations()` updates `wpan_dev->max_associations` and returns the old value.

Control flow and state: association state lives in `wpan_dev->parent`, `wpan_dev->children`, `wpan_dev->nchildren`, and `wpan_dev->max_associations`, protected by `association_lock`. Matching intentionally rejects short-address input because the PAN management helpers expect extended addresses for identity checks.

Dependencies and integration points: used by modern nl802154 to block PAN ID/short address changes while associated and set max associations. Exported helpers are available to drivers/mac802154 code.

Risks: `cfg802154_get_free_short_addr()` contains a `continue` inside `list_for_each_entry()` that only advances the list loop, not the outer random-selection loop, so collision handling with child addresses deserves close review/testing. Random selection can loop indefinitely only under pathological/full address-space conditions.

Test signals: parent/child lookup with extended and short targets, association-present checks, max-association update, short-address allocation avoiding reserved/self/parent/children, and lockdep assertions for helpers requiring held lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/pan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/rdev-ops.h -->
## sources/distributed-fs/ceph-client/net/ieee802154/rdev-ops.h

Purpose: inline dispatch layer from cfg802154/nl802154 code to driver `cfg802154_ops`. It wraps most operations with tracepoints and optional-operation checks, keeping call sites concise and consistent.

Important APIs/types/functions: wrappers include deprecated and modern virtual interface add/delete, suspend/resume, channel/CCA/ED/tx-power setters, PAN ID/short-address setters, CSMA/backoff/frame-retry/LBT/ackreq setters, scan trigger/abort, beacon start/stop, associate/disassociate, and experimental LLSEC table/parameter/key/device/security-level operations. Most non-LLSEC wrappers call `trace_802154_rdev_*` before the driver op and `trace_802154_rdev_return_int()` after return.

Control flow and state: wrappers do not own persistent state; they pass `&rdev->wpan_phy` and sometimes `wpan_dev` or request structures to driver callbacks. Optional operations return `-EOPNOTSUPP` when absent for scan, beacon, association, and disassociation; many basic setters assume the operation exists because command exposure/driver registration should guarantee it.

Dependencies and integration points: depends on `net/cfg802154.h`, private `core.h`, and `trace.h`. Heavily used by `nl802154.c`, legacy `nl-phy.c`, and potentially power-management paths.

Risks: wrappers that do not check for NULL ops rely on higher-level supported-command gating and driver correctness; a missing callback can crash. Request ownership for scan/beacon wrappers is delegated to driver on success and caller on failure. Experimental LLSEC wrappers are untraced and assume ops exist under config.

Test signals: tracepoint presence around successful and failing ops, unsupported optional operations returning `-EOPNOTSUPP`, command exposure matching non-NULL callbacks, driver callback argument correctness, and LLSEC behavior under `CONFIG_IEEE802154_NL802154_EXPERIMENTAL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/ieee802154/rdev-ops.h -->
