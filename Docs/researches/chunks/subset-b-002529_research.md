# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 7504-9879

Covered source range: lines 7504-9879 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h`

## Purpose

This chunk is a generated AMDGPU GC 11.0.3 register-field shift/mask header section. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The constants describe bit positions for graphics-core MMIO registers so AMDGPU code can compose, update, and decode 32-bit register values without embedding raw bit arithmetic at call sites.

The range exports 2,187 `#define` lines for 173 distinct registers. Macro names follow the generated AMD convention:

- `REGISTER__FIELD__SHIFT`: starting bit position of a hardware field.
- `REGISTER__FIELD_MASK`: field mask in its final 32-bit register position.

The chunk starts in the middle of `IA_UTCL1_STATUS_2`: the first lines contain the remaining shift definitions and all mask definitions for that register. The preceding part of `IA_UTCL1_STATUS_2` is in the previous chunk. This matters for merge/reconciliation because the complete register report should not treat the missing early shifts as absent from the source file.

## Register Areas Covered

The opening portion finishes front-end, UTCL1, graphics-engine, VGT, PA, and clipping controls:

- `IA_UTCL1_STATUS_2`, `IA_UTCL1_CNTL`, `IA_UTCL1_STATUS`, `WD_UTCL1_CNTL`, and `WD_UTCL1_STATUS` expose UTCL1 fault, retry, PRT, invalidate, bypass, snoop, VMID-reset, MTYPE, LLC no-allocate, and XNACK redo timer fields.
- `WD_CNTL_STATUS`, `WD_QOS`, `CC_GC_PRIM_CONFIG`, `CC_GC_SA_UNIT_DISABLE`, and `CC_GC_SHADER_ARRAY_CONFIG` cover draw-distributor busy state, draw stall, write-disable guards, inactive primitive assembler masks, disabled shader arrays, and inactive WGP masks.
- `GE_RATE_CNTL_1`, `GE_RATE_CNTL_2`, `GE_PRIV_CONTROL`, `GE_STATUS`, `GE2_SE_CNTL_STATUS`, `GE_SPI_IF_SAFE_REG`, and `GE_PA_IF_SAFE_REG` describe graphics-engine pacing, merged HS/GS and LS/ES modes, reset-on-pipeline-change behavior, primitive-group clamping, fine-grain clock-gating override, thread-trace/perf-counter state, GE/SPI safe data, and GE/PA interface safe data.
- `VGT_SYS_CONFIG`, `VGT_GS_MAX_WAVE_ID`, and `VGT_RESET_DEBUG` describe dual-core mode, LS/HS thread group sizing, subgroup count, GS wave ID reporting, and many debug disables for GS, tessellation, WD, prefetch, mesh shader attribute packing, distribution pipes, and patch optimizations.
- `GFX_PIPE_CONTROL` supplies hysteresis and context suspend control fields.
- `PA_CL_CNTL_STATUS`, `PA_CL_ENHANCE`, `PA_CL_RESET_DEBUG`, `PA_SU_CNTL_STATUS`, and `PA_SC_FIFO_DEPTH_CNTL` cover clipping and setup busy state, clip vertex reorder, NGG/primitive-filter behavior, NaN processing, near-clip programming, rate control, inner-edge flags, fine clock-gating disables, and PA-to-SC FIFO depth.

The `gc_sqdec` address block starts at line 7806 and covers shader queue/cache and local data share controls:

- `SQ_CONFIG`, `SQC_CONFIG`, and `SQC_MISC_CONFIG` include instruction/data cache sizing, miss/hit FIFO depth, cache eviction and force-miss modes, per-VMID invalidation disable, SQC clock-gating disables, GL1 clock enable override, and miscellaneous SQC/SPI/SQ fine-grain clock-gating overrides.
- `LDS_CONFIG` defines local data share behavior such as address-out-of-range reporting, wave32 interpolation issue control, and LDS/SQC fine-grain clock-gating overrides.
- `SQ_RANDOM_WAVE_PRI`, `SQ_FIFO_SIZES`, `SQ_ARB_CONFIG`, `SQ_PERF_SNAPSHOT_CTRL`, `SQ_INTERRUPT_AUTO_MASK`, and `SQ_INTERRUPT_MSG_CTRL` describe wave priority randomization, interrupt/thread-trace/export/VMEM FIFO sizing, workgroup arbitration intervals, snapshot timer controls, interrupt auto masks, and interrupt message stalling.
- `SQ_DSM_CNTL` and `SQ_DSM_CNTL2` expose design-for-stress/error-injection knobs for SGPR, LDS, SP, wavefront stall, SPI backpressure, injected delay selection, and single-write forcing.
- `SP_CONFIG`, `SQG_STATUS`, `SQG_GL1H_STATUS`, `SQG_CONFIG`, `SQ_DEBUG_HOST_TRAP_STATUS`, and `CC_GC_SHADER_RATE_CONFIG` cover SP cache/clock/debug control, SQG register busy state, GL1H ACK/XNACK error status, SQG prefetch and XNACK interrupt mask, host-trap pending count, and shader-rate DPFP rate selection.
- `SQ_WATCH{0..3}_ADDR_H`, `SQ_WATCH{0..3}_ADDR_L`, and `SQ_WATCH{0..3}_CNTL` define watchpoint address, mask, VMID, and valid fields.
- `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD` define indirect wave/workitem indexing, indexed data payload, and command fields including mode, VMID check, wave ID, queue ID, and VM ID.

The `gc_shsdec` address block is dominated by shader export/interpolator debug and SPI controls:

- `SX_DEBUG_BUSY`, `SX_DEBUG_BUSY_2` through `SX_DEBUG_BUSY_10`, `SX_DEBUG_BUSY_5` through `SX_DEBUG_BUSY_9`, and `SX_DEBUG_1` provide a very broad busy/valid/free/idle view across SX color write-control queues, DB interface FIFOs, color buffer banks, position buffer banks, scoreboard state, export buffers, shader input/output handshakes, command/address paths, and reserved debug lanes.
- `SPI_PS_MAX_WAVE_ID`, `SPI_GFX_CNTL`, `SPI_DEBUG_READ`, `SPI_DSM_CNTL`, `SPI_DSM_CNTL2`, `SPI_EDC_CNT`, and `SPI_DEBUG_BUSY` define pixel-shader wave ID status, graphics control, debug read data, SPI stress/error injection control, EDC counters, and SPI busy status bits.
- `SPI_CONFIG_PS_CU_EN` and `SPI_PG_ENABLE_STATIC_WGP_MASK` gate pixel-shader CU/WGP enablement and static WGP masks.
- `SPI_WF_LIFETIME_CNTL`, `SPI_WF_LIFETIME_LIMIT_0` through `_5`, `SPI_WF_LIFETIME_STATUS_*`, and `SPI_WF_LIFETIME_DEBUG` define wavefront lifetime counter control, max-count limits, warning enables, status counters, interrupt-sent flags, and debug start-value override. The status registers are sparse by name: this chunk includes `_0`, `_2`, `_4`, `_6`, `_7`, `_9`, `_11`, `_13`, `_14`, `_15`, `_16`, `_17`, `_18`, `_19`, `_20`, and `_21`.
- `SPI_LB_CTR_CTRL`, `SPI_LB_WGP_MASK`, `SPI_LB_DATA_REG`, `SPI_LB_DATA_WAVES`, `SPI_LB_DATA_PERWGP_WAVE_HSGS`, and `SPI_LB_DATA_PERWGP_WAVE_CS` describe load-balancer counter loading, wave selection, clear-on-read, reset, WGP masks, raw counter data, and per-WGP wave counts for HS/GS/CS.
- `SPI_GDS_CREDITS`, `SPI_SX_EXPORT_BUFFER_SIZES`, `SPI_SX_SCOREBOARD_BUFFER_SIZES`, `SPI_CSQ_WF_ACTIVE_STATUS`, and `SPI_CSQ_WF_ACTIVE_COUNT_0` through `_3` define GDS command/data credits, SX export and scoreboard sizing, and active wavefront status/count/event fields.
- `SPIS_DEBUG_READ` and `BCI_DEBUG_READ` expose raw debug data fields.
- `SPI_P0_TRAP_SCREEN_*` and `SPI_P1_TRAP_SCREEN_*` define trap-screen memory-base low/high registers and minimum VGPR/SGPR thresholds for two trap-screen partitions.

The `gc_tpdec` address block covers texture address/data pipe controls:

- `TD_CNTL`, `TD_STATUS`, `TD_POWER_CNTL`, `TD_CNTL2`, and `TD_SCRATCH` expose TD filtering/math options, residency-map overrides, UTC-error VGPR preservation, gather4 modes, RT BVH4 arbiter selection, power-throttle disable, round-to-zero controls, scoreboard depth, formatter power options, LDS return FIFO credit, and scratch storage.
- `TA_CNTL`, `TA_CNTL_AUX`, `TA_CNTL2`, `TA_STATUS`, and `TA_SCRATCH` describe TA-to-SQ XNACK clock gating, aligner/TD FIFO credits, anisotropic filtering and deterministic-mode disables, gather and swizzle behavior, cubemap/array rounding, point-sample acceleration, element-size hashing, coordinate truncation, unlit-quad elimination, FIFO non-empty flags, per-subunit busy bits, aggregate busy state, and scratch storage.

The `gc_gdsdec` address block covers global data share configuration, faults, and reliability state:

- `GDS_CONFIG`, `GDS_CNTL_STATUS`, and `GDS_ENHANCE` expose write-disable/unused fields, GDS/GRBM/DS/GWS/ORD busy state, clamp state, credit busy bits, and enhancement controls.
- `GDS_PROTECTION_FAULT` and `GDS_VM_PROTECTION_FAULT` define fault-detected status plus metadata for GRBM source, SE/SA/WGP/SIMD/wave, GWS/OA/TMZ, VMID, and address.
- `GDS_EDC_CNT`, `GDS_EDC_GRBM_CNT`, `GDS_EDC_OA_DED`, `GDS_EDC_OA_PHY_CNT`, and `GDS_EDC_OA_PIPE_CNT` define single/double error counters and per-ME/pipe/PHY EDC status bits.
- `GDS_DSM_CNTL` and `GDS_DSM_CNTL2` define stress/error-injection controls for GDS memory, input queue, PHY command RAM, PHY data RAM, pipe memory, injection-delay selection, and single-write forcing.

The `gc_rbdec` address block begins at line 9469 and the chunk covers depth-buffer/debug registers through the first fields of `DB_DEBUG5`:

- `DB_DEBUG`, `DB_DEBUG2`, `DB_DEBUG3`, `DB_DEBUG4`, `DB_DEBUG6`, `DB_DEBUG7`, and the beginning of `DB_DEBUG5` cover many DB disable/force/debug knobs: depth/stencil compression disables, full tile fetches, forced depth/stencil reads, HiZ/HiS forcing, fast Z/stencil disables, viewport/Z-plane optimizations, context suspend insertion/deletion, EQAA behavior, TC write-combine controls, clock/debug gating, cache preload, VRS conflict controls, NOZ power savings, OSB deadlock fixes, LQO RAM optimization, and spare bits.
- `DB_ETILE_STUTTER_CONTROL`, `DB_LTILE_STUTTER_CONTROL`, `DB_EQUAD_STUTTER_CONTROL`, and `DB_LQUAD_STUTTER_CONTROL` define interval and timeout fields for tile/quad stutter behavior.
- `DB_CREDIT_LIMIT`, `DB_WATERMARKS`, `DB_FREE_CACHELINES`, `DB_FIFO_DEPTH1`, `DB_FIFO_DEPTH2`, and `DB_FIFO_DEPTH3` define DB internal credits, depth/free/flush watermarks, cacheline availability, and FIFO depths for MI, MCC, QC, equad/etile/lquad/ltile, OSB, OREO, and quad read requests.
- `DB_SUBTILE_CONTROL` defines X/Y subtile encodings for MSAA1, MSAA2, MSAA4, MSAA8, and MSAA16.
- `DB_LAST_OF_BURST_CONFIG`, `DB_RING_CONTROL`, `DB_MEM_ARB_WATERMARKS`, and `DB_EXCEPTION_CONTROL` define burst sizing/timeouts, LOB generation/flush/coalescing/disabling behavior, ring counter control, memory arbitration watermarks, panic disables, auto flush, force summarize, and DTAG watermark fields.

## APIs, Types, and Functions

There are no C functions, types, structs, or enums in this chunk. The API surface is the exported macro namespace. Callers typically use these constants through AMDGPU register helpers rather than directly spelling bit operations:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` clears `REGISTER__FIELD_MASK` and inserts `field_value << REGISTER__FIELD__SHIFT`.
- `REG_GET_FIELD(value, REGISTER, FIELD)` extracts a masked field by applying `REGISTER__FIELD_MASK` and shifting by `REGISTER__FIELD__SHIFT`.
- `RREG32*`, `WREG32*`, `RREG32_SOC15`, `WREG32_SOC15`, and related helpers perform the actual MMIO read/write once an address from the matching GC 11.0.3 offset header has been selected.

The header also supports direct arithmetic patterns such as `(value & REGISTER__FIELD_MASK) >> REGISTER__FIELD__SHIFT`, but the driver convention is to use helper macros where possible to reduce manual mistakes.

## Control Flow and Data Flow

This header has no runtime control flow. Its data flow is compile-time macro substitution:

1. A GC 11.0.3 AMDGPU source file includes `gc/gc_11_0_3_offset.h` for register addresses and `gc/gc_11_0_3_sh_mask.h` for field layout.
2. Driver code selects a register address, often via `SOC15_REG_OFFSET(...)` or a generated register macro from the offset header.
3. Code reads, modifies, or writes a 32-bit register value using AMDGPU helper macros.
4. The helper expands to this header's `__SHIFT` and `_MASK` definitions to isolate the targeted field.

For status registers such as `WD_CNTL_STATUS`, `TD_STATUS`, `TA_STATUS`, `GDS_CNTL_STATUS`, and the `SX_DEBUG_BUSY*`/`SPI_DEBUG_BUSY` groups, the constants are usually read-side decode metadata. For control/debug registers such as `VGT_RESET_DEBUG`, `SQ_CONFIG`, `SQC_CONFIG`, `SPI_WF_LIFETIME_CNTL`, `TA_CNTL_AUX`, `GDS_DSM_CNTL2`, and `DB_DEBUG*`, the constants describe writable fields that can change GPU behavior.

## State and Persistence Behavior

The file itself stores no state. The state is in GPU hardware registers addressed elsewhere. These masks and shifts define how driver-visible state is interpreted and changed:

- Busy/status bits reflect transient hardware state for command distribution, geometry, shader, texture, global-data-share, depth-buffer, and cache/FIFO pipelines.
- Fault/protection fields preserve hardware fault metadata until the underlying register semantics clear or overwrite them; examples include UTCL1 fault/retry/PRT IDs and GDS protection fault address/source fields.
- Debug and control fields can persist in hardware across normal register-programming sequences until reset, context reinitialization, or a later MMIO write changes them.
- Error-injection and DSM controls (`SQ_DSM_*`, `SPI_DSM_*`, `GDS_DSM_*`) are especially stateful because enabling them affects future hardware stress/error behavior rather than merely reporting current state.
- Counter/status registers such as SPI wavefront lifetime status, SPI load-balancer counters, GDS EDC counters, and DB ring counters can have read, clear, or saturation semantics determined by hardware and by the code that programs companion control fields.

## Dependencies and Integration Points

This chunk depends on the rest of `gc_11_0_3_sh_mask.h` for the include guard and complete register-field namespace. It is meaningful only with the companion address header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h`, which supplies the register addresses for these field definitions.

Repository integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, which includes both `gc_11_0_3_offset.h` and `gc_11_0_3_sh_mask.h` for GC 11.0.3 graphics setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`, which includes this header for GC 11.0.3 GFXHUB register field access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`, which includes this header for IMU-specific GC 11.0.3 register programming.
- Shared AMDGPU register helper infrastructure that expects generated field names to be stable and exactly paired as `REGISTER__FIELD__SHIFT` plus `REGISTER__FIELD_MASK`.

The chunk also integrates with ASIC revision selection for GC 11.0.3 devices. Firmware declarations and display-side ASIC revision checks in nearby AMDGPU/DC code identify this generation, while the actual field-level programming for these GC registers is routed through the generated register headers.

## Risks and Gotchas

- Manual edits are high risk. A wrong mask or shift can compile cleanly but program or decode the wrong hardware bits.
- The chunk starts mid-register for `IA_UTCL1_STATUS_2`; generated-report tooling must merge with the previous chunk to reconstruct the whole register.
- Some fields are read-only status, some are writable controls, and some are clear-on-read/write-one-to-clear or hardware-latched in practice. The mask header does not encode access type, so callers need hardware knowledge and existing driver patterns.
- Many debug fields are negative controls (`DISABLE_*`, `FORCE_*`, `BYPASS_*`). Inverting semantics while composing register values can silently disable critical optimizations, coherency behavior, power management, or reset/workaround logic.
- The `DSM` and `*_ENABLE_ERROR_INJECT` fields are not ordinary tuning bits. Accidentally enabling stress/error-injection paths could produce artificial faults, EDC events, or data corruption symptoms.
- UTCL1, GDS protection fault, and VMID fields are security and fault-diagnostics sensitive. Mis-decoding source IDs, VMIDs, or fault addresses would mislead GPU fault reporting and recovery.
- Repeated or sparse numbered registers are intentional. Examples include `SQ_WATCH0` through `SQ_WATCH3`, multiple `SPI_WF_LIFETIME_STATUS_*` registers with skipped numbers, and `SX_DEBUG_BUSY*` sequences. Tooling should not assume dense numbering.
- A field whose hardware name includes `MASK` would generate `*_MASK_MASK`; this specific chunk has normal `_MASK` suffixes, but the broader generated-header convention must preserve such names.
- Several masks use full-width or high-bit fields such as `0xFFFFFFFFL`, `0xFFFF0000L`, and `0x80000000L`; signedness assumptions in external tooling can corrupt interpretation if values are parsed as signed 32-bit integers.

## Test and Validation Signals

Useful validation for this chunk is mostly build-time and hardware-integration oriented:

- Kernel/driver build coverage for translation units including `gc_11_0_3_sh_mask.h`, especially `gfx_v11_0_3.c`, `gfxhub_v3_0_3.c`, and `imu_v11_0_3.c`.
- Static generation checks that every `REGISTER__FIELD_MASK` in the range has a corresponding `REGISTER__FIELD__SHIFT`, with explicit allowance for the chunk-boundary split at `IA_UTCL1_STATUS_2`.
- Static checks that each mask is compatible with its shift and field width, and that repeated groups such as `SQ_WATCH{0..3}`, `SPI_CSQ_WF_ACTIVE_COUNT_{0..3}`, and tile/FIFO depth registers preserve the expected symmetric layouts.
- Runtime smoke on GC 11.0.3 hardware that exercises graphics initialization, shader queue setup, GFXHUB setup, command submission, VM fault reporting, and GPU reset/recovery paths.
- Debugfs or tracing checks that decode busy/fault/status registers without impossible values, especially UTCL1 fault IDs, GDS protection fault metadata, TA/TD busy state, SPI wavefront lifetime counters, and DB watermarks/FIFO depths.
- Negative testing should avoid enabling DSM/error-injection fields outside controlled diagnostics.

## Chunk Boundary Notes

This is chunk 4 of 18 for `gc_11_0_3_sh_mask.h` in the current manifest. It begins at line 7504 with the tail of `IA_UTCL1_STATUS_2` and ends at line 9879 inside `DB_DEBUG5`; the remaining `DB_DEBUG5` fields continue in the next chunk. The final per-file report should reconcile this range with chunks 1-3 and 5-18 for complete GC 11.0.3 register coverage.
