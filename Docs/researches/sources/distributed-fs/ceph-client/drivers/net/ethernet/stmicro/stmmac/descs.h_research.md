# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs.h

## Purpose
`descs.h` defines legacy DWMAC100/1000 normal, enhanced, and extended DMA descriptor bitfields and structures used by STMMAC descriptor operations.

## Important APIs, Types, And Functions
- RX normal descriptor bits cover checksum, CRC, dribble, MII, watchdog, frame type, collision, first/last, VLAN, overflow, length, filter failures, error summary, frame length, and ownership.
- RX enhanced/extended bits add alternate buffer sizing, chained/ring markers, PTP message metadata, timestamp drop, AV/VLAN/L3/L4 filter metadata.
- TX normal/enhanced bits cover collisions, carrier, payload/header errors, timestamp status, checksum insertion, padding/CRC controls, first/last segment, interrupt, chained/ring markers, and ownership.
- `struct dma_desc` is the four-word basic descriptor.
- `struct dma_extended_desc` adds extended status and timestamp words after the basic descriptor.
- `struct dma_edesc` supports enhanced descriptor layout for TBS with extra words before the basic descriptor.
- `dma_desc_to_edesc()` converts a basic descriptor pointer to the enclosing enhanced descriptor.
- `TX_CIC_FULL` encodes full checksum insertion.

## Control Flow
No control flow; descriptor ops and mode ops use these constants to interpret and prepare descriptors.

## State And Persistence
The structures define DMA-coherent memory shared with hardware. Values persist while rings are active and are updated by both CPU and DMA engine.

## Dependencies And Integration Points
Included by `common.h` and descriptor implementation files. The bit definitions are coupled to STMMAC normal/enhanced descriptor ops, timestamping, checksum offload, VLAN, and filtering.

## Risks
- Bitfield mistakes directly corrupt DMA ownership or status handling.
- Layout differences among normal, enhanced, extended, and TBS descriptors require callers to use the correct operations table.
- Endianness conversion must be handled by users of these fields; raw constants are CPU-side definitions.

## Test Signals
Traffic tests with checksum offload, VLAN, PTP timestamping, jumbo frames, ring and chain modes, and descriptor error injection validate these definitions. Compile coverage should include normal, enhanced, extended, and TBS descriptor users.
