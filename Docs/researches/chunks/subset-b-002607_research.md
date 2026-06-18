# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 37628-40016

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask header slice. It contains 2,168 `#define` constants for register bit positions and bit masks, plus register-name comments that group those constants. There are no functions, structs, enums, variables, locks, allocation paths, or executable statements in these lines.

The slice starts in the middle of the performance-counter selection area, at `PA_SU_PERFCOUNTER2_SELECT`, and ends in the middle of `CGTT_PH_CLK_CTRL3`. The next chunk must provide the remaining `CGTT_PH_CLK_CTRL3` masks and any following registers before a full per-file report can make complete claims about the tail of the clock-control block.

Major register groups covered here are:

- Performance counter selectors for PA/SU, PA/SC, SPI, PC, SQ, SQG, SX, TA, TD, TCP, GL1C, GL1XC, CB, DB, RMI, PA/PH, UTCL1, WGS, GL1A, and GL1XA blocks.
- SQ and SQG performance-counter control fields, including shader-stage enables, pipe disables, force enable, VMID filtering, poll-before-read, and sample-finish status fields.
- SQ thread trace buffer, control, mask, token-mask, write-pointer, halt, poweroff-restore, status, draw/marker/dropped counters, and finish-done debug fields.
- The beginning of the `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_pwrdec` address block, covering fine-grained clock-gating and clock-trunk controls for SPI, PC, BCI, VGT, GS/NGG, PA, SQ, SQG, SX, TA, TD, DB, CB, RMI, SE CAC, and PH.

## Purpose

The purpose of this chunk is to publish ASIC-specific bit layouts for GC 12.1.0 graphics registers. Companion offset headers define the register addresses; this `*_sh_mask.h` file defines how software packs field values into those 32-bit registers and how it extracts fields from readbacks.

The performance-counter selectors let the driver or profiling stack choose hardware events and counter modes. The common selector pattern is:

- `PERF_SEL`, often plus `PERF_SEL1`, `PERF_SEL2`, or `PERF_SEL3`, for one or more event selector slots.
- `CNTR_MODE`, `COUNTER_MODE`, `SPM_MODE`, or `PERF_MODE` fields for counter behavior and streaming-performance-monitoring mode.
- `*_SELECT1` companion registers that carry extra selector lanes or mode fields.

The SQ thread-trace fields configure shader execution tracing. They describe trace buffer size/base registers, double-buffering, high-water and low-water control, interrupt generation, stall behavior, SIMD/WGP/SA selection, token inclusion/exclusion, write-pointer format, halt/poweroff handshakes, trace status, and dropped/finish counters. These fields are critical for profiling, debug capture, and KFD thread-trace interrupt interpretation.

The final pwrdec section describes clock-gating override registers. Those constants name on/off delay and hysteresis fields, performance-monitor clock overrides, register-clock overrides, debug-bus enables, and many `SOFT_OVERRIDE*` and `SOFT_STALL_OVERRIDE*` bits that can force clocks or stalls in individual graphics sub-blocks.

## Important APIs, Types, And Macros

This chunk's interface is C preprocessor metadata. The important API shape is the pair of generated names:

- `<REGISTER>__<FIELD>__SHIFT` gives the right shift for a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit mask for that field.

Representative selector groups include:

- `PA_SU_PERFCOUNTER2_SELECT` and `PA_SU_PERFCOUNTER3_SELECT`, each with `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE` fields.
- `PA_SC_PERFCOUNTER0_SELECT` and `PA_SC_PERFCOUNTER0_SELECT1`, plus simpler `PA_SC_PERFCOUNTER1_SELECT` through `PA_SC_PERFCOUNTER7_SELECT` with only `PERF_SEL`.
- `SPI_PERFCOUNTER0_SELECT` through `SPI_PERFCOUNTER5_SELECT` and matching `*_SELECT1` registers.
- `PC_PERFCOUNTER0_SELECT` through `PC_PERFCOUNTER3_SELECT` and matching `*_SELECT1` registers.
- `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` and `SQG_PERFCOUNTER0_SELECT` through `SQG_PERFCOUNTER7_SELECT`; these use `PERF_SEL`, `SPM_MODE`, and `PERF_MODE` fields with 9-bit selector masks.
- `SX`, `TA`, `TD`, `TCP`, `GL1C`, `GL1XC`, `CB`, `DB`, `RMI`, `PA_PH`, `UTCL1`, `WGS`, `GL1A`, and `GL1XA` performance-counter selectors.

Important control and status groups include:

- `SQG_PERFCOUNTER_CTRL`: `PS_EN`, `GS_EN`, `HS_EN`, `CS_EN`, per-ME/pipe disable bits, and `POLL_BEFORE_PERF_READ`.
- `SQG_PERFCOUNTER_CTRL2` and `SQ_PERFCOUNTER_CTRL2`: `FORCE_EN` and `VMID_EN` masks.
- `SQ_PERFCOUNTER_CTRL`: stage enables and per-ME/pipe performance disables.
- `SQG_PERF_SAMPLE_FINISH`: `STATUS`.
- `CB_PERFCOUNTER_FILTER`: color-buffer perf filtering by operation, format, clear, MRT, sample count, and fragment count.
- `RMI_PERF_COUNTER_CNTL`: transaction/event/TC enable selectors, event-window masks, CID/VMID filters, burst-length threshold, soft reset, and SPM selection.

Important SQ thread-trace groups include:

- `SQ_THREAD_TRACE_BUF0_SIZE`, `SQ_THREAD_TRACE_BUF0_BASE_LO`, `SQ_THREAD_TRACE_BUF0_BASE_HI`, and the corresponding buffer 1 registers.
- `SQ_THREAD_TRACE_CTRL`: `MODE`, `GL1_PERF_EN`, `INTERRUPT_EN`, `DOUBLE_BUFFER`, `HIWATER`, `REG_AT_HWM`, `SPI_STALL_EN`, `SQ_STALL_EN`, `STALL_ALL_SIMDS`, `UTIL_TIMER`, `WAVESTART_MODE`, sync-count controls, `LOWATER_OFFSET`, `GL1X_PREFETCH_PAGE`, auto-flush fields, `NCP_REG_TOKEN_EN`, and `DRAW_EVENT_EN`.
- `SQ_THREAD_TRACE_MASK`: SIMD, WGP, SA, wave-type include, non-detail exclusion, and SIMD-power fields.
- `SQ_THREAD_TRACE_TOKEN_MASK`: token exclude, execution-token, BOP-event include, barrier/ALU-exec exclusions, register include/exclude/detail, and instruction exclude fields.
- `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_HALT`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_STATUS2`, draw/marker counters, dropped counter, and finish-done debug fields.

The pwrdec clock-control groups include:

- SPI-related `GFX_ICG_SPI_RA0_CLK_CTRL`, `GFX_ICG_SPI_RA1_CLK_CTRL`, `GFX_ICG_SPI_CS_CTRL`, `GFX_ICG_SPI_PS_CTRL`, `GFX_ICG_SPIS_CTRL`, `CGTX_SPI_DEBUG_CLK_CTRL`, and `GFX_ICG_SPI_CTRL`.
- Pipeline clock controls such as `GFX_ICG_PC_CLK_CTRL`, `GFX_ICG_BCI_CTRL`, `CGTT_VGT_CLK_CTRL`, `CGTT_GS_NGG_CLK_CTRL`, `CGTT_PA_CLK_CTRL`, `CGTT_SQ_CLK_CTRL`, `CGTT_SQG_CLK_CTRL`, `SQ_ALU_CLK_CTRL`, `SQ_TEX_CLK_CTRL`, `SQ_LDS_CLK_CTRL`, `SQ_CLK_CTRL`, `ICG_SQ_CLK_CTRL`, and `ICG_SP_CLK_CTRL`.
- Backend and cache-related controls such as `GFX_ICG_SX_CLK_CTRL0` through `GFX_ICG_SX_CLK_CTRL4`, `GFX_ICG_TA_CTRL`, `GFX_ICG_TD_CTRL`, `DB_CGTT_CLK_CTRL_0`, `GFX_ICG_CB_CTRL`, `GFX_ICG_RMI_CTRL`, `GFX_ICG_SE_CAC_CLK_CTRL`, and `CGTT_PH_CLK_CTRL0` through the first fields of `CGTT_PH_CLK_CTRL3`.

## Control Flow

There is no direct control flow in this header. Runtime control flow is provided by consumers that include this file and use the macros with AMDGPU register helpers. The typical flow is:

1. A GC 12.1.0 driver path chooses a register from `gc_12_1_0_offset.h`.
2. The driver constructs a 32-bit register value using field values shifted by `__SHIFT` and constrained by the matching `_MASK`, often through local helpers such as `REG_SET_FIELD()` or equivalent bit operations.
3. The driver writes the register through SOC15 MMIO helpers such as `WREG32_SOC15()` or reads through `RREG32_SOC15()`.
4. For status registers, the driver extracts fields from the read value with the generated mask/shift pair, often through `REG_GET_FIELD()`.

For performance counters, the runtime flow is selection/programming, workload execution, sample/finish polling, then counter readback. For SQ thread trace, the flow is buffer programming, mask/token/control setup, trace enable, status or interrupt observation, write-pointer and buffer readback, and optional halt/poweroff coordination. For clock-control fields, the flow is usually read-modify-write around feature toggles, power management transitions, debug modes, or performance-monitor clock override changes.

## State And Persistence Behavior

The macros themselves hold no state. They describe state fields in hardware registers.

Performance-counter selector state persists in the programmed GC hardware registers until reset, reprogramming, power-gating loss, or another driver/profiling client changes the selector registers. The selected events determine what the corresponding hardware counters accumulate or stream.

SQ thread-trace state is split between programmed configuration and live status. Buffer base and size fields point hardware at trace memory. Control, mask, and token-mask fields define what gets captured. Write pointer, busy/full/error/status, dropped counter, and finish-done fields are live hardware observations. These fields can change while shaders run, while trace buffers fill, when interrupts fire, or during halt/poweroff transitions.

Clock-control state is persistent hardware configuration while the graphics block remains powered and programmed. The `ON_DELAY`, `OFF_HYSTERESIS`, `REG_CLK_OVERRIDE`, `PERFMON_CLK_OVERRIDE`, `SOFT_OVERRIDE*`, and `SOFT_STALL_OVERRIDE*` fields alter how clocks gate or remain forced on. Wrong values can persist across workloads until reset or explicit restoration, affecting power, performance, trace collection, and debug visibility.

## Dependencies And Integration Points

This chunk depends on the generated AMD register database for GC 12.1.0. It must remain synchronized with:

- `gc_12_1_0_offset.h`, which supplies the register addresses for the fields named here.
- Other generated GC 12.1.0 headers, especially field names consumed by `REG_SET_FIELD()` and `REG_GET_FIELD()` call sites.
- AMDGPU SOC15 accessors such as `RREG32_SOC15()`, `WREG32_SOC15()`, and instance/XCC selection through helpers like `GET_INST(GC, xcc_id)`.
- GC 12.1.0 driver files that include this header: `gfx_v12_1.c`, `mes_v12_1.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `gfxhub_v12_1.c`, `sdma_v7_1.c`, `soc_v1_0.c`, `imu_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`.
- Profiling, perfmon, SPM, SQ thread-trace, GPU debug, KFD trace-interrupt handling, and clock/power-management paths that program or decode the named hardware registers.

The path lives under a `ceph-client` source tree mirror, but this file is AMD GPU driver hardware metadata and has no distributed-filesystem data path, no Ceph protocol behavior, and no storage persistence semantics.

## Risks And Edge Cases

- These macros are untyped constants. A wrong mask or shift can compile cleanly and silently program the wrong bits.
- Many register names repeat a similar pattern across blocks, but field widths differ. For example, SQ/SQG selectors use 9-bit `PERF_SEL` masks in this chunk, while many other blocks use 10-bit selector masks. Copying a selector pattern across blocks can corrupt neighboring mode fields.
- The chunk begins and ends mid-logical area. `PA_SU_PERFCOUNTER0/1` are in the previous chunk, and `CGTT_PH_CLK_CTRL3` is incomplete here. Whole-file analysis must merge adjacent chunks.
- Thread-trace fields are sensitive to buffer sizing, base-address programming, high-water/low-water thresholds, double-buffer selection, and token filters. A mask mismatch can cause lost packets, missing register/detail tokens, wrong buffer selection, or trace interrupts that never arrive.
- Performance-counter selector errors may produce plausible but wrong numbers. These failures are hard to catch with compile tests because the register writes remain syntactically valid.
- VMID and pipe-disable fields in `SQ_PERFCOUNTER_CTRL2`, `SQG_PERFCOUNTER_CTRL2`, and the per-ME/pipe controls can accidentally hide events from some workloads or queues.
- Clock-gating override fields can affect power and liveness. Leaving a soft override asserted may increase power or prevent clock gating; clearing a required debug/perfmon override may make counters or trace logic unreliable.
- Some `SOFT_OVERRIDE*` bits are sparse and hardware-specific. The absence of certain bit numbers is intentional generated metadata, not an invitation to fill gaps manually.
- Cross-generation AMD GC headers contain similarly named fields with different masks. Reusing GC 12.1.0 masks for GC 12.0, GC 11, or GC 9 hardware can break profiling or power-management behavior.

## Test Signals

Useful validation signals include:

- Build AMDGPU and AMDKFD with GC 12.1.0 support enabled. Missing macro names or renamed fields should surface in include users that rely on this register namespace.
- Run static or generated-header consistency checks that compare `gc_12_1_0_sh_mask.h` against AMD's authoritative GC 12.1.0 register database and the paired `gc_12_1_0_offset.h`.
- Exercise GPU performance-counter programming on GC 12.1.0 hardware across PA, SPI, SQ/SQG, TCP, GL1, CB, DB, RMI, and UTCL1 blocks. Look for implausible zero counters, saturated counters, or events attributed to the wrong block.
- Run SQ thread-trace capture with single and double buffering, VMID/WGP/SIMD masks, token filters, finish handling, and buffer-full interrupts. Validate `SQ_THREAD_TRACE_STATUS`, `STATUS2`, `WPTR`, dropped counter, and finish-done fields against expected trace buffer contents.
- Test KFD thread-trace interrupt paths on GC 12.1.0 workloads and confirm buffer-full and UTC/error reporting match hardware status.
- Toggle graphics clock-gating and perfmon-clock override paths, then check power-management telemetry, performance-counter reliability, and absence of hangs during suspend/resume, reset, and GPU fault recovery.
- Compare against nearby generated GC headers only with generation-aware expectations. Similar names should not be treated as proof that bit positions are interchangeable.

## Cross-Chunk Notes

The previous chunk is needed for the beginning of the PA/SU performance-counter selection block and other preceding GC shift/mask definitions. The next chunk is needed for the rest of `CGTT_PH_CLK_CTRL3` and any following pwrdec or closing definitions. The final per-file research document should combine this chunk with adjacent chunks before summarizing complete performance-counter, thread-trace, and clock-control coverage for `gc_12_1_0_sh_mask.h`.
