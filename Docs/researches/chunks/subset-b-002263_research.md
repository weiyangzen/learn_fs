# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 9721-12191

## Scope

This chunk is part of the generated AMD DPCS 3.1.4 ASIC register shift/mask header. It contains preprocessor constants only: each hardware bitfield is represented by a `...__SHIFT` bit offset and a matching `..._MASK` bit mask. There are no C functions, structs, branches, dynamic allocations, locks, direct MMIO operations, or file-backed persistence mechanisms in this range.

The slice contains 2,111 `#define` entries: 1,056 shift definitions and 1,055 mask definitions, organized under 360 register-comment blocks. It starts in the middle of the `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1` mask/shift family and ends in the middle of `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QDF_CODE_0`, so neighboring chunks are needed to reconstruct both boundary registers completely.

Major block coverage in this chunk:

- Tail of `RAWLANE2` PCS transfer override fields.
- Full `RAWLANE3` PCS transfer, RX/TX PCS, ATE override, equalization, FSM, IRQ, PMA transfer, TX control, and RX control field families.
- Always-on lane register families for `RAWAONLANE0` and `RAWAONLANE1`.
- Opening portion of `RAWAONLANE2`, through RX DCC calibration code register fields.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for AMD display PHY/DPCS lane registers. Runtime driver code combines these constants with companion DPCS register-address headers and AMD register-helper macros to perform masked reads, writes, updates, and polling without embedding raw bit arithmetic at call sites.

The represented hardware area is PHY/lane-oriented rather than high-level display-pipe composition. It covers per-lane PCS control, RX adaptation/calibration, TX/RX reset and request handshakes, loopback and test overrides, PMA interface state, interrupt status/mask/clear fields, and always-on calibration/status/configuration registers. The constants are compile-time metadata; the real behavior occurs when AMDGPU display code programs the matching hardware registers.

## Important Macros and Field Families

The exported API is the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset within a 16-bit register image.
- `<REGISTER>__<FIELD>_MASK` gives the pre-shifted bit mask for preserving or updating that field.
- Prefixes such as `DPCSSYS_CR0_RAWLANE3_DIG_*` and `DPCSSYS_CR0_RAWAONLANE1_DIG_*` are semantically important because they bind the same logical field families to a specific DPCS instance or lane namespace.

Important register families in this chunk include:

- `RAWLANE2_DIG_PCS_XF_*`: the tail of lane 2 PCS ATE/TX/RX override metadata, including DETRX request, voltage/current boost, TX beacon, serial loopback, async data, master MPLL loop enable, RX LOS/adaptation overrides, VCO/reference lock override fields, RX-valid override, and TX data/async override fields.
- `RAWLANE3_DIG_PCS_XF_TX_*`: lane 3 TX PCS input, override input/output, PCS output, reset/request state, P-state, low-power detect, width/rate, MPLL selection/enables, master MPLL state, DETRX, TX data enable, async enable/data, beacon, and TX-to-RX serial loopback metadata.
- `RAWLANE3_DIG_PCS_XF_RX_*`: lane 3 RX PCS and override fields for reset/request, P-state, rate, MPLL selection/enables, adaptation request/disable/continue, off-cancellation continue, RX data enable, RX-to-TX serial loopback, TX pre/main/post cursor direction values, lane number, ATE override fields, RX equalization delta IQ overrides, TX/RX termination control, RX LOS threshold/valid overrides, RX adaptation FOM/ack, and phase-2 calibration fields.
- `RAWLANE3_DIG_FSM_*`: finite-state-machine control and monitor fields for override control, memory address/status monitors, fast RX startup/adaptation/calibration flags, common calibration status, continuous calibration/adaptation flags, CR lock, TX DCC flags/status, OCLA debug hooks, TX EQ update flags, RCAL status, and RX IQ phase offset.
- `RAWLANE3_DIG_IRQ_CTL_*`: interrupt request, clear, and mask fields for RX reset/request/rate/P-state/adaptation events, lane transceiver mode events, RX phase-2 calibration events, RX-to-TX serial loopback events, DCC on-demand, and TX reset/request events.
- `RAWLANE3_DIG_PMA_XF_*`: PMA interface metadata for lane, supervisor, TX, RX, MPHY, lane retune, and RX adaptation override/incoming fields. These constants describe PMA-facing reset, request, acknowledge, power, PLL, signal-detect, termination, calibration, loopback, and adaptation wires exposed through DPCS registers.
- `RAWLANE3_DIG_TX_CTL_*` and `RAWLANE3_DIG_RX_CTL_*`: lane-local TX/RX control metadata for TX FSM and clock control, TX DCC continuous status, OCLA/UPCS debug paths, RX FSM control, RX LOS mask timing, RX data enable override, and continuous off-cancellation/adaptation status.
- `RAWAONLANE0/1/2_DIG_*`: always-on per-lane calibration/status/configuration fields, including AFE/CTLE/DFE offset registers, RX adaptation IQ/FOM/ATT/VGA/CTLE/DFE tap values, DFE reference levels, phase adjust linear/map fields, MPLL coarse tune, initial power-up done, fast flags, slicer control, common calibration MPLL/RCAL status, adaptation control registers, MPLL disable, TX/RX disable override, RX LOS/signal-detect filtering, RX PMA override outputs, RX signal-detect calibration and code fields, RX VREF generator enable, RX DCC calibration code fields, TX DCC bank/configuration fields, MPLL bandgap control, signal-detect output override/input, firmware MM/adaptation/calibration configuration, lane transceiver mode override/input, RX signal-detect configuration, and TX DCC configuration. This chunk fully covers lane 0 and lane 1 instances and begins the same pattern for lane 2.

## Control Flow and Runtime Integration

There is no executable control flow in this file. Runtime behavior is indirect:

1. DPCS 3.1.4 display/PHY code includes this shift/mask header together with matching generated register-address headers.
2. Register helper macros pair an address or indirect index with the `__SHIFT` and `_MASK` constants from this file.
3. Driver code reads, writes, updates, or polls individual fields while bringing up lanes, training links, calibrating RX/TX paths, entering or leaving low-power states, servicing PHY interrupts, and collecting debug status.
4. Hardware registers hold the actual lane state; this header only describes how to isolate each field.

The represented operational flow is typically lane bring-up and maintenance: reset/request handshakes are asserted through PCS/PMA-facing fields, PLL and rate/width state are selected, RX detection and adaptation are requested, calibration FSM status and IRQs are observed or cleared, PMA override paths are used for test or bring-up modes, and always-on calibration/status registers retain lane-local tuning state across parts of the PHY power sequence.

## State and Persistence Behavior

The file itself has no mutable state. It contributes compile-time constants to the kernel build.

The hardware state represented by this chunk includes:

- PCS lane state: TX/RX reset, request, acknowledge, P-state, rate, width, low-power detect, MPLL selection/enables, DETRX, TX data/async controls, RX valid/data enable, loopback, and adaptation request/ack/FOM state.
- Calibration and adaptation state: RX adaptation IQ/FOM values, ATT/VGA/CTLE/DFE tap values, DFE reference and offset codes, phase-adjust values, RX VCO/reference lock overrides, RX LOS thresholds, signal-detect calibration/tune codes, RX DCC calibration codes, TX DCC status and banked data, common MPLL/RCAL status, and fast/continuous calibration flags.
- PMA-facing state: PMA reset/request/acknowledge wires, supervisor PMA input, lane retune controls, MPHY override state, RX adaptation override outputs, termination controls, signal-detect controls, and VREF generator controls.
- Event state: IRQ request, mask, and clear registers for lane reset/request/rate/P-state/adaptation, transceiver mode, phase-2 calibration, loopback, DCC on-demand, and TX reset/request events.
- Debug and observability state: FSM memory/status monitors, OCLA and UPCS OCLA hooks, TX/RX continuous status fields, CR lock, initial power-up done, signal-detect input/output mirrors, and firmware configuration fields.

Persistence is hardware scoped. Register values may survive some local block transitions but should be treated as volatile across GPU reset, display engine reset, DPCS/PHY reset, power gating, suspend/resume, hotplug retraining, and mode/link reconfiguration. Higher-level AMDGPU display state and firmware sequencing remain the source of truth; this header does not store policy or restore values.

## Dependencies

This chunk depends on the companion generated DPCS 3.1.4 register address/index headers. Shift and mask constants alone do not identify an MMIO address or indirect register selector.

It also depends on:

- AMDGPU/DC register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked register access.
- Silicon register database inputs used to generate the DPCS 3.1.4 headers.
- Display PHY, link encoder, DisplayPort/HDMI link-training, AUX/hotplug recovery, power-management, diagnostics, and firmware-coordination code that programs DPCS lane registers.
- Correct instance mapping between `RAWLANE2`, `RAWLANE3`, and `RAWAONLANE0/1/2` prefixes and the hardware lanes/register address spaces in companion headers.

Because this is generated silicon metadata, manual edits are high risk unless synchronized with the register database, matching offset headers, generated register tables, and all call sites using the field names.

## Integration Points

Primary integration points are macro references in AMD display code and generated register tables. A consumer that names a field such as `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_PCS_IN__RATE`, `DPCSSYS_CR0_RAWLANE3_DIG_IRQ_CTL_IRQ_MASK__RX_REQ_IRQ_MASK`, or `DPCSSYS_CR0_RAWAONLANE1_DIG_RX_ADPT_DFE_TAP1__VAL` relies on this header to provide the exact bit location and mask.

Integration surfaces include:

- Lane bring-up and reset sequencing: PCS/PMA reset, request, acknowledge, P-state, rate/width, MPLL selection, master MPLL loop state, and initial power-up done fields.
- Link training and adaptation: DETRX request/result, RX adaptation request/disable/continue, RX adaptation FOM/ack, TX pre/main/post direction controls, RX equalization delta IQ overrides, phase-2 calibration request/disable IRQs, and DFE/CTLE/VGA/ATT/tap status fields.
- Power and clock handling: MPLL enable/disable, MPLL coarse tune, common calibration MPLL status, TX clock control, low-power detect fields, lane transceiver mode, and fast/continuous calibration flags.
- Test, debug, and manufacturing modes: ATE override fields, TX/RX serial loopback, PMA/MPHY override paths, OCLA/UPCS OCLA debug registers, signal-detect overrides, firmware configuration fields, and calibration code readbacks.
- Interrupt handling: IRQ status, mask, and clear fields for RX/TX reset/request, rate/P-state changes, adaptation requests, phase-2 calibration, loopback, transceiver mode, and DCC events.
- Always-on lane state capture: `RAWAONLANE0`, `RAWAONLANE1`, and partial `RAWAONLANE2` calibration/status blocks provide lane-local observability that can be read during training diagnostics and recovery.

## Risks and Failure Modes

- Incorrect shift or mask values can corrupt neighboring fields in the same 16-bit register, leading to failed lane bring-up, incorrect PLL/rate/width selection, unstable RX adaptation, broken signal detection, or disabled TX/RX paths.
- Instance-prefix mistakes can compile successfully while targeting the wrong lane. Confusing `RAWLANE3` with `RAWAONLANE1`, for example, would mix live PCS/PMA controls with always-on calibration/status registers.
- Boundary incompleteness matters for this chunk: it begins after the register comment for `RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1` and ends before the mask/reserved fields for `RAWAONLANE2_DIG_RX_DCC_CAL_QDF_CODE_0`. The final file-level merge must reconcile both partial register families with adjacent chunk reports.
- Interrupt clear/mask fields require exact masks. A wrong IRQ clear bit can drop events, leave stale interrupts asserted, or mask real lane reset/adaptation failures.
- Override-enable fields are particularly sensitive because they can force hardware wires away from normal firmware/PHY sequencing. Bad masks in ATE, PMA, MPHY, TX/RX disable, signal-detect, or equalization override fields can cause hard-to-debug link failures.
- Calibration fields often encode signed or hardware-specific tune codes even though this header exposes only raw bit positions. Misinterpreting value width or sign in consumers can produce invalid CTLE/DFE/DCC/VREF/signal-detect tuning.
- Generated-header drift against silicon documentation or companion address headers can pass compilation but fail only on affected ASIC revisions or lane instances.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: AMDGPU display code builds without missing `DPCSSYS_CR0_RAWLANE2`, `DPCSSYS_CR0_RAWLANE3`, `DPCSSYS_CR0_RAWAONLANE0`, `DPCSSYS_CR0_RAWAONLANE1`, or `DPCSSYS_CR0_RAWAONLANE2` shift/mask symbols.
- Register-generation consistency checks: every non-boundary field has matching `__SHIFT` and `_MASK` definitions, reserved masks match the documented field widths, and instance prefixes align with companion DPCS register address headers.
- Lane/link smoke tests: hotplug, modeset, link retraining, suspend/resume, GPU reset recovery, lane-count/rate changes, and low-power transitions on hardware using DPCS 3.1.4.
- Training/adaptation diagnostics: RX adaptation request/ack/FOM transitions, DFE/CTLE/VGA/ATT value readback, phase-2 calibration IRQs, RX LOS/signal-detect behavior, TX EQ update status, and MPLL/RCAL calibration done flags.
- Interrupt validation: RX/TX reset/request IRQ assertion and clear, RX rate/P-state/adaptation IRQ mask behavior, lane transceiver mode IRQ handling, loopback IRQ handling, and DCC on-demand event reporting.
- Debug/status validation: OCLA/UPCS OCLA access, FSM status/memory monitors, TX/RX continuous calibration status, signal-detect input/output mirrors, initial power-up done, and firmware configuration fields read back as expected.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create a final per-file synthesis for `dpcs_3_1_4_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
