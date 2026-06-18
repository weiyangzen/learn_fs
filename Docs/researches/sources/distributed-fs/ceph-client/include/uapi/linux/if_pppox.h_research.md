
# sources/distributed-fs/ceph-client/include/uapi/linux/if_pppox.h

## Purpose

`if_pppox.h` defines the generic PPP-over-X socket ABI, especially PPPoE, PPTP, and protocol-specific PPPoL2TP sockaddr wrappers. The complete 154-line file was read.

## Important APIs, Types, and Functions

Important definitions include `AF_PPPOX`/`PF_PPPOX` fallback values, `sid_t`, `pppoe_addr`, `pptp_addr`, protocol IDs `PX_PROTO_OE`, `PX_PROTO_OL2TP`, `PX_PROTO_PPTP`, `sockaddr_pppox`, four L2TP-specific sockaddr variants, PPPoE discovery codes `PADI/PADO/PADR/PADS/PADT`, `pppoe_tag`, tag type constants `PTT_*`, `pppoe_hdr`, and `PPPOE_SES_HLEN`.

## Control Flow

No executable logic is present. User space fills the correct sockaddr for `bind()`/`connect()` on AF_PPPOX sockets; the kernel chooses PPPoE, PPTP, or L2TP handling based on `sa_protocol`. PPPoE packet parsing uses the packed header and variable tag arrays.

## State and Persistence Behavior

Socket addressing state persists in the PPPoX socket and PPP channel. PPPoE session IDs, peer MAC, device name, and L2TP/PPTP identifiers are kernel-managed after connection.

## Dependencies and Integration Points

The header includes type, byteorder, socket, interface, Ethernet, PPPoL2TP, IPv4, and IPv6 headers. It integrates with PPP generic channels, Ethernet discovery/session traffic, PPTP, and L2TP transport sockets.

## Risks and Edge Cases

Packed structures and endian-converted tag constants are ABI-sensitive. The comment notes that `sockaddr_pppox` could not be extended safely, so L2TP uses protocol-specific sockaddr types; consumers must use the correct size. PPPoE flexible tags require careful length validation.

## Test Signals

AF_PPPOX tests should cover PPPoE discovery/session header encoding, sockaddr sizes, L2TP v2/v3 IPv4/IPv6 connection paths, invalid protocol IDs, and endian correctness for tag constants.
