# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002713`: lines 1-4698, `Docs/researches/chunks/subset-b-002713_research.md`
- `subset-b-002714`: lines 4699-9309, `Docs/researches/chunks/subset-b-002714_research.md`
- `subset-b-002715`: lines 9310-13970, `Docs/researches/chunks/subset-b-002715_research.md`
- `subset-b-002716`: lines 13971-19163, `Docs/researches/chunks/subset-b-002716_research.md`
- `subset-b-002717`: lines 19164-20836, `Docs/researches/chunks/subset-b-002717_research.md`

## Chunk Research

### subset-b-002713: lines 1-4698

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 1-4698

## Purpose

This chunk is the opening slice of the generated AMD GFX 8.0 register shift/mask header. It defines preprocessor constants for hardware register fields in the GCA/GFX8 block: every field has a `*_MASK` literal and a matching `*__SHIFT` literal that callers use to construct, update, or decode 32-bit MMIO register values.

The chunk covers three major hardware areas:

- Color buffer (`CB`) render target state and diagnostics, including blend state, color target base/pitch/slice/view, color target format and compression metadata, CMASK/FMASK/DCC addresses, target/shader masks, CB performance counters, clock gating, and CB debug bus fields.
- Command processor (`CP`, `CPC`, `CPF`, `CPG`, `CP_HQD`, `CP_MQD`) queue, interrupt, microcode, coherency, DMA, scratch, ring/IB, performance, and compute queue state.
- Depth buffer (`DB`) state through the start of `DB_DEBUG3`, including depth/stencil surface layout, render control/override, shader depth/stencil export control, HTILE/preload/stencil-ref state, DB performance counters, and debug/optimization-disable fields.

The chunk is not a complete header by itself. It starts with the include guard and ends mid-file at `DB_DEBUG3__ALLOW_RF2P_RW_COLLISION__SHIFT`; later chunks continue the rest of `gfx_8_0_sh_mask.h`.

## Important APIs, Types, And Data

This file defines no functions, structs, enums, or storage. Its API surface is macro data consumed by AMDGPU register helpers and by code that fills GPU queue descriptors.

Important macro families in this chunk:

- `CB_BLEND*_CONTROL` and `CB_COLOR_CONTROL` define source/destination blend factors, blend combine functions, separate-alpha behavior, ROP3 control, degamma, and color-control mode bits.
- `CB_COLOR[0-7]_{BASE,PITCH,SLICE,VIEW,INFO,ATTRIB}` define render target addresses and layout: 256-byte base fields, tile maxima, slice start/max, format, endian, number type, component swap, fast clear/compression/DCC/CMASK fields, tile mode, sample and fragment count fields.
- `CB_COLOR[0-7]_{DCC_CONTROL,CMASK,CMASK_SLICE,FMASK,FMASK_SLICE,CLEAR_WORD0,CLEAR_WORD1,DCC_BASE}` define auxiliary color compression and fast-clear state.
- `CB_TARGET_MASK`, `CB_SHADER_MASK`, `CB_HW_CONTROL*`, `CB_DCC_CONFIG`, `CB_PERFCOUNTER*`, `CB_CGTT_SCLK_CTRL`, and `CB_DEBUG_BUS_17` through `CB_DEBUG_BUS_22` expose target write masks, CB cache/overwrite-combiner tuning, performance counter selection/data, clock gating delays/overrides, and debug-bus busy/credit signals.
- `CP_RB*`, `CP_IB*`, `CP_CE_IB*`, `CP_ST_*`, `CP_ROQ*`, `CP_STQ*`, `CP_MEQ*`, and `CP_CEQ*` define command ring, indirect buffer, state buffer, read-order queue, state queue, micro-engine queue, and constant-engine queue base, size, pointer, threshold, and status fields.
- `CP_INT_*`, `CPC_INT_*`, `CP_ME[12]_PIPE*_INT_*`, `CP_*_INT_STAT_DEBUG`, and `CP_*_F32_*` define interrupt enable, status, and debug fields for graphics and compute command processor paths. These include doorbell, ECC, timeout, busy/context, privileged access, opcode, timestamp, reserved-bit, dequeue, query-status, and generic interrupt bits.
- `CP_RB_DOORBELL_*`, `CP_MEC_DOORBELL_*`, `CP_HQD_PQ_DOORBELL_CONTROL`, and queue pointer poll registers define how host writes and doorbells wake hardware queues.
- `CP_PFP_UCODE_*`, `CP_CE_UCODE_*`, `CP_MEC_ME[12]_UCODE_*`, `CP_ME_RAM_*`, and program-counter/intr-routine start fields define microcode and instruction-memory access/control metadata.
- `CP_COHER_*` and `COHER_DEST_BASE*` define CP surface-sync/coherency actions for CB, DB, TC/TCL1, shader instruction/cache, destination-base ranges, and coherency status.
- `CP_DMA_{ME,PFP}_*`, atomic-preop, GDS atomic, append, semaphore, wait-reg-mem, EOP done, stream-out, pipe stats, and primitive/invocation count registers define packet-side memory operations and counters.
- `CP_HQD_*` and `CP_MQD_*` define compute queue descriptor state: queue active/VMID/persistence/quantum, PQ/IB/EOP bases and pointers, queue control, IQ timer/dequeue/offload/semaphore/message fields, context-save metadata, GDS resource state, and HQD error state.
- `DB_*` macros in this chunk define depth/stencil base addresses, surface tiling, Z/stencil formats, render control, Z/stencil count control, render overrides, EQAA, shader export/depth ordering, bounds/clear values, HTILE, preload, stencil ref/mask state, DB performance counters, and debug bits.

The paired GFX8 offset header supplies the register addresses for these field definitions; for example `gfx_8_0_d.h` defines `mmCB_COLOR0_INFO` at `0xa31c`, `mmCP_COHER_CNTL` at `0xc07c`, `mmCP_HQD_PQ_CONTROL` at `0x3256`, and `mmDB_DEPTH_CONTROL` at `0xa200`.

## Control Flow

There is no executable control flow in this chunk. The C preprocessor exposes field masks and shifts at compile time. Runtime behavior is supplied by callers that:

- build register values with left shifts and masks, or with AMDGPU helpers such as `REG_SET_FIELD`;
- write those values to GFX8 MMIO registers named by sibling `gfx_8_0_d.h` offsets;
- decode status, interrupt, busy, performance counter, queue pointer, or debug fields from MMIO reads.

The practical flow for a field is usually: read or initialize a 32-bit value, clear the field mask, insert `value << FIELD__SHIFT`, and write the register. Queue-descriptor paths often assemble fields directly into an MQD memory image instead of immediately writing MMIO.

## State And Persistence Behavior

The macros are stateless compile-time constants. The state they describe lives in GPU registers, queue descriptors, or memory-mapped ring/queue metadata.

- CB and DB render state persists in GPU context/register state until overwritten, context-switched, reset, or invalidated by a command stream. Compression-related fields such as DCC, CMASK, FMASK, HTILE, fast clear, and render override bits affect how color/depth surfaces are interpreted and synchronized.
- CP ring and queue fields describe persistent runtime scheduling state: ring bases, read/write pointers, doorbell offsets/ranges, VMIDs, priority counts, queue sizes, IB bases/sizes, EOP rings, context-save areas, and MQD/HQD fields. KFD queue creation code writes many of these into MQD structures, so incorrect field definitions can persist for the lifetime of a compute queue.
- Interrupt enable/status fields configure and observe GPU interrupt state. Status and debug fields may be sticky or hardware-latched depending on the register contract, while enable fields persist until the driver reprograms them or hardware resets.
- Performance counter and debug fields are volatile hardware telemetry. Counter low/high pairs represent sampled hardware counts and can wrap; debug bus and busy/stalled fields reflect instantaneous or latched internal pipeline state.
- Coherency fields describe cache flush/invalidate/surface-sync operations and the address ranges those operations target. These are central to making CB/DB/TC/shader cache effects visible in the right order.

No filesystem persistence is implemented here. Durable policy comes from the driver, firmware, user queue setup, or command streams that use these constants.

## Dependencies

Direct dependencies are generated-register metadata and AMDGPU helper conventions:

- `gfx_8_0_d.h` provides the matching GFX8 register offsets for the field names in this chunk.
- `gfx_8_0_enum.h` and related ASIC headers provide symbolic field values where code does not use raw literals.
- Register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` rely on the exact `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` naming convention.
- KFD MQD and queue management code depends on CP/HQD/MQD field definitions matching the MQD layout for GFX8.
- Power-management and SMU support code includes this GFX8 mask header for register-level control of older Sea Islands/Volcanic Islands-era hardware paths.

The constants are ASIC-generation-specific. Similar names exist in GFX7, GFX8.1, GC9, and later GC headers, but masks and shifts can differ. Code must include the matching header for the target ASIC.

## Integration Points

Concrete consumers in this tree include:

- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c`, which includes `gca/gfx_8_0_sh_mask.h` and uses fields such as `CP_HQD_PQ_CONTROL__RPTR_BLOCK_SIZE__SHIFT`, `CP_HQD_PQ_CONTROL__PQ_ATC__SHIFT`, `CP_HQD_PQ_CONTROL__MTYPE__SHIFT`, `CP_HQD_PQ_CONTROL__NO_UPDATE_RPTR_MASK`, `CP_HQD_PQ_CONTROL__SLOT_BASED_WPTR__SHIFT`, `CP_HQD_PQ_CONTROL__PRIV_STATE__SHIFT`, and `CP_HQD_PQ_CONTROL__KMD_QUEUE__SHIFT` while constructing VI MQDs.
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c`, which includes this header for GFX8 queue management paths.
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.c` and `drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h`, which include this header for SMU/PowerPlay register access on the relevant generation.
- Generic AMDGPU register programming patterns in GFX code that combine offset headers, `*_sh_mask.h` fields, and `REG_SET_FIELD`/masked writes for CP interrupts, ring control, doorbells, cache coherency, ME/MEC control, and render/depth state.
- Command stream and queue-descriptor ABI surfaces. The `CP_HQD_*`, `CP_MQD_*`, and `CP_RB*` fields are part of the software/hardware contract for compute queue setup and dispatch.

## Risks

- Mask/shift drift is high impact. A one-bit error can program the wrong render target format, compression mode, queue control bit, doorbell offset, interrupt enable, or coherency action.
- Cross-generation reuse is unsafe. Nearby GFX7/GFX8.1/GC9 headers contain similarly named fields with different masks, missing fields, or extra fields.
- Partial masked writes can preserve stale bits if callers do not clear the full mask before setting a field. This is especially risky for CB/DB compression flags, CP coherency actions, queue privilege/KMD bits, and interrupt enable/status registers.
- Address fields use implicit alignment units such as 256-byte bases or low-address masks starting at bit 2, 3, 5, or 12. Passing byte addresses without required shifting/alignment can point hardware at the wrong memory.
- Queue state fields influence scheduling, preemption, VMID ownership, doorbell behavior, and context save/restore. Incorrect `CP_HQD_*` or `CP_MQD_*` fields can hang queues, corrupt context state, or make user queues run with unintended privilege/cache policy.
- CB/DB compression and fast-clear fields must align with metadata allocations and cache/coherency programming. Mismatches can produce rendering corruption that only appears under MSAA, DCC/HTILE, fast clear, or resolve paths.
- Debug and performance counter fields are often hardware-diagnostic and may have side effects or generation-specific interpretation. Treating them as stable ABI without hardware documentation can mislead diagnostics.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for GFX8 AMDGPU/KFD/SMU paths that include `gca/gfx_8_0_sh_mask.h`.
- Static checks that each line-1-4698 register field has both a `*_MASK` and matching `*__SHIFT`, and that the paired register exists in `gfx_8_0_d.h` when it represents an MMIO register rather than an MQD memory field.
- KFD VI queue smoke tests that create, run, suspend, and destroy compute queues, then verify MQD fields such as `cp_hqd_pq_control`, doorbell offsets, VMID, PQ/IB/EOP bases, and read/write pointer reporting behave correctly.
- Graphics render tests covering color target formats, blend modes, MRT masks, MSAA/FMAsk/CMASK, DCC/fast clear, depth/stencil formats, HTILE, depth bounds, alpha-to-mask/EQAA, and DB render overrides.
- Interrupt tests that enable/disable CP and CPC/ME pipe interrupt bits and verify expected interrupt status/debug bits without spurious privileged-register, opcode, reserved-bit, or timeout interrupts.
- Coherency and synchronization tests that exercise CB/DB/TC/shader-cache invalidation and writeback paths after render, compute, DMA, stream-out, and EOP events.
- Performance/debug validation on real GFX8 hardware: counters should increment under targeted workloads, busy/stalled fields should correlate with induced stalls, and 64-bit low/high counter reads should handle wraparound.

### subset-b-002714: lines 4699-9309

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 4699-9309

## Scope

This chunk covers a generated mask/shift section of the AMD GFX 8.0 graphics register bitfield header. It begins in the middle of `DB_DEBUG3`, then spans depth-buffer backend controls, render-backend and graphics-buffer addressing, RAS signatures, GRBM global status/debug/perf/reset state, PA clip/setup/scan-converter/rasterization state, clipper and setup debug buses, compute dispatch/context state, CSPRIV thread-trace state, and a large RLC power-management/microcontroller/performance/save-restore block.

The file is hardware ABI data. The chunk contains only C preprocessor constants following the AMDGPU convention:

- `<REGISTER>__<FIELD>_MASK`
- `<REGISTER>__<FIELD>__SHIFT`

There are no functions, structs, variables, runtime branches, dynamic allocation, or direct MMIO operations in this chunk.

## Purpose

The purpose of this chunk is to define how GFX8 register fields are packed into 32-bit values. Driver code includes this header with the matching GFX8 offset header and uses the masks and shifts through register helper macros to compose writes and decode reads without open-coding bit positions.

This section is centered on fixed-function graphics and GPU-management state:

- DB fields for depth/stencil backend credits, watermarks, cachelines, MSAA subtile placement, debug controls, z-pass and occlusion counters.
- GB/CC/GC fields for render-backend redundancy, backend disable maps, pipe/bank/shader-engine tiling, tile/macro-tile mode tables, EDC, and GPU ID mapping.
- GRBM fields for global graphics idle/busy status, per-shader-engine busy/clean state, soft reset, broadcast indexing, read/write error diagnostics, scratch registers, and global/per-SE perf counters.
- PA/SC/SU/CL fields for viewport transform, clip/cull distances, guard-band settings, primitive setup, polygon offset, culling, line and point state, scissor/viewport rectangles, MSAA sample locations, raster config, scan-converter modes, and debug buses.
- COMPUTE and CSPRIV fields for dispatch initiation, grid and thread dimensions, program resources, scratch/temp ring state, CU masks, user SGPR data, doorbell/queue/VMID connection, and thread trace group metadata.
- RLC fields for the run-list controller and graphics power management: enable/safe mode, memory-controller request attributes, clock/power gating, load balancing, GPM microcode/scratch/logging, SERDES master control, save/restore memory, SRM commands, SPM performance rings, SMU/CP handshakes, and power-state status.

## Important Macro Families

### DB Depth Backend

`DB_DEBUG3` and `DB_DEBUG4` expose debug and workaround toggles such as disabling TC write combine paths, DB process reset insertion/deletion, QC mask summation, pre/post-Z conflict stalls, and delayed/interleaved MSAA behavior. These are low-level tuning and erratum-facing controls rather than API-visible state.

`DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH1`, and `DB_FIFO_DEPTH2` describe internal queue/cacheline capacity and panic/flush behavior between DB, SC, CB, memory clients, and tile/quad FIFOs. `DB_SUBTILE_CONTROL` maps X/Y subtile positions for 1x, 2x, 4x, 8x, and 16x MSAA. `DB_CGTT_CLK_CTRL_0` controls DB clock-gating delay/hysteresis and soft overrides.

`DB_ZPASS_COUNT_*`, `DB_OCCLUSION_COUNT*_LOW/HI`, `DB_RING_CONTROL`, and `DB_READ_DEBUG_*` provide counter and debug-read fields for depth pass/occlusion queries and backend diagnostics.

### CC, GC, GB, EDC, and RAS

`CC_RB_REDUNDANCY`, `GC_USER_RB_REDUNDANCY`, `CC_RB_BACKEND_DISABLE`, and `GC_USER_RB_BACKEND_DISABLE` describe failed render-backend lanes, redundancy enable bits, and backend-disable masks. `CC_RB_DAISY_CHAIN` packs the eight render-backend daisy-chain slots.

`GB_ADDR_CONFIG` is the main graphics address layout descriptor: pipe count, pipe/bank interleave, shader-engine count, shader-engine tile size, multi-GPU tile size, row size, and lower-pipe configuration. `GB_BACKEND_MAP` and `GB_GPU_ID` identify backend/GPU routing. `GB_TILE_MODE0` through `GB_TILE_MODE31` repeat the same fields for array mode, pipe config, tile split, micro-tile mode, and sample split. `GB_MACROTILE_MODE0` through `GB_MACROTILE_MODE15` repeat bank width/height, macro-tile aspect, and number-of-banks fields. These mode tables must agree with surface tiling metadata used by memory management and user-mode drivers.

`GB_EDC_MODE` and `CC_GC_EDC_CONFIG` define EDC behavior, including DED mode, SEC-on-DED propagation, bypass, and disable bits. `RAS_SIGNATURE_CONTROL`, `RAS_SIGNATURE_MASK`, and the `RAS_*_SIGNATURE*` registers expose signature capture for graphics blocks such as SX, DB, PA, VGT, SQ, SC, IA, SPI, TA, TD, CB, and BCI.

### GRBM Global Graphics Management

`GRBM_STATUS`, `GRBM_STATUS2`, and `GRBM_STATUS_SE0` through `GRBM_STATUS_SE3` are central busy/idle observation registers. They expose command FIFO availability, SRBM/CP/RLC/request-pending state, DB/CB clean bits, and busy bits for TA, GDS, WD, VGT, IA, SX, SPI, BCI, SC, PA, DB, CP, CPF, CPC, CPG, TC, and GUI activity. Driver idle-wait, reset, and diagnostics code depends on these fields.

`GRBM_SOFT_RESET` defines reset bits for CP, RLC, GFX, CPF, CPC, CPG, and CAC. `GRBM_GFX_INDEX` selects instance/shader-array/shader-engine addressing and broadcast-write behavior. `GRBM_CNTL`, `GRBM_PWR_CNTL`, `GRBM_GFX_CLKEN_CNTL`, `GRBM_WAIT_IDLE_CLOCKS`, and `GRBM_DEBUG` cover read timeouts, power requests/responses, clock enable timing, idle-wait timing, and debug/trap behavior.

`GRBM_READ_ERROR`, `GRBM_READ_ERROR2`, and `GRBM_WRITE_ERROR` expose fault addresses, requesters, pipe/ME identifiers, and read/write error flags. `GRBM_DEBUG_SNAPSHOT` captures ready signals for CPF/CPG/SRBM, WD, GDS, and per-SE SPI paths. `GRBM_PERFCOUNTER*_SELECT`, `GRBM_SE*_PERFCOUNTER_SELECT`, and corresponding LO/HI counter registers configure and read global and per-shader-engine performance counters. `GRBM_SCRATCH_REG0` through `GRBM_SCRATCH_REG7`, `DEBUG_INDEX`, `DEBUG_DATA`, and `GRBM_NOWHERE` are general diagnostic/scratch access points.

### PA Clip, Setup, Rasterization, and Debug

`PA_CL_VPORT_*` covers 16 viewport scale/offset sets for X/Y/Z. `PA_CL_VTE_CNTL`, `PA_CL_VS_OUT_CNTL`, `PA_CL_NANINF_CNTL`, and `PA_CL_CLIP_CNTL` define viewport-transform enables, vertex position formats, VS output sideband usage, clip/cull-distance enables, NaN/Inf handling, user clip planes, DX clip-space mode, rasterization kill, and near/far Z clip disables.

`PA_CL_GB_*_CLIP_ADJ`, `PA_CL_GB_*_DISC_ADJ`, `PA_CL_UCP_*`, and point-size/radius registers are full-width data-register masks used for guard-band, user clip plane, and point parameters. `PA_CL_ENHANCE` and `PA_CL_RESET_DEBUG` expose clipper sequencing/debug/erratum bits.

`PA_SU_*` covers setup state: vertex pixel-center and quantization modes, point size and min/max, line width/stipple controls, primitive filtering and expansion, face culling, polygon mode, provoking vertex, perspective correction disable, polygon offset format/clamp/front/back scale/offset, hardware screen offset, and setup perf/debug registers.

`PA_SC_*` covers scan converter state: MSAA enable and AA config, line and edge rules, tile walk/order modes, multi-GPU/supertiling/out-of-order controls, raster config and raster config 1, generic/screen/window/viewport scissors for 16 viewports, Z min/max for 16 viewports, sample locations for each 2x2 pixel quadrant and 16 samples, centroid priority, clip rectangles/rules, screen extent controls, FIFO sizing, EOV force counts, trap-screen counters, performance counters, and debug registers.

`CLIPPER_DEBUG_REG00` through `CLIPPER_DEBUG_REG19`, `SXIFCCG_DEBUG_REG0` through `SXIFCCG_DEBUG_REG3`, and `SETUP_DEBUG_REG0` through `SETUP_DEBUG_REG5` decode internal debug buses: FIFO valid/full/empty/write/advance states, primitive validity, clip-code state, vertex-store indices, state-machine state, event IDs, output counters, SX pending reads, setup sort coordinates, primitive type, backfacing/null/clipped flags, and clock-valid indicators.

### Compute and CSPRIV State

`COMPUTE_DISPATCH_INITIATOR` defines dispatch-start behavior: compute shader enable, partial threadgroup enable, forced start origin, ordered append controls, thread-dimension use, order/cache controls, scalar/vector L1 volatile invalidation, ATC, and restore dispatch mode. `COMPUTE_DIM_*`, `COMPUTE_START_*`, `COMPUTE_RESTART_*`, and `COMPUTE_NUM_THREAD_*` define grid dimensions, starts/restarts, and full/partial thread counts.

`COMPUTE_PGM_LO/HI`, `COMPUTE_TBA_*`, `COMPUTE_TMA_*`, `COMPUTE_PGM_RSRC1`, and `COMPUTE_PGM_RSRC2` define shader program addresses and resource requirements: VGPRs, SGPRs, priority, float mode, privilege, IEEE/DX10 clamp/debug modes, scratch, user SGPR count, trap present, TGID/TG size enables, TIDIG component count, LDS size, and exception enable bits. `COMPUTE_RESOURCE_LIMITS`, `COMPUTE_STATIC_THREAD_MGMT_SE0` through `SE3`, and `COMPUTE_TMPRING_SIZE` define wave/threadgroup limits, CU masks, and temporary ring sizing.

`COMPUTE_USER_DATA_0` through `COMPUTE_USER_DATA_15`, `COMPUTE_VMID`, dispatch/threadgroup IDs, relaunch payloads, thread trace enable, wave restore address/control, and `COMPUTE_NOWHERE` are per-dispatch/context support registers. `CSPRIV_CONNECT` binds doorbell offset, queue ID, VMID, and unordered-dispatch mode. `CSPRIV_THREAD_TRACE_TG*` and `CSPRIV_THREAD_TRACE_EVENT` expose traced threadgroup coordinates, wave ID base, group size, partial/first/last flags, and event ID.

### RLC, GPM, Power, Save/Restore, and SPM

`RLC_CNTL`, `RLC_STAT`, `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, `RLC_SMU_SAFE_MODE`, `RLC_RLCV_COMMAND`, and `SMU_RLC_RESPONSE` define RLC enable/step/debug/reset behavior, busy bits, safe-mode command/message/response fields, RLCV command fields, and SMU response payloads.

`RLC_MC_CNTL` defines RLC memory-controller read/write request attributes such as swap, transaction type, privilege, urgent levels, stalls, and write DWORD masks. `RLC_MEM_SLP_CNTL`, `CGTT_RLC_CLK_CTRL`, `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` cover memory light/deep sleep, clock-gating delay/hysteresis, MGCG enable, CGCG/CGLS enable, idle thresholds, controller selection, sleep mode, and ramp timing.

`RLC_PG_CNTL`, `RLC_PG_DELAY`, `RLC_PG_DELAY_2`, `RLC_PG_DELAY_3`, `RLC_GPM_STAT`, `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, and `RLC_AUTO_PG_CTRL` define graphics/CU/pipeline power-gating policy, SMU/CHUB handshakes, quick PG, per-CU dynamic/static power status and requests, delays/timeouts, always-on CU masks, max powered-up CU count, and automatic register-save/power-gate thresholds.

`RLC_LB_*`, `RLC_THREAD1_DELAY`, and `RLC_CU_STATUS` support CU load balancing and power-down decisions: counters, initial/always-active CU masks, sample windows, idle sample intervals, and work-pending masks. `RLC_GPM_THREAD_ENABLE`, `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_RESET`, and `RLC_GPM_VMID_THREAD*` define GPM thread enable/reset/priority and VMID/queue mapping.

`RLC_GPM_UCODE_ADDR/DATA`, `RLC_HYP_GPM_UCODE_ADDR/DATA`, `RLC_UCODE_CNTL`, `RLC_GPM_GENERAL_*`, `RLC_GPM_SCRATCH_*`, `RLC_GPM_LOG_*`, `RLC_GPM_INT_*`, and `RLC_GPR_REG*` expose GPM firmware upload/control, general-purpose storage, scratch indexing, logging, interrupt disable/force, and registers.

`RLC_SERDES_*` controls SERDES reads/writes and master selection: CU and non-CU master masks, read master index fields for CU/SH/SE/non-SE/data register ID, write control power-up/down/read/write/short-format/BPM address/data/reg address bits, read data registers, and CU/non-CU busy status.

`RLC_SAVE_AND_RESTORE_BASE`, `RLC_JUMP_TABLE_RESTORE`, `RLC_SRM_*`, `RLC_CSIB_*`, `RLC_CP_RESPONSE*`, `RLC_SMU_COMMAND`, and `RLC_CP_SCHEDULERS` define save/restore base and jump-table addresses, SRM enable/debug/ARAM/DRAM/command/status/indexed address/data/abort state, CSIB buffer address/length, CP response mailboxes, SMU command payload, and CP scheduler mapping.

`RLC_PERFMON_*`, `RLC_PERFCOUNTER*`, `RLC_GPM_PERF_COUNT_*`, and `RLC_SPM_*` define RLC performance monitor state: perfmon clock/state/sample enable, simple counters, GPM feature/SE/SH/CU/event selectors, SPM VMID/interrupt/debug controls, SPM perfmon ring base/size/segment layout, SE mux selector address/data, and per-block sample delays for CPG, CPC, CPF, CB, DB, PA, and GDS.

## Control Flow and State Behavior

This header has no executable control flow. Its runtime effect is indirect: included code uses the constants to pack values for MMIO writes or command/context register packets and to unpack values read from hardware.

Most fields represent persistent GPU state until overwritten by command submission, context switch restore, firmware/RLC programming, driver initialization, or reset. Persistent state includes tiling tables, backend maps, viewport/scissor/sample locations, clip/raster/setup controls, compute program resources, user data, CU masks, RLC power-gating policy, clock-gating policy, save/restore addresses, and SPM ring configuration.

Some fields are observational or counter-like rather than configuration: GRBM busy/clean/status/error fields, DB z-pass/occlusion counters, RAS signatures, RLC/GPM power status, SERDES busy bits, FIFO empty/full bits, and debug data buses. Some are command/mailbox-like: `COMPUTE_DISPATCH_INITIATOR`, `COMPUTE_RELAUNCH`, RLC safe-mode command/message fields, SMU/CP response/command registers, SRM command registers, and SERDES write/read command bits.

The state described here has no kernel persistence by itself; persistence is in hardware registers, GPU context images, command streams, and firmware-managed save/restore memory. Driver code must preserve reserved bits where the hardware requires read-modify-write semantics and must sequence writes around idle waits, safe mode, resets, and power/clock transitions.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header scheme. The sibling GFX8 offset header supplies register addresses, while this `*_sh_mask.h` file supplies field positions. AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32`, `WREG32`, SOC15-style wrappers where applicable, and packet/context-state emission paths consume these masks.

Direct include points for `gca/gfx_8_0_sh_mask.h` in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c`
- `drivers/gpu/drm/amd/amdgpu/vi.c`
- `drivers/gpu/drm/amd/amdgpu/mxgpu_vi.c`
- `drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v8.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_vi.c`
- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c`
- `drivers/gpu/drm/amd/amdgpu/sdma_v2_4.c`
- `drivers/gpu/drm/amd/amdgpu/sdma_v3_0.c`
- `drivers/gpu/drm/amd/amdgpu/vce_v3_0.c`
- `drivers/gpu/drm/amd/pm/powerplay/smumgr/smu8_smumgr.c`
- `drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h`

The macros therefore sit on several integration boundaries: graphics initialization, clear-state and context setup, KFD queue/MQD programming, virtualized GFX8 behavior, graphics/RLC reset paths, powerplay/SMU handshakes, and diagnostics/performance collection.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can silently program unrelated hardware bits, corrupting rendering, dispatch, power state, or firmware communication.
- Repeated register families are mechanically risky. `GB_TILE_MODE*`, `GB_MACROTILE_MODE*`, `GRBM_STATUS_SE*`, `PA_CL_VPORT_*`, `PA_SC_VPORT_SCISSOR_*`, `PA_SC_AA_SAMPLE_LOCS_*`, `COMPUTE_USER_DATA_*`, and RLC SRM/SPM indexed-register families are regular but not interchangeable.
- Tiling and backend fields are memory-layout sensitive. Incorrect `GB_ADDR_CONFIG`, tile mode, macrotile mode, backend map, or RB disable/redundancy definitions can cause address swizzling mismatches and data corruption.
- Reset, safe-mode, and power-gating fields are sequencing sensitive. Incorrect GRBM soft reset, RLC safe mode, RLC power-gating, clock-gating, SERDES, or SMU handshake masks can lead to hangs, incomplete register save/restore, or failed resume.
- Status and error fields drive diagnostics and idle waits. Misdecoded GRBM/RLC busy bits or read/write error requesters can make the driver wait incorrectly, reset prematurely, or report the wrong fault source.
- Compute resource fields affect queue execution and isolation. Incorrect program-resource, VMID, doorbell, queue ID, CU mask, LDS, scratch, or user-data masks can break KFD queues, dispatch correctness, or memory translation behavior.
- Debug and reserved fields are often hardware-revision-specific. Treating reserved masks as writable feature bits, or losing reserved bits during read-modify-write, can expose errata on specific GFX8 ASICs.
- The chunk starts mid-register (`DB_DEBUG3`) and ends before the file end. The merge lane must reconcile adjacent chunks for complete register-family coverage.

## Test and Validation Signals

Useful validation is primarily build, hardware execution, and low-level diagnostic coverage:

- Build AMDGPU, KFD, powerplay, SDMA, and VCE paths that include `gca/gfx_8_0_sh_mask.h`; this catches missing or renamed macros.
- Exercise GFX8 initialization, clear-state programming, context switching, suspend/resume, GPU reset, and virtualization paths that program GRBM, GB, DB, PA/SC, and RLC state.
- Run rendering tests that cover depth/stencil queries, occlusion counters, MSAA/EQAA sample locations, scissor/viewport arrays, line/point/polygon rasterization, clip/cull distances, guard bands, primitive filtering, and multi-render-backend configurations.
- Run compute and KFD queue tests covering dispatch dimensions, partial threadgroups, scratch/temp rings, user data, VMID/doorbell/queue connection, CU masks, wave restore, relaunch, and thread trace.
- Run power-management tests for GFX clock gating, memory sleep, graphics power gating, dynamic/static per-CU power gating, SMU handshakes, RLC safe mode, and register save/restore across idle/resume cycles.
- Validate performance and debug tooling that reads GRBM/RLC/PA/SC counters, status registers, RAS signatures, DB counters, SPM rings, GPM perf counters, and read/write error registers.
- Include negative/reset tests that force read/write errors, stuck busy bits, or aborted power-down sequences to verify masks decode diagnostics and recovery states correctly.

### subset-b-002715: lines 9310-13970

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 9310-13970

## Scope

This chunk is a generated AMD GFX 8.0 register shift/mask header segment. It contains only C preprocessor constants: each hardware register field is represented by `<REGISTER>__<FIELD>_MASK` and `<REGISTER>__<FIELD>__SHIFT` macros. There are no functions, structs, enums, variables, includes, allocations, locks, branches, or executable control flow in this range.

The selected range starts in the tail of the RLC SPM sample-delay family, covers RLC GPU IOV/SR-IOV control/status fields, a large SPI programming block, SPI and SQ performance counters, CGTS/CGTT clock-gating controls, shader program resource/user-data registers for PS/VS/GS/ES/HS/LS, SQC/SQ configuration fields, and ends in the SQ thread-trace mask family. Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for GFX8-era AMD GPUs, not Ceph filesystem code.

## Purpose

`gfx_8_0_sh_mask.h` supplies the bit layouts for GFX8 hardware registers. GFX8 driver code combines these masks with register-address macros from `gfx_8_0_d.h`, value enums from `gfx_8_0_enum.h`, and helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD`, MMIO accessors, and PM4 packet builders. The header lets the driver pack or decode register fields without open-coded bit positions.

This chunk primarily supports:

- RLC streaming performance monitor setup, including per-block sample delays and global mux/ring controls.
- RLC GPU IOV virtualization control, firmware/scratch interfaces, function scheduling, VF/PF reset signaling, SDMA save/restore status, SMU/RLC responses, and interrupt force/disable masks.
- Pixel shader input interpolation and barycentric setup through `SPI_PS_INPUT_CNTL_0..31`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL`.
- Shader export, ring, arbitration, debug, wave lifetime, and context-save state through SPI configuration registers.
- Shader program base, trap base, trap memory, resource, user-data, late-allocation, and resource-limit fields for PS, VS, GS, ES, HS, and LS stages.
- Per-CU SPI resource reservation and enable masks for 16 CUs.
- CGTS/CGTT clock-gating and light-sleep controls for SPI, PC, BCI, SQ, SQG, and per-CU shader sub-blocks.
- SPI and SQ performance-counter select/readout registers, including counter modes, bin thresholds, SQC client/bank/SIMD masks, SPM modes, and 64-bit low/high counter pairs.
- SQC/SQ configuration, DSM, cache, writeback, random priority, credits, interrupt message, power throttle, timestamp, and thread-trace buffer/mask fields.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this slice. Its exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>_MASK` identifies the bits occupied by a field in a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position.
- Full-register data, counter, address-low, and response fields use `0xffffffff` masks.
- High address fields for shader trap/program bases often use an 8-bit mask, reflecting the high portion accepted by GFX8 register encoding.
- Repeated indexed families, such as `SPI_PS_INPUT_CNTL_0..31`, `SPI_RESOURCE_RESERVE_CU_0..15`, `SPI_SHADER_USER_DATA_*_0..15`, `SPI_WF_LIFETIME_*`, and `SQ_PERFCOUNTER0..15`, are part of the ABI-like hardware metadata surface and must remain index-aligned with the offset header.

Major macro families in this chunk include:

- `RLC_SPM_*_PERFMON_SAMPLE_DELAY`, `RLC_SPM_GLOBAL_MUXSEL_*`, `RLC_SPM_RING_RDPTR`, and `RLC_SPM_SEGMENT_THRESHOLD`: streaming performance monitor sample delay, mux selection, ring read pointer, and segment threshold fields.
- `RLC_GPU_IOV_*` and `RLC_GPM_VMID_THREAD2`: SR-IOV/PF/VF control, command/status, time quantum, active function ID, microcode and scratch access, F32 control/reset, SDMA context status, virtual FLR request, interrupt, busy, scheduler, and VMID/thread fields.
- `SPI_PS_INPUT_CNTL_0..31`, `SPI_PS_INPUT_ENA`, `SPI_PS_INPUT_ADDR`, `SPI_INTERP_CONTROL_0`, `SPI_PS_IN_CONTROL`, and `SPI_BARYC_CNTL`: pixel shader input offsets, defaults, flat shade, cylindrical wrap, point-sprite attributes, FP16 interpolation, valid flags, interpolation enable/address masks, point-sprite override, interpolation count, and barycentric position controls.
- `SPI_SHADER_POS_FORMAT`, `SPI_SHADER_Z_FORMAT`, and `SPI_SHADER_COL_FORMAT`: position, depth, and color export format fields.
- `SPI_ARB_PRIORITY`, `SPI_ARB_CYCLES_0`, and `SPI_ARB_CYCLES_1`: SPI time-slice order and duration controls. GFX8 init code programs `SPI_ARB_PRIORITY` through `REG_SET_FIELD`.
- `SPI_CDBG_SYS_*`, `SPI_GDBG_*`, `SPI_RESET_DEBUG`, `SPI_DEBUG_*`, and `SPI_SLAVE_DEBUG_BUSY`: shader-stage debug enablement, trap base/memory, trap mask/config, debug reads, busy bits, and reset-debug disable fields.
- `SPI_RESOURCE_RESERVE_CU_*` and `SPI_RESOURCE_RESERVE_EN_CU_*`: per-CU reserved VGPR, SGPR, LDS, wave, and barrier resources plus enable/type/queue masks.
- `SPI_PERFCOUNTER*`, `SPI_PERFCOUNTER*_SELECT*`, and `SPI_PERFCOUNTER_BINS`: SPI performance counter readout, event selection, counter mode, and bin threshold fields.
- `CGTS_*` and `CGTT_*`: coarse-grain tree shader and clock-gating controls, including per-CU SP/LDS/SQ/TA/SQC/TD/TCP control/override/busy-override fields and SPI/PC/BCI/SQ/SQG clock on-delay/off-hysteresis/override bits.
- `SPI_WF_LIFETIME_*`, `SPI_CSQ_WF_ACTIVE_*`, `SPI_GDS_CREDITS`, `SPI_SX_*`, and trap-screen registers: wave lifetime limits/status, active wavefront counts, GDS credits, export/scoreboard buffer sizes, and pre-shader trap-screen address/mask/minimum register fields.
- `SPI_SHADER_TBA_*`, `SPI_SHADER_TMA_*`, `SPI_SHADER_PGM_*`, `SPI_SHADER_PGM_RSRC*_*`, `SPI_SHADER_USER_DATA_*`, and `SPI_SHADER_LATE_ALLOC_VS`: shader trap/program addresses, shader resource fields, user SGPR payloads, scratch/trap/wave-count/exception controls, streamout controls, CU enable/wave limits, and late VS allocation.
- `SQ_CONFIG`, `SQ_FIFO_SIZES`, `SQ_RANDOM_WAVE_PRI`, `SQ_DSM_CNTL`, `SQC_DSM_CNTL`, `SQC_CONFIG`, `SQC_CACHES`, `SQC_WRITEBACK`, `SQ_REG_CREDITS`, and `SQ_INTERRUPT_*`: shader queue and shader cache configuration/status/diagnostic/cache-control fields.
- `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, `SQ_PERFCOUNTER_CTRL2`, `SQ_PERFCOUNTER*_LO/HI`, and `SQ_PERFCOUNTER*_SELECT`: SQ counter enable/rate/flush controls, shader-array masks, force enable, 64-bit counter readouts, event selection, SQC bank/client masks, SPM mode, SIMD mask, and perf mode.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `SQ_POWER_THROTTLE*`, `SQ_TIME_*`, and `SQ_THREAD_TRACE_*`: CU force-on masks, power throttle thresholds/intervals, SQ timestamp, thread-trace base/size, and selected CU/SH/SIMD/VM/stall capture masks.

## Control Flow

This header has no runtime control flow; all behavior is compile-time macro substitution.

The implied driver flow is:

1. GFX8-specific code includes `gca/gfx_8_0_d.h`, `gca/gfx_8_0_enum.h`, and this shift/mask header.
2. A caller selects a register address from `gfx_8_0_d.h`.
3. The caller reads, writes, builds a context-state PM4 packet, creates an MQD, snapshots debug/perf state, or polls a status register.
4. The caller packs or extracts fields with the generated mask/shift pair, usually through helper macros.
5. The resulting value programs GPU hardware state or decodes volatile hardware status.

Concrete consumers in this tree include `gfx_v8_0.c`, which uses `REG_SET_FIELD` to program `SPI_ARB_PRIORITY`, update `RLC_SPM_VMID`, decode and set RLC/CGTS clock-gating state, issue SQ commands, and handle SQ interrupt fields. KFD VI MQD code includes this header and uses matching GFX8 shift/mask definitions when initializing compute queue descriptors, trap settings, memory type fields, doorbells, and context-save controls. Clear-state headers carry reset/context values for many SPI registers in this chunk.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe fields in live GPU registers and context images whose values may be global engine state, per-context graphics state, per-queue compute state, firmware-managed state, performance-monitor state, volatile status, or side-effect triggers.

RLC SPM and SQ/SPI performance counter state persists until the driver or firmware reprograms the relevant registers. Counter low/high readouts are volatile and require a coherent sampling sequence outside this header. SPM sample delays, mux selection, ring read pointers, and segment thresholds shape profiler output and can affect attribution or sampling quality.

RLC GPU IOV fields are virtualization-sensitive. `VF_ENABLE`, `VF_NUM`, `ACTIVE_FCN_ID`, function switching fields, time quanta, virtual reset request bits, SDMA preempt/save/restore status, busy masks, interrupt force/disable controls, and scheduler data reflect PF/VF scheduling and reset state. Incorrect field packing can disrupt SR-IOV isolation, leave a VF stuck, misreport SDMA context save/restore, or confuse firmware handshakes.

SPI shader input, interpolation, export format, barycentric, and shader program resource fields are context programming state. Values are usually submitted through command streams or clear-state/context programming paths and persist as GPU context state until changed. Misprogramming can surface as rendering corruption, broken interpolation, invalid shader exports, bad scratch or user SGPR setup, or shader trap failures.

Shader TBA/TMA/PGM low/high fields and trap-screen base/mask fields are split address encodings. The header gives only bit widths; alignment, address shifting, and valid virtual/physical address rules come from the surrounding driver sequence and hardware spec. KFD VI MQD setup, for example, shifts trap base and memory addresses before storing them in descriptor fields.

CGTS/CGTT registers control clock gating and light sleep. `gfx_v8_0.c` reads `CGTS_SM_CTRL_REG` to report CG support and writes `SM_MODE`, `SM_MODE_ENABLE`, `OVERRIDE`, `LS_OVERRIDE`, and monitor address fields when toggling medium-grain clock gating. Per-CU CGTS override/busy-override fields can force or block sub-block gating for SP, LDS, SQ, TA/SQC, TD, and TCP. These settings persist globally and can affect power, latency, and hang behavior.

SQ cache, DSM, writeback, credits, random priority, interrupt, throttle, timestamp, and thread-trace registers are a mix of persistent configuration and volatile readback. Thread-trace base/size/mask fields describe capture buffers and selection filters; bad values can capture the wrong CU/SH/SIMD/VM, overflow buffers, or miss stalls. SQ power throttle controls can intentionally constrain shader execution.

Reserved, unused, and full-register data fields are present because the header is generated. Their presence does not make arbitrary writes safe. Register programming code should preserve undocumented bits unless the hardware sequence requires a full-register write.

## Dependencies And Integration Points

This chunk depends on the generated GFX8 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_d.h` supplies matching register address macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h` supplies many field value enums used with these masks.
- AMDGPU helper macros and MMIO/PM4 accessors in the driver provide packing, extraction, register read/write, and command-stream emission.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c` is the main GFX8 graphics/RLC/clock-gating consumer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v8.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_vi.c` integrate these definitions with KFD compute queue management, MQDs, trap setup, context save/restore, CU masks, and memory type/ATC controls.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_vi.c` is an SR-IOV/MxGPU-adjacent consumer that includes the same GFX8 register headers.
- Power-management SMU8/VI paths include the header for GFX8 register fields related to clock, power, and firmware-managed controls.
- Clear-state headers such as `clearstate_vi.h` list reset/context values for many SPI state registers whose fields are described here.

Driver subsystems that depend indirectly on this metadata include graphics context programming, command submission, shader trap/debug support, KFD queue creation and preemption, SR-IOV virtualization, RLC firmware handshakes, GPU reset and safe-mode paths, clock-gating/power-management policy, debugfs/hang dumps, and performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask still compiles but programs or decodes the wrong hardware bits.
- This chunk starts mid-family at `RLC_SPM_GDS_PERFMON_SAMPLE_DELAY__RESERVED__SHIFT` and ends mid-family after `SQ_THREAD_TRACE_MASK__VM_ID_MASK__SHIFT`. File-level reconciliation must merge adjacent chunks to complete both boundaries.
- Repeated families are index-sensitive. `SPI_PS_INPUT_CNTL_0..31`, `SPI_RESOURCE_RESERVE_CU_0..15`, `SPI_SHADER_USER_DATA_*_0..15`, `SPI_WF_LIFETIME_STATUS_0..20`, and `SQ_PERFCOUNTER0..15` must keep identical layouts where expected and correct exceptions where the hardware differs.
- Some `SPI_PS_INPUT_CNTL` fields differ between indices: early entries include cylindrical wrap and point-sprite attribute fields, while later entries omit some of those fields. Consumers must not assume every index has every field.
- Address split fields such as shader TBA/TMA/PGM and trap-screen bases require correct high/low composition and alignment. Shifting by the wrong granularity can produce valid-looking but incorrect trap or program addresses.
- Full-register masks are easy to misuse in read-modify-write code. Response, data, scheduler, counter, and userdata registers are not semantically interchangeable even when they all expose `0xffffffff` data fields.
- RLC GPU IOV fields affect virtualization isolation and reset behavior. Incorrect VF/PF identifiers, time quanta, FLR masks, command execute/status bits, or SDMA busy/save/restore interpretation can destabilize SR-IOV scheduling.
- Clock-gating override bits are power and liveness sensitive. Clearing overrides too early or setting light-sleep controls without the required RLC/SerDes idle sequencing can cause hangs or misleading clock-gating capability reporting.
- Performance counters require coherent low/high sampling and correct event/mode selection. The header does not describe latch order, overflow behavior, mux programming, or block-specific valid event IDs.
- `SQC_CACHES` invalidate/complete and `SQC_WRITEBACK` are side-effect-like cache controls. Treating them as ordinary passive state risks stale instruction/scalar cache data or false completion.
- SQ interrupt, thread-trace, debug, and wave lifetime fields interact with diagnostics and error handling. Bad masks can hide trap/thread-trace interrupts, misreport SQ event sources, or flood interrupts.
- Resource reservation and CU mask fields can reduce visible compute capacity or starve selected queue classes if enable/type/queue masks are wrong.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for all GFX8/VI AMDGPU and KFD files that include `gfx_8_0_sh_mask.h`.
- Mechanical comparison of every `__SHIFT` and `_MASK` in lines 9310-13970 against AMD's authoritative GFX8 register database.
- Static checks that each register field in this chunk has a matching address macro in `gfx_8_0_d.h` where applicable and that mask/shift pairs align.
- Repeated-family checks for index continuity and field-layout consistency across `SPI_PS_INPUT_CNTL`, `SPI_RESOURCE_RESERVE_CU`, `SPI_SHADER_USER_DATA`, `SPI_WF_LIFETIME`, `SPI_PERFCOUNTER`, and `SQ_PERFCOUNTER` groups.
- GFX8 boot/init tests that exercise `SPI_ARB_PRIORITY`, shader memory/program setup, clear-state restore, and graphics context switching.
- KFD queue tests that validate VI MQD initialization, user SGPR fields, trap TBA/TMA setup, CU masks, CWSR context-save fields, queue priority, and doorbell behavior.
- SR-IOV/MxGPU tests that cover VF enablement, active function reporting, VF/PF time quanta, virtual FLR request/response, SDMA save/restore status, and RLC/SMU response paths.
- RLC SPM/perf tests that program sample delays, mux selection, ring pointers, SPI/SQ counter selects, and low/high counter readout while checking monotonicity and overflow handling.
- Clock-gating tests that toggle MGCG/CGTS/CGLS/MGLS paths, verify `CGTS_SM_CTRL_REG` override/light-sleep behavior, and watch for hangs during RLC SerDes sequencing.
- Shader-interpolation and export rendering tests that exercise flat shade, point sprites, FP16 interpolation, barycentric modes, position/Z/color export formats, and user-data payloads.
- Debug and trap tests that validate shader trap bases, trap-screen bounds, SQ interrupt decoding, thread-trace buffer base/size/mask capture, wave lifetime warnings, and SPI/SQ busy status dumps.
- Cache and SQ state tests that validate SQC invalidate/writeback completion, SQ credits/fifo settings, power throttle behavior, and SQ timestamp/thread-trace readback.

Runtime warning signals include GPU hangs during clock-gating transitions, VF reset failures, SDMA save/restore timeouts, invalid shader trap dispatch, corrupted interpolation/export output, KFD queue launch/preemption failures, stale shader cache behavior, impossible busy/status dumps, performance counters stuck at zero, or thread-trace buffers missing expected events.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002715`. It covers lines 9310-13970 of `gfx_8_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the RLC SPM sample-delay boundary at the start and the SQ thread-trace family after the end, then place these GFX8 RLC/SPI/SQ/CGTS register masks in the full generated header map.

### subset-b-002716: lines 13971-19163

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 13971-19163

## Purpose

This chunk is generated-style bitfield metadata for the AMD GFX 8.0 graphics core register interface. It contains C preprocessor constants that map hardware register fields to their 32-bit masks and low-bit shifts. The definitions are not executable code; they are the symbolic contract used by AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, raw `RREG32`/`WREG32`, packet register programming, golden-setting tables, debug capture code, and shader/debug tooling to compose or decode register values without hard-coding bit positions.

The range starts in the middle of shader queue/thread-trace definitions, covers shader resource descriptors, wave and instruction encodings, SQ/SQC interrupt and cache controls, clock-gating controls for several graphics blocks, SX/TCC/TCA/TCP/TD/TA/GDS performance and debug registers, GDS VMID/resource partitioning, VGT draw/index/tessellation/GS/streamout controls, WD debug state, and IA/VGT debug status. It ends in the middle of `VGT_DEBUG_REG1`, so the following chunk owns the remaining fields for that register.

## Important APIs, Types, And Data

There are no C functions, structs, enums, runtime variables, locks, or allocation paths in this chunk. The public surface is a large set of macros following the generated AMD ASIC register naming pattern:

- `REGISTER__FIELD_MASK` gives the unshifted mask for a field inside a 32-bit register word.
- `REGISTER__FIELD__SHIFT` gives the field's low bit index.
- Full-word payload fields use masks such as `0xffffffff`, for example thread-trace userdata, counter values, descriptor addresses, instruction words, wave registers, GDS read/write data, index counts, primitive IDs, tessellation levels, and debug-data payloads.
- Repeated register families are flattened into individual macro names, for example `GDS_VMID0_BASE` through `GDS_VMID15_BASE`, `GDS_GWS_RESET0/1`, `TC_CFG_L1_LOAD_POLICY0/1`, and `WD_DEBUG_REG0` through `WD_DEBUG_REG10`.

Major register families in this range include:

- SQ thread trace setup and decode: `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_USERDATA_0..3`, `SQ_THREAD_TRACE_MODE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK2`, `SQ_THREAD_TRACE_PERF_MASK`, `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_CNTR`, `SQ_THREAD_TRACE_HIWATER`, and decoded thread-trace packet formats such as `SQ_THREAD_TRACE_WORD_CMN`, `INST`, `INST_PC_*`, `INST_USERDATA_*`, `TIMESTAMP_*`, `WAVE`, `MISC`, `WAVE_START`, `REG_*`, `REG_CS_*`, `EVENT`, `ISSUE`, and `PERF_*`.
- SQ shader-visible descriptors and wave state: `SQ_BUF_RSRC_WORD0..3`, `SQ_IMG_RSRC_WORD0..7`, `SQ_IMG_SAMP_WORD0..3`, `SQ_FLAT_SCRATCH_WORD0/1`, `SQ_M0_GPR_IDX_WORD`, `SQ_IND_INDEX`, `SQ_CMD`, `SQ_IND_DATA`, `SQ_REG_TIMESTAMP`, `SQ_CMD_TIMESTAMP`, `SQ_HV_VMID_CTRL`, `SQ_WAVE_INST_DW0/1`, `SQ_WAVE_PC_LO/HI`, `SQ_WAVE_IB_DBG0/1`, `SQ_WAVE_EXEC_LO/HI`, `SQ_WAVE_STATUS`, `SQ_WAVE_MODE`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_STS`, `SQ_WAVE_M0`, trap-base registers, trap-memory registers, and temporary trap registers `SQ_WAVE_TTMP0..11`.
- SQ/SQC cache, interrupt, and instruction formats: `SQC_EDC_CNT`, `SQC_GATCL1_CNTL`, `SQC_ATC_EDC_GATCL1_CNT`, `SQ_EDC_SEC_CNT`, `SQ_EDC_DED_CNT`, `SQ_EDC_INFO`, `SQ_INTERRUPT_WORD_CMN`, `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_WAVE`, and instruction encodings for `SQ_SOP*`, `SQ_VOP*`, `SQ_MUBUF`, `SQ_MTBUF`, `SQ_MIMG`, `SQ_FLAT`, `SQ_DS`, `SQ_EXP`, `SQ_VINTRP`, `SQ_INST`, and `SQ_WREXEC_EXEC_*`.
- Clock-gating and block control: `CGTT_SX_CLK_CTRL0..4`, `CGTT_TCP_CLK_CTRL`, `CGTT_TCI_CLK_CTRL`, `CGTT_GDS_CLK_CTRL`, `CGTT_IA_CLK_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_WD_CLK_CTRL`, `TD_CGTT_CTRL`, `TA_CGTT_CTRL`, `TCC_CGTT_SCLK_CTRL`, and `TCA_CGTT_SCLK_CTRL`, each with `ON_DELAY`, `OFF_HYSTERESIS`, and soft override fields.
- Shader export/cache/memory blocks: `SX_DEBUG_BUSY*`, `SX_DEBUG_1`, `SX_PERFCOUNTER*`, `TCC_CTRL`, `TCC_EDC_CNT`, `TCC_REDUNDANCY`, `TCC_EXE_DISABLE`, `TCC_DSM_CNTL`, `TCC_PERFCOUNTER*`, `TCA_CTRL`, `TCA_PERFCOUNTER*`, `TD_CNTL`, `TD_STATUS`, `TD_DSM_CNTL`, `TD_PERFCOUNTER*`, `TA_CNTL`, `TA_CNTL_AUX`, `TA_STATUS`, `TA_DEBUG_*`, `TA_PERFCOUNTER*`, `SH_MEM_BASES`, `SH_MEM_APE1_BASE/LIMIT`, `SH_MEM_CONFIG`, `SH_STATIC_MEM_CONFIG`, and `SH_HIDDEN_PRIVATE_BASE_VMID`.
- Texture/cache policy and watchpoints: `TCP_INVALIDATE`, `TCP_STATUS`, `TCP_CNTL`, `TCP_CNTL2`, `TCP_ADDR_CONFIG`, `TCP_CREDIT`, `TCP_CHAN_STEER_LO/HI`, `TCP_BUFFER_ADDR_HASH_CNTL`, `TCP_EDC_CNT`, `TCP_GATCL1_CNTL`, `TCP_ATC_EDC_GATCL1_CNT`, `TCP_GATCL1_DSM_CNTL`, `TCP_DSM_CNTL`, `TCP_WATCH0..3_ADDR_H/L`, `TCP_WATCH0..3_CNTL`, and `TC_CFG_L1/L2_*_POLICY*` plus volatile-policy registers.
- GDS and GWS/OA state: `GDS_CONFIG`, `GDS_CNTL_STATUS`, `GDS_ATOM_*`, `GDS_RD_*`, `GDS_WR_*`, `GDS_WRITE_COMPLETE`, `GDS_PROTECTION_FAULT`, `GDS_VM_PROTECTION_FAULT`, `GDS_DEBUG_*`, `GDS_DSM_CNTL`, `GDS_EDC_*`, `GDS_ENHANCE*`, `GDS_PERFCOUNTER*`, VMID partition registers `GDS_VMID0..15_BASE/SIZE`, global-wave-sync windows `GDS_GWS_VMID0..15`, ordered-append masks `GDS_OA_VMID0..15`, `GDS_GWS_RESET0/1`, `GDS_GWS_RESOURCE*`, `GDS_OA_RESET*`, `GDS_OA_ADDRESS`, `GDS_OA_COUNTER`, `GDS_OA_CNTL`, `GDS_OA_INCDEC`, `GDS_OA_RING_SIZE`, and GDS context-switch counters/status registers.
- VGT, WD, and IA frontend pipeline state: `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, `VGT_DMA_*`, `VGT_INDEX_TYPE`, draw count and instance registers, primitive ID/reset, vertex reuse, index bounds, output path, tessellation controls, GS ring/sizing/on-chip controls, cache invalidation, shader-stage enablement, streamout buffer/config registers, `VGT_MULTI_PRIM_IB_RESET_*`, `VGT_RESET_DEBUG`, `VGT_FIFO_DEPTHS`, `VGT_CNTL_STATUS`, `WD_CNTL_STATUS`, `WD_QOS`, `WD_DEBUG_REG0..10`, `IA_MULTI_VGT_PARAM`, `IA_CNTL_STATUS`, `IA_DEBUG_REG0..9`, and the start of `VGT_DEBUG_REG0/1`.

## Control Flow

This header chunk has no runtime control flow. Its effect is through preprocessing and compilation: consumers include `gfx_8_0_sh_mask.h` with the matching GFX 8 offset header, then use these masks and shifts to read, write, decode, or emit values for GFX8 hardware registers.

Typical consumer flow is:

1. Select the GFX8 register headers by compiling the GFX8/VI AMDGPU code path.
2. Read or synthesize a 32-bit register value using `RREG32`, `WREG32`, packet3 register writes, or a golden-setting table entry.
3. Use these `*_MASK` and `*__SHIFT` constants directly or via `REG_GET_FIELD`/`REG_SET_FIELD` to isolate or place fields.
4. Program the register, store decoded state in driver structures, or export captured values through debug/hang-info paths.

Visible integration in the tree follows that pattern. `gfx_v8_0.c` includes this header, defines GFX8 golden-setting arrays with registers covered by this chunk such as `mmTA_CNTL_AUX`, `mmTCC_CTRL`, `mmTCP_ADDR_CONFIG`, `mmCGTT_GDS_CLK_CTRL`, `mmCGTT_IA_CLK_CTRL`, `mmCGTT_WD_CLK_CTRL`, `mmCGTT_SX_CLK_CTRL0..4`, `mmCGTT_TCI_CLK_CTRL`, `mmCGTT_TCP_CLK_CTRL`, and `mmCGTT_VGT_CLK_CTRL`, and initializes `gds_reg_offset` with `mmGDS_VMID*_BASE`, `mmGDS_VMID*_SIZE`, `mmGDS_GWS_VMID*`, and `mmGDS_OA_VMID*`. The same driver path reads GDS sizing registers into `adev->gds`, writes `mmGDS_COMPUTE_MAX_WAVE_ID` in ring setup, and captures `ixSQ_WAVE_STATUS` through the wave debug path.

Because many of these registers are command-processor or per-shader-engine state, the real runtime ordering is imposed by GFX initialization and command submission rather than by this header. Golden settings run early during device setup. GDS VMID windows are reset or programmed when address spaces and queues are initialized. VGT draw/index/tessellation registers are normally driven by command packets. Wave debug and thread-trace state is read only after selecting a wave/SIMD or enabling a trace session. Clock-gating controls must be programmed in a context where the relevant graphics blocks can tolerate clock control changes.

## State And Persistence Behavior

The macros do not store state. The state they describe lives in hardware registers, command streams, memory descriptors, or driver fields populated from those registers.

State categories in this chunk include:

- Persistent hardware configuration until reset, suspend/resume, power transition, or explicit reprogramming: clock-gating controls, `TA_CNTL_AUX`, `TCC_CTRL`, `TCP_ADDR_CONFIG`, `TCP_BUFFER_ADDR_HASH_CNTL`, `SH_MEM_CONFIG`, `SH_STATIC_MEM_CONFIG`, cache policy registers, GDS VMID/GWS/OA partition registers, GDS enhance/OA controls, VGT topology/GS/tessellation controls, and FIFO depth registers.
- Per-dispatch, per-draw, or command-stream state: VGT draw initiators, DMA/index registers, primitive type, instance counts, vertex index bounds, streamout buffer size/offset/filled-size registers, shader-stage enablement, GS ring sizing, and primitive-ID/reset controls.
- Debug/observation state: SQ wave state, SQ thread-trace words and status, SQ/SQC/TCP/TCC/GDS EDC counters, SX/WD/IA/VGT debug registers, block busy bits, FIFO fullness/emptiness, context-switch status counters, protection fault fields, and performance counter low/high registers.
- Address and resource descriptor state: SQ buffer/image/sampler descriptor words, scratch base/size fields, trap base/memory addresses, TCP watchpoint address/control registers, and GDS atom/read/write addresses and payloads.
- Command or handshake state: trace reset/autoflush/interrupt/wrap controls, `SQ_CMD`, TCP invalidate, GDS atom controls and complete bits, GDS/GWS/OA reset registers, VGT cache invalidation, and draw/DMA initiator registers.

Some of this state is restored from driver tables after reset or resume, while other state is emitted in command streams for each workload. GDS partition state is particularly persistent from the driver's perspective: `gfx_v8_0.c` caches global GDS sizing and programs per-VMID base/size/GWS/OA windows so user queues see the expected resource partitioning. Debug and counter fields are transient snapshots and should not be treated as stable configuration.

## Dependencies

This chunk depends on the rest of the generated GFX8 register header set:

- `gfx_8_0_offset.h` supplies the matching `mm*` and `ix*` register identifiers used with these field masks, such as `mmGDS_VMID0_BASE`, `mmGDS_COMPUTE_MAX_WAVE_ID`, `mmTCP_ADDR_CONFIG`, `mmTA_CNTL_AUX`, `mmTCC_CTRL`, `mmCGTT_*`, and `ixSQ_WAVE_STATUS`.
- Adjacent sections of `gfx_8_0_sh_mask.h` define fields before line 13971 and after line 19163, including the beginning of `SQ_THREAD_TRACE_MASK` before this chunk and the remainder of `VGT_DEBUG_REG1` after this chunk.
- GFX8 AMDGPU consumers include `gfx_v8_0.c`, `vi.c`, SDMA/VCE/SMU8 paths that include the same mask header, and shared register helper macros from the DRM AMDGPU tree.
- Packet building and register access code supplies the actual IO mechanisms: direct MMIO helpers, indexed SQ debug accessors, packet3 `SET_*_REG` writes, and golden-setting application helpers.
- Hardware/firmware behavior is the ultimate dependency. These constants must match the GFX8 ASIC specification; they are not self-validating and cannot be inferred safely from similar GC/GFX generations.

Macro names are intentionally similar across GFX6, GFX7, GFX8, GFX9, and later GC headers, but field widths and semantics can differ. Consumers must pair the offset and mask headers for the active ASIC generation.

## Integration Points

Important integration points include:

- GFX8 golden settings: registers from this chunk are present in `gfx_v8_0.c` golden tables. Mask/value pairs for `TA_CNTL_AUX`, `TCC_CTRL`, `TCP_ADDR_CONFIG`, `CGTT_*`, and `SX_DEBUG_1` rely on the same hardware bit layout represented here.
- GDS resource management: the `gds_reg_offset` table and GDS initialization paths use VMID base/size, GWS, and OA registers covered by this chunk. Correct fields are required for per-VMID GDS memory, global wave sync resources, and ordered-append resource isolation.
- Command submission and ring setup: VGT DMA/index/draw fields, primitive controls, streamout controls, shader-stage controls, and `GDS_COMPUTE_MAX_WAVE_ID` are emitted through command packets, so these masks define the contract between kernel command construction and the graphics frontend.
- Debug and hang analysis: wave capture reads `ixSQ_WAVE_STATUS`, and adjacent SQ wave/debug fields describe the values needed to identify wave ID, SIMD, CU, shader engine, queue, VMID, trap state, execution masks, instruction buffer state, and exception status. WD/IA/VGT/SX debug fields provide lower-level pipeline busy and FIFO diagnostics.
- Thread trace and profiling: `SQ_THREAD_TRACE_*` setup/status fields and decoded packet-word fields integrate with performance tooling and low-level diagnostics. `*_PERFCOUNTER*_SELECT`, `*_LO`, and `*_HI` registers describe block-specific counter selection and readback.
- Cache, memory, and coherency policy: SQC/TCP/TCC cache control, invalidation, EDC, L1/L2 policy, volatile, watchpoint, and channel steering registers interact with VM, command processor synchronization, SDMA/graphics interop, and shader memory semantics.
- Power and clock management: CGTT controls for SX, TCP, TCI, GDS, IA, VGT, WD, TD, TA, TCC, and TCA integrate with VI/GFX8 clock-gating defaults and power-management flows.
- Shader/user-mode ABI surface: SQ resource descriptor words, image sampler words, wave status/mode/trap fields, and instruction encoding fields mirror hardware formats that userspace compilers and command streams must match, even when the kernel only observes or validates pieces of them.

## Risks

- A wrong mask or shift compiles cleanly but changes the wrong hardware bits. In this chunk, likely symptoms include GPU hangs, bad golden-setting programming, broken GDS partitioning, corrupted indexed draws, incorrect tessellation/GS/streamout behavior, cache incoherency, or unusable debug captures.
- Several families contain command/action bits rather than passive configuration. Misusing `SQ_CMD`, `TCP_INVALIDATE`, `GDS_ATOM_CNTL`, `GDS_GWS_RESET*`, `GDS_OA_RESET*`, `VGT_DRAW_INITIATOR`, `VGT_EVENT_INITIATOR`, or `VGT_CACHE_INVALIDATION` can trigger hardware actions at the wrong time.
- Debug/status fields are mixed with writable policy fields. Treating `SQ_THREAD_TRACE_STATUS`, `TA_STATUS`, `TCP_STATUS`, `GDS_CNTL_STATUS`, `WD_DEBUG_REG*`, `IA_DEBUG_REG*`, or `VGT_DEBUG_REG*` as ordinary configuration can produce meaningless writes or mask real hang diagnostics.
- GDS VMID/GWS/OA partition registers are isolation-sensitive. Incorrect base/size/mask fields can let one queue or VMID consume resources intended for another, or can make GDS unavailable to workloads that expect it.
- Cache and coherency fields have system-wide effects. Bad `SQC_GATCL1_CNTL`, `TCP_GATCL1_CNTL`, `TCP_CNTL`, `TCC_CTRL`, `TC_CFG_*`, or volatile-policy programming can show up as intermittent shader memory corruption, stale data, unexpected force-miss behavior, or large performance cliffs.
- Resource descriptor and instruction encoding fields are ABI-like. If `SQ_BUF_RSRC_*`, `SQ_IMG_RSRC_*`, `SQ_IMG_SAMP_*`, or `SQ_*` instruction masks do not match hardware, tools that decode descriptors/instructions or any kernel-side validation/debugging can misinterpret user workloads.
- Many registers contain reserved, spare, or unused fields. Raw full-register writes can disturb these bits; masked read/modify/write or golden-setting masks are safer when the hardware programming guide requires preservation.
- The chunk starts and ends mid-register-family. The previous chunk owns earlier `SQ_THREAD_TRACE_MASK` fields, and the next chunk owns the rest of `VGT_DEBUG_REG1`. Any final per-file analysis must merge adjacent chunks before making complete claims about those registers.
- Generated ASIC register headers should not be hand-edited casually. Updates should normally come from regenerated hardware register specifications so offset headers, masks, comments, and consumer code stay synchronized.

## Test Signals

Useful validation signals for this chunk include:

- Build coverage for GFX8/VI AMDGPU configurations that include `gca/gfx_8_0_sh_mask.h`, ensuring all referenced `mm*`, `ix*`, `*_MASK`, and `*__SHIFT` symbols resolve with the matching offset header.
- Golden-setting smoke tests on GFX8 hardware: boot, initialize graphics, apply `gfx_v8_0.c` golden tables, and verify no register access faults or early GPU hangs around `TA_CNTL_AUX`, `TCC_CTRL`, `TCP_ADDR_CONFIG`, CGTT, and SX debug programming.
- GDS tests that initialize per-VMID GDS, GWS, and OA resources, then run compute/graphics queues using GDS atomics and ordered append. Failures may appear as resource allocation errors, wrong GDS readback, protection faults, or hangs.
- Wave debug and hang-dump tests that read `ixSQ_WAVE_STATUS` and adjacent wave registers after synthetic shader traps or hangs, checking that decoded wave, SIMD, CU, SE, queue, VMID, trap, and execution status fields are plausible.
- Thread-trace/profiling validation that enables thread trace, checks `SQ_THREAD_TRACE_STATUS`/`WPTR`, captures tokens, and decodes instruction, wave, event, register, timestamp, and performance words using the packet masks in this chunk.
- Cache/coherency stress using shader buffer/image loads/stores, atomics, TCP/SQC invalidation paths, SDMA/graphics interop, and VMID changes. Stale reads, VM faults, EDC counter changes, or performance regressions point at bad cache-policy or invalidation field handling.
- Draw/index frontend tests covering direct draws, indexed draws, instancing, primitive restart, multi-primitive IB reset, tessellation, GS, streamout, and opaque draws. These exercise `VGT_*`, `WD_*`, and `IA_*` register families.
- Suspend/resume, GPU reset, and runtime clock-gating tests. These stress whether persistent CGTT, cache policy, GDS, and frontend registers are restored and whether busy/debug status remains meaningful after transitions.
- Performance counter tests for SQ/SX/TCC/TCA/TCP/TD/TA/GDS counters, ensuring counter select/mode fields and high/low readback fields produce stable, monotonic, or workload-correlated results as expected.

### subset-b-002717: lines 19164-20836

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_sh_mask.h lines 19164-20836

## Scope And Purpose

This chunk is the final line range of the GFX 8.0 shader/register mask header. It contains preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>_MASK` and matching `<REGISTER>__<FIELD>__SHIFT` definition. There are no functions, structs, storage objects, or executable control-flow paths in this range.

The chunk covers three major hardware-contract areas:

- `VGT_DEBUG_REG1` tail plus `VGT_DEBUG_REG2` through `VGT_DEBUG_REG36`, describing bit layouts for Vertex Grouper/Tessellator debug snapshot registers.
- `VGT_PERFCOUNTER*`, `IA_PERFCOUNTER*`, and `WD_PERFCOUNTER*`, describing performance counter select, mode, low, and high counter fields for VGT, input assembler, and work distributor blocks.
- `DIDT_*`, describing dynamic independent digital temperature/power-throttling controls, thresholds, weights, over-current protection limits, tuning registers, and indirect register index/data fields for SQ, DB, TD, TCP, and DBR blocks.

The header itself is a generated-style ASIC register description file. Its purpose is to let driver code form and decode 32-bit MMIO/indirect register values without hard-coded literals at each call site.

## Important APIs, Types, And Constants

There are no C APIs or types exported here. The usable interface is the macro namespace:

- `VGT_DEBUG_REG*__*_{MASK,__SHIFT}`: bitfield definitions for VGT debug reads. The fields expose internal pipeline state such as busy flags, FIFO empty/full flags, ready-to-receive/ready-to-send handshakes, primitive/index validity, GS/ES/VS table states, tessellation ring state, patch/edge FIFO state, active shader masks, and available ring-buffer space.
- `VGT_PERFCOUNTER_SEID_MASK__PERF_SEID_IGNORE_MASK_*`: shader-engine filtering for VGT performance counter collection.
- `VGT_PERFCOUNTER[0-3]_SELECT*__*`: event selector and mode fields. Counters 0 and 1 have wider multi-selector forms (`PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, `PERF_MODE*`), while counters 2 and 3 expose simpler `PERF_SEL` and `PERF_MODE` fields in this ASIC definition.
- `VGT_PERFCOUNTER[0-3]_{LO,HI}__PERFCOUNTER_*`: full-width 32-bit low/high halves for counter reads.
- `IA_PERFCOUNTER*` and `WD_PERFCOUNTER*`: analogous input-assembler and work-distributor performance counter field definitions.
- `DIDT_IND_INDEX__DIDT_IND_INDEX_*` and `DIDT_IND_DATA__DIDT_IND_DATA_*`: full-width fields for the indirect DIDT address and data registers.
- `DIDT_{SQ,DB,TD,TCP,DBR}_CTRL0`: enable/reset/clock/reference/phase fields for DIDT blocks. For SQ, TD, and TCP, this chunk also defines `DIDT_MAX_STALLS_ALLOWED_{HI,LO}` overlays on the corresponding `CTRL0` register.
- `DIDT_{SQ,DB,TD,TCP,DBR}_CTRL1`, `CTRL2`, and `CTRL_OCP`: min/max power, max power delta, interval size, long-term ratio, and OCP max power field layouts.
- `DIDT_{SQ,DB,TD,TCP,DBR}_WEIGHT0_3`, `WEIGHT4_7`, and `WEIGHT8_11`: packed 8-bit activity weights.
- `DIDT_{SQ,TD,TCP}_STALL_CTRL` and `DIDT_{SQ,TD,TCP}_TUNING_CTRL`: additional stall enable, stall delay, high-power threshold, and split max-power-delta tuning fields.

## Control Flow And State Behavior

This chunk has no local control flow. At compile time, including C files receive symbolic constants. Runtime behavior appears only in consumers:

- DIDT indirect reads and writes in `amdgpu/vi.c` and `amdgpu/cik.c` lock `adev->reg.didt.lock`, write `mmDIDT_IND_INDEX`, then read or write `mmDIDT_IND_DATA`. The masks in this chunk are used after those register accesses to preserve unrelated bits or place field values correctly.
- Power management code such as `pm/powerplay/hwmgr/smu7_powertune.c` stores tables of `{register, mask, shift, value, register-space}` entries. Those tables use the DIDT field macros here to program Polaris/SMU7 power-tune defaults through the DIDT indirect register path.
- Legacy DPM code such as `pm/legacy-dpm/kv_dpm.c` reads `ixDIDT_*_CTRL0`, toggles `DIDT_*_CTRL0__DIDT_CTRL_EN_MASK`, and writes the result back to enable or disable ramping for SQ, DB, TD, and TCP blocks.

State is persisted in GPU hardware registers, not in this header. Debug/performance fields are observational state when read from hardware. DIDT fields are configuration state whose values survive only according to GPU reset/power-management behavior; the header does not manage lifetime, caching, locking, or restore sequencing.

## Dependencies And Integration Points

This file is included by GFX 8-era AMDGPU and AMDKFD code through `gca/gfx_8_0_sh_mask.h`. It is paired with address headers such as `gfx_8_0_d.h`, where `mm*` and `ix*` register offsets are defined. The mask header is not useful by itself: code needs a register address macro plus these mask/shift macros to generate an MMIO value.

Important integration points visible from repository cross-references:

- `drivers/gpu/drm/amd/amdgpu/vi.c` and `cik.c` provide DIDT indirect accessor functions around `mmDIDT_IND_INDEX` and `mmDIDT_IND_DATA`.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_powertune.c` consumes many `DIDT_*` macros in static power-tune configuration tables.
- `drivers/gpu/drm/amd/pm/legacy-dpm/kv_dpm.c` consumes `DIDT_*_CTRL0__DIDT_CTRL_EN_MASK` macros for runtime enable/disable toggles.
- AMDKFD VI queue/MQD managers include this header as part of the shared GFX 8 register vocabulary, though this specific chunk is primarily debug/perf/power-management oriented.

## Risks And Edge Cases

- Hardware contract drift is the main risk. These constants must match the exact GFX 8.0 register specification. A wrong mask or shift can write reserved bits, leave a power-management field unchanged, select the wrong performance event, or misdecode debug state.
- Some registers have full-width fields (`0xffffffff`) and some masks use an `L` suffix. Consumers should keep values unsigned/32-bit to avoid sign-extension or host-width surprises in arithmetic and formatting.
- DIDT registers are accessed indirectly through an index/data pair. Any consumer must serialize access, as `vi.c` and `cik.c` do with `adev->reg.didt.lock`; otherwise interleaved index/data operations can read or write the wrong indirect register.
- Several DIDT control fields are duplicated or overlaid late in the file, such as additional `DIDT_MAX_STALLS_ALLOWED_*` fields on `DIDT_SQ_CTRL0`, `DIDT_TD_CTRL0`, and `DIDT_TCP_CTRL0`. Table-driven code must use the exact mask/shift pair for the intended ASIC generation rather than assuming similarly named fields across GFX versions share layout.
- Debug register fields expose internal pipeline names (`rtr`, `rts`, `dr`, FIFO flags, `_q` latched state) that are easy to misinterpret. They are best treated as hardware diagnostic signals unless documentation ties a field to a stable software-visible behavior.
- The chunk ends with the header guard close. Any generated merge or patch must preserve this `#endif`; losing it breaks all users of the header.

## Test And Validation Signals

There are no direct unit tests for this macro chunk. Useful validation signals are integration-level:

- Compile coverage of AMDGPU/AMDKFD users that include `gfx_8_0_sh_mask.h`, especially files that build SMU7 power-tune tables and legacy DPM DIDT toggles.
- Static checks that every edited or regenerated field preserves mask/shift consistency: single-bit masks shift to their bit index; contiguous multi-bit masks shift down to a dense field; full-width fields have shift zero.
- Runtime power-management smoke tests on GFX 8 hardware: DIDT enable/disable paths should preserve unrelated bits and not trigger hangs, throttling regressions, or invalid register access warnings.
- Perf-counter tests or manual debugfs/perf instrumentation on supported ASICs can confirm `VGT`, `IA`, and `WD` selector fields map to expected events and counter values.
- Register dumps before and after SMU7/legacy DPM initialization should show only intended DIDT fields changing when table-driven programming applies masks and shifts.

## Chunk Notes For Merge Lane

This is a partial chunk of a much larger generated register mask header. Whole-file research should avoid describing this chunk as standalone logic. It should be merged as the tail section that supplies VGT debug/performance-counter and DIDT bitfield definitions for GFX 8-era AMDGPU register programming.
