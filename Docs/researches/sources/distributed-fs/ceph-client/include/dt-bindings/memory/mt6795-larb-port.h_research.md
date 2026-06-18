<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt6795-larb-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt6795-larb-port.h

## Purpose
This header defines MT6795 larb and M4U port IDs for display, video decode, camera, video encode, and MJC motion/processing clients.

## Important APIs, types, and functions
It exports `M4U_LARB0_ID` through `M4U_LARB5_ID` and `M4U_PORT_*` constants for display OVL/RDMA/WDMA, VDEC, camera IMGI/IMG2O/LSCI, VENC stream/current/reference ports, and MJC read/write DMA ports.

## Control flow
MT6795 DTS uses these macros in IOMMU specifiers. MediaTek IOMMU logic decodes `MTK_M4U_ID` values into larb/port identifiers for SMI and M4U programming.

## State and persistence
No state is stored here. DTB port IDs are persistent; runtime DMA translation and faults are managed by the driver.

## Dependencies and integration points
It depends on `mtk-memory-port.h` and integrates with MT6795 display, VDEC, camera, VENC, MJC, SMI, and IOMMU code.

## Risks and test signals
Risks include legacy port naming drift, wrong VENC set assignment, and MJC port misrouting. Test signals include DTS validation, larb attach traces, multimedia DMA tests, and IOMMU fault reports matching the named client.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mt6795-larb-port.h -->
