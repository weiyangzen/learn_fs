<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mtk-memory-port.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/memory/mtk-memory-port.h

## Purpose
This shared MediaTek memory binding header defines helper macros for packing and unpacking larb/port IDs used by many MediaTek M4U/IOMMU port headers.

## Important APIs, types, and functions
It exports `MTK_LARB_NR_MAX`, `MTK_M4U_ID(larb, port)`, `MTK_M4U_TO_LARB(id)`, `MTK_M4U_TO_PORT(id)`, and `MTK_IFAIOMMU_PERI_ID(port)`. The packing uses 5 bits for the port and supports larb IDs up to 31.

## Control flow
SoC-specific headers include this file and build concrete port macros. DTS preprocessing emits packed IDs; MediaTek IOMMU drivers decode them with the inverse helpers or equivalent logic.

## State and persistence
No state exists. The packing format is stable DT ABI and is embedded in all dependent DTBs.

## Dependencies and integration points
It is a dependency for MediaTek larb/memory-port headers and integrates with SMI larb drivers, M4U/IOMMU code, and infra IOMMU per-port IDs.

## Risks and test signals
Risks include port values above 31 truncating in `MTK_M4U_TO_PORT`, larb values above `MTK_LARB_NR_MAX`, and SoC headers using helper names not defined here. Test signals include preprocessing every dependent header, static scans for port values over 31, `dtbs_check`, and IOMMU fault decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/memory/mtk-memory-port.h -->
