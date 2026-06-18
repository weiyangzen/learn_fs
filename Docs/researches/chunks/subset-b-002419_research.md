# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 80269-82680

## Chunk Scope

This chunk is part of the generated AMD DPCS 4.2.3 shift/mask register header. It contains C preprocessor definitions only: register field `__SHIFT` macros and matching `_MASK` macros. There are no functions, structs, storage declarations, or executable control paths in this span.

The slice starts inside `DPCSSYS_CR4_SUP_DIG_MPLLB_ASIC_IN_0`, after the first field shifts for that register have already appeared in the previous chunk. It then covers the rest of the CR4 supervisor (`SUP`) digital and analog PLL/reference/RTUNE register field definitions, the start of CR4 lane 0 ASIC/TX/RX/power-control/analog TX register fields, and the start of CR4 lane 1 ASIC/TX/RX/power-control fields. The last visible register header is `DPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S`; that register's field definitions continue in the next chunk.

## Purpose

The macros describe bit positions and masks for programming Display Core PHY Subsystem CR4 registers on the ASIC generation represented by `dpcs_4_2_3`. The paired `dpcs_4_2_3_offset.h` file supplies the `ix...` register addresses, while this header supplies the per-field packing and extraction constants used by AMD display register helpers and register tables.

The hardware areas represented here are:

- CR4 supervisor MPLL input and clocking fields for MPLLA/MPLLB, including enable, divider, VCO frequency, multiplier, spread-spectrum clocking peak/step size, fractional-N update, HDMI/divided clock output, charge-pump control, and global PHY/reference clock controls.
- Supervisor analog support registers for prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB analog tuning, override, ATB/debug, control, and reserved words.
- Supervisor MPLL power-control fields for override requests, lock/power state, DAC range, timer programming, calibration, analog DAC output, and SSC spread type for both MPLLA and MPLLB.
- Supervisor clock/reset and RTUNE fields for bandgap/reference power-up timing, reference VPHUD selection, debug/config/status, set values, status values, counters, and TX calibration code.
- Supervisor digital-to-analog override/status outputs, including MPLLA/MPLLB override output words, RTUNE override output, analog status, bandgap override output, and PMIX override output.
- Lane 0 ASIC interface, TX power-control, TX DCC, TX clock alignment, LBERT, RX statistics, analog TX override/status, and analog TX control fields.
- Lane 1 ASIC interface and TX power-control groups, followed by the beginning of RX power-control pstate programming.

## Important APIs, Types, and Macros

There are no typed C APIs in this chunk. The public surface is the macro namespace, grouped by hardware block:

- `DPCSSYS_CR4_SUP_DIG_MPLLB_ASIC_IN_*__*__SHIFT` / `_MASK`: MPLLB input programming for enable/standby, TX clock divider, VCO frequency, multiplier, spread-spectrum enable/up-spread/peak/step size, PMIX, word divide, and fractional-N configuration update.
- `DPCSSYS_CR4_SUP_DIG_MPLLA_DIV_CLK_ASIC_IN`, `DPCSSYS_CR4_SUP_DIG_MPLLA_HDMI_CLK_ASIC_IN`, `DPCSSYS_CR4_SUP_DIG_MPLLB_DIV_CLK_ASIC_IN`, and `DPCSSYS_CR4_SUP_DIG_MPLLB_HDMI_CLK_ASIC_IN`: divided-clock and HDMI pixel clock divider controls.
- `DPCSSYS_CR4_SUP_DIG_ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, `MPLLA_CP_ASIC_IN`, `MPLLA_CP_GS_ASIC_IN`, `MPLLB_CP_ASIC_IN`, and `MPLLB_CP_GS_ASIC_IN`: PHY reset/reference clock/test/RTUNE handshakes, RX/TX level selections, bandgap enable, and charge-pump proportional/integral settings.
- `DPCSSYS_CR4_SUP_ANA_*`: analog prescaler, RTUNE, bandgap, MPLLA/MPLLB miscellaneous, override, ATB, counter/control, and reserved register fields. Many of these are small one-bit or few-bit trim/debug controls such as bypass/chop/test selections, ATB measurement selection, ring/VCO controls, and loop-filter/current tuning.
- `DPCSSYS_CR4_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and `DPCSSYS_CR4_SUP_DIG_MPLLB_MPLL_PWR_CTL_*`: MPLL power-state, override, lock, timer, calibration, DAC output, and SSC generator fields for both PLL instances.
- `DPCSSYS_CR4_SUP_DIG_CLK_RST_*` and `DPCSSYS_CR4_SUP_DIG_RTUNE_*`: power-up timing for bandgap/reference paths plus RTUNE request/config/status/set/stat/counter/calibration fields.
- `DPCSSYS_CR4_SUP_DIG_ANA_*`: supervisor digital outputs into analog override/status paths for MPLLA/MPLLB, RTUNE, bandgap, and PMIX.
- `DPCSSYS_CR4_LANE0_DIG_ASIC_*`: lane 0 digital ASIC override/input/output fields for lane mode, TX swing/equalization/DCC/reset/clock/data/receiver-detect controls, RX CDR/VCO/equalizer/adaptation controls, and lane OCLA/debug state.
- `DPCSSYS_CR4_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power-state enables for P0/P0S/P1/P2, TX power-up timers, DCC bank and DAC controls, clock-alignment fields, and LBERT mode/pattern controls.
- `DPCSSYS_CR4_LANE0_DIG_RX_STAT_*`: lane 0 RX statistic match/mask/control/sample/counter fields, including multiple `STAT_CNT_*` words and calibration compare clock control.
- `DPCSSYS_CR4_LANE0_DIG_ANA_TX_*` and `DPCSSYS_CR4_LANE0_ANA_TX_*`: lane 0 analog TX override outputs and analog TX measurement/power/ATB/DCC/termination/equalization/misc/reserved fields.
- `DPCSSYS_CR4_LANE1_DIG_ASIC_*` and `DPCSSYS_CR4_LANE1_DIG_TX_PWRCTL_*`: same lane-facing ASIC and TX power-control pattern for lane 1. This chunk reaches lane 1 RX pstate fields for `RX_PSTATE_P0`; `RX_PSTATE_P0S` starts at the boundary.

Most masks in the lane/supervisor PHY payloads are 16-bit values such as `0xFFFFL`, `0x8000L`, or narrower masks like `0x03FFL`. Some top-level DPCS and display-decoder fields elsewhere in the file are 32-bit masks, but this chunk is dominated by 16-bit CR payload definitions.

## Control Flow

This header has no software control flow. Runtime behavior is implicit in the hardware protocols that the fields represent:

- PLL programming is modeled as register fields for enable, standby, multiplier/divider, fractional-N update, spread-spectrum settings, lock state, DAC range, timer, and calibration. Driver code using these macros must supply the sequencing and wait logic.
- Override registers use common value/enable patterns. Examples include supervisor analog override outputs, lane ASIC TX/RX override inputs and outputs, and analog TX override outputs. Setting an override value without the corresponding enable bit, or leaving an enable asserted after diagnostics, changes hardware behavior even though this header cannot express the lifecycle.
- Request/acknowledge and status handshakes appear in RTUNE and DCC paths. RTUNE fields include request/config/status/set/stat words, while DCC DAC selection uses request, acknowledge, control-update, and range-update bits.
- Power-control fields define desired power-state behavior for TX and RX pstate transitions. TX P0/P0S/P1/P2 fields gate analog refgen, VCM hold, clocks, reset, serializer, data, RX detect allowance, VBOOST allowance, and DCC compensation calibration. RX pstate fields gate AFE, clock regulator, analog clock, deserializer, CDR, VCO resets, continuous calibration, and digital clock.
- RX statistic registers provide a hardware observation path rather than a loop in this header. Match controls, sample count, status controls, stop, and counter words are consumed by driver diagnostics or hardware validation sequences.

## State and Persistence

The state described by these macros is stored in DPCS hardware registers, not in kernel memory. Values persist according to the hardware block lifetime: a register write may remain active until another write, PHY reset, lane power transition, display link reinitialization, or GPU power-management event clears or reprograms the block.

State categories visible in this chunk include:

- Clock and PLL state: MPLLA/MPLLB enable, divider, multiplier, VCO frequency, fractional-N, spread-spectrum, lock, calibration, DAC range/output, and timer values.
- Supervisor analog state: bandgap/reference settings, prescaler and RTUNE trims, analog test bus selections, control words, reserved trim words, PMIX override outputs, and analog status.
- Lane mode and override state: TX/RX rate, width, pstate, link training requests, loopback, reset, clock/data enables, TX swing/equalization, RX CDR/VCO/equalization/adaptation, and lane transceiver mode.
- Power sequencing state: TX and RX pstate enable bits, power-up delay fields, skip/fast flags, and receive-detect/VBOOST behavior.
- Calibration and debug state: DCC DAC/bank programming, DCC status, LBERT pattern controls, OCLA visibility, RX statistic counters, ATB measurement selections, and ATE/test-oriented override paths.

Reserved masks are explicitly generated for many registers. Any runtime writer should preserve reserved bits unless the ASIC programming guide or generated table explicitly requires a whole-register write.

## Dependencies and Integration Points

The direct include site found in this tree is `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`. The resource file initializes DCN 3.1.6 display resources and pulls in ASIC-specific register definitions for lower-level display/link PHY programming.

This chunk depends on:

- The matching `dpcs_4_2_3_offset.h` register indices. Examples corresponding to this chunk include `ixDPCSSYS_CR4_SUP_DIG_MPLLB_ASIC_IN_0` at `0x002b`, `ixDPCSSYS_CR4_LANE0_DIG_ASIC_LANE_OVRD_IN` at `0x1000`, and `ixDPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` at `0x1141`.
- AMD display register helper conventions that combine an `ix...` offset with `__SHIFT` and `_MASK` macros for `REG_SET`, `REG_GET`, table initialization, or indirect DPCS access patterns. The helpers are outside this chunk; this file supplies only generated constants.
- Hardware generator input for DPCS 4.2.3. Similar DPCS 4.2.2 and other generation headers nearby have matching register families, so cross-generation comparison can validate generator output but cannot replace ASIC-specific documentation.

The CR4 prefix indicates this is one instance of a repeated DPCS channel/register block. Adjacent portions of the file define CR0 through CR3 and later CR4 lane fields, so callers must use the correct CR instance and lane number when mapping a physical connector or link lane to these macros.

## Risks and Maintenance Notes

- The chunk starts and ends on register boundaries that are not self-contained. `DPCSSYS_CR4_SUP_DIG_MPLLB_ASIC_IN_0` starts before line 80269, and `DPCSSYS_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0S` continues after line 82680. The later merge lane must account for both boundaries.
- The file is generated hardware data. Manual edits to a mask or shift can silently misprogram PLLs, analog trims, TX/RX pstate sequencing, lane equalization, or debug paths.
- MPLLA and MPLLB fields are visually similar. Copying a field from the wrong PLL group can send a valid-looking value to the wrong clock source.
- Lane 0 and lane 1 blocks repeat many names with only the lane number changed. A lane-number mismatch may only fail on connectors or link widths that exercise that lane.
- Pstate and timing fields directly affect PHY power-up and link-training behavior. Incorrect masks for reset, clock, serializer, CDR, VCO calibration, RX detect, VBOOST, or delay fields can cause blank displays, training failures, resume failures, or intermittent signal-integrity problems.
- Debug/test/override fields such as ATB, ATE-style analog controls, OCLA, LBERT, DCC, PMIX, and reserved words may require strict hardware sequencing or lab-only contexts. This header does not encode those safety constraints.
- Reserved fields are exported as normal macros, increasing the chance that broad mask composition writes reserved bits. Read-modify-write helpers should avoid touching them unless the generated programming sequence says otherwise.

## Test Signals

Useful validation signals for changes involving this chunk include:

- Compile coverage for AMD DCN 3.1.6 display resource code that includes `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Static checks that every `DPCSSYS_CR4_SUP_*`, `DPCSSYS_CR4_LANE0_*`, and `DPCSSYS_CR4_LANE1_*` shift/mask symbol used by code has a corresponding `ixDPCSSYS_CR4_*` offset in the matching offset header.
- Cross-generation diffs against `dpcs_4_2_2_sh_mask.h` and other nearby generated DPCS headers to separate intentional ASIC changes from generator drift or accidental edits.
- Hardware smoke tests on affected AMD ASICs: boot, enumerate connectors, hotplug, train DisplayPort/USB-C links at multiple rates and lane widths, modeset repeatedly, suspend/resume, and verify no link-training, blank-screen, or IRQ/power-transition regressions.
- PHY diagnostics around PLL lock/calibration, RTUNE status, TX/RX pstate transitions, DCC request/acknowledge, RX statistic counters, LBERT controls, and analog override clear paths when exercising link retraining and low-power transitions.
