# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h lines 4984-7461

## Scope

This chunk covers lines 4984 through 7461 of AMD's generated GC 11.0.0 register-offset header. It is a declarative C preprocessor map: each hardware register gets a `reg...` offset macro and a matching `reg..._BASE_IDX` macro. The slice contains 1,203 register offset macros and 1,203 base-index macros.

The range starts inside the tail of `gc_gusdec`, then contains all of `gc_gfxdec0`, several PF/VF and PF-only GC control blocks, the GC CAC/EDC/power weighting block, SPI compute-unit reservation registers, the large `gc_gfxudec` user/config register block, and ends at the opening of `gc_cprs64dec`. There are no functions, structs, enums, branches, allocations, or direct MMIO operations in this header. Runtime behavior comes from AMDGPU code that includes this file and passes the generated symbols to SOC15 register access helpers.

## Purpose

`gc_11_0_0_offset.h` gives AMDGPU symbolic register offsets for the GC 11.0.0 graphics and compute IP. This chunk is centered on graphics context state, PF/VF-visible controls, PF-only power/debug controls, user/config-space surfaces, and the beginning of MES CP register offsets.

The macros let driver code use names such as `regDB_RENDER_CONTROL`, `regCP_MEC_CNTL`, `regDIDT_IND_INDEX`, `regGC_CAC_CTRL_1`, `regSPI_RESOURCE_RESERVE_CU_0`, `regGDS_RD_ADDR`, `regSPI_ATTRIBUTE_RING_SIZE`, and `regCP_MES_CNTL` instead of hard-coded offsets. The paired `BASE_IDX` values tell the SOC15 register infrastructure which base-address table entry to combine with the offset. In this chunk all visible `BASE_IDX` values are `1`, which distinguishes these blocks from earlier low-index SDMA/CP/GDS blocks that use base index `0`.

## Exported API Surface

The public surface is macro-only:

- `reg<REGISTER>`: generated register offset inside a GC 11.0.0 address block.
- `reg<REGISTER>_BASE_IDX`: generated SOC15 base-index selector for the same register.
- The surrounding header guard is `_gc_11_0_0_OFFSET_HEADER`, defined near the top of the full file outside this chunk.

Important address blocks in this slice are:

- `gc_gusdec` tail, base `0x33000`: GUS IO/DRAM priority quantum, combine/flush, SDP arbitration/credits/reserves, error/status, misc, and L1 channel/shader-array counters.
- `gc_gfxdec0`, base `0x28000`: DB, PA, VGT, CB, SX, GE, SPI, SQ, SQC, TA, GDS, and related graphics context offsets. This is the largest block in the chunk, with 519 register offset macros.
- `gc_pfvf_cpdec`, `gc_pfvf_grbmdec`, `gc_pfvf_padec`, and `gc_pfvf_sqdec`: registers intended to be visible in PF/VF flows, including CP engine control, GRBM addressing, PA scanner/binning/VRS/enhance controls, SQ runtime/debug state, shader trap base addresses, and shader memory configuration.
- `gc_pfonly_*` blocks: PF-only CP, HQD, DIDT, SPI, TCP, GDS, UTCL1, PMM/GCR, and CAC/EDC/power-management offsets.
- `gc_sedcdec`: SEDC GL1/GL2 override offset.
- `gc_pfonly_gccacdec`: GC and shader-engine CAC aggregation, EDC controls, throttle status, stall-pattern controls, indirect CAC access, and per-unit weight registers.
- `gc_pfonly2_spidec`: SPI per-CU resource reservation and enable masks for CU indices 0-15.
- `gc_gfxudec`, base `0x30000`: user/config-style graphics registers including scratch/user data, context controls, shader program resources, dispatch/draw controls, streamout counters, GDS direct/atomic access, occlusion counters, and SPI attribute-ring state.
- `gc_cprs64dec`, base `0x32000`: the start of MES CP register offsets, including `regCP_MES_PRGRM_CNTR_START`, `regCP_MES_INTR_ROUTINE_START`, `regCP_MES_MTVEC_LO/HI`, `regCP_MES_CNTL`, pipe priority registers, header dump, and interrupt-enable registers.

## Register Areas Covered

The `gc_gusdec` tail supplies arbitration and quality-of-service knobs for graphics memory or fabric traffic. The visible names cover IO read/write priority quantums, DRAM priority aging and urgency, SDP virtual-channel priority, tag/VCC/VCD reservation, SDP request control, error status, and L1 channel or shader-array command/data counters. Since the chunk begins mid-block, earlier GUS combine and priority controls are outside this item and must be merged from the preceding chunk.

`gc_gfxdec0` maps graphics pipeline context state. Its families include DB depth/stencil/render controls; PA scissor, viewport, primitive, binning, VRS, raster, and clip/setup state; VGT index, draw, geometry, primitive, instance, and streamout state; CB color target base, view, info, DCC, clear-word, attribute, and blend state; SX and shader export state; GE and WD controls; SPI shader/program interpolation and wave limits; SQ/SQC debug/cache surfaces; TA constant-buffer base registers; GDS direct and atomic access; streamout counters; occlusion counters; and the SPI attribute ring. This is the register-address layer used by command submission, context save/restore, debugging, and hang dumps; the actual bit fields live in the matching shift/mask header.

The PF/VF-visible blocks expose the subset of CP, GRBM, PA, and SQ controls that virtualization paths can legally address. `regCONFIG_RESERVED_REG0/1`, `regCP_MEC_CNTL`, and `regCP_ME_CNTL` are CP controls; `regGRBM_GFX_CNTL` selects graphics address routing; PA entries cover binner, VRS, trap-screen lock, interface FIFO, packer, and enhancement controls; SQ entries cover runtime/debug state plus shader TBA/TMA and shared memory base/config registers.

The PF-only blocks contain registers that should not be directly owned by virtual functions. They include CP debug/fetcher controls, HPD/ROQ status, DIDT EDC throttle/threshold/stall/status and indirect index/data, SPI trap/debug/arbiter/resource-limit controls, TCP invalidate/status/debug, GDS enhancement and OA clock-gating restore, UTCL1 invalidation and FIFO/GCRD controls, PMM/GCR command/status controls, and SEDC overrides.

`gc_pfonly_gccacdec` is power and activity accounting heavy. It maps GC-wide and per-shader-engine CAC aggregation windows, GFXCLK cycle counters, EDC stretch/unstretch counters, throttle control/status, PCC/PWRBRK/DIDT stall-pattern tables, hysteresis, indirect CAC access, and many per-client weight registers for CP, EA, UTCL2, GDS, GE, PMM, RLC, SQ, SP, LDS, SQC, CU, CB, DB, RMI, SX, UTCL1, GL1C, SPI, PC, PA, and SC. These offsets are sensitive because they feed power/thermal throttling and telemetry code.

`gc_pfonly2_spidec` contributes the per-CU SPI reservation surface: `regSPI_RESOURCE_RESERVE_CU_0` through `_15` and `regSPI_RESOURCE_RESERVE_EN_CU_0` through `_15`. These controls are likely consumed by firmware or privileged driver paths that reserve compute resources for queues, debug, or scheduling policy.

`gc_gfxudec` is a broad user/config block. It includes scratch registers; `CP_STRMOUT_CNTL`; context controls and anti-hang state; `COMPUTE_*` queue, dispatch, shader resource, trap, scratch, threadgroup, and user-data registers; `GE_*`, `VGT_*`, `PA_*`, `DB_*`, `CB_*`, `SPI_*`, `SQ_THREAD_TRACE_*`, `SQC_CACHES`, TA constant-buffer base, DB occlusion counters, GDS direct/atomic accessors, GDS streamout counters, and the attribute-ring registers. Many of these are programmed by graphics packets or queue setup and later sampled by driver diagnostics.

The `gc_cprs64dec` portion is only the first 14 offsets of the block. It introduces MES command processor state and aliases: `regCP_MES_INTR_ROUTINE_START` shares offset `0x2801` with `regCP_MES_MTVEC_LO`, and `regCP_MES_INTR_ROUTINE_START_HI` shares offset `0x2802` with `regCP_MES_MTVEC_HI`. This aliasing is intentional generated-header behavior but is a useful merge-time risk marker.

## Control Flow And State Behavior

There is no local control flow. The generated offsets become runtime behavior when included code calls SOC15 helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_FIELD15`, `REG_SET_FIELD`, or `REG_GET_FIELD`.

The state represented by this chunk is hardware MMIO state:

- Graphics context registers persist until context switch, clear-state load, queue command programming, reset, or power-gating domain loss.
- PF/VF-visible registers participate in virtualization-safe programming paths; PF-only registers require privileged ownership and should not be exposed to VF code without mediated access.
- DIDT, CAC, EDC, PCC, PWRBRK, and throttle registers hold power/thermal accounting, thresholds, status, and stall policy that can affect clocks, performance, and protection behavior.
- SPI CU reservation registers persist privileged scheduling/resource policy for compute units.
- `gc_gfxudec` compute, shader, scratch, GDS, streamout, occlusion, and trace registers reflect per-queue, per-context, or debug state programmed by command streams or kernel queue setup.
- MES CP state at the end of the chunk controls firmware command processor start vectors, interrupt vectors, priorities, and enables.

No software persistence is implemented here. These are compile-time constants. Actual persistence and reset behavior depend on ASIC reset domains, PF/VF ownership, firmware programming, command processor context save/restore, and driver write ordering.

## Dependencies And Integration Points

This file depends only on the C preprocessor syntactically, but it is part of a generated register-header set:

- `gc_11_0_0_offset.h` provides offsets and base indices.
- `gc_11_0_0_sh_mask.h` provides field shifts and masks for many of the same register names.
- `gc_11_0_0_default.h` provides full-register default values for many names in this chunk.

Direct include users in this tree include `amdgpu/gfx_v11_0.c`, `amdgpu/gfxhub_v3_0.c`, `amdgpu/mes_v11_0.c`, `amdgpu/imu_v11_0.c`, `amdgpu/sdma_v6_0.c`, `amdgpu/soc21.c`, `amdgpu/amdgpu_amdkfd_gfx_v11.c`, `amdkfd/kfd_device_queue_manager_v11.c`, and `amdkfd/kfd_mqd_manager_v11.c`. `gfx_v11_0.c` includes this header and builds register dump lists with chunk symbols such as `regCP_MES_CNTL`, `regCP_HQD_*`, `regGDS_*`, `regSQC_CACHES`, and graphics status registers. It also programs HQD/MQD queue state using offsets from the same GC 11 namespace. `mes_v11_0.c` reads and writes `regCP_MES_CNTL` and programs HQD queue registers. `gfxhub_v3_0.c` pairs this offset header with the shift/mask and default headers to program GCVM/GCMC state from earlier file chunks.

`soc21.c` uses `SOC15_REG_OFFSET(GC, 0, regDIDT_IND_INDEX)` and `regDIDT_IND_DATA`, which are defined in the PF-only DIDT block in this slice, for indirect DIDT access. KFD v11 queue-management code includes this header for CP/HQD/SQ/GDS register names used in MQD load/unload and compute queue control.

The generated offsets are also tied to firmware-facing surfaces: `gfx_v11_0.c` declares GC 11 PFP/ME/MEC/RLC firmware blobs, while this chunk exposes MES and CP/HQD/MEC controls that must match firmware expectations for queue scheduling, preemption, and context management.

## Risks

- Generated-register drift is the main risk. If any offset or base index diverges from the ASIC register database, SOC15 reads and writes will hit the wrong MMIO address.
- The chunk starts and ends mid-block. Merge/reconciliation must combine neighboring chunks before making whole-block claims about `gc_gusdec` or `gc_cprs64dec`.
- All visible base-index macros are `1`; a mistaken `0`/`1` base-index change can be as damaging as a wrong offset because SOC15 address calculation changes the final MMIO target.
- PF/VF versus PF-only boundaries matter. Accidentally using `gc_pfonly_*` offsets in VF paths can cause access faults, no-ops, security issues, or inconsistent virtualized GPU state.
- Several registers are aliases or repeated families. The MES vector aliases at offsets `0x2801` and `0x2802`, repeated CB color target arrays, per-CU SPI reservation arrays, and per-client CAC weights all need generation consistency checks.
- Power and throttle registers in DIDT/CAC/EDC/PCC/PWRBRK blocks are high impact. Wrong programming can create performance cliffs, thermal throttling problems, hangs, or misleading telemetry.
- Graphics context offsets cover command-stream-programmed state. Wrong DB/PA/VGT/CB/SPI/SQ offsets can surface as rendering corruption, GPU hangs, failed context restore, bad shader dispatch, or unusable debug traces.
- Some names in `gc_gfxudec` are naturally packet-programmed user/config registers, while others are status or debug registers. The offset header does not encode access permissions, clear-on-read behavior, write-one-to-clear behavior, or firmware ownership.

## Test Signals

Good validation signals are mostly build-time, generated-header, and hardware-integration checks:

- Build AMDGPU with GC 11 support enabled so all include users of `gc_11_0_0_offset.h` compile, especially `gfx_v11_0.c`, `mes_v11_0.c`, `gfxhub_v3_0.c`, `soc21.c`, and KFD v11 queue-management files.
- Static generation checks should confirm that every `reg...` macro in this chunk has exactly one matching `reg..._BASE_IDX` macro and, where fields/defaults are expected, corresponding entries in `gc_11_0_0_sh_mask.h` and `gc_11_0_0_default.h`.
- Register-dump tests from `gfx_v11_0.c` should successfully read chunk-defined CP/MES/HQD, GDS, SQ/SQC, and status registers without invalid-address faults.
- Graphics workloads should cover clear-state/context programming, viewport/scissor, VRS/binning, primitive assembly, streamout, depth/stencil, render target color, occlusion queries, and shader trace/debug paths.
- Compute/KFD tests should cover MQD creation/load/unload, HQD programming, VMID/PASID queue ownership, AQL dispatch, trap TBA/TMA programming, scratch/user-data registers, preemption, and MES scheduling.
- Virtualization tests should verify that PF/VF-visible registers are usable from VF-mediated flows while PF-only blocks remain PF-controlled.
- Power-management tests should monitor DIDT/CAC/EDC/PCC/PWRBRK throttle status, power telemetry, stall counters, and suspend/resume behavior after touching GC 11 power and throttle code.
- Low-level register tests should verify `SOC15_REG_OFFSET(GC, 0, regDIDT_IND_INDEX)` and `regDIDT_IND_DATA` indirect access, plus `regCP_MES_CNTL` reads/writes in MES bring-up and halt/resume paths.

## Chunk Notes For Merge

This document is source-tree aligned and covers only `gc_11_0_0_offset.h` lines 4984-7461. It should be merged with adjacent chunk documents before producing the final per-file report. The preceding chunk is needed for the beginning of `gc_gusdec`; the following chunk is needed for the rest of `gc_cprs64dec` and later address blocks. The final report should treat this file as one generated GC 11.0.0 offset/base-index map paired with the matching default and shift/mask headers, with this chunk contributing the graphics-context, PF/VF, PF-only power/debug, user/config, and initial MES CP coverage.
