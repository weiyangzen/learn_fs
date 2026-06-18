<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt6893-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt6893-memory-port.h

## Purpose
This header defines MT6893 multimedia IOMMU/M4U port IDs by larb for display, MDP, video decode/encode, image, camera, CCU, and IPE/FDVT blocks. Comments document 16GB IOVA partitioning across display, vcodec, camera/MDP, and CCU regions.

## Important APIs, types, and functions
The exported macros are `M4U_PORT_L*_*` constants for larbs 0, 1, 2, 4, 5, 7, 9, 11, 13, 14, 16, 17, 18, 19, and 20. They use a MediaTek M4U ID helper and include domain suffixes such as `_MDP` and `_DISP` for some duplicated functional ports.

## Control flow
DTS IOMMU specifiers reference these macros for device ports. The MediaTek IOMMU/SMI driver decodes the larb and port portions to attach the correct hardware master and enforce the intended DMA address region.

## State and persistence
No state exists here. The IOMMU attachment and fault state live in runtime drivers and hardware; macro values persist in DTBs.

## Dependencies and integration points
It includes `mtk-memory-port.h` and integrates with MediaTek SMI larb, M4U/IOMMU, display, MDP, VDEC/VENC, camera, CCU, and IPE drivers.

## Risks and test signals
This file uses `MTK_M4U_DOM_ID`, while the included shared header in this tree defines `MTK_M4U_ID`; unless another include defines the DOM helper, DTS preprocessing will fail. Other risks include wrong larb-to-domain partitioning, null larb references, and duplicated port names mapped to the wrong 4GB window. Test signals include direct header preprocessing, `dtbs_check`, IOMMU attach logs, SMI larb probe, and DMA/fault tests for display, codec, camera, and CCU clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt6893-memory-port.h -->
