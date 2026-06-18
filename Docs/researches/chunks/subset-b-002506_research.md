# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 5128-7584

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C logic; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, display, and SDMA code to compose or decode 32-bit MMIO register values for this graphics IP generation. The companion register addresses and base indices live in `gc_11_0_0_offset.h`, while reset/default values are in `gc_11_0_0_default.h`.

The selected range starts in the `gc_sdma0_sdma1hypdec` block after `SDMA1_UCODE_ADDR`, covers SDMA performance counter selectors and data windows, GRBM global status/control/debug registers, command processor status and queue/ring debug registers, primitive assembler/geometry frontend controls, shader queue controls, shader/SX/SPI debug and lifetime registers, and ends in the middle of the texture pipe `TA_CNTL_AUX` mask definitions. Although this repository subtree is named `ceph-client`, this file is AMD GPU driver hardware metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, callbacks, locks, or allocations in this range. The exported interface is a generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field low bit.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- Consumers combine these with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_11_0_0_offset.h`, usually through AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD`.

Major register groups in this chunk:

- SDMA1 hypervisor/microcode controls: `SDMA1_UCODE_DATA`, `SDMA1_BROADCAST_UCODE_ADDR`, `SDMA1_BROADCAST_UCODE_DATA`, and `SDMA1_F32_CNTL`. These expose microcode indirect address/data fields, broadcast thread selection, F32 halt, per-thread checksum-clear/reset/enable bits, and thread priorities. The chunk starts after the `SDMA1_UCODE_ADDR` shift/mask pair, so the full SDMA1 microcode address register is split with the preceding chunk.
- SDMA0 and SDMA1 performance control and data blocks: `SDMA*_PERFCNT_PERFCOUNTER*_CFG`, `SDMA*_PERFCNT_PERFCOUNTER_RSLT_CNTL`, `SDMA*_PERFCNT_MISC_CNTL`, `SDMA*_PERFCOUNTER*_SELECT`, `SDMA*_PERFCOUNTER*_SELECT1`, `SDMA*_PERFCNT_PERFCOUNTER_LO/HI`, and `SDMA*_PERFCOUNTER{0,1}_LO/HI`. These provide event selector ranges, counter/performance modes, enable/clear bits, start/stop triggers, stop-on-saturate, command op fields, dual/four-way event selectors, and low/high counter readback fields.
- GRBM control/status block: `GRBM_CNTL`, `GRBM_SKEW_CNTL`, `GRBM_STATUS`, `GRBM_STATUS2`, `GRBM_STATUS3`, `GRBM_STATUS_SE0` through `GRBM_STATUS_SE5`, `GRBM_SOFT_RESET`, `GRBM_GFX_CLKEN_CNTL`, `GRBM_WAIT_IDLE_CLOCKS`, read/write error registers, interrupt/trap registers, UTCL2 invalidation range registers, fence ranges, scratch registers, and `VIOLATION_DATA_ASYNC_VF_PROG`. These macros describe top-level graphics busy/idle status, per-SE clean/busy state, CP/SDMA/RLC/TCP/UTCL2/EA/RMI request pending bits, soft-reset strobes, clock-gating waits, fault addresses/status, trap watch data/address masks, and scratch storage.
- Command processor decode block: `CP_CPC_*`, `CP_CPF_*`, `CP_STALLED_STAT*`, `CP_BUSY_STAT*`, `CP_STAT`, header dumps for ME/PFP/MEC, instruction pointers, `CP_CSF_STAT`, `CP_CNTX_STAT`, `CP_ME_PREEMPTION`, ring read pointers, write-pointer delay/polling, ROQ/STQ/MEQ thresholds and availability, command index/data indirect registers, queue status registers, debug indirect registers, and `CP_PRIV_VIOLATION_ADDR`. These expose CP pipeline busy/stall visibility, firmware/header diagnostics, queue/ring backpressure state, preemption state, and privileged violation address capture.
- Primitive assembler / geometry frontend block: `VGT_*`, `IA_UTCL1_*`, `WD_*`, `CC_GC_*`, `GE_*`, `GFX_PIPE_CONTROL`, `PA_CL_*`, `PA_SU_CNTL_STATUS`, and `PA_SC_FIFO_DEPTH_CNTL`. The fields cover FIFO depth reporting, MC latency thresholds, UTCL1 invalidation/status, work distributor controls and QoS, shader array and SA unit disable masks, geometry engine rate and status, pipe controls, safe-register flags, clipping enhancements, scan-converter limits, and primitive configuration.
- Shader queue block: `SQ_CONFIG`, `SQC_CONFIG`, `LDS_CONFIG`, `SQ_RANDOM_WAVE_PRI`, `SQG_STATUS`, `SQ_FIFO_SIZES`, `SQ_DSM_CNTL*`, `SP_CONFIG`, `SQ_ARB_CONFIG`, `SQ_DEBUG_HOST_TRAP_STATUS`, `SQG_GL1H_STATUS`, `SQG_CONFIG`, `SQ_PERF_SNAPSHOT_CTRL`, `CC_GC_SHADER_RATE_CONFIG`, `SQ_INTERRUPT_*`, four SQ watchpoint address/control sets, `SQ_IND_INDEX`, `SQ_IND_DATA`, and `SQ_CMD`. These define CU/simd mode flags, cache and LDS configuration, arbitration and prioritization, trap/debug status, GL1H/SQG status, shader-rate configuration, auto-masking and interrupt message controls, watchpoint address/mode/VMID fields, and indirect SQ command dispatch fields.
- Shader/SX/SPI block: `SX_DEBUG_1`, `SPI_PS_MAX_WAVE_ID`, `SPI_GFX_CNTL`, `SPI_DSM_CNTL*`, `SPI_EDC_CNT`, `SPI_CONFIG_PS_CU_EN`, `SPI_WF_LIFETIME_CNTL`, lifetime limit/status registers, `SPI_LB_*`, `SPI_GDS_CREDITS`, export/scoreboard buffer sizing, CSQ wavefront active status/counts, and P0/P1 trap-screen base/mask/GPR minimum registers. These support shader export debug options, wave ID tracking, lifetime monitoring and warning status, load-balancer wave counts, GDS credit configuration, buffer sizing, active wavefront counters, and trap-screen memory/GPR filters.
- Texture pipe start: `TD_STATUS`, `TD_SCRATCH`, `TA_CNTL`, and `TA_CNTL_AUX`. These include TD busy/scratch fields, TA credit controls, XNACK clock-gating disable, and many texture address/filtering behavior toggles. The chunk ends at `TA_CNTL_AUX__DETERMINISM_WRITEOP_READFMT_DISABLE_MASK`; remaining `TA_CNTL_AUX` masks and `TA_CNTL2` continue in the next chunk.

Field naming is descriptive. `*_LO`/`*_HI` are counter or pointer halves, `*_STATUS` and `*_STAT` expose live hardware state, `*_CNTL` and `*_CONFIG` program behavior, `*_SCRATCH_REG*` hold general scratch values, `*_ADDR`/`*_WD`/`*_MSK` describe trap/watch address and data matching, and indirect pairs such as `CP_CMD_INDEX`/`CP_CMD_DATA`, `CP_DEBUG_CNTL`/`CP_DEBUG_DATA`, `SQ_IND_INDEX`/`SQ_IND_DATA`, and SDMA microcode address/data registers require ordered accesses by the consumer.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU, AMDKFD, SDMA, display, MES, IMU, and GFX11 initialization/debug/profiling code:

1. A consumer includes `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
2. The consumer selects the register offset with the `mm*` macro and base index.
3. It builds or decodes a 32-bit register value using the `__SHIFT` and `_MASK` constants in this file.
4. It performs MMIO reads/writes or indirect index/data accesses through the driver register helpers while firmware, interrupts, reset code, power-management code, profiling tools, or debugfs paths coordinate the actual sequencing.

The chunk describes fields needed for SDMA performance counting, GRBM idle/fault inspection, CP queue and ring diagnostics, geometry/frontend control, SQ/SPI watchpoints and lifetime monitoring, and texture pipe configuration. It does not encode valid enum values, legal state transitions, read/write permissions, timeout policies, reset ordering, interrupt routing, or power-gating constraints; those must come from the consuming driver code and the hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes hardware state exposed through GC 11.0.0 registers.

The represented hardware state includes SDMA microcode address/data windows and F32 thread controls, SDMA perf counter selector/configuration and readback state, global GRBM busy/idle/fault/trap/scratch state, CP pipeline stall/busy/queue/ring/preemption diagnostics, primitive assembler and geometry frontend configuration, SQ watchpoint/interrupt/indirect command state, SPI wavefront lifetime counters and warnings, shader export debug controls, and the start of texture pipe configuration.

Persistence is hardware-defined. Some fields are durable configuration until GPU reset, suspend/resume, power gating, or driver reprogramming; some are live status bits that change as work progresses; some are latched fault or violation records; some are command/action bits such as reset, invalidate, clear, load, halt, or indirect command fields; and some are readback data windows owned by hardware or firmware. The macros do not identify access class, so consumers must preserve reserved and unrelated bits on mixed-control registers and must not infer that a full-width `0xFFFFFFFFL` field is always safe to write.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the matching register offsets and base indices. `gc_11_0_0_default.h` provides default values for the same register generation, and firmware loaded by GFX11/MES/IMU paths supplies part of the behavior behind CP, RLC, MEC, MES, IMU, and SDMA state.

Observed include users of this generated shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc21.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v11.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c`

Integration points include GFX11 ASIC initialization, SDMA setup and performance monitoring, GFX/MES/IMU firmware loading and control, KFD queue and MQD setup, display plane programming that needs GC register definitions, GPU reset/recovery, idle-wait and hang diagnostics, debugfs/register dumps, trap/watchpoint handling, shader profiling, performance-counter tools, and runtime power-management paths that must reprogram or validate volatile GC state.

## Risks And Edge Cases

- Header/offset mismatches are the primary generated-metadata risk. Pairing `gc_11_0_0_sh_mask.h` with another IP generation's offset header can compile but access the wrong register or field.
- The macros are untyped integer constants. Wrong register names, stale masks, or incorrect shifts can silently program a different bitfield, especially in dense status/control registers such as GRBM, CP, SQ, SPI, and TA controls.
- The chunk has artificial boundaries. It starts after `SDMA1_UCODE_ADDR` and ends before all `TA_CNTL_AUX` masks are present, so adjacent chunks are required for complete per-register coverage.
- Indirect register pairs require strict ordering. SDMA microcode address/data, CP command/debug index/data, and SQ indirect index/data accesses can return or update the wrong target if consumers interleave accesses without serialization.
- Status registers are live and often race with hardware progress. GRBM/CP/SQ/SPI busy, pending, clean, active, and stall bits can change between reads; timeout loops need appropriate polling, barriers, and power-state awareness.
- Soft reset, trap, invalidate, clear, load, halt, and warning/status bits may be self-clearing, sticky, write-one-to-clear, write-only, or firmware-owned. The macro file does not distinguish these semantics.
- Performance counters can produce false zeros or saturation if event selectors, enable/clear/start ordering, stop triggers, clock gating, per-instance filters, or workload placement do not match the active engine.
- CP queue/ring diagnostics and preemption fields are firmware- and scheduler-sensitive. Reading stale pointers or issuing commands during reset, preemption, MES ownership changes, or GPU recovery can misdiagnose hangs.
- Watchpoints and trap-screen registers involve address masks, VMID/context fields, and GPR thresholds. Incorrect preservation or programming can break debugging, raise unexpected traps, or miss intended memory events.
- Texture pipe and shader determinism/optimization disables in `TA_CNTL_AUX`, `SX_DEBUG_1`, and related controls can affect correctness, performance, or validation reproducibility; they should be changed only through known ASIC workarounds or documented debug paths.

## Test Signals

Useful validation is mostly build, static, and hardware/profiling coverage:

- Build coverage for all GFX11, SDMA v6, MES v11, IMU v11, display, and KFD files that include `gc_11_0_0_offset.h` and `gc_11_0_0_sh_mask.h`.
- Generated-header consistency checks that each field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts, and register names match entries in `gc_11_0_0_offset.h`.
- Static checks for non-overlapping fields within each register, except documented aliases or full-width data/status registers.
- SDMA perf counter smoke tests that clear/configure/start counters, run known SDMA copy/fill workloads, stop/read low/high values, and verify plausible nonzero or monotonic counter behavior.
- GPU idle/reset tests that poll GRBM and per-SE status before and after queue drains, soft resets, GPU recovery, suspend/resume, and runtime power transitions.
- CP diagnostics tests covering ring pointer readback, queue threshold/availability status, preemption visibility, header dumps, stalled/busy status, and privileged violation capture under controlled workloads.
- SQ/SPI debug tests for watchpoints, interrupt auto-mask behavior, indirect SQ commands, lifetime warning/status bits, active wavefront counters, and shader-rate or CU mask configuration.
- Geometry/frontend and texture-pipe validation using graphics workloads that exercise VGT, IA/WD/GE/PA, TA, and TD paths, with regression signals such as hangs, unexpected busy bits, bad primitive output, texture sampling differences, or validation-only determinism failures.
- Negative/regression indicators include counters stuck at zero or saturation, GRBM idle waits timing out, CP queue pointers not advancing, unexpected traps or violation addresses, watchpoints failing to trigger, lifetime interrupts firing unexpectedly, and failures isolated to specific GC 11.0.0 ASICs or firmware revisions.
