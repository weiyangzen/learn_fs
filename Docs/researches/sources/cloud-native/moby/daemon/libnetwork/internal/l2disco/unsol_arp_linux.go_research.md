# Research: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_arp_linux.go

Purpose: constructs and sends unsolicited IPv4 ARP announcements on Linux. Important type/API are `UnsolARP`, `NewUnsolARP`, `Send`, `Close`, and helper `htons`.

Control flow: constructor opens an `AF_PACKET` datagram socket, clones a static ARP request template, copies sender MAC and IP into sender and target fields, builds a broadcast `SockaddrLinklayer` for the interface index and ARP protocol, and returns a sender object. `Send` calls `unix.Sendto`; `Close` closes the socket once and marks it invalid. `htons` converts protocol constants using native-endian interpretation of big-endian bytes.

State/dependencies: state is the raw packet bytes, socket descriptor, and link-layer sockaddr. Dependencies include Linux `unix`, standard net types, and slices. Integration point is L2 neighbor discovery/announcement after endpoint address changes. Risks include requiring Linux capabilities, no IP/MAC length validation beyond copy behavior, and no retry/backoff. Test signal is not local, likely integration-only because raw sockets need privileges.
