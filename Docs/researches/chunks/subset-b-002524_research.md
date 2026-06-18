# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_offset.h lines 7490-9939

## Purpose

This chunk is generated AMD GC 11.0.3 register offset metadata. It contains no executable C logic; it exports preprocessor constants that name MMIO/register-file offsets and paired `_BASE_IDX` values for the GC hardware IP block. The register names in this range are consumed by AMDGPU, GFXHUB, IMU, MES, KFD/debug, performance-monitoring, reset, and power-management code through SOC15 register helpers.

The selected range starts in the tail of a base GC graphics register span and then covers several address blocks:

- Base GC register span from `regVGT_NUM_INSTANCES` through `regSPI_ATTRIBUTE_RING_SIZE`: draw/geometry setup, primitive assembly, screen/trap controls, thread-trace userdata, GDS direct/atomic/streamout registers, and SPI configuration/throttling/attribute-ring controls.
- `gc_cprs64dec` at base `0x32000`: RS64 command-processor registers for MES, MEC, and graphics front-end firmware engines.
- `gc_gl1dec`, `gc_chdec`, `gc_gl2dec`, and `gc_gl1hdec`: cache, channel, burst, arbitration, retry, and soft-reset registers for GL1/GL1C/GL1H/GL2/CH front-end cache and transport blocks.
- `gc_perfddec` at base `0x34000`: performance counter data/readback registers, usually low/high counter halves and latency-stat data.
- `gc_perfsdec` at base `0x36000`: performance counter select/config/control registers, RLC streaming performance monitor controls, SQ thread-trace buffer controls, and GDFLL EDC hysteresis select/status.
- `gc_gdfll_gdfll_dec` and `gc_gdfll_se_gdfll_dec`: global and shader-engine GDFLL EDC hysteresis control/status registers.
- The final line begins the next `gc_grtavfs_grtavfs_dec` block, but no complete GRTAVFS register pair is included in this chunk.

Although the repository path is under `ceph-client`, this file is GPU driver hardware metadata and is unrelated to Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, or direct I/O operations in this range. The API is the generated macro namespace:

- `reg<NAME>` maps a hardware register to a numeric offset such as `0x224d`, `0x2800`, `0x3c80`, or `0x48e9`.
- `reg<NAME>_BASE_IDX` gives the register base-index selector used by SOC15-style helpers; every macro in this chunk uses base index `1`.
- Consumers commonly use generated aliases from the same offset header family, such as `mm<NAME>` or `ix<NAME>`, together with bit definitions from `gc_11_0_3_sh_mask.h`.

Major register groups in this chunk:

- `VGT_*` and `GE_*`: instance counts, tessellation factor ring size and memory base, hull-shader off-chip parameters, vertex index bounds, primitive instance base, graphics engine control, user VGPR registers/enables, stereo control, primitive allocation, GS fast-launch workgroup dimensions, and GS output primitive type.
- `PA_*`: line stipple state, screen extent min/max values, and P3D/HP3D/general trap-screen enable, horizontal/vertical position, occurrence, and count registers.
- `SQ_THREAD_TRACE_USERDATA_*` and later `SQ_THREAD_TRACE_*`: shader thread-trace userdata slots, trace buffer base/size pairs, trace control/masks, write pointer, status, draw/marker counters, and dropped-counter telemetry.
- `GDS_*`: GDS read/write windows, burst access, atomics, GWS resource state, ordered-append counters/addressing, streamout counters, and GS scratch-style data registers.
- `SPI_*`: shader processor interpolator/global SPI configuration, wave limits, GS throttling, attribute ring base/size, and performance-counter select/config entries.
- `CP_MES_*`, `CP_MEC_*`, and `CP_GFX_RS64_*`: RS64 firmware program-counter and trap-vector start registers, interrupt enable/pending/status data, instruction pointers, machine CSRs (`MSTATUS`, `MEPC`, `MCAUSE`, `MBADADDR`, `MIP`, `MIE`, `MISA`, vendor/arch/impl/hart IDs), cycle/time/retired-instruction counters, process quantum and doorbell controls, GP registers, local/data/instruction/scratch apertures, cache operation controls, perfcount controls, interrupt data slots, and repeated data-cache aperture base/mask/control windows.
- `GL1*`, `GL2*`, `CH*`, and `CHA/CHC/CHCG/CHI`: cache/channel arbitration controls, burst masks/controls, status, retry, clock-gating overrides, virtual-channel enable, GL2 address-match controls, writeback/invalidate and soft-reset controls, command-merge controls, load-balancer counter controls/data/selects, and response throttling.
- `*_PERFCOUNTER*_LO`/`HI` under `gc_perfddec`: sampled counter data for CP, GRBM, GE1/GE2, PA, SPI, PC, SQ/SQG, SX, GCEA, GDS, TA, TD, TCP, GL2, GL1, CH, CB, DB, RLC, RMI, GCR, UTCL1, CHA, and GUS blocks.
- `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, filters, modes, and result controls under `gc_perfsdec`: event-selection and configuration registers that feed the matching `gc_perfddec` readback counters.
- `RLC_SPM_*`: RLC streaming performance monitor ring base/size/pointers, segment threshold/size, global and shader-engine mux selection address/data windows, accumulator data/control/status registers, pause/status/mode, graphics-clock counts, RSPM request/return mailboxes, command/ack, and GPU IOV perf-count access windows.
- `GDFLL_*EDC_HYSTERESIS_*`: electrical-design-current hysteresis controls and status for global and shader-engine GDFLL blocks.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by code that includes the generated header and performs register access:

1. A GC 11.0.3 driver path includes `gc_11_0_3_offset.h`, usually with `gc_11_0_3_sh_mask.h`.
2. The path chooses a register macro for direct MMIO, SOC15 indexed access, register-list save/restore, golden-register programming, firmware setup, or performance-monitoring configuration.
3. The offset and base index are passed through helpers such as `SOC15_REG_OFFSET`, `SOC15_REG_ENTRY`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, or `WREG32`.
4. The actual ordering, synchronization, power-state checks, firmware ownership, and read/modify/write behavior live in the consuming AMDGPU paths and hardware programming rules, not in this generated file.

The chunk names registers used during graphics setup, MES/MEC/GFX firmware control, trap/debug capture, cache and fabric control, performance-counter programming, streaming perf sampling, and EDC hysteresis. It does not describe when those registers may be safely touched, which registers are read-only, which bits are self-clearing, or which firmware owns a register at runtime.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It is compile-time metadata.

The represented hardware state is broad:

- Draw and geometry state includes instance counts, vertex bounds, transform-feedback/tessellation memory addresses, and GE/VGT/SPI programming that can affect submitted draws.
- Trap, thread-trace, and SQ-related state includes user payload registers, trace buffers, masks, write pointers, statuses, draw/marker counters, and dropped-trace telemetry.
- GDS and streamout state includes memory access windows, atomic source/destination operands, ordered-append counters, GWS allocation counters, and streamout written/needed primitive counters.
- RS64 CP/MES/MEC/GFX state includes firmware PC/vector/counter/CSR values, interrupt pending/data state, doorbell routing, local aperture mappings, scratch/instruction/data-cache aperture setup, and firmware-visible GP registers.
- GL1/GL2/CH state includes arbitration, burst throttling, retry/status, writeback/invalidate, soft-reset, address-match, response-throttle, and clock-gating override values.
- Performance state includes both selectable event sources and readback counters across many GC subblocks, plus RLC SPM ring state, mux selections, accumulator RAM windows, request/response mailboxes, pause/status, and clock-count registers.
- GDFLL EDC hysteresis state controls and reports droop/current-related hysteresis behavior for global and shader-engine domains.

Persistence is hardware-defined. Some values are programmed during initialization or workload setup and survive until GPU reset, suspend/resume, power-gating, or explicit reprogramming. Others are volatile live counters, pointers, firmware CSRs, interrupt payloads, status bits, reset strobes, indirect windows, or hardware-owned fields that can change while command processors and shader engines run. The macros provide addresses only; they do not encode ownership or lifetime.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_3_sh_mask.h`, which supplies field shifts and masks for the registers named here. Consumers must keep the offset and mask headers from the same GC generation together.

Observed include users in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/imu_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v11_0_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c`

Related GC 11.0.3 firmware declarations appear in `gfx_v11_0.c`, `mes_v11_0.c`, and `imu_v11_0.c` for PFP, ME, MEC, RLC, MES, MES2/MES1, and IMU firmware blobs. Those firmware paths are natural integration points for this chunk's CP/MES/MEC/GFX RS64 control registers and RLC/SPM/performance state.

Key integration surfaces:

- GFX 11.0.3 bring-up and reset code that programs golden registers, initializes rings, configures GE/VGT/SPI state, and manages CP firmware engines.
- MES/MEC scheduling and queue-management paths that rely on RS64 program counters, trap vectors, doorbells, local apertures, scratch state, and pending interrupt registers.
- GFXHUB and memory-system code that touches GL1/GL2/cache/channel state or uses address-match and invalidation controls during VM/cache setup.
- Debug, trap, KFD, and profiling flows that consume SQ thread trace, GDS, PA trap screen, and perf counter registers.
- RLC SPM and perfmon infrastructure that programs select registers under `gc_perfsdec`, reads counter data under `gc_perfddec`, and manages SPM rings/muxes/accumulators.
- Power, reliability, and validation flows that observe or tune GDFLL EDC hysteresis state.

## Risks And Edge Cases

- Header generation mismatches are the highest risk. Using `gc_11_0_3_offset.h` with a different generation's `*_sh_mask.h`, firmware path, or register table can compile while targeting the wrong register.
- These constants are untyped preprocessor values. The compiler cannot distinguish a counter select register from a counter data register, an RLC SPM indirect address from data, or a read-only status register from a writable control register.
- Every macro in this chunk has `_BASE_IDX` value `1`; code that assumes base index `0`, bypasses SOC15 helpers, or mixes direct and indexed addressing can silently access the wrong block.
- RS64 CP/MES/MEC/GFX registers are firmware-facing. Reads can observe live firmware state, and writes can corrupt firmware execution, interrupt handling, doorbell routing, aperture mappings, or cache behavior if not sequenced with halt/reset/ownership rules.
- Repeated aperture windows (`CP_MES_DC_APERTURE*`, `CP_MEC_DC_APERTURE*`, `CP_GFX_RS64_DC_APERTURE*`) are easy to index incorrectly. Off-by-one aperture programming can expose the wrong local/data/instruction/scratch address range to firmware.
- Performance counters and RLC SPM registers are stateful. Reprogramming select registers while counters are active, racing ring pointers, or mixing per-SE/global mux selections can produce misleading samples or stall the monitoring path.
- Some registers are live hardware counters split into `LO` and `HI` halves. Readers need rollover-safe sampling and should not assume a single 32-bit read is enough.
- Cache/channel controls such as GL2 writeback/invalidate, soft reset, address-match, and response throttling can affect correctness and performance globally if written outside documented quiescent states.
- GDS direct and atomic windows expose hardware data/control operations rather than ordinary memory. Incorrect access can clobber streamout/GWS/OA state or interfere with running workloads.
- Trap-screen, thread-trace, and shader debug registers may be per-shader-engine, privilege-sensitive, or workload-sensitive. Sampling while waves execute can produce transient or inconsistent data unless the caller coordinates with debug/trap mechanisms.
- The chunk boundary is artificial: it starts after earlier VGT/GE register definitions and ends immediately after the next address block header. Adjacent chunks are needed for the complete file-level map.

## Test Signals

Useful validation is mostly build coverage, generated-header consistency, and hardware/runtime smoke coverage:

- Compile AMDGPU with GC 11.0.3 support and ensure `imu_v11_0_3.c`, `gfx_v11_0_3.c`, and `gfxhub_v3_0_3.c` include this header without macro conflicts.
- Generated-header checks that every `reg*` macro in this range has a matching `_BASE_IDX` macro, all base indices are intentional for the address block, and companion field definitions exist where the register has named fields in `gc_11_0_3_sh_mask.h`.
- Register-list/golden-register tests that verify `SOC15_REG_OFFSET` and `SOC15_REG_ENTRY` resolve expected offsets for GE/VGT/SPI, CP RS64, GL1/GL2/CH, RLC SPM, and perf-counter registers on GC 11.0.3 ASICs.
- Firmware bring-up tests for PFP/ME/MEC/RLC/MES/IMU that cover RS64 program-counter/vector setup, interrupt pending/data paths, doorbell controls, and local aperture programming.
- Graphics and compute workload smoke tests that exercise VGT/GE/SPI draw setup, GDS/streamout counters, and GWS/OA resources while checking for hangs, malformed draws, or unexpected protection faults.
- SQ thread-trace and profiling tests that allocate trace buffers, program masks/control registers, run known workloads, and verify write pointers, status, draw/marker counters, and dropped counters are plausible.
- Perfmon/SPM tests that program select registers, read low/high data pairs with rollover handling, configure RLC SPM ring/mux/accumulator state, and confirm counters advance under targeted workloads.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests that verify volatile RS64, cache, perfmon, and GDFLL/EDC state is restored or intentionally reset.
- Regression signals include invalid firmware PCs or pending interrupts after init, stuck SPM ring pointers, zero or saturated performance counters under load, trace dropped counters rising unexpectedly, cache invalidation timeouts, GDS/streamout counter mismatches, or failures limited to GC 11.0.3 hardware.
