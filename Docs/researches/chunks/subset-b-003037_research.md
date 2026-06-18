# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 78884-81236

## Scope

This chunk covers a generated AMD NBIO 6.1 shift/mask header segment for `DWC_E12MP_PHY_X4_NS_X4_1` PHY register fields. It contains 2,353 source lines, with 217 register-comment blocks and roughly matched `__SHIFT` and `_MASK` macro definitions. There are no C functions, structs, enums, variables, locks, allocations, or direct register accesses in this range.

The range starts at the tail of `DWC_E12MP_PHY_X4_NS_X4_1_SUPX_DIG_ASIC_IN`, after the first two shift fields from that register have appeared in the previous chunk. It then covers SUPX common PHY controls and status for level inputs, MPLLA/MPLLB override outputs, RTUNE, RX termination, PLL power-control/calibration, spread-spectrum clocking, analog MPLL/RTUNE/bandgap measurement controls, and common digital RTUNE state. Most of the chunk then describes the generic lane template `LANEX`, including lane digital ASIC override/input/output fields, TX/RX power states and timing, RX VCO calibration, loopback BERT controls, CDR/DPLL/adaptation/statistical counters, digital-to-analog override fields, and lane analog TX/RX measurement and override fields. The chunk ends after `DWC_E12MP_PHY_X4_NS_X4_1_LANEX_ANA_RX_ATB_VREG`; the next chunk begins with `RAWCMNX` raw common-memory fields.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of AMD's generated NBIO 6.1 hardware interface. Each register field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or update the field.

The companion `nbio_6_1_offset.h` supplies matching SMN/register offsets, while `nbio_6_1_default.h` supplies reset/default values for many of the same register names. Runtime AMDGPU code consumes these macros through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, SOC15/NBIO address helpers, and direct SMN/MMIO read-modify-write paths.

This particular chunk describes PCIe/PHY implementation details for a Synopsys-style DWC E12MP x4 PHY block inside NBIO. The fields are low-level PLL, receiver, transmitter, calibration, adaptation, clock, reset, loopback, measurement, and analog-test-bus controls. They are not filesystem-specific despite living under a `ceph-client` source mirror.

## Important Macro Families

### SUPX Common Digital and Analog PHY State

The `SUPX_DIG_*` and `SUPX_ANA_*` families describe common, non-lane-specific PHY controls:

- `SUPX_DIG_LVL_ASIC_IN` exposes level inputs such as RX VREF control and TX vboost level.
- `SUPX_DIG_ANA_MPLLA_OVRD_OUT` and `SUPX_DIG_ANA_MPLLB_OVRD_OUT` encode override outputs for analog enable, reset, calibration, output enables, lane-side output enables, divider clock enables, feedback clock, phase select, and override select for each MPLL.
- `SUPX_DIG_ANA_RTUNE_OVRD_OUT`, `SUPX_DIG_ANA_RX_TERM_OVRD_OUT`, and `SUPX_DIG_ANA_STAT` provide RTUNE override/reset/mode/value/enable fields, RX termination value fields, and analog comparator status.
- `SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and `SUPX_DIG_MPLLB_MPLL_PWR_CTL_*` define calibration load counts, skip/external calibration controls, coarse tune values, power-control override bits, FSM/status bits, and many timing thresholds for PCLK, VCO stabilization, VCO power-down, analog power-up, feedback clock enable, and feedback digital clock disable.
- `SUPX_DIG_MPLLA_SSC_*` and `SUPX_DIG_MPLLB_SSC_*` define spread-spectrum clocking phase and frequency fields.
- `SUPX_ANA_MPLLA_*` and `SUPX_ANA_MPLLB_*` expose analog MPLL reference/divider/charge-pump/VCO bias and measurement/ATB selectors.
- `SUPX_ANA_RTUNE_CTRL`, `SUPX_ANA_SWITCH_PWR_MEAS`, `SUPX_ANA_SWITCH_MISC_MEAS`, and `SUPX_ANA_BG` describe RTUNE reference/force controls, switch power/misc measurement controls, and bandgap controls.
- `SUPX_DIG_RTUNE_*` covers RTUNE request/status and per-domain set/status values for RX, TXDN, and TXUP termination.

These fields are central to PHY bring-up, calibration, spread-spectrum configuration, impedance tuning, and low-level diagnostics.

### LANEX Digital ASIC Interface and Overrides

The `LANEX_DIG_ASIC_*` families describe the lane-template interface between ASIC logic and the PHY lane:

- `LANEX_DIG_ASIC_LANE_OVRD_IN`, `TX_OVRD_IN_*`, and `RX_OVRD_IN_*` provide override controls for lane reset/enable, TX/RX requests, power state, rate, margin, swing, de-emphasis, coefficient requests, VREG control, CDR/VCO setup, adaptation, equalization, and RX/TX test or detect behavior.
- `LANEX_DIG_ASIC_*_ASIC_IN_*` mirrors the non-overridden ASIC input/control values for TX and RX setup, including power state/rate, TX coefficient controls, RX termination/vref/control, CDR/VCO inputs, and equalization/adaptation inputs.
- `LANEX_DIG_ASIC_TX_OVRD_OUT`, `RX_OVRD_OUT_0`, `TX_ASIC_OUT`, and `RX_ASIC_OUT_0` expose override and live output/status paths such as acknowledgment, valid flags, electrical idle, RX detection, and adaptation complete/status.
- `LANEX_DIG_ASIC_RX_OVRD_EQ_IN_*`, `RX_EQ_ASIC_IN_*`, and later digital analog override fields capture equalization, DFE, CTLE, slicer, and adaptation inputs.

These macros are repeated lane-template definitions rather than separate per-lane copies. Offset/header generation maps `LANEX`-style fields to actual lane instances elsewhere in the NBIO register map.

### Lane TX/RX Power, Timing, Calibration, and Loopback

The lane digital control section defines operational timing and diagnostic behavior:

- `LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` encode TX power-state behavior such as valid/request enables, power/reset behavior, rate masks, and lane timing bits.
- `LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_*` and `LANEX_DIG_RX_PWRCTL_RX_PWRUP_TIME_*` provide power-up and transition timing thresholds.
- `LANEX_DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` mirror the RX side with enable/reset/data/detect/CDR/adaptation controls per power state.
- `LANEX_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_*`, `RX_VCO_CAL_TIME_*`, and `RX_VCO_STAT_*` describe RX VCO calibration configuration, counters, thresholds, and status such as calibration done, DAC values, and bounds.
- `LANEX_DIG_TX_LBERT_CTL`, `RX_LBERT_CTL`, and `RX_LBERT_ERR` provide loopback BERT enable/control and error count fields.
- `LANEX_DIG_RX_CDR_CDR_CTL_*`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*` define CDR/DPLL proportional/integral gains, lock/fast-lock behavior, frequency setpoints, lock status, and frequency bounds.

These fields participate in live link bring-up, retraining, PHY power transitions, and receiver lock/calibration loops.

### RX Adaptation, Statistics, and Digital Analog Overrides

The middle and later lane families cover receiver adaptation and observability:

- `LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` through `ADPT_CFG_9` configure adaptation loops, calibration modes, limits, thresholds, and selection controls.
- `LANEX_DIG_RX_ADPTCTL_RST_ADPT_CFG` and status registers for attenuation, VGA, CTLE, and DFE taps expose adaptation reset/config and measured adapted values.
- Offset/status registers for even/odd data and error slicer VDAC values, bypass slicers, and slicer controls describe fine-grained RX front-end tuning.
- `LANEX_DIG_RX_STAT_*` defines load values, data masks, match controls, statistic controls, sample counts, statistic counters, and calibration/comparator clock controls for lane-level observation.
- `LANEX_DIG_ANA_TX_OVRD_OUT`, `ANA_TX_TERM_*`, `ANA_TX_EQ_*`, `ANA_RX_CTL_OVRD_OUT`, `ANA_RX_PWR_OVRD_OUT`, `ANA_RX_VCO_OVRD_OUT_*`, `ANA_RX_CAL`, and `ANA_RX_*` selector/control fields expose digital control of analog TX/RX blocks.

These macros support hardware-managed and software-forced RX equalization/adaptation, data-eye/statistical observation, and manufacturing or debug measurement flows.

### Lane Analog TX/RX Measurement and Override Controls

The final lane analog section covers analog measurement and power controls:

- TX-side families such as `LANEX_ANA_TX_OVRD_MEAS`, `TX_PWR_OVRD`, `TX_ALT_BUS`, `TX_ATB1`, `TX_ATB2`, `TX_VBOOST`, `TX_TERM_CODE_DN`, `TX_TERM_CODE_UP`, `TX_IBOOST_CODE`, `TX_OVRD_CLK`, and `TX_MISC` describe TX enable overrides, power overrides, alternate bus/ATB measurement selection, boost, termination, current boost, clock override, and misc controls.
- RX-side families such as `LANEX_ANA_RX_ATB_IQSKEW`, `RX_DCC_OVRD`, `RX_PWR_CTRL1`, `RX_ATB_REGREF`, `RX_CDR_AFE`, `RX_PWR_CTRL2`, `RX_MISC_OVRD`, `RX_CAL_MUXA/B`, `RX_ATB_MEAS1/2`, `RX_TERM`, `RX_SLC_CTRL`, and `RX_ATB_VREG` cover RX ATB measurement, duty-cycle correction, analog power enables, regulator/reference overrides, CDR AFE phase detector controls, loopback/DFE/deserializer power, calibration muxes, termination, slicer control, and vreg measurement/override selection.

These fields are especially sensitive because they map directly to analog front-end behavior, test-bus selection, and calibration observability.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, usually with an `L` suffix for masks.

The macros encode only bit position and bit mask. They do not encode access width beyond the visible 16-bit-style masks, reset value, read/write permission, write-one-to-clear semantics, hardware sequencing, power-domain ownership, privilege rules, or required delays. Call sites must combine these masks with the companion offset/default headers and the ASIC programming model.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU or firmware-facing code selects an NBIO/SMN PHY register offset from `nbio_6_1_offset.h`.
2. Code reads or composes a register value using the generated `__SHIFT` and `_MASK` macros.
3. The value is written to hardware or decoded for diagnostics/status.
4. Hardware PHY state machines act on the resulting reset, power, calibration, PLL, CDR, adaptation, loopback, or measurement controls.

Likely flows using these field families include GPU/PCIe PHY bring-up, link retraining, power-state transitions, suspend/resume restoration, reset handling, spread-spectrum and PLL setup, RTUNE impedance calibration, receiver adaptation, loopback BERT diagnostics, and analog test-bus measurement.

## State and Persistence Behavior

The header itself stores no state. It names hardware-visible register fields in NBIO's PHY blocks. Persistence is controlled by GPU reset domains, NBIO/PCIe PHY resets, firmware initialization, driver save/restore paths, suspend/resume, and explicit register writes.

Represented state includes PLL enable/reset/calibration state, spread-spectrum parameters, timing thresholds, RTUNE configuration and measured values, TX/RX power-state policy, TX/RX request/acknowledge paths, RX VCO calibration data, CDR/DPLL lock and frequency state, equalization/adaptation configuration and status, loopback BERT counters, statistic counters, analog measurement mux selections, termination/vboost/current settings, slicer/DFE/CTLE/VGA/attenuation values, and analog power/clock overrides.

Several fields are command-like or status-like rather than ordinary persistent configuration. Examples include reset and calibration request bits, `OVRD_SEL`/override-enable bits, RTUNE request/acknowledge/status, PLL FSM/status fields, RX VCO calibration status, BERT error counts, CDR lock state, adaptation-complete/status fields, statistic counter clear/control fields, and measurement/ATB mux selections. Correct software needs sequencing, polling, timeout, and power-domain rules from the owning AMDGPU code and hardware specification.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 6.1 header set:

- `nbio_6_1_offset.h` supplies matching register offsets and address-space names.
- `nbio_6_1_default.h` supplies default values for the same `DWC_E12MP_PHY_X4_NS_X4_1_*` register families.
- AMDGPU register helper macros consume the shift/mask convention for extraction and update.

Observed source-tree integration includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes the NBIO 6.1 offset and shift/mask headers for NBIO generation-specific control.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, which includes the same headers for SR-IOV/MxGPU behavior on the affected generation.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`, which pull the generated NBIO 6.1 definitions into Vega power-management code.
- `drivers/gpu/drm/amd/amdgpu/psp_v3_1.c` and `drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`, which include related NBIO 6.1 generated headers in PSP and display-resource integration paths.

The `DWC_E12MP_PHY_X4_NS_X4_1` macros are generated hardware metadata. They may be referenced directly by low-level bring-up or debug code, but many values are also consumed indirectly through generated register tables and include stacks.

## Risks and Edge Cases

- Shift/mask drift can compile cleanly while targeting the wrong PHY bit. In this chunk that can break PLL reset/calibration, power sequencing, CDR lock, equalization, termination, or analog measurement behavior.
- The chunk starts in the middle of `SUPX_DIG_ASIC_IN`. The previous chunk is required for the full register definition and for any source-file-level summary.
- Many fields are override controls. Leaving an override-enable bit asserted can bypass hardware state machines and cause unstable link training, bad power behavior, or misleading status.
- PLL and spread-spectrum fields are timing-sensitive. Incorrect thresholds, divider enables, or phase/frequency fields can prevent lock or create marginal PCIe links.
- RTUNE, termination, vboost, iboost, slicer, CTLE, VGA, DFE, and VREF fields directly affect analog signal integrity. Wrong masks can produce intermittent link errors rather than deterministic failures.
- Status, statistic, BERT, and adaptation fields may be latched, sampled, or cleared by side effects not expressed in the header. Treating them as normal read/write fields can lose diagnostic evidence or mis-sequence calibration.
- Repeated `MPLLA`/`MPLLB`, TX/RX, and power-state families are mechanically similar but not interchangeable. Copying a mask between families can silently alter the wrong clock or lane path.
- Reserved and `NC*` fields appear throughout. Software should preserve them on read-modify-write unless the hardware programming guide says otherwise.
- `LANEX` is a template-style namespace. Final per-file reconciliation should avoid treating it as a single physical lane without checking offset/header mapping.

## Test Signals

- Build AMDGPU configurations that include NBIO 6.1, Vega10/Vega12 powerplay, MXGPU, PSP, and DCE120 display-resource paths; this catches missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: shift/mask width checks, non-overlap within each 16-bit register, offset-to-field-name pairing, default-header alignment, and repeated-family checks for MPLLA/MPLLB and TX/RX power states.
- On affected AMD GPUs, verify PCIe link bring-up, negotiated speed/width, retraining, suspend/resume, and GPU reset across cold boot and warm reset.
- Validate PLL and PHY calibration by checking MPLL lock/status, VCO calibration status, RTUNE status/set values, and absence of unexpected timeout paths.
- Exercise power-management transitions that move TX/RX through P0/P0S/P1/P2 and confirm link stability and resume behavior.
- Use hardware diagnostics or debugfs paths, where available, to read CDR/DPLL lock/frequency state, adaptation status, statistic counters, and BERT error counters.
- Signal-integrity or lab validation should cover termination, vboost/iboost, CTLE/VGA/DFE/slicer controls, RX VREF, and analog test-bus mux selections because software-visible bitfield errors may appear as marginal or board-specific link faults.
- Regression tests should preserve reserved fields during read-modify-write and should specifically check that override-enable fields are cleared or restored after diagnostic flows.

## Unresolved Cross-Chunk References

Line 78884 is inside the already-started `DWC_E12MP_PHY_X4_NS_X4_1_SUPX_DIG_ASIC_IN` definition, so the previous chunk is needed to see the register comment and first fields. The next chunk starts a new `RAWCMNX` memory-register family after this chunk's final `LANEX_ANA_RX_ATB_VREG` masks. The final per-file document should stitch those boundaries before making complete statements about the `DWC_E12MP_PHY_X4_NS_X4_1` PHY block.
