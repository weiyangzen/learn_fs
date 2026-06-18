## sources/distributed-fs/ceph-client/arch/x86/events/amd/iommu.h

Purpose: local header for AMD IOMMU performance-counter register indexes and hardware maximum constants.

Important definitions: `IOMMU_PC_COUNTER_REG`, `IOMMU_PC_COUNTER_SRC_REG`, `IOMMU_PC_PASID_MATCH_REG`, `IOMMU_PC_DOMID_MATCH_REG`, `IOMMU_PC_DEVID_MATCH_REG`, `IOMMU_PC_COUNTER_REPORT_REG`, `PC_MAX_SPEC_BNKS`, and `PC_MAX_SPEC_CNTRS`.

Control flow: no runtime logic; constants are consumed by `iommu.c` when programming AMD IOMMU PC registers.

State/persistence: none locally; defines the offsets used to access persistent hardware registers.

Integration points: AMD IOMMU perf driver and `linux/amd-iommu.h` register access helpers.

Risks: offset mistakes program the wrong IOMMU registers. Test signals include IOMMU perf counter programming tests, hardware register trace/debug, and build coverage for `CONFIG_AMD_IOMMU`.
