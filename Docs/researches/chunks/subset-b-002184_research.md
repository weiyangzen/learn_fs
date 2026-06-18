# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 81496-83888

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask slice. It contains no executable C logic, structs, enums, or functions. Its public interface is a dense set of C preprocessor constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`; AMDGPU Display Core code combines these constants with matching `dcn_4_1_0_offset.h` register offsets and register-access helpers to read or update individual MMIO bitfields.

The requested range contains 2,178 `#define` entries, including 1,098 shift macros and 1,091 mask macros, plus 215 register-heading comments. It starts at the tail of the `DPCSSYS_CR0_SUPX_DIG_RTUNE_STAT` group, covers Super-X (`SUPX`) retune/analog override fields, then a large `CR0_LANEX` physical-lane slice: ASIC override inputs/outputs, TX and RX power-control state tables, TX DCC DAC controls, RX VCO/CDR/adaptation/statistics controls, MPHY low-speed controls, digital-to-analog override outputs, and direct analog TX/RX control/measurement registers. It ends inside the beginning of `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1`; the first and last register groups are therefore artificial chunk-boundary splits.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU Display Core hardware metadata for DCN/DPCS link PHY programming. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The exported API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position of a field inside a display hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, or update that field.

The main register families covered here are:

- `DPCSSYS_CR0_SUPX_DIG_RTUNE_*`: receiver/transmitter retune set and status values, retune timing counters, TX calibration code fields, and the tail of the retune status register from the preceding chunk.
- `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLA_*` and `DPCSSYS_CR0_SUPX_DIG_ANA_MPLLB_*`: master PLL A/B analog override outputs for word/HDMI/div clocks, output enables, lane-side output enables, analog enable, reset, calibration, feedback clock, gearshift, standby, analog integrator/charge-pump fields, and PMIX enable/selection controls.
- `DPCSSYS_CR0_SUPX_DIG_ANA_RTUNE_OVRD_OUT`, `ANA_STAT`, and `ANA_BG_OVRD_OUT`: retune comparator/mode/enable/value overrides, analog comparator/clock-detect status, bandgap/reference regulator enables, fast-start, kick-start, async reset, and reference-selection overrides.
- `DPCSSYS_CR0_LANEX_DIG_ASIC_*`: per-lane digital override and ASIC-facing input/output fields for lane resets, requests, P-state, low-power detect, width, rate, MPLL select/enables, TX async modes, DETRX, VBOOST/IBOOST, TX EQ/term settings, RX data rate, DFE taps, loopback/slicer settings, CDR startup/frequency tune, calibration DAC controls, and readback/status fields.
- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*`: TX P-state templates for P0/P0S/P1/P2, TX power-up timing fields, DCC coefficient/DAC bank address/data/control/range/select/ack/address fields, TX clock alignment, and TX LBERT pattern/error trigger fields.
- `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: RX P-state templates for P0/P0S/P1/P2 and RX power-up timing, including analog clock/CDR/VREG/DCC/AFE/DFE/deserializer/fast-start/loopback and termination controls.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`: RX VCO calibration control/timing/status, CDR control/status, DPLL frequency and frequency-bound fields.
- `DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_*`: adaptation configuration, reset, status, DAC offset/select, CR-bank address/data, ATT/VGA/CTLE/DFE-tap statuses, slicer control, and error slicer level fields.
- `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*`: receiver statistic/match engine fields for load values, masks, match controls, statistic source/clock/counter enables, sample counts, counter values, comparator clock control, and statistic stop.
- `DPCSSYS_CR0_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stability count fields.
- `DPCSSYS_CR0_LANEX_DIG_ANA_*`: digital override outputs into analog TX/RX blocks, including TX power, term-code, equalization, DCC DAC, RX control/power/VCO/calibration/DAC/AFE/CTLE/scope/slicer/IQ phase/status/termination/MPHY/signal-detect controls.
- `DPCSSYS_CR0_LANEX_ANA_TX_*` and `DPCSSYS_CR0_LANEX_ANA_RX_*`: direct analog TX/RX measurement, power, alternate-bus, ATB, DCC, termination, clock, misc, VREG, CDR/deserializer, slicer, signal-quality, calibration, and register-reference controls.

Many fields are one-bit enables/override-enables, but this range also includes packed multi-bit tuning values for rate, width, equalization, calibration codes, power timing, VCO/frequency calibration, DAC controls, statistic counters, ATB measurement selects, and analog regulator/charge-pump/termination settings.

## Control Flow

This header slice has no local control flow. Runtime behavior comes from AMDGPU Display Core code that includes this generated header and its companion offset header:

1. DCN 4.1.0-specific code includes `dcn/dcn_4_1_0_offset.h` and `dcn/dcn_4_1_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into ASIC-specific register, shift, and mask tables.
3. Display Core code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to access hardware.
4. Those helpers use the masks and shifts to preserve unrelated fields while programming DPCS/SUPX/LANEX link PHY state.

The macros do not encode sequencing rules. Consumers still need to perform hardware-defined sequences: power-up/power-down lane state machines, PLL reset/calibration/lock ordering, retune calibration timing, TX/RX P-state transitions, CDR/VCO calibration, adaptation reset and convergence, and status polling. They also must distinguish writable controls from status, self-clearing, sticky, or debug-only fields.

## State And Persistence Behavior

This chunk stores no software state. It describes state that lives in DCN 4.1.0 display PHY registers:

- SUPX retune state for RX/TXUP/TXDN calibration setpoints, status values, retune timing, comparator reset/mode/enable, and analog comparator results.
- MPLL A/B state for clock enables, output enables, reset, calibration, standby, feedback clock, gearshift, PMIX routing, analog integrator and charge-pump controls.
- Lane override state for forcing ASIC-visible lane inputs and TX/RX control paths instead of normal sequencer-provided values.
- TX state for P-state templates, power-up timing, reset/refgen/clock/serial/data/VCM/DCC/RXDET/VBOOST behavior, clock alignment, DCC DAC operations, and TX LBERT diagnostics.
- RX state for P-state templates, RX power-up timing, CDR/VCO/DPLL calibration, AFE/DFE/deserializer/loopback/fast-start/termination behavior, adaptation configuration, and error/slicer/statistic capture.
- Analog TX/RX state for direct overrides, equalization, term codes, VREG settings, calibration DACs, ATB measurement routing, signal-detect thresholds, MPHY low-speed controls, and analog status readbacks.

Persistence is hardware-defined. Many control fields remain programmed until a modeset, link retrain, PHY reset, power-gating transition, suspend/resume, GPU reset, or ASIC reset rewrites them. Status fields such as ACK/done/counter/status/FSM bits may be read-only, sticky, clear-on-read, write-one-to-clear, or valid only while the related PLL/lane/analog block is powered. This generated header does not describe those side effects.

## Dependencies And Integration Points

- The shift/mask definitions must remain synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which supplies matching `ixDPCSSYS_*` MMIO offsets.
- DCN 4.1.0 display code includes this header from paths such as `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/gpio/dcn401/*`, `display/dc/resource/dcn401/dcn401_resource.c`, and `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`.
- The same DPCS register naming shape appears in `include/asic_reg/dpcs/*_offset.h` and `*_sh_mask.h` for related DPCS generations. Consumers depend on exact ASIC-version pairing rather than just similarly named fields.
- Link bring-up, HPD/display resource initialization, clock management, DMUB firmware-facing setup, diagnostics, and low-level PHY debug paths can indirectly depend on this range through generated register tables.
- The `SUPX` fields integrate with shared PHY support logic for PLL/retune/reference/bandgap control; the `LANEX` fields integrate with per-lane TX/RX state machines and analog link PHY tuning.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while writing the wrong MMIO bits, corrupting neighboring fields, or silently leaving a link-control feature unprogrammed.
- Generated-header and offset-header drift is the main integrity risk. Correct masks paired with stale offsets, or correct offsets paired with stale masks, can misprogram PLLs, lane state, calibration, or diagnostic registers without obvious compile failures.
- Chunk boundaries are not semantic. `DPCSSYS_CR0_SUPX_DIG_RTUNE_STAT` starts before this slice, and `DPCSSYS_CR0_LANEX_ANA_RX_ATB_MEAS1` continues after this slice.
- Full-register writes are risky because many registers pack override values, override enables, hardware-status bits, reserved bits, and self-clearing pulses in one 16-bit or 32-bit word. Read-modify-write helpers are expected unless hardware documentation requires an exact write.
- Override-enable bits are especially hazardous. Leaving an override enabled can mask normal hardware sequencer behavior and cause intermittent link training, hotplug, suspend/resume, or power-state failures.
- PLL and retune fields are sequencing-sensitive. Misprogramming reset/calibration/gearshift/standby/timing or lock-related fields can create blank displays, unstable clocks, EMI/spread issues, or link failures that appear only at certain rates.
- TX/RX P-state template fields affect power, reset, data, clock, DCC, CDR, AFE/DFE, loopback, VBOOST, RXDET, and termination behavior. A one-bit error can cause lane power leakage, inability to exit low-power states, failed receiver detect, or PHY bring-up timeouts.
- RX adaptation/statistic controls are signal-integrity-sensitive. Wrong DFE, CTLE, VGA, ATT, slicer, DAC, match/statistic, or CDR settings can pass basic compile and boot tests while failing under marginal cables, high bit rates, cold/thermal corners, or after long runtime.
- Analog test-bus and measurement controls can disturb live lanes if enabled outside controlled diagnostics. ATB, force, pull-up/down, regulator-reference, signal-detect, or loopback fields should be treated as hardware debug controls unless the call site proves otherwise.
- Repeated register layouts across lanes and DCN/DPCS generations make copy/generator drift hard to spot. Testing a single lane, rate, or connector mode does not validate the whole macro family.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 4.1.0 display behavior:

- Build coverage for AMDGPU Display Core with DCN 4.1.0 enabled, ensuring all generated token-paste register references compile against this header and `dcn_4_1_0_offset.h`.
- Static generated-header checks that each field has a matching shift/mask pair when expected, masks align with shifts, masks do not overlap unintentionally inside the same register group, and reserved-field widths match the implied register width.
- Cross-file comparison against the authoritative generated source or adjacent DPCS/DCN versions for renamed, added, removed, or shifted fields, especially around `SUPX` retune/MPLL and `LANEX` TX/RX power/adaptation blocks.
- Display smoke tests on DCN 4.1.0 hardware across cold boot, modeset, hotplug, suspend/resume, GPU reset recovery, and multiple connector/link-rate combinations.
- Link-training and PHY validation at low and high link rates, including DP/USB-C/HDMI paths where applicable, with attention to PLL lock, RXDET, CDR/VCO calibration done, and lane P-state transitions.
- Stress tests that exercise power-state transitions repeatedly, watching for blank screens, training retries, underflow, link loss, increased error counters, or wake failures.
- Diagnostic readback tests for status/statistic/counter fields, verifying that register helper reads decode plausible values and that writes do not disturb reserved or read-only bits.
- Hardware lab signal-integrity tests for marginal cables, temperature/voltage corners, and long-duration display output, because many fields in this chunk control analog tuning and may only fail outside nominal conditions.
