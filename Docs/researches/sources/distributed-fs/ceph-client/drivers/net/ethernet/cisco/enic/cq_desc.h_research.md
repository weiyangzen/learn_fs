<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_desc.h

## Purpose

`cq_desc.h` defines the base ENIC/vNIC completion queue descriptor format and common field masks used to interpret completion entries.

## Important APIs, Types, and Definitions

`enum cq_desc_types` assigns hardware descriptor type values for Ethernet WQ, descriptor copy, exchange WQ, Ethernet RQ, and FCP RQ completions. `struct cq_desc` is the generic 16-byte layout: completed descriptor index, queue number, 11 bytes of type-specific payload, and a combined type/color byte. The masks and bit counts describe type, color, queue number, completion index, and fetch-index masks for larger CQ entry formats.

## Control Flow

No executable control flow exists. Polling code in vNIC/ENIC completion paths uses these definitions to decode completion type/color ownership and queue/completed indices.

## State and Persistence Behavior

The structures describe DMA-visible hardware memory. State is produced by the adapter in completion rings and consumed by the driver; it is not persisted.

## Dependencies and Integration Points

The header is included by `cq_enet_desc.h` and indirectly by RX/TX CQ service code. It depends on Linux bit macros and fixed-width little-endian types through included kernel headers in consumers.

## Risks and Edge Cases

Descriptor layout must remain exactly 16 bytes and match firmware/hardware. Incorrect type or color masks would cause ring ownership errors, missed completions, or queue misassociation.

## Test Signals

RX/TX completion processing, color wrap behavior, queue index decoding, and builds with 16/32/64-byte RX CQ formats are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/cisco/enic/cq_desc.h -->
