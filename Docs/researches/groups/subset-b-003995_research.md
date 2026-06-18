# Research: subset-b-003995

Grouped research for Intel VT-d IOMMU files under `sources/distributed-fs/ceph-client/drivers/iommu/intel/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/debugfs.c

## Purpose

`debugfs.c` implements Intel IOMMU debugfs observability for live VT-d hardware state. It exposes register snapshots, root/context/PASID translation structures, per-domain page table walks, queued invalidation descriptors, interrupt-remapping tables, and invalidation latency counters. It is compiled behind `CONFIG_INTEL_IOMMU_DEBUGFS` and is invoked from the main IOMMU initialization/probe paths through declarations in `iommu.h`.

## Important APIs, Types, And Functions

- `struct tbl_walk` carries the current bus/devfn/PASID plus root, context, and PASID entry pointers while dumping translation structures.
- `struct iommu_regset`, `iommu_regs_32`, and `iommu_regs_64` define the MMIO registers printed by `iommu_regset_show()`.
- `intel_iommu_debugfs_init()` creates `/sys/kernel/debug/iommu/intel` and the global files `iommu_regset`, `dmar_translation_struct`, `invalidation_queue`, optional `ir_translation_struct`, and `dmar_perf_latency`.
- `intel_iommu_debugfs_create_dev()` and `intel_iommu_debugfs_remove_dev()` create/remove one debugfs directory per probed device and expose default-domain page-table dumps.
- `intel_iommu_debugfs_create_dev_pasid()` and `intel_iommu_debugfs_remove_dev_pasid()` do the same for `{device, pasid}` pairs.
- `domain_translation_struct_show()` is the main per-device dump path. It supports legacy context entries and scalable-mode PASID table entries, selects first-level or second-level roots based on PGTT/TT bits, and walks VT-d page tables.
- `invalidation_queue_show()` snapshots `struct q_inval` descriptors and descriptor statuses under `qi->q_lock`.
- `ir_translation_struct_show()` dumps interrupt-remapping and posted-interrupt entries when `CONFIG_IRQ_REMAP` is enabled.
- `dmar_perf_latency_write()` toggles latency accounting for IOTLB, DevTLB, or interrupt-entry-cache invalidations by calling `dmar_latency_enable()` and `dmar_latency_disable()`.

## Control Flow

Global debugfs initialization happens from `intel_iommu_init()` after DMAR tables and device scopes have been initialized and before devices are fully probed. The global show handlers iterate `for_each_active_iommu()` under RCU, then use per-IOMMU locks only where live MMIO or mutable tables require it.

The root/context/PASID dump path starts in `dmar_translation_struct_show()`, verifies `DMA_GSTS_TES`, and calls `root_tbl_walk()`. `root_tbl_walk()` takes `iommu->lock`, prints the root table physical address, and visits all 256 buses. `ctx_tbl_walk()` resolves context entries with `iommu_context_addr()`, skips non-present contexts, and either prints the legacy context entry directly or, if `DMAR_RTADDR_REG` has `DMA_RTADDR_SMT`, walks the PASID directory and PASID tables before printing every present PASID entry.

The per-device page-table path starts from device or PASID debugfs file private data. `domain_translation_struct_show()` filters active IOMMUs by segment, checks translation enablement, locks `iommu->lock`, locates the context entry, selects the page-table root from legacy context bits or scalable-mode PASID entry bits, then recursively walks page tables with `pgtable_walk_level()` until a leaf PTE or superpage is found.

The invalidation queue path locks `qi->q_lock`, reads hardware head/tail registers, and prints all `QI_LENGTH` descriptor slots. The IRQ-remapping path locks `irq_2_ir_lock` while scanning `INTR_REMAP_TABLE_ENTRIES`.

## State And Persistence

This file does not own persistent configuration. It keeps only `intel_iommu_debug`, a static `debug_buf` for latency snapshots, and debugfs dentries embedded in `struct device_domain_info` and `struct dev_pasid_info`. The actual state being displayed lives in `struct intel_iommu`, root/context/PASID tables, page tables, queued invalidation memory, and interrupt-remapping tables. Debugfs files expose live kernel and MMIO state, so results are point-in-time snapshots rather than stable records.

## Dependencies And Integration Points

The file depends on `iommu.h` for register offsets, context/PTE helpers, queue structures, and exported debugfs declarations; `pasid.h` for PASID table helpers; `perf.h` for latency counters; Linux debugfs and seq_file APIs; PCI helpers for BDF formatting; RCU and raw spinlocks for live traversal; and irq remapping internals when `CONFIG_IRQ_REMAP` is set. It integrates with `intel_iommu_probe_device()`, `intel_iommu_release_device()`, `intel_iommu_set_dev_pasid()`, and `domain_remove_dev_pasid()` through the create/remove helpers.

## Risks And Edge Cases

- `domain_translation_struct_show()` explicitly notes that page-table traversal can race with `iommu_unmap()` because page table pages are not RCU-freed in that path. A debugfs read could observe stale or freed page-table memory if lifetime guarantees change.
- Debugfs private data points directly at `device_domain_info` and `dev_pasid_info`; remove paths must call the recursive debugfs removers before freeing those objects.
- MMIO register reads use live hardware offsets and can be invalid if a DMAR unit is hot-removed or only partly initialized. The global show paths rely on RCU iteration over active IOMMUs.
- The PASID directory walk uses physical-to-virtual conversion on hardware table pointers. It assumes these tables are kernel-owned, mapped memory.
- `dmar_perf_latency_write()` applies a global operation to all active IOMMUs. Invalid or long input returns errors, and partial writes advance `ppos`.
- Interrupt-remapping table dumps scan 65,536 entries and can be expensive on large systems.

## Test Signals

Useful signals include successful creation/removal of debugfs directories during device probe/release and PASID attach/detach, readable global debugfs files under `/sys/kernel/debug/iommu/intel`, stable output while hotplugging devices, correct behavior with and without scalable mode, and lockdep/KASAN results during concurrent map/unmap and debugfs reads. Functional checks should cover legacy mode, scalable mode with PASID entries, queued invalidation enabled/disabled, IRQ remapping enabled/disabled, and latency toggling values 0 through 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/dmar.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/dmar.c

## Purpose

`dmar.c` implements the ACPI DMAR discovery and low-level VT-d hardware management layer shared by DMA remapping and interrupt remapping. It parses DMAR structures, allocates `struct intel_iommu` instances for DRHD units, tracks device scopes, maps register windows, manages queued invalidation, handles DMAR fault interrupts, supports ACPI DMAR hotplug through `_DSM`, and exposes platform opt-in detection.

## Important APIs, Types, And Functions

- `DECLARE_RWSEM(dmar_global_lock)` and `LIST_HEAD(dmar_drhd_units)` are the central synchronization primitive and global DRHD registry. Process context uses the rwsem; interrupt context uses RCU.
- `struct dmar_res_callback` generalizes walking ACPI DMAR entries with per-type handlers.
- `dmar_table_init()`, `parse_dmar_table()`, `dmar_walk_dmar_table()`, and `dmar_walk_remapping_entries()` locate, validate, and dispatch ACPI DMAR entries.
- `dmar_parse_one_drhd()` creates `struct dmar_drhd_unit`, copies its ACPI header, builds scope storage, allocates the matching `struct intel_iommu`, and registers the unit in RCU order.
- `alloc_iommu()`, `map_iommu()`, `free_iommu()`, and `unmap_iommu()` own low-level IOMMU object allocation, register mapping, capability reads, sysfs/iommu-device registration for hotplug, IRQ cleanup, queue cleanup, and IDA cleanup.
- `dmar_dev_scope_init()`, `dmar_insert_dev_scope()`, `dmar_remove_dev_scope()`, `dmar_pci_bus_notifier()`, and `dmar_iommu_notify_scope_dev()` keep scope tables synchronized with PCI and ACPI devices.
- `dmar_find_matched_drhd_unit()` resolves a PCI device to its DRHD unit, including `INCLUDE_ALL` fallback.
- `dmar_enable_qi()`, `dmar_disable_qi()`, `dmar_reenable_qi()`, `qi_submit_sync()`, and the `qi_flush_*()` wrappers implement queued invalidation.
- `dmar_fault()`, `dmar_fault_do_one()`, `dmar_set_interrupt()`, and `enable_drhd_fault_handling()` manage primary fault reporting and MSI setup.
- `dmar_device_add()` and `dmar_device_remove()` implement ACPI hot-add/hot-remove flows for DMAR units.
- `dmar_platform_optin()` detects the `DMAR_PLATFORM_OPT_IN` firmware flag and is exported.

## Control Flow

Early detection starts in `detect_intel_iommu()`: it takes `dmar_global_lock`, detects the ACPI DMAR table, validates DRHD MMIO registers with temporary mappings, sets `iommu_detected` and PCI ACS requirements when appropriate, and installs `intel_iommu_init()` as the x86 IOMMU initializer.

Full table setup runs through `dmar_table_init()`. `parse_dmar_table()` refreshes `dmar_tbl`, accounts for tboot-provided protected copies, verifies host address width, and walks each ACPI entry. DRHD entries allocate `dmar_drhd_unit` plus `intel_iommu`; RMRR, ATSR, RHSA, ANDD, and SATC handlers are dispatched to this file or `iommu.c` as appropriate.

Device scope initialization first maps ACPI namespace devices, then scans existing PCI devices, building `dmar_pci_notify_info` paths and inserting matching endpoint/bridge scopes. The PCI notifier repeats the same add/remove logic for hotplug and delegates RMRR/ATSR/SATC updates and IRQ-remapping additions.

Queued invalidation setup allocates `struct q_inval`, descriptor memory sized for legacy or scalable mode, and a descriptor-status array. `__dmar_enable_qi()` programs IQA/IQT and sets `DMA_GCMD_QIE`. `qi_submit_sync()` appends caller descriptors plus a wait descriptor, advances the hardware tail, spins until the wait descriptor reports completion, handles IQE/ITE/ICE faults, reclaims descriptor slots, and updates latency statistics.

Fault handling is interrupt-driven. `dmar_set_interrupt()` allocates a DMAR hardware IRQ and requests `dmar_fault()`. The handler reads the fault status and primary fault records, rate-limits logs, clears fault bits, decodes DMA or interrupt-remapping reasons, and calls `dmar_fault_dump_ptes()` when debug dumping is available.

Hotplug uses `_DSM` buffers. Insert validates DRHD resources, parses and registers DRHD/RHSA/ATSR entries, then enables interrupt and DMA-remapping hotplug. Failure unwinds in reverse order. Remove checks ATSR/DRHD busy state, disables consumers, and releases RCU-protected units.

## State And Persistence

The primary long-lived state is the RCU-protected `dmar_drhd_units` list, each `dmar_drhd_unit` owning copied ACPI header bytes, device-scope arrays, segment/register metadata, and a pointer to `struct intel_iommu`. `dmar_dev_scope_status` memoizes initialization success or failure. `dmar_seq_ids` allocates bounded per-IOMMU sequence IDs. Per-IOMMU persistent runtime state includes MMIO base/size, `cap`, `ecap`, `ecmdcap`, `gcmd`, queued invalidation state, IRQ numbers, domain IDA, and sysfs/iommu-device registration. ACPI table pointers are released after detection except when retained for initialization flow.

## Dependencies And Integration Points

This file depends on Linux ACPI, PCI, MSI/IRQ, RCU, IDA, NUMA, tboot, DMI, IOVA, and IOMMU core APIs. It includes `iommu.h`, shared IRQ-remapping headers, page allocation helpers, perf/latency support, tracepoints, and PerfMon support. It calls parser functions implemented in `iommu.c` for RMRR/ATSR/SATC and calls main IOMMU entry points such as `intel_iommu_init()`, `intel_iommu_shutdown()`, `dmar_iommu_hotplug()`, and `dmar_iommu_notify_scope_dev()`. IRQ remapping integrates through `dmar_ir_hotplug()`, `intel_irq_remap_add_device()`, and `dmar_ir_support()`.

## Risks And Edge Cases

- Firmware tables can be malformed. The walker guards against zero-length and overrun entries, validates DRHD registers returning all ones, checks ANDD string termination, and taints firmware-workaround paths.
- Device-scope matching includes a fallback for broken one-level RMRR paths. Changes here can affect device ownership and reserved-region enforcement.
- `dmar_pci_notify_info_buf` is a static optimization for normal-sized notifier payloads, so notifier handling is serialized by `dmar_global_lock`; using it outside that assumption would be unsafe.
- `qi_submit_sync()` spins with interrupts disabled while holding `qi->q_lock` for portions of the wait path to avoid queue deadlock. Fault recovery paths must preserve descriptor status consistency.
- ITE recovery may retry or timeout based on source ID and device presence; stale `device_rbtree_find()` results require caller-side synchronization.
- Hotplug assumes firmware ordering: DMAR units are added before devices and removed after devices. Violating that can cause `-EBUSY` or unsafe teardown.
- `IOMMU_WAIT_OP()` can panic on hardware timeout; register programming errors are high impact.

## Test Signals

Boot tests should show DMAR table detection, DRHD registration, valid capability logging, and correct fallback when no DRHD exists. Device hotplug tests should verify scope insertion/removal for endpoints, bridges, VFs, ACPI namespace devices, RMRR, ATSR, and SATC. QI tests should cover descriptor submission, queue wraparound, scalable-mode descriptor size, IQE/ITE/ICE handling, and latency accounting. Fault-injection tests should exercise primary fault records, rate-limited logging, PASID and non-PASID faults, and invalidation timeout recovery. ACPI `_DSM` hotplug tests should validate insert/remove unwinds and RCU lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/dmar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/iommu.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/iommu.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/iommu.h

## Purpose

`iommu.h` is the shared Intel VT-d driver contract for the files in this directory. It defines hardware register offsets, capability decoders, command/status bit encodings, queued-invalidation descriptor formats, core data structures for IOMMUs/domains/devices/PASIDs/cache tags, inline context/PTE/descriptor helpers, and cross-file function declarations. It is the schema binding `dmar.c`, `iommu.c`, debugfs, PASID, PRQ, SVM, nested translation, cache tag, and perf code together.

## Important APIs, Types, And Functions

- VT-d page constants: `VTD_PAGE_SHIFT`, `VTD_PAGE_SIZE`, `VTD_PAGE_MASK`, `VTD_PAGE_ALIGN()`, `VTD_STRIDE_SHIFT`, and address-width constants.
- Register offsets: `DMAR_VER_REG`, `DMAR_CAP_REG`, `DMAR_ECAP_REG`, global command/status registers, fault registers, invalidation queue registers, interrupt-remapping registers, PRQ registers, PerfMon registers, and enhanced command registers.
- Capability decoders: `cap_*()` and `ecap_*()` macros expose hardware features such as scalable mode, PASID, PRS, nested translation, snoop control, queued invalidation, interrupt remapping, superpages, fault register count, and address widths.
- `IOMMU_WAIT_OP()` is the common MMIO polling macro used by hardware command paths and panics on timeout.
- Queued invalidation structures and encodings include `struct qi_desc`, `struct q_inval`, `QI_*` descriptor types, status values, queue length, PRQ sizing, and descriptor-building helpers.
- Translation structures include `struct root_entry`, `struct context_entry`, `struct dma_pte`, and helpers such as `context_present()`, `context_set_present()`, `context_clear_present()`, `context_set_translation_type()`, `context_set_address_root()`, `context_set_domain_id()`, `dma_pte_addr()`, `dma_pte_present()`, and `dma_pte_superpage()`.
- Core state structs include `struct intel_iommu`, `struct dmar_domain`, `struct iommu_domain_info`, `struct device_domain_info`, `struct dev_pasid_info`, `struct iommu_pmu`, and `struct cache_tag`.
- Domain helpers include `to_dmar_domain()`, `domain_id_iommu()`, `iommu_domain_did()`, `intel_domain_is_fs_paging()`, and `intel_domain_is_ss_paging()`.
- Cross-file declarations expose DMAR/QI functions, domain attach/detach, PASID setup helpers, cache tag operations, PRQ/IOPF functions, SVM allocation, debugfs hooks, sysfs attribute groups, IOMMU ops, and enhanced command submission.

## Control Flow

This header does not execute a runtime flow by itself, but its inline helpers define the ordering and encodings used by runtime flows. Context entry setup generally clears or initializes fields, sets domain ID/address/translation type, performs a DMA write memory barrier, and then sets the present bit. Teardown clears the present bit with `context_clear_present()`, which includes a write barrier and documents the caller's obligation to perform the VT-d invalidation handshake.

Queued invalidation flow is encoded by helpers such as `qi_desc_iotlb()`, `qi_desc_dev_iotlb()`, `qi_desc_piotlb_all()`, `qi_desc_piotlb()`, and `qi_desc_dev_iotlb_pasid()`. `dmar.c` builds descriptors with these helpers, submits them with `qi_submit_sync()`, and interprets the `QI_FREE`, `QI_IN_USE`, `QI_DONE`, and `QI_ABORT` status array.

Domain/device flows use header-defined structs as shared state. `iommu.c` allocates and mutates `dmar_domain`, `device_domain_info`, and `dev_pasid_info`; `dmar.c` uses `intel_iommu` and QI fields for hardware control; debugfs reads the same structures for observability.

## State And Persistence

The header describes persistent state rather than owning it. `struct intel_iommu` persists per hardware remapping unit and contains MMIO addresses, capability registers, command shadow, locks, domain ID allocator, root table pointer, invalidation queue, PRQ/IOPF state, device rbtree, IRQ-remapping state, IOMMU core device, NUMA node, flags, DRHD backpointer, perf state, and PMU state. `struct dmar_domain` persists per IOMMU domain and tracks page-table implementation, attached IOMMUs, devices, PASIDs, cache tags, dirty tracking, force snooping, nested parent/child relationships, and SVA notifier state. `struct device_domain_info` persists per probed device and records BDF/segment, ATS/PASID/PRI state, IOPF reference count, IOMMU/domain pointers, PASID table, debugfs dentry, and RID rbtree node.

## Dependencies And Integration Points

The header includes Linux IOVA, IOMMU, IDR/IDA, MMU notifier, xarray, perf, PCI, bitfield, IO, generic page-table IOMMU, x86 IOMMU, and iommufd UAPI definitions. Conditional sections adapt to `CONFIG_IRQ_REMAP`, `CONFIG_INTEL_IOMMU`, `CONFIG_INTEL_IOMMU_SVM`, and `CONFIG_INTEL_IOMMU_DEBUGFS`. It imports PASID-related types by forward declaration and exposes hooks to PASID, SVM, nested, PRQ, debugfs, cache tag, and perf modules.

## Risks And Edge Cases

- Register and descriptor encodings are hardware ABI. Any incorrect bit definition can corrupt translation, fail invalidations, or mis-handle interrupts.
- `IOMMU_WAIT_OP()` panics on hardware timeout. Callers must use it only for operations where panic is the intended fail-stop behavior.
- Context field setters mostly OR fields into existing values. Callers are expected to clear entries first when reprogramming, or stale bits can remain.
- `context_set_present()` and `context_clear_present()` encode memory-order assumptions. Reordering these relative to cache flushes and invalidations is unsafe.
- `qi_desc_dev_iotlb_pasid()` warns on non-aligned invalidation addresses and encodes size by manipulating low address bits; off-by-one errors here directly affect TLB invalidation coverage.
- `device_rbtree_find()` declaration returns a device pointer without lifetime protection; callers must synchronize if release can race.
- Conditional stubs for disabled configs must preserve call-site semantics, especially for debugfs and SVM paths.

## Test Signals

Validation should include compile coverage across combinations of `CONFIG_INTEL_IOMMU`, `CONFIG_IRQ_REMAP`, `CONFIG_INTEL_IOMMU_SVM`, and `CONFIG_INTEL_IOMMU_DEBUGFS`; static assertions from `PT_IOMMU_CHECK_DOMAIN`; sparse/lockdep checks around inline synchronization assumptions; descriptor encoding tests or trace validation for IOTLB, DevTLB, PASID cache, page group response, and PRQ paths; and boot/runtime tests that read capability fields and confirm the driver programs expected register bits in legacy and scalable modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/iommu.h -->
