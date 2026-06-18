# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 17089-19501

## Scope

This chunk is a mid-file slice of the generated AMD DPCS 3.1.4 register shift/mask header. It contains compile-time preprocessor metadata only: hardware bitfields are exposed as `...__SHIFT` bit offsets and matching `..._MASK` constants. There are no C functions, structs, executable branches, locks, allocations, direct register accesses, or software persistence mechanisms in this range.

The slice contains 2,185 `#define` entries: 1,100 shift macros and 1,085 mask macros across 244 register-comment blocks. The imbalance is a chunk-boundary artifact. The first two lines are masks for the preceding `DPCSSYS_CR1_SUP_DIG_MPLLB_DIV_CLK_OVRD_IN` register, and the range ends after the first shift for `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P2`, before the rest of that register's fields.

Although the repository path is under `ceph-client`, this file is AMDGPU display PHY metadata. The covered namespace is `DPCSSYS_CR1`, the DPCS control/register instance used by DCN 3.1.4 display code.

## Purpose

The purpose of this chunk is to publish exact bit positions and masks for DCN 3.1.4 DPCS CR1 supervisor, PLL, analog, and lane-control registers. Runtime AMD display code combines these constants with companion indirect-register offsets from `dpcs_3_1_4_offset.h` and register-helper macros to isolate fields while programming the DisplayPort/HDMI PHY-side hardware.

Major covered areas:

- CR1 supervisor digital PLL and clock controls for MPLLA/MPLLB, including HDMI/divider clocks, PLL enable/divider/VCO/standby/calibration controls, fractional-N quotient/remainder/denominator fields, spread-spectrum peak/stepsize fields, charge-pump controls, and clock-sync override bits.
- Supervisor override, ASIC-input, analog-input, power-control, clock/reset, RTUNE, bandgap, PMIX, and status fields that describe or force PHY supervisor state.
- Lane 0 ASIC-facing lane/TX/RX override and mirror fields, TX power-state programming, TX power-up timing, TX DCC DAC access, TX clock alignment, TX LBERT, RX statistic counters and pattern-match controls, and TX analog override/status fields.
- Lane 1 ASIC-facing lane/TX/RX override and mirror fields, TX power-state/timing/DCC/LBERT controls, and the beginning of RX power-state programming.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset inside the register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by masked register read/update/write helpers.
- Register comments such as `//DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0` identify the register block whose field macros follow.
- Instance and lane prefixes are part of the ABI. `DPCSSYS_CR1_SUP_*` refers to the CR1 supervisor block, while `DPCSSYS_CR1_LANE0_*` and `DPCSSYS_CR1_LANE1_*` refer to lane-specific PHY registers.

Important register families in this chunk include:

- `DPCSSYS_CR1_SUP_DIG_MPLLA_*` and `DPCSSYS_CR1_SUP_DIG_MPLLB_*`: PLL override inputs, PLL multipliers, TX clock dividers, VCO frequency, standby/calibration controls, fractional-N programming, SSC enable/up-spread/peak/stepsize, PMIX/word-divide controls, charge-pump proportional/integral settings, gear-shift charge-pump overrides, HDMI clock divider fields, and PLL power-control status/timers/calibration/analog-DAC outputs.
- `DPCSSYS_CR1_SUP_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, and `LVL_OVRD_IN`: supervisor-level overrides for prescaler, RTUNE, TX calibration codes, PHY reset, reference clock, HDMI mode, bandgap, PLL enable/calibration, TX/RX power states, and level-based digital behavior.
- `DPCSSYS_CR1_SUP_DIG_*_ASIC_IN`: hardware input mirrors for MPLL A/B, divider clocks, HDMI clocks, general supervisor state, level controls, bandgap, and charge-pump settings. These pair with the override input/output blocks to distinguish programmed override values from ASIC-provided live values.
- `DPCSSYS_CR1_SUP_ANA_*`: analog supervisor controls for prescaler, RTUNE, bandgap configuration, and switch-power measurement.
- `DPCSSYS_CR1_SUP_DIG_CLK_RST_*` and `RTUNE_*`: bandgap/reference-clock power-up timers, VPH under-drive timing, RTUNE configuration/status, RX/TX down/up set values and observed status, counter configuration, and TX calibration code reporting.
- `DPCSSYS_CR1_SUP_DIG_ANA_*_OVRD_OUT`, `ANA_STAT`, and PMIX override outputs: observable analog override outputs and status mirrors for MPLL, RTUNE, bandgap, and PMIX state.
- `DPCSSYS_CR1_LANE0_DIG_ASIC_*` and `DPCSSYS_CR1_LANE1_DIG_ASIC_*`: per-lane request, reset, pstate, rate, width, enable, clock-ready, TX swing/pre/post cursor, de-emphasis, HDMI mode, RX detect, RX/TX inversion, RX equalizer/CDR/VCO/low-power control, and override output fields.
- `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_*` and `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_*`: TX P0/P0S/P1/P2 state bitmaps for analog reference generation, VCM hold, clocks, reset, serial/data enable, RX-detect allowance, vboost allowance, and DCC compensation calibration; plus power-up timer fields and DCC calibration/DAC address/data/range/acknowledge controls.
- `DPCSSYS_CR1_LANE0_DIG_RX_STAT_*`: RX statistic load values, data masks, match controls, statistic control, sample counts, seven statistic counters, calibration comparator clock control, extended match controls, and statistic stop controls.
- `DPCSSYS_CR1_LANE0_DIG_ANA_*` and `DPCSSYS_CR1_LANE0_ANA_TX_*`: TX analog override outputs and raw analog TX controls for term codes, equalization, DCC DACs, power override, alternate/ATB buses, clocks, misc controls, and reserved analog fields.
- `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1`: RX AFE, clock regulator, clock, deserializer, CDR, VCO reset/calibration, continuous calibration, and digital-clock enable fields. `RX_PSTATE_P2` begins at the final line and is completed in the next chunk.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. DCN 3.1.4 resource/display code includes `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`.
2. Register descriptors or helper macros pair an indirect DPCS register offset such as `ixDPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0` or `ixDPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0` with this file's shift/mask constants.
3. AMD display register helpers perform masked reads, writes, updates, and polling against the DPCS CR1 indirect register interface.
4. Hardware state changes occur in the PHY, PLL, supervisor, TX, RX, analog, and diagnostic registers. This file only supplies the bitfield metadata needed to avoid hard-coded bit arithmetic.

The represented hardware flow is typically: configure or observe supervisor reference/PLL state, program MPLL A/B clocks and spread-spectrum behavior, handle RTUNE and calibration state, program per-lane TX/RX override inputs or observe ASIC-provided inputs, sequence lane TX/RX power states and timers, access DCC calibration controls, and read diagnostics such as RX counters, LBERT controls, and analog status mirrors.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros resides in DPCS hardware registers.

Hardware state represented by this chunk includes:

- PLL and clock state: MPLLA/MPLLB enable, divider, multiplier, VCO frequency, standby, calibration, fractional-N fields, SSC fields, HDMI clock division, charge-pump tuning, PLL power-control timers/status, and PMIX controls.
- Supervisor state: PHY reset, reference-clock and bandgap control, prescaler/RTUNE overrides, TX calibration code, level controls, and ASIC input/output mirrors.
- Lane state: lane reset, pstate/rate/width requests, TX/RX enable and clock-ready state, TX swing/equalization/pre/post-cursor settings, HDMI mode, RX detection, RX equalizer/CDR/VCO controls, and lane OCLA hook for lane 1.
- TX/RX power sequencing state: TX P0/P0S/P1/P2 power bitmaps, TX power-up timers, RX P0/P0S/P1 power bitmaps, and the start of RX P2.
- Diagnostics and calibration state: DCC CR bank and DAC access, LBERT mode/error injection fields, RX pattern-match/statistic counters, analog override outputs, analog TX DCC/term/equalization fields, RTUNE status, and PLL analog DAC output fields.

Persistence is limited to the lifetime of hardware register programming. Values may be lost or require reprogramming after GPU reset, display engine reset, PHY reset, power gating, suspend/resume, hotplug retraining, mode set, link-rate changes, or lane-count changes. Higher-level AMD display state and BIOS/firmware policy remain the source of truth for reprogramming these registers.

## Dependencies

This chunk depends on the matching generated DPCS 3.1.4 offset header. Shift and mask constants alone do not identify the indirect register address; for example, the offset header maps the CR1 supervisor block at offsets such as `0x0007` for `ixDPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0` and lane 1 TX/RX blocks at offsets such as `0x1120` for `ixDPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0` and `0x1140` for `ixDPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`.

It also depends on:

- AMD display register-helper infrastructure, especially masked read/write/update and polling helpers that consume generated `__SHIFT` and `_MASK` symbols.
- DCN 3.1.4 resource code, which includes the generated DPCS offset and shift/mask headers alongside the DCN 3.1.4 display register headers.
- The silicon register database or generator that produced the DPCS 3.1.4 headers.
- Display link, PHY, clock, PLL, HPD/link-training, HDMI/DP, power-management, and diagnostic code that programs these fields during mode set, retraining, suspend/resume, reset recovery, and validation.

Because this is generated silicon metadata, manual edits are risky unless synchronized with the register database, companion offset header, and any generated register tables that reference these names.

## Integration Points

The primary integration point is the macro-name ABI between generated headers and AMD display code. A consumer naming `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_DCC_DAC_SEL__REQ_MASK` or `DPCSSYS_CR1_SUP_DIG_MPLLB_OVRD_IN_0__MPLLB_EN_MASK` relies on this header for the exact bit position and mask.

Integration surfaces include:

- DCN 3.1.4 resource initialization: `dcn314_resource.c` includes `dpcs/dpcs_3_1_4_offset.h` and `dpcs/dpcs_3_1_4_sh_mask.h` so generated register definitions are available to display-resource construction and lower-level hardware blocks.
- DPCS indirect register access: CR1 `ixDPCSSYS_*` offsets from the companion header select the register, while this header selects or updates the field within that register.
- PHY clock and PLL programming: MPLLA/MPLLB override, divider, HDMI clock, SSC, charge-pump, fractional-N, power-control timer/status, and calibration fields feed display clock and link PHY setup.
- Lane power and link bring-up: lane ASIC override/input fields and TX/RX pstate/timing fields are used when enabling lanes, changing link rates, powering down idle lanes, handling RX detect, and coordinating TX/RX analog/digital clocks.
- Calibration and analog tuning: RTUNE, TX calibration code, DCC DAC, analog override outputs, term code, equalization, vboost, and DCC compensation fields integrate with PHY calibration and board/silicon tuning paths.
- Diagnostics and debug: RX statistic counters, match controls, LBERT fields, analog status, MPLL status, OCLA, and switch-power measurement provide validation and debug signals.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent hardware fields in the same 16-bit register, leading to bad PLL programming, failed link training, unstable clocks, blank displays, or audio/video link instability.
- Instance-prefix mistakes can compile cleanly while programming CR0/CR1 or lane 0/lane 1 incorrectly. The lane offset pattern differs by `0x100` blocks, so a wrong macro family can target a different physical lane.
- PLL, SSC, and fractional-N fields are timing-sensitive. Bad masks can produce incorrect link clocks, excessive spread, failed lock, or intermittent display failures that only appear at certain link rates or HDMI/DP modes.
- Power-state and timer fields control sequencing of analog reference generation, VCM hold, clocks, reset, serial/data enable, RX detect, VCO reset/calibration, CDR, deserializer, and digital clocks. Misprogramming can cause hangs, missed detects, or incomplete power transitions.
- Status and clear/update fields must be handled with exact masks. RTUNE, DCC DAC request/acknowledge, statistic stop/counter fields, LBERT trigger, and analog status fields can otherwise lose events or report stale state.
- Reserved bits are explicitly represented. Writes that fail to preserve reserved fields may violate silicon programming requirements.
- This chunk starts and ends mid-register context. The merge lane must combine adjacent chunks before making whole-file claims about the complete `MPLLB_DIV_CLK_OVRD_IN` and `LANE1 RX_PSTATE_P2` definitions.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 3.1.4 AMD display code builds without missing `DPCSSYS_CR1_SUP_*`, `DPCSSYS_CR1_LANE0_*`, or `DPCSSYS_CR1_LANE1_*` shift/mask symbols.
- Generated-header consistency: every field in this slice pairs with the matching `ixDPCSSYS_CR1_*` offset in `dpcs_3_1_4_offset.h`, and regenerated output has stable shift/mask values.
- Mode-set smoke tests: DP and HDMI displays light up across common resolutions, refresh rates, color depths, link rates, and lane counts.
- Link training and retraining: hotplug, unplug/replug, GPU reset recovery, suspend/resume, link-rate changes, lane-count changes, and RX-detect paths succeed without PHY lock or clock instability.
- PLL and clock validation: MPLL lock/status, HDMI/divider clock behavior, SSC enable/disable, fractional-N programming, and PLL power-control timer/status fields read back as expected.
- Lane power sequencing: TX/RX P0/P0S/P1/P2 programming, power-up timers, RX VCO/CDR/deserializer enables, and low-power transitions behave across active and idle lanes.
- Calibration and debug: RTUNE status, TX calibration code, DCC DAC request/acknowledge, analog override/status fields, RX statistic counters, and LBERT controls produce expected values during hardware diagnostics.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_3_1_4_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
