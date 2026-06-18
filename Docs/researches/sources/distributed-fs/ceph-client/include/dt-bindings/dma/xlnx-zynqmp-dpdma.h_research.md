# sources/distributed-fs/ceph-client/include/dt-bindings/dma/xlnx-zynqmp-dpdma.h

## Purpose
Defines Xilinx ZynqMP DisplayPort DMA channel IDs.

## Important APIs, Types, and Constants
Exports `ZYNQMP_DPDMA_VIDEO0`, `VIDEO1`, `VIDEO2`, `GRAPHICS`, `AUDIO0`, and `AUDIO1`, numbered 0 through 5. These are channel indexes for display pipeline layers and audio streams.

## Control Flow and State
No local control flow. Runtime transfer state belongs to the ZynqMP DPDMA driver.

## Dependencies and Integration Points
Self-contained header used by ZynqMP display/audio DT nodes that reference DPDMA channels.

## Risks and Test Signals
Channel swaps can corrupt displayed layers or audio routing. Test signals include DT schema validation and display pipeline tests for video, graphics overlay, and audio channels.
