<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.h

Purpose: shared ARM LPAE register field constants for io-pgtable ARM backends and tests.

Important APIs/types/functions: defines TCR granule encodings for TTBR0/TTBR1, shareability values, inner/outer cacheability values, and physical address size encodings from 32 to 52 bits.

Control flow: allocation code in `io-pgtable-arm.c` selects these constants while constructing `arm_lpae_s1_cfg.tcr` and `arm_lpae_s2_cfg.vtcr` based on page granule, coherency, output address size, and TTBR1 quirk.

State and persistence: no runtime state; constants become persistent hardware register configuration stored in `io_pgtable_cfg`.

Dependencies and integration: included by ARM LPAE implementation and KUnit tests.

Risks: constants are hardware ABI values; any mismatch changes page-table walk behavior. Header intentionally contains no guards around feature availability, so callers must validate formats elsewhere.

Test signals: compile use in implementation/tests, register field comparisons on ARM SMMU drivers, and KUnit coverage across address sizes/granules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/io-pgtable-arm.h -->
