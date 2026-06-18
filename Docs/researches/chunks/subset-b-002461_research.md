# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h lines 29912-32520

## Purpose

This chunk is generated AMD GC 10.1.0 register bitfield metadata. It contains no executable C code; it publishes preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU and AMDKFD code to compose, update, and decode 32-bit MMIO register values. The matching register addresses and base indices live in `gc_10_1_0_offset.h`.

The selected range starts at the end of the GL2 cache/control block, covers a large graphics performance-counter decode area, and ends in the first RLC streaming performance monitor accumulator controls. Although this repository subtree is named `ceph-client`, this file is GPU driver hardware metadata, not filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or callbacks in this range. The exposed API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for the same field.
- Consumers pair these with `mm<REGISTER>` and `mm<REGISTER>_BASE_IDX` macros from `gc_10_1_0_offset.h`, then use AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and bitfield helper patterns.

Major register groups in this chunk:

- GL2 cache/load-balancer and routing controls: `GL2C_LB_CTR_CTRL`, `GL2C_LB_DATA0` through `GL2C_LB_DATA3`, `GL2C_LB_CTR_SEL0/1`, `GL2A_ADDR_MATCH_*`, `GL2A_PRIORITY_CTRL`, `GL2A_CTRL`, and `GL2_PIPE_STEER_0/1`. These define load-balancer counter start/load/clear bits, counter data words, counter event selectors and dividers, GL2A address-match masks and limits, return-arbitration/stay-on-burst behavior, and pipe-to-channel steering fields.
- Perf counter value registers in `addressBlock: gc_perfddec`: low/high counter data registers for command processor blocks (`CPG`, `CPC`, `CPF`), `GRBM`, `GE`, primitive assembly (`PA_SU`, `PA_SC`, `PA_PH`), shader processor input (`SPI`), shader queue (`SQ`), shader export (`SX`), GDS/GCEA, texture blocks (`TA`, `TD`, `TCP`), GL2/GL1 cache blocks, CHC/CHCG/CHA, color/depth blocks (`CB`, `DB`), RLC, RMI, UTCL1, GCR, GUS, and VM/ATC L2 counter windows. Most value registers expose a full 32-bit `PERFCOUNTER_LO`, `PERFCOUNTER_HI`, or `DATA` field.
- Additional counter address blocks: `gc_gcatcl2pfcntrdec`, `gc_gcvml2prdec`, `gc_gcvml2perfddec`, and `gc_gcatcl2perfddec`, providing ATC L2, GCMC VM L2, and GCVML2 counter data fields.
- Perf counter select/configuration registers in `addressBlock: gc_perfsdec`: `*_PERFCOUNTER*_SELECT`, `*_SELECT1`, and related controls for CPG/CPC/CPF, GRBM and per-SE GRBM, GE, PA, SPI, SQ, SX, GDS, TA/TD/TCP, GL2C/GL2A/GL1C, CHC/CHCG, CB, and DB. Common fields are `PERF_SEL`, `PERF_SEL1`, `CNTR_MODE`, `PERF_MODE`, `PERF_MODE1`, `PERFMON_STATE`, `PERFMON_SAMPLE_ENABLE`, `PERFMON_ENABLE_MODE`, `PERFMON_RING_MODE`, and per-instance filters such as shader engine, shader array, VMID, queue, SIMD, pipe, and pixel pipe selection.
- Command processor draw/perf monitor controls: `CP_PERFMON_CNTL`, `CP_DRAW_OBJECT`, `CP_DRAW_OBJECT_COUNTER`, `CP_DRAW_WINDOW_*`, and `CP_DRAW_WINDOW_CNTL`, which gate or window draw-object-oriented performance measurement.
- Shader queue controls: `SQ_PERFCOUNTER0_SELECT` through `SQ_PERFCOUNTER15_SELECT`, `SQ_PERFCOUNTER_CTRL`, and `SQ_PERFCOUNTER_CTRL2`. These define per-counter event selection plus stage enable bits (`PS`, `VS`, `GS`, `ES`, `HS`, `LS`, `CS`), counter rate, flush behavior, and force enable.
- Color/depth filtering: `CB_PERFCOUNTER_FILTER` selects shader engine/array, VMID, cache action, client, and slice-specific filter fields; DB selectors use dual event selectors and counter/perf modes.
- RLC SPM and accumulator setup: `RLC_SPM_PERFMON_CNTL`, ring base/size, segment sizing, ring read/write pointers, SE/global mux selector address/data pairs, skew and sample-delay registers, accumulator data/control RAM address/data registers, `RLC_SPM_ACCUM_STATUS`, `RLC_SPM_ACCUM_CTRL`, and the beginning of `RLC_SPM_ACCUM_MODE`. These fields define SPM ring layout, sampling interval, mux programming, sampling skew, accumulator state, reset/start/rearm strobes, and automatic accumulation/SPM enable modes.

Field naming is descriptive. `*_LO`/`*_HI` are counter halves; `*_SELECT` programs an event source; `*_SELECT1` typically holds the second event selector and counter mode; `CNTR_MODE` and `PERF_MODE` choose accumulation/sample semantics; `START`, `LOAD`, `CLEAR`, and `Strobe*` fields trigger hardware actions; `DONE`, `OVERFLOW`, `IDLE`, and `IN_PROGRESS` fields expose status; `RESERVED` fields mark bits that should be preserved by read-modify-write consumers unless an ASIC guide says otherwise.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers in AMDGPU and AMDKFD:

1. GFX10/Navi code includes `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
2. Driver paths select a concrete register using the `mm*` offset macro and base index.
3. The code composes values with the field masks and shifts from this header.
4. MMIO helpers read or write the register while firmware, CP/RLC microcode, perf tooling, or debug paths coordinate the actual hardware sequence.

The chunk describes fields needed for perf monitor setup and sampling, but it does not encode event IDs, allowed counter modes, sampling order, polling delays, reset sequencing, interrupt behavior, or locking. Safe ordering around counter clear/load/start, CP draw windows, SPM ring programming, mux selector writes, accumulator start/rearm/reset, and status polling must come from the consuming driver and hardware programming guide.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware state exposed through GC 10.1 registers.

The represented hardware state includes GL2 load-balancer counter values and selectors, GL2A address-match/priority controls, GL2 pipe steering, many 64-bit performance counters exposed as low/high 32-bit registers, event-selector configuration, per-block/per-instance filters, CP draw-window state, SQ stage enable/rate controls, CB/DB filters, and RLC SPM ring and accumulator state. Persistence is hardware-defined: values may remain until explicitly changed, reset by a GPU reset, cleared by power-gating or suspend/resume, or advanced by hardware while counters are running. Several fields are action strobes or live status bits rather than durable configuration.

The macros do not identify access class. A field may be read-only, write-only, write-one-to-clear, self-clearing, sticky, latched, or reserved depending on the register definition. Consumers must preserve unrelated and reserved bits when updating mixed-control registers.

## Dependencies And Integration Points

The direct dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h`, which provides the corresponding `mm*` register offsets and base indices. The same generated register database also includes default-value and enum headers such as `navi10_enum.h`, where perf counter and SPM mode values are defined.

Known include users of the GC 10.1.0 shift/mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_packet_manager_v9.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_v10.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdkfd/kfd_device_queue_manager_v10.c`

Integration points are graphics IP initialization, power management, GPU reset/recovery, KFD queue setup, developer/debug register access, performance counter programming, profiling, RLC SPM streaming, shader stage and VMID filtering, draw-window measurement, and hardware validation tooling. This chunk is especially relevant to perf event collection because it provides both counter data register definitions and selector/control fields for most GFX pipeline blocks.

## Risks And Edge Cases

- Header/offset mismatch is the main correctness risk. Pairing `gc_10_1_0_sh_mask.h` with a different GC offset header can compile while addressing the wrong register or field.
- The macros are untyped constants. A wrong event selector, shift, mask, or register name can silently program an unintended block, counter, shader engine, VMID, SIMD, queue, pipe, or pixel pipe.
- Performance counter registers are sequencing-sensitive. Counters often require clear/load/start/stop ordering, clock/power availability, shader-stage filtering, VMID/context selection, and stable read ordering for 64-bit low/high values.
- SPM programming is particularly stateful. Ring base/size, segment sizing, mux selector address/data writes, read/write pointers, skew/sample-delay fields, accumulator RAM programming, and start/rearm/reset strobes must be coordinated with `RLC_SPM_ACCUM_STATUS` bits such as `AccumDone`, `SpmDone`, `AccumOverflow`, `SequenceInProgress`, `FinalSequenceInProgress`, `AllFifosEmpty`, and `FSMIsIdle`.
- Full-width `0xFFFFFFFFL` masks are common for counter data and selector payloads. Consumers must avoid treating every full-width field as safe to write; many full-width registers are readback data, indirect data windows, or hardware-owned counters.
- Reserved fields appear throughout. Direct writes that do not preserve reserved bits can create ASIC-specific failures that only show up on particular SKUs, power states, or firmware revisions.
- Block-local filters can make tests look falsely idle. A counter may remain zero because the selected shader stage, VMID, SE/SA, SIMD, queue, pipe, client, or slice filter does not match current workload placement.
- The chunk boundary is artificial. It starts after `GL2C_CTRL3` and ends in `RLC_SPM_ACCUM_MODE`; adjacent chunks are needed for a complete per-file view.

## Test Signals

Useful validation is mostly build, static, and hardware/profiling coverage:

- Build coverage for AMDGPU and AMDKFD files that include `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h`.
- Generated-header checks that each `__SHIFT` has a matching `_MASK`, each mask is aligned to its shift, and register names match entries in `gc_10_1_0_offset.h`.
- Static checks for non-overlapping fields within each register except documented aliases or full-width data fields.
- Perf counter smoke tests that clear/load/start counters, run known graphics and compute workloads, stop/read counters, and verify low/high counter behavior is monotonic or otherwise plausible.
- Filter coverage across shader stages, VMIDs, queues, shader engines/arrays, SIMDs, pixel pipes, cache clients, and CB/DB filters to catch field-shift or mask mistakes that only appear under non-default placement.
- RLC SPM tests that configure ring base/size, mux selections, sample interval, segment size, accumulator mode, and start/rearm/reset sequences, then poll status bits for completion, overflow, empty FIFOs, and idle state.
- Reset, suspend/resume, runtime power-management, and GPU recovery tests while perf counters or SPM are active, because hardware-owned counter and ring state can be lost, stale, or require reinitialization.
- Regression indicators include zero or saturated counters for active workloads, counter overflows at unexpected rates, profiler event misattribution, SPM ring pointer stalls, accumulator overflow/done never asserted, GPU hangs during perf collection, or failures isolated to specific GFX10/Navi SKUs.
