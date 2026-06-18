<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8188-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8188-memory-port.h

## Purpose
This header defines MT8188 memory/IOMMU port IDs across many software-indexed SMI larbs. It documents non-linear larb numbering, two MM IOMMU hardware blocks, and suggested 16GB IOVA partitioning for display, vcodec, camera/MDP, and CCU regions.

## Important APIs, types, and functions
It exports `SMI_L*_ID` software larb indexes and hundreds of `M4U_PORT_L*_*` constants built with `MTK_M4U_ID`, plus `IFR_IOMMU_PORT_PCIE_0` for infra IOMMU. Ports cover VDO/VPP display, MDP, WPE, IMG, camera raw/CAMSV/CCU, VDEC, VENC, and related fake/reserved engines.

## Control flow
MT8188 DTS nodes use these constants in `iommus` specifiers. The MediaTek IOMMU and SMI drivers decode IDs into larb/port pairs, attach devices to the correct IOMMU instance, and apply the DMA address-region policy described in the comments.

## State and persistence
The header has no runtime state. DTB constants persist across boots; runtime state lives in IOMMU page tables, SMI larb power state, and fault registers.

## Dependencies and integration points
It includes `mtk-memory-port.h` and integrates with MT8188 display/video/image/camera pipelines, VDO/VPP IOMMU instances, PCIe infra IOMMU, and SMI larb drivers.

## Risks and test signals
Risks include software larb reindexing drift from hardware names, assigning a port to the wrong IOMMU instance, crossing documented 4GB IOVA boundaries, and duplicate/reserved fake-engine use. Test signals include `dtbs_check`, IOMMU attach traces per larb, SMI power-domain tests, multimedia DMA stress, IOMMU fault injection, and PCIe infra IOMMU validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8188-memory-port.h -->
