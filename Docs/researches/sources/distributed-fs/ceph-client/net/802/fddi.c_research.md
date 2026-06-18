<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fddi.c -->
# sources/distributed-fs/ceph-client/net/802/fddi.c

This file implements generic FDDI net-device helpers. It exports `fddi_type_trans()` for receive protocol classification and `alloc_fddidev()` for FDDI device allocation.

`fddi_header()` pushes either a SNAP header for IP/IPv6/ARP or an 802.2 header form for other protocols, fills the FDDI frame-control byte, SNAP fields, source address, and optional destination address. `fddi_type_trans()` sets skb device and MAC header, pulls the correct header length, returns either `ETH_P_802_2` or the SNAP ethertype, and classifies broadcast/multicast/otherhost packet types. `fddi_setup()` initializes ARPHRD_FDDI type, header lengths, MTU range, address length, queue length, flags, and broadcast address.

State is per-device configuration and skb metadata; no persistent global state exists. Dependencies are FDDI header structures, skb pull/push rules, netdevice flags, and packet-type conventions.

Risks include assuming SNAP on receive, incorrect header pull on malformed frames, and promiscuous-mode classification edge cases. Tests should cover IP/IPv6/ARP and non-SNAP header construction, receive type translation for unicast/broadcast/multicast/otherhost frames, and device allocation defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/802/fddi.c -->
