<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8183-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8183-larb-port.h

## Purpose
This header defines MT8183 larb IDs and M4U port IDs for display, VDEC, VPU/IPU, VENC, camera, WPE/DPE/MFB/RSC, and CCU clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB7_ID` and `M4U_PORT_*` constants using `MTK_M4U_ID`. Ports include display OVL/RDMA/WDMA/MDP, VDEC, image IPU, camera IPU, VENC, extensive camera larb5/6 ports, and `M4U_PORT_CCU0/1`.

## Control flow
DTS files reference these constants in IOMMU specifiers. The MediaTek IOMMU driver decodes larb/port fields to configure translation for each multimedia and camera master.

## State and persistence
The file is stateless. DTB port IDs are persistent; runtime state lives in SMI larbs, IOMMU page tables, and fault tracking.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8183 display, VDEC, VENC, VPU/IPU, camera, CCU, SMI, and IOMMU drivers.

## Risks and test signals
Risks include tab/spacing inconsistency hiding macro additions, camera larb6 port count approaching the 5-bit port field limit, and wrong IPU/camera larb split. Test signals include `dtbs_check`, multimedia and camera stream tests, CCU DMA tests, and fault decode validation for high-numbered camera ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8183-larb-port.h -->
