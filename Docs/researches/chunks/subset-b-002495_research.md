# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_sh_mask.h lines 47859-49396

## Purpose

This chunk is generated AMD GC 10.3.0 register bitfield metadata. It contains no executable C code; it exports preprocessor `__SHIFT` and `_MASK` constants used by AMDGPU, AMDKFD, SDMA, and SMU/PM code to compose and decode MMIO register values for this graphics IP generation. The matching register offsets and base-index macros are in `gc_10_3_0_offset.h`.

The selected range covers the tail of the RTAVFS tuning/status register block, a small `spiind` block selector, shader queue (`sqind`) debug and wave-state registers, SQ interrupt payload layouts, and the full `didtind` Dynamic Inductive Droop Throttling / Electrical Design Current control tables for SQ, DB, TD, and TCP blocks. Although the repository path is under `ceph-client`, this file is GPU driver hardware metadata, not filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, memory allocations, or direct I/O operations in this range. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit for a hardware register field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register bit mask for that field.
- Consumers pair these macros with `mm<REGISTER>`/`ix<REGISTER>` address macros from generated offset headers and register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, indirect register accessors, and `REG_GET_FIELD`/`REG_SET_FIELD`-style bit helpers.

Major register groups in this chunk:

- `RTAVFS_REG160` through `RTAVFS_REG165`: real-time adaptive voltage/frequency scaling style fields. They define CPO average divider slots, proportional/integral gains, voltage code thresholds, binary-search and hardware-calibration enables, FSM state, guard-band values, and ripple-counter readback.
- `SA_WGP_BLK_ID`: `spiind` selector fields for block ID, WGP side, and shader-array ID. This is used to target per-WGP/per-SA indexed state.
- `SQ_DEBUG`, `SQ_DEBUG_STS_GLOBAL`, `SQ_DEBUG_STS_GLOBAL2`, and `SQ_DEBUG_STS_LOCAL`: shader queue debug and busy/occupancy state, including single-memory-operation debug mode, global busy flags, interrupt-message busy status, graphics/compute FIFO levels, wave levels by SA, and block-local busy bits for SQ, instruction scheduler, instruction buffer, arbiter, export, broadcast-message, and VM subunits.
- `SQ_WAVE_*`: wavefront inspection and state-register layouts. The range includes active/valid wave-slot masks, wave mode bits, status bits, trap status, legacy and split hardware IDs, GPR/LDS allocation fields, instruction-buffer counters, program counter low/high words, current instruction word, flat scratch address words, POPS packer state, scheduler mode, VGPR offset fields, shader-cycle count, all TTMP scratch registers, `M0`, and `EXEC_LO`/`EXEC_HI`.
- `SQ_INTERRUPT_WORD_AUTO`, `SQ_INTERRUPT_WORD_ERROR`, and `SQ_INTERRUPT_WORD_WAVE`: packed SQ interrupt payload formats. They expose thread-trace/WLT flags, buffer-full and UTC-error bits, error detail/type, privilege, wave/SIMD/WGP/SA/SE identity, payload data, and encoding fields. These masks are wider than 32 bits for context payload layouts.
- `DIDT_SQ_*`, `DIDT_DB_*`, `DIDT_TD_*`, and `DIDT_TCP_*`: parallel DIDT/EDC control families for shader queue, depth block, texture data, and texture cache pipeline blocks. Each family has repeated layouts for enable/reset/clock override, high-power and over-current thresholds, short/long interval sizing, stall delay and max-stall limits, tuning limits, auto-release timing, throttle policy and force-stall controls, stall patterns, MPD scale factors, stall-release FSM configuration/status, weight tables, EDC enable/reset/threshold/pattern/timer controls, throttle source enables, per-instance EDC stall delays, EDC status/overflow/readback, rolling power delta, and PCC performance counter readback.
- `DIDT_{SQ,DB,TD,TCP}_STALL_EVENT_COUNTER`: full-width stall event counter readback registers for the DIDT-controlled blocks.

The field names are hardware-oriented and generated directly from AMD register descriptions. Fields named `RESERVED` or `UNUSED` still have masks, but consumers should normally preserve them unless a programming guide explicitly defines a safe write value.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by driver code that includes the generated header:

1. A GC 10.3.0 consumer includes `gc_10_3_0_offset.h` and `gc_10_3_0_sh_mask.h`.
2. The consumer chooses a direct or indirect register address using the matching `mm*` or `ix*` offset macro.
3. It composes or decodes a value with this chunk's shift/mask constants.
4. AMDGPU, AMDKFD, PM, or SDMA register helpers perform the actual MMIO or indirect-register access while the relevant hardware block, firmware, interrupt path, debug path, or power-management sequence owns ordering.

The chunk describes fields needed for wave inspection, interrupt decoding, adaptive voltage/frequency tuning, and DIDT/EDC throttling, but it does not encode when those fields may be accessed, which bits are read-only or self-clearing, how to sequence reset/enable/stall operations, or how to coordinate with firmware and power-gated hardware. Those rules live in the consuming driver paths and the ASIC programming guide.

## State And Persistence Behavior

The file stores no software state and persists nothing. It only names hardware state exposed through GC 10.3.0 registers.

The represented hardware state is substantial:

- RTAVFS tuning and status state includes divider/gain tables, voltage-code thresholds, FSM state, guard-band values, calibration mode, and ripple-counter readback.
- SQ debug and wave state includes live busy flags, queue occupancy, active and idle wave slots, wave execution mode, status/trap flags, hardware identity, program counter, allocation state, outstanding counter state, TTMP scratch state, `M0`, `EXEC`, and instruction readback.
- SQ interrupt word fields describe context payloads generated by hardware for thread-trace, WLT, wave, and error interrupts.
- DIDT and EDC state includes enable bits, reset strobes, clock overrides, thresholds, interval and delay parameters, stall/throttle policies, weight tables, state-machine status, overflow counters, rolling power values, PCC performance counters, and stall event counters for SQ, DB, TD, and TCP blocks.

Persistence is hardware-defined. Some values are durable configuration until GPU reset, suspend/resume, power-gating, or explicit reprogramming; others are live status, counters, indirect readback windows, write-one/self-clearing control strobes, sticky overflow indicators, or hardware-owned state that changes while the GPU is running. The macros do not tell consumers which category a field belongs to, so callers must preserve unrelated bits and respect access restrictions from the hardware guide.

## Dependencies And Integration Points

The direct companion dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_3_0_offset.h`, which provides corresponding `mm*` register offsets and base indices. Indirect registers in this range are associated with the `spiind`, `sqind`, and `didtind` address blocks, so consumers also depend on the correct indirect-index/data access path for the target block.

Observed include users of the GC 10.3.0 shift/mask header in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu11/vangogh_ppt.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_amdkfd_gfx_v10_3.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v2_1.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_sdma.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/sdma_v5_2.c`

Integration points include GFX 10.3 initialization, KFD queue and trap/debug support, wavefront save/restore and inspection tooling, interrupt decoding, SMU/Vangogh power management, adaptive voltage/frequency tuning, droop and current throttling, EDC/PCC monitoring, GPU reset/recovery, suspend/resume, runtime power management, and low-level hardware validation. The SQ interrupt word layouts also align conceptually with KFD interrupt-processing code that decodes SQ-generated context payloads, although some paths carry local copies of related field definitions for older IP families.

## Risks And Edge Cases

- Header/offset mismatch is the primary correctness risk. Pairing `gc_10_3_0_sh_mask.h` with another GC generation's offset header can compile while silently targeting the wrong register or field.
- These macros are untyped constants. A wrong register family, field name, shift, or mask can alter hardware throttling, decode the wrong wave identity, or misinterpret interrupt/error payloads without compiler help.
- Several SQ interrupt masks are wider than 32 bits, such as fields above bit 31. Consumers must use a sufficiently wide integer type when decoding these payloads; truncating to `u32` loses WGP/SE/encoding fields.
- SQ wave state is live and per-wave/per-SIMD/per-WGP. Reads can race with scheduling, trap handling, context save/restore, wave completion, or reset unless the caller has halted or otherwise synchronized the target wave.
- DIDT and EDC controls are power/performance sensitive. Incorrect thresholds, interval sizes, weights, stall patterns, force-stall bits, or throttle-source enables can cause unnecessary stalls, missed protection throttling, performance regressions, or GPU hangs.
- Reset and enable fields are mixed with status and configuration in many registers. Blind writes can drop active configuration, assert reset unexpectedly, clear counters, or write reserved/unused fields.
- Full-width masks such as `0xFFFFFFFFL` often describe readback values or counters, not necessarily safe write payloads.
- `RESERVED` and `UNUSED` fields appear throughout. Code should use read-modify-write patterns or documented reset values rather than fabricating whole-register writes.
- The chunk boundary is artificial. It starts in the middle of the RTAVFS register family and ends at the file trailer, so adjacent chunks are needed for the complete per-file register-map narrative.

## Test Signals

Useful validation is mostly build, generated-header consistency, and hardware/profiling coverage:

- Build coverage for GC 10.3.0 AMDGPU, AMDKFD, SDMA, GFXHUB, and SMU/Vangogh paths that include this header.
- Generated-header checks that every field has aligned shift/mask pairs, masks do not overlap within a register except documented aliases, and each register name has a matching offset entry in `gc_10_3_0_offset.h`.
- Static checks that 64-bit SQ interrupt word fields are decoded with 64-bit-capable types and that whole-register writes do not trample reserved bits.
- SQ debug smoke tests that halt or safely sample waves, read active/valid/idle slots, decode mode/status/trap/hardware ID fields, and verify program counter, allocation, TTMP, `M0`, and `EXEC` readbacks are plausible.
- KFD interrupt tests that exercise thread-trace, wave, and error interrupt payload decoding and verify SE/SA/WGP/SIMD/wave/privilege/error fields are not truncated or shifted incorrectly.
- DIDT/EDC tests on supported GC 10.3.0 ASICs that enable/disable throttling, program thresholds and stall patterns, observe FSM status, overflow, rolling power delta, PCC counters, and stall event counters under known graphics/compute workloads.
- Power-management and recovery tests across suspend/resume, runtime power-gating, SMU interactions, and GPU reset while DIDT/EDC or wave debug features are active.
- Regression indicators include unexpected zero or saturated counters, stuck DIDT/EDC FSM state, overflow counters climbing immediately, excessive throttling or no throttling under stress, lost SQ interrupt identity bits, invalid wave debug snapshots, and hangs isolated to GFX 10.3/Vangogh-class hardware.
