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
