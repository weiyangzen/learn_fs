# Research: sources/cloud-native/moby/daemon/libnetwork/internal/l2disco/unsol_na_linux.go

Purpose: constructs and sends unsolicited IPv6 Neighbor Advertisements. Important type/API are `UnsolNA`, `NewUnsolNA`, `Send`, and `Close`.

Control flow: constructor opens an IPv6 ICMP packet socket bound to `::1`, wraps it in `ipv6.PacketConn`, blocks incoming ICMP with a filter, sets a control message with hop limit 255, source IP, and interface index, clones an NA template, and inserts target IP and MAC. `Send` writes the packet to the link-local all-nodes multicast address and verifies the full packet length was sent. `Close` closes the packet connection once.

State/dependencies: state is packet bytes, IPv6 packet connection, and control message. Dependencies include `golang.org/x/net/ipv6`, containerd logging, and net types. Integration point is IPv6 L2 discovery for container endpoints. Risks include requiring raw ICMP privileges, logging but not failing on ICMP filter setup errors, and the misleading comment saying `Send` sends ARP. Test signal is not local because real socket behavior is environment-dependent.
