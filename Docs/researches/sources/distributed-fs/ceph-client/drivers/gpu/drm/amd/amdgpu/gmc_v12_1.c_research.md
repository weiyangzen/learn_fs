# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_1.c

## Purpose
This file supplies GC 12.1-specific GMC helper callbacks that are installed by `gmc_v12_0.c`. It is not a standalone IP block; it provides VM fault IRQ logic, multi-XCC/MMHUB TLB invalidation, GFX12.1 page-table encoding/coherency policy, memory partition query hooks, and default VRAM metadata.

## Important APIs, Types, and Functions
Public functions are `gmc_v12_1_set_gmc_funcs`, `gmc_v12_1_set_irq_funcs`, and `gmc_v12_1_init_vram_info`. The `gmc_v12_1_gmc_funcs` table supplies `flush_gpu_tlb`, `flush_gpu_tlb_pasid`, `emit_flush_gpu_tlb`, `emit_pasid_mapping`, `get_vm_pde`, `get_vm_pte`, and memory partition callbacks. The IRQ table uses `gmc_v12_1_process_interrupt`.

## Control Flow and State
Fault-mask enable/disable iterates every set VM hub and all 16 contexts, using MMHUB register access for MM hubs and `RREG32_XCC/WREG32_XCC` for GFX hubs, skipping GFXHUB during S0ix. Fault processing maps IH node IDs to MMHUB or logical XCC, handles retry faults through retry CAM or software filtering/delegation, calls `amdgpu_vm_handle_fault`, fast-paths KFD, then rate-limited logs and reads L2 fault status on non-VF devices. TLB flushing chooses per-XCC KIQ/MES firmware paths when available or direct RLC writes under `invalidate_lock`; PASID invalidation can use MES v0x6f+ from the master XCC, otherwise scans per-instance VMID LUTs. PDE/PTE encoding uses GFX12 flags, snooping, bus atomics, local/remote memory-type policy, and rev-dependent defaults for IP 12.1.0.

## Dependencies and Integration Points
The file depends on OSSSYS 7.1 registers, SOC v1.0 IH client names, retry CAM doorbells, MES invalidation APIs, KFD fast-path fault handling, memory partition helpers, and BO/TTM locality data. It is installed only by GMC v12 early init for `IP_VERSION(12, 1, 0)`.

## Risks and Test Signals
Risks include node-to-XCC mapping, retry CAM doorbell ordering, MES master-XCC filtering, VMID LUT index selection, memory-type policy regressions, and 57-bit address encoding. Test signals include GC 12.1 multi-XCC boot, retry fault recovery, KFD VM fault fast path, MES PASID invalidation across hubs, local/remote VRAM mappings, atomics/coherency tests, and memory partition requests.
