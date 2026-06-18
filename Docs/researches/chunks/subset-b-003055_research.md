# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 123731-126138

## Scope

This chunk covers a generated AMD NBIO 6.1 shift/mask header segment for `DWC_E12MP_PHY_X4_NS_X4_3` PCIe PHY fields. The selected range contains 2,408 source lines, 2,107 `#define` lines, 1,053 `__SHIFT` macros, 1,057 `_MASK` macros, and 301 register-comment markers. It has no C functions, structs, enums, variables, allocations, locks, or executable statements.

The range begins at the final mask lines for `DWC_E12MP_PHY_X4_NS_X4_3_SUPX_DIG_MPLLB_MPLL_PWR_CTL_PCLK_EN_AND_VCO_CLK_STABILIZATION_TIME_THRESHOLD`, then continues through the shared `SUPX` MPLLB timing, coarse-tune, spread-spectrum clocking, analog MPLL, RTUNE, switch-measurement, and bandgap fields. Most of the chunk describes the generic `LANEX` register template for lane digital ASIC inputs/overrides, TX/RX power sequencing, RX VCO calibration, CDR/DPLL, RX adaptation, statistics, digital-to-analog controls, and lane analog TX/RX measurement and override controls. The tail starts the raw common-memory `RAWCMNX_DIG_MEM_CMN2` bank table through `B3_R10__DATA__SHIFT`; the matching `B3_R10__DATA_MASK` is on the next source line outside this chunk.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 6.1 register contract. For each named hardware register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position for packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the mask for isolating or preserving that field.

The companion generated headers provide the other pieces of the contract: `nbio_6_1_offset.h` and `nbio_6_1_smn.h` identify register addresses, while `nbio_6_1_default.h` supplies reset/default values. Runtime AMDGPU code normally consumes these names through helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, SOC15/NBIO offset helpers, and MMIO/SMN read-modify-write paths.

This particular slice describes low-level DesignWare E12MP x4 PCIe PHY controls for the `NS_X4_3` instance. The fields are about PLL timing and calibration, spread-spectrum clocking, analog test and tuning, TX/RX power states, RX lock and equalization, signal-integrity controls, and opaque raw PHY common memory. They are hardware register metadata, not Ceph or filesystem logic.

## Important Macro Families

### Shared SUPX MPLLB, Analog, and RTUNE Controls

The first portion completes and continues the shared supervisor/common PHY block:

- `SUPX_DIG_MPLLB_MPLL_PWR_CTL_*` defines MPLLB timing thresholds and calibration knobs, including PCLK disable timing, VCO power-down, analog power-up, feedback-clock enable, feedback digital-clock disable, coarse tune, skip-calibration coarse tune, and spread-spectrum phase/frequency fields.
- `SUPX_ANA_MPLLA_*` and `SUPX_ANA_MPLLB_*` define analog MPLL controls for misc regulator bits, override enables, enable/calibration/feedback/reset override values, and analog test-bus selectors.
- `SUPX_ANA_RTUNE_CTRL`, `SUPX_DIG_RTUNE_*`, `SUPX_ANA_SWITCH_PWR_MEAS`, `SUPX_ANA_SWITCH_MISC_MEAS`, and `SUPX_ANA_BG` cover impedance tuning, RX/TX termination set/status values, switch power/misc measurement controls, and bandgap/test-bus behavior.

These fields participate in shared PHY bring-up, PLL stability, spread-spectrum setup, impedance calibration, and low-level diagnostics.

### LANEX Digital ASIC Interface and Overrides

The `LANEX_DIG_ASIC_*` macros describe a lane-template interface between ASIC link logic and the PHY lane:

- `LANEX_DIG_ASIC_LANE_OVRD_IN`, `TX_OVRD_IN_*`, and `RX_OVRD_IN_*` provide override-enable/value fields for lane reset, TX/RX requests, TX coefficients, power state, rate, electrical-idle, RX termination, VREF, equalization, CDR/VCO controls, adaptation, and detection/test controls.
- `LANEX_DIG_ASIC_*_ASIC_IN_*` mirrors the live non-overridden ASIC inputs for the same TX/RX paths.
- `LANEX_DIG_ASIC_TX_OVRD_OUT`, `RX_OVRD_OUT_0`, `TX_ASIC_OUT`, and `RX_ASIC_OUT_0` expose outgoing override/status paths such as acknowledgements, valid indicators, RX detection, adaptation status, and electrical-idle style state.
- `RX_OVRD_EQ_IN_*`, `RX_EQ_ASIC_IN_*`, and `RX_CDR_VCO_ASIC_IN_*` capture receiver equalization and clock recovery inputs, including DFE, CTLE, slicer, adaptation, and VCO-related control fields.

The `LANEX` namespace is template-like. It describes the repeated lane layout; companion offset/default headers map related generated names to concrete hardware registers and defaults.

### Lane TX/RX Power, Calibration, and CDR/DPLL

The next lane block defines power sequencing and receiver lock behavior:

- `LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` describe TX behavior by power state, including request/valid handling, power/reset controls, rate masks, and timing bits.
- `LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_*` and `LANEX_DIG_RX_PWRCTL_RX_PWRUP_TIME_*` define transition thresholds and timer values for TX/RX power-up and reset sequencing.
- `LANEX_DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` mirror RX-side power-state policy, including RX enable, reset, data enable, CDR, adaptation, and detect behavior.
- `LANEX_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_*`, `RX_VCO_CAL_TIME_*`, and `RX_VCO_STAT_*` define RX VCO calibration controls, timeouts, thresholds, DAC/status fields, and calibration-done indicators.
- `LANEX_DIG_RX_CDR_CDR_CTL_*`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*` expose CDR loop gains, lock controls, fast-lock controls, frequency setpoints, bounds, and lock/status fields.
- `LANEX_DIG_TX_LBERT_CTL`, `RX_LBERT_CTL`, and `RX_LBERT_ERR` provide loopback BERT control and error-count fields.

These macros are used by link bring-up, retraining, reset recovery, power-management transitions, and PHY diagnostic flows.

### RX Adaptation, Statistics, and Digital-to-Analog Controls

The RX adaptation and observability portion is dense:

- `LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0` through `ADPT_CFG_9` configure receiver adaptation loops, limits, calibration choices, thresholds, and selectors.
- `RST_ADPT_CFG` and status registers for attenuation, VGA, CTLE, and DFE taps expose reset/config bits and adaptation results.
- DFE/slicer offset families such as even/odd data/error/bypass VDAC offsets, `RX_SLICER_CTRL_*`, and `ERROR_SLICER_LEVEL` describe fine-grained receiver front-end tuning.
- `LANEX_DIG_RX_STAT_*` defines load values, data masks, match controls, statistic controls, sample counts, multiple statistic counters, and calibration/comparator clock controls.
- `LANEX_DIG_ANA_TX_*` and `LANEX_DIG_ANA_RX_*` fields bridge digital control to analog TX/RX blocks: TX output/termination/equalization override outputs, RX control/power/VCO override outputs, RX calibration, DAC controls/selectors, AFE attenuation/VGA/CTLE, scope/slicer controls, IQ phase/sense, and analog status.

These fields make receiver tuning and diagnostics visible to software and firmware, but they also directly affect link margin and signal integrity.

### Lane Analog TX/RX Measurement and Raw Common Memory

The later lane analog section describes analog measurement and override points:

- TX-side families such as `LANEX_ANA_TX_OVRD_MEAS`, `TX_PWR_OVRD`, `TX_ALT_BUS`, `TX_ATB1`, `TX_ATB2`, `TX_VBOOST`, `TX_TERM_CODE_DN`, `TX_TERM_CODE_UP`, `TX_IBOOST_CODE`, `TX_OVRD_CLK`, and `TX_MISC` cover TX power override, test-bus measurement selection, boost/current/termination coding, clock override, and miscellaneous analog controls.
- RX-side families such as `LANEX_ANA_RX_ATB_IQSKEW`, `RX_DCC_OVRD`, `RX_PWR_CTRL1`, `RX_ATB_REGREF`, `RX_CDR_AFE`, `RX_PWR_CTRL2`, `RX_MISC_OVRD`, `RX_CAL_MUXA/B`, `RX_ATB_MEAS1/2`, `RX_TERM`, `RX_SLC_CTRL`, and `RX_ATB_VREG` cover RX duty-cycle correction, power enables, regulator/reference controls, CDR AFE controls, loopback/DFE/deserializer power, calibration muxes, termination, slicer controls, and vreg measurement selection.
- `RAWCMNX_DIG_MEM_CMN2_B0_R0` through the beginning of `B3_R10` are raw common-memory registers. Each register has a single 16-bit `DATA` field (`DATA__SHIFT` at `0x0`, `DATA_MASK` normally `0xFFFFL`). These opaque table-like registers likely represent PHY micro-configuration or internal common-memory data rather than semantically named control fields.

## APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the generated macro namespace. Masks are untyped preprocessor integer constants, usually with an `L` suffix, and shifts are small integer constants.

The macros do not encode access permissions, side effects, reset domains, polling rules, write-one-to-clear semantics, timing requirements, or ownership between firmware and the kernel driver. Callers must combine these field constants with the matching offset/default headers and the ASIC programming model.

## Control Flow

This header has no local control flow. Runtime flow is external:

1. AMDGPU or firmware-facing code identifies an NBIO/SMN register offset from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`.
2. Code reads a register, composes a new value, or extracts a field using the `__SHIFT` and `_MASK` constants.
3. The value is written back through NBIO, SMN, PCIE, or SOC15 register helpers.
4. Hardware PHY state machines react by changing PLL, clock, reset, power, calibration, CDR, adaptation, loopback, statistic, or analog-test behavior.

Likely flows involving these fields include cold boot PHY initialization, PCIe link training/retraining, GPU reset recovery, suspend/resume register restore, dynamic PCIe power management, RTUNE calibration, RX equalization/adaptation, BERT diagnostics, and lab or manufacturing analog measurement.

## State and Persistence Behavior

The header itself stores no state. It names hardware-visible register fields whose persistence depends on GPU reset domains, NBIO/PHY resets, firmware initialization, driver save/restore logic, and explicit hardware writes.

Represented state includes MPLLB timing and calibration values, spread-spectrum clock parameters, analog MPLLA/MPLLB override state, RTUNE requests and measured/set values, TX/RX power-state policies, request/acknowledge handshakes, RX VCO calibration data, CDR/DPLL lock and frequency state, adaptation configuration/results, DFE/CTLE/VGA/attenuation/slicer values, BERT and statistic counters, analog test-bus mux selections, termination/vboost/iboost settings, RX/TX power controls, and opaque raw common-memory data.

Some fields are command-like or sampled/status-like rather than stable configuration. Reset, calibration, request, clear, counter, BERT, lock, adaptation status, override-enable, and test-bus selection fields need sequencing and timeout behavior from the owning code or hardware specification. Reserved and `NC*` fields should normally be preserved during read-modify-write unless the hardware programming guide says otherwise.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 6.1 header family:

- `nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide matching register addresses.
- `nbio_6_1_default.h` provides reset/default values for the same `DWC_E12MP_PHY_X4_NS_X4_3_*` names, including default MPLLB timing, `SUPX_ANA_MPLLA`, `LANEX_DIG_RX_ADPTCTL`, and `RAWCMNX_DIG_MEM_CMN2` values.
- AMDGPU register helpers rely on the exact `REGISTER, FIELD` naming convention used by `REG_SET_FIELD`, `REG_GET_FIELD`, and related macros.

Observed include-level integration in this source tree includes:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which includes `nbio_6_1_default.h`, `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` for NBIO 6.1 runtime programming.
- `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, which includes the NBIO 6.1 offset and shift/mask headers for SR-IOV/MxGPU paths.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`, which aggregate NBIO 6.1 generated headers into Vega power-management code.
- `drivers/gpu/drm/amd/amdgpu/psp_v3_1.c` and `drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`, which include related NBIO 6.1 generated register headers in PSP and display-resource integration.

Direct C references to this exact PHY-lane slice may be sparse because generated ASIC headers intentionally expose the complete hardware register database for firmware tables, bring-up, debug tooling, and hardware-specific paths that are not always present as named call sites.

## Risks and Edge Cases

- Generated-header drift can compile cleanly while assigning software to the wrong PHY bit. In this range that can break MPLLB timing, PLL stability, RX lock, adaptation, termination, or analog measurement behavior.
- The chunk starts at the tail of one register definition and ends before `RAWCMNX_DIG_MEM_CMN2_B3_R10__DATA_MASK`; adjacent chunks are required for complete source-file-level statements at both boundaries.
- Override-enable fields are high risk. Leaving a TX/RX/PLL/analog override asserted can bypass hardware state machines and produce unstable PCIe link behavior or misleading status.
- PLL, CDR, DPLL, VCO calibration, and spread-spectrum fields are timing-sensitive. Wrong masks may cause intermittent link failures, retraining loops, or board-specific instability rather than obvious boot failures.
- RTUNE, termination, vboost, iboost, VREF, slicer, CTLE, VGA, DFE, and ATB controls affect analog signal integrity directly.
- Status, counter, statistic, BERT, calibration, and adaptation fields may latch or clear through side effects not expressed in this header.
- Repeated `MPLLA`/`MPLLB`, TX/RX, P0/P0S/P1/P2, and `B*_R*` families are mechanically similar but not interchangeable.
- Raw common-memory `DATA` fields are opaque; treating them as ordinary semantic controls without matching offset/default/register-database context can corrupt PHY initialization tables.

## Test Signals

- Build AMDGPU configurations that include NBIO 6.1, Vega10/Vega12 PowerPlay, SR-IOV/MxGPU, PSP, and display-resource paths. This catches missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: shift/mask width validation, field non-overlap, reserved-bit coverage, address-to-field pairing, default-header alignment, and repeated-family checks for `NS_X4_3`.
- Cross-check `nbio_6_1_sh_mask.h` against `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h` for matching `DWC_E12MP_PHY_X4_NS_X4_3_SUPX`, `LANEX`, and `RAWCMNX_DIG_MEM_CMN2` names and ordering.
- On affected AMD GPUs, validate PCIe link bring-up, negotiated speed/width, retraining, warm reset, GPU reset, suspend/resume, and runtime power transitions through P0/P0S/P1/P2.
- Check PHY health signals where debug paths exist: MPLL lock/status, VCO calibration done/status, CDR/DPLL lock and frequency bounds, RTUNE status/set values, adaptation completion/status, BERT error counts, and statistic counters.
- Lab validation should cover analog-sensitive controls such as termination, VREF, vboost/iboost, CTLE/VGA/DFE/slicer settings, and ATB mux selection because bitfield errors may surface as marginal signal integrity.
- Regression tests for read-modify-write code should preserve reserved and `NC*` bits and should verify that temporary override-enable and measurement-selection bits are restored after diagnostics.

## Unresolved Cross-Chunk References

Line 123731 is already inside `DWC_E12MP_PHY_X4_NS_X4_3_SUPX_DIG_MPLLB_MPLL_PWR_CTL_PCLK_EN_AND_VCO_CLK_STABILIZATION_TIME_THRESHOLD`; the previous chunk is needed for that register's comment and shift fields. Line 126138 defines only `DWC_E12MP_PHY_X4_NS_X4_3_RAWCMNX_DIG_MEM_CMN2_B3_R10__DATA__SHIFT`; the matching `DATA_MASK` appears on line 126139 outside this work item. The merge lane should stitch those boundaries before making complete per-file claims about the `DWC_E12MP_PHY_X4_NS_X4_3` PHY block.
