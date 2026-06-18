<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/ndisc.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/ndisc.c

This file supplies the 6LoWPAN-specific `ndisc_ops` hooks used by IPv6 neighbor discovery when the lower link is IEEE 802.15.4. Its purpose is to preserve and advertise 802.15.4 short-address information in ND source/target link-layer address options and to synthesize short-address-based autoconfigured IPv6 addresses from router advertisements.

Important entry points are the static hooks installed in `lowpan_ndisc_ops`: option parsing, neighbor update, option-space calculation, option filling, and prefix receive address addition. `lowpan_ndisc_parse_options()` accepts only IEEE802154 lowpan devices and handles source/target LL address options whose option length is the short-address form. `lowpan_ndisc_802154_update()` extracts short addresses from ND options and stores them in `struct lowpan_802154_neigh` under the neighbor lock. `lowpan_ndisc_opt_addr_space()` and `lowpan_ndisc_fill_addr_option()` decide whether outgoing RS/NS/NA/Redirect packets should carry the short address option.

Control flow is callback-driven from the IPv6 ndisc core. Incoming packets are parsed into `struct ndisc_options`, neighbor updates run only for override updates, and outgoing packet construction first asks for option space and then writes the option. State is in per-neighbor lowpan private data and the underlying `wpan_dev->short_addr`; there is no persistent storage. Dependencies include `net/ndisc.h`, `net/addrconf.h`, 6LoWPAN internals, IEEE802154 address helpers, and neighbor locking.

Integration risk is mainly around malformed option lengths, byte-order conversion between big-endian ND option data and little-endian IEEE802154 addresses, and races with neighbor updates. Test signals should include RA/RS/NS/NA/Redirect traffic on IEEE802154 6LoWPAN, duplicate option parsing, invalid short addresses, and non-IEEE802154 lowpan devices where hooks must be no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/ndisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc.c

This file implements the registry and dispatch layer for 6LoWPAN next-header compression modules. It maps IPv6 `nexthdr` values to `struct lowpan_nhc` handlers and dispatches compression/uncompression callbacks during 6LoWPAN packet encode/decode.

The key state is `lowpan_nexthdr_nhcs[NEXTHDR_MAX + 1]`, protected by `lowpan_nhc_lock`. `lowpan_nhc_add()` and `lowpan_nhc_del()` are exported for NHC modules declared with `module_lowpan_nhc()`. `lowpan_nhc_check_compression()` tests whether a compressor exists for the IPv6 next header. `lowpan_nhc_do_compression()` calls the handler, fixes a missing transport header for raw sockets, and pulls the uncompressed transport header from the skb. `lowpan_nhc_do_uncompression()` reads the compressed id byte, finds a matching handler by `(id & idmask) == id`, calls its uncompressor if present, updates the IPv6 header's next-header field, and resets the transport header.

Control flow is synchronous and occurs while holding the spinlock. Deletion clears the registry slot and then calls `synchronize_net()` to reduce use-after-free exposure after module removal. The code still documents a race between check and compression if a module is removed between the two phases; it handles this by dropping the packet with `-EINVAL`.

Dependencies are `struct sk_buff`, IPv6 headers, lowpan helper APIs such as `lowpan_fetch_skb()` in handlers, and module lifetime rules. Risks include callback execution under a spinlock, module unload races, unknown id handling, and handlers with `NULL` callbacks that intentionally register ids but cannot actually compress/decompress. Tests should cover module add/delete conflicts, unknown ids, unsupported ids, raw-socket transport header setup, and successful UDP NHC round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.h -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc.h

This header defines the internal 6LoWPAN next-header compression contract. It provides the `struct lowpan_nhc` descriptor, the `LOWPAN_NHC()` declaration macro, module init/exit glue through `module_lowpan_nhc()`, and function prototypes for registry and dispatch operations implemented in `nhc.c`.

The central type, `struct lowpan_nhc`, records a human-readable name, IPv6 next-header value, uncompressed header length to reserve or pull, compressed id and mask bytes, and optional `compress`/`uncompress` callbacks. The macro-generated descriptors are static const objects that individual NHC modules register at module load and deregister at exit. Public functions include `lowpan_nhc_check_compression()`, `lowpan_nhc_do_compression()`, `lowpan_nhc_do_uncompression()`, `lowpan_nhc_add()`, and `lowpan_nhc_del()`.

State is not held in the header itself, but the contract defines how modules participate in the global `lowpan_nexthdr_nhcs` table. Integration points include Linux module init/exit, `struct sk_buff` mutation, IPv6 next-header fields, and lowpan packet formatting.

Risks are mostly API-contract risks: descriptor ids and masks must not overlap ambiguously for the same decoded byte, `nexthdrlen` must match the actual header consumed/restored by handlers, and callbacks must tolerate skb linearity and bounds. Tests should compile NHC modules against this header, verify that each descriptor registers to the expected next-header number, and exercise unsupported descriptors with `NULL` callbacks so the core returns `-ENOTSUPP` rather than corrupting packet state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_dest.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_dest.c

This small module registers the RFC6282 destination-options next-header compression identifier. It declares `nhc_dest` with next header `NEXTHDR_DEST`, id `0xe6`, mask `0xfe`, and zero uncompressed header length.

The file contains no custom compression or uncompression callbacks; both are `NULL`. Its purpose is therefore registry-level recognition of the RFC6282 NHC id rather than a working transform in this tree. Module init and exit are generated by `module_lowpan_nhc(nhc_dest)`.

State is limited to the static descriptor while loaded and the global registry slot managed by `nhc.c`. Dependencies are `nhc.h`, the IPv6 next-header constants, and module registration.

The main integration risk is that receiving this id will find a descriptor but return `-ENOTSUPP` because `uncompress` is not implemented, while outbound compression checks also fail because `compress` is `NULL`. Tests should verify load/unload registration, id matching for `0xe6/0xe7` under mask `0xfe`, and the expected unsupported behavior rather than packet mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_dest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_fragment.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_fragment.c

This module registers the RFC6282 fragment-header next-header compression id. The descriptor `nhc_fragment` maps `NEXTHDR_FRAGMENT` to id `0xe4` with mask `0xfe` and no transform callbacks.

Control flow is entirely module registration through `module_lowpan_nhc()`. Once loaded, the descriptor can be discovered by id during uncompression, but because `uncompress` is `NULL`, the core warns and returns `-ENOTSUPP`. Compression is similarly unavailable because `compress` is `NULL`.

There is no persistent state except the static descriptor and registry membership. Dependencies are the 6LoWPAN NHC framework and IPv6 fragment next-header constants.

Risks are misinterpreting this file as full fragment support; actual fragmentation behavior must be handled elsewhere in the 6LoWPAN stack. Test signals are descriptor registration, duplicate-registration rejection if another fragment NHC is loaded, masked id matching, and graceful unsupported receive behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_fragment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_dest.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_dest.c

This file registers the RFC7400 generic-header-compression id for IPv6 destination extension headers. `ghc_ext_dest` maps `NEXTHDR_DEST` to id `0xb6` with mask `0xfe`.

The descriptor has no compressor or uncompressor. It is a recognition stub that allows the framework to identify the id while still rejecting actual packet transformation as unsupported. It uses the same module registration macro as the RFC6282 NHC files.

State and persistence are limited to the module's static descriptor and the global NHC registry slot. A notable integration point is collision potential: it registers the same IPv6 next-header value as `nhc_dest`, so only one descriptor per `nexthdr` can be registered by the current registry. Loading both RFC6282 and RFC7400 destination modules can trigger `-EEXIST` depending on order.

Risks are id-space collisions, next-header slot conflicts, and user expectations of RFC7400 functionality despite missing callbacks. Tests should include module load ordering with `nhc_dest`, id matching for `0xb6/0xb7`, and unsupported uncompression paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_dest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_frag.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_frag.c

This module declares the RFC7400 generic header compression descriptor for IPv6 fragmentation extension headers. It maps `NEXTHDR_FRAGMENT` to id `0xb4` masked by `0xfe`.

There are no custom callbacks, so the file participates only in descriptor registration. Compression checks for fragment headers will not select it as usable, and uncompression of a matching id returns unsupported from the core.

State is the static descriptor plus global registration. Dependencies are `nhc.h`, module init/exit, and IPv6 fragment constants. Like the destination GHC module, it can conflict with the RFC6282 fragment descriptor because the registry is keyed only by IPv6 next-header number.

Risk areas include module load conflicts, silently unavailable compression, and correctness of the id/mask pair. Tests should verify `lowpan_nhc_add()` conflict behavior with `nhc_fragment`, unload synchronization, and expected `-ENOTSUPP` on receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_frag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_hop.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_hop.c

This file registers the RFC7400 generic compression id for hop-by-hop IPv6 extension headers. `ghc_ext_hop` uses `NEXTHDR_HOP`, id `0xb0`, and mask `0xfe`.

No actual compression or uncompression implementation is provided. The descriptor can be loaded into the NHC registry, but any matching received packet will be reported as an implemented id with no uncompressor and rejected by the core.

State is not persistent beyond module load. It depends on the 6LoWPAN NHC framework and module registration. It also shares the `NEXTHDR_HOP` registry key with the RFC6282 hop-by-hop descriptor, so load ordering can matter.

Risks are registry conflicts and unsupported packet paths. Tests should cover load/unload, conflict with `nhc_hop`, id-mask matching, and receive behavior that warns and returns `-ENOTSUPP` without advancing skb state incorrectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_hop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_route.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_route.c

This module registers RFC7400 generic compression metadata for IPv6 routing extension headers. The descriptor maps `NEXTHDR_ROUTING` to id `0xb2` under mask `0xfe`.

The file contains no transform callbacks, so it is a registration stub. Compression is not offered, and uncompression of matching bytes is rejected as unsupported by the core after descriptor lookup.

State is the static `ghc_ext_route` descriptor and the global NHC registry entry while the module is loaded. Dependencies are `nhc.h` and IPv6 routing next-header definitions. It can conflict with `nhc_routing` because the registry allows only one descriptor per next-header value.

Risks include unexpected `-EEXIST` during module load, unsupported RFC7400 packet reception, and ambiguity between RFC6282/RFC7400 ids in deployments. Tests should check module conflict paths, id matching, and graceful unsupported uncompression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_ext_route.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_icmpv6.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_icmpv6.c

This file registers the RFC7400 generic-header-compression id for ICMPv6. The descriptor `ghc_icmpv6` maps `NEXTHDR_ICMP` to exact id `0xdf` with mask `0xff`.

No compression or uncompression callbacks are implemented. The descriptor can be discovered by compressed id, but the core will return unsupported for receive and will not offer transmit compression.

State is limited to the descriptor and registry membership. Dependencies include `nhc.h`, IPv6/ICMP next-header constants, and module lifecycle. Unlike the extension stubs, it does not obviously conflict with another listed ICMP NHC descriptor in this work item.

Risks are operational confusion about RFC7400 support and exact-id matching mistakes. Tests should load/unload the module, inject a compressed id byte `0xdf`, and assert that the framework produces a warning and `-ENOTSUPP` without corrupting skb transport-header state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_icmpv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_udp.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_udp.c

This module registers the RFC7400 generic UDP compression id range. It maps `NEXTHDR_UDP` to id `0xd0` with mask `0xf8`.

It has no compressor or uncompressor and therefore differs from `nhc_udp.c`, which implements RFC6282 UDP compression. Because the NHC registry is keyed by next-header number, this GHC UDP descriptor can conflict with the implemented RFC6282 UDP descriptor if both are loaded.

State is the static descriptor and global registry slot. Integration points are module load ordering, the NHC id scanner, and UDP next-header dispatch. There is no persistence.

Risks are high because UDP is the one fully implemented NHC in this group; loading the GHC stub instead of the RFC6282 UDP module could make UDP compression unavailable. Tests should cover conflict behavior with `nhc_udp`, exact range matching for ids `0xd0` through `0xd7`, compression check failure due to `NULL` callback, and receive `-ENOTSUPP` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ghc_udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_hop.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_hop.c

This file registers the RFC6282 hop-by-hop options next-header compression descriptor. `nhc_hop` maps `NEXTHDR_HOP` to id `0xe0` with mask `0xfe`.

No callbacks are supplied, so the module only identifies the id range. It does not implement actual header reconstruction or compression. Module init and exit are generated by `module_lowpan_nhc()`.

State is limited to registry membership. Dependencies are `nhc.h` and IPv6 hop-by-hop constants. It may conflict with the RFC7400 hop extension descriptor because both use the same next-header registry key.

Risks are unsupported receive handling and load-order conflicts. Test signals include descriptor add/delete, masked id matching, compression check returning `-ENOENT`, and uncompression returning `-ENOTSUPP` with a warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_hop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ipv6.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_ipv6.c

This module registers RFC6282 IPv6 next-header compression metadata. The descriptor `nhc_ipv6` maps `NEXTHDR_IPV6` to id `0xee` with mask `0xfe`.

There are no transform callbacks, making this a recognition-only module. It allows the core to name the id but cannot compress or rebuild an IPv6-in-IPv6 header.

The only state is the descriptor's presence in the global NHC table. It depends on `nhc.h`, module lifecycle, and IPv6 next-header constants. There is no persistent configuration.

Risks are limited but important for nested IPv6 traffic: matching ids are unsupported and should be dropped cleanly. Tests should cover add/delete, id mask matching, and unsupported receive paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_ipv6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_mobility.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_mobility.c

This file registers the RFC6282 mobility-header NHC id. `nhc_mobility` maps `NEXTHDR_MOBILITY` to id `0xe8` masked by `0xfe`.

It does not implement compression or uncompression. The framework can recognize the id but will reject actual packet handling as unsupported.

State is static descriptor registration. Dependencies are the NHC core and IPv6 mobility header constants. There is no persistence or runtime configuration.

Risks are primarily unsupported mobility traffic and possible incorrect assumptions by users or tests that descriptor registration means functional compression. Tests should validate load/unload, id matching, and `-ENOTSUPP` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_mobility.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_routing.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_routing.c

This module registers RFC6282 routing-header next-header compression metadata. The descriptor `nhc_routing` maps `NEXTHDR_ROUTING` to id `0xe2` under mask `0xfe`.

No custom callbacks exist, so the file is a descriptor-only module. Compression is not available and uncompression returns unsupported after id recognition.

State is the descriptor plus registry membership. Dependencies include `nhc.h`, module lifecycle, and IPv6 routing header constants. It can conflict with the RFC7400 routing extension descriptor because both use `NEXTHDR_ROUTING`.

Risks include unsupported routed-extension packets and registry conflicts. Tests should cover masked id recognition, load conflict with `ghc_ext_route`, and clean unsupported receive behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_routing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_udp.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/nhc_udp.c

This file implements RFC6282 UDP next-header compression and uncompression for 6LoWPAN. It is the functional NHC implementation in this group and registers `nhc_udp` for `NEXTHDR_UDP` with id `0xf0` and mask `0xf8`.

`udp_compress()` examines UDP source and destination ports and emits the shortest supported port encoding: both inline, destination 8-bit compressed, source 8-bit compressed, or both 4-bit compressed in the `0xf0b0` range. The checksum is always emitted inline. `udp_uncompress()` reads the id/port-mode byte, reconstructs ports, rejects checksum-elided packets as unsupported, infers UDP length from the 802.15.4 datagram size when available or from remaining skb length otherwise, and pushes a rebuilt `struct udphdr` into the skb after ensuring writable headroom with `skb_cow()`.

Control flow is invoked by the NHC core under the registry lock. Compression writes header-compression bytes via `lowpan_push_hc_data()` and leaves the core to pull the original UDP header. Uncompression consumes compressed fields with `lowpan_fetch_skb()`, then prepends the full UDP header. State is transient in the skb; there is no persistent module state beyond registration.

Dependencies include UDP header helpers, skb headroom/linear data rules, lowpan device callbacks, IEEE802154 datagram size metadata, and byte-order conversions. Risks include malformed short packets, checksum-elision rejection, wrong inferred length for fragmented or non-802.15.4 frames, and registry conflict with RFC7400 UDP stub. Tests should cover all four port modes, invalid/truncated compressed headers, checksum-elided receive, 802.15.4 `d_size` length inference, non-802154 fallback length, and full compress/uncompress round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/nhc_udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Kconfig -->
# sources/distributed-fs/ceph-client/net/802/Kconfig

This Kconfig fragment declares build-time switches for IEEE 802 support helpers. It defines tristate symbols `STP`, `GARP`, and `MRP`.

`STP` selects `LLC`, because the spanning-tree SAP demux depends on LLC SAP registration and PDU parsing. `GARP` selects `STP`, since GARP traffic is received through the STP/bridge-group LLC SAP demultiplexer. `MRP` is a standalone tristate here; VLAN MVRP selects it from the 802.1Q Kconfig.

There is no runtime control flow or persistent state. The integration point is Kconfig dependency propagation into the Makefile and dependent subsystems such as VLAN GVRP/MVRP.

Risks are configuration omissions: enabling GARP must pull in STP/LLC, while MRP users must ensure packet receive infrastructure is compiled. Test signals are configuration matrix builds with `STP=m/y`, `GARP=m/y`, and `MRP=m/y`, plus dependent VLAN options selecting the expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Makefile -->
# sources/distributed-fs/ceph-client/net/802/Makefile

This Makefile maps 802-layer configuration symbols to kernel objects. It builds `psnap.o` for LLC and AppleTalk users, `fc.o` for Fibre Channel net devices, `fddi.o` for FDDI, `stp.o` for STP, `garp.o` for GARP, and `mrp.o` for MRP.

The only control flow is kbuild conditional object selection with `obj-$(CONFIG_...)`. There is no runtime state. A subtle integration point is that `psnap.o` can be requested by both `CONFIG_LLC` and `CONFIG_ATALK`; kbuild coalesces duplicate object names in the built-in/module context.

Risks are build coverage and dependency mismatch with Kconfig. Tests should include all relevant configuration combinations, especially GARP selecting STP and VLAN GVRP/MVRP pulling in GARP/MRP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fc.c -->
# sources/distributed-fs/ceph-client/net/802/fc.c

This file provides generic Fibre Channel net-device setup and header construction. It exports `alloc_fcdev()` for drivers that need a preconfigured FC-style `struct net_device`.

`fc_header()` is the key header operation. It pushes a Fibre Channel header and, for IPv4 or ARP, also pushes an 802.2 SNAP-style `struct fcllc` header because IPv4 can call `dev->hard_header` directly. It fills source from the provided address or device address and either copies the destination or returns a negative header length to signal unresolved destination. `fc_setup()` configures header ops, ARPHRD type, MTU, address length, queue length, broadcast flag, and all-ones broadcast address. `alloc_fcdev()` wraps `alloc_netdev()` with this setup.

State is per-net-device configuration only; there is no module-global mutable state. Dependencies are FC device header definitions, skb header push semantics, ARP/header-ops integration, and Ethernet protocol constants.

Risks include insufficient skb headroom, wrong SNAP insertion for non-IP/ARP protocols, and driver assumptions around FC address length and MTU. Tests should exercise header creation with and without destination/source addresses, IPv4/ARP SNAP formatting, non-IP header length, and basic device allocation defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fddi.c -->
# sources/distributed-fs/ceph-client/net/802/fddi.c

This file implements generic FDDI net-device helpers. It exports `fddi_type_trans()` for receive protocol classification and `alloc_fddidev()` for FDDI device allocation.

`fddi_header()` pushes either a SNAP header for IP/IPv6/ARP or an 802.2 header form for other protocols, fills the FDDI frame-control byte, SNAP fields, source address, and optional destination address. `fddi_type_trans()` sets skb device and MAC header, pulls the correct header length, returns either `ETH_P_802_2` or the SNAP ethertype, and classifies broadcast/multicast/otherhost packet types. `fddi_setup()` initializes ARPHRD_FDDI type, header lengths, MTU range, address length, queue length, flags, and broadcast address.

State is per-device configuration and skb metadata; no persistent global state exists. Dependencies are FDDI header structures, skb pull/push rules, netdevice flags, and packet-type conventions.

Risks include assuming SNAP on receive, incorrect header pull on malformed frames, and promiscuous-mode classification edge cases. Tests should cover IP/IPv6/ARP and non-SNAP header construction, receive type translation for unicast/broadcast/multicast/otherhost frames, and device allocation defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fddi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/garp.c -->
# sources/distributed-fs/ceph-client/net/802/garp.c

This file implements the IEEE 802.1D Generic Attribute Registration Protocol applicant. It is used by VLAN GVRP to advertise and withdraw VLAN attributes over the bridge-group LLC SAP through the STP demux.

The core state is per-device `struct garp_port` published through `dev->garp_port`, per-application `struct garp_applicant`, and per-attribute `struct garp_attr` nodes stored in an rbtree keyed by type/length/data. The large `garp_applicant_state_table` drives applicant state transitions and transmit actions. Public APIs are `garp_request_join()`, `garp_request_leave()`, `garp_init_applicant()`, `garp_uninit_applicant()`, `garp_register_application()`, and `garp_unregister_application()`.

Control flow starts with application registration through `stp_proto_register()`. Applicant initialization creates the port/applicant, joins the multicast group, arms a randomized join timer, and publishes the applicant with RCU. Join/leave requests create or look up attributes and feed request events into the state table. The join timer emits pending PDUs, appends end marks and LLC headers, queues skbs, and transmits them. Receive flow enters through `garp_pdu_rcv()`, validates protocol id, parses messages/attributes/end marks, and applies remote events under the applicant lock.

Persistence is in memory only. Synchronization uses RTNL for lifecycle, RCU for device pointers, spinlocks for applicant state, timers, and skb queues. Risks include malformed PDU parsing, timer/lifecycle races, rbtree mutation during iteration, allocation failures while building PDUs, and a suspicious `dlen = sizeof(*ga) - ga->len` calculation that appears inverted and should be validated against the intended attribute-data length. Tests should cover GVRP join/leave, timer retransmission, final leave on uninit, malformed PDUs, concurrent device unregister, and multicast membership cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/garp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/mrp.c -->
# sources/distributed-fs/ceph-client/net/802/mrp.c

This file implements the IEEE 802.1Q Multiple Registration Protocol applicant, used by VLAN MVRP. It generalizes attribute registration with vector-attribute packing and both join and periodic timers.

State is per-device `struct mrp_port`, per-application `struct mrp_applicant`, and rbtree-backed `struct mrp_attr` entries keyed by type/length/value. Applicant state transitions come from `mrp_applicant_state_table`; transmit events map through `mrp_tx_action_table`. Public APIs include `mrp_request_join()`, `mrp_request_leave()`, `mrp_init_applicant()`, `mrp_uninit_applicant()`, `mrp_register_application()`, and `mrp_unregister_application()`.

Control flow registers a packet type with `dev_add_pack()`. Applicant init joins the group address, initializes rbtrees/queues, marks the applicant active, and arms join and periodic timers. Join/leave requests mutate attributes under lock. TX events build PDUs with message headers and vector-attribute headers, packing three events per byte and incrementing sequential attribute values. Receive flow ignores `PACKET_OTHERHOST`, verifies application version, parses messages and vector attributes with `skb_header_pointer()`/`skb_copy_bits()`, handles LeaveAll flags, and feeds remote events into the state machine.

State is volatile and synchronized with RTNL lifecycle, RCU pointers, spinlocks, timers, and skb queues. The `active` flag prevents timer rearming during teardown before final TX flushing. Dependencies include netdevice packet handlers, multicast membership, skb control-buffer sizing, and MRP UAPI structures.

Risks include packed-vector parsing mistakes, skb control-buffer overflow for long attributes, timer teardown races, malformed length/flag handling, and hardware/device unregister interaction. Tests should cover MVRP join/leave, sequential vector packing/unpacking, LeaveAll handling, periodic redeclare behavior, malformed frames, and applicant uninit final flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/mrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/psnap.c -->
# sources/distributed-fs/ceph-client/net/802/psnap.c

This file implements SNAP demultiplexing over LLC. It lets protocols register a five-byte SNAP descriptor and receive matching frames.

State consists of `snap_list`, protected by `snap_lock` and traversed under RCU, plus the LLC SAP handle `snap_sap`. `register_snap_client()` allocates a `struct datalink_proto`, stores the descriptor, receive callback, header length, and request function, then adds it to the list. `unregister_snap_client()` removes it with RCU synchronization. `snap_init()` opens LLC SAP `0xAA`, and `snap_exit()` releases it.

Receive control flow enters `snap_rcv()` from LLC, pulls five descriptor bytes, looks up a client, pulls the SNAP header, resets the transport header, and calls the client's `rcvfunc`; unknown or malformed frames are freed. Transmit flow uses `snap_request()` to push the descriptor and send an LLC UI packet.

There is no persistence beyond module state. Dependencies include LLC SAP APIs, datalink protocol structures, skb bounds checks, RCU lists, and module lifecycle. Risks include duplicate descriptor registration, receive callback ownership of skb, SAP open failure, and concurrent unregister. Tests should register/unregister clients, receive matching/unknown/truncated frames, verify SNAP header insertion on transmit, and exercise module unload with active clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/psnap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/stp.c -->
# sources/distributed-fs/ceph-client/net/802/stp.c

This file is the LLC SAP demultiplexer for STP and GARP-family protocols. It registers one LLC SAP for bridge spanning-tree traffic and dispatches either to the generic STP protocol or to GARP protocol slots based on the destination multicast address.

State includes RCU pointers for `stp_proto` and `garp_protos[]`, the shared LLC `sap`, a registration count, and a mutex for registration lifecycle. `stp_proto_register()` opens the LLC SAP on first user and installs the protocol pointer either as the zero-group STP handler or into the GARP address-indexed table. `stp_proto_unregister()` clears the pointer, waits for RCU readers, and releases the SAP when the last user leaves.

Receive control flow in `stp_pdu_rcv()` validates LLC SSAP/DSAP/control fields, selects GARP slots for destination addresses `01:80:c2:00:00:20` through `2f`, verifies exact group address if a GARP proto is found, and calls `proto->rcv()`. Invalid or unregistered frames are freed.

Dependencies are LLC PDU helpers, Ethernet headers, RCU, and `struct stp_proto` provided by STP/GARP users. Risks include out-of-range group-address indexing if callers register malformed GARP addresses, SAP registration reference imbalance, and packet drops from strict LLC validation. Tests should cover STP and GARP registration/unregistration, multicast dispatch, malformed LLC fields, exact-address mismatch, and concurrent receive during unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/stp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Kconfig -->
# sources/distributed-fs/ceph-client/net/8021q/Kconfig

This Kconfig fragment controls 802.1Q/802.1ad VLAN support. `VLAN_8021Q` is a tristate module/built-in option for VLAN interfaces. `VLAN_8021Q_GVRP` enables GARP VLAN Registration Protocol support and selects `GARP`; `VLAN_8021Q_MVRP` enables Multiple VLAN Registration Protocol support and selects `MRP`.

There is no runtime logic. The important integration behavior is dependency propagation from optional VLAN features to the generic registration-protocol modules in `net/802`.

Risks are build-time only: GVRP and MVRP code paths must be compiled consistently with the helper modules they call, and users must have the `ip` tooling or netlink/ioctl control path to create VLAN devices. Tests should include `VLAN_8021Q` built-in and modular builds, with and without GVRP/MVRP, and verify symbol availability for selected helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Makefile -->
# sources/distributed-fs/ceph-client/net/8021q/Makefile

This Makefile builds the VLAN layer. It always builds `vlan_core.o` when `CONFIG_VLAN_8021Q` is enabled in either built-in or module form through `$(subst m,y,...)`, and builds the `8021q.o` module from `vlan.o`, `vlan_dev.o`, and `vlan_netlink.o`. Optional objects are `vlan_gvrp.o`, `vlan_mvrp.o`, and `vlanproc.o`.

There is no runtime state. Integration points are kbuild object aggregation and conditional compilation of optional protocol and procfs support. The split between `vlan_core.o` and `8021q.o` matters because core offload receive/GRO support can be needed by other networking paths.

Risks are missing optional objects when Kconfig symbols are enabled or duplicate core linkage. Tests should compile config combinations for VLAN core, module, GVRP, MVRP, and PROC_FS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan.c

This file is the main VLAN module lifecycle and legacy ioctl control plane. It registers per-net namespace state, netdevice notifiers, GVRP/MVRP helpers, rtnetlink ops, and the legacy VLAN ioctl handler.

Key functions are `register_vlan_dev()`, `unregister_vlan_dev()`, `vlan_check_real_dev()`, `register_vlan_device()`, `vlan_device_event()`, and `vlan_ioctl_handler()`. Device registration adds the VID to the real device, initializes GVRP/MVRP applicants when the first VLAN appears, preallocates the VLAN group array slot, registers the netdevice, links it as an upper device, publishes it in the VLAN group, and updates features. Unregistration withdraws GVRP/MVRP, clears the group slot, unlinks the upper device, queues netdevice unregister, tears down applicants when the last VLAN leaves, and drops the VID reference.

Netdevice notifier flow propagates lower-device state to VLAN devices: address changes update inherited or unicast-filtered addresses; MTU changes clamp VLAN MTUs; feature changes refresh offloads; lower down/up closes or opens VLANs unless loose binding is set; unregister removes all VLAN uppers; filter push/drop events program hardware VIDs. It also auto-adds VID 0 to hardware CTAG filters while devices are up.

State includes per-net `struct vlan_net`, per-real-device `struct vlan_info`, VLAN group arrays, proc entries, GVRP/MVRP applicants, and device upper links. Synchronization relies on RTNL, RCU-published `vlan_info`, and netdevice notifier ordering. Dependencies are VLAN core helpers, rtnetlink, procfs, GARP/MRP, net namespaces, and capability checks.

Risks include registration unwind leaks, notifier ordering during device unregister, VID 0 auto-filter imbalance, address-filter churn, and legacy ioctl validation. Tests should cover netlink and ioctl creation/deletion, duplicate VID rejection, lower device up/down/changeaddr/changemtu/feat-change/unregister, GVRP/MVRP flag behavior, and namespace proc initialization/cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.h -->
# sources/distributed-fs/ceph-client/net/8021q/vlan.h

This internal header defines the VLAN layer's core data structures and helper APIs. It establishes the VLAN protocol index space, the sparse fixed-range `struct vlan_group` array layout, `struct vlan_info` for a real device, per-net `struct vlan_net`, and prototypes shared among `vlan.c`, `vlan_core.c`, `vlan_dev.c`, netlink, procfs, GVRP, and MVRP code.

Important inline helpers are `vlan_proto_idx()`, `__vlan_group_get_device()`, `vlan_group_get_device()`, `vlan_group_set_device()`, `vlan_find_dev()`, `vlan_tnl_features()`, `vlan_group_for_each_dev`, and `vlan_get_ingress_priority()`. The group array is split into eight parts to give constant-time VID lookups while allocating only chunks that are needed. `__vlan_group_get_device()` pairs an `smp_rmb()` with preallocation's write barrier so readers see initialized arrays.

State is not allocated here, but the header codifies persistent in-memory state: real-device VLAN groups, VID lists, optional proc entries, and namespace naming policy. Optional GVRP/MVRP and procfs APIs compile to stubs when disabled.

Risks include invalid protocol handling, memory-order assumptions for group array publication, and callers using `vlan_find_dev()` without RTNL or RCU. Tests should cover protocol index validation, lookup after preallocation/publication, optional configuration builds, and ingress priority mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_core.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_core.c

This file implements VLAN receive demux, VID bookkeeping, hardware filter programming, and VLAN GRO offload support. It exports lookup and VID-management APIs used by drivers and the VLAN module.

`vlan_do_receive()` maps an skb's hardware-accelerated VLAN tag to a VLAN device, clones if needed, drops if the VLAN is down, optionally reinserts the VLAN header when reorder is disabled, maps ingress priority, clears the accel tag, and updates per-CPU RX stats. `__vlan_find_dev_deep_rcu()` searches a device's VLAN group or recurses to a master upper. Accessors expose real device, VLAN id, and VLAN protocol.

VID state is held in `struct vlan_info` attached to the real device and a `vid_list` of `struct vlan_vid_info` reference-counted entries. `vlan_vid_add()` allocates `vlan_info` on demand, programs hardware filters through `ndo_vlan_rx_add_vid`, increments refcounts, and publishes with RCU. `vlan_vid_del()` decrements, removes hardware filters, and frees the whole `vlan_info` via RCU when no VIDs remain. Bulk helpers copy/drop VID filters between devices.

GRO integration registers packet offloads for 802.1Q and 802.1ad. `vlan_gro_receive()` parses VLAN headers, compares VLAN headers across candidate flows, pulls the VLAN header, and delegates to inner IPv4/IPv6 GRO. `vlan_gro_complete()` delegates completion by inner ethertype.

Dependencies include skb VLAN metadata, netdevice hardware filter ops, RCU, RTNL, per-CPU u64 stats, GRO APIs, and VLAN header parsing. Risks include refcount imbalance, filter programming unwind, RCU lifetime mistakes, down-device skb drops, and GRO parsing of malformed headers. Tests should cover RX demux with reorder on/off, down VLAN drops, priority maps, VID add/del refcounts, hardware filter push/drop/unwind, master-upper recursive lookup, and VLAN GRO aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_dev.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_dev.c

This file defines the VLAN netdevice operations, header operations, statistics, feature inheritance, and lower-device pass-through hooks. It is the behavior surface for a VLAN interface after it has been created.

Transmit flow starts in `vlan_dev_hard_start_xmit()`: it adds a hardware-accelerated VLAN tag when header reordering is enabled or the skb lacks an inline VLAN header, switches `skb->dev` to the real device, sends through netpoll or `dev_queue_xmit()`, and updates per-CPU TX stats or drops. Header creation is split between `vlan_dev_hard_header()` for inline VLAN headers and `vlan_passthru_hard_header()` for hardware-offload-capable devices. MTU, MAC address, multicast/unicast sync, RX flags, hwtstamp, MII ioctl, neighbor setup, FCoE, MACsec offload, and forward-path operations are delegated to or constrained by the real device.

Lifecycle functions include `vlan_dev_init()`, `vlan_dev_uninit()`, `vlan_dev_free()`, `vlan_dev_open()`, and `vlan_dev_stop()`. Init copies lower-device flags/features, sets header ops based on VLAN offload capability, allocates per-CPU stats, and holds the real device. Open verifies lower device state unless loose binding is set, maintains unicast filters for non-inherited MACs, records the real MAC, requests GVRP/MVRP joins, and mirrors carrier. Stop unsyncs filters and carrier. Free releases stats and the lower-device reference.

State includes `struct vlan_dev_priv`, ingress and RCU-protected egress priority maps, per-CPU stats, optional netpoll state, inherited real-device address, and lower-device reference tracking. Synchronization uses RTNL for configuration, RCU for egress maps, per-CPU u64 stat sequences, and netdevice core serialization.

Risks include skb tagging/header-order mistakes, priority-map lifetime, lower-device reference leaks, MAC filter imbalance, feature mismatch for Q-in-Q, netpoll cleanup, and optional MACsec/FCoE delegation. Tests should cover transmit with reorder on/off and offload/no-offload, egress/ingress QoS maps, open/stop with inherited/custom MACs, stats aggregation, MTU limits, feature changes, and optional netpoll/MACsec paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_gvrp.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_gvrp.c

This file adapts generic GARP to VLAN GVRP. It defines a single `garp_application` for VLAN ID attributes sent to multicast address `01:80:c2:00:00:21`.

`vlan_gvrp_request_join()` and `vlan_gvrp_request_leave()` extract the VLAN id from the VLAN device, encode it big-endian, and call `garp_request_join()` or `garp_request_leave()` on the real device for `GVRP_ATTR_VID`. They are no-ops for non-802.1Q VLAN protocols. Applicant lifecycle is delegated to `garp_init_applicant()`/`garp_uninit_applicant()`, and module lifecycle registers/unregisters the GARP application.

State is the static application descriptor plus per-real-device applicant state managed by `garp.c`. Dependencies are VLAN device private data, GARP APIs, and 802.1Q ethertype filtering.

Risks include advertising S-tag/802.1ad VLANs by mistake, byte-order errors in VID attributes, and missing applicant initialization before request calls. Tests should enable the VLAN GVRP flag on 802.1Q and 802.1ad devices, verify only 802.1Q emits requests, and validate applicant init/uninit around first/last VLAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_gvrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_mvrp.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_mvrp.c

This file adapts generic MRP to VLAN MVRP. It defines `vlan_mrp_app`, an MRP application for VLAN ID attributes using packet type `ETH_P_MVRP`, group address `01:80:c2:00:00:21`, and version 0.

Join and leave helpers encode the VLAN id as big-endian and call `mrp_request_join()` or `mrp_request_leave()` on the real device for `MVRP_ATTR_VID`. Like GVRP, requests are ignored for non-802.1Q VLAN protocols. Applicant lifecycle and application registration are delegated to the generic MRP layer.

State is a static descriptor plus per-device MRP applicants managed by `mrp.c`. Dependencies are VLAN private data, MRP APIs, packet type registration, and 802.1Q ethertype filtering.

Risks include incorrect VID byte order, unintended operation on 802.1ad VLANs, and mismatched MRP version/type. Tests should cover MVRP flag toggling, applicant startup/shutdown when VLANs appear/disappear, no-op behavior for non-802.1Q VLANs, and emitted MRP VLAN attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_mvrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_netlink.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlan_netlink.c

This file implements the rtnetlink `kind = "vlan"` interface for creating, changing, deleting, and dumping VLAN devices. It is the modern control plane for VLAN configuration.

Validation is handled by `vlan_validate()`, which checks link-layer address length/validity, required data, VLAN protocol (`ETH_P_8021Q` or `ETH_P_8021AD`), VID range, flag mask, and nested QoS map policies. `vlan_newlink()` resolves the lower device, fills `vlan_dev_priv`, defaults to header reordering, validates the real device, computes MTU limits, applies initial changes, and calls `register_vlan_dev()`. `vlan_changelink()` applies flag changes plus ingress and egress QoS maps. `vlan_fill_info()` serializes protocol, id, flags, and QoS maps for dumps. `vlan_get_link_net()` reports the lower device's net namespace.

State mutated here lives in the VLAN netdevice private area: flags, VLAN protocol/id, real device pointer, and priority maps. Egress map allocations are freed on newlink failure. Dependencies include rtnetlink policies, net namespace lookup, extack messages, VLAN registration, and RCU/RTNL access to priority maps.

Risks include incomplete unwind after failed QoS-map allocation, allowing invalid MTUs, bad nested attribute validation, and mismatch between dump size calculation and emitted attributes. Tests should cover netlink create with missing link/id, bad protocol/id/address/flags/QoS, 802.1Q and 802.1ad creation, change flags/QoS, dump round trips, and failure paths that free egress mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlan_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.c -->
# sources/distributed-fs/ceph-client/net/8021q/vlanproc.c

This file implements the optional `/proc/net/vlan` interface. It creates per-net namespace proc entries for VLAN configuration and one proc file per VLAN device.

`vlan_proc_init()` creates `/proc/net/vlan` and `/proc/net/vlan/config`; `vlan_proc_cleanup()` removes them. `vlan_proc_add_dev()` creates a per-device proc file named after the VLAN device and stores the proc entry in `vlan->dent`; `vlan_proc_rem_dev()` removes it. The `config` file uses seq operations to iterate netdevices under RCU and print VLAN device name, VID, and real device. Per-device output from `vlandev_seq_show()` prints VID, reorder flag, private flags, stats, real-device name, ingress priority map, and egress priority map.

State is per-net proc directory/config pointers and per-device proc dent pointers. The display path reads VLAN device private data, stats, and RCU-protected egress maps. Dependencies include procfs, seq_file, net namespace generic storage, netdevice iteration, and VLAN stats helpers.

Risks include proc-name collisions with `config`, stale private data if proc removal races with device teardown, and egress-map traversal without proper RCU. Tests should cover namespace init/cleanup, VLAN register/unregister and rename proc updates, reading config and per-device files, priority-map display, and builds without `CONFIG_PROC_FS` using stubs from `vlanproc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.h -->
# sources/distributed-fs/ceph-client/net/8021q/vlanproc.h

This header declares the VLAN procfs integration points and provides no-op stubs when procfs is disabled. With `CONFIG_PROC_FS`, it exposes `vlan_proc_init()`, `vlan_proc_rem_dev()`, `vlan_proc_add_dev()`, and `vlan_proc_cleanup()`.

The header does not hold state itself. It controls compile-time integration between the main VLAN module and `vlanproc.c`, allowing callers to invoke proc helpers unconditionally.

Risks are limited to configuration mismatches: stubs must preserve caller semantics and return success for add/init when procfs is disabled. Tests should compile VLAN with and without procfs and verify callers do not need conditional code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/8021q/vlanproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Kconfig -->
# sources/distributed-fs/ceph-client/net/9p/Kconfig

This Kconfig fragment defines Plan 9 resource-sharing protocol support. `NET_9P` is a tristate menu option and selects `NETFS_SUPPORT`. Transport options include FD/TCP/Unix (`NET_9P_FD`), virtio, Xen, USB gadget, and RDMA. `NET_9P_DEBUG` enables debug logging.

There is no runtime logic in the file, but it shapes which transport modules and dependencies are built. FD transport implies INET and UNIX; virtio depends on VIRTIO; Xen selects the Xen frontend; USB gadget selects configfs and USB composite support; RDMA depends on networking and InfiniBand address translation.

Risks are configuration gaps where a filesystem mount selects 9p but no usable transport is enabled or loadable. Tests should build common transport combinations and verify module autoload names match the transport lookup paths in `mod.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Makefile -->
# sources/distributed-fs/ceph-client/net/9p/Makefile

This Makefile builds the 9P network core and transport modules. `9pnet.o` is composed of `mod.o`, `client.o`, `error.o`, `protocol.o`, and `trans_common.o`. Separate transport modules are built for FD, virtio, Xen, RDMA, and USB gadget according to Kconfig.

There is no runtime state. The integration point is object composition: core protocol/client/error handling is shared by all transports, while each transport registers a `p9_trans_module` at runtime.

Risks are missing object inclusion when new core helpers are added or transport module names not matching `request_module("9p-%s")`. Tests should compile each transport and verify symbol dependencies against the core module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/client.c -->
# sources/distributed-fs/ceph-client/net/9p/client.c

This file is the core 9P client RPC implementation. It manages client sessions, request tags, fids, version negotiation, request/response marshalling, cancellation/flush, zero-copy IO, and exported helpers corresponding to 9P filesystem operations.

The main persistent state is `struct p9_client`: selected transport, protocol version, negotiated msize, request and fid IDRs, status, spinlock, and fcall cache. `struct p9_req_t` holds transmit/receive fcalls, status, waitqueue, refcount, and tag. `struct p9_fid` tracks remote file identifiers, qids, mode, iounit, uid, and refcount. `p9_tag_alloc()`, `p9_tag_lookup()`, `p9_req_put()`, and `p9_client_cb()` implement tag lifetime and transport callback completion using IDR, RCU-safe slab allocation, refcounts, waitqueues, and memory barriers.

RPC control flow begins with `p9_client_prepare_req()`, which allocates a tag, writes the request PDU with `p9pdu_vwritef()`, finalizes the size, and traces it. `p9_client_rpc()` sends through `trans_mod->request()`, waits for status, handles signals by canceling or sending `TFLUSH`, checks transport errors, parses protocol errors, and returns a referenced request. `p9_client_zc_rpc()` is the analogous path for transports with zero-copy support. `p9_client_create()` applies mount options, chooses/default-loads a transport, creates it, negotiates version/msize, and creates a usercopy fcall cache. Destroy closes the transport, releases module refs, destroys leaked fids/tags, and frees caches.

Exported filesystem operation helpers build on `p9_client_rpc()`: attach, walk, open/create, symlink/link, fsync, clunk/remove/unlink, read/write/readdir including zero-copy thresholds, stat/getattr/wstat/setattr/statfs, rename/renameat, xattrwalk/xattrcreate, mknod/mkdir, lock/getlock, and readlink. State changes to fids happen after successful responses; destructive operations destroy or drop fids even on most errors, matching protocol semantics.

Dependencies include transport modules, protocol.c format parsing, error mapping, tracepoints, netfs for write subrequests, fs_context mount options, IDR, refcounting, usercopy slab caches, and signal handling. Risks are request lifetime races, refcount imbalance between transports, signal/flush edge cases, response-size validation, zero-copy iterator rollback, fid leaks on interrupted clunk, and server-provided bogus counts. Tests should cover version negotiation, all request lifecycle statuses, tag lookup races, cancellation and flush, read/write partial and overlarge responses, zero-copy and non-zero-copy iterator accounting, fid create/destroy paths, and protocol-version variants 9P2000, 9P2000.u, and 9P2000.L.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/error.c -->
# sources/distributed-fs/ceph-client/net/9p/error.c

This file maps Plan 9 server error strings to Linux errno values. Plan 9 protocols commonly return strings, while Linux callers need negative errno results.

State is a static `errmap[]` table and a hash table `hash_errmap`. `p9_error_init()` computes lengths and jhash values for each static string and inserts them into the hash table. `p9_errstr2errno()` hashes the incoming server string, searches matching length/content, returns `-val` when found, and logs unknown strings before returning `-ESERVERFAULT`.

There is no removal path because the table is static and module lifetime covers the hash entries. Dependencies include Linux errno values, jhash, hash table helpers, and 9P error handling in `client.c`.

Risks include writing `errstr[len] = 0` for unknown errors, which assumes the buffer is writable and has room for a terminator; callers currently pass allocated strings from protocol parsing, but this is an important contract. Duplicate or overly broad string mappings can also change user-visible errors. Tests should cover known mappings, unknown strings with writable buffers, zero-valued non-error strings, case-sensitive fossil/u9fs variants, and initialization before first lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/mod.c -->
# sources/distributed-fs/ceph-client/net/9p/mod.c

This file is the 9P network module entry point and dynamic transport registry. It also provides optional debug logging when `CONFIG_NET_9P_DEBUG` is enabled.

State includes global `p9_debug_level` under debug builds, a spinlock-protected `v9fs_trans_list`, and registered `struct p9_trans_module` entries. `v9fs_register_trans()` and `v9fs_unregister_trans()` add/remove transport modules. `v9fs_get_trans_by_name()` searches by name, optionally `request_module("9p-%s")`, and takes a module reference with `try_module_get()`. `v9fs_get_default_trans()` first picks a registered default, then any registered transport, then tries built-in default names in order: virtio, tcp, fd, unix, xen, rdma. `v9fs_put_trans()` drops the module reference.

Module initialization calls `p9_client_init()`, initializes error mappings, and logs installation. Exit logs unload and destroys client caches through `p9_client_exit()`.

Dependencies are Linux module refcounting, optional module autoloading, transport modules, 9P client initialization, and error mapping. Risks include transport unregister while clients hold references, default transport selection surprises, missing autoload aliases, and no cleanup for error hash entries because they are static. Tests should register/unregister dummy transports, lookup by name with module refs, default selection ordering, debug logging masks, and init failure if request cache allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/mod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.c -->
# sources/distributed-fs/ceph-client/net/9p/protocol.c

This file implements 9P wire-format sizing, marshalling, unmarshalling, and helpers for stat and directory-entry parsing. It is shared by the client RPC layer and filesystem consumers.

`p9_msg_buf_size()` estimates request/response buffer sizes from message type, protocol version, and the same format template used for marshalling. It special-cases variable-size messages such as attach, walk, create, read, write, renameat, symlink, and error responses; small messages default to 4 KiB or 8 KiB. `pdu_read()`, `pdu_write()`, and `pdu_write_u()` operate on `struct p9_fcall` buffers and return the number of bytes not copied.

The format engine is `p9pdu_vreadf()` and `p9pdu_vwritef()`. Format letters encode integers, strings, qids, stats, data blobs, arrays of names/qids, 9P2000.L stat/iattr structures, iterator-backed data, and optional 9P2000.u/L fields via `?`. Reads allocate strings and arrays where needed and free partially parsed structures on failure. Writes convert to little-endian wire values and clamp strings to `USHRT_MAX`.

`p9pdu_prepare()` writes a placeholder header, `p9pdu_finalize()` rewrites the final size and traces the PDU, and `p9pdu_reset()` clears offsets. `p9stat_read()` and `p9dirent_read()` parse standalone stat and dirent records from buffers; `p9dirent_read()` copies the allocated name into a fixed destination and rejects overlong names.

State is transient in fcall offsets, sizes, capacities, and allocated parse results. Dependencies include 9P message constants, user namespace uid/gid conversion, iov_iter, tracepoints, and client protocol version. Risks include buffer-size estimate mismatch, unchecked format/template coupling enforced by `BUG_ON`, allocation cleanup on partial parses, string truncation to 16-bit length, data blob pointers referencing the fcall buffer lifetime, and iterator short copies. Tests should cover every format character, optional fields under each protocol version, malformed/truncated PDUs, oversized strings and dirent names, buffer finalization, and size estimates for large reads/writes/walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.h -->
# sources/distributed-fs/ceph-client/net/9p/protocol.h

This internal header declares the protocol marshalling helpers used by `client.c` and implemented in `protocol.c`. It exposes buffer sizing, formatted PDU read/write, PDU header prepare/finalize/reset, and raw `pdu_read()`.

No state is defined here. The header is an integration contract between the 9P client RPC layer and the wire-format implementation. Callers must pass format strings and arguments that match the expectations in `protocol.c`, and must respect allocation ownership for parsed strings, stats, qid arrays, and data pointers.

Risks are mostly API misuse: wrong format strings can trigger `BUG()` or produce invalid wire data, and returned data blob pointers are only valid while the fcall buffer remains alive. Tests should compile all users and exercise format helpers through client operations rather than treating the declarations as independent logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/protocol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_common.c -->
# sources/distributed-fs/ceph-client/net/9p/trans_common.c

This file provides a small shared transport helper, `p9_release_pages()`. It releases an array of pages acquired for a 9P transaction by calling `put_page()` on each non-NULL element.

Control flow is a simple counted loop over `nr_pages`. There is no persistent state. Dependencies are Linux page reference counting and transport code that supplies page arrays.

Risks are caller-side: `nr_pages` must match the allocated array length, and each page must have a reference that should be dropped exactly once. Tests should cover arrays with NULL holes and transport error paths that release partially acquired pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_common.h -->
# sources/distributed-fs/ceph-client/net/9p/trans_common.h

This header declares `p9_release_pages()` for 9P transports. It contains no state or inline logic.

Its integration role is to let transport implementations share page-release cleanup without duplicating loops. The contract is that callers pass an array of `struct page *` entries and the number of entries to inspect.

Risks are limited to misuse by callers, especially passing an incorrect count or pages without owned references. Tests are transport-level cleanup tests that verify page refcounts are balanced on success and failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/9p/trans_common.h -->
