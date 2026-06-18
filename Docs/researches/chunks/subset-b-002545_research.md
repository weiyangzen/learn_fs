# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 2548-5018

## Scope

This chunk is a generated AMD GC 11.5.0 register-offset header segment. It contains C preprocessor constants only: `reg...` symbols map named GPU registers to SOC15 register offsets, and each register has a matching `..._BASE_IDX` symbol that selects the SOC15 base index used by AMDGPU register helpers. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines start in the tail of a GC UTCL2 performance-counter address block from the previous chunk, then cover GC ATC L2 and GCL2 TLB performance counter controls, GCVM/IOMMU/translation-fault controls, a large shader/compute (`gc_shdec`) block, command-processor (`gc_cppdec`) registers, SPI arbitration and compute debug controls, CP HQD/MQD queue registers, TCP watchpoint registers, GDS per-VMID resource registers, RAS signature registers, a large graphics context-state block (`gc_gfxdec0`), and the start of a PF/VF CP block. The chunk ends at the `gc_pfvf_grbmdec` address-block marker; its registers continue in the next adjacent chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for AMD graphics IP and is not Ceph filesystem code.

## Purpose

`gc_11_5_0_offset.h` provides compile-time register offsets for the GC 11.5.0 graphics IP. Driver code pairs these offsets with field layouts from `gc_11_5_0_sh_mask.h` and access helpers such as `SOC15_REG_OFFSET`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `RREG32_SOC15`, and command-stream packet builders. The header removes hard-coded register numbers from initialization, queue setup, debugging, power/reset, performance monitoring, virtualization, KFD compute, and graphics context programming paths.

This chunk is centered on active GPU execution state rather than passive metadata:

- GC L2/ATC/TLB performance counter selection, configuration, and result-control offsets.
- GCVM/IOMMU and translation-fault controls for ATS, host translation, bypass-by-VMID, fault handling, and GPUVA VMID translation assistance.
- Shader-program and user-data register windows for pixel, geometry, hull, local, export, and compute shader stages.
- Compute-dispatch state including dimensions, start coordinates, thread-group sizes, shader program addresses, scratch bases, VMID, resource limits, wave relaunch/restore, DDID, accumulators, and user data.
- Command-processor ring, doorbell, interrupt, priority, VMID, queue, context, suspend/resume, DDID, debug, watchpoint, timestamp, UTCL1, and soft-reset offsets.
- CP HQD/MQD queue programming offsets for packet queues, indirect buffers, doorbells, EOP queues, AQL, context-save areas, GDS resource state, and dequeue/status controls.
- Texture cache watchpoint registers, GDS allocation and context-switch counters, RAS signature controls, and graphics pipeline context registers for depth/stencil, scissors, viewport state, VRS, VGT, PA/CL/SU/SC, CB, DB, SX, and render-target programming.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `regNAME` gives the register offset value used by SOC15 register helpers.
- `regNAME_BASE_IDX` gives the base-index selector for the register aperture. In this chunk shader/CP/HQD/GDS/RAS blocks mostly use base index `0`, while GCVM, graphics context, and PF/VF blocks use base index `1`.
- Field shifts and masks are intentionally absent here; callers must use the matching `gc_11_5_0_sh_mask.h` definitions when setting or decoding bitfields.

The main macro families in this slice are:

- `GC_ATC_L2_*`, `GCL2TLB_*`, and `GCUTCL2_*`: performance counter selectors, modes, config registers, and result controls for L2 address translation and TLB paths.
- `GCVM_*` and `GCUTC_*`: PCIe ATS control, IOMMU host translation enable/control/performance tuning, per-VMID translation bypass, translation-fault controls, and GPUVA VMID translation-assist controls.
- `SPI_SHADER_*`: program address low/high registers, program resource registers, checksums, 32 user-data slots, request controls, and four user accumulators for PS, GS/ES-GS, HS/LS-HS, ES, and LS shader stages. Some entries provide stage-pair addresses such as `SPI_SHADER_PGM_LO_ES_GS` and `SPI_SHADER_PGM_LO_LS_HS`.
- `COMPUTE_*`: dispatch initiator, grid dimensions, start positions, thread counts, pipeline/perf enables, compute program address/resources, VMID, resource limits, static thread-management aliases, restart/relaunch controls, wave-restore address, dispatch IDs, DDID registers, and 16 compute user-data slots.
- `CP_*`, `CPC_*`, `CPF_*`, and `CPG_*` in `gc_cppdec`: command-processor ring state, interrupt/status/priority controls, doorbell ranges, UTCL1 controls and errors, ECC/EDC/debug registers, per-ME pipe interrupt/priority registers, firmware program-counter starts, context controls, suspend/resume save areas, DDID state, graphics HQD state, DMA watchpoints, timestamps, SDMA command-stream handoff, GCR/UTCL1 status, and soft-reset controls.
- `SPI_ARB_*`, `SPI_WCL_PIPE_PERCENT_*`, `SPI_USER_ACCUM_VMID_CNTL`, `SPI_GDBG_PER_VMID_CNTL`, `SPI_COMPUTE_QUEUE_RESET`, and `SPI_COMPUTE_WF_CTX_SAVE`: arbitration, wave-control/pipe percentage, per-VMID debug/accounting, compute queue reset, and wavefront context-save hooks.
- `CP_HQD_*`, `CP_MQD_*`, and `CP_HPD_*`: hardware queue descriptor and memory queue descriptor offsets for compute queues. These cover MQD base, active/VMID/priority/quantum, PQ base/read/write pointers, write-pointer polling, doorbell control, indirect-buffer state, dequeue/offload/semaphore/message/atomic registers, scheduler/status/control aliases, EOP queues, context-save areas, suspend state, GDS resource state, AQL control, DDID accounting, and dequeue status.
- `TCP_WATCH*`: four texture/cache watchpoint address/control triplets.
- `GDS_*`: per-VMID GDS base/size, GWS ownership, ordered-append ownership, reset masks, compute max wave ID, CS/GFX/PS/GS context-switch counters, and memory-clean indication.
- `RAS_*`: signature control/mask and block-specific signature registers for SX, DB, PA, SC, SPI, CB, and BCI.
- `DB_*`, `PA_*`, `VGT_*`, `CB_*`, `SX_*`, `TA_*`, `COHER_*`, and `CONTEXT_*` in `gc_gfxdec0`: graphics context registers for depth/stencil targets, HTILE, scissor/clip rectangles, viewport scissor/Z ranges and transforms, user clip planes, primitive assembly, rasterization, VRS feedback/rate images, blend constants, color/depth/stencil controls, shader export controls, and eight color render targets with base/view/info/attrib/FDCC/DCC/base-extension registers.
- `CONFIG_RESERVED_REG*`, `CP_MEC_CNTL`, and `CP_ME_CNTL` in `gc_pfvf_cpdec`: PF/VF-visible command-processor controls at the end of this chunk.

Several symbols intentionally alias the same offset for compatibility with different naming paths. Examples include `COMPUTE_DESTINATION_EN_SE*` and `COMPUTE_STATIC_THREAD_MGMT_SE*`, `CP_RB0_*` and `CP_RB_*`, `CP_ME0_PIPE*` and `CP_RING*`, `CP_HQD_DMA_OFFLOAD` and `CP_HQD_OFFLOAD`, `CP_HQD_HQ_SCHEDULER*` and `CP_HQD_HQ_STATUS/CONTROL*`, `CP_PIPEID` and `CP_RINGID`, and `CP_DDID_*`/`CPC_DDID_*`. Consumers must treat these as alternate names for one hardware address, not independent registers.

## Control Flow

This header has no runtime control flow. Its behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU is:

1. Select the GC 11.5.0 generated header for the active ASIC/IP version.
2. Use a `reg...` macro with SOC15 helpers to compute the MMIO or packet register address for the selected GC instance/base index.
3. Optionally combine the offset with field masks from `gc_11_5_0_sh_mask.h` through helpers such as `REG_SET_FIELD` or `REG_GET_FIELD`.
4. Read, write, poll, or emit the register through MMIO helpers, RLC-safe helpers, KFD queue/MQD setup, MES queue programming, debug dump paths, perf counter code, or graphics command packets.

For shader and graphics context state, the hardware programming flow is driven by command submissions and context switching: user-mode or kernel-built packets program these context registers before draws or dispatches. For CP/HQD state, initialization and queue management code writes MQD/HQD registers to map queues, enable doorbells, establish read/write pointer reporting, and handle dequeue or reset. For GDS and VMID resources, setup and restore paths allocate per-VMID ranges and clear or restore ownership when processes are scheduled. For GCVM/IOMMU and performance counters, low-level bring-up, debugging, and perf paths program global controls and then read status/result registers.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe GPU hardware registers whose state is owned by AMDGPU, firmware, the command processor, and the graphics/compute engines.

Shader and compute registers are live context state. Program address registers, resource descriptors, user-data windows, scratch bases, VMID, thread dimensions, static thread management, and relaunch/restore registers determine which shader code executes, which address space it uses, and how waves are resumed after preemption or reset. These values can be context-switched, overwritten by command packets, restored by queue/MQD programming, or lost on GPU reset/power transitions.

CP and HQD/MQD registers are persistent queue state while a ring or compute queue is active. Ring bases, read/write pointers, write-pointer polling addresses, doorbell controls, EOP buffers, indirect-buffer state, AQL controls, context-save buffers, DDID counters, and dequeue controls must remain coherent with kernel-managed MQD memory and KFD process state. A stale queue base or VMID can resume the wrong process queue; a stale doorbell or write-pointer address can make submitted work invisible to the hardware.

Graphics context registers in `gc_gfxdec0` are part of draw state. Depth/stencil surfaces, HTILE, render-target bases, CB/DB compression metadata, scissor/viewport transforms, VRS images, user clip planes, primitive/raster controls, and blend constants persist as context state until the next packet or context restore changes them. Incorrect offsets here can cause rendering corruption, memory writes to wrong surfaces, invalid compression metadata access, or bad viewport/scissor clipping.

GDS registers partition shared on-chip data-store resources by VMID and track context-switch/reset state. Per-VMID base/size, GWS, and ordered-append ownership persist across compute scheduling until explicitly reprogrammed or reset. GDS memory-clean and context-switch counters are hardware state used for diagnostics and validation.

Performance-counter and RAS signature registers are diagnostic/control state. Counter selectors/configuration persist while counters run; result-control and reset semantics are determined by hardware and field masks, not by this offset file. RAS signature controls and signatures may be sticky or capture-oriented depending on the hardware sequence.

Reserved registers and reserved holes appear throughout the range. Callers should not infer writability from the existence of a generated offset, and full-register writes must preserve undocumented bits unless the hardware programming guide requires otherwise.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h` supplies matching field shifts and masks.
- Generated defaults, where available for the same IP family, supply reset/default values for register programming and diagnostics.
- AMDGPU SOC15 register helpers translate `reg...` plus `..._BASE_IDX` into the correct MMIO address for the selected GPU instance.
- `gfxhub_v11_5_0.c` includes this exact offset header for GCVM/gfxhub programming. Common GFX 11 code paths also use the same register names for CP/HQD/GDS programming, with `gfx_v11_0.c`, `mes_v11_0.c`, and `amdgpu_amdkfd_gfx_v11.c` showing representative use of symbols such as `regGDS_VMID0_BASE` and `regCP_HQD_PQ_BASE`.

Major integration points include:

- GPU memory-translation setup and fault policy through GCVM/IOMMU/ATS/translation-fault controls.
- KFD and MES compute queue creation, teardown, suspension, resume, preemption, and dequeue through CP HQD/MQD offsets.
- Graphics ring initialization and diagnostics through CP ring base/control/pointer/doorbell/interrupt/status offsets.
- Shader dispatch and graphics pipeline state programming through SPI, COMPUTE, PA, VGT, DB, CB, SX, and TA context registers.
- Context save/restore and post-reset state rebuild through shader context, CP suspend/resume, HQD context-save, GDS, and graphics context registers.
- GPU hang/debug dump paths through CP status/debug/watchpoint, SPI queue reset/context-save, GDS counters, RAS signatures, and render backend state.
- Performance monitoring through GC L2/TLB counters, compute/SPI perf enables, and CP perf context controls.
- Virtualization/PF-VF paths through base index 1 registers, VMID state, doorbell ranges, and PF/VF CP controls.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong offset compiles cleanly but reads or writes the wrong hardware register.
- This chunk starts and ends mid-file and partially crosses address-block boundaries. The preceding chunk owns the beginning of the GCUTCL2 performance-counter block, and the following chunk owns the `gc_pfvf_grbmdec` registers.
- `reg..._BASE_IDX` is as important as the numeric offset. Using an otherwise correct offset with the wrong SOC15 base index can target the wrong aperture.
- Alias macros can hide offset collisions. Code should not assume two differently named macros imply separate hardware state when they intentionally share one offset.
- Address-pair registers must be programmed coherently. Low/high pairs for shader programs, scratch bases, MQD/HQD/PQ/EOP/context-save buffers, watchpoints, timestamp offsets, DCC/color/depth/stencil bases, and VRS resources are vulnerable to partial updates and ordering mistakes.
- Queue registers have direct scheduling side effects. Incorrect HQD active state, VMID, priority, quantum, doorbell, write-pointer polling, AQL, dequeue, EOP, or context-save offsets can hang queues, lose work, or attribute work to the wrong process.
- Graphics context offsets affect memory safety as well as rendering. CB/DB base and compression metadata registers can route render writes to incorrect GPU addresses if an offset or base-index is wrong.
- VMID/GDS ownership mistakes can leak or corrupt per-process GPU state. The sequential `GDS_VMID*`, `GDS_GWS_VMID*`, and `GDS_OA_VMID*` ranges are commonly addressed with arithmetic, so spacing errors are high impact.
- Volatile status and diagnostic registers can change while being read. Debug dump and hang-detection code must treat CP, GDS, SPI, and RAS state as snapshots rather than stable software-owned values.
- Reserved and config-reserved registers should not be treated as safe scratch space. They may be hardware-, firmware-, or ASIC-stepping-specific.
- Performance counter offsets are only addresses; they do not encode event validity, latching order, clear semantics, overflow behavior, or per-instance availability.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware/runtime behavior:

- Kernel build coverage for AMDGPU code that includes `gc_11_5_0_offset.h`, especially gfxhub, GFX, MES, KFD, queue management, reset, debug, and perf paths.
- Mechanical comparison against AMD's authoritative GC 11.5.0 register database to confirm every offset and `BASE_IDX` in lines 2548-5018.
- Cross-checks that every `reg...` macro in this chunk has a matching shift/mask register definition in `gc_11_5_0_sh_mask.h` when fields are defined, and expected defaults where generated.
- Static sanity checks for repeated ranges: 32 shader user-data registers per stage, 16 compute user-data registers, 16 viewport scissor and Z ranges, 16 per-VMID GDS base/size pairs, 16 GWS and OA ownership registers, four TCP watchpoints, four CP DMA watchpoints, and eight color render targets.
- Queue bring-up tests that create, run, preempt, suspend, resume, and destroy compute queues while validating HQD/MQD, doorbell, PQ, EOP, AQL, and context-save programming.
- KFD/MES tests that compare programmed `regCP_HQD_PQ_BASE`/`HI`, VMID, active state, and write-pointer reporting against expected MQD contents.
- Graphics rendering tests covering depth/stencil, render targets, DCC/FDCC, HTILE, blend constants, viewport/scissor arrays, VRS resources, user clip planes, and primitive restart.
- VMID/GDS tests that allocate per-process GDS/GWS/OA resources, context-switch them, reset them, and verify no cross-VMID leakage.
- Memory-translation and fault tests that exercise ATS/IOMMU/translation-fault controls and verify fault attribution and recovery.
- Debug and hang-dump tests that read CP, SPI, GDS, TCP watchpoint, and RAS signature registers and check for coherent, non-impossible state.
- Perf counter tests that program GC_ATC_L2/GCL2TLB/GCUTCL2 counter registers, run controlled workloads, and validate counter changes and clear/enable behavior.
- Reset/suspend/resume tests that verify shader/compute, CP ring, HQD/MQD, GDS, and graphics context state is restored or intentionally reset according to driver policy.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002545`. It covers lines 2548-5018 of `gc_11_5_0_offset.h`. The final per-file research should merge this with adjacent chunks to complete the GCUTCL2 performance-counter block before line 2548 and the PF/VF GRBM block after line 5018, and to place these shader, CP/HQD, GDS/RAS, and graphics context offsets in the full GC 11.5.0 register map.
