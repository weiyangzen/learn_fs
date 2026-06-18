# sources/distributed-fs/ceph-client/drivers/cxl/pmu.h

Purpose: small private header defining the CXL Performance Monitoring Unit device object and constructor used when CXL PCI discovers PMU register blocks.

Important APIs/types/functions: `enum cxl_pmu_type`, `CXL_PMU_REGMAP_SIZE`, `struct cxl_pmu`, `to_cxl_pmu()`, and `devm_cxl_pmu_add()`.

Control flow and state: a PMU object records the parent-associated ID, per-device PMU index, type (`CXL_PMU_MEMDEV` here), mapped register base, and embedded device. `pci.c` counts PMU register blocks, maps each block, and calls `devm_cxl_pmu_add()` with the memdev ID and PMU index.

Dependencies and integration: depends on Linux device core and the CXL register-map type; integrates with CXL PCI enumeration and the separate CXL PMU implementation/perf path.

Risks and test signals: the file is simple, but register-map size/type/index associations must match CXL spec expectations and PMU consumers. Test devices with zero, one, and multiple PMU regblocks; failed map/add paths; and module namespace/export behavior.
