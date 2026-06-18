# sources/distributed-fs/ceph-client/net/dsa/tag_lan9303.c

Purpose: DSA tag driver for SMSC/Microchip LAN9303 switches, which use a normal 802.1Q tag field with special VID semantics to encode destination or source port and control bits.

Important APIs/functions: `lan9303_xmit_use_arl()` chooses ALR lookup for bridged unicast traffic. `lan9303_xmit()` inserts the special VLAN tag. `lan9303_rcv()` removes either hardware-accelerated VLAN metadata or an in-frame VLAN tag and decodes source/trap bits. `lan9303_netdev_ops` registers `DSA_TAG_PROTO_LAN9303`.

Control flow: TX inserts `ETH_P_8021Q` plus either the ALR bit or direct destination port with STP override. RX pulls the VLAN tag, extracts source port from low bits, maps the user device, and only marks offload-forwarded packets when they were not trapped for IGMP/STP.

State and persistence: no tagger-owned state; it reads `struct lan9303` from `ds->priv` to know whether ports are bridged.

Dependencies and integration: depends on LAN9303 driver-private bridge state, Linux VLAN helpers, DSA etype helpers, and switchdev bridge offload semantics.

Risks and test signals: risks include ALR/direct mode misselection, bad handling of VLAN hardware acceleration, and STP/IGMP trap classification. Tests should cover bridged unicast, multicast/flooding, VLAN hwaccel and in-frame RX, invalid source ports, and bridge learning behavior.
