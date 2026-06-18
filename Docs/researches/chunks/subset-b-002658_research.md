# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 22304-24747

## Scope

This chunk covers generated shift and mask macros from the AMD GC 9.2.1 register mask header. It starts in the `gc_perfsdec` address block at command-processor performance counter selectors and continues through graphics block performance selectors, RLC streaming performance monitor fields, ATC/VM L2 performance counter control, and the first large part of the `gc_rlcpdec` RLC control/status block. The slice ends at `RLC_PG_DELAY_3`, immediately before subsequent RLC SRM/GPM fields in the next chunk.

The file is a pure C preprocessor hardware register description. It defines no functions, structs, globals, persistence containers, or executable control flow. Each register field is represented by the generated pair `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

## Purpose

These macros are the bitfield ABI between AMDGPU driver code and GC 9.2.1 hardware registers. The paired `gc_9_2_1_offset.h` header provides register addresses such as `mmRLC_CNTL`, `mmRLC_SAFE_MODE`, and other GC register offsets; this file provides field offsets and masks used by helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15`.

For this specific range, the primary purpose is to support:

- Selection and mode programming for graphics pipeline performance counters.
- Command processor and RLC performance-monitor state control.
- RLC SPM ring-buffer configuration and sample mux programming.
- UTCL2/VM L2 performance counter configuration/result behavior.
- RLC firmware enable, safe-mode entry, status polling, timers, clock counts, clock gating, power gating, CU load balancing, SERDES access, scratch/general registers, and SMU-facing control messages.

## Important Macro Families

### Graphics and Command Processor Performance Counters

The chunk begins with `CPF_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, `CPG_PERFCOUNTER*`, and `CP_PERFMON_CNTL`. These fields choose counter events (`CNTR_SEL*`), SPM mode, counter mode, global perfmon state, and sample enable state. Window and latency selectors such as `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, and `CPF/CPG/CPC_LATENCY_STATS_SELECT` add index, clear, always, and enable fields for more constrained measurement windows.

Most graphics front-end and shader/backend blocks then expose regular selector groups:

- `GRBM_PERFCOUNTER0/1_SELECT` and `GRBM_SE0..SE3_PERFCOUNTER_SELECT` include event selector fields plus many per-block busy/clean user-defined mask bits for DB, CB, VGT, TA, SX, SPI, SC, PA, GRBM, CP, IA, GDS, BCI, RLC, TC, WD, UTCL2, EA, and RMI.
- `WD`, `IA`, `VGT`, `PA_SU`, `PA_SC`, `SPI`, `SQ`, `SX`, `GDS`, `TA`, `TD`, `TCP`, `TCC`, `TCA`, `CB`, `DB`, and `RMI` counter selectors provide `PERF_SEL` or `CNTR_SEL` fields plus mode fields. The repeated `*_SELECT1` registers extend packed selector slots for additional events.
- `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` are especially dense: each has SIMD-mask, SQC bank mask, CNTR mode, and performance mode fields. `SQ_PERFCOUNTER_CTRL`, `SQ_PERFCOUNTER_MASK`, and `SQ_PERFCOUNTER_CTRL2` add wave/bank masking and counter arbitration/control.
- `CB_PERFCOUNTER_FILTER` is filter-oriented rather than only selector-oriented. It carries fields for operation, format, clear, MRT, sample-count, and fragment-count filtering.
- `RMI_PERF_COUNTER_CNTL` adds transaction/event/TC enable selection, window masks, CID/VMID filters, burst length threshold, soft reset, and SPM selection.

These macros are consumed by profiling, debug, and performance-monitor setup code. Event IDs and sequencing are hardware-defined; the header only describes how to place those values into 32-bit registers.

### Draw Object and Draw Window Control

`CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` describe command-processor draw filtering/window registers. They expose object IDs, object counts, high/low window bounds, and disables for individual low/high window comparisons. These fields are relevant to draw-window scoped perf/debug collection.

### RLC Streaming Performance Monitor

`RLC_SPM_PERFMON_CNTL` controls SPM ring mode and sample interval. `RLC_SPM_PERFMON_RING_BASE_LO/HI`, `RLC_SPM_PERFMON_RING_SIZE`, `RLC_SPM_RING_RDPTR`, `RLC_SPM_PERFMON_SEGMENT_SIZE`, and `RLC_SPM_SEGMENT_THRESHOLD` describe the memory ring and segment layout used for streamed samples.

`RLC_SPM_SE_MUXSEL_ADDR/DATA` and `RLC_SPM_GLOBAL_MUXSEL_ADDR/DATA` provide indirect mux-selection programming windows for shader-engine and global sample sources. Per-block sample delay registers cover CPG, CPC, CPF, CB, DB, PA, GDS, IA, SC, TCC, TCA, TCP, TA, TD, VGT, SPI, SQG, SX, and RMI; each uses an 8-bit delay plus reserved upper bits. `RLC_SPM_PERFMON_SAMPLE_DELAY_MAX` defines the maximum delay field.

`RLC_SPM_MC_CNTL`, `RLC_SPM_INT_CNTL`, and `RLC_SPM_INT_STATUS` later in the chunk connect SPM traffic with memory-client behavior, VMID, policy, memory type override, and interrupt enable/status.

### RLC Local Perfmon and IOV Perf Counters

`RLC_PERFMON_CLK_CNTL_UCODE`, `RLC_PERFMON_CLK_CNTL`, and `RLC_PERFMON_CNTL` expose RLC perfmon clock state, local perfmon state, and sample enable bits. `RLC_PERFCOUNTER0_SELECT` and `RLC_PERFCOUNTER1_SELECT` select RLC-local events.

`RLC_GPU_IOV_PERF_CNT_CNTL`, `RLC_GPU_IOV_PERF_CNT_WR_ADDR/DATA`, and `RLC_GPU_IOV_PERF_CNT_RD_ADDR/DATA` define a small virtual-function performance counter access path. They include enable, mode select, reset, VFID, counter ID, and 4-bit data fields. These are virtualization-sensitive and should be treated as privileged/SR-IOV plumbing rather than normal queue configuration.

### ATC and VM L2 Performance Counters

The chunk transitions into `gc_utcl2_atcl2pfcntldec` for `ATC_L2_PERFCOUNTER0_CFG`, `ATC_L2_PERFCOUNTER1_CFG`, and `ATC_L2_PERFCOUNTER_RSLT_CNTL`. These fields configure ATC L2 event selection, counter mode, compare enable/mask, and result control.

The `gc_utcl2_vml2pldec` block provides `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG` plus `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`. The VM L2 configuration registers share event, counter mode, compare, and compare-mask fields, while result control selects counter ID and behavior for reading/clearing or result handling.

### RLC Core Control, Safe Mode, Timers, and Status

The `gc_rlcpdec` block starts with RLC firmware/core controls:

- `RLC_CNTL` defines RLC enable, force retry, read-cache disable, and step mode.
- `RLC_STAT` exposes aggregate busy state for RLC, SRM, GPM, SPM, MC, and RLC threads 0-2.
- `RLC_SAFE_MODE`, `RLC_RLCV_SAFE_MODE`, and `RLC_SMU_SAFE_MODE` share command, message, response, and reserved fields. GFX code writes `CMD` and a message value to enter or leave safe mode, then polls `CMD` to clear.
- `SMU_RLC_RESPONSE`, `RLC_SMU_MESSAGE`, `RLC_SMU_GRBM_REG_SAVE_CTRL`, and `RLC_RLCV_COMMAND` are command/response channels between RLC, SMU, and virtualization firmware paths.

Timer and interrupt fields include `RLC_GPM_TIMER_INT_0..3`, `RLC_GPM_TIMER_CTRL`, `RLC_GPM_TIMER_STAT`, `RLC_INT_STAT`, and `RLC_GPM_CP_DMA_COMPLETE_T0/T1`. They describe timer values, enable/synchronized status bits, last CP/RLC interrupt ID, pending interrupt state, and CP DMA completion flags for GPM threads.

Clock/time fields include `RLC_REFCLOCK_TIMESTAMP_LSB/MSB`, `RLC_GPU_CLOCK_COUNT_LSB/MSB`, `RLC_CAPTURE_GPU_CLOCK_COUNT`, `RLC_CLK_COUNT_GFXCLK_LSB/MSB`, `RLC_CLK_COUNT_REFCLK_LSB/MSB`, `RLC_CLK_COUNT_CTRL`, `RLC_CLK_COUNT_STAT`, `RLC_GPU_CLOCK_32_RES_SEL`, and `RLC_GPU_CLOCK_32`. These back clock-count capture, enable, accumulation, and status reporting.

### RLC Clock Gating, Power Gating, and CU Load Balancing

Power-management fields are a major part of the RLC region:

- `RLC_MEM_SLP_CNTL` controls RLC memory light/deep sleep enables, busy override, and on/off delays.
- `RLC_MGCG_CTRL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL` describe medium-grain clock gating, CGCG/CGLS override/enables, idle thresholds, compensation delay, sleep mode, and ramp timing.
- `RLC_PG_CNTL` includes GFX power-gating enable/source, dynamic and static per-CU power gating, pipeline power gating, CP PG disable, SMU slowdown/handshake controls, voltage-reduction handshake control, and reserved fields.
- `RLC_PG_DELAY`, `RLC_PG_DELAY_2`, and `RLC_PG_DELAY_3` define power-up/down, command propagation, memory sleep, SERDES, CGCG/CGPG, and other hysteresis delay fields.
- `RLC_DYN_PG_STATUS`, `RLC_DYN_PG_REQUEST`, `RLC_STATIC_PG_STATUS`, `RLC_CU_STATUS`, `RLC_LB_INIT_CU_MASK`, `RLC_LB_ALWAYS_ACTIVE_CU_MASK`, `RLC_PG_ALWAYS_ON_CU_MASK`, `RLC_MAX_PG_CU`, `RLC_LB_PARAMS`, `RLC_LB_CNTL`, `RLC_LB_CNTR_*`, `RLC_LOAD_BALANCE_CNTR`, and `RLC_THREAD1_DELAY` describe per-CU power state, pending work, load-balancing masks/counters, sampling, and idle-delay tuning.
- `RLC_AUTO_PG_CTRL` coordinates automatic power gating, GRBM register save on idle, auto wakeup, and thresholds.

Cross-generation AMDGPU GFX code uses these exact macro families to enable/disable RLC, enter safe mode before changing clock/power state, program CGCG/CGLS thresholds, and toggle GFX power-gating bits. For GC 9.2.1, the mask definitions are included directly by `amdgpu/gfxhub_v1_1.c` and by Vega12 power-management include plumbing via `pm/powerplay/hwmgr/vega12_inc.h`.

### RLC GPM, SERDES, Scratch, and General Registers

`RLC_GPM_THREAD_RESET`, `RLC_GPM_THREAD_PRIORITY`, `RLC_GPM_THREAD_ENABLE`, and the large `RLC_GPM_STAT` register expose GPM thread reset, priority, enable, busy/wait state, sleep, DMA, interrupt, queue, and scheduling status. `RLC_UCODE_CNTL`, `RLC_FIREWALL_VIOLATION`, `RLC_JUMP_TABLE_RESTORE`, and `RLC_GPM_LOG_SIZE` are firmware/control diagnostics.

SERDES access is represented by `RLC_SERDES_RD_PENDING`, `RLC_SERDES_RD_MASTER_INDEX`, `RLC_SERDES_RD_DATA_0..2`, `RLC_SERDES_WR_CU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK`, `RLC_SERDES_WR_NONCU_MASTER_MASK_1`, `RLC_SERDES_WR_CTRL`, `RLC_SERDES_WR_DATA`, `RLC_SERDES_CU_MASTER_BUSY`, `RLC_SERDES_NONCU_MASTER_BUSY`, and `RLC_SERDES_NONCU_MASTER_BUSY_1`. These encode CU/non-CU master selection, read data windows, write/read command bits, power-up/down command bits, BPM address/data, SRBM override, and busy masks.

`RLC_GPM_GENERAL_0..7`, `RLC_GPM_SCRATCH_ADDR`, and `RLC_GPM_SCRATCH_DATA` provide generic firmware-visible scratch or mailbox-style storage windows. Their state is hardware/firmware state, not software persistence in this header.

## Control Flow and State Behavior

There is no C control flow in this chunk. Runtime behavior is created by driver code that includes this header and writes or reads MMIO registers using the generated constants.

The state described here is persistent hardware state until reset, firmware reinitialization, suspend/resume restore, or another MMIO write changes it. Examples include performance counter event selection, SPM ring base/size and read pointer, VM L2 perf counter configuration, RLC enable state, safe-mode command/response state, timer enables, CG/PG configuration, CU masks, load-balancing counters, SERDES command/busy state, scratch contents, and interrupt/status bits.

Some fields are ordinary configuration bits, while others are command strobes, sticky status, read-only status, or indirect-address/data windows. Examples requiring sequencing include safe-mode `CMD` polling, SPM mux address/data programming, VM/ATC performance counter result control, RLC clock-count capture, GPM thread reset, timer status/enable synchronization, SMU/RLC message exchange, and SERDES read/write command with busy/read-pending checks.

## Dependencies and Integration Points

This chunk depends on the generated GC 9.2.1 register set:

- `gc_9_2_1_offset.h` supplies the matching register offsets.
- Other generated GC headers provide defaults or adjacent bitfields outside this line range.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` naming convention.

Observed integration points in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/gfxhub_v1_1.c`, which includes `gc/gc_9_2_1_offset.h` and `gc/gc_9_2_1_sh_mask.h` for GC 9.2.1 register field access.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`, included by Vega12 power, thermal, BACO, and SMU manager code, which brings in the GC 9.2.1 offsets and masks.
- GFX generation code such as `gfx_v9_0.c`, which uses the same RLC macro families to test `RLC_CNTL__RLC_ENABLE_F32_MASK`, issue `RLC_SAFE_MODE` commands, program `RLC_CGCG_CGLS_CTRL`, and coordinate clock/power gating. That code demonstrates the expected sequencing pattern even when the exact include selected for a build depends on ASIC/IP version.
- Profiling/debug paths that configure graphics block performance counters, CP/RLC perfmon state, and SPM streaming buffers.

## Risks

- Bit layout drift between GC revisions is a real risk. The macro names are similar across GC 9, 10, 11, and 12, but field widths and semantics can differ. Code must include the GC 9.2.1 header only for matching hardware.
- Reserved fields are explicitly mapped but should not be programmed with arbitrary nonzero values unless the hardware specification or existing driver sequence requires it.
- RLC safe-mode, SMU message, SERDES, SPM mux, and VM/ATC result-control fields are sequencing-sensitive. Incorrect ordering can leave firmware busy, return stale samples, or hang waiting for a status bit.
- Power-gating and clock-gating fields affect live graphics hardware. Incorrect thresholds, masks, or enable bits can cause hangs, missed wakeups, unstable performance, or broken suspend/resume.
- Performance counter fields often pack multiple event selectors and modes into one register. Using the wrong mask/shift can silently count the wrong event rather than failing visibly.
- SR-IOV/IOV perf counter fields include VFID addressing. Incorrect use can leak, corrupt, or misattribute virtual-function performance state.

## Test Signals

- Build coverage: compile configurations that include `gfxhub_v1_1.c` and Vega12 power-management paths should catch missing or renamed macros.
- Register helper correctness: code using `REG_SET_FIELD`/`REG_GET_FIELD` with these macros should preserve unrelated bits and extract expected values in unit-style register composition tests where available.
- Runtime RLC health: GFX initialization should enable RLC, enter and leave safe mode without timeout, and report sane `RLC_STAT`/`RLC_GPM_STAT` values.
- Clock/power tests: suspend/resume, runtime power management, BACO, and clock-gating/power-gating toggles should not produce GPU resets or timeout waiting for RLC/SMU responses.
- Perf tests: block perf counters, RLC perfmon, SPM ring collection, ATC L2, and VM L2 counters should produce nonzero and stable counts for known workloads and should reset/clear according to result-control programming.
- Virtualization tests: SR-IOV or VF-aware paths should verify VFID counter read/write isolation and correct behavior of RLC GPU IOV perf counter controls.
- Diagnostics: dmesg should remain free of RLC safe-mode timeout, CP/RLC interrupt storm, GPU reset, and SMU response timeout messages when exercising the fields in this chunk.
