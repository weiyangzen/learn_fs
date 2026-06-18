# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 101312-103687

## Purpose

This chunk is part of AMDGPU's generated NBIO 6.1 shift/mask header for the `DWC_E12MP_PHY_X4_NS_X4_2` PCIe PHY register block. It contains bitfield geometry for the second x4 PHY instance's `SUPX`, `LANEX`, and `RAWCMNX` register namespaces. The contents are hardware metadata: each register field is represented by a `__SHIFT` constant and a matching `_MASK` constant so driver code can encode or decode individual fields when reading or writing NBIO/SMN registers.

The chunk starts inside the `SUPX_DIG_MPLLA_MPLL_PWR_CTL_STAT` block, covering the mask definitions for MPLLA status bits such as `MPLL_OUTPUT_EN`, `MPLL_FBCLK_EN`, `MPLL_CAL`, `MPLL_RST`, and `MPLL_ANA_EN`. It then covers the remaining MPLLA timing, calibration, and spread-spectrum-clocking fields; a complete corresponding MPLLB block; shared SUPX analog and RTUNE controls; the LANEX digital ASIC interface, TX/RX power control, VCO calibration, CDR, adaptation, statistics, and digital-to-analog override/status registers; LANEX analog TX/RX measurement and override registers; and finally the start of the `RAWCMNX_DIG_MEM_CMN2` data window for banks B0 and B1.

The range contains 2,116 `#define` entries across 261 commented register blocks. There are 1,055 `__SHIFT` entries and 1,061 `_MASK` entries. The apparent imbalance is because the line range begins at the tail of a register whose shifts are in the previous chunk and ends cleanly at `RAWCMNX_DIG_MEM_CMN2_B1_R19`.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, typedefs, or executable helpers in this chunk. The exported interface is entirely preprocessor constants following the generated AMD register naming scheme:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a field in the register.
- `<REGISTER>__<FIELD>_MASK`: already-shifted bit mask for that field.

The main register families in this chunk are:

- `DWC_E12MP_PHY_X4_NS_X4_2_SUPX_DIG_MPLLA_*` and `..._MPLLB_*`: master PLL A/B power-control calibration, override, state, timing-threshold, coarse-tune, skip-calibration, and spread-spectrum-clocking fields. Important fields include `MPLL_SKIPCAL`, `MPLL_EXTCAL`, `EXT_COARSE_TUNE`, `EXT_CAL_DONE`, `OVRD_SEL`, `MPLL_FBDIGCLK_EN`, `MPLL_PCLK_EN`, `FAST_MPLL_PWRUP`, `FAST_MPLL_LOCK`, `FSM_STATE`, `MPLL_CAL_RDY`, VCO/PCLK stabilization thresholds, feedback clock thresholds, `MPLL_COARSE_TUNE_VAL`, SSC phase, and SSC frequency peak/init overrides.
- `DWC_E12MP_PHY_X4_NS_X4_2_SUPX_ANA_*`: shared analog PLL and reference-tuning fields. These include MPLLA/MPLLB bias, charge-pump, reference, feedback, measurement, ATB, override, RTUNE, switch power/misc measurement, and bandgap fields.
- `DWC_E12MP_PHY_X4_NS_X4_2_SUPX_DIG_RTUNE_*`: digital RTUNE configuration, status, set-value, and status-value fields for RX, TX pull-down, and TX pull-up resistance tuning.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_DIG_ASIC_*`: digital handoff between ASIC-side PCS/control logic and lane PHY logic. This covers TX/RX override inputs, ASIC inputs, override outputs, equalization override inputs, lane reset/rate/width/pll selection, TX amplitude/de-emphasis/swing settings, RX CDR/equalizer/terminal/slicer controls, and status outputs.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_DIG_TX_PWRCTL_*` and `...RX_PWRCTL_*`: TX and RX P-state definitions and power-up sequencing timers. TX fields gate reference generator, VCM hold, analog clock, word clock, reset, serial enable, digital clock, data enable, RX detect, Vboost disable timing, and LBERT pattern generation. RX fields gate LOS, AFE, clock regulator, div clocks, DCC, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, adaptation, and RX bring-up timing.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_DIG_RX_VCOCAL_*`: RX VCO calibration control, timing, and status fields, including calibration reset, continuous calibration, DPLL calibration update gain, frequency tune start/steps, startup/update/settle timing, VCO FSM state, calibration-done, final counter, too-fast indication, and VCO-correct/up status.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_DIG_RX_CDR_*` and `...RX_DPLL_*`: CDR control/status and DPLL frequency/frequency-bound fields. These fields select update modes, lock-detect thresholds, gain/path controls, frequency status, and bounds used when the receiver tracks incoming serial data.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_DIG_RX_ADPTCTL_*`: receiver adaptation configuration and status. The fields define CTLE/VGA/ATT/DFE enables, thresholds, step sizes, mu values, initial error slicer levels, adaptation resets, and status readback for attenuator, VGA, CTLE, DFE taps, slicer levels, and DFE bypass offsets.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_DIG_RX_STAT_*`: scope/statistics capture controls, sample counters, pattern masks/matches, statistic counters, comparator clock controls, and data masks. These are diagnostic and validation-oriented fields for inspecting receiver behavior.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_DIG_ANA_*`: digital-side outputs to the analog lane macros and analog status readbacks. This includes TX/RX analog override outputs, RX calibration, DAC controls, AFE ATT/VGA/CTLE, scope selection, slicer controls, IQ phase adjustment, self-clear-disable bits, analog update enables, and analog status such as RX LOS, calibration result, scope data, and VCO counter.
- `DWC_E12MP_PHY_X4_NS_X4_2_LANEX_ANA_*`: analog lane override, measurement, ATB, term-code, boost, clock, power, CDR/AFE, RX calibration mux, RX termination, slicer, and voltage-regulator measurement fields. These are low-level PHY analog controls used for bring-up, tuning, debug, and manufacturing diagnostics.
- `DWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_CMN2_B0_R0` through `B0_R31` and `B1_R0` through `B1_R19`: raw common-memory data registers. Each block has a single `DATA` field at shift 0 with mask `0xFFFFL`.

These constants are intended to be consumed with the generated address constants in `nbio_6_1_offset.h` and, where applicable, reset/default constants in `nbio_6_1_default.h`. Runtime users typically access the hardware through AMDGPU/SOC15 helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and SMN/NBIO access wrappers rather than using the masks directly.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. Including the header only makes constants available for compile-time expansion. Any behavior happens in AMDGPU driver code that combines an offset macro, a shift/mask macro from this header, and a register read/modify/write helper.

The hardware behavior represented here is sequencing-heavy even though the header is not executable. The SUPX MPLL fields model PLL calibration and clock/power sequencing: driver or firmware can select overrides, skip calibration, provide external coarse tuning, wait on status bits such as `EXT_CAL_DONE` or `MPLL_CAL_RDY`, and apply time thresholds for VCO stabilization, PCLK enable/disable, analog power-up, and feedback-clock transitions. The LANEX TX/RX power-control fields similarly define state-machine inputs for bringing analog and digital sub-blocks up and down across P-states.

Receiver bring-up and training are represented by VCO calibration, CDR, DPLL, and adaptation fields. A normal lane-training path would depend on hardware/firmware-managed state machines using these settings to enable clocks, reset/calibrate VCOs, lock CDR/DPLL, adapt CTLE/VGA/DFE/slicer levels, and report status. Diagnostic paths may program LBERT, RX statistic/scope controls, analog test-bus fields, or raw memory data windows to validate link quality and PHY state.

The `LANEX` prefix indicates a per-lane template rather than a concrete `LANE0`/`LANE1` name. Companion generated offset/default headers expand the same hardware description across concrete lanes and instances. The final `RAWCMNX` memory-register series is a simple 16-bit data aperture; control flow for selecting/interpreting those entries lives outside this header.

## State and Persistence

The header itself owns no state, allocates no memory, and persists nothing. The state described by these constants is hardware state in NBIO PCIe PHY registers.

Fields in this chunk fall into several state categories:

- Configuration/override state: MPLL override selection, PLL/coarse-tune values, SSC overrides, RTUNE set values, lane TX/RX override inputs, P-state enable bits, CDR/DPLL/adaptation configuration, analog override bits, and raw memory data registers.
- Timing/state-machine thresholds: VCO stabilization, PCLK enable/disable, analog power-up, feedback clock enable/disable, TX/RX power-up waits, VCO calibration timing, CDR/adaptation waits, and statistic sample controls.
- Status/readback state: PLL FSM/calibration state, RTUNE status, ASIC/analog status outputs, RX VCO status, CDR status, adaptation codes/done bits, RX statistic counters, analog calibration results, LOS, RX detect results, scope data, and VCO counters.
- Reserved fields: many masks explicitly cover reserved high bits. These define the generated register layout but should generally be preserved or left at hardware defaults in read/modify/write code unless the hardware specification says otherwise.

Persistence and reset behavior are determined by the ASIC register specification, firmware initialization, power-gating behavior, and the NBIO reset domain. A wrong mask or shift in this generated header would persist at the software-contract level: every compiled user would read, set, or preserve the wrong hardware bits until the header is regenerated or fixed.

## Dependencies and Integration Points

The direct dependencies are the companion generated NBIO 6.1 headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` supplies the register addresses for these field definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` supplies reset/default values for many matching `DWC_E12MP_PHY_X4_NS_X4_2_*` registers.
- Other AMD generated register headers provide similar field layouts for neighboring PHY instances, concrete lanes, or other ASIC/NBIO revisions.

In-tree AMDGPU integration points include source files that include `nbio_6_1_sh_mask.h`, notably `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, `drivers/gpu/drm/amd/amdgpu/psp_v3_1.c`, the Vega10/Vega12 PowerPlay include files, and display resource code that includes NBIO 6.1 offsets. This specific chunk is most relevant to low-level NBIO/PCIe PHY initialization, ASIC bring-up, firmware-mediated PHY programming, link training/debug, manufacturing diagnostics, and power-management paths that alter or inspect PHY PLL/lane state.

Because these are generated constants, the practical integration contract is name alignment. A register field must align across:

- The commented register block name in `nbio_6_1_sh_mask.h`.
- The address macro in `nbio_6_1_offset.h`.
- The reset/default macro in `nbio_6_1_default.h` when one exists.
- The hardware register specification used by firmware and driver code.

## Risks

- Generated-header drift is the primary risk. If any `_MASK` or `__SHIFT` diverges from the ASIC register database, driver code will silently manipulate the wrong bits.
- The chunk crosses a boundary at the start. The line range begins with masks for `SUPX_DIG_MPLLA_MPLL_PWR_CTL_STAT`; the matching shifts are in the prior chunk. Whole-file reconciliation must join those halves before checking pair completeness.
- The low-level PHY fields are timing and sequencing sensitive. Incorrect threshold masks for VCO stabilization, PCLK transitions, TX/RX power-up, VCO calibration, CDR, or adaptation could cause intermittent link-training failures rather than obvious compile-time errors.
- Override fields can bypass hardware state machines. Misprogramming `OVRD_SEL`, analog override enables, skip-calibration bits, self-clear-disable bits, or raw data windows can leave the PHY in a mode that is only visible on specific boards, speeds, lanes, or power states.
- Many fields are narrow and adjacent. A one-bit width error can bleed into reserved bits or neighboring controls, especially in packed analog registers and DFE/CTLE/VGA adaptation controls.
- Reserved-bit masks appear throughout the chunk. Read/modify/write users must preserve reserved state correctly; writing a value assembled without masking against the expected field layout can alter undocumented hardware behavior.
- The `LANEX` template naming can be confused with concrete lane register names. Any code generator or manual lookup must map this template to the correct concrete lane/instance offset.
- The `RAWCMNX_DIG_MEM_CMN2` blocks are uniform 16-bit data apertures. Their semantic meaning is not encoded in this header, so validation requires the hardware memory-map documentation or the firmware flow that selects the memory context.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware-oriented integration testing:

- Build AMDGPU with NBIO 6.1 support enabled to catch missing, renamed, or syntactically invalid macros.
- Run static consistency checks that every complete register block has paired `__SHIFT` and `_MASK` entries, masks are contiguous where expected, and `(mask >> shift)` matches the documented field width.
- Cross-check every `DWC_E12MP_PHY_X4_NS_X4_2_*` field block against matching names in `nbio_6_1_offset.h` and `nbio_6_1_default.h`.
- Compare the `SUPX` and `SUPX`-like duplicated MPLLA/MPLLB layouts against neighboring generated blocks to detect copy/generation skew between PLL A and PLL B or between PHY instances.
- On supported Vega/NBIO 6.1 hardware, exercise PCIe link training across rates and widths, suspend/resume, runtime power management, GPU reset, and any available SR-IOV or virtualization paths that use NBIO programming.
- Use debug or bring-up diagnostics to read PLL status, VCO calibration done/state, CDR lock/status, RX adaptation status, analog status, RX statistic counters, and raw memory windows after link initialization.
- PHY validation should include LBERT/pattern-test paths, RX scope/statistic capture, and analog test-bus measurement flows because this chunk defines many diagnostic controls that normal display or compute workloads may not touch.
