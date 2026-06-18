# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mt8188-mmsys.h

## Purpose
This header supplies MT8188 VDOSYS0 and VDOSYS1 MMSYS route tables, reset tables, and video pipeline register constants. It covers complex display/video routing through OVL, RDMA, DITHER, DSC, VPP MERGE, DSI, DP, DPI, MDP RDMA, and ETHDR mixer components.

## Important APIs, Types, and Functions
Important exported data includes `mmsys_mt8188_vdo0_rst_tb[]`, `mmsys_mt8188_vdo1_rst_tb[]`, `mmsys_mt8188_routing_table[]`, and `mmsys_mt8188_vdo1_routing_table[]`. Reset tables translate dt-binding reset IDs into MMSYS bank/bit numbers via `MMSYS_RST_NR`. The route tables encode both source-output and destination-input register fields.

## Control Flow and State
No code executes in the header. Runtime control is table-driven by the MMSYS driver: matching component pairs cause writes to VDO0/VDO1 selector registers, while reset controller operations translate external reset IDs through the tables.

## Dependencies and Integration Points
The file includes public MMSYS and MT8188 reset binding headers. It is bound in `mtk-mmsys.c` to `mediatek,mt8188-vdosys0` and `mediatek,mt8188-vdosys1`; VPP system compatibles are separate clock-only MMSYS instances.

## Risks and Test Signals
Risks include mismatched reset binding indices, selector-mask mistakes, and cross-subsystem routing errors between VDO0 and VDO1. Test signals are DP/DSI/DPI output, DSC and VPP merge paths, ETHDR mixer composition, reset controller consumers, and command queue register updates.
