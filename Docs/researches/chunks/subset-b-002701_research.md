# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gca/gfx_6_0_sh_mask.h lines 8716-12821

## Purpose

This chunk is generated-style bitfield metadata for AMD Southern Islands / GFX 6.0 graphics-core registers. It exposes `*_MASK` and `*__SHIFT` constants for shader-queue (`SQ`/`SQC`) descriptors, instruction encodings, wave/debug state, thread trace packets, texture/cache blocks (`TA`, `TD`, `TCP`, `TCA`, `TCC`, `TCI`), shader export (`SX`), geometry/tessellation (`VGT`), and the final `WD_DEBUG_DATA` field before the include guard closes.

The file contains no executable driver logic. Its value is the hardware contract: code that includes `gca/gfx_6_0_d.h` for offsets can include this header for field layout and then build or decode register words with `REG_SET_FIELD`, `REG_GET_FIELD`, direct masks, or command-stream packet data. The chunk is especially relevant to legacy SI AMDGPU power-management code, Radeon SI clear-state/blit tables, debug tooling, performance counters, and any generated register validation that must understand GFX6 bit positions.

## Important APIs, Types, And Data

There are no C functions, structs, enums, storage objects, callbacks, or runtime APIs in this range. The public interface is the macro naming convention:

- `REGISTER__FIELD_MASK` gives the field bit mask in the 32-bit register or packet word.
- `REGISTER__FIELD__SHIFT` gives the low-bit shift for the same field.
- Full-word payload registers use fields such as `DATA`, `SIZE`, `OFFSET`, `BASE`, `COUNTER`, or `ENCODING` with `0xffffffffL` masks.
- Register families are encoded in the macro names, not in C namespaces.

Important groups in this chunk include:

- Shader resource descriptors and instruction encodings: `SQ_BUF_RSRC_WORD1..3`, `SQ_IMG_RSRC_WORD0..7`, `SQ_IMG_SAMP_WORD0..3`, `SQ_DS_*`, `SQ_EXP_*`, `SQ_MIMG_*`, `SQ_MTBUF_*`, `SQ_MUBUF_*`, `SQ_SMRD`, `SQ_SOP*`, `SQ_VOP*`, `SQ_VINTRP`, and `SQ_INST`. These describe buffer/image/sampler descriptors and instruction packet fields such as encodings, opcodes, register operands, GLC/SLC, data masks, formats, swizzles, type, mtype, address, offsets, and destination selectors.
- Shader queue configuration and cache/debug state: `SQC_CACHES`, `SQC_CONFIG`, `SQ_CONFIG`, `SQ_FIFO_SIZES`, `SQ_DEBUG_STS_*`, `SQ_DEBUG_CTRL_LOCAL`, `SQ_SEC_CNT`, `SQ_DED_CNT`, `SQ_DED_INFO`, and `SQC_SECDED_CNT`.
- Wave and indirect debug accessors: `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_WAVE_STATUS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_MODE`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_IB_DBG0`, `SQ_WAVE_IB_STS`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_EXEC_*`, `SQ_WAVE_PC_*`, `SQ_WAVE_TBA_*`, `SQ_WAVE_TMA_*`, `SQ_WAVE_TTMP0..11`, and wave instruction words. These define per-wave status, allocation, PC, trap, SIMD/CU/VMID, and temporary-register fields.
- Thread-trace and interrupt metadata: `SQ_THREAD_TRACE_BASE*`, `SQ_THREAD_TRACE_SIZE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_MODE`, `SQ_THREAD_TRACE_MASK`, token/perf masks, write pointers, high-water marks, userdata words, and `SQ_THREAD_TRACE_WORD_*` packet decoders for timestamps, events, waves, instruction PC, issue, perf, reg, and userdata tokens. `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_CMN`, and `SQ_INTERRUPT_WORD_WAVE` define SQ interrupt packet fields.
- Performance and profiling registers: `SQ_PERFCOUNTER0..15_{LO,HI,SELECT}`, `SQ_PERFCOUNTER_CTRL*`, `SQ_LB_CTR_CTRL`, load-balancer data counters, `SX_PERFCOUNTER0..3_*`, `TA_PERFCOUNTER0..1_*`, `TD_PERFCOUNTER0_*`, `TCP_PERFCOUNTER0..3_*`, `TCA_PERFCOUNTER0..3_*`, `TCC_PERFCOUNTER0..3_*`, and `VGT_PERFCOUNTER0..3_*`.
- Texture/cache and memory-facing controls: `TA_CNTL`, `TA_CNTL_AUX`, `TA_BC_BASE_ADDR*`, `TA_CS_BC_BASE_ADDR*`, `TA_STATUS`, `TA_CGTT_CTRL`, `TD_CNTL`, `TD_CGTT_CTRL`, `TCP_CNTL`, `TCP_CHAN_STEER_*`, `TCP_CGTT_SCLK_CTRL`, `TCP_STATUS`, `TCP_WATCH*`, `TCC_CTRL`, `TCC_CGTT_SCLK_CTRL`, `TCC_EDC_COUNTER`, `TCA_CTRL`, `TCA_CGTT_SCLK_CTRL`, and `TCI_CNTL_*`.
- Shader export and crossbar debug: `SX_DEBUG_1`, `SX_DEBUG_BUSY*`, `SXIFCCG_DEBUG_REG0..3`, and `SX_PERFCOUNTER*`.
- Geometry, tessellation, and streamout state: a large `VGT_*` block covers event/init command words, DMA/index controls, draw index/instance counts, primitive type/id, group-vector formatting, GS/ES/VS ring sizing and offsets, geometry shader mode/output/instance controls, hull/tessellation controls, LS-HS configuration, streamout config and buffer sizes/offsets/strides, TF parameters, vertex reuse, shader-stage enables, system config, and VGT performance counters.
- Debug-heavy VGT status registers: `VGT_DEBUG_REG0..35`, `VGT_CNTL_STATUS`, `VGT_CACHE_INVALIDATION`, `VGT_FIFO_DEPTHS`, `VGT_HS_OFFCHIP_PARAM`, and related state expose many low-level busy, counter, FIFO, request, and arbitration fields.

## Control Flow

This header chunk has no control flow of its own. All behavior occurs at preprocessing and compile time:

1. A GFX6 source includes `gca/gfx_6_0_d.h` for register offsets and this `gca/gfx_6_0_sh_mask.h` file for field definitions.
2. Driver code, generated state tables, or command packet builders combine masks and shifts into register values.
3. Runtime code writes those values through MMIO helpers, indirect register access, or PM4 packets, or reads hardware values and decodes fields.
4. The GPU hardware interprets, latches, increments, or reports the corresponding state.

Local AMDGPU legacy SI power-management files (`si_dpm.c` and `si_smc.c`) include this generated header alongside GFX6, DCE6, GMC6, BIF3, and SMU6 register headers. The Radeon SI clear-state and blit tables show adjacent runtime usage of many same registers, including `VGT_GS_MODE`, `VGT_SHADER_STAGES_EN`, `VGT_STRMOUT_CONFIG`, streamout buffer state, primitive-id state, and tessellation/geometry controls. Those tables encode register values directly rather than using these macros at every call site, but the macros document the field layout those values must obey.

## State And Persistence Behavior

The macros are stateless constants. The state they describe lives in GPU registers, command-stream state, shader descriptors, or hardware-generated trace/status packets.

State categories represented by this chunk include:

- Persistent or context-saved graphics state: `VGT_*` geometry/tessellation/streamout controls, shader-stage enables, primitive ID reset/enables, index/instance ranges, GS ring sizes, and transform-feedback controls remain in the graphics context until cleared, reset, or overwritten by command streams.
- Per-dispatch or per-draw descriptor state: `SQ_BUF_RSRC_*`, `SQ_IMG_RSRC_*`, and `SQ_IMG_SAMP_*` fields define buffer, image, and sampler descriptors consumed by shaders. Incorrect mtype, format, swizzle, dimension, address, or tiling fields affect shader memory accesses.
- Volatile status and debug state: `SQ_DEBUG_STS_*`, `SQ_WAVE_*`, `TA_STATUS`, `TCP_STATUS`, `VGT_CNTL_STATUS`, `SX_DEBUG_BUSY*`, and numerous `VGT_DEBUG_REG*` fields report live hardware activity, queues, arbitration, wave allocation, or block busy conditions.
- Performance counter state: `SQ`, `SX`, `TA`, `TD`, `TCP`, `TCA`, `TCC`, and `VGT` perf-counter select/control/data pairs configure event sources and expose counter values that persist until reset, rollover, stop, or reprogramming.
- Thread-trace state: base, size, mode, masks, write pointer, high-water mark, status, token masks, and packet-word definitions describe a trace buffer workflow where programming selects what to capture and hardware emits tokenized records.
- Cache, clock-gating, and power-related state: `SQC_CACHES`, `SQC_CONFIG`, `SQ_TEX_CLK_CTRL`, `TA_CGTT_CTRL`, `TD_CGTT_CTRL`, `TCP_CGTT_SCLK_CTRL`, `TCA_CGTT_SCLK_CTRL`, and `TCC_CGTT_SCLK_CTRL` affect invalidation, cache behavior, or block clock-gating.
- Error-counting state: `SQ_SEC_CNT`, `SQ_DED_CNT`, `SQ_DED_INFO`, `SQC_SECDED_CNT`, and `TCC_EDC_COUNTER` expose single/double-error counts and diagnostic IDs. The header does not state whether individual fields are sticky, clear-on-read, clear-on-write, or reset-only.

Because generated masks do not encode sequencing rules, consumers must still follow the GFX6 register specification for reserved-bit preservation, read-modify-write safety, status-clear semantics, clock/power gating ordering, and shader-context save/restore.

## Dependencies

This chunk depends on the rest of the GFX6 generated register set:

- `gca/gfx_6_0_d.h` provides matching GFX6 offset symbols such as the `mm*` register names for these masks.
- Earlier and later ranges of `gfx_6_0_sh_mask.h` define other fields in the same generated mask namespace.
- AMDGPU/Radeon register helpers provide runtime use: `RREG32`, `WREG32`, `WREG32_P`, `REG_SET_FIELD`, `REG_GET_FIELD`, PM4 packet builders, and context-state table emitters.
- Legacy SI AMDGPU power management includes this header in `si_dpm.c` and `si_smc.c`, tying it to Southern Islands DPM/SMC setup with GFX6 register definitions available for clock, power, and block-control programming.
- Radeon SI-era command tables and clear-state headers depend on equivalent register layouts for initial graphics context values, blit shader setup, streamout disables, primitive/geometry defaults, and thread-trace clear state.
- Hardware documentation or generated register databases are the authoritative source. Cross-generation siblings may reuse macro names but not necessarily identical shifts or masks.

## Integration Points

Primary integration points are:

- Southern Islands graphics initialization and power management. The AMDGPU legacy SI DPM/SMC sources include this header with the GFX6 register offset header, making these fields available when configuring SI ASIC power, clocks, SMC memory access, and graphics-block state.
- Graphics command-stream setup. The `VGT_*` masks describe context registers used in clear-state tables and PM4 packets for primitive type, index ranges, instance counts, shader-stage enables, tessellation, geometry shader rings, streamout buffers, and transform feedback.
- Shader ABI and descriptor programming. `SQ_BUF_RSRC_*`, `SQ_IMG_RSRC_*`, and `SQ_IMG_SAMP_*` are the field-level contract for user/kernel code that constructs descriptors consumed by GFX6 shaders.
- Debug and hang diagnosis. `SQ_WAVE_*`, `SQ_IND_INDEX`, `SQ_IND_DATA`, `SQ_DEBUG_STS_*`, `TA_STATUS`, `TCP_STATUS`, `SX_DEBUG_BUSY*`, and `VGT_DEBUG_REG*` provide decoded views into wave state, block busy state, FIFOs, and internal counters.
- Thread tracing and profiling. `SQ_THREAD_TRACE_*` controls and token decoders, plus the per-block performance-counter selects, integrate with profiling paths that program capture buffers, enable trace modes, select event counters, and decode emitted records.
- Cache and memory-path control. `SQC_CACHES`, `SQC_CONFIG`, `TCP_CNTL`, `TCC_CTRL`, `TCI_CNTL_*`, `TA_CNTL`, and clock-gating controls sit on performance, invalidation, and memory-traffic paths.
- Error reporting and RAS-adjacent diagnostics. `SQ_*SEC*`, `SQ_*DED*`, `SQC_SECDED_CNT`, and `TCC_EDC_COUNTER` describe counters and IDs that can be read during reliability diagnostics, even though this GFX6-era header does not provide higher-level RAS policy.

## Risks

- Wrong masks or shifts silently program the wrong hardware bits. In this chunk, that can corrupt shader descriptors, instruction decoders, wave debug access, thread trace setup, cache invalidation, VGT draw state, streamout buffers, or performance counters.
- Similar register names recur across AMD GPU generations. Reusing GFX7/GFX8/GFX9 field assumptions for this GFX6 header can compile but produce invalid SI register values.
- Reserved and debug fields are exposed as plain macros. Callers must preserve reserved bits and avoid enabling low-level debug, force, stall, or clock-gating controls outside documented sequences.
- Full-word `0xffffffffL` masks do not imply arbitrary values are safe. Address, size, counter, index, and descriptor fields often still require alignment, range, tiling, VMID, or packet-format constraints.
- Thread-trace fields combine setup registers and hardware-emitted packet decoders. Confusing control fields with trace-record fields can break profiling or produce misleading decoders.
- Status and counter registers can have destructive read/clear semantics not represented in the header. Polling or clearing `SQ`, `TA`, `TCP`, `TCC`, `SX`, or `VGT` status incorrectly can mask real faults or perturb diagnostics.
- VGT streamout/geometry/tessellation state has broad draw-path impact. Misprogramming `VGT_GS_MODE`, `VGT_SHADER_STAGES_EN`, `VGT_LS_HS_CONFIG`, `VGT_TF_PARAM`, or streamout buffer fields can cause incorrect rendering, command processor hangs, or memory corruption.
- Manual edits are high risk because this is generated hardware metadata. Changes should come from regenerated AMD ASIC register sources and be validated against matching offset/default headers.

## Test Signals

Useful validation signals include:

- Build coverage for SI AMDGPU legacy DPM/SMC paths that include `gca/gfx_6_0_d.h` and `gca/gfx_6_0_sh_mask.h`.
- Static consistency checks that each register family in this chunk has matching offset symbols in `gfx_6_0_d.h` and that field masks within a register do not overlap unexpectedly except for documented aliases such as nested/mask fields.
- Southern Islands boot and display bring-up without invalid GFX register access, clock-gating warnings, SMC/DPM failures, or graphics ring timeouts.
- Radeon/AMDGPU clear-state and blit-path smoke tests that exercise `VGT_GS_MODE`, `VGT_SHADER_STAGES_EN`, streamout disables, primitive ID state, and draw-index/instance setup.
- Graphics workloads with tessellation, geometry shaders, streamout, instancing, primitive restart, and transform feedback to cover the dense `VGT_*` field set.
- Shader descriptor tests that stress buffer, image, sampler, typed buffer, and memory instruction paths using the `SQ_*RSRC*`, `SQ_MIMG`, `SQ_MTBUF`, and `SQ_MUBUF` fields.
- Profiling and debug tests that program SQ/SX/TA/TD/TCP/TCA/TCC/VGT performance counters and verify event selection, counter rollover, start/stop/reset, and high/low reads.
- Thread-trace capture tests that validate base/size/mode/mask setup, write-pointer progress, overflow/high-water status, and token decoding for event, wave, instruction, issue, perf, timestamp, userdata, and register packets.
- Hang/debug workflows that read `SQ_IND_*`, `SQ_WAVE_*`, `SQ_DEBUG_STS_*`, `TA_STATUS`, `TCP_STATUS`, `SX_DEBUG_BUSY*`, and `VGT_DEBUG_REG*` while preserving status semantics.
- Cache and memory stress tests that monitor invalidation behavior, TCC/TCP/TCI controls, EDC counters, and clock-gating transitions under rendering and compute-like shader memory traffic.
