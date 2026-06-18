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
