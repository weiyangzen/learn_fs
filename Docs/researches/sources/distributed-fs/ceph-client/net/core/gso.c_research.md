# sources/distributed-fs/ceph-client/net/core/gso.c

Purpose: Implements Generic Segmentation Offload dispatch and validation helpers. It routes GSO skbs to registered protocol segmentation callbacks and computes whether segmented packets would fit network or MAC length constraints.

Important APIs, types, and functions: `skb_eth_gso_segment()` dispatches by explicit ethertype; `skb_mac_gso_segment()` derives network protocol through possible VLAN headers and dispatches after temporarily pulling MAC/VLAN headers. `__skb_gso_segment()` is the main segmentation entry and handles checksum/head preparation and GSO partial feature filtering. `skb_gso_validate_network_len()` and `skb_gso_validate_mac_len()` validate post-segmentation sizes. Internal helpers compute transport, network, and MAC segment lengths and handle `GSO_BY_FRAGS`.

Control flow: Segmentation lookup scans `net_hotdata.offload_base` under RCU for a `gso_segment` callback matching the protocol. `__skb_gso_segment()` first ensures the skb is writable when checksum fields need to be initialized, trims `NETIF_F_GSO_PARTIAL` unless the device's partial features can actually support the skb, initializes `SKB_GSO_CB`, resets MAC metadata, and calls MAC-level segmentation. After callback return, it warns for bad offload if checksum verification was required but no error was returned. Validation computes expected per-segment lengths from header offsets, encapsulation state, TCP/SCTP/UDP_L4 type, and gso_size; `GSO_BY_FRAGS` walks frag_list children instead of using a constant payload size.

State and persistence: No independent persistent state. It reads skb shared info, device feature bits, GSO control block space, protocol offload registrations, and skb header pointers.

Dependencies and integration points: Shares `net_hotdata.offload_base` with GRO, depends on packet offload callbacks registered by protocol stacks, skb GSO metadata, checksum conventions, netdev feature flags, VLAN/network protocol helpers, and driver transmit feature negotiation.

Risks: Header pull/push imbalance can corrupt skb layout. Incorrect partial-GSO feature filtering may send unsupported packets to drivers. Length validation must handle encapsulation and `GSO_BY_FRAGS` accurately to avoid oversized segments. Checksum preparation differs between TX and RX/OVS paths.

Test signals: Segment TCPv4/v6, SCTP, UDP_L4, VLAN-tagged, encapsulated, and unsupported protocol skbs. Validate GSO partial acceptance/rejection against device features, checksum-needed paths, `GSO_BY_FRAGS` frag list sizes, network MTU checks, and MAC length checks. Confirm callback absence returns `-EPROTONOSUPPORT` and malformed protocol detection returns `-EINVAL`.
