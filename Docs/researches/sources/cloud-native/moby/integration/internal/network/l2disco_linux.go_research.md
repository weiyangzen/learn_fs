# sources/cloud-native/moby/integration/internal/network/l2disco_linux.go

Purpose: Linux packet-capture helpers for collecting and decoding layer-2 discovery traffic such as unsolicited ARP and IPv6 neighbor advertisements.

Important APIs and types: `TimestampedPkt`, `CollectBcastARPs`, `CollectICMP6`, `collectPackets`, `UnpackUnsolARP`, and `UnpackUnsolNA`.

Control flow: collectors open AF_PACKET raw sockets on an interface, filter by ARP or ICMPv6 ethertype, start a goroutine reading packets with timestamps, and return a stop function that closes the socket and returns collected packets. `UnpackUnsolARP` parses Ethernet/ARP fields and returns sender hardware/protocol addresses for broadcast gratuitous ARP-like packets. `UnpackUnsolNA` parses Ethernet/IPv6/ICMPv6 neighbor advertisement and target link-layer option.

State and persistence: keeps captured packets in memory until stop. It opens raw sockets and reads live kernel network traffic.

Dependencies and integration: depends on Linux syscalls, `x/sys/unix`, `net`, `netip`, `encoding/binary`, and interface names from network tests.

Risks: Linux-only and requires permissions for raw packet sockets. Packet parsing is intentionally narrow and returns errors for unexpected lengths/types/options. Collection goroutine behavior depends on closing the socket to unblock reads.

Test signals: helper-only; enables tests to assert that network drivers emit expected L2 discovery packets.
