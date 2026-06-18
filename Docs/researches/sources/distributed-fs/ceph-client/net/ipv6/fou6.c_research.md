# sources/distributed-fs/ceph-client/net/ipv6/fou6.c

## Purpose
Provides IPv6 tunnel encapsulation operations for Foo-over-UDP (FOU) and Generic UDP Encapsulation (GUE), when `CONFIG_IPV6_FOU_TUNNEL` is enabled. It builds UDP outer headers for IPv6 tunnel packets and routes ICMPv6 errors back to the encapsulated protocol handlers.

## Important APIs, Types, and Functions
Important functions are `fou6_build_udp()`, `fou6_build_header()`, `gue6_build_header()`, `gue6_err()`, `gue6_err_proto_handler()`, `ip6_tnl_encap_add_fou_ops()`, and `ip6_tnl_encap_del_fou_ops()`. Registration uses `struct ip6_tnl_encap_ops fou_ip6tun_ops` and `gue_ip6tun_ops`.

## Control Flow
Header build first calls common FOU/GUE builders to create the encapsulation-specific header and source port/GSO type, then pushes an IPv6 UDP header, sets ports and length, computes or suppresses UDP checksum according to tunnel flags, and changes the next protocol to UDP. Error handling validates that enough bytes are present, parses GUE version/control/options, supports direct IPv4/IPv6 encapsulation for version 1, rejects unsupported control/UDP-recursive cases, temporarily rewinds transport header relative to the ICMPv6 header, and calls the encapsulated protocol's registered IPv6 error handler.

## State and Persistence
State is limited to registered encapsulation ops. Per-packet state is skb header positions and tunnel encapsulation parameters. If the config is disabled, registration functions are no-ops.

## Dependencies and Integration Points
Depends on common FOU/GUE helpers, IPv6 tunnel encapsulation registry, UDP checksum helpers, IPv6 protocol table, and ICMPv6 error delivery. Integrates with `ip6_tunnel` and protocol-specific error handlers such as IPIP/IPV6.

## Risks and Test Signals
Risks include incorrect UDP checksum flag semantics, GUE option length validation, transport-header restoration after errors, recursion through UDP encapsulation, and config-dependent silent no-op behavior. Test signals include IPv6 FOU and GUE tunnel transmit, checksum/no-checksum modes, GSO tunnel type flags, ICMPv6 PMTU/error delivery for GUE direct IPv4/IPv6 and full GUE headers, malformed GUE versions/options, and module registration failure unwinding.
