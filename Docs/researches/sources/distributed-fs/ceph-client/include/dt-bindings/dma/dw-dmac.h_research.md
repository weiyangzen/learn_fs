# sources/distributed-fs/ceph-client/include/dt-bindings/dma/dw-dmac.h

## Purpose
Defines DesignWare DMAC AHB HPROT flag bits for DT configuration.

## Important APIs, Types, and Constants
Exports `DW_DMAC_HPROT1_PRIVILEGED_MODE`, `DW_DMAC_HPROT2_BUFFERABLE`, and `DW_DMAC_HPROT3_CACHEABLE`, corresponding to bits 0, 1, and 2. These are bit flags that may be ORed.

## Control Flow and State
No control flow. The DesignWare DMA driver interprets these flags when programming transfer protection/cache attributes.

## Dependencies and Integration Points
Self-contained binding used by DT DMA controller configuration and potentially DMA client properties.

## Risks and Test Signals
Incorrect flag composition can affect security attributes, buffering, or cacheability. Test signals include DT schema validation and DMA transfer tests on platforms using privileged, bufferable, or cacheable modes.
