# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_dma.h

## Purpose
`fsl_dma.h` defines the CCSR/Elo DMA register layout, mode/status/attribute bitfields, address helper macros, and packed/aligned list and link descriptor formats used by the Freescale SSI DMA PCM driver.

## Important APIs, Types, and Definitions
- `struct ccsr_dma` and nested `struct ccsr_dma_channel` model the memory-mapped DMA controller and per-channel registers.
- Mode register macros define bandwidth count, external master pause/start, transfer sizes, address hold enable, snoop/read-write flags, interrupt enables, channel abort, chaining mode, and start bits.
- Status register macros define transmit error, channel halt, programming error, end-of-link/list, channel busy, and end-of-segment conditions.
- `CCSR_DMA_ECLNDAR_ADDR()` and `CCSR_DMA_CLNDAR_ADDR()` split link descriptor addresses for current/extended registers.
- Attribute macros define platform/bus attributes, no-snoop/snoop encodings, and extended source/destination address bits.
- `struct fsl_dma_list_descriptor` and `struct fsl_dma_link_descriptor` describe 32-byte aligned hardware descriptors for chaining.

## Control Flow and Usage
The header has no executable flow. `fsl_dma.c` uses the register layout with big-endian MMIO accessors, writes mode/status/address registers, and fills link descriptors in coherent memory. Helper macros convert physical addresses and field values to the hardware's expected register fields.

## State and Persistence
State represented here is hardware register state and coherent descriptor memory. Descriptor structures are owned by the PCM runtime and consumed by the DMA controller until stream close/hw_free.

## Dependencies and Integration Points
The header depends on kernel integer and endian types. It is tightly coupled to the CCSR DMA controller manual and the `fsl_dma.c` PCM implementation. Descriptor alignment/packing is part of the hardware ABI.

## Risks and Edge Cases
- Field macros assume valid inputs; for example `CCSR_DMA_MR_BWC(x)` calls `ilog2(x)` and expects a positive bandwidth count.
- Descriptor structures must remain exactly aligned and packed; compiler or manual layout changes would break DMA hardware reads.
- 36-bit address support depends on upper bits being written consistently in register and descriptor attributes.
- Status and mode constants are raw bit values with no type safety.

## Test Signals
- Build and sparse/endian checks should validate big-endian field usage.
- Hardware descriptor dumps during playback/capture should show correct ring pointers, counts, snoop attributes, and extended address bits.
