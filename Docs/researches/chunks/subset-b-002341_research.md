# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 9581-11939

## Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.2 shift/mask register header. It contains C preprocessor constants only; each useful symbol describes either a field bit offset (`...__SHIFT`) or a pre-shifted field mask (`..._MASK`) for DPCSSYS CR lane registers. Runtime display code pairs this file with `dpcs_4_2_2_offset.h` and AMD display register helpers so link/PHY code can compose indexed DPCS register reads and writes without embedding numeric bit positions.

The requested range is a line-bounded PHY slice. It starts in the tail of `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`, completes lane 1 analog TX/RX control and measurement fields, covers a large lane 2 digital and analog PHY block, and ends at the comment for `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2`. The `RX_PWR_CTRL2` fields themselves are outside this chunk. The range contains 2,140 `#define` lines across 219 register groups: 1,069 shift definitions and 1,071 mask definitions. The small imbalance is expected because the first visible register began in the previous chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocation paths, locks, callbacks, or executable APIs in this chunk. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position, usually in a 16-bit-style DPCS CR register payload and emitted with an `L` suffix.

The important source-aligned register families are:

- `DPCSSYS_CR0_LANE1_ANA_TX_*`: tail of lane 1 analog transmitter fields for DCC DAC selection/control, termination code and update/reset controls, TX clock override, VREG/current behavior, slew/inversion/peaking options, ATB force bits, and reserved low-byte fields.
- `DPCSSYS_CR0_LANE1_ANA_RX_*`: lane 1 analog receiver fields for CDR/VCO startup and clock enable overrides, IQ phase adjustment, loopback clock, deserializer/word-clock controls, slicer controls, AFE/DFE/DESER/loopback power overrides, signal-detect threshold/response, calibration mux selections, ATB regulator/reference and measurement controls, VDAC ranges, CDR regulator behavior, and reserved fields.
- `DPCSSYS_CR0_LANE2_DIG_ASIC_*`: lane 2 digital ASIC override, ASIC input, and ASIC output fields for loopback, lane enable, RX AC JTAG, TX/RX request/p-state/rate/width, MPLLB selection, data enable, TX main/pre/post cursor values, HDMI mode, clock-ready, RX detect, polarity inversion, low-power detect, DC coupling, MPHY mode, reset, boost/equalization controls, VCO/DAC controls, signal detect, adaptation status, ACK/valid flags, OCLA, and repeat/master lane clock synchronization.
- `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX p-state recipes for P0/P0S/P1/P2, TX power-up timing fields, DCC CR bank address/data, DCC DAC enable/range/selection/ack/address fields, clock alignment, and TX LBERT control.
- `DPCSSYS_CR0_LANE2_DIG_RX_PWRCTL_*`, `*_RX_VCOCAL_*`, `*_RX_CDR_*`, and `*_RX_DPLL_*`: lane 2 RX p-state and timing controls, RX VCO calibration controls/status/timers, XAUI comma mask, RX LBERT control/error count, CDR/SSC/PI controls, CDR lock/status, DPLL frequency, and DPLL frequency bounds.
- `DPCSSYS_CR0_LANE2_DIG_RX_ADPTCTL_*`: lane 2 receiver adaptation configuration and status fields for ATT, VGA, CTLE, DFE taps 1-5, even/odd data and error VDAC offsets, slicer controls, error slicer level, adaptation reset, DAC selector controls, and CR bank address/data access.
- `DPCSSYS_CR0_LANE2_DIG_RX_STAT_*`: data-mask, match-control, statistic-control, sample-count, statistic counter, calibration-comparator clock, additional match controls, statistic-control extension, and statistic-stop fields.
- `DPCSSYS_CR0_LANE2_DIG_MPHY_*`: MPHY low-speed PWM, termination, and analog PWM clock-stability fields.
- `DPCSSYS_CR0_LANE2_DIG_ANA_*`: digital-to-analog bridge fields for TX override outputs, TX termination-code outputs, TX equalization outputs, RX control/power/VCO override outputs, RX calibration/DAC/AFE/CTLE/scope/slicer/IQ controls, analog status readback, MPHY override outputs, signal-detect override outputs, and TX DCC DAC override outputs.
- `DPCSSYS_CR0_LANE2_ANA_TX_*`: direct lane 2 analog TX fields for override measurement, power override, alternate bus, ATB muxing/measurement, DCC DAC, termination code and update/reset controls, clock overrides, miscellaneous TX controls, and reserved fields.
- `DPCSSYS_CR0_LANE2_ANA_RX_CLK_1`, `CLK_2`, `CDR_DES`, `SLC_CTRL`, and `PWR_CTRL1`: beginning of direct lane 2 analog RX fields for CDR/VCO startup, RX clock enable override, IQ phase adjustment, loopback clock, word-clock/deserializer controls, slicer controls, AFE/ACJT power controls, common-mode selection, and attenuator pulldown.

Reserved, `NC*`, and `RSVD*` fields are still emitted as masks. They are part of the register layout contract even when ordinary driver code should preserve them rather than treat them as programmable features.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers:

1. DCN315 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Register-list macros such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(__SHIFT/_MASK)` token-paste DPCS register and field names into link-encoder register tables.
3. Link encoder, PHY, clock/power, training, and diagnostics code uses those tables through AMD register helpers to read, write, update, and poll DPCS fields.
4. Hardware and firmware sequencing decides when to apply p-state recipes, rate/width changes, resets, CDR/DPLL/VCO calibration, RX adaptation, TX DCC settings, LBERT/loopback modes, statistic sampling, or analog override paths.

The macros do not encode access semantics. They do not say whether a field is read-only, sticky, write-one-to-clear, self-clearing, reset-sensitive, or safe to modify while a link is active.

## State And Persistence Behavior

The file itself stores no software state and persists nothing. It describes hardware-backed lane state:

- Lane 1 analog TX/RX trim, clocking, DCC, termination, CDR/deserializer, slicer, signal-detect, ATB, and calibration selection state.
- Lane 2 digital override and normal ASIC interface state for lane requests, p-states, rate/width, data enable, cursor/equalization, reset, detect, polarity, loopback, low-power, MPHY, VCO/DAC, adaptation, and status handshakes.
- Lane 2 TX/RX p-state recipes and power-up wait counters used by hardware sequencing.
- Lane 2 RX clock recovery, VCO calibration, DPLL, CDR, SSC, adaptation, slicer, CTLE/VGA/DFE, statistic counter, and LBERT state.
- Lane 2 digital-to-analog bridge state and direct analog TX/RX override/measurement state.

Persistence is device-local and tied to hardware reset and power domains. Configuration fields can remain until a modeset, link retrain, lane reset, DPCS block reset, power-gate transition, suspend/resume restore, or ASIC reset. Status, ACK, calibration, counter, and measurement fields can change asynchronously while the PHY trains, calibrates, enters low power, receives symbols, or runs diagnostics.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h`, which provides the matching indexed DPCS register addresses and base-index metadata. Shifts and masks are not meaningful without the correct offset header.

The direct include site found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both the DPCS 4.2.2 offset and shift/mask headers and builds DCN315 link encoder register, shift, and mask tables. The shared macro definitions live in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` through `DPCS_DCN31_REG_LIST` and `DPCS_DCN31_MASK_SH_LIST`.

Functionally, these fields integrate with AMD display link encoder and PHY paths: DisplayPort/HDMI lane bring-up, link training, lane-rate and lane-width programming, p-state transitions, suspend/resume restore, hotplug-triggered retraining, clock recovery, RX adaptation, analog trimming, signal-detect handling, loopback/BERT diagnostics, statistic counters, and manufacturing/debug access through ATB/OCLA-style paths.

The generated namespace is ASIC-version-specific. Nearby headers such as `dpcs_4_2_0_sh_mask.h` and `dpcs_4_2_3_sh_mask.h` have similar shapes, but consumers must bind the DPCS 4.2.2 mask file to the DPCS 4.2.2 offset file and the target DCN315 register tables unless the hardware database explicitly says a layout is shared.

## Risks And Edge Cases

- Shift/mask drift is high impact. These are untyped preprocessor constants, so a one-bit error can compile cleanly while writing a neighboring PHY field.
- Offset/header mismatch can apply a valid field mask to the wrong indexed DPCS register address.
- Override-enable fields are hazardous. `*_OVRD*`, p-state, reset, rate, width, cursor, termination, DCC, VCO, CDR, DPLL, MPHY, loopback, and analog mux fields can force hardware away from normal sequencing.
- Lane-instance mistakes may be connector-specific. A lane 1 or lane 2 table error may only reproduce on displays or link configurations that use that physical lane.
- Reserved and `NC` fields are exposed as masks. Driver read-modify-write paths should preserve them unless hardware documentation requires an explicit value.
- Timing and count fields are narrow. Callers must clamp or mask software values before shifting so high bits do not spill into adjacent fields.
- Status, ACK, counter, and calibration fields can be transient or side-effect-sensitive. Wrong masks can cause polling timeouts, false adaptation status, lost LBERT/statistic data, stuck calibration flows, or bad link-training decisions.
- The chunk boundaries are artificial. The first visible register is only the mask tail of `LANE1_ANA_TX_DCC_DAC`, and the final `LANE2_ANA_RX_PWR_CTRL2` comment has no fields in this range. Whole-register validation needs neighboring chunks.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU/DC with DCN315 support enabled so `dcn315_resource.c`, `dcn31_dio_link_encoder.h`, and DPCS register-table expansion catch missing, renamed, or malformed macros.
- Mechanically verify shift/mask pairing after merging adjacent chunks. For this exact range, 1,069 shifts and 1,071 masks are expected because the start boundary includes masks whose shifts are above line 9581.
- Cross-check `dpcs_4_2_2_sh_mask.h` against `dpcs_4_2_2_offset.h` so every covered register group has a matching indexed register address and base-index context.
- Compare repeated lane 1/lane 2 field layouts against adjacent lane blocks and nearby generated DPCS 4.2.x variants where the hardware register database expects matching geometry.
- Exercise display links using the affected lanes across link rates, lane counts, hotplug, retraining, suspend/resume, low-power entry/exit, and mode changes. Watch for lane-specific training failures, blank displays, repeated retraining, stuck reset/power status, or signal-detect errors.
- Run PHY diagnostics where available: LBERT/loopback, statistic counters, CDR/DPLL/VCO calibration polling, RX adaptation status, TX DCC DAC programming, OCLA/ATB measurement routing, and analog status readback.
- Inspect kernel logs and register dumps for wrong ACK/valid bits, unexpected p-state recipes, invalid cursor/equalization values, stuck calibration-done fields, counter overflow handling problems, or connector-specific instability after generated-register changes.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`. The next chunk owns all fields under `DPCSSYS_CR0_LANE2_ANA_RX_PWR_CTRL2` and continues later lane 2 analog RX definitions. The final per-file research document should reconcile those boundaries before making whole-file claims about DPCS 4.2.2 lane coverage or shift/mask pairing.
