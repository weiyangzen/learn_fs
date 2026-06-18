# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_0_0_sh_mask.h lines 35082-37536

## Scope

This chunk covers a generated GC 12.0.0 shader/register mask header range. It starts in the middle of the `TCP_PERFCOUNTER0_LO` field definitions and ends in the `ICG_SQ_CLK_CTRL` clock override register, after the `TAG_CLK_OVERRIDE` mask and before the final fields of that register in the following chunk.

The covered range contains only C preprocessor constants. It does not define functions, structs, storage, runtime branches, or executable control flow. The constants are bitfield ABI definitions for AMDGPU GC 12 hardware registers:

- Low/high 32-bit performance counter value registers for TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A, and GL1XA blocks.
- Performance counter filter registers for TCP and CB.
- Shader-engine performance counter selection and control for GE2_SE, GRBMH, PA_SU, PA_SC, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A, and GL1XA.
- SQ and SQG performance counter enable/control registers and sample-finish status.
- SQ thread-trace buffer, control, masking, write pointer, halt, poweroff-restore, status, draw/marker, dropped counter, and finish-done debug registers.
- GFX shader-engine power/clock gating controls for SPI, PC, BCI, VGT, GS/NGG, PA, SQ, SQG, ALU, TEX, LDS, and fine-grained SQ clock domains.

## Purpose

The purpose of this header section is to encode field locations for GC 12.0.0 MMIO registers. Each field is represented as a conventional pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field in a 32-bit register value.

The matching `gc_12_0_0_offset.h` file supplies register addresses such as `regSQ_THREAD_TRACE_CTRL`, `regSQ_PERFCOUNTER0_SELECT`, or `regCGTT_SQ_CLK_CTRL`; this file supplies the bit layout for those registers. AMDGPU and KFD code then use the generated names through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15_PREREG`, and `SOC15_REG_OFFSET`.

## Important Macro Families

### Performance Counter Values and Filters

The first part of the chunk provides low/high value masks for multiple block-local counters. Registers such as `TCP_PERFCOUNTER*_LO/HI`, `GL1C_PERFCOUNTER*_LO/HI`, `GL1XC_PERFCOUNTER*_LO/HI`, `CB_PERFCOUNTER*_LO/HI`, `DB_PERFCOUNTER*_LO/HI`, `RMI_PERFCOUNTER*_LO/HI`, `PA_PH_PERFCOUNTER*_LO/HI`, `UTCL1_PERFCOUNTER*_LO/HI`, `GL1A_PERFCOUNTER*_LO/HI`, and `GL1XA_PERFCOUNTER*_LO/HI` expose full-width `PERFCOUNTER_LO` or `PERFCOUNTER_HI` fields with `0xFFFFFFFFL` masks. Consumers combine the low and high halves to read wider hardware performance counter state.

`TCP_PERFCOUNTER_FILTER` and `TCP_PERFCOUNTER_FILTER2` define filters for texture/cache requests: buffer, flat, dimensionality, data format, compression enable, numeric format, software mode, sample count, opcode type, temporal hint, scope, and request mode. `TCP_PERFCOUNTER_FILTER_EN` provides the corresponding per-filter enable bits. This split matters because filter values can be programmed without taking effect unless their enable bits are set.

`CB_PERFCOUNTER_FILTER` is render-backend specific. It filters color-buffer performance counting by operation, format, clear state, MRT, sample count, and fragment count. The enable and selector fields sit next to each other, so mask drift can silently change which render traffic contributes to a counter.

### Shader-Engine Performance Counter Selection

After the `gc_gfx_se_gfx_se_perfsdec` address block marker, the chunk describes event selection for shader-engine-local performance counters.

Most graphics pipeline blocks use a repeated layout:

- `*_PERFCOUNTER0_SELECT` can pack `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`.
- `*_PERFCOUNTER0_SELECT1` can add `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`.
- Later counters sometimes use a narrower single-event layout with only `PERF_SEL` and `PERF_MODE`.

The covered blocks include GE2_SE, SPI, PC, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA_PH, GL1A, and GL1XA. Most selectors use 10-bit event fields (`0x000003FFL`), while SQ and SQG use 9-bit `PERF_SEL` fields plus `SPM_MODE` and `PERF_MODE`. UTCL1 uses `PERF_SEL` plus `COUNTER_MODE` fields rather than the common graphics-pipe `CNTR_MODE` naming.

The RMI block also includes `RMI_PERF_COUNTER_CNTL`, which controls transaction/event/TC performance enable selection, event windows, CID, VMID, burst-length threshold, soft reset, and SPM counter selection. That register is more stateful than a simple event selector because it gates how RMI events are attributed and sampled.

`GRBMH_CP_PERFMON_CNTL` and `CP_PERFMON_CNTL_1` connect the shader-engine performance monitor domain to command processor/performance monitor state, with fields for sample enable, perfmon state, SPM perfmon state, and enable mode.

### SQ and SQG Performance Controls

`SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` and `SQG_PERFCOUNTER0_SELECT` through `SQG_PERFCOUNTER7_SELECT` use a compact GC 12 layout: `PERF_SEL`, `SPM_MODE`, and `PERF_MODE`. These fields are central to shader performance profiling because they select events from the shader core and SQG front-end domains and decide how they participate in streaming performance monitoring.

`SQ_PERFCOUNTER_CTRL` and `SQG_PERFCOUNTER_CTRL` include shader-stage enables (`PS_EN`, `CS_EN`, `GS_EN`, `HS_EN`) and per-ME/pipe disable bits. `SQ_PERFCOUNTER_CTRL2` and `SQG_PERFCOUNTER_CTRL2` add `VMID_EN` and `FORCE_EN`. `SQG_PERF_SAMPLE_FINISH` has a `STATUS` bit for sample completion/handshake visibility.

### SQ Thread Trace

The thread-trace section defines the per-SQ trace buffer programming surface:

- `SQ_THREAD_TRACE_BUF0_SIZE`, `BUF0_BASE_LO/HI`, `BUF1_SIZE`, and `BUF1_BASE_LO/HI` describe two trace buffers.
- `SQ_THREAD_TRACE_CTRL` controls mode, high-water/low-water behavior, draw-event capture, register-at-high-water behavior, shader/SPI stalls, interrupt enable, draw/marker synchronization, token behavior, GL1 performance enable, double buffering, prefetch page, util timer, and auto-flush policy.
- `SQ_THREAD_TRACE_MASK` chooses WGP, SIMD, shader-array, wave-type inclusion, and non-detail exclusions.
- `SQ_THREAD_TRACE_TOKEN_MASK` gates token categories such as register detail, instruction tokens, barriers, BOP events, and execution tracing.
- `SQ_THREAD_TRACE_WPTR` exposes buffer ID and write offset.
- `SQ_THREAD_TRACE_HALT` controls entry into poweroff/CGCG and reports readiness.
- `SQ_THREAD_TRACE_STATUS` and `STATUS2` expose busy, finish pending/done, owner VMID, write error, buffer fullness, issue state, lost-packet state, and full-write-buffer state.
- Draw, marker, HP3D draw/marker, dropped counter, and finish-done debug registers expose trace-progress and diagnostic counters.

These registers are integration points for profiling and developer/debug tooling. They are also sensitive to power-state transitions because trace halt and poweroff-restore fields coordinate with clock/power gating.

### GFX Shader-Engine Clock and Power Controls

The final portion, after the `gc_gfx_se_gfx_se_pwrdec` marker, covers clock-gating controls:

- `GFX_ICG_SPI_RA0_CLK_CTRL`, `GFX_ICG_SPI_RA1_CLK_CTRL`, `GFX_ICG_SPI_CS_CTRL`, `GFX_ICG_SPI_PS_CTRL`, `GFX_ICG_SPIS_CTRL`, `CGTX_SPI_DEBUG_CLK_CTRL`, and `GFX_ICG_SPI_CTRL` define SPI-side group overrides, register overrides, off hysteresis, and debug clock controls.
- `GFX_ICG_PC_CLK_CTRL` controls primitive/PC/GL1/LDS/miss-walker/perfmon medium-grain clock-gating overrides, plus on-delay and off-hysteresis.
- `GFX_ICG_BCI_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_GS_NGG_CLK_CTRL`, and `CGTT_PA_CLK_CTRL` expose on-delay, off-hysteresis, performance/debug enables, soft-stall overrides, and block-specific override bits for VGT, tessellation, GS/NGG, PA, SU, CL/VTE, SX interface, and related domains.
- `CGTT_SQ_CLK_CTRL` and `CGTT_SQG_CLK_CTRL` define SQ/SQG on-delay, off-hysteresis, soft-stall overrides, perfmon/thread-trace overrides, core overrides, register overrides, and SQG force-FGCG fields.
- `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, and `SQ_LDS_CLK_CTRL` pack per-shader-array `FORCE_WGP_ON` bitmaps for ALU, texture, and LDS domains.
- `SQ_CLK_CTRL` and `ICG_SQ_CLK_CTRL` provide fine-grained SQ clock override bits for SPI/SX messaging, SQC thread trace, wave clocks, LDS, VMEM, SMEM, scalar/SALU/VALU paths, instruction-buffer paths, export, tag, and status domains. This chunk ends before the final `ICG_SQ_CLK_CTRL` masks complete.

## Control Flow and State Behavior

There is no software control flow in this header. The runtime behavior emerges when AMDGPU/KFD code composes MMIO writes or decodes MMIO reads with these masks.

The persistent state represented by this chunk lives in hardware registers:

- Performance counter values and event selectors persist until the profiling setup changes or the hardware block is reset.
- Filter registers constrain which requests or render-backend operations are counted.
- SQ/SQG performance-control and sample-finish bits coordinate sampling state for shader profiling.
- Thread-trace base/size/mask/control registers define trace capture buffers and capture policy, while status and counters report trace progress, errors, dropped data, and ownership.
- Clock-gating control registers alter hardware power/performance behavior by overriding automatic clock gating, forcing WGP domains on, or changing delay/hysteresis thresholds.

Some fields are configuration fields, some are status fields, and some are command-like or handshake fields. For example, trace halt/poweroff fields and sample-finish status require sequencing with hardware state; clock override bits should usually be changed only through the owning power-management or debug path.

## Dependencies and Integration Points

This chunk depends on the generated AMD register header set:

- `gc_12_0_0_offset.h` supplies register offsets for the field names defined here.
- `gc_12_0_0_default.h`, where present for adjacent register families, supplies reset/default values.
- `soc15.h` and AMDGPU register helper macros provide the read/write and field-composition API.

Observed include points in this source tree include:

- `amdgpu/gfx_v12_0.c`, the main GC 12 graphics IP implementation, which includes `gc_12_0_0_offset.h` and this mask header for register setup, RLC/CP bring-up, clock gating, resets, and debug state.
- `amdkfd/kfd_device_queue_manager_v12.c` and `amdkfd/kfd_mqd_manager_v12.c`, which include this header for GC 12 queue/MQD programming.
- `amdgpu/mes_v12_0.c`, `sdma_v7_0.c`, `gfxhub_v12_0.c`, `imu_v12_0.c`, `soc24.c`, and `amdgpu_amdkfd_gfx_v12.c`, which compile against the same GC 12 register definitions.

The specific macros in this chunk are most likely consumed by performance/debug and power-management paths rather than ordinary queue setup. Their natural consumers are GPU performance counter tooling, RLC/SPM setup, shader thread-trace capture, GFX clock-gating control, and diagnostics that read block-local performance counter values.

## Risks

- Bitfield drift is high impact. A wrong shift or mask can program a different hardware field, producing invalid performance data, broken trace capture, clock-gating instability, or GPU hangs.
- Repeated performance counter families are easy to edit incorrectly. Many blocks share similar names and masks, but SQ/SQG, UTCL1, CB, RMI, and some later counters use different layouts.
- Low/high counter reads require correct sequencing in consumers. The header exposes 32-bit halves only; it does not enforce stable 64-bit read ordering or rollover handling.
- Filter value and filter enable fields are separate. Programming `TCP_PERFCOUNTER_FILTER` without `TCP_PERFCOUNTER_FILTER_EN`, or mismatching CB filter enables/selectors, can make profiling silently count the wrong traffic.
- Thread trace can interact with VMID ownership, buffer fullness, dropped packets, interrupts, stalls, CGCG/poweroff, and restore state. Incorrect control sequencing can lose trace packets or stall shader work.
- Clock-gating override fields affect power and timing behavior. Leaving overrides set, forcing WGP domains on, or changing hysteresis/delay fields outside the intended path can regress power, thermal behavior, or performance.
- Cross-generation similarity is not a substitute for compatibility. GC 11 and GC 12 have nearby names but different SQ/SQG selector widths, thread-trace fields, and clock override layouts.
- The chunk starts and ends mid-register-family. The merge lane must stitch it to adjacent chunks for the beginning of `TCP_PERFCOUNTER0_LO` and the remaining `ICG_SQ_CLK_CTRL` fields.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and profiling/debug coverage:

- Build AMDGPU, KFD, MES, SDMA, GFXHUB, IMU, and display configurations that include `gc/gc_12_0_0_sh_mask.h`; this catches missing or renamed macros.
- Run GC 12 graphics bring-up, reset, suspend/resume, and clock-gating tests to catch bad power-control masks and unexpected clock override persistence.
- Validate performance counters across TCP, GL1C/GL1XC, CB, DB, RMI, PA_PH, UTCL1, GL1A/GL1XA, GE2, GRBMH, SPI, PC, SQ/SQG, SX, TA, and TD, including multi-event selectors where available.
- Exercise TCP and CB filtering with known workloads so request-shape, data-format, sample-count, MRT, clear, and fragment filters change counter results as expected.
- Run SQ/SQG SPM sampling and sample-finish tests to verify `SPM_MODE`, `PERF_MODE`, stage enables, VMID filtering, force enable, and disabled ME/pipe fields.
- Capture SQ thread traces through both buffers, verify write pointer/status/owner VMID/error fields, and test high-water/low-water, interrupt, draw/marker sync, dropped-packet, halt, and poweroff-restore behavior.
- Use power-management telemetry to confirm clock-gating override changes do not leave ALU/TEX/LDS WGP domains forced on unexpectedly.

## Unresolved Cross-Chunk References

This chunk begins after `TCP_PERFCOUNTER0_LO` has already started, so the preceding comment and any earlier field context are in the previous chunk. It ends before the last fields of `ICG_SQ_CLK_CTRL`, so the final merged document should combine this analysis with the next chunk to cover that register completely.
