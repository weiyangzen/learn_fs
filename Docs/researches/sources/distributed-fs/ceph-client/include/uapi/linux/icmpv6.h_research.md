<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmpv6.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/icmpv6.h

## Purpose
`icmpv6.h` defines ICMPv6 wire-format constants, the base ICMPv6 header, raw-socket filters, and multicast listener constants used by IPv6 networking.

## Important APIs, types, and functions
`struct icmp6hdr` contains type, code, checksum, and unions for identifier/sequence, MTU/pointer/unused words, neighbor advertisement flags, and router advertisement fields. Constants cover router preference values, destination unreachable, packet-too-big, time exceeded, parameter problem, echo, multicast listener discovery, node information, MLDv2 reports, mobile IPv6 discovery, multicast router discovery, and extended echo. Macros map union members to names such as `icmp6_identifier`, `icmp6_sequence`, `icmp6_mtu`, `icmp6_router_pref`, and ND flags. `ICMPV6_FILTER` and `struct icmp6_filter` define raw-socket filtering; MLDv2 record type constants and `MLD2_ALL_MCR_INIT` support multicast listener reports.

## Control flow
IPv6 receivers parse the common header, dispatch by type/code, and interpret the union for echo, errors, neighbor discovery, router advertisement, MLD, and extended echo. Raw ICMPv6 sockets can set filters over the 256 possible message types.

## State and persistence behavior
ICMPv6 packets are transient, but ND/RA/MLD messages update neighbor cache, router state, multicast membership, and MTU state in the IPv6 stack. Socket filters are per-socket state.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<asm/byteorder.h>`. It integrates with IPv6, Neighbor Discovery, multicast listener discovery, router advertisement daemons, ping6, traceroute6, and firewalling.

## Risks and test signals
Risks include invalid type/code acceptance, endian mistakes in flags and MTU, router preference bit misuse, ICMPv6 filter mask errors, and incompatible handling of newer message types. Test signals include IPv6 ping/traceroute, ND conformance tests, RA/MLD daemon tests, packet-too-big PMTU behavior, raw-socket filter tests, MLDv2 report parsing, and raw-socket checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/icmpv6.h -->
