# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_sh_mask.h lines 19722-22327

## Scope

This chunk is a generated AMD GC 9.0 register shift/mask header slice. It contains C preprocessor `#define` constants only: for each named hardware register field, one `<REGISTER>__<FIELD>__SHIFT` macro and one `<REGISTER>__<FIELD>_MASK` macro define the field position and bit mask inside a 32-bit register value.

The selected range contains 2,123 `#define` statements covering 471 register-field groups. There are no functions, structs, enums, global variables, allocations, locks, direct MMIO operations, persistence formats, or executable branches in this range.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM hardware metadata. It is unrelated to Ceph filesystem protocols or storage behavior except by source-tree placement.

## Purpose

`gc_9_0_sh_mask.h` gives AMDGPU GC 9.0 code symbolic field positions for graphics-core registers. Driver code combines these masks with register offsets from `gc_9_0_offset.h` and SOC15 MMIO helpers to compose, read, decode, or modify register values without embedding raw bit numbers.

This chunk starts in the `gc_gfxudec` user/config command-processor and draw-state field definitions, then crosses these major surfaces:

- CP indirect draw/dispatch/index address fields, index type, GDS backup address fields, sample-status bits, and ME coherency command base/size/status fields.
- RLC GPM performance counter selector fields and `GRBM_GFX_INDEX`, which selects shader engine, shader array, and instance targets for indexed/broadcast register writes.
- VGT, WD, IA, PA, and screen/trap draw-state fields for primitive/index type, streamout filled sizes, index ranges, tessellation factor memory, work distributor buffers, multi-VGT setup, line stipple, screen extents, and trap-screen counters.
- SQ thread trace buffer, token, performance, mode, status, watermark, counter, and userdata fields.
- SQC cache/writeback controls, texture constant base fields, DB occlusion/Z-pass counters, and GDS read/write/atomic/GWS/OA fields.
- SPI configuration controls before the chunk switches into generated performance-counter address blocks.
- `gc_perfddec` performance-counter data fields for CP, GRBM, WD, IA, VGT, PA, SPI, SQ, SX, GDS, TA/TD/TCP/TCC/TCA, CB, DB, RLC, and RMI counter low/high registers.
- UTCL2/ATCL2 and VM L2 counter fields for `ATC_L2_PERFCOUNTER_*` and `MC_VM_L2_PERFCOUNTER_*`.
- `gc_perfsdec` performance-counter selector, mode, window, filter, and global control fields for the same GC sub-blocks.
- The beginning of RLC streaming performance monitor fields: `RLC_SPM_PERFMON_CNTL`, ring base/size, and segment sizing.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` is the bit offset for `FIELD`.
- `<REGISTER>__<FIELD>_MASK` is the already-positioned bit mask for `FIELD`.
- `// addressBlock:` comments mark generated register-database block boundaries such as `gc_perfddec`, `gc_utcl2_atcl2pfcntrdec`, `gc_utcl2_vml2prdec`, and `gc_perfsdec`.

AMDGPU code normally consumes these macros through helpers such as `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and `REG_GET_FIELD(value, REGISTER, FIELD)`, together with `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_RLC`, `WREG32_SOC15_RLC_SHADOW`, `SOC15_REG_OFFSET`, and golden-register table macros.

Representative field families in this range include:

- Address low/high pairs: `CP_DRAW_INDX_INDR_ADDR_HI`, `CP_DISPATCH_INDR_ADDR`, `CP_INDEX_BASE_ADDR`, `CP_GDS_BKUP_ADDR`, `VGT_TF_MEMORY_BASE`, `WD_*_BUF_BASE`, `SQ_THREAD_TRACE_BASE`, `TA_CS_BC_BASE_ADDR`, and `RLC_SPM_PERFMON_RING_BASE_*`.
- Coherency fields: `CP_ME_COHER_CNTL` destination enables for generic bases, color-buffer destinations, DB destination, and additional destination bases; `CP_ME_COHER_SIZE*`, `CP_ME_COHER_BASE*`, and `CP_ME_COHER_STATUS`.
- Indexed addressing fields: `GRBM_GFX_INDEX__INSTANCE_INDEX`, `SH_INDEX`, `SE_INDEX`, and broadcast-write bits.
- Draw-state fields: `VGT_INDEX_TYPE`, `VGT_MULTI_PRIM_IB_RESET_EN`, `VGT_HS_OFFCHIP_PARAM`, `IA_MULTI_VGT_PARAM`, and line/screen/trap-state fields in `PA_SC_*` and `PA_SU_*`.
- SQ thread-trace fields: buffer size/base masks, token/perf masks, control/mode, status bits such as `BUSY`, `UTC_ERROR`, `FINISH_PENDING`, `DROPPED_CNTR`, and high-water/counter/userdata fields.
- GDS fields: direct read/write address/data/burst fields, atom control/source/destination/readback fields, GWS resource fields, and ordered-append counter/address/ring fields.
- Performance-counter data registers: almost all counter data fields are full-width 32-bit `PERFCOUNTER_*` low/high values, with repeated pairs by block and counter index.
- Performance-counter selector registers: repeated `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, and `PERF_MODE*` fields across CPG/CPC/CPF/GRBM/WD/IA/VGT/PA/SPI/SQ/SX/GDS/TA/TD/TCP/TCC/TCA/CB/DB blocks.
- Filter and SPM fields: `CB_PERFCOUNTER_FILTER` operation/format/clear/MRT/sample/fragment filters, `SQ_PERFCOUNTER_CTRL*`, `SQ_PERFCOUNTER_MASK`, `CP_PERFMON_CNTL`, `CPF/CPG_TC_PERF_COUNTER_WINDOW_SELECT`, latency-stat selectors, and RLC SPM ring/sample/segment fields.

## Control Flow

This header has no runtime control flow. It only gives compile-time constants to code that performs register programming or decoding.

The implied runtime flow is:

1. GC 9.0 driver code chooses a register offset from the matching offset header and a field macro from this shift/mask header.
2. The code builds or extracts a field value with `REG_SET_FIELD`, `REG_GET_FIELD`, or explicit mask/shift arithmetic.
3. SOC15 register helpers issue the MMIO read, write, shadowed write, or indirect access against the selected GC instance.
4. The command processor, graphics pipeline, shader core, GDS, performance monitor, or RLC block interprets the resulting register value.

For draw-state and CP registers, the actual sequencing is owned by command submission, ring setup, fence/coherency emission, KFD compute queue setup, and graphics pipeline programming. For GRBM indexed writes, callers must select the correct SE/SH/instance or broadcast scope before accessing registers behind the GRBM index. For performance counters and thread trace, external profiling/debug paths handle counter selection, trace-buffer setup, sampling, start/stop, and readback; this chunk only names the bitfields.

## State And Persistence Behavior

The macros are stateless compile-time constants. Persistent or volatile state exists only in the GPU registers and in memory objects whose addresses are programmed through those registers.

State represented by this chunk includes indirect draw/dispatch/index pointers, ME coherency command windows, selected GRBM target instance, VGT/IA/WD/PA draw parameters, SQ thread-trace buffers and status, GDS read/write/atomic/OA/GWS control state, SPI configuration knobs, performance counter data and selection state, latency-stat selectors, counter windows, CB filtering, and RLC SPM ring/segment layout.

Some represented registers are durable configuration until rewritten, context-switched, power-gated, reset, or restored during suspend/resume. Others are counters, latches, status bits, command registers, readback FIFOs, or self-clearing controls. This generated header does not encode read-only, write-only, write-one-to-clear, sticky, privilege, broadcast, clock-domain, reset-default, or sequencing semantics; those rules live in hardware documentation and in the code paths that use these fields.

The mask definitions themselves must match the register database exactly. A stale mask can compile successfully while silently corrupting adjacent fields, missing high bits, or causing code to poll/decode the wrong status condition.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_offset.h` supplies matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_0_default.h` and nearby generated headers provide related reset/default metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h` provides enum values for some GC 9.0 concepts, including SQ thread-trace token/mode types.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_0.c` includes this header for GC 9.0 graphics initialization, golden settings, GRBM indexed targeting, RLC SPM programming, and register access setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v9.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v9.c` include it for KFD/compute queue and MQD-related GC 9.0 register programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_arcturus.c`, `gfxhub_v1_0.c`, `gmc_v9_0.c`, `mxgpu_ai.c`, and `soc15.c` also include the GC 9.0 mask header.
- PowerPlay Vega10 integration includes it through `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`.

Observed direct use patterns in this source tree include `GRBM_GFX_INDEX` field composition in `gfx_v9_0.c` and `amdgpu_amdkfd_gfx_v9.c`, golden settings for `SPI_CONFIG_CNTL_1` and RLC SPM-related registers in `gfx_v9_0.c`, and explicit RLC SPM mask/shift arithmetic in `gfx_v9_0.c` around SPM VMID selection. Many performance-counter and SQ thread-trace definitions are integration points for profiling, debugging, and register-dump decoding even when they are not all referenced by current in-tree code.

Runtime integration points include graphics command submission, compute/KFD queue setup, GRBM broadcast and per-instance register access, GPU profiling/perfmon, SQ thread tracing, GDS atomics/OA/GWS diagnostics, cache/coherency events, streamout/tessellation/draw setup, RLC streaming performance monitor capture, debug register dumps, SR-IOV-capable GC 9.0 paths, reset, suspend/resume, and golden-register programming.

## Risks And Edge Cases

- Generated-header drift is the main risk. Wrong shifts or masks compile cleanly and can corrupt register fields at runtime.
- This chunk starts mid logical `gc_gfxudec` sequence at `CP_DRAW_INDX_INDR_ADDR_HI`; the low half `CP_DRAW_INDX_INDR_ADDR` is in the previous chunk.
- This chunk ends mid RLC SPM sequence at `RLC_SPM_PERFMON_SEGMENT_SIZE`; `RLC_SPM_SE_MUXSEL_*` and later SPM fields continue in the next chunk.
- Address-pair fields must be programmed consistently. Low/high masks for CP, VGT, WD, SQ trace, TA, and RLC SPM ring base registers can truncate or misplace GPU addresses if paired incorrectly.
- `GRBM_GFX_INDEX` controls broadcast versus per-SE/SH/instance access. A mask error or stale selected index can write only one hardware instance when broadcast was intended, or broadcast a per-instance update globally.
- Coherency fields in `CP_ME_COHER_*` are command-submission critical. Incorrect destination-enable or base/size masks can leave CB/DB or memory ranges unflushed, or flush the wrong range.
- Draw-state fields in VGT/IA/WD/PA are tightly coupled to packet streams and hardware primitive assembly. Mask errors can present as rendering corruption, hangs, missing primitives, or incorrect streamout/tessellation behavior.
- SQ thread trace and performance counter fields are mostly debug/profiling-facing, but they interact with trace buffer memory, sampling modes, high-water status, and dropped-counter indicators. Bad field definitions can lose trace data or mislead performance tooling.
- GDS read/write/atomic/OA/GWS fields affect shared GPU data resources. Incorrect atom size/base/operation/resource masks can corrupt GDS state or break synchronization diagnostics.
- Counter families are highly repetitive. Per-block/per-index selector fields differ subtly in width, especially between CB 9-bit event selectors and 10-bit selectors used by many other blocks.
- `RESERVED` fields appear in several registers. Callers should avoid relying on generated reserved masks as permission to write arbitrary values unless the hardware programming sequence explicitly requires it.
- Full-width `0xFFFFFFFFL` masks rely on C integer promotion behaving as intended in the existing kernel macro environment. Consumers should keep values unsigned where needed.

## Test Signals

Useful validation is mostly generated-data consistency plus GC 9.0 hardware exercise:

- Build AMDGPU configurations that include GC 9.0 support. Missing or malformed macros should surface in `gfx_v9_0.c`, KFD GC 9 code, SOC15 code, and PowerPlay Vega10 includes.
- Mechanically compare every shift/mask pair in this chunk against AMD's authoritative GC 9.0 register database.
- Cross-check every register field here against a matching register offset in `gc_9_0_offset.h`, especially at the chunk boundaries and address-block transitions.
- Verify repeated families for expected count and naming consistency: SQ thread-trace registers, GDS atom/OA/GWS registers, performance counter low/high pairs, selector/select1 variants, GRBM SE0-3 selectors, SQ counter selectors 0-15, and CB/DB counter selectors.
- Exercise `GRBM_GFX_INDEX` selection through debugfs or driver paths that target all instances versus one SE/SH/instance, confirming indexed writes land on the expected hardware block.
- Run graphics workloads that use indirect draw/dispatch, indexed draws, primitive restart, instancing, tessellation factor memory, streamout, scissor/screen extent state, and line/trap-related PA state.
- Exercise compute/KFD workloads that use queues, dispatch, GDS, and coherency operations on GC 9.0 ASICs.
- Run profiling and tracing paths that program SQ thread trace, performance counters, latency stats, CB filters, and RLC SPM ring capture; confirm counters increment, status bits decode correctly, trace buffers fill as expected, and dropped/error indicators are meaningful.
- Include reset, suspend/resume, preemption, and power/clock-gating cycles while checking that GRBM index, RLC SPM, SQ trace, and perf-counter state is saved, restored, or reinitialized by the appropriate driver paths.
- Decode known-good GC 9.0 register dumps with these masks and compare field extraction against reference tools.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002623`. The final per-file research should merge it with neighboring chunks for full `gc_9_0_sh_mask.h` coverage. The previous chunk owns the start of the indirect draw address group and earlier CP EOP/PFP/CE metadata fields. The next chunk continues the RLC SPM field definitions after `RLC_SPM_PERFMON_SEGMENT_SIZE`.
