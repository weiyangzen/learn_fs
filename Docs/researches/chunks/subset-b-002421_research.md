# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 85089-87514

## Chunk Scope

This chunk is part of the generated AMD DPCS 4.2.3 register shift/mask header. It contains C preprocessor constants only: register-field `__SHIFT` macros and corresponding `_MASK` macros for 16-bit DPCS register payloads. There are no structs, functions, executable statements, or kernel-owned storage in this slice.

The range starts mid-register in `DPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_ADPT_CFG_8`, then covers the rest of the CR4 lane 2 RX adaptation/status/statistics block, lane 2 digital-to-analog TX/RX override fields, lane 2 analog TX/RX tuning and measurement fields, a large CR4 lane 3 ASIC/TX power/statistics/analog TX block, CR4 raw common PLL/always-on common controls, and the beginning of CR4 RAWLANE0 PCS transfer override fields. The final line is only the comment for `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_3`; its field definitions are outside this chunk.

## Purpose

The macros define how AMD display code should pack and unpack fields in DPCS 4.2.3 control/status registers for the CR4 PHY instance. The paired `dpcs_4_2_3_offset.h` header supplies the `reg...` and `ix...` register addresses; this header supplies bit positions and masks within those registers. Runtime display code can use these constants with AMD register helper macros to program PHY lanes, PLLs, adaptation, calibration, and debug paths without hard-coding numeric bit positions.

The hardware areas represented here are:

- Lane 2 RX adaptation: DFE tap adaptation parameters, ATT/VGA/CTLE/DFE readback status, adaptation reset, data/error VDAC offsets, slicer controls, error slicer levels, and DAC selector fields.
- Lane 2 RX statistic/correlation engine: pattern masks/matches, sample counters, statistic counter enables/readbacks, data/scope delay controls, valid-loss clear/control, calibration clock divider, and statistic stop.
- Lane 2 digital/analog override and analog tuning: MPHY PWM/termination controls, TX analog clock/data/reset/equalization/termination/DCC overrides, RX analog power/CDR/VCO/calibration/DAC/AFE/CTLE/scope/slicer/phase controls, signal-detect thresholds, TX/RX analog test bus measurement fields, and reserved/no-connect fields.
- Lane 3 ASIC and TX/RX lane controls: lane loopback and AC JTAG inputs, TX override inputs/outputs, TX ASIC inputs/outputs, RX status outputs, per-pstate TX power definitions, TX power-up timers, DCC DAC bank/ack/address controls, TX clock alignment, link BERT control, RX statistic engine, and TX analog override/tuning groups.
- CR4 raw common controls: common PHY reset, MPLLA/MPLLB clock divider/bandwidth/SSC/fractional controls, HDMI/PWM/RTUNE/init-cal overrides, MPLL state timing, TX calibration code, SRAM init, OCLA probe selection, supervisor analog overrides, firmware/id codes, eight sets of common RTUNE RX/TX up/down values, SRAM bootloader/power-gate controls, supervisor/reservation handshakes, reference range override, and MPLL power-down timing.
- RAWLANE0 PCS transfer beginning: TX and RX PCS override/input/output handshakes for pstate, low-power detect, width, rate, MPLL selection/enables, reset/request, RX detect, VBOOST/IBOOST, beacon, adaptation, loopback, data enable, and VCO override inputs.

## Important APIs, Types, and Macros

There are no typed APIs in this chunk. The exported interface is the macro namespace:

- `DPCSSYS_CR4_LANE2_DIG_RX_ADPTCTL_*__FIELD__SHIFT` / `_MASK`: lane 2 adaptation and readback fields. Important registers include `ADPT_CFG_9`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS`, even/odd data and error VDAC offsets, even/odd slicer controls, `ERROR_SLICER_LEVEL`, `ADPT_RESET`, `DAC_CTRL_SEL_*`, and adaptation CR bank address/data.
- `DPCSSYS_CR4_LANE2_DIG_RX_STAT_*`: lane 2 statistic engine fields. These cover `SC1_LD_VAL`, pattern A/B masks and matches, statistic source/correlation controls, counter enables and readback counters 0-6, sample-count done bits, calibration-comparator clock control, extended pattern words, and `SC1_STOP`.
- `DPCSSYS_CR4_LANE2_DIG_ANA_*` and `DPCSSYS_CR4_LANE2_ANA_*`: lane 2 digital-to-analog and analog-native controls. These include TX clock/data/reset/serial/rate/termination/equalization/DCC overrides, RX control/power/VCO/calibration/AFE/scope/slicer/phase/signal-detect fields, MPHY/PWM controls, analog status fields, and ATB measurement selectors.
- `DPCSSYS_CR4_LANE3_DIG_ASIC_*`: lane 3 ASIC interface macros for loopback, TX reset/request/rate/width/pstate/MPLL/async/ACJTAG/VBOOST/IBOOST/USB4-style signals, TX/RX ASIC in/out handshakes, and override output gates.
- `DPCSSYS_CR4_LANE3_DIG_TX_PWRCTL_*`: lane 3 TX power-control macros for P0/P0S/P1/P2 analog/digital enables, RX detect permissions, DCC calibration enable, power-up timers, DCC DAC bank address/data/control/range/select/ack/address, TX clock alignment, and `TX_LBERT_CTL`.
- `DPCSSYS_CR4_LANE3_DIG_RX_STAT_*`, `DPCSSYS_CR4_LANE3_DIG_ANA_TX_*`, and `DPCSSYS_CR4_LANE3_ANA_TX_*`: lane 3 copies of the RX statistics and TX analog override/tuning patterns described for lane 2.
- `DPCSSYS_CR4_RAWCMN_DIG_*`: raw common macros for common reset, MPLLA/MPLLB overrides, SSC and fractional controls, lane-FSM extension data, common control overrides, MPLL state, calibration/readiness/id/debug fields, RTUNE values 0-7, power-gate/supervisor/reservation controls, reference range override, and common miscellaneous timing.
- `DPCSSYS_CR4_RAWLANE0_DIG_PCS_XF_*`: beginning of raw lane 0 PCS transfer macros for TX/RX override inputs and raw PCS inputs/outputs.

Most masks are 16-bit `L` constants such as `0xFFFFL`, `0x8000L`, or narrower field masks such as `0x03FFL`, `0x1FFFL`, and `0x7FFFL`. The generator also emits masks for reserved fields, which are useful for documentation but should generally not be used to force writes into reserved bits.

## Control Flow

This chunk has no software control flow. Hardware sequencing is implied by the fields:

- Request/acknowledge paths appear in PCS and DCC controls, including TX/RX `REQ`, `ACK`, RX-detect request/result, DCC DAC `REQ`/`ACK`, common reservation request/ack, and adaptation request bits.
- Many override registers follow a value-plus-enable convention, for example `*_OVRD_VAL` with `*_OVRD_EN`, `*_OVR_VAL` with `*_OVR_EN`, or field-specific `*_OVRD`/`*_OVRD_EN` pairs. Callers must program both the desired value and its enable bit when taking control away from hardware state machines.
- Self-clearing or clocked update controls are represented by fields such as term-code clocks, frequency-tune clocks, DAC/control update enables, signal-change update enables, and statistic start/stop bits. The ordering and polling rules live in hardware programming sequences, not in this header.
- Statistic collection is represented by load/start, mask/match, counter enable, done, valid-loss, and stop fields. Runtime logic must explicitly stage masks/patterns, start sampling, poll done/read counters, and stop/clear as needed.
- PLL/common controls imply clock sequencing: MPLLA/MPLLB divider, bandwidth, SSC, fractional, state, bank select, force-on/off timing, power-down timing, and init-cal-disable fields affect the clock source used by one or more lanes.

## State and Persistence

All state described here is DPCS hardware register state. The header itself is compile-time metadata and persists no values in kernel memory.

State categories visible in this chunk include:

- Link/lane mode: pstate, low-power detect, width, rate, MPLL select/enable, master MPLL state, TX/RX reset/request, async/beacon/data-enable paths, loopback, and AC JTAG.
- RX adaptation and observation: ATT/VGA/CTLE/DFE tap status, adaptation done bits, DFE data/error offsets, slicer levels, AFE gain/attenuation, CTLE boost, scope/phase controls, signal-detect thresholds, and statistic counters.
- TX analog and calibration: TX refgen/clock/word-clock/reset/serial/data enables, equalization pre/post/leg controls, termination codes, DCC DAC controls, VCM hold, VBOOST/IBOOST, RX detect timing, TX power states, and TX BERT fields.
- Common PHY state: common reset, PLL divider/bandwidth/SSC/fractional state, RTUNE values, SRAM init/bootloader state, power-gate and supervisor handshakes, reservation request/ack bits, and firmware/id code readbacks.
- Debug/test state: OCLA probe selection, ATB measurement selectors, AC JTAG, no-connect/reserved registers, raw bank address/data windows, and analog override fields.

Register values persist according to the hardware block lifetime: until a later write, PHY reset, lane reset, common reset, power-gate transition, link retrain, suspend/resume, or ASIC reset. Reserved bits should be preserved unless a hardware programming guide explicitly requires a full-register value.

## Dependencies and Integration Points

This header depends on the paired DPCS 4.2.3 offset header, `dpcs_4_2_3_offset.h`, for the register addresses that match these shift/mask definitions. The AMD display stack combines offset, shift, and mask headers through generated register-access patterns and resource tables for DCN-family display PHY programming.

Important integration points are:

- AMD display resource/link code that includes DPCS 4.2.3 headers for the target ASIC generation. The include pairing must remain generation-consistent; mixing `dpcs_4_2_3_sh_mask.h` fields with another offset version can silently address the wrong hardware register layout.
- Register helper macros such as field set/get helpers used in AMDGPU DC code. These helpers rely on the exact `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming pattern generated here.
- Hardware sequencing code for DisplayPort/USB-C/HDMI link bring-up, retraining, low-power transitions, lane calibration, PLL setup, signal detect, and diagnostics. This header only exposes bit positions; sequencing, delays, polling, and link-idle requirements are external.
- Cross-generation generated headers, especially DPCS 4.2.2 and other nearby DPCS versions. They are useful comparison points for generator drift but are not interchangeable with this CR4 4.2.3 slice.

## Risks and Maintenance Notes

- The chunk starts and ends on register boundaries imperfectly. It begins after the comment and first fields of `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_8`, and ends with only the `RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_3` comment.
- Manual edits are high risk. A one-bit mask or shift error can misprogram PHY adaptation, PLL selection, TX power timing, DCC calibration, or common power-gate handshakes, leading to display link failures that may be lane-, rate-, or connector-specific.
- Lane names are visually similar. This slice mixes `LANE2`, `LANE3`, `RAWCMN`, and `RAWLANE0`; copy/paste mistakes can compile while targeting the wrong lane or common block.
- Override value/enable pairs must be handled carefully. Leaving override enables asserted after diagnostics can keep hardware state machines from returning to autonomous control.
- Common PLL and power-gate fields affect more than one lane. Changes around `RAWCMN_DIG_MPLLA*`, `MPLLB*`, `MPLL_STATE_CTL`, RTUNE, power-gate, supervisor, and reservation fields have broader blast radius than lane-local changes.
- Statistic, DCC, SRAM, OCLA, ATB, BERT, ACJTAG, and raw bank fields are diagnostic or calibration oriented. They may require strict sequencing, clock availability, or link quiescence that this header cannot express.
- Reserved and no-connect masks are generated alongside real fields. Runtime writes should avoid setting reserved bits unless the register programming sequence explicitly documents the complete value.

## Test Signals

Useful validation signals for work touching this chunk include:

- Build coverage for the AMD display driver configuration that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static checks that each referenced `DPCSSYS_CR4_LANE2_*`, `DPCSSYS_CR4_LANE3_*`, `DPCSSYS_CR4_RAWCMN_*`, and `DPCSSYS_CR4_RAWLANE0_*` shift/mask macro has a matching register in the paired offset header.
- Cross-generation diffs against DPCS 4.2.2 and neighboring generated headers to distinguish intentional ASIC layout changes from generator or merge mistakes.
- Hardware smoke tests on affected AMD ASICs: boot, enumerate connectors, train and retrain DisplayPort/USB-C links at multiple rates and widths, exercise HDMI mode where relevant, hotplug repeatedly, suspend/resume, and perform mode-set stress.
- PHY diagnostics around RX adaptation, DFE/CTLE/VGA/ATT status, signal detect, statistic counters, DCC DAC ack paths, TX power-state timing, PLL state, RTUNE values, and power-gate/reservation handshakes.
- Negative signals to watch for include link-training failures, blank displays after resume, IRQ storms or stuck status bits, unstable high-rate links, lane-specific failures, and failures only when diagnostics or overrides have been used.
