# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 53444-55916

## Scope

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice for the `DPCSSYS_CR2` CR-indirect register namespace. It contains 2,113 `#define` constants across 361 register-field groups: 1,092 `*_SHIFT` constants and 1,021 `*_MASK` constants. The represented hardware is display PHY/DPCS lane-control metadata for CR2, starting in the final masks of `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_PCS_IN`, covering the remainder of RAWLANE3 PCS/PMA/FSM/IRQ/TX/RX controls, and then covering repeated always-on raw-lane definitions for `RAWAONLANE0`, `RAWAONLANE1`, and most of `RAWAONLANE2`.

The source file is declarative generated register metadata. It has no functions, structs, runtime branches, local storage, or include dependencies inside this chunk. The file-level guard and license live earlier in the header. The matching address/index data is provided by `dpcs_4_2_3_offset.h`, and DCN 3.1.6 resource code includes both files.

The chunk boundaries are artificial. The first lines are the mask half of `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_PCS_IN`; the corresponding shifts are immediately before this range. The range ends at the complete `DPCSSYS_CR2_RAWAONLANE2_DIG_SIGDET_OUT_OVRD` masks; subsequent `RAWAONLANE2` firmware, lane-mode, signal-detect configuration, TX DCC configuration, and `RAWAONLANE3` definitions continue after line 55916.

## Purpose

This header slice publishes symbolic bit positions and bit masks for 16-bit DPCS CR2 raw-lane and always-on lane registers. AMDGPU display code pairs these definitions with `ixDPCSSYS_CR2_*` offsets from `dpcs_4_2_3_offset.h` to form masked register values for indirect CR access. The macros let consumers avoid hard-coded bit numbers when programming link PHY controls, reading lane status, forcing overrides, clearing or masking IRQs, and inspecting calibration/adaptation results.

Although the path is under a local `ceph-client` mirror, this chunk is AMD display-driver hardware metadata, not Ceph filesystem code. Its behavior is entirely determined by generated constants, the display driver register helper layer, and the underlying DPCS/PHY hardware.

## Important Definitions

The macro interface follows the generated AMD register pattern:

- `DPCSSYS_CR2_<REGISTER>__<FIELD>__SHIFT`: low bit index for a hardware field.
- `DPCSSYS_CR2_<REGISTER>__<FIELD>_MASK`: bit mask for that field, usually covering a 16-bit register and using an `L` suffix.
- `RESERVED_*` fields: generated coverage for reserved bit ranges. They document layout but are not driver-owned feature bits.

Major RAWLANE3 groups in this chunk:

- PCS transmit and receive interface fields: `DIG_PCS_XF_TX_PCS_IN`, `TX_OVRD_OUT`, `TX_PCS_OUT`, `RX_OVRD_IN`, `RX_OVRD_IN_1` through `_3`, `RX_PCS_IN` through `_4`, `RX_OVRD_OUT`, `RX_PCS_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `LANE_NUMBER`, `ATE_OVRD_IN`, RX equalization override inputs, TX/RX termination controls, and RX phase-two calibration.
- FSM and calibration controls: `DIG_FSM_FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, many `FAST_RX_*` and `FAST_TX_*` single-bit fast-path controls, `CMNCAL_MPLL_STATUS`, `FAST_FLAGS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `OCLA`, `TX_EQ_UPDATE_FLAG`, `CMNCAL_RCAL_STATUS`, and `RX_IQ_PHASE_OFFSET`.
- IRQ controls: one-bit status and clear registers for RX reset/request/rate/P-state/adaptation, lane transceiver mode, RX phase-two calibration, serial loopback, DCC on-demand, TX reset, and TX request. `IRQ_MASK` and `IRQ_MASK_2` aggregate mask bits for these events.
- PMA cross-interface and analog-related fields: `PMA_XF_LANE_OVRD_IN/OUT`, supervisor PMA override/input, TX PMA input/override output, RX PMA input/override output, lane RTUNE control, MPHY override input/output, and RX adaptation override output.
- TX/RX control and ATE fields: `TX_CTL_*`, `RX_CTL_*`, `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `MASTER_MPLL_LOOP`, RX override output extensions, and the final `PCS_XF_TX_OVRD_IN_2` loopback/data override controls.

Major RAWAONLANE0/1/2 groups:

- RX adaptation readbacks and offsets: AFE attenuator/CTLE IDAC offsets, IQ adaptation, adaptation FOM, DFE summer/phase/data/bypass/error offsets, even/odd reference levels, phase-adjust linear/map values, MPLLA/MPLLB coarse tune, and `INIT_PWRUP_DONE`.
- Adaptation result fields: `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, `RX_ADPT_DFE_TAP1` through `TAP5`, `RX_ADAPT_DONE`, `RX_SLICER_CTRL_EVEN/ODD`, lane common-calibration MPLL/RCAL status, and `FAST_FLAGS`/`FAST_FLAGS_2`.
- Firmware and adaptation controls: `ADPT_CTL_0` through `ADPT_CTL_7`, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`.
- Power/PLL/DCC/signaling controls: `MPLL_DISABLE`, `TXRX_OVRD_IN`, `RX_LOS_MASK_CTL`, `RX_SIGDET_FILT_CTRL`, `STATS`, RX PMA override output banks, RX signal-detect calibration/code registers, RX VREF generator enable, generic calibration code registers, RX DCC calibration code registers, TX DCC bank address/data/continuous enable, `MPLL_BG_CTL`, signal-detect output override/input, lane transceiver mode override/input, and RX signal-detect filter configuration.

The always-on raw-lane definitions are almost copy-identical for lanes 0, 1, and 2 in this slice. That repetition is useful for generic lane programming, but the code still must use the correct lane-specific offset and mask namespace.

## Control Flow

There is no C control flow in this header. Its effective flow is compile-time macro substitution followed by runtime driver register access:

1. `dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`.
2. AMD display register-table macros or helper code select an `ixDPCSSYS_CR2_*` register index from the offset header.
3. The caller combines a value with this chunk's `*_SHIFT` and `*_MASK` constants, normally through read-modify-write helper logic.
4. The driver accesses the CR2 indirect register window for the relevant DPCS/PHY instance.
5. Hardware applies the value or returns status. Hardware FSMs then perform link, PLL, RX adaptation, DCC, signal-detect, interrupt, or debug behavior.

The field names expose hardware handshakes and state transitions even though this file does not implement them. Examples include PCS `REQ`/`ACK`, TX/RX reset/request/rate/P-state IRQ status and clear bits, RX adaptation request/ack/FOM, TX DCC flags/status, common calibration done/init flags, RX signal-detect calibration codes, and DCC bank address/data programming.

## State And Persistence

This chunk persists no software state and performs no I/O by itself. The state is hardware register state reached through the generated constants:

- Override registers are stateful until reset or later writes. Many use a value bit plus an `*_OVRD_EN` selector bit; both must be programmed coherently.
- RAWLANE3 PCS/PMA/FSM fields expose active link-control state such as TX/RX reset/request, P-state, rate, width, MPLL selection, loopback, data-enable, ATE overrides, PMA cross-interface signals, and lane-numbering.
- IRQ status, clear, and mask fields represent transient or sticky hardware events for lane reset/request/rate/P-state/adaptation, phase-two calibration, loopback, DCC on-demand, and TX events.
- Always-on raw-lane adaptation and calibration fields expose or control PHY training values: AFE, CTLE, VGA, DFE taps, IQ/phase adjustment, slicer control, FOM, signal-detect thresholds and codes, VREF generation, RX DCC calibration, TX DCC banks, common calibration, MPLL disable/coarse tune, and firmware calibration configuration.
- Reserved masks are layout information, not durable driver-owned state. Consumers should preserve reserved bits through read-modify-write unless the hardware programming sequence explicitly says otherwise.

Persistence duration is hardware-defined. These registers may retain values across ordinary modesets but can be reset by PHY reset, link reset, power gating, suspend/resume, or full ASIC reset. Status and clear registers may be read-only, sticky, self-clearing, or write-one-to-clear; this header does not encode those access semantics.

## Dependencies And Integration Points

The primary dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`, which supplies the matching CR2 `ixDPCSSYS_CR2_*` register indices. A shift/mask macro from this file is only meaningful when paired with the corresponding 4.2.3 register index.

The direct in-tree integration point is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both DPCS 4.2.3 generated headers. The broader consumers are AMD display core register abstractions, link encoder/resource tables, and PHY programming paths for DCN 3.1.6-class hardware.

Neighboring generated headers such as `dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_2_sh_mask.h`, `dcn_3_2_0_sh_mask.h`, and `dcn_4_1_0_sh_mask.h` contain similar PHY register families and are useful for generator drift checks. They are not interchangeable contracts: field width, reserved coverage, and lane/block availability can differ by ASIC/IP version.

## Risks

- Header/offset skew: using these 4.2.3 masks with a different DPCS offset header can compile while targeting the wrong bit fields or CR indices.
- Direct/indirect access confusion: `DPCSSYS_CR2_*` field masks belong with CR-indirect `ix...` offsets, not direct MMIO `reg...` offsets.
- Reserved-bit writes: generated `RESERVED_*_MASK` constants make reserved regions visible. Whole-register writes that do not preserve reserved bits can disturb undocumented PHY behavior.
- Override-pair hazards: value/enable pairs such as `*_OVRD_VAL` plus `*_OVRD_EN` must be updated consistently. Enabling an override with a stale value can force bad link state, loopback, signal detect, termination, or data enable.
- Lane-copy assumptions: RAWAONLANE0/1/2 are highly repetitive, but the requested range stops before the full RAWAONLANE2 trailer and before RAWAONLANE3. Generic code must bind actual lane offsets and not infer complete availability from this partial chunk.
- Interrupt semantics are not typed. Status, clear, and mask registers are separate generated fields, but the header does not prevent writing a status bit as though it were a clear bit, or masking an event needed for link recovery.
- Value-width overflow: callers must clamp values to `FIELD_MASK >> FIELD_SHIFT` before shifting; the preprocessor constants cannot enforce this.
- Debug/test controls such as ATE, OCLA, loopback, DCC, and firmware calibration fields can make hardware appear functional in one diagnostic mode while breaking normal link training if left enabled.

## Test Signals

Useful validation signals for changes or generated-header refreshes involving this chunk:

- Build coverage for `dcn316_resource.c` and AMDGPU display code that instantiates DCN 3.1.6 register tables, proving expected macro names still exist.
- Static generation checks pairing each `DPCSSYS_CR2_RAWLANE3_*` and `DPCSSYS_CR2_RAWAONLANE[0-2]_*` field group with a matching `ixDPCSSYS_CR2_*` entry in `dpcs_4_2_3_offset.h`.
- Cross-version diffs against AMD's authoritative generated DPCS 4.2.3 register source and nearby 4.2.x headers, focusing on lane repetition, reserved masks, multi-bit field widths, and chunk-boundary registers.
- Runtime DCN 3.1.6 hardware tests for DisplayPort link training across rates and lane counts, hotplug, suspend/resume, DP alternate mode if present, and recovery after link failure.
- PHY diagnostics watching RX adaptation FOM/done values, DFE/CTLE/VGA/tap results, MPLL and common calibration status, signal-detect calibration outputs, DCC bank programming, TX/RX acknowledge bits, and IRQ status/clear behavior.
- Regression symptoms to watch: lane-specific link failures, rate-specific instability, HPD/link-training storms, RX-detect failures, stuck IRQs, black screens after power-state transitions, and display resume failures.

## Cross-Chunk Notes

The full-file reconciliation lane should merge this report with adjacent chunks before making file-level claims. The preceding chunk contains the first half of `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_PCS_IN`; the following chunk contains the remaining `DPCSSYS_CR2_RAWAONLANE2_*` definitions and starts/continues `DPCSSYS_CR2_RAWAONLANE3_*`. This report intentionally documents only lines 53444-55916 and does not create the final per-file report.
