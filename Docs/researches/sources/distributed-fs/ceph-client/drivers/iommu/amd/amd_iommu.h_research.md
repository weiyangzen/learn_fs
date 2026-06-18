# sources/distributed-fs/ceph-client/drivers/iommu/amd/amd_iommu.h

## Purpose

This header is the internal AMD IOMMU interface shared by AMD initialization, runtime domain operations, interrupt remapping, PPR/PASID/IOPF, debugfs, quirks, and nested/IOMMUFD code. It includes `amd_iommu_types.h`, declares exported internal state, and provides small helpers for feature checks, address encryption handling, device lookup, domain conversion, and DTE clearing.

## Important APIs And Helpers

Initialization and interrupt-remapping entry points include `amd_iommu_prepare()`, `amd_iommu_enable()`, `amd_iommu_disable()`, `amd_iommu_reenable()`, and `amd_iommu_enable_faulting()`. Interrupt/log handling is declared through `amd_iommu_int_thread*()` variants and log restart helpers. Domain APIs include identity-domain initialization, protection-domain allocation/free, SVA allocation, PASID attach/remove, GCR3 set/clear, page-response, IOPF device add/remove, PPR log allocation/enabling/polling/completion, cache flushes, and nested-domain allocation.

Helpers include `check_feature()` and `check_feature2()` over global EFR/EFR2 masks, `amd_iommu_v2_pgtbl_supported()`, `amd_iommu_gt_ppr_supported()`, SME-aware `iommu_virt_to_phys()`/`iommu_phys_to_virt()`, `get_pci_sbdf_id()`, post-probe `get_amd_iommu_from_dev()`, `get_amd_iommu_from_dev_data()`, `to_pdomain()`, and `amd_iommu_make_clear_dte()`. The DTE clear helper preserves IVRS-derived persistent DTE bits by consulting `amd_iommu_get_ivhd_dte_flags()`.

## State And Dependencies

The header exposes global configuration such as event/PPR log sizes, guest interrupt remapping mode, selected page-table mode, guest/host page-table levels, supported page-size bitmap, and HAT disable state. It depends on Linux IOMMU APIs, PCI types, AMD type definitions, generic page-table hardware info, IRQ remapping when configured, DMI quirks, and IOMMUFD user data for nested allocation.

## Risks And Test Signals

This file is a cross-module contract; signature drift can break multiple AMD objects. Feature helpers assume global EFR values have been initialized before use. Address helpers must preserve SME encryption-bit semantics or hardware receives wrong physical addresses. `amd_iommu_make_clear_dte()` must keep IVRS persistent flags or firmware-required pass-through/system-management bits may be lost during detach. Test signals include AMD IOMMU builds across debugfs, IRQ remap, IOMMUFD, SVA/IOPF, and DMI configurations; boot tests with SME/SNP; PASID/PPR attach tests; and DTE inspection after attach/detach.
