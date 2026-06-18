<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8167-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8167-larb-port.h

## Purpose
This header defines MT8167 larb IDs and M4U port IDs for display, video encode, image/camera, and video decode clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB2_ID` and `M4U_PORT_*` constants for display OVL/RDMA/WDMA, MDP, VENC, camera/image ports, and VDEC external ports.

## Control flow
DTS `iommus` properties use these macros. The MT8167 IOMMU driver decodes the resulting IDs to associate each device with SMI larb and port hardware.

## State and persistence
The header is stateless. Port IDs persist in DTBs; runtime state is controlled by MediaTek IOMMU and SMI drivers.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8167 display, MDP, VENC, camera/image, VDEC, SMI, and IOMMU support.

## Risks and test signals
Risks include wrong larb assignment across compact three-larb layout and incomplete VDEC port coverage. Test signals include `dtbs_check`, SMI larb probe, DMA stress for each multimedia block, and fault decode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8167-larb-port.h -->
