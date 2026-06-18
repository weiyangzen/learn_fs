# sources/distributed-fs/ceph-client/include/uapi/linux/l2tp.h

Purpose: defines the userspace ABI for L2TP-over-IP sockets and the generic netlink family used to manage L2TP tunnels and sessions.

Important APIs and types: `struct sockaddr_l2tpip` and `struct sockaddr_l2tpip6` encode IPv4/IPv6 L2TP-over-IP socket addresses with connection IDs. Generic netlink commands include tunnel/session create, delete, modify, and get operations. Attributes cover pseudowire type, encapsulation type, protocol version, interface name, connection/session IDs, cookies, sequencing flags, IP/UDP addressing, checksums, file descriptors, and nested stats. Enums define `l2tp_pwtype`, `l2tp_l2spec_type`, `l2tp_encap_type`, `l2tp_seqmode`, and debug flags. The family is `L2TP_GENL_NAME` version `L2TP_GENL_VERSION`.

Control flow: userspace creates sockets or sends generic netlink messages to create a tunnel, bind it to UDP or raw IP encapsulation, create sessions under that tunnel, then queries stats or deletes objects. Kernel validation keys off command-specific attributes.

State and persistence: no state in the header. Runtime state lives in kernel L2TP tunnel/session objects and netdevice/socket state. Stats attributes expose packet, byte, error, sequence discard, cookie discard, and invalid-packet counters.

Dependencies and integration points: depends on `linux/types.h`, `linux/socket.h`, `linux/in.h`, and `linux/in6.h`. Integrates socket address handling, generic netlink policy, L2TP netdevices, UDP/IP encapsulation, and userspace tunnel managers.

Risks and test signals: risks include sockaddr layout compatibility, netlink attribute length/type drift, unused legacy attributes misleading callers, and IPv6 zero-checksum handling mistakes. Test with generic netlink create/get/delete flows, IPv4 and IPv6 socket binding, UDP and IP encapsulation, cookie validation, stats reporting, and invalid attribute fuzzing.
