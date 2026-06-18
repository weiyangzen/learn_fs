# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c

## Purpose
This file implements the GMC v10 IP block for GC 10 GPUs. It owns memory-controller software/hardware lifecycle, VM fault and ECC IRQ registration, GART allocation/enabling, VRAM/GTT address placement, TLB flushing, PTE/PDE encoding, UMC/MMHUB/GFXHUB function selection, and clock-gating integration.

## Important APIs, Types, and Functions
Public exports are `gmc_v10_0_ip_funcs` and `gmc_v10_0_ip_block`. Core callback tables include `gmc_v10_0_gmc_funcs`, `gmc_v10_0_irq_funcs`, and `gmc_v10_0_ecc_funcs`. Important functions include `gmc_v10_0_process_interrupt`, `flush_gpu_tlb`, `flush_gpu_tlb_pasid`, `emit_flush_gpu_tlb`, `emit_pasid_mapping`, `get_vm_pde`, `get_vm_pte`, `mc_init`, `gart_init`, `sw_init`, `gart_enable`, and `hw_init`.

## Control Flow and State
Early init selects MMHUB, GFXHUB, GMC, IRQ, and UMC callback tables, sets shared/private apertures, and configures no-retry flags. SW init initializes VM hubs, lock state, VRAM info, MALL size, VM hub mask, VM sizing, IRQ IDs, DMA mask, MC layout, BO manager, GART table, KFD VMID split, VM manager, and RAS. HW init sets flush policy, applies golden/harvest setup, enables GART, optionally checks VRAM in emulation, and initializes UMC registers. GART enable programs GFXHUB except in S0ix, always programs MMHUB, initializes HDP, sets fault default policy, flushes VMID0, and logs GART size/table. TLB flushing chooses a KIQ/firmware write-wait path when available, otherwise serializes direct register access with `adev->gmc.invalidate_lock` and optional MMHUB semaphore.

## Dependencies and Integration Points
This file integrates with `gfxhub_v2_0/2_1`, `mmhub_v2_0/2_3`, `athub_v2_0/2_1`, UMC v8.7 RAS, NBIO memory-size queries, DRM BO/GART/VM managers, KFD PASID/VMID mappings, and SOC15 IRQ client IDs. It uses VM fault cache updates and retry-fault handling before KFD delivery.

## Risks and Test Signals
Risk areas include TLB flush races, semaphore timeout handling, S0ix skipping of GFXHUB fault masks, XGMI offset math, PTE memory-type correctness, visible VRAM sizing, and version-table selection. Test signals include Navi10/GC 10.3 boot, suspend/resume/S0ix, SR-IOV VF, KFD PASID TLB flush, page-fault logging and retry handling, RAS ECC IRQs, GART table allocation/fini, and clock-gating transitions.
