<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arcnet.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_arcnet.h

## Purpose
`if_arcnet.h` defines ARCnet packet header formats, protocol IDs, and constants used by ARCnet network drivers and packet tools.

## Important APIs, types, and functions
The header defines ARCnet address/header lengths, MTU-related constants, protocol IDs for IP, ARP, RARP, Ethernet-encapsulated, diagnostics, and RFC1201/RFC1051 variants, plus structs for ARCnet hard headers, RFC1201 soft headers, RFC1051 headers, Ethernet-encapsulation headers, and cap-mode framing.

## Control flow
Drivers prepend ARCnet hard headers and protocol-specific soft headers, fragment/reassemble payloads according to ARCnet framing rules, and dispatch based on protocol ID. User space sees these layouts through packet sockets and captures.

## State and persistence behavior
Header fields are packet-local. Driver state such as node ID, fragmentation queues, and protocol mode lives in ARCnet netdevices.

## Dependencies and integration points
It depends on fixed-width UAPI types and integrates with legacy ARCnet drivers, packet sockets, ARP/IP support over ARCnet, and diagnostic tooling.

## Risks and test signals
Risks include incorrect fragmentation flags, soft-header variant confusion, MTU mismatch, legacy protocol ID handling, and struct packing assumptions. Test signals include ARCnet packet capture decoding, ARP/IP round trips, fragmentation/reassembly tests, unsupported protocol rejection, and header-size compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_arcnet.h -->
