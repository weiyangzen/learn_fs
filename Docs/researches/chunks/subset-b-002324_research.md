# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 85816-88172

## Scope

This chunk covers lines 85816-88172 of the generated AMD DPCS 4.2.0 shift/mask header. It contains 2,141 preprocessor definitions and register-block comments for DPCSSYS CR4 lane metadata. The range begins with the tail masks for `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0`, continues through lane 0 analog TX registers, and then covers a large lane 1 surface: digital ASIC override/actual fields, TX/RX power control, RX VCO/CDR/adaptation/statistical monitor controls, MPHY and analog TX/RX override/status fields, and the beginning marker for `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF`.

This file is declarative generated data. It exports constants only; it has no functions, structs, loops, allocations, locking, or direct MMIO access.

## Purpose

The purpose of this chunk is to describe bit positions and masks for low-level DPCS/PHY lane registers used by AMD display code. Each field is represented by a `__SHIFT` macro and a `_MASK` macro. Consumers combine these field constants with offsets from the matching `dpcs_4_2_0_offset.h` header and register helper macros to perform read-modify-write operations against 16-bit CR-space registers.

The main hardware concerns represented here are:

- Lane 0 analog TX diagnostics and override fields after the preceding lane 0 status block.
- Lane 1 digital ASIC override inputs and outputs for TX, RX, loopback, reset, request/acknowledge, rate, width, power state, equalization, CDR/VCO load values, MPHY/PWM mode, and cross-lane/master-lane clock handshakes.
- Lane 1 TX power-state sequencing for P0, P0S, P1, and P2, including reference generator, VCM hold, analog/digital clocks, reset, serial/data enable, receiver detection, VBOOST, and DCC compensation calibration.
- Lane 1 RX power-state sequencing, VCO calibration, CDR/DPLL controls, adaptation configuration/status, RX statistical pattern matching/counters, MPHY low-speed controls, analog TX/RX override controls, analog status, and analog RX calibration/power/signal-detect controls.

## Important API Surface

There are no callable APIs or local types. The exported API is the macro namespace for this line range.

Important lane 0 macro families in this chunk include:

- `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0` tail masks for TX clock-shift acknowledgement, RX detect results, loopback, RX analog calibration/scope data, TX DCC calibration result, and TX EQ mux status. The corresponding shifts started in the prior chunk.
- `DPCSSYS_CR4_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT*` for TX analog DCC calibration range, comparator enable, control value, control select, clock compensation, and override-enable gates.
- `DPCSSYS_CR4_LANE0_DIG_ANA_TX_OVRD_OUT_2` and `DPCSSYS_CR4_LANE0_ANA_TX_*` for TX fast start, clock loopback, AC JTAG enable, measurement ATB paths, TX power override, alternate bus/JTAG routing, DCC DAC values, termination code controls, clock overrides, VREF/DCC-range controls, peaking/slew/inversion settings, and reserved analog TX fields.

Important lane 1 digital ASIC macro families include:

- `DPCSSYS_CR4_LANE1_DIG_ASIC_LANE_OVRD_IN` and `...LANE_ASIC_IN` for TX-to-RX serial loopback, RX-to-TX parallel loopback, lane override enable, and RX AC JTAG.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_TX_OVRD_IN_0` through `_5` and `...TX_ASIC_IN_0` through `_2` for TX request, power state, rate, width, MPLL selection, data enable, main/pre/post cursor values, asynchronous drive/data, reset, clock ready, invert, LPD, HDMI/MPHY/DC-coupled modes, FIFO mode, receiver-detect request, and master-lane clock/repeater synchronization fields.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_TX_OVRD_OUT*` and `...TX_ASIC_OUT` for TX acknowledge, detect-RX result, repeater enable, digital clock enable/state, shift control, and shift-ack status.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_RX_OVRD_IN_0` through `_6` and `...RX_ASIC_IN_*` for RX request/data enable/pstate/rate/width, VCO/ref load values, CDR track and SSC enable, alignment, clock shift, disable, LPD, inversion, AFE/DFE adaptation, termination enable/ACDC, reset, PWM clock selection, LS/LCC termination, and PWM enable overrides.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_RX_OVRD_EQ_IN_*` and `...RX_EQ_ASIC_IN_*` for ATT, AFE gain, CTLE boost, DFE tap1/tap2, and EQ override enable.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_RX_OVRD_OUT_0` and `...RX_ASIC_OUT_0` for RX acknowledge, valid/adaptation status, async data, and weak-keeper outputs.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_OCLA` for RX DWORD OCLA clock/data enable.

Important lane 1 TX/RX control macro families include:

- `DPCSSYS_CR4_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0`, `_P0S`, `_P1`, and `_P2` for per-power-state TX analog and digital enable/reset sequencing. P2 adds `TX_P2_ALLOW_VBOOST`.
- `DPCSSYS_CR4_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_5` for TX refgen/clock timing, VCM hold timing, VBOOST disable timing, RX-detect timing, reset timing, serial-enable timing, skip/fast flags, and DTB selection.
- `DPCSSYS_CR4_LANE1_DIG_TX_PWRCTL_DCC_*` for DCC CR bank address/data and DCC DAC control/range/select/ack/address handshakes.
- `DPCSSYS_CR4_LANE1_DIG_TX_CLK_ALIGN_TX_CTL_0` and `...TX_LBERT_CTL` for TX UI-shift alignment, FIFO bypass, and lane BERT pattern/error injection control.
- `DPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, `_P0S`, `_P1`, and `_P2` for RX AFE, clock regulator, analog clock, deserializer, CDR, VCO reset/calibration/continuous-calibration, and digital clock enable states.
- `DPCSSYS_CR4_LANE1_DIG_RX_VCOCAL_*` for RX VCO calibration control, frequency-tune calibration, startup/update/counter timing, final counter status, VCO direction/correctness flags, and calibration-done state.
- `DPCSSYS_CR4_LANE1_DIG_RX_CDR_*`, `...RX_DPLL_FREQ`, and `...RX_DPLL_FREQ_BOUND_*` for phase detector controls, SSC on/off counters, DPLL gain overrides, PHUG/FRUG status, frequency value, and upper/lower frequency bounds.
- `DPCSSYS_CR4_LANE1_DIG_RX_ADPTCTL_*` for RX adaptation algorithm timing, enable masks, CTLE/VGA/ATT/DFE thresholds and mu values, reset controls, adapted code status for ATT/VGA/CTLE/DFE taps 1-5, slicer and DAC offset controls, DAC-control selects, and CR bank address/data access.
- `DPCSSYS_CR4_LANE1_DIG_RX_STAT_*` for RX pattern load/mask/match controls, statistic control, sample count, statistic counters 0-6, calibration comparator clock control, and statistic stop.
- `DPCSSYS_CR4_LANE1_DIG_MPHY_RX_*` for PWM polarity/data polarity, low-speed termination LCC count, and analog PWM clock stable count.

Important lane 1 analog macro families include:

- `DPCSSYS_CR4_LANE1_DIG_ANA_TX_OVRD_OUT` and `...TX_TERM_CODE*` for TX analog clock/data/refgen/VCM/word-clock/MPLL/reset/serial/rate/rx-detect overrides, TX termination code, driver source, and self-clearing termination-clock behavior.
- `DPCSSYS_CR4_LANE1_DIG_ANA_TX_EQ_OVRD_OUT_0` through `_5` for TX EQ load clock, leg pull enables/directions, EQ mux selection, pre-cursor and post-cursor values, and EQ override enable.
- `DPCSSYS_CR4_LANE1_DIG_ANA_RX_CTL_OVRD_OUT`, `...RX_PWR_OVRD_OUT`, and `...RX_VCO_OVRD_OUT_*` for RX analog data rate, word/div4 clocks, DFE/adaptation enable, loopback clock, AFE/clock/CDR/deserializer power, fast start, CDR VCO enable/startup, frequency tuning, counter enable/clock/power-down, low-frequency mode, and self-clearing frequency-tune clock.
- `DPCSSYS_CR4_LANE1_DIG_ANA_RX_CAL`, `...DAC_CTRL*`, `...AFE_ATT_VGA`, `...AFE_CTLE`, `...SCOPE`, `...SLICER_CTRL`, `...IQ_*`, and update-clock registers for RX calibration muxes, DAC controls, AFE gain/attenuation/CTLE, scope capture, slicer control, IQ phase/sense, and self-clearing analog-update strobes.
- `DPCSSYS_CR4_LANE1_DIG_ANA_STATUS_0` and `_1` for analog result/status readback, including RX detect, loopback, RX calibration/scope, TX DCC calibration result, TX EQ mux, and RX VCO counter.
- `DPCSSYS_CR4_LANE1_DIG_ANA_RX_TERM_CODE*`, `...MPHY_OVRD_OUT`, `...SIGDET_OVRD_OUT_*`, `...TX_DCC_DAC_OVRD_OUT*`, and `...TX_OVRD_OUT_2` for RX termination code, MPHY squelch/PWM overrides, signal-detect voltage/reference/comparator/mux controls, TX DCC overrides, and TX fast-start/loopback/AC-JTAG.
- `DPCSSYS_CR4_LANE1_ANA_TX_*` for the analog-side TX measurement, power, alternate bus, ATB, DCC DAC/control, termination code/control, clock, VREF/DCC range, peaking/slew/inversion, and reserved fields.
- `DPCSSYS_CR4_LANE1_ANA_RX_CLK_*`, `...RX_CDR_DES`, `...RX_SLC_CTRL`, `...RX_PWR_CTRL*`, `...RX_SQ`, and `...RX_CAL*` for analog-side RX CDR/startup/clock, IQ phase, loopback clock, word-clock/phase-detector, slicer, AFE/DFE/deserializer/loopback/fast-start power overrides, squelch response/threshold, and calibration mux/DFE tap enable controls.

The final line in scope is the comment for `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF`; its field definitions are outside this chunk and belong to the next chunk.

## Control Flow

There is no executable control flow in this header range. The implied use flow is:

1. AMD display code selects a DPCS CR4 lane 0 or lane 1 register offset from `dpcs_4_2_0_offset.h`.
2. A register helper reads or writes the CR-space register through the display resource/link path.
3. Callers isolate or set a field by applying the `_MASK` and `__SHIFT` constants from this header.
4. Override-enable fields gate whether software-provided values replace hardware state-machine values.
5. Hardware returns status through acknowledge, result, calibration, counter, DPLL/CDR, VCO, adaptation, and statistic fields.

The naming indicates several hardware handshakes: TX/RX request and acknowledge, DCC DAC request and acknowledge, analog self-clearing update clocks, VCO calibration done/correct/up signals, adaptation ASM1 done bits, statistic sample-count done bits, and cross-lane master/other-lane clock shift acknowledgements.

## State And Persistence

The header stores no software state and persists nothing. The defined constants describe hardware-backed state and control fields:

- Override registers can force TX/RX reset, request, power state, rate, width, data enable, clock enable, loopback, termination, VCO/CDR tuning, EQ/cursor values, DCC calibration, signal detect, MPHY/PWM, and analog calibration paths.
- Power-control registers encode the desired analog/digital enable state for TX and RX power states and timing registers encode hardware sequencing delays.
- Status registers expose transient hardware results such as RX/TX acknowledgements, RX detect, CDR/VCO state, VCO calibration result, DPLL bounds, adapted equalizer codes, statistic counters, and analog calibration/scope outputs.
- Self-clearing control bits and update clocks are stateful at the hardware register level. Misusing their masks can trigger repeated updates or prevent intended updates.
- Reserved and `NC*` masks occupy many upper-bit regions. Correct consumers should preserve those bits unless the silicon programming guide explicitly defines a full-register write.

Durable effects are limited to hardware programming during display link bring-up, retraining, power management, diagnostics, lab/ATE modes, and recovery. The C preprocessor constants themselves do not allocate memory or retain runtime values.

## Dependencies And Integration Points

This header depends only on the C preprocessor and the larger include guard of `dpcs_4_2_0_sh_mask.h`. Its field constants are useful only with the matching DPCS 4.2.0 offset header.

In this source tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`. That is the visible in-tree integration point tying this generated register contract to DCN 3.1 display resource setup. Runtime access is expected to go through AMD display register helper infrastructure rather than through this header directly.

The constants are ASIC-version-specific and must remain synchronized with:

- `dpcs_4_2_0_offset.h`, which provides the register addresses.
- AMD's generated register database or silicon programming reference for DPCS 4.2.0.
- Adjacent generated DPCS headers for related versions where the driver expects compatible lane layouts.
- Link/PHY code that configures DisplayPort, embedded PHY, MPHY, low-speed/PWM modes, DCC calibration, CDR/VCO calibration, and RX adaptation.

## Risks

- A single incorrect mask or shift can silently misprogram PHY control fields. The highest-risk fields in this chunk are reset, power enable, clock enable, VCO/CDR tuning, TX EQ/cursor, termination, DCC calibration, adaptation, and self-clearing update strobes.
- The lane 1 register set is highly repetitive and mirrors patterns from other lanes and DPCS versions. Generated-data drift can create lane-specific failures that compile cleanly.
- Many fields are override gates paired with values. Setting a value without the matching override-enable bit, or leaving an override enabled after diagnostics, can cause hard-to-debug link training and power-state behavior.
- Reserved/NC bits are widespread. Full-register writes that do not preserve reserved bits risk changing undocumented hardware behavior.
- Some fields represent diagnostic or lab features such as OCLA, LBERT, ATB, JTAG, ATE-style measurement, scope, and loopback. Accidental use in normal display paths can alter signal integrity or hide real link failures.
- Timing fields for TX power-up and RX VCO/CDR/adaptation are hardware-sequencing sensitive. Incorrect values can lead to intermittent bring-up failures rather than deterministic build-time errors.
- This chunk begins and ends at generated-file boundaries: the first five lane 0 status masks depend on prior-chunk shift definitions, and the final `ANA_RX_ATB_REGREF` heading lacks its fields until the next chunk. The merge lane must reconcile these boundaries before making complete whole-register claims.

## Test Signals

Useful validation signals include:

- Build or preprocess AMDGPU DCN 3.1 display code that includes `dpcs_4_2_0_sh_mask.h`, especially `dcn31_resource.c`, to catch missing or renamed macros.
- Generated-header consistency checks that verify every non-boundary field has both a `__SHIFT` and `_MASK`, masks match their shifts and widths, and masks within a register do not overlap except where reserved/NC fields intentionally cover unused regions.
- Diff checks against AMD's authoritative DPCS 4.2.0 register data and against sibling generated headers for expected lane-to-lane structural equivalence.
- Hardware or emulator tests for DisplayPort link bring-up, link retraining, TX/RX power-state transitions, receiver-detect, lane reset/request handshakes, CDR/VCO calibration, DPLL frequency bounds, RX adaptation, DCC calibration, termination, MPHY/PWM low-speed behavior, loopback/LBERT diagnostics, and statistic counter reads.
- Failure signatures to watch for include lane 1-only link training timeouts, missing TX/RX ACK/VALID status, stuck VCO calibration done/correct/up flags, unstable DPLL/CDR lock, bad adapted CTLE/VGA/DFE codes, RX statistic counters not completing, unexpected signal-detect behavior, and display failures that appear only after power-state transitions.

## Chunk Boundaries

This document intentionally covers only lines 85816-88172 of `dpcs_4_2_0_sh_mask.h`. The previous chunk is needed for the beginning of `DPCSSYS_CR4_LANE0_DIG_ANA_STATUS_0`; the next chunk is needed for `DPCSSYS_CR4_LANE1_ANA_RX_ATB_REGREF` fields and the remaining CR4 lane definitions. The final per-file research document should merge all chunks before presenting complete DPCS 4.2.0 register coverage.
