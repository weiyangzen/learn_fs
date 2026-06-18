# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8183-mmsys.h

## Purpose
This header provides MT8183 display routing constants and reset offset data for MMSYS.

## Important APIs, Types, and Functions
It defines `mmsys_mt8183_routing_table[]`, route constants for OVL to 2L overlays, RDMA, DITHER, DPI, DSI, and `MT8183_MMSYS_SW0_RST_B` for reset control. Routes cover the primary path and some secondary output selections.

## Control Flow and State
There is no local control flow. Runtime state is hardware register state set by `mtk_mmsys_ddp_connect()` and reset controller callbacks in `mtk-mmsys.c` using the reset offset.

## Dependencies and Integration Points
This header integrates with the MT8183 driver-data entry in `mtk-mmsys.c`, which sets `num_resets = 32`. It depends on the shared MMSYS route machinery and DDP component IDs.

## Risks and Test Signals
Route omissions are visible as broken display pipelines, especially OVL_2L and RDMA path failures. Reset offset mistakes can affect display block recovery. Test signals are DSI/DPI display bring-up, display reset testing, and DDP topology validation.
