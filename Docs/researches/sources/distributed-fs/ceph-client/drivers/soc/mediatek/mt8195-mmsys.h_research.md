# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8195-mmsys.h

## Purpose
This header provides MT8195 VDOSYS0, VDOSYS1, and VPPSYS-related routing constants. It represents a complex video/display fabric with OVL, WDMA, DITHER, DSC, MERGE, DSI, DPI, DP, MDP RDMA, and ETHDR mixer paths.

## Important APIs, Types, and Functions
The key exported arrays are `mmsys_mt8195_routing_table[]` and `mmsys_mt8195_vdo1_routing_table[]`. The header also defines VPP DCM and resize-merge registers used by exported MMSYS helper functions in `mtk-mmsys.c`, such as `mtk_mmsys_vpp_rsz_merge_config()` and `mtk_mmsys_vpp_rsz_dcm_config()`.

## Control Flow and State
All behavior is declarative here. Runtime state consists of selector fields and MOUT/SOUT bits programmed by `mtk_mmsys_update_bits()` from the C driver. VPP DCM and resize-merge bits are toggled by exported helper functions.

## Dependencies and Integration Points
This header is included by `mtk-mmsys.c` for MT8195 VDO0/VDO1 and VPP systems. It integrates with DRM display topology, MDP/video processing, and optional CMDQ-backed register programming.

## Risks and Test Signals
The route matrix contains many paths sharing the same registers with different masks, so small mask or shift errors can affect unrelated outputs. Comments marked `NEED CONFIRM` are not in this file but adjacent PMIC data shows similar SoC bring-up risk. Test signals include DSI0/DSI1, DP0/DP1, DPI0/DPI1, DSC, VPP merge, WDMA, ETHDR mixer, and MDP pipeline validation.
