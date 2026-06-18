# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 46184-48595

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice. It provides preprocessor constants that describe bit positions and masks for DPCS CR2 lane registers; it does not contain executable driver logic. AMDGPU display code combines these constants with the companion DPCS offset header and register access helpers so PHY, link, power, calibration, adaptation, debug, and status fields can be programmed without open-coded bit arithmetic.

The requested range contains 2,412 lines, 2,170 `#define` statements, 1,167 `__SHIFT` macros, 1,003 `_MASK` macros, and 242 register comment boundaries. It starts in the middle of `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT`, completes the rest of CR2 lane 1 digital analog-output and analog TX/RX fields, then covers a large CR2 lane 2 block: digital ASIC override and mirror registers, TX/RX power-control and calibration registers, CDR/DPLL/adaptation/statistics registers, MPHY controls, digital-to-analog override/status registers, and the beginning of lane 2 analog TX fields. The final line is inside `DPCSSYS_CR2_LANE2_ANA_TX_ATB1`; the rest of that register continues in the next chunk.

Although the source path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, global variables, locks, allocations, direct MMIO operations, or exported symbols in this range. Its public interface is the generated macro pair convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index of a field.
- `<REGISTER>__<FIELD>_MASK`: mask for that field in the register value.

The main macro groups in this chunk are:

- `DPCSSYS_CR2_LANE1_DIG_ANA_*`: tail definitions for lane 1 digital-to-analog output and status fields. These include TX termination code, TX termination clock pulse/self-clear control, TX equalization override fields, RX control and power override outputs, RX VCO/CDR override outputs, RX calibration and DAC controls, RX AFE ATT/VGA/CTLE fields, scope and slicer controls, IQ phase/sense controls, signal-change strobes, analog status readback, RX termination, MPHY, signal-detect, TX DCC DAC override, and TX fast-start/loopback/ACJTAG controls.
- `DPCSSYS_CR2_LANE1_ANA_TX_*` and `DPCSSYS_CR2_LANE1_ANA_RX_*`: lane 1 analog TX/RX register fields for measurement override, TX power override, alt bus and ATB controls, DCC DAC/control, termination, clock override, TX miscellaneous/reserved registers, RX clock/CDR/deserializer, slicer, power, squelch, calibration, analog test-bus measurement, forced ATB value, and reserved fields.
- `DPCSSYS_CR2_LANE2_DIG_ASIC_*_OVRD_IN_*`: lane 2 digital ASIC override inputs for lane loopback, TX request/pstate/rate/width/MPLL/data-enable, TX main/pre/post cursor and HDMI mode, detect-RX, polarity, low-power detect, reset, RX request/data-enable/pstate/rate/width, RX CDR/VCO, DFE/CTLE/VGA/ATT/slicer/adaptation settings, PH2 calibration, ATE, signal-detect, SQ, MPHY, and termination controls.
- `DPCSSYS_CR2_LANE2_DIG_ASIC_*_ASIC_IN_*` and `*_ASIC_OUT*`: lane 2 non-override mirror fields for TX/RX request/ack, reset, data enable, pstate/rate/width, loopback, RX adaptation, CDR/VCO, equalization, RX termination, valid/adaptation status, and detect-RX results.
- `DPCSSYS_CR2_LANE2_DIG_TX_PWRCTL_*`: TX pstate definitions for P0/P0S/P1/P2, TX power-up timing windows, DCC CR bank address/data access, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR2_LANE2_DIG_RX_PWRCTL_*`: RX pstate definitions and power-up timers for request, data-enable, AFE/clock/CDR/deserializer/DFE, fast start, reset, clocking, and loopback behavior.
- `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_*`, `DPCSSYS_CR2_LANE2_DIG_RX_CDR_*`, and `DPCSSYS_CR2_LANE2_DIG_RX_DPLL_*`: VCO calibration enable/reset/range/done/status/timing fields, CDR control and status fields, and DPLL frequency and frequency-bound fields.
- `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration and status fields for adaptation enable/delay, ATT/VGA/CTLE, DFE taps, slicer offsets, DAC-control muxes, adaptation reset, and CR-bank address/data access.
- `DPCSSYS_CR2_LANE2_DIG_RX_STAT_*`: RX pattern/mask/match controls, statistic source controls, sample and statistic counters, stop controls, clock controls, and calibration-comparator clock controls.
- `DPCSSYS_CR2_LANE2_DIG_MPHY_*`: MPHY RX PWM polarity, low-speed termination count, and analog PWM clock-stability count fields.
- `DPCSSYS_CR2_LANE2_DIG_ANA_*`: lane 2 digital-to-analog output and readback fields for TX analog enable/reset/rate/clock/termination/EQ, RX analog control/power/VCO/calibration/DAC/scope/slicer/IQ, analog status, MPHY, signal-detect, TX DCC DAC, and TX fast-start/loopback/ACJTAG controls.
- `DPCSSYS_CR2_LANE2_ANA_TX_*`: beginning of lane 2 analog TX fields for override measurement, power override, alt bus, and the first ATB measurement bits.

Field-name patterns encode the hardware intent: `*_OVRD_EN`, `*_OVRD_OUT`, `*_ASIC_IN`, `*_ASIC_OUT`, `REQ`, `ACK`, `DONE`, `STATUS`, `PSTATE`, `PWRUP_TIME`, `CAL`, `DCC`, `CDR`, `DPLL`, `VCO`, `DFE`, `CTLE`, `VGA`, `ATT`, `SLICER`, `TERM`, `SIGDET`, `MPHY`, `LBERT`, `OCLA`, `ATB`, `RESERVED`, and `NC`.

## Control Flow

This header has no runtime control flow. It affects runtime behavior only when included by AMD display code:

1. The matching `dpcs_4_2_3_offset.h` header provides register indexes such as CR2 lane 1 digital analog registers around `0x11a0` and CR2 lane 2 registers beginning at `0x1200`.
2. This shift/mask header provides the bit layout for those register names.
3. DC resource and PHY/link code token-pastes or table-expands offset, shift, and mask names into register descriptors.
4. Runtime register helpers perform read/modify/write, polling, and decode operations against DPCS hardware.

The operational sequencing is external to this file. The named fields participate in TX/RX pstate entry, reset and data-enable changes, link-rate and width programming, MPLL selection, TX equalization and termination programming, RX adaptation and equalization, CDR/VCO/DPLL calibration, DCC DAC programming, request/ack polling, scope/statistics capture, and debug or test-bus flows.

## State And Persistence Behavior

This chunk stores no software state and persists nothing itself. It names hardware-visible state bits whose lifetime and access semantics are defined by the DPCS block, not by this header.

The state represented by these definitions includes:

- Lane 1 digital-to-analog outputs and analog TX/RX controls for TX termination/EQ/DCC, RX power/control/VCO/calibration/DAC/slicer/scope/IQ/signal-detect, analog status, MPHY, and analog test-bus paths.
- Lane 2 digital override state for forcing or observing TX/RX request, pstate, rate, width, reset, data enable, clock readiness, detect-RX, polarity, MPLL source, loopback, RX termination, RX CDR/VCO, equalization/adaptation, PH2 calibration, MPHY, and signal-detect settings.
- Lane 2 TX/RX power state definitions, including per-pstate enable bits, timing counters, fast-start behavior, DCC control, clock alignment, and LBERT controls.
- Lane 2 calibration and adaptation state for VCO, CDR, DPLL, RX ATT/VGA/CTLE/DFE/slicer, DAC selectors, and adaptation reset.
- Lane 2 status and debug capture state for RX pattern matching, statistic counters, sample counters, scope delay, counter stop, clocking, OCLA/LBERT, MPHY, and analog ATB measurement controls.

Values may be transient, latched, read-only, write-one-to-clear, self-clearing, retained across link reconfiguration, or lost across power-gating, suspend/resume, GPU reset, or ASIC reset depending on the specific register. This header does not document reset values, legal encodings, access widths, ownership, volatility, or required write ordering.

## Dependencies And Integration Points

The direct include site found for this generated DPCS 4.2.3 mask header is `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which also includes `dpcs_4_2_3_offset.h`. That ties these macros to DCN 3.1.6 resource initialization and register-table construction.

Important integration points are:

- The companion DPCS 4.2.3 offset header under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`; complete register names in this chunk should have matching `ixDPCSSYS_CR2_*` offset definitions.
- Adjacent generated DPCS and DCN mask headers. Similar DPCS 4.2.0, DPCS 4.2.2, and DCN 4.1.0 generated headers contain corresponding CR2 lane definitions, which are useful for drift checks but must not be mixed at build time.
- AMDGPU Display Core resource, PHY, link, encoder, and register-helper layers that consume generated offset/mask pairs for DisplayPort/HDMI lane bring-up, link training, hotplug, modeset, power management, and diagnostics.
- Firmware and hardware state machines that own request/ack, pstate, reset, calibration, adaptation, and status fields when software has not explicitly enabled overrides.

The chunk crosses semantic boundaries. Lines 46184-46791 complete lane 1 digital analog-output and analog TX/RX field definitions. Line 46792 begins the CR2 lane 2 digital ASIC override/mirror block. Line 47264 begins lane 2 TX/RX power-control, calibration, CDR/DPLL, adaptation, statistic, and MPHY fields. Line 48182 begins lane 2 digital-to-analog output/status fields. Line 48563 moves into lane 2 analog TX fields, and line 48595 stops before `DPCSSYS_CR2_LANE2_ANA_TX_ATB1` is complete.

## Risks And Edge Cases

- These are untyped preprocessor constants. A bad mask or shift can compile cleanly while causing subtle display PHY failures.
- The file is generated. Manual edits can diverge from AMD's register database, companion offset headers, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines continue `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT` from the previous chunk, and the final lines start but do not complete `DPCSSYS_CR2_LANE2_ANA_TX_ATB1`.
- Override value fields and override-enable fields are adjacent throughout the range. Confusing them can force clocks, resets, pstate/rate/width, MPLL selection, data enable, loopback, termination, CDR/VCO behavior, adaptation, or analog controls away from normal hardware or firmware ownership.
- Request, acknowledge, valid, done, status, counter, and self-clear fields are sequencing-sensitive. Incorrect definitions can manifest as link-training timeouts, missed readiness, false readiness, stuck calibration, stale counters, or hangs during lane power transitions.
- Analog tuning fields such as TX EQ pre/post/main, TX termination, DCC DAC, RX ATT/VGA/CTLE/DFE/slicer, CDR/DPLL/VCO, signal-detect thresholds, squelch settings, and MPHY PWM/termination can fail only at specific link rates, boards, sink devices, cables, or voltage/temperature corners.
- Reserved and `NC` masks are common. Software should not repurpose them without authoritative silicon documentation for the exact ASIC stepping.
- Generated spelling and case are API surface. Names such as `sq_ctrl_tresh`, split field suffixes like `_13_0`, and repeated lane-specific prefixes must remain exactly as generated for token-pasted users.
- Lane 1/lane 2 and DPCS-generation names are highly repetitive. Accidentally combining a CR2 lane 1 mask with a lane 2 offset, or using DPCS 4.2.3 masks with another DPCS generation, may compile if names overlap but program the wrong layout.

## Test Signals

Useful validation should combine generated-header checks with real display hardware coverage:

- Build AMDGPU display configurations that include DCN 3.1.6 and DPCS 4.2.3. Missing, renamed, duplicated, or malformed macros should be caught by register-table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.3 register database and verify that complete fields have expected `__SHIFT` and `_MASK` definitions; account for the split first and last registers.
- Cross-check complete register groups against `dpcs_4_2_3_offset.h` so every full register in this chunk has a corresponding offset macro.
- Run structural diffs against adjacent generated DPCS 4.2.x and DCN headers to detect generator drift while allowing intentional ASIC differences.
- Exercise DisplayPort/HDMI hotplug, link bring-up, link-rate changes, lane-count changes, modeset, blank/unblank, suspend/resume, and GPU reset on hardware using this DPCS generation.
- Monitor driver logs and register dumps for request/ack timeouts, stuck reset/data-enable/clock override bits, RX adaptation failure, CDR/DPLL/VCO calibration failure, DCC calibration issues, unstable signal detect, LBERT errors, and RX statistic counters that do not progress or clear as expected.
- Decode known-good register dumps with these masks and compare against silicon documentation or reference tooling for pstate, power timing, TX termination/EQ/DCC, RX ATT/VGA/CTLE/DFE/slicer, CDR/DPLL/VCO, MPHY, signal-detect, scope/statistic, and ATB fields.
- Treat OCLA, LBERT, ATE, ACJTAG, loopback, and analog test-bus paths as diagnostic-only signals; forcing these bits can bypass normal PHY control.

## Cross-Chunk Notes

The previous chunk should contain the register comment and earlier fields for `DPCSSYS_CR2_LANE1_DIG_ANA_TX_TERM_CODE_OVRD_OUT`; this chunk starts at `TX_DRV_SRC__SHIFT` and finishes that register's masks before continuing through lane 1 digital analog-output and analog RX/TX tail fields.

The next chunk should complete `DPCSSYS_CR2_LANE2_ANA_TX_ATB1` by adding the remaining shifts and masks after `MEAS_ATB_VDDH`, then continue lane 2 analog TX/RX fields. The final per-file merge should reconcile these split register groups before making whole-file coverage claims.
