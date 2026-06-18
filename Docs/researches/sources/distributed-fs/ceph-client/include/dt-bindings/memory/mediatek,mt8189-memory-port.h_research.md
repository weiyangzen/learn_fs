<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8189-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8189-memory-port.h

## Purpose
This header defines MediaTek MT8189 memory/IOMMU port IDs for display, MDP, video, WPE, image, camera, CCU, APU, and infra PCIe clients.

## Important APIs, types, and functions
It exports software larb IDs `SMI_L0_ID` through `SMI_L20_ID`, port macros named `M4U_Lx_Py_*` using `MTK_M4U_ID`, named workload ports such as `M4U_PORT_WFD_HEAP`, APU ports `M4U_L0_APU_DATA/CODE/SECURE/VLM`, and `IFR_IOMMU_PORT_PCIE_0`.

## Control flow
DTS nodes place these constants in IOMMU specifier cells. MediaTek IOMMU code decodes the larb and port values to bind each hardware master and route DMA through the intended translation domain.

## State and persistence
No state is held in the header. The selected IDs persist in DTBs; runtime mappings, faults, and page-table state live in the IOMMU drivers and hardware.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8189 display, MDP, VDEC/VENC, camera, WPE/IPE/FDVT, APU, and PCIe IOMMU consumers.

## Risks and test signals
Risks include sparse software larb numbering, incorrect port suffix interpretation, and cross-subsystem DMA routed through the wrong domain. Test signals include DTS validation, larb probe logs, IOMMU attach/fault tests per multimedia block, APU DMA tests, and PCIe IOMMU smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mediatek,mt8189-memory-port.h -->
