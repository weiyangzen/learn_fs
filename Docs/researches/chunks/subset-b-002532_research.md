# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 14596-17258

## Purpose

This chunk is generated AMD GC 11.0.3 register bitfield metadata. It contains no executable C code; it exposes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD-adjacent paths, graphics hub setup, interrupt/error handling, command processor setup, and profiling/debug code to compose or decode MMIO register values for this ASIC generation. The matching register offsets are in `gc_11_0_3_offset.h`.

The selected range covers the tail of GCVM invalidation address-range fields, all 16 GCVM context page-table base/start/end address layouts, per-PF/VF PTE cache fragment sizing, several GCVM/ATC/L2/TLB performance-counter blocks, IOMMU and MARC translation controls, shader-program register layouts for PS/GS/HS/LS/ES stages, compute dispatch register layouts, and the beginning of command-processor queue/error control fields. Although this repository path is under `ceph-client`, this source is AMD GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, memory allocations, or direct I/O operations in this range. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for that field.
- Consumers combine these masks with `reg<REGISTER>` offsets from `gc_11_0_3_offset.h` and helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`.

Major register groups in this chunk:

- `GCVM_INVALIDATE_ENG1_ADDR_RANGE_*` through `GCVM_INVALIDATE_ENG17_ADDR_RANGE_*`: per-invalidation-engine low/high logical page range fields. The low word carries an `S_BIT` and low logical-page bits; the high word carries upper logical-page bits. The chunk starts in the middle of the engine 1 low-word definition, while engine 0 and the first engine 1 fields are in the preceding chunk.
- `GCVM_CONTEXT0_*` through `GCVM_CONTEXT15_*`: page-table base, start, and end address fields for each VM context. Base registers split the 64-bit page-directory-entry address into low/high words; start/end registers split logical page numbers into low 32 bits plus a small high field.
- `GCVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` and `GCVM_L2_CONTEXT*_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES`: PTE cache fragment-size controls, with small-fragment, big-fragment, and bank-select fields per context.
- `GCVML2_*`, `GCMC_VM_L2_*`, `GCUTCL2_*`, `GC_ATC_L2_*`, and `GCL2TLB_*` performance-counter registers: counter low/high readback, event selection, mode, per-counter configuration, and result-control fields for GCVM L2, UTCL2, ATC L2, and L2 TLB monitor blocks.
- `GCUTCL2_TRANSLATION_BYPASS_BY_VMID`, `GCVM_IOMMU_*`, `GCUTC_GPUVA_VMID_TRANSLATION_ASSIST_CNTL`, and `GCUTC_TRANSLATION_FAULT_CNTL*`: translation bypass, GPU-host translation enable, IOMMU enable and optimization knobs, MMIO control, GPUVA/VMID translation-assist controls, and default translation-fault physical-page attributes.
- `GCMC_VM_MARC_BASE_*`, `GCMC_VM_MARC_RELOC_*`, `GCMC_VM_MARC_LEN_*`, and `GCMC_VM_MARC_PFVF_MAPPING_*`: MARC aperture base, relocation, length, and PF/VF enable mapping fields for up to 16 windows.
- `SPI_SHADER_*_PS`, `SPI_SHADER_*_GS`, `SPI_SHADER_*_HS`, `SPI_SHADER_PGM_LO/HI_ES`, and `SPI_SHADER_PGM_LO/HI_LS`: graphics shader program resource, checksum, program-address, user-data, request-control, accumulator, and meshlet fields. Resource fields include CU enable masks, VGPR/SGPR sizing, priority, floating-point mode, privilege/debug/trap bits, LDS sizing, exception enables, shared VGPR count, and stage-specific controls.
- `COMPUTE_*`: compute dispatch packet and state fields, including dispatch initiator flags, dimensions, starts/restarts, thread counts, pipeline/perfcount enable, program address, AQL dispatch packet address, scratch base, program resource fields, VMID, resource limits, destination/static thread management by shader engine, temp-ring size, trace enable, dispatch IDs, relaunch payloads, wave restore addresses, user data, dispatch tunnel/end, and reserved scratch registers.
- `CP_CU_MASK_*`, `CP_EOPQ_WAIT_TIME`, `CP_CPC_MGCG_SYNC_CNTL`, `CPC_INT_*`, `CP_VIRT_STATUS`, `CP_GFX_ERROR`, `CP{G,C,F}_UTCL1_CNTL`, `CP_AQL_SMM_STATUS`, `CP_RB0_BASE`, `CP_RB_BASE`, and the beginning of `CP_RB0_CNTL`: command processor compute-unit mask programming, EOP queue wait timing, CPC clock-gating sync timing, interrupt address/PASID/VMID payload fields, virtualization status, UTCL1 error bits, UTCL1 control bits, AQL SMM status, ring-buffer base addresses, and initial ring-buffer control fields.

Fields named `RESERVED`, `SH_RESERVED_REG*`, or full-width `DATA` are still part of the generated register contract. They are not evidence that whole-register writes are safe; consumers need hardware-guide context and should preserve undocumented bits unless reset-value programming explicitly requires otherwise.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from driver code that includes it:

1. A GC 11.0.3 consumer includes `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h`.
2. The consumer selects a `reg*` address macro, sometimes using an offset stride for per-VMID or per-engine register arrays.
3. The consumer composes or decodes values with the shift/mask macros.
4. AMDGPU register helpers perform the actual MMIO access while the relevant block initialization, queue setup, VM update, profiling, interrupt, reset, or power-management sequence owns ordering.

Concrete examples in this tree include `gfxhub_v3_0_3_setup_vm_pt_regs()`, which writes `regGCVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` with per-VMID offsets, and `gfxhub_v3_0_3_init()`, which derives context and invalidation-engine strides from generated offsets. Generic GFX 11 ring setup code programs `CP_RB0_CNTL` with `REG_SET_FIELD(..., CP_RB0_CNTL, RB_BUFSZ, ...)` and `RB_BLKSZ`, illustrating how this mask namespace is consumed with SOC15 register helpers.

The chunk describes fields needed for GPU VM setup, translation fault behavior, performance-counter programming, shader-stage and compute-dispatch state, and CP queue/error handling. It does not encode legal access order, read-only versus write-only behavior, self-clearing semantics, power-gating requirements, firmware ownership, or reset sequencing.

## State And Persistence Behavior

The file stores no software state and persists nothing. It only names hardware state exposed through GC 11.0.3 registers.

The represented hardware state is broad:

- GCVM context state includes per-VMID page-table root addresses and valid logical address ranges.
- GCVM invalidation state includes per-engine logical-page ranges for targeted TLB/cache invalidation.
- L2, ATC, UTCL2, and TLB performance-counter state includes event selection, modes, configuration, result control, and counter readback values.
- Translation and virtualization state includes VMID bypass masks, GPU-host translation enable, IOMMU enable/optimization/MMIO settings, translation-assist control, default translation-fault page attributes, and MARC aperture mapping for PF/VF access.
- Shader state includes program addresses, resource descriptors, checksums, user SGPR payloads, accumulators, request controls, trap/debug/exception bits, meshlet layout fields, and stage-specific resource sizing for graphics shader stages.
- Compute state includes dispatch dimensions, workgroup/thread counts, shader program/scratch addresses, program resources, VMID, SE/CU targeting, static thread-management masks, temp-ring size, trace controls, relaunch and restore state, and user-data payloads.
- Command-processor state includes CU mask address/policy, EOP wait timing, CPC clock-gating sync timing, interrupt address/PASID metadata, graphics error status bits, UTCL1 control knobs, AQL SMM status, and ring-buffer base/control fields.

Persistence is hardware-defined. Some fields are programmed configuration that should survive until GPU reset, suspend/resume, power-gating, or reinitialization; others are live status, performance counters, interrupt payloads, error latches, or write-trigger controls. The masks alone do not identify volatility or side effects, so driver code must use ASIC-specific sequencing and preserve unrelated bits.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which provides matching `reg*` offsets and address-block placement. For this chunk, relevant address blocks include GCVM/L2 performance and PSP-facing translation blocks, `gc_shdec` shader registers, and the beginning of `gc_cppdec` command-processor registers.

GC 11.0.3-specific include users observed in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`

Integration points include GFXHUB v3.0.3 GART/aperture setup, per-VMID page-table programming, TLB invalidation, VM fault handling, SR-IOV/PF-VF translation aperture setup, GPU-host/IOMMU translation controls, profiling through GCVM/ATC/TLB counters, shader program setup through PM4 packets or firmware-owned programming, compute dispatch packet construction, command-processor ring initialization, CP graphics error reporting, UTCL1 control, GPU reset/recovery, suspend/resume, and golden-register initialization through IMU/RLC tables.

## Risks And Edge Cases

- Header/offset mismatches are the largest correctness risk. These GC 11.0.3 masks must be paired with `gc_11_0_3_offset.h`; using a different GC generation can compile while programming the wrong bits.
- The chunk boundary is artificial. It starts after part of `GCVM_INVALIDATE_ENG1_ADDR_RANGE_LO32` and ends before the `CP_RB0_CNTL` mask definitions, so adjacent chunks are required for complete per-register coverage.
- These macros are untyped constants. Wrong field/register pairing can silently corrupt VM context state, shader resource descriptors, compute dispatch behavior, CP queue setup, or performance-counter configuration.
- VM page-table and invalidation fields are security and isolation sensitive. Incorrect start/end/base values, PF/VF mappings, bypass masks, IOMMU enablement, or translation-fault defaults can expose memory, fault valid workloads, or mask real GPU faults.
- Many address fields are split low/high and use page-number alignment rather than raw byte addresses. Consumers must shift GPU addresses consistently and avoid truncating high bits.
- Repeated per-context and per-MARC-window registers make indexing errors easy. Off-by-one VMID/window strides can modify another process, VM context, or VF mapping.
- Performance-counter select/config fields can perturb profiling state or produce misleading diagnostics if programmed while counters are running or without clearing/latched-read sequencing.
- Shader and compute resource fields encode compiler/ABI contracts. Incorrect VGPR/SGPR counts, LDS size, user SGPR count, trap/exception/debug bits, wave limit, WGP mode, or CU enable masks can cause hangs, invalid execution, lost traps, or bad debug data.
- `COMPUTE_DISPATCH_INITIATOR` includes cache invalidation, restore, tunnel, wave32, AMP shader, and preemption-related controls. Blindly carrying assumptions from older GC families is risky because this GC 11.0.3 layout differs from earlier headers.
- CP ring-buffer control mixes sizing, trusted-memory-zone state, privilege, cache policy, execution, KMD queue, and read-pointer writeback enable fields. Whole-register writes can disable queues, break writeback, or change security attributes.
- Error/status registers such as `CP_GFX_ERROR` and counter readbacks may be sticky, live, or clear-on-read/write depending on the block; the generated masks do not document side effects.
- Reserved/full-width fields should not be fabricated into writes without hardware-guide reset values.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware smoke/stress coverage:

- Build AMDGPU paths that include `gc_11_0_3_sh_mask.h`, especially `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`.
- Generated-header consistency checks that each field has aligned shift/mask pairs, repeated per-context/per-engine/per-window layouts are regular, and registers in this chunk have matching `reg*` entries in `gc_11_0_3_offset.h`.
- GFXHUB tests that initialize GART and per-VMID page tables, validate base/start/end programming, issue VM invalidations, and confirm expected page-fault reporting under valid and invalid GPUVA accesses.
- SR-IOV and virtualization tests that exercise PF/VF MARC mappings, VMID bypass masks, translation-assist controls, and IOMMU/GPU-host translation enable paths without cross-VM leakage.
- Performance-counter tests that program GCVM L2, UTCL2, ATC L2, and L2 TLB counter select/config/mode registers, run known memory workloads, and verify low/high counter readback changes plausibly.
- Shader and compute dispatch smoke tests covering graphics pipeline creation, trap/debug modes, wave32/64 compute dispatch, scratch/user-data programming, threadgroup dimensions, restart/relaunch state, and thread trace enablement.
- CP queue tests that bring up the graphics ring, verify ring base/read-pointer/write-pointer behavior, exercise KMD and privilege/security settings where applicable, and confirm CP error bits stay clear under normal workloads.
- Suspend/resume, runtime power management, GPU reset, and recovery tests while VM contexts, counters, shader dispatch, and CP queues are active.
- Regression indicators include page faults on valid mappings, missing faults on invalid mappings, corrupted VMID context roots, stuck invalidation acknowledgements, zero or saturated perf counters, shader dispatch hangs, lost trap/debug behavior, CP ring timeouts, unexpected `CP_GFX_ERROR` bits, and failures isolated to GC 11.0.3-class hardware.
