# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 43855-46340

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice. It exports preprocessor constants that describe bit positions and masks for CR2 display PHY/DPCS registers, mainly the `DPCSSYS_CR2_RAWLANE3` digital PCS/PMA lane-control block and the beginning of the repeated `DPCSSYS_CR2_RAWAONLANE*` always-on lane diagnostic and calibration blocks.

The source tree path is under a `ceph-client` mirror, but this file is AMDGPU DRM display hardware metadata. It does not implement filesystem behavior. Its purpose is to give display-driver code symbolic field definitions for safe read-modify-write access to memory-mapped or indexed DPCS registers when setting link rate, lane width, power state, resets, loopback, RX adaptation, PMA controls, interrupts, and lane calibration fields.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, locks, callbacks, allocation paths, or direct MMIO operations in this range. The exported interface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used to encode or decode a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, clear, preserve, or update that field.

The chunk contains 2,101 `#define` lines: 1,051 `__SHIFT` macros and 1,050 `_MASK` macros. The one-count mismatch is a chunk-boundary artifact: line 46340 defines `DPCSSYS_CR2_RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST__RESERVED_15_8__SHIFT`, and its matching mask is outside this work-item range. The chunk also starts without the preceding register comment for `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_1`, though it contains that register's complete fields.

Major macro families in this slice:

- `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_*`: PCS transfer interface fields for TX/RX overrides, PCS inputs and outputs, RX adaptation acknowledgements, figure-of-merit reporting, TX pre/main/post direction controls, lane number, ATE overrides, RX equalization overrides, termination controls, and phase-2 calibration.
- `DPCSSYS_CR2_RAWLANE3_DIG_FSM_*`: lane FSM override, status, fast-state observability, RX startup/adaptation/calibration states, common calibration status, CR lock, TX DCC flags/status, OCLA debug selection, TX EQ update flags, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANE3_DIG_IRQ_CTL_*`: per-event interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation, lane transceiver mode, phase-2 calibration, loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR2_RAWLANE3_DIG_PMA_XF_*`: PMA transfer and MPHY override/status fields covering lane reset, test powerdown, beacon/receiver-detect controls, transmit and receive PMA enable/idle/signaling controls, VCO/reference load values, RTUNE state, SRAM bypass/load/init status, and RX adaptation outputs.
- `DPCSSYS_CR2_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANE3_DIG_RX_CTL_*`: TX/RX local FSM control, clock control, DCC/continuous adaptation status, loss-of-signal masking, RX data-enable override, and OCLA observability.
- `DPCSSYS_CR2_RAWAONLANE0_DIG_*`, `RAWAONLANE1_DIG_*`, and `RAWAONLANE2_DIG_*`: repeated always-on lane fields for RX adaptation values, fast flags, DFE taps, slicer control, common calibration status, RX signal-detect filtering/calibration, DCC calibration codes, TX DCC bank access, MPLL background controls, firmware configuration, and lane transceiver mode.
- `DPCSSYS_CR2_RAWAONLANE3_DIG_*`: the beginning of the lane 3 always-on block, through the first DFE bypass offset shift at the chunk boundary.

## Control Flow

This header has no runtime control flow. It contributes constants to control paths elsewhere:

1. AMDGPU display code includes `dpcs_3_1_4_offset.h` for register addresses and `dpcs_3_1_4_sh_mask.h` for fields.
2. Register helper macros token-paste a register and field name into offset, mask, and shift constants.
3. Runtime code composes values, performs read-modify-write updates, polls status, or writes interrupt clear bits through ASIC-specific register accessors.
4. Hardware state machines consume or expose these fields for PHY bring-up, link training, lane reset, clocking, adaptation, calibration, loopback, ATE/test modes, interrupt delivery, and debug capture.

The constants do not encode required sequencing. Consumer code must still follow the hardware rules for reset ordering, power-state changes, MPLL selection, TX/RX request and acknowledge handshakes, adaptation request/acknowledge handling, DCC calibration, signal-detect tuning, and interrupt clear/mask ordering.

## State And Persistence Behavior

The header stores no software state and persists nothing. The underlying registers are live hardware state:

- TX and RX PCS override fields persist programmed values such as reset/request overrides, link rate, lane width, pstate, low-power detect, MPLL selection/enables, async data controls, beacon enable, loopback, RX data enable, adaptation controls, VCO/reference load overrides, and equalization override values until hardware reset, power-domain reset, or later driver writes.
- PCS/PMA output and status fields expose transient or sticky hardware observations such as ACK bits, DETRX result, RX adaptation acknowledgement, TX/RX PMA enables, idle/valid state, VCO/ref load values, RTUNE done, SRAM load/init state, MPHY override output, RX adaptation outputs, and lane transceiver mode.
- FSM fields expose current and historical state-machine details, including fast-state flags, calibration phase state, TX DCC flags/status, CR lock, TX EQ update, common calibration status, and OCLA debug selection.
- IRQ status, clear, and mask fields represent interrupt state. Some fields are likely status-only, some are mask/configuration bits, and clear registers are write-triggered. The header does not state which bits are write-one-to-clear, read-only, self-clearing, or sticky.
- RAWAON lane fields hold or expose calibration/adaptation data for RX AFE/DFE, DCC, signal detection, firmware configuration, and transceiver mode. These values can survive longer than the active lane datapath depending on the always-on power domain, but the header itself gives no reset-value or retention contract.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which defines matching `ix...` register addresses. In that file, this chunk maps `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_*` from the `0x3300` range, `DPCSSYS_CR2_RAWLANE3_DIG_FSM_*` from `0x3320`, IRQ control from `0x3340`, PMA transfer from `0x3360`, TX/RX local control from `0x3380` and `0x33a0`, ATE-related PCS registers from `0x33c0`, and RAWAON lane registers beginning at `0x4000`.

The practical integration points are AMDGPU display and PHY code that configures DisplayPort/HDMI/USB-C physical lanes for ASICs using DPCS 3.1.4. The generated names are intended for common AMD register helper idioms such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or indexed-register wrappers. The repeated register shapes across `RAWLANE3` and `RAWAONLANE0/1/2/3` are an ABI contract: generic lane-management code can select an instance while relying on consistent field names, shifts, and masks.

This slice also integrates with firmware/test/debug surfaces:

- ATE override registers let manufacturing or validation code force TX/RX values independent of normal PCS/PMA control.
- OCLA and UPCS OCLA fields expose internal observability selections for debug capture.
- Firmware configuration and calibration fields under `FW_*`, `FAST_FLAGS`, `ADPT_CTL_*`, and calibration-code registers reflect coordination with firmware or microcontroller-managed lane adaptation.
- Interrupt status/clear/mask fields connect low-level lane events to DRM hotplug/link-management recovery paths.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask compiles cleanly but programs or reads the wrong silicon bits, which can manifest as link-training failures, unstable displays, calibration timeouts, or unhandled lane interrupts.
- This work item starts and ends on register boundaries only partially. The previous chunk owns the `PCS_XF_TX_OVRD_IN_1` register comment context, and the next chunk owns the matching mask for the final `RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST` shift.
- The register names mix command, override-enable, override-value, status, clear, mask, and reserved fields. Treating all fields as normal writable configuration can lose interrupts, write reserved bits, or fight hardware-owned state machines.
- PCS/PMA reset, request/ack, data-enable, MPLL, pstate, width, and rate fields are sequencing-sensitive. Updating them while the lane is active can disrupt link training or data transmission.
- ATE, loopback, MPHY override, RX/TX PMA override, and signal-detect override fields can bypass normal hardware control. Leaving these set after diagnostics can break normal PHY operation.
- RAWAON lanes 0, 1, and 2 are large parallel blocks. Copy/paste or generation errors between lane instances are especially hard to notice because the field layouts are intentionally similar.
- Several registers expose mostly `RESERVED_*` fields. Driver code should not infer those are safe storage bits; reserved masks mainly describe bits to preserve during field updates.
- Status fields for adaptation, calibration, DCC, signal detect, and common calibration depend on analog hardware behavior. Software-only tests cannot prove their semantics without hardware readback.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU display code for ASICs using DPCS 3.1.4; missing or renamed generated macros should become compile failures in register-table or PHY programming code.
- Mechanical consistency checks against AMD's generated register database and `dpcs_3_1_4_offset.h`, especially that every complete field has one `__SHIFT` and one matching `_MASK`.
- Cross-lane comparison of the repeated RAWAON blocks for lanes 0, 1, and 2, plus reconciliation with the next chunk for the rest of lane 3.
- Runtime display validation on relevant hardware: link bring-up, hotplug, suspend/resume, mode changes, link-rate changes, lane-count changes, DP Alt Mode transitions, and HDMI/DP PHY power cycling.
- Instrumented register readback during PHY bring-up to confirm reset, request/ack, pstate, width/rate, MPLL enable/state, RTUNE, SRAM load/init, DCC, adaptation, and signal-detect fields move through expected states.
- Interrupt-path tests that trigger or observe RX reset/request/rate/pstate/adaptation events, phase-2 calibration events, loopback events, DCC on-demand, and TX reset/request interrupts; stale IRQs or repeated clears indicate mask/clear-field errors.
- Diagnostic/validation tests for ATE, OCLA, loopback, RX equalization, signal-detect calibration, DFE tap reporting, and firmware calibration fields, with cleanup checks that override enable bits return to normal values.

## Cross-Chunk Notes

The previous chunk should be consulted for the beginning of the `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` area and the register comment context immediately before line 43855. The next chunk should be consulted for the rest of `DPCSSYS_CR2_RAWAONLANE3_DIG_*`, including the mask paired with the final shift in this range. The final merged per-file report should describe this header as generated DPCS 3.1.4 register ABI metadata, not handwritten driver logic.
