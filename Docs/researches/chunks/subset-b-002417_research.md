# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 75406-77827

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header segment for CR3 raw always-on lane, CR3 supervisor, and CR3 generic lane-X register fields. It contains only C preprocessor constants: `__SHIFT` macros encode field bit positions and `_MASK` macros encode the field masks used by AMDGPU display PHY register programming. There are no functions, structs, storage objects, or runtime branches in this range.

The range begins in the tail of `DPCSSYS_CR3_RAWAONLANEX_DIG_RX_OVRD_OUT_2`, after that register's shift definitions were introduced by the previous chunk, and then covers complete groups from `DPCSSYS_CR3_RAWAONLANEX_DIG_RX_OVRD_OUT_3` through most of `DPCSSYS_CR3_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_6`. It ends before the final mask definitions for the same `ADPT_CFG_6` register family continue into the next chunk.

## Purpose

The header provides generated bit layout metadata for DPCS CR3 PHY registers. Driver code pairs these constants with address macros from `dpcs_4_2_3_offset.h` and register helper macros to construct read-modify-write values without hard-coding bit positions. The fields in this chunk describe low-level analog/display PHY behavior for:

- Raw always-on lane RX signal detection, squelch, termination, VREF, DCC calibration, TX DCC bank access, firmware-visible configuration, lane transceiver mode, and signal-detect filtering.
- CR3 supervisor reference clock, bandgap, prescaler, RTUNE, MPLLA/MPLLB, spread-spectrum, power-state, and analog override/status controls.
- Generic lane-X ASIC TX/RX override and ASIC input/output mirrors, TX and RX power-state programming, TX DCC controls, TX clock alignment, LBERT controls, RX VCO/CDR/DPLL calibration, and the beginning of RX adaptation configuration.

This is hardware-description support for AMD display link bring-up, link training, diagnostics, and PHY tuning. It is unrelated to Ceph logic except for the repository import path.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The important interface is the generated macro naming convention:

- `DPCSSYS_CR3_*__FIELD__SHIFT` gives the least-significant bit position for `FIELD`.
- `DPCSSYS_CR3_*__FIELD_MASK` gives the mask for `FIELD` in the register value.
- Register comments such as `//DPCSSYS_CR3_SUPX_DIG_REFCLK_OVRD_IN` delimit groups that correspond to `ixDPCSSYS_CR3_*` address definitions in the companion offset header.

Key raw always-on lane groups include:

- `RAWAONLANEX_DIG_RX_OVRD_OUT_2/3`: override-value and override-enable fields for RX VREF generation, squelch output, termination mode/enables, and LF/HF signal-detect enables.
- `RAWAONLANEX_DIG_RX_SIGDET_CAL`, `RX_SIGDET_HF_CODE`, and `RX_SIGDET_LF_CODE`: signal-detect thresholds, calibration enable, and LF/HF calibration tune codes.
- `RAWAONLANEX_DIG_RX_VREFGEN_EN` and `CAL_*_CODE`: VREF generator pull-up enable plus calibration codes for IOFF, ICONST, and VREFGEN.
- `RAWAONLANEX_DIG_RX_DCC_CAL_{ICM,IDF,QCM,QDF}_CODE_{0,1}`: 10-bit DCC calibration code fields for I/Q common-mode and differential paths.
- `RAWAONLANEX_DIG_TX_DCC_BANK_ADDR`, `TX_DCC_BANK_DATA`, `TX_DCC_CONT`: TX DCC bank addressing/data and continuous-control enable.
- `RAWAONLANEX_DIG_MPLL_BG_CTL`: MPLL state wait and delay-enable controls.
- `RAWAONLANEX_DIG_SIGDET_OUT_OVRD` and `SIGDET_OUT_IN`: override and input status fields for LF/HF signal-detect outputs.
- `RAWAONLANEX_DIG_FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`: firmware-visible mode/adaptation/calibration fields.
- `RAWAONLANEX_DIG_LANE_XCVR_MODE_OVRD_IN` and `LANE_XCVR_MODE_IN`: lane transceiver mode override and observed mode fields.
- `RAWAONLANEX_DIG_RX_SIGDET_CONFIG` and `TX_DCC_CONFIG`: filter counters, LF hold, and TX DCC configuration data.

Key supervisor digital groups include:

- `SUPX_DIG_IDCODE_LO/HI`: supervisor identification data fields.
- `SUPX_DIG_REFCLK_OVRD_IN`: reference clock enable/source/range, bandgap enable, HDMI-mode enable, and pre-hotplug override fields.
- `SUPX_DIG_MPLLA_*` and `SUPX_DIG_MPLLB_*`: parallel families for PLL A/B divider clock, HDMI clock, override inputs, spread-spectrum peak/stepsize, charge-pump settings, ASIC inputs, and clock synchronization.
- `SUPX_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, and `DEBUG`: supervisor-level override, prescaler, status override, voltage/boost-level override, and debug mux fields.
- `SUPX_DIG_ASIC_IN`, `LVL_ASIC_IN`, `BANDGAP_ASIC_IN`, and per-MPLL `*_ASIC_IN`: observed or ASIC-driven inputs for reset, reference clocking, RTUNE handshake, MPLL state, reference/boost levels, multiplier, SSC, PMIX, charge pump, and divider controls.
- `SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `SUPX_DIG_MPLLB_MPLL_PWR_CTL_*`: MPLL power-control override/status, timer, calibration, DAC, and SSC spread-type fields.
- `SUPX_DIG_CLK_RST_*`: bandgap and reference power-up timing, fast-wait controls, state update enables, and VPHUD controls.
- `SUPX_DIG_RTUNE_*`: RTUNE debug, configuration, status, set values, result registers, timers, and TX calibration code fields.
- `SUPX_DIG_ANA_*`: digital outputs/status for analog MPLL A/B controls, RTUNE override, bandgap override, and PMIX override.

Key supervisor analog groups include:

- `SUPX_ANA_PRESCALER_CTRL`, `RTUNE_CTRL`, `BG1/BG2/BG3`, and `SWITCH_PWR_MEAS`: prescaler, resistor tuning, bandgap, ATB, and power measurement fields.
- `SUPX_ANA_MPLLA_*` and `SUPX_ANA_MPLLB_*`: analog PLL miscellaneous, override, ATB, control, and reserved fields for both PLL instances. These include RC filter, VREG, calibration, gearshift, standby, charge-pump, feedback, divider, and bypass controls.

Key generic lane-X groups include:

- `LANEX_DIG_ASIC_LANE_OVRD_IN` and `LANE_ASIC_IN`: lane loopback and ACJTAG override/input fields.
- `LANEX_DIG_ASIC_TX_OVRD_IN_0..5`, `TX_OVRD_OUT`, and `TX_OVRD_OUT_1`: TX request, PSTATE, rate, width, MPLL selection, data enable, disable, beacon, cursor, async drive, reset, lane-master, repeater, digital-clock, shift, and acknowledgement overrides/status.
- `LANEX_DIG_ASIC_RX_OVRD_IN_0..6`, `RX_OVRD_EQ_IN_0..1`, and `RX_OVRD_OUT_0`: RX request/data/PSTATE/rate/width, reference-load, VCO load, CDR tracking, SSC, align, clock shift, disable, LPD, invert, adaptation, termination, reset, PWM, EQ, acknowledgement, adaptation status, async data, and squelch weak-keep overrides/status.
- `LANEX_DIG_ASIC_TX_ASIC_IN_*`, `TX_ASIC_OUT`, `RX_ASIC_IN_*`, `RX_EQ_ASIC_IN_*`, `RX_CDR_VCO_ASIC_IN_*`, and `RX_ASIC_OUT_0`: ASIC-provided or mirrored TX/RX request/status fields for the same lane control surface.
- `LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2` and `TX_PWRUP_TIME_0..5`: TX power-state enables and sequencing delays for refgen, VCM hold, clocks, reset, serial/data enable, RX detect, VBOOST, and DCC calibration.
- `LANEX_DIG_TX_PWRCTL_DCC_*`: TX DCC CR bank address/data, DAC control/range/selection/ack/address.
- `LANEX_DIG_TX_CLK_ALIGN_TX_CTL_0`, `TX_LBERT_CTL`, and `ASIC_OCLA`: TX clock alignment, TX LBERT, and OCLA debug-clock/data enables.
- `LANEX_DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2` and `RX_PWRUP_TIME_1..3`: RX power-state enables and startup timing for AFE, clock regulators, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, and rate/CDR timing.
- `LANEX_DIG_RX_VCOCAL_*`: VCO calibration controls, timing, and status including gain calibration, override selection, DPLL calibration gain, tune start/step, skip controls, FSM state, calibration done, final counter, fast/slow/correct indicators, and VCO direction.
- `LANEX_DIG_RX_RX_ALIGN_XAUI_COMM_MASK`, `RX_LBERT_CTL`, and `RX_LBERT_ERR`: XAUI comma mask and RX LBERT mode/sync/error count.
- `LANEX_DIG_RX_CDR_CDR_CTL_0..4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_0/1`: CDR phase-detector, SSC counter, loop-gain override, status, DPLL frequency, and frequency bounds.
- `LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0..6`: RX adaptation setup through the start of adaptation step-size/saturation fields. This chunk includes CTLE/VGA/ATT/DFE enable masks, TGG patterns, thresholds, wait/top counters, CTLE pole override, and the beginning of `ADPT_CFG_6` fields such as `CTLE_MU`, `VGA_MU`, `ATT_MU`, `VGA_SAT_CNT`, `VGA_SAT_CNT_STICKY`, and `ATT_LOW_TH`.

## Control Flow

This header has no runtime control flow. Its compile-time constants are consumed by driver code that performs sequences such as:

1. Read a DPCS CR register value through the AMD display register access path.
2. Clear a field with the `_MASK` value.
3. Insert a value shifted by the matching `__SHIFT`.
4. Write the updated value back to the address defined in `dpcs_4_2_3_offset.h`.

The hardware behavior implied by the field groups is sequenced outside this file: reference clock and bandgap startup, MPLL A/B setup, RTUNE calibration, lane TX/RX power-state transitions, VCO/CDR/DPLL calibration, RX adaptation, DCC programming, link diagnostics, and status polling. Override fields commonly appear as value/enable pairs, so the caller must set the override value and its enable bit coherently.

## State And Persistence

The macros are stateless compile-time constants. The state they describe is volatile DPCS hardware state in PHY registers. Those register values can change due to display link training, hotplug/modeset activity, PHY calibration, firmware or hardware state machines, GPU reset, display engine reset, power-gating, suspend/resume, or link disable/re-enable.

Reserved masks are part of the generated hardware contract. They help consumers identify fields that should usually be preserved across read-modify-write operations or avoided entirely. Because this is analog and PHY control state, incorrect writes can persist until a later PHY reset or power-cycle even though the header itself stores nothing.

## Dependencies

This chunk depends on AMD's ASIC register-generation pipeline staying synchronized with DPCS 4.2.3 hardware specifications. It is normally used with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which defines register addresses such as `ixDPCSSYS_CR3_RAWAONLANEX_DIG_RX_SIGDET_CAL`, `ixDPCSSYS_CR3_SUPX_DIG_REFCLK_OVRD_IN`, and `ixDPCSSYS_CR3_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_6`.
- AMDGPU DRM display/DC register access helpers that combine field masks and shifts into MMIO or indexed DPCS CR writes.
- ASIC-specific link encoder, PHY, DisplayPort, HDMI, and diagnostics code that decides when these low-level fields should be programmed.
- Closely related generated DPCS/DCN headers for neighboring ASIC revisions; the same register families exist in 4.2.0/4.2.2, but masks are not always textually identical across versions.

## Integration Points

The raw always-on lane macros integrate with signal-detect calibration, termination control, DCC calibration, lane transceiver mode selection, and firmware-visible PHY knobs. These are relevant during receiver detection, lane initialization, PHY bring-up, and debugging of marginal signal-detect behavior.

The supervisor macros integrate with reference clock setup, bandgap/prescaler startup, RTUNE calibration, MPLL A/B programming, spread-spectrum control, PLL power-state sequencing, and analog override/status readback. They affect both DP and HDMI PHY operation because PLL selection, divider clock, HDMI clock, and reference-clock behavior determine link clock generation.

The generic lane-X macros integrate with per-lane link training and diagnostics. TX power-state and cursor controls affect transmitted signal quality. RX power, VCO, CDR, DPLL, and adaptation controls affect lock, equalization, and data recovery. LBERT, OCLA, debug muxes, and status fields are validation/debug integration points for lab bring-up and hardware characterization.

## Risks

- The range starts and ends on chunk boundaries inside active register groups; the previous chunk completes `RAWAONLANEX_DIG_RX_OVRD_OUT_2` shifts, and the next chunk completes `LANEX_DIG_RX_ADPTCTL_ADPT_CFG_6` masks plus later adaptation fields.
- The constants are generated and highly repetitive. A copied macro from the wrong lane, PLL instance, or ASIC revision can compile but program the wrong hardware field.
- Many registers contain value/override-enable pairs. Setting an enable bit without the intended value, or writing a value while the enable remains clear, can make debug and bring-up behavior misleading.
- Reserved-bit masks indicate undocumented or hardware-owned regions. Callers that write full constants instead of preserving reserved bits risk destabilizing PLL, analog, or PHY state.
- PLL, reference clock, bandgap, RTUNE, VCO, CDR, DPLL, and TX/RX power-state fields are sequencing-sensitive. Programming them out of order can cause link-training failure, display blanking, unstable high-rate links, or intermittent hotplug/modeset failures.
- Some fields are status/acknowledgement surfaces rather than pure controls. Treating status masks as writable controls can produce no effect or hide the actual state-machine failure.
- Version drift matters: DPCS 4.2.3 uses 16-bit-looking masks in this chunk, while related generated headers may use wider hex formatting or slightly different layouts. Consumers must include the matching 4.2.3 header for the target ASIC.

## Test Signals

Useful validation signals for changes touching this generated header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_3_sh_mask.h`.
- Static checks that each complete register field has both a `__SHIFT` and `_MASK`, and that masks stay within the expected DPCS CR register width unless a documented wider register exists.
- Comparison against the corresponding `dpcs_4_2_3_offset.h` register names to catch missing or mismatched generated groups.
- Display bring-up on ASICs using DPCS 4.2.3, including boot display, hotplug, modeset, suspend/resume, and GPU reset recovery.
- DP and HDMI link-training tests across lane counts, rates, pixel clocks, spread-spectrum settings, and multi-monitor configurations.
- PHY diagnostics that exercise RTUNE, MPLL lock/status, DCC bank access, LBERT, OCLA, signal-detect calibration, VCO/CDR/DPLL status, and RX adaptation readback.
- Stress tests for high-bandwidth display modes and repeated HPD/retrain cycles, since timing and analog override mistakes often surface as intermittent link instability rather than compile-time failures.
