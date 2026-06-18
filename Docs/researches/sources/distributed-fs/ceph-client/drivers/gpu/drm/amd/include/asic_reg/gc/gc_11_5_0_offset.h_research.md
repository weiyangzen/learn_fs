# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002544`: lines 1-2547, `Docs/researches/chunks/subset-b-002544_research.md`
- `subset-b-002545`: lines 2548-5018, `Docs/researches/chunks/subset-b-002545_research.md`
- `subset-b-002546`: lines 5019-7499, `Docs/researches/chunks/subset-b-002546_research.md`
- `subset-b-002547`: lines 7500-9967, `Docs/researches/chunks/subset-b-002547_research.md`
- `subset-b-002548`: lines 9968-10002, `Docs/researches/chunks/subset-b-002548_research.md`

## Chunk Research

### subset-b-002544: lines 1-2547

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 1-2547

## Purpose

This chunk is generated AMD GC 11.5.0 register offset metadata. It contains no executable driver logic; it publishes preprocessor constants that name memory-mapped hardware registers and the SOC15 base-index bank used to access them. Consumers combine these `reg*` offsets with `*_BASE_IDX` constants, the companion `gc_11_5_0_sh_mask.h` field masks, and AMDGPU MMIO helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and their offset variants.

The selected range covers the header guard and the first 2,387 `#define` entries. It starts with SDMA0 engine and queue registers, then moves through early graphics-command/status blocks, color/depth/cache arbitration blocks, RMI and UTC/VM blocks, and ends inside the VM L2 performance-counter configuration block. Although this source tree is under `sources/distributed-fs/ceph-client`, this file is AMD GPU driver hardware metadata, not Ceph or filesystem code.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, locks, allocations, callbacks, or control structures in this chunk. The exported API is a generated macro namespace:

- `reg<REGISTER>` gives the register offset within the relevant GC address block.
- `reg<REGISTER>_BASE_IDX` gives the SOC15 register-space base index, usually `0` for the main GC block and `1` for a secondary MMIO aperture used by some hypervisor, power, and perf blocks.
- Address-block comments group the offsets by hardware decode block and record the underlying base address for the generated database.

Major address blocks in this chunk:

- `gc_sdma0_sdma0dec` at base `0x4980`: the largest section in the chunk. It defines SDMA0 global control/status registers, timestamp, power, chicken bits, address configuration, UTCL1/XNACK status, queue reset, error logs, scratch RAM, and eight SDMA queue register groups. Each queue group follows a repeated layout for ring-buffer control/base/read/write pointers, indirect-buffer control/base/size/offset, skip/context/doorbell state, CSA addresses, scheduling, preemption, polling addresses, AQL control, minor pointer update, RB preempt, and mid-command save/restore registers.
- `gc_sdma0_sdma0hypdec`, `gc_sdma0_sdma0perfsdec`, `gc_sdma0_sdma0perfddec`, and `gc_sdma0_sdma0pwrdec`: SDMA0 hypervisor/virtualization, microcode load, VM context, active function, virtual reset, perf-counter selection/data, and SDMA clock/power-control offsets.
- Early graphics blocks: `gc_grbmdec`, `gc_cpdec`, `gc_padec`, `gc_sqdec`, `gc_shsdec`, `gc_tpdec`, `gc_gdsdec`, and `gc_rbdec`. These expose GRBM status/reset/scratch/trap/error registers; CP/CPC/CPF/CPG debug and busy/stall status; primitive assembler and shader queue debug/status windows; shader front-end control/status; texture pipe debug/status; GDS control/status; and render-backend/color/depth-related control and status.
- GCEA and RMI blocks: `gc_gceadec`, `gc_gceadec2`, `gc_gceadec3`, and `gc_rmi_rmidec` define graphics client/external arbitration maps, read/write priority and urgency controls, SDP arbitration/credits/reserves, latency/EDC/debug controls, and RMI crossbar/UTCL1/scoreboard/clock/status registers.
- VM and translation blocks: `gc_pmmdec`, `gc_utcl1dec`, `gc_gcvmsharedpfdec`, `gc_gcvml2pfdec`, `gc_gcatcl2dec`, `gc_gcl2tlbpfdec`, `gc_gcvmsharedvcdec`, and `gc_gcvml2vcdec`. These include system aperture, AGP, FB, local FB, default-page, virtual reset, active function, L1 TLB, VM L2 control/status, protection-fault, dummy-fault, invalidate, context, page-table, identity aperture, bank-select, walker throttle, cache-dump, credit-safety, ATC L2, L2 TLB, translation-assist, and per-context fragment-size registers.
- VM perf blocks at the chunk tail: `gc_gcvml2perfddec`, `gc_gcvml2prdec`, `gc_gcatcl2perfddec`, `gc_gcatcl2pfcntrdec`, `gc_gcl2tlbprdec`, `gc_gcvml2perfsdec`, and the beginning of `gc_gcvml2pldec`. These define low/high VM L2, UTCL2, ATC L2, and L2 TLB performance-counter data registers plus select/mode/config registers. Line 2547 stops at `regGCUTCL2_PERFCOUNTER3_CFG`, so the full `gc_gcvml2pldec` group continues in the next chunk.

Important naming patterns:

- `*_LO` and `*_HI` registers are 32-bit halves of 64-bit addresses, counters, or status values.
- `QUEUE<N>_*` macros identify repeated SDMA queue register windows. Driver code can compute per-queue offsets using the distance between queue 0 and queue 1 register names.
- `CONTEXT<N>_*` macros identify repeated VM context register windows for VMID/context programming.
- `INVALIDATE_ENG<N>_*` macros identify repeated VM invalidation engines with semaphore, request, acknowledge, and address-range registers.
- `PERFCOUNTER*_SELECT`, `*_SELECT1`, `*_MODE`, `*_CFG`, and `*_LO`/`*_HI` distinguish perf event selection, mode/config, and readback registers.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU and AMDKFD consumers:

1. Driver code selects GC 11.5.0 support based on the discovered graphics IP version.
2. The relevant module includes `gc/gc_11_5_0_offset.h` and `gc/gc_11_5_0_sh_mask.h`.
3. Code computes an MMIO address from a `reg*` offset and base index using SOC15 helper macros.
4. Field values are composed or decoded with the matching shift/mask macros from `gc_11_5_0_sh_mask.h`.
5. MMIO reads and writes program hardware state or poll status while higher-level driver logic handles ordering, locking, reset, power state, firmware, and virtualization policy.

`gfxhub_v11_5_0.c` is the direct include user in this repository. It uses the VM-related offsets from this chunk to program GART and system apertures, page-table base/start/end registers, VM context controls, L1 TLB and L2 cache controls, protection-fault defaults and status, invalidation request/ack/semaphore registers, and per-context/per-engine register spacing. SDMA offsets in this generated namespace are used by related SDMA, KFD, MES, and GFX paths for GC 11-era hardware, often through shared `regSDMA0_*` names and per-instance offset helpers.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes hardware state that lives in GPU registers.

The represented hardware state includes:

- SDMA0 queue state: ring-buffer base addresses, read/write pointers, indirect-buffer pointers, doorbell offsets/logs, context status, preemption state, AQL control, polling addresses, CSA addresses, and mid-command save/restore data.
- SDMA0 global state: microcode version and load address/data windows, power/control bits, timestamp, address swizzle/tiling configuration, UTCL1 status and invalidation/XNACK state, error/status logs, scratch RAM, interrupt status, and performance-counter registers.
- Graphics front-end and command state: GRBM status/reset/trap/error/scratch, CP/CPC/CPF/CPG debug and stall status, PA/SQ/SPI/texture/GDS/render-backend controls, and cache/color/depth hardware controls.
- Memory-system and VM state: FB/AGP/system aperture limits, default-page address, VM L1/L2 TLB/cache controls, protection-fault status and default addresses, context enable/control registers, per-context page-table base/start/end registers, invalidation sem/req/ack/range registers, identity apertures, ATC L2/L2TLB controls, RMI/UTC status, and credit-safety registers.
- Profiling state: VM L2, UTCL2, ATC L2, and L2TLB performance-counter select/config/mode registers and low/high result registers.

Persistence is hardware-defined. Some registers retain values until a GPU reset, suspend/resume, power-gating transition, function-level reset, or explicit reprogramming. Others are live status, write-one-to-clear, write-only command, self-clearing strobe, indirect data, or hardware-owned counter registers. This offset header does not encode access type, reset value, side effects, reserved-bit policy, or ordering requirements.

## Dependencies And Integration Points

Directly paired files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h` supplies the register field shifts and masks for these offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c` directly includes this header and uses the VM and GCMC/GCVM register offsets from this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/navi10_enum.h` is included by the direct GFXHUB user for enum-style field values used with the masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc15_common.h` and AMDGPU register helpers provide the MMIO access layer.

Functional integration points:

- GFXHUB initialization and teardown: page-table base programming, GART aperture setup, system aperture setup, L1 TLB control, L2 cache control, system-domain enablement, identity aperture setup, and fault handling.
- VM invalidation: the repeated `regGCVM_INVALIDATE_ENG*` offsets allow the VM hub code to issue per-VMID invalidations, program optional address ranges, and poll acknowledgements.
- GPU fault reporting: `regGCVM_L2_PROTECTION_FAULT_STATUS`, address, default-address, and control registers provide the hardware state decoded for VM fault logs.
- SDMA queue setup and recovery: SDMA queue ring, pointer, doorbell, polling, preemption, and context-status offsets are used by SDMA/KFD/MES style paths to create queues, restore queue state, reset queues, and diagnose hangs.
- Power, reset, and clock-gating: GRBM status/reset and SDMA/GCVM/GCEA/ATC/RMI clock/power-related offsets are consumed by graphics initialization, reset recovery, runtime power management, and firmware setup.
- Profiling and diagnostics: perf-counter select/config/data offsets expose VM and SDMA performance-monitor registers, while debug/status registers support low-level diagnostics and validation.

## Risks And Edge Cases

- Offset/header mismatch is the central risk. Pairing `gc_11_5_0_offset.h` with the wrong shift/mask header or an incompatible GC IP version can compile successfully while reading or writing the wrong register.
- The macros are untyped constants. A caller can accidentally use a register from the wrong block, base index, queue, VM context, or invalidation engine without compiler help.
- Repeated register windows rely on exact spacing. Code such as GFXHUB context setup and SDMA queue setup computes distances between queue/context/engine registers; a generated offset change or wrong base register breaks every derived address.
- SDMA queue registers are stateful and ordering-sensitive. Ring base, read/write pointers, doorbells, polling addresses, AQL control, preemption, and mid-command state must be programmed in the sequence expected by the SDMA engine and firmware.
- VM registers are high impact. Wrong page-table base, aperture, context-control, or invalidation programming can cause GPU page faults, stale translations, memory corruption, hangs, or broken SR-IOV isolation.
- Many `LO`/`HI` pairs represent 64-bit values. Consumers need stable read/write ordering and correct shifts; mixing `>> 12`, `>> 24`, `>> 44`, or raw lower/upper 32-bit programming is context-specific.
- Some registers are PF-only, VF-visible, hypervisor, or PSP/firmware-owned. The header does not encode access privilege, so SR-IOV and secure/firmware mediated paths must decide whether a write is legal.
- Register side effects are not visible in the offset list. Invalidation requests, reset requests, queue reset, counter result controls, fault clears, and indirect data windows may be strobes or command registers, not durable configuration.
- Perf counters can return misleading results if the select/mode/config registers are programmed while clocks are gated, blocks are idle, wrong clients/contexts are selected, or low/high halves are sampled inconsistently.
- The chunk boundary is artificial. The `gc_gcvml2pldec` perf-counter configuration block is only partially present here, so downstream research must merge adjacent chunks before treating the per-file coverage as complete.

## Test Signals

Useful validation signals are mostly build, static generated-header checks, and hardware smoke tests:

- Build AMDGPU with GC 11.5.0 support enabled and ensure `gfxhub_v11_5_0.c` compiles against both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h`.
- Static generated-header checks that every `reg*` macro has a matching `reg*_BASE_IDX`, that register names used by `gfxhub_v11_5_0.c` exist in this offset header, and that corresponding field macros exist in `gc_11_5_0_sh_mask.h`.
- VM initialization tests on GC 11.5.0-class hardware: GART aperture setup, system aperture setup, VM context enablement, page-table base programming, and successful command submission using VMID-backed mappings.
- VM invalidation tests that issue per-VMID invalidations, poll `GCVM_INVALIDATE_ENG*_ACK`, and verify stale translations are not observed after page-table updates.
- Fault-path tests that intentionally trigger invalid GPU virtual addresses and verify `GCVM_L2_PROTECTION_FAULT_STATUS` plus fault address/default-page handling are decoded and cleared correctly.
- SDMA queue smoke tests that initialize queues, update doorbells and write pointers, submit copy/fill work, exercise preemption or reset where supported, and verify status/idle registers after completion.
- Suspend/resume, GPU reset, runtime power-management, and SR-IOV VF/PF tests because many offsets in this chunk touch state that is lost, privileged, firmware-owned, or reinitialized across power and function transitions.
- Perf-counter smoke tests for SDMA, VM L2, UTCL2, ATC L2, and L2TLB counters: configure select/mode registers, run known memory or copy workloads, read low/high counter pairs, and verify values are plausible and not stuck at zero or saturated.

### subset-b-002545: lines 2548-5018

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

### subset-b-002546: lines 5019-7499

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 5019-7499

## Purpose

This chunk is generated AMD GC 11.5.0 register-offset metadata. It does not implement executable control flow; it provides C preprocessor symbols that map Graphics/Compute (GC) hardware register names to SOC15 register offsets and companion `*_BASE_IDX` values. Kernel driver code can then use symbolic names such as `regGRBM_GFX_CNTL`, `regCP_MES_CNTL`, or `regGL2C_CTRL` through SOC15 helpers instead of hard-coded offsets.

The assigned range starts at the tail of `gc_pfvf_grbmdec` with `regGRBM_GFX_CNTL` and `regGRBM_NOWHERE`, then covers complete blocks for PA/SQ/CP/DIDT/SPI/TCP/GDS/UTCL1/PMM/CAC/GFXU/CP RS64/cache decoders, and ends mid-`gc_perfddec` at `regTCP_PERFCOUNTER1_LO`. The next line outside the chunk supplies `regTCP_PERFCOUNTER1_LO_BASE_IDX`, so merge/reconciliation should treat the final register pair as split across chunks.

## Register Map Content

The chunk contains 1,203 non-`BASE_IDX` register symbols and 1,202 visible `*_BASE_IDX` companions, plus 13 intentional offset aliases. Every visible base index is `1`, which means these GC registers belong to the second base-address table slot used by SOC15 address computation.

Covered address blocks:

| Lines | Address block | Base address | Visible register range | Count |
| --- | --- | ---: | --- | ---: |
| 5019-5022 | `gc_pfvf_grbmdec` tail | `0x2a400` | `regGRBM_GFX_CNTL`..`regGRBM_NOWHERE` | 2 |
| 5025-5096 | `gc_pfvf_padec` | `0x2a500` | `regPA_SC_VRS_SURFACE_CNTL`..`regPA_SC_BINNER_OUTPUT_TIMEOUT_COUNTER` | 34 |
| 5097-5120 | `gc_pfvf_sqdec` | `0x2a780` | `regSQ_RUNTIME_CONFIG`..`regSQ_SHADER_TMA_HI` | 10 |
| 5121-5128 | `gc_pfonly_cpdec` | `0x2e000` | `regCP_DEBUG_2`..`regCP_FETCHER_SOURCE` | 2 |
| 5129-5138 | `gc_pfonly_cpphqddec` | `0x2e080` | `regCP_HPD_MES_ROQ_OFFSETS`..`regCP_HPD_STATUS0` | 3 |
| 5139-5170 | `gc_pfonly_didtdec` | `0x2e400` | DIDT EDC and indirect-index/data registers | 14 |
| 5171-5192 | `gc_pfonly_spidec` | `0x2e500` | SPI debug, arbitration, feature, and context-save status | 9 |
| 5193-5204 | `gc_pfonly_tcpdec` | `0x2e680` | TCP invalidate/status/control | 4 |
| 5205-5212 | `gc_pfonly_gdsdec` | `0x2e6c0` | GDS enhancement and OA CGPG restore | 2 |
| 5213-5230 | `gc_pfonly_utcl1dec` | `0x2e600` | UTCL1 and GCRD credit/target controls | 7 |
| 5231-5242 | `gc_pfonly_pmmdec` | `0x2e640` | GCR general/target/cmd/spare controls | 4 |
| 5243-5542 | `gc_pfonly_gccacdec` | `0x2eb40` | GC/SE CAC controls, weights, and indirect registers | 148 |
| 5543-5610 | `gc_pfonly2_spidec` | `0x2f000` | per-CU SPI resource reserve and enable registers | 32 |
| 5611-6206 | `gc_gfxudec` | `0x30000` | CP EOP/fence/stats/scratch/atomic/GDS/SPI user registers | 296 |
| 6207-7084 | `gc_cprs64dec` | `0x32000` | MES and GFX RS64 program/control/debug/aperture registers | 437 |
| 7085-7112 | `gc_gl1dec` | `0x33400` | GL1/GL1C arbitration, burst, status, and UTCL0 controls | 12 |
| 7113-7132 | `gc_chdec` | `0x33600` | CH/CHC arbitration, burst, delay, and status controls | 8 |
| 7133-7194 | `gc_gl2dec` | `0x33800` | GL2C/GL2A cache controls, address matching, flush/reset, counters | 29 |
| 7195-7206 | `gc_gl1hdec` | `0x33900` | GL1H arbitration and burst/status registers | 4 |
| 7207-7499 | `gc_perfddec` partial | `0x34000` | performance-counter registers from CPG through TCP | 146 visible |

Important symbol families include `GRBM`, `PA_SC`, `SQ`, `CP`, `DIDT`, `SPI`, `TCP`, `GDS`, `UTCL1`, `GCR`, `GC_CAC`, `SE_CAC`, `GL1`, `CH`, `GL2`, and many `*_PERFCOUNTER*` registers. The largest parts are the command processor/MES/RS64 families (`CP_*`) and the graphics performance counter block.

## APIs, Types, and Integration Points

There are no functions, structs, enums, or runtime APIs in this range. The public interface is the set of macros:

- `regNAME` gives the register offset used by SOC15 register access machinery.
- `regNAME_BASE_IDX` gives the base-address-table index paired with that offset.

The file is included directly by `drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`. The same naming convention is used across AMDGPU GC headers by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_ENTRY_STR`, and golden-register table macros in neighboring GC/GFX/MES code. In this source tree, similar register names are accessed in version-specific files such as `gfx_v11_0.c`, `gfx_v12_0.c`, `mes_v12_0.c`, and `mes_v12_1.c`; for GC 11.5.0, this header supplies the authoritative offsets for code that includes the `gc_11_5_0` register set.

Several symbols deliberately alias the same offset to preserve hardware/manual naming variants:

- `regCP_HPD_MES_ROQ_OFFSETS` and `regCP_HPD_ROQ_OFFSETS` at `0x1821`.
- `regSCRATCH_REG_ATOMIC` and `regSCRATCH_REG_CMPSWAP_ATOMIC` at `0x2048`.
- `regCP_APPEND_DATA` and `regCP_APPEND_DATA_LO` at `0x205a`.
- `regCP_APPEND_LAST_CS_FENCE` and `regCP_APPEND_LAST_CS_FENCE_LO` at `0x205b`.
- `regCP_APPEND_LAST_PS_FENCE` and `regCP_APPEND_LAST_PS_FENCE_LO` at `0x205c`.
- CP/ME atomic preop aliases from `0x205d` through `0x2062`.
- MES interrupt-vector aliases `regCP_MES_INTR_ROUTINE_START`/`regCP_MES_MTVEC_LO` and `_HI`/`MTVEC_HI` at `0x2801` and `0x2802`.

## Control Flow and State

The header has no branches, loops, locking, allocation, or I/O by itself. Control flow appears only in consumers that compile these constants into register reads and writes. State is entirely hardware-resident: writes through consumers can affect GPU scheduler/MES state, command-processor fences and atomics, cache control/flush behavior, CAC/power accounting, performance counters, scratch registers, and debug/trap settings.

The macros are compile-time constants and are not persisted by software. Persistence and reset behavior depend on the underlying GC hardware block. Many registers in the chunk are volatile operational registers, including counters, status registers, indirect-index/data windows, fence addresses, scratch slots, cache-control registers, and MES/RS64 program/aperture registers. Values may be reset by GPU reset, power-gating, clock-gating, firmware initialization, or mode switches outside this header.

## Dependencies

The chunk depends on the AMD ASIC register-generation contract: register symbols, offsets, address-block comments, and base-index companions must match the GC 11.5.0 hardware specification and the SOC15 base-address table used by AMDGPU. It is paired conceptually with sibling generated headers such as `gc_11_5_0_sh_mask.h`, which provide field masks and shifts for many of these registers.

Consumer dependencies are the AMDGPU register-access helpers and include ordering. A consumer must include the correct ASIC offset header for the active IP version; using a GC 11.5.0 offset against a different hardware generation can silently target the wrong MMIO address.

## Risks

- Offset drift is high impact: a single incorrect constant can make `RREG32_SOC15`/`WREG32_SOC15` read or write the wrong hardware register.
- The chunk boundary splits `regTCP_PERFCOUNTER1_LO` from its `BASE_IDX`, so partial analysis or generated diffs must not treat that symbol as missing a companion in the full file.
- Aliased offsets are expected; deduplication tooling must preserve all names because consumers may use either the generic or block-specific spelling.
- PF/VF and PF-only block names matter for virtualization/security. Exposing or writing PF-only registers in the wrong execution context could break SR-IOV assumptions.
- Indirect register pairs such as `DIDT_IND_INDEX`/`DIDT_IND_DATA`, `GC_CAC_IND_INDEX`/`GC_CAC_IND_DATA`, and `SE_CAC_IND_INDEX`/`SE_CAC_IND_DATA` require ordered consumer access and appropriate serialization; the header only names the windows.
- Counter low/high pairs and 64-bit address/data pairs require consumer-side ordering to avoid torn reads or partially programmed addresses.
- Generated headers are easy to review superficially; validation should rely on generator inputs, hardware tables, and compile-time/use-site tests rather than manual spot checks only.

## Test and Validation Signals

- Build coverage: compile AMDGPU code paths that include `gc/gc_11_5_0_offset.h`, especially `gfxhub_v11_5_0.c`.
- Static checks: verify every `reg*` symbol in the full header has the expected `*_BASE_IDX` companion and that all base indices match the SOC15 base-address table for GC 11.5.0. The apparent missing companion at this chunk end is resolved at line 7500.
- Register-table checks: compare address-block base comments and offset ranges against the vendor register database used to generate the file.
- Runtime smoke: on matching GC 11.5.0 hardware, confirm safe reads of status/version/counter registers through debugfs or driver diagnostic paths and confirm no invalid-register faults during bring-up.
- Functional signals: MES initialization, ring scheduling, GPU reset/recovery, cache invalidation, performance-counter collection, and SR-IOV/PF-VF paths should continue to work because this chunk names registers used by those paths.

### subset-b-002547: lines 7500-9967

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 7500-9967

## Scope

This chunk is a generated AMD GC 11.5.0 register-offset header slice. It contains C preprocessor constants only: register offset macros, matching `_BASE_IDX` macros, and generated comments that split the register namespace into address blocks. There are no functions, structs, enums, runtime branches, allocations, locks, or direct MMIO operations in this range.

The requested lines contain 2,404 `#define` statements: 2,083 `reg...` macros for directly addressed registers, 321 `ix...` macros for indexed address spaces, and 1,042 `_BASE_IDX` macros. The chunk starts in the middle of the GC performance-counter offset table at `regTCP_PERFCOUNTER1_LO_BASE_IDX`, covers multiple performance-select and control address blocks, and ends inside the `sqind` indexed shader-queue debug register group at `ixSQ_WAVE_LDS_ALLOC`.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata and is unrelated to Ceph filesystem behavior.

## Purpose

`gc_11_5_0_offset.h` maps symbolic GC 11.5.0 register names to hardware register offsets. Driver code pairs these constants with generated bitfield definitions from companion shift/mask headers and uses SOC15/MMIO helper macros to access the right register for this ASIC generation.

This chunk covers late graphics-core performance monitoring and control surfaces:

- Performance counter data and selector registers for texture, cache, shader, geometry, color/depth, command processor, RLC, rasterization, primitive assembly, global data share, and UTCL1 blocks.
- GRTAVFS and RTAVFS target frequency/voltage, soft reset, clock, power-state, and indirect register windows.
- CP hypervisor-facing microcode and instruction/data cache base, bound, and control registers for PFP, ME, MEC, CPC, MES, and RS64 surfaces.
- RLC control/status, timers, interrupts, clock counts, doorbells, power-gating, safe-mode, microcontroller, save/restore, SPM, residency, interrupt-handler client, IMU boot, and SMU mailbox registers.
- Power decoder clock-gating and clock-control registers across shader, geometry, rasterization, cache, command processor, RLC, GDS, DB, CB, and UTCL1 units.
- Hypervisor, PSP, and GFX IMU mailboxes, scratch registers, interrupt controls, reset/power state, DPM, firmware timestamp, RAM windows, and security/access-control surfaces.
- Indexed CAC, RTAVFS, and SQ debug/wave register offsets.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace:

- `reg<NAME>` expands to the register offset used by AMDGPU register access helpers.
- `reg<NAME>_BASE_IDX` expands to a base-index selector, almost always `1` in this chunk, used by SOC15-style helpers to choose the MMIO base aperture.
- `ix<NAME>` expands to an index within an indirect register space rather than a normal direct MMIO offset.
- `// addressBlock: ...` and `// base address: ...` comments identify generated address-map regions.

Important direct-address macro families include:

- Performance counter data registers before `gc_perfsdec`: `TCP`, `GL2C`, `GL2A`, `GL1C`, `CHC`, `CB`, `DB`, `RLC`, `RMI`, `GCR`, `PA_PH`, `UTCL1`, `GL1A`, `GL1H`, `CHA`, `GDS`, `GE1`, `GE2`, `SPI`, `SQ`, `SQG`, `SX`, `GCEA`, `PC`, `PA_SC`, `PA_SU`, `GRBM`, `CPG`, `CPF`, and `CPC` `PERFCOUNTER*_LO/HI`, filter, and control registers.
- `gc_perfsdec` selector registers such as `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, and `*_PERFCOUNTER*_CNTR` for the same broad graphics and cache blocks. These choose events for the counter data registers.
- `gc_grtavfs_grtavfs_dec` and `gc_grtavfsdec` macros for `GRTAVFS_RTAVFS_REG_ADDR`, write/read data, general, control/status, target frequency/voltage, soft reset, PSM, and clock control.
- `gc_cphypdec` CP microcode and cache registers including `CP_HYP_PFP_UCODE_*`, aliases such as `CP_PFP_UCODE_*`, ME RAM address/data aliases, `CP_HYP_ME_*`, `CP_HYP_MEC1/2_*`, `CP_PFP_IC_*`, `CP_ME_IC_*`, `CP_CPC_IC_*`, `CP_MES_IC_*`, `CP_MES_MI/MD*`, `CP_GFX_RS64_*`, and `CP_MEC_MI/MD*`.
- `gc_rlcdec` macros for `RLC_CNTL`, firmware version/status, reference and GPU clock timestamps, GPM timers and interrupts, microcode control, RLCG doorbells, power-gating controls and status, SRM index/control windows, save/restore lists, SPM setup, performance monitor selection, safe-mode/SMU command mailbox registers, IMU bootload address/size, and RLC interrupt/debug surfaces.
- `gc_rlcsdec` and `gc_pfvfdec_rlc` macros for RLC GPM status, safe mode, SPM interrupt state, CSIB address/length, CP scheduler hooks, EOF interrupts, and spare interrupt registers.
- `gc_pwrdec` macros for `CGTS_TCC_DISABLE`, per-block `GFX_ICG_*`, `CGTT_*`, `ICG_*`, `GL1*/GL2*`, `GCEA`, `RMI`, `GCR`, `DB`, `CB`, `CP`, `RLC`, and `UTCL1` clock controls.
- `gc_hypdec` macros for pipe priority, GRBM save/restore select/data, SE/SA/WGP/RB remapping, SDMA status, RLC hypervisor semaphores, busy/clock controls, IH cookie state, runlist and save/restore control, CP/GFX command status, address-window controls, and user shader rate configuration.
- `gc_pspdec` macros for MES debug-message index/data and GRBM hypervisor CAM address/data windows.
- `gc_gfx_imu_gfx_imudec` and `gc_gfx_imu_gfx_imu_pspdec` macros for GFX IMU C2P message registers, access controls, interrupt controls/status, RLC command/data/status mailboxes, scratch registers, firmware timestamps, GTS offsets, PIC/IH controls, doorbell control, DPM counters, RAM address/data windows, reset/power-good state, and IMU instruction/data RAM windows.

Important indexed macro families include:

- `gccacind`: `ixGC_CAC_ID`, `ixGC_CAC_CNTL`, `ixGC_CAC_STATUS`, multiple GC CAC weight/override/status registers, clock counter readouts, dynamic override/status registers, power/clock residency counters, accumulator controls, power-good/ready readouts, and LUT update status.
- `secacind`: `ixSE_CAC_ID` and `ixSE_CAC_CNTL`.
- `grtavfsind`: `ixRTAVFS_REG0` through `ixRTAVFS_REG194`, a dense RTAVFS indexed-register range.
- `sqind`: the first local SQ debug and wave state offsets in this chunk: `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_ACTIVE`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_GPR_ALLOC`, and `ixSQ_WAVE_LDS_ALLOC`.

## Control Flow

This header has no executable control flow. It affects runtime behavior only through macro expansion in code that reads, writes, or read-modify-writes GC 11.5.0 registers.

The implied access flow is:

1. Driver code selects a symbolic register macro from this offset header.
2. For direct registers, AMDGPU SOC15/MMIO helpers combine the offset with the `_BASE_IDX` value and the GC instance to access the hardware aperture.
3. For indexed registers, driver code uses the corresponding indirect-index mechanism, such as an index/data window, and writes an `ix...` selector rather than a direct `reg...` offset.
4. Companion shift/mask definitions, where present, compose or decode bitfields at the chosen offset.
5. The actual sequencing is owned by higher-level AMDGPU components such as performance-counter setup, RLC/SMU/IMU initialization, CP firmware loading, clock-gating programming, reset, suspend/resume, and debug dump paths.

Performance monitoring usually programs event selector registers in `gc_perfsdec`, enables counting through the relevant control/filter registers, then samples low/high counter pairs from the earlier direct counter region. RLC, CP, IMU, PSP, and GRTAVFS paths often require ordered mailbox or index/data transactions, but this header records only numeric addresses and does not encode polling, acknowledgement, timeout, clear, or ownership rules.

## State And Persistence Behavior

The macros themselves are stateless compile-time constants. Persistent and volatile state exists in GPU registers, firmware-owned SRAM/RAM windows, command processor state, RLC/IMU/SMU mailboxes, counter latches, doorbell capture registers, indexed CAC/RTAVFS/SQ spaces, and memory-backed save/restore areas.

State covered by this chunk includes:

- Performance counter selectors, filter controls, low/high counter data, and SPM/event-monitoring state.
- RLC firmware status, timers, interrupts, GPM state, power-gating controls, residency counters, safe-mode state, doorbell monitor data, IMU bootload metadata, and SMU command arguments/responses.
- CP firmware upload and instruction/data cache base/bound registers for multiple engines. Some entries are aliases at the same numeric offset, reflecting different consumer names for the same hardware window.
- Clock-gating and power control state for many graphics blocks. These settings persist until reprogrammed, reset, or power-management firmware changes them.
- Hypervisor and PSP-visible state such as GRBM save/restore windows, remap controls, semaphores, CAM windows, and user shader-rate configuration.
- GFX IMU firmware mailboxes, scratch space, interrupt controller state, DPM counters, reset/power-good bits, RAM windows, and IH gasket controls.
- Indexed CAC and RTAVFS telemetry/control state, plus local SQ wave/debug state for the selected shader context.

Some registers are configuration, some are live counters or status, some are firmware mailboxes, some are aliases, and some may be write-one-to-clear, self-clearing, or read-sensitive. This offset header does not encode access type or side-effect semantics; consumers must rely on the hardware register database and established driver sequences.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register set staying synchronized:

- `gc_11_5_0_sh_mask.h` supplies matching field shifts and masks for registers that have named fields.
- `gc_11_5_0_default.h`, where present for this generation, supplies reset/default values for related registers.
- AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_SOC15_IP`, `WREG32_SOC15_IP`, `RREG32`, `WREG32`, `REG_SET_FIELD`, and indirect-register helper paths supply actual access behavior.
- Performance tooling and profiling paths rely on the counter and selector pairs remaining consistent.
- RLC, CP, PSP, SMU, IMU, reset, suspend/resume, power-management, clock-gating, GPU virtualization, SR-IOV, debugfs/register-dump, KFD, and hang-diagnosis paths can all consume these symbolic offsets.

The `reg..._BASE_IDX` values are part of the integration contract with SOC15-style address translation. The `ix...` values are part of a different contract: callers must route them through the proper indexed address block instead of treating them as ordinary MMIO offsets.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong offset or base index can compile cleanly while touching the wrong register.
- This chunk starts and ends mid-group. The previous chunk owns the beginning of the `TCP_PERFCOUNTER1` context, and the next chunk continues the `sqind` SQ wave/debug register table.
- Many performance counter families are repetitive but not interchangeable. Counter data, event selector, filter, and enable registers belong to different blocks and may have different widths, event encodings, and sampling rules.
- `_BASE_IDX` macros are mechanically paired with direct `reg...` macros. Missing or wrong base indices can break SOC15 register access even when the visible offset looks correct.
- `ix...` offsets have base address `0x0` in their generated blocks, but they are not normal direct MMIO offsets. Misrouting indexed CAC, RTAVFS, or SQ debug offsets through direct helpers can access unrelated hardware.
- Several CP and RLC macro names are aliases for the same numeric offsets, such as CP hypervisor and non-hypervisor microcode windows. Consumers must use the alias appropriate to the privilege and engine context.
- RLC, IMU, SMU, PSP, and GRTAVFS mailbox/register-window transactions are ordering- and timeout-sensitive. The offset table does not protect callers from missing a required poll, acknowledgement, mutex, safe-mode transition, or firmware ownership check.
- Clock-gating and power-control registers can destabilize active GPU blocks if modified outside the established bring-up, suspend/resume, or reset sequencing.
- Performance counters and residency counters may be split into low/high halves or latched by capture controls. Sampling without the expected latch order can produce torn values.
- Debug and wave-state indexed SQ registers are context-sensitive. Reads may depend on prior wave selection, debug halt state, shader engine selection, or GRBM indexing.
- Hypervisor, PSP, and security/access-control registers are isolation-sensitive. Incorrect offsets or access paths can break SR-IOV partitioning, firmware communication, or fault attribution.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations that include GC 11.5.0 support. Missing or renamed register macros should surface as compile failures in RLC, CP, power-management, debug, profiling, IMU, PSP, or KFD paths.
- Mechanically compare every offset and `_BASE_IDX` in this chunk against AMD's authoritative GC 11.5.0 register database.
- Check that each `reg...` macro has a matching `_BASE_IDX` macro and that direct-register names with fields also have corresponding shift/mask entries in `gc_11_5_0_sh_mask.h`.
- Validate that `ix...` macros are used only through indirect-index paths and not through direct SOC15 MMIO helpers.
- Exercise GPU performance counters and SPM sampling across TCP, cache, shader, geometry, DB/CB, RLC, UTCL1, and command processor blocks, checking selector-to-counter consistency and low/high sampling behavior.
- Exercise RLC initialization, safe mode, GPM timers/interrupts, RLCG/XT doorbells, power-gating transitions, residency counters, SMU mailbox commands, and IMU bootload handoff while monitoring for timeouts or stuck status bits.
- Exercise CP firmware loading and instruction/data cache base/bound setup for PFP, ME, MEC, CPC, MES, and RS64 paths where supported.
- Run suspend/resume, GPU reset, runtime power management, clock-gating enable/disable, SR-IOV or hypervisor paths, and PSP/IMU mailbox communication on GC 11.5.0 hardware.
- Decode register dumps with these offsets and compare against known-good dumps or vendor tooling, especially for RLC status, CP microcode windows, clock-gating controls, GFX IMU messages, CAC/RTAVFS indexed registers, and SQ wave debug state.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002547`. The final per-file research should merge this with neighboring chunks for full `gc_11_5_0_offset.h` coverage. The previous chunk supplies the beginning of the performance-counter section, while the next chunk continues the `sqind` indexed SQ debug/wave register table after `ixSQ_WAVE_LDS_ALLOC`.

### subset-b-002548: lines 9968-10002

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h lines 9968-10002

## Scope

This chunk is the tail of the generated AMD GC 11.5.0 register-offset header. It contains C preprocessor constants only: no functions, structs, enums, storage, includes, locking, or runtime branches are introduced in this range. The selected lines define the last `sqind` indexed shader-queue wave register offsets and then close the `_gc_11_5_0_OFFSET_HEADER` include guard.

The exact chunk starts after the first basic SQ wave state registers were already introduced by the previous chunk. Lines 9968-10002 cover instruction-buffer status, program counter, scratch base, wave hardware identity, scheduler mode, shader cycle count, temporary trap registers, scalar `M0`, and execution-mask offsets:

- `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, and `ixSQ_WAVE_IB_DBG1`.
- `ixSQ_WAVE_PC_LO` and `ixSQ_WAVE_PC_HI`.
- `ixSQ_WAVE_FLUSH_IB`.
- `ixSQ_WAVE_FLAT_SCRATCH_LO` and `ixSQ_WAVE_FLAT_SCRATCH_HI`.
- `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_POPS_PACKER`, `ixSQ_WAVE_SCHED_MODE`, and `ixSQ_WAVE_SHADER_CYCLES`.
- `ixSQ_WAVE_TTMP0` through `ixSQ_WAVE_TTMP15`.
- `ixSQ_WAVE_M0`, `ixSQ_WAVE_EXEC_LO`, and `ixSQ_WAVE_EXEC_HI`.

Although this repository is under a `ceph-client` source tree, this file is AMDGPU DRM hardware metadata for the GC 11.5.0 graphics IP block, not filesystem implementation code.

## Purpose

`gc_11_5_0_offset.h` maps generated register names to numeric offsets for the GC 11.5.0 ASIC family. The `ix...` names in this chunk are not normal memory-mapped register addresses by themselves. They are indexes into the shader queue indexed-register path, selected through the companion `regSQ_IND_INDEX`/`regSQ_IND_DATA` MMIO window defined earlier in the same offset header.

The driver uses this kind of register metadata to avoid embedding raw hardware indices in engine code. For SQ wave inspection, the runtime flow is to write `regSQ_IND_INDEX` with a wave selector and one of these `ixSQ_WAVE_*` index values, then read `regSQ_IND_DATA` to snapshot the selected wave register. The matching field layout for `SQ_IND_INDEX` lives in `gc_11_5_0_sh_mask.h`, where `SQ_IND_INDEX__WAVE_ID`, `SQ_IND_INDEX__WORKITEM_ID`, `SQ_IND_INDEX__AUTO_INCR`, and `SQ_IND_INDEX__INDEX` describe how the index register is packed.

This tail section is primarily diagnostic and context-inspection metadata. It supports wave dump paths, hang analysis, shader debugging, KFD/compute fault triage, and low-level validation of live wave execution state. It is not queue creation logic and does not directly program draw or dispatch commands.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the macro naming contract:

- `ixSQ_WAVE_IB_STS` (`0x0107`) selects the wave instruction-buffer status register.
- `ixSQ_WAVE_PC_LO` (`0x0108`) and `ixSQ_WAVE_PC_HI` (`0x0109`) select the low and high halves of the wave program counter.
- `ixSQ_WAVE_IB_DBG1` (`0x010d`) selects additional instruction-buffer debug state.
- `ixSQ_WAVE_FLUSH_IB` (`0x010e`) selects an indexed control/status register related to flushing the wave instruction buffer.
- `ixSQ_WAVE_FLAT_SCRATCH_LO` (`0x0114`) and `ixSQ_WAVE_FLAT_SCRATCH_HI` (`0x0115`) select the wave flat-scratch base address halves.
- `ixSQ_WAVE_HW_ID1` (`0x0117`) and `ixSQ_WAVE_HW_ID2` (`0x0118`) select hardware identity information for the wave.
- `ixSQ_WAVE_POPS_PACKER` (`0x0119`) selects POPS packer state.
- `ixSQ_WAVE_SCHED_MODE` (`0x011a`) selects scheduling-mode state.
- `ixSQ_WAVE_IB_STS2` (`0x011c`) selects a second instruction-buffer status register.
- `ixSQ_WAVE_SHADER_CYCLES` (`0x011d`) selects the wave shader-cycle counter/state.
- `ixSQ_WAVE_TTMP0` through `ixSQ_WAVE_TTMP15` (`0x026c` through `0x027b`) select the wave temporary trap registers.
- `ixSQ_WAVE_M0` (`0x027d`) selects the scalar `M0` register.
- `ixSQ_WAVE_EXEC_LO` (`0x027e`) and `ixSQ_WAVE_EXEC_HI` (`0x027f`) select the low and high halves of the wave execution mask.

The main integration macros outside this chunk are:

- `regSQ_IND_INDEX` and `regSQ_IND_DATA` from the same offset header. These provide the indexed access aperture used to read the `ixSQ_WAVE_*` entries.
- `SQ_IND_INDEX__*` field masks and shifts from `gc_11_5_0_sh_mask.h`. These define how callers place the wave ID, work-item/thread ID, auto-increment bit, and target index into `regSQ_IND_INDEX`.
- `WREG32_SOC15`, `RREG32_SOC15`, `SOC15_REG_OFFSET`, and related AMDGPU register helpers. These perform the actual MMIO access after the generated constants are selected.

Representative consumers in the broader AMDGPU tree include the GC v11 and GC v12 wave snapshot helpers. In `gfx_v11_0_read_wave_data()`, the driver reads `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_PC_HI`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_EXEC_HI`, `ixSQ_WAVE_HW_ID1`, `ixSQ_WAVE_HW_ID2`, `ixSQ_WAVE_GPR_ALLOC`, `ixSQ_WAVE_LDS_ALLOC`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_IB_STS`, `ixSQ_WAVE_IB_STS2`, `ixSQ_WAVE_IB_DBG1`, `ixSQ_WAVE_M0`, and `ixSQ_WAVE_MODE` through the indexed SQ path. Several of the offsets used by that flow are defined in this chunk.

## Control Flow

This header has no runtime control flow. The only direct behavior is compile-time macro substitution.

The implied runtime control flow for these constants is:

1. AMDGPU selects the GC 11.5.0 generated register headers for a matching ASIC family.
2. A debug, hang-dump, wave-inspection, or compute diagnostics path selects a shader engine/shader array/SIMD/wave context using higher-level GPU selection helpers.
3. The path writes `regSQ_IND_INDEX` with `wave << SQ_IND_INDEX__WAVE_ID__SHIFT` and `index << SQ_IND_INDEX__INDEX__SHIFT`; register-read helpers may also set work-item/thread and auto-increment fields when reading SGPR/VGPR ranges.
4. The path reads `regSQ_IND_DATA`, which returns the contents of the selected wave indexed register.
5. The collected values are copied into a wave dump buffer or decoded by higher-level debug tooling.

For the specific macros in this chunk, the common ordering in diagnostic dumps is to read PC and execution-mask values alongside wave status and hardware ID, then read allocation, trap, instruction-buffer, and mode registers. This chunk contributes the PC, EXEC, IB status/debug, M0, hardware ID, and scheduler-mode pieces of that snapshot.

The header does not define wave selection, shader-engine selection, register-read barriers, polling, retry behavior, or the lifetime of the returned data. Those details live in AMDGPU engine code and in the hardware programming model.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They name hardware-owned indexed registers whose values are live wave state.

The values selected by this chunk are volatile. `PC_LO`/`PC_HI`, `EXEC_LO`/`EXEC_HI`, `M0`, `IB_STS`, `IB_STS2`, `IB_DBG1`, `SCHED_MODE`, and `SHADER_CYCLES` can change while a wave is executing. A snapshot collected without halting or otherwise stabilizing the target wave is best treated as a point-in-time diagnostic view, not a persistent software-owned record.

Some registers represent architecturally meaningful execution state. The program counter identifies where the wave is executing. `EXEC_LO` and `EXEC_HI` identify active lanes. `M0` is used by shader instructions for addressing and control behavior. `TTMP0..TTMP15` are trap-handler temporary registers and may contain context save/restore, exception, or trap handling state. `FLAT_SCRATCH_LO/HI` participates in per-wave flat scratch addressing. Incorrect offsets for these registers can make a debug dump point at the wrong instruction, wrong lanes, or wrong trap state.

Other registers are diagnostic or scheduling observability state. `HW_ID1/HW_ID2` identify where the wave resides in the hardware, `SCHED_MODE` reports scheduling mode, `SHADER_CYCLES` exposes cycle/accounting state, and the instruction-buffer status/debug registers expose fetch/decode-side state. These are especially useful during GPU hang analysis but are not persistent driver configuration.

The `ixSQ_WAVE_FLUSH_IB` name suggests a control/status register with a side-effect-oriented purpose. This chunk only supplies the index value and does not document whether reads are passive or writes are allowed. Any caller writing indexed SQ registers must rely on the hardware guide and established engine code, not on the offset header alone.

## Dependencies And Integration Points

This chunk depends on the generated GC 11.5.0 register family remaining synchronized:

- `gc_11_5_0_offset.h` earlier lines define `regSQ_IND_INDEX`, `regSQ_IND_DATA`, and the surrounding GC register offsets used to access these indexed values.
- `gc_11_5_0_sh_mask.h` defines the shift/mask layout for the indexed access register and for any non-indexed GC registers that surround the wave-debug flow.
- `gfx_v11_0.c` is the closest generation-level consumer pattern for GC 11.x wave dumps. It calls a local `wave_read_ind()` helper that writes `regSQ_IND_INDEX` and reads `regSQ_IND_DATA` for `ixSQ_WAVE_*` offsets.
- GFX hang detection, GPU reset diagnostics, debugfs register dumping, KFD compute debugging, and user-space tools that consume AMDGPU wave dumps rely on these index constants being generation-correct.
- The same logical register names appear across older and newer generated headers, but the numeric index values can vary by architecture generation. Code must include the header for the active IP version rather than assuming cross-generation constants are interchangeable.

The integration boundary is intentionally narrow: this header publishes numeric constants; engine code decides when it is safe to sample a wave, how to select the target shader instance, how large the output record is, and how to interpret the returned bits.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong `ixSQ_WAVE_*` value compiles cleanly but causes diagnostics to read the wrong indexed register.
- This chunk starts mid-`sqind` family. `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_GPR_ALLOC`, and `ixSQ_WAVE_LDS_ALLOC` are in the previous chunk, while this chunk covers the remaining values. File-level documentation must merge both chunks to describe a complete wave snapshot map.
- Wave state is volatile. Reading PC, EXEC, M0, scheduler, and instruction-buffer registers from a running wave can produce internally inconsistent snapshots unless the consumer uses a hardware-supported halt, trap, or debug sequence.
- Split registers must be paired correctly. `PC_LO/PC_HI`, `EXEC_LO/EXEC_HI`, and `FLAT_SCRATCH_LO/HI` are separate indices; a stale high half or mismatched low half can misrepresent addresses or lane masks.
- `TTMP0..TTMP15` are contiguous in this chunk. Off-by-one errors are easy because they are a dense sequence from `0x026c` to `0x027b`; a single bad value shifts every temporary register after it.
- The `regSQ_IND_INDEX` packing layout is separate from these index constants. If a caller shifts the index with the wrong generation's `SQ_IND_INDEX__INDEX__SHIFT`, the correct `ixSQ_WAVE_*` macro will still address the wrong hardware location.
- Some entries may be read-only, write-only, side-effecting, or debug-gated by hardware state. The offset header does not encode access permissions or sequencing.
- `ixSQ_WAVE_FLUSH_IB` is particularly sensitive because the name describes a flush action. Treating every `ixSQ_WAVE_*` constant as safe to write or safe to poll would be a bug.
- Cross-generation copy/paste is risky. GC v11, GC v12, and earlier GCA headers share names such as `ixSQ_WAVE_PC_LO` and `ixSQ_WAVE_EXEC_LO`, but consumers must not assume identical numeric offsets without generated-register verification.
- Because this is the final chunk of the file, a missing `#endif` or accidental edit near the guard terminator would break all compilation units that include this generated header.

## Test Signals

Useful validation is mostly generated-data consistency plus runtime diagnostic behavior:

- Build AMDGPU configurations that include GC 11.5.0 register headers and GFX v11 paths. Compilation catches missing or renamed macros such as `ixSQ_WAVE_PC_LO`, `ixSQ_WAVE_EXEC_LO`, `ixSQ_WAVE_HW_ID1`, and `ixSQ_WAVE_IB_STS`.
- Mechanically compare this tail of `gc_11_5_0_offset.h` against AMD's authoritative GC 11.5.0 register database, especially the dense `TTMP0..TTMP15` sequence and the `PC`, `EXEC`, `M0`, `IB_STS`, and `HW_ID` values used in wave dumps.
- Cross-check `regSQ_IND_INDEX`/`regSQ_IND_DATA` offsets and `SQ_IND_INDEX__*` masks in the matching `gc_11_5_0_sh_mask.h` to ensure the indexed access path and index values are from the same generated register set.
- Exercise GPU hang or debug-dump collection on GC 11.5.0 hardware and verify that wave records contain plausible PC values, lane masks, hardware IDs, allocation state, instruction-buffer state, and `M0` values.
- Run compute workloads that intentionally trap, fault, or hang, then confirm `TTMP`, `IB_STS`, `IB_STS2`, `IB_DBG1`, `EXEC`, and PC snapshots align with expected trap-handler/debug behavior.
- Validate split-register consistency in debug tooling: PC high/low and EXEC high/low should be decoded as paired values, not independent unrelated fields.
- Check that indexed SGPR/VGPR read helpers still use the correct `SQ_IND_INDEX__AUTO_INCR` and work-item fields when adjacent wave state reads are added or refactored.
- Runtime warning signals include impossible wave IDs or hardware IDs, all-zero or all-ones PCs for active waves, mismatched EXEC masks, trap temporaries that do not line up with a known trap path, wave dumps changing layout unexpectedly, or hang reports that lose instruction-buffer status fields.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002548`. It covers lines 9968-10002 of `gc_11_5_0_offset.h`, the final tail of the file. The previous chunk contains the opening `sqind` entries, including `ixSQ_DEBUG_STS_LOCAL`, `ixSQ_DEBUG_CTRL_LOCAL`, `ixSQ_WAVE_ACTIVE`, `ixSQ_WAVE_VALID_AND_IDLE`, `ixSQ_WAVE_MODE`, `ixSQ_WAVE_STATUS`, `ixSQ_WAVE_TRAPSTS`, `ixSQ_WAVE_GPR_ALLOC`, and `ixSQ_WAVE_LDS_ALLOC`. The final per-file research should merge those entries with this chunk to present the complete GC 11.5.0 indexed SQ wave register map.
