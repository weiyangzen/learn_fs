# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 93480-95898

## Scope and Purpose

This chunk is part of the generated DCN 4.1.0 ASIC register shift/mask header used by the AMD display driver. It contains preprocessor constants for bit positions (`__SHIFT`) and bit masks (`_MASK`) in DPCSSYS CR1 raw lane display PHY/PCS registers. The chunk covers the tail of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`, complete register-field metadata for raw lanes 0 and 1 across PCS, FSM, IRQ, PMA, TX control, RX control, and ATE/test blocks, and the opening PCS portion of raw lane 2 through the `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_RESERVED_2` comment.

The file is not executable logic. Its purpose is to provide the compile-time hardware field contract consumed by register accessor macros in DCN 4.1 display code. Adjacent offset headers provide register addresses such as `ixDPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`; this header provides field extraction and update metadata for those registers.

## Important API Surface

The exported surface is entirely macro definitions. In this line range there are 2,146 `#define` entries: 1,068 shift constants and 1,078 mask constants. The slightly higher mask count is caused by chunk-boundary effects: the range starts after the shift definitions for `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN` and includes that register's mask definitions.

Important register groups in the chunk include:

- `DPCSSYS_CR1_RAWLANE*_DIG_PCS_XF_TX_*`: TX PCS input, override input, override output, PCS output, async enable, reset/request override, detect-RX request, VBOOST, IBOOST, beacon enable, lane rate/width, P-state, low-power disable, and master MPLL state fields.
- `DPCSSYS_CR1_RAWLANE*_DIG_PCS_XF_RX_*`: RX PCS/override input and output fields for request, rate, width, P-state, CDR low-frequency state, reset, adaptation control, data enable overrides, loss-of-signal threshold, VCO/ref load values, equalizer values, phase-2 calibration, adaptation ack/FOM, and TX pre/main/post direction indicators.
- `DPCSSYS_CR1_RAWLANE*_DIG_FSM_*`: lane FSM override, memory/status monitors, fast calibration/adaptation status bits, common calibration MPLL/RCAL status, CR lock, DCC flags/status, OCLA taps, TX EQ update, and RX IQ phase offset metadata.
- `DPCSSYS_CR1_RAWLANE*_DIG_IRQ_CTL_*`: per-lane IRQ status, clear, and mask fields for RX reset/request/rate/P-state/adaptation, phase-2 calibration, serial loopback enable, DCC on-demand, TX reset/request, and lane transceiver mode.
- `DPCSSYS_CR1_RAWLANE*_DIG_PMA_XF_*`: PMA lane/supervisor/TX/RX/MPHY override and PMA input fields, including DCC calibration, TX pre/main/post cursor controls, TX voltage mode, RTUNE, TX/RX acknowledgment, and PMA ready/reset/enable signals.
- `DPCSSYS_CR1_RAWLANE*_DIG_TX_CTL_*` and `DPCSSYS_CR1_RAWLANE*_DIG_RX_CTL_*`: control/status field metadata for TX/RX FSM bypass, clock control, continuous DCC/adaptation status, OCLA, RX LOS masks, and data enable override controls.
- `DPCSSYS_CR1_RAWLANE*_DIG_PCS_XF_ATE_*`: automated-test override fields for RX/TX reset/request, adaptation enable, data enable, lane rate/width/P-state/LPD, MPLL controls, TX levels, RX EQ values, and RX/TX acknowledge paths.

The lane layout is intentionally repetitive. Raw lane 0 and raw lane 1 are fully represented for the local register families listed above. Raw lane 2 begins at `PCS_XF_TX_OVRD_IN` and continues through `PCS_XF_RESERVED_2` at the end of this chunk; lane 2 ATE/FSM/IRQ/PMA/TX/RX control fields continue in later lines outside this work item.

## Control Flow and Data Flow

There is no runtime control flow in this chunk. The data flow is compile-time token composition:

1. DCN 4.1 source files include `dcn/dcn_4_1_0_sh_mask.h`.
2. Register helper macros such as `FN(reg, field)`, `FD(reg_field)`, `REG_SET_*`, and `REG_GET` concatenate a register token and field token into names of the form `REG__FIELD__SHIFT` and `REG__FIELD_MASK`.
3. The generated shift/mask constants are used to pack field values into MMIO register writes or unpack field values from MMIO register reads.
4. Register address macros from the matching DCN/DPCS offset headers identify which MMIO register is accessed; this header identifies which bits inside that register are accessed.

Because these macros encode hardware bit layout, the effective "control flow" lives in users of the AMD display register framework. For example, a call that sets a lane override bit depends on the `*_OVRD_VAL__SHIFT` and `*_OVRD_VAL_MASK` pair here to target the correct bit without disturbing adjacent fields.

## State and Persistence Behavior

This header stores no software state and persists nothing on its own. The constants describe fields in hardware registers whose values are persistent only in the device register state until reset, power transition, firmware action, or driver write changes them.

Several represented fields affect sensitive lane state when used by callers:

- Reset/request and override-enable fields can force PCS/PMA paths away from hardware-controlled state machines.
- Rate, width, P-state, LPD, and MPLL fields influence link-training and power behavior.
- RX adaptation, equalizer, LOS threshold, VCO/ref load, and phase calibration fields influence receiver bring-up and signal integrity.
- IRQ mask and clear fields determine whether lane events are visible to display interrupt handling.
- ATE fields expose test-mode overrides that should normally be controlled only by validated bring-up, diagnostics, or firmware paths.

## Dependencies and Integration Points

Direct dependencies are limited to the C preprocessor and include guards from the surrounding header. The macros integrate with:

- DCN 4.1 display units that include this exact header, including `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, GPIO translation/factory code, the DCN 4.0.1 clock manager, and DCN 4.0.1 resource construction.
- AMD display register helper layers that expect a consistent `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- Matching offset headers under `include/asic_reg/dpcs/` and other generated DCN register headers that provide `ix...` register addresses for the same logical blocks.
- Hardware/firmware contracts for DPCSSYS CR1 raw lane PHY/PCS behavior.

The chunk is generated-style data and should remain synchronized with the matching ASIC register database. Hand edits are high risk because many call sites rely on token naming rather than explicit references to individual constants.

## Risks and Edge Cases

- Bitfield mismatch risk: an incorrect shift or mask can silently write the wrong hardware bits, affecting link training, lane reset sequencing, IRQ delivery, power state transitions, or PHY calibration.
- Lane copy/paste risk: lane 0 and lane 1 share nearly identical layouts with only the lane number changed. A single divergent field name or mask in one lane can compile cleanly but misconfigure only that lane.
- Chunk-boundary risk: this range starts after the shift definitions for `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`, so a reviewer must combine this with the previous chunk for the complete lane 0 first register. It also ends at the `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_RESERVED_2` comment; the two definitions for that reserved register begin immediately after this range and belong to the following chunk.
- Reserved-field risk: many registers expose `RESERVED_*` masks. Driver code should avoid writing non-reset values into reserved fields unless the hardware programming guide explicitly requires it.
- Override/test-mode risk: PCS/PMA/ATE override fields can bypass normal lane FSM behavior. Incorrect use can leave a lane stuck in reset, force invalid rate/width/P-state settings, mask interrupts, or destabilize RX/TX adaptation.
- Generated-header drift: this DCN 4.1.0 header must stay aligned with matching offset and register-list headers. If offsets update without corresponding shift/mask updates, register accessor code may target the right address but wrong bits.

## Test and Validation Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration oriented:

- Compile coverage for DCN 4.1.0 display, DMUB, IRQ, GPIO, clock-manager, and resource files that include `dcn_4_1_0_sh_mask.h`; token-concatenation failures surface as missing macro errors.
- Static generation checks comparing each field's mask with its shift and width, and ensuring every `__SHIFT` has a corresponding `_MASK` for complete registers outside chunk boundaries.
- Cross-header checks that every register represented here has a matching `ix...` offset in the relevant DCN/DPCS offset header.
- Per-lane consistency checks confirming raw lane 0, 1, 2, and later lanes expose equivalent field layouts where hardware intends them to be repeated.
- Runtime display link tests on DCN 4.1 hardware: hotplug, DisplayPort link training, lane-count/rate changes, power-state transitions, suspend/resume, IRQ delivery, and PHY calibration/adaptation paths.
- Diagnostic register dumps around link failures: unexpected values in reset/request, override-enable, IRQ mask/clear, LOS, adaptation, MPLL, or EQ fields would point back to this generated field contract or its callers.

## Cross-Chunk Notes

This work item is a partial view of a large generated header. The previous chunk is needed to see the `__SHIFT` entries for `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`; the next chunk is needed for the `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_RESERVED_2` definitions and the remainder of raw lane 2. The final per-file research pass should merge this lane-local analysis with adjacent chunks that cover common DPCSSYS blocks, additional raw lanes, and any remaining DCN 4.1 register families.
