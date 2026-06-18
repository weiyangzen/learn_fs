# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 38924-41334

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice. It provides C preprocessor constants for DPCS CR1 SUPX and LANEX register bit layouts; it does not contain executable driver logic. AMDGPU display code consumes these constants with companion register-offset headers and register helpers so link, PHY, lane, PLL, power, calibration, status, and debug fields can be programmed or decoded without open-coded bit positions.

The requested range contains 2,411 lines, 2,167 `#define` statements, 1,153 `__SHIFT` macros, 1,025 `_MASK` macros, and 242 register comment boundaries. It starts in the middle of `DPCSSYS_CR1_SUPX_ANA_MPLLA_OVRD`, covers CR1 SUPX analog/digital MPLLA/MPLLB, clock/reset, RTUNE, and analog override/status definitions, then moves through a broad CR1 LANEX digital lane block: ASIC override and mirror fields, TX/RX power-control, DCC DAC, VCO/CDR/DPLL, RX adaptation, statistics, MPHY, digital-to-analog override/readback, and the beginning of analog TX override/power definitions. The final line stops inside `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD`; its remaining fields continue in the next chunk.

Although the path is under a local `ceph-client` mirror, this header belongs to AMDGPU display hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, MMIO operations, or exported symbols in this range. The interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: mask for that field in the register value.

The major macro groups are:

- `DPCSSYS_CR1_SUPX_ANA_MPLLA_*` and `DPCSSYS_CR1_SUPX_ANA_MPLLB_*`: MPLL analog override, miscellaneous, ATB measurement, control, calibration, reset, feedback clock, VREF, charge-pump, filter, SPO, bypass, DLL/divider, and reserved fields for the A and B PLL paths. `MPLLA_OVRD` is split at the first line of this chunk; its mask definitions are before this range.
- `DPCSSYS_CR1_SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR1_SUPX_DIG_MPLLB_MPLL_PWR_CTL_*`: digital MPLL power-control override, lock/power-up/status, DAC max-range, timer, calibration, analog DAC readback, and SSC spread-type fields for both PLLs.
- `DPCSSYS_CR1_SUPX_DIG_CLK_RST_*`: bandgap and reference power-up timing and reference VPHUD fields.
- `DPCSSYS_CR1_SUPX_DIG_RTUNE_*`: RTUNE debug/configuration, status, RX/TXDN/TXUP set values and measured status, counter configuration, and TX calibration code fields.
- `DPCSSYS_CR1_SUPX_DIG_ANA_*`: digital-to-analog override outputs and analog status for MPLLA/MPLLB, RTUNE, bandgap, and PMIX paths, including override-enable and value fields.
- `DPCSSYS_CR1_LANEX_DIG_ASIC_*_OVRD_IN_*`, `*_ASIC_IN_*`, and `*_ASIC_OUT*`: generic CR1 lane override inputs and ASIC mirror/status fields for lane, TX, RX, RX EQ, RX CDR/VCO, additional TX/RX override banks, and OCLA. These include pstate, rate, width, reset, data-enable, request/ack, detect-RX, loopback, MPLL selection/enables, serializer, termination, equalization, adaptation, CDR/VCO, CTLE/VGA/ATT, DFE, slicer, ATE, PH2 calibration, and override-enable fields.
- `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_*`: TX pstate programming, request/data-enable/reset behavior, RX-detect and termination settings, power-up timing windows, DCC CR-bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT controls.
- `DPCSSYS_CR1_LANEX_DIG_RX_PWRCTL_*`, `DPCSSYS_CR1_LANEX_DIG_RX_VCOCAL_*`, `DPCSSYS_CR1_LANEX_DIG_RX_CDR_*`, and `DPCSSYS_CR1_LANEX_DIG_RX_DPLL_*`: RX pstate and timing controls, VCO calibration controls/status/timers, CDR configuration/status, DPLL frequency and bounds, and RX alignment masks.
- `DPCSSYS_CR1_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration and status for ATT, VGA, CTLE, DFE taps, slicer offsets, DAC-control mux selection, adaptation reset, and adaptation CR-bank access.
- `DPCSSYS_CR1_LANEX_DIG_RX_STAT_*`: RX status load/mask/match/control/sample/counter/stop fields and calibration-comparator clock controls.
- `DPCSSYS_CR1_LANEX_DIG_MPHY_*`: MPHY RX PWM, low-speed termination, and analog PWM clock-stability count fields.
- `DPCSSYS_CR1_LANEX_DIG_ANA_*`: digital-to-analog TX/RX override outputs, TX termination and EQ, RX control/power/VCO/calibration/DAC/scope/slicer/IQ/signal-change controls, analog status, RX termination, MPHY, signal-detect, TX DCC DAC, and extra TX override output fields.
- `DPCSSYS_CR1_LANEX_ANA_TX_OVRD_MEAS` and the first fields of `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD`: analog TX measurement/override, ATB calibration mux/compare, VCM hold, pull-up/down, loopback, refgen, divider, data, and clock-enable fields.

Field-name patterns carry the hardware semantics: `OVRD`, `OVRD_EN`, `*_REG`, `REQ`, `ACK`, `DONE`, `STATUS`, `STAT`, `PSTATE`, `PWRUP_TIME`, `CAL`, `DCC`, `RTUNE`, `DFE`, `CTLE`, `VGA`, `ATT`, `SLICER`, `TERM`, `SIGDET`, `LBERT`, `OCLA`, and `ATB`.

## Control Flow

This header has no runtime control flow. It shapes runtime behavior indirectly:

1. A companion DPCS 4.2.3 offset header defines register addresses or indirect indexes for CR1 SUPX/LANEX registers.
2. This file supplies the field shift and mask constants for those registers.
3. AMD display code token-pastes register/field names into generated register tables or helper macros.
4. Runtime register helpers perform read/modify/write, polling, decode, interrupt/status clearing, and indirect CR-bank access against the DPCS hardware.

Actual sequencing lives in the display driver and firmware/hardware state machines, not here. The sequences implied by this chunk include PLL power-up and lock, SSC configuration, bandgap/reference power-up timing, RTUNE calibration, lane ownership override, TX/RX pstate transitions, DCC programming, RX VCO/CDR/DPLL calibration, RX adaptation, RX statistics collection, MPHY low-speed operation, signal detect, and analog TX/RX override/readback.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It names hardware-visible fields whose state is defined by silicon and access path. Some fields are controls, some are readback/status, some are request/ack handshakes, and some may be latched, self-clearing, write-one-to-clear, or reserved.

Hardware state represented by this range includes:

- CR1 SUPX MPLLA/MPLLB analog and digital state for enable, reset, calibration, feedback clocks, power-up/lock status, timers, DAC values, SSC type, PMIX, and PLL/charge-pump/filter tuning.
- Clock/reset and RTUNE state for bandgap/reference timing, impedance tuning setpoints, measured RTUNE results, debug counters, and TX calibration codes.
- CR1 LANEX ownership and lane state for override inputs, ASIC mirrors, request/ack status, lane rate/width/pstate, data enable, resets, TX/RX analog enables, loopback, detect-RX, and MPLL selection.
- TX/RX power state, power-up timing, DCC DAC, clock alignment, LBERT, RX VCO calibration, CDR/DPLL, and RX adaptation state.
- RX observation state for statistics match/mask/control registers, sample counts, counters, stop controls, and calibration comparator clocks.
- Digital-to-analog and analog readback/override state for TX equalization/termination/DCC and RX power, VCO, signal detect, termination, DAC, slicer, scope, IQ, MPHY, and status paths.

Persistence is hardware-defined. Values may last until the next modeset, link retrain, hotplug handling path, suspend/resume, GPU reset, ASIC reset, power-gating transition, or firmware/hardware state-machine rewrite. This header does not document reset defaults, legal values, access permissions, read side effects, write-one-to-clear behavior, polling deadlines, or ordering rules.

## Dependencies And Integration Points

This generated header must stay synchronized with the DPCS 4.2.3 register database and the matching offset header under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`. Consumers assume exact register and field spelling because generated AMDGPU Display Core register tables and helper macros often depend on token-pasted names.

Integration points include:

- The companion DPCS 4.2.3 offset header and adjacent chunks of this same shift/mask file.
- AMDGPU Display Core resource, link, PHY, encoder, transmitter, and link-training code that selects ASIC-specific DPCS register tables.
- Register access helpers that program DisplayPort/HDMI/USB-C/DP-alt PHY paths, PLLs, lane power states, TX equalization, RX adaptation, DCC/VCO/CDR/DPLL calibration, signal detection, and debug paths.
- Hardware or firmware owners that arbitrate the same override/value pairs, request/ack pairs, done/status bits, and calibration engines.
- Diagnostics using OCLA, LBERT, ATB, debug counters, and RX statistics registers.

The chunk crosses semantic boundaries: the first lines complete only the shift/mask tail of `DPCSSYS_CR1_SUPX_ANA_MPLLA_OVRD`; the main body spans complete SUPX and LANEX digital groups; the final lines start `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD` but do not include its remaining masks or later analog TX/RX registers.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly and cause link-training failures, display blanking, unstable PHY operation, or board-specific regressions.
- The file is generated. Manual edits risk divergence from AMD's register source, companion offset headers, firmware expectations, and silicon documentation.
- Chunk boundaries split registers. `DPCSSYS_CR1_SUPX_ANA_MPLLA_OVRD` begins before this slice, and `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD` continues after it; a final report should reconcile those register groups before making complete-register claims.
- Override-enable and override-value fields are easy to mix up. Incorrect programming can force PLLs, pstate/rate/width, resets, data enables, loopback, termination, TX EQ, RX adaptation, CDR/VCO, DFE/CTLE/VGA/ATT, MPHY, or signal-detect behavior away from hardware or firmware ownership.
- Request/ack, done, status, counter, and calibration fields are sequencing-sensitive. Bad definitions can cause false readiness, timeouts, missed events, stuck pstate transitions, or diagnostics that read plausible but wrong values.
- Analog tuning fields are often sensitive to link rate, board routing, retimers, cable/sink characteristics, and voltage/temperature corners. Problems may only reproduce under specific DisplayPort/HDMI modes or suspend/resume/retrain paths.
- Reserved and split `RESERVED_*` fields appear throughout the range. Driver code should not repurpose them without an authoritative programming guide for the exact ASIC stepping.
- Generated spellings are API. Names such as `TRESH`, `TUNNING`, numbered split fields, and mixed upper/lower case must remain exact for token-pasted users.
- Repeated A/B PLL, TX/RX, and override/status families make copy/paste mistakes plausible. Mixing CR1 LANEX masks with another CR, another lane, or another DPCS generation may still compile if names are similar elsewhere.

## Test Signals

Useful validation should combine generated-header checks with hardware-oriented display tests:

- Build AMDGPU display configurations that include DPCS 4.2.3 support. Missing or renamed macros should surface in register table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.3 register database and verify that complete fields have matching `__SHIFT`/`_MASK` pairs, accounting for the split first and last registers.
- Cross-check every complete register group in this range against the companion DPCS 4.2.3 offset header.
- Diff repeated MPLLA/MPLLB, TX/RX, ASIC override/mirror, and status/readback families against neighboring CR/lane generations to catch generator drift while allowing intentional hardware differences.
- Exercise DisplayPort/HDMI/USB-C display bring-up, link-rate changes, lane-count changes, hotplug, modeset, blank/unblank, suspend/resume, GPU reset, and link retraining on hardware using this DPCS generation.
- Watch kernel logs, register dumps, and debug traces for PLL lock/power-up failures, RTUNE anomalies, request/ack timeouts, stuck reset/data-enable/clock overrides, RX adaptation failures, CDR/DPLL/VCO calibration failures, signal-detect instability, DCC calibration problems, LBERT errors, and RX statistics counters that do not advance or stop correctly.
- Decode known-good register dumps with these masks and compare pstate, power timing, PLL, RTUNE, TX termination/EQ/DCC, RX ATT/VGA/CTLE/DFE/slicer/CDR/DPLL/VCO, MPHY, signal-detect, OCLA/LBERT, and analog ATB fields against hardware documentation or reference tools.
- Treat OCLA, LBERT, ATB, ATE, and forced analog/debug override paths as controlled diagnostics; test plans should ensure normal firmware/hardware ownership is restored afterward.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR1_SUPX_ANA_MPLLA_OVRD`, including the register comment and any mask definitions before `DPCSSYS_CR1_SUPX_ANA_MPLLA_OVRD__OVRD_ENABLE__SHIFT`. This chunk completes the visible tail of that register and then covers complete SUPX analog/digital and LANEX digital groups.

The next chunk should complete `DPCSSYS_CR1_LANEX_ANA_TX_PWR_OVRD` after `CLK_EN_REG`, then continue the CR1 LANEX analog TX/RX definitions. The merge lane should preserve these boundaries and avoid treating either split register as complete within this chunk alone.
