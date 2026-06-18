# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_default.h lines 1-2930

## Purpose

This chunk is generated AMD Graphics Core 11.0.0 register reset/default metadata. It has no executable C logic; it publishes preprocessor constants named `reg..._DEFAULT` for hardware register reset values used by AMDGPU GC, SDMA, GFXHUB, MES, queue, VM, shader, render, and PF/VF setup code.

The requested range is the first 2,930 lines of a 6,114-line header. It starts at the file license and include guard, then covers these generated address blocks:

- Full `gc_sdma0_sdma0dec` and `gc_sdma0_sdma1dec` SDMA engine default families, including engine control/status, UTCL1, error, doorbell, queue, indirect-buffer, preemption, and mid-command registers for queues 0-7.
- GRBM, CP, PA, SQ, SHS/SPI, texture, GDS, RB, GCEA, PMM, UTCL1, GCVM shared/PF/VC, shader-program, graphics/compute queue, TCP, GDS partition, render-context, PF/VF, RMI, DIDT, SPI debug, and UTCL1 PF-only default blocks.
- The final visible line stops inside `gc_pfonly_utcl1dec` at `regGCRD_SA0_TARGETS_DISABLE_DEFAULT`; subsequent default blocks are outside this chunk and must be reconciled by neighboring chunk reports.

The chunk contains 2,793 `#define` lines. Most values are zero reset states; repeated non-zero defaults encode known hardware reset programming such as SDMA queue controls, VM context enables, L2 invalidation request defaults, MQD/HQD queue control defaults, GDS VMID sizes, raster configuration, RMI/UTC settings, DIDT EDC patterns, and PF/VF raster/binning defaults.

Although this source tree is under a `ceph-client` mirror, this file is AMDGPU kernel-driver hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocation paths, or direct register accesses in this chunk. The public interface is the generated macro namespace:

- `reg<REGISTER>_DEFAULT`: 32-bit numeric default/reset value for an MMIO register or register-backed queue/MQD field.
- Address-block comments such as `// addressBlock: gc_cpphqddec`: generated grouping hints that align defaults with matching offset and field-mask headers.

The macros are normally paired with:

- Register offsets from `gc_11_0_0_offset.h`, such as `regCP_HQD_PQ_CONTROL`, `regGCVM_L2_CNTL3`, `regSDMA0_QUEUE0_RB_CNTL`, and `regGCMC_VM_MX_L1_TLB_CNTL`.
- Bitfield definitions from `gc_11_0_0_sh_mask.h`, such as `CP_HQD_PQ_CONTROL`, `CP_GFX_HQD_CNTL`, `GCVM_L2_CNTL3`, and `CP_HQD_PERSISTENT_STATE` fields.
- AMDGPU helper macros and accessors including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and SOC15 register offset helpers.

High-value macro families in this range include:

- `regSDMA0_*_DEFAULT` and `regSDMA1_*_DEFAULT`: reset defaults for both SDMA engines. Queue defaults are repeated for queues 0-7; representative values include ring-buffer control `0x00040800`, indirect-buffer control `0x00000100`, context status `0x00000804`, AQL control `0x00004000`, and dummy register `0x0000000f`.
- `regCP_GFX_*_DEFAULT`: graphics queue MQD/HQD defaults, including `regCP_GFX_MQD_CONTROL_DEFAULT`, `regCP_GFX_HQD_VMID_DEFAULT`, `regCP_GFX_HQD_QUEUE_PRIORITY_DEFAULT`, `regCP_GFX_HQD_QUANTUM_DEFAULT`, `regCP_GFX_HQD_CNTL_DEFAULT`, `regCP_RB_DOORBELL_CONTROL_DEFAULT`, and pointer defaults.
- `regCP_HQD_*_DEFAULT`: compute/MES queue defaults, including `regCP_HQD_EOP_CONTROL_DEFAULT`, `regCP_HQD_PQ_CONTROL_DEFAULT`, `regCP_HQD_PERSISTENT_STATE_DEFAULT`, `regCP_HQD_IB_CONTROL_DEFAULT`, `regCP_HQD_EOP_RPTR_DEFAULT`, `regCP_HQD_EOP_WPTR_DEFAULT`, and HQ scheduler/status defaults.
- `regGCVM_*_DEFAULT` and `regGCMC_*_DEFAULT`: graphics VM and cache defaults for contexts 0-15, invalidation engines 0-17, page-table base/start/end address registers, per-PF/VF PTE cache fragment sizes, L2 cache controls, fault/default-page addresses, and system aperture/AGP registers.
- `regSPI_SHADER_*_DEFAULT` and `regCOMPUTE_*_DEFAULT`: shader program address/resource/user-data defaults for PS, GS/ESGS, HS/LSHS, compute, trap, accumulators, and request-control registers.
- `regDB_*`, `regPA_SC_*`, `regPA_CL_*`, `regCB_*`, and `regVGT_*`: render-context defaults for depth/stencil, scissor/viewport state, rasterization, VRS, primitive restart, color targets 0-7, DCC base extensions, blend constants, and context metadata.
- PF/VF and PF-only defaults such as `regCP_MEC_CNTL_DEFAULT`, `regCP_ME_CNTL_DEFAULT`, `regPA_SC_VRS_SURFACE_CNTL_DEFAULT`, `regRLC_SAFE_MODE_DEFAULT`, `regSQ_RUNTIME_CONFIG_DEFAULT`, `regDIDT_*_DEFAULT`, and `regUTCL1_*_DEFAULT`.

## Control Flow

This header has no local control flow. It affects runtime behavior when included code uses a generated default as a baseline, modifies selected fields, then writes the result into a hardware register or queue descriptor.

The clearest queue initialization flow is in GFX/MES code:

1. GFX v11 graphics MQD initialization starts from defaults such as `regCP_GFX_MQD_CONTROL_DEFAULT`, `regCP_GFX_HQD_VMID_DEFAULT`, `regCP_GFX_HQD_QUANTUM_DEFAULT`, `regCP_GFX_HQD_CNTL_DEFAULT`, and `regCP_RB_DOORBELL_CONTROL_DEFAULT`.
2. The driver applies runtime queue properties with `REG_SET_FIELD`, including VMID, privilege/cache policy, queue priority, ring-buffer size, TMZ, non-privileged mode, and doorbell offset/enabling.
3. The initialized MQD is copied to GPU-visible memory and restored from backup on reset/suspend paths.

Compute and MES queue setup follows the same pattern:

1. The driver zeros the MQD, fills fixed software fields, then derives EOP, MQD, HQD, read-pointer, write-pointer, and queue-base addresses from ring or queue properties.
2. It starts with defaults such as `regCP_HQD_EOP_CONTROL_DEFAULT`, `regCP_MQD_CONTROL_DEFAULT`, `regCP_HQD_PQ_CONTROL_DEFAULT`, `regCP_HQD_PQ_DOORBELL_CONTROL_DEFAULT`, `regCP_HQD_PERSISTENT_STATE_DEFAULT`, `regCP_HQD_IB_CONTROL_DEFAULT`, `regCP_HQD_IQ_TIMER_DEFAULT`, and `regCP_HQD_QUANTUM_DEFAULT`.
3. It overlays fields for queue size, RPTR block size, unordered/tunneled dispatch, KMD/private state, TMZ, doorbells, preload size, and minimum IB availability before activating the queue.

The VM/cache programming path uses the same default-as-template model:

1. GFXHUB initialization programs AGP/system-aperture/fault address registers from `adev->gmc`, scratch memory, and dummy page addresses.
2. It reads or starts from GCVM defaults, especially `regGCVM_L2_CNTL3_DEFAULT`, `regGCVM_L2_CNTL4_DEFAULT`, and `regGCVM_L2_CNTL5_DEFAULT`.
3. It sets cache-bank selection, fragment sizes, request mode, and small-page fragment fields before writing back with SOC15 helpers.

SDMA defaults in this chunk are also data inputs for ring/MQD programming. In this tree, SDMA v6 includes `gc_11_0_0_default.h`, and later SDMA code for newer generations mirrors some queue defaults as literals with comments referencing `regSDMA0_QUEUE0_RB_AQL_CNTL_DEFAULT` and `regSDMA0_QUEUE0_DUMMY_REG_DEFAULT`.

Render, shader, PF/VF, RMI, DIDT, and UTCL1 defaults do not impose ordering themselves. Actual sequencing is provided by surrounding GFX initialization, context programming, reset, power-management, SR-IOV PF/VF, KFD, and firmware/MES paths.

## State And Persistence Behavior

The header stores no software state and persists nothing on its own. It describes hardware reset/default state and default queue-descriptor field values.

Runtime persistence comes from consumers:

- MQD/HQD defaults become persistent GPU-visible queue descriptors in memory. GFX queue setup backs up MQDs in `adev->gfx.me.mqd_backup` and restores them across reset/suspend paths when appropriate.
- Doorbell defaults start disabled and are converted into active doorbell programming only when runtime queue properties request doorbells.
- VM defaults become live GCVM/GCMC MMIO state. Context enablement, page-table base/start/end, invalidation requests, fault addresses, and cache controls persist until GPU reset, suspend/resume reprogramming, VM hub reinitialization, or SR-IOV PF intervention changes them.
- Shader and render-context defaults represent reset state for graphics pipeline context registers. Command submission and context switching replace these defaults with per-draw, per-dispatch, or per-context state.
- SDMA queue defaults represent inactive queues with zeroed bases, pointers, doorbells, and CSA addresses until ring setup programs real buffers and writeback addresses.
- PF/VF-only defaults separate virtualization surfaces. VF-accessible defaults and PF-only defaults are not interchangeable; SR-IOV paths may leave some PF-only registers programmed by the host/PF rather than by guest driver code.

Most defaults are not evidence that a field is safe to rewrite at arbitrary times. Register side effects, read-only status, write-one-to-clear behavior, firmware ownership, and reserved-bit rules are defined by hardware documentation and by the associated driver sequencing code, not by this default header.

## Dependencies And Integration Points

This chunk must remain synchronized with AMD's generated GC 11.0.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h` for matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h` for matching field shifts and masks.
- SOC15/GFX/MES/GFXHUB register access infrastructure that consumes these macros through `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

Direct include sites observed in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c`

There are also closely related local copies of defaults in `gfx_v11_0.c`, `gfx_v12_0.c`, `gfx_v12_1.c`, and GFXHUB/MMHUB files. Those copies show the intended runtime use of this style of macro even where the generated header is not directly included in that translation unit.

Concrete consumers and behavior tied to macros in this chunk:

- `gfx_v11_0_gfx_mqd_init()` uses graphics queue defaults as baselines for MQD control, HQD VMID, quantum, HQD control, doorbell control, and read-pointer initialization.
- `gfx_v11_0_compute_mqd_init()` uses compute HQD defaults for EOP control, MQD control, PQ control, PQ doorbell control, PQ read pointer, persistent state, and IB control.
- `mes_v11_0_mqd_init()`, `mes_v12_0_mqd_init()`, and `mes_v12_1_mqd_init()` include this header and use compute HQD defaults for MES ring MQD construction.
- `gfxhub_v3_0.c` includes this header and uses `regGCVM_L2_CNTL3_DEFAULT`, `regGCVM_L2_CNTL4_DEFAULT`, and `regGCVM_L2_CNTL5_DEFAULT` while programming GC VM L2 cache behavior.
- `sdma_v6_0.c` includes this header for SDMA v6/GC 11 register defaults and offsets; SDMA queue setup depends on the same queue-control reset semantics represented here.

## Risks And Edge Cases

- The macros are untyped numeric constants. A wrong generated default compiles cleanly but can silently program an unsafe queue, VM, cache, render, or power/clock state.
- Defaults are often used as baselines before `REG_SET_FIELD`. If a reset value changes but copied local definitions or generated headers diverge, fields not explicitly overwritten may retain stale bits.
- Queue defaults are security- and stability-sensitive. Incorrect `CP_GFX_*` or `CP_HQD_*` defaults can break doorbells, write pointers, VMID assignment, KMD/private state, TMZ handling, EOP buffers, IB availability, or queue activation.
- VM defaults are fault-path critical. Bad `GCVM_CONTEXT*`, invalidation engine, L2 control, or fault-default address defaults can produce VM faults, stale TLB/cache state, page migration failures, or invalid memory accesses.
- SDMA defaults are heavily repeated. A single generation/copy error in one queue instance can affect only a subset of queues and be missed by single-ring smoke tests.
- Many register families are per-VMID, per-context, per-shader-stage, per-render-target, or per-invalidation-engine. Repetition makes off-by-one and partial-family updates easy during generated-header refreshes.
- PF/VF and PF-only defaults must be respected under SR-IOV. Programming a PF-owned register from a VF path may fail, be ignored, or violate virtualization assumptions.
- Some defaults include magic-looking non-zero values (`0x0be05501`, `0x00308509`, `0x02f80000`, `0x2a00126a`, RMI maps, DIDT stall patterns). These should be treated as generated hardware contract values, not simplified unless verified against the ASIC register database.
- This chunk is partial for the full file. It covers complete early blocks but stops inside `gc_pfonly_utcl1dec`; file-level conclusions must merge with later chunks.

## Test Signals

Useful validation is mostly build, hardware initialization, queue execution, and reset testing:

- Kernel build coverage with AMDGPU, GFXHUB, SDMA v6, MES v11/v12, GFX v11, and KFD enabled catches missing, renamed, or conflicting default macros.
- GFX ring and compute ring initialization should complete without MQD programming errors, doorbell failures, ring timeouts, or invalid queue activation after using `CP_GFX_*` and `CP_HQD_*` defaults as baselines.
- MES firmware queues should initialize and submit work successfully on GC 11/related ASICs; failures often surface as MES ring timeouts or queue map/unmap errors.
- VM/GART initialization should complete without GCVM protection faults, repeated TLB invalidation timeouts, or bad fault-default-address behavior.
- SDMA rings should pass copy/fill tests and suspend/resume/reset cycles with stable read/write pointer and doorbell behavior.
- Graphics workloads should exercise render-context defaults indirectly through clear, depth/stencil, color target, viewport/scissor, VRS, and shader-stage programming without hangs or corrupted output.
- SR-IOV validation should cover both PF and VF paths, ensuring PF-only defaults are not assumed writable by VF code.
- Reset, suspend/resume, and GPU recovery tests are important because defaults become most visible when queue descriptors and VM/cache state are rebuilt from reset baselines.
