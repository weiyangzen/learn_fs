# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 88684-91077

## Scope

This chunk is part of the generated DCN 4.1.0 ASIC register shift/mask header used by the AMD display driver. It contains preprocessor constants only: each hardware field is represented by a `...__SHIFT` bit offset and a matching `..._MASK` value. There are no C functions, structs, branches, allocations, or direct MMIO operations in this range.

The range covers the end of the `DPCSSYS_CR1_LANE1` receiver adaptation/statistic block, lane 1 digital-to-analog and analog PHY control/status fields, and the start of the `DPCSSYS_CR1_LANE2` lane register set through early RX statistic controls. It is lane-aligned metadata for the DisplayPort/USB-C PHY-side DPCS lane hardware under CR1.

## Purpose

The purpose of this chunk is to publish exact bit positions and masks for lane-level PHY control, override, calibration, power, loopback, link-test, CDR/DPLL, adaptation, and statistic registers. Runtime driver code includes this header together with matching offset headers, then uses register-helper macros to read or update named fields without hard-coding bit arithmetic.

Important covered areas:

- `DPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_*` tail: DFE VDAC offsets, slicer controls, adaptation reset, DAC source selection, and CR bank address/data access.
- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*`: statistic load values, data/pattern masks, match controls, counter enables, sample counters, calibration compare clock controls, and statistic stop controls.
- `DPCSSYS_CR1_LANE1_DIG_MPHY_RX_*`: M-PHY receive PWM polarity, low-speed termination count, and analog PWM clock-stable timing.
- `DPCSSYS_CR1_LANE1_DIG_ANA_*` and `DPCSSYS_CR1_LANE1_ANA_*`: digital override outputs and analog lane registers for TX/RX power, clocks, equalization, termination, DCC DACs, CDR/VCO, calibration muxes, slicers, AFE/DFE, ATB measurement, VDAC ranges, and regulator trims.
- `DPCSSYS_CR1_LANE2_DIG_ASIC_*`: lane, TX, and RX override inputs/outputs plus live ASIC input/output mirrors for request, pstate, rate, width, enable, clock-ready, detect-RX, inversion, HDMI mode, main/pre/post cursor, equalizer, VCO, CDR, and low-power controls.
- `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_*` and `DPCSSYS_CR1_LANE2_DIG_RX_PWRCTL_*`: TX/RX pstate programming and power-up/down timing for analog clocks, data, serial/deserial, DCC, VCO, AFE, CDR, and digital clocks.
- `DPCSSYS_CR1_LANE2_DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, and `DIG_RX_STAT_*`: VCO calibration control/status, clock/data recovery tuning, DPLL frequency bounds, adaptation control/status, and the beginning of RX statistic controls.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the starting bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 16-bit lane-side register represented in this block.
- Instance and lane prefixes are part of the ABI. For example, lane 1 analog receive power fields use `DPCSSYS_CR1_LANE1_ANA_RX_PWR_CTRL*`, while lane 2 digital ASIC override fields use `DPCSSYS_CR1_LANE2_DIG_ASIC_*`.

Notable register families:

- Receiver adaptation: `DIG_RX_ADPTCTL_ADPT_CFG_0` through `ADPT_CFG_9`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP*_STATUS`, `DFE_*_VDAC_OFST`, `RX_SLICER_CTRL_*`, `ERROR_SLICER_LEVEL`, and DAC selector registers. These describe attenuation/VGA/CTLE/DFE adaptation setup and completion state.
- Receiver statistics: `DIG_RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL*`, `STAT_CTL*`, `SMPL_CNT*`, and `STAT_CNT_*`. These fields configure pattern matching, counter sources, correlation/statistic modes, sample windows, valid-loss clearing, and statistic counter enables.
- Digital analog overrides: `DIG_ANA_TX_OVRD_OUT`, `DIG_ANA_TX_EQ_OVRD_OUT_*`, `DIG_ANA_RX_CTL_OVRD_OUT`, `DIG_ANA_RX_PWR_OVRD_OUT`, `DIG_ANA_RX_VCO_OVRD_OUT_*`, `DIG_ANA_RX_CAL`, `DIG_ANA_RX_DAC_CTRL*`, and `DIG_ANA_STATUS_*`. These are override/control/status surfaces between digital logic and lane analog circuits.
- Analog TX/RX trim and measurement: `ANA_TX_*` and `ANA_RX_*` registers cover termination, DCC, power, alternate bus/ATB routing, CDR/deserializer, slicer, AFE/DFE, squelch, calibration, VDAC range, and regulator controls.
- Lane 2 ASIC interface: `DIG_ASIC_TX_OVRD_IN_*`, `DIG_ASIC_RX_OVRD_IN_*`, `DIG_ASIC_*_ASIC_IN_*`, and `DIG_ASIC_*_ASIC_OUT_*` provide forced override values and observed hardware-side values for TX/RX lane request, pstate, rate, width, data enable, equalization, clocking, and acknowledge/status paths.
- Power and timing controls: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_*`, `DCC_*`, `DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2`, and `RX_PWRUP_TIME_*` map lane power sequencing and DCC DAC programming.
- Calibration and test: `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_TX_LBERT_CTL`, `DIG_RX_LBERT_CTL`, `DIG_RX_LBERT_ERR`, `DIG_TX_CLK_ALIGN_TX_CTL_0`, and `DIG_ASIC_OCLA` expose VCO/CDR/DPLL tuning, loopback bit-error tests, clock alignment, and observation/debug controls.

## Control Flow and Runtime Integration

There is no executable control flow in this header. Runtime behavior is indirect:

1. ASIC-specific DCN/DPCS resource files include the generated offset and shift/mask headers.
2. Register tables are built with macro expansion patterns such as `SR`, `SRI`, `SF`, `FN`, or `FD`, pairing addresses from offset headers with shifts and masks from this file.
3. Display core and link/PHY code calls helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and `REG_WAIT`.
4. The helpers combine the register address with these shift/mask values to modify only the requested hardware field.
5. State transitions occur in the DPCS/DPCSSYS hardware registers. This file only supplies compile-time metadata for those transitions.

The register flow represented by the fields is generally: select a lane instance, program pstate/rate/width and power timing, optionally force or clear override-enable bits, start calibration or adaptation, then poll status/done/error/statistic fields such as `RX_VCO_CAL_DONE`, `ASM1_DONE`, `ACK`, `SYNC`, or `STAT_CNT_*`.

## State and Persistence Behavior

The header itself has no mutable or persistent state. All state described here is hardware state in lane-local PHY registers.

The represented state includes:

- Override state: paired value and `*_OVRD_EN` fields force lane controls such as request, pstate, data enable, rate, width, CDR tracking, HDMI mode, cursor/equalization, reset, inversion, and loopback.
- Power state: `PSTATE_P0`, `P0S`, `P1`, and `P2` fields define per-state enable/reset behavior for analog clocks, serial/deserial blocks, VCO/DCC, AFE, CDR, and digital clocks.
- Calibration state: VCO, CDR, DPLL, DCC DAC, RX adaptation, and ATB fields hold setup values, in-progress controls, counters, done bits, final measurements, and error/overflow status.
- Statistic state: pattern masks, sample windows, correlation/statistic source selectors, counter enables, sample-done flags, and statistic counters are latched in hardware and reset or reprogrammed by lane/debug/test flows.

Persistence is limited to the hardware register lifetime. Values can be lost or reset by GPU reset, display engine reset, lane reset, power-gating, suspend/resume, link retraining, mode set, or PHY reinitialization. Higher-level driver state must be the source of truth for reprogramming these fields.

## Dependencies

This chunk depends on matching generated address definitions in the DCN 4.1.0 offset headers. Shift/mask macros alone do not identify an MMIO or indirect-register address. It also depends on AMD display register-helper infrastructure that expands logical register and field names into register reads, writes, updates, and waits.

Semantic dependencies include:

- DCN 4.1.0 DPCS/DPCSSYS hardware register specifications.
- AMD display link encoder and PHY programming code for lane power, link training, USB-C/DP/HDMI PHY setup, and diagnostics.
- Any generated register-table code that maps `DPCSSYS_CR1_LANE1` and `DPCSSYS_CR1_LANE2` instances to the correct lane offsets.
- Debug and validation tools that read CDR/VCO/DPLL, LBERT, statistic counter, ATB, and calibration status fields.

Because these definitions are generated silicon metadata, manual edits are high risk unless they are synchronized with the register database and the paired offset header.

## Integration Points

The key integration point is the macro-name ABI between generated headers and display hardware code. A consumer naming `DPCSSYS_CR1_LANE2_DIG_RX_ADPTCTL_CTLE_STATUS__ASM1_DONE` relies on the corresponding `__SHIFT` and `_MASK` values here to isolate the correct bit in the lane register.

Instance and lane alignment are also critical. The line range crosses from lane 1 definitions into lane 2 definitions, and many fields are structurally repeated across lanes. Register-table generation must keep prefixes, offsets, shifts, and masks aligned so code operating on lane 2 does not accidentally use lane 1 fields or vice versa.

Protocol and hardware integration surfaces include:

- DP/HDMI PHY setup: TX/RX rate, width, cursor/equalization, HDMI-mode enable, clocking, inversion, and detect-RX controls.
- Link training and recovery: RX CDR/DPLL/VCO calibration, CDR tracking/SSC controls, adaptation status, DFE/CTLE/VGA/ATT results, and slicer/error VDAC offsets.
- Power management: pstate-specific enable/reset fields and timing fields for fast/normal lane bring-up and shut-down.
- Diagnostics: LBERT, loopback, OCLA, ATB measurement, statistic counters, pattern matching, and calibration status fields.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent analog/PHY fields in the same 16-bit lane register, causing link-training failure, blank display, unstable CDR lock, bad equalization, or broken low-power transitions.
- Lane-prefix mistakes are easy to miss because lane 1 and lane 2 field sets are similar. A wrong prefix can make a bug appear only on a subset of physical lanes, connectors, or link widths.
- Override-enable fields are dangerous when stale. Leaving `*_OVRD_EN` asserted can pin hardware state and defeat normal link-training, power-management, or calibration sequences.
- Status and self-clearing fields require correct write semantics. Misusing masks for `ACK`, reset, load-clock, update, or done bits can wedge calibration or hide failures.
- Analog trim fields such as termination, VDAC range, DCC DAC, regulator, ATB, and CDR/VCO controls are silicon-sensitive. Bad metadata can create intermittent failures tied to board, temperature, cable, sink, or link-rate conditions.
- Many constants use high-bit masks such as `0x8000L`. Consumers should keep unsigned-safe register math and avoid assumptions that narrow signed types are harmless.
- The chunk begins and ends inside larger repeated hardware blocks, so full per-file conclusions require neighboring chunks for the complete CR1 lane map.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 4.1.0 display and link/PHY code builds with no missing `__SHIFT` or `_MASK` macro names.
- Register-table sanity: generated lane 1/lane 2 DPCS register tables match the paired offset header and preserve the expected lane prefix ordering.
- Display link smoke tests: DP and HDMI bring-up across supported rates, lane counts, bit depths, and connector routes, with mode set, hotplug, suspend/resume, and GPU reset coverage.
- Link-training diagnostics: CDR lock, DPLL frequency bounds, VCO calibration done/correct/up status, CTLE/VGA/DFE adaptation done bits, and slicer/VDAC status readbacks.
- Power-management tests: transitions through P0/P0S/P1/P2, fast-start paths, lane power-up timing, DCC DAC request/ack, and low-power entry/exit.
- PHY debug paths: TX/RX loopback, LBERT error count/overflow, OCLA visibility, ATB measurement routing, RX statistic pattern/counter operation, and clock-alignment/FIFO behavior.
- Multi-lane tests: exercise one-lane, two-lane, and four-lane configurations to catch lane-index or replicated-field mismatches.

## Chunk Notes

This chunk starts after the lane 1 `DFE_TAP2_STATUS` definitions and ends inside `DPCSSYS_CR1_LANE2_DIG_RX_STAT_STAT_CTL1`. Neighboring chunks are needed for the complete lane 1 and lane 2 register blocks before a final per-file report is produced.
