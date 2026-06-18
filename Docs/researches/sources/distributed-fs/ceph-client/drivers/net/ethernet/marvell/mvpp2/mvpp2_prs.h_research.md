# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/mvpp2/mvpp2_prs.h Research

## Purpose
`mvpp2_prs.h` defines the internal contract for the MVPP2 parser. It describes parser table dimensions, TCAM and SRAM bit layouts, reserved row ranges, result-info and additional-info encodings, lookup identifiers, shadow metadata, parser entry storage, and the public parser helper API used by the rest of the driver.

## Important APIs, Types, And Functions
The header defines `MVPP2_PRS_TCAM_SRAM_SIZE`, TCAM/SRAM word counts, flow-id size and masks, byte-to-word helpers, TCAM enable/data fields, reserved parser entry IDs, per-port MAC and VID filter ranges, SRAM offsets for RI, shift, UDF, AI, next lookup, done/generate bits, and RI masks for MAC, DSA, VLAN, CPU special packets, L2/L3/L4 protocol classification, fragmentation, UDF fields, and drop decisions. `enum mvpp2_prs_udf` identifies shadow UDF categories, and `enum mvpp2_prs_lookup` names the parser stages from `MVPP2_PRS_LU_MH` through `MVPP2_PRS_LU_FLOWS`.

The main data structures are `struct mvpp2_prs_entry`, `struct mvpp2_prs_result_info`, and `struct mvpp2_prs_shadow`. The declared API covers initialization, hardware row readback, TCAM data inspection, MAC DA filtering, tag mode updates, custom flow rows, default flow selection, VID filter enable/disable/add/remove, promiscuous mode, MAC filter cleanup, netdev MAC address update, and hit counter access.

## Control Flow
The header does not implement control flow, but it fixes the parser state machine consumed by `mvpp2_prs.c`: packet parsing starts at Marvell-header lookup, advances through MAC, DSA, VLAN, VID, L2, PPPoE, IPv4/IPv6, and ends at flow lookup. The reserved entry IDs encode where default and dynamic rows are expected to live, so callers indirectly depend on those ranges when invoking runtime update helpers.

## State, Persistence, And Dependencies
The header owns no storage itself. It defines the shape of persistent state stored in hardware and mirrored in `struct mvpp2_prs_shadow`. It depends on `mvpp2.h` for register and device types and includes kernel netdevice/platform headers for `struct mvpp2`, `struct mvpp2_port`, `struct net_device`, and address/VID-facing APIs.

## Integration Points
This is included by `mvpp2_prs.c` and by MVPP2 modules that need parser lifecycle or filter updates. The constants also tie parser RI values to downstream classifier and receive logic, since result-info bits tell later hardware/software whether a frame is dropped, addressed to the port, VLAN tagged, ARP/IP/PPPoE, fragmented, TCP/UDP, or special CPU-directed traffic.

## Risks
The file hardcodes parser row partitioning and assumes three VID-filtered ports, fixed 256-row hardware, and specific TCAM/SRAM bit packing. Any hardware variant with different row count, lookup encoding, or filter capacity requires coordinated changes here and in `mvpp2_prs.c`. Because many macros are raw bit positions, overlap errors are easy to introduce and hard to detect by compilation. The API exposes low-level parser mutation primitives broadly inside the driver, so call ordering and locking expectations must be respected by consumers.

## Test Signals
Compile coverage should catch most type and prototype changes. Runtime test signals mirror parser behavior: parser default initialization, all parser lookup transitions, MAC and VLAN filter capacity boundaries, DSA/EDSA modes, flow-id generation, drop decisions from RI masks, hit counter access, and traffic classification for L2, PPPoE, IPv4, IPv6, multicast, broadcast, fragmented, and unknown-protocol packets.
