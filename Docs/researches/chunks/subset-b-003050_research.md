# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 111294-113662

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,145 `#define` lines across 2,369 source lines: 1,070 `__SHIFT` constants, 1,081 `_MASK` constants, and 224 register comment markers. There are no C functions, structs, enums, global objects, allocations, locks, or executable statements in this range.

The range starts mid-register at the mask definitions for `DWC_E12MP_PHY_X4_NS_X4_3_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0S`, after its shift definitions and first masks were defined in the previous chunk. It then covers most of the remaining lane 1 PCIe PHY register bit layouts, including TX/RX power control, RX VCO calibration, CDR/DPLL, RX adaptation/status, diagnostics, digital-to-analog override/status, and analog TX/RX controls. The chunk then enters lane 2 and covers lane 2 ASIC override/input/output definitions, lane 2 TX/RX power control, VCO calibration, CDR/DPLL, and the beginning of lane 2 RX adaptation controls through `DWC_E12MP_PHY_X4_NS_X4_3_LANE2_DIG_RX_ADPTCTL_RX_SLICER_CTRL_EVEN`. The boundary is artificial: the previous chunk is needed for the beginning of lane 1 `TX_PSTATE_P0S`, and the next chunk is needed for the rest of lane 2 RX slicer/error/bypass/stat definitions.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of the generated NBIO 6.1 hardware register interface. Each field is represented by:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion generated headers provide the other pieces of the same hardware contract: `nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide addresses, while `nbio_6_1_default.h` provides default values for the same register names. Runtime AMDGPU code combines these macros with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE` to read, update, and write NBIO/PCIe registers.

This particular range documents the software-visible bit layout for Synopsys-style `DWC_E12MP_PHY_X4_NS_X4_3` PCIe PHY lanes. Lane 1 is represented from the tail of TX P0S power-state masks through analog RX termination/slicer/voltage-regulator controls. Lane 2 starts with ASIC-facing override and status fields, then repeats the same TX/RX power, calibration, CDR, and RX adaptation field families. These definitions are hardware metadata: they do not implement the PHY sequence, but they are the names and bit positions that any NBIO 6.1 lane bring-up, reset, diagnostics, or signal-integrity code must use.

## Important Macro Families

The lane 1 TX/RX power-control groups define the programmable lane state used around link training, low-power states, reset, and RX detect:

- `DWC_E12MP_PHY_X4_NS_X4_3_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0S`, `P1`, and `P2` define per-power-state TX enables for analog reference generation, VCM hold, analog clock, word clock, analog reset, serializer, digital clock, data enable, and RX-detect allowance. The `P0S` register is split by the chunk boundary, so only its final masks appear here.
- `DWC_E12MP_PHY_X4_NS_X4_3_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_3` define TX sequencing delays and options: reference-generator enable delay, clock-enable delay, VCM-hold time, VBOOST-disable time, RX-detect time, reset time, serial-enable time, fast RX detect, FIFO bypass, and debug/test-bus select.
- `DWC_E12MP_PHY_X4_NS_X4_3_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` define RX analog/digital enable bits for LOS, AFE, clock regulator, div16.5 clock, RX clock, DCC, deserializer, CDR, VCO reset/calibration, continuous calibration, and digital clock.
- `DWC_E12MP_PHY_X4_NS_X4_3_LANE1_DIG_RX_PWRCTL_RX_PWRUP_TIME_0` through `_2` and `RX_PWRUP_CTL_0` define RX power-up sequencing for reset, CDR enable, DFE enable, adaptation enable, data-valid timing, transition width, full-rate/half-rate behavior, and DCC control.

The lane 1 calibration, test, CDR, and DPLL groups expose the receiver's signal-recovery state:

- `DIG_TX_LBERT_CTL`, `DIG_RX_LBERT_CTL`, and `DIG_RX_LBERT_ERR` define loopback/bit-error-rate test modes, test patterns, error injection, and error-count fields.
- `DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0` through `_2`, `RX_VCO_CAL_TIME_0` and `_1`, and `RX_VCO_STAT_0` through `_2` define VCO calibration reference/code controls, skip flags, calibration timeouts, calibration done/fail status, and latched VCO results.
- `DIG_RX_RX_ALIGN_XAUI_COMM_MASK` provides byte/symbol mask controls for XAUI alignment.
- `DIG_RX_CDR_CDR_CTL_0` through `_4`, `DIG_RX_CDR_STAT`, `DIG_RX_DPLL_FREQ`, and `DIG_RX_DPLL_FREQ_BOUND_0`/`_1` define CDR rate selection, DPLL clock enables/resets, PI step configuration, lock status, center frequency, and high/low frequency bounds.

The lane 1 RX adaptation and diagnostics groups describe receiver equalization and measurement state:

- `DIG_RX_ADPTCTL_ADPT_CFG_0` through `_9` configure adaptation mode, CTLE/VGA/attenuator/DFE override and enable fields, training patterns, thresholds, loop gains, saturation behavior, DFE tap adaptation, and initial even/odd error-slicer settings.
- `DIG_RX_ADPTCTL_RST_ADPT_CFG` provides reset controls for adaptation sub-blocks: attenuator, VGA, CTLE boost, CTLE pole, and DFE tap 1.
- `DIG_RX_ADPTCTL_ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, and `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS` expose adapted equalizer values and `ASM1_DONE`/`ASM1_DON` completion bits.
- `DIG_RX_ADPTCTL_DFE_DATA_*_VDAC_OFST`, `RX_SLICER_CTRL_EVEN`, `RX_SLICER_CTRL_ODD`, `DFE_ERROR_*_VDAC_OFST`, `ERROR_SLICER_LEVEL`, and `DFE_BYPASS_*_VDAC_OFST` define data/error/bypass slicer offsets and slicer-level controls for even and odd paths.
- `DIG_RX_STAT_*` registers define diagnostic load values, data masks, match controls, statistic controls, sample count, statistic counters, calibration-comparator clock control, and extended match/stat controls.

The lane 1 digital-to-analog and analog groups bridge digital control to physical TX/RX blocks:

- `DIG_ANA_TX_OVRD_OUT`, `DIG_ANA_TX_TERM_UP_CODE_OVRD_OUT`, `DIG_ANA_TX_TERM_DN_CODE_OVRD_OUT`, and `DIG_ANA_TX_EQ_OVRD_OUT_0` through `_4` define TX analog override outputs for termination, pre/post cursor, main cursor, and related TX equalization/control values.
- `DIG_ANA_RX_CTL_OVRD_OUT`, `DIG_ANA_RX_PWR_OVRD_OUT`, `DIG_ANA_RX_VCO_OVRD_OUT_0`/`_1`, `DIG_ANA_RX_CAL`, `DIG_ANA_RX_DAC_CTRL`, `DIG_ANA_RX_DAC_CTRL_OVRD`, `DIG_ANA_RX_DAC_CTRL_SEL`, `DIG_ANA_RX_AFE_ATT_VGA`, `DIG_ANA_RX_AFE_CTLE`, `DIG_ANA_RX_SCOPE`, `DIG_ANA_RX_SLICER_CTRL`, IQ phase/sense/calibration enable registers, `DIG_ANA_STATUS_0`, and `DIG_ANA_STATUS_1` expose RX analog override, calibration, DAC, CTLE, scope, slicer, IQ, and status fields.
- `LANE1_ANA_TX_*` and `LANE1_ANA_RX_*` registers describe direct analog measurement, power override, alternate/test bus, VBOOST, termination code, iboost, override clock, TX misc, RX DCC override, RX power, CDR AFE, calibration muxes, RX termination, slicer, and voltage-regulator fields.

The lane 2 ASIC-facing groups start the next lane's repeated PHY register map:

- `DWC_E12MP_PHY_X4_NS_X4_3_LANE2_DIG_ASIC_LANE_OVRD_IN` controls lane-level override inputs such as PHY ready, TX/RX reset, pin selection, active logic, and idle data.
- `LANE2_DIG_ASIC_TX_OVRD_IN_0` through `_2` and `LANE2_DIG_ASIC_TX_OVRD_OUT` define TX override controls and resulting TX status/ack fields, including P-state, detect request, beacon, electrical idle, rate, deemphasis, margin, swing, termination offset, equalization coefficients, and TX-ready indication.
- `LANE2_DIG_ASIC_RX_OVRD_IN_0` through `_3`, `LANE2_DIG_ASIC_RX_OVRD_EQ_IN_0`/`_1`, and `LANE2_DIG_ASIC_RX_OVRD_OUT_0` define RX override controls for P-state, polarity, termination, LOS thresholds, RX valid, RX termination, LOS filtering, equalizer fields, and RX adaptation request/ack/status.
- `LANE2_DIG_ASIC_LANE_ASIC_IN`, `TX_ASIC_IN_*`, `TX_ASIC_OUT`, `RX_ASIC_IN_*`, `RX_EQ_ASIC_IN_*`, `RX_CDR_VCO_ASIC_IN_*`, `RX_ASIC_OUT_0`, and `RX_OVRD_EQ_IN_2`/`_3` define the non-override ASIC input/output bit layouts for lane 2, including TX/RX state, equalizer values, CDR/VCO load values, acknowledgements, LOS, RX valid, adaptation status, and DFE taps.

The lane 2 TX/RX power-control, calibration, CDR, and adaptation groups mirror lane 1:

- `LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` plus `TX_PWRUP_TIME_0` through `_3` define TX state enables and sequencing.
- `LANE2_DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` plus `RX_PWRUP_TIME_0` through `_2` and `RX_PWRUP_CTL_0` define RX state enables and sequencing.
- `LANE2_DIG_RX_VCOCAL_*`, `LANE2_DIG_RX_CDR_*`, `LANE2_DIG_RX_DPLL_FREQ*`, and `LANE2_DIG_RX_ADPTCTL_ADPT_CFG_0` through `_9` define the same VCO calibration, CDR/DPLL, and RX adaptation configuration fields for lane 2.
- The chunk ends after `LANE2_DIG_RX_ADPTCTL_RX_SLICER_CTRL_EVEN`, so lane 2 odd-slicer, error-slicer, bypass-slicer, and statistic definitions continue in the following chunk.

## APIs, Types, And Functions

There are no callable APIs or local C types in this range. The public interface is the generated macro namespace. Consumers depend on the exact register names, field names, shifts, and masks staying synchronized with the generated offset/default headers and the underlying hardware register database.

The constants are untyped preprocessor integer literals. Masks generally carry an `L` suffix and represent 16-bit or narrower field masks in these PHY registers, while shifts identify the least significant bit of the field. They encode field placement only. They do not encode read/write permissions, access width, reset domain, required delays, polling rules, side effects, firmware ownership, sticky behavior, or whether a field is live status, command, latched status, or reserved. Those semantics must come from the hardware specification and the AMDGPU call site that uses the field.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU or power-management code selects an NBIO/SMN/PCIe register address from generated address headers.
2. The code reads a register, decodes fields with these `__SHIFT`/`_MASK` constants, or composes a new value with register-field helpers.
3. The resulting value is written back to hardware, used to poll hardware status, or used as input to NBIO/PCIe/link/power-management policy.

Likely runtime flows involving these field families include PCIe PHY lane reset, lane bring-up, P-state transitions, RX detect, TX/RX clock and data enable sequencing, RX VCO calibration, CDR/DPLL lock, receiver adaptation, DFE/CTLE/VGA/attenuation tuning, signal-integrity diagnostics, LBERT test mode, statistics sampling, analog override/debug flows, and ASIC override handshakes.

## State And Persistence Behavior

The header stores no state. It names hardware-visible state in NBIO 6.1 PCIe PHY lane registers. Persistence is determined by GPU reset domains, NBIO/PCIe reset behavior, firmware or BIOS initialization, runtime power management, suspend/resume restore paths, SR-IOV PF/VF ownership, and explicit driver writes.

Represented state includes TX/RX per-P-state enable masks, TX/RX power-up timing, LBERT mode and counters, RX VCO calibration control/status, CDR and DPLL control/status, RX adaptation configuration and adapted values, DFE tap status, slicer offset/level controls, diagnostic statistic counters, digital-to-analog override values, direct analog measurement/control fields, and ASIC override/input/output handshake state.

Several fields are not passive storage. Reset, calibration, CDR/DPLL, adaptation, serializer, deserializer, data-enable, RX-detect, electrical-idle, and analog override bits can change live PHY behavior. Status and counter fields may be transient, latched, clear-on-read, or sampling-window dependent depending on the hardware. Reserved fields appear throughout these 16-bit register layouts and should generally be preserved with read-modify-write updates unless the hardware sequence explicitly requires a full literal write.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 6.1 register database and must stay aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` for matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` for SMN-addressed names where applicable.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` for reset/default values. The corresponding lane 1 and lane 2 defaults appear in the same generated PHY register region, including defaults for TX/RX power states, VCO/CDR/adaptation controls, slicer offsets, and analog controls.

Direct include users in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega power-management include bundles such as `pm/powerplay/hwmgr/vega10_inc.h` and `pm/powerplay/hwmgr/vega12_inc.h`. Those files include the NBIO 6.1 generated masks as part of a broader register-programming surface for NBIO revision detection, memory-controller access, doorbells, interrupts, PCIe/LTR/ASPM, clock gating, SR-IOV mailbox behavior, and Vega power-management flows.

Although this repository path is under a `ceph-client` mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem logic.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while causing software to program or decode the wrong PHY bit. In this chunk, the riskiest areas are power/reset sequencing, RX detect, CDR/DPLL, VCO calibration, adaptation, DFE/slicer controls, and analog override fields.
- The source range starts and ends mid-register-family. The beginning of lane 1 `TX_PSTATE_P0S` is in the previous chunk, and the rest of lane 2 RX slicer/error/bypass/stat definitions are in the next chunk.
- Lane 1 and lane 2 definitions are intentionally repetitive. Per-lane differences should be treated carefully: some are legitimate address/name changes, while a mismatched field width or mask pattern may indicate generator or register-database drift.
- Reserved fields cover large portions of many registers. Full-register writes risk clobbering reserved or firmware-owned bits unless the sequence is known to require them.
- Power-state, reset, serializer/deserializer, CDR, DFE, adaptation, and analog-control fields operate on live PCIe PHY state. Wrong values can cause link training failures, unstable retraining, intermittent lane errors, poor signal margin, failed resume, or hard-to-diagnose AER events.
- LBERT, statistic, and analog debug fields are useful for validation but can perturb normal traffic or signal quality if enabled on an active production link.
- ASIC override fields can bypass normal hardware or firmware control. Incorrect override-enable combinations can leave a lane stuck in reset, force bad TX/RX settings, hide true link status, or make lane failures look like board/cable/endpoint defects.

## Test Signals

- Build AMDGPU with NBIO 6.1/Vega support enabled. Direct macro users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset/default/shift/mask name alignment, mask-width checks, non-overlap checks within each register, and per-lane repetition checks for lanes 0 through 3.
- Validate chunk-boundary registers with adjacent chunks: lane 1 `TX_PSTATE_P0S` should have complete shift and mask definitions when the prior chunk is included, and lane 2 RX adaptation/slicer/stat definitions should continue cleanly in the next chunk.
- On NBIO 6.1/Vega hardware, boot and suspend/resume tests should show stable PCIe link training, expected negotiated width/speed, no unexpected AER storms, and no lane-related regressions.
- Power-management tests should cover ASPM/LTR, runtime suspend, system suspend, reset, and retraining paths while observing that TX/RX P-state transitions do not break link stability.
- PHY validation should exercise RX VCO calibration done/fail status, CDR/DPLL lock/frequency status, receiver adaptation status, DFE tap status, slicer offsets, and statistic counters against known-good hardware behavior.
- Lab-only diagnostics can use LBERT, RX statistic counters, and analog override/status fields to detect generator mistakes that normal boot paths may not touch.
- SR-IOV smoke tests should verify that NBIO 6.1 include users still build and that PF/VF mailbox and virtualization paths are unaffected by generated header changes.
