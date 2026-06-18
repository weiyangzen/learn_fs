# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 125850-128517

## Purpose

This chunk is generated AMD DPCS 4.2.3 register-field metadata. It contains no executable C code; it publishes preprocessor constants that describe bit positions for fields in `C20_PHY_CR1_RAWLANE*` DPCS/PHY control registers. Consumer code uses these constants with AMD display register helpers and matching register-address metadata to compose, read, update, or decode 16-bit PHY control-register fields.

The selected range covers the tail of CR1 raw lane 0 receive IRQ/control/FSM field shifts, complete repeated digital TX/RX/firmware/FSM field-shift blocks for raw lanes 1 and 2, and the beginning of raw lane 3 through the first field of `C20_PHY_CR1_RAWLANE3_DIG_RX_PCS_XF_CNTX_CFG_5`. The boundaries are artificial: line 125850 starts with the reserved shift for a lane 0 margin IRQ register whose comment is in the previous chunk, and line 128517 stops after the `RATE` field shift for a lane 3 RX context configuration register whose remaining fields continue in the next chunk.

Although this repository tree is under `sources/distributed-fs/ceph-client`, the file is AMDGPU display hardware metadata, not Ceph or distributed-filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, inline helpers, allocation paths, locks, or callbacks in this range. The entire public surface is generated `#define` names with the shape:

- `C20_PHY_CR1_RAWLANE<n>_<REGISTER>__<FIELD>__SHIFT`

The chunk contains 2,006 `#define` lines and no conventional field-mask suffix definitions for these `C20_PHY_CR1_*` registers. Some register names include the word `IRQ_MASK`, but those are register identifiers, not `_MASK` value macros. This means consumers that need masks either rely on generated masks elsewhere, helper-side width knowledge, or field definitions from a related generated header/version.

Major macro families in this slice:

- `RAWLANE0`: partial receive-side and FSM tail. The chunk includes RX margin IRQ clear/status shifts, RX term/adaptation/CDR/margining controls, RX PMA request/ack override shifts, FSM override/jump/breakpoint/status/scratch/debug shifts, numerous fast/skip calibration controls, and `RX_CAL_STATUS`.
- `RAWLANE1` and `RAWLANE2`: full repeated lane bodies. Each lane has TX PCS bridge overrides and live inputs, TX firmware bridge overrides and live inputs, TX IRQ mask/enable/status/clear shifts, TX FSM/clock/termination/power-up/MPLL/RTUNE/PMA shifts, RX PCS bridge overrides and live inputs, RX PCS context configuration fields, RX firmware bridge fields, RX IRQ controls, RX PMA/adaptation/margin controls, and FSM calibration controls.
- `RAWLANE3`: beginning of the repeated lane body. The chunk includes TX PCS bridge, TX firmware bridge, TX IRQ/control/PMA/RTUNE shifts and the start of RX PCS bridge/context fields through `RX_PCS_XF_CNTX_CFG_5__RATE__SHIFT`.

Representative field groups:

- Bridge handshakes: `RESET`, `REQ`, `ACK`, and corresponding `*_OVRD_EN` bits for PCS, firmware, PMA, TX, and RX crossings.
- Link and lane mapping: `LANE_LINK_NUM`, `LANE_NUMBER`, `CNTX_SEL`, `TX_UNIQUE_ID`, and RX `UNIQUE_ID`.
- TX datapath controls: `PSTATE`, `LPD`, `DATA_EN`, `INVERT`, `CLK_RDY`, `BEACON_EN`, `MPLL_EN`, `MPLLB_SEL`, `WIDTH`, `RATE`, `ALIGN_WIDE_XFER_EN`, `VREG_TX_BYPASS`, `VBOOST_EN`, `IBOOST_LVL`, `DRV_EN_KR`, `DCC_CTRL_RANGE`, `DCC_BYPASS`, `TERM_CTRL`, RX-detect request/result, parallel/serial loopback, and RTUNE request/ack.
- RX datapath controls: `CDR_SSC_EN`, `ADAPT_REQ`, `ADAPT_IN_PROG`, `MARGIN_IQ`, `MARGIN_VDAC`, `MARGIN_IN_PROG`, `MARGIN_ERROR_CLEAR`, `RECAL_FORCE_EN`, `RECAL_SKIP_EN`, `RECAL_BANK_SEL`, `LOOPBACK_SEL`, equalization fields, CDR VCO/reference load values, signal-detect thresholds, DCC/term controls, and adaptation/offcan continuous-mode bits.
- IRQ controls: TX and RX interrupt mask, enable-flag, latched IRQ, and clear registers for rate, reset, request, pstate, adaptation, margining, term-control, loopback, RTUNE, lane transceiver mode, and calibration done events.
- FSM and calibration controls: FSM override/jump/bank, breakpoints, memory address monitor, status monitor, firmware configuration stage, scratch/debug registers, CR lock, fast-path controls, many `SKIP_*` startup/continuous/rate calibration bits, and `RST_CAL_DONE`.

Most fields in the chunk are 1-bit or small packed fields inside 16-bit PHY control-register words. Reserved-field shift definitions such as `RESERVED_15_1`, `RESERVED_15_8`, and `RESERVED_15_15` document layout gaps and must be preserved by register writers unless the hardware programming guide explicitly says otherwise.

## Control Flow

This header has no runtime control flow. It does not branch, call functions, poll hardware, sleep, retry, or handle errors.

Runtime control flow is supplied by AMD display code that includes the generated headers and then performs register operations. The observed integration point in this tree is `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. Display-core resource, link, PHY, diagnostics, and bring-up code can then use generated names with register helper macros to program DPCS state.

The field names imply sequencing requirements that are not encoded here:

- `REQ`/`ACK` pairs require consumer-side request issue, polling, timeout, and cleanup logic.
- `RESET` and `RESET_OVRD_EN` fields must be ordered against clock, data-enable, power-state, and lane-rate changes.
- `*_IRQ`, `*_IRQ_CLR`, `IRQ_MASK`, and `IRQ_EN_FLAGS` fields require interrupt masking, latch clearing, and status interpretation in the right order.
- Calibration controls such as `FAST_*`, `SKIP_*`, `RST_CAL_DONE`, `RECAL_FORCE_EN`, and `RECAL_SKIP_EN` affect hardware FSM paths and must be sequenced with link training and PHY power-up/down code.
- Margining fields such as `MARGIN_IQ`, `MARGIN_VDAC`, `MARGIN_IN_PROG`, and `MARGIN_ERROR_CLEAR` require a higher-level margining procedure to avoid stale status or forced analog state.

## State And Persistence Behavior

The file stores no software state and persists nothing to disk. It describes hardware state locations and bit positions.

The represented state includes:

- Per-lane TX/RX bridge state between PCS, firmware, and PMA blocks.
- Per-lane reset/request/ack handshakes.
- Power state and low-power-detect inputs.
- Link rate, lane width, clock readiness, MPLL selection/state, data enable, invert, beacon, deskew, and loopback configuration.
- TX termination, DCC, boost, bypass, and RTUNE controls.
- RX CDR, VCO/reference load, equalization, CTLE/VGA/DFE/AFE, signal-detect, adaptation, margining, and recalibration controls.
- IRQ mask/enable/status/clear bits for lane events.
- FSM override, debug, scratch, skip, fast-path, and calibration-done fields.

Persistence depends entirely on the GPU hardware domain. Some fields are configuration bits that may persist until a modeset, link retrain, power-gate event, suspend/resume, or ASIC reset. Other fields are live status, sticky IRQ latches, write-one-to-clear bits, self-clearing controls, or read-only firmware/PMA outputs. This generated shift-only header does not encode access type, reset value, volatility, or side effects, so consumers must follow the hardware programming sequence for each block and preserve reserved bits during read-modify-write operations.

## Dependencies And Integration Points

Primary dependencies:

- The generated DPCS 4.2.3 register database that produced this header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, included beside this header by DCN316 resource code.
- AMD display register helper layers that combine register offsets, shifts, and masks or widths into MMIO/indirect-register reads and writes.
- DCN316 display resource setup in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`.

Important integration surfaces are DisplayPort/USB-C PHY lane bring-up, link training, lane mapping, link-rate changes, low-power transitions, hotplug recovery, suspend/resume, PHY margining, loopback/compliance modes, firmware-managed lane power-up, RTUNE, and hardware diagnostics.

A notable naming integration risk is that this slice uses `C20_PHY_CR1_RAWLANE*` mask names, while the DPCS offset header visible in the same directory largely exposes `DPCSSYS_CR*` offset names. Related DCN headers also contain `C20_PHY_CR1_*` shift and mask definitions. Merge/reconciliation should therefore avoid assuming a simple one-to-one token match with `dpcs_4_2_3_offset.h` for every macro in this tail of the DPCS mask header.

## Risks And Edge Cases

- Generated-header mismatch is the dominant risk. A shift definition from this header must match the exact ASIC register database and access path used by the caller; mixing DPCS/DCN generations can compile while programming or decoding the wrong bit.
- This chunk is shift-only for these `C20_PHY_CR1_*` fields. Code expecting sibling `_MASK` macros in this same file range will fail to compile or, worse, may accidentally use masks from another generated header.
- The chunk boundaries split logical register groups. Line 125850 is already inside lane 0 RX margin IRQ metadata, and line 128517 stops inside lane 3 `RX_PCS_XF_CNTX_CFG_5`; adjacent chunks are required for a complete per-file narrative.
- Per-lane repetition makes copy/paste and lane-index mistakes easy. Lane 1 and lane 2 are full repeated bodies, while lane 0 and lane 3 are partial in this chunk.
- Override fields are high risk. Setting `*_OVRD_EN` without a consistent forced value can override firmware/PCS/PMA handshakes and break link training, low-power entry/exit, clocking, or calibration.
- Reset/request/ack and IRQ clear bits are sequencing-sensitive. Missing timeouts or clearing a latch before reading the relevant status can hide link failures.
- Calibration skip/fast bits can mask real analog problems. Incorrect use may make bring-up appear faster while leaving unstable CDR, DCC, AFE, CTLE, VGA, DFE, IQ, signal-detect, or margining state.
- Reserved fields are common. Writers must preserve them during read-modify-write; using a whole-register write based only on visible non-reserved shifts can corrupt undocumented hardware state.
- The raw PHY naming indicates low-level hardware contracts. These macros should not be used casually from generic display code without the associated ASIC-specific programming sequence.

## Test Signals

Useful validation is mostly build, static-generation, and hardware integration coverage:

- Build coverage for DCN316/AMDGPU display code that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static checks that generated shift values for each register are within 0-15 for these 16-bit control-register fields and that packed fields do not overlap when widths/masks are available from the source register database or a sibling generated header.
- Header consistency checks against the generator input and related DCN/DPCS generated headers, especially for `C20_PHY_CR1_RAWLANE*` names that may not have obvious offset-token peers in `dpcs_4_2_3_offset.h`.
- Display bring-up across lane counts and lane mappings that exercise raw lanes 1 and 2, plus boundary coverage for lane 0 RX/FSM and lane 3 TX/RX PCS portions.
- Link training and hotplug tests at multiple rates and widths, including reset/request/ack handshakes, pstate transitions, MPLL selection, lane deskew, data enable, invert, and clock-ready handling.
- Suspend/resume and power-gating tests that verify lane power-up, low-power detect, firmware ACKs, and reset return behavior.
- PHY diagnostics and compliance tests for RX/TX loopback, RTUNE request/ack, RX margining, adaptation request/disable paths, CDR/VCO load fields, equalization context fields, and calibration-done status.
- Regression signals include blank display, link-training timeout, repeated hotplug retraining, high error counters, lane-specific failures, incorrect pstate behavior, stuck ACK/REQ bits, uncleared IRQ latches, failed margining, or failures isolated to CR1 raw lanes 1/2.
