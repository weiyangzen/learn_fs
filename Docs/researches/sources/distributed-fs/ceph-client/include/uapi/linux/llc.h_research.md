# sources/distributed-fs/ceph-client/include/uapi/linux/llc.h

Purpose: defines the IEEE 802.2 LLC userspace socket address, socket options, SAP constants, and ancillary packet-info ABI.

Important APIs and types: `struct sockaddr_llc` carries LLC family, ARP hardware type, TEST/XID/UA fields, SAP, MAC address, and padding. `enum llc_sockopts` defines retry, PDU size, timer expiry, TX/RX window, and packet-info options. Limits such as `LLC_OPT_MAX_RETRY`, `LLC_OPT_MAX_SIZE`, and timer maxima constrain socket options. `LLC_SAP_*` constants define well-known service access points. `struct llc_pktinfo` reports interface index, SAP, and MAC address.

Control flow: userspace opens AF_LLC sockets, binds/connects with `sockaddr_llc`, tunes LLC behavior through sockopts, and may receive packet metadata through `LLC_OPT_PKTINFO`.

State and persistence: socket option values, connection state, timers, and windows are kernel socket state. No persistent storage is defined here.

Dependencies and integration points: depends on `linux/socket.h` and `linux/if.h`; integrates LLC networking, Ethernet MAC addressing, ancillary data, and legacy protocol users.

Risks and test signals: risks include fixed sockaddr size/padding mismatch, invalid SAP values, option limit validation, timer overflow, and ancillary data layout drift. Test AF_LLC bind/connect/send/recv, sockopt boundaries, pktinfo delivery, and SAP-specific behavior.
