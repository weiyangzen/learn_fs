# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/rq_enet_desc.h

## Purpose
`rq_enet_desc.h` defines the 16-byte ENIC Ethernet receive descriptor format and inline encoder/decoder helpers.

## Important APIs, types, and functions
- `struct rq_enet_desc` contains a little-endian DMA address and packed length/type field.
- `enum rq_enet_type_types` defines `ONLY_SOP` and `NOT_SOP` descriptor type values.
- `rq_enet_desc_enc()` writes DMA address, 14-bit length, and 2-bit type in little-endian hardware format.
- `rq_enet_desc_dec()` reverses the packed fields for diagnostics or tests.

## Control flow and state
There is no standalone control flow. The helpers are called during RQ descriptor posting, after DMA buffer preparation and before the RQ posted-index update.

## Dependencies and integration points
The header is used by `enic_res.h` and receive-queue code. It depends on Linux endian types and the ENIC hardware descriptor ABI.

## Risks and test signals
Lengths beyond 14 bits are masked, so callers must provide hardware-valid buffer sizes. Test signals include RX buffer posting correctness, endian-safe descriptor inspection, and hardware acceptance of posted RQ descriptors.
