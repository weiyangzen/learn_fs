<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8365-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8365-larb-port.h

## Purpose
This header defines MT8365 SMI larb IDs and M4U port IDs for display, camera, MDP, VENC, and VDEC clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB3_ID` and `M4U_PORT_*` constants built with `MTK_M4U_ID`, including display OVL/RDMA/WDMA, camera IMGI/IMG2O/LSCI, MDP RDMA/WROT/WDMA, VENC ports, and hardware VDEC external ports.

## Control flow
MT8365 DTS nodes use the constants in `iommus` properties. The MediaTek IOMMU driver decodes each ID into larb and port values for SMI/IOMMU attachment.

## State and persistence
The file has no state. DTB port selections persist; runtime state is in IOMMU mappings and SMI hardware.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8365 SMI larb, display, camera, MDP, VENC, VDEC, and IOMMU drivers.

## Risks and test signals
Risks include assigning a port to the wrong larb, missing VDEC external port coverage, and DTS values drifting from driver larb data. Test signals include `dtbs_check`, IOMMU attach logs, multimedia DMA stress, and IOMMU fault decoding that reports expected larb/port pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8365-larb-port.h -->
