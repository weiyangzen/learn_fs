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
