<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2712-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2712-larb-port.h

## Purpose
This header defines MT2712 larb IDs and M4U port IDs for display, VDEC, CAM, VENC, MDP, and video output/write channels.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB6_ID` and `M4U_PORT_*` constants using `MTK_M4U_ID`, including display, VDEC external, camera, VENC, MDP RDMA/WROT, VDO, NR, TVD, and write channel ports.

## Control flow
Device-tree `iommus` specifiers reference these macros. The MT2712 IOMMU/SMI drivers decode the larb and port fields to attach each multimedia master to translation hardware.

## State and persistence
The header has no runtime state. DTB IDs are persistent board/SoC configuration; runtime state lives in IOMMU page tables and SMI larb registers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT2712 display/video/camera/MDP pipelines and MediaTek IOMMU drivers.

## Risks and test signals
Risks include mixed display/video port naming, wrong larb for video output channels, and port collisions from manual additions. Test signals include `dtbs_check`, IOMMU attach logs, display/camera/video DMA stress, and fault decoding by larb/port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2712-larb-port.h -->
