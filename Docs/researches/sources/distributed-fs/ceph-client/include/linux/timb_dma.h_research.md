<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_dma.h -->
# sources/distributed-fs/ceph-client/include/linux/timb_dma.h

## Purpose
defines platform data for the Timberdale DMA controller channels.

## Important APIs, Types, and Functions
The file is 44 lines and exports these visible symbol families: types/enums `timb_dma_platform_data_channel`, `timb_dma_platform_data`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
Board/platform code supplies channel names, DMA request lines, and byte-order flags through `timb_dma_platform_data`; the DMA driver consumes that table at probe to register channels.

## State and Persistence Behavior
The header stores no state; platform-data instances persist in board/device setup.

## Dependencies and Integration Points
It depends on DMA engine direction definitions and platform-device wiring in Timberdale MFD users. Direct includes are none.

## Risks and Edge Cases
Wrong request-line or byte-order data can route DMA to the wrong peripheral or swap data unexpectedly.

## Test Signals
Build Timberdale platform users, probe DMA channels, and run memory-to-device/device-to-memory transfers for each platform-data entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timb_dma.h -->
