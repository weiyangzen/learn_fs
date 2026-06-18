# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.c

## Purpose
`amdgpu_gmc.c` implements common Graphics Memory Controller helpers. It computes VRAM/GART/AGP/sysvm address apertures, allocates and initializes VMID0 PDB0 for XGMI/sysvm cases, writes CPU-side PTE/PDE entries, filters retry VM faults, delegates recoverable faults, registers GMC-family RAS blocks, allocates VM invalidation engines, flushes GPU TLBs, selects TMZ and no-retry defaults, reserves stolen/VGA VRAM, exposes memory partition sysfs, and initializes partition memory ranges.

## Important APIs, types, and functions
Address and page-table helpers include `amdgpu_gmc_vram_location()`, `amdgpu_gmc_sysvm_location()`, `amdgpu_gmc_gart_location()`, `amdgpu_gmc_agp_location()`, `amdgpu_gmc_set_agp_default()`, `amdgpu_gmc_pdb0_alloc()`, `amdgpu_gmc_init_pdb0()`, `amdgpu_gmc_get_pde_for_bo()`, `amdgpu_gmc_pd_addr()`, `amdgpu_gmc_set_pte_pde()`, `amdgpu_gmc_vram_mc2pa()`, and `amdgpu_gmc_vram_pa()`. Fault/TLB paths are `amdgpu_gmc_filter_faults()`, `amdgpu_gmc_filter_faults_remove()`, `amdgpu_gmc_handle_retry_fault()`, `amdgpu_gmc_allocate_vm_inv_eng()`, `amdgpu_gmc_flush_gpu_tlb()`, `amdgpu_gmc_flush_gpu_tlb_pasid()`, and `amdgpu_gmc_fw_reg_write_reg_wait()`. Partition and sysfs helpers include `amdgpu_gmc_sysfs_init()`, `amdgpu_gmc_get_nps_memranges()`, `amdgpu_gmc_request_memory_partition()`, `amdgpu_gmc_prepare_nps_mode_change()`, and `amdgpu_gmc_init_mem_ranges()`.

## Control flow
Memory placement starts with VRAM/FB location, then GART and optional AGP apertures are fit into the MC address space while avoiding the VA hole and 4 GiB crossing constraints. Sysvm mode for XGMI uses hive-wide VRAM at low addresses and puts GART after aligned hive VRAM. PDB0 allocation creates pinned, CPU-mapped VRAM storage; initialization writes PDE0 entries directly as PTEs for hive VRAM and one PDE pointing to the GART PTB.

Retry fault handling first filters repeated faults by `(addr,pasid)` and IH timestamp unless retry CAM is enabled. Hardware faults can be delegated from the main IH ring to a secondary/software ring, then `amdgpu_vm_handle_fault()` attempts page-table recovery and writes the retry-CAM doorbell when required. Fault filter removal marks an expiry timestamp so a future fault on an address can be reprocessed after the current IH stream checkpoint.

TLB flush paths either call ASIC MMIO hooks under the reset-domain read lock or submit a small SDMA/IB workaround job for GART VMID0 invalidation. PASID flush can use direct GMC hooks or emit KIQ invalidation packets and wait on a polling fence. VM invalidation engines are assigned to rings from a reserved bitmap while excluding firmware/MES/UMSCH rings and sharing engines for selected SDMA page rings.

NPS sysfs parses requested partition modes, stores requests either in XGMI hive state or device state, and tells users to reload the driver. During unload/init preparation, the code asks XGMI/PSP/ASIC hooks to apply requested NPS changes. Memory ranges come from discovery tables where possible, are validated for count, ordering, and overlap, and otherwise fall back to software partitioning.

## State and persistence behavior
The file mutates `adev->gmc` runtime fields: aperture starts/ends/sizes, real/visible VRAM limits, PDB0 BO and CPU mapping, retry fault ring/hash, partition request and supported-mode fields, memory partition array, XGMI view, TMZ/no-retry flags, and reset flags. NPS requests can be stored in hive memory until driver reload, but no disk persistence is used. Sysfs nodes represent live driver state and requested hardware changes.

## Dependencies and integration points
GMC depends on TTM BOs/resources, VM manager fields, GART, IH timestamp decoding, KIQ/MES rings, SDMA workaround submission, RAS subblocks (UMC, MMHUB, HDP, MCA, XGMI), XGMI hive management, PSP memory partition calls, Atom firmware VRAM info, ACPI NUMA memory info, reset-domain synchronization, and ASIC-specific `gmc_funcs`/`vmhub_funcs`.

## Risks and edge cases
Address placement must not overlap VRAM/GART/AGP or the VA hole. XGMI/sysvm PDB0 calculations depend on node segment size, physical node id, and page-table block size. Retry fault filtering is timestamp-sensitive and can suppress legitimate retries if expiry handling is wrong. TLB flushes during reset intentionally skip work; callers must tolerate that. KIQ-based PASID flush can timeout. Partition range validation currently has TODOs for holes and invalid hardware reports. Sysfs memory partition writes only request a mode change and require reload, which can surprise callers.

## Test signals
Validate VRAM/GART/AGP placement on APUs, dGPUs, SR-IOV, and XGMI hives; PDB0 allocation/init; VM fault retry recovery and duplicate filtering; retry CAM doorbell writes; TLB flush via MMIO, SDMA workaround, and KIQ; VM invalidation engine allocation across ring mixes; RAS init ordering; TMZ/no-retry defaults per IP version; sysfs NPS show/store; discovery and fallback memory-range construction; and VRAM checking fault injection.
