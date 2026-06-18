<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-nvidia.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-nvidia.c

## Purpose

`arm-smmu-nvidia.c` implements NVIDIA Tegra integration quirks for the legacy Arm SMMU driver. Tegra194/Tegra234 systems can expose multiple MMU-500 instances that must be programmed identically for non-isochronous clients, and the SMMU driver must coordinate with the Tegra memory controller to program stream ID overrides. This file wraps the generic SMMU device in an NVIDIA-specific structure, mirrors register writes across instances, aggregates TLB sync and fault handling across instances, limits page sizes for a Tegra walk-cache erratum, and finalizes memory-controller device probing.

## Important APIs, Types, and Functions

`struct nvidia_smmu` embeds `struct arm_smmu_device`, stores up to `MAX_SMMU_INSTANCES` MMIO bases, tracks `num_instances`, and holds a `struct tegra_mc *`. Helpers `to_nvidia_smmu` and `nvidia_smmu_page` convert generic SMMU state into instance-specific MMIO pages.

Register accessors are `nvidia_smmu_read_reg`, `nvidia_smmu_write_reg`, `nvidia_smmu_read_reg64`, and `nvidia_smmu_write_reg64`. TLB and reset hooks are `nvidia_smmu_tlb_sync` and `nvidia_smmu_reset`. Fault handling is split across `nvidia_smmu_global_fault_inst`, `nvidia_smmu_global_fault`, `nvidia_smmu_context_fault_bank`, and `nvidia_smmu_context_fault`.

Integration hooks are `nvidia_smmu_probe_finalize`, `nvidia_smmu_init_context`, `nvidia_smmu_impl`, `nvidia_smmu_single_impl`, and `nvidia_smmu_impl_init`.

## Control Flow

`nvidia_smmu_impl_init` is called from the legacy implementation dispatcher for Tegra186/Tegra194/Tegra234 compatible strings. It reallocates the generic SMMU object to `struct nvidia_smmu`, obtains the Tegra memory controller handle, records the already mapped instance-0 base, maps additional memory resources up to two instances, and selects either a single-instance implementation table or a multi-instance mirroring implementation table.

For multi-instance systems, generic register reads come from instance 0 while writes are broadcast to all instances. TLB sync writes the sync register through the generic accessor and then polls the status register on every instance, ORing active bits until all instances are inactive or timeout. Reset clears global fault status on every instance.

Global fault handling scans every instance and reports/clears any nonzero GR0 global fault status with syndrome registers. Context fault handling scans every context bank on every instance because the interrupt line is shared, reports FSR/FSYNR/FAR/CBFRSYNRA, and clears the fault status.

Context initialization restricts page mappings to `PAGE_SIZE` for Tegra194 and Tegra234. This avoids stale walk-cache entries caused by a hardware erratum where the walk-cache index differs between translation and invalidation requests. Probe finalize calls into the memory controller driver for each attached device so SID overrides are programmed.

## State and Persistence Behavior

`struct nvidia_smmu` persists for the SMMU device lifetime. It stores per-instance MMIO mappings, instance count, and memory-controller reference. The selected `smmu.impl` table persists as the legacy core's hook table. Runtime hardware state is written identically across instances for multi-instance configurations, so stream table, context bank, and control register programming stay mirrored.

Fault state is not persisted; handlers read and clear hardware fault registers. Page-size restriction mutates `smmu->pgsize_bitmap` and the io-pgtable config for affected SoCs during context initialization, affecting subsequent domain mappings.

## Dependencies and Integration Points

The file depends on the legacy `arm-smmu.h` interface, Tegra memory-controller API (`devm_tegra_memory_controller_get`, `tegra_mc_probe_device`), platform resources, device-tree matching, MMIO helpers, and Linux IRQ interfaces. It is linked into the legacy `arm_smmu` aggregate by the Makefile and selected by `arm-smmu-impl.c`.

The memory controller integration is essential for SID override programming. The SMMU integration hooks are consumed by the generic legacy driver through `struct arm_smmu_impl`, including register accessors, reset, tlb_sync, fault handlers, probe_finalize, and init_context.

## Risks and Edge Cases

Mirrored writes assume all non-isochronous SMMU instances require identical programming and are compatible. Reads always come from instance 0, so divergent state in another instance is only caught by sync/fault paths. TLB sync timeout ORs status from all instances; one stuck instance reports the same generic timeout message.

Context fault handling scans every bank and every instance on a shared interrupt, which is robust but can be expensive under repeated faults. Fault logs are rate-limited but still indicate serious device or programming errors.

The page-size workaround for Tegra194/Tegra234 reduces mapping granularity to base pages and can impact performance. It mutates the device page-size bitmap during context initialization, so callers must not assume larger MMU-500 page sizes remain available on those SoCs.

`nvidia_smmu_impl_init` supports at most two mirrored instances via `MAX_SMMU_INSTANCES`, while comments mention a third Tegra194 instance used for isochronous devices. The code intentionally handles the paired non-isochronous instances and stops mapping when platform resources end.

## Test Signals

Tests should cover single-resource and dual-resource probe paths, failure to acquire the Tegra memory controller, additional resource mapping failure, correct selection of single versus multi-instance hook tables, write mirroring across instances, read-from-instance-0 behavior, TLB sync success and timeout with one active instance, global and context fault aggregation/clearing, page-size limiting for Tegra194/Tegra234 only, and memory-controller probe-finalize error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu/arm-smmu-nvidia.c -->
