<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8173-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8173-larb-port.h

## Purpose
This header defines MT8173 larb IDs and M4U port IDs for display, VDEC, camera, VENC, and alternate VENC port sets.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB5_ID` and `M4U_PORT_*` constants, including display OVL/RDMA/WDMA, VDEC external ports, camera image ports, VENC RCPU/REC/BSDMA/current/reference ports, and `_SET2` VENC aliases.

## Control flow
MT8173 DTS nodes reference the constants in IOMMU specifiers. The MediaTek IOMMU driver splits `MTK_M4U_ID` values into larb/port fields to program SMI and M4U hardware.

## State and persistence
No header state exists. DTB IDs persist and runtime translation state is held by the IOMMU subsystem.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT8173 display, video decode/encode, camera, SMI larb, and IOMMU drivers.

## Risks and test signals
Risks include confusing base VENC ports with `_SET2` ports, port collision during additions, and DTS/driver table mismatch. Test signals include DTS validation, VENC/VDEC DMA tests, display/camera streaming, and IOMMU fault reports with expected larb/port IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt8173-larb-port.h -->
