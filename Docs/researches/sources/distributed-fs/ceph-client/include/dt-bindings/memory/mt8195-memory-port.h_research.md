<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8195-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8195-memory-port.h

## Purpose
This header defines MT8195 multimedia and infra IOMMU port IDs. It spans VDO/VPP display, MDP, WPE, image, camera, CCU, VDEC/VENC/JPEG, and infra PCIe/USB clients, with comments documenting two MM IOMMUs and 16GB IOVA partitioning.

## Important APIs, types, and functions
It exports many `M4U_PORT_L*_*` macros built with `MTK_M4U_ID` for software larbs, plus `IOMMU_PORT_INFRA_*` macros built with `MTK_IFAIOMMU_PERI_ID` for PCIe and SSUSB read/write ports.

## Control flow
MT8195 DTS nodes use the constants in IOMMU specifiers. MediaTek MM IOMMU drivers decode larb/port values for multimedia masters, while infra IOMMU consumers use peri IDs for PCIe/USB clients.

## State and persistence
There is no header state. Port IDs persist in DTBs; runtime mapping, fault, and SMI state lives in the IOMMU and SMI drivers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8195 VDO/VPP, display, MDP, WPE, IMG, CAM, CCU, VDEC/VENC/JPEG, PCIe, USB, SMI, MM IOMMU, and infra IOMMU code.

## Risks and test signals
Risks include wrong software larb reindexing, assigning a port to the wrong MM IOMMU, confusing infra peri IDs with MM larb IDs, and crossing documented 4GB boundaries. Test signals include DTS validation, MM and infra IOMMU attach logs, display/video/camera DMA stress, PCIe/USB DMA tests, and IOMMU fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8195-memory-port.h -->
