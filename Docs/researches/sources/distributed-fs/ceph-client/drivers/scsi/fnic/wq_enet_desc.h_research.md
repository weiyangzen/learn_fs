# sources/distributed-fs/ceph-client/drivers/scsi/fnic/wq_enet_desc.h

## Purpose

`wq_enet_desc.h` defines the 16-byte Ethernet transmit/work queue descriptor used by Cisco vNIC hardware and helpers to encode/decode DMA address, length, offload, segmentation, FCoE, VLAN, and loopback fields.

## Important APIs, types, and data

- `struct wq_enet_desc` stores little-endian address, length, MSS/loopback, header-length/flags, and VLAN tag.
- Field masks and shifts define length, MSS, header length, offload mode, EOP, CQ entry request, FCoE encapsulation, VLAN tag insertion, and loopback.
- Offload modes include checksum, L4 checksum, and TSO.
- `wq_enet_desc_enc()` writes CPU values into descriptor bitfields.
- `wq_enet_desc_dec()` reads descriptor bitfields back to CPU-endian outputs.

## Control flow

Transmit code fills descriptors with `wq_enet_desc_enc()` before calling WQ post helpers. Debug/test code can decode descriptors for inspection. EOP and CQ-entry flags affect completion generation and packet segmentation.

## State and persistence behavior

Descriptor state persists in the DMA WQ ring until hardware consumes or the driver clears it. The header owns no software state.

## Dependencies and integration points

It depends on endian conversion helpers and integrates with `vnic_wq` transmit posting and completion handling.

## Risks and edge cases

- Length, MSS, header length, and offload mode are masked and silently truncated.
- Callers must supply semantically valid combinations, such as TSO with meaningful MSS/header length.
- EOP/CQ-entry flags directly affect completion behavior; incorrect flags can leak descriptors or lose completions.

## Test signals

Encode/decode tests should cover max field values, flag combinations, VLAN insertion, FCoE encapsulation, and TSO descriptors. Hardware tests should verify completions and packet output for each offload mode.
