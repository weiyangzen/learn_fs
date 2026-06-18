# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 115500-118171

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift header slice for C20 PHY register fields. It contains no executable C logic; its exported surface is a set of C preprocessor constants naming bit positions for hardware register fields.

The requested range contains 2,000 `#define` lines across 662 register names. It starts at the tail of the CR0 raw-lane TX PMA RTUNE handshake fields, then covers CR0 raw-lane RX PCS/FW/IRQ/control/FSM fields, CR0 always-on TX/RX calibration and adaptation fields, lane0 and lane1 PIPE message-bus PHY field groups, and the beginning of the CR1 supervisor/PLL/analog transfer block. The final line lands on the `C20_PHY_CR1_SUP_DIG_ANA_XF_MPLLA_ANA_CREG03` comment; that register's fields continue in the next chunk.

Although this repository path sits under a local `ceph-client` source mirror, the code is AMDGPU display/PHY metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The API contract is the generated macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for `FIELD` inside `REGISTER`.

Unlike many AMD `*_sh_mask.h` chunks, this exact line range exposes only `__SHIFT` constants; paired `_MASK` definitions for these registers are outside this range or not generated in this slice.

Major register families in this chunk are:

- `C20_PHY_CR0_RAWLANEX_DIG_RX_PCS_XF_*`: RX PCS cross-interface reset/request, power state, low-power detect, data enable, polarity invert, CDR SSC, adaptation, margining, recalibration, loopback, context selection, ACK, and equalization/context configuration fields.
- `C20_PHY_CR0_RAWLANEX_DIG_RX_FW_XF_*`: RX firmware interface override/input/output fields, adaptation acknowledgement and figure-of-merit readback, TX pre/main/post direction fields, clock-enable controls, and ACK signaling.
- `C20_PHY_CR0_RAWLANEX_DIG_RX_IRQ_CTL_*`: interrupt mask/enable/status/clear shifts for RX request, rate, pstate, adaptation request/disable, reset, termination control, and RX margining events.
- `C20_PHY_CR0_RAWLANEX_DIG_RX_CTL_*`: RX control/status fields for term code, continuous offset cancellation/adaptation, adaptation mode/selection, PPM drift, CDR detector status, PMA misc controls, FOM values, reference error, IQ/phase adjustment codes, margin status/error, FSM control, and rate IRQ acknowledgement.
- `C20_PHY_CR0_RAWLANEX_DIG_FSM_*`: firmware/FSM override, jump bank, breakpoints, monitored address/status, firmware stage/scratch/debug registers, lock, fast-path flags, many skip-startup/skip-continuous calibration bits, and RX calibration completion.
- `C20_PHY_CR0_RAWLANEAONX_DIG_TX_*`: always-on TX firmware states, SRAM recovery controls, CCA wait counters, startup/continuous algorithm skip controls, fast flags, high-power protection, lane transceiver mode, TX disable input, MPLLA/MPLLB DCC calibration banks, calibration done status, selected calibration codes, and TX calibration bank select.
- `C20_PHY_CR0_RAWLANEAONX_DIG_RX_*`: always-on RX startup/adaptation/continuous algorithm skip controls, fast flags, VGEN/sigdet/AFE/REF/DFE offset calibration fields, DCC calibration banks, IQ calibration, calibration done state, adaptation limits/results by bank, TX EQ direction/threshold helpers, generic `RX_ADPT_CTL_0` through `RX_ADPT_CTL_28`, CDR detector controls, RX disable/termination/sigdet/vrefgen overrides, and PMA override output.
- `C20_PHY_LANE0_PIPE0_UPCSLANE_PIPE_LPC_PHY_*` and `C20_PHY_LANE1_PIPE0_UPCSLANE_PIPE_LPC_PHY_*`: per-lane PIPE message-bus PHY fields for RX margining, elastic buffer, RX control/equalization, TX deemphasis and preset coefficient controls, HDP TX controls, encode/decode bypass, vendor-defined register read/write address/data windows, custom DP/FRL/HDMI rate/width, LFPS timer, debug address/value, EQ overrides, recalibration bank/force/skip controls, deskew controls, and recal/deskeW override enables.
- `C20_PHY_CR1_SUP_DIG_*`: CR1 supervisor fields for ID code, reference-clock overrides, MPLLA/MPLLB div-clock and HDMI override inputs, MPLLA/MPLLB control and spread-spectrum inputs, supervisor overrides, ASIC input/output mirrors, RTUNE debug/config/status, clock/reset power-up timers, MPLLA/MPLLB power-control/calibration/status/timing, SSC outputs/configuration, analog transfer status, analog override outputs, RTUNE/supervisor analog overrides, MPLLA tune overrides, supervisor analog CREG fields, and the start of MPLLA analog CREG fields.

## Control Flow

This header chunk has no runtime control flow. It contributes compile-time constants to the AMD display driver's register abstraction:

1. DCN 3.1.6 resource code includes the companion DPCS offset header and this shift header.
2. Driver register-table macros and helper structures bind generated register offsets, base indices, shifts, and masks to typed display objects.
3. Runtime code uses AMD display register helpers to read, write, poll, or update bitfields in the DPCS PHY register space.

Programming order is not encoded here. PHY bring-up, PLL configuration, RTUNE, lane calibration, RX adaptation, PIPE message-bus transactions, margining, and interrupt handling are controlled by driver code, firmware, and hardware rules outside this generated header.

## State And Persistence Behavior

The file stores no software state and persists nothing itself. It names hardware-visible state fields:

- RX PCS/FW interface state: reset/request/ack handshakes, power state, low-power detect, data enable, invert, SSC, adaptation, margining, recalibration, loopback, context select, and RX valid/ACK output.
- RX interrupt state: mask, enable, latched status, and clear bits for request/rate/pstate/adaptation/reset/termination/margining events.
- RX equalization/adaptation state: CTLE/AFE/VGA/DFE parameters, adaptation modes, IQ/phase adjustment data, FOM/readback values, margin status/error, CDR detector status, and continuous calibration/adaptation controls.
- FSM/firmware state: stage, scratch/debug registers, breakpoints, fast mode flags, skip bits for startup/continuous/rate calibrations, and reset calibration completion.
- TX/RX calibration state in the always-on lane block: DCC calibration codes per bank, selected recalibration banks, done bits, algorithm skip controls, fast flags, SRAM recovery counters, and TX/RX disable or protection inputs.
- PIPE sideband state: RX margin controls, elastic buffer control, TX EQ/preset coefficients, vendor-defined read/write data windows, custom rate/width settings, LFPS timer, debug windows, recalibration/deskew override controls, and per-lane duplicate fields for lane0 and lane1.
- CR1 supervisor state: reference clock source/range/enables, MPLLA/MPLLB enable/reset/calibration/gearshift/SSC/divider controls, supervisor bandgap/reference/power-up timers, RTUNE measured/set values, PLL power FSM timing/status, analog transfer status, and analog CREG/override fields.

Persistence and side effects are hardware-defined. Configuration bits generally remain until modeset, link reset, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, clear, calibration-done, and handshake bits may be latched, self-clearing, write-one-to-clear, or valid only while the relevant PHY clock/power domain is active. This header only provides bit positions; it does not describe access type or sequencing semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with the DPCS 4.2.3 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies register offsets and base indices for the same DPCS IP version.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` directly includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`, so this chunk feeds DCN 3.1.6 display resource initialization and register helper tables.
- AMD display register helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and local resource/register-list macros consume generated shift constants indirectly through the resource and block tables.
- The neighboring `dcn_3_2_0_sh_mask.h` file contains many structurally matching C20 PHY field names with both shifts and masks, making it a useful consistency reference when auditing generated C20 PHY metadata across ASIC families.
- DPCS IP base-address headers such as platform `*_ip_offset.h` files provide `DPCS_BASE` segment values used to address this IP block; this chunk only names fields within registers after those base and offset calculations.

Behaviorally, this chunk describes the PHY-side register surface behind display link setup. It is relevant to DP/HDMI/FRL lane bring-up, PLL/clock configuration, PHY termination tuning, lane margining, TX equalization, RX equalization/adaptation, PHY interrupts, and debug/firmware diagnostics.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift value can compile cleanly and only appear as register corruption, link instability, or missing status at runtime.
- The file is generated. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- This range lacks `_MASK` definitions. Consumers must combine these shifts with masks from the proper generated location/table; pairing a correct shift with a stale or wrong mask is enough to damage adjacent fields.
- Chunk boundaries are artificial. The first lines finish a TX PMA RTUNE register begun in the previous chunk, and the last line is only the comment for `MPLLA_ANA_CREG03`; its field definitions continue in the next chunk.
- Repeated lane blocks are copy-sensitive. Lane0 and lane1 PIPE message-bus groups should remain structurally identical except for the lane prefix; a generator drift can break only one lane or only multi-lane links.
- Override fields are hazardous. Many registers use a value bit plus an override-enable bit. Setting only one side, using the wrong shift, or leaving overrides enabled can force clocks, PLLs, termination, resets, margining, calibration, or power states against normal firmware control.
- Interrupt fields have status/clear/mask/enable variants with similar names. Mixing shifts between status and clear registers can leave RX rate/adaptation/margining interrupts stuck or silently disabled.
- Calibration bank fields are repeated for MPLLA, MPLLB, TX, and RX. Wrong bank select or DCC/IQ code shifts can produce failures only on specific data rates, recalibration paths, temperature changes, or after resume.
- RTUNE and analog CREG fields affect PHY termination, bandgap/reference, PLL, and regulator behavior. Bad bit placement can cause hard-to-debug electrical/link failures rather than clean software errors.
- Vendor-defined PIPE register windows use address/data high/low fields. Incorrect shifts can corrupt indirect PHY accesses or read back misleading debug information.

## Test Signals

Useful validation combines generated-header consistency checks with real display link behavior:

- Build AMDGPU display support for DCN 3.1.6. Missing or renamed macros should surface where `dcn316_resource.c` includes the DPCS 4.2.3 headers and initializes resource register tables.
- Mechanically compare this range against AMD's generated DPCS 4.2.3 register database and the companion `dpcs_4_2_3_offset.h`; every register field in this chunk should have a matching register offset and the expected bit position.
- Cross-check repeated groups for structural consistency: `LANE0_PIPE0` versus `LANE1_PIPE0`, MPLLA versus MPLLB calibration/status groups where intentionally symmetric, and bank 0 through bank 3 DCC/IQ/adaptation fields.
- Compare selected C20 PHY definitions against nearby generated ASIC headers such as `dcn_3_2_0_sh_mask.h` to catch accidental shift drift while allowing intentional IP-version differences.
- Exercise DP/HDMI/FRL link bring-up across supported rates and lane counts. Expected signals include stable link training, no unexpected PHY interrupt storms, sane PLL lock/calibration status, and no lane-specific failures.
- Exercise suspend/resume, hot reset, display modesets, and rapid link disable/enable cycles to catch stale override, calibration-done, reset, or power-domain assumptions.
- Run PHY margining and RX adaptation paths where available. Watch for correct margin start/finish/error events, plausible FOM/adaptation readbacks, and no stuck update or interrupt-clear bits.
- Validate TX equalization and preset coefficient programming via link training logs, register dumps, and sink-side behavior, especially for the duplicated lane0/lane1 PIPE message-bus groups.
- Use register dumps around RTUNE, MPLLA/MPLLB, DCC, and analog CREG fields during known-good boot/link states as golden signals for bitfield placement.

## Cross-Chunk Notes

The previous chunk owns the preceding TX PMA fields and the start of the `C20_PHY_CR0_RAWLANEX_DIG_TX_PMA_XF_LANE_RTUNE_CTL_1` context. This chunk starts with that register's two shift definitions and then transitions into RX PCS/FW/control/FSM, always-on lane calibration, lane0/lane1 PIPE message-bus, and CR1 supervisor metadata. The next chunk must finish `C20_PHY_CR1_SUP_DIG_ANA_XF_MPLLA_ANA_CREG03` and continue the remaining CR1 analog/PLL definitions before the final per-file synthesis makes whole-header claims.
