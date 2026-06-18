# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h - subset-b-002344

## Scope

This chunk covers lines 16697-19117 of the generated AMD DPCS 4.2.2 shift/mask header. It is a compile-time register-field map, not executable driver logic. The visible content begins in the tail of the `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_TX_OVRD_IN_2` mask block, then defines the full `DPCSSYS_CR0_RAWLANE3_*` digital lane 3 PCS/FSM/IRQ/PMA/TX/RX field masks, and ends after the `DPCSSYS_CR0_RAWAONLANE2_DIG_FAST_FLAGS_2` block with the next `RAWAONLANE2_DIG_LANE_CMNCAL_RCAL_STATUS` register header starting at the boundary.

## Purpose

The header exposes symbolic `__SHIFT` and `_MASK` constants for DPCS CR0 lane registers. Consumers combine these constants with matching register offsets from the DPCS offset headers and AMD register access helpers to read, modify, or decode packed hardware registers without hard-coded bit numbers.

Within this chunk, the purpose is mainly lane bring-up, training, override, interrupt, and status support:

- `RAWLANE3_DIG_PCS_XF_*` describes PCS-facing TX/RX request, reset, power-state, link-rate, width, MPLL, loopback, adaptation, equalization, ATE, and RX validity controls for raw lane 3.
- `RAWLANE3_DIG_FSM_*` describes the lane finite-state-machine control, status, fast-calibration shortcut flags, command lock/status, OCLA/debug, TX DCC, common calibration, and RX IQ phase status fields.
- `RAWLANE3_DIG_IRQ_CTL_*` maps lane 3 interrupt status, clear, and mask bits for RX/TX reset/request, rate/pstate/adaptation transitions, lane transceiver mode, phase-2 calibration, loopback, and DCC on-demand events.
- `RAWLANE3_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` define the PMA interface, test/override outputs, lane/supervisor power and clocking signals, TX/RX control FSM knobs, data-enable/LOS timing, and OCLA visibility.
- `RAWAONLANE0/1/2_DIG_*` defines always-on lane analog/training status and calibration data: AFE/DFE offsets, adaptation result values, coarse MPLL tune, power-up done, fast flags, common-calibration status, disable bits, signal-detect data, DCC calibration data, firmware config bits, and lane transceiver mode.

## Important Constants And Register Families

The file has no C types, functions, structs, enums, or callable APIs in this range. Its public API is the generated macro namespace. Each register appears as a comment marker followed by one or more `REGISTER__FIELD__SHIFT` constants and matching `REGISTER__FIELD_MASK` constants. Most registers are 16-bit logical fields represented in 32-bit C constants with an `L` suffix.

Key lane 3 PCS register families:

- TX inputs and override inputs: `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`, `_IN_1`, `_IN_2`, and `TX_PCS_IN` map reset/request, `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, master MPLL override states, TX async/data enables, TX beacon, detect-RX request, voltage/current boost, and TX-to-RX serial loopback fields.
- TX outputs: `TX_OVRD_OUT` and `TX_PCS_OUT` expose acknowledge, detect-RX result, enable control, and TX dword clock sync override/status bits.
- RX inputs and override inputs: `RX_OVRD_IN`, `_IN_1`, `_IN_2`, `_IN_3`, `RX_PCS_IN`, and `_IN_1` through `_IN_4` cover request, rate, width, power state, low-power disable, CDR/VCO/ref load values, AFE/DFE adaptation enables, LOS threshold, continuous adaptation/off-cancellation controls, RX data enable, RX clock enable, phase-2 calibration request, and RX-to-TX loopback fields.
- RX outputs and adaptation status: `RX_OVRD_OUT`, `RX_OVRD_OUT_1`, `RX_OVRD_OUT_2`, `RX_PCS_OUT`, `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, and `RX_TXPOST_DIR` expose ack/data-valid/adaptation result values and transmitter equalization direction hints derived from RX adaptation.
- Equalization/test controls: `RX_EQ_DELTA_IQ_OVRD_IN`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, `TXRX_TERM_CTRL_OVRD_IN`, `TXRX_TERM_CTRL_IN`, `RX_PH2_CAL`, `ATE_OVRD_IN`, `ATE_RX_OVRD_IN*`, `ATE_TX_OVRD_IN*`, and `MASTER_MPLL_LOOP` map explicit override/test paths for ATE and diagnostics.

Key lane 3 control/status families:

- `DPCSSYS_CR0_RAWLANE3_DIG_FSM_FSM_OVRD_CTL` provides FSM jump address, jump enable, command start, override enable, and break bits. `FSM_MEM_ADDR_MON` and `FSM_STATUS_MON` expose FSM memory address and state/ALU/wait/mask status.
- Per-feature fast-path registers such as `FSM_FAST_RX_STARTUP_CAL`, `FSM_FAST_RX_ADAPT`, `FSM_FAST_RX_AFE_CAL`, `FSM_FAST_RX_DFE_CAL`, `FSM_FAST_SUP`, `FSM_FAST_TX_RXDET`, `FSM_FAST_RX_PWRUP`, and `FSM_FAST_RX_VCO_CAL` each carry a one-bit fast mode plus reserved bits. `FSM_FAST_FLAGS` packs the same family into a consolidated bitfield.
- `FSM_CMNCAL_MPLL_STATUS` and `FSM_CMNCAL_RCAL_STATUS` expose common-calibration init/done bits. `FSM_CR_LOCK`, `FSM_TX_DCC_FLAGS`, `FSM_TX_DCC_STATUS`, `FSM_TX_EQ_UPDATE_FLAG`, `FSM_RX_IQ_PHASE_OFFSET`, and `FSM_OCLA` cover command-register lock/debug, TX DCC calibration, TX equalization update, RX IQ phase, and observation/debug latching.
- `IRQ_CTL_*` registers are split into event status, event clear, and masks. `IRQ_MASK` packs RX reset/req/rate/pstate/adapt, return reset request, TX reset/req, lane mode, phase-2 calibration, loopback, and DCC events; `IRQ_MASK_2` covers additional TX reset/request mask bits.
- `PMA_XF_*` registers bridge PCS-side control to the PMA: lane/supervisor override inputs and outputs, TX/RX PMA inputs, MPHY override input/output, lane RTUNE, and RX adaptation override output.
- `TX_CTL_*` and `RX_CTL_*` define lane-local controller policy and debug fields such as TX/RX FSM enables, rate-change behavior, TX clock enable mode, TX DCC continuous status, LOS mask count, RX data enable override count, internal reference tracking count, off-cancellation/adaptation continuous status, and UPCS/OCLA data/clock enables.

Key always-on lane families:

- Lanes 0 and 1 are represented with complete repeated `DPCSSYS_CR0_RAWAONLANE{0,1}_DIG_*` blocks in this chunk. Lane 2 begins at `AFE_ATT_IDAC_OFST` and continues through `FAST_FLAGS_2`; the `LANE_CMNCAL_RCAL_STATUS` block begins but is completed by the next chunk.
- Analog/adaptation result registers include `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, `DFE_*_VDAC_OFST`, `DFE_*_REF_LVL`, `RX_PHSADJ_LIN`, `RX_PHSADJ_MAP`, `RX_IQ_PHASE_ADJUST`, `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, `RX_ADPT_DFE_TAP1` through `TAP5`, and `RX_ADAPT_DONE`.
- Power and calibration status/control registers include `INIT_PWRUP_DONE`, `LANE_CMNCAL_MPLL_STATUS`, `LANE_CMNCAL_RCAL_STATUS` for lanes 0 and 1, `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `MPLL_DISABLE`, `MPLL_BG_CTL`, `RX_SIGDET_CAL`, DCC calibration code registers, `TX_DCC_BANK_ADDR`, `TX_DCC_BANK_DATA`, and `TX_DCC_CONT`.
- Packed fast-control registers `FAST_FLAGS` and `FAST_FLAGS_2` mirror lane FSM fast-path concepts: RX startup/adapt/AFE/DFE/bypass/ref-level/IQ/power/VCO calibration, supervisor and TX RX-detect shortcuts, continuous calibration/adaptation shortcuts, TX/RX DCC, VPHUD/VREF, TX RTUNE skip, and signal-detect calibration.
- Firmware and mode registers include `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, `LANE_XCVR_MODE_OVRD_IN`, `LANE_XCVR_MODE_IN`, `RX_SIGDET_CONFIG`, and `TX_DCC_CONFIG`.

## Control Flow

There is no software control flow in this chunk. Hardware-facing control flow is implied by the register groups:

1. Driver code selects the DPCS 4.2.2 register-offset/mask set for an ASIC.
2. Code reads or writes a 16-bit lane register through the AMD MMIO/register abstraction.
3. For writes, a value is shifted by the corresponding `__SHIFT` and constrained by the corresponding `_MASK`.
4. Override enable bits gate whether a forced value replaces the normal PCS/PMA/FSM signal.
5. Status and ack bits are read back to verify reset/request handshakes, adaptation completion, calibration completion, signal detect, RX validity, TX/RX DCC state, or IRQ events.

The chunk separates normal PCS/PMA inputs from override/test inputs. That split matters operationally: setting an `*_OVRD_VAL` field without the paired `*_OVRD_EN` bit generally should not affect hardware, while setting an enable bit with a stale value can force a lane into an unintended reset, power, loopback, or adaptation state.

## State And Persistence

These macros do not store software state and do not persist data themselves. They describe volatile hardware register fields whose state lives in the GPU DPCS block. Persistence and reset behavior are hardware-defined:

- `RAWLANE3` fields describe live lane state, handshakes, masks, clears, and override controls.
- `RAWAONLANE*` fields are in the always-on lane namespace and can remain observable across parts of lane power sequencing, but the header does not define exact retention semantics.
- `*_IRQ_CLR` fields imply write-to-clear style interrupt behavior in consuming code, while `*_IRQ_MASK` fields persist as register-programmed masks until changed or reset.
- Calibration/adaptation result fields expose current or last hardware calibration values; software should treat them as snapshots that can change after retraining, hotplug, link-rate changes, or power transitions.

## Dependencies And Integration Points

This header is generated hardware metadata. It is normally included alongside the matching DPCS 4.2.2 offset header and consumed by AMDGPU display/link code through register helper macros that know how to combine register addresses, masks, shifts, and instance/lane selection.

Important integration points:

- AMD display link bring-up and retraining code can use TX/RX `REQ`, `ACK`, `RATE`, `WIDTH`, `PSTATE`, `LPD`, `MPLL`, adaptation, and LOS fields to coordinate PHY lane state.
- Diagnostics, factory/ATE flows, and low-level debug tooling can use the ATE and override fields to force reset/request/data/clock/loopback/equalization behavior.
- Interrupt handling uses the `IRQ_CTL_*` status, clear, and mask definitions to detect lane changes and clear latched events.
- Calibration and telemetry paths use `RAWAONLANE*` result fields to inspect AFE/DFE/CTLE/VGA/DCC/signal-detect state and calibration outcomes.
- Cross-generation headers under the same `asic_reg/dpcs/` directory may contain similarly named macros for other DPCS revisions; consumers must pair this file with the DPCS 4.2.2 offset definitions for the target ASIC.

## Risks And Review Notes

- Generated macro drift is the primary risk. A wrong shift or mask silently programs the wrong hardware bit and may only appear as unstable link training, failed hotplug, broken low-power transitions, or hard-to-reproduce display failures.
- The namespace is repetitive across lanes and DPCS revisions. Accidentally mixing a DPCS 4.2.2 mask with another generation's offset or using a lane 3 mask for a differently laid-out register can compile cleanly but touch the wrong field.
- Several control fields are destructive or disruptive when written: reset overrides, request overrides, loopback enables, MPLL disable/select, TX/RX data enable overrides, DCC/calibration controls, IRQ clears, and FSM override/jump/break bits.
- Reserved masks are explicitly present. Write paths should preserve reserved bits with read-modify-write helpers unless hardware documentation says otherwise.
- The chunk boundary splits related content: it starts after the lane 2 TX override block has already begun, and it ends just before the lane 2 always-on `LANE_CMNCAL_RCAL_STATUS` fields. The merge lane should not infer that either neighboring register group is complete from this chunk alone.

## Test Signals

Useful validation for code that consumes this header:

- Build coverage for the ASICs that include `dpcs_4_2_2_sh_mask.h`; generated macro names should resolve without fallback to another DPCS generation.
- Register pack/unpack unit checks can assert representative fields: multi-bit fields such as `RATE`, `WIDTH`, `PSTATE`, `FSM_JMP_ADDR`, `RX_LOS_THRSHLD_OVRD_VAL`, `VCO_LD_VAL_OVRD`, `CTLE_BOOST_ADPT_VAL`, and DFE tap masks should round-trip through shift/mask helpers.
- Hardware or emulation smoke tests should exercise link bring-up, hotplug/retraining, low-power entry/exit, interrupt clear/mask paths, RX adaptation completion, signal detect, and DCC/calibration status reads.
- Debug/test flows that set overrides should verify paired value/enable behavior and then restore normal control, especially for reset, request, loopback, MPLL, TX/RX data enable, and ATE fields.
- Cross-header consistency checks should compare repeated `RAWAONLANE0`, `RAWAONLANE1`, and `RAWAONLANE2` field layouts where the same register family appears in this chunk, while respecting that lane 2 continues in the next chunk.
