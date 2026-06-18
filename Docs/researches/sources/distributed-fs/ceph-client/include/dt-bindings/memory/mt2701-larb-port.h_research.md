<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2701-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2701-larb-port.h

## Purpose
This header defines MT2701 M4U larb port IDs using explicit larb port offsets for display, VDEC, camera, MDP, VENC, and JPGDEC clients.

## Important APIs, types, and functions
It exports `LARB0_PORT_OFFSET` through `LARB3_PORT_OFFSET`, helper macros `MT2701_M4U_ID_LARB0..3(port)`, and `MT2701_M4U_PORT_*` constants for display OVL/RDMA/WDMA, VDEC MC/PP/VLD/MV, camera IMGI/IMG2O, MDP RDMA/WDMA/WROT, VENC, and JPEG decode write DMA.

## Control flow
DTS nodes use the port macros in IOMMU specifiers. The MT2701 IOMMU driver receives flat IDs derived from larb offsets and maps them to M4U port hardware.

## State and persistence
No state exists in the header. The flat IDs persist in DTBs; runtime state is in M4U/IOMMU configuration and fault registers.

## Dependencies and integration points
It integrates with the older MT2701 MediaTek IOMMU binding style, SMI larb hardware, and display/video/camera/MDP/JPEG drivers.

## Risks and test signals
Risks include offset arithmetic errors, flat ID collisions between larbs, and mismatches with newer `MTK_M4U_ID` style bindings. Test signals include DTS preprocessing, IOMMU probe, DMA tests for every larb, and fault reports matching the expected flat port ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt2701-larb-port.h -->
