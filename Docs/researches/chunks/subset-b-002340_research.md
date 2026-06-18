# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 7220-9580

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for CR0 lane register fields. It contains only C preprocessor constants: `__SHIFT` macros identify bit positions and `_MASK` macros identify the corresponding field masks. The range starts inside `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0`, covers the rest of CR0 lane 0 RX statistic and TX analog definitions, then covers a broad CR0 lane 1 region from ASIC-facing override/status fields through TX/RX power, calibration, adaptation, statistics, MPHY, digital analog overrides, and analog TX registers. It ends after the `__SHIFT` definitions for `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`.

## Purpose

The header provides register-field metadata used by AMDGPU display/PHY code when programming DPCS 4.2.2 hardware. Driver code can combine these masks and shifts with matching address macros from `dpcs_4_2_2_offset.h` to perform read-modify-write operations against indexed CR registers without embedding numeric bit layouts in the caller.

In this range, the fields describe:

- CR0 lane 0 RX statistic pattern matching, sample counters, statistic counters, statistic clocks, valid-loss control, and stop control.
- CR0 lane 0 TX digital-to-analog override outputs, termination-code override/clock controls, TX equalization taps, DCC DAC controls, fast-start/loopback controls, and raw analog TX measurement/power/ATB/termination/miscellaneous registers.
- CR0 lane 1 ASIC override and ASIC status interfaces for lane, TX, RX, RX equalization, RX CDR/VCO, cross-lane clock/shift handshakes, and OCLA clock/data enables.
- CR0 lane 1 TX power-state controls, power-up timing, DCC CR-bank/DAC access, TX clock alignment, and TX LBERT control.
- CR0 lane 1 RX power-state controls, RX power-up timing, VCO calibration controls/status, RX alignment/LBERT, CDR/DPLL controls, RX adaptation configuration/status, RX statistic counters, MPHY controls, RX/TX analog overrides, and analog TX registers.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or callable APIs in this chunk. The public interface is the generated macro naming convention:

- `DPCSSYS_CR0_LANE*_...__FIELD__SHIFT`: bit offset for `FIELD`.
- `DPCSSYS_CR0_LANE*_...__FIELD_MASK`: mask for the same field after shifting.
- Register delimiter comments such as `//DPCSSYS_CR0_LANE1_DIG_RX_CDR_CDR_CTL_0` identify field groups that correspond to `ix...` address macros in the companion offset header.

Notable lane 0 groups include:

- `DIG_RX_STAT_*`: pattern CR1A/CR1B match fields, data masks, sample/count enable bits, clock/control selectors, done bits, calibration comparator clock controls, extended pattern-mask registers, and statistic stop.
- `DIG_ANA_TX_*`: digital override outputs for TX clocks, refgen, VCM hold, reset, serial/data enable, data rate, div4/RX detect, termination code, driver source, DCC calibration, fast start, loopback, AC JTAG, and TX equalization coefficients such as pre/post cursor and main cursor fields.
- `DIG_ANA_STATUS_0` and raw `ANA_TX_*`: status/measurement paths and analog TX controls for power override, alternate bus/ATB measurement selection, DCC DAC/control, termination code, override clocking, and miscellaneous/reserved analog registers.

Notable lane 1 groups include:

- `DIG_ASIC_*`: ASIC-facing lane/TX/RX override inputs, output status, TX/RX ASIC inputs, RX equalization inputs, RX CDR/VCO input fields, extra cross-lane override registers, and OCLA data/clock enables.
- `DIG_TX_PWRCTL_*`: per-power-state TX enables for refgen, VCM hold, analog/digital clocks, reset, serial, data, RX detect, VBOOST allowance, and DCC calibration, plus power-up timing and DCC DAC register access.
- `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, and `DIG_RX_DPLL_*`: RX analog/clock/AFE/adaptation/CDR power controls, VCO calibration, CDR status/configuration, and DPLL frequency/bounds.
- `DIG_RX_ADPTCTL_*`: RX adaptation configuration, ATT/VGA/CTLE/DFE tap status, slicer/DAC offsets, adaptation reset, DAC control selection, and CR-bank access.
- `DIG_RX_STAT_*` and `DIG_MPHY_*`: statistic pattern/counter controls plus MPHY PWM/termination and clock-stability fields.
- `DIG_ANA_RX_*`, `DIG_ANA_TX_*`, and raw `ANA_TX_*`: digital analog override/status fields for RX/TX power, VCO, calibration, DAC selection, AFE, scope, slicer, phase/IQ controls, signal-change enables, squelch/signal detect, TX DCC/equalization, analog measurement, power override, ATB selection, and TX DCC DAC.

## Control Flow

This header contributes no runtime control flow. Runtime sequencing is implemented by AMD display/PHY code that uses these constants to assemble register values, typically by clearing bits with a `_MASK`, shifting a field value by the matching `__SHIFT`, and writing the result to the DPCS register address from the offset header.

The implied hardware control paths are display PHY bring-up and diagnostics: TX/RX power transitions, TX startup timing, RX VCO/CDR/DPLL setup, RX adaptation, lane alignment, LBERT testing, RX statistic sampling, MPHY low-speed behavior, and analog override programming.

## State And Persistence

The macros are stateless compile-time constants. The state they describe lives in DPCS hardware registers and is volatile hardware state, not persisted by this header. Values can be changed by display link training, PHY reinitialization, hotplug handling, suspend/resume, GPU/display reset, power gating, or diagnostic/debug code. Reserved masks are present so consumers can preserve or avoid undocumented bits during read-modify-write sequences.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline staying synchronized with DPCS 4.2.2 hardware specifications. It is normally consumed with:

- `dpcs_4_2_2_offset.h`, including lane 0 addresses such as `ixDPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0` at `0x1082` and lane 1 addresses beginning at `ixDPCSSYS_CR0_LANE1_DIG_ASIC_LANE_OVRD_IN` around `0x1100`.
- AMDGPU display/DC register access helpers that combine address, mask, and shift constants for indexed DPCS CR MMIO access.
- Link-training, PHY power-management, receiver adaptation, and debug/validation code in the AMD GPU driver.

The file is part of an imported Linux GPU driver tree under this repository and has no dependency on Ceph filesystem logic.

## Integration Points

These definitions integrate with AMD display link bring-up, DisplayPort/HDMI PHY tuning, high-speed lane power sequencing, receiver calibration, and diagnostic paths. Lane 0 content in this slice is mostly RX statistic and TX analog-side control, while lane 1 content spans the whole lane control surface from ASIC handshakes to analog TX/RX programming. The companion offset header supplies the physical register addresses; the macros here supply the bit layout for those addresses.

The repetitive lane-specific naming is an important integration contract. A consumer must pair `DPCSSYS_CR0_LANE1_*` masks with the lane 1 `ixDPCSSYS_CR0_LANE1_*` register address, not with lane 0 or another CR instance. ASIC-version specificity also matters: these are `dpcs_4_2_2` layouts and should not be mixed casually with nearby `dpcs_4_2_0` or `dpcs_4_2_3` headers unless the caller explicitly gates by the matching ASIC register block.

## Risks

- The range starts in the middle of `DPCSSYS_CR0_LANE0_DIG_RX_STAT_MATCH_CTL0`; the preceding chunk is needed for the full field list of that register.
- The range ends before the `_MASK` definitions for `DPCSSYS_CR0_LANE1_ANA_TX_DCC_DAC`; the following chunk is needed to complete that register summary.
- Generated mask/shift mistakes would compile cleanly but could silently program the wrong hardware bits.
- Writing reserved bits, failing to preserve reserved bits, or mixing lane/ASIC-version macros can destabilize the analog PHY or misprogram a different physical lane.
- TX/RX power-state, reset, DCC, VCO/CDR/DPLL, adaptation, and analog override fields are sequencing-sensitive. Incorrect use can cause link training failures, display blanking, intermittent high-rate instability, or misleading diagnostic counter results.
- Many fields have override-enable companions; setting an override value without the corresponding enable, or leaving an enable asserted after diagnostics, can make later normal link management behave unexpectedly.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_2_sh_mask.h`.
- Static checks that each field has matching `__SHIFT` and `_MASK` constants, that masks match their shifts and widths, and that DPCS CR masks fit the expected 16-bit register shape unless a register is known wider.
- Display bring-up on hardware using DPCS 4.2.2, including boot display, modesets, hotplug, suspend/resume, GPU reset recovery, and multi-monitor operation.
- Link-training stress across lane counts and rates, especially CR0 lane 0 statistic paths and CR0 lane 1 TX/RX power/adaptation paths.
- PHY diagnostics that exercise TX/RX LBERT, RX statistic counters, pattern-match controls, VCO/CDR/DPLL status, DCC DAC selection/acknowledgement, MPHY controls, and analog override/status readback.
