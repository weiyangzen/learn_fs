# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 102726-105125

## Purpose

This chunk is a generated DCN 3.2.0 shift/mask header slice for C20 PHY Control Router 1 display PHY registers. It defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for a late portion of `C20_PHY_CR1_LANE3` receive-side digital/analog control and the beginning of `C20_PHY_CR1_RAWLANE0` transmit/receive PCS, firmware handoff, IRQ, PMA, and calibration controls.

The range contains 2,160 `#define` entries across 240 register comment sections. It starts in lane 3 RX power-state controls (`C20_PHY_CR1_LANE3_DIG_RX_PWRCTL_RX_PSTATE_P1`) and ends at the first rawlane0 RX firmware adaptation status fields (`C20_PHY_CR1_RAWLANE0_DIG_RX_FW_XF_ADAPT_FOM`). These constants are not executable logic; they are the register-field ABI used by AMDGPU DCN32 display, DMUB, IRQ, and low-level PHY programming paths when they need exact bitfield layouts for this ASIC generation.

## Important APIs, Types, and Register Groups

There are no functions, structs, or enums in this chunk. The API surface is the macro naming contract:

- `<register>__<field>__SHIFT` gives the right-shift amount for a hardware field.
- `<register>__<field>_MASK` gives the already-positioned hardware mask.
- Driver register helpers consume these generated names through generated field tables and `REG_*` helper macros rather than by treating the header as ordinary hand-written C logic.

Major register families in this slice:

- `C20_PHY_CR1_LANE3_DIG_RX_PWRCTL_*`: lane 3 RX power state setup for P1/P2, power-up delays, clock enables, CDR/deserializer/VCO reset enables, RX control, and RX power-state status.
- `C20_PHY_CR1_LANE3_DIG_RX_VCOCAL_*`: RX VCO calibration control, tuning start values, calibration timing, frequency/counter/status readbacks, lock status, compare/status controls, and DPLL calibration knobs.
- `C20_PHY_CR1_LANE3_DIG_RX_CDR_*` and `*_DPLL_*`: CDR/DPLL control, frequency values, min/max bounds, loop bandwidth, phase detector, hold, frequency override, lock, and diagnostic state.
- `C20_PHY_CR1_LANE3_DIG_RX_ADPTCTL_*`: receiver adaptation configuration and status for ATT, VGA, CTLE, DFE taps 1-5, slicer offsets, DCC offsets, reset/reload behavior, fast flags, and SSM final code generation.
- `C20_PHY_CR1_LANE3_DIG_RX_STAT_*` and `RX_IQC_CTL_*`: RX statistics/match controls, sample counts, counter shadows, stop/clear behavior, and IQ calibration adjustment/status.
- `C20_PHY_CR1_LANE3_DIG_ANA_XF_RX_*`: digital-to-analog transfer and override fields for RX power, VCO, AFE, signal detect calibration, DAC controls, IQC, loopback, sampler select, termination code, stat in/out, and analog CREG fields.
- `C20_PHY_CR1_RAWLANE0_DIG_TX_*`: rawlane0 TX PCS/FW/IRQ/CTL/PMA handoff fields, including override input/output, lane numbering, reset/request/ack handshakes, rate/width/PSTATE/LPD controls, IRQ mask/enable/clear bits, term code, RTUNE, MPLL restore calibration, and PMA controls.
- `C20_PHY_CR1_RAWLANE0_DIG_RX_*`: rawlane0 RX PCS and firmware-facing handoff fields for reset, request, PSTATE, LPD, rate, width, DFE bypass, adaptation request, margining, CTLE/DFE/context configuration, CDR/VCO config, signal detect thresholds, termination control, and RX valid/ack/adaptation status.

Representative field themes are enable bits (`*_EN`, `*_CLK_EN`, `*_OVRD_EN`), reset bits (`*_RST`, `RESET`, `RESET_OVRD_EN`), link/lane operating values (`RATE`, `WIDTH`, `PSTATE`, `LPD`), analog calibration values (`VDAC`, `IDAC`, `CREG`, `VCO`, `DPLL`, `CTLE`, `DFE`, `VGA`, `ATT`), and status/interrupt fields (`*_STATUS`, `*_IRQ`, `*_IRQ_CLR`, `ACK`, `ADAPT_ACK`, `RX_PWRSM_STATE`).

## Control Flow

This header has no local control flow. Runtime control flow exists in the register access layers that include `dcn_3_2_0_sh_mask.h` and pair these field definitions with the matching offset header:

- DCN32 display and DMUB code include the header to materialize ASIC-specific register-field tables.
- Higher-level link initialization, training, HPD/IRQ handling, firmware handoff, power management, and diagnostics use register helper macros to mask, shift, read, write, and poll individual hardware fields.
- For this chunk, the implied hardware sequences are PHY-oriented: power-state programming enables or disables RX analog/digital blocks, VCO/CDR/DPLL programming calibrates and locks receiver clocks, adaptation control tunes signal equalization, TX/RX PCS and FW transfer registers coordinate request/ack handshakes, and IRQ clear fields acknowledge rawlane events.

The generated definitions must be internally consistent with the corresponding `dcn_3_2_0_offset.h` register-address definitions. If a caller selects the right register address but a wrong field mask, the C control flow still runs normally while the hardware state changes incorrectly.

## State and Persistence Behavior

The file stores no software state. Its constants define how software accesses persistent MMIO/register state inside the display PHY until hardware reset, link retraining, power gating, suspend/resume, firmware reprogramming, or another register write changes it.

Important hardware state domains represented here include:

- RX power state and timing: P1/P2 block enables, VREG/clock/deserializer/CDR/VCO reset timing, fast-start controls, and power-state-machine status.
- Clock recovery and calibration: VCO frequency tune and calibration status, DPLL frequency/bounds, CDR lock counters, integrator/gain controls, and calibration done/skip/status fields.
- Equalization and adaptation: ATT/VGA/CTLE/DFE tap status, DFE bypass, adaptation reset/reload/mode, margining controls, slicer/DAC/DCC offsets, and SSM status.
- Analog override state: RX AFE, power, VCO, signal detect, loopback, IQ calibration, termination, CREG, and stat input/output override fields.
- Rawlane TX/RX handoff state: firmware and PCS request/reset/ack signals, rate/width/PSTATE/LPD, lane number, PMA/PMA-supply controls, TX/RX valid flags, and adaptation acknowledgements.
- Interrupt state: rawlane0 TX IRQ mask, enable, asserted, and clear fields for rate, reset, request, RX-to-TX loopback enable/disable, RTUNE, term control, and transceiver mode changes.

Some fields are likely write-one-to-clear, latch, status, override-enable, or handshake bits. This makes exact masks more important than ordinary compile-time API compatibility: stale or shifted masks can leave hardware stuck waiting for an acknowledgement or can clear an unrelated interrupt.

## Dependencies and Integration Points

This chunk depends on the generated AMD ASIC register ecosystem:

- `dcn_3_2_0_offset.h` supplies register addresses and instance offsets matching the field names here.
- `dcn_3_2_0_sh_mask.h` is included by DCN32 display code such as `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` and `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`.
- Display Core register helper layers use macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and generated `SE_SF`/`LE_SF` style field tables to combine register addresses with these shifts and masks.
- The C20 PHY definitions overlap conceptually with DPCS register headers, so PHY programming and debugging must keep DCN and DPCS generated register layouts aligned for the same hardware block.

The direct integration points are lower-level display PHY, link, IRQ, and DMUB firmware-adjacent paths. Even when these exact long macro names are not spelled in ordinary C files, they provide the generated bitfield vocabulary available to DCN32 register tables and debug scripts.

## Risks

- Bitfield drift is the core risk. A wrong `__SHIFT` or `_MASK` can silently program the wrong analog/PCS field while all C code compiles.
- Lane and rawlane boundaries are easy to confuse. This slice transitions from `LANE3` RX analog/digital controls to `RAWLANE0` TX/RX PCS/FW controls; copy-generation mistakes across lanes can affect a different physical lane than intended.
- Override fields usually have paired value and enable bits. Updating a value mask without the matching `*_OVRD_EN` mask, or vice versa, can leave firmware/hardware ownership ambiguous.
- Handshake and interrupt fields are sequencing-sensitive. Bad masks for `REQ`, `ACK`, `RESET`, `*_IRQ`, or `*_IRQ_CLR` can cause firmware waits, lost interrupts, repeated IRQ storms, or uncleared status.
- Calibration fields affect signal integrity rather than obvious software invariants. Incorrect VCO/CDR/DPLL/CTLE/DFE/DCC fields can manifest as intermittent link training failures, hotplug instability, high error rates, or monitor-specific blanking.
- Reserved-field masks are present throughout. Accidentally writing reserved bits through broad masks can cause undocumented PHY behavior.

## Test Signals

Useful validation is mostly build, hardware, and register-trace oriented:

- Build coverage: DCN32 AMDGPU display code compiles with this header and no missing generated shift/mask symbols.
- Header consistency: generated masks align with shifts and field widths, and matching offset-header register names exist for the same ASIC generation.
- Display/link smoke tests: DisplayPort/USB-C/eDP outputs using C20 PHY lanes light up, retrain, suspend/resume, and hotplug without PHY or AUX/link-training regressions.
- PHY calibration signals: VCO/CDR/DPLL lock and calibration-done status bits reach expected states; RX power-state-machine status transitions complete after power-up/down.
- Interrupt tests: rawlane0 TX rate/reset/request/loopback/RTUNE/term/transceiver IRQ bits assert, mask, enable, and clear as expected.
- Firmware handoff tests: TX/RX `REQ`/`ACK`, reset, PSTATE, rate, width, DFE bypass, adaptation request/ack, and RX valid paths do not hang when firmware or DMUB participates.
- Signal-integrity tests: CTLE/VGA/DFE adaptation status, margining, PRBS/loopback, error counters, and link error-rate checks remain stable across rates and lane widths.
