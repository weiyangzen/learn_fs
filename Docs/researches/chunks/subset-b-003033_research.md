# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 68801-71176

## Scope

This chunk is a generated AMD NBIO 6.1 shift/mask header segment for the Synopsys DWC E12MP x4 PCIe PHY instance `DWC_E12MP_PHY_X4_NS_X4_1`. It contains C preprocessor constants only. There are no functions, structs, variables, branches, loops, allocations, locks, register reads, or register writes in this range.

The assigned lines begin at the final mask for `LANE2_DIG_RX_RX_ALIGN_XAUI_COMM_MASK`, then cover the rest of the lane 2 receive, statistic, digital-analog bridge, and analog PHY bitfields. The chunk then begins lane 3 and covers its ASIC interface, TX/RX power-control, RX VCO calibration, CDR, DPLL, receiver adaptation, statistics, and digital analog override bitfields. The range ends inside `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_1`, before the masks for that register and before the following `LANE3_DIG_ANA_RX_CAL` block.

Although this file lives under a local `ceph-client` source mirror, the content in this range is AMDGPU hardware register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and masks for NBIO 6.1 PHY lane registers. Each hardware field is represented by generated macro pairs:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when extracting or composing the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or set the field.

Runtime code pairs these macros with matching address definitions and reset/default definitions from the NBIO 6.1 register set. The same register names have corresponding defaults in `nbio_6_1_default.h` under `smnDWC_E12MP_PHY_X4_NS_X4_1_*_DEFAULT`; for this slice, those defaults include nonzero values for RX CDR tuning, DPLL bounds, adaptation thresholds and gains, RX statistic setup, TX/RX power-state timing, and several analog calibration or termination values.

Consumers normally use these constants through AMDGPU register helpers and field helpers such as `RREG32`, `WREG32`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, `REG_SET_FIELD`, and related NBIO/SMN access wrappers, depending on the register aperture and call site.

## Important Macro Families

The first line finishes the lane 2 XAUI comma alignment mask register. The immediately preceding chunk owns the full register header and earlier fields; this chunk contains only `RESERVED_15_10_MASK` for `LANE2_DIG_RX_RX_ALIGN_XAUI_COMM_MASK`.

The lane 2 RX digital block starts with LBERT receive controls and error counting. `DIG_RX_LBERT_CTL` exposes loopback bit-error-test mode and sync fields, while `DIG_RX_LBERT_ERR` exposes the error counter and overflow bit. These are useful for PHY diagnostics and low-level link validation rather than ordinary filesystem or block I/O logic.

The lane 2 CDR and DPLL blocks define clock/data recovery tuning and status fields. `DIG_RX_CDR_CDR_CTL_0` covers phase detector enable/edge/polarity, realign policy, and debug/test-bus selection. `CDR_CTL_1` through `CDR_CTL_4` define spread-spectrum clocking on/off counters and proportional/frequency gain controls. `CDR_STAT`, `DPLL_FREQ`, and `DPLL_FREQ_BOUND_0/1` expose current gain/frequency information and upper/lower frequency-bound programming.

The lane 2 receiver adaptation controller block is a large group of `DIG_RX_ADPTCTL_*` fields. `ADPT_CFG_0` through `ADPT_CFG_9` define adaptation machine timing, training patterns, CTLE/VGA/ATT/DFE enablement, thresholds, adaptation step sizes, saturation behavior, DFE tap gains, and adaptation clock behavior. `RST_ADPT_CFG` controls which adaptation sub-blocks reset. Status registers report ATT, VGA, CTLE, and DFE tap values. Additional fields define DFE data/error/bypass VDAC offsets, even/odd slicer controls, and error slicer level. These fields describe receiver equalization state used to train and maintain PCIe signal quality.

The lane 2 RX statistics block defines pattern matching and sample/counter controls. `STAT_LD_VAL_1`, `STAT_DATA_MSK`, `MATCH_CTL0/1/2/3/4/5`, `STAT_CTL0/1/2`, `SMPL_CNT1`, `STAT_CNT_0` through `STAT_CNT_6`, and `CAL_COMP_CLK_CTL` expose pattern masks, data masks, sample count setup, statistic counter enables, done bits, data-delay selections, clock selection, valid-loss clearing, skip behavior, and calibration comparator clock timing.

The lane 2 digital analog bridge block exposes TX/RX override outputs and analog status. TX-side fields include `DIG_ANA_TX_OVRD_OUT`, TX termination up/down override outputs, and TX equalization override output registers that split attenuation and pre/post cursor controls across multiple 16-bit fields. RX-side fields include RX control, power, VCO, calibration, DAC, AFE ATT/VGA, CTLE, scope, slicer, IQ phase/sense, calibration DAC enable, signal-change enable, and analog status fields.

The lane 2 analog lane block covers lower-level analog PHY controls outside the `DIG_ANA_*` namespace. TX fields include override measurement, power override, alternate bus, ATB measurement, VBOOST, termination codes, IBOOST, override clocks, and misc oscillator/RX-detect controls. RX fields include ATB/IQ skew, DCC override, power controls, register-reference measurement, CDR/AFE measurement and phase-detector settings, calibration muxes, termination, slicer controls, and ATB/VREG measurement fields.

The lane 3 portion starts with ASIC-facing override and status registers. `DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0/1/2`, `DIG_ASIC_TX_OVRD_OUT`, `DIG_ASIC_RX_OVRD_IN_0/1/2/3`, and `DIG_ASIC_RX_OVRD_EQ_IN_0/1/2/3` define lane loopback, TX/RX reset, inversion, data enable, request, low-power, pstate/rate/width, PLL selection, detect-RX request, TX cursor override, RX reference/VCO load values, CDR tracking/SSC/alignment, LOS threshold, termination, and EQ override fields. Matching `DIG_ASIC_*_ASIC_IN` and `*_ASIC_OUT` registers expose the non-override ASIC input/output view for the same lane.

The lane 3 TX and RX power-control blocks define power states and timing. `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2` and `DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1/P2` describe per-state power behavior. `TX_PWRUP_TIME_0` through `TX_PWRUP_TIME_3`, `RX_PWRUP_TIME_0` through `RX_PWRUP_TIME_2`, and `RX_PWRUP_CTL_0` define reset, refgen, clock, data, serial, detect, AFE, CDR, deserializer, and wait/timeout timing.

The lane 3 RX VCO calibration and RX digital blocks mirror lane 2. `DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0/1/2`, `CAL_TIME_0/1`, and `STAT_0/1/2` define RX VCO startup, update, counter, tuning, continuous calibration, reset, done, too-fast, correct, and up/down status fields. The subsequent lane 3 RX align, LBERT, CDR, DPLL, adaptation, and statistics families repeat the lane 2 field layout under lane 3 names, giving each physical lane an independent macro namespace.

The final complete register in this chunk is `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_0`, covering RX analog CDR VCO enable/startup, CDR override enable, frequency tune, VCO counter enable/clock, and CDR frequency-tune override enable. The range then includes only the `__SHIFT` macros for `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_1` fields `RX_ANA_CDR_VCO_LOWFREQ`, `RX_ANA_VCO_CNTR_PD`, and `RESERVED_15_2`; the corresponding masks are in the next chunk.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is the macro namespace in `nbio_6_1_sh_mask.h`.

Direct include sites for this header include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`
- `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_inc.h`

Those include sites do not mean every macro in this chunk is directly referenced by hand-written code. AMD hardware register headers intentionally expose a broader generated register database than any one driver path consumes.

## Control Flow

There is no executable control flow in this header. Runtime control flow happens in code that includes the generated register metadata:

1. Driver code identifies the target NBIO/PHY register for a concrete lane and hardware instance.
2. It reads the register through the AMDGPU MMIO, SMN, or SOC15 register access layer.
3. It extracts fields using the relevant `__SHIFT` and `_MASK` macros, often through generic field-helper macros.
4. It composes new field values and writes the register back, or uses status fields for diagnostics, link training, power sequencing, or hardware validation.

For this range, likely runtime contexts are PCIe PHY lane bring-up, link training, clock/data recovery setup, DPLL/VCO calibration, TX/RX power sequencing, PHY loopback and LBERT diagnostics, RX equalization adaptation, analog override/debug paths, link statistic collection, and GPU virtualization or low-level service flows that need per-lane PHY control.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes bit layouts for hardware-backed state owned by the NBIO 6.1 PHY, firmware, platform initialization, and AMDGPU runtime code.

The represented state includes:

- Lane alignment and LBERT diagnostic state.
- RX CDR, DPLL, VCO calibration, and frequency-bound control/status.
- RX adaptation controller state for CTLE, VGA, ATT, DFE taps, slicers, and VDAC offsets.
- RX statistic pattern matchers, sample counters, and statistic counters.
- Digital analog override outputs and analog status fields.
- Low-level analog TX/RX calibration, termination, measurement, power, and clock controls.
- Lane 3 ASIC override and non-override interface fields.
- Lane 3 TX/RX power-state and power-up timing state.

Some fields are controls that software or firmware can program. Some are hardware-updated status or counters. Some are diagnostic or override fields that should normally stay at generated defaults unless a bring-up, validation, or workaround path intentionally changes them. The masks do not encode reset defaults, access permissions, side effects, timing requirements, write-one-to-clear behavior, lock requirements, or ordering constraints. Those properties must come from the hardware specification, firmware contract, matching default header, and driver code.

## Dependencies And Integration Points

The primary dependency is consistency across the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h` provides the field shifts and masks in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides matching `smnDWC_E12MP_PHY_X4_NS_X4_1_*_DEFAULT` values for the same lane/register families.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` and related NBIO address headers provide the register address side of the same generated database.
- AMDGPU register helper macros provide typed-enough read/modify/write and field extraction mechanics around these untyped preprocessor constants.

Integration points are AMDGPU NBIO initialization and query code, MxGPU virtualization paths, Vega power-management include bundles, low-level PCIe link bring-up and retraining, PHY diagnostics, firmware-controlled PHY initialization, suspend/resume and runtime power transitions, and any board/ASIC workaround path that touches NBIO 6.1 PHY lane state.

The repeated lane naming is itself an integration contract. Lane 2 and lane 3 use nearly identical field layouts but different macro prefixes. Call sites and generated tables must pair a lane's register offset with the same lane's masks; mixing lane 2 masks with lane 3 offsets may compile and even produce plausible bit arithmetic while targeting the wrong hardware lane.

## Risks And Edge Cases

- Chunk boundaries are artificial. Line 68801 is only the tail mask of a register that starts in the previous chunk, and line 71176 stops before the masks for `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_1`.
- The macros are untyped preprocessor constants. A stale mask, wrong shift, or copied lane prefix can compile cleanly but corrupt PHY programming.
- Most registers in this slice are 16-bit field maps expressed as `L` constants. Wider call sites must preserve unrelated high bits and reserved bits when performing read/modify/write sequences.
- Reserved masks are numerous. Software should avoid using reserved fields as writable payload unless an explicit hardware workaround requires it.
- CDR, DPLL, VCO, frequency-bound, and calibration fields are timing-sensitive. Incorrect settings can prevent lane lock, create intermittent link instability, or break retraining after power transitions.
- RX adaptation and DFE/slicer fields are signal-integrity-sensitive. Wrong thresholds, gains, offsets, or enable bits can degrade margin in ways that only appear under high link speed, temperature, voltage, board-loss, or spread-spectrum conditions.
- Power-state and power-up timing masks must remain aligned with firmware and hardware expectations. Bad timing can cause suspend/resume, runtime power management, reset, or low-power-state failures.
- TX/RX analog override fields can bypass normal hardware/firmware control. Accidentally enabling overrides, termination changes, VBOOST/IBOOST changes, or TX equalization overrides can produce link compliance and reliability issues.
- LBERT, statistic, ATB, and measurement fields are diagnostic controls. Test or debug code must restore production defaults after use, especially on shared hardware or virtualization paths.
- Lane 3 begins mid-file after lane 2 analog fields. Adjacent chunks must be merged to understand the complete lane 3 analog block and the complete `DWC_E12MP_PHY_X4_NS_X4_1` PHY instance.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware or platform integration testing:

- Build AMDGPU with NBIO 6.1, Vega10/Vega12, and MxGPU-relevant options enabled. Missing, renamed, or malformed macros should surface in include users or register helper call sites.
- Cross-check this chunk against `nbio_6_1_default.h` for matching `smnDWC_E12MP_PHY_X4_NS_X4_1_LANE2_*` and `LANE3_*` default names and against offset/address headers for matching register names and lane ordering.
- Run generated-register consistency checks to confirm every field mask is aligned with its shift, reserved masks cover only intended unused bits, and duplicate lane layouts stay synchronized where the hardware design expects them to match.
- On NBIO 6.1 hardware, validate PCIe link bring-up, retraining, speed/width negotiation, and error-free traffic across all physical lanes, with attention to lanes 2 and 3.
- Exercise suspend/resume, runtime power management, GPU reset, and low-power transitions while watching TX/RX power-state and power-up timing behavior.
- Run high-throughput PCIe traffic, error monitoring, and stress tests under multiple link speeds to catch CDR, DPLL, VCO, adaptation, and analog override regressions.
- Use PHY diagnostics where available: LBERT, loopback, RX statistic counters, ATB measurement, scope/slicer controls, and calibration-status reads should behave consistently with documented defaults and expected status transitions.
- Test SR-IOV/MxGPU or firmware-assisted paths on hardware that uses this NBIO generation, since virtualization and firmware flows may rely on generated lane metadata indirectly.

## Chunk Notes

- Lines 68801-68801 contain only `LANE2_DIG_RX_RX_ALIGN_XAUI_COMM_MASK__RESERVED_15_10_MASK`; the rest of that register is above this chunk.
- Lines 68802-69898 cover lane 2 LBERT, CDR/DPLL, adaptation, statistic, digital analog, and analog TX/RX field definitions.
- Lines 69901-71172 cover lane 3 ASIC, TX/RX power-control, RX VCO calibration, RX align/LBERT/CDR/DPLL/adaptation/statistic, TX analog override, and RX analog override fields through `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_0`.
- Lines 71173-71176 begin `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_1` with shift definitions only; the masks and following lane 3 analog RX calibration fields are in the next chunk.
