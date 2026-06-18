# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 86504-88864

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,146 `#define` field-layout macros and 215 register-family comments for the `DWC_E12MP_PHY_X4_NS_X4_2` PCIe/SerDes PHY block. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts at the tail of `DWC_E12MP_PHY_X4_NS_X4_2_SUP_DIG_MPLLB_MPLL_PWR_CTL_CAL_CTRL`, covers the rest of the MPLLB shared/supervisor PHY controls, all of lane 0's digital/analog PHY field definitions, and ends at the `DWC_E12MP_PHY_X4_NS_X4_2_LANE1_DIG_ASIC_TX_ASIC_OUT` register comment before that register's field macros appear. Adjacent chunks are required for a complete view of the preceding MPLLB calibration-control register and the following lane 1 transmit status register.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of AMD's generated NBIO 6.1 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk specifically describes low-level Synopsys/DesignWare-style `DWC_E12MP_PHY_X4_NS_X4_2` PHY state for an x4 PCIe/SerDes instance: MPLL power/calibration and spread-spectrum controls, analog override/test-bus controls, resistor tuning, per-lane ASIC handoff signals, TX/RX power states, RX VCO/CDR/adaptation/equalization, PRBS/LBERT-style test controls, link/statistical counters, and analog TX/RX tuning/status fields. The constants let AMDGPU code decode or compose 16-bit register words without hard-coding bit positions at call sites.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The supervisor/shared section covers MPLLB and shared analog control:

- MPLLB power/calibration controls and status: override select, feedback/digital/PCLK enables, fast power-up/lock, diagnostic/test-bus select, FSM state, calibration-ready/done state, too-slow detection, reset, analog enable, coarse tune, skip-calibration coarse tune, and timing thresholds for VCO stabilization, PCLK enable/disable, VCO power-down, analog power-up, feedback clock enable, and feedback digital-clock disable.
- Spread-spectrum clocking fields: `SSC_SS_PHASE`, `SSC_SS_FREQ_0`, and `SSC_SS_FREQ_1` define dithering, phase, zero-frequency, fractional divider, frequency count, peak frequency, and override bits.
- MPLLA/MPLLB analog controls: `SUP_ANA_MPLLA_*` and `SUP_ANA_MPLLB_*` define miscellaneous regulator fields, analog override bits for enable/calibration/feedback clock/reset, and ATB measurement/override selections.
- Shared tuning/measurement: `SUP_ANA_RTUNE_CTRL`, `SUP_ANA_SWITCH_PWR_MEAS`, `SUP_ANA_SWITCH_MISC_MEAS`, `SUP_ANA_BG`, and `SUP_DIG_RTUNE_*` define resistor tuning controls, power/misc measurement muxes, bandgap trim, RTUNE run/status bits, and RX/TX pull-up/pull-down tune set/status values.

The lane 0 digital ASIC interface section maps the signals exchanged between digital control logic and the lane PHY:

- `LANE0_DIG_ASIC_LANE_OVRD_IN` and `LANE0_DIG_ASIC_LANE_ASIC_IN` define loopback override and actual loopback control signals.
- TX override and ASIC input/output registers define clock-ready, reset, invert, data enable, request, low-power detect, P-state, rate, width, MPLLB select, detect-RX request, disable, beacon, iboost, vboost, main/pre/post cursor values, override-enable bits, TX acknowledge, and detect-RX result fields.
- RX override and ASIC input/output registers define reset, invert, data enable, request, low-power detect, P-state, rate, width, DIV16P5 clock enable, AFE/DFE adaptation enables, reference/VCO load values, CDR track/SSC enable, align enable, clock shift, loss-of-signal threshold/filter, termination enable, termination AC/DC selection, acknowledgement, LOS, adaptation status, and enable-control status.
- RX equalization override and ASIC EQ input registers expose attenuation, VGA1/VGA2 gain, CTLE boost/pole, DFE tap1, EQ override enable, CDR VCO load, and CDR VCO low-frequency select.

The lane 0 power, calibration, and receive-control section covers:

- TX power-state templates for P0, P0s, P1, and P2, with divider clock enables, clock readiness, reset, request/low-power fields, rate/width, PCLK enables, enable/ack status, and power-up timing thresholds.
- RX power-state templates for P0, P0s, P1, and P2, plus RX power-up timing/control fields, covering CDR, align, DFE, AFE, LOS, termination, DIV16P5 clock, reset, request, low-power, data enable, and acknowledgement timing.
- RX VCO calibration controls/status: external load/update/select fields, count window, update-rate controls, VCO reference/load values, coarse-code status, measured count, start/done flags, too-low/too-high flags, overflow/underflow flags, and coarse-code compare state.
- CDR and DPLL controls: proportional/integral gains, second-order frequency gain, pattern filter enables, transition validation, VCO step controls, SSC step size, tracking mode, DPLL frequency, min/max bounds, and CDR lock status.
- Adaptation controls/status: CTLE/VGA/attenuation/DFE enablement, timing/pattern parameters, fast settle, mode toggles, status readback for ATT/VGA/CTLE and DFE taps 1-5, data/error/bypass slicer VDAC offsets, slicer controls, and error slicer levels.
- RX statistic controls/counters: load values, data masks, match controls, statistic mux/control fields, sample count, statistic counters 0-6, compare-clock controls, and additional match/stat control fields.

The lane 0 digital-to-analog and analog register sections cover:

- Digital analog override outputs for TX/RX control, TX term codes, TX equalization, RX control, RX power, RX VCO, RX calibration, DAC control, AFE/CTLE/scope/slicer controls, phase/IQ sense and adjust, analog signal-change enables, and analog status readbacks.
- Lane 0 analog TX override/measurement, power override, alternate bus, ATB, vboost, termination code, iboost code, override clock, and miscellaneous fields.
- Lane 0 analog RX controls for IQ skew, DCC override, power control, ATB regulator/reference/measurement muxes, CDR AFE, miscellaneous override, calibration muxes, termination, slicer control, and regulator ATB fields.

The final section begins lane 1 and repeats the same digital ASIC interface pattern through TX ASIC inputs: lane override, TX override input/output, RX override input/equalization/output, loopback input, and TX ASIC input fields. It stops before the `LANE1_DIG_ASIC_TX_ASIC_OUT` field definitions.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not encode register addresses, reset values, access width, read/write permissions, write-one-to-clear behavior, sequencing requirements, firmware ownership, or hardware side effects. Consumers must combine them with the matching generated address/default metadata and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the NBIO/SMN/PCIe access path appropriate for the target register.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a `DWC_E12MP_PHY_X4_NS_X4_2_*` register address from companion generated NBIO metadata.
2. The code reads a hardware register, extracts fields with the `__SHIFT` and `_MASK` constants, or composes a new register value while preserving unrelated and reserved bits.
3. The decoded values guide PHY bring-up, link training, reset, diagnostics, or error reporting; composed values program PLLs, TX/RX lane state, equalization, calibration, adaptation, loopback, or test modes.

The field names imply several asynchronous hardware flows outside the header: MPLL power-up/calibration state machines, PCLK and VCO stabilization windows, RX VCO calibration, CDR/DPLL lock and tracking, adaptation convergence, LOS detection, per-P-state TX/RX power transitions, loopback/test enablement, and status/statistic counter sampling.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO's PCIe/SerDes PHY registers. Persistence depends on the GPU reset domain, PCIe link reset, PHY reset, power-gating/clock-gating, firmware/BIOS setup, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable control bits, analog trim values, timing thresholds, override enables, calibration requests, P-state templates, TX equalization coefficients, RX equalization/adaptation settings, test/loopback selections, status latches, counters, and analog measurement mux selections. Some fields are likely sampled from live hardware state (`ACK`, `LOS`, `LOCK`, `DONE`, `FSM_STATE`, `ADAPT_STS`, counter fields), while others are control or override inputs.

Because these are low-level PHY fields, stale or incorrect values can affect link availability and signal integrity across reset/resume or lane retraining. Call sites must not infer reset persistence from the mask definitions alone; reset/default behavior is described by hardware documentation and the sibling generated default header.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 6.1 register database and must remain synchronized with sibling headers:

- `nbio_6_1_default.h` contains matching `smnDWC_E12MP_PHY_X4_NS_X4_2_*_DEFAULT` values for the same PHY registers.
- `nbio_6_1_offset.h` and/or `nbio_6_1_smn.h` provide address metadata for NBIO register access paths elsewhere in the generated register set.
- `nbio_6_1_sh_mask.h` consumers rely on AMDGPU's SOC15/NBIO register access and bitfield helper macros to apply these shifts and masks.

Direct include users in this tree include AMDGPU NBIO, virtualization, PSP, display, and power-management code paths through generated ASIC register include stacks. These particular `DWC_E12MP_PHY_X4_NS_X4_2` fields are most relevant to PCIe PHY initialization, lane bring-up, link training recovery, signal tuning, low-power transitions, loopback/BERT diagnostics, and hardware debug tooling rather than high-level file-system behavior.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing code to write the wrong PHY bit, a class of bug that can appear as link-training failure, unstable PCIe links, incorrect equalization, or broken low-power transitions.
- The chunk starts and ends mid-register-family. Whole-file research must reconcile the preceding MPLLB calibration-control fields and the following lane 1 TX output fields from adjacent chunks before treating either register family as complete.
- Many fields are single-bit overrides paired with value bits. Setting the value without the matching override-enable, or leaving an override enabled after diagnostics, can force the PHY away from firmware/hardware-managed behavior.
- Power, reset, PLL, VCO, CDR, adaptation, and statistic fields represent asynchronous hardware state. Polling code needs timeouts and must handle non-convergence, transient statuses, and reset races.
- Reserved masks are explicitly present throughout the chunk. Writers must preserve reserved bits unless the hardware specification says otherwise.
- Lane 0 and lane 1 definitions are mechanically repeated. Copy or generation errors may affect only one lane, producing lane-width, polarity, equalization, or signal-integrity failures that are hard to isolate.
- Analog measurement, ATB, and calibration mux fields can perturb debug visibility or calibration paths if changed in production code.
- TX cursor, iboost/vboost, termination, CTLE/VGA/DFE, slicer, and regulator fields are signal-integrity sensitive. Incorrect values can degrade reliability without causing an immediate software-visible failure.

## Test Signals

- Build AMDGPU with NBIO 6.1 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: each `__SHIFT` should have a compatible `_MASK`, masks should not overlap unexpectedly within a register, reserved fields should fill documented gaps, and lane 0/lane 1 repeated ASIC-interface definitions should match except for the lane number.
- Cross-check register names against sibling default/address headers so every `DWC_E12MP_PHY_X4_NS_X4_2_*` field layout maps to a known register and default value.
- On supported hardware, validate PCIe link bring-up, retraining, link-width/rate negotiation, suspend/resume, and GPU reset recovery with NBIO 6.1 paths enabled.
- Exercise PHY diagnostics where available: loopback, LBERT/error counters, RX statistic counters, LOS detection, CDR/DPLL lock reporting, RX VCO calibration done/fail status, and adaptation status readbacks.
- Validate signal-integrity-sensitive paths by comparing decoded TX cursor/boost/termination and RX CTLE/VGA/DFE/slicer values against expected board/firmware programming across cold boot, warm reset, and resume.
- For any code that writes these fields, review register traces to ensure reserved bits are preserved and override bits are cleared or restored after temporary debug or recovery use.
