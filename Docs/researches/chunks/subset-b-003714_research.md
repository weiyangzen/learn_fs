# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik.c lines 1-9019

## Scope And Purpose

This chunk is the main body of the Radeon CIK ASIC support file. It covers initialization and runtime control for Sea Islands-class Radeon GPUs and APUs including Bonaire, Hawaii, Kaveri, Kabini, and Mullins. Although the path is inside a `ceph-client` source mirror, the code is DRM Radeon GPU driver logic, not Ceph filesystem code.

The range starts with firmware declarations, chip-specific golden register tables, RLC save/restore tables, register access helpers, and temperature helpers. It then implements firmware loading, memory-controller setup, global tiling/GPU configuration, command processor setup for graphics and compute rings, fence and semaphore packet emission, CP DMA copies, indirect buffer execution, GPU reset, PCIe GART and VM setup, RLC clock/power gating, interrupt setup and processing, media-engine startup for UVD/VCE, top-level ASIC init/resume/suspend/fini paths, display formatter programming, and the first display watermark helpers. The chunk ends at line 9019, which is only the opening comment for `dce8_dmif_request_bandwidth`; that function body is outside this work item.

## Important APIs, Types, And Functions

Externally visible or callback-style functions in this chunk include:

- `cik_get_allowed_info_register()` exposes a restricted set of status registers to the info ioctl.
- `cik_didt_rreg()`, `cik_didt_wreg()`, `cik_pciep_rreg()`, and `cik_pciep_wreg()` provide locked indirect register access for DIDT and PCIe-port registers.
- `ci_get_temp()` and `kv_get_temp()` decode SMC thermal registers into millidegrees Celsius for CI/Hawaii-style dGPUs and Kaveri-family APUs.
- `ci_mc_load_microcode()` loads memory-controller firmware and IO debug register tables into MC sequencing hardware on non-IGP parts.
- `cik_ring_test()`, `cik_ib_test()`, `cik_ring_ib_execute()`, `cik_fence_gfx_ring_emit()`, `cik_fence_compute_ring_emit()`, `cik_semaphore_ring_emit()`, and `cik_copy_cpdma()` are ring, fence, IB, semaphore, and CP-DMA support hooks used by Radeon scheduling, TTM moves, and synchronization.
- `cik_gfx_get_rptr()`, `cik_gfx_get_wptr()`, `cik_gfx_set_wptr()`, `cik_compute_get_rptr()`, `cik_compute_get_wptr()`, and `cik_compute_set_wptr()` bridge Radeon ring state to hardware registers, writeback memory, and doorbells.
- `cik_gpu_check_soft_reset()`, `cik_asic_reset()`, and `cik_gfx_is_lockup()` implement hang detection and reset selection.
- `cik_pcie_gart_tlb_flush()`, `cik_vm_init()`, `cik_vm_fini()`, `cik_vm_flush()`, and `cik_ib_parse()` provide VM/GART callbacks.
- `cik_update_cg()`, `cik_init_cp_pg_table()`, `cik_enter_rlc_safe_mode()`, `cik_exit_rlc_safe_mode()`, `cik_get_csb_size()`, and `cik_get_csb_buffer()` expose clock/power gating and RLC clear-state support.
- `cik_irq_set()` and `cik_irq_process()` are the main interrupt enable and interrupt-handler hooks.
- `cik_resume()`, `cik_suspend()`, `cik_init()`, and `cik_fini()` are the top-level ASIC lifecycle entry points.
- `dce8_program_fmt()` configures display output formatting, truncation, and dithering for DCE8 display encoders.

Important internal types and state layouts include `struct hqd_registers`, which mirrors compute HQD queue state, `struct bonaire_mqd`, which describes the memory queue descriptor allocated for compute queues, `struct kv_reset_save_regs`, which preserves selected APU reset registers, and `struct dce8_wm_params`, which carries display watermark calculation inputs. The file also relies heavily on `struct radeon_device`, `struct radeon_ring`, `struct radeon_ib`, `struct radeon_fence`, `struct radeon_sync`, and Radeon buffer-object helpers.

Major static data includes `MODULE_FIRMWARE()` declarations for old uppercase and newer lowercase firmware names; RLC save/restore register lists for Spectre/Kaveri and Kalindi/Kabini/Mullins; golden register and MGC/CGC initialization sequences for Bonaire, Hawaii, Kaveri, Kabini, Mullins, and Godavari-derived paths; and MC IO debug register tables for Bonaire and Hawaii.

## Control Flow And Runtime Behavior

Initialization starts in `cik_init()`. It reads and initializes ATOM BIOS, posts the card if needed, programs golden registers, initializes scratch/surface/clock/fence state, probes MC VRAM information, initializes BO management, loads required firmware through `cik_init_microcode()`, initializes power management, allocates graphics/compute/DMA/media/IH rings, allocates compute doorbells, initializes GART backing storage, and calls `cik_startup()`.

`cik_startup()` performs the hardware bring-up sequence. It enables PCIe Gen3 and ASPM, creates the VRAM scratch page, programs the memory controller apertures, loads MC firmware when needed, enables the PCIe GART and VM contexts, configures global GPU and tiling state, allocates RLC buffers and writeback memory, allocates MEC HPD/EOP buffers, starts fence drivers for GFX/compute/SDMA/media rings, initializes UVD/VCE firmware paths, installs and initializes interrupts, initializes all rings, resumes the graphics and compute CP, resumes SDMA, initializes IB and VM managers, and starts Radeon audio.

Graphics initialization is centered on `cik_gpu_init()`. It selects chip-family topology parameters, programs HDP and address configuration registers, derives memory row and tile configuration from MC registers, writes tile and macrotile mode tables through `cik_tiling_mode_table_init()`, sets up render backends with `cik_setup_rb()`, counts active CUs, and writes a broad set of graphics defaults for CP, SPI, DB, CB, PA/SC, VGT, and HDP state.

The command processor is split into graphics and compute paths. `cik_cp_gfx_load_microcode()` loads PFP, CE, and ME firmware; `cik_cp_gfx_resume()` programs the graphics ring buffer, writeback read pointer, scratch base, and ring base; `cik_cp_gfx_start()` emits clear-state setup packets and initializes CE partition state. Compute uses MEC firmware in `cik_cp_compute_load_microcode()`, allocates HPD/EOP memory in `cik_mec_init()`, creates MQD BOs, programs per-queue HQD registers via `cik_srbm_select()`, enables doorbells, and validates each exposed compute ring with `radeon_ring_test()`.

VM setup uses VMID 0 for kernel physical GPU addresses and VMIDs 1-15 for Radeon VM clients. `cik_pcie_gart_enable()` pins the GART table, configures L1/L2 TLBs, programs context 0 for the system GART, restores context 1-15 page table bases, enables protection-fault interrupts, and initializes `SH_MEM_*` registers per VMID. `cik_vm_flush()` emits CP packets to update a VM page-directory base, reprogram `SH_MEM_*`, flush HDP, request VM invalidation, wait for completion, and synchronize PFP to ME for graphics rings.

Interrupt setup allocates the IH ring, disables all sources, resumes the RLC, programs IH base/writeback/control registers, and enables the interrupt ring. `cik_irq_set()` maps Radeon software state to CP, compute, SDMA, vblank, page-flip, and HPD interrupt enable registers. `cik_irq_process()` reads IH entries, acknowledges display status up front, walks 16-byte vectors, dispatches vblank/page-flip/hotplug/DP/VM-fault/UVD/VCE/fence/SDMA/thermal events, schedules deferred work, marks reset-needed state on illegal command stream events, advances the IH read pointer, and restarts if the write pointer changed while processing.

Suspend and fini are reverse-order teardown paths. `cik_suspend()` stops power management/audio/VM/CP/SDMA/media, disables power and clock gating, suspends interrupts and RLC, disables writeback, and disables GART. `cik_fini()` fully releases rings, RLC/MEC/writeback/IB/VM/IRQ/GART/scratch/GEM/fence/BO/ATOM BIOS resources and frees compute doorbells.

## State And Persistence Behavior

Most persistent state is hardware register state programmed through `RREG32`/`WREG32` families, Radeon ring BOs, writeback memory, firmware blobs, and GPU buffer objects pinned into VRAM or GTT.

Firmware state is loaded into `rdev->pfp_fw`, `me_fw`, `ce_fw`, `mec_fw`, optional `mec2_fw`, `rlc_fw`, `sdma_fw`, `mc_fw`, and `smc_fw`. `rdev->new_fw` records whether all required firmware files use the newer header format; mixed old/new firmware is rejected because later loaders use different endian, offset, and jump-table handling.

Memory state includes MC VRAM aperture placement, GART page-table GPU address, VM context page-table bases, dummy page fault address, `rdev->vm_manager.saved_table_addr[]` saved across GART disable/enable, writeback slots for ring read/write pointers and IH write pointer, scratch registers, VRAM scratch BO, RLC save/restore BOs, RLC clear-state buffer, RLC CP jump table, MEC HPD/EOP BO, and per-compute-ring MQD BOs.

Ring state persists in `rdev->ring[]` and hardware. Graphics uses `CP_RB0_*` registers and optional writeback read pointers. Compute queues use selected HQD registers, MQD memory, doorbells, and writeback poll/report addresses. SDMA and media rings are initialized in neighboring helpers but are integrated here through fence startup, interrupt routing, suspend, and fini.

Power and clock state is controlled through `rdev->cg_flags` and `rdev->pg_flags`. Clock gating spans GFX MGCG/CGCG, MC, SDMA, BIF, UVD, HDP, and VCE blocks. Power gating configures RLC/SMU handshakes, CP/GDS/GFX power gating, active CU masks, clear-state descriptors, save/restore register lists, and CP firmware jump tables. These settings are deliberately disabled before reset/suspend and restored during RLC resume/startup.

Interrupt state persists in the IH ring, `rdev->ih.rptr`, `rdev->ih.enabled`, writeback state, `rdev->irq.stat_regs.cik`, atomic interrupt enables, HPD/vblank/page-flip flags, and scheduled work items for hotplug, DP, thermal, and reset recovery.

## Dependencies And Integration Points

This file is tightly coupled to Radeon DRM core infrastructure:

- Firmware and microcode infrastructure: Linux `request_firmware()`, `release_firmware()`, `radeon_ucode_validate()`, and firmware header types from `radeon_ucode.h`.
- MMIO/register definitions: `cik.h`, `cikd.h`, `si.h`, `evergreen.h`, and the Radeon `RREG32`/`WREG32`/SMC/PCIE/UVD helper families.
- Memory management: Radeon BO, TTM, GART, VM manager, dummy page, VRAM scratch, and DMA reservation synchronization.
- Command submission: Radeon ring, IB, fence, semaphore, sync, packet macros, CP DMA packets, and writeback memory.
- Display integration: DRM vblank handling, Radeon CRTC page-flip handling, HPD/DP work, DCE8 formatter setup, line-buffer allocation, and display watermark helpers.
- Power management: Radeon PM/DPM, SMC access, clock/power gating flags, UVD/VCE clock gating, RLC/SMU handshakes, and thermal work scheduling.
- Reset and suspend/resume: PCI config reset, BIOS scratch engine-hung marker, Evergreen MC stop/resume helpers, VGA render disable, and ATOM BIOS posting.
- Media engines: UVD and VCE init/resume/fini helpers from `uvd_*` and `vce_*` code paths.
- Interrupt handling: DRM IRQ install/fini, R600 IH ring allocation/fini, Radeon fence processing, and workqueue scheduling.

The code is chip-family-sensitive throughout. Bonaire/Hawaii dGPUs load MC and SMC firmware and use family-specific golden registers and MC IO tables. Kaveri/Kabini/Mullins APUs skip MC/SMC firmware, use IGP-specific reset save/restore and VM base offsets, and Kaveri exposes a second MEC firmware path.

## Risks And Edge Cases

- Firmware handling rejects mixed old and new formats, but each loader assumes `rdev->new_fw` is globally consistent. Any future firmware naming or header-size drift can break microcode loading or jump-table extraction.
- Several paths use raw register magic values and chip-specific tables. Incorrect golden registers, RLC lists, MC IO debug tables, or tiling modes can compile cleanly but cause hangs, corruption, or display artifacts only on specific ASIC families.
- `cik_tiling_mode_table_init()` derives layout from tile pipes, row size, bank count, and RB topology. Bad MC-derived row size or family topology can make GPU addresses, SDMA tiling, UVD tiling, and display tiling disagree.
- `cik_setup_rb()` mutates `enabled_rbs` while programming per-SE raster config. The bit mapping is sensitive to Hawaii versus non-Hawaii bitmap widths and disabled RB fuses.
- Indirect register selection through SRBM and GRBM is global hardware state. Callers use `srbm_mutex` where needed; missing locking around selected-instance registers would risk programming the wrong queue, VMID, SE, or SH.
- Compute queue setup uses only two kernel queues even though MEC hardware exposes more. Doorbell indices, writeback offsets, MQD BO pinning, and HQD selection must remain consistent for CP1/CP2.
- `cik_compute_set_wptr()` writes the write pointer to writeback memory and then rings a doorbell. Incorrect doorbell allocation or stale writeback offsets can strand compute work.
- Reset paths deliberately disable CG/PG, halt CP/MEC/SDMA/RLC, stop MC, and optionally use PCI config reset. Ordering mistakes here can deadlock reset, lose VRAM contents, or leave APU power-gating registers in a bad state.
- VM fault handling resets fault status and logs decoded clients, but it does not repair the faulting submission directly. Repeated VM faults can lead to reset scheduling or user-visible GPU hangs.
- Interrupt processing shares display status registers with IH vectors. The handler logs "event without asserted irq bit" cases and clears shadowed status as it processes vectors; missed acks or stale status can cause interrupt storms or lost vblank/page-flip events.
- The CP1/CP2 interrupt enable switch uses pipe 3 cases that set the pipe-2 enable fields, which looks suspicious and should be treated as a potential copy/paste bug unless confirmed by hardware documentation.
- `cik_asic_reset()` returns 0 even if a post-reset `reset_mask` remains set. Higher layers must rely on subsequent lockup detection or logs rather than this return value alone.
- The chunk boundary cuts the display watermark code before `dce8_dmif_request_bandwidth()` and later watermark programming functions. Final per-file reconciliation must include following chunks before making complete claims about DCE8 bandwidth calculations.

## Test Signals

Useful build and runtime validation signals include:

- Kernel build coverage for Radeon CIK with firmware-header support, UVD/VCE, DPM, PCIe GART, VM, IRQ, and suspend/resume enabled.
- Boot/load tests on each supported family in this file: Bonaire, Hawaii, Kaveri, Kabini, and Mullins. Watch for firmware load errors, "mixing new and old firmware", MC firmware failures, ring-test failures, IB-test failures, and IH init failures.
- Ring validation: `cik_ring_test()` and `cik_ib_test()` should succeed for graphics and the exposed compute queues; SDMA, UVD, and VCE fence processing should advance sequence numbers under workload.
- VM/GART validation: GPUVM submissions should update page table bases through `cik_vm_flush()`, invalidate TLBs, and avoid `VM_CONTEXT1_PROTECTION_FAULT_*` logs during normal operation.
- Memory-move validation: TTM BO moves through `cik_copy_cpdma()` should synchronize reservations, split copies larger than `0x1fffff` bytes, emit a fence, and preserve data.
- Interrupt validation: vblank, page flip, HPD, DP RX, CP EOP, SDMA trap, UVD, VCE, thermal, and VM fault sources should be acknowledged and routed to the expected Radeon/DRM handlers without IH overflow.
- Reset validation: forced soft reset and hard PCI config reset should halt engines, preserve/restore required APU registers, resume MC access, clear BIOS scratch hung state when successful, and allow rings to reinitialize.
- Suspend/resume validation: after resume, golden registers, MC/GART/VM, RLC, CG/PG, CP, SDMA, UVD/VCE, interrupts, audio, and fences should recover without leaked BO pins or missing doorbells.
- Display validation: DCE8 formatter programming should honor connector bpc and dither settings for non-LVDS/eDP digital outputs, and line-buffer adjustment should complete DMIF allocation for active CRTCs.

## Cross-Chunk Notes

This is the first and largest chunk for `cik.c` and covers lines 1-9019 of 9807. It ends immediately before the body of `dce8_dmif_request_bandwidth()` and before later display watermark programming, UVD/VCE clock programming, PCIe Gen3 enablement, and ASPM programming. The merge/reconciliation lane should combine this document with the remaining chunk(s) for the same source file before producing a complete per-file report.
