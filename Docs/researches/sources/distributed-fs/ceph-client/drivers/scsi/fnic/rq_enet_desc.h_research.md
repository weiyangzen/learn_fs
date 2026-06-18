# sources/distributed-fs/ceph-client/drivers/scsi/fnic/rq_enet_desc.h

## Purpose

`rq_enet_desc.h` defines the 16-byte Ethernet receive queue descriptor used by Cisco vNIC/FNIC receive queues. It provides encode/decode helpers for DMA address, receive descriptor type, and buffer length.

## Important APIs, types, and data

- `struct rq_enet_desc` contains a little-endian 64-bit buffer address, a little-endian combined length/type field, and reserved bytes.
- `enum rq_enet_type_types` defines SOP-only and non-SOP descriptor type values.
- `RQ_ENET_LEN_MASK` and `RQ_ENET_TYPE_MASK` bound the 14-bit length and 2-bit type fields.
- `rq_enet_desc_enc()` writes CPU values into descriptor endian format.
- `rq_enet_desc_dec()` reads descriptor values back into CPU-endian outputs.

## Control flow

Receive-buffer preparation calls `rq_enet_desc_enc()` before posting descriptors to hardware. Debug or cleanup paths can call `rq_enet_desc_dec()` to inspect descriptor contents. The type is stored in bits above the length inside `length_type`.

## State and persistence behavior

The descriptor is persistent only as DMA ring memory shared with hardware. The header owns no mutable state.

## Dependencies and integration points

It depends on Linux endian helpers `cpu_to_le64()`, `cpu_to_le16()`, `le64_to_cpu()`, and `le16_to_cpu()`. It is integrated with `vnic_rq` rings and any FNIC receive path that posts Ethernet/FCoE receive buffers.

## Risks and edge cases

- Length is truncated to 14 bits; callers must ensure buffer sizes fit.
- Reserved type values are not rejected by the encode helper.
- The descriptor must be fully initialized before the RQ posted index is advanced, which is enforced by queue-level memory barriers rather than this header.

## Test signals

Unit-style encode/decode round trips for boundary lengths and all type values are useful. Runtime receive tests should verify hardware consumes posted descriptors and reports completions with the expected buffer address and length.
