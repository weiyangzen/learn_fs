# subset-b-005982 Research

Grouped source research for Linux UAPI networking, input, IIO, io_uring, IOAM, inotify, and ioctl headers under the ceph-client source mirror. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_link.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_link.h

## Purpose

`if_link.h` is the major rtnetlink netdevice UAPI contract. It defines interface statistics layouts, generic `IFLA_*` link attributes, nested attributes for bridge, VLAN, MACVLAN, VRF, MACsec, XFRM, IPVLAN, VXLAN, Geneve, bareudp, PPP, GTP, bonding, SR-IOV VFs, IPoIB, HSR/PRP, stats, XDP, TUN, rmnet, MCTP, DSA, and OVPN link types. The source was read as a complete 2057-line file.

## Important APIs, Types, and Functions

Key structures include `rtnl_link_stats`, `rtnl_link_stats64`, `rtnl_hw_stats64`, `rtnl_link_ifmap`, `ifla_bridge_id`, `ifla_cacheinfo`, `ifla_vlan_flags`, `ifla_vlan_qos_mapping`, `tunnel_msg`, `ifla_vxlan_port_range`, `ifla_geneve_port_range`, many `ifla_vf_*` structs, `ifla_port_vsi`, `if_stats_msg`, and `ifla_rmnet_flags`. Important enums define top-level `IFLA_*`, address-family payloads, bridge/bridge-port controls, per-link-type netlink attributes, MACsec validation/offload values, VXLAN/Geneve DF policies, bonding and VF management attributes, stats filters, XDP attach attributes and flags, and TUN/rmnet/MCTP/DSA/OVPN attributes. There are no functions; this is an ABI declaration file.

## Control Flow

There is no executable control flow. Runtime flow is external: user space sends rtnetlink messages carrying these attributes; kernel rtnetlink handlers parse nested attributes according to the active link kind; replies use the same IDs and structures for dumps, stats, and events.

## State and Persistence Behavior

The file does not own state. It defines persistent UAPI numeric IDs and struct layouts that kernel networking code and user-space tools must treat as stable. Some attributes configure kernel-resident netdevice state, such as bridge timers, VLAN policy, tunnel endpoints, VF trust/rate/VLAN settings, XDP attachment, and TUN persistence, but storage lives in the owning networking subsystems.

## Dependencies and Integration Points

It includes `linux/types.h` and `linux/netlink.h` and is consumed by iproute2-style tools, rtnetlink users, network drivers, virtual link modules, bridge/bond/VLAN/tunnel code, XDP/BPF attachment paths, and stats dump handlers.

## Risks and Edge Cases

This file is ABI-critical: renumbering enum values, changing struct field order, or changing integer widths breaks user space. Risk is high around nested attribute validation, endian-marked fields, obsolete aliases, bridge timer units in `USER_HZ`, VF list bounds, XDP flag compatibility, and old tunnel flags that exhausted `__be16` space.

## Test Signals

Useful signals include UAPI header compile tests, rtnetlink selftests for every link kind touched, iproute2 compatibility tests, netlink policy validation tests for nested attrs, bridge/VLAN/tunnel/XDP integration tests, and struct size/offset checks for stats and VF structs on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ltalk.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_ltalk.h

## Purpose

`if_ltalk.h` defines LocalTalk link-layer constants for Linux UAPI consumers. The complete 10-line file contains only header guards and MTU/header/address length constants.

## Important APIs, Types, and Functions

Constants are `LTALK_HLEN`, `LTALK_MTU`, and `LTALK_ALEN`. There are no structs, enums, functions, or ioctls.

## Control Flow

No runtime flow is present. Drivers or tools include the constants when sizing LocalTalk headers, device addresses, or MTU constraints.

## State and Persistence Behavior

No state is stored by the header. The constants describe protocol sizing assumptions used by external code.

## Dependencies and Integration Points

The header has no includes and integrates with legacy LocalTalk networking code and generic network-device validation.

## Risks and Edge Cases

The values are legacy ABI assumptions. Changing them can mis-size buffers or break tools that assume one-byte LocalTalk addresses and a 600-byte MTU.

## Test Signals

Compile coverage for LocalTalk users and simple checks that interface setup paths still apply the expected header length, MTU, and address length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ltalk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_macsec.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_macsec.h

## Purpose

`if_macsec.h` defines the generic-netlink UAPI for configuring and dumping MACsec devices, secure channels, secure associations, offload mode, cipher IDs, key sizes, ICV lengths, commands, and statistics. The complete 194-line file was read.

## Important APIs, Types, and Functions

Important constants include `MACSEC_GENL_NAME`, `MACSEC_GENL_VERSION`, key/key-id/salt lengths, MACsec GCM AES cipher IDs, and min/std/max ICV lengths. Enums define `macsec_attrs`, `macsec_secy_attrs`, `macsec_rxsc_attrs`, `macsec_sa_attrs`, `macsec_offload_attrs`, `macsec_nl_commands`, and RXSC/SA/TXSC/SecY stats attribute families. There are no C functions.

## Control Flow

The header defines message shape rather than flow. User space sends MACsec generic-netlink commands such as add/delete/update RXSC/TXSA/RXSA or update offload; kernel MACsec code validates nested attributes and mutates the target MACsec netdevice; dumps return nested SecY, SC, SA, and stats attributes.

## State and Persistence Behavior

Configured state lives in kernel MACsec SecY, RXSC, TXSC, and SA objects. Keys, packet numbers, replay windows, validation/encryption/protection flags, XPN salt/SSCI, and offload type persist with the MACsec device until changed or deleted.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with generic netlink, rtnetlink-created MACsec devices, IEEE 802.1AE crypto handling, hardware offload code, and user tools such as `ip macsec`.

## Risks and Edge Cases

Sensitive key material passes through `MACSEC_SA_ATTR_KEY`. Edge risks include XPN PN width differences, strict ICV length bounds, replay-window validation, offload type disagreement with hardware, and keeping stats attributes consistently 32-bit or 64-bit as documented.

## Test Signals

MACsec selftests should cover add/update/delete flows, XPN and non-XPN SAs, replay-protect validation, dumps with all nested stats, invalid key/ICV lengths, and hardware-offload negotiation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_macsec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_packet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_packet.h

## Purpose

`if_packet.h` defines the AF_PACKET socket ABI for raw link-layer access, including socket address layouts, packet type IDs, ring-buffer versions, mmap ring headers, status bits, fanout, multicast membership, and packet statistics. The complete 320-line file was read.

## Important APIs, Types, and Functions

Key structs and unions are `sockaddr_pkt`, `sockaddr_ll`, `tpacket_stats`, `tpacket_stats_v3`, `tpacket_rollover_stats`, `tpacket_stats_u`, `tpacket_auxdata`, `tpacket_hdr`, `tpacket2_hdr`, `tpacket_hdr_variant1`, `tpacket3_hdr`, `tpacket_bd_ts`, `tpacket_hdr_v1`, `tpacket_block_desc`, `tpacket_req`, `tpacket_req3`, `tpacket_req_u`, `packet_mreq`, and `fanout_args`. Macros define `PACKET_*` socket options, fanout modes/flags, `TP_STATUS_*`, `TPACKET_*` alignment/header sizes, membership types, and `TPACKET_V1..V3`.

## Control Flow

No executable flow is defined. Packet socket code uses these layouts when user space binds an AF_PACKET socket, configures options with `setsockopt`, maps RX/TX rings, waits for status-bit ownership transfer between kernel and user space, and optionally fans out traffic across sockets.

## State and Persistence Behavior

Runtime state is in packet sockets and mmap rings. `TP_STATUS_KERNEL`/`TP_STATUS_USER` style bits coordinate per-frame/block ownership, while membership and fanout options persist for the life of the socket or until changed.

## Dependencies and Integration Points

The header includes `asm/byteorder.h` and `linux/types.h`. It integrates with AF_PACKET sockets, network drivers through skb delivery, BPF fanout selectors, VLAN auxiliary data, timestamping, and tools such as tcpdump/libpcap.

## Risks and Edge Cases

Ring layouts are ABI-sensitive and alignment-dependent. Risks include incorrect TPACKET version handling, stale status-bit ownership causing packet loss or corruption, endian-sensitive `fanout_args`, VLAN metadata validity bits, timestamp source ambiguity, and user buffers sized incorrectly for variable block/frame layout.

## Test Signals

AF_PACKET selftests should exercise V1/V2/V3 RX rings, TX rings, rollover stats, auxdata VLAN fields, fanout modes including BPF, membership changes, timestamp flags, and 32/64-bit layout compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_phonet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_phonet.h

## Purpose

`if_phonet.h` defines minimal Phonet network-device MTU constants for the Linux UAPI. The complete 17-line file was read.

## Important APIs, Types, and Functions

Constants are `PHONET_MIN_MTU`, `PHONET_MAX_MTU`, and `PHONET_DEV_MTU`. There are no structs or functions.

## Control Flow

No control flow exists. Phonet device setup and validation code use the constants to bound link MTU.

## State and Persistence Behavior

No state is held by the file; actual MTU state is per network device.

## Dependencies and Integration Points

The header has no includes. It integrates with Phonet device drivers and any user-space configuration tooling that needs Phonet MTU bounds.

## Risks and Edge Cases

The max value accounts for `pn_length = 0xffff`; changing it can reject valid Phonet packets or permit oversized buffers that downstream code does not expect.

## Test Signals

Compile coverage and Phonet link setup tests that attempt minimum, maximum, and out-of-range MTU values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_phonet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_plip.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_plip.h

## Purpose

`if_plip.h` exposes legacy PLIP tuning ioctls and the `plipconf` argument structure for parallel-line IP devices. The complete 28-line file was read.

## Important APIs, Types, and Functions

It includes `linux/sockios.h`, defines `SIOCDEVPLIP`, `PLIP_GET_TIMEOUT`, `PLIP_SET_TIMEOUT`, and `struct plipconf` with command, nibble timeout, and trigger timeout fields.

## Control Flow

There is no local code. User space passes `plipconf` through a private device ioctl; the PLIP driver interprets `pcmd` to get or set timeout parameters.

## State and Persistence Behavior

Timeout state is driver/device state. It persists while the PLIP interface exists and is changed through ioctls.

## Dependencies and Integration Points

The header depends on socket private ioctl numbering and integrates with the legacy PLIP network driver.

## Risks and Edge Cases

Private ioctl numbering can collide if misused. Timeout values are untyped `unsigned long`, so 32/64-bit compatibility and range validation matter.

## Test Signals

Driver ioctl tests should cover get/set timeout operations, invalid commands, compat ioctl handling, and behavior at zero and large timeout values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_plip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ppp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_ppp.h

## Purpose

`if_ppp.h` is a one-line compatibility include that exposes PPP ioctl definitions through `linux/ppp-ioctl.h`. The complete file was read.

## Important APIs, Types, and Functions

The only API surface is `#include <linux/ppp-ioctl.h>`. All actual PPP constants and structures are provided by that dependency.

## Control Flow

There is no control flow. Including this header forwards consumers to the canonical PPP ioctl UAPI.

## State and Persistence Behavior

No state is defined here. PPP channel/unit state is managed by the PPP subsystem.

## Dependencies and Integration Points

The file integrates legacy include paths with the PPP ioctl header used by PPP daemons and kernel PPP code.

## Risks and Edge Cases

The main risk is include-path compatibility: removing or changing this shim can break user-space sources that include `linux/if_ppp.h`.

## Test Signals

UAPI compile tests should include `linux/if_ppp.h` directly and verify expected PPP ioctl symbols remain visible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_ppp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_pppol2tp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_pppol2tp.h

## Purpose

`if_pppol2tp.h` defines socket address and socket-option UAPI structures for PPP over L2TP, including IPv4/IPv6 and L2TPv2/L2TPv3 variants. The complete 105-line file was read.

## Important APIs, Types, and Functions

Structures are `pppol2tp_addr`, `pppol2tpin6_addr`, `pppol2tpv3_addr`, and `pppol2tpv3in6_addr`. Enums define `PPPOL2TP_SO_DEBUG`, `PPPOL2TP_SO_RECVSEQ`, `PPPOL2TP_SO_SENDSEQ`, `PPPOL2TP_SO_LNSMODE`, `PPPOL2TP_SO_REORDERTO`, plus deprecated debug category aliases mapped to `L2TP_MSG_*`.

## Control Flow

User space creates a PPPoL2TP socket and calls `connect()` with the matching address structure. Kernel PPPoL2TP code binds the socket to an existing UDP/IP tunnel fd, local/remote tunnel IDs, session IDs, and peer address; socket options then control sequencing, LNS mode, and reordering.

## State and Persistence Behavior

The header defines connection-time state passed into the kernel. Tunnel/session bindings and socket options persist on the PPPoL2TP socket and related L2TP session objects until disconnect/close or option changes.

## Dependencies and Integration Points

It includes `linux/types.h`, `linux/in.h`, `linux/in6.h`, and `linux/l2tp.h`. It integrates with PPP, L2TP, IPv4/IPv6 sockets, and AF_PPPOX protocol-specific sockaddr wrappers.

## Risks and Edge Cases

The main compatibility risks are 16-bit versus 32-bit tunnel/session IDs, pid/fd ownership semantics, IPv4 versus IPv6 layout selection, reorder timeout interpretation, and deprecated debug options that may be accepted but unused.

## Test Signals

Tests should connect v2/v3 and IPv4/IPv6 sessions, validate bad fd/pid/session combinations, exercise sequence send/receive options, and confirm LNS/reorder settings are reflected in session behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_pppol2tp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_pppox.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_pppox.h

## Purpose

`if_pppox.h` defines the generic PPP-over-X socket ABI, especially PPPoE, PPTP, and protocol-specific PPPoL2TP sockaddr wrappers. The complete 154-line file was read.

## Important APIs, Types, and Functions

Important definitions include `AF_PPPOX`/`PF_PPPOX` fallback values, `sid_t`, `pppoe_addr`, `pptp_addr`, protocol IDs `PX_PROTO_OE`, `PX_PROTO_OL2TP`, `PX_PROTO_PPTP`, `sockaddr_pppox`, four L2TP-specific sockaddr variants, PPPoE discovery codes `PADI/PADO/PADR/PADS/PADT`, `pppoe_tag`, tag type constants `PTT_*`, `pppoe_hdr`, and `PPPOE_SES_HLEN`.

## Control Flow

No executable logic is present. User space fills the correct sockaddr for `bind()`/`connect()` on AF_PPPOX sockets; the kernel chooses PPPoE, PPTP, or L2TP handling based on `sa_protocol`. PPPoE packet parsing uses the packed header and variable tag arrays.

## State and Persistence Behavior

Socket addressing state persists in the PPPoX socket and PPP channel. PPPoE session IDs, peer MAC, device name, and L2TP/PPTP identifiers are kernel-managed after connection.

## Dependencies and Integration Points

The header includes type, byteorder, socket, interface, Ethernet, PPPoL2TP, IPv4, and IPv6 headers. It integrates with PPP generic channels, Ethernet discovery/session traffic, PPTP, and L2TP transport sockets.

## Risks and Edge Cases

Packed structures and endian-converted tag constants are ABI-sensitive. The comment notes that `sockaddr_pppox` could not be extended safely, so L2TP uses protocol-specific sockaddr types; consumers must use the correct size. PPPoE flexible tags require careful length validation.

## Test Signals

AF_PPPOX tests should cover PPPoE discovery/session header encoding, sockaddr sizes, L2TP v2/v3 IPv4/IPv6 connection paths, invalid protocol IDs, and endian correctness for tag constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_pppox.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_slip.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_slip.h

## Purpose

`if_slip.h` declares constants and private ioctls for legacy SLIP, CSLIP, and KISS TNC line modes. The complete 31-line file was read.

## Important APIs, Types, and Functions

Mode and option constants include `SL_MODE_SLIP`, `SL_MODE_CSLIP`, `SL_MODE_KISS`, `SL_OPT_SIXBIT`, and `SL_OPT_ADAPTIVE`. Private ioctls are `SIOCSKEEPALIVE`, `SIOCGKEEPALIVE`, `SIOCSOUTFILL`, `SIOCGOUTFILL`, `SIOCSLEASE`, and `SIOCGLEASE`.

## Control Flow

No local flow exists. User space uses private network-device ioctls to configure line keepalive, outfill, and leased-line behavior; the SLIP driver applies the values.

## State and Persistence Behavior

Line mode and timers are driver/device state, persisting while the SLIP interface exists.

## Dependencies and Integration Points

The header expects `SIOCDEVPRIVATE` from surrounding includes and integrates with legacy serial-line networking and amateur radio KISS paths.

## Risks and Edge Cases

Because the file does not include `sockios.h` directly, include-order assumptions matter. Private ioctl numbering and legacy timer semantics also require compatibility care.

## Test Signals

Compile tests for direct and indirect inclusion, plus SLIP ioctl tests for get/set timer and lease settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_slip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_team.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_team.h

## Purpose

`if_team.h` is an auto-generated YNL UAPI header for the team generic-netlink family. It defines family metadata, string limits, multicast group name, attributes, nested option/port entries, and commands. The complete 79-line file was read.

## Important APIs, Types, and Functions

Constants include `TEAM_GENL_NAME`, `TEAM_GENL_VERSION`, `TEAM_STRING_MAX_LEN`, and `TEAM_GENL_CHANGE_EVENT_MC_GRP_NAME`. Enums define `TEAM_ATTR_*`, `TEAM_ATTR_ITEM_OPTION_*`, `TEAM_ATTR_OPTION_*`, `TEAM_ATTR_ITEM_PORT_*`, `TEAM_ATTR_PORT_*`, and commands `TEAM_CMD_NOOP`, `TEAM_CMD_OPTIONS_SET`, `TEAM_CMD_OPTIONS_GET`, and `TEAM_CMD_PORT_LIST_GET`.

## Control Flow

No executable flow exists. Generic-netlink requests set or get team options and list ports. Kernel team code emits change events on the configured multicast group.

## State and Persistence Behavior

Team device state, options, and port membership live in kernel team objects. The header only fixes the netlink contract used to mutate and observe that state.

## Dependencies and Integration Points

It is generated from `Documentation/netlink/specs/team.yaml` and integrates with the YNL tooling, generic netlink, the team driver, and users such as teamd/libteam.

## Risks and Edge Cases

Manual edits can be overwritten or diverge from the YAML spec. Risks include attribute renumbering, inconsistent nested list shapes, string-length assumptions, and stale users expecting old option type/data encoding.

## Test Signals

Regeneration diff checks, generic-netlink policy tests, team option set/get tests, port-list dump tests, and multicast change-event tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_team.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_tun.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_tun.h

## Purpose

`if_tun.h` defines the user-space ioctl and data-structure ABI for Universal TUN/TAP devices, including device creation/configuration, queue management, offload flags, BPF filters, carrier, netns access, packet-info headers, and TAP multicast filters. The complete 127-line file was read.

## Important APIs, Types, and Functions

Important ioctls include `TUNSETIFF`, `TUNSETPERSIST`, `TUNSETOWNER`, `TUNSETGROUP`, `TUNGETFEATURES`, `TUNSETOFFLOAD`, `TUNATTACHFILTER`, `TUNSETVNETHDRSZ`, `TUNSETQUEUE`, `TUNSETVNETLE/BE`, `TUNSETSTEERINGEBPF`, `TUNSETFILTEREBPF`, `TUNSETCARRIER`, and `TUNGETDEVNETNS`. Flags include `IFF_TUN`, `IFF_TAP`, `IFF_NO_PI`, `IFF_VNET_HDR`, `IFF_MULTI_QUEUE`, `IFF_ATTACH_QUEUE`, `IFF_DETACH_QUEUE`, `IFF_PERSIST`, and offloads `TUN_F_*`. Structs are `tun_pi` and flexible `tun_filter`.

## Control Flow

User space opens `/dev/net/tun`, issues `TUNSETIFF` and other ioctls, then reads/writes packets. Kernel TUN/TAP code prepends or strips `tun_pi` depending on `IFF_NO_PI`, manages queues, applies optional filters, and advertises or consumes offload metadata.

## State and Persistence Behavior

Per-device state includes owner/group, persistence, queue attachment, vnet header size and endian mode, offload capabilities, BPF/filter settings, and carrier. Persistent devices survive fd close when `TUNSETPERSIST` is enabled.

## Dependencies and Integration Points

It includes `linux/types.h`, `linux/if_ether.h`, and `linux/filter.h`. It integrates with character-device ioctls, netdevices, virtio-style vnet headers, BPF filters, network namespaces, and virtual networking stacks.

## Risks and Edge Cases

`IFF_NO_PI` and `IFF_NOFILTER` share the same numeric value in different contexts, so callers must interpret flags by ioctl path. Other risks are multi-queue attach/detach races, endian mode support, offload feature mismatch, flexible filter sizing, and persistent-device ownership mistakes.

## Test Signals

TUN/TAP selftests should cover device creation, persistence, ownership, queue attach/detach, packet-info present/absent modes, vnet header sizing/endian, BPF filters, carrier toggles, and offload negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_tun.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_tunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_tunnel.h

## Purpose

`if_tunnel.h` defines ioctl, flag, structure, and netlink attribute UAPI for IP tunnels, GRE, SIT/6rd, VTI, tunnel encapsulation, and modern tunnel option bits. The complete 221-line file was read.

## Important APIs, Types, and Functions

Important ioctls include `SIOCGETTUNNEL`, `SIOCADDTUNNEL`, `SIOCDELTUNNEL`, `SIOCCHGTUNNEL`, PRL and 6rd variants. It defines GRE flags and helpers, `ip_tunnel_parm`, `ip_tunnel_prl`, `ip_tunnel_6rd`, tunnel encapsulation types/flags, `IFLA_IPTUN_*`, `IFLA_GRE_*`, `IFLA_VTI_*`, legacy `TUNNEL_*` flags for user space, and `IP_TUNNEL_*_BIT` values for expanded flag space.

## Control Flow

There is no local executable flow. User space configures tunnels through legacy private ioctls or rtnetlink attributes. Kernel tunnel drivers parse endpoints, keys, flags, encapsulation, 6rd/PRL settings, and route packets through the configured tunnel device.

## State and Persistence Behavior

Tunnel state is stored on netdevices and includes names, underlying link, input/output flags, keys, outer IP header template, 6rd parameters, PRL entries, encapsulation ports, fwmark, and GRE/ERSPAN options.

## Dependencies and Integration Points

The header includes `linux/types.h`, `linux/if.h`, `linux/ip.h`, `linux/in6.h`, and byteorder definitions. It integrates with IPIP/SIT/GRE/VTI tunnel drivers, rtnetlink, and legacy private ioctls.

## Risks and Edge Cases

The file explicitly warns that old `__be16` tunnel flags have no free bits; new code should use `*_BIT` definitions. Endian conversions, option-present masks, SIT/VTI bit aliasing, and ioctl/netlink parity are common compatibility traps.

## Test Signals

Tests should cover legacy ioctl and rtnetlink creation/change/delete, GRE key/seq/csum flags, 6rd and PRL operations, FOU/GUE/MPLS encapsulation, VTI flag behavior, and endian compatibility for old and new flag forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_tunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_vlan.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_vlan.h

## Purpose

`if_vlan.h` defines the legacy 802.1Q VLAN ioctl argument ABI, VLAN operation commands, device flags, naming modes, and command payload union. The complete 66-line file was read.

## Important APIs, Types, and Functions

Enums define `vlan_ioctl_cmds`, `vlan_flags`, and `vlan_name_types`. `struct vlan_ioctl_args` carries a command, primary device name, union payload (`device2`, VID, skb priority, name type, bind type, flag), and `vlan_qos`.

## Control Flow

User space passes `vlan_ioctl_args` to VLAN ioctls defined in `sockios.h`. Kernel VLAN code branches on `cmd` to add/delete VLAN devices, set or get ingress/egress QoS mappings, set naming type/flags, and report real device or VID.

## State and Persistence Behavior

VLAN devices, flags, naming behavior, QoS mappings, and bindings persist as kernel netdevice/VLAN state until changed or the device is removed.

## Dependencies and Integration Points

The header intentionally relies on VLAN ioctl numbers from `sockios.h`. It integrates with legacy VLAN configuration tools and the VLAN netdevice subsystem; modern rtnetlink VLAN attributes in `if_link.h` are a parallel interface.

## Risks and Edge Cases

Device name arrays are fixed at 24 bytes, smaller than some modern interface-name expectations. Union interpretation depends entirely on `cmd`; callers must validate VID and QoS ranges and handle legacy naming modes.

## Test Signals

VLAN ioctl tests should cover add/delete, get realdev/VID, ingress/egress QoS mapping, flag changes, naming modes, invalid VID values, and compatibility with rtnetlink-created VLAN devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_vlan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_x25.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_x25.h

## Purpose

`if_x25.h` defines small packet-to-device interface constants for Linux X.25. The complete 27-line file was read.

## Important APIs, Types, and Functions

Constants are `X25_IFACE_DATA`, `X25_IFACE_CONNECT`, `X25_IFACE_DISCONNECT`, and `X25_IFACE_PARAMS`, with a reference to `Documentation/networking/x25-iface.rst`. It includes `linux/types.h` but defines no types.

## Control Flow

No code flow exists. X.25 interface code uses the leading message type constants to distinguish data, connect, disconnect, and parameter messages.

## State and Persistence Behavior

The header does not own state. Connection/session state is maintained by the X.25 networking implementation.

## Dependencies and Integration Points

It integrates with the X.25 packet/device interface and documentation-defined framing.

## Risks and Edge Cases

The numeric values are wire/interface ABI. Changing them would make user-space X.25 helpers and kernel drivers disagree about message type.

## Test Signals

X.25 interface tests should verify message classification for all four constants and reject malformed or unexpected type values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_x25.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_xdp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_xdp.h

## Purpose

`if_xdp.h` defines the AF_XDP socket UAPI for high-performance packet I/O through XDP, including bind sockaddr, UMEM registration, mmap ring offsets, socket options, statistics, descriptors, multi-buffer support, and transmit metadata/offloads. The complete 184-line file was read.

## Important APIs, Types, and Functions

Key structs are `sockaddr_xdp`, `xdp_ring_offset`, `xdp_mmap_offsets`, `xdp_umem_reg`, `xdp_statistics`, `xdp_options`, `xsk_tx_metadata`, and `xdp_desc`. Important flags/options include `XDP_SHARED_UMEM`, `XDP_COPY`, `XDP_ZEROCOPY`, `XDP_USE_NEED_WAKEUP`, `XDP_USE_SG`, `XDP_UMEM_*`, socket options `XDP_MMAP_OFFSETS` through `XDP_MAX_TX_SKB_BUDGET`, mmap page offsets, unaligned buffer masks, `XDP_TXMD_FLAGS_*`, `XDP_PKT_CONTD`, and `XDP_TX_METADATA`.

## Control Flow

User space creates AF_XDP sockets, registers UMEM, configures RX/TX/fill/completion rings, mmaps ring pages, binds to an ifindex/queue, and exchanges descriptors with the kernel. Need-wakeup flags tell applications when to poll or sendto to restart driver progress.

## State and Persistence Behavior

Socket state includes UMEM address/length/chunking/headroom, ring producer/consumer positions, bind queue, shared-UMEM fd, copy/zerocopy mode, statistics, and tx metadata settings. State is per socket/UMEM and lasts until socket close or option reset.

## Dependencies and Integration Points

The header includes `linux/types.h` and integrates with XDP programs, AF_XDP sockets, network drivers supporting zero-copy, NAPI, UMEM DMA mapping, and users such as libxdp/libbpf.

## Risks and Edge Cases

Ring synchronization and memory ordering are critical. Risks include invalid descriptors, unaligned chunk address decoding, multi-buffer packet continuation handling, zerocopy fallback, tx metadata length/placement, need-wakeup stalls, and driver support variation for checksum/timestamp/launch-time offloads.

## Test Signals

AF_XDP selftests should cover copy and zerocopy modes, shared UMEM, need-wakeup, scatter-gather, unaligned chunks, invalid descriptors, ring-full/empty stats, tx timestamp/checksum/launch-time metadata, and mmap offset correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_xdp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ife.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ife.h

## Purpose

`ife.h` defines the UAPI metadata IDs for Intermediate Functional Block Encapsulation metadata. The complete 19-line file was read.

## Important APIs, Types, and Functions

It defines `IFE_METAHDRLEN`, enum metadata IDs `IFE_META_SKBMARK`, `IFE_META_HASHID`, `IFE_META_PRIO`, `IFE_META_QMAP`, `IFE_META_TCINDEX`, and `IFE_META_MAX`.

## Control Flow

No code flow exists. Traffic-control IFE code uses these IDs to encode and decode skb metadata carried with encapsulated packets.

## State and Persistence Behavior

No state is stored here. IFE metadata values come from skb fields and tc action configuration at packet-processing time.

## Dependencies and Integration Points

The header has no includes and integrates with Linux traffic control actions and classifiers that manipulate skb mark/hash/priority/queue mapping/tc index metadata.

## Risks and Edge Cases

Metadata ID renumbering would break tc/user-space decoders. Runtime override of max metadata by module option means consumers should not assume every ID is always accepted.

## Test Signals

tc IFE tests should encode/decode each metadata type, verify max-ID handling, and check behavior when module options restrict supported metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ife.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/igmp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/igmp.h

## Purpose

`igmp.h` defines on-wire IGMP packet layouts, IGMPv3 report/query structures, record/type constants, host state constants, timing constants, and well-known multicast groups. The complete 130-line file was read.

## Important APIs, Types, and Functions

Structures are `igmphdr`, `igmpv3_grec`, `igmpv3_report`, and `igmpv3_query`. Constants cover IGMPv3 record types, packet type values such as membership query/report/leave and mtrace, BSD-compatible host member states, `IGMP_MINLEN`, delay/timer scale/age threshold, and multicast group addresses such as `IGMP_ALL_HOSTS`, `IGMP_ALL_ROUTER`, and `IGMPV3_ALL_MCR`.

## Control Flow

No implementation flow is present. Kernel and packet-processing code parse these on-wire structures, inspect type fields, handle endian-sensitive bitfields in IGMPv3 queries, and update multicast membership state elsewhere.

## State and Persistence Behavior

The header only defines packet layouts and constants. Membership state, timers, source filters, and router-version state live in IPv4 multicast code.

## Dependencies and Integration Points

It includes `linux/types.h` and `asm/byteorder.h`. It integrates with IPv4 multicast, bridge snooping, raw packet tools, routing daemons, and netfilter/packet parsers.

## Risks and Edge Cases

Flexible arrays and bitfields require length and endian validation. Risks include malformed `grec_nsrcs`/`ngrec`, query `qrv` and suppress bit ordering, checksum handling, and use of `htonl` group constants in UAPI code.

## Test Signals

Packet parser tests should cover IGMPv1/v2/v3 headers, multiple source records, truncated reports/queries, endian bitfield layout, checksum failures, leave/query timing, and bridge snooping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/igmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iio/buffer.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/iio/buffer.h

## Purpose

`iio/buffer.h` defines Industrial I/O buffer DMABUF UAPI objects and ioctls for exporting, attaching, detaching, and enqueuing DMA buffers. The complete 32-line file was read.

## Important APIs, Types, and Functions

It defines `IIO_BUFFER_DMABUF_CYCLIC`, `IIO_BUFFER_DMABUF_SUPPORTED_FLAGS`, `struct iio_dmabuf` with fd/flags/bytes_used, and ioctls `IIO_BUFFER_GET_FD_IOCTL`, `IIO_BUFFER_DMABUF_ATTACH_IOCTL`, `IIO_BUFFER_DMABUF_DETACH_IOCTL`, and `IIO_BUFFER_DMABUF_ENQUEUE_IOCTL`.

## Control Flow

User space obtains or supplies DMABUF file descriptors through ioctls, attaches them to an IIO buffer, queues transfers with `iio_dmabuf`, and the kernel/device driver consumes or fills the buffer.

## State and Persistence Behavior

DMABUF attachments and queued buffers are kernel IIO buffer state. `bytes_used` describes the active transfer amount, and cyclic mode persists for that queued buffer/attachment as interpreted by the driver.

## Dependencies and Integration Points

It includes `linux/types.h` and relies on ioctl macros from surrounding UAPI context. It integrates with IIO character devices, DMA-BUF, sensor/ADC/DAC drivers, and zero-copy data paths.

## Risks and Edge Cases

Risks include fd lifetime management, bytes_used exceeding DMABUF size, unsupported flags, cyclic transfer semantics, and driver-specific DMA constraints.

## Test Signals

IIO buffer tests should attach/detach valid and invalid DMABUF fds, enqueue normal and cyclic buffers, validate `bytes_used` limits, and verify ioctl error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iio/buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iio/events.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/iio/events.h

## Purpose

`iio/events.h` defines the Industrial I/O event delivery ABI, including event data layout, event-fd ioctl, and bit extraction helpers for packed event identifiers. The complete 43-line file was read.

## Important APIs, Types, and Functions

The key structure is `iio_event_data` with `id` and `timestamp`. It defines `IIO_GET_EVENT_FD_IOCTL` and macros to extract event type, direction, channel type, channel numbers, modifier, and differential flag from a packed event code.

## Control Flow

User space obtains an event fd via ioctl and reads `iio_event_data` records. The extraction macros decode the `id` field into semantic components supplied by IIO drivers.

## State and Persistence Behavior

The header owns no state. Event queues and timestamps are maintained in kernel IIO devices and exposed through the event fd.

## Dependencies and Integration Points

It includes `linux/ioctl.h` and `linux/types.h`, and integrates with IIO event-capable drivers and `iio/types.h` enum values.

## Risks and Edge Cases

Packed bit layouts are ABI. Risks include sign extension for 16-bit channel extraction, stale assumptions about event type-specific channel numbering, timestamp source consistency, and invalid user buffers.

## Test Signals

Tests should validate ioctl event-fd creation, event read format, extraction macro results for constructed IDs, timestamp ordering, and invalid/closed device behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iio/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iio/types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/iio/types.h

## Purpose

`iio/types.h` defines common Industrial I/O enum IDs for channel types, channel modifiers, event types, and event directions used in sysfs/event identifiers and driver/user-space contracts. The complete 140-line file was read.

## Important APIs, Types, and Functions

Enums are `iio_chan_type`, `iio_modifier`, `iio_event_type`, and `iio_event_direction`. They cover electrical, motion, light, environmental, chemical, orientation, mass concentration, chromaticity, attention, AC-current, many modifiers, threshold/change/gesture/fault event types, and rising/falling/singletap/doubletap/openwire directions.

## Control Flow

There is no control flow. Drivers publish channels/events using these enum values; user-space libraries map values to names and interpret event codes.

## State and Persistence Behavior

No state is held by the header. Channel/event state is in IIO device instances and generated event streams.

## Dependencies and Integration Points

The header has no includes and integrates with IIO drivers, sysfs ABI generation, event packing in `iio/events.h`, and user-space IIO tooling.

## Risks and Edge Cases

Enum order is ABI-like for event codes and naming tables. Adding values is safer than reordering. User-space must tolerate unknown newer values and handle modifier combinations consistently.

## Test Signals

Compile and ABI tests should verify enum-to-name tables, event code construction/extraction, and representative drivers for each channel/event category.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/iio/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ila.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ila.h

## Purpose

`ila.h` defines the generic-netlink UAPI for Identifier-Locator Addressing, including family metadata, attributes, commands, direction flags, checksum modes, identifier types, and hook types. The complete 68-line file was read.

## Important APIs, Types, and Functions

Constants include `ILA_GENL_NAME` and `ILA_GENL_VERSION`. Enums define `ILA_ATTR_*`, `ILA_CMD_ADD/DEL/GET/FLUSH`, checksum modes, address/identifier types, and route input/output hook types. Direction flags are `ILA_DIR_IN` and `ILA_DIR_OUT`.

## Control Flow

User space sends generic-netlink commands to add, delete, fetch, or flush ILA mappings. Kernel ILA code applies mappings at route input or output hooks and adjusts or preserves transport checksums according to the selected mode.

## State and Persistence Behavior

ILA locator/identifier mappings and hook configuration are kernel networking state. They persist until deleted or flushed.

## Dependencies and Integration Points

The header has no includes and integrates with generic netlink, IPv6 routing, checksum adjustment code, and user tooling for ILA.

## Risks and Edge Cases

Risks include checksum-neutral mapping errors, direction/hook mismatch, identifier type confusion, ifindex scoping, and generic-netlink attribute validation.

## Test Signals

ILA tests should cover add/get/delete/flush, input/output direction behavior, checksum modes, identifier types, invalid ifindex/attribute combinations, and packet checksum preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ila.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/in.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/in.h

## Purpose

`in.h` defines IPv4 socket UAPI types, protocol numbers, socket options, multicast request structures, packet-info layout, `sockaddr_in`, classful address macros, special addresses, and multicast constants. The complete 337-line file was read.

## Important APIs, Types, and Functions

It conditionally defines the `IPPROTO_*` enum, `in_addr`, socket option constants such as `IP_TOS`, `IP_TTL`, `IP_HDRINCL`, `IP_RECVERR`, multicast membership/source-filter options, PMTU discovery values, `ip_mreq`, `ip_mreqn`, `ip_mreq_source`, `ip_msfilter`, `group_req`, `group_source_req`, `group_filter`, `in_pktinfo`, `sockaddr_in`, classful address macros, `INADDR_*`, loopback/multicast helpers, and `IP_MSFILTER_SIZE`/`GROUP_FILTER_SIZE`.

## Control Flow

No implementation flow exists. Sockets code uses the constants and structures for `setsockopt`, `getsockopt`, ancillary data, multicast group management, route/PMTU behavior, and bind/connect address handling.

## State and Persistence Behavior

Socket options and multicast memberships persist on sockets. Address and protocol constants are stable ABI; actual routing, membership filters, and packet info are maintained by IPv4 networking code.

## Dependencies and Integration Points

It includes `linux/types.h`, `linux/stddef.h`, `linux/libc-compat.h`, `linux/socket.h`, and `asm/byteorder.h`. It integrates with libc header coordination, AF_INET sockets, multicast, routing, IPsec/XFRM, transparent proxying, MPTCP, and raw sockets.

## Risks and Edge Cases

Conditional `__UAPI_DEF_*` blocks must remain compatible with libc. Flexible multicast filters require size validation. Edge cases include source-filter counts, `IP_PMTUDISC_INTERFACE/OMIT`, local port range option, endian expectations for addresses, and protocol numbers beyond 255 such as SMC/MPTCP.

## Test Signals

UAPI compile tests with libc combinations, IPv4 socket option tests, multicast join/source-filter tests, ancillary `IP_PKTINFO` tests, PMTU mode tests, and struct-size compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/in6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/in6.h

## Purpose

`in6.h` defines IPv6 socket UAPI types, address structures, flow-label management, extension-header constants, socket option numbers, PMTU modes, source-address preferences, and multicast request layout. The complete 302-line file was read.

## Important APIs, Types, and Functions

Key types are `in6_addr`, `sockaddr_in6`, `ipv6_mreq`, and `in6_flowlabel_req`. Constants include flow-label actions/flags/share values, `IPV6_FLOWINFO_*`, obsolete priority values, extension header protocol numbers, TLV option IDs including IOAM, many `IPV6_*` socket options, PMTU discovery modes, RFC5014 source preference flags, original-destination/freebind/transparent options, and multicast option references shared with IPv4.

## Control Flow

No local flow is defined. IPv6 sockets and routing code use these values during bind/connect, flow-label management, setsockopt/getsockopt, ancillary data, multicast membership, PMTU handling, and extension-header processing.

## State and Persistence Behavior

Socket options, flow labels, multicast membership, and address preferences are kernel state. The header defines stable layouts and option IDs.

## Dependencies and Integration Points

It includes `linux/types.h` and `linux/libc-compat.h`, and coordinates with libc, AF_INET6 sockets, IPv6 routing, multicast, netfilter, IOAM TLVs, XFRM/IPsec, and advanced IPv6 API consumers.

## Risks and Edge Cases

Conditional libc-compat definitions and address union aliases are ABI-sensitive. Risks include flowinfo host/network byte-order confusion, scope-id handling, obsolete priority constants, PMTU mode semantics, and option-number gaps shared with netfilter/multicast routing.

## Test Signals

IPv6 socket option tests, flow-label manager tests, multicast join/leave tests, scope-id binding tests, ancillary data tests, libc include compatibility tests, and struct layout checks on 32/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/in6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/in_route.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/in_route.h

## Purpose

`in_route.h` defines IPv4 routing cache/route flags and a TOS extraction helper for UAPI consumers. The complete 33-line file was read.

## Important APIs, Types, and Functions

Constants include `RTCF_DEAD`, `RTCF_ONLINK`, obsolete `RTCF_NOPMTUDISC`, notification/redirect/NAT/broadcast/multicast/local flags, `RTCF_NAT`, and macro `RT_TOS(tos)`.

## Control Flow

No code flow exists. IPv4 routing code and user-space route consumers interpret route flags and TOS masks using these constants.

## State and Persistence Behavior

No state is held here. Route flags are stored in routing objects/messages elsewhere.

## Dependencies and Integration Points

It depends on route and TOS flag symbols such as `RTNH_F_*`, `RTM_F_NOPMTUDISC`, and `IPTOS_TOS_MASK` being visible through inclusion context. It integrates with IPv4 routing and rtnetlink route dumps.

## Risks and Edge Cases

Several flags are marked unused or obsolete but remain ABI. Removing them or changing values can break old tools. Include-order assumptions are also important.

## Test Signals

Route UAPI compile tests and route dump tests verifying local, multicast, broadcast, redirected, and NAT-related flag decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/in_route.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/inet_diag.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/inet_diag.h

## Purpose

`inet_diag.h` defines the inet socket diagnostics netlink ABI used to query TCP, DCCP, raw, and related sockets, including request/response layouts, bytecode filters, extension IDs, memory/congestion-control info, and socket option snapshots. The complete 248-line file was read.

## Important APIs, Types, and Functions

Important types include `inet_diag_sockid`, `inet_diag_req`, `inet_diag_req_v2`, `inet_diag_req_raw`, `inet_diag_bc_op`, `inet_diag_hostcond`, `inet_diag_markcond`, `inet_diag_msg`, `inet_diag_meminfo`, `inet_diag_sockopt`, `tcpvegas_info`, `tcp_dctcp_info`, `tcp_bbr_info`, and `tcp_cc_info`. Enums define request attributes, bytecode operations, timers, diagnostic extensions, ULP info attributes, and constants such as `INET_DIAG_NOCOOKIE`.

## Control Flow

User space sends netlink diagnostic requests with address family, protocol, state mask, socket identity, and optional bytecode filters. Kernel diag handlers scan socket tables, apply filters, and return `inet_diag_msg` plus requested extensions.

## State and Persistence Behavior

The header defines snapshots of live socket state. Socket queues, timers, uid/inode, congestion-control metrics, marks, cgroup IDs, and ULP info are owned by protocol stacks and reported at dump time.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `NETLINK_SOCK_DIAG`, TCP/DCCP/raw protocol tables, BPF storage reporting, TLS/MPTCP ULPs, cgroups, and tools such as `ss`.

## Risks and Edge Cases

`idiag_ext` in v2 is only 8 bits, so later extensions have special request aliases. Flexible address arrays and bytecode jumps require bounds checks. Cookie matching, CAP_NET_ADMIN-gated mark data, and raw protocol aliasing through `pad` are compatibility-sensitive.

## Test Signals

Socket diag tests should cover IPv4/IPv6 TCP/DCCP/raw requests, state masks, bytecode filters, extension dumps, congestion-control structs, ULP info, mark/cgroup/BPF storage attributes, and malformed filter rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/inet_diag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/inotify.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/inotify.h

## Purpose

`inotify.h` defines the inotify event record ABI, watch masks, special flags, aggregate event mask, init flags, and the `INOTIFY_IOC_SETNEXTWD` ioctl. The complete 84-line file was read.

## Important APIs, Types, and Functions

`struct inotify_event` contains watch descriptor, mask, cookie, name length, and flexible filename. Constants include all implemented watch events `IN_ACCESS` through `IN_MOVE_SELF`, generated events `IN_UNMOUNT`, `IN_Q_OVERFLOW`, `IN_IGNORED`, helper masks `IN_CLOSE`/`IN_MOVE`, flags `IN_ONLYDIR`, `IN_DONT_FOLLOW`, `IN_EXCL_UNLINK`, `IN_MASK_CREATE`, `IN_MASK_ADD`, `IN_ISDIR`, `IN_ONESHOT`, `IN_ALL_EVENTS`, `IN_CLOEXEC`, `IN_NONBLOCK`, and `INOTIFY_IOC_SETNEXTWD`.

## Control Flow

User space initializes an inotify fd, adds watches with masks, then reads one or more variable-length `inotify_event` records. Kernel fsnotify code queues events, supplies move cookies, marks overflow, and removes one-shot or ignored watches.

## State and Persistence Behavior

Inotify instances keep per-fd watch descriptors, masks, queues, and next watch descriptor state. Events persist in the queue until read or dropped on overflow.

## Dependencies and Integration Points

It includes `linux/fcntl.h` and `linux/types.h`. It integrates with fsnotify, VFS path/inode events, file-descriptor flags, and user-space file watchers.

## Risks and Edge Cases

Variable-length names require careful record iteration using `len`. Event queues can overflow, move cookies must be matched carefully, watch descriptors can be reused, and `IN_MASK_CREATE`/`IN_MASK_ADD` semantics differ.

## Test Signals

Inotify tests should cover all event masks, directory filename payloads, move cookies, queue overflow, one-shot watches, symlink and only-dir flags, nonblocking reads, close-on-exec, and `SETNEXTWD` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/inotify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/input-event-codes.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/input-event-codes.h

## Purpose

`input-event-codes.h` defines the Linux input subsystem's event type, property, key/button, axis, switch, misc, LED, repeat, sound, and sound-profile numeric codes. It is intentionally usable from C and device-tree source, so it contains comments and `#define`s only. The complete 1016-line file was read.

## Important APIs, Types, and Functions

Major groups are `INPUT_PROP_*`, `EV_*`, `SYN_*`, hundreds of `KEY_*` and `BTN_*` codes, `REL_*`, `ABS_*` including multitouch slots and tracking IDs, `SW_*`, `MSC_*`, `LED_*`, `REP_*`, `SND_*`, and `SND_PROFILE_*`. It also defines count/max helpers such as `EV_CNT`, `KEY_CNT`, `ABS_CNT`, and compatibility aliases like `KEY_HANGUEL`, `KEY_SCREENLOCK`, and `BTN_A`.

## Control Flow

No executable flow exists. Drivers emit events using these numeric codes; user-space input libraries decode event streams and advertise capability bitmaps with the same values.

## State and Persistence Behavior

The header owns no runtime state. Input device state and capability bitmaps live in kernel input devices; event values are read through `struct input_event` from `input.h`.

## Dependencies and Integration Points

It has no includes by design and is included by `input.h`, device-tree sources, input drivers, HID mappings, evdev clients, libinput, compositors, and keymap tools.

## Risks and Edge Cases

Because device-tree includes the file, adding anything beyond comments/defines is unsafe. Numeric code stability is critical. Reserved `REL_RESERVED` and `ABS_RESERVED` help users detect historical HID misuse; new keys must avoid inappropriate fallback to macro or vendor ranges.

## Test Signals

Signals include UAPI compile and devicetree parse tests, input capability bitmap tests, HID/keymap mapping tests, evdev decoding tests, and checks that max/count constants track the highest defined codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/input-event-codes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/input.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/input.h

## Purpose

`input.h` defines the evdev/input UAPI record layouts, ioctls, device ID and bus constants, multitouch tool types, force-feedback structures, force-feedback effect type constants, and compatibility timestamp layout. The complete 539-line file was read.

## Important APIs, Types, and Functions

Key structs are `input_event`, `input_id`, `input_absinfo`, `input_keymap_entry`, `input_mask`, `ff_replay`, `ff_trigger`, `ff_envelope`, `ff_constant_effect`, `ff_ramp_effect`, `ff_condition_effect`, `ff_periodic_effect`, `ff_rumble_effect`, `ff_haptic_effect`, and `ff_effect`. Important ioctls include `EVIOCGVERSION`, `EVIOCGID`, keycode get/set v1/v2, name/phys/uniq/property queries, `EVIOCGMTSLOTS`, capability/state queries, abs get/set, force-feedback upload/erase/count, grab/revoke, event mask get/set, and `EVIOCSCLOCKID`.

## Control Flow

Applications read `input_event` records from evdev fds and use ioctls to query or change device metadata, capabilities, absolute-axis calibration, event masks, and force-feedback effects. Kernel input core converts driver events into evdev records and applies per-client masks/grabs.

## State and Persistence Behavior

Per-device state includes capabilities, keymaps, abs info, repeat settings, force-feedback effect slots, and clock selection. Per-client state includes event masks, grabs, revocation, and read queues.

## Dependencies and Integration Points

It conditionally includes libc headers for user space, includes `linux/types.h`, and includes `input-event-codes.h`. It integrates with evdev, input drivers, HID, force-feedback drivers, libinput, SDL/game frameworks, and desktop stacks.

## Risks and Edge Cases

`input_event` timestamp layout varies with word size and `__USE_TIME_BITS64`; this is a core compat risk. Other risks include `__user *custom_data` in force-feedback uploads, variable ioctl buffer lengths, per-client event mask semantics, revoked fds returning `ENODEV`, and force-feedback effect ID limits around `FF_GAIN`.

## Test Signals

Input selftests should cover 32/64-bit timestamp layout, keymap v1/v2 ioctls, abs calibration, multitouch slot queries, event masks, grab/revoke, force-feedback upload/update/delete, and clock id selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring.h

## Purpose

`io_uring.h` is the primary io_uring UAPI header. It defines submission/completion queue entry layouts, operation codes, setup/enter/register flags, ring mmap offsets, feature flags, resource registration structures, restrictions, provided buffers, NAPI controls, wait/cancel arguments, socket uring-command operations, timestamp flags, and zero-copy receive integration. The complete 1065-line file was read.

## Important APIs, Types, and Functions

Key types include `io_uring_sqe`, `io_uring_attr_pi`, `io_uring_cqe`, `io_sqring_offsets`, `io_cqring_offsets`, `io_uring_params`, `io_uring_files_update`, `io_uring_region_desc`, `io_uring_mem_region_reg`, `io_uring_rsrc_register`, `io_uring_rsrc_update`, `io_uring_rsrc_update2`, `io_uring_probe_op`, `io_uring_probe`, `io_uring_restriction`, `io_uring_task_restriction`, `io_uring_clock_register`, `io_uring_clone_buffers`, `io_uring_buf`, `io_uring_buf_ring`, `io_uring_buf_reg`, `io_uring_buf_status`, `io_uring_napi`, `io_uring_reg_wait`, `io_uring_getevents_arg`, `io_uring_sync_cancel_reg`, `io_uring_file_index_range`, `io_uring_recvmsg_out`, and `io_timespec`. Enums cover SQE flags, `io_uring_op`, register operations, worker types, provided-buffer flags, NAPI op/tracking strategy, restriction ops, and socket operations.

## Control Flow

The UAPI models a shared-memory producer/consumer flow: user space calls `io_uring_setup`, mmaps rings/SQEs, writes SQEs, advances SQ tail, calls `io_uring_enter`, and consumes CQEs from the completion ring. Registration operations add buffers, files, rings, personalities, restrictions, NAPI settings, zcrx queues, memory regions, queries, and BPF filters.

## State and Persistence Behavior

Kernel ring state includes SQ/CQ heads/tails, features, registered resources, worker settings, restrictions, provided buffer rings, NAPI state, registered wait regions, zcrx state, and optional eventfd integration. User-visible state is shared through mmap offsets and CQE/SQE fields until ring teardown.

## Dependencies and Integration Points

It includes `linux/fs.h`, `linux/types.h`, `linux/io_uring/zcrx.h`, and optionally `linux/time_types.h`. It is shared with liburing and integrates with most kernel file/socket operations, registered files/buffers, networking, NAPI, BPF filters, zcrx, and memory-region registration.

## Risks and Edge Cases

This is dense ABI. Risks include union field aliasing by opcode, SQE/CQE 64/128 and 16/32 byte mixed-size modes, memory ordering on ring heads/tails, registered fd indexes, buffer-selection lifetime, `IORING_SETUP_SQ_REWIND` constraints, feature/flag probing, 32-bit compat layout, and evolving register opcodes.

## Test Signals

io_uring selftests should cover every opcode class, setup flags, ring mmap offsets, CQ overflow/skip/large CQEs, registered resources, provided buffers including incremental consumption, NAPI, restrictions, sync cancel, socket uring commands, zcrx registration, queries, BPF filters, and 32/64-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/bpf_filter.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/bpf_filter.h

## Purpose

`io_uring/bpf_filter.h` defines the UAPI for registering BPF filters that can inspect or gate io_uring operations. The complete 68-line file was read.

## Important APIs, Types, and Functions

Types are `io_uring_bpf_ctx`, `io_uring_bpf_filter`, and `io_uring_bpf`. The context exposes `user_data`, opcode, SQE flags, PDU size, and opcode-specific socket/open fields. Flags include `IO_URING_BPF_FILTER_DENY_REST` and `IO_URING_BPF_FILTER_SZ_STRICT`; command type `IO_URING_BPF_CMD_FILTER` selects filter registration.

## Control Flow

User space passes an `io_uring_bpf` registration command through io_uring registration. The kernel installs classic/eBPF-style filter instructions for the specified opcode, then supplies `io_uring_bpf_ctx` when evaluating submissions.

## State and Persistence Behavior

Installed filters persist on the ring until replaced, removed, or ring teardown. Deny-rest behavior can make unfiltered opcodes fail by default.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `IORING_REGISTER_BPF_FILTER` from `io_uring.h`, BPF instruction validation, and opcode-specific io_uring submission paths.

## Risks and Edge Cases

Strict PDU size matching can reject registrations across kernel/application version mismatches. Deny-rest can unexpectedly block operations. Opcode-specific context must stay synchronized with SQE interpretation.

## Test Signals

Tests should register allow/deny filters, use deny-rest mode, verify strict/non-strict PDU behavior, cover socket/open context fields, and confirm rejected submissions return expected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/bpf_filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/mock_file.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/mock_file.h

## Purpose

`io_uring/mock_file.h` defines a small test/mock-file UAPI for probing and creating io_uring mock files with configurable features and delay behavior. The complete 47-line file was read.

## Important APIs, Types, and Functions

It defines feature bits `IORING_MOCK_FEAT_*`, `io_uring_mock_probe`, create flags `IORING_MOCK_CREATE_F_SUPPORT_NOWAIT` and `IORING_MOCK_CREATE_F_POLL`, `io_uring_mock_create`, manager commands `IORING_MOCK_MGR_CMD_PROBE`/`CREATE`, mock command `IORING_MOCK_CMD_COPY_REGBUF`, and copy flag `IORING_MOCK_COPY_FROM`.

## Control Flow

Test/user code probes supported mock features, requests creation of a mock file with size and read/write delay, then exercises io_uring operations and mock commands against that fd.

## State and Persistence Behavior

Mock file state includes file size, delay, nowait/poll support, and feature set. It persists for the lifetime of the created fd.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with io_uring testing infrastructure, `IORING_OP_URING_CMD`, registered buffers, nowait, async, and poll behavior.

## Risks and Edge Cases

Because this is test-oriented UAPI, risk is mostly semantic drift between mock features and io_uring tests. Reserved fields must remain zeroed for forward compatibility.

## Test Signals

Mock-file tests should probe features, create files with and without nowait/poll, verify delayed I/O behavior, exercise registered-buffer copy commands, and reject unsupported flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/mock_file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/query.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/query.h

## Purpose

`io_uring/query.h` defines the io_uring query-registration ABI for discovering supported opcodes, ring/setup/enter flags, zcrx capabilities, and shared SQ/CQ header sizing. The complete 72-line file was read.

## Important APIs, Types, and Functions

Structures are `io_uring_query_hdr`, `io_uring_query_opcode`, `io_uring_query_zcrx`, and `io_uring_query_scq`. Query op IDs are `IO_URING_QUERY_OPCODES`, `IO_URING_QUERY_ZCRX`, and `IO_URING_QUERY_SCQ`.

## Control Flow

User space submits `IORING_REGISTER_QUERY` requests with a query header. The kernel fills query-specific payloads and can chain entries through `next_entry`.

## State and Persistence Behavior

The header reports capability state rather than storing state. Results describe the current kernel's supported request/register/query opcodes, feature flags, setup/enter/SQE flags, zcrx properties, and SQ/CQ header layout.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `io_uring.h`, zcrx registration, liburing capability probing, and no-ring query paths for opcode support.

## Risks and Edge Cases

Query payload sizes and chaining must be validated. User space must tolerate newer query opcodes and partial support. Capability bitmasks can exceed assumptions if code hard-codes old limits.

## Test Signals

Tests should query opcode support without a ring where allowed, query zcrx and SCQ data, validate size/result handling, chain multiple entries, and reject unknown query opcodes cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/query.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/zcrx.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/zcrx.h

## Purpose

`io_uring/zcrx.h` defines the io_uring zero-copy receive UAPI, including refill/completion entries, area registration, queue offsets, registration flags, feature flags, interface-queue registration, and control operations. The complete 115-line file was read.

## Important APIs, Types, and Functions

Types are `io_uring_zcrx_rqe`, `io_uring_zcrx_cqe`, `io_uring_zcrx_offsets`, `io_uring_zcrx_area_reg`, `io_uring_zcrx_ifq_reg`, `zcrx_ctrl_flush_rq`, `zcrx_ctrl_export`, and `zcrx_ctrl`. Enums define area flags, registration flags `ZCRX_REG_IMPORT`/`NODEV`, features such as `ZCRX_FEATURE_RX_PAGE_SIZE`, and control ops `ZCRX_CTRL_FLUSH_RQ` and `ZCRX_CTRL_EXPORT`. Offset area encoding uses `IORING_ZCRX_AREA_SHIFT` and `IORING_ZCRX_AREA_MASK`.

## Control Flow

User space registers a memory area and network receive queue through io_uring registration, mmaps or manages refill queue offsets, posts refill entries, receives zero-copy completions carrying offsets, and uses control ops to flush or export zcrx instances.

## State and Persistence Behavior

Zcrx state includes registered areas, optional DMABUF/imported memory, ifindex/RX queue binding, refill queue head/tail, zcrx ID, and rx buffer length. It persists until unregister/control teardown or ring close.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `io_uring.h`, netdev RX queues, memory-region descriptors, DMABUF import, NAPI/driver receive paths, and zcrx query reporting.

## Risks and Edge Cases

Zero-copy memory lifetime, DMA ownership, offset area encoding, nodev fallback, queue flush behavior, and rx page-size negotiation are high-risk. Reserved fields need zeroing for forward compatibility.

## Test Signals

Tests should register normal, imported, DMABUF, and nodev zcrx areas; validate refill/completion offsets; query features; flush queues; export instances; and exercise teardown while buffers are outstanding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/io_uring/zcrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioam6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ioam6.h

## Purpose

`ioam6.h` defines IPv6 IOAM option and trace header wire layouts, unavailable/default sentinel IDs, trace data size, and endian-sensitive trace-type bitfields. The complete 133-line file was read.

## Important APIs, Types, and Functions

Constants include unavailable/default IDs for 16/32/64-bit fields, `IOAM6_TYPE_PREALLOC`, and `IOAM6_TRACE_DATA_SIZE_MAX`. Structures are packed `ioam6_hdr` and `ioam6_trace_hdr`, with bitfield layouts for little- and big-endian builds and a flexible trace data array.

## Control Flow

No implementation flow exists. IPv6 IOAM insertion/parsing code reads or writes the option header, interprets namespace/type/nodelen/remlen/overflow fields, and appends trace data according to selected type bits.

## State and Persistence Behavior

No state is stored here. Per-namespace/default IDs and trace insertion policy live in IOAM kernel configuration and packet headers.

## Dependencies and Integration Points

It includes `asm/byteorder.h` and `linux/types.h`. It integrates with IPv6 Hop-by-Hop IOAM TLV handling, IOAM generic netlink namespace/schema config, and lightweight tunnel insertion.

## Risks and Edge Cases

Packed bitfields are endian-sensitive. Trace data is variable-length and bounded by 244 bytes. Risks include overflow flag handling, nodelen/remlen validation, reserved/unused bits, and alignment of packed network headers.

## Test Signals

IOAM packet tests should cover little/big endian bitfield expectations, preallocated trace insertion, overflow behavior, max trace data length, reserved-bit validation, and namespace/default ID encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioam6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_genl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_genl.h

## Purpose

`ioam6_genl.h` defines the IPv6 IOAM generic-netlink UAPI for namespaces, schemas, schema binding, and trace events. The complete 72-line file was read.

## Important APIs, Types, and Functions

Constants include `IOAM6_GENL_NAME`, `IOAM6_GENL_VERSION`, `IOAM6_MAX_SCHEMA_DATA_LEN`, and event multicast group `IOAM6_GENL_EV_GRP_NAME`. Enums define namespace/schema attributes, commands `ADD/DEL/DUMP_NAMESPACE`, `ADD/DEL/DUMP_SCHEMA`, `NS_SET_SCHEMA`, event types, and trace event attributes.

## Control Flow

User space manages IOAM namespaces and schemas through generic-netlink commands. Kernel IOAM code emits trace events with namespace, nodelen, trace type, and binary trace data through the event group.

## State and Persistence Behavior

Namespaces, schema data, and namespace-to-schema bindings are kernel IOAM state. They persist until deleted or reconfigured.

## Dependencies and Integration Points

The header has no includes and integrates with generic netlink, `ioam6.h` trace formats, IPv6 IOAM packet processing, and observability tooling.

## Risks and Edge Cases

Schema binary data length is bounded by `255 * 4`. Risks include namespace ID collisions, schema deletion while referenced, event payload sizing, and generic-netlink attribute validation.

## Test Signals

Generic-netlink tests should add/delete/dump namespaces and schemas, bind schemas to namespaces, reject oversized schema data, and verify trace event attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_genl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_iptunnel.h

## Purpose

`ioam6_iptunnel.h` defines lightweight tunnel attributes for IPv6 IOAM insertion, including insertion mode, destination/source addresses, trace header, and insertion frequency. The complete 64-line file was read.

## Important APIs, Types, and Functions

Enums define tunnel modes `IOAM6_IPTUNNEL_MODE_INLINE`, `ENCAP`, and `AUTO`, min/max mode helpers, attributes `IOAM6_IPTUNNEL_MODE`, `DST`, `TRACE`, `FREQ_K`, `FREQ_N`, and `SRC`, plus frequency bounds `IOAM6_IPTUNNEL_FREQ_MIN` and `IOAM6_IPTUNNEL_FREQ_MAX`.

## Control Flow

User space configures an lwtunnel route with IOAM attributes. Kernel routing/tunnel code inserts IOAM inline, encapsulates in ip6ip6, or chooses auto behavior for local versus transit packets, applying k/n packet frequency sampling.

## State and Persistence Behavior

IOAM tunnel mode, destination/source, trace header template, and insertion frequency are route/lwtunnel state and persist with the route.

## Dependencies and Integration Points

The header references `struct in6_addr` and `struct ioam6_trace_hdr` by contract and integrates with IPv6 lightweight tunnels, IOAM trace formatting, and rtnetlink route configuration.

## Risks and Edge Cases

Frequency must satisfy `0 < k <= n` within the documented range. Mode-specific address requirements differ; encap/auto need destination and optional source handling. Trace-header size and validation must match `ioam6.h`.

## Test Signals

Route/lwtunnel tests should configure inline/encap/auto modes, validate k/n boundaries, require destination where needed, check trace insertion on sampled packets, and reject malformed trace headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioam6_iptunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ioctl.h

## Purpose

`ioctl.h` is a small Linux UAPI wrapper that exposes architecture ioctl encoding macros by including `asm/ioctl.h`. The complete 8-line file was read.

## Important APIs, Types, and Functions

The only API surface is the include of `asm/ioctl.h`, which provides macros such as `_IO`, `_IOR`, `_IOW`, `_IOWR`, and related ioctl number encoding helpers.

## Control Flow

There is no control flow. Other UAPI headers include this wrapper to define ioctl command numbers portably.

## State and Persistence Behavior

No state is defined or modified.

## Dependencies and Integration Points

It depends entirely on the architecture-specific `asm/ioctl.h` and is included by many subsystem UAPI headers that define ioctl constants.

## Risks and Edge Cases

The wrapper preserves include-path compatibility. Changing it would affect broad ioctl command encoding across UAPI headers. Architecture-specific encoding must remain consistent with user-space libc expectations.

## Test Signals

UAPI compile tests should include `linux/ioctl.h` directly and through subsystem headers, verifying ioctl macros are visible and command numbers remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ioctl.h -->
