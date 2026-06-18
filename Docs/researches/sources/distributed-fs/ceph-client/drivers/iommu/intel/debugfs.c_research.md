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
