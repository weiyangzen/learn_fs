<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8192-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8192-larb-port.h

## Purpose
This header defines MT8192 M4U port IDs for multimedia IOMMU clients across display, MDP, VDEC/VENC, WPE, image, camera, CCU, and IPE/FDVT blocks. Comments describe 16GB IOVA region partitioning.

## Important APIs, types, and functions
It exports `M4U_PORT_L*_*` constants using `MTK_M4U_ID` for larbs 0, 2, 4, 5, 7, 8, 9, 11, 13, 14, 16, 17, 19, and 20. Names identify display, codec, image, camera, CCU, IPE, fake, and reserved ports.

## Control flow
MT8192 DTS uses these macros in `iommus` properties. Runtime MediaTek IOMMU code decodes the larb/port fields and manages DMA translation for each SMI master.

## State and persistence
No state exists in the header. IDs are persistent DT configuration; runtime state is in page tables and SMI/IOMMU registers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8192 display, MDP, VDEC/VENC, WPE, image, camera, CCU, IPE/FDVT, SMI, and IOMMU drivers.

## Risks and test signals
Risks include duplicated functional ports across MDP/DISP domains, boundary-sensitive IOVA mapping, and DTS using an undefined larb. Test signals include `dtbs_check`, SMI/IOMMU probe, multimedia pipeline DMA tests, CCU camera tests, and fault log larb/port verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8192-larb-port.h -->
