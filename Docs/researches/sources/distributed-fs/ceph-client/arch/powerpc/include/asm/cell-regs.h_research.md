# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-regs.h

Purpose: defines Cell Broadband Engine I/O page-table entry bit masks shared by on-chip system device code.

Important APIs/types/functions: includes `cell-pmu.h` and defines `CBE_IOPTE_PP_W`, `CBE_IOPTE_PP_R`, `CBE_IOPTE_M`, `CBE_IOPTE_SO_R`, `CBE_IOPTE_SO_RW`, `CBE_IOPTE_RPN_Mask`, `CBE_IOPTE_H`, and `CBE_IOPTE_IOID_Mask`.

Control flow: declarative only. Cell IOMMU/platform code composes and decodes IOPTE values using these masks.

State and persistence: state is stored in Cell I/O page-table entries maintained by platform/IOMMU code. The header itself owns no state.

Dependencies and integration points: integrates Cell on-chip system devices, IOMMU/page-table setup, and PMU-related Cell headers.

Risks: IOPTE bit masks control read/write permission, coherency, ordering, real page number, cache hint, and IOID fields; incorrect masks can expose device memory or break DMA translation.

Test signals: Cell platform boot, DMA/IOMMU mapping tests, device access with read/write permission changes, and IOPTE dumps compared with hardware documentation.
