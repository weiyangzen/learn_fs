# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 48788-51226

## Scope And Purpose

This chunk is a generated AMD DC/DPCS register field mask header segment. It contains no executable C logic, functions, structs, or enum declarations. Its role is to publish preprocessor constants for bit shifts and masks used by AMDGPU display code when composing or decoding register values for the DPCS 3.1.4 block, especially CR2 per-lane PHY control/status registers and the following `dpcssys_dcio_dcio_dispdec` address block.

Every field follows the same contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask value.
- Most CR2 lane registers in this chunk are 16-bit fields with masks ending in `L`; the DCIO/UNIPHY display decode block at the end uses 32-bit masks for wider display registers.

The chunk starts mid-register with `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_DCC_DAC_ACK` fields, then covers many complete register-comment blocks through `DCIO_SOFT_RESET`.

## Register Families Covered

The CR2 lane digital TX/RX control region defines constants for DCC DAC acknowledge/addressing, TX clock alignment, LBERT test pattern generation, RX power-state definitions, RX power-up timing, VCO/CDR calibration, RX adaptive equalization, statistics/counters, MPHY/PWM support, analog override/status fields, PCS/PMA cross-interface fields, FSM controls, IRQ flags/masks, and TX/RX control state. These names are all prefixed primarily with `DPCSSYS_CR2_LANEX_*` or `DPCSSYS_CR2_RAWLANEX_*`.

The `dpcssys_dcio_dcio_dispdec` address block begins at line 51050 and switches to display/DCIO naming. It includes `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, UNIPHY channel inversion/crossbar registers for UNIPHYA through UNIPHYE, `DC_PINSTRAPS`, `INTERCEPT_STATE`, backlight PWM frame-start selection, genlock/swaplock pad controls, and `DCIO_SOFT_RESET`.

## Important Macro Interfaces

RX power-state macros define the bit layouts for `DPCSSYS_CR2_LANEX_DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2`. Each p-state block exposes the same operational signals: AFE enable, clock regulator enable, analog clock enable, deserializer enable, CDR enable, VCO frequency reset, VCO calibration reset, continuous VCO calibration enable, and digital clock enable. These masks are used by callers to program different receiver power/performance states without hardcoding the bit positions.

RX power-up timing is represented by `RX_PWRUP_TIME_1`, `RX_PWRUP_TIME_2`, and `RX_PWRUP_TIME_3`. The fields cover AFE/VREG/clock enable delays, fast-start enable bits, RX rate timing, CDR enable timing, deserializer enable timing, and deserializer disable timing. These constants matter when software sequences a lane into active operation or fast-start modes.

RX VCO/CDR calibration is represented by `RX_VCO_CAL_CTRL_0` through `_2`, `RX_VCO_CAL_TIME_0` and `_1`, `RX_VCO_STAT_0` through `_2`, `RX_CDR_CDR_CTL_0` through `_4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and DPLL frequency bounds. The fields expose fixed-count controls, calibration step count, skip-calibration bits, VCO startup/update/settle timing, calibration done flags, final counter values, VCO correctness/up indicators, CDR phase detector controls, spread-spectrum counters, DPLL gain override fields, and upper/lower frequency bounds.

RX adaptive equalization is represented by `RX_ADPTCTL_ADPT_CFG_0` through `_9`, reset controls, status fields for ATT/VGA/CTLE/DFE taps, slicer and VDAC offset fields, DAC control selects, and CR bank address/data fields. Important knobs include adaptation timing and clock division, CTLE/VGA/ATT/DFE enable masks, threshold fields, adaptation step-size fields, initial error slicer levels, adaptation reset bits, and final adaptation code/status fields.

RX statistic and match/counter macros define `RX_STAT_*` registers. These include pattern masks and pattern values, statistic source/shift/clock selection, sample-count start/stop/pause bits, seven statistic counter enable bits and counter values, valid-loss clear/control bits, and calibration comparison clock controls. These macros are likely used by diagnostic or bring-up flows to measure link behavior and pattern matches.

Analog override macros map software-accessible controls for TX/RX analog behavior. TX coverage includes data/clock/reference/reset/serial enable, data rate, RX detect, termination code override, TX equalization leg pull enables/directions, pre/post controls, DCC calibration controls, fast start, loopback clock enable, and AC JTAG enable. RX coverage includes data rate, word/div4 clocks, DFE/adaptation enable, power overrides, VCO/frequency tuning overrides, calibration muxes/modes, DAC control selection, AFE ATT/VGA/CTLE/slicer/scope controls, IQ phase adjustment, signal-change enables, analog status, termination override, MPHY PWM/squelch controls, and signal-detect calibration thresholds.

The raw lane PCS/PMA cross-interface macros define override/input/output handshakes between PCS and PMA. PCS fields include TX/RX `REQ`, `RESET`, `PSTATE`, `RATE`, `WIDTH`, low-power detect, MPLL selection/enables, adaptation request/continuous/offcan signals, loopback enable overrides, async data enables, RX EQ fields, phase-2 calibration request/ack bits, lane number, ATE overrides, termination controls, and TX pre/main/post direction hints. PMA fields include lane MPLL enables, supervisor states, TX/RX request/reset/data enable overrides, beacon/async/loopback controls, lane retune request/ack, MPHY PWM and termination overrides, and IQ phase map override.

FSM and IRQ macros expose the lane micro-sequencer and interrupt model. `FSM_FSM_OVRD_CTL` can select jump address, start commands, enable override, or break execution; monitor registers expose memory address, state, command-ready, ALU flags, wait counter, and read/write-mask disabled flags. The many `FAST_RX_*`, `FAST_TX_*`, and `FAST_FLAGS` registers provide one-bit fast-path calibration/power/adaptation bypass or status controls. IRQ fields expose RX/TX reset/request/rate/pstate/adaptation/phase-2-calibration/loopback/DCC interrupts, matching clear registers, and aggregate mask registers.

The DCIO/UNIPHY macros at the end are wider display fabric controls. `DC_GENERICA` and `DC_GENERICB` select generic outputs and UNIPHY clock sources. UNIPHY link/crossbar controls expose channel inversion and channel source mapping. `INTERCEPT_STATE` exposes PWRSEQ and DPCS intercept state bits. `DCIO_SOFT_RESET` publishes per-UNIPHY and per-DSYNC soft-reset bits.

## Control Flow And State Behavior

There is no direct control flow in this header chunk. Runtime behavior emerges in code that includes this header and performs register read/modify/write operations using these masks and shifts. Typical consumers combine field values as `(value << SHIFT) & MASK`, OR several fields together, or extract a register field by masking then shifting.

The represented hardware state is persistent only in device registers. Writes to control, override, reset, IRQ-clear, and calibration fields can change PHY/display hardware state until hardware, firmware, driver, or reset code changes the register again. Status macros name readback-only or status-like fields such as `ACK`, `*_DONE`, `*_STATUS`, `*_STAT`, `RX_VALID`, VCO counter values, interrupt latches, and calibration results. The header itself stores no state and has no initialization.

Several macro groups imply hardware sequencing dependencies even though this file does not implement them: power p-state bits must be coherent with RX/TX timing fields; VCO/CDR resets and continuous calibration enables must match calibration timing; adaptation enable/reset/status fields must be sequenced around receiver training; IRQ clear registers pair with IRQ status and mask registers; PCS/PMA override enable bits must be set consistently with override value bits; and DCIO soft-reset bits must be used with care because they target shared UNIPHY/DSYNC blocks.

## Dependencies And Integration Points

This header depends only on the C preprocessor. It is intended to be included by AMDGPU display and DC register access layers along with corresponding register address headers for the same ASIC block. The naming indicates integration with the Linux AMD DRM display stack under `drivers/gpu/drm/amd`, especially low-level display core code that programs DPCS/DCIO/UNIPHY lanes.

The macro names are part of a generated register ABI. Other code can reference them directly, so renaming or regenerating with changed names has broad build impact. The address constants are not in this chunk; callers must pair these `_SHIFT` and `_MASK` definitions with the corresponding register offset definitions from sibling ASIC register headers.

The chunk also bridges multiple hardware conceptual layers: analog PHY lane controls, digital PCS/PMA interfaces, FSM/IRQ management, and display fabric/DCIO controls. That makes it an integration point between normal display link bring-up, factory/ATE test paths, diagnostics, and low-level debug tooling.

## Risks And Maintenance Notes

Incorrect mask or shift values can silently corrupt hardware programming. The highest-risk fields are reset, override-enable, power-state, VCO/CDR calibration, adaptation, and soft-reset bits because a wrong value can disable a lane, stall link training, mask interrupts, or reset a shared display block.

Reserved fields are explicitly named and masked throughout the chunk. Driver code should avoid writing arbitrary values to reserved masks unless the hardware programming guide or generated sequence requires it. A broad register write that fails to preserve reserved bits can introduce ASIC-specific regressions.

Many fields have paired `*_OVRD_VAL` and `*_OVRD_EN` bits. Setting the value without the enable bit, or leaving enable set after a debug/test path, can produce misleading behavior. IRQ fields also have status, clear, and mask variants with similar names; accidentally using a clear mask where a status or mask field is expected would be a hard-to-debug interrupt issue.

The DCIO/UNIPHY section uses 32-bit masks while most earlier CR2 lane macros use 16-bit masks. Callers and code generators should preserve the target register width and not assume all masks in this file are 16-bit.

Because this is generated source, hand edits are risky. The reliable maintenance path is regeneration from the authoritative register database, followed by build and hardware-focused validation.

## Test Signals

Useful build-time signals are successful compilation of AMDGPU display code that includes this header and absence of duplicate or missing macro-name errors after regeneration. Static checks can verify that every field has a matching `_SHIFT`/`_MASK` pair, masks align with shifts, masks do not overlap unexpectedly within a register, and 16-bit versus 32-bit register widths are preserved.

Runtime validation requires hardware or simulation. Relevant signals include successful display link bring-up across rates and power states, stable RX/TX training and adaptation, correct VCO/CDR calibration done/status readbacks, expected IRQ masking/clearing behavior, successful loopback/LBERT/ATE diagnostics where supported, correct UNIPHY channel routing/inversion, and safe behavior of DCIO soft resets.

For this specific chunk, regression tests should emphasize RX p-state transitions, fast-start timing, DPLL/VCO calibration bounds and statuses, adaptation status counters, PCS/PMA override handshakes, IRQ clear/mask behavior, and DCIO/UNIPHY channel crossbar programming.
