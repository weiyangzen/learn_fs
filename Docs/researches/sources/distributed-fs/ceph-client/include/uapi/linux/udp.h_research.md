# sources/distributed-fs/ceph-client/include/uapi/linux/udp.h

Purpose: Defines the UDP packet header and Linux UDP socket option/encapsulation constants.

Important APIs/types/functions: `struct udphdr` contains big-endian source port, destination port, length, and checksum. Socket options include `UDP_CORK`, `UDP_ENCAP`, IPv6 checksum disable/accept controls, `UDP_SEGMENT` for GSO size, and `UDP_GRO`. Encapsulation types include ESP-in-UDP, L2TP, GTP0/GTP1U, RXRPC, ESP-in-TCP, and OpenVPN-in-UDP.

Control flow: Packet parsing reads `udphdr`; socket options alter send/receive paths, segmentation aggregation, checksum behavior, or encapsulation demultiplexing.

State and persistence behavior: Socket options are per-socket runtime state. Packet headers are wire-format transient data.

Dependencies and integration points: Includes `linux/types.h`; integrates with IPv4/IPv6 UDP stacks, tunnel drivers, xfrm, GTP, L2TP, RXRPC, OpenVPN, GRO/GSO offload, and packet capture tools.

Risks: Checksum disabling is protocol-sensitive. Encapsulation values overlap with other subsystems and must remain stable. `UDP_SEGMENT` requires correct MTU/offload validation.

Test signals: Validate UDP header layout, setsockopt/getsockopt behavior, UDP GSO/GRO, each encapsulation demux path, IPv6 checksum controls, and packet captures.
