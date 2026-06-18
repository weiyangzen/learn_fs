# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 7582-10044

## Scope

This chunk is a generated AMD GC 12.0.0 shift/mask header slice. It contains C preprocessor `#define` constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro. There are no functions, structs, enums, global variables, allocations, locks, MMIO operations, or executable branches in this range.

The selected lines contain 2,148 `#define` statements. The chunk starts in the middle of `COMPUTE_REQ_CTRL`, continues through compute shader dispatch and user-data fields, then covers RAS signature state, PF-only GC current/activity counter and throttle controls, EA/SDP fabric controls, GCR/PMM controls, GCUTCL2 shared VM aperture controls, GCVM L2 translation-cache and protection-fault controls, GCVM context control registers for contexts 0-15, and the beginning of the GCVM invalidate-engine semaphore family. It ends at `GCVM_INVALIDATE_ENG2_SEM`, so the remainder of the invalidate-engine register family is in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_12_0_0_sh_mask.h` gives GC 12.0.0 AMDGPU code the bit positions and masks needed to compose, update, and decode graphics-core registers without embedding raw bit constants in driver code. Consumers pair these field definitions with register offsets from `gc_12_0_0_offset.h` and access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and RLC/golden-register table macros.

This chunk covers these hardware surfaces:

- Compute queue and dispatch state: request throttling in `COMPUTE_REQ_CTRL`, CU enable masks for static thread management, user accumulators, program resource field 3, dispatch interleave, relaunch payload/state flags, wave restore address, prescaled dimensions, 16 compute user-data registers, dispatch tunnel/end markers, and reserved shader registers.
- RAS and power telemetry: `RAS_GE_SIGNATURE0` plus GC CAC aggregation, per-SE aggregation, EDC/DIDT/PCC/PWRBRK throttle controls, status, overflow, rolling-power, clock-monitor, soft snapshot, indirect index/data, and per-block weighting fields.
- EA/SDP fabric controls for CPWD and SE paths: VC mapping, arbitration, priority, tag and credit reserve registers, request controls, miscellaneous/error fields, backdoor credit programming, and enable bits.
- GCR and PMM controls: `GCR_PIO_CNTL`, `GCR_PIO_DATA`, `PMM_CNTL`, and `PMM_STATUS`.
- GCUTCL2/GCMC shared virtual-memory controls: MMIO aperture, PCI, top-of-DRAM, framebuffer offset/location, system aperture defaults, steering, shared virtual reset, cacheable/local sysmem/local framebuffer ranges, local-FB locking, clock-gating controls, active function ID, harvest bypass, and group fault status.
- GCVM L2 and context controls: L2 cache/TLB configuration, invalidation controls, protection fault defaults and status decode, identity aperture registers, bank/partition controls, parity controls, clock-gating controls, GCR integration, walker throttling, PTE cache dump fields, GPUVA VMID translation-assist request/response fields, credit-safety controls, contexts 0-15 enable/page-table/fault-policy fields, context disable bits, and the first invalidate-engine semaphore bits.

## Important APIs, Types, And Macros

The only interface in this chunk is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit index for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the register-width mask for the same field.
- `// addressBlock:` comments identify the generated hardware address block that owns the following register fields.
- Plain `//<REGISTER>` comments group the field macros by register.

There are no callable APIs or C types here. Important macro families include:

- `COMPUTE_*`: shader/compute dispatch and queue fields, especially `COMPUTE_STATIC_THREAD_MGMT_SE4..SE8`, `COMPUTE_PGM_RSRC3`, `COMPUTE_RELAUNCH*`, `COMPUTE_WAVE_RESTORE_ADDR_*`, `COMPUTE_PRESCALED_DIM_*`, and `COMPUTE_USER_DATA_0..15`.
- `GC_CAC_*`, `SE*_CAC_*`, `GC_EDC_*`, `GC_THROTTLE_*`, `DIDT_*`, `PCC_*`, and `PWRBRK_*`: current/activity counting, power estimation, hysteresis, throttle pattern, status, performance counter, and weighting fields.
- `GC_EA_CPWD_*` and `GC_EA_SE_*`: EA fabric virtual-channel, credit, priority, arbitration, request-control, backdoor, error, and enable fields.
- `GCMC_VM_*`, `GCUTCL2_*`, `GCVM_L2_*`, and `GCUTC_GPUVA_*`: graphics hub aperture, L1/L2 VM cache, translation, fault, invalidate, parity, clock-gating, and translation-assist fields.
- `GCVM_CONTEXT0_CNTL` through `GCVM_CONTEXT15_CNTL`: repeated per-VMID context controls for enabling a context, page-table depth/block size, retry behavior, and interrupt/default handling of range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `GCVM_CONTEXTS_DISABLE` and `GCVM_INVALIDATE_ENG0_SEM..ENG2_SEM`: context disable and invalidate engine semaphore fields at the chunk boundary.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic bit positions and masks into driver code.

The implied runtime flow is:

1. A GC 12.0.0 driver path selects a register offset from `gc_12_0_0_offset.h` and field macros from this header.
2. The driver composes or extracts a value with `REG_SET_FIELD`, `REG_GET_FIELD`, explicit shifts, or masks.
3. The value is written to or read from the GPU through SOC15 MMIO helpers, RLC-safe helpers, indirect GC CAC helpers, IMU/RLC golden initialization tables, queue descriptor setup, or KFD queue-management code.
4. The hardware block applies the resulting state to dispatch scheduling, queue descriptors, VM translation, cache invalidation, fault reporting, throttling, power telemetry, or fabric credit behavior.

Observed consumers in this tree include `gfxhub_v12_0.c`, which programs `GCVM_L2_CNTL*`, context controls, protection fault defaults/status, and invalidate request/ack/semaphore spacing; `imu_v12_0.c`, which uses GC 12 golden values for EA/SDP and GCVM setup; KFD MQD code for compute queue descriptors; and the v12.1 device queue manager, which toggles `GCVM_CONTEXT0_CNTL__RETRY_PERMISSION_OR_INVALID_PAGE_FAULT__SHIFT` for XNACK behavior.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists in the GPU registers or in memory descriptors interpreted by the GPU.

The represented hardware state includes compute dispatch inputs, CU selection masks, user SGPR payloads, shader program resource flags, relaunch/wave-restore state, RAS signatures, CAC/EDC/DIDT/PCC/PWRBRK counters and throttle policy, EA fabric credit allocation, GCR/PMM status, VM aperture/range configuration, GCVM L2 cache behavior, fault-default and fault-status registers, identity aperture mappings, translation-assist request/response state, per-context translation and fault policy, and invalidate engine semaphores.

Many of these registers persist until rewritten, GPU reset, graphics hub reinitialization, queue teardown/reload, VM context reprogramming, suspend/resume restore, clock/power-gating loss, or PF-level management intervention. Others are counters, status latches, command bits, self-clearing controls, or clear-on-write status fields. This generated header does not encode access permissions, reset values, polling requirements, clear semantics, or required ordering; those rules live in hardware documentation and in the sequencing of the AMDGPU/KFD consumers.

## Dependencies And Integration Points

This chunk depends on the GC 12.0.0 register set remaining synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_offset.h` supplies matching register offsets for the fields named here.
- AMDGPU field helpers in the broader driver expect each `__SHIFT`/`_MASK` pair to match the hardware bit layout.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c` uses the GCVM field macros for cache setup, context setup, fault decoding, invalidate request construction, aperture setup, and hub spacing calculations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v12_0.c` includes this header and programs golden values for `GC_EA_CPWD_*`, `GC_EA_SE_*`, and `GCVM_L2_*` registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v12.c` includes this header for compute queue descriptor fields such as HQD, CP, and compute state macros, with this chunk contributing compute static-thread and shader-resource field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v12.c` includes this header for queue-manager setup, and the adjacent v12.1 implementation shows the same GCVM context retry bit pattern for XNACK.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc24.c`, `mes_v12_0.c`, `sdma_v7_0.c`, `gfx_v12_0.c`, and `amdgpu_amdkfd_gfx_v12.c` include this generated header as part of GC 12 platform integration.
- `amdgpu_reg_gc_cac_rd32`/`amdgpu_reg_gc_cac_wr32`, exposed through `RREG32_GC_CAC` and `WREG32_GC_CAC`, integrate with the `GC_CAC_IND_INDEX`/`GC_CAC_IND_DATA` indirect register access pattern.

Runtime integration points include graphics hub initialization, VMID/context programming, page-table setup, GPUVM invalidation, page-fault reporting, retry/XNACK policy, KFD process queue state, compute CU masking, IMU/RLC golden-register programming, SR-IOV PF/VF aperture and active function handling, throttling/power telemetry, and diagnostic register dumps.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong bit shift or mask compiles cleanly but causes driver writes to modify the wrong hardware bits or driver reads to decode fault/status fields incorrectly.
- The chunk starts mid-register at `COMPUTE_REQ_CTRL`; the first fields of that register are in the previous chunk. Any per-register review must merge both chunks before treating `COMPUTE_REQ_CTRL` coverage as complete.
- The chunk ends mid-family at `GCVM_INVALIDATE_ENG2_SEM`; later invalidate engine semaphores, requests, acknowledgements, and address ranges continue in following lines/chunks.
- Repeated fields are easy to mis-index. The per-SE compute masks, 16 compute user-data registers, SE0-SE3 CAC aggregators, multiple CAC weight tables, GCVM contexts 0-15, and invalidate engines rely on stable numbering and identical field layouts.
- GCVM context bit positions are security and reliability sensitive. Incorrect retry/default/interrupt bits can convert recoverable VM faults into hangs, hide page faults, disable fault interrupts, or break XNACK behavior.
- `GCVM_L2_PROTECTION_FAULT_STATUS_LO32` decoding is user-visible during GPU fault reporting. Incorrect `CID`, `VMID`, `VF/VFID`, `PRT`, `UCE`, permission, mapping, or read/write fields can mislead debugging and automated recovery.
- Cache and invalidate fields have ordering-sensitive behavior. Incorrect `GCVM_L2_CNTL*`, `GCVM_INVALIDATE_CNTL`, or invalidate semaphore/request/ack fields can leave stale PTE/PDE data, trigger intermittent VM faults, or stall the graphics hub.
- PF-only CAC/EDC/DIDT/PWRBRK controls affect power, throttling, and reliability telemetry. Exposing or programming them incorrectly can affect virtualization isolation, performance, thermal behavior, or fault evidence.
- EA/SDP credit and priority fields are fabric-performance sensitive. Bad masks for tag/credit reserves or VC mapping can produce deadlock-like stalls, traffic starvation, or performance cliffs.
- Some registers are status, latch, clear, or self-clearing command registers, but this file only describes bit layout. Consumers must not infer read/write safety from the existence of a mask.
- Nearby GC 12.1 and older GC headers use similar names but may not share identical layouts. Cross-generation code must include the correct ASIC-specific header.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU/KFD configurations that include GC 12.0.0 support. Missing or malformed macros should surface in `gfxhub_v12_0.c`, `imu_v12_0.c`, `gfx_v12_0.c`, KFD MQD/queue manager code, MES, SDMA, and SOC24 integration.
- Mechanically compare every shift and mask in this chunk against AMD's authoritative GC 12.0.0 register database.
- Cross-check that every field family here has matching register offsets in `gc_12_0_0_offset.h`, especially chunk-boundary families such as `COMPUTE_REQ_CTRL` and `GCVM_INVALIDATE_ENG*`.
- Verify repeated-family consistency for `COMPUTE_USER_DATA_0..15`, `COMPUTE_STATIC_THREAD_MGMT_SE4..SE8`, CAC weight groups, `GCVM_CONTEXT0_CNTL..GCVM_CONTEXT15_CNTL`, and invalidate engine semaphores.
- Exercise GC 12 graphics hub initialization and teardown, checking that `GCVM_L2_CNTL*`, context controls, system aperture, default fault address, and identity aperture programming match expected register dumps.
- Exercise GPUVM invalidation under graphics, compute, SDMA, and KFD workloads while watching invalidate semaphores, request/ack progress, page-table update visibility, and absence of stale PTE/PDE faults.
- Trigger or inject VM faults where possible and confirm `GCVM_L2_PROTECTION_FAULT_STATUS_*` decoding reports the expected client ID, VMID, access type, VF/VFID, PRT, and UCE state.
- Run KFD compute queues with CU masks, debugger/CWSR paths, user-data payloads, and XNACK on/off process settings to validate compute and GCVM context fields.
- Run IMU/RLC golden-setting initialization and compare EA/SDP and GCVM programmed values against reference hardware traces.
- In SR-IOV configurations, validate PF/VF behavior around shared aperture registers, active function ID fields, PF-only CAC/throttle controls, and fault reporting isolation.
- Monitor power/throttle telemetry under high-load workloads to catch regressions in CAC/EDC/DIDT/PCC/PWRBRK status, counters, hysteresis, and throttle pattern fields.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002572`. The final per-file research should merge it with neighboring chunks for complete `gc_12_0_0_sh_mask.h` coverage. The previous chunk owns the beginning of `COMPUTE_REQ_CTRL`, while the next chunk continues the GCVM invalidate-engine register family after `GCVM_INVALIDATE_ENG2_SEM`.
