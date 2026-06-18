# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 69372-71761

## Purpose

This chunk is generated AMD DCN 4.1.0 register field metadata. It contains C preprocessor constants only; every useful symbol describes either a field bit offset (`...__SHIFT`) or a pre-shifted field mask (`..._MASK`) for DPCSSYS clock-recovery/PHY lane registers. Runtime display code combines these constants with the matching offset header and AMD display register helpers to read, write, update, and poll hardware fields without hard-coding bit positions.

The requested range is a lane-oriented DPCSSYS slice. It begins in the tail of `DPCSSYS_CR0_LANE1_ANA_RX_SQ`, finishes the visible lane 1 analog RX controls, covers the large lane 2 digital/analog PHY field block, and ends at the shift definitions for `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`. The range contains 2,180 `#define` lines across 211 register groups: 1,099 `__SHIFT` definitions and 1,092 `_MASK` definitions. The mismatch is expected for this exact line slice because both the start and end are artificial chunk boundaries: the first visible register started in the prior chunk, and the lane 3 masks continue immediately after this chunk.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata and has no Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, allocation paths, locks, or callbacks in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position.

The important register families in this range are:

- `DPCSSYS_CR0_LANE1_ANA_RX_*`: tail-end lane 1 analog receiver fields for squelch response/threshold, DFE tap enable, calibration mux selection, ATB register-reference and measurement paths, VDAC ranges, CDR VREG behavior, and RX VREG control.
- `DPCSSYS_CR0_LANE2_DIG_ASIC_*`: lane 2 digital ASIC override/input/output fields for TX/RX loopback, request, p-state, rate, width, MPLLB selection, data enable, TX main/pre/post cursors, HDMI mode, clock-ready, RX detect, inversion, low-power detect, DC coupling, MPHY mode, reset, boost controls, lane transceiver mode, termination, RX equalization, VCO/DAC controls, signal detect, and status readback.
- `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*` and `DPCSSYS_CR0_LANE2_DIG_RX_PWRCTL_*`: digital power-state and power-up timing fields for TX/RX P0/P0S/P1/P2 states, plus DCC DAC bank/address/data/range/ack control.
- `DPCSSYS_CR0_LANE2_DIG_TX_CLK_ALIGN_*`, `*_LBERT_*`, `*_RX_VCOCAL_*`, `*_RX_CDR_*`, and `*_RX_DPLL_*`: clock alignment, loopback/BER test controls, RX VCO calibration control/status/timing, CDR control/status, and DPLL frequency/bound fields.
- `DPCSSYS_CR0_LANE2_DIG_RX_ADPTCTL_*`: RX adaptation configuration and status for attention/VGA/CTLE/DFE taps, even/odd VDAC offsets, slicer controls, error level, reset, DAC selector, and CR bank address/data.
- `DPCSSYS_CR0_LANE2_DIG_RX_STAT_*`: statistic/match/sample/counter fields for lane-level data-mask, match control, statistic control, sample counts, statistic counters, calibration comparator clock control, and stop control.
- `DPCSSYS_CR0_LANE2_DIG_MPHY_*` and `DPCSSYS_CR0_LANE2_DIG_ANA_*`: low-speed MPHY PWM/termination/stability controls and the bridge between digital controls and analog TX/RX controls/status.
- `DPCSSYS_CR0_LANE2_ANA_TX_*` and `DPCSSYS_CR0_LANE2_ANA_RX_*`: analog lane 2 transmitter and receiver fields for override measurement, power override, alternate bus, ATB measurement, DCC DAC, termination code, mux selection, VREG control, CDR/DES, slicer, power control, squelch, calibration, ATB measurement, VDAC range, and CDR/VREG control.
- `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`: the first lane 3 register in this chunk, with shift definitions for serial/parallelloopback, enable, RX AC JTAG enable, and reserved bits. Its masks are in the following chunk.

Most fields are 16-bit-style PHY/CR fields with masks such as `0x0001L`, `0x00FFL`, or `0xFFFFL`, rather than the 32-bit display-pipe registers seen elsewhere in `dcn_4_1_0_sh_mask.h`.

## Control Flow

This header has no direct control flow. Runtime flow is created by consumers:

1. DCN 4.1.0/DCN401 display code includes this shift/mask header together with the matching offset header.
2. ASIC-specific register tables and helper macros paste register and field names into generated symbols such as `DPCSSYS_CR0_LANE2_DIG_RX_CDR_CDR_CTL_0__CDR_EN__SHIFT` and the corresponding mask.
3. Register helper code uses those constants to isolate fields during MMIO or indexed DPCSSYS register access.
4. Link encoder, PHY setup, clock/power management, diagnostics, and low-level bring-up flows decide when to program p-states, rates, equalization, adaptation, CDR/DPLL/VCO calibration, loopback, test, and analog measurement fields.

The macros do not encode sequencing rules. For example, they do not say whether VCO calibration must complete before enabling a receiver, whether a status bit is sticky, whether an ack is write-one-to-clear, or which fields are read-only. Those semantics come from the hardware specification and the AMD display code using these definitions.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware-backed lane state:

- TX/RX override state for lane 2, including explicit override-enable bits that can disconnect normal hardware/firmware control from PHY behavior.
- Power and timing state for TX/RX p-states and power-up delays.
- Clock-recovery and data-path state for CDR, DPLL, VCO calibration, deserializer, word clock, and loopback controls.
- Equalization/adaptation state for VGA, CTLE, DFE tap controls, slicer levels, VDAC offsets, and RX calibration selectors.
- Diagnostic and production-test state for LBERT, PRBS-like loopback support, statistic counters, ATB measurement muxes, analog override outputs, and MPHY low-speed controls.
- Analog TX/RX state for termination codes, DCC DAC selection, boost/current controls, power gates, squelch thresholds, and VREG settings.

Persistence is device-local and power/reset sensitive. Configuration fields may retain values until a modeset, link retrain, lane reset, power-gate transition, suspend/resume, or ASIC reset. Status and statistic fields can change asynchronously as the PHY trains, calibrates, enters or exits low-power states, receives symbols, runs loopback/test modes, or exposes analog measurement signals.

## Dependencies And Integration Points

The direct dependency is the generated DCN 4.1.0 register database. These field constants must match the companion `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`; shifts and masks alone do not identify MMIO addresses or indexed-register locations.

Known include sites for `dcn_4_1_0_sh_mask.h` in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`

Functional integration is likely through DCN401 register-table construction, link encoder/PHY programming, DMUB-assisted display bring-up, GPIO/HPD translation, clock manager sequencing, and diagnostic/test paths. DPCSSYS lane fields are especially tied to DisplayPort/USB-C/PHY lane behavior: link training, lane-rate selection, p-state transition, receiver adaptation, analog trim, loopback, and test access.

The repeated lane prefix is an integration contract. Lane 2 fields should mirror the same logical lane block in adjacent lane 0/1/3 sections except where the hardware intentionally differs. Token-pasting table macros depend on that naming regularity.

## Risks And Edge Cases

- Shift/mask drift is high risk. These macros are untyped compile-time constants, so a wrong bit position can compile while silently programming a neighboring PHY field.
- Offset/header mismatch can apply a valid field mask to the wrong register address or indexed CR register.
- Override fields are hazardous. `*_OVRD_EN` and `*_OVRD_*` bits can force lane power, reset, rate, width, cursor, termination, equalization, CDR, VCO, DPLL, loopback, or analog controls away from normal hardware sequencing.
- Lane-instance mistakes can be connector-specific. A copy or table-index error involving `LANE2` versus adjacent lanes may only reproduce on configurations using that physical lane.
- Boundary incompleteness matters. The first visible lane 1 register and the final lane 3 register are partial in this chunk, so whole-register validation needs neighboring chunk data.
- Status, counter, ack, and calibration fields can be side-effect-sensitive. Incorrect masks can lose statistics, misread calibration completion, poll the wrong CDR/VCO/DPLL status, or acknowledge the wrong hardware event.
- Analog measurement and ATB mux fields may affect debug or manufacturing access rather than normal display flow; accidentally enabling them can perturb the receiver/transmitter or expose misleading measurements.
- Signedness and width assumptions remain a concern even though most masks are 16-bit. Constants use an `L` suffix, and consumers should preserve the expected unsigned field extraction/update behavior.

## Test Signals

Useful validation for this chunk is a mix of generated-header consistency and hardware behavior:

- Build AMDGPU/DC with DCN401 support enabled so all consumers of `dcn_4_1_0_sh_mask.h` compile and register-table macro expansion catches missing or renamed field macros.
- Mechanically verify shift/mask pairing across this chunk plus its neighbors. For lines 69372-71761 alone, there are 1,099 shifts and 1,092 masks because the range starts and ends mid-register; reconciliation should include adjacent chunks before flagging a mismatch.
- Compare lane 2 field names and values against the corresponding lane 0/1/3 generated register blocks where the hardware block is expected to be repeated.
- Exercise physical links that use lane 2: link training across rates and lane counts, p-state transitions, suspend/resume, hotplug, USB-C/DP-alt-mode lane mapping where applicable, and low-power entry/exit.
- Run display PHY diagnostics: loopback/LBERT modes, statistic counters, PRBS or equivalent pattern tests, CDR/DPLL/VCO calibration status, RX adaptation status, and output/input analog status readback.
- Validate analog-sensitive paths with multiple sinks and cables: DP link stability, error counters, FEC/retraining behavior if enabled elsewhere, blanking during retrain, audio/video continuity, and resume after power gating.
- Watch kernel logs and display diagnostics for training timeouts, stuck calibration/power-status bits, unexpected lane disable, repeated retraining, signal-detect failures, or lane-specific failures that point to an incorrect generated field.

## Cross-Chunk Notes

The previous chunk owns the beginning of the lane 1 analog RX register group that this range starts inside. The next chunk owns the masks for `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` and continues the lane 3 block. The final per-file report should merge adjacent chunk reports before making complete claims about all DPCSSYS lane definitions in `dcn_4_1_0_sh_mask.h`.
