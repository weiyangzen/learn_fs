# sources/distributed-fs/ceph-client/drivers/net/geneve.c

### Purpose
`geneve.c` implements the Linux rtnetlink `geneve` virtual net_device and UDP tunnel endpoint for Generic Network Virtualization Encapsulation. It supports fixed endpoint tunnels and collect-metadata tunnels used by controllers such as Open vSwitch, IPv4 and IPv6 outer transport, per-network-namespace device and socket tracking, UDP tunnel offload announcements, GRO/GSO handling, ECN handling, and exported fallback device creation through `geneve_dev_create_fb()`.

### Important APIs, Types, And Functions
Key local state is split across `struct geneve_net`, `struct geneve_sock`, `struct geneve_dev`, and `struct geneve_config`. `geneve_net` owns per-netns device and socket lists. `geneve_sock` wraps one UDP socket, a reference count, collect-metadata/GRO-hint attributes, and a VNI hash table. `geneve_dev` is the netdev private area and stores IPv4/IPv6 socket RCU pointers, GRO cells, and the configured `ip_tunnel_info`.

Important entry points are `geneve_newlink()`, `geneve_changelink()`, `geneve_dellink()`, `geneve_open()`, `geneve_stop()`, `geneve_xmit()`, `geneve_udp_encap_recv()`, `geneve_gro_receive()`, `geneve_gro_complete()`, `geneve_fill_metadata_dst()`, and `geneve_dev_create_fb()`. Link registration is via `struct rtnl_link_ops geneve_link_ops`; runtime netdev operations are in `geneve_netdev_ops`.

Helper groups include VNI conversion and lookup (`vni_to_tunnel_id()`, `tunnel_id_to_vni()`, `geneve_lookup*()`), socket lifecycle (`geneve_socket_create()`, `geneve_sock_add()`, `geneve_sock_release()`), encapsulation (`geneve_build_header()`, `geneve_build_skb()`, `geneve_xmit_skb()`, `geneve6_xmit_skb()`), and netlink parsing/reporting (`geneve_validate()`, `geneve_nl2info()`, `geneve_fill_info()`).

### Control Flow
Creation starts in `geneve_newlink()`: defaults are prepared, netlink attributes are parsed by `geneve_nl2info()`, duplicate and collect-metadata conflicts are rejected by `geneve_configure()`, and the device is registered and linked into the per-netns list. `geneve_open()` creates or reuses UDP sockets for IPv4, IPv6, or both when collect metadata is enabled. Each opened socket gets UDP tunnel callbacks and stores a `geneve_sock` in `sk_user_data`.

RX enters through UDP encapsulation callbacks. `geneve_udp_encap_recv()` validates the Geneve base header and version, looks up the device by VNI/source address unless the socket is metadata mode, validates inner protocol policy, pulls the outer headers, optionally processes post-decap GRO hints, and calls `geneve_rx()`. `geneve_rx()` creates tunnel metadata when needed, rejects unsupported critical options outside metadata mode, converts Ethernet payloads with `eth_type_trans()` or sets packet host fields for inherited protocols, performs ECN decapsulation, then submits through GRO cells or directly to `netif_rx()` for hinted encapsulated packets.

TX starts in `geneve_xmit()`, which either consumes `skb_tunnel_info()` for collect-metadata mode or the static device config. IPv4 and IPv6 transmit paths perform VLAN/IP preparation, source port selection, route lookup with optional dst cache, PMTU checks and local EMSGSIZE loopback, TTL/TOS/DF selection, Geneve header construction, option copying, offload preparation, and final UDP tunnel send.

GRO flow parses Geneve headers and options in `geneve_gro_receive()`. A private netdev-class option can carry nested header hints for double encapsulation; the code validates offsets, protocols, checksums, and flow equivalence before handing the inner protocol to Ethernet or typed GRO callbacks.

### State And Persistence Behavior
All state is in kernel memory. Per-netns lists persist while the net namespace lives. Socket sharing is reference-counted by destination port, family, and GRO-hint setting. Device lookup from RX uses RCU-protected VNI hash lists. `dst_cache` persists route choices per `ip_tunnel_info` until reset. `geneve_changelink()` quiesces TX/RX by nulling RCU socket pointers and socket `sk_user_data`, synchronizes with in-flight users, updates config, then restores pointers.

There is no disk persistence. User-visible configuration is reflected through rtnetlink attributes from `geneve_fill_info()`.

### Dependencies And Integration Points
The driver integrates with rtnetlink, net namespaces, UDP tunnel sockets, `dst_metadata`, `ip_tunnel_info`, GRO cells, `udp_tunnel_*` transmit helpers, netdev notifier events for UDP tunnel offload port push/drop, ethtool driver info, IPv6 conditionals, and Open vSwitch style fallback creation exported as GPL.

### Risks
Risk areas are strict option and header length validation, collect-metadata exclusivity on a UDP port, RCU socket lifetime during changelink and teardown, GRO-hint trust boundaries, PMTU fallback behavior, IPv6 zero checksum choices, and compatibility with devices using `inner_proto_inherit`. Another important edge is shared socket attributes: sockets are reused only when family, port, and GRO-hint match, while `collect_md` is stored on the shared socket and guarded by config-level exclusivity.

### Test Signals
Useful signals include `ip link add type geneve` permutations for IPv4, IPv6, VNI, port range, DF, TTL/TOS, metadata, `inner_proto_inherit`, and GRO hint; duplicate tunnel and metadata-on-same-port rejection; packet RX/TX for Ethernet and inherited inner protocols; PMTU and ICMP generation; ECN decapsulation logging and stats; UDP tunnel offload notifier behavior; namespace teardown; and OVS collect-metadata fallback creation.
