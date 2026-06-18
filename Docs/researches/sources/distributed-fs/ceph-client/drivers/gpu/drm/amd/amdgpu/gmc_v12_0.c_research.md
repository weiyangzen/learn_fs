# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_0.c

## Purpose
This file implements the GMC v12 IP block for GC 12.0 and dispatches GC 12.1-specific helper callbacks from `gmc_v12_1.c`. It owns VM/GART lifecycle, GFX12 PTE/PDE encoding, VM fault/ECC IRQ setup, XGMI/host-GPU aperture handling, PDB0 setup, and clock-gating integration.

## Important APIs, Types, and Functions
Public exports are `gmc_v12_0_ip_funcs` and `gmc_v12_0_ip_block`. Internal callback tables include `gmc_v12_0_gmc_funcs`, `gmc_v12_0_irq_funcs`, and `gmc_v12_0_ecc_funcs`; for GC 12.1 early init delegates to `gmc_v12_1_set_gmc_funcs()` and `gmc_v12_1_set_irq_funcs()`. Important functions include `process_interrupt`, `flush_vm_hub`, `flush_gpu_tlb`, `flush_gpu_tlb_pasid`, `get_vm_pde`, `get_vm_pte`, `get_dcc_alignment`, `mc_init`, `gart_init`, `sw_init`, and `gart_enable`.

## Control Flow and State
Early init probes host XGMI support, chooses v12.0 or v12.1 GMC/IRQ callbacks, sets GFXHUB/MMHUB/UMC callbacks, apertures, private aperture size, and no-retry flags. SW init initializes hubs, VRAM info (or v12.1 HBM4 defaults), VM hub masks, 48-bit or 57-bit VM sizing, VM fault/retry IRQ IDs, ECC IRQ IDs, DMA mask, MC layout, optional ACPI memory ranges, BO/GART/PDB0 allocation, KFD VMID split, VM manager, and RAS. GART init may allocate `pdb0_bo` and sets GFX12 PTE flags. GART enable initializes PDB0 for CPU-connected XGMI, enables MMHUB, sets fault defaults, flushes MMHUB VMID0, and reports either PDB0 or GART table address. PASID TLB invalidation can use unified MES, otherwise scans VMID LUTs.

## Dependencies and Integration Points
The file depends on GFXHUB v12.0/v12.1, MMHUB v4.1/v4.2, ATHUB v4.1, UMC v8.14, SOC21/SOC24 IRQ IDs, ACPI memory range support, NBIF/SMUIO, BO/GART/VM managers, KFD retry-fault routing, and RAS.

## Risks and Test Signals
Risks include GC 12.1 dispatch, 57-bit VM sizing, XGMI/PDB0 address math, PTE flag changes (`AMDGPU_PTE_IS_PTE`, DCC, PRT), MES version gates, ECC client ID variation, and freeing `pdb0_bo`. Test signals include GC 12.0 and 12.1 boot, CPU-connected XGMI, large VA/KFD workloads, retry faults, MES PASID invalidation, DCC buffer mappings, RAS ECC IRQs, and suspend/resume.
