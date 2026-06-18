# Research: subset-b-001343

This grouped report covers AMDGPU GMC, HDP, and Iceland IH source files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu`. Each file section is wrapped for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.h

## Purpose
`gmc_v6_0.h` is the public declaration header for the GMC v6 IP block. It contains only the include guard and the external `gmc_v6_0_ip_block` declaration used by AMDGPU device-discovery and ASIC setup code to bind Southern Islands-era memory-controller support into the common IP block lifecycle.

## Important APIs, Types, And Functions
The only exported symbol is `extern const struct amdgpu_ip_block_version gmc_v6_0_ip_block;`. The type comes from the wider AMDGPU IP framework and carries the block type, version tuple, and callback table for early/software/hardware init, suspend/resume, reset, and power management.

## Control Flow And Integration
This header has no executable control flow. Its integration point is compile-time inclusion by ASIC tables or driver initialization files that need to reference the v6 GMC IP block object without seeing the implementation. The actual behavior is provided by a matching `gmc_v6_0.c` elsewhere in the tree.

## State, Persistence, And Dependencies
The file declares no state and persists nothing. It depends on consumers including an AMDGPU core header that defines `struct amdgpu_ip_block_version` before using the declaration.

## Risks And Test Signals
The risk surface is symbol-contract drift: if the implementation renames or drops `gmc_v6_0_ip_block`, builds fail at link time. Useful test signals are allmodconfig or AMDGPU build coverage for SI support and successful probe paths on v6 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c

## Purpose
`gmc_v7_0.c` implements the AMDGPU Graphics Memory Controller IP block for CIK/GMC 7 hardware, exporting `gmc_v7_0_ip_block` and `gmc_v7_4_ip_block`. It owns memory-controller firmware loading, VRAM/GART placement, VM page-table setup, TLB invalidation callbacks, VM fault IRQ handling, suspend/resume state transitions, soft reset, and generation-specific clock-gating controls.

## Important APIs, Types, And Functions
The IP lifecycle is collected in `gmc_v7_0_ip_funcs`: `early_init`, `late_init`, `sw_init`, `sw_fini`, `hw_init`, `hw_fini`, `suspend`, `resume`, `is_idle`, `wait_for_idle`, `soft_reset`, and clock/power gating hooks. `gmc_v7_0_gmc_funcs` supplies VM/GMC services to the core VM layer: `flush_gpu_tlb`, `flush_gpu_tlb_pasid`, `emit_flush_gpu_tlb`, `emit_pasid_mapping`, `set_prt`, `get_vm_pde`, `get_vm_pte`, and `get_vbios_fb_size`. `gmc_v7_0_irq_funcs` handles VM fault interrupt enable/disable and decoding.

Firmware helpers include `gmc_v7_0_init_microcode()` and `gmc_v7_0_mc_load_microcode()`, selecting Bonaire, Hawaii, and Topaz MC firmware while returning early for CIK APUs. Memory setup flows through `gmc_v7_0_mc_init()`, `gmc_v7_0_mc_program()`, `gmc_v7_0_gart_init()`, `gmc_v7_0_gart_enable()`, and `gmc_v7_0_gart_disable()`.

## Control Flow
Probe starts with `early_init`, which installs GMC and IRQ function tables and sets shared/private apertures plus no-retry flags. `sw_init` records the single GFX VM hub, derives VRAM type and width, registers legacy VM fault IRQ IDs, adjusts VM size to a 40-bit CIK layout, sets a 40-bit DMA mask, loads MC firmware into memory, initializes MC placement, BO management, GART table allocation, VM manager state, KFD VMID split, and `kfd_vm_fault_info` storage.

`hw_init` programs golden registers, writes MC/HDP/system aperture registers, loads MC firmware to hardware on discrete parts, enables GART and VM contexts, then optionally performs VRAM checking in emulation. `late_init` enables VM fault IRQs unless faults are configured to stop always. Suspend and fini paths reverse this by dropping IRQs, disabling GART, freeing the VM manager, GART table, BO manager, firmware, and KFD fault storage.

## State And Persistence
Persistent runtime state is stored in `adev->gmc`, `adev->gart`, `adev->vm_manager`, and `adev->gmc.vm_fault_info`. Hardware-visible state includes MC apertures, VM context registers, TLB/L2 cache controls, PRT aperture registers, ATC PASID mappings, and clock-gating bits. Firmware is requested into `adev->gmc.fw` during software init and released during software fini; the hardware copy is only loaded during hardware init for supported dGPUs.

## Dependencies And Integration Points
The file depends on CIK register headers, AtomBIOS helpers, AMDGPU BO/GART/VM/KFD subsystems, firmware loading, DRM DMA mask helpers, PCI BAR sizing, and legacy interrupt IDs. It integrates with KFD by reserving VMIDs 8-15 and caching the first KFD VM fault in `kfd_vm_fault_info`.

## Risks And Test Signals
High-risk areas include firmware selection/loading, register sequencing around MC blackout/reset, GART table placement in VRAM, VM fault interrupt policy changes under `amdgpu_vm_fault_stop`, and KFD fault-info synchronization. Tests should include CIK dGPU/APU boot, suspend/resume, GPU reset, GART allocation/free, PRT mappings, VM fault injection, KFD page-fault reporting, and clock-gating state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.h

## Purpose
`gmc_v7_0.h` declares the public GMC v7 IP block objects for AMDGPU CIK-era memory-controller integration.

## Important APIs, Types, And Functions
It exports `gmc_v7_0_ip_block` and `gmc_v7_4_ip_block`, both typed as `const struct amdgpu_ip_block_version`. These declarations allow ASIC setup code to bind either GMC minor version to the same implementation callback table in `gmc_v7_0.c`.

## Control Flow, State, And Dependencies
The header has no control flow or local state. It relies on a prior declaration of `struct amdgpu_ip_block_version` from AMDGPU core headers and is consumed by device/IP discovery code.

## Integration, Risks, And Test Signals
The file is an ABI-like internal compile contract. Link/build failures are the primary signal for declaration drift. Runtime validation belongs to the implementation: CIK probe should select the proper v7.0 or v7.4 IP block and execute the common GMC lifecycle callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.c

## Purpose
`gmc_v8_0.c` implements the VI/GMC 8 memory-controller block, exporting `gmc_v8_0_ip_block`, `gmc_v8_1_ip_block`, and `gmc_v8_5_ip_block`. It is structurally close to GMC v7 but adds VI PTE semantics, Tonga and Polaris firmware paths, SR-IOV awareness, expanded golden-register handling, and split soft-reset callbacks.

## Important APIs, Types, And Functions
`gmc_v8_0_ip_funcs` registers lifecycle callbacks including `check_soft_reset`, `pre_soft_reset`, `soft_reset`, and `post_soft_reset`. `gmc_v8_0_gmc_funcs` exposes TLB flushing, ring-emitted TLB flushing, PASID mapping, PRT control, VM PDE/PTE flag construction, and VBIOS framebuffer sizing. `gmc_v8_0_irq_funcs` manages VM fault interrupt masks and dispatches decoded faults.

Key implementation functions are `gmc_v8_0_init_microcode()`, `gmc_v8_0_tonga_mc_load_microcode()`, `gmc_v8_0_polaris_mc_load_microcode()`, `gmc_v8_0_mc_init()`, `gmc_v8_0_mc_program()`, `gmc_v8_0_gart_enable()`, `gmc_v8_0_process_interrupt()`, and the Fiji clock-gating helpers.

## Control Flow
`early_init` installs function tables and sets aperture ranges. `sw_init` records the GFX VM hub, determines VRAM type from ATOM or MC registers, registers legacy VM fault sources, configures a 40-bit DMA/MC address space, loads required MC firmware, initializes MC placement, BO/GART/VM manager state, KFD VMIDs, and KFD VM fault storage. `hw_init` programs golden registers, writes MC/HDP apertures, conditionally uploads Tonga or Polaris MC firmware, enables GART and VM contexts, and optionally runs VRAM checking.

Reset flow is staged. `check_soft_reset` records busy MC/VMC reset bits in `adev->gmc.srbm_soft_reset`; `pre_soft_reset` blackouts MC and waits for idle; `soft_reset` toggles SRBM reset bits; `post_soft_reset` resumes MC access. VM faults are delegated to the soft IH ring when available, decoded from protection-fault registers unless running as SR-IOV VF, logged with task-info lookup, cached for VM recovery, and copied to KFD fault info for KFD VMIDs.

## State And Persistence
State lives in `adev->gmc`, `adev->gart`, `adev->vm_manager`, firmware pointer `adev->gmc.fw`, and `adev->gmc.srbm_soft_reset`. Hardware state includes MC aperture registers, VM context controls, L1/L2 TLB controls, PRT aperture registers, PASID LUTs, HDP registers, and clock-gating bits. The GART table is allocated in VRAM and freed during `sw_fini`.

## Dependencies And Integration Points
The file depends on VI register headers, firmware loading, AtomBIOS, DRM cache/DMA helpers, BO/GART/VM core, KFD fault structures, PCI BAR sizing, and SR-IOV helpers. It integrates with the IRQ layer through legacy VM fault IDs and with the VM layer through `adev->gmc.gmc_funcs`.

## Risks And Test Signals
Important risks include incorrect MC firmware selection for Polaris variants, SR-IOV register access that should be skipped, stale `srbm_soft_reset` state across reset phases, VM fault IRQ default policy, and clock-gating regressions on Fiji. Test signals include VI dGPU/APU boot, Tonga/Polaris firmware load, SR-IOV VF probe, suspend/resume, GPU reset, KFD VM fault handling, PRT behavior, GART table validation, and clock-gating state reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.h

## Purpose
`gmc_v8_0.h` declares the GMC v8 IP block versions exposed by the VI memory-controller implementation.

## Important APIs, Types, And Functions
The header exports `gmc_v8_0_ip_block`, `gmc_v8_1_ip_block`, and `gmc_v8_5_ip_block`, all `const struct amdgpu_ip_block_version`. The declarations let ASIC code select the correct minor version while sharing the implementation in `gmc_v8_0.c`.

## Control Flow, State, Dependencies, And Risks
There is no executable flow or state. The only dependency is the AMDGPU IP block type definition from broader headers. Risk is limited to declaration/definition drift, caught by build and link coverage. Runtime test signals are successful VI-family probe and IP block callback dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c

## Purpose
`gmc_v9_0.c` implements the SOC15/GFX9 generation memory-controller block. It exports `gmc_v9_0_ip_funcs` and `gmc_v9_0_ip_block` and coordinates GFXHUB, MMHUB, ATHUB, UMC, HDP RAS, MCA RAS, XGMI, memory partitioning, GART, VM page-table flag generation, VM fault handling, ECC interrupt setup, clock gating, and suspend/resume register restore.

## Important APIs, Types, And Functions
The main AMDGPU IP callbacks are in `gmc_v9_0_ip_funcs`. `gmc_v9_0_gmc_funcs` supplies the core VM API: hub-aware `flush_gpu_tlb`, PASID TLB flush, ring-emitted invalidate, PASID mapping, PDE/PTE flag construction, per-page PTE overrides, VBIOS framebuffer sizing, memory partition query/request, and reset-on-init detection. IRQ function tables include `gmc_v9_0_irq_funcs` for VM faults and `gmc_v9_0_ecc_funcs` for UMC ECC IRQs.

Support routines select hub/RAS implementations: `gmc_v9_0_set_umc_funcs()`, `gmc_v9_0_set_mmhub_funcs()`, `gmc_v9_0_set_mmhub_ras_funcs()`, `gmc_v9_0_set_gfxhub_funcs()`, `gmc_v9_0_set_hdp_ras_funcs()`, `gmc_v9_0_set_mca_ras_funcs()`, and `gmc_v9_0_set_xgmi_ras_funcs()`. Hardware setup uses `gmc_v9_0_mc_init()`, `gmc_v9_0_gart_init()`, `gmc_v9_0_gart_enable()`, and hub-specific `gart_enable` callbacks.

## Control Flow
`early_init` detects implicit XGMI support, CPU-connected XGMI, and APP APU mode, then installs GMC/IRQ/UMC/MMHUB/GFXHUB/RAS function tables and initializes aperture constants. `sw_init` initializes GFXHUB and MMHUB register maps, sets the invalidate lock, derives VRAM width/type/vendor, configures VM hub masks based on GC IP versions and multi-AID topology, adjusts VM size to 48-bit layouts, registers VMC/UTCL2/DF IRQ IDs, sets DMA mask width, initializes MC placement, memory ranges for multi-AID devices, BO/GART, NPS details, VMID split, VM manager, saved DCE register state, RAS software state, and multi-AID sysfs.

`late_init` allocates VM invalidate engines, applies an ECC partial-write workaround where needed, resets RAS counters when persistent harvesting is unavailable, runs RAS late init, and enables VM fault IRQs. `hw_init` sets KIQ-based PASID flush state, handles the Vega20 XGMI extra-flush workaround, programs golden registers, disables VGA access, updates MMHUB power gating, initializes HDP registers, flushes HDP, sets default fault behavior on each hub, flushes VMID0 TLBs for every hub, initializes UMC registers, and enables GART through GFXHUB/MMHUB callbacks.

VM fault processing reconstructs fault addresses from IV data, identifies MMHUB/GFXHUB and multi-AID/XCC origin, handles retry faults through `amdgpu_gmc_handle_retry_fault`, gives KFD a fast path, rate-limits diagnostics, reads L2 protection status when legal, clears fault status, updates the VM fault cache, and prints client names using per-IP client maps. TLB invalidation uses KIQ register-write-wait when ready; otherwise it serializes MMIO invalidates with `adev->gmc.invalidate_lock` and optional MMHUB invalidation semaphores.

## State And Persistence
The file mutates broad device state: `adev->gmc` apertures, xGMI fields, APP APU flags, NPS/reset flags, mem partitions, flush flags, saved SDPIF register, `adev->vmhub[]`, `adev->vmhubs_mask`, `adev->vm_manager`, `adev->gart`, `adev->umc`, `adev->mmhub`, `adev->gfxhub`, `adev->hdp.ras`, `adev->mca`, IRQ sources, and BO/GART resources. Persistent hardware state includes hub page-table registers, invalidate engines, fault-control bits, HDP registers, MMHUB power-gating state, and UMC/RAS registers.

## Dependencies And Integration Points
Dependencies include SOC15 register access, GFXHUB/MMHUB/ATHUB helpers, UMC and RAS modules, HDP v4 RAS, MCA v3, XGMI, AtomFirmware VRAM info, BO/GART/VM core, KFD fault fast path, NBIO/DF/SMUIO callbacks, SR-IOV helpers, DRM DMA/PCI helpers, and memory-partition sysfs. It is a central integration layer for GFX9 memory management and errors.

## Risks And Test Signals
High-risk areas are hub selection across MMHUB/GFXHUB/XCC/AID instances, KIQ versus direct-MMIO TLB invalidation, invalidation semaphore timeout handling, retry-fault/KFD handoff, RAS IRQ enablement conditions, APP APU and XGMI address placement, NUMA-aware PTE overrides, PDB0 allocation, NPS reset/resume, and SR-IOV register avoidance. Test signals should cover GFX9 dGPU/APU/SR-IOV boot, XGMI hives, multi-AID memory partitions, VM fault injection, retry faults, KFD faults, suspend/resume including S0ix, GART/PDB0 placement, RAS ECC interrupts, HDP flush after init, and clock-gating state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.h

## Purpose
`gmc_v9_0.h` exposes the public interface for the GFX9/SOC15 GMC implementation.

## Important APIs, Types, And Functions
It declares `extern const struct amd_ip_funcs gmc_v9_0_ip_funcs`, `extern const struct amdgpu_ip_block_version gmc_v9_0_ip_block`, and `void gmc_v9_0_restore_registers(struct amdgpu_device *adev)`. Unlike the v7/v8 headers, it exposes the raw IP function table and a restore helper used outside the main IP block registration path.

## Control Flow And Integration
The header has no local control flow. External users can bind the GMC IP block or call `gmc_v9_0_restore_registers()` to restore saved SOC15 display/HDP-related register state after suspend or reset sequencing.

## State, Dependencies, Risks, And Test Signals
The restore declaration depends on `struct amdgpu_device`; consumers must include suitable AMDGPU core declarations. Risk is declaration drift against `gmc_v9_0.c`. Build coverage plus suspend/resume tests that call the restore helper provide the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c

## Purpose
`hdp_v4_0.c` implements Host Data Path helpers for HDP 4.x blocks. HDP mediates CPU/host visibility of GPU memory, so this file supplies cache flush/invalidate behavior, clock-gating state transitions, HDP register initialization, and HDP RAS error reporting.

## Important APIs, Types, And Functions
The exported function table is `hdp_v4_0_funcs`, containing generic HDP flush, `hdp_v4_0_invalidate_hdp`, clock-gating update/read callbacks, and `hdp_v4_0_init_registers`. It also exports `hdp_v4_0_ras`, backed by `hdp_v4_0_ras_hw_ops`, with `query_ras_error_count` and `reset_ras_error_count`.

## Control Flow
Invalidate skips selected HDP 4.4.x revisions, otherwise either writes `mmHDP_READ_CACHE_INVALIDATE` directly and posts the write with a readback or emits the write through a ring. RAS query zeroes counts, checks whether HDP RAS is supported, and treats `mmHDP_EDC_CNT` as uncorrectable errors. Reset either writes zero for newer HDP versions or reads the counter for older clear-on-read behavior.

Clock gating chooses between legacy `mmHDP_MEM_POWER_LS` and newer `mmHDP_MEM_POWER_CTRL` layouts based on HDP IP version. Register init applies a 4.2.1 MMHUB GCC bit, avoids most programming for SR-IOV VFs, sets flush/invalidate cache behavior, adjusts read buffer watermark for 4.4.0, and programs nonsurface base registers from `adev->gmc.vram_start`.

## State, Dependencies, And Integration
State is hardware-resident in HDP registers and RAS counters; software integration is via `adev->hdp.funcs` and `adev->hdp.ras`, typically selected by GMC setup. Dependencies include SOC15 register macros, `amdgpu_ras_is_supported`, AMDGPU ring write helpers, IP version checks, and KFD constants for remapped MMIO context.

## Risks And Test Signals
Risks include clearing or reading RAS counters with the wrong semantics, skipping invalidation on the wrong HDP revision, programming HDP registers on SR-IOV VFs, and mismatched clock-gating bits across 4.x revisions. Test signals include host-visible memory coherency tests, HDP RAS injection/count reset, SR-IOV VF probe, clock-gating flag checks, and GFX9 hardware init that calls HDP init followed by flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.h

## Purpose
`hdp_v4_0.h` declares the HDP 4.x function table and RAS descriptor.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `hdp_v4_0_funcs` as `const struct amdgpu_hdp_funcs` plus `hdp_v4_0_ras` as `struct amdgpu_hdp_ras`.

## Control Flow, State, And Integration
There is no executable code. The declarations are consumed by GMC/IP setup, especially GMC v9 code, to assign HDP cache and RAS callbacks into `adev->hdp`.

## Risks And Test Signals
The risk is declaration mismatch with `hdp_v4_0.c` or missing includes for the function-table types. Build coverage and successful HDP function dispatch during GMC init are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.c

## Purpose
`hdp_v5_0.c` provides HDP 5.0 cache invalidation, memory power gating, medium-grain clock gating, clock-gating state reporting, and basic register initialization.

## Important APIs, Types, And Functions
The exported `hdp_v5_0_funcs` table wires `amdgpu_hdp_generic_flush`, `hdp_v5_0_invalidate_hdp`, `hdp_v5_0_update_clock_gating`, `hdp_v5_0_get_clockgating_state`, and `hdp_v5_0_init_registers`.

## Control Flow
Invalidate uses direct MMIO when no ring write function is available and ring-emitted register writes otherwise. Memory power gating first forces IPH and RC memory clocks on, disables all LS/DS/SD controls because HDP 5.0 cannot switch dynamically, then enables exactly one supported memory power mode according to `adev->cg_flags`, and finally releases clock overrides. Medium-grain clock gating toggles soft override masks in `mmHDP_CLK_CNTL`: clearing overrides enables gating, setting overrides disables it. Init sets `HDP_MISC_CNTL.FLUSH_INVALIDATE_CACHE`.

## State, Dependencies, And Integration
State lives in HDP 5.0 registers (`mmHDP_READ_CACHE_INVALIDATE`, `mmHDP_CLK_CNTL`, `mmHDP_MEM_POWER_CTRL`, `mmHDP_MISC_CNTL`) and in `adev->cg_flags`. The file depends on SOC15 register access, HDP 5.0 headers, AMDGPU ring helpers, and generic HDP flush.

## Risks And Test Signals
Risks include enabling multiple SRAM power modes, failing to force clocks before mode changes, not posting invalidation writes, and stale clock-gating state reporting. Test signals are host/GPU coherency tests, ring and direct invalidation paths, clock-gating flag validation, and suspend/resume with HDP gating enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.h

## Purpose
`hdp_v5_0.h` declares the HDP 5.0 function table for AMDGPU IP setup.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `extern const struct amdgpu_hdp_funcs hdp_v5_0_funcs;`.

## Control Flow, State, Dependencies, And Risks
The header has no code or state. It depends on the HDP function-table type being visible through included headers. Build/link coverage catches declaration drift, and runtime coverage is successful assignment and use of the HDP 5.0 callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.c

## Purpose
`hdp_v5_2.c` implements HDP 5.2 behavior, with a custom flush path through KFD MMIO remap registers and clock/power gating logic for ATOMIC and RC memory blocks.

## Important APIs, Types, And Functions
The exported `hdp_v5_2_funcs` table provides `hdp_v5_2_flush_hdp`, `hdp_v5_2_update_clock_gating`, and `hdp_v5_2_get_clockgating_state`. Unlike v5.0, this table does not provide invalidate or init-register callbacks.

## Control Flow
`hdp_v5_2_flush_hdp` writes the remapped `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` register either directly or through a command ring. Direct flush posts the write by reading back the remapped register on SR-IOV VF, but on bare metal avoids reading the remapped register and instead calls `nbio.funcs->get_memsize()` when available.

Clock gating forces ATOMIC/RC memory clocks on, disables all memory power-control bits, then enables the preferred single mode in priority order SD, LS, then DS according to `adev->cg_flags`. It sets ATOMIC and RC power-control enable bits before releasing clock overrides. Medium-grain gating toggles soft override masks in `regHDP_CLK_CNTL`; state reporting inspects those masks and the ATOMIC memory power mode bits.

## State, Dependencies, And Integration
State is in HDP 5.2 clock and memory-power registers plus remapped MMIO offsets in `adev->rmmio_remap`. Dependencies include HDP 5.2 headers, KFD MMIO remap constants, SOC15 register access, NBIO memsize callback, ring writes, SR-IOV helpers, and `adev->cg_flags`.

## Risks And Test Signals
Risks include incorrect remap offset arithmetic, unsafe readback of remapped flush registers, SR-IOV posting differences, and memory-power mode priority changes. Tests should exercise direct and ring HDP flush, SR-IOV VF behavior, KFD-visible memory coherency, and clock-gating state with LS/DS/SD combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.h

## Purpose
`hdp_v5_2.h` declares the HDP 5.2 function table.

## Important APIs, Types, And Functions
The only exported symbol is `extern const struct amdgpu_hdp_funcs hdp_v5_2_funcs;`, with `soc15_common.h` included for AMDGPU/SOC15 type context.

## Control Flow, State, Integration, And Risks
There is no control flow or local state. The header is consumed by ASIC/IP setup code that assigns HDP 5.2 callbacks. Build/link tests catch symbol mismatch; runtime signals are successful HDP flush and clock-gating callback dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c

## Purpose
`hdp_v6_0.c` supplies HDP 6.0 clock and memory power-gating callbacks plus generic HDP flush support.

## Important APIs, Types, And Functions
The exported `hdp_v6_0_funcs` table contains `amdgpu_hdp_generic_flush`, `hdp_v6_0_update_clock_gating`, and `hdp_v6_0_get_clockgating_state`.

## Control Flow
`hdp_v6_0_update_clock_gating` returns early unless LS/DS/SD HDP gating is supported. It selects `regHDP_CLK_CNTL_V6_1` for HDP IP 6.1.0 and `regHDP_CLK_CNTL` otherwise, forces RC memory clock on, clears all ATOMIC/RC power mode bits, enables exactly one mode in priority order SD, LS, then DS, sets ATOMIC/RC power-control enable bits, and releases the RC clock override. `hdp_v6_0_get_clockgating_state` reads `regHDP_MEM_POWER_CTRL` and maps ATOMIC LS/DS/SD bits to AMDGPU clock-gating flags.

## State, Dependencies, And Integration
State is fully hardware-resident in HDP clock and memory-power registers, with policy gated by `adev->cg_flags` and HDP IP version. Dependencies include HDP 6 register headers, SOC15 macros, KFD ioctl constants, and generic HDP flush. Integration occurs through `adev->hdp.funcs`.

## Risks And Test Signals
Risks include using the wrong clock-control register for 6.1.0, mode-priority regressions, and failing to release clock overrides after power-mode changes. Test signals are HDP flush coherency, clock-gating state reporting on 6.0 and 6.1 hardware, and suspend/resume with clock gating enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.h

## Purpose
`hdp_v6_0.h` declares the HDP 6.0 callback table.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `extern const struct amdgpu_hdp_funcs hdp_v6_0_funcs;`.

## Control Flow, State, Integration, And Risks
The file has no executable control flow or state. It participates in AMDGPU IP wiring by making the function table visible to ASIC setup. Build/link coverage catches declaration drift; runtime validation is callback use on HDP 6.x hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v6_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.c

## Purpose
`hdp_v7_0.c` provides HDP 7.0 clock and memory power-gating callbacks and uses generic HDP flushing.

## Important APIs, Types, And Functions
The exported `hdp_v7_0_funcs` table contains `amdgpu_hdp_generic_flush`, `hdp_v7_0_update_clock_gating`, and `hdp_v7_0_get_clockgating_state`.

## Control Flow
`hdp_v7_0_update_clock_gating` exits unless HDP LS/DS/SD support is advertised. It reads `regHDP_CLK_CNTL` and `regHDP_MEM_POWER_CTRL`, forces RC memory clocks on, clears ATOMIC and RC LS/DS/SD enable bits, then enables one mode with SD preferred over LS and DS. It sets ATOMIC/RC power-control enable bits when any supported mode exists and finally clears the RC clock override. `hdp_v7_0_get_clockgating_state` reports LS/DS/SD based on ATOMIC memory power bits.

## State, Dependencies, And Integration
The state model is hardware register state plus `adev->cg_flags`. Dependencies include HDP 7.0 register headers, SOC15 access macros, KFD ioctl constants, and generic HDP flush. Integration is via the device HDP function table.

## Risks And Test Signals
Risks are the same class as v6 but without the v6.1 alternate register path: incorrect power-mode priority, stale overrides, or inaccurate state reporting. Test signals include HDP cache coherency, clock-gating state readback, and suspend/resume on HDP 7 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.h

## Purpose
`hdp_v7_0.h` declares the HDP 7.0 function table.

## Important APIs, Types, And Functions
It includes `soc15_common.h` and exports `extern const struct amdgpu_hdp_funcs hdp_v7_0_funcs;`.

## Control Flow, State, Integration, And Risks
There is no code or state. The header supports AMDGPU IP setup by exposing the HDP 7.0 callback table. Build/link coverage catches declaration mismatches; hardware probe and HDP flush/clock-gating callback dispatch validate integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v7_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c

## Purpose
`iceland_ih.c` implements the VI/Iceland interrupt-handler IP block. It configures the hardware interrupt ring, provides ring pointer management and interrupt-vector decoding, initializes AMDGPU IRQ software state, and exports `iceland_ih_ip_block`.

## Important APIs, Types, And Functions
The IP lifecycle is in `iceland_ih_ip_funcs`: early/software/hardware init and fini, suspend/resume, idle polling, soft reset, and no-op clock/power gating. `iceland_ih_funcs` provides the IH ring callbacks `get_wptr`, `decode_iv`, and `set_rptr`. Core helpers include `iceland_ih_irq_init()`, `iceland_ih_irq_disable()`, `iceland_ih_enable_interrupts()`, `iceland_ih_disable_interrupts()`, `iceland_ih_get_wptr()`, and `iceland_ih_decode_iv()`.

## Control Flow
`early_init` creates the IRQ domain and installs IH callbacks. `sw_init` allocates the 64 KiB hardware IH ring, creates the software IH ring, and initializes IRQ sources. `hw_init` disables interrupts, programs dummy-page and interrupt control registers, writes ring base and writeback addresses, configures ring size and overflow handling, clears rptr/wptr, sets MSI rearm behavior when enabled, calls `pci_set_master`, enables the ring, and marks the software ring enabled if present.

Runtime interrupt processing asks `get_wptr` for the current write pointer, which prefers writeback memory, checks and clears overflow on the hardware ring, advances `rptr` to a catch-up position after overflow, and masks the pointer. `decode_iv` reads four dwords from the ring, fills legacy client ID, source ID, source data, ring ID, VMID, and PASID, then advances `rptr` by 16 bytes. `set_rptr` writes the hardware read pointer.

## State And Persistence
State lives in `adev->irq.ih`, `adev->irq.ih_soft`, their ring buffers, writeback memory, read pointers, enabled flags, IRQ domain state, and IH hardware registers. On disable, hardware and software rptr/wptr state is reset to zero. No disk persistence is involved.

## Dependencies And Integration Points
The file depends on OSS/BIF VI register headers, PCI bus mastering, AMDGPU IH and IRQ core, ring allocation helpers, dummy-page allocation from the device, MSI state, and SRBM reset/status registers. It integrates with the global IRQ processing path through `adev->irq.ih_funcs`.

## Risks And Test Signals
Risks include incorrect ring size encoding, bad writeback address programming, overflow recovery losing vectors, MSI rearm mismatch, rptr/wptr byte-versus-dword mistakes, and reset while interrupts are live. Test signals are interrupt delivery under MSI and non-MSI, ring overflow stress, suspend/resume, IRQ domain setup/teardown, soft reset when IH busy, and VM fault IRQ delivery through the decoded legacy IV format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.h

## Purpose
`iceland_ih.h` declares the Iceland/VI interrupt-handler IP block.

## Important APIs, Types, And Functions
The only exported symbol is `extern const struct amdgpu_ip_block_version iceland_ih_ip_block;`, which points device/IP setup code to the implementation in `iceland_ih.c`.

## Control Flow, State, Integration, And Risks
The header has no executable code or state. It depends on the AMDGPU IP block type definition being available to consumers. Build/link coverage catches symbol drift; runtime validation is successful VI IH probe, interrupt ring initialization, and IRQ delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/iceland_ih.h -->
