# Research: subset-b-001369

Grouped research for AMDGPU VI/VPE and AMDKFD CIK/CWSR source files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.c

## Purpose
`vi.c` implements the common AMDGPU "Volcanic Islands" ASIC support layer. It provides shared register accessors, ASIC function callbacks, reset policy, clock setup, BIOS/ROM access, clock and power-gating controls, doorbell setup, video codec capability reporting, SR-IOV hooks, and per-chip IP block registration for Topaz, Tonga, Fiji, Polaris, VegaM, Carrizo, and Stoney families.

## Important APIs, Types, And Functions
The externally visible entry points are `vi_srbm_select()`, `vi_set_virt_ops()`, `vi_set_ip_blocks()`, and `legacy_doorbell_index_init()`. The file also installs a private `amdgpu_asic_funcs` table through `vi_common_early_init()`, including callbacks for BIOS reads, register reads, reset, clock programming, HDP flush/invalidate, PCIe counters, BACO support, and video codec queries. Register access helpers include `vi_pcie_rreg/wreg`, `vi_smc_rreg/wreg`, `cz_smc_rreg/wreg`, `vi_uvd_ctx_rreg/wreg`, `vi_didt_rreg/wreg`, and `vi_gc_cac_rreg/wreg`. Initialization is exposed to the IP framework through `vi_common_ip_funcs` and `vi_common_ip_block`.

## Control Flow
The AMDGPU device setup path calls `vi_set_ip_blocks()`, which selects an ordered list of IP blocks based on `adev->asic_type`, virtual-display state, DC support, SR-IOV VF status, and optional ACP support. The common IP block then runs `vi_common_early_init()`, where register accessor functions, ASIC callbacks, revision IDs, external revision IDs, and clock/power-gating flags are established. Hardware init programs golden registers, ASPM, and doorbell aperture state. Suspend/resume map to hardware fini/init, and late/software init attach SR-IOV mailbox IRQ state when applicable.

Reset flow chooses between BACO and PCI config reset in `vi_asic_reset_method()` and `vi_asic_reset()`. PCI config reset clears bus mastering, triggers config reset, polls `CONFIG_MEMSIZE`, restores bus mastering, and updates scratch engine-hung state. Clock programming for UVD/VCE uses AtomBIOS dividers, SMC registers, and timeout loops. ASPM programming is gated by policy and ASIC generation, then writes multiple PCIe/SMC/BIF registers and accounts for L1 substates and Polaris revision quirks.

## State And Persistence
The code mutates persistent in-memory device state such as `adev->asic_funcs`, register accessor callbacks, `adev->rev_id`, `adev->external_rev_id`, `adev->cg_flags`, `adev->pg_flags`, `adev->doorbell_index`, `adev->has_hw_reset`, and SR-IOV virtual settings. Hardware state is changed through MMIO/SMC/PCIe register writes for golden registers, clock dividers, ASPM, doorbell aperture, HDP flush/invalidate, clock gating, and ring-emitted HDP operations. BIOS reads temporarily modify ROM/VGA control registers and restore them before returning.

## Dependencies And Integration Points
This file sits at the center of the VI AMDGPU stack. It depends on generated ASIC register headers, AtomBIOS helpers, DPM/SMU services, PCI helpers, the AMDGPU IP block framework, display backends (`dm_ip_block`, DCE, VKMS), memory controllers (`gmc_v7_4`, `gmc_v8_*`), interrupt handlers, graphics/SDMA/UVD/VCE blocks, ACP when configured, and SR-IOV support in `mxgpu_vi`. Register read whitelisting supports debug/ioctl paths that expose only selected status/configuration registers.

## Risks
Most risk is hardware-sequencing risk: incorrect ASIC dispatch, revision mapping, clock-gating flags, or register offsets can hang devices or break power management. Indirect register access relies on spinlocks and readbacks; missed locking would corrupt index/data windows. ASPM programming is especially revision-sensitive and touches PCIe link behavior. `vi_read_bios_from_rom()` casts the BIOS buffer to `u32 *` and reads aligned dwords, so callers must provide suitable storage and size. `vi_common_get_clockgating_state()` sets `*flags = 0` for SR-IOV but continues reading registers, which is benign only if those reads are valid for the VF path.

## Test Signals
Useful signals are successful boot/probe across all VI ASIC types, absence of MMIO timeout or GPU reset errors, correct `amdgpu_device_ip_block_add()` order, successful UVD/VCE ring tests after clock programming, suspend/resume stability, BACO and PCI reset recovery, expected debug register reads, PCIe replay/usage counters, and power-management tests that verify clock-gating flags and ASPM behavior. SR-IOV should exercise mailbox IRQ attach/detach and virtual display paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.h

## Purpose
`vi.h` is the public local header for the AMDGPU VI common implementation. It exposes the VI-specific setup and selection helpers used by other AMDGPU components while keeping the large implementation details in `vi.c`.

## Important APIs, Types, And Functions
The header defines `VI_FLUSH_GPU_TLB_NUM_WREG` as the number of write-register operations needed for a VI GPU TLB flush sequence. It declares `vi_srbm_select()`, `vi_set_virt_ops()`, `vi_set_ip_blocks()`, and `legacy_doorbell_index_init()`.

## Control Flow
Other VI-era blocks include this header when they need to select an SRBM register instance, install virtualization operations, populate the device IP block list, or initialize legacy doorbell indices. The implementation is called during device discovery and IP block setup.

## State And Persistence
This header itself owns no state. Its declared functions mutate `amdgpu_device` hardware and software state in `vi.c`, including SRBM selection registers, virtual operation tables, IP block lists, and doorbell index assignments.

## Dependencies And Integration Points
It depends on the including translation unit already knowing `struct amdgpu_device` and `u32`. It integrates VI common code with GFX, KIQ, VM/TLB, virtualization, and device initialization paths.

## Risks
The file has low direct risk, but it is an ABI-like internal contract: changing declarations, the TLB write-count constant, or doorbell helper name can break multiple VI-generation source files. The include guard name `__VI_H__` differs from `vid.h`'s `VI_H`, avoiding a direct collision.

## Test Signals
Compile coverage is the primary signal. Runtime signals come indirectly from VI probe, SRBM-indexed register access, KIQ/TLB flush paths using the constant, and queue doorbell operation after `legacy_doorbell_index_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vid.h

## Purpose
`vid.h` collects VI-era register offsets, PM4 packet helpers, packet opcodes, VCE/HEVC command IDs, SDMA/CRTC/DIG/audio/HPD instance offsets, and raster configuration bit helpers. It is a constants-only companion used by ring emitters, queue managers, and VI ASIC code.

## Important APIs, Types, And Functions
There are no functions or types. Important macro groups include SDMA instance offsets, display/audio/hotplug instance offsets, `PIPEID/MEID/VMID/QUEUEID`, memory type masks, PM4 packet constructors (`PACKET0`, `PACKET2`, `PACKET3`, `PACKET3_COMPUTE`), many `PACKET3_*` opcodes and field helpers, VCE and HEVC command constants, and raster backend mapping helpers for `PA_SC_RASTER_CONFIG` and `PA_SC_RASTER_CONFIG_1`.

## Control Flow
The macros are expanded by callers when building command buffers or interpreting packet headers. They do not execute directly, but they encode GPU command-processor contracts: packet type, count, opcode, destination selection, cache policy, synchronization, queue mapping, unmapping, query status, and DMA control fields.

## State And Persistence
The header owns no software state. Its constants shape persistent GPU command streams submitted to rings and IBs. Incorrect bit encodings can persist in ring buffers, MQDs, fences, or indirect buffers until consumed by hardware.

## Dependencies And Integration Points
`vid.h` is included by `vi.c` and may be used by VI-era GFX, SDMA, VCE, HEVC, KIQ, and queue-management code. It integrates with register definitions from generated ASIC headers and with common AMDGPU ring-write helpers that expect correctly packed PM4 words.

## Risks
Macro correctness is critical because the compiler cannot validate GPU packet semantics. Some helpers do not parenthesize every argument in a defensive style and several macros encode raw bit shifts; accidental signed or oversized inputs can bleed into adjacent fields. Packet count fields have hardware limits, so callers must bound counts before invoking constructors. Any opcode or field change risks hard GPU hangs rather than clean software failures.

## Test Signals
Compile coverage catches only syntax and missing macro names. Runtime signals include passing ring tests, successful fence/trap/write-data/wait-reg-mem operations, KIQ map/unmap/query flows, VCE/HEVC command submission, and GPU recovery tests that do not show bad opcode interrupts or command processor stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_6_1_fw_if.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_6_1_fw_if.h

## Purpose
`vpe_6_1_fw_if.h` defines the command ABI between the AMDGPU VPE driver and VPE 6.1 firmware. It supplies opcode enums and bitfield macros for building VPE command stream words.

## Important APIs, Types, And Functions
The main enum is `enum VPE_CMD_OPCODE`, covering NOP, VPE descriptor, plane config, VPEP config, indirect buffer, fence, trap, register write, poll reg/mem, conditional execute, atomic, predicated execute, collaboration sync, and timestamp commands. Subopcode enums cover plane config and VPEP config modes. Key macros include `VPE_CMD_HEADER()`, `VPE_CMD_NOP_HEADER_COUNT()`, `VPE_DESC_CMD_HEADER()`, `VPE_PLANE_CFG_CMD_HEADER()`, `VPE_DIR_CFG_CMD_HEADER()`, `VPE_IND_CFG_CMD_HEADER()`, `VPE_CMD_INDIRECT_HEADER_VMID()`, and poll-regmem interval/retry/function/memory field helpers.

## Control Flow
The header has no direct control flow. Callers such as `amdgpu_vpe.c` use these macros while emitting VPE ring and IB packets for fences, traps, predication, indirect buffers, polling, and register writes. VPE firmware interprets the encoded words and performs the actual control flow.

## State And Persistence
No C state is stored here. The macro output becomes persistent ring/IB data until VPE firmware consumes it. Plane config fields encode source/destination plane counts, swizzle, rotation, pitch, viewport, and element size, so mistakes affect image-processing state in firmware.

## Dependencies And Integration Points
`amdgpu_vpe.h` includes this header, and `amdgpu_vpe.c` uses the command constructors while `vpe_v6_1.c` sets up firmware and rings. The definitions must match the shipped `amdgpu/vpe_6_1_*.bin` firmware interface.

## Risks
The header is a firmware ABI. Any opcode, mask, or shift mismatch can cause silent firmware misinterpretation. Several masks are expressed as field masks but the macros first mask the raw value and then shift; for fields whose mask is already in post-shift position, this pattern can drop valid high bits. `VPE_PLANE_CFG_CMD_HEADER()` appears to use `npd0` for the `NPD1` field, which should be reviewed because it may prevent independent destination-plane count encoding for the second plane.

## Test Signals
Signals include VPE ring tests, successful fence and trap completion, indirect-buffer execution with expected VMID, poll-regmem timeout behavior, and image-processing workloads that cover 1-to-1, 2-to-1, and 2-to-2 plane configurations. Firmware interface changes should be tested with each declared VPE 6.1 firmware binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_6_1_fw_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c

## Purpose
`vpe_v6_1.c` implements the hardware-facing function table for AMD VPE 6.1. It loads VPE firmware, configures collaboration mode and DPM, initializes and starts/stops the VPE ring queue, registers trap IRQ handling, and exposes register offsets to generic VPE code.

## Important APIs, Types, And Functions
The external entry point is `vpe_v6_1_set_funcs()`, which installs `vpe_v6_1_funcs` and `vpe_v6_1_trap_irq_funcs` into `struct amdgpu_vpe`. Important internals are `vpe_v6_1_get_reg_offset()`, `vpe_v6_1_halt()`, `vpe_v6_1_irq_init()`, `vpe_v6_1_set_collaborate_mode()`, `vpe_v6_1_load_microcode()`, `vpe_v6_1_ring_start()`, `vpe_v_6_1_ring_stop()`, `vpe_v6_1_set_trap_irq_state()`, `vpe_v6_1_process_trap_irq()`, and `vpe_v6_1_set_regs()`.

## Control Flow
Generic VPE initialization selects these functions for IP version 6.1. `vpe_v6_1_load_microcode()` first disables UMSCH interrupt enable per instance, enables collaboration and DPM, then either asks PSP to update SRAM or manually halts VPE, writes command-thread and control-thread microcode through `VPEC_UCODE_ADDR/DATA`, and unhalts. `vpe_v6_1_ring_start()` configures queue0 ring size, privilege, VMID, read/write pointers, rptr writeback address, ring base, doorbell offset and range, queue enable, and IB enable for each VPE instance before running `amdgpu_ring_test_helper()`. Stop requests queue reset and waits for reset bits to clear. Trap IRQ processing turns VPE trap interrupts into fence processing on the VPE ring.

## State And Persistence
The file writes VPE instance registers for halt/reset, queue state, ring base, writeback address, doorbell enable/range, collaboration mode, DPM pseudo-registers, trap-enable state, and firmware SRAM. It mutates `vpe->regs`, `vpe->funcs`, `vpe->trap_irq.funcs`, `ring->wptr`, and `ring->sched.ready`. It also uses `adev->vpe.cmdbuf_cpu_addr` as a two-word PSP command buffer for SRAM update.

## Dependencies And Integration Points
Dependencies include VPE register offset/mask headers, SOC21 interrupt IDs, generic AMDGPU VPE helpers, PSP firmware loading, NBIO doorbell-range programming, AMDGPU ring/fence helpers, and `amdgpu_ip_version()` for 6.1.1 register layout exceptions. Firmware files declared with `MODULE_FIRMWARE` are `amdgpu/vpe_6_1_0.bin`, `vpe_6_1_1.bin`, and `vpe_6_1_3.bin`.

## Risks
Register layout differences for IP 6.1.1 are handled by conditionals; missing a renamed register would break queue reset or interrupt setup. Manual microcode loading assumes valid firmware header offsets and sizes and writes two threads per instance. Doorbell offsets add `i * 4`, so instance count and doorbell allocation must match NBIO range programming. `vpe_v_6_1_ring_stop()` returns `ret` after the loop; if `vpe->num_instances` were zero, `ret` would be uninitialized. Ring start writes the same shared ring base for all instances, so collaboration and firmware expectations must align.

## Test Signals
Test signals include firmware request/load success for all declared binaries, PSP and non-PSP load paths, VPE ring test success, fence completion after trap IRQs, queue reset without timeout, suspend/resume ring restart, DPM configuration warnings, multi-instance collaboration mode tests, and doorbell range validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.h

## Purpose
`vpe_v6_1.h` is the local interface for installing VPE 6.1 hardware callbacks into an `amdgpu_vpe` instance.

## Important APIs, Types, And Functions
It includes `amdgpu_vpe.h` and declares `void vpe_v6_1_set_funcs(struct amdgpu_vpe *vpe);`.

## Control Flow
Generic VPE initialization includes this header and calls `vpe_v6_1_set_funcs()` when the discovered VPE IP version should use the 6.1 implementation. After that, generic VPE code calls through the installed function table.

## State And Persistence
The header owns no state. The declared function mutates `vpe->funcs` and `vpe->trap_irq.funcs` in `vpe_v6_1.c`.

## Dependencies And Integration Points
This file bridges generic VPE code (`amdgpu_vpe.c`/`amdgpu_vpe.h`) to the version-specific implementation. Its correctness depends on `struct amdgpu_vpe` being defined by `amdgpu_vpe.h`.

## Risks
Direct risk is low. The main risk is interface drift: if generic VPE initialization changes the callback-install contract, this declaration and implementation must stay synchronized.

## Test Signals
Compile coverage catches declaration mismatches. Runtime evidence is successful selection of VPE 6.1 callbacks, firmware load, ring start, and trap IRQ handling on VPE 6.1 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vpe_v6_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Kconfig

## Purpose
This `Kconfig` file defines build-time configuration options for the AMD HSA/KFD driver: core HSA support, HMM-based shared virtual memory, and peer-to-peer GPU access.

## Important APIs, Types, And Functions
The configuration symbols are `HSA_AMD`, `HSA_AMD_SVM`, and `HSA_AMD_P2P`. `HSA_AMD` depends on `DRM_AMDGPU` and supported 64-bit architectures, and selects `HMM_MIRROR`, `MMU_NOTIFIER`, and `DRM_AMDGPU_USERPTR`. `HSA_AMD_SVM` depends on `HSA_AMD && DEVICE_PRIVATE`, defaults to `y`, and selects HMM/MMU notifier support. `HSA_AMD_P2P` depends on `HSA_AMD && PCI_P2PDMA`.

## Control Flow
There is no runtime control flow. Kernel configuration resolves these symbols before compilation, which determines which source files and code paths are built and which memory-management features are exposed.

## State And Persistence
The selected symbols persist in the kernel `.config` and influence compiled kernel/module contents. They indirectly control runtime availability of KFD char devices, SVM/HMM migration, and P2P paths.

## Dependencies And Integration Points
This file integrates KFD with DRM AMDGPU, Linux HMM, MMU notifier, DEVICE_PRIVATE memory, PCI P2PDMA, and architecture support. Its symbols are consumed by the AMDKFD Makefile and by `#if IS_ENABLED(CONFIG_HSA_AMD_SVM)` or `CONFIG_HSA_AMD_P2P` guards in KFD sources.

## Risks
Incorrect dependencies can allow unsupported builds or hide valid functionality. SVM depends on kernel memory-management features and module parameters such as `amdgpu.noretry=0` for page-fault mode on many GFXv9 GPUs. P2P help text notes runtime chipset, large BAR, and physical address constraints that are not fully represented by Kconfig dependencies.

## Test Signals
Signals include configuration matrix builds across supported architectures, builds with SVM and P2P both enabled/disabled, HIP managed-memory tests, page-fault/preemption SVM tests, and multi-GPU P2P topology/performance validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Makefile

## Purpose
The AMDKFD Makefile enumerates the KFD object files that are linked into the AMDGPU/KFD build. It centralizes the core module, queue, interrupt, topology, debug, SVM, migration, and per-generation manager objects.

## Important APIs, Types, And Functions
The key build variable is `AMDKFD_FILES`. It includes core objects such as `kfd_module.o`, `kfd_device.o`, `kfd_chardev.o`, `kfd_topology.o`, process/queue/device-queue managers, MQD managers for CIK/VI/v9/v10/v11/v12/v12_1, packet managers, interrupt/event handlers, SMI events, CRAT, and debug. Conditional additions include `kfd_debugfs.o` when `CONFIG_DEBUG_FS` is set and `kfd_svm.o` plus `kfd_migrate.o` when `CONFIG_HSA_AMD_SVM` is set.

## Control Flow
There is no runtime flow. During kernel build evaluation, the parent AMDGPU build uses `AMDKFD_FILES` to decide which KFD translation units become part of the module. Kconfig symbols control optional object inclusion.

## State And Persistence
The Makefile does not hold runtime state. It persists build composition: adding, removing, or reordering objects changes which code is linked and can affect initcall availability, symbol resolution, and feature coverage.

## Dependencies And Integration Points
It depends on `AMDKFD_PATH` being set by the including build system and on Kconfig symbols from `amdkfd/Kconfig`. It integrates all KFD generations with the broader `drivers/gpu/drm/amd` build.

## Risks
Missing an object can cause unresolved symbols or disabled runtime features. Including an object without the right Kconfig guard can break builds on configurations that lack supporting kernel APIs. Because multiple hardware generations are listed together, new generation support must update both source and build lists consistently.

## Test Signals
Build tests should cover baseline KFD, `CONFIG_DEBUG_FS`, `CONFIG_HSA_AMD_SVM`, and combinations across supported architectures. Linker errors, modpost warnings, missing debugfs entries, or absent SVM functionality are strong failure signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_event_interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_event_interrupt.c

## Purpose
`cik_event_interrupt.c` implements KFD event interrupt filtering and workqueue processing for CIK-era GPUs. It converts selected IH ring entries into user-visible KFD events, hardware-exception events, SMI VM fault notifications, and process-device eviction on VM faults.

## Important APIs, Types, And Functions
The file exports `event_interrupt_class_cik`, a `struct kfd_event_interrupt_class` with `.interrupt_isr = cik_event_interrupt_isr` and `.interrupt_wq = cik_event_interrupt_wq`. The ISR parses `struct cik_ih_ring_entry`, filters KFD VMID ranges, validates PASID, handles a Hawaii VM fault workaround, and selects interrupt source IDs. The workqueue handler signals events via `kfd_signal_event_interrupt()`, `kfd_signal_hw_exception_event()`, `kfd_signal_vm_fault_event()`, and calls `kfd_evict_process_device()`.

## Control Flow
The interrupt top half receives an IH entry and either rejects it or marks it for deferred KFD processing. For Hawaii VM faults, it patches missing VMID/PASID information by reading VM fault registers and ATC VMID/PASID mappings through `kfd2kgd` callbacks. Normal entries extract VMID/PASID from `ring_id`, reject non-KFD VMIDs and zero PASIDs, and accept EOP, SDMA trap, SQ message, bad opcode, and optionally VM fault sources. The workqueue then decodes the same source IDs and signals the appropriate event or fault path.

## State And Persistence
This file does not own persistent structures, but it mutates event state in KFD process/event subsystems, updates SMI VM fault state, evicts process-device queues on faults, and may write a patched IH entry into caller-provided storage. It also references global module policy `amdgpu_no_queue_eviction_on_vm_fault`.

## Dependencies And Integration Points
It depends on `kfd_priv.h`, `kfd_events.h`, `cik_int.h`, `amdgpu_amdkfd.h`, `kfd_smi_events.h`, KFD VMID range metadata, and KGD callbacks in `struct kfd2kgd_calls`. `kfd_device.c` installs `event_interrupt_class_cik` for CIK devices.

## Risks
Interrupt filtering must be exact: accepting foreign VMIDs could signal the wrong process, while rejecting valid PASIDs can lose user events or faults. The Hawaii workaround trusts fallback register reads and mapping callbacks. VM fault handling must unref looked-up processes on all paths; this file does so after signaling or after empty fault info, but early `!pdd` returns rely on lookup semantics. Queue eviction policy is tied to `amdgpu_no_queue_eviction_on_vm_fault`.

## Test Signals
Signals include EOP, SDMA trap, and SQ message user event delivery; bad opcode hardware exception delivery; CIK VM fault reporting with process eviction; Hawaii-specific patched VM fault entries; no warnings for valid PASIDs; and interrupt rejection for non-KFD VMIDs. Stress tests should include concurrent process teardown during fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_event_interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_int.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_int.h

## Purpose
`cik_int.h` defines the CIK interrupt-ring entry layout and source IDs used by AMDKFD CIK interrupt processing.

## Important APIs, Types, And Functions
The main type is `struct cik_ih_ring_entry`, containing `source_id`, `data`, `ring_id`, and `reserved` dwords. Defined source IDs include CP end-of-pipe, CP bad opcode, SDMA trap, SQ interrupt message, GFX page invalid fault, and GFX memory protection fault.

## Control Flow
There is no direct control flow. `cik_event_interrupt.c` casts raw IH ring-entry dwords to this structure, decodes `source_id`, and extracts VMID/PASID from `ring_id`.

## State And Persistence
The header owns no state. It describes the binary interrupt payload format persisted in the GPU IH ring until software consumes it.

## Dependencies And Integration Points
It includes `<linux/types.h>` for fixed-width integer types and is consumed by CIK interrupt/event code. Its constants must match CIK hardware firmware interrupt source encodings.

## Risks
Structure layout and source IDs are ABI-like hardware contracts. Any packing, field order, or constant mistake causes interrupts to be misclassified. Because users cast from raw `uint32_t *`, alignment and size assumptions must remain four dwords.

## Test Signals
Compile coverage plus runtime interrupt tests are needed. Expected signals include correct event delivery for all listed sources, correct VMID/PASID extraction from `ring_id`, and no bad-opcode or VM fault misclassification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_regs.h

## Purpose
`cik_regs.h` provides CIK KFD register-field helper macros and default values for queue, memory, HQD, doorbell, and scheduling setup.

## Important APIs, Types, And Functions
There are no functions or types. Important macros include `PRIVATE_BASE`, `SHARED_BASE`, `PTR32`, `ALIGNMENT_MODE`, memory type constants, `DEFAULT_CP_HQD_PERSISTENT_STATE`, `PRELOAD_REQ`, `MQD_CONTROL_PRIV_STATE_EN`, `DEFAULT_MIN_IB_AVAIL_SIZE`, `IB_ATC_EN`, quantum fields, read-pointer block/min-available defaults, `PQ_ATC_EN`, `NO_UPDATE_RPTR`, `DOORBELL_OFFSET`, `DOORBELL_EN`, `PRIV_STATE`, `KMD_QUEUE`, `AQL_ENABLE`, and `GRBM_GFX_INDEX`.

## Control Flow
Callers use these macros while initializing MQDs, HQDs, queue properties, memory apertures, and doorbells. The macros expand into bit patterns consumed by GPU registers.

## State And Persistence
The header owns no state. Its values become persistent hardware queue state in MQDs and registers, including memory aperture behavior, ATC enablement, read pointer behavior, queue privilege, and scheduling quantum.

## Dependencies And Integration Points
It is used by CIK KFD queue/device-queue/MQD managers, and indirectly depends on CIK hardware register semantics. A repository search shows `PRIVATE_BASE` and `DEFAULT_CP_HQD_PERSISTENT_STATE` used by CIK queue manager and MQD manager code.

## Risks
Incorrect bit positions can corrupt queues or memory aperture configuration. Default ATC, pointer, and doorbell flags affect address translation, ring progress, and interrupt behavior. The macros are raw shifts without validation, so callers must bound and sanitize inputs.

## Test Signals
Signals include successful CIK queue creation/destruction, AQL dispatch, doorbell writes, HQD scheduling, scratch/LDS aperture correctness, ATC-enabled memory access, and no queue hangs under preemption or pointer-update stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cik_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler.h

## Purpose
`cwsr_trap_handler.h` embeds preassembled Compute Wave Save/Restore trap-handler instruction images for multiple AMD GFX generations. KFD copies the appropriate image into per-process CWSR memory so GPU waves can be saved and restored for preemption/debug/runtime control.

## Important APIs, Types, And Functions
The file defines static `uint32_t` arrays, not C functions. Arrays are `cwsr_trap_gfx8_hex`, `cwsr_trap_gfx9_hex`, `cwsr_trap_nv1x_hex`, `cwsr_trap_arcturus_hex`, `cwsr_trap_aldebaran_hex`, `cwsr_trap_gfx10_hex`, `cwsr_trap_gfx11_hex`, `cwsr_trap_gfx9_4_3_hex`, `cwsr_trap_gfx12_hex`, `cwsr_trap_gfx9_5_0_hex`, and `cwsr_trap_gfx12_1_0_hex`.

## Control Flow
The control flow is GPU microcode, not C. On the CPU side, `kfd_device.c` selects an array based on GPU generation, checks that selected images fit within a page using `BUILD_BUG_ON`, and stores `kfd->cwsr_isa` plus `kfd->cwsr_isa_size`. `kfd_process.c` later copies the selected image into process/device CWSR backing memory. On the GPU, these instruction streams implement trap-time wave save/restore behavior.

## State And Persistence
The arrays are read-only kernel data. Once selected and copied, the bytes persist in GPU-accessible process CWSR memory and become part of queue/process execution state. The selected pointer and size persist in `struct kfd_dev`.

## Dependencies And Integration Points
This header is included by KFD device setup and depends on exact ISA encodings for each GPU generation. It integrates with KFD preemption, process queue state, debug/trap handling, and memory allocation for CWSR areas. The size checks in `kfd_device.c` constrain each selected image to page-sized storage.

## Risks
This is opaque binary firmware-like content. A single word change can break trap handling, corrupt wave context, or hang the GPU. Review and testing require disassembly or provenance from AMD's assembler flow, because C compilers cannot validate instruction semantics. Size growth beyond expected page limits breaks build-time checks or runtime copy assumptions. Endianness and alignment matter because the arrays are 32-bit words copied as instruction bytes.

## Test Signals
Signals include build-time `BUILD_BUG_ON` size checks, successful KFD process creation with CWSR allocation/copy, compute preemption under load, debugger trap handling, queue eviction/requeue, suspend/resume with active queues, and generation-specific stress tests for every array selected by `kfd_device.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/cwsr_trap_handler.h -->
