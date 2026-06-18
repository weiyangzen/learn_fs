# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 35754-38156

## Scope

This chunk is a generated AMD DPCS 4.2.0 shift/mask header segment for CR1 raw lane and raw always-on lane registers. It covers lines 35754-38156 and defines 2,096 preprocessor constants: 1,050 `__SHIFT` macros and 1,046 `_MASK` macros across 307 register-comment groups. The count imbalance is expected for this slice because the range starts inside `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK` with two mask definitions whose shifts are in the previous chunk, and ends inside `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_2` after several shifts and only the first masks.

The content is declarative only. It contains no C functions, structs, runtime branches, or local storage. Its public surface is the macro set used by AMDGPU display code to compose register field values for memory-mapped DPCS hardware.

## Purpose

The header provides symbolic bit positions and masks for DPCS CR1 raw-lane digital control registers. This chunk covers:

- The tail of raw lane 2 interrupt mask/status/clear definitions.
- Raw lane 2 PMA interface overrides, TX/RX control, ATE overrides, and PCS bridge fields.
- A broad raw lane 3 PCS, FSM, interrupt, PMA, TX control, RX control, and ATE register surface.
- Raw always-on lane 0 analog/adaptation/calibration registers.
- The beginning of raw always-on lane 1 analog/adaptation/calibration registers through the first masks of `RX_OVRD_OUT_2`.

The macros let consumer code write field-safe register programming logic without embedding magic constants for lane reset, request/ack handshakes, adaptation controls, PLL state, DCC calibration, signal detect, loopback, and lane diagnostics.

## Exported API Surface

There are no callable APIs or types. Every exported item is a C preprocessor constant following the generated naming pattern:

- `REGISTER__FIELD__SHIFT` gives the low bit for a register field.
- `REGISTER__FIELD_MASK` gives the bit mask for that field.

Important macro families in this chunk:

- `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_*`: lane 2 interrupt mask/status/clear fields for TX reset/request, RX phase-2 calibration request/disable, lane transceiver mode, RX-to-TX serial loopback, and DCC on-demand events.
- `DPCSSYS_CR1_RAWLANE2_DIG_PMA_XF_*`: lane 2 PMA cross-interface override and readback fields for MPLL enable/state, TX and RX request/reset, data-enable, async, beacon, loopback, RTUNE, MPHY PWM word/data/control, and RX adaptation handshake.
- `DPCSSYS_CR1_RAWLANE2_DIG_TX_CTL_*` and `RX_CTL_*`: lane 2 TX/RX FSM controls, clock controls, DCC continuous status, OCLA/UPCS observability, loss-of-signal masking, data-enable override, off-cancel, and adaptation continuous status.
- `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_*`: lane 2 PCS interface and ATE override fields for RX/TX valid/data/header/start/end/sync/standby/error/speed-change signaling, MPLL loop selection, RX power state, RX rate, and TX override inputs.
- `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*`: lane 3 PCS interface fields, including TX/RX override inputs and outputs, PCS input/output readbacks, RX adaptation acknowledgements/FOM, directed TX pre/main/post values, lane number, reserved full fields, ATE overrides, EQ delta IQ, termination control, RX EQ overrides, and RX phase-2 calibration.
- `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*`: lane 3 FSM override/status/monitor fields, fast calibration/adaptation triggers, common calibration status, TX DCC status/flags, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR1_RAWLANE3_DIG_IRQ_CTL_*`: lane 3 IRQ status, clear, and mask fields matching the raw lane 2 interrupt family, plus reset return request.
- `DPCSSYS_CR1_RAWLANE3_DIG_PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and `PCS_XF_ATE_*`: lane 3 PMA/PCS/TX/RX controls parallel to the lane 2 definitions.
- `DPCSSYS_CR1_RAWAONLANE0_DIG_*`: always-on lane 0 analog calibration/adaptation fields for AFE/CTLE offsets, DFE references and offsets, phase adjustment, MPLL coarse tune, power-up/adaptation done status, fast flags, adaptation controls, LOS/sigdet controls, stats, RX overrides, signal-detect calibration, DCC calibration code banks, TX DCC bank access, firmware MM/adaptation/calibration configuration, transceiver mode, and TX DCC configuration.
- `DPCSSYS_CR1_RAWAONLANE1_DIG_*`: the same always-on lane pattern for lane 1 through `RX_OVRD_OUT_2`, ending mid-register at line 38156.

## Register Areas Covered

`RAWLANE2` in this chunk is mostly the second half of the lane's digital control surface. It starts with IRQ mask continuation and then defines PMA/PCS interface controls for forcing or reading lane-local TX/RX state. Fields model TX reset/request, RX reset/request, data enable, async enable, beacon enable, loopback controls, RTUNE request/ack, MPHY PWM interface values, RX adaptation acknowledgement, and PCS traffic/control signals. The TX/RX control registers expose lane-local FSM reset, bypass, clock enable, DCC status, loss-of-signal masking, and data-enable override behavior.

`RAWLANE3` is more complete in this slice. Its PCS interface groups expose both driver-side override values and PCS-side readback/status for TX and RX datapath signals. Its FSM groups expose calibration acceleration flags and status monitors for RX startup, AFE/DFE/bypass/reference-level/IQ calibration, continuous adaptation, common calibration, TX DCC, RCAL, and EQ updates. Its IRQ groups provide status, clear, and mask bits for reset, request, rate, pstate, adaptation, phase-2 calibration, loopback, DCC, TX reset, and TX request events. Its PMA/TX/RX/ATE groups mirror the lane 2 low-level control surface.

`RAWAONLANE0` and `RAWAONLANE1` describe analog and always-on lane sideband registers rather than the main PCS/PMA handshake surface. These fields cover adaptation results and controls, DFE tap/reference values, phase adjust mapping, MPLL coarse tuning, initial power-up status, fast calibration flags, TX/RX disable overrides, signal-detect filtering and calibration, RX squelch/termination/VREF overrides, DCC calibration code registers, firmware configuration windows, transceiver-mode override/readback, and TX DCC configuration.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior appears only when AMDGPU display code includes the header and passes these masks into register read/modify/write helpers.

The field names imply several hardware state machines and handshakes:

- TX/RX lane bring-up: reset, request, acknowledge, pstate, rate, data-enable, clock enable, and clock-ready fields coordinate PHY lane activation and shutdown.
- PCS/PMA boundary control: `PMA_XF` and `PCS_XF` fields expose override-enable/value pairs and readback inputs/outputs so low-level code can force or inspect lane-facing signals during training, diagnostics, and recovery.
- Interrupt processing: IRQ status bits have paired clear bits and mask registers for RX reset/request/rate/pstate/adaptation, phase-2 calibration, loopback, DCC on-demand, TX reset, and TX request events.
- Calibration and adaptation: FSM fast flags, AFE/DFE/IQ/reference-level fields, RX adaptation done/FOM/ack, DCC calibration code registers, signal-detect calibration, RTUNE, RCAL, and CMNCAL status fields represent lane-local analog calibration workflows.
- Diagnostic and test paths: ATE override fields, OCLA/UPCS observability fields, memory-address/status monitors, firmware configuration fields, and reserved/diagnostic fields expose manufacturing, validation, or firmware-controlled hooks.

No software persistence is implemented in this header. Hardware register values persist according to the ASIC's reset, power, and lane domains. Fields named `ADPT_CTL_*`, `FW_*_CONFIG`, DCC code banks, calibration code registers, reserved registers, and override values may latch state in hardware, but this chunk defines only bit layout, not policy for saving or restoring those values.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. The masks are intended to be included with companion generated DPCS 4.2.0 register address headers and used by AMDGPU/DC register helper macros that know how to read and write the corresponding MMIO addresses.

Integration points visible from the naming include:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, particularly DC link encoder, DPCS, PHY, lane training, and diagnostics paths.
- Companion `dpcs_4_2_0` address/offset headers that provide the register addresses matching these field definitions.
- DisplayPort/PHY link training and recovery code that controls TX/RX reset, request/ack, rate, pstate, data enable, and adaptation.
- Interrupt handlers or polling paths that consume the `DIG_IRQ_CTL_*` status, clear, and mask fields.
- Low-level bring-up, validation, and firmware interfaces using ATE overrides, OCLA/UPCS monitors, `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, and `FW_CALIB_CONFIG`.
- Hardware calibration flows for MPLL, DCC, RX signal detect, RX VREF/squelch, RCAL/CMNCAL, AFE/DFE/IQ adaptation, and RTUNE.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently modify adjacent hardware bits in read-modify-write sequences.
- The range is lane-repetitive and partially sliced. Lane 2, lane 3, AON lane 0, and AON lane 1 definitions should remain structurally consistent except where the chunk begins or ends mid-register.
- Access semantics are not encoded in the macros. Status/readback fields, clear-on-write fields, override enables, and writable control values are adjacent and easy to misuse without the hardware register spec.
- Many controls are override/value pairs. Setting an override value without the corresponding enable, or leaving an enable asserted after diagnostics, can hold the PHY lane in an unintended state.
- Interrupt clear and mask fields have similar names to status fields. Consumers must distinguish status observation, write-to-clear, and mask programming.
- Calibration fields expose analog tuning surfaces. Invalid writes to DFE, DCC, signal-detect, VREF, termination, MPLL, or RTUNE controls can cause link training failures or lane instability that build tests will not catch.
- The final register group is incomplete in this chunk; merge/reconciliation should use the following chunk for the remaining `RAWAONLANE1_DIG_RX_OVRD_OUT_2` masks before evaluating per-register completeness.

## Test Signals

Useful validation signals are mostly compile-time, generated-data, and hardware-integration oriented:

- Preprocess or build AMDGPU display code that includes `dpcs_4_2_0_sh_mask.h`.
- Static generated-header checks that each complete register group has matching `__SHIFT` and `_MASK` definitions; for this exact slice, expect 1,050 shifts and 1,046 masks because of the two partial boundaries.
- Diff this header against the authoritative DPCS 4.2.0 register database or generator output.
- Grep/compile consumer references for `DPCSSYS_CR1_RAWLANE2`, `DPCSSYS_CR1_RAWLANE3`, `DPCSSYS_CR1_RAWAONLANE0`, and `DPCSSYS_CR1_RAWAONLANE1` to catch renamed or missing fields.
- Hardware tests on ASICs using DPCS 4.2.0: DP link training, hotplug, lane disable/enable, rate and pstate transitions, suspend/resume, loopback diagnostics, RX adaptation, signal-detect behavior, DCC calibration, and interrupt clear/mask recovery.
- Register readback during bring-up to confirm reset/request/ack transitions, fast calibration status, CMNCAL/RCAL done bits, TX DCC status, RX adaptation done/FOM, lane transceiver mode, RX squelch/signal-detect status, and IRQ clear behavior.

## Chunk Notes For Merge

This document is source-tree aligned and intentionally covers only lines 35754-38156 of `dpcs_4_2_0_sh_mask.h`. Earlier chunks should include the first part of `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_IRQ_MASK`; the following chunk should finish `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_OVRD_OUT_2` and continue the raw AON lane 1 surface. The final per-file report should describe the whole file as generated ASIC register bitfield metadata, not handwritten driver logic.
