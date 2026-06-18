# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_sh_mask.h lines 29636-31186

## Scope

This chunk is the final range of the generated GC 9.2.1 shader/register mask header. It starts inside the mask definitions for `GC_CAC_OVRD_TA`, then covers complete register-field mask/shift groups for late GC CAC power-accounting registers, SE CAC indirect controls, SQ wave debug/readback registers, and DIDT/EDC throttling controls. It ends with `DIDT_TCP_EDC_THRESHOLD` and the header's closing `#endif`.

The range contains 1,330 `#define` macros and 212 comment anchors, including three explicit address-block transitions: `secacind`, `sqind`, and `didtind`. The macros are generated-style constants named `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`; there are no C functions, structs, or runtime branches in this slice.

## Purpose

`gc_9_2_1_sh_mask.h` is a hardware contract for AMDGPU GC 9.2.1 register programming. This chunk supplies the bit positions and masks needed to compose, decode, or update 32-bit register values for:

- GC CAC counters and overrides for graphics/cache blocks, including TCC, TCP, TD, VGT, WD, UTCL2 router/VML2/walker, and BCI accumulator groups.
- PCC stall-pattern and throttle pattern registers used by throttling logic.
- SE CAC indirect block controls for selecting and overriding CAC signals per shader engine.
- SQ indirect debug state for wave status, wave mode, trap status, hardware identity, resource allocation, instruction-buffer state, PC/instruction words, TTMP registers, `M0`, `EXEC`, and SQ interrupt words.
- DIDT indirect controls for SQ, DB, TD, and TCP domains, including enable/reset bits, stall/tuning controls, auto-release controls, stall patterns, multi-power-delta scaling, throttle controls, weight tables, EDC controls, EDC stall patterns/delays, event counters, min/max power limits, and EDC thresholds.

The header does not implement policy. Power-management, debug, trap, and register-access code include these constants so they can avoid hard-coded bit numbers when talking to the GPU register file.

## Important API Surface

- The chunk begins boundary-partial with only the two masks for `GC_CAC_OVRD_TA`; the corresponding comment and shifts are in the previous chunk. Complete `GC_CAC_OVRD_*` groups then define `OVRRD_SELECT` and `OVRRD_VALUE` fields for TCC, TCP, TD, VGT, WD, UTCL2 router, UTCL2 VML2, and UTCL2 walker.
- `GC_CAC_WEIGHT_UTCL2_*` registers pack 16-bit signal weights. Router weights cover signals 0-9 across five registers; VML2 and walker weights cover signals 0-4 across three registers each.
- `GC_CAC_ACC_*` registers expose full-width `ACCUMULATOR_31_0` fields for BCI, UTCL2 ATCL2, router slots 0-9, VML2 slots 0-4, and walker slots 0-4. These are telemetry-style fields rather than configuration bitfields.
- `PCC_STALL_PATTERN_*` packs seven 15-bit stall patterns, two per register except the final single-pattern register. `PCC_THROT_REINCR_FIRST_PATN_*` and `PCC_THROT_DECR_FIRST_PATN_*` encode compact first-pattern selections for reincrement and decrement behavior.
- `SE_CAC_CNTL`, `SE_CAC_OVR_SEL`, and `SE_CAC_OVR_VAL` form the `secacind` block. They expose CAC force-disable, threshold, block ID, signal ID, override-select, and override-value fields.
- `SQ_DEBUG_STS_GLOBAL` and `SQ_DEBUG_STS_LOCAL` expose SQ FIFO, busy, interrupt-message, and wave-level status fields.
- `SQ_WAVE_*` registers under `sqind` describe wave readback/debug state: mode bits, status bits, trap status, hardware ID tuple, VGPR/SGPR allocation, LDS allocation, instruction-buffer counters/status, PC, instruction dwords, TTMP0-15, `M0`, and `EXEC_LO/HI`.
- `SQ_INTERRUPT_WORD_*` registers describe auto/common/wave interrupt payload encodings, including thread-trace, timestamp, overflow, SE ID, wave ID, SIMD ID, CU ID, VM ID, privilege, and encoding fields.
- `DIDT_{SQ,DB,TD,TCP}_CTRL0` groups define the primary DIDT enable/reset/clock/stall/tuning/event bits, including `DIDT_CTRL_EN`, `DIDT_CTRL_RST`, `DIDT_STALL_CTRL_EN`, `DIDT_TUNING_CTRL_EN`, `DIDT_STALL_AUTO_RELEASE_EN`, `DIDT_HI_POWER_THRESHOLD`, `DIDT_AUTO_MPD_EN`, `DIDT_STALL_EVENT_EN`, and `DIDT_STALL_EVENT_COUNTER_CLEAR`.
- `DIDT_*_CTRL2`, `DIDT_*_STALL_CTRL`, `DIDT_*_TUNING_CTRL`, `DIDT_*_STALL_AUTO_RELEASE_CTRL`, and `DIDT_*_CTRL3` define power-delta, stall delay, maximum stall, auto-release, throttle-policy, level-combine, stall-select, force-stall, and delay-enable behavior.
- `DIDT_*_STALL_PATTERN_*`, `DIDT_*_MPD_SCALE_FACTOR`, `DIDT_*_THROTTLE_CNTL*`, `DIDT_*_WEIGHT*`, and `DIDT_*_EDC_*` define the table-like data used by DIDT and EDC throttling across SQ, DB, TD, and TCP domains.
- `DIDT_*_STALL_EVENT_COUNTER` registers expose full-width 32-bit event counters for SQ, DB, TD, TCP, and DBR domains. The chunk also defines per-domain `CTRL1` min/max power fields and EDC threshold registers for SQ, DB, TD, and TCP.

There are no local C types or functions. The public API is the preprocessor namespace, used with companion `gc_9_2_1_offset.h` offsets and common AMDGPU register helpers such as `REG_SET_FIELD`, `CGS_WREG32_FIELD_IND`, and indirect DIDT/SQ register accessors in consuming code.

## Control Flow

This header has no executable control flow. Runtime behavior appears in consumers that use the masks:

1. Select an ASIC-appropriate offset from `gc_9_2_1_offset.h`, usually an `ix...` indirect register for `secacind`, `sqind`, or `didtind`.
2. Read the current 32-bit register value if only some fields are being changed.
3. Clear a field with `REGISTER__FIELD_MASK`, shift the new value by `REGISTER__FIELD__SHIFT`, and merge it into the register word.
4. Write the result through the relevant MMIO or indirect-register accessor.
5. For readback/debug paths, mask and shift hardware values to decode wave state, interrupt payloads, CAC accumulators, or DIDT counters.

PowerTune code for nearby GC generations shows the intended pattern: tables list `ixDIDT_*` offsets together with `DIDT_*__FIELD_MASK`, `DIDT_*__FIELD__SHIFT`, and programmed values; enable/disable paths use indirect DIDT writes to toggle `DIDT_CTRL_EN`, `EDC_EN`, and `EDC_SW_RST`. SQ wave debug paths similarly read `ixSQ_WAVE_STATUS` and related `SQ_WAVE_*` registers when dumping or preserving wave state.

## State and Persistence

The macros are stateless compile-time constants, but the hardware state they describe is persistent until the GPU, power-management code, debug code, context restore, or reset path changes it.

GC CAC and SE CAC registers describe power-accounting configuration and telemetry. Weight and override fields alter how block-level CAC signals contribute to accounting; accumulator fields expose hardware-maintained counters. These counters are volatile hardware state and can wrap because the masks are full-width 32-bit fields.

SQ wave registers describe live execution state. `SQ_WAVE_STATUS`, `SQ_WAVE_MODE`, `SQ_WAVE_TRAPSTS`, `SQ_WAVE_HW_ID`, `SQ_WAVE_GPR_ALLOC`, `SQ_WAVE_LDS_ALLOC`, `SQ_WAVE_PC_*`, instruction words, TTMP registers, `M0`, and `EXEC` represent per-wave state visible through the SQ indirect debug interface. Reads are snapshots of live GPU execution, and writes or debug actions in this area can affect trapping, halt behavior, replay, and wave scheduling.

DIDT and EDC registers are power-management state. Enables, stall policies, thresholds, weights, delays, and throttle controls can persist across workloads while the ASIC is powered and directly influence throttling behavior for SQ, DB, TD, TCP, and related DBR telemetry. Event counters persist until reset or explicit clear via the relevant `DIDT_STALL_EVENT_COUNTER_CLEAR` fields. EDC reset semantics are visible in consumers that set `EDC_EN` and invert `EDC_SW_RST` when enabling or disabling EDC.

No disk persistence or software cache is implemented here. The stateful behavior belongs to the GPU register file and to runtime drivers that program these fields.

## Dependencies

- Depends on AMD's generated GC 9.2.1 register specification. Manual edits risk diverging from the ASIC hardware contract.
- Must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_2_1_offset.h`, which supplies the matching register offsets.
- Consumers depend on AMDGPU register helper macros and indirect register spaces for GC, SE CAC, SQ, and DIDT access.
- Power-management integration depends on PowerPlay/DPM code that programs DIDT/EDC tables and toggles ramping capabilities.
- Debug and trap integration depends on SQ wave debug readers and KFD CWSR/trap code understanding the same wave status and register-state layout.
- The masks are generation-specific. Similar names appear in GC 9.0, GC 9.1, GC 10.x, and later headers, but fields and offsets can differ, so cross-generation reuse must include the correct header pair.

## Integration Points

- AMDGPU power tuning uses DIDT masks to build initialization tables and runtime writes for SQ, DB, TD, and TCP ramping. The same programming model controls EDC thresholds, EDC enables, stall patterns, throttle release behavior, and event-counter clearing.
- SQ debug paths use wave registers to read live wave information for diagnostics, hang analysis, shader debugging, and wave dumps. The fields in this chunk line up with concepts also handled by KFD trap/CWSR assembly, such as wave status, halt, trap, SPI priority, ECC error, TTMP registers, and `EXEC`.
- Telemetry and diagnostics can use CAC accumulator and DIDT event-counter fields to inspect power/throttle activity. Because these are hardware counters, sampling code must handle wraparound and coordination with clear/reset operations.
- Register decode tools and golden-register validation can use the shift/mask pairs to verify emitted state against known-good programming sequences.
- The include path is architecture-specific: this header is pulled by GC 9.2.1 users such as Vega12-era power-management include code, not by generic code that should be ASIC-agnostic.

## Risks

- Bitfield drift is the primary risk. A wrong shift or mask silently updates the wrong hardware bits, which can misprogram power throttling, corrupt debug reads, or break CAC accounting.
- This chunk is boundary-partial at the start. `GC_CAC_OVRD_TA` is not fully represented here, so merge tooling should combine it with the previous chunk for complete per-register documentation.
- DIDT/EDC controls have high operational impact. Incorrect values for enable, reset, stall delay, throttle policy, thresholds, or weight registers can over-throttle the GPU, fail to throttle during droop events, trigger performance regressions, or destabilize the device.
- SQ wave debug fields are sensitive live state. Misdecoding `SQ_WAVE_STATUS`, trap status, `EXEC`, TTMP, or PC fields can mislead hang/debug analysis; accidental writes through SQ indirect paths could alter a running wave.
- Counter and accumulator fields are full 32-bit values with no type safety. Readers must handle wraparound and avoid racing with code that clears DIDT event counters.
- Repeated register families are copy/paste prone. SQ, DB, TD, and TCP DIDT groups share many field names; using a mask from the wrong domain can produce a compile-time-valid but hardware-wrong access.
- Cross-generation similarity is dangerous. GC 9.2.1 masks resemble GC 9.0/9.1/10.x masks, but fields such as DIDT controls and EDC controls evolve between generations.

## Test Signals

- Build coverage: compile AMDGPU code paths that include `gc_9_2_1_sh_mask.h` to catch syntax errors, duplicate macros, and missing companion definitions.
- Static consistency: verify each `REGISTER__FIELD__SHIFT` in this range has the expected `REGISTER__FIELD_MASK`, and that each register has a matching offset in `gc_9_2_1_offset.h`.
- Register-generation checks: compare this chunk against AMD's GC 9.2.1 register source/spec and against adjacent generated headers to detect accidental manual drift.
- Power-management runtime tests: on matching GC 9.2.1 hardware, enable and disable DIDT/EDC ramping paths and watch for invalid register accesses, GPU resets, performance cliffs, or thermal/power telemetry anomalies.
- Counter tests: sample `DIDT_*_STALL_EVENT_COUNTER` and CAC accumulator registers under controlled workloads, then clear/reset where supported and verify expected counter behavior and wraparound-safe decoding.
- SQ debug tests: trigger wave dumps or hang diagnostics and confirm `SQ_WAVE_*` fields decode plausible wave IDs, SIMD/CU/SE identity, status, PC, instruction words, `EXEC`, and TTMP values.
- Graphics and compute stress: run shader-heavy, texture-heavy, depth-heavy, and mixed workloads to exercise SQ/TD/TCP/DB throttling domains while monitoring for hangs, VM faults, throttling instability, or debug-register decode failures.
