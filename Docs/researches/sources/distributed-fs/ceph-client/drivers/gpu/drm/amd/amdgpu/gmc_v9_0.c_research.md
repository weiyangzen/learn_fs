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
