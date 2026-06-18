# sources/distributed-fs/ceph-client/drivers/net/bareudp.c

## Purpose
`bareudp.c` implements the BareUDP virtual tunnel netdevice. BareUDP encapsulates payloads such as MPLS, NSH, IP, or other configured ethertypes directly in UDP without an inner Ethernet header. The driver is controlled through rtnetlink, keeps per-netns device lists, creates one UDP tunnel socket per opened device, decapsulates received UDP packets into the configured protocol, and transmits packets using metadata supplied by the tunnel infrastructure.

## Important APIs, Types, and Functions
- `struct bareudp_net` stores the per-network-namespace device list.
- `struct bareudp_conf` captures netlink configuration: destination UDP port, ethertype, source-port minimum, and multiprotocol mode.
- `struct bareudp_dev` is the netdev private state: netns, netdev, ethertype, port, source port range, multiprotocol flag, RCU-protected socket, list node, and GRO cells.
- `bareudp_udp_encap_recv()` is the UDP tunnel receive callback.
- `bareudp_xmit()`, `bareudp_xmit_skb()`, and `bareudp6_xmit_skb()` implement IPv4/IPv6 transmit encapsulation from `skb_tunnel_info()`.
- `bareudp_fill_metadata_dst()` resolves route/source-port metadata for collect-metadata users.
- `bareudp_newlink()`, `bareudp_dellink()`, `bareudp_fill_info()`, and `bareudp_link_ops` expose rtnetlink creation, deletion, and introspection.
- `bareudp_net_ops` registers per-netns initialization and cleanup.

## Control Flow
Module init registers pernet state first, then rtnl link ops. Creating a link validates required netlink attributes (`PORT`, `ETHERTYPE`), rejects unsupported multiprotocol combinations, prevents duplicate ports in the same netns, registers the netdevice, and links it into the namespace list. Opening the device creates an IPv6 UDP socket when IPv6 is available, otherwise IPv4, enables UDP GSO, installs UDP tunnel callbacks, and stores the socket via RCU. Stopping clears the socket pointer, waits for network readers with `synchronize_net()`, and releases the UDP tunnel socket.

Receive starts in the UDP encap callback. It identifies outer address family, determines the inner protocol from configured ethertype plus optional multiprotocol inference (IPv4/IPv6 payload version or MPLS unicast/multicast based on outer destination), pulls the UDP header using `iptunnel_pull_header()`, attaches tunnel metadata, resets skb headers, validates inner network header availability, decapsulates ECN, and submits the skb through `gro_cells_receive()`. Transmit requires a valid configured inner protocol and `IP_TUNNEL_INFO_TX` metadata. The IPv4/IPv6 transmit helpers choose a UDP source port, resolve a route, check PMTU, scrub cross-netns packets, ensure headroom, handle offloads, and emit through `udp_tunnel_xmit_skb()` or `udp_tunnel6_xmit_skb()`.

## State and Persistence
Persistent runtime state is per-netns only: the list of devices and each device's config. Socket state exists only while the netdev is open and is protected by RCU. GRO cell state is initialized in `ndo_init` and destroyed in `ndo_uninit`. Stats are per-CPU device stats plus explicit error counters. There is no disk persistence.

## Dependencies and Integration Points
BareUDP depends on rtnetlink, pernet operations, UDP tunnel helpers, IP tunnel metadata, route lookup, ECN helpers, GRO cells, skb offload handling, and optional IPv6. User space integrates through `ip link add type bareudp ...` using `IFLA_BAREUDP_*` attributes. Datapath integration expects collect-metadata tunnel users to attach `struct ip_tunnel_info`.

## Risks
Transmit drops packets without tunnel metadata, with protocols outside configured/multiprotocol rules, or when the socket has not been opened. Multiprotocol MPLS receive infers unicast/multicast from the outer destination address, so policy errors can drop traffic. The duplicate-port check only compares ports, not ethertype, making port exclusive per netns. ECN errors may be logged unless the module parameter disables them. Correct RCU socket lifetime is critical around stop/uninit.

## Test Signals
Tests should verify netlink validation, duplicate port rejection, multiprotocol mode constraints, IPv4 and IPv6 socket creation, open/stop socket lifetime, receive decapsulation for configured ethertypes, IP multiprotocol IPv4/IPv6 detection, MPLS unicast/multicast behavior, ECN error accounting/logging, GRO delivery stats, metadata route filling, IPv4/IPv6 transmit encapsulation, PMTU behavior, and namespace cleanup deleting all devices.
