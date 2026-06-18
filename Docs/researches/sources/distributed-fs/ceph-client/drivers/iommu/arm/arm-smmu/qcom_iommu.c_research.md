# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/qcom_iommu.c

## Purpose
Legacy Qualcomm secure IOMMU driver, based on Arm SMMU concepts but managing Qualcomm MSM IOMMU v1/v2 devices with child context-bank devices. It registers its own IOMMU ops, initializes secure page-table memory through SCM when needed, programs stage-1 32-bit LPAE context banks, and handles faults, runtime PM, and DT `of_xlate` for ASIDs.

## Important APIs, Types, And Functions
`struct qcom_iommu_dev` owns the parent IOMMU, clocks, local base, secure ID, max ASID, and flexible array of context pointers. `struct qcom_iommu_ctx` represents one context bank with MMIO base, ASID, secure flags, and attached domain. `struct qcom_iommu_domain` wraps `iommu_domain` with io-pgtable ops, page-table lock, init mutex, IOMMU pointer, and fwspec. Key functions include `qcom_iommu_init_domain()`, domain alloc/free, attach/identity attach, map/unmap, TLB flush ops, fault handler, `qcom_iommu_sec_ptbl_init()`, context probe/remove, parent probe/remove, runtime PM callbacks, and `qcom_iommu_of_xlate()`.

## Control Flow
The initcall registers context and parent platform drivers. Parent probe determines max ASID from child nodes, allocates the parent object, gets clocks and secure ID, optionally allocates secure page-table memory via SCM, enables runtime PM, populates child context devices, registers sysfs and IOMMU core, and configures non-secure interrupt selection. Child probes map context-bank registers, request shared fault IRQs, detect secure contexts, clear stale FSR, compute ASID, and store the context pointer. Device `of_xlate` binds a client to one parent IOMMU and appends ASID IDs. Attach initializes the domain once, restores secure config for each ASID, programs non-secure context banks, and leaves secure context banks unprogrammed but associated. Map/unmap are serialized by `pgtbl_lock` and unmap forces runtime PM to keep TLB invalidations safe.

## State And Persistence
Runtime state includes parent context array, per-context `secure_init`/`secured_ctx`/domain fields, domain page-table ops and fwspec, clocks, secure page-table one-time allocation state, and hardware registers. There is no disk persistence. Secure page-table allocation uses a static `allocated` boolean, making it global and one-time for the kernel lifetime.

## Dependencies And Integration Points
It depends on `arm-smmu.h` register definitions, io-pgtable `ARM_32_LPAE_S1`, Qualcomm SCM calls (`qcom_scm_restore_sec_cfg`, secure page-table size/init), OF platform population, runtime PM, IOMMU core, clocks, device links, and DMA allocation for secure tables.

## Risks
ASID from DT must match context array bounds. Secure contexts cannot be programmed; mistakes can touch protected registers. Domain initialization publishes `pgtbl_ops` after programming contexts, so failure paths must clear `iommu`. Unmap/free paths use runtime PM because clients can unmap after power-off. The TLB invalidation loop writes every context in the fwspec; missing context pointers would crash. The static secure allocation assumes one global secure table setup.

## Test Signals
Boot MSM IOMMU v1/v2 DTs with non-secure and secure contexts; verify child population order; attach clients with one and multiple ASIDs; map/unmap and TLB sync under runtime suspend; fault IRQ reporting and resume; secure page-table SCM failures; parent remove; invalid/multiple-IOMMU `of_xlate` cases.
