# sources/distributed-fs/ceph-client/drivers/iommu/intel/iommu.c

## Purpose

`iommu.c` is the main Intel VT-d DMA-remapping implementation. It parses boot options, chooses legacy versus scalable mode, initializes IOMMU hardware, manages root/context/PASID programming, implements the Linux `iommu_ops` and paging-domain operations, handles device probe/release, tracks domains and PASID attachments, processes RMRR/ATSR/SATC table entries, integrates IOPF/PRI/ATS/PASID, supports suspend/resume and hotplug, and applies chipset/device quirks.

## Important APIs, Types, And Functions

- Global policy flags include `dmar_disabled`, `intel_iommu_sm`, `intel_iommu_enabled`, `intel_iommu_superpage`, `iommu_identity_mapping`, `iommu_skip_te_disable`, `disable_igfx_iommu`, and `force_on`.
- Local ACPI resource structs `dmar_rmrr_unit`, `dmar_atsr_unit`, and `dmar_satc_unit` track reserved memory, ATS remapping scopes, and SATC scopes.
- `intel_iommu_setup()` parses `intel_iommu=` boot parameters.
- `iommu_context_addr()` allocates or resolves context entries, including scalable-mode lower/upper context tables.
- `device_lookup_iommu()` maps Linux devices to an active `struct intel_iommu`, handling PCI real DMA devices, VFs, ACPI companions, bridge scopes, include-all units, and dummy/ignored units.
- `init_dmars()`, `intel_iommu_init()`, `intel_iommu_shutdown()`, `init_iommu_hw()`, `iommu_suspend()`, and `iommu_resume()` are the main lifecycle functions.
- `domain_attach_iommu()` and `domain_detach_iommu()` allocate/free per-IOMMU domain IDs and store `struct iommu_domain_info` in a domain xarray.
- `dmar_domain_attach_device()`, `domain_context_mapping()`, `domain_setup_first_level()`, `domain_setup_second_level()`, and `device_block_translation()` program or tear down default-domain translations.
- `intel_iommu_domain_alloc_first_stage()`, `intel_iommu_domain_alloc_second_stage()`, `paging_domain_compatible()`, `intel_iommu_attach_device()`, and `intel_iommu_domain_free()` implement paging domains.
- `intel_iommu_probe_device()`, `intel_iommu_probe_finalize()`, and `intel_iommu_release_device()` are the IOMMU core device lifecycle hooks.
- `intel_iommu_set_dev_pasid()`, `domain_add_dev_pasid()`, and `domain_remove_dev_pasid()` manage PASID-bound domains.
- `intel_iommu_set_dirty_tracking()` and helpers enable/disable second-stage dirty tracking across attached devices and nested first-stage domains.
- `intel_iommu_ops`, `intel_fs_paging_domain_ops`, and `intel_ss_paging_domain_ops` export the driver to the IOMMU core.
- Quirk handlers alter behavior for broken integrated graphics, RWBF capability, Calpella shadow GTT, Tylersburg ISOCH, and extra DevTLB invalidation.

## Control Flow

Boot starts with command-line parsing and `detect_intel_iommu()` in `dmar.c`, then `intel_iommu_init()` performs full setup. It may force enablement for tboot or platform opt-in, initializes the DMAR table and device scopes under `dmar_global_lock`, registers the PCI bus notifier, creates debugfs if enabled, exits early if IOMMU is disabled, marks no-remapping or graphics-only units, and calls `init_dmars()`.

`init_dmars()` iterates IOMMUs, skips ignored units, computes global PASID limits, initializes queued or register-based invalidation, records pre-enabled translation, disables unexpected pre-enabled translation outside kdump, allocates root tables, optionally copies old translation tables in kdump, and runs SVM capability checks. It then programs root entries and cache flushes on all active IOMMUs, handles platform quirks, enables PRQ and fault interrupts, and leaves final translation enablement to `intel_iommu_init()` after IOMMU devices are registered.

Device probing calls `device_lookup_iommu()` and allocates `device_domain_info`. PCI ATS/PASID/PRI capabilities are discovered, ATS devices are inserted in the IOMMU RID rbtree, scalable-mode PASID tables and context entries are prepared, and debugfs directories are created. Finalization enables PASID before ATS, assigns DevTLB cache tags when appropriate, and enables PRI. Release reverses PRI/ATS/PASID, removes rbtree entries, tears down scalable-mode context when owned by this kernel, frees PASID tables, removes debugfs, and frees `device_domain_info`.

Domain attachment blocks old translations first, verifies compatibility against the target IOMMU, enables IOPF if requested, attaches the domain to the IOMMU IDA/xarray, links the device into the domain list, programs legacy context entries or scalable-mode PASID entries for `IOMMU_NO_PASID`, and assigns cache tags. Failure paths block translation and unwind IOPF.

PASID attachment similarly validates paging-domain compatibility, allocates `dev_pasid_info`, attaches the domain to the IOMMU, assigns cache tags, replaces IOPF ownership, programs first-stage or second-stage PASID entries, removes the old domain/PASID binding, and creates PASID debugfs. Blocking or identity domains use specialized `set_dev_pasid` paths.

TLB synchronization is abstracted through cache tags. Map sync calls `cache_tag_flush_range_np()` when required by hardware write-buffer or caching-mode constraints. Unmap sync flushes ranges and releases gathered page-table pages. Full flush calls `cache_tag_flush_all()`.

## State And Persistence

Long-lived state includes global DMAR resource lists for RMRR, ATSR, and SATC; per-IOMMU root tables, copied-table bitmaps, domain IDA, device RID rbtree, queued invalidation choice, PRQ state, and hardware flags; per-domain xarray mappings from IOMMU sequence ID to domain ID, attached device/PASID lists, cache tags, dirty-tracking and nesting flags; and per-device ATS/PASID/PRI capability/enabled state. Hardware state persists in root/context/PASID tables and MMIO registers until explicitly reprogrammed, disabled, or restored across suspend/resume. Kdump handling can copy pre-existing hardware translation tables and marks copied contexts to avoid unsafe reuse until torn down.

## Dependencies And Integration Points

This file depends on `iommu.h`, `pasid.h`, generic page-table IOMMU helpers, DMA-IOMMU helpers, IRQ remapping, IOMMU page allocators, PerfMon, Linux PCI/ATS/PRI/PASID APIs, ACPI device scope data, syscore suspend/resume, tboot, DMI, and `iommufd` UAPI types. It provides parser functions consumed by `dmar.c` for RMRR/ATSR/SATC and consumes low-level functions from `dmar.c` for QI, fault IRQs, hotplug, and platform opt-in. It integrates with SVM, nested translation, page request queue code, cache tag code, debugfs, and the IOMMU core.

## Risks And Edge Cases

- Context and PASID programming is high impact. Ordering relies on present-bit transitions, cache flushes, context/IOTLB invalidations, and hardware write-buffer flushes.
- Kdump copied-table handling deliberately avoids changing scalable-mode root-table type while translation is enabled; failure falls back to disabling translation and may cause faults.
- Domain ID allocation is per IOMMU and refcounted through xarray entries. Bugs can leak IDs or detach still-used domains.
- `device_block_translation()` is the safety fallback and must stay correct for default domains, PASID domains, identity domains, and real DMA subdevices.
- The code comments identify missing reference counting for dependent PCI DMA aliases; unbinding one endpoint can affect others with intersecting aliases.
- Dirty tracking has unwind logic across nested domains and attached PASIDs; partial failure must restore previous tracking state.
- ATS/PRI/PASID ordering matters. PASID is enabled before ATS because PCIe leaves behavior undefined otherwise.
- Some compatibility logic has a FIXME about locking around forced coherence checks, indicating residual concurrency risk.
- Platform quirks are skipped for untrusted external-facing devices; weakening that check could allow unsafe IOMMU bypasses.

## Test Signals

Test coverage should include boot with `intel_iommu=on/off/sm_on/sm_off/sp_off/igfx_off/tboot_noforce`, platform opt-in, tboot force-on, legacy and scalable mode, kdump with pre-enabled translation, suspend/resume, hotplug DRHD units, and ignored graphics-only units. IOMMU core tests should cover device probe/release, default DMA domains, identity and blocking domains, first-stage and second-stage paging allocation, nested parent domains, PASID attach/detach, IOPF enable/disable, dirty tracking, ATS/PRI/PASID combinations, reserved-region reporting for RMRR and MSI, and cache-tag flushing under map/unmap. Fault injection should check translation enable/disable failures, QI fallback to register invalidation, PRQ setup failures, and quirk paths on trusted versus untrusted devices.
