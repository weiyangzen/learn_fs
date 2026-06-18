# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_icrc.c

## Purpose
`rxe_icrc.c` computes and verifies the RoCE invariant CRC (ICRC) for RXE packets.

## Important APIs, types, and functions
`rxe_icrc_check()` compares a received packet's ICRC with a locally computed value. `rxe_icrc_generate()` writes the ICRC for outgoing packets. Internal helpers `rxe_crc32()` and `rxe_icrc_hdr()` compute cumulative CRC across masked network/transport headers, BTH, remaining RXE headers, payload, and padding.

## Control flow
The receive path calls `rxe_icrc_check()` after packet metadata is initialized. It locates the delivered ICRC at the end of the packet, computes a header CRC using a masked LRH seed, masks mutable IPv4/IPv6/UDP/BTH fields per RoCE ICRC rules, adds payload and pad bytes, complements the result, and returns `-EINVAL` on mismatch. The transmit path calls `rxe_icrc_generate()` before xmit and stores the complemented CRC in the packet trailer.

## State and persistence
No persistent driver state. It reads SKB protocol/header contents and writes the outgoing packet's ICRC field.

## Dependencies and integration points
The file depends on Linux `crc32_le`, IP/IPv6/UDP header layouts, RXE header accessors, opcode header length metadata, and net receive/transmit paths.

## Risks
Header masking must exactly match RoCE requirements. `rxe_icrc_hdr()` assumes receive validation has guaranteed enough header length; related receive code comments note short packets could otherwise underflow. IPv4 vs IPv6 protocol detection must match SKB setup.

## Test signals
Test ICRC generation/check for IPv4 and IPv6, varied payload sizes and padding, corrupted payload/header/trailer, mutable header fields that should be masked, and too-short packet rejection in receive before ICRC.
