# sources/distributed-fs/ceph-client/include/linux/pim.h

## Purpose
Protocol Independent Multicast header definitions and helpers for IPv4 multicast routing PIM-SM/DM handling.

## Important APIs, Types, and Functions
Defines PIM v1/v2 version constants, PIM message type enum values from RFC 7761, `PIM_NULL_REGISTER`, `struct pimhdr`, `struct pimreghdr`, `pim_rcv_v1()`, `ipmr_pimsm_enabled()`, `pim_hdr()`, `pim_hdr_version()`, `pim_hdr_type()`, and `pim_ipv4_all_pim_routers()`.

## Control Flow
Network receive paths can extract the PIM header from an skb transport header, classify version/type, detect all-PIM-routers multicast address, and dispatch v1 handling via `pim_rcv_v1()`.

## State and Persistence
No owned persistent state. It interprets packet header bytes in `sk_buff` instances.

## Dependencies and Integration Points
Depends on skbuff, byte-order helpers, multicast routing config symbols, and IPv4 multicast router code.

## Risks
Packet parsing assumes transport header points at a complete PIM header. Version/type extraction relies on packed high/low nibbles. Endianness constants must be used for wire-format flags and addresses.

## Test Signals
PIM packet receive tests, multicast route tests with PIM-SM v1/v2 configs, malformed skb tests, and all-PIM-routers address matching.
