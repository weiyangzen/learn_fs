# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/txheader.h

## Purpose

`txheader.h` defines mlxsw transmit-header field accessors and constants. The transmit header is prepended to packets sent from the host CPU to the switch ASIC and tells hardware whether a packet is control or data, which port or multicast id to use, whether FID forwarding lookup is valid, and which protocol/type fields apply.

## Important APIs, Types, And Functions

The file uses `MLXSW_ITEM32` macros to define bitfield accessors for version, control/data type, protocol, router-origin flag, FID-valid flag, switch partition id, control traffic class, destination port/MID, FID, and packet type. Constants define header length (`MLXSW_TXHDR_LEN`), supported versions, Ethernet control/data values, Ethernet protocol value, traffic-class enum values, receive descriptor queue ids, CPU signature values, EMAD marker values, and data/control type values.

## Control Flow

There is no runtime control flow in this header. Tx paths allocate or access a 16-byte header and use the generated accessors to pack fields before sending packets to the ASIC.

## State And Persistence

The header defines packet metadata layout only. State exists transiently in skb/headroom buffers and hardware interpretation of each transmitted packet.

## Dependencies And Integration Points

It depends on the mlxsw item macro infrastructure, usually available from register/header packing includes. It integrates with EMAD/control packet paths, data packet injection, L2 forwarding through FID lookup, and CPU-port transmission.

## Risks And Edge Cases

Bit offsets and constants must match the ASIC transmit-header format exactly. Data packets and control packets use different semantics for destination fields; setting `fid_valid`, `port_mid`, or `type` incorrectly can misdirect traffic. Version and protocol fields have fixed required values.

## Test Signals

Useful tests are packet injection through control and data paths, EMAD operation, CPU-to-port transmission, FID-valid forwarding, and hardware drops caused by malformed tx headers. Static build coverage should catch missing accessor macro definitions. No local executable tests were run for this research item.
