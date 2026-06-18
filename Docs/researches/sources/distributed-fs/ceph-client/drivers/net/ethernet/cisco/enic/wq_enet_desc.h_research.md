# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/wq_enet_desc.h

## Purpose
`wq_enet_desc.h` defines the 16-byte ENIC Ethernet transmit descriptor format and inline encoder/decoder helpers.

## Important APIs, types, and functions
- `struct wq_enet_desc` stores DMA address, length, MSS/loopback, header/offload flags, and VLAN tag.
- Field masks and shifts define address, 14-bit length, 14-bit MSS, loopback, 10-bit header length, offload mode, EOP, CQ entry, FCoE encapsulation, VLAN insert, and VLAN tag fields.
- Offload modes include checksum, checksum-L4, and TSO.
- `wq_enet_desc_enc()` writes the hardware descriptor in little-endian packed format.
- `wq_enet_desc_dec()` decodes fields for diagnostics/tests.

## Control flow and state
Descriptor encoding is performed by ENIC TX queue helpers before `vnic_wq_post()` advances software queue state. The descriptor itself carries hardware offload instructions for the packet or segment.

## Dependencies and integration points
`enic_res.h` uses this header to implement TX descriptor posting variants. The ENIC transmit path must supply correct DMA address, offload, VLAN, SOP/EOP, and completion flags.

## Risks and test signals
Field-width masking can hide caller errors. Risks include wrong checksum/TSO mode, header length/MSS mismatch, VLAN insertion mistakes, and missing completion entries. Tests should cover checksum offload, TSO, VLAN-tag insertion, multi-fragment TX, loopback, and descriptor decode self-tests where available.
