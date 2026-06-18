# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_sh_mask.h lines 27594-30086

## Scope

This chunk is a generated AMD GC 11.5.0 shift/mask register-header segment. It contains preprocessor constants only: each hardware field is represented by a `__SHIFT` bit position and an `_MASK` value used by AMDGPU register helpers to compose or decode 32-bit register values.

The requested range contains 2,145 `#define` entries: 1,074 `__SHIFT` constants and 1,087 `_MASK` constants. The mismatch is caused by artificial chunk boundaries and by the generated layout, not by executable behavior. The first requested line starts inside `SPI_PERFCOUNTER0_SELECT` after `PERF_SEL__SHIFT` was defined on line 27593, and the final requested line stops inside `RLC_CGCG_RAMP_CTRL` before its remaining masks on lines 30087-30090.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU DRM graphics-core register metadata. It does not implement distributed filesystem logic.

## Purpose

`gc_11_5_0_sh_mask.h` supplies the bit layouts for GC 11.5.0 graphics, compute, cache, command processor, RLC, performance-monitoring, and power-management registers. Driver code pairs these constants with register offsets from `gc_11_5_0_offset.h` and uses helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, indexed-register accessors, and command-stream state programming paths.

This chunk covers several dense register families:

- Graphics and compute performance counter selector registers for SPI, primitive/parameter cache, shader queues, global shader queues, SX, GDS, TA, TD, TCP, GL2C, GL2A, GL1C, CHC, CB, DB, RMI, GCR, PA_PH, UTCL1, GL1A, GL1H, and CHA blocks.
- Counter mode/filter controls, including packed `PERF_SEL*`, `PERF_MODE*`, `CNTR_MODE`, `SPM_MODE`, `PERFCOUNT_EN`, client/instance selectors, mux selectors, block selection, start/stop controls, and result counter controls.
- SQ thread trace setup and status fields for buffer bases and sizes, trace masks, token filtering, write pointers, draw/marker counters, HP3D counters, dropped-event counts, and status/error visibility.
- RLC SPM and RSPM monitoring controls, including SPM ring base/size/writer/reader pointers, segment thresholds, global and shader-engine mux select address/data registers, accumulator data/control RAM accessors, sample thresholds, pause/status, clock counters, remote SPM request/return operations, command/ack, and spare fields.
- GRTAVFS and RTAVFS voltage/frequency register access windows, target frequency/voltage fields, soft reset, PSM and clock control, and related register status fields.
- CP hypervisor and command processor microcode windows for PFP, ME, and MEC engines, plus instruction-cache and data-cache base/bound/control fields for PFP, ME, CPC, MES, GFX RS64, and MEC paths.
- The start of the RLC decoder block, including RLC control/status, firmware version, reference and GPU clock timestamps, GPM timer and interrupt controls, jump-table restore, power-gating delay, ucode control, GPM thread controls, clock-count sampling, RLCG doorbells, 32-bit GPU clock selection, power-gating control, GPM thread priority/enable, doorbell ranges, clock-gating overrides, and CGCG/CGLS ramp controls.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, memory allocations, locks, callbacks, or runtime branches in this range. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register value.
- Register offsets for the same GC 11.5.0 address space live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`.
- Consumers typically compose values with `REG_SET_FIELD`, decode with `REG_GET_FIELD`, and access hardware through SOC15 MMIO helpers or command-stream packets.

Important macro families in this chunk include:

- `SPI_PERFCOUNTER*_SELECT`, `PC_PERFCOUNTER*_SELECT`, `SQ_PERFCOUNTER*_SELECT`, `SQG_PERFCOUNTER*_SELECT`, `SX_PERFCOUNTER*_SELECT`, `GDS_PERFCOUNTER*_SELECT`, `TA_PERFCOUNTER*_SELECT`, `TD_PERFCOUNTER*_SELECT`, `TCP_PERFCOUNTER*_SELECT`, `GL2C/GL2A/GL1C/GL1A/GL1H_PERFCOUNTER*_SELECT`, `CHC/CHA_PERFCOUNTER*_SELECT`, `CB_PERFCOUNTER*_SELECT`, `DB_PERFCOUNTER*_SELECT`, `RMI_PERFCOUNTER*_SELECT`, `GCR_PERFCOUNTER*_SELECT`, `PA_PH_PERFCOUNTER*_SELECT`, and `UTCL1_PERFCOUNTER*_SELECT`: packed event selector and mode fields for block-specific performance counters.
- `SPI_PERFCOUNTER_BINS` and `CB_PERFCOUNTER_FILTER`: binning and filter masks that constrain which events/fragments/samples/formats/MRT operations contribute to counters.
- `SQG_PERFCOUNTER_CTRL`, `SQG_PERFCOUNTER_CTRL2`, `SQ_PERFCOUNTER_CTRL`, and `SQ_PERFCOUNTER_CTRL2`: block selection, perfmon state, client control, token mask selection, SPM enablement, SIMD/CU/WGP/SA/SE instance selectors, and perfcounter engine gating.
- `SQ_THREAD_TRACE_BUF*_BASE`, `SQ_THREAD_TRACE_BUF*_SIZE`, `SQ_THREAD_TRACE_CTRL`, `SQ_THREAD_TRACE_MASK`, `SQ_THREAD_TRACE_TOKEN_MASK`, `SQ_THREAD_TRACE_WPTR`, `SQ_THREAD_TRACE_STATUS`, `SQ_THREAD_TRACE_STATUS2`, and thread-trace counter registers: shader trace buffer placement, capture filters, token filters, wrap/finish/status bits, and event counters.
- `GCEA_PERFCOUNTER*_CFG`, `GCEA_PERFCOUNTER2_MODE`, and `GCEA_PERFCOUNTER_RSLT_CNTL`: GCEA counter configuration, enable/clear, selection ranges, compare values/modes, and result-control fields.
- `RLC_SPM_*`: streaming performance monitor ring, mux, accumulator, pause, status, clock-count, and remote SPM request/return field definitions.
- `RLC_PERFMON_CNTL`, `RLC_PERFCOUNTER0_SELECT`, and `RLC_PERFCOUNTER1_SELECT`: RLC-level perfmon enable and event selection.
- `GRTAVFS_*` and `RTAVFS_*`: register-window address/data/control/status fields for adaptive voltage/frequency control and target frequency/voltage programming.
- `CP_HYP_*_UCODE_*`, `CP_*_UCODE_*`, `CP_ME_RAM_*`: command processor microcode and ME RAM address/data windows.
- `CP_PFP_IC_*`, `CP_ME_IC_*`, `CP_CPC_IC_*`, `CP_MES_IC_*`, `CP_MES_DC_*`, `CP_GFX_RS64_DC_*`, `CP_MEC_DC_*`, and corresponding base/bound/control registers: instruction/data cache base address, VMID, cache policy, execute-disable, address-clamp, invalidate, and prime-status fields.
- `RLC_CNTL`, `RLC_STAT`, `RLC_GPM_TIMER_*`, `RLC_INT_STAT`, `RLC_MGCG_CTRL`, `RLC_UCODE_CNTL`, `RLC_CLK_COUNT_*`, `RLC_RLCG_DOORBELL_*`, `RLC_PG_CNTL`, `RLC_CGTT_MGCG_OVERRIDE`, `RLC_CGCG_CGLS_CTRL`, and `RLC_CGCG_RAMP_CTRL`: low-level RLC control, interrupts, clocks, doorbells, power gating, and clock gating.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 11.5.0 register definitions for the active ASIC or for a shared GC 11.x path.
2. Pair a register address from `gc_11_5_0_offset.h` with the field layout from this header.
3. Use a register helper to insert or extract field values.
4. Perform MMIO, indexed-register, RLC-safe, KIQ, or command-stream register access in the surrounding driver code.

For performance monitoring, higher-level code chooses a hardware block and event IDs, writes the relevant `*_PERFCOUNTER*_SELECT` fields, configures counter mode/filtering, optionally enables SPM capture through `SPM_MODE` or RLC SPM registers, starts capture, reads counters or SPM ring data, then disables or reconfigures counters.

For SQ thread trace, the surrounding trace/debug path programs buffer base/size registers, masks target shader engines/arrays/CUs/SIMDs/waves, configures token filtering and capture behavior, starts tracing, watches status/write-pointer fields, and collects trace buffer contents. This header only names the bit layout; it does not provide the sequencing, synchronization, or ownership rules.

For CP microcode and cache registers, firmware-loading and engine-init code writes address/data windows for PFP/ME/MEC microcode or ME RAM, programs IC/DC bases and bounds, sets VMID/cache policy/execute-disable bits, and requests instruction-cache invalidation or priming. The cache-control fields here are side-effect sensitive, but the header does not encode waits or completion polling.

For RLC and GRTAVFS, driver power-management and firmware-control paths read or write control/status registers, configure timers and interrupts, sample clock counters, set doorbell modes and ranges, enable or disable clock/power gating, and interact with voltage/frequency target windows. The exact order is owned by the RLC, SMU, gfx, and power-management code.

## State And Persistence Behavior

The macros themselves hold no state and persist nothing. They describe hardware-visible state in GC 11.5.0 registers:

- Performance counter selector and control registers persist until the driver reprograms them, resets the engine, changes context/state where applicable, or power management loses/restores the block state. Counter results and status fields can change continuously while workloads run.
- SPM ring fields describe GPU memory addresses, ring sizes, read/write pointers, segment sizes, mux selectors, accumulator RAM access, pause state, and clock-count sampling. These values influence DMA-like performance data capture into memory and must agree with allocated buffers and VMID/addressing setup.
- SQ thread trace fields describe trace buffers, capture masks, token masks, write pointers, and status bits. Some fields are software-programmed configuration; others are hardware-updated status/counters.
- GRTAVFS and RTAVFS fields represent an indirect register access window plus voltage/frequency targets and control bits. Their effects persist in the adaptive voltage/frequency subsystem until changed, reset, or overridden by firmware/power-management policy.
- CP microcode address/data windows, ME RAM address/data windows, and cache base/bound/control registers affect command processor firmware storage and instruction/data fetch behavior. Base and bound fields usually carry address alignment/unit constraints not visible from the mask name alone.
- RLC control, clock, timer, interrupt, doorbell, power-gating, and clock-gating registers describe persistent firmware/engine state. Some status/interrupt/clear fields may be latched, write-one-to-clear, or read-sensitive according to hardware documentation; this generated header does not mark those access semantics.

Reserved fields appear throughout the range. Callers should preserve reserved bits on read-modify-write unless they are emitting a documented full-register value from an initialization table.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_5_0_offset.h`, which supplies matching register offsets. The shift/mask file and offset file must remain synchronized with the same GC 11.5.0 register database.

Observed integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c`, which includes both `gc_11_5_0_offset.h` and `gc_11_5_0_sh_mask.h` and uses GC register field helpers for GFXHUB VM/fault handling.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0.c`, which declares GC 11.5.x firmware names for PFP, ME, MEC, and RLC. The CP and RLC register families in this chunk are part of the same hardware initialization surface even where this exact generated header is included indirectly or shared through common GC 11 code paths.
- Common AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, KIQ-safe accessors, and debug/perfmon register paths.
- Profiling and tracing consumers that program SQ/SQG/SPI/cache/block performance counters, RLC SPM, and SQ thread trace registers.
- Firmware loading and engine setup paths for PFP, ME, MEC, MES, CPC, and RS64 cache/register state.
- Power-management and clock-gating paths coordinating RLC, SMU, GRTAVFS/RTAVFS, CGCG/CGLS, MGCG, dynamic/static WGP power gating, and clock-count sampling.

Behaviorally, this chunk sits at the boundary between performance observability, shader tracing, command processor firmware/cache setup, low-level RLC firmware services, and graphics-core clock/power control.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask compiles cleanly but writes or decodes the wrong hardware bits.
- The chunk begins and ends mid-register. The previous chunk owns `SPI_PERFCOUNTER0_SELECT__PERF_SEL__SHIFT`; the next chunk owns the remaining `RLC_CGCG_RAMP_CTRL` masks and subsequent dynamic power-gating fields. File-level research must merge these boundaries before making complete register-family claims.
- Repeated performance counter layouts are copy-sensitive. A single typo in `PERF_SEL`, `PERF_SEL1`, `PERF_SEL2`, `PERF_SEL3`, `CNTR_MODE`, or `PERF_MODE*` can corrupt only one counter lane or one block, which may escape broad build testing.
- SPM and thread trace fields are buffer-address sensitive. Incorrect base, size, write-pointer, segment, or mux fields can cause lost samples, overwritten memory, invalid traces, or GPU faults during profiling.
- Instance selector fields such as SE/SA/WGP/CU/SIMD/wave and global/instance mux selectors can make counters appear valid while measuring the wrong hardware instance.
- CP cache base and bound fields likely use aligned address units. Misinterpreting low/high address masks, VMID fields, execute-disable bits, or cache policy fields can cause firmware fetch failures, command processor hangs, or security/isolation regressions.
- Cache operation bits such as `INVALIDATE_CACHE`, `PRIME_ICACHE`, completion bits, and primed status are ordering-sensitive. The header provides masks but not the required polling or wait sequence.
- RLC interrupt/status/clear fields can be access-sensitive. Using masks without respecting W1C, latched, or firmware-owned semantics can lose interrupts or wedge low-level firmware coordination.
- Doorbell control/range/data fields affect RLCG communication. Bad mode, ID, valid, or address-range fields can drop firmware doorbells, accept unexpected doorbells, or break virtualization/resource isolation.
- RLC power-gating and clock-gating fields interact with SMU handshakes, MGCG/CGCG/CGLS controls, low-voltage mode, and per-WGP gating. Incorrect masks may show up as intermittent hangs, resume failures, performance regressions, or broken clock/power reporting rather than immediate compile failures.
- GRTAVFS and RTAVFS target frequency/voltage fields are power-management sensitive. Incorrect access-window or target field definitions can create unstable voltage/frequency programming or ineffective power policy changes.

## Test Signals

Useful validation should combine generated-data checks, build coverage, and runtime hardware coverage:

- Build AMDGPU with GC 11.5 support enabled. Missing or renamed macros should surface in `gfxhub_v11_5_0.c`, common GC 11 code, perfmon/debug paths, firmware setup, and RLC/power-management code.
- Mechanically compare this range against the authoritative GC 11.5.0 register database. Check that complete registers in the range have aligned `__SHIFT` and `_MASK` pairs and that repeated counter families are structurally consistent.
- Cross-check every register family in this chunk against `gc_11_5_0_offset.h` for matching register offset names.
- Run static mask sanity checks: masks should align with shifts, full-width fields should use `0xFFFFFFFFL`, reserved fields should cover the expected holes, and repeated `*_PERFCOUNTER*_SELECT` families should share identical layouts where the hardware block names imply repetition.
- Exercise graphics/compute performance counter collection across SPI, PC, SQ/SQG, SX, GDS, TA/TD/TCP, GL1/GL2, CB/DB, RMI/GCR, PA_PH, UTCL1, and CH blocks. Relevant signals include nonzero counters under targeted workloads, correct block/instance selection, clean start/stop, and no GPU reset.
- Exercise RLC SPM capture with valid and boundary ring sizes, segment thresholds, mux settings, pause/resume, accumulator modes, and clock-count sampling. Expected signals are coherent sample buffers, stable write/read pointers, and no memory faults.
- Exercise SQ thread trace with multiple shader-engine/array/CU masks, token masks, buffer sizes, wrap modes, draw/marker workloads, and high event pressure. Watch for dropped-count behavior, status flags, and trace decodability.
- Exercise CP firmware loading or cache initialization paths for PFP, ME, MEC, MES/CPC/RS64 cache bases and bounds. Expected signals include successful firmware start, cache invalidate/prime completion, no command processor hangs, and correct engine status.
- Exercise RLC timers, interrupts, GPM thread controls, doorbells, and clock-count sampling. Relevant signals include expected interrupt/status transitions and stable firmware communication.
- Exercise power and clock gating transitions, suspend/resume, runtime power management, and heavy graphics/compute workloads while toggling relevant RLC/SMU policies. Watch for hangs, clock-count anomalies, SMU handshake failures, or regressions in idle/power behavior.
- Validate GRTAVFS/RTAVFS control through power-management test paths where supported, checking that target frequency/voltage and status fields behave as expected without destabilizing the GPU.

## Cross-Chunk Notes

The previous chunk must be consulted for the first field of `SPI_PERFCOUNTER0_SELECT`; this chunk starts at `SPI_PERFCOUNTER0_SELECT__PERF_SEL1__SHIFT`. The next chunk must be consulted for the remaining masks of `RLC_CGCG_RAMP_CTRL` and the following RLC dynamic power-gating registers. The final per-file document should reconcile these artificial boundaries and describe `gc_11_5_0_sh_mask.h` as a single generated GC 11.5.0 register field map.
