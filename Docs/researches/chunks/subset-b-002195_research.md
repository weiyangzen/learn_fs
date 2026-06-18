# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 108007-110396

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask register-field slice for the DPCSSYS CR2 PHY lane register block. It contains no executable C logic; its exported surface is the preprocessor contract of `#define ...__SHIFT` and `#define ..._MASK` constants used by AMDGPU display register helpers to encode, update, and decode MMIO bitfields.

The requested range starts at the tail of `DPCSSYS_CR2_LANE1_DIG_ASIC_RX_OVRD_IN_4` mask definitions, then covers most of the remaining CR2 lane 1 digital/analog PHY lane fields, and ends early in `DPCSSYS_CR2_LANE2_DIG_ASIC_RX_ASIC_IN_0` at the `REQ_MASK` definition. The line boundaries are chunking artifacts, not hardware-block boundaries.

Although this path is under a local `ceph-client` tree, the content is AMDGPU display/PHY register metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct I/O operations in this range. The public API is the generated bitfield macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a field inside the register value.
- `<REGISTER>__<FIELD>_MASK`: bit mask for that field inside the register value.

This range contains 2,191 field definitions across 210 register-comment blocks: 1,101 `__SHIFT` constants and 1,090 `_MASK` constants. The mismatch is expected for this exact line slice because it begins and ends inside register definitions.

The visible register families are DPCSSYS CR2 lane 1 and the beginning of CR2 lane 2:

- Lane 1 ASIC override and live interface fields: RX/TX override inputs and outputs, `LANE_ASIC_IN`, `TX_ASIC_IN_0..2`, `TX_ASIC_OUT`, `RX_ASIC_IN_0..1`, `RX_ASIC_OUT_0`, RX EQ controls, RX CDR/VCO inputs, loopback controls, reset/disable/ack/status bits, lane rate/width/pstate selectors, RX/TX polarity inversion, request/data-enable/low-power controls, and override-enable gates.
- Lane 1 TX power and calibration fields: TX pstate presets `P0`, `P0S`, `P1`, `P2`, TX power-up timing registers, DCC CR-bank address/data registers, DCC DAC control/range/select/ack/address registers, clock-alignment control, and TX LBERT control fields.
- Lane 1 RX power, calibration, CDR, and adaptation fields: RX pstate presets, RX power-up timing, RX VCO calibration controls/timers/status, RX alignment communication mask, RX LBERT control/error counters, CDR control/status, DPLL frequency and bounds, adaptation configuration `ADPT_CFG_0..9`, adaptation reset, ATT/VGA/CTLE/DFE status, DFE data/error VDAC offsets, slicer controls, DAC control selection, and RX adaptation CR-bank address/data.
- Lane 1 RX statistics and MPHY fields: RX statistic load/mask/match/control/sample-count/counter/stop fields, calibration-comparison clock control, MPHY RX PWM, low-speed termination, and analog PWM-clock stability counter fields.
- Lane 1 digital-to-analog and analog fields: digital analog TX/RX override outputs, TX EQ override outputs, TX/RX termination-code override outputs, RX VCO override outputs, RX analog control/power/status/DAC/scope/slicer/IQ phase controls, signal-change enables, analog TX measurement/power/ATB/DCC/termination/misc/mux/vreg fields, and analog RX clock/CDR/slicer/power/squelch/calibration/ATB/VDAC/vreg fields.
- Lane 2 beginning: lane override input, TX override inputs and output, RX override inputs and outputs, ASIC lane input, TX ASIC input/output registers, and the beginning of `RX_ASIC_IN_0`.

Representative field names include `RESET`, `RESET_OVRD_EN`, `REQ`, `REQ_OVRD_EN`, `ACK`, `ACK_OVRD_EN`, `DISABLE`, `PSTATE`, `RATE`, `WIDTH`, `MPLLB_SEL`, `TX_MAIN_CURSOR`, `TX_PRE_CURSOR`, `TX_POST_CURSOR`, `DETRX_RESULT`, `ADAPT_AFE_EN`, `ADAPT_DFE_EN`, `CDR_TRACK_EN`, `CDR_SSC_EN`, `ALIGN_EN`, `RX_REF_LD_VAL`, `RX_VCO_CAL_START`, `RX_VCO_CAL_DONE`, `LBERT_EN`, `LBERT_ERR_OVRD_EN`, `DPLL_FREQ`, `ADPT_RESET`, `DFE_TAP1`, `DFE_TAP2`, `SLICER_CTRL`, `CR_ADDR`, `CR_DATA`, `STAT_CNT`, `PWM_EN`, `TERM_CODE`, `ATB_SEL`, `VREG_CTRL`, and many `RESERVED_*` placeholders.

Most masks in this chunk describe 16-bit PHY-side registers with values such as `0x0001L`, `0x00C0L`, `0x0FC0L`, `0xF000L`, and `0xFFFFL`. Consumers normally combine these masks with shifts through AMD display register helpers and generated register-field lists rather than using the constants as standalone logic.

## Control Flow

This header has no runtime control flow. Its role is compile-time macro expansion:

1. DCN 4.1.0 display code includes this shift/mask header with the matching generated offset headers for DPCSSYS/DPCS register addresses.
2. Register-list and field-list macros token-paste symbolic register and field names into per-block tables.
3. Runtime link, PHY, AUX/USB-C, DisplayPort, and debug paths call AMD register helpers. Those helpers read or write MMIO offsets from the offset headers and use these shift/mask constants to isolate fields.
4. Hardware sequencing for link training, PHY power state changes, resets, CDR/VCO calibration, adaptation, loopback, LBERT testing, statistics, and analog override control is implemented in driver code and hardware. This generated header only supplies bit positions and masks.

The repeated lane naming is part of the compile-time control path. A consumer expanding `DPCSSYS_CR2_LANE1_*` and one expanding `DPCSSYS_CR2_LANE2_*` can compile against similar field names while targeting different physical lane instances. The chunk boundary includes lane 1 mostly as a continuing block and lane 2 only through the early RX ASIC input definitions.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It defines field encodings for hardware-visible PHY state:

- Link-lane control state: resets, request/ack handshakes, data enable, lane disable, low-power entry, polarity inversion, loopback selection, TX/RX width, rate, pstate, and MPLL selection.
- TX analog/equalization state: main/pre/post cursor values, beacon/asynchronous transmit controls, boost and DCC bypass fields, termination-code and VREG controls, TX DCC DAC state, TX power-up timing, and TX pstate programming.
- RX clocking/equalization/adaptation state: RX termination, CDR tracking and SSC, alignment and clock shift, RX IQ phase adjustment, VCO reference/load/frequency controls, DPLL frequency bounds, AFE gain, CTLE boost, DFE taps, slicer settings, and adaptation configuration/status.
- Calibration and diagnostics state: VCO calibration start/status fields, LBERT enable/error controls, OCLA/debug controls, RX statistic match/control/counter fields, analog status fields, ATB measurement selections, and MPHY low-speed/PWM settings.
- Override state: many fields appear as value plus `*_OVRD_EN` pairs. The override-enable bit decides whether the paired software-provided value supersedes the normal hardware or microcontroller path.

Persistence is hardware-defined. Control and override fields generally remain until driver reprogramming, pstate transitions, link retraining, hotplug handling, suspend/resume, GPU reset, power gating, or ASIC reset. Status, acknowledgement, calibration-done, LBERT error, and statistic counter fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant lane block is powered and clocked. This header does not encode those access rules.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated register-header convention. This file must remain synchronized with:

- The matching DCN/DPCS offset headers that provide `ixDPCSSYS_CR2_LANE*...` addresses and base-index values.
- AMD's generated DCN 4.1.0 register database, because the masks and shifts are silicon ABI metadata.
- DCN 4.1.0 display code that builds link-encoder, PHY, AUX/USB-C, and debug register tables from generated offset and shift/mask headers.

Important integration points are the AMDGPU DCN link stack and PHY service code. Runtime code that programs DisplayPort/USB-C lane rate and width, lane pstate, TX drive/equalization values, receiver adaptation, CDR/VCO calibration, DPLL programming, and link diagnostics depends on these constants matching the hardware layout. Debug and bring-up paths also depend on the analog override, ATB, OCLA, LBERT, and statistic fields to inspect or force lane behavior safely.

The chunk also crosses a lane-instance boundary. Lane 1 definitions continue from earlier chunks and are followed by lane 2 definitions in this range; lane 2 continues in the next chunk. The final per-file report should reconcile adjacent chunks before describing all CR2 lanes as complete units.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting unrelated MMIO bits or decoding the wrong status.
- The file is generated. Manual edits risk divergence from the authoritative register database, paired offset headers, firmware assumptions, and silicon documentation.
- The chunk boundaries are not semantic. It begins with the tail masks for `DPCSSYS_CR2_LANE1_DIG_ASIC_RX_OVRD_IN_4` and ends before all masks for `DPCSSYS_CR2_LANE2_DIG_ASIC_RX_ASIC_IN_0` are visible.
- Repeated lane layouts make instance drift hard to catch. A `LANE1`/`LANE2` prefix mistake can still compile if both symbols exist, but it may program the wrong physical lane.
- Override fields are especially sensitive. Enabling an override bit without a matching value, or leaving an override enabled after diagnostics, can bypass normal hardware state machines for reset, request, pstate, termination, adaptation, CDR, or analog controls.
- Pstate, power-up timing, VCO calibration, CDR, and DPLL fields affect link stability. Incorrect masks can cause intermittent training failures, clock recovery loss, power-transition hangs, or marginal high-rate behavior that appears only on specific cables, retimers, docks, or displays.
- TX equalization and RX adaptation fields are protocol- and board-sensitive. Bad cursor, termination, boost, CTLE, DFE, slicer, or IQ-phase fields can produce eye-margin regressions without obvious compile-time signals.
- Statistic, LBERT, OCLA, ATB, and analog measurement fields are often used in bring-up or diagnostics. Wrong definitions can make debug output misleading, hide real errors, or force unsafe analog states during validation.
- Reserved fields are explicitly named in the generated layout. Consumers should preserve reserved bits through read-modify-write helpers unless the hardware specification says otherwise.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks, build coverage, and link-runtime behavior:

- Build the DCN 4.1.0 AMDGPU display code with the paired offset and shift/mask headers. Missing or renamed macros should fail in generated register-table initializers or register-helper use sites.
- Mechanically compare this range against AMD's authoritative DCN 4.1.0 register source. Treat the first and last registers as partial chunk boundaries.
- Run static checks that every complete field in the range has both `__SHIFT` and `_MASK`, and separately allow the known partial boundary cases at `RX_OVRD_IN_4` and `RX_ASIC_IN_0`.
- Check that lane 1 and lane 2 common ASIC TX/RX override and ASIC input/output field sets remain isomorphic where the hardware expects repeated lane layouts.
- Validate masks against shifts for packed fields such as `PSTATE`, `RATE`, `WIDTH`, `TX_MAIN_CURSOR`, `TX_PRE_CURSOR`, `TX_POST_CURSOR`, `EQ_DFE_TAP1`, `EQ_DFE_TAP2`, `DPLL_FREQ`, statistic counters, DCC DAC fields, and analog control fields.
- Exercise DisplayPort/USB-C link training across supported rates and lane counts on hardware using CR2 lanes. Watch for training failures, CDR lock loss, unstable pstate transitions, or lane-specific regressions.
- Exercise suspend/resume, hotplug, dock/retimer paths, GPU reset, and active-link power transitions. Expected signals are stable lane recovery, no stuck request/ack handshakes, and no lingering diagnostic overrides.
- Use PHY diagnostics where available: LBERT error counts, RX statistic counters, OCLA/ATB observations, VCO calibration status, and DPLL/CDR status should respond consistently with programmed register values.

## Cross-Chunk Notes

The previous chunk contains the earlier CR2 lane 1 register definitions, including the beginning of `DPCSSYS_CR2_LANE1_DIG_ASIC_RX_OVRD_IN_4`. The next chunk continues after `DPCSSYS_CR2_LANE2_DIG_ASIC_RX_ASIC_IN_0__REQ_MASK` with the rest of lane 2 RX ASIC input masks and later CR2 lane 2 register groups. The merge/reconciliation lane should join adjacent chunks before making whole-file claims about all DCN 4.1.0 DPCSSYS CR2 lane definitions.
