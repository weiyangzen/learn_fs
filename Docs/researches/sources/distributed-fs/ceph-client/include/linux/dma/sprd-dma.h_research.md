<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/sprd-dma.h -->
# sources/distributed-fs/ceph-client/include/linux/dma/sprd-dma.h

## Purpose
Defines Spreadtrum DMA flags, two-stage transfer modes, request/interrupt modes, and link-list metadata.

## Important APIs, Types, And Functions
`SPRD_DMA_FLAGS()` packs channel mode, trigger mode, request mode, and interrupt type. Enums define channel roles for two-stage transfer, trigger points, request granularity, and interrupt types. `struct sprd_dma_linklist` carries virtual, physical, and wrap addresses for link-list mode.

## Control Flow
Slave drivers configure a DMA channel with packed flags. For two-stage transfers, source channel completion triggers a destination channel based on trigger mode. For link-list transfers, descriptors in always-on IRAM or coherent memory point to the next configuration, with the last node wrapping to the first.

## State And Persistence
State is DMA channel configuration and link-list descriptor memory. It persists only while the DMA channel and descriptor memory remain active.

## Dependencies And Integration Points
Integrates Spreadtrum peripheral drivers with the Spreadtrum DMA controller and DMAengine. Link-list mode depends on coherent or always-on memory visible to the controller.

## Risks And Edge Cases
Flag packing must match hardware bit fields. The comments contain transfer-state requirements: two-stage transfers require matching channel and trigger modes, and link lists must wrap correctly to avoid loading invalid configuration after the last descriptor. Descriptor memory must remain DMA-visible for the whole transfer.

## Test Signals
Tests should cover each request mode, interrupt type, two-stage trigger mode, source/destination channel pairing, link-list wrap behavior, config-error interrupt, and descriptor memory lifetime across suspend or clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dma/sprd-dma.h -->
