# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_default.h lines 5870-6028

## Scope

This chunk is the final segment of the generated AMD GC 10.1.0 default-register header. It contains only C preprocessor `#define` constants for reset/default values. There are no functions, structs, runtime branches, storage objects, or executable initialization logic in this range.

The range starts at the tail of the `sqind` address block with shader wave register defaults from `ixSQ_WAVE_TTMP10_DEFAULT` through the SQ interrupt-word defaults. It then covers the complete `didtind` address block for dynamic inductive droop/throttling defaults across the SQ, DB, TD, and TCP graphics sub-blocks, ending with stall event counter defaults and the file's `#endif`.

## Purpose

`gc_10_1_0_default.h` is generated hardware metadata for AMDGPU's GC 10.1 ASIC generation. Its `_DEFAULT` macros document the hardware reset/default value associated with each register name from the matching GC register address header. Driver code includes this file alongside `gc_10_1_0_offset.h` and `gc_10_1_0_sh_mask.h` so ASIC-specific code can use the correct register names, bit fields, and known default values for Navi10-era graphics hardware.

In this chunk, the SQ wave defaults describe debug-visible per-wave state and interrupt payload registers. The DIDT defaults describe the baseline power/throttle configuration for several graphics pipeline clients:

- `SQ`: shader sequencer / shader queue logic.
- `DB`: depth buffer/render backend logic.
- `TD`: texture data path logic.
- `TCP`: texture cache processor logic.

The DIDT block is concerned with droop-aware throttling, stall insertion, auto-release timing, energy/current-delta control, per-level weights, stall delay tables, status, overflow, rolling power delta, PCC performance counters, and stall event counters.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro convention:

- `ix<REGISTER>_DEFAULT` gives the reset/default value for an indexed GC register.
- The corresponding register address is defined in `gc_10_1_0_offset.h`.
- The corresponding bit layout is defined in `gc_10_1_0_sh_mask.h`.
- AMDGPU register helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and DIDT indirect helpers in older power-management code are the normal consumers of these register descriptions.

The `sqind` macros at the beginning of this chunk are all zero defaults:

- `ixSQ_WAVE_TTMP10_DEFAULT` through `ixSQ_WAVE_TTMP15_DEFAULT`: temporary trap scratch register defaults for a selected wave, with full-width `DATA` fields in the companion shift/mask header.
- `ixSQ_WAVE_M0_DEFAULT`, `ixSQ_WAVE_EXEC_LO_DEFAULT`, and `ixSQ_WAVE_EXEC_HI_DEFAULT`: wave scalar `M0` and execution-mask defaults.
- `ixSQ_WAVE_FLAT_SCRATCH_LO_DEFAULT`, `ixSQ_WAVE_FLAT_SCRATCH_HI_DEFAULT`, and `ixSQ_WAVE_FLAT_XNACK_MASK_DEFAULT`: flat scratch and XNACK mask defaults.
- `ixSQ_INTERRUPT_WORD_AUTO_DEFAULT`, `ixSQ_INTERRUPT_WORD_ERROR_DEFAULT`, and `ixSQ_INTERRUPT_WORD_WAVE_DEFAULT`: default encodings for SQ interrupt payload words. The companion masks expose fields such as thread trace, WLT, buffer-full/error bits, error type/detail, wave/SIMD/WGP/SE identifiers, privilege, and encoding.

The DIDT control defaults repeat across SQ, DB, TD, and TCP with block-specific macro prefixes:

- `*_CTRL0_DEFAULT` is `0x0000ff00`, which maps primarily to the high-power threshold field in the matching `*_CTRL0` masks while enable/reset/stall control bits default clear.
- `*_CTRL1_DEFAULT` is `0x00ff00ff`, setting default min/max power fields.
- `*_CTRL2_DEFAULT` is `0x18800004`, covering max power delta plus short-term and long-term interval fields.
- `*_CTRL_OCP_DEFAULT` is `0x000000ff` for SQ/DB/TD and `0x0000ffff` for TCP, setting the over-current-protection maximum power default.
- `*_STALL_CTRL_DEFAULT` is `0x00fff000`, describing default high/low stall delay and maximum-stall fields.
- `*_TUNING_CTRL_DEFAULT` is `0x00010004`, setting high/low max-power-delta tuning fields.
- `*_STALL_AUTO_RELEASE_CTRL_DEFAULT` is `0x00ffffff`, the default auto-release timer value.
- `*_CTRL3_DEFAULT` is `0x00038000`, covering DIDT throttle trigger/power-level/stall-pattern bit selection fields while enable/force/qualify bits default clear.

Each DIDT client also has common pattern and scale defaults:

- `*_STALL_PATTERN_1_2_DEFAULT` = `0x01010001`.
- `*_STALL_PATTERN_3_4_DEFAULT` = `0x11110421`.
- `*_STALL_PATTERN_5_6_DEFAULT` = `0x25291249`.
- `*_STALL_PATTERN_7_DEFAULT` = `0x00002aaa`.
- `*_MPD_SCALE_FACTOR_DEFAULT`, `*_STALL_RELEASE_CNTL0_DEFAULT`, `*_STALL_RELEASE_CNTL1_DEFAULT`, `*_STALL_RELEASE_CNTL_STATUS_DEFAULT`, and `*_WEIGHT0_3/4_7/8_11_DEFAULT` all default to zero.

The EDC and throttle-related defaults likewise repeat across the clients:

- `*_EDC_CTRL_DEFAULT` = `0x00001c00`, setting EDC trigger/stall-pattern bit fields while enable, reset, force-stall, GC/SE combination, and policy bits default clear.
- `*_EDC_THRESHOLD_DEFAULT` = `0x00000000`.
- `*_EDC_STALL_PATTERN_1_2/3_4/5_6/7_DEFAULT` mirror the DIDT stall-pattern defaults.
- `*_EDC_TIMER_PERIOD_DEFAULT` = `0x00003fff`.
- `*_THROTTLE_CTRL_DEFAULT` = `0x00000000`, so GC EDC, PCC, power-brake, and EDC-only stall modes default disabled.
- `*_EDC_STALL_DELAY_*_DEFAULT`, `*_EDC_STATUS_DEFAULT`, `*_EDC_OVERFLOW_DEFAULT`, `*_EDC_ROLLING_POWER_DELTA_DEFAULT`, and `*_EDC_PCC_PERF_COUNTER_DEFAULT` default to zero.

The range is not perfectly symmetrical: `DIDT_DB_EDC_STALL_DELAY_2` and `DIDT_DB_EDC_STALL_DELAY_3` are absent from this GC 10.1.0 default chunk, while SQ, TD, and TCP include delays 1-3. This should be treated as generated hardware description, not as a documentation omission.

## Control Flow

This header has no runtime control flow. The only behavior is compile-time substitution of numeric constants.

The implied driver control flow happens in consumers:

1. Include the GC 10.1.0 offset, shift/mask, and default headers for the target ASIC.
2. Address a register through its `ix...` or `mm...` address macro.
3. Use the shift/mask macros to modify a field with read-modify-write helpers.
4. Optionally compare, initialize, restore, or document expected values using the `_DEFAULT` macro from this file.

For the DIDT registers, real control flow is normally power-management or hardware-initialization sequencing outside this file: enable or reset a DIDT block, program thresholds/timers/patterns, allow/force throttling or stall insertion, poll status/counters, and clear event counters. The defaults in this chunk establish the hardware baseline before that sequencing begins.

## State And Persistence

The macros themselves are stateless constants and do not persist anything. The state they describe lives in GPU registers:

- SQ wave registers are volatile debug/state windows for currently selected shader waves. Values can change as waves are scheduled, trapped, interrupted, killed, or inspected by debug/thread-trace machinery.
- SQ interrupt-word registers describe interrupt payload formatting and event state that is hardware-generated rather than durable driver state.
- DIDT registers hold graphics power/throttling policy, timers, stall patterns, and counters. These can be reset by GPU reset, graphics IP reset, power-gating transitions, suspend/resume, firmware or SMU policy changes, and explicit driver writes.

The default values are important because they are the only persistent source-level record of expected reset state in this header. Code that writes DIDT registers must preserve hardware-owned or reserved fields according to the companion masks, because a full-register write can unintentionally change throttle policy, stall thresholds, or counter clear bits.

## Dependencies

This chunk depends on AMD's generated register metadata for the same ASIC revision staying in sync:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_offset.h` supplies register addresses such as `ixSQ_WAVE_TTMP10`, `ixSQ_INTERRUPT_WORD_ERROR`, `ixDIDT_SQ_CTRL0`, `ixDIDT_DB_CTRL0`, `ixDIDT_TD_CTRL0`, and `ixDIDT_TCP_CTRL0`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_10_1_0_sh_mask.h` supplies field names and masks for interpreting the defaults, including `SQ_WAVE_TTMP10__DATA_MASK`, `SQ_INTERRUPT_WORD_ERROR__ERR_TYPE_MASK`, and the `DIDT_*` enable, threshold, pattern, timer, status, and throttle masks.
- AMDGPU GC/GFX hub and power-management code includes GC 10.1.0 generated headers when programming Navi10-class graphics registers.
- SOC15 register access helpers provide the actual MMIO or indexed-register access paths.
- Firmware/SMU policy may also influence DIDT/throttling behavior, so these defaults are not the complete runtime policy.

The file path is under a Ceph-client source mirror, but the content is AMDGPU DRM hardware metadata and has no dependency on Ceph filesystem logic.

## Integration Points

The SQ wave defaults integrate with shader debugging, trap handling, wave inspection, thread trace, and interrupt reporting. The associated field layouts expose wave identifiers, SIMD/WGP/SE location, privilege state, error detail/type, and thread trace conditions used by diagnostics and fault reporting.

The DIDT defaults integrate with graphics power and reliability management. The common SQ/DB/TD/TCP pattern means the same conceptual throttling machinery is replicated per hardware client: thresholds and interval sizing estimate power or droop risk, stall patterns shape the duty cycle of inserted stalls, auto-release and release-control registers govern stall recovery, and EDC/PCC status/counter registers expose whether power-delta or current-related controls are triggering.

The header is directly included by `amdgpu/gfxhub_v2_0.c`, which includes the GC 10.1.0 offset, shift/mask, and default headers as the ASIC description set for GFXHUB v2.0. DIDT register families are also conceptually tied to power-management code paths that read and write `ixDIDT_*_CTRL0` registers using `DIDT_*_CTRL0__DIDT_CTRL_EN_MASK`-style masks, even when the visible example in this source tree is for older ASIC support.

## Risks

- This is generated hardware data. Hand-editing a default value can silently desynchronize the driver from AMD's register specification.
- The chunk starts mid-`sqind` register family. Earlier `SQ_WAVE_*` defaults are in the previous chunk, so file-level research should merge both ranges before drawing conclusions about the full SQ wave window.
- The DIDT register families are repetitive. Copying a value or mask between SQ, DB, TD, and TCP can compile cleanly but affect the wrong hardware client.
- `DIDT_TCP_CTRL_OCP_DEFAULT` differs from the SQ/DB/TD OCP default. Treating the four clients as byte-for-byte identical would lose a real hardware distinction.
- DB lacks the EDC stall delay 2 and 3 defaults present for SQ, TD, and TCP in this chunk. Consumers or validators should not assume every DIDT client has the exact same register list.
- Many DIDT controls are sequencing-sensitive: enable, reset, force-stall, throttle-mode, auto-release, and counter-clear bits must be written deliberately. Incorrect full-register writes can cause performance loss, throttling instability, or misleading counters.
- Some SQ interrupt masks in the companion header extend above 32 bits. Consumers must use appropriately wide integer types when decoding those payload words.
- Runtime firmware or SMU policy may override or reprogram throttling behavior, so these defaults should not be interpreted as the steady-state operating configuration after driver and firmware initialization.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU code that includes `gc_10_1_0_default.h`, especially GFXHUB v2.0 and GC 10.1 paths.
- Static comparison against regenerated AMD register headers to ensure `_DEFAULT` values and register presence match the authoritative hardware source.
- Cross-checks that every default macro in this range has a matching address macro in `gc_10_1_0_offset.h` and field definitions in `gc_10_1_0_sh_mask.h` where applicable.
- GPU reset, suspend/resume, and power-gating tests on GC 10.1/Navi10 hardware to confirm default restore assumptions do not regress.
- Shader trap/debug/thread-trace tests that exercise SQ wave state and SQ interrupt-word decoding.
- Power-management stress tests that exercise graphics load transitions, throttling, over-current or power-brake paths, and DIDT/EDC counter readback.
- Performance regression tests for shader, depth-buffer, texture, and texture-cache workloads, since DIDT misprogramming is likely to show up as unexpected throttling rather than a build failure.
