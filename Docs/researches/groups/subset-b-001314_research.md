# Group Research: subset-b-001314

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_device.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_device.c

## Purpose

`amdgpu_device.c` is the central AMDGPU device lifecycle and recovery implementation. It owns device bring-up, IP block discovery/init/fini sequencing, runtime/system power transitions, GPU reset and PCI error recovery, sysfs registration, firmware/VBIOS handling, scheduler setup, PCIe capability/state management, VRAM/MMIO access helpers, RAS/KFD/XGMI integration, and small cross-cutting utilities such as UID storage and isolation fences. Most higher-level AMDGPU driver paths eventually pass through this file when a PCI GPU is initialized, suspended, resumed, reset, or removed.

The file is organized as a set of orchestration helpers around `struct amdgpu_device`. It does not define the hardware IP implementations themselves; instead it discovers and walks `adev->ip_blocks[]` and invokes function tables supplied by ASIC/IP-specific code. The persistent kernel state is almost entirely stored in `adev` substructures: firmware, power management, graphics, memory controller, writeback, virtual/SR-IOV, reset domain, RAS, XGMI, PCI reset context, and scheduler/ring state.

## Important APIs, Data, and Entry Points

- Init-level state: `amdgpu_init_default`, `amdgpu_init_recovery`, and `amdgpu_init_minimal_xgmi` describe which IP block types are expected to receive hardware init. `amdgpu_set_init_level()` switches `adev->init_lvl`, and `amdgpu_ip_member_of_hwini()` gates init/resume/suspend work by IP type.
- Public lifecycle entry points: `amdgpu_device_init()`, `amdgpu_device_fini_hw()`, `amdgpu_device_fini_sw()`, `amdgpu_device_prepare()`, `amdgpu_device_complete()`, `amdgpu_device_suspend()`, and `amdgpu_device_resume()` are called from the DRM/PCI driver layer.
- IP block orchestration: `amdgpu_device_ip_early_init()`, `amdgpu_device_ip_init()`, `amdgpu_device_ip_late_init()`, `amdgpu_device_ip_fini_early()`, `amdgpu_device_ip_fini()`, `amdgpu_device_ip_suspend_phase1()`, `amdgpu_device_ip_suspend_phase2()`, and the three `amdgpu_device_ip_resume_phase*()` helpers enforce ordering around COMMON/GMC/IH/PSP/display/non-display blocks.
- Reset/recovery API: `amdgpu_device_gpu_recover()`, `amdgpu_device_asic_reset()`, `amdgpu_do_asic_reset()`, `amdgpu_device_pre_asic_reset()`, `amdgpu_device_reinit_after_reset()`, `amdgpu_device_mode1_reset()`, `amdgpu_device_link_reset()`, `amdgpu_device_baco_enter()`, and `amdgpu_device_baco_exit()` coordinate soft reset, full reset, BACO/mode/link reset, SR-IOV reset, XGMI hive reset, scheduler stop/start, KFD, user queues, RAS, and display/client suspension.
- PCI error recovery: `amdgpu_pci_error_detected()`, `amdgpu_pci_mmio_enabled()`, `amdgpu_pci_slot_reset()`, and `amdgpu_pci_resume()` implement Linux PCI AER/DPC style callbacks and reuse the same reset machinery with PCI state restore and hive handling.
- Sysfs/user-visible helpers: `pcie_replay_count`, binary `reg_state`, `board_info`, UMA carveout attributes, firmware/PM/FRU/XCP sysfs registration, `amdgpu_get_soft_full_reset_mask()`, and `amdgpu_show_reset_mask()`.
- Memory/register helpers: `amdgpu_device_mm_access()`, `amdgpu_device_aper_access()`, `amdgpu_device_vram_access()`, `amdgpu_device_program_register_sequence()`, `amdgpu_device_flush_hdp()`, and `amdgpu_device_invalidate_hdp()` provide controlled access to VRAM/MMIO and HDP cache coherency.
- Writeback and scratch state: `amdgpu_device_wb_init()`, `amdgpu_device_wb_get()`, `amdgpu_device_wb_free()`, `amdgpu_device_wb_fini()`, `amdgpu_device_mem_scratch_init()`, and `amdgpu_device_mem_scratch_fini()` allocate and track GPU-visible memory used by fences/ring pointers and scratch operations.
- PCI/runtime power helpers: `amdgpu_device_supports_px()`, `amdgpu_device_supports_boco()`, `amdgpu_device_supports_baco()`, `amdgpu_device_detect_runtime_pm_mode()`, `amdgpu_device_supports_smart_shift()`, ASPM/PCIe bandwidth capability helpers, BAR resize, PCI state cache/restore, and switcheroo callbacks integrate with ACPI, PCI core, runtime PM, and hybrid GPU power control.
- Scheduler/isolation utilities: `amdgpu_device_init_schedulers()`, `amdgpu_device_has_job_running()`, `amdgpu_device_get_gang()`, `amdgpu_device_switch_gang()`, and `amdgpu_device_enforce_isolation()` wire DRM scheduler instances, gang submission ordering, and client isolation fences.
- UID helpers: `amdgpu_uid_init()`, `amdgpu_uid_fini()`, `amdgpu_device_set_uid()`, and `amdgpu_device_get_uid()` store per-type/per-instance unique IDs for multi-AID devices.

## Control Flow

Device initialization starts in `amdgpu_device_init()`. It initializes scalar defaults, resets ring/accounting pointers, allocates fence contexts, initializes locks/work items/sync objects, maps MMIO BARs, creates an early reset domain, detects virtualization and PCIe capabilities, validates module parameters, and selects the default init level. It then calls `amdgpu_device_ip_early_init()` to choose ASIC/IP block tables (`si_set_ip_blocks()`, `cik_set_ip_blocks()`, `vi_set_ip_blocks()`, or IP discovery), parse GPU info firmware, load/init VBIOS, set PX/PR3/PP feature flags, initialize XGMI and KFD probe state, and mark valid IP blocks.

After early init, `amdgpu_device_init()` removes conflicting framebuffers for display-class devices, configures TMZ/noretry/XGMI/atomics/doorbells, initializes reset support, optionally resets or posts the ASIC, parses clock/I2C information, initializes the fence driver and DRM mode config, then enters `amdgpu_device_ip_init()`. The IP init pass calls `sw_init` for each valid IP, performs early `hw_init` for COMMON and GMC so GPU memory can be allocated, initializes scratch, writeback, CSA, seq64, IB pool and ucode BOs, runs phase1 hardware init, firmware loading, phase2 hardware init, RAS bad-page recovery, XGMI reset-domain sharing, scheduler creation, TTM buffer-function enablement, KFD init, FRU, and CPER. Finally `amdgpu_device_init()` runs fence hardware init, marks acceleration working, registers the GPU instance, performs late init/gating/RAS resume/IB test work for normal init levels, handles SR-IOV release, initializes KFD zone/SVM, optionally triggers XGMI reset-on-init, creates sysfs and PMU hooks, caches PCI state, registers VGA/switcheroo, detects IOMMU mapping, and registers a PM notifier.

Suspend is split for ordering and recovery. `amdgpu_device_prepare()` evicts VRAM resources and lets IPs prepare. `amdgpu_device_suspend()` marks `in_suspend`, handles SR-IOV full-GPU access, updates SmartShift, suspends DRM clients, cancels delayed work, suspends RAS, runs display-first IP suspend phase1, suspends KFD/user queues, evicts resources, disables TTM buffer funcs/fence HW, then runs non-display phase2. Failure paths unwind through resume phases, KFD/user queue resume, SmartShift D0, client resume, RAS resume, and SR-IOV reacquisition. `amdgpu_device_resume()` reacquires SR-IOV access, handles XGMI migration, posts if needed, resumes IP phase1, firmware, phase2, fence hardware, phase3, KFD/user queues, late init, delayed IB tests, client hotplug, RAS, VRAM reset block cleanup, and SmartShift D0.

Teardown is also split. `amdgpu_device_fini_hw()` flushes delayed work, drains TTM workqueue, unregisters PM notifier, handles SR-IOV access, ungates power/clock, disables IRQs and display, tears down fence HW, sysfs, RAS, TTM buffer funcs, KFD if disconnected, coredump state, early IP hardware fini, IRQ hardware, DMA mappings, dummy page, and MMIO on surprise removal. `amdgpu_device_fini_sw()` runs IP software fini in reverse order, releases fence SW, firmware, gang/isolation sync state, reset domain, I2C, BIOS, FRU/XCP, switcheroo/VGA, MMIO, PMU/discovery, PCI saved state, and bridge saved state.

GPU recovery starts with `amdgpu_device_gpu_recover()`. It yields to RAS if needed, handles emergency restart policy, acquires an XGMI hive if present, builds a reset list, checks bus health, runs RAS pre-reset, locks the reset domain, and calls `amdgpu_device_halt_activities()` to suspend audio, stop error queries, cancel delayed work, pre-reset KFD/user queues, unregister GPU instances, suspend DRM clients, maybe suspend RAS, stop all schedulers, and increment reset counters. It can skip hardware reset if the guilty job is already signaled. Otherwise `amdgpu_device_asic_reset()` runs `amdgpu_device_pre_asic_reset()` for each device, chooses SR-IOV reset or bare-metal reset, retries selected failures, then drops stale pending reset work. Bare-metal `amdgpu_do_asic_reset()` prefers the reset-handler abstraction, otherwise performs parallel XGMI resets if needed, clears RAS interrupts, and reinitializes via `amdgpu_device_reinit_after_reset()`. Reinit reposts the ASIC, resumes IP phases, checks VRAM loss with reset magic, dumps coredump state, reloads firmware, restores XCP partitioning, re-enables TTM buffer funcs, late-inits, restores user queues, resumes DRM clients/RAS, updates XGMI topology, runs IB tests, and returns devices to default init level. Scheduler and GPU resume then restart DRM schedulers, report reset success/failure, post-reset KFD, re-enable audio, clear MP1 state, and re-enable RAS queries.

PCI AER recovery is a related but distinct lane. `amdgpu_pci_error_detected()` records the channel state, handles normal/frozen/permanent states, checks XGMI/link-reset support, may set DPC status, locks hives, builds the reset list, locks the reset domain, and halts device activities before returning `NEED_RESET`. `amdgpu_pci_slot_reset()` waits for the device/vendor ID to return, restores switch and device PCI config state, confirms memory size is readable, marks link-reset state, and invokes `amdgpu_device_asic_reset()` with full reset and coredump skipped. `amdgpu_pci_resume()` later clears link-reset state, resumes schedulers and GPU-side services, and unlocks the reset domain.

## State and Persistence Behavior

Persistent runtime state lives in `struct amdgpu_device` and subordinate structs. `adev->ip_blocks[].status` tracks `valid`, `sw`, `hw`, `late_initialized`, and `hang` for each hardware block and drives all init/suspend/resume/fini walks. `adev->init_lvl` chooses whether all blocks, reset-recovery blocks, or only a minimal XGMI-capable subset receive hardware init. `adev->reset_domain` supplies the reset semaphore, reset result, reset workqueue, and `in_gpu_reset` flag used by lockdep and schedulers. XGMI devices may replace their single-device reset domain with a hive reset domain after XGMI add-device succeeds.

Power and suspend state is tracked through flags such as `in_suspend`, `in_s0ix`, `in_s3`, `in_s4`, `in_runpm`, `shutdown`, `accel_working`, `no_hw_access`, `mp1_state`, runtime PM mode, SmartShift state, clock/power gating flags, and module-parameter-derived values. PCI persistence includes `adev->pci_state`, `pcie_reset_ctx.swds_pcistate`, `pcie_reset_ctx.swus_pcistate`, `pcie_reset_ctx.swus`, `pcie_reset_ctx.audio_suspended`, and `pcie_reset_ctx.in_link_reset`; these are used to restore device and AMD switch bridge state after mode reset, link reset, or AER recovery.

Memory state includes kernel BOs for scratch, writeback, ucode, CSA, seq64, IB pool, GART reset magic, and mapped MMIO/VRAM aperture pointers. `amdgpu_device_fill_reset_magic()` and `amdgpu_device_check_vram_lost()` persist a small sentinel in VRAM to detect memory loss across reset, with BACO/mode1/link/legacy resets treated as VRAM-losing in reset context. `adev->wb.used` is a bitmap protected by `adev->wb.lock`; `adev->mmio_idx_lock` serializes indirect MMIO index/data access.

The file also persists sysfs-visible and cross-subsystem state: UMA carveout entries and selected index with an update mutex, firmware sysfs enabled state, PM sysfs initialized state, board/form-factor attributes, RAS error query readiness, KFD initialization and process suspension state, XCP partition scheduler lists, gang submission fence pointer under RCU/cmpxchg, per-XCP isolation sync fences, UID tables, GPU instance registry membership, and MGPU fan boost state in global `mgpu_info`.

## Dependencies and Integration Points

This file integrates with the Linux DRM core (`drm_device`, mode config, atomic/helper suspend/resume, DRM clients, DRM scheduler, wedge events), PCI core (BARs, config space, reset, AER callbacks, P2P DMA, rebar, ASPM, bridge topology), ACPI and platform power (`ATPX`, BOCO/BACO/MACO, SmartShift, PR3, Apple gmux, power supply), firmware loaders (`request_firmware`, AMDGPU ucode request/release), atom BIOS/atom firmware, AMDGPU ASIC/IP function tables, TTM memory management, KFD/HSA, RAS/CPER/FRU/EEPROM, XGMI hive and topology management, virtualization/SR-IOV PF/VF mailbox and exclusive access, PM/SMU/DPM, PSP, doorbells, IRQ/fence/ring infrastructure, debug/coredump, PMU/perf, sysfs/devm groups, IOMMU, and architecture memory type APIs.

The IP block model is the strongest internal dependency. `amdgpu_device.c` assumes each block’s `amdgpu_ip_block_version->funcs` implements the appropriate lifecycle callbacks and that ordering by block type is enough to satisfy hardware dependencies. COMMON and GMC are special because early hardware init is required before memory allocations; PSP is special for firmware loading and SR-IOV; DCE/display is split into a separate suspend/resume phase; SMC/SMU is special for MP1 state during reset; GFX/SDMA/MES are special for S0ix behavior; UVD/VCE/VCN/JPEG are excluded from generic clock/power gating loops.

## Risks and Edge Cases

- Ordering regressions are high impact. Many callbacks are invoked by block type and status bits rather than explicit dependency graph, so moving a step around can break firmware loading, GPU memory allocation, RAS EEPROM I2C, display suspend, or KFD resume.
- Reset concurrency is delicate. The code mixes hive locks, reset-domain semaphores, scheduler stop/start, work cancellation, RAS recovery work, user queue reset work, SR-IOV FLR work, delayed IB tests, and PCI AER callbacks. Incorrect lock ordering or missing work cancellation can deadlock or allow hardware access during reset.
- SR-IOV and bare-metal paths diverge substantially. VF reset can wait for host FLR, request/release full GPU access, exchange PF/VF data, retry `-EBUSY`, `-ETIMEDOUT`, and `-EINVAL`, and resume RAS telemetry; changes must preserve both runtime and non-runtime VF behavior.
- XGMI hive reset has tight timing and topology constraints. Parallel reset work uses task barriers for BACO and system workqueue for hive nodes, then the code must update topology and share/reset domains correctly.
- VRAM-loss handling is conservative and reset-method dependent. Incorrect reset-method classification or reset magic placement could cause stale VRAM contents to be trusted or valid contents to be discarded.
- PCI state restore is hardware-topology-specific. AMD upstream/downstream switch state is cached only when the expected bridge topology is found; AER paths must tolerate missing saved bridge state and disconnected devices.
- Sysfs callbacks expose hardware state and ACPI writes. UMA carveout writes use `array_index_nospec()` and a mutex, but still depend on valid VBIOS-derived option tables and ACPI support. Register-state and replay-count sysfs require ASIC support checks to avoid invalid access.
- Hot-unplug and `no_hw_access` behavior must be preserved. `amdgpu_device_skip_hw_access()` relies on reset sem lockdep assertions and `adev->no_hw_access`; `amdgpu_device_halt()` unplugs DRM, disables IRQ/fences, unmaps MMIO, and disables PCI to keep the host stable.
- Error unwinds are partial by design. Many init failures return after state has been initialized and rely on upper teardown paths; late error handling must avoid double-freeing BOs, sysfs groups, reset domains, PCI saved state, and firmware.
- Module parameters mutate global defaults in validation paths (`amdgpu_sched_jobs`, `amdgpu_vm_size`, etc.), so one device’s validation can affect later devices.

## Test and Validation Signals

- Driver probe smoke tests should verify `amdgpu_device_init()` succeeds across representative ASIC families: legacy SI/CIK/VI, IP discovery devices, APUs, dGPUs, SR-IOV VFs, XGMI multi-node GPUs, and headless/virtual-display configurations.
- Suspend/resume validation should cover S3, S4, S0ix, runtime PM, PX/BOCO/BACO/BAMACO, SmartShift updates, and display hotplug events after resume.
- Reset validation should exercise soft recovery, full reset, mode1, mode2/link reset, BACO enter/exit, XGMI hive reset, RAS-triggered reset, scheduler timeout recovery with a guilty job, already-signaled guilty job skip, VRAM-lost accounting, and failed reset propagation.
- PCI AER/DPC tests should confirm `error_detected`, `slot_reset`, and `resume` paths restore PCI/switch state, scheduler state, audio state, and reset-domain locks for both hive and non-hive devices.
- SR-IOV tests should cover exclusive access, host FLR notification, mailbox data exchange, VF MMIO protection, XGMI node migration, GIM VRAM-lost feature, and retryable reset errors.
- Sysfs tests should check presence/absence and output of `pcie_replay_count`, `reg_state`, `board_info`, UMA carveout files, PM/ucode/FRU/XCP sysfs, and reset mask formatting according to ASIC/APU/support flags.
- Memory/path tests should verify writeback slot allocation/free under concurrency, scratch BO lifetime, VRAM aperture fallback to MM index/data access, HDP flush/invalidate ordering, BAR resize fallback, and P2P accessibility decisions under IOMMU/remap/large-BAR configurations.
- Build coverage should include configs with and without SI/CIK, AMD DC, HSA AMD P2P, perf events, x86-specific CPU quirks, debugfs, hotplug PCIe, and 32-bit/64-bit differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_df.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_df.h

## Purpose

`amdgpu_df.h` declares the AMDGPU Data Fabric abstraction. It is a compact header that stores Data Fabric hash capability state and a per-ASIC function table used by the rest of the driver to initialize DF support, query channel topology, control DF broadcast/clock-gating/ECC behavior, access DF performance counters, access FICA registers, and query RAS poison mode.

The header intentionally contains no implementation logic. It defines the contract that DF implementation files fill in and that callers access through `adev->df.funcs`.

## Important Types and APIs

- `struct amdgpu_df_hash_status` records whether Data Fabric address hashing is enabled/supported for `64k`, `2m`, and `1g` granularities. This state is stored under `struct amdgpu_df` and can be consumed by memory-management and topology paths that need to understand address distribution.
- `struct amdgpu_df_funcs` is the function-table contract for a DF implementation:
  - `sw_init()` / `sw_fini()` initialize and tear down software DF state.
  - `hw_init()` performs hardware initialization.
  - `enable_broadcast_mode()` toggles broadcast access across DF instances.
  - `get_fb_channel_number()` and `get_hbm_channel_number()` report framebuffer/HBM channel topology.
  - `update_medium_grain_clock_gating()` and `get_clockgating_state()` control/report DF clock-gating state.
  - `enable_ecc_force_par_wr_rmw()` toggles ECC forced partial-write read-modify-write handling.
  - `pmc_start()`, `pmc_stop()`, and `pmc_get_count()` expose DF performance monitor counter operations by config and counter index.
  - `get_fica()` and `set_fica()` abstract FICA register access using FICAA/FICADL/FICADH values.
  - `query_ras_poison_mode()` reports whether DF/RAS poison mode is active/supported for the device.
- `struct amdgpu_df` embeds the current `hash_status` and a `const struct amdgpu_df_funcs *funcs` pointer selected by ASIC/IP discovery code.

## Control Flow and State

DF control flow is indirect. During device/IP setup, ASIC-specific code assigns `adev->df.funcs` and may call `sw_init()`/`hw_init()` through the AMDGPU IP block lifecycle. Later call sites guard on the presence of `adev->df.funcs` and individual callbacks, then invoke the relevant function for clock gating, RAS, performance counters, topology queries, or register access.

Persistent state in this header is limited to `amdgpu_df_hash_status` and the immutable function-table pointer. Counter state, register side effects, and hardware programming are implementation-specific and not stored in this header. Because the function table is `const`, runtime mutation should occur in implementation-private state or `adev->df.hash_status`, not by editing callback slots.

## Dependencies and Integration Points

The declarations depend on `struct amdgpu_device` being visible to users of the header, so it is designed for inclusion from AMDGPU internal code rather than standalone compilation. The callbacks integrate with device initialization, power management, clock gating, RAS poison handling, memory-channel topology, and performance monitoring. The FICA callbacks expose low-level DF register access through a uniform interface so ASIC generation differences can stay in the implementation files.

## Risks and Edge Cases

- Callers must treat every callback as optional unless the selected ASIC generation guarantees it. A missing `funcs` pointer or missing callback should not be dereferenced.
- PMC operations take a raw `config`, `counter_idx`, and add/remove flags; mismatched start/stop/remove semantics can leak counters or return misleading counts.
- Broadcast-mode and FICA operations can affect multiple DF instances or low-level fabric registers, so callers need serialization and ASIC-specific preconditions from the implementation.
- Hash-status booleans are compact but easy to misinterpret: they describe address hash modes, not memory page-size support in general.
- RAS poison-mode reporting is function-table based, so devices without a callback need a conservative fallback in callers.

## Test and Validation Signals

- Build tests should cover all DF implementation files that instantiate `struct amdgpu_df_funcs`, ensuring callback signatures match this header.
- Device init tests should verify `adev->df.funcs` is assigned for supported ASICs and absent or safely ignored for unsupported ones.
- Clock-gating tests should confirm `update_medium_grain_clock_gating()` and `get_clockgating_state()` agree with PM flags after gate/ungate cycles.
- PMC tests should cover start, read, stop, add/remove variants, invalid counter indices, and multiple counter configurations.
- RAS tests should verify poison-mode query behavior with and without callback support.
- FICA tests should validate read/write paths on each supported DF generation and confirm broadcast mode is disabled or enabled only when expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_df.h -->
