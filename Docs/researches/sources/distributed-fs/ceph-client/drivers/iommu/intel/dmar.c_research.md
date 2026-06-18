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
