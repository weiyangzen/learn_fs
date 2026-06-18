# sources/distributed-fs/ceph-client/include/dt-bindings/dma/axi-dmac.h

## Purpose
Defines bus-type constants for Analog Devices AXI DMAC bindings. The long comment describes whether the source and destination bus type cells are meaningful for different compatible strings and directions.

## Important APIs, Types, and Constants
Exports `AXI_DMAC_BUS_TYPE_AXI_MM` 0, `AXI_DMAC_BUS_TYPE_AXI_STREAM` 1, and `AXI_DMAC_BUS_TYPE_FIFO` 2. These constants encode memory-mapped AXI, AXI Stream, and FIFO endpoints.

## Control Flow and State
No executable flow. Runtime DMA transfer routing is configured by the AXI DMAC driver after parsing DT cells.

## Dependencies and Integration Points
Self-contained header used by AXI DMAC controller nodes and DMA client/device-tree descriptions that specify endpoint bus types.

## Risks and Test Signals
The risk is semantic mismatch between compatible string and bus type cells. Tests include `dtbs_check`, DTS compile coverage for memory-to-stream and stream-to-memory designs, and runtime DMA transfer tests.
