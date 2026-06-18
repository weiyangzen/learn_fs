# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 71103-73540

## Purpose

This chunk is a generated DCN 3.2.0 shift/mask header slice for the `c20_phy_cr0_rdpcspipecrind` raw-lane PHY/DPCS register space. It defines C preprocessor constants for bit positions (`__SHIFT`) and bit masks (`_MASK`) used when AMDGPU display code reads or writes DCN 3.2.0 PHY control/status registers. The content is data, not executable code, but it is still part of the hardware programming contract: every value encodes where a named register field lives in a 16-bit PHY register.

The range contains 2,124 `#define` entries across 314 register comment sections. It starts in the middle of `C20_PHY_CR0_RAWLANE0_DIG_TX_PCS_XF_OVRD_IN_1`, covers the remainder of raw lane 0 transmit PCS/FW/IRQ/PMA blocks, raw lane 0 receive PCS/FW/IRQ/control/PMA blocks, raw lane 0 digital FSM debug/calibration controls, and then continues into the beginning of raw lane 1 transmit and receive PCS/FW/IRQ definitions. It ends in the first four shift definitions for `C20_PHY_CR0_RAWLANE1_DIG_RX_IRQ_CTL_IRQ_MASK`; the rest of that register is in the next chunk.

## Important APIs, Types, and Register Groups

There are no C functions, structs, enums, or inline helpers here. The exported API is the macro namespace consumed by AMD display register helpers and by any code building DCN 3.2.0 shift/mask tables. Names follow the generated pattern:

- `<register>__<field>__SHIFT` for the bit offset.
- `<register>__<field>_MASK` for the unshifted field mask.
- `C20_PHY_CR0_RAWLANE<n>_...` to identify the PHY instance (`CR0`) and raw lane index (`RAWLANE0`, `RAWLANE1`).

Major groups in this chunk:

- Raw lane 0 TX PCS crossbar controls: `DIG_TX_PCS_XF_OVRD_IN_*`, `DIG_TX_PCS_XF_IN_*`, `DIG_TX_PCS_XF_OVRD_OUT_0`, `DIG_TX_PCS_XF_OUT_0`, and `DIG_TX_PCS_XF_CNTX_CFG_*`. These describe reset/request handshakes, power state (`PSTATE`), low-power detect (`LPD`), data enable, polarity invert, clock ready, beacon, MPLL state, detect-RX request/result, deskew enable, recalibration force/skip, context select, rate/width, MPLLB select, TX voltage/boost/current controls, DCC controls, termination, and TX unique ID.
- Raw lane 0 TX firmware crossbar controls: `DIG_TX_FW_XF_OVRD_IN_*`, `DIG_TX_FW_XF_IN_0`, `DIG_TX_FW_XF_OUT_0`, and `DIG_TX_FW_XF_LANE_NUMBER`. These expose firmware-visible override, request, reset, clock, lane number, and ACK fields for TX-side sequencing.
- Raw lane 0 TX interrupt controls: `DIG_TX_IRQ_CTL_IRQ_MASK`, `DIG_TX_IRQ_CTL_IRQ_EN_FLAGS`, per-event IRQ status registers, and matching `_CLR` registers for rate, reset, request, RX-to-TX loopback enable/disable, resistor tune (`RTUNE`), termination control, and lane transceiver mode.
- Raw lane 0 TX digital control/PMA controls: `DIG_TX_CTL_FSM_CTL`, `DIG_TX_CTL_CLK_CTL`, off-cancellation status, rate IRQ ACK, termination code, firmware power-up done, MPLLA/MPLLB restart calibration controls, PMA lane/supervisor override inputs and outputs, PMA input status, and lane RTUNE controls.
- Raw lane 0 RX PCS and firmware crossbar controls: `DIG_RX_PCS_XF_OVRD_IN_*`, `DIG_RX_PCS_XF_IN_*`, `DIG_RX_PCS_XF_CNTX_CFG_*`, `DIG_RX_FW_XF_OVRD_IN_*`, `DIG_RX_FW_XF_IN_0`, `DIG_RX_FW_XF_OVRD_OUT_0`, `DIG_RX_FW_XF_ADAPT_ACK`, `DIG_RX_FW_XF_ADAPT_FOM`, TX pre/main/post direction hints, RX clock control, and ACK output.
- Raw lane 0 RX interrupt and control registers: RX IRQ masks/enables/status/clear fields for reset, request, rate, pstate, adaptation request/disable, term control, and margining events; RX term/offcan/adaptation status; PPM drift; CDR detect; PMA miscellaneous controls; adaptation mode override/enable; margin IQ/VDAC/status/error controls; phase-adjustment update controls; RX FSM and IQ step read/write fields.
- Raw lane 0 digital FSM controls: `DIG_FSM_FSM_OVRD_CTL`, jump bank, auto-reset control, breakpoints, memory address/status monitors, firmware config stage, scratch registers 0-11, lock bits, fast/skip flags for TX and RX calibration or adaptation phases, and `DIG_FSM_RX_CAL_STATUS`.
- Raw lane 1 beginning: equivalent TX PCS lane loopback/link-number controls, TX PCS/FW/IRQ/TX control/PMA groups, and RX PCS/FW groups through the start of `DIG_RX_IRQ_CTL_IRQ_MASK`. These mirror raw lane 0 naming and bit layouts for the next physical lane.

Representative field families:

- Handshake bits: `RESET`, `REQ`, `ACK`, `*_OVRD_EN`, and interrupt clear fields.
- Link and electrical configuration: `RATE`, `WIDTH`, `PSTATE`, `MPLLB_SEL`, `MPLL_EN`, `TERM_CTRL`, `VBOOST_EN`, `IBOOST_LVL`, `DCC_*`, `VCO_LD_VAL`, `REF_LD_VAL`, and `CDR_PPM_MAX`.
- RX adaptation and margining: `EQ_ATT_LVL`, `EQ_VGA_GAIN`, `EQ_CTLE_*`, `EQ_DFE_TAP1`, `DFE_BYPASS`, `ADAPT_REQ`, `ADAPT_MODE`, `ADAPT_SEL`, `ADAPT_FOM`, `MARGIN_IQ`, `MARGIN_VDAC`, margin IRQs, IQ/phase adjustment fields, and `RX_MARGIN_*` status/error fields.
- Debug and microsequencer controls: `FSM_JMP_ADDR`, `FSM_CMD_START`, `FSM_OVRD_EN`, breakpoints, status flags, scratch registers, fast flags, skip flags, and CR register/memory locks.

## Control Flow

This file chunk has no local control flow. Runtime flow is created when display driver code combines these shift/mask constants with matching address macros and MMIO helper macros.

The intended flow for consumers is:

1. Select the C20 PHY CR instance and raw lane register address from the matching offset header or indirect-register table.
2. Use the `__SHIFT` and `_MASK` symbols to encode or decode a field value in that register.
3. Program the hardware through the AMD display register helpers, direct indirect-register access, or generated tables.
4. Poll or clear corresponding ACK/status/IRQ fields when the hardware sequence requires it.

The control semantics represented by the fields are primarily PHY sequencing rather than CPU branches: TX/RX reset-request-ACK handshakes, power-state transitions, PLL enable/state selection, lane deskew, RX adaptation, margining, DCC/off-cancellation, RX detect, lane loopback, interrupt masking/enabling/clearing, and debug FSM override/jump sequences.

The chunk boundaries are important for reconciliation. The first two lines are only the tail masks of `RAWLANE0_DIG_TX_PCS_XF_OVRD_IN_1`; the associated shifts and most masks for that register live in the previous chunk. The final register, `RAWLANE1_DIG_RX_IRQ_CTL_IRQ_MASK`, is incomplete here and continues after line 73540.

## State and Persistence Behavior

The header itself stores no state. The constants describe stateful hardware registers whose values persist in the PHY block until reset, power gating, firmware/driver reprogramming, or a later MMIO/indirect write changes them.

State domains represented here include:

- TX lane configuration state: lane link number, loopback enable, TX power state, rate, width, data enable, invert, clock ready, TX current/boost/voltage controls, termination code, DCC settings, recalibration skip/force, and MPLL selection/enables.
- RX lane configuration state: RX power state, data enable, invert, CDR SSC, rate/width, analog equalizer settings, CTLE/DFE controls, VCO/reference load values, signal-detect thresholds, DCC bypass, RX clock enables, and adaptation mode/selection.
- Handshake and event state: reset/request/ACK bits, IRQ mask/enable/status/clear bits, block-ACK enable bits, rate IRQ ACK, RX valid override, adaptation ACK/FOM, detect-RX result, and margining status/error fields.
- Calibration/debug state: FSM current state, command-ready and ALU/wait status bits, breakpoints, firmware stage flags, scratch registers, CR lock bits, fast path flags, and skip flags for TX/RX calibration and adaptation phases.

Many fields have write-one-to-clear, clear-on-write, status, or override-enable behavior in hardware even though this header only names bit locations. Incorrect masks can therefore cause persistent hardware side effects: uncleared interrupts, stuck reset/request handshakes, disabled calibration, wrong equalization, or locked debug/register access.

## Dependencies and Integration Points

This file depends on the matching DCN 3.2.0 offset header for register addresses and base/instance selection. In `dcn_3_2_0_offset.h`, the relevant address block is `c20_phy_cr0_rdpcspipecrind`; it exposes raw-lane IRQ mask addresses such as `ixC20_PHY_CR0_RAWLANE0_DIG_TX_IRQ_CTL_IRQ_MASK`, `ixC20_PHY_CR0_RAWLANE0_DIG_RX_IRQ_CTL_IRQ_MASK`, `ixC20_PHY_CR0_RAWLANE1_DIG_TX_IRQ_CTL_IRQ_MASK`, and `ixC20_PHY_CR0_RAWLANE1_DIG_RX_IRQ_CTL_IRQ_MASK`, plus lane status addresses such as `ixC20_PHY_CR0_LANE0_DIG_RX_ADPTCTL_VGA_STATUS`.

The wider AMD display stack uses these generated headers through register helper macros and generation-specific register tables. Older DPCS integration files show the same raw-lane programming model clearly: `dcn201_link_encoder.h` maps raw-lane RX override registers with `SRI_IX(RAWLANE0_DIG_PCS_XF_RX_OVRD_IN_2, DPCSSYS_CR, id)` and maps field names like `VCO_LD_VAL_OVRD`; `dcn20_link_encoder.h`, `dcn21_link_encoder.h`, and HPO link encoder files use related RDPCS/DPCS fields for DP alternate mode, clock readiness, data enable, TX EQ, and PHY power sequencing. This DCN 3.2.0 C20 block is a newer generated register namespace for the same class of PHY/link-lane responsibilities.

Integration points to check during merge:

- `dcn_3_2_0_offset.h` must contain every address needed by any C20 field table that consumes these masks. This slice includes many more field definitions than the narrow set of C20 raw-lane addresses visible in the offset header excerpt, so direct consumers may be sparse or generated elsewhere.
- Any driver table using `LE_SF`, `SE_SF`, `SRI_IX`, `REG_GET`, `REG_SET`, or `REG_UPDATE` for C20 PHY raw-lane fields depends on the field name, shift, and mask matching exactly.
- The lane instance pattern must remain consistent across `RAWLANE0`, `RAWLANE1`, later raw lanes, and other `C20_PHY_CR<n>` copies in the same generated header.
- The register families in this chunk connect to DP link training, PHY power sequencing, RX adaptation, lane margining, IRQ handling, and low-level debug flows rather than to high-level stream encoder packet programming.

## Risks

- Bit drift is the primary risk. A wrong shift or mask compiles cleanly but programs the wrong hardware bit, which can break link bring-up, RX adaptation, margining, calibration, interrupt handling, or lane power transitions.
- The generated naming is highly repetitive. A raw-lane or CR-instance copy error between `RAWLANE0` and `RAWLANE1`, or between `C20_PHY_CR0` and later CR blocks, is hard to spot by review because most registers are structurally identical.
- Override pairs are fragile. Fields such as `PSTATE`/`PSTATE_OVRD_EN`, `RATE`/`RATE_OVRD_EN`, `WIDTH`/`WIDTH_OVRD_EN`, `ACK`/`ACK_OVRD_EN`, and `*_OVRD_VAL`/`*_OVRD_EN` must be paired correctly; a mask error can leave firmware or hardware sequencing overridden unintentionally.
- IRQ masks, enables, status, and clear fields are easy to confuse because the same event names appear in several registers. Mixing status and `_CLR` masks can leave interrupts stuck active or permanently masked.
- Calibration skip and fast flags directly affect PHY bring-up quality. Incorrect definitions around `SKIP_RX_*`, `FAST_RX_*`, `FAST_TX_*`, DCC range/calibration, DFE/CTLE/VGA adaptation, or margining can produce intermittent monitor compatibility failures rather than immediate build failures.
- Debug FSM fields (`FSM_JMP_ADDR`, breakpoints, scratch registers, locks) are low-level and potentially disruptive. Wrong masks could interfere with firmware-controlled PHY microsequencing or make indirect debug access unreliable.
- The chunk begins and ends inside logical register families. A merge that treats this chunk as a complete lane report without adjacent chunks would miss the start of `TX_PCS_XF_OVRD_IN_1` and the completion of `RAWLANE1_DIG_RX_IRQ_CTL_IRQ_MASK`.

## Test Signals

Useful validation is mostly build-time plus hardware smoke coverage:

- Build signal: AMDGPU/DCN 3.2.0 code compiles with no missing C20 PHY shift/mask symbols in generated tables or register helper use.
- Header consistency checks: for every field, `MASK` covers the width implied by the next field shift or reserved field, and repeated `RAWLANE0`/`RAWLANE1` register layouts match where hardware expects them to match.
- Offset/mask pairing checks: C20 raw-lane register field definitions have matching `ixC20_PHY_CR0_*` addresses when consumed by code, especially TX/RX IRQ mask registers exposed in `dcn_3_2_0_offset.h`.
- DP link smoke tests: DP links train at expected rates and lane counts, clocks/data enable correctly, and hotplug/modeset cycles do not leave lanes stuck in reset or request/ACK waits.
- PHY power and calibration tests: suspend/resume, display idle, low-power transitions, and mode changes do not regress MPLL state, TX/RX power state, DCC/offcan, RX adaptation, or CDR/VCO behavior.
- IRQ tests: TX/RX rate, reset, request, adaptation, term-control, loopback, and margining IRQs can be masked, enabled, observed, and cleared without repeated storms or missed events.
- RX quality tests: equalizer, CTLE, DFE, VGA, IQ/phase adjustment, PPM drift, and margining status behave plausibly on hardware that exposes those diagnostics.
- Debug safety checks: use of FSM override, breakpoint, scratch, and lock fields remains limited to intended diagnostic paths and does not affect normal link training.
