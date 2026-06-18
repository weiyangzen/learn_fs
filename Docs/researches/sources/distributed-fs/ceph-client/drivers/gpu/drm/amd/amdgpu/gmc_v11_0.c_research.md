# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c

## Purpose
This file implements the GMC v11 IP block for GC 11 devices. It is the memory-controller lifecycle owner for this generation, selecting MMHUB/GFXHUB/UMC implementations, registering VM fault and ECC IRQs, managing GART and VM sizing, encoding page-table entries, and handling TLB invalidation.

## Important APIs, Types, and Functions
Public exports are `gmc_v11_0_ip_funcs` and `gmc_v11_0_ip_block`. Main internal APIs include `gmc_v11_0_process_interrupt`, `flush_gpu_tlb`, `flush_gpu_tlb_pasid`, `emit_flush_gpu_tlb`, `emit_pasid_mapping`, `get_vm_pde`, `get_vm_pte`, `mc_init`, `gart_init`, `sw_init`, `gart_enable`, `hw_init`, and clock-gating callbacks.

## Control Flow and State
Early init selects `gfxhub_v3_0`, `gfxhub_v3_0_3`, or `gfxhub_v11_5_0`, selects MMHUB v3 variants, installs GMC/IRQ/UMC callbacks, and initializes apertures/no-retry flags. SW init initializes MMHUB then GFXHUB, gets VRAM metadata, adjusts MALL size for gfx1151, sets VM hub mask and 48-bit VM sizing, registers SOC21 VMC/GFX/DF IRQ IDs, sets DMA mask, initializes MC placement, BO/GART/VM managers, KFD VMID split, and RAS. HW init applies golden-register handling, enables GART through MMHUB, and initializes UMC registers. TLB invalidation skips powered-off GFXHUB, uses KIQ/MES firmware paths when ready, otherwise writes direct registers under `invalidate_lock`; MMHUB invalidation may additionally toggle the private-cache invalidation bit in `vm_l2_bank_select_reserved_cid2`.

## Dependencies and Integration Points
The file integrates with MMHUB v3.0/v3.0.1/v3.0.2/v3.3, GFXHUB v3.0/v3.0.3/v11.5, UMC v8.10, ATHUB v3.0, SOC21 IRQ identifiers, NBIO memory sizing, VM/BO/GART managers, KFD PASID mapping, and RAS.

## Risks and Test Signals
Risks include generation dispatch mistakes, MMHUB-only GART enable assumptions, powered-off GFXHUB flush skips, private-cache invalidation register handling, visible VRAM clamping, and `disable_kq` changing KFD VMID allocation. Test signals include GC 11/11.5 boot, suspend/resume/runpm, SR-IOV, KFD workloads, page-fault logging and retry handling, ECC/RAS paths, GART allocation/fini, and clock-gating state collection.
