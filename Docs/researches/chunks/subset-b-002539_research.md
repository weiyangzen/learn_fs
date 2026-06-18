# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h lines 32348-34934

## Scope

This chunk covers generated shift and mask macros from the GC 11.0.3 AMD GPU register header. It begins in the tail of `GL2C_CM_CTRL2`, then spans register field layouts for:

- GL2C control, load-balancer counters, discard-stall control, and GL2A arbitration/address-match controls.
- `gc_gl1hdec` GL1H arbitration, credit, burst, and status registers.
- `gc_perfddec` performance counter data registers for CP, GRBM, GE, PA, SPI, PC, SQ/SQG, SX, GCEA, GDS, TA/TD/TCP, GL2, GL1, CH, CB/DB, RLC/RMI/GCR, PH, UTCL1, CHA, and GUS blocks.
- `gc_perfsdec` performance counter selector/control registers, CP latency/window/draw filtering controls, GRBM busy-mask selectors, GE/PA/SPI/PC/SQ/SQG/SX/GCEA/GDS selectors, SQ thread trace buffer/control/status registers, and TCP performance counter filters.

The chunk is a preprocessor-only hardware description. It defines no C functions, structs, enums, storage, or executable control flow. Its contract is the exact bit layout used by AMDGPU code and debug/performance tooling when composing, writing, reading, or decoding GC 11.0.3 MMIO registers.

## Purpose

Each register field is represented by two macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for encoding or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit field mask for isolating that field.

These macros are intended to be used with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`. Register addresses live in the matching `gc_11_0_3_offset.h`; reset/default values live in the matching default header. This file supplies only the per-field bit layout.

The most important behavior represented by this chunk is performance/debug instrumentation. It describes how to select performance events, gate them by shader stage, VMID, draw windows, command processor state, TCP request attributes, and thread trace masks, and how to read low/high counter data registers. It also contains a smaller amount of GL2/GL1 cache/arbitration configuration metadata.

## GL2C, GL2A, and GL1H Register Fields

The opening lines finish `GL2C_CM_CTRL2`, including masks for read burst timing, VRS disable, compression-ratio skipping, NBC indirect disables, partial-write optimization modes, recompression disable, and DCC compression-key error detection/clear behavior.

`GL2C_CTRL3` and `GL2C_CTRL4` provide broad GL2 cache-control metadata:

- Metadata memory type/coherency, no-fill, next-line prefetch, bank-linear hash mode/enable, 256-byte hash enable, set-group linear hash enable, and dGPU shared mode.
- Priority controls for HTILE, FMASK, DCC/CMASK, and SQC traffic.
- Writeback/write-read behavior such as force-read-on-write, writeback optimization enable/burst count, sector-full write marking, uncached-write atomic handling, read bypass as UC, and force MTYPE UC.
- Clock-gating and safe-mode controls such as `FGCG_OVERRIDE`, `CM_MGCG_MODE`, `MDC_MGCG_MODE`, `TAG_MGCG_MODE`, `CORE_MGCG_MODE`, `EXECUTE_MGCG_MODE`, and `FED_SAFE_MODE`.
- External access and protocol controls such as IO channel enable, SPA channel enable, EA read-size/GMI/NACK controls, source FIFO priority, writeback FIFO stall enable, flush-set counter mask disable, and no-write-ack-to-hit-queue.

The GL2C load-balancer counter group includes `GL2C_LB_CTR_CTRL`, `GL2C_LB_DATA0..3`, and `GL2C_LB_CTR_SEL0/1`. These fields control counter start/load/clear, select four events, optionally divide them, and read the resulting 32-bit counter values.

`GL2C_DISCARD_STALL_CTRL` provides a limit/window/drop-next/enable layout for discard-stall throttling. `GL2A_ADDR_MATCH_CTRL`, `GL2A_ADDR_MATCH_MASK`, and `GL2A_ADDR_MATCH_SIZE` describe address-match disabling, masks, and max-count sizing. `GL2A_PRIORITY_CTRL`, `GL2A_CTRL`, and `GL2A_RESP_THROTTLE_CTRL` describe priority disables, return arbitration timing, burst staying, FGCG override, credit safe values, write-combine timeout, address column-bit removal, internal return bypass, and response throttle credits for GL1/channel paths.

The `gc_gl1hdec` block contains `GL1H_ARB_CTRL`, `GL1H_GL1_CREDITS`, `GL1H_BURST_MASK`, `GL1H_BURST_CTRL`, and `GL1H_ARB_STATUS`. These fields cover request/source/return fine-grain clock gating disables, GL1 request credits, burst-mask selection, burst-timer value, burst-in-flight counter, and stall status.

## Performance Counter Data Registers

The `gc_perfddec` portion is mostly readout storage for performance counters. The simple `*_PERFCOUNTER*_LO` and `*_PERFCOUNTER*_HI` macros define full-width 32-bit low/high fields named `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, or a variant such as `PERFCOUNTER0_LO`. These pairs form 64-bit counter values when read in the correct order by consumers.

Covered blocks include:

- Command processor families: `CPG`, `CPC`, `CPF`, plus latency statistics data for CPF/CPG/CPC.
- Global graphics and shader engine front-end: `GRBM`, `GRBM_SE0..3`, `GE1`, `GE2_DIST`, and `GE2_SE`.
- Geometry/raster/front-end units: `PA_SU`, `PA_SC`, `PA_PH`, `SPI`, and `PC`.
- Shader and shader-global counters: `SQ_PERFCOUNTER0..7_LO` and `SQG_PERFCOUNTER0..7_LO/HI`.
- Pixel/export/shared-data paths: `SX`, `GCEA`, `GDS`, `TA`, `TD`, `TCP`, `CB`, `DB`, `CHC`, `CHCG`, `CHA`, and `GUS`.
- Cache, memory, and control paths: `GL2C`, `GL2A`, `GL1C`, `GL1A`, `GL1H`, `UTCL1`, `RLC`, `RMI`, and `GCR`.

Most of these registers expose only a single full-register data field. They are semantically dependent on the selector/configuration registers in `gc_perfsdec`; incorrect selector programming will still produce syntactically valid reads but meaningless or misleading counter values.

## TCP Counter Filters

`TCP_PERFCOUNTER_FILTER`, `TCP_PERFCOUNTER_FILTER2`, and `TCP_PERFCOUNTER_FILTER_EN` describe request filtering for TCP performance counters. The filter value includes buffer/flat/dimension fields, data and number format fields, software mode, sample count, opcode type, SLC/DLC/GLC coherency attributes, compression enable, and request mode. The corresponding enable register has one bit per filter dimension.

This split means consumers must program both a filter value and the enable mask. A filter field set in `TCP_PERFCOUNTER_FILTER` has no effect unless its enable bit is set in `TCP_PERFCOUNTER_FILTER_EN`. Conversely, leaving enable bits set while changing only part of the filter can silently narrow or broaden captured traffic.

## Performance Counter Select and Control Registers

The `gc_perfsdec` block provides the programming side for the data registers:

- CP selectors include `CPG_PERFCOUNTER*`, `CPC_PERFCOUNTER*`, and `CPF_PERFCOUNTER*` select layouts with `PERF_SEL`, `PERF_SEL1`, `SPM_MODE`, and counter-mode fields.
- `CP_PERFMON_CNTL` exposes overall performance monitor state, SPM performance monitor state, enable mode, and sample enable.
- `CPF_TC_PERF_COUNTER_WINDOW_SELECT`, `CPG_TC_PERF_COUNTER_WINDOW_SELECT`, and `CPC_TC_PERF_COUNTER_WINDOW_SELECT` select indexed thread/transaction-counter windows with `ALWAYS` and `ENABLE` controls.
- `CPF_LATENCY_STATS_SELECT`, `CPG_LATENCY_STATS_SELECT`, and `CPC_LATENCY_STATS_SELECT` select latency statistic indexes and expose `CLEAR` and `ENABLE` command bits.
- `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_MASK_HI`, `CP_DRAW_WINDOW_HI`, `CP_DRAW_WINDOW_LO`, and `CP_DRAW_WINDOW_CNTL` describe draw-window filtering and draw/object counting.

`GRBM_PERFCOUNTER0_SELECT` and `GRBM_PERFCOUNTER1_SELECT` select global GRBM counter events and user-defined busy/clean masks for DB, CB, TA, SX, SPI, SC, PA, GRBM, CP, GDS, BCI, RLC, TCP, GE, UTCL2, EA, and RMI. The `GRBM_SE0..3_PERFCOUNTER_SELECT` variants select per-shader-engine events and busy masks for DB/CB/TA/SX/SPI/SC/PA/BCI/RMI/UTCL1/TCP/GL1CC/GL1H/PC/SEDC. `GRBM_PERFCOUNTER0_SELECT_HI` and `GRBM_PERFCOUNTER1_SELECT_HI` extend global busy masks for UTCL1, GL2CC, SDMA, CH, PH, PMM, GUS, GL1CC, and GL1H.

The GE, PA, SPI, PC, SX, GCEA, and GDS selector families share a repeated layout: primary selectors use `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE` or `SPM_MODE`, and per-selector `PERF_MODE` fields; companion `SELECT1` registers usually provide `PERF_SEL2`, `PERF_SEL3`, `PERF_MODE2`, and `PERF_MODE3`. Some later counters have only one selector and mode. This repetition is an important ABI shape for generic performance counter setup code.

## SQ, SQG, and Thread Trace

The SQ/SQG section defines:

- `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT` and `SQG_PERFCOUNTER0_SELECT` through `SQG_PERFCOUNTER7_SELECT`, each with event selection and counter mode fields.
- `SQG_PERFCOUNTER_CTRL` and `SQ_PERFCOUNTER_CTRL`, which gate counters by shader stage (`PS`, `GS`, `HS`, `CS`) and can disable performance collection for specific ME/pipe combinations.
- `SQG_PERFCOUNTER_CTRL2` and `SQ_PERFCOUNTER_CTRL2`, which provide force-enable and VMID enable masks.
- `SQG_PERF_SAMPLE_FINISH`, which exposes sample-finish status.

Thread trace registers are more stateful:

- `SQ_THREAD_TRACE_BUF0_BASE/SIZE` and `SQ_THREAD_TRACE_BUF1_BASE/SIZE` define trace buffer base low bits, high base bits, and size fields.
- `SQ_THREAD_TRACE_CTRL` selects tracing mode, all-VMID mode, GL1 performance capture, interrupt enable, double buffering, high-water/low-water behavior, SPI/SQ stall behavior, utility timer, wave-start mode, real-time frequency, sync-count markers/draws, auto-flush behavior, and draw event enable.
- `SQ_THREAD_TRACE_MASK` selects SIMD, WGP, shader array, wave type include mask, and non-detail shader-data exclusion.
- `SQ_THREAD_TRACE_TOKEN_MASK` selects token exclusion, execution token inclusion, BOP event token inclusion, register inclusion/exclusion, instruction exclusion, and full register detail.
- `SQ_THREAD_TRACE_WPTR` reports the trace write pointer and active buffer id.
- `SQ_THREAD_TRACE_STATUS` reports finish-pending, finish-done, write-error, busy, and owner VMID state.
- `SQ_THREAD_TRACE_STATUS2` reports full buffers, lost packets, buffer issue status, buffer issue, and write-buffer full state.
- Draw, marker, HP3D, and dropped counters expose full 32-bit count fields.

These definitions are sensitive because trace setup crosses memory allocation, VMID ownership, interrupt behavior, and GPU pipeline stalling. The header does not enforce alignment, buffer lifetime, ownership, or sequencing; it only provides field positions.

## GCEA, SX, and GDS Tail

The tail of this chunk covers GCEA performance selectors and mode/config registers, then SX and GDS selector families. `GCEA_PERFCOUNTER2_SELECT`, `GCEA_PERFCOUNTER2_SELECT1`, and `GCEA_PERFCOUNTER2_MODE` support four event selectors with compare modes and compare values. `GCEA_PERFCOUNTER0_CFG` and `GCEA_PERFCOUNTER1_CFG` provide range-style `PERF_SEL`/`PERF_SEL_END`, performance mode, enable, and clear bits. `GCEA_PERFCOUNTER_RSLT_CNTL` selects which performance counter result is controlled and provides start/stop trigger masks, enable-any, clear-all, and stop-all-on-saturate bits.

The SX and GDS selectors follow the common event/mode shape. `SX_PERFCOUNTER0/1_SELECT` include two event selectors plus modes, while `SX_PERFCOUNTER2/3_SELECT` define one event selector and mode. `SX_PERFCOUNTER0/1_SELECT1` add selectors two and three. `GDS_PERFCOUNTER0..3_SELECT` each expose `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE1`, and `PERF_MODE`. This chunk ends immediately before `GDS_PERFCOUNTER0_SELECT1`, so the final merged file report must connect this section with the following chunk for the remaining GDS selector companion registers.

## Control Flow and State Behavior

There is no C control flow in this header. The runtime behavior occurs in AMDGPU/KFD/display consumers that include this generated ASIC header and write/read the associated MMIO registers through SOC15 register helpers.

The persistent state affected by these macros is hardware state:

- Cache/arbitration controls persist in GL2C/GL2A/GL1H registers until reset or reprogramming.
- Performance selectors, filters, monitor state, latency selectors, and draw windows persist while profiling is active and determine which hardware events increment data counters.
- Counter data registers hold hardware-maintained values and may require explicit clear/start/stop sequencing depending on the owning block.
- Thread trace buffer base/size/control/mask/token settings persist for a trace session; status and write-pointer registers reflect asynchronous hardware progress.
- Clear, load, start, stop, enable, request, and status bits are command-like or latch-like even though the header exposes them as plain masks.

Because these macros are raw field constants, the header cannot validate legal event IDs, valid mode values, buffer alignment, VMID ownership, polling order, counter read ordering, or whether a register is safe to program while the block is busy.

## Dependencies and Integration Points

This chunk depends on the generated AMD register-header naming convention:

- `gc_11_0_3_offset.h` supplies the matching `reg...`/`mm...` register addresses for these field names.
- A matching default header supplies reset/default values for many of the same registers.
- AMDGPU register helpers in `soc15.h`/related headers consume `__SHIFT` and `_MASK` definitions through `REG_SET_FIELD` and `REG_GET_FIELD`.

Direct GC 11.0.3 include users in this source tree include:

- `drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`, which includes the offset and mask headers for GC 11.0.3-specific GFX/RAS handling.
- `drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`, which includes the same ASIC headers for GFXHUB programming.
- `drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`, which uses GC 11.0.3 register definitions for IMU/RLC programming tables.

The specific performance and trace macro families are also part of the broader AMDGPU performance/debug ABI. Sibling generation files (`gc_11_0_0_sh_mask.h`, GC 9/10/12 headers, and older GCA headers) contain similar names with generation-specific layouts. Consumers must pair GC 11.0.3 masks with GC 11.0.3 offsets and defaults; similar register names from another ASIC generation are not interchangeable.

## Risks

- A wrong shift or mask can program the wrong hardware bit. In this chunk, the likely failures include corrupt performance captures, missed or excessive profiling interrupts, forced stalls, broken trace buffer ownership, cache/arbitration regressions, or invalid counter reads.
- Repeated selector families are typo-prone. GE, PA, SPI, PC, SQ, SQG, SX, GDS, and GRBM selectors use near-identical layouts, but there are deliberate variations in field names, number of selectors, busy-mask coverage, and high-selector registers.
- Status and command fields look like ordinary bitfields. Misusing `CLEAR`, `START`, `STOP`, `LOAD`, `ENABLE`, `FINISH_*`, buffer-full, or clear-all bits can drop diagnostic data or leave profiling hardware in an active state.
- Thread trace fields can affect execution. Stall-enable, interrupt-enable, double-buffer, high-water, low-water, auto-flush, and VMID fields must be sequenced with buffer allocation and ownership rules outside this header.
- Performance counters are not self-describing. Event selector values are hardware-defined; compile success only proves the bit layout exists, not that the selected event is legal or meaningful.
- Cross-generation copy/paste is risky. The same macro families appear in many GC/GCA headers with different masks, extra fields, or older field names such as `PERFCOUNTER_SELECT` instead of `PERF_SEL`.

## Test and Validation Signals

Useful validation for this chunk is mostly compile-time and hardware-integration level:

- Build coverage for GC 11.0.3 AMDGPU sources that include `gc/gc_11_0_3_sh_mask.h`; this catches missing, renamed, or syntactically invalid macros.
- Static checks can verify that every field has a matching `__SHIFT` and `_MASK`, repeated selector families remain internally consistent, and masks do not overlap unexpectedly within a register.
- Register programming tests should exercise performance monitor enable/disable, CP latency statistics selection/clear, draw-window filters, TCP filter enable/value pairing, and low/high counter reads.
- Profiling/debug tooling should validate that SQ/SQG/SX/GDS/GCEA/GRBM event selection produces expected counter movement under known workloads.
- Thread trace validation should allocate trace buffers, program base/size/control/masks, start and finish trace capture, poll `SQ_THREAD_TRACE_STATUS*`, inspect write pointers, and verify dropped/error counters under both normal and near-full-buffer conditions.
- Reset, suspend/resume, and GPU recovery tests should confirm that persistent performance/debug/cache-control registers are restored or cleared by the owning driver paths and do not leak stale profiling state.

## Unresolved Cross-Chunk References

This chunk starts after the `GL2C_CM_CTRL2` definition began in an earlier chunk and ends in the middle of the GDS performance selector family, immediately before `GDS_PERFCOUNTER0_SELECT1`. Later chunks should cover the remaining GDS selector companion registers and any subsequent performance/debug definitions. The final per-file report should merge this with adjacent chunks to describe the full `gc_11_0_3_sh_mask.h` generated header, its include guard, all address blocks, and complete repeated register families.
