# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 90529-92906

## Scope

This chunk covers lines 90529-92906 of the generated AMD DPCS 4.2.0 shift/mask header. It contains 2,121 `#define` entries: 1,061 `__SHIFT` macros and 1,060 `_MASK` macros.

The count imbalance is a chunk-boundary artifact. The range starts with the final mask for `DPCSSYS_CR4_LANE3_DIG_ASIC_TX_OVRD_IN_4`, whose shift and earlier masks are immediately above line 90529. The range ends inside `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN`, after `MSTR_MPLL_OVRD_EN_MASK`; the remaining masks for `TX_ASYNC_EN_OVR_VAL` and `TX_ASYNC_EN_OVR_EN` follow below line 92906.

The content is declarative only. It defines preprocessor constants for register bit positions and masks. There are no C functions, structs, enums, branches, loops, allocations, locks, or local runtime state in this range.

## Purpose

The header gives AMDGPU display code symbolic field definitions for DPCS 4.2.0 CR4 display PHY and controller registers. Consumer code combines these `__SHIFT` and `_MASK` constants with generated register-address headers and AMDGPU/DC register helpers to compose read-modify-write operations against memory-mapped or indirect ASIC registers.

This slice covers three major CR4 areas:

- The tail of CR4 lane 3 controls, including ASIC TX/RX override mirrors, lane ASIC inputs, TX/RX ASIC status, TX power-state sequencing, DCC DAC controls, TX clock alignment, loopback/BERT, RX statistic matching/counters, digital-to-analog TX override outputs, and lane 3 analog TX controls.
- CR4 raw common controls, including MPLLA/MPLLB override and spread-spectrum fields, common control/status, SRAM/ID/OCLA, always-on RTUNE values for multiple lanes, power-gate/supervisor/resource overrides, VREF status, and miscellaneous common configuration.
- CR4 raw lane 0 and the beginning of raw lane 1, including PCS TX/RX override and PCS in/out mirrors, RX adaptation and equalization, FSM fast-calibration/status registers, IRQ status/clear/mask fields, PMA crossbar fields, TX/RX control registers, ATE paths, and the first raw lane 1 TX override register.

## Exported API Surface

There are no callable APIs or local types. The public surface is the generated macro namespace. Important families in this chunk include:

- `DPCSSYS_CR4_LANE3_DIG_ASIC_*`: ASIC-facing lane, TX, and RX fields for TX acknowledgement, DETRX result/request, RX ACK/VALID/adaptation status, loopback, clock-ready, reset, invert, data-enable, request, low-power detect, P-state, rate, width, MPLLB selection, beacon, async TX, vreg bypass, pre/main/post cursor values, and multi-lane clock/shift/master-lane override signals.
- `DPCSSYS_CR4_LANE3_DIG_TX_PWRCTL_*`: TX power-state definitions for P0/P0s/P1/P2, power-up timing windows, and DCC CR-bank/DAC programming fields. These fields name analog reference generation, VCM hold, analog/word clock enables, reset, serial enable, digital clock enable, data enable, RX detect allowance, DCC compensation calibration, and per-phase timeouts.
- `DPCSSYS_CR4_LANE3_DIG_RX_STAT_*`: receiver statistic load, data mask, match controls, statistic controls, sample count, status counters, calibration compare clock control, and stop control fields.
- `DPCSSYS_CR4_LANE3_DIG_ANA_*` and `DPCSSYS_CR4_LANE3_ANA_TX_*`: digital override outputs and analog TX controls for TX request/reset/invert/low-power, rate/width/P-state, clocks, TX async, main/pre/post cursor, vboost/iboost, termination code, equalization, DCC DAC, power measurement, alternate bus, analog test bus, power override, termination update/reset, HDMI/MPHY/DC-coupled modes, and reserved analog tuning windows.
- `DPCSSYS_CR4_RAWCMN_DIG_*`: common digital controls for MPLLA/MPLLB power and overrides, PLL bandwidth and SSC programming, lane FSM extended operation, common control bits, MPLL state, TX calibration code, SRAM init done, OCLA, supervisor analog override, raw PCS and firmware ID codes, AON common RTUNE readbacks, SRAM bitline config, power-gate/resource/supervisor override inputs and outputs, VREF status, reference range override, and miscellaneous common configuration.
- `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_*`: raw lane 0 PCS crossbar fields for TX/RX overrides, PCS in/out mirrors, RX adaptation acknowledgement and figure-of-merit, TX pre/main/post cursor direction, lane number, reserved windows, ATE override, RX equalization and phase-2 calibration controls, TX/RX termination control, and additional ATE TX/RX override registers.
- `DPCSSYS_CR4_RAWLANE0_DIG_FSM_*`: lane 0 FSM override, memory/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration controls, supervisor and TX fast-state controls, common-calibration status, continuous calibration/adaptation states, flags, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR4_RAWLANE0_DIG_IRQ_CTL_*`: status, clear, and mask fields for RX reset/request/rate/P-state/adaptation request/adaptation disable, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, and TX reset/request interrupts.
- `DPCSSYS_CR4_RAWLANE0_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*`: PMA lane/supervisor/TX/RX override and input/output mirrors, lane RTUNE, MPHY override, RX adaptation override, TX/RX FSM controls, TX clock and DCC continuous status, loss-of-signal masking, RX data-enable override, off-cancel/adaptation continuous status, and OCLA taps.
- `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN_*`: the opening raw lane 1 TX override fields for P-state, LPD, width, rate, MPLLB select, MPLL enable, override enable, master MPLLA/MPLLB state, and master MPLL override enable.

## Register Areas Covered

The lane 3 ASIC and TX power-control area is the per-lane interface between display link logic and the DPCS PHY. It exposes both normal ASIC inputs/outputs and explicit override outputs. The field names separate value bits from adjacent override-enable bits, especially around TX ACK, DETRX, RX ACK/adaptation status, clock-ready, reset, low-power detect, master-lane coordination, and clock-shift handshakes. The TX P-state registers describe the electrical enable set for each power state, while the power-up timing registers provide timeout/count fields for analog reference, VCM, clocks, reset, serial/data enable, RX detect, and DCC calibration stages.

The lane 3 RX statistic and analog TX area is a diagnostic and calibration surface. Statistic registers define match masks, compare controls, counters, stop behavior, and calibration compare clock selection. Analog TX override and analog TX registers expose termination, equalization cursor, DCC DAC, clocking, analog test-bus, measurement, and miscellaneous mode bits. These are low-level PHY knobs rather than high-level display policy.

The raw common area manages CR4 shared DPCS state. MPLLA and MPLLB override groups include reference-clock enables, reset/calibration requests, fractional feedback dividers, multiplier ranges, HDMI clock controls, SSC peak and step-size fields, and bandwidth override values. AON common fields expose RTUNE values per lane, SRAM bitline setup, power-gate and supervisor overrides, resource ASIC input/output mirrors, VREF status, reference range, and miscellaneous common configuration. ID and firmware-code registers identify the raw PCS/firmware view.

The raw lane 0 PCS/PMA area is the digital bridge around the lane PHY. PCS fields cover TX/RX value overrides, PCS input mirrors, output/status mirrors, adaptation controls, figure-of-merit readback, cursor direction feedback, lane numbering, equalization override, phase-2 calibration, ATE override, and TX/RX termination controls. PMA fields mirror lane, supervisor, TX, RX, MPHY, RTUNE, and adaptation status across override and ASIC-input style registers.

The raw lane 0 FSM and IRQ area describes hardware sequencing and event signaling. FSM fields name fast calibration/adaptation phases, continuous calibration states, lock/status flags, TX DCC state, CMNCAL MPLL/RCAL status, and RX IQ phase offset. IRQ fields are organized as status/clear/mask groups, so the same event families appear repeatedly with different write semantics.

The raw lane 1 material is only the beginning of a repeated lane pattern. It starts the `PCS_XF_TX_OVRD_IN` register and should be merged with the following chunk before drawing complete conclusions about raw lane 1.

## Control Flow And State Behavior

This header has no software control flow. Runtime behavior is created by driver code that includes this header and writes the corresponding hardware registers.

The field names imply several hardware state machines and handshakes:

- TX/RX lane bring-up uses reset, clock-ready, request/acknowledge, data-enable, low-power detect, P-state, rate, width, MPLL select/enable, RX detect request/result, beacon, and async-data controls.
- TX power sequencing uses the P0/P0s/P1/P2 power-state bit sets and the TX power-up timing registers to coordinate analog reference generation, VCM hold, analog/word/digital clocks, reset release, serial enable, data enable, RX detect, and DCC compensation.
- Common PLL programming uses MPLLA/MPLLB override inputs, bandwidth values, SSC peak/step-size fields, MPLL state controls, and master MPLL override state bits visible in lane-level registers.
- Calibration and adaptation use RX adaptation acknowledgement/status, FOM, RX EQ overrides, PH2 calibration controls, fast FSM phase fields, continuous adaptation/calibration status, CMNCAL MPLL/RCAL status, CR lock, TX DCC flags/status, RX IQ phase offset, and RTUNE readbacks.
- Interrupt behavior is latch-like and split across status, clear, and mask registers for RX/TX reset/request/rate/P-state/adaptation/PH2/loopback/DCC events. Consumers must use the correct status, clear, or mask macro family.
- Diagnostic and validation flows use LBERT, OCLA, ATE, ATB, SRAM init/status, memory monitor, statistic counters, analog measurement, firmware ID, raw PCS ID, and reserved/tuning windows.

No software persistence is implemented here. Hardware register contents persist or reset according to ASIC power, reset, and clock domains. Fields named `STATUS`, `ACK`, `RESULT`, `CNT`, `FOM`, `LOCK`, `FLAGS`, `CODE`, `ID`, `RTUNE`, `VREF`, `ASIC_IN`, `PMA_IN`, and `PCS_IN` indicate hardware readback or latched state, but this chunk does not define save/restore policy.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. These macros are intended to be included with generated DPCS 4.2.0 register address headers and AMDGPU/DC helper macros that derive field values from shift and mask constants.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DPCS/RDPCS PHY, Display Core, link encoder, clock, DisplayPort, HDMI, and PHY diagnostics paths.
- Generated ASIC register offset headers for DPCS 4.2.0 CR4 registers. This file supplies field shifts and masks, not register addresses.
- DisplayPort and HDMI link training and recovery paths that control lane width/rate/P-state, TX EQ pre/main/post cursors, RX adaptation, FOM, RX/TX reset, RX detect, beacon, and PLL selection.
- Suspend/resume and hotplug paths that reinitialize common PLL, power-gate, supervisor, RTUNE, bandgap/VREF, lane power, and analog TX state after power-domain transitions.
- Hardware validation, manufacturing, and bring-up tooling that uses OCLA, ATE, ATB, LBERT, statistic counters, FSM monitors, firmware/raw ID codes, SRAM init, and analog measurement fields.
- Firmware or hardware state-machine coordination paths, reflected by `ASIC_IN`, `ASIC_OUT`, `OVRD_IN`, `OVRD_OUT`, `PCS_IN`, `PCS_OUT`, `PMA_IN`, and `PMA_OUT` naming.

## Risks

- Generated-header drift is the main risk. A wrong mask or shift can silently write adjacent PHY or PLL bits during read-modify-write operations.
- This chunk mixes CR4 lane 3, CR4 raw common, raw lane 0, and the beginning of raw lane 1. Prefix mistakes can compile cleanly while targeting the wrong lane or common block.
- Many registers pair a value bitfield with an override-enable bitfield. Setting only the value, or leaving override-enable asserted after diagnostics, can force PHY behavior away from normal ASIC or FSM control.
- IRQ status, clear, and mask registers have similar names but different semantics. Using a clear macro as persistent state, or writing a status mirror as a control value, can lose interrupts or leave stale event latches.
- Analog TX, PLL, SSC, RTUNE, VREF, DCC DAC, termination, boost, and cursor fields affect signal integrity. Changes need hardware-spec validation and link testing, not only compile coverage.
- Reserved and spare masks are exposed beside active fields. Driver code should preserve reserved bits unless the hardware specification explicitly documents a write value.
- Chunk boundaries are partial. `DPCSSYS_CR4_LANE3_DIG_ASIC_TX_OVRD_IN_4` is missing its shifts and earlier masks here, and `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` is missing its final two masks. Merge tooling must combine adjacent chunks before doing per-register completeness checks.
- Repeated per-lane and MPLLA/MPLLB patterns are copy-generation sensitive. A single instance-specific field error may only affect one lane, one PLL path, or one diagnostic mode.

## Test Signals

Useful validation signals are build-time, generation-time, and hardware-integration oriented:

- Preprocess/compile AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-header checks against the authoritative DPCS 4.2.0 register database, especially around the lane 3 to raw common to raw lane 0 address-region transitions.
- Macro-pair checks that each complete register block has matching `__SHIFT` and `_MASK` definitions and that masks correspond to field width and shift. For this sliced chunk, the expected local count is 1,061 shifts and 1,060 masks because of partial boundaries.
- Grep/compile checks for consumers of `DPCSSYS_CR4_LANE3_DIG_ASIC`, `DPCSSYS_CR4_LANE3_DIG_TX_PWRCTL`, `DPCSSYS_CR4_LANE3_DIG_RX_STAT`, `DPCSSYS_CR4_LANE3_DIG_ANA`, `DPCSSYS_CR4_LANE3_ANA_TX`, `DPCSSYS_CR4_RAWCMN_DIG`, `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF`, `DPCSSYS_CR4_RAWLANE0_DIG_FSM`, `DPCSSYS_CR4_RAWLANE0_DIG_IRQ_CTL`, and `DPCSSYS_CR4_RAWLANE0_DIG_PMA_XF` macros.
- Runtime display tests on ASICs using DPCS 4.2.0: DP and HDMI link training, hotplug, suspend/resume, link-rate changes, lane-count changes, RX/TX reset recovery, PLL lock/recalibration, RX adaptation convergence, and interrupt clear/mask behavior.
- PHY bring-up readback for TX ACK, DETRX result, RX ACK/VALID/adaptation status, P-state/rate/width, TX power-state timing, DCC DAC acknowledgement, RX statistic counters, MPLL state, SRAM init done, RTUNE values, VREF status, FOM, CR lock, TX DCC status, CMNCAL status, RX IQ phase offset, and lane IRQ status/clear/mask behavior.
- Diagnostic coverage for OCLA, ATE, ATB, LBERT, statistic match/counter, analog measurement, firmware/raw ID, FSM monitor, and reserved/tuning register paths when hardware validation or manufacturing flows depend on them.

## Chunk Notes For Merge

This document intentionally covers only lines 90529-92906 of `dpcs_4_2_0_sh_mask.h`. The previous chunk should complete `DPCSSYS_CR4_LANE3_DIG_ASIC_TX_OVRD_IN_4` before this range, and the following chunk should complete `DPCSSYS_CR4_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN` and continue the raw lane 1 repeated register families. The later per-file merge should describe this source as a generated ASIC bitfield map for AMD DPCS 4.2.0, not handwritten driver logic, and should preserve the distinction between CR4 lane 3, raw common, raw lane 0, and raw lane 1 surfaces.
