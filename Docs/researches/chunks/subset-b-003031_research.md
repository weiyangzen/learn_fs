# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 64083-66436

## Scope

This chunk is a generated AMD NBIO 6.1 shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, allocations, locks, reference counts, or direct register accesses in this range.

The assigned range starts at the tail of `DWC_E12MP_PHY_X4_NS_X4_1_SUP_DIG_ANA_RX_TERM_OVRD_OUT`, then covers a large set of Synopsys/DWC E12MP PCIe PHY register fields for the `X4_NS_X4_1` PHY instance. The main content is supervisor-level MPLL/SSC/analog tuning metadata, lane 0 digital ASIC override and PHY control/status metadata, lane 0 TX/RX power/calibration/adaptation/analog metadata, and the beginning of lane 1 digital ASIC override metadata. The range ends partway through `DWC_E12MP_PHY_X4_NS_X4_1_LANE1_DIG_ASIC_RX_OVRD_IN_0`, so the lane 1 RX override register is incomplete in this chunk and continues in the following chunk.

Although this file is under a local `ceph-client` source mirror, this path is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and masks for NBIO 6.1 PCIe PHY registers. Each field is represented as a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to extract or compose the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or set the field.

Consumers combine these constants with register addresses from `nbio_6_1_offset.h` and reset/default values from `nbio_6_1_default.h`. Runtime code normally uses AMDGPU register helpers and field helpers such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`, depending on the target register aperture and call site.

For this chunk specifically, the macros describe low-level PCIe PHY programming surfaces: MPLL A/B calibration and power sequencing, spread-spectrum clocking, analog bypass/test-bus controls, resistor tuning, lane TX/RX override inputs and outputs, lane power-state parameters, RX VCO/CDR/adaptation state, statistics counters, analog TX/RX control handoff, and early lane 1 TX override fields.

## Important Macro Families

The opening supervisor digital analog status and MPLL sections cover `SUP_DIG_ANA_STAT`, `SUP_DIG_MPLLA_*`, and `SUP_DIG_MPLLB_*`. These fields expose MPLL calibration controls such as `LOAD_CNT`, `MPLL_SKIPCAL`, `MPLL_EXTCAL`, external check-frequency enable, external coarse tune, and external calibration done. The matching override/status fields expose override selection, feedback and pixel clock enables, fast power-up/lock controls, debug/test-bus selection, FSM state, too-slow indication, check-frequency completion, calibration-ready state, lane-side selection, output and feedback clock enables, reset, and analog enable.

The MPLL timing and tuning register families define VCO stabilization, MPLL calibration update timing, PCLK enable/disable timing, VCO power-down timing, analog power-up timing, feedback clock enable and digital feedback clock disable timing, coarse tune value, and skip-calibration coarse tune value. These are duplicated for MPLLA and MPLLB, with matching masks and field widths. The `SSC_SS_PHASE`, `SSC_SS_FREQ_0`, and `SSC_SS_FREQ_1` groups define spread-spectrum clocking phase, dithering, fractional divider, initial frequency count, peak frequency count, zero-frequency behavior, and override enables for both MPLLs.

The supervisor analog sections cover `SUP_ANA_MPLLA_*` and `SUP_ANA_MPLLB_*` metadata. `MISC` and `OVRD` fields describe MPLL bandwidth, divider clock selection, multiplier selection, SSC range, SSC enable, bandwidth override, multiplier override, refclk divider override, and PMA power-state selection. The `ATB1`, `ATB2`, and `ATB3` fields expose analog test-bus and measurement selections, including VCO signals, reference clock paths, bias/current monitor selections, and override gates.

The supervisor resistor and measurement sections include `SUP_ANA_RTUNE_CTRL`, `SUP_ANA_SWITCH_PWR_MEAS`, `SUP_ANA_SWITCH_MISC_MEAS`, `SUP_ANA_BG`, and `SUP_DIG_RTUNE_*`. These fields describe termination tuning power/reset/enable controls, resistor comparator enables, RTUNE ready and comparator result status, explicit RX/TX up/down set values, and measured RX/TX up/down status values. They also expose analog switch measurement selectors and bandgap/reference measurement controls.

The lane 0 digital ASIC override and ASIC input/output families cover `LANE0_DIG_ASIC_*`. Override input registers allow software or debug flows to force lane loopback, TX clock ready/reset/invert/data enable/request/low-power detect/pstate/rate/width/MPLLB selection/RX-detect request, TX boost and cursor settings, RX reset/invert/data enable/request/termination enable/electrical idle detect/rate/pstate/width/MPLLB selection/loss-of-signal threshold, RX CDR VCO configuration, equalization controls, and RX adaptation seed values. Output/status registers expose TX acknowledge, RX acknowledge, RX status, electrical-idle acknowledgement, termination acknowledgement, and RX status-valid style bits. The corresponding `*_ASIC_IN` groups define the non-override hardware inputs with the same logical lane-control vocabulary.

The lane 0 TX power-control sections cover `LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` plus TX power-up timing registers. These fields describe per-state TX request behavior, reset behavior, low-power detect, rate, width, MPLLB selection, RX-detect request, clock/data enables, boost levels, vboost enable, main/pre/post cursor values, and override enable bits. The timing registers define TX pstate transitions, reset/request delays, data enable timing, clock-ready timing, and related wait counts. `LANE0_DIG_TX_LBERT_CTL` provides loopback bit-error-rate test control.

The lane 0 RX power-control and calibration sections include `LANE0_DIG_RX_PWRCTL_RX_PSTATE_*`, RX power-up timing and control registers, `LANE0_DIG_RX_VCOCAL_*`, `LANE0_DIG_RX_CDR_*`, `LANE0_DIG_RX_DPLL_*`, and `LANE0_DIG_RX_LBERT_*`. These define RX pstate behavior, reset/request/data enable/termination/electrical-idle timing, calibration trigger/skip/external-calibration controls, VCO calibration thresholds and status, CDR proportional/integral controls and state, DPLL frequency bounds, XAUI alignment mask, and LBERT controls/error counters.

The lane 0 RX adaptation-control groups are a dense block of `LANE0_DIG_RX_ADPTCTL_*` fields. Configuration registers define adaptation mode enables, control-loop settings, timer thresholds, offset/update behavior, CTLE/VGA/attenuation/DFE knobs, and reset controls. Status registers expose attenuation, VGA, CTLE, DFE tap1 through tap5, adaptation done flags, data/error/bypass VDAC offsets, slicer controls, and error-slicer levels. These masks are central to any code that decodes or programs RX equalization and adaptation state.

The lane 0 RX statistic groups cover `LANE0_DIG_RX_STAT_*`. They define load values, data masks, match-control registers, statistic-control registers, sample-count control, statistic counters 0 through 6, calibration comparison clock control, and additional match/stat control registers. These fields are used for sampled status comparison and counter-based diagnostics rather than persistent software state.

The lane 0 digital-to-analog handoff and analog control sections cover `LANE0_DIG_ANA_*` and `LANE0_ANA_*`. Digital analog output registers expose TX override state, TX termination up/down override values, TX equalization overrides, RX control/power/VCO override outputs, RX calibration fields, DAC controls, AFE attenuation/VGA/CTLE fields, RX scope, slicer controls, IQ phase adjust, IQ sense enable, calibration DAC enable, signal-change enables, status bits, and analog status captures. The analog TX/RX registers define direct analog measurement and override fields for TX power, alternate bus, analog test bus, vboost, termination codes, iboost code, TX clock/misc settings, RX IQ skew, DCC override, RX power controls, ATB/regref measurement, CDR AFE, RX DFE/deserializer/loopback controls, LOS/LFPS and short-enable controls, calibration muxes, RX termination, slicer controls, and VREG/ATB measurement selections.

The final lane 1 section begins a second lane's digital ASIC override namespace. It includes lane-level loopback override, TX override input 0/1/2, and TX override output fields. The same TX concepts appear as lane 0: clock ready, reset, invert, data enable, request, LPD, pstate, rate, width, MPLLB select, detect-RX request, nyquist data, disable, beacon enable, iboost, vboost, main/pre/post cursor values, override enables, and TX acknowledge/RX-detect result. The chunk stops after the first fields of lane 1 RX override input 0.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is a macro namespace consumed by AMDGPU source files that include `nbio/nbio_6_1_sh_mask.h` or `asic_reg/nbio/nbio_6_1_sh_mask.h`.

Direct include sites for this NBIO 6.1 shift/mask header include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and PowerPlay aggregators such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. Related NBIO 6.1 offset headers are also included by PSP and display resource code. These include sites do not mean every PHY macro in this chunk is referenced directly; generated hardware headers intentionally expose a register database wider than any one driver path uses.

## Control Flow

There is no executable control flow in this header. Runtime behavior happens in including code:

1. Driver code selects a PHY register offset from `nbio_6_1_offset.h`.
2. It reads a hardware register through the AMDGPU register access layer.
3. It extracts fields with the corresponding `__SHIFT` and `_MASK` macros, often through a field helper.
4. It composes and writes a new control value, decodes status for diagnostics, waits on a hardware status bit, compares state against default expectations, or preserves reserved fields during read/modify/write.

For this range, likely runtime contexts are PCIe link bring-up, PHY clock/MPLL power sequencing, PLL calibration, spread-spectrum programming, lane power-state transitions, TX/RX reset sequencing, link training and equalization, RX CDR/VCO calibration, RX adaptation monitoring, analog debug/test-bus capture, termination tuning, loopback/BERT diagnostics, and multi-lane PHY setup.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes bit layout for hardware-backed state owned by the NBIO PCIe PHY, firmware-initialized defaults, platform policy, and AMDGPU runtime register programming.

The represented hardware state includes static reset/default values, software-programmed controls, hardware-updated status bits, calibration FSM state, timing thresholds, power-state programming, analog measurement selection, lane equalization/adaptation status, diagnostic counters, and direct analog/digital override latches. Some fields are intended as read-only status, some as writeable controls, some as override gates paired with override values, and some as debug-only measurement selectors. The masks do not encode reset defaults, access permissions, side effects, sequencing requirements, clock-domain constraints, polling timeouts, or reserved-bit preservation rules.

The paired `nbio_6_1_default.h` provides default values for the same register namespace. In this range, it defines defaults for MPLLA/MPLLB power-control, timing and SSC registers; supervisor analog and RTUNE registers; lane 0 ASIC override/ASIC input defaults; lane 0 TX/RX power-control, VCO calibration, CDR, DPLL, adaptation, statistics, digital analog and analog control defaults; and the beginning of lane 1 ASIC override defaults. The defaults include nonzero values for several MPLL timing registers, SSC frequency/phase settings, supervisor analog measurement controls, lane 0 TX/RX override defaults, RX adaptation configuration, slicer/VDAC offsets, and TX/RX analog code defaults. The shift/mask pairs in this chunk must stay synchronized with those defaults and with matching offsets.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` provides matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` provides reset/default values for the same register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` provides related NBIO SMN address definitions.
- AMDGPU register and field helper macros provide read/modify/write and field extraction mechanics.

Integration points include NBIO setup and query logic in `nbio_v6_1.c`, virtualization paths in `mxgpu_ai.c`, Vega10/Vega12 PowerPlay include users, PSP code that includes NBIO offsets for firmware/security flows, and display resource code that references NBIO offset state. Broader integration is with PCIe link initialization, SR-IOV/MxGPU virtualization, firmware PHY training, power management, runtime suspend/resume, link retraining, equalization, AER/link diagnostics, and board-specific signal-integrity tuning.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first two lines are the mask tail of the preceding supervisor RX termination override register, and the last line stops inside lane 1 `DIG_ASIC_RX_OVRD_IN_0`; a complete per-file view must merge adjacent chunks.
- The macros are untyped preprocessor constants. A wrong mask, stale shift, or lane/register-family mismatch can compile cleanly while manipulating the wrong hardware field.
- MPLLA and MPLLB blocks are structurally repetitive. Copy/generation drift can make one PLL differ subtly from the other even when names and masks appear parallel.
- Lane 0 and lane 1 override blocks are also repetitive. Applying a lane 0 mask to a lane 1 offset, or vice versa, can produce plausible bit arithmetic while targeting the wrong lane.
- Many registers contain override-enable bits paired with override values. Setting a value without its enable, or leaving an enable asserted after diagnostics, can produce silent PHY misconfiguration.
- Power sequencing and timing fields affect clocks, resets, VCO stabilization, PCLK enable/disable, analog power-up, and feedback clock behavior. Bad values can cause link training failures, timeouts, unstable clocks, or resume failures.
- RX adaptation and equalization fields are signal-integrity sensitive. Incorrect attenuation, VGA, CTLE, DFE, slicer, VDAC offset, or adaptation reset settings can degrade link margin without an obvious software fault.
- Status/counter fields can be transient or hardware-updated. Read/modify/write against a mixed control/status register can accidentally clear or corrupt live status if the access semantics are not known from the hardware spec.
- Reserved and `NC*` fields are explicitly masked in this header but do not describe safe write values. Driver code should preserve reserved bits unless the hardware programming guide says otherwise.
- Analog test-bus and measurement mux fields can disturb debug visibility or analog routing. They should be treated as board/ASIC-specific diagnostic surfaces rather than generic configuration knobs.
- Termination tuning and bandgap/reference controls can affect electrical compliance. Incorrect RTUNE, TX termination, RX termination, vboost, iboost, or reference override values may appear as link instability, marginal compliance, or platform-only failures.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware integration testing:

- Build AMDGPU with NBIO 6.1, Vega10/Vega12, MxGPU/SR-IOV, PowerPlay, PSP, and display paths enabled. Missing or renamed macros should surface at include users or register helper call sites.
- Compare this chunk against `nbio_6_1_offset.h` and `nbio_6_1_default.h` to confirm register names, ordering, defaults, lane transitions, and supervisor/lane block boundaries remain synchronized.
- On NBIO 6.1 hardware, verify PCIe link bring-up, retraining, suspend/resume, runtime power management, and speed/width negotiation while monitoring PHY lock, CDR/VCO calibration, lane status, and AER/link errors.
- Exercise PLL calibration and spread-spectrum settings under cold boot, warm reset, and resume paths; check for calibration-ready status, FSM progress, and absence of link-training regressions.
- Run lane loopback and LBERT diagnostics where available to validate TX/RX override, acknowledge, and error-counter fields.
- Stress RX equalization/adaptation under different link speeds and board conditions; inspect adaptation status, DFE tap status, CTLE/VGA/attenuation status, slicer/VDAC offsets, and statistic counters.
- Validate multi-lane behavior by comparing lane 0 and lane 1 programming paths; lane-specific offset/mask pairing errors should show up as asymmetric link stability or missing acknowledgements.
- For any generated-header update, run a scriptable consistency check that every `__SHIFT`/`_MASK` pair in this range has a matching register in the offset/default headers and that masks match the declared bit widths.

## Chunk Notes

- Lines 64083-64089 finish the preceding supervisor digital RX termination override output masks and define supervisor analog comparator status.
- Lines 64090-64321 cover MPLLA/MPLLB power-control, calibration, timing, coarse tune, and SSC phase/frequency fields.
- Lines 64322-64587 cover supervisor analog MPLL, RTUNE, measurement, bandgap, and digital RTUNE fields.
- Lines 64588-64911 cover lane 0 digital ASIC override, ASIC input/output, RX equalization override, and CDR VCO input/output fields.
- Lines 64912-65254 cover lane 0 TX/RX power-control, timing, VCO calibration, LBERT, CDR, and DPLL fields.
- Lines 65347-65576 cover lane 0 RX adaptation configuration and status fields.
- Lines 65577-65726 cover lane 0 RX statistic, match, sample, counter, and calibration comparison fields.
- Lines 65727-65991 cover lane 0 digital-to-analog TX/RX override, calibration, AFE, scope, slicer, signal-change, and analog status fields.
- Lines 65992-66358 cover lane 0 analog TX/RX measurement, power, termination, clock, CDR/AFE, calibration mux, slicer, and VREG fields.
- Lines 66359-66436 begin lane 1 digital ASIC lane/TX override fields and stop at the first lane 1 RX override input fields.
