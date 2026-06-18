# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_sh_mask.h lines 27319-30049

## Purpose

This chunk is generated AMD GC 11.0.0 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, debug, profiling, and power/reset paths to compose or decode 32-bit graphics-core register values. The corresponding register addresses are provided by the companion GC 11.0.0 offset header.

The selected range starts in primitive-assembler/screen-space controls, then covers SQ/SQC trace and cache control, GDS and streamout accounting, SPI setup/throttle controls, a large RS64 command-processor block for MES/MEC/GFX microcontrollers, GL1/CH/GL2 cache and arbitration controls, GL1H controls, and the beginning of the GC performance counter data block. Although the repository root is named `ceph-client`, this source file is AMD GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, allocations, locks, or callbacks in this range. The only exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field in a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for that field.
- Consumers combine these field macros with matching `reg*` or `mm*` offset symbols and helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.

Major register families in this chunk:

- PA/SC screen and trap registers: `PA_SC_SCREEN_EXTENT_MIN_0`, `PA_SC_SCREEN_EXTENT_MAX_0`, `PA_SC_SCREEN_EXTENT_MIN_1`, `PA_SC_SCREEN_EXTENT_MAX_1`, and P3D/HP3D/general `PA_SC_*TRAP_SCREEN*` registers define 16-bit X/Y extents, trap X/Y coordinates, trap occurrence counters, and pre-shader trap enable/force bits.
- SQ/SQC and texture-address setup: `SQ_THREAD_TRACE_USERDATA_0` through `_7` carry full-width thread-trace userdata, `SQC_CACHES` selects instruction/data cache invalidation targets and exposes completion, and `TA_CS_BC_BASE_ADDR(_HI)` defines a compute-shader border-color base address split across low and high parts.
- DB/GDS/streamout state: `DB_OCCLUSION_COUNT[0-3]_{LOW,HI}` expose query counters; `GDS_RD_*` and `GDS_WR_*` provide direct and burst read/write data windows; `GDS_ATOM_*` defines atomic operation parameters and return data; `GDS_GWS_RESOURCE*` and `GDS_OA_*` expose global-wave-sync and ordered-append resource state; `GDS_STRMOUT_DWORDS_WRITTEN_*`, `GDS_GS_*`, and `GDS_STRMOUT_PRIMS_*` expose streamout and geometry-shader accounting.
- SPI controls: `SPI_CONFIG_CNTL`, `SPI_CONFIG_CNTL_1`, `SPI_CONFIG_CNTL_2`, `SPI_WAVE_LIMIT_CNTL`, `SPI_GS_THROTTLE_CNTL1`, `SPI_GS_THROTTLE_CNTL2`, `SPI_ATTRIBUTE_RING_BASE`, and `SPI_ATTRIBUTE_RING_SIZE` define shader-processor input arbitration, event enable bits, power-save disables, vertex/PS timing, wave granularity, GS/PS throttling, and attribute-ring base/size.
- `addressBlock: gc_cprs64dec`: RS64 command-processor registers for MES, MEC, and GFX engines. This includes program-counter starts, trap/vector addresses, interrupt enables/status, instruction pointers, scratch/indexed scratch windows, RISC-V-like status/cause/bad-address/cycle/time/ISA/vendor/hart registers, cache base and invalidate controls, process quantum, doorbell controls, general-purpose registers, local data/instruction/scratch apertures, performance counter controls, pending interrupts, interrupt data slots 16-31, and DC aperture base/mask/control windows 0-15.
- GFX RS64 dual-engine state: `CP_GFX_RS64_*` repeats interrupt, local aperture, dcache, perfcount, pending-interrupt, GP, instruction-pointer, and DC aperture fields for engine selectors `0` and `1`, with `CP_GFX_CNTL` selecting/configuring the active graphics engine.
- `addressBlock: gc_gl1dec`: `GL1_DRAM_BURST_MASK`, `GL1_ARB_STATUS`, `GL1I_GL1R_REP_FGCG_OVERRIDE`, `GL1C_STATUS`, and `GL1C_UTCL0_*` cover GL1 arbitration/burst behavior, fine-grain clock-gating overrides, GL1C stall/busy status, UTCL0 VM response and invalidation controls, fault/retry/PRT detection, and retry counts.
- `addressBlock: gc_chdec`: `CH_ARB_CTRL`, `CH_DRAM_BURST_*`, `CHA_CHC_CREDITS`, `CHA_CLIENT_FREE_DELAY`, `CHI_CHR_REP_FGCG_OVERRIDE`, `CH_VC5_ENABLE`, `CHC_*`, and `CHCG_*` define channel arbitration, memory/IO burst behavior, credits, client-free delay, clock-gating overrides, status/stall counters, and channel-cache controls.
- `addressBlock: gc_gl2dec`: `GL2C_CTRL`, `GL2C_CTRL2`, `GL2C_CTRL3`, and `GL2C_CTRL4` define L2 cache sizing, FIFOs, hashing, priority, writeback, metadata, coherency, read/write, MGCG, and EA/NACK behavior. `GL2C_WBINVL2`, `GL2C_SOFT_RESET`, `GL2C_CM_*`, `GL2C_LB_*`, `GL2C_DISCARD_STALL_CTRL`, and `GL2A_*` cover writeback-invalidate done state, halt-for-reset, compression-manager settings, L2 bank/load-balance counters, discard throttling, address-match controls, priority disabling, and response throttling.
- `addressBlock: gc_gl1hdec`: `GL1H_ARB_CTRL`, `GL1H_GL1_CREDITS`, `GL1H_BURST_MASK`, `GL1H_BURST_CTRL`, and `GL1H_ARB_STATUS` cover GL1 hub arbitration, credits, burst sizing, clock-gating disable bits, and busy/illegal-request status.
- `addressBlock: gc_perfddec`: the chunk begins the performance data decode block with `CPG`, `CPC`, `CPF`, `GRBM`, per-SE GRBM, and `GE1` low/high counter and latency-stat data registers.

Important field themes include `ADDR`, `BASE`, `MASK`, `CNTL`, `STATUS`, `ACTIVE`, `RESET`, `HALT`, `STEP`, `INSTR_PNTR`, `INT`, `PENDING_INTERRUPT`, `INVALIDATE_*`, `*_COMPLETE`, `CACHE_POLICY`, `VMID`, `APERTURE`, `DOORBELL`, `PRIORITY`, `CREDIT`, `BUSY`, `STALL`, `FAULT_DETECTED`, `RETRY_DETECTED`, `ENABLE`, `SIZE`, `DATA`, `COUNTER`, and full-width `0xFFFFFFFFL` payload/counter windows.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by include users and hardware:

1. GC 11 code includes this shift/mask header together with the matching GC 11 offset header.
2. Driver code chooses a concrete register offset for the ASIC instance and block.
3. The field macros here are used to pack a new register value, update selected bits with read-modify-write helpers, or decode a value read from hardware.
4. AMDGPU helpers perform the actual MMIO or indirect access while higher-level GFX, KFD, reset, queue, and power-management code provides ordering, locking, timeout, and firmware sequencing.

The RS64 command-processor fields participate in firmware bring-up and recovery sequences: program-counter/vector registers are programmed, instruction and data caches are invalidated or primed, pipe reset/active/halt/step bits are toggled or polled, doorbell controls are configured, and instruction pointers or pending interrupt registers are sampled for diagnostics. In this tree, neighboring GC 11 and GC 12 GFX code references these same families through `SOC15_REG_ENTRY_STR`, `REG_SET_FIELD`, `RREG32_SOC15`, and `WREG32_SOC15` for debug register lists, MEC/MES pipe reset, cache invalidation, firmware memory setup, and hang analysis.

The cache and memory-system registers describe control surfaces rather than procedures. GL1/CH/GL2 users must decide when it is safe to halt, reset, invalidate, throttle, alter arbitration/credit settings, or sample status. The `GL2C_WBINVL2__DONE` and RS64 `*_INVALIDATE_*_COMPLETE` bits are examples of completion/status signals that polling code can use after issuing an action bit elsewhere.

## State And Persistence Behavior

This file stores no software state and persists nothing by itself. It describes hardware state in GC 11.0.0 registers.

The represented state includes screen extents and trap counters, thread-trace userdata, SQC cache invalidation target/completion bits, compute border-color base addresses, DB occlusion query counters, GDS direct/burst data windows, GDS atomic operands/results, GWS/OA allocation and queue state, streamout/GS counters, SPI arbitration and throttling controls, RS64 firmware control/status registers, local data/instruction/scratch apertures, command-processor GP registers, per-engine interrupt and pending-interrupt state, GL1/CH/GL2 cache configuration, arbitration and credit settings, TLB/fault/retry status, L2 writeback-invalidate and soft-reset status, L2 load-balance/perf counter data, and GC perfcounter readback values.

Persistence is hardware-defined. Some fields are configuration that remains until reset, GPU reset, suspend/resume, runtime power transition, or explicit reprogramming. Some are action strobes or self-clearing requests, such as invalidation, clear/load/start, reset, halt-for-reset, release-all, or retry increment fields. Some are live hardware-owned status or counters that can change asynchronously while shaders, queues, firmware, or cache pipelines are running. Full-width `DATA`, `COUNTER`, `PERFCOUNTER_LO/HI`, and `*_INT` fields are untyped payload windows here; full-width masks do not imply that writes are safe.

The macros do not encode read-only, write-only, write-one-to-clear, sticky, self-clearing, reserved, privileged, or indirect-only semantics. Consumers must preserve unrelated bits in mixed-control registers and follow the hardware programming guide for ordering, polling, and reset behavior.

## Dependencies And Integration Points

The direct companion dependency is the generated GC 11.0.0 offset header, normally `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_11_0_0_offset.h`, which provides the matching `reg*`, `mm*`, and base-index symbols. Generated default and enum headers may provide reset values or event selectors, but this chunk only defines bit positions and masks.

Important integration points include:

- AMDGPU GFX 11 initialization, reset, hang-dump, and debug paths that include GC 11 register metadata and list command-processor, SQC, GL1/GL2, and performance registers.
- AMDKFD/MES scheduling and queue-management paths, because `CP_MES_*`, `CP_MEC_RS64_*`, doorbell, local aperture, pending interrupt, and process-quantum fields describe firmware-controlled command scheduling state.
- Firmware loading and recovery, where program-counter starts, vector registers, instruction pointers, GP registers, cache invalidation controls, and pipe reset/active/halt bits are used to start, stop, inspect, or recover RS64 firmware engines.
- Cache/TLB and VM integration, especially `SQC_CACHES`, `GL1C_UTCL0_*`, GL2 writeback/invalidate, GL2 coherency/hash/metadata controls, VMID fields, local aperture masks, and fault/retry/PRT status bits.
- GDS and streamout integration in graphics queue packet emission and resource allocation. Similar GDS/GWS macros are used by older/newer GFX paths to program per-VMID GDS/GWS state and packet payloads.
- Profiling and telemetry integration: thread-trace userdata, SPI event enables, GL2 load-balance counters, CP/GRBM/GE perfcounter low/high registers, and latency-stat data registers are read by debugfs, perf, RGP, or internal diagnostics.
- Power and clock-gating policy: `FGCG`/`MGCG` override fields, power-save disable fields, burst/credit/throttle controls, and cache clock-gating modes can interact with SMU policy, golden settings, runtime power management, and ASIC-specific workarounds.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. These constants are untyped and can compile while targeting the wrong GC revision or register block if paired with incompatible offsets.
- The chunk boundaries are artificial. It starts after the first lines of `PA_SC_SCREEN_EXTENT_MIN_0` and ends immediately after `GE1_PERFCOUNTER3_HI`; adjacent chunks are needed for complete source-file coverage.
- RS64 control bits are sequencing-sensitive. Misusing `*_PIPE*_RESET`, `*_ACTIVE`, `HALT`, `STEP`, program-counter, vector, cache-invalidate, or local-aperture fields can leave MES/MEC/GFX firmware stopped, executing from the wrong address, or reporting misleading instruction pointers.
- Cache invalidation fields require polling and timeout handling. `SQC_CACHES__COMPLETE`, RS64 `*_INVALIDATE_*_COMPLETE`, and `GL2C_WBINVL2__DONE` can race with in-flight work if issued without drains, fences, or reset sequencing.
- Full-width register fields are ambiguous. `DATA`, `INT`, `PERFCOUNTER`, `PENDING_INTERRUPT`, GP, scratch, GDS read/write, and aperture base/mask fields may be readback, write payload, hardware-owned status, or action windows depending on the register.
- GDS/GWS/OA registers mix allocation state, queue head state, counters, and action bits such as `RELEASE_ALL`; an incorrect write can release resources or corrupt synchronization visible to graphics or compute queues.
- Address, base, mask, and aperture fields are alignment- and unit-sensitive. Splitting addresses across low/high registers, using field masks as byte masks, or ignoring implicit address shifts can place firmware, scratch, border color, GDS, or local apertures incorrectly.
- GL1/CH/GL2 cache and arbitration knobs affect global memory-system behavior. Wrong credit, burst, priority, coherency, hash, volatile, metadata, NACK, or force-miss settings can cause severe performance regressions, stale data, replay storms, GPU hangs, or failures only under specific workloads.
- Fault and retry bits in `GL1C_UTCL0_STATUS` and retry counters are live status. Tests must tolerate transitions and clear/observe semantics rather than assuming a stable snapshot.
- Reserved, unused, and chicken-bit fields appear throughout the chunk. Driver code should preserve such bits unless an ASIC-specific workaround explicitly requires changing them.
- Perfcounter low/high pairs are not necessarily atomic. Readers need a stable sampling method, especially for counters that can roll over between `LO` and `HI` reads.

## Test Signals

Useful validation is mostly build, generated-header consistency, hardware smoke, reset, and profiling coverage:

- Build GC 11 AMDGPU, AMDKFD, KFD/MES, and SMU-adjacent code that includes `gc_11_0_0_sh_mask.h` with the matching offset header.
- Generated-header checks that every field has a `__SHIFT` and `_MASK`, masks align with shifts, fields for each register do not overlap except documented aliases/reserved fields, and register names in this slice exist in the GC 11 offset header.
- RS64 firmware bring-up tests that program MES/MEC/GFX program-counter/vector registers, invalidate/prime caches, toggle pipe reset bits, poll active/halt/instruction-pointer state, and verify firmware queues accept work after reset and resume.
- MES/KFD queue tests that exercise doorbell setup, process quantum, pending-interrupt handling, local scratch/data/instruction apertures, queue preemption, eviction/restore, and GPU reset recovery.
- Cache and VM tests that issue SQC invalidations, GL2 writeback/invalidate, GL1 UTCL0 invalidation/fault/retry paths, and workloads that stress VM faults, PRT, retry/XNACK-like behavior, and coherency between shader, CP, and memory clients.
- GDS/streamout tests that allocate GDS/GWS/OA resources, issue atomics and streamout/GS workloads, verify counters/readback data, and ensure resource release/reset paths do not leak or corrupt per-VMID state.
- Graphics pipeline tests that vary PA/SC extents/trap screen behavior, occlusion queries, SPI attribute-ring sizing, wave limits, GS throttling, and shader trace userdata collection.
- Profiling tests that enable thread trace and performance counters, sample CP/GRBM/GE/GL2 low/high pairs, and compare monotonicity or workload sensitivity against known workloads.
- Reset, suspend/resume, runtime power-gating, and GPU recovery tests while graphics/compute queues and profiling are active, because RS64 state, GDS counters, cache configuration, and perfcounter state can be lost or become stale.
- Regression indicators include MES or MEC firmware failing to leave reset, stuck instruction pointers, incomplete cache invalidation, unexpected GL1/GL2 busy or stall bits, increased VM fault/retry status, GDS/GWS deadlocks, nonsensical performance counters, or failures isolated to GC 11 hardware.
