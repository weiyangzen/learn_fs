# subset-b-001342 research

Grouped source research for the AMDGPU GMC/GFXHUB files in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.h

## Purpose
This header is the public declaration point for the GFXHUB 1.0 backend used by the AMDGPU GMC code on older Vega-era GC 9 hardware. It exposes `gfxhub_v1_0_funcs`, a `const struct amdgpu_gfxhub_funcs` implemented in the matching `gfxhub_v1_0.c` and selected by generation-specific GMC code such as `gmc_v9_0.c`.

## Important APIs, Types, and Functions
The only exported symbol is `gfxhub_v1_0_funcs`. The type is defined elsewhere in the AMDGPU core and supplies callbacks for VM hub register initialization, GART enable/disable, page-table base programming, fault-default policy, and related GFX VM-hub services. This header relies on including translation units already knowing `struct amdgpu_gfxhub_funcs`.

## Control Flow and State
There is no executable control flow or persistent state in the header. Its effect is compile-time linkage: users include it so they can assign `adev->gfxhub.funcs` to the v1.0 callback table during GMC early initialization.

## Dependencies and Integration Points
The include guard `__GFXHUB_V1_0_H__` prevents duplicate declarations. Integration is with AMDGPU device setup code that switches callback tables by GC IP version. The callbacks eventually operate on `adev->vmhub[AMDGPU_GFXHUB(0)]`, GART objects, VM manager sizing, and SOC15 register offsets.

## Risks and Test Signals
The main risk is wrong function-table selection rather than header-local behavior. Compile/link tests catch missing or mismatched `gfxhub_v1_0_funcs`; boot/resume on GC 9 boards validates the callback table, GART enablement, TLB invalidation, and VM fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c

## Purpose
This file provides the GFXHUB 1.1 XGMI topology query helper for Vega20, Arcturus, and Aldebaran-class devices. It reads the GFX hub XGMI local-frame-buffer registers and records node count, node id, and segment size in `adev->gmc.xgmi`.

## Important APIs, Types, and Functions
`gfxhub_v1_1_get_xgmi_info(struct amdgpu_device *adev)` is the sole exported function. It uses `RREG32_SOC15`, `REG_GET_FIELD`, and local Aldebaran-specific register/mask definitions for `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE`. The output state is `adev->gmc.xgmi.num_physical_nodes`, `physical_node_id`, and `node_segment_size`.

## Control Flow and State
The function first selects Aldebaran-specific register addresses and masks when `adev->asic_type == CHIP_ALDEBARAN`; otherwise it uses the standard GC 9.2.1 register definitions. It derives `seg_size` by shifting the hardware PF LFB size field by 24, derives `max_region`, then constrains expected physical-node limits by ASIC: 4 nodes for Vega20, 8 for Arcturus, and 16 for Aldebaran. When XGMI appears enabled (`max_region` nonzero) or the GPU is connected to the CPU over XGMI, it writes the derived GMC XGMI fields and returns `-EINVAL` if either the number of nodes or local node id exceeds the generation limit.

## Dependencies and Integration Points
This helper is declared by `gfxhub_v1_1.h` and is used by GMC initialization paths that need XGMI-aware VRAM/GART placement. It depends on `amdgpu.h`, GC 9.2.1 offset/mask headers, and SOC15 register access helpers.

## Risks and Test Signals
The risk is topology mis-detection: an incorrect `node_segment_size` or `physical_node_id` shifts VRAM base calculations and can corrupt multi-GPU address placement. Test signals include XGMI multi-node boot, KFD peer-memory workloads, GPU reset/resume on Vega20/Arcturus/Aldebaran, and validation that unsupported ASICs return `-EINVAL` instead of silently programming invalid topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.h

## Purpose
This header declares the GFXHUB 1.1 XGMI information helper for other AMDGPU source files. It is intentionally narrow: GFXHUB 1.1 in this subset contributes topology discovery rather than a whole public callback table.

## Important APIs, Types, and Functions
The exported prototype is `int gfxhub_v1_1_get_xgmi_info(struct amdgpu_device *adev);`. The function returns `0` on successful discovery or disabled XGMI, and `-EINVAL` for unsupported ASICs or invalid register-derived topology. The caller owns the `struct amdgpu_device` and reads the resulting `adev->gmc.xgmi` fields.

## Control Flow and State
The header itself has no runtime control flow. It establishes a compile-time contract for code that needs to query XGMI and then use the persisted GMC XGMI fields during VRAM/GART placement.

## Dependencies and Integration Points
It relies on a forward-visible `struct amdgpu_device` from the including translation unit. It is included by `gfxhub_v1_2.c` and other generation-specific GMC/GFXHUB code that can reuse the v1.1 topology convention.

## Risks and Test Signals
The main header-local risk is declaration drift if the implementation changes signature. Build coverage catches that. Runtime validation belongs to the `.c` implementation: multi-node XGMI address layout, hot reset, and VM fault-free access to remote/local VRAM segments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c

## Purpose
This file implements the GFXHUB 1.2 backend for GC 9.4.3-style multi-XCC hardware. It programs per-XCC VM context registers, GART/system apertures, TLB and L2 cache controls, fault behavior, XGMI topology, and XCP suspend/resume hooks.

## Important APIs, Types, and Functions
The public exports are `gfxhub_v1_2_funcs` and `gfxhub_v1_2_xcp_funcs`. Important callbacks include `get_mc_fb_offset`, `setup_vm_pt_regs`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `init`, and `get_xgmi_info`. Internal helpers are mostly `gfxhub_v1_2_xcc_*` variants that iterate an `xcc_mask` with `for_each_inst`.

## Control Flow and State
Initialization computes a mask from `adev->gfx.xcc_mask`, then seeds each `adev->vmhub[AMDGPU_GFXHUB(i)]` with page-table base, invalidate-engine, fault, and stride register offsets. GART enable programs VMID0 page-table base and aperture limits, system/AGP apertures, default scratch/dummy fault pages, L1 TLB settings, optional L2 cache controls, system-domain context 0, disabled identity apertures, contexts 1-15, and invalidate engine address ranges. `pdb0_bo` and `amdgpu_virt_xgmi_migrate_enabled()` alter VMID0 coverage so system memory and VRAM can share a translated aperture. `gart_disable` clears contexts and disables L1/L2 controls. Fault defaults are broadcast per XCC and can turn crash-on-retry/no-retry bits on when default handling is disabled.

## Dependencies and Integration Points
The file depends on GC 9.4.3 register headers, `amdgpu_xcp.h`, `soc15_common.h`, and shared GMC/VM helpers such as `amdgpu_gmc_pd_addr`, `amdgpu_gmc_vram_mc2pa`, and SR-IOV checks. `gfxhub_v1_2_xcp_funcs` is consumed by XCP partitioning code such as `aqua_vanjaram.c`, allowing partition-specific suspend/resume of selected XCC instances.

## Risks and Test Signals
Risks cluster around multi-XCC masking, `NUM_XCC()` assumptions, PDB0/GART aperture boundaries, SR-IOV register accessibility, and retry/XNACK fault policy. Test signals include boot and reset on GC 9.4.3, XCP partition suspend/resume, XGMI-connected CPU configurations, VM fault-stop modes, multi-XCC TLB invalidation, and KFD per-process XNACK workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.h

## Purpose
This header exposes the GFXHUB 1.2 callback table and XCP IP hooks used by GC 9.4.3-style multi-XCC devices.

## Important APIs, Types, and Functions
It declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v1_2_funcs;` and `extern struct amdgpu_xcp_ip_funcs gfxhub_v1_2_xcp_funcs;`. The first is assigned to `adev->gfxhub.funcs`; the second gives XCP partitioning code suspend/resume hooks that accept an instance mask.

## Control Flow and State
The header has no runtime flow. Its declarations connect GMC generation selection and XCP registration to the implementation in `gfxhub_v1_2.c`. State affected by the implementation includes per-XCC `adev->vmhub[]` register offsets and persistent GMC fault/cache configuration registers.

## Dependencies and Integration Points
Users must include or otherwise know `struct amdgpu_gfxhub_funcs` and `struct amdgpu_xcp_ip_funcs`. Integration points are GMC early initialization, GART enable/disable, VM fault policy, and XCP partition lifecycle.

## Risks and Test Signals
Declaration drift is the compile-time risk. Runtime confidence comes from successful linkage and from multi-XCC partition tests that call `gfxhub_v1_2_xcp_funcs` with partial instance masks without disturbing other partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c

## Purpose
This file implements the GFXHUB 2.0 VM hub backend for Navi 1x-era GC 10.1 devices. It programs the GCVM/GCMC register set, exposes fault-status decoding, and provides callback operations used by GMC v10.

## Important APIs, Types, and Functions
The public table is `gfxhub_v2_0_funcs`. Its callbacks read FB location and MC FB offset, set VM page-table bases, enable/disable the GART, set fault-default behavior, and initialize `adev->vmhub[AMDGPU_GFXHUB(0)]`. A private `amdgpu_vmhub_funcs` table supplies `print_l2_protection_fault_status` and `get_invalidate_req`. `gfxhub_client_ids[]` maps GCVM fault client IDs to readable names.

## Control Flow and State
`init()` writes register offsets, context/invalidate strides, fault interrupt masks, `sdma_invalidation_workaround`, and the VM hub function table into `adev->vmhub`. GART enable programs VMID0 page-table base/range from `adev->gart.bo`, system and AGP apertures, scratch/default fault addresses, L1 TLB controls, L2 cache and fragment defaults, context0, disabled identity aperture, contexts 1-15, and invalidate ranges for 18 engines. VMID user contexts use `adev->vm_manager.num_level`, `block_size - 9`, and `max_pfn`. Fault default toggling updates every protection-fault default bit and sets crash-on-fault bits when disabled.

## Dependencies and Integration Points
The implementation depends on GC 10.1 offset/mask/default headers, `navi10_enum.h`, and SOC15 register helpers. It is selected by `gmc_v10_0_set_gfxhub_funcs()` for older GC 10 variants. GMC TLB flushing calls the VM hub `get_invalidate_req` callback generated here.

## Risks and Test Signals
Risks include off-by-one VMID context programming, stale invalidate ranges, SR-IOV register access, and fault-status interpretation. Test signals include Navi10 boot/resume, GART log line, page-fault logging with decoded CID, VM update workloads, SDMA invalidation behavior, and suspend/resume with VM faults enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.h

## Purpose
This header declares the GFXHUB 2.0 callback table for GC 10.1/Navi 1x VM hub support.

## Important APIs, Types, and Functions
It exports `gfxhub_v2_0_funcs`, a `const struct amdgpu_gfxhub_funcs`. Consumers use it through `adev->gfxhub.funcs`, not by calling individual static functions.

## Control Flow and State
There is no runtime control flow. The declaration allows GMC v10 setup code to bind the correct GFXHUB implementation. The implementation persists VM hub register metadata in `adev->vmhub` and hardware VM/cache/fault settings in GCVM/GCMC registers.

## Dependencies and Integration Points
It requires the including C file to have the AMDGPU type definitions in scope. Integration is with `gmc_v10_0.c`, VM fault handling, GART enablement, and TLB invalidation.

## Risks and Test Signals
The header risk is symbol mismatch or missing implementation at link time. Runtime testing is driven by the `.c` callback table: Navi-class boot, GART allocation, VM fault decode, and TLB flush workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c

## Purpose
This file implements the GFXHUB 2.1 backend for later GC 10.3 devices. It is close to v2.0 but adds SR-IOV handling, UTCL2 harvest programming, mode2 register save/restore, and a halt path for quiescing EA activity.

## Important APIs, Types, and Functions
`gfxhub_v2_1_funcs` exports the standard GFXHUB callbacks plus `utcl2_harvest`, `mode2_save_regs`, `mode2_restore_regs`, and `halt`. Private functions mirror v2.0 for invalidate request generation, fault-status printing, GART enable/disable, fault default policy, and VM hub initialization.

## Control Flow and State
GART enable optionally programs VF FB location copy registers, then initializes VMID0 page tables, apertures, TLB/cache controls, context0, disabled identity aperture, user contexts, and invalidation ranges. SR-IOV VFs skip many L2 and system-aperture register writes that the PF owns. `utcl2_harvest()` computes disabled shader-array bits from eFuse and VBIOS fields for selected GC 10.3 IPs and writes the harvest bypass register. `save_regs()` snapshots many GCVM context, L2, dummy fault, and protection registers into `adev->gmc`; `restore_regs()` replays them and restores FB location and L1 TLB control. `halt()` disables default fault handling, invalidates user page-table ranges, and polls `GRBM_STATUS2` for EA/link idle.

## Dependencies and Integration Points
It depends on GC 10.3 register headers and is selected by `gmc_v10_0.c` for GC 10.3.x IP versions. Mode2 save/restore integrates with lower-power reset paths. UTCL2 harvest is invoked before GFX block register setup in GMC v10 hardware init.

## Risks and Test Signals
Key risks are SR-IOV PF/VF register ownership, saved-register stride correctness, harvested-SA bit translation, and `halt()` timeouts. Test signals include GC 10.3 boot and reset, VF assignment, S0ix/mode2 cycles, harvested SKU boot, fault logging, and GPUVM invalidation after GFXOFF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.h

## Purpose
This header declares the GFXHUB 2.1 callback table used by GMC v10 for GC 10.3-generation devices.

## Important APIs, Types, and Functions
It exports `gfxhub_v2_1_funcs` as a `const struct amdgpu_gfxhub_funcs`. The table contains the standard VM hub callbacks and extra function pointers for UTCL2 harvest, mode2 register save/restore, and halt support.

## Control Flow and State
The header has no runtime behavior. Its symbol lets `gmc_v10_0_set_gfxhub_funcs()` bind GC 10.3 devices to the v2.1 implementation, which then persists VM hub register offsets and mode2 state in `adev->vmhub` and `adev->gmc`.

## Dependencies and Integration Points
Compilation depends on AMDGPU core type definitions being visible. Runtime integration is with GART enablement, GFXOFF/S0ix flows, VM faults, and hardware reset/harvest handling.

## Risks and Test Signals
Compile/link coverage validates the declaration. Runtime confidence comes from GC 10.3 board boot, reset, mode2 save/restore, VF operation, and UTCL2 harvest testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c

## Purpose
This file implements the GFXHUB 3.0 backend for GC 11 devices. It programs the newer `regGCVM_*` and `regGCMC_*` register namespace and exposes GFX VM hub callbacks for GMC v11.

## Important APIs, Types, and Functions
The public export is `gfxhub_v3_0_funcs`. It includes callbacks for FB base/offset discovery, VM page-table base writes, GART enable/disable, default fault handling, and VM hub initialization. Private VM hub functions create invalidate requests and print L2 protection fault status using the local `gfxhub_client_ids[]` table.

## Control Flow and State
The flow follows the modern GFXHUB pattern: `init()` seeds `adev->vmhub[AMDGPU_GFXHUB(0)]`; `gart_enable()` handles SR-IOV VF FB location programming, programs VMID0 GART page tables, system apertures, dummy/default fault pages, L1/L2 cache controls, context0, identity aperture disablement, contexts 1-15, and invalidate engine ranges. `set_fault_enable_default()` additionally sets `CP_DEBUG.CPG_UTCL1_ERROR_HALT_DISABLE` before applying L2 protection default bits, preventing CP halt on page faults. User contexts use `amdgpu_noretry` for retry policy rather than per-device `adev->gmc.noretry`.

## Dependencies and Integration Points
The file depends on GC 11.0.0 offset/mask/default headers, SOC15 helpers, and `navi10_enum.h`. `gmc_v11_0_set_gfxhub_funcs()` selects this implementation by default for GC 11 devices that do not require v3.0.3 or v11.5-specific tables.

## Risks and Test Signals
Risks include global retry-policy mismatch, CP debug side effects, SR-IOV register access, and incorrect context stride offsets. Test signals include GC 11 boot/resume, VM fault logging without CP halt, KFD retry/no-retry workloads, GFXOFF TLB invalidation, and VF boot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.h

## Purpose
This header declares the GFXHUB 3.0 callback table for GC 11-generation VM hub support.

## Important APIs, Types, and Functions
It exports `gfxhub_v3_0_funcs` as a `const struct amdgpu_gfxhub_funcs`. Consumers select it through generation-specific GMC setup, then use the callback table indirectly via `adev->gfxhub.funcs`.

## Control Flow and State
There is no executable flow in the header. Runtime state is created by the implementation when it initializes `adev->vmhub[AMDGPU_GFXHUB(0)]` and programs GCVM/GCMC registers.

## Dependencies and Integration Points
The header expects AMDGPU core type definitions to be available. It integrates with `gmc_v11_0.c`, fault handling, GART setup, and VM invalidation.

## Risks and Test Signals
Header risk is compile/link mismatch. Runtime test signals include GC 11 hardware initialization, GART enable log output, VM faults, and suspend/resume behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c

## Purpose
This file implements a GC 11.0.3-specific GFXHUB 3.0.3 backend. It is structurally similar to `gfxhub_v3_0.c` but uses GC 11.0.3 register headers and local default values for GCVM L2 controls.

## Important APIs, Types, and Functions
The public callback table is `gfxhub_v3_0_3_funcs`. It provides FB location/offset readers, VM page-table base programming, GART enable/disable, fault-default policy, and VM hub initialization. Private helpers produce invalidation requests and decode L2 protection faults.

## Control Flow and State
`gart_enable()` initializes VMID0 page-table base/range, system apertures, TLB and L2 cache controls, system-domain context, disabled identity aperture, contexts 1-15, and invalidate address ranges. SR-IOV VFs skip system aperture, cache, identity, and fault default writes that are PF-owned. Unlike v3.0, this file does not set the CP debug halt-disable bit in fault-default handling. `init()` records GC 11.0.3 register offsets, context/invalidation strides, fault interrupt masks, and the private `vmhub_funcs` table in `adev->vmhub`.

## Dependencies and Integration Points
The implementation depends on GC 11.0.3 offset/mask headers and SOC15 accessors. `gmc_v11_0_set_gfxhub_funcs()` selects it when GC IP version is `11.0.3`. GMC and VM code depend on the `vmhub_funcs` hooks for invalidation request encoding and fault decode.

## Risks and Test Signals
Risks are mostly generation-specific register drift, SR-IOV access assumptions, and differences from v3.0 fault behavior. Test signals include boot on GC 11.0.3 devices, GART enable/disable, VM fault decoding, VF operation, and reset/resume with TLB flushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.h

## Purpose
This header declares the GC 11.0.3-specific GFXHUB callback table.

## Important APIs, Types, and Functions
It exports `gfxhub_v3_0_3_funcs` as a `const struct amdgpu_gfxhub_funcs`. The table is selected by GMC v11 when the GC IP version requires GC 11.0.3 register programming.

## Control Flow and State
The header has no runtime flow. It enables linkage to the implementation that initializes `adev->vmhub` and hardware GCVM/GCMC registers.

## Dependencies and Integration Points
It depends on AMDGPU core type declarations in including files. Integration is with `gmc_v11_0.c`, VM fault processing, GART initialization, and reset/resume paths.

## Risks and Test Signals
Risks are compile/link mismatch and accidental selection for the wrong GC IP version. Tests should cover GC 11.0.3 boot, VM activity, and fault handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.h

## Purpose
This header declares the GMC v10 IP-function table and IP-block descriptor used to register GC 10 memory-controller support with the AMDGPU IP-block framework.

## Important APIs, Types, and Functions
It exports `gmc_v10_0_ip_funcs` (`struct amd_ip_funcs`) and `gmc_v10_0_ip_block` (`struct amdgpu_ip_block_version`). Callers add the block to the device during ASIC discovery rather than invoking the static implementation functions directly.

## Control Flow and State
No runtime flow exists in the header. The implementation behind the declarations manages lifecycle callbacks such as early/sw/hw init, suspend/resume, idle checks, clock gating, VM/GART setup, and IRQ handling.

## Dependencies and Integration Points
Including files need AMDGPU IP framework type declarations. Integration is with ASIC setup code that registers GMC v10 for applicable devices.

## Risks and Test Signals
Compile/link tests validate declarations. Runtime coverage comes from the `gmc_v10_0.c` lifecycle: boot, GART enable, page faults, ECC IRQs, and power management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.h

## Purpose
This header declares the GMC v11 IP functions and IP-block descriptor.

## Important APIs, Types, and Functions
It exports `gmc_v11_0_ip_funcs` and `gmc_v11_0_ip_block`. These connect the implementation to the AMDGPU IP-block framework for GC 11 devices.

## Control Flow and State
The header is declaration-only. The implementation manages VM/GART/RAS/IRQ lifecycle, MMHUB/GFXHUB function selection, memory placement, and power management.

## Dependencies and Integration Points
Including code needs AMDGPU IP framework type declarations. The declarations are consumed by ASIC setup paths that register the GMC v11 block.

## Risks and Test Signals
Compile/link coverage validates header correctness. Runtime testing should exercise the corresponding IP-block lifecycle on GC 11 devices, including page faults, KFD, GART, reset, and clock gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_0.h

## Purpose
This header declares the GMC v12 IP functions and IP-block descriptor.

## Important APIs, Types, and Functions
It exports `gmc_v12_0_ip_funcs` and `gmc_v12_0_ip_block`. These are the registration handles that expose GMC v12 lifecycle callbacks to the AMDGPU IP-block framework.

## Control Flow and State
The header is declaration-only. The implementation handles generation dispatch for v12.0/v12.1, VM/GART setup, IRQ handling, PDB0 allocation, and power management.

## Dependencies and Integration Points
Including code must have AMDGPU IP framework types in scope. ASIC setup code uses the exported IP-block descriptor to register GMC v12 support.

## Risks and Test Signals
Compile/link coverage catches header drift. Runtime validation belongs to `gmc_v12_0.c`: GC 12 boot, 12.1 helper dispatch, VM faults, GART/PDB0, and reset/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_1.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_1.h

## Purpose
This header declares the GC 12.1 GMC helper entry points consumed by the v12.0 IP block implementation.

## Important APIs, Types, and Functions
It declares `gmc_v12_1_set_gmc_funcs(struct amdgpu_device *adev)`, `gmc_v12_1_set_irq_funcs(struct amdgpu_device *adev)`, and `gmc_v12_1_init_vram_info(struct amdgpu_device *adev)`. These install v12.1-specific GMC and IRQ callback tables and seed default VRAM type/width.

## Control Flow and State
The header has no runtime flow. The implementation writes function pointers into `adev->gmc`, configures IRQ source function pointers, and initializes `adev->gmc.vram_type`/`vram_width`.

## Dependencies and Integration Points
It depends on `struct amdgpu_device` being visible in including files. `gmc_v12_0.c` includes it and calls the helpers when GC IP version is 12.1.0.

## Risks and Test Signals
The risk is mismatched helper signatures or failure to call them during v12.1 early init. Test signals include GC 12.1 boot selecting v12.1 callbacks, HBM4 metadata appearing in GMC state, retry-fault processing, and PASID TLB invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v12_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.c -->
