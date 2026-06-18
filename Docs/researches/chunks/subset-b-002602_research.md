# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 25182-27636

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or executable branches in this range.

The selected lines begin in the tail of the `SX_DEBUG_BUSY_9` mask list, then cover `SX_DEBUG_BUSY_10` and a broad SPI diagnostics/configuration block. The main middle of the chunk crosses generated address blocks for TP (`TD_*`, `TA_*` texture front-end controls), RB (`DB_*`, `CB_*`, `GB_*`, backend/render-cache controls), `spipdec2` throttle controls, RMI memory-interface controls, UTCL1 cache/TLB controls, and the beginning of SH shader-program registers for PS, GS/ESGS, and the start of HS/LS state. Although the path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_12_1_0_sh_mask.h` supplies bit layouts for the GC 12.1.0 graphics IP. Driver code pairs these masks with register addresses from the matching `gc_12_1_0_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack fields before MMIO writes, command-packet programming, or firmware setup, and to decode status/debug reads.

This chunk describes several hardware areas:

- SX/SPI busy/debug controls, scratch status, wave lifetime controls/status, compute-unit enable masks, work-pending/active counters, lightweight-bench data selectors, GDS/SX buffer sizing, trap-screen registers, and crawler controls.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_tpdec`: TD/TA texture data/address controls, power/debug enable bits, format/rounding/aniso/determinism settings, FIFO credits, and texture front-end busy/status bits.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_rbdec`: DB depth/stencil debug and FIFO/arbiter controls, backend memory/cache/free-cacheline/ring/watermark fields, CB hardware controls, backend mapping/GPU ID fields, cache eviction points, and fine-grain clock-gating override fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_spipdec2`: pixel-queue event and export throttle fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_rmi_gfx_se_rmidec`: RMI routing, request/return queue state, UTCL1-facing controls, formatter, scoreboard, crossbar arbiter, XNACK/debug, CID mapping, spare/mode bits, and redundancy controls.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_utcl1dec`: UTCL1 bypass/page-size/hash/allocation-log/status fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_shdec`: shader-program checksum, program-address, resource, user-data, request-control, output-config, meshlet, and user-accumulator fields for PS, GS/ESGS, and the beginning of HS/LS.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register-address symbols are provided by the companion GC 12.1.0 offset header and are consumed by AMDGPU MMIO helpers, packet builders, debug paths, golden-register programming, and hang-dump code.

Notable macro families in this slice are:

- `SX_DEBUG_BUSY_9` tail and `SX_DEBUG_BUSY_10`: SX busy bits for index/value banks and POS/IDX scoreboard, requester, PA/SX, and write-control queues.
- `SPI_DEBUG_CNTL`, `SPI_DEBUG_CNTL_2`, `SPI_DEBUG_CNTL_3`, `SPI_DEBUG_READ`, `SPIRA_DEBUG_READ`, `SPIS_DEBUG_READ`, and `BCI_DEBUG_READ`: selectors and read-data fields for SPI debug inspection, plus gating/debug overrides and FIFO debug write enablement.
- `SPI_DEBUG_BUSY`, `SPI_SLAVE_DEBUG_BUSY`, `SPI_WGP_WORK_PENDING`, `SPI_CSQ_WF_ACTIVE_STATUS`, `SPI_*_WF_ACTIVE_COUNT*`, `SPI_WF_LIFETIME_*`, `SPI_PS_MAX_WAVE_ID`, and `SPI_SCRATCH_ADDR_STATUS`: live status and instrumentation fields for shader-stage busy state, scratch overflow attribution, wave IDs, lifetime accounting, and per-WGP/CSQ wave activity.
- `SPI_CONFIG_PS_CU_EN` and `SPI_CONFIG_CU_MASK_{GFX,HP3D,CS}*`: CU and WGP masks for pixel, graphics/HP3D, and compute scheduling paths.
- `SPI_LB_*`, `SPI_GDS_CREDITS`, `SPI_SX_EXPORT_BUFFER_SIZES`, `SPI_SX_SCOREBOARD_BUFFER_SIZES`, `SPI_P0/P1_TRAP_SCREEN_*`, `SPI_GFX_CRAWLER_CONFIG`, and `SPI_CS_CRAWLER_CONFIG`: lightweight-benchmark counters, GDS/SX credit sizing, trap-screen address/range filters, and crawler activity/FSM controls.
- `TD_*` and `TA_*`: texture-data/address registers covering format behavior, rounding, power throttling, debug enable, FIFO credits, anisotropic filtering parameters, deterministic-mode disables, PRT behavior, texture status, and scratch/debug data.
- `DB_DEBUG*`, `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH*`, `DB_RING_CONTROL`, `DB_MEM_*`, `DB_ARB_CONFIG`, `DB_EXCEPTION_CONTROL`, `DB_DFD_INDIRECT_*`, `DB_SUMMARIZER_TIMEOUTS`, and `DB_FGCG_*`: depth/stencil backend debug, compression, HiZ/HiS, stencil/depth read forcing, arbitration, FIFO sizing, cacheline/watermark tuning, exception handling, indirect DFD access, summarizer timeout, and clock-gating controls.
- `CC_RB_BACKEND_DISABLE`, `GB_ADDR_CONFIG_1`, `GB_BACKEND_MAP`, `GB_GPU_ID`, `GB_ADDR_CONFIG_READ`, `CB_HW_CONTROL*`, `CB_HW_MEM_ARBITER_CTL`, `CB_FGCG_SRAM_OVERRIDE`, and `CB_CACHE_EVICT_POINTS`: render backend disable/configuration, GPU/backend mapping, color-buffer hardware control, cache arbiter, SRAM clock-gating override, and evict thresholds.
- `SPI_PQEV_CTRL` and `SPI_EXP_THROTTLE_CTRL`: event/throttle knobs for SPI pixel/export paths.
- `RMI_*`: memory-interface general controls/status, subblock busy/status, crossbar setup, probe pop logic, XNACK and UTC/UTCL1 controls, TCIW formatter, scoreboard counters/status, arbiter config, clock control, UTCL1 status, RB/GLX CID mapping, spare behavior, and redundancy repair controls.
- `UTCL1_CTRL_1`, `UTCL1_HASH_CTRL`, `UTCL1_ALOG`, and `UTCL1_STATUS`: per-client bypass, invalidation forcing, page-size, hashing, allocation logging, idle/busy, XNACK, and range-invalidation status.
- `SPI_SHADER_PGM_*_{PS,GS,HS}` and `SPI_SHADER_USER_DATA_*`: shader program code addresses/checksums, resource fields for VGPR/SGPR counts, priority, float mode, privilege/debug/trap/exceptions, scratch/LDS/shared VGPR configuration, CU enables, wave limits, instruction prefetch, and 32 dword user-data windows for PS and GS.
- `SPI_SHADER_REQ_CTRL_{PS,ESGS}`, `SPI_SHADER_GS_OUT_CONFIG_PS*`, `SPI_SHADER_GS_MESHLET_*`, and `SPI_SHADER_USER_ACCUM_*`: scheduling request grouping/throttling, GS/PS export/interpolator counts, meshlet dimensions/export allocation/interleave, and user accumulator contribution fields.

## Control Flow

This header has no runtime control flow. Its only direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select the GC 12.1.0 generated register headers for the detected ASIC.
2. Choose a register address from the matching offset header.
3. Read the current register value, prepare an indexed/debug/perf access, or construct a command/MMIO write value.
4. Use these `__SHIFT` and `__MASK` constants, typically through `REG_SET_FIELD` or `REG_GET_FIELD`, to pack or extract field values.
5. Apply the value in initialization, golden-register programming, shader/ring setup, queue scheduling, power management, reset/recovery, debugfs, hang analysis, or performance/telemetry code.

For the SPI and SX debug groups, runtime code selects a pipe/thread/group/SIMD/SH/debug bank, enables the debug register path when needed, then reads the relevant debug data or busy register. Wave lifetime and active-count fields are live counters/status registers; reset/count controls and selector registers must be sequenced by the driver or firmware, not by this header.

For TD/TA, DB/CB/GB, RMI, and UTCL1 fields, initialization and golden-setting paths program persistent hardware policy: texture formatting and determinism, backend compression/debug modes, cache and FIFO depths, arbitration, memory-interface routing, XNACK behavior, UTCL1 bypass/hash/page-size, and clock-gating overrides. Status registers are read by diagnostics and hang/recovery paths to determine which subblocks remain busy.

For SH shader-program fields, graphics pipeline setup programs code base addresses, resource descriptors, per-stage user SGPR/user-data registers, trap/exception behavior, CU masks, wave limits, GS meshlet parameters, and GS/PS export/interpolator counts before waves are launched. The macros do not document the higher-level packet ordering, cache flush, VMID, or firmware sequencing needed around those writes.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, command submission, and AMDGPU initialization/recovery code.

SPI/SX status fields are mostly live hardware state: busy bits, active wave counts, work-pending bits, scratch overflow attribution, wave lifetime counters, and debug-read data can change while the GPU is running. Some control fields, such as `SPI_GFX_CNTL__RESET_COUNTS`, debug enable/selectors, crawler controls, CU masks, and trap-screen ranges, persist until reprogrammed or reset and may have side effects when written.

TD/TA, DB/CB/GB, RMI, and UTCL1 control registers persist as pipeline, cache, routing, arbitration, compression, XNACK, clock-gating, and TLB/cache policy. Incorrect full-register writes can alter unrelated reserved or mode bits, disable compression or cache behavior, starve queues, force unnecessary bypasses, or leave the frontend/backend stuck in a debug or low-power override mode. Busy/status registers should be treated as volatile, and indirect DFD/debug accesses may need hardware-specific select/read sequencing outside this header.

Shader-program and user-data registers are persistent pipeline state for a draw or dispatch context. Program low/high address fields, user-data address fields, resource descriptors, CU masks, wave limits, trap/exception enables, LDS/shared VGPR sizing, meshlet controls, and export/interpolator counts must match the compiled shader and command stream. A bad mask or shift can point execution at the wrong code address, allocate the wrong VGPR/SGPR/LDS resources, corrupt user SGPR mapping, misconfigure trap handling, or produce invalid exports.

## Dependencies And Integration Points

This chunk depends on the generated GC 12.1.0 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_offset.h` provides matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_default.h`, where present, provides reset/default values for related registers.
- Common AMDGPU macros and helpers, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and golden-register programming helpers, consume these field definitions.
- GC 12.1.0 code that includes this header includes AMDGPU graphics initialization/recovery, MES, SDMA, IMU, gfxhub, KFD queue management, and AMDKFD interop paths.

Integration points include shader setup for PS/GS/HS/LS, command processor and graphics ring initialization, KFD/compute scheduling masks, trap/debug-screen programming, debugfs and hang dumps, performance and wave-lifetime telemetry, golden-register tables, power/clock-gating policy, cache/TLB invalidation diagnostics, XNACK handling, render-backend compression and eviction tuning, and RMI/UTCL1 routing between shader, texture, render-backend, and memory-system blocks.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong shift or mask compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- The chunk starts and ends mid-family. It begins in the tail of `SX_DEBUG_BUSY_9` and ends in the middle of `SPI_SHADER_PGM_RSRC1_HS`; adjacent chunks are required for complete SX and HS/LS shader-resource context.
- Similar register families are not interchangeable. PS, GS, ESGS, HS, CS, GFX, HP3D, TD/TA, DB/CB, and RMI fields often look structurally alike but have different widths, reserved bits, side effects, or stage-specific meanings.
- Debug and status registers can be volatile, latched, sticky, clear-on-read, or write-one-to-clear depending on hardware behavior not encoded here. Casual debug writes can disturb the state being investigated.
- Full-width `DATA`, `MEM_BASE`, and `CHECKSUM` masks do not imply unconstrained values. Address fields can have alignment, address-unit, VM, high/low split, or packet-ordering constraints outside this header.
- CU/WGP masks and shader resource fields affect scheduling and occupancy. Incorrect packing can disable compute units, over-allocate resources, break fairness, or produce launch failures only under specific shader stages.
- TD/TA determinism, texture-format, rounding, and PRT bits can cause subtle rendering differences rather than obvious crashes.
- DB/CB/RMI/UTCL1 control fields are high-risk for coherency and hangs: compression disables, cache bypasses, eviction points, FIFO depths, watermarks, XNACK behavior, and routing/hash fields can create data corruption, stalls, performance collapse, or reset loops if misprogrammed.
- Meshlet and GS/PS export fields must match shader compiler output. Mismatched threadgroup dimensions, export counts, primitive/interpolator counts, or LDS sizes can corrupt geometry/pixel data.
- Reserved masks are present in several registers. Callers should preserve reserved bits unless a hardware programming sequence explicitly requires a value.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_12_1_0_sh_mask.h`, especially GC 12.1.0 GFX, MES, KFD, gfxhub, SDMA, IMU, reset, debug, and power-management paths.
- Mechanical comparison against AMD's authoritative GC 12.1.0 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_12_1_0_offset.h` and expected reset/default entries where generated.
- Static mask/shift sanity checks: masks align with shifts, field masks do not overlap unexpectedly, repeated user-data families remain consistent, full-width fields use `0xFFFFFFFFL`, and reserved masks cover only unused bits.
- GFX bring-up and suspend/resume tests that validate golden-register writes for TA/TD, DB/CB, RMI, and UTCL1 controls without hangs or unexpected busy bits.
- Shader execution tests for PS, GS/ESGS, meshlet paths, and HS/LS startup that exercise program address packing, resource descriptors, user SGPR counts, scratch/trap/exception bits, CU masks, wave limits, LDS/shared VGPR sizing, exports, and user-data windows.
- Debug/hang tests that read `SPI_DEBUG_*`, `SX_DEBUG_BUSY_*`, `SPI_DEBUG_BUSY`, `SPI_SLAVE_DEBUG_BUSY`, TD/TA/DB/RMI/UTCL1 status fields, and scratch overflow attribution during known workloads.
- Wave telemetry tests that reset/read lifetime counters, active wave counts, max wave IDs, work-pending fields, CSQ active counts, and lightweight-benchmark data under controlled workloads.
- Render and texture stress tests covering anisotropic filtering, deterministic modes, gather/rounding behavior, PRT, depth/stencil compression, color-buffer cache eviction, DCC/compression behavior, backend mapping, and trap-screen ranges.
- Memory-system stress tests with XNACK, UTCL1 invalidation, RMI reorder/bypass/no-fill controls, crossbar arbitration, scoreboard status, and CID mapping while checking for faults, stale data, or reset loops.
- Runtime warning signals include stuck SPI/SX/TA/TD/DB/RMI/UTCL1 busy bits, shader launch failures, trap storms, bad scratch overflow attribution, incorrect wave counts, rendering corruption, cache coherency failures, XNACK anomalies, and repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002602`. It covers lines 25182-27636 of `gc_12_1_0_sh_mask.h`. The final per-file research should merge this with adjacent chunks to complete the `SX_DEBUG_BUSY_9` context before line 25182 and the remaining HS/LS shader-resource definitions after line 27636.
