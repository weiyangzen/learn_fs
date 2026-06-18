<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/tegra241-cmdqv.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/tegra241-cmdqv.c

## Purpose

`tegra241-cmdqv.c` implements NVIDIA Tegra241/Tegra264 CMDQ-V support for the Arm SMMUv3 driver. CMDQ-V provides multiple virtual command queues and virtual interfaces that can accelerate command submission for the kernel and expose guest-owned command queues through iommufd. The file plugs into `arm_smmu_impl_ops`, allocates and maps CMDQV resources, routes supported SMMU commands to secondary queues, handles CMDQV errors, and implements iommufd viommu/hw_queue/vdevice operations for user-owned virtual interfaces.

## Important APIs, Types, and Functions

Core types are `struct tegra241_cmdqv`, `struct tegra241_vintf`, `struct tegra241_vcmdq`, and `struct tegra241_vintf_sid`. `tegra241_cmdqv` embeds `struct arm_smmu_device` as its first member so `devm_krealloc` can replace the generic SMMU object. `tegra241_vintf` embeds `struct arm_vsmmu` for iommufd virtual SMMU integration. `tegra241_vcmdq` embeds `struct iommufd_hw_queue` and contains an `arm_smmu_cmdq`.

Hardware config helpers include `tegra241_cmdqv_write_config`, `cmdqv_write_config`, `vintf_write_config`, `vcmdq_write_config`, and `lvcmdq_error_header`. Interrupt and error handling is in `tegra241_cmdqv_isr`, `tegra241_vintf0_handle_error`, and `tegra241_vintf_user_handle_error`. Queue selection is in `tegra241_cmdqv_get_cmdq`, with guest queue command filtering in `tegra241_guest_vcmdq_supports_cmd`.

Reset and hardware lifecycle are handled by `tegra241_cmdqv_hw_reset`, `tegra241_vintf_hw_init`, `tegra241_vintf_hw_deinit`, `tegra241_vcmdq_hw_init`, `tegra241_vcmdq_hw_deinit`, `tegra241_vcmdq_hw_flush_timeout`, `tegra241_vcmdq_map_lvcmdq`, and `tegra241_vcmdq_unmap_lvcmdq`. Allocation helpers include `tegra241_vcmdq_alloc_smmu_cmdq`, `tegra241_vintf_alloc_lvcmdq`, `tegra241_cmdqv_init_vintf`, `tegra241_cmdqv_init_structures`, and removal helpers.

Implementation registration uses `tegra241_cmdqv_probe`, `__tegra241_cmdqv_probe`, `tegra241_cmdqv_impl_ops`, `tegra241_cmdqv_hw_info`, `tegra241_cmdqv_get_vintf_size`, and `tegra241_cmdqv_init_vintf_user`. iommufd-facing operations include `tegra241_vintf_get_vcmdq_size`, `tegra241_vintf_alloc_lvcmdq_user`, `tegra241_vintf_destroy_lvcmdq_user`, `tegra241_vintf_init_vsid`, `tegra241_vintf_destroy_vsid`, `tegra241_cmdqv_destroy_vintf_user`, and `tegra241_cmdqv_viommu_ops`.

## Control Flow

The main SMMUv3 probe discovers a CMDQV companion device and calls `tegra241_cmdqv_probe`. This file maps the CMDQV resource, honors the `disable_cmdqv` module parameter by disabling hardware and falling back, optionally requests the CMDQV interrupt, reads parameter registers to calculate the number of VINTFs, global VCMDQs, LVCMDQs per VINTF, and SID slots per VINTF, allocates the VINTF pointer table and IDA, and installs early implementation ops.

During main SMMU structure initialization, `tegra241_cmdqv_init_structures` allocates VINTF0 for in-kernel use, preallocates every logical VCMDQ under VINTF0, allocates a normal `arm_smmu_cmdq` for each LVCMDQ, and then installs the final implementation ops. During SMMU reset, `tegra241_cmdqv_hw_reset` disables and re-enables CMDQV, programs global VCMDQ allocation registers to assign queues to VINTFs/LVCMDQs, and initializes VINTF0 as hypervisor-owned.

Command routing happens from the main driver's `arm_smmu_get_cmdq`. If `bypass_vcmdq` is false, VINTF0 is enabled, and the selected per-CPU LVCMDQ exists and supports the command, `tegra241_cmdqv_get_cmdq` returns that secondary command queue. Otherwise the main SMMU command queue is used. LVCMDQ choice is currently `raw_smp_processor_id() % num_lvcmdqs_per_vintf`.

Error IRQ flow reads the VINTF error map and global VCMDQ error maps. VINTF0 errors are handled in-kernel by iterating LVCMDQ error bits, using the common SMMUv3 command error skipper, and acknowledging VCMDQ `GERRORN`. User VINTF errors are packaged into `iommu_vevent_tegra241_cmdqv` and reported through the iommufd viommu event queue.

User VINTF creation initializes a non-hypervisor-owned VINTF, allocates an mmap region for its VINTF page0, copies offsets back to userspace, initializes SID and LVCMDQ locks/IDAs, and installs `tegra241_cmdqv_viommu_ops`. User LVCMDQ allocation validates queue type, local index, strict ascending allocation dependency, power-of-two length, maximum IDR1 command queue size, physical address mask and alignment, maps the global VCMDQ, programs the queue base, and registers a destroy callback. User vdevice initialization allocates a SID mapping slot and writes SID_REPLACE/SID_MATCH for a physical SID to virtual SID mapping.

## State and Persistence Behavior

CMDQV state is volatile kernel and MMIO state. `tegra241_cmdqv` stores hardware parameters, the CMDQV MMIO base and physical base, IRQ, VINTF ID allocator, and VINTF pointer array. VINTF state tracks index, enable state, hypervisor ownership read back from hardware, local command queues, userspace mutex, mmap offset, and SID mapping allocator. VCMDQ state tracks global/local queue indexes, enabled state, queue dependency, parent pointers, embedded SMMU command queue, and two MMIO pages.

Hardware state persists until reset/remove: CMDQV enable state, global VCMDQ allocation registers, VINTF enable/config including VMID and ownership, SID replacement/match registers, VCMDQ queue base and enable state, and error status registers. Removal deinitializes VINTFs, LVCMDQs, global allocations, IRQ, MMIO mapping, and the companion device reference.

User-owned resources are lifetime-managed through iommufd destroy callbacks. The driver relies on iommufd dependency tracking to enforce descending destruction order for LVCMDQs after requiring ascending allocation order.

## Dependencies and Integration Points

The file depends on the SMMUv3 core header, iommufd viommu/hw_queue/vdevice APIs, uapi iommufd Tegra241 structures, DMA mapping, debugfs, platform resources, interrupts, and polling helpers. It imports the `IOMMUFD` namespace. It integrates with the main driver through `arm_smmu_impl_ops`, with `get_secondary_cmdq` for kernel acceleration and with `hw_info`/`get_viommu_size`/`vsmmu_init` for user-visible virtual SMMU support.

It also uses common SMMUv3 queue initialization and command issue helpers. Each LVCMDQ is represented as an `arm_smmu_cmdq`, so most command publication, valid-map, and sync logic remains in the generic driver.

## Risks and Edge Cases

The hardware has strict order requirements: LVCMDQs must be mapped in ascending order and unmapped in descending order. User allocation enforces the forward dependency, and iommufd dependencies help enforce destruction order, but failures in mid-initialization need to undo mapping, local table insertion, and dependencies exactly once.

Guest-owned queues support only `TLBI_NH_ASID`, `TLBI_NH_VA`, and `ATC_INV`. Unsupported commands must fall back to the kernel queue; otherwise a guest queue could receive commands hardware does not permit. The module parameter `bypass_vcmdq` and debugfs bool intentionally force fallback for comparison/debugging.

`tegra241_vcmdq_hw_deinit` issues a CMD_SYNC on the main SMMU queue to flush a possible guest ATC timeout before reassigning a queue. This protects future VMs from stale timeout reports, but it assumes the main queue remains operational during deinit.

User physical queue base validation is security-sensitive. The base must fit the VCMDQ address field and align to queue length. The userspace VINTF mmap exposes only the VINTF page0 window, while queue memory is supplied by userspace physical address through iommufd.

Error reporting splits VINTF0 and user VINTFs. VINTF0 actively rewrites bad commands to CMD_SYNC via common skip logic, while user errors become events. Event delivery depends on a configured iommufd event queue; otherwise diagnostics may be limited to kernel warnings.

## Test Signals

Tests should cover probe fallback when resource mapping, IRQ request, parameter allocation, or `disable_cmdqv` fails; VINTF0 preallocation and reset ordering; secondary command queue routing and fallback for unsupported commands; `bypass_vcmdq`; per-CPU LVCMDQ selection; VCMDQ enable/disable polling timeouts; guest queue timeout flushing; VINTF error IRQ handling for VINTF0 and user VINTFs; hardware info output; viommu mmap output; user queue length/address/index validation; ascending allocation and descending destruction dependency; SID replacement allocation/exhaustion; and cleanup paths for partially initialized user VINTFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/arm/arm-smmu-v3/tegra241-cmdqv.c -->
