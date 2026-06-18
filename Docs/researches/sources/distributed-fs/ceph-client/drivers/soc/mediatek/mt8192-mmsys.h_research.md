# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8192-mmsys.h

## Purpose
This header defines MT8192 MMSYS routing registers and table entries for display pipelines involving OVL, OVL_2L, RDMA, COLOR, CCORR, AAL, DITHER, DSI, and RDMA4.

## Important APIs, Types, and Functions
The exported data is `mmsys_mt8192_routing_table[]`. It includes OVL_2L0 to RDMA0, OVL_2L2 to RDMA4, DITHER0 to DSI0, CCORR to AAL0, RDMA0 to COLOR0, and OVL/OVL_2L blend selection entries.

## Control Flow and State
The file is declarative. The runtime driver applies matching route entries as masked register writes and uses `MT8186_MMSYS_SW0_RST_B` as the reset offset for MT8192 in the C file.

## Dependencies and Integration Points
It depends on shared DDP component IDs and route infrastructure. The MT8192 driver-data entry in `mtk-mmsys.c` uses this table and exposes 32 reset lines.

## Risks and Test Signals
Route correctness is critical for the multi-overlay display path and RDMA4 support. Test signals include main display bring-up, external display paths using RDMA4, DSI output, CCORR/AAL processing, and reset-controller smoke tests.
