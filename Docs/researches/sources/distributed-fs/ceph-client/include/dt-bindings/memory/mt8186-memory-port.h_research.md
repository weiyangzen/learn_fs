<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8186-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8186-memory-port.h

## Purpose
This header defines MT8186 IOMMU port IDs for display, MDP, VDEC, VENC/JPEG, WPE, image, camera, CCU, and IPE/FDVT clients. Comments document 16GB IOVA partitioning across display, vcodec, camera/MDP, and CCU.

## Important APIs, types, and functions
It exports `IOMMU_PORT_L*_*` macros built with `MTK_M4U_ID` across larbs 0, 1, 2, 4, 7, 8, 9, 11, 13, 14, 16, 17, 19, and 20. It includes reserved/fake ports and separate camera A/B larb variants.

## Control flow
MT8186 DTS nodes use the macros in IOMMU specifiers. The MediaTek IOMMU/SMI stack decodes the IDs into larb and port, then attaches masters to the configured DMA translation domain.

## State and persistence
The header has no state. DTB IDs persist; runtime state lives in IOMMU mappings, SMI power/clock state, and fault registers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8186 display, MDP, VDEC/VENC, WPE/image/camera, CCU, IPE, SMI, and IOMMU drivers.

## Risks and test signals
Risks include wrong IOVA region assignment, fake/reserved port misuse, and confusing `IOMMU_PORT_*` naming with older `M4U_PORT_*` consumers. Test signals include `dtbs_check`, IOMMU attach logs, DMA stress per subsystem, SMI larb suspend/resume tests, and fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8186-memory-port.h -->
