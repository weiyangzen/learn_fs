# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/descs_com.h

## Purpose
`descs_com.h` provides inline helpers for preparing normal and enhanced descriptors in ring and chained modes.

## Important APIs, Types, And Functions
- Ring-mode RX helpers set second-buffer size and end-ring bits for enhanced or normal descriptors.
- Ring-mode TX helpers set/clear end-ring bits and encode TX length across buffer 1 and buffer 2 masks.
- Chain-mode RX/TX helpers mark descriptors as second-address-chained.
- Chain-mode length helpers encode TX buffer length into the appropriate normal/enhanced mask.

## Control Flow
The inline helpers are called by descriptor operation implementations when initializing/refilling descriptors or preparing TX descriptors. Ring helpers branch on end-of-ring and buffer size; chain helpers set fixed chained bits.

## State And Persistence
They mutate hardware-visible descriptor fields in DMA memory. No additional state is stored.

## Dependencies And Integration Points
These helpers depend on `struct dma_desc`, descriptor bit definitions from `descs.h`, buffer size constants, `FIELD_PREP()`, and little-endian conversion. They are shared by ring and chain descriptor implementations.

## Risks
- The enhanced TX ring helper intentionally caps buffer 1 at 4 KiB despite a larger hardware mask; callers must understand split behavior.
- Incorrect `end` or buffer-size inputs can break ring wrap or overflow descriptor length fields.
- Because helpers OR fields into descriptors, callers must zero or mask descriptors before reuse.

## Test Signals
Ring wrap tests, chain mode traffic, jumbo frames, enhanced and normal descriptor modes, and static inspection for proper descriptor zeroing before helper use.
