# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.c

## Purpose
This file implements the legacy GMC v6 IP block for Southern Islands-era ASICs. It manages MC firmware loading/training, memory-controller blackout/resume, VRAM/GART placement, direct legacy VM register programming, VM fault IRQs, reset handling, and clock/low-power gating.

## Important APIs, Types, and Functions
The public export is `gmc_v6_0_ip_block`; `gmc_v6_0_ip_funcs`, `gmc_v6_0_gmc_funcs`, and `gmc_v6_0_irq_funcs` are static callback tables. Important functions include `init_microcode`, `mc_load_microcode`, `mc_program`, `mc_init`, `gart_enable`, `gart_disable`, `flush_gpu_tlb`, `emit_flush_gpu_tlb`, `set_prt`, `process_interrupt`, `soft_reset`, `set_clockgating_state`, and lifecycle callbacks.

## Control Flow and State
SW init sets the single GFX hub bit, derives VRAM type from `MC_SEQ_MISC0`, registers legacy VM fault IRQ IDs 146/147, sets 40-bit VM/DMA constraints, loads required MC firmware, initializes MC sizing/placement, BO/GART/VM managers, and VMID split. HW init programs HDP/system apertures, loads MC firmware on discrete GPUs, enables the GART, and optionally checks VRAM in emulation. GART enable writes legacy L1/L2 VM registers, context0 GART page-table base/range, context1-15 defaults, dummy fault page, fault policy, and invalidates VMID0. Soft reset detects busy MC/VMC bits, blackouts CPU access, toggles `SRBM_SOFT_RESET`, then resumes MC access. Fault IRQ handling may delegate to a soft IH, reads legacy fault address/status registers, clears fault status, updates the fault cache, optionally disables further default handling, and logs decoded protection details.

## Dependencies and Integration Points
Dependencies include firmware files `tahiti_mc.bin`, `pitcairn_mc.bin`, `verde_mc.bin`, `oland_mc.bin`, `hainan_mc.bin`, and `si58_mc.bin`; SI register headers; AMDGPU ucode, BO, GART, VM, IRQ, and PCI/DMA helpers. ASIC setup in `si.c` registers `gmc_v6_0_ip_block`.

## Risks and Test Signals
Risk areas include required firmware availability, MC training timeouts, blackout/reset sequencing, 40-bit address assumptions, legacy fault IRQ handling, PRT disabling faults, and clock-gating register tables. Test signals include SI board boot, firmware load logs, GART enable log, VM fault decode, soft reset recovery, suspend/resume, VRAM checking in emulation, and clock-gating transitions.
