# sources/distributed-fs/ceph-client/include/linux/amd-iommu.h

## Purpose
Declares AMD IOMMU discovery, interrupt remapping/guest AVIC hooks, performance-counter accessors, and SEV-SNP/TIO support helpers.

## Important APIs, Types, And Functions
`amd_iommu_detect()` is real only with `CONFIG_AMD_IOMMU`. Guest/GA log functions such as `amd_iommu_register_ga_log_notifier()`, `amd_iommu_update_ga()`, `amd_iommu_activate_guest_mode()`, and `amd_iommu_deactivate_guest_mode()` are available only when both AMD IOMMU and IRQ remapping are enabled. Performance counter helpers include `amd_iommu_get_num_iommus()`, `amd_iommu_pc_supported()`, bank/counter limit accessors, and `amd_iommu_pc_{set,get}_reg()`. `amd_iommu_snp_disable()` and `amd_iommu_sev_tio_supported()` are gated by `CONFIG_KVM_AMD_SEV`.

## Control Flow, State, And Persistence
The header does not own state. It gates call sites so nonconfigured builds compile to harmless no-ops or false returns. Real state lives in AMD IOMMU core objects represented by opaque `struct amd_iommu`.

## Dependencies And Integration Points
Depends on `linux/types.h` and interacts with x86 IOMMU, KVM AMD, IRQ remapping, SEV-SNP, and IOMMU performance-counter code.

## Risks And Test Signals
Stubbed success returns can hide disabled feature paths if callers do not separately check capabilities. Tests should cover config matrices, KVM guest mode activation/deactivation, GA log notification, performance-counter bounds, SNP disable behavior, and build coverage without AMD IOMMU.
