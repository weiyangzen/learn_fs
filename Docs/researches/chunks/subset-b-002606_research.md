# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_12_1_0_sh_mask.h lines 34981-37627

## Scope

This chunk is a generated AMD GC 12.1.0 shift/mask register-header segment. It defines preprocessor constants only: each hardware register field is represented by a `__SHIFT` macro and a matching `_MASK` macro for composing or decoding 32-bit MMIO register values. There are no C functions, structs, enums, global variables, branches, allocations, locks, callbacks, or direct persistence logic in this range.

The selected lines start in the middle of `SPI_TCP_CNTL`, so this document sees only the final masks for `MIN_LDS_PARTITIONS`, `MAX_LDS_PARTITIONS`, `IDLE_ALLOC_OPT_DIS`, `PARTIAL_DRAIN_DIS`, and `LDS_PINGPONG_DIS`; their shifts and the `DEFAULT_LDS_PARTITIONS` mask are immediately before the chunk boundary. The main covered address blocks are:

- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_comp_wgsdec`: WGS compute-dispatch register fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_wgsdec`: WGS controller, microcontroller, interrupt, status, scratch, metadata, and timer fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_gl1dec`: GL1/GL1X arbitration, credit, compression, UTCL0, control, and status fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_pfonly_secacdec`: shader-engine CAC and DIDT/EDC power-throttling fields.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_perfddec`: performance-counter data registers for GE2, GRBMH, PA, SPI, PC, SQ/SQG, SX, TA/TD/TCP, GL1, CB/DB, RMI, UTCL1, WGS, and related blocks.
- `CHIP_XCD_gfxip_xcc_gfx_se_gfx_se_perfsdec`: performance-counter selector registers through `PA_SU_PERFCOUNTER1_SELECT`; the final line is only the `PA_SU_PERFCOUNTER1_SELECT1` register comment, with that register's fields in the next chunk.

Although the repository path is under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata for the GC 12.1 graphics IP and is not Ceph filesystem code.

## Purpose

`gc_12_1_0_sh_mask.h` supplies the bit-level ABI between GC 12.1.0 hardware registers and AMDGPU/KFD driver code. Runtime code combines these masks with register addresses from `gc_12_1_0_offset.h` and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_FIELD15`, and `SOC15_REG_OFFSET`. This chunk describes WGS compute launch state, WGS microcontroller/debug state, GL1 cache/client arbitration, shader-engine power telemetry/throttling, and performance-monitor data and selector layouts.

The WGS compute-dispatch block defines fields for a hardware-driven compute dispatch path. It covers dispatch initiation flags such as compute-shader enable, partial thread-group enable, ordered append, ordering mode, scalar/vector L1 invalidation, ping-pong, tunnel, restore, wave32, AMP shader, display preemption disable, 2D interleave, WGS dispatch, and TTRACE queue id. It then defines grid dimensions, start and restart coordinates, per-axis full and partial thread counts, pipeline-stat and perfcount enables, program and dispatch-packet addresses, scratch base addresses, VMID, resource limits, per-SE CU destinations and static thread-management masks, temporary ring sizing, thread trace, dispatch and threadgroup ids, request controls, user accumulators, resource words, DDID index, shader checksum, dispatch interleave, relaunch controls, wave-restore address, prescaled dimensions, 16 user-data registers, dispatch tunnel/end sentinels, and a `NOWHERE` sink register.

The WGS controller block supplies fields for the WGS engine around interrupt reporting, endianness, generated base addresses, clock control, ME1 microcode address/data/checksum, suspend/resume context-save addresses and sizes, OS pipe exposure, DDID base/control, RS64 program counter and interrupt state, machine trap vector and interrupt-enable/pending registers, data/instruction cache base/bound/control windows, general-purpose registers, local data/instruction/scratch apertures, RS64 perfcount/exception state, ME1 pipe priority, IQ wait timers, microcode version, busy/stall/status surfaces, scratch index/data, latency-stat windows, TC perf-counter window selection, data registers, metadata base/control, IQ timer messages, and RS64 thread controls.

The GL1 block describes the shader-engine local cache and associated arbitration path. It covers GL1 and GL1X memory-pipe count, fine-grain clock-gating override, performance-counter enable override, arbitration status, DRAM burst masks and burst control, repeater clock-gating overrides, GL1A-to-GL1C and GL1XA-to-GL1XC credits, client-free delays, client-type compression overrides, compressor format overrides, GL1C/GL1XC control and status registers, UTCL0 controls/status/retry state, and secondary control fields.

The SE CAC/DIDT block describes shader-engine current/power estimation and throttling controls. It includes CAC controls, soft controls, override values, window aggregate values and cycle counters, DIDT EDC control/throttle/threshold/stretch/counter/stall/status/overflow/power-delta fields, per-block CAC weights for LDS, TCP, SQ, SP, SQC, CU, UTCL1, GL1C, and SPI, plus the indexed `SE_CAC_IND_INDEX` and `SE_CAC_IND_DATA` access registers.

The performance data/select blocks define the low/high counter storage and selector programming for many graphics sub-blocks. Most counter-data registers expose either a full 32-bit low value or a 16-bit high value. Selector registers commonly expose 10-bit event selector fields, a 4-bit counter mode, and high-nibble performance mode fields. Specialized selector forms include GRBMH user-defined busy/clean masks for many sub-blocks and TCP filter/filter-enable fields for cache operation, opcode, swizzle, data/number format, sample count, address mode, GLC/SLC, and compression attributes.

## Important APIs, Types, and Macros

This chunk defines no callable APIs or C types. Its API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Register comments such as `//WGS_COMPUTE_PGM_RSRC1` and address-block comments preserve generated hardware grouping.
- Companion address symbols are in `gc_12_1_0_offset.h`, for example `regWGS_COMPUTE_DISPATCH_INITIATOR`, `regWGS_STATUS`, `regGL1_DRAM_BURST_CTRL`, `regSE_CAC_IND_INDEX`, `regTCP_PERFCOUNTER_FILTER`, and `regPA_SU_PERFCOUNTER0_SELECT`.

Observed GC 12.1 consumers include `gfx_v12_1.c`, `mes_v12_1.c`, `sdma_v7_1.c`, `gfxhub_v12_1.c`, `imu_v12_1.c`, `soc_v1_0.c`, `amdgpu_amdkfd_gfx_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`, all of which include the GC 12.1 offset and/or mask headers. The specific names in this chunk are mostly consumed by MMIO helpers, register-dump/profiling paths, power/clock/debug plumbing, and packet or firmware initialization flows rather than by a single local algorithm.

Two integration points are visible outside the generated headers. `soc15.c` provides locked indexed accessors for `SE_CAC_IND_INDEX` and `SE_CAC_IND_DATA`, so the final SE CAC registers in this chunk are part of the generic shader-engine CAC indirect access path. `gfx_v12_1.c` writes `regGL1_DRAM_BURST_CTRL` during GC 12.1 setup, so GL1 control fields in this chunk are runtime-relevant even when written as whole-register values rather than through `REG_SET_FIELD`.

## Control Flow

There is no executable control flow in this header. Control flow exists in consumers that compose register values, write MMIO registers, poll status bits, or decode register dumps using these constants.

The WGS compute path is a programmed-state flow: software or firmware writes program address, packet address, scratch address, program resource words, VMID, grid dimensions, thread counts, CU routing, user data, and related controls before asserting dispatch/initiation fields. Restart, relaunch, wave-restore, tunnel, dispatch-end, and status fields are then used by the hardware/firmware path to manage progress, recover waves, or report diagnostics.

The WGS controller path is a firmware/microcontroller flow. Microcode address/data/checksum registers support loading or inspecting WGS/ME1 firmware state; RS64 program counter, interrupt, cache base/bound/control, local aperture, timer, and scratch/data windows support initialization and debug. Busy, stalled, status, error, interrupt, and pending-interrupt fields are read or polled by diagnostics and recovery paths.

The GL1 path is a configuration/status flow. Driver setup or firmware can tune arbitration, burst policy, credits, client-free delay, compression overrides, UTCL0 behavior, and clock-gating overrides, then status registers expose stalls, FIFO pressure, request/data credits, retry state, translation activity, and other cache-front-end health signals.

The SE CAC/DIDT path uses both direct registers and indexed registers. Generic `soc15_se_cac_rreg()` and `soc15_se_cac_wreg()` serialize indexed accesses with `adev->reg.se_cac.lock`, write `SE_CAC_IND_INDEX`, then read or write `SE_CAC_IND_DATA`. DIDT/EDC fields are configuration/status surfaces for power throttling and error-detection controls; CAC weight registers feed shader-engine power/current estimation.

The performance-monitor path is a select, sample, read flow. Selector registers choose event ids, packing/modes, filters, and user-defined busy masks; counter data registers then expose low/high portions of sampled counts. GC clock-gating code in `gfx_v12_1.c` also toggles performance-monitor clock state through RLC controls outside this chunk, which is an enabling condition for reliable performance-counter sampling.

## State and Persistence

The macros themselves are compile-time constants and have no state. The hardware registers they describe are volatile MMIO state owned by the GC 12.1 graphics engine, shader engines, WGS firmware, cache blocks, power-management logic, and performance monitor hardware.

Some described register state is persistent across a running queue or dispatch. WGS program address, dispatch-packet address, scratch base, resource words, VMID, dimensions, user-data registers, static thread-management masks, destination CU masks, metadata base/control, cache apertures, and GL1 arbitration/credit/compression settings remain meaningful until reprogrammed, reset, or overwritten by firmware.

Other state is transient, sticky, or command-like. Dispatch initiator bits, relaunch controls, cache invalidate/prime controls, IQ timer active/rearm bits, interrupt status/pending bits, error latches, busy/stalled/status bits, latency-stat clear/enable bits, EDC overflow/status, and performance-counter values can change as hardware runs. Consumers must use the sequencing, polling, and timeout rules in the owning driver/firmware code because this header only describes bit positions.

SE CAC indirect accesses have software serialization in `soc15.c`. The index/data pair is shared hardware state, so callers must use the locked helper path or equivalent serialization to avoid racing an index write against another reader/writer.

## Dependencies and Integration Points

The immediate dependency is the generated GC 12.1 offset header, `gc_12_1_0_offset.h`, which supplies the register addresses corresponding to this chunk's field layouts. Unlike several older generated GC header sets in this tree, no `gc_12_1_0_default.h` file is present; GC 12.1 code uses explicit defaults in local source where needed and, in `mes_v12_1.c`, includes `gc_11_0_0_default.h` for shared default values.

Runtime integration points include:

- GC 12.1 graphics bring-up in `gfx_v12_1.c`, which includes this mask header, programs GL1/TCP/RLC/CP registers, initializes MEC/RLC firmware, controls clock gating, sets up queues, and reads status.
- MES bring-up in `mes_v12_1.c`, which includes the same generated headers and programs firmware, queues, doorbells, HQD/MQD state, and cache controls.
- KFD queue and debug paths in `amdgpu_amdkfd_gfx_v12_1.c`, `kfd_mqd_manager_v12_1.c`, and `kfd_device_queue_manager_v12_1.c`, which rely on the same register macro contract for queue/debug register state.
- Generic SOC15 CAC access in `soc15.c`, whose `SE_CAC_IND_INDEX`/`SE_CAC_IND_DATA` accessors are the software integration point for the final SE CAC indexed registers.
- Performance tooling and debug/register-dump paths, which depend on counter-data, selector, TCP filter, WGS status, GL1 status, and GRBMH busy-mask fields to produce meaningful diagnostics.
- Power-management and throttling flows, where SE CAC weights, DIDT/EDC thresholds, throttle controls, rolling/average power deltas, and CAC aggregate windows connect shader-engine activity to power/current management policy.

The generated names also align with `soc24_enum.h`, which provides event selector enumerations for GC 12-era performance counters such as GL1C and GL1XC. Event enums identify what to count; this chunk identifies where those event ids and modes are encoded in hardware registers.

## Risks

The primary risk is silent hardware misprogramming. A wrong shift or mask usually still compiles, but it can write the wrong bit, truncate an address, enable a reserved mode, decode a stale status bit as current, or select the wrong performance event.

WGS compute fields are high risk because they describe dispatch launch state. Incorrect program address high/low masks, scratch base masks, VMID, resource words, user-data fields, thread counts, CU masks, dispatch initiator bits, or relaunch/restore controls can cause bad shader execution, lost dispatches, privilege issues, invalid memory accesses, or hangs during recovery.

WGS controller fields are high risk for firmware and diagnostics. Bad microcode address/data/checksum fields, RS64 cache controls, program-counter fields, interrupt/pending/error masks, local aperture fields, metadata controls, timer fields, or thread-control bits can break firmware bring-up, interrupt attribution, debug capture, or reset handling.

GL1 and GL1X fields are sensitive for memory correctness and performance. Arbitration, credit, burst, compression override, UTCL0, retry, and status fields affect cache traffic, translation behavior, and stall diagnosis. Wrong masks can produce subtle data-path corruption, severe performance cliffs, or misleading fault/stall reports.

SE CAC/DIDT fields are power-policy sensitive. Incorrect weight, threshold, throttle, stretch, rolling/average delta, override, or overflow fields can make power/current estimation inaccurate, trigger unnecessary throttling, or fail to throttle under high-current conditions. Indexed SE CAC access is also race-prone if the index/data pair is touched without proper locking.

Performance-counter fields are mechanically repetitive and easy to corrupt during generation or manual edits. Similar register families differ in high/low width, selector field names (`PERF_SEL`, `PERF_SEL0`, `PERF_SEL1`), mode packing, filter availability, and user-defined busy masks. Counter code may appear to work while silently sampling the wrong event or applying the wrong filter.

The chunk boundaries are themselves a reconciliation risk. It starts after the first `SPI_TCP_CNTL` field definitions and ends before `PA_SU_PERFCOUNTER1_SELECT1` fields. A merged per-file report must connect those partial registers with adjacent chunks.

## Test Signals

Useful compile-time signals are successful builds of GC 12.1 AMDGPU, MES, SDMA, GFXHUB, IMU, SOC, and KFD paths that include `gc_12_1_0_sh_mask.h`. Missing or renamed macros are normally caught by compilation, while wrong numeric values require hardware or register-level validation.

Graphics and compute bring-up signals include successful probe of GC 12.1 ASICs, MEC/RLC/MES firmware load, queue initialization, KIQ/MES ring tests, KFD queue creation, dispatch completion, suspend/resume, and GPU reset recovery. WGS-specific confidence would come from workloads that exercise work-graph or WGS dispatch paths, relaunch/restore behavior, thread trace, VMID isolation, scratch use, and user-data/resource programming.

GL1 signals include stable shader memory workloads, no unexpected VM/XNACK or cache retry storms, correct GL1/GL1X status under stress, no regressions from `regGL1_DRAM_BURST_CTRL` setup, and sane cache/performance behavior when compression, burst, credit, and arbitration settings are active.

SE CAC/DIDT validation should cover indexed `SE_CAC_IND_INDEX`/`SE_CAC_IND_DATA` reads and writes through the locked SOC15 helpers, power/thermal stress workloads, EDC threshold and overflow reporting, throttle activation/deactivation, CAC aggregate windows, and sane rolling/average power delta values.

Performance-monitor validation should program GE2, GRBMH, PA, SPI, PC, SQ/SQG, SX, TA/TD/TCP, GL1, CB/DB, RMI, UTCL1, and WGS counters with known event selectors; verify low/high counter reads; exercise TCP filters; verify GRBMH user-defined busy masks; and ensure performance-monitor clock gating does not leave counters frozen or returning implausible values.

Diagnostic signals include coherent register dumps for `WGS_STATUS`, `WGS_BUSY_STAT`, `WGS_STALLED_STAT1`, `WGS_BUSY_STAT2`, `GL1C_STATUS`, `GL1XC_STATUS`, `GL1XC_UTCL0_STATUS`, `DIDT_EDC_STATUS`, `DIDT_EDC_OVERFLOW`, `WGS_PERFMON_CNTL`, counter low/high registers, and selector registers after representative compute, graphics, memory, and power workloads.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002606`. It covers lines 34981-37627 of `gc_12_1_0_sh_mask.h`. The final per-file report should merge this with the preceding chunk for the full `SPI_TCP_CNTL` context and with the following chunk for `PA_SU_PERFCOUNTER1_SELECT1` and later performance selector definitions.
