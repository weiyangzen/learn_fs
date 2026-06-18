# sources/distributed-fs/ceph-client/include/uapi/linux/ipv6.h

## Purpose
`ipv6.h` exports IPv6 packet header, extension-header structures, socket ancillary-data structures, routing-header types, and IPv6 per-device configuration constants.

## Important APIs, Types, and Functions
Types include `in6_pktinfo`, `ip6_mtuinfo`, `in6_ifreq`, `ipv6_rt_hdr`, `ipv6_opt_hdr`, `rt0_hdr`, `rt2_hdr`, `ipv6_destopt_hao`, and `ipv6hdr`. The `ipv6hdr` layout uses endian-specific bitfields for priority/version and network-order flow label, payload length, next header, hop limit, and addresses. Constants define minimum MTU, deprecated and active routing header types, router alert values, and devconf enum entries.

## Control Flow
Userspace interacts through sockets, ancillary data, raw packet tooling, route configuration, and tunnel/IPsec stacks. The kernel parses these wire layouts during IPv6 receive/transmit and consults devconf values for per-interface behavior.

## State and Persistence
Header structures are transient packet/control data. Persistent state is in sockets, netdevice IPv6 devconf, routes, neighbor discovery, and namespaces.

## Dependencies and Integration Points
It includes libc compatibility gates, Linux integer/address types, and byteorder definitions. Integration points include IPv6 sockets, raw packet capture, iproute2, routing-header processing, segment routing, RPL, and MLD/router-alert handling.

## Risks and Test Signals
Tests should cover endian-sensitive header fields, extension-header length calculations, libc compatibility macro exposure, devconf enum stability, deprecated routing-header handling, and ancillary-data sizes on 32/64-bit userspace.
