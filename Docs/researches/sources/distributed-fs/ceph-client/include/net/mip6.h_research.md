<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mip6.h -->
# sources/distributed-fs/ceph-client/include/net/mip6.h

## Purpose
`mip6.h` declares the IPv6 Mobility Header wire structure and message type constants for Mobile IPv6 support.

## Important APIs, types, and functions
The main type is packed `struct ip6_mh`, containing next-header protocol, header length, type, reserved byte, checksum, and variable message data. Constants enumerate Binding Refresh Request, HoTI/CoTI, HoT/CoT, Binding Update, Binding ACK, and Binding Error.

## Control flow
There are no functions. IPv6 mobility code can cast validated packet payload to `struct ip6_mh`, inspect `ip6mh_type`, and dispatch to type-specific handling.

## State and persistence
The header defines no state. Packet state is transient in skbs and type-specific payloads after the header.

## Dependencies and integration points
It depends on skb and socket headers for consumers. It integrates with IPv6 extension-header and mobility-message processing.

## Risks and test signals
Risks include packed unaligned access, insufficient length validation before reading `data[]`, checksum coverage mistakes, and unknown type handling above `IP6_MH_TYPE_MAX`. Tests should cover truncated headers, every declared type, checksum validation, and endian-safe field reads.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mip6.h` completely for this pass (41 lines, 1016 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mip6.h -->
