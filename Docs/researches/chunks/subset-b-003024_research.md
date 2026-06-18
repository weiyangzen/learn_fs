# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 46345-48856

## Scope

This chunk is a generated AMDGPU NBIO 6.1 shift/mask header segment. It contains 2,031 `#define` macros across 2,512 source lines: 1,012 `__SHIFT` constants, 1,022 `_MASK` constants, and 481 register comment markers. There are no C functions, structs, enums, global objects, locks, allocations, or executable statements in this range.

The range starts mid-register in `DWC_E12MP_PHY_X4_NS_X4_0_LANE3_DIG_ASIC_RX_ASIC_IN_1`, after its shift definitions and at the mask definitions for clock shift, disable, loss-of-signal threshold/filter, RX termination, and reserved bits. It then covers the rest of the lane 3 digital RX/TX/analog register bit layouts for the first `DWC_E12MP_PHY_X4_NS_X4_0` PCIe PHY instance, followed by a large generated block of raw common-memory data registers. The boundary is artificial: the previous chunk is needed for the beginning of `LANE3_DIG_ASIC_RX_ASIC_IN_1`, and this chunk ends at `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MEM_CMN3_B2_R14`, before the remaining CMN3 bank/register entries.

## Purpose

`nbio_6_1_sh_mask.h` is the bitfield half of the generated NBIO 6.1 hardware register interface. Each register field is represented by:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to compose or decode a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, or update that field.

The companion `nbio_6_1_offset.h` supplies the matching SMN/register addresses, and `nbio_6_1_default.h` supplies reset/default values for the same generated names. Runtime AMDGPU code includes these headers and uses register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, `WREG32_PCIE`, and `RREG32_PCIE` to program NBIO, PCIe, doorbell, interrupt, virtualization, and power-management behavior.

This specific chunk describes software-visible field layout for one PHY lane and common PHY memory area. The lane 3 definitions cover RX equalization, CDR/VCO loading, power-state sequencing, LBERT test controls, VCO calibration, receiver adaptation, diagnostic statistics, digital-to-analog override/status registers, and analog TX/RX controls. The RAWCMN definitions expose opaque 16-bit data payload fields for common-memory banks `CMN2` and the beginning of `CMN3`.

## Important Macro Families

The lane 3 digital ASIC RX macros define internal ASIC-facing controls and status:

- `DIG_ASIC_RX_EQ_ASIC_IN_0` and `_1` describe equalizer attenuation, VGA gains, CTLE boost/pole, and DFE tap 1 fields.
- `DIG_ASIC_RX_CDR_VCO_ASIC_IN_0` and `_1` expose CDR VCO low-frequency selection and reference/VCO load values.
- `DIG_ASIC_RX_ASIC_OUT_0` reports acknowledge, loss-of-signal, valid, and adaptation status bits.
- `DIG_ASIC_RX_OVRD_EQ_IN_2` and `_3` carry DFE tap 2 through tap 5 override fields.

The TX and RX power-control groups define lane power-state programming:

- `DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` provide per-state enables for analog reference generation, VCM hold, analog clock, word clock, analog reset, serializer, digital clock, data enable, and RX-detect allowance.
- `DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_3` define TX sequencing delays and behavior such as refgen enable time, clock enable time, VCM hold time, VBOOST disable time, RX-detect time, reset time, serial-enable time, fast RX-detect, FIFO bypass, and debug/test-bus selection.
- `DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` provide the analogous RX analog/digital enable, calibration, DFE, CDR, tracking, adaptation, and data-enable controls.
- `DIG_RX_PWRCTL_RX_PWRUP_TIME_0` through `_2` and `RX_PWRUP_CTL_0` define RX reset/CDR/DFE/adaptation/data-valid sequencing and power-up control bits.

The receiver calibration and link-test groups include:

- `DIG_TX_LBERT_CTL`, `DIG_RX_LBERT_CTL`, and `DIG_RX_LBERT_ERR` for lane bit-error-rate test mode, pattern, injected error, and error-count fields.
- `DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0` through `_2`, `RX_VCO_CAL_TIME_0` and `_1`, and `RX_VCO_STAT_0` through `_2` for RX VCO calibration code/load controls, current-reference tuning, skip flags, calibration timing, done/fail status, and latched calibration results.
- `DIG_RX_RX_ALIGN_XAUI_COMM_MASK` for XAUI alignment symbol masking.
- `DIG_RX_CDR_CDR_CTL_0` through `_4`, `DIG_RX_CDR_STAT`, `DIG_RX_DPLL_FREQ`, and `DIG_RX_DPLL_FREQ_BOUND_0`/`_1` for CDR rate selection, lock/step controls, DPLL center frequency, frequency bounds, and CDR/DPLL status.

The RX adaptation and diagnostic groups are the densest lane-specific portion:

- `DIG_RX_ADPTCTL_ADPT_CFG_0` through `_9` configure attenuation/VGA/CTLE/DFE adaptation enablement, adaptation mode, loop gains, thresholds, timers, reset behavior, and acquisition/tracking behavior.
- `DIG_RX_ADPTCTL_RST_ADPT_CFG` defines reset/clear controls for adaptation state.
- `DIG_RX_ADPTCTL_ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, and `DFE_TAP1_STATUS` through `DFE_TAP5_STATUS` expose adapted equalizer and DFE values.
- `DIG_RX_ADPTCTL_DFE_*_VDAC_OFST`, `RX_SLICER_CTRL_EVEN`, `RX_SLICER_CTRL_ODD`, and `ERROR_SLICER_LEVEL` define data/error/bypass slicer voltage DAC offsets and slicer thresholds for even/odd paths.
- `DIG_RX_STAT_*` registers define diagnostic compare/match masks, match controls, statistic controls, sample counts, statistic counters, calibration-comparator clock control, and extra match/stat controls.

The digital/analog override and analog measurement groups bridge lane digital control to physical analog blocks:

- `DIG_ANA_TX_OVRD_OUT`, TX termination override outputs, and `DIG_ANA_TX_EQ_OVRD_OUT_0` through `_4` describe digital override values for TX termination, pre/post cursor, main cursor, serializer/termination state, and TX equalization.
- `DIG_ANA_RX_CTL_OVRD_OUT`, `DIG_ANA_RX_PWR_OVRD_OUT`, `DIG_ANA_RX_VCO_OVRD_OUT_0`/`_1`, `DIG_ANA_RX_CAL`, `DIG_ANA_RX_DAC_CTRL`, `DIG_ANA_RX_AFE_ATT_VGA`, `DIG_ANA_RX_AFE_CTLE`, `DIG_ANA_RX_SCOPE`, `DIG_ANA_RX_SLICER_CTRL`, IQ phase/sense/calibration enable registers, and `DIG_ANA_STATUS_0`/`_1` describe RX analog override, calibration, slicer, CTLE, scope, DAC, IQ, and status fields.
- `LANE3_ANA_TX_*` and `LANE3_ANA_RX_*` registers define direct analog TX/RX measurement, power override, ATB, VBOOST, termination code, iboost, DCC, CDR AFE, calibration mux, RX termination, slicer, and voltage-regulator fields.

The final RAWCMN block consists of `DWC_E12MP_PHY_X4_NS_X4_0_RAWCMN_DIG_MEM_CMN2_B0_R0` through `CMN2_B7_R31` and `CMN3_B0_R0` through `CMN3_B2_R14`. Every one of these registers has a single `DATA` field at shift 0 with mask `0xFFFFL`, indicating an opaque 16-bit payload rather than named subfields. Their defaults in `nbio_6_1_default.h` contain nontrivial data values, so these entries likely represent generated PHY common-memory image words or microcode/configuration table contents.

## APIs, Types, And Functions

There are no callable APIs or local C types in this chunk. The public interface is the generated macro namespace. Consumers depend on the exact register names, field names, shifts, and masks remaining synchronized with the generated offset and default headers and with the hardware register database.

The constants are untyped preprocessor integer literals, usually with an `L` suffix for masks. They encode only bit placement. They do not encode register access width, reset value, read/write permission, side effects, required delays, polling rules, firmware ownership, or whether a field is live status, sticky status, one-shot command, or reserved. That behavior must come from the hardware specification and the AMDGPU call site.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU, Vega power-management, virtualization, or diagnostics code selects an NBIO/PCIe/SMN register offset from `nbio_6_1_offset.h` or `nbio_6_1_smn.h`.
2. The code reads a register value, decodes fields using the `__SHIFT` and `_MASK` constants, or composes a new value through `REG_SET_FIELD`.
3. The resulting value is written back to hardware or used to drive link, power, reset, interrupt, virtualization, or diagnostic policy.

Likely flows involving the field families in this chunk include PCIe PHY lane bring-up, per-lane TX/RX power-state transitions, RX VCO/CDR calibration, adaptation and equalization tuning, lane diagnostics, LBERT testing, analog override/debug flows, and loading or inspecting PHY common-memory image words.

## State And Persistence Behavior

The header stores no state. It names hardware-visible state in NBIO 6.1 PHY lane and common-memory registers. Persistence is determined by the GPU reset domain, PCIe/NBIO reset behavior, firmware initialization, power-management transitions, suspend/resume restore paths, SR-IOV PF/VF ownership, and explicit driver writes.

Represented state includes lane 3 RX equalization settings, DFE tap values, CDR/VCO load values, RX LOS and valid status, TX/RX power-state enable masks, sequencing timers, LBERT mode and counters, RX VCO calibration control/status, CDR/DPLL frequency and lock state, adaptation configuration and adapted status, diagnostic statistic counters, TX/RX analog override values, direct analog measurement controls, and raw common-memory data words.

Several fields are not passive storage. Power-state and reset bits can change the live PHY state; RX-detect, data enable, serializer enable, CDR, DFE, adaptation, and calibration controls interact with link bring-up; status fields may be transient or latched; diagnostic counters can depend on sampling windows; and RAWCMN `DATA` words may be part of a tightly ordered PHY configuration image. Reserved masks are present in many registers and should be preserved unless the hardware specification explicitly permits writes.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 6.1 register database and must stay aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` for register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` for reset/default values. The corresponding lane 3 defaults appear around the same generated block and include defaults for every lane 3 register family plus RAWCMN memory words.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` for SMN-addressed access where used.

Direct include users in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and Vega power-management include bundles such as `pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`. `nbio_v6_1.c` uses the generated NBIO field macros for NBIO revision, memory controller access, doorbell apertures/ranges, interrupt control, clock gating, PCIe/LTR/ASPM behavior, and related SOC15 register programming. `mxgpu_ai.c` includes the same generated NBIO macros for SR-IOV mailbox and VF/PF communication paths.

Although the repository path sits under a `ceph-client` mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem logic.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while causing software to program or decode the wrong hardware bit. In this chunk that is most dangerous for lane power/reset sequencing, CDR/VCO calibration, adaptation, DFE, RX/TX analog override, and RAWCMN memory image fields.
- The chunk boundaries split real register families. The first register is missing its shift definitions in this chunk, and the final RAWCMN CMN3 bank is incomplete without the next chunk.
- Repeated lane and memory-bank definitions are intentionally mechanical. A single mismatch in a repeated P-state, adaptation, DFE, status, or RAWCMN `DATA` pattern may indicate generator or register-database drift, but chunk truncation must be accounted for before treating it as a defect.
- Reserved fields occupy large parts of many 16-bit PHY registers. Callers should use read-modify-write helpers and preserve reserved bits unless the hardware sequence requires a full literal write.
- Power-state, reset, CDR, VCO, DFE, and adaptation fields interact with live PCIe PHY timing. Incorrect values can produce link training failures, intermittent lane errors, unstable retraining, or resume/reset races.
- LBERT and diagnostic statistic fields are useful for lab validation but can disturb normal traffic if enabled on an active lane.
- Analog override fields can bypass normal hardware/firmware control. Wrong override values can degrade signal integrity or make lane failures look like board, cable, or endpoint faults.
- RAWCMN `DATA` fields are opaque 16-bit words; generic bitfield helpers cannot infer their meaning. Writes should be treated as hardware-table programming and validated against the generated defaults or authoritative register source.

## Test Signals

- Build AMDGPU with NBIO 6.1/Vega support enabled. Direct macro users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 6.1 register database: offset/default/shift/mask name alignment, mask-width checks, non-overlap checks inside named registers, and per-lane repetition checks for lanes 0 through 3.
- Validate that every RAWCMN memory register in this chunk has exactly one `DATA` field at shift 0 and mask `0xFFFFL`, and that its default value exists in `nbio_6_1_default.h`.
- On affected Vega/NBIO 6.1 GPUs, boot and resume tests should show stable PCIe link training, correct negotiated width/speed, no unexpected AER storms, and no lane-related regressions.
- Power-management tests should cover ASPM/LTR and runtime/suspend/resume paths while observing that TX/RX lane power-state transitions do not break link stability.
- PHY diagnostic or lab validation should exercise LBERT, RX adaptation status, DFE tap status, CDR/DPLL status, VCO calibration done/fail bits, and statistic counters against known-good hardware behavior.
- SR-IOV smoke tests should verify that NBIO 6.1 include users still build and that mailbox/PF/VF communication is unaffected by generated header changes.
