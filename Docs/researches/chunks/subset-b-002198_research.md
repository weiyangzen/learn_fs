# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 115206-117635

## Scope And Purpose

This chunk is part of the AMD DCN 4.1.0 generated register shift/mask header. It contains C preprocessor constants for display PHY lane register bitfields under the `DPCSSYS_CR2_RAWLANE*` namespace. The covered range starts in the RAWLANE1 digital FSM fast-calibration block, covers the remaining RAWLANE1 digital control/mask definitions, covers all visible RAWLANE2 digital PCS/FSM/IRQ/PMA/TX/RX/test definitions, and ends in the RAWLANE3 IRQ mask block.

The file is not executable logic. Its purpose is to provide the bit positions and masks consumed by AMDGPU Display Core and DMUB register helper macros when firmware or display driver code needs to read, update, or decode memory-mapped DCN hardware registers. Address offsets are supplied by companion offset headers; this header supplies the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants that make typed field access possible.

## Register Families In This Chunk

The chunk contains 2,138 `#define` lines: 1,073 shift definitions and 1,065 mask definitions. The line range covers RAWLANE1 lines 115206-115907, RAWLANE2 lines 115908-116994, and RAWLANE3 lines 116995-117635. RAWLANE2 is the only complete lane in the chunk; RAWLANE1 and RAWLANE3 are partial because adjacent chunks carry the surrounding register blocks.

Major register groups are:

- `DIG_PCS_XF_*`: PCS cross-function TX/RX override, input, output, adaptation, figure-of-merit, lane number, ATE, equalization, termination, and phase-2 calibration fields.
- `DIG_FSM_*`: lane FSM override, memory address monitor, status monitor, fast RX/TX calibration state bits, common calibration status, lock bits, TX DCC flags/status, on-chip logic analyzer enable bits, and RX IQ phase offset.
- `DIG_IRQ_CTL_*`: request/status/clear/mask bits for RX reset, RX request, RX rate, RX p-state, RX adaptation request/disable, lane transceiver mode, RX phase-2 calibration, serial loopback, DCC on-demand, TX reset, and TX request interrupts.
- `DIG_PMA_XF_*`: PMA lane/supervisor/TX/RX override and input/output fields, including power state, reset, reference clock, PLL selection, rate/divider, common mode, RX detection, calibration requests, and MPHY-related control.
- `DIG_TX_CTL_*` and `DIG_RX_CTL_*`: TX and RX controller FSM commands/status, clock control, DCC/offcan/adaptation continuous status, data-enable override, LOS mask control, and UPCS/OCLA selector fields.

Most registers are 16-bit field maps. Single-bit request, status, and clear fields usually use shift `0x0` and mask `0x0001L`, with the remaining high bits marked reserved. Wider fields encode enumerations or numeric values such as pre-emphasis levels, main/post/pre cursor values, rate/divider selections, FSM jump addresses, FSM states, ATE patterns, equalizer values, termination controls, PLL loop enables, IQ phase offsets, and OCLA register-bank enables.

## Important APIs, Types, And Macros

There are no functions, structs, or C types declared in this chunk. The important API surface is the macro naming contract:

- `DPCSSYS_CR2_RAWLANE<n>_<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `DPCSSYS_CR2_RAWLANE<n>_<REGISTER>__<FIELD>_MASK` gives the field mask before shifting values into or out of the register word.
- `RESERVED_*` fields document bits that should generally be preserved rather than assigned arbitrary values.

These constants are designed for AMD register helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `FD`, `FN`, `FD_SHIFT`, and `FD_MASK`. In the DMUB path, `dmub_dcn401.c` includes both `dcn/dcn_4_1_0_offset.h` and `dcn/dcn_4_1_0_sh_mask.h`; its register table initializer expands field definitions through `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`. Other Display Core blocks use the same broader idiom: offsets identify the MMIO register, while shift/mask headers identify the bitfields inside it.

The paired DPCS offset header shows the corresponding `ixDPCSSYS_CR2_RAWLANE*` addresses. For example, RAWLANE1 maps the PCS block around `0x3100`, FSM block around `0x3120`, IRQ block around `0x3140`, PMA block around `0x3160`, TX control around `0x3180`, RX control around `0x31a0`, and ATE/diagnostic PCS block around `0x31c0`; RAWLANE2 follows the same shape at `0x3200` and above. This chunk's masks depend on those offsets remaining aligned with the same generated register schema.

## Control Flow And Hardware Behavior

No software control flow is implemented here, but the fields describe hardware control-flow surfaces:

- FSM override fields such as `FSM_JMP_ADDR`, `FSM_JMP_EN`, `FSM_CMD_START`, `FSM_OVRD_EN`, and `FSM_BREAK` allow debug or low-level control over the lane FSM. Monitor fields expose state, command readiness, ALU flags, wait-count state, and read/write mask disable states.
- Fast calibration bits represent discrete calibration and adaptation milestones or enables, including startup calibration, AFE/DFE/bypass/reference-level/IQ calibration, continuous calibration/adaptation, VCO wait/calibration, TX common mode, TX RX detection, and supervisor handling.
- IRQ fields follow a consistent status/clear/mask control model. Individual event registers expose a single event bit, paired `_CLR` registers clear latched events, and `IRQ_MASK`/`IRQ_MASK_2` select which RX/TX or lane events can interrupt higher-level logic.
- PMA and PCS override fields allow forcing lane electrical and protocol state for bring-up, diagnostics, ATE, or firmware-controlled transitions. The naming consistently separates override values (`*_OVRD_VAL`) from override enables (`*_OVRD_EN`).
- TX/RX control fields expose command acknowledgements and continuous status for data enablement, DCC, adaptation, off-cancellation, and OCLA/UPCS muxing.

Driver code using these constants typically performs read-modify-write operations: read the register, clear the field mask, shift the new value by the field shift, apply the mask, and write the result back. Polling flows use the same constants to extract status bits until hardware reaches an expected state.

## State And Persistence Behavior

This header itself has no runtime state and persists no data. It is a compile-time hardware ABI description.

The underlying registers are live device state. Some fields are transient status signals, such as IRQ status, FSM monitor bits, calibration done/init bits, adaptation acknowledgements, and DCC status. Other fields can mutate persistent hardware configuration until reset or until another software/firmware actor writes a new value, including override enables, IRQ masks, calibration mode bits, TX/RX equalization parameters, termination overrides, PLL/rate/divider controls, and data-enable overrides.

Several fields are likely write-one-to-clear or write-to-clear semantics by convention because they appear in `_IRQ_CLR` registers. The header does not encode access type, reset value, side effects, or required sequencing; callers must rely on generated register specs, hardware programming guides, firmware ownership rules, and existing driver sequencing.

## Dependencies And Integration Points

Primary dependencies are the AMD generated register ecosystem:

- `dcn_4_1_0_offset.h` and DPCS offset headers provide the register addresses that match these field masks.
- AMDGPU Display Core and DMUB register helper macros combine offset, mask, and shift constants for MMIO access.
- Hardware/firmware ownership of DisplayPort/USB-C PHY lane resources determines whether the kernel driver, DMUB firmware, or diagnostic tooling should touch a given field.
- Link training, PHY bring-up, power management, hotplug/interrupt handling, and debug/ATE paths may use these lane controls indirectly through higher-level DCN link-encoder and PHY abstractions.

The repeated RAWLANE pattern is an integration contract: each physical lane should expose the same field layout at lane-specific offsets. Any mismatch between lane 1, 2, and 3 definitions can break generic lane-indexed code that assumes fields have identical bit positions across lanes.

## Risks And Edge Cases

- Generated header drift is the main risk. If a mask/shift is wrong or mismatched with the offset header, register helpers silently write or read the wrong bits.
- Reserved bits are explicitly present in most registers. Callers must preserve them during updates; writing full literal register values can disturb undocumented hardware state.
- Many fields control PHY electrical behavior, calibration, reset, loopback, and lane data enablement. Incorrect writes can cause link-training failures, display blanking, unstable high-speed links, or difficult-to-debug intermittent failures.
- IRQ status, clear, and mask registers have similar names. Confusing status with clear or mask fields can either drop events or create interrupt storms.
- Override value and override enable fields must be programmed consistently. Setting an override value without its enable may do nothing; enabling an override with stale data can force an unintended lane state.
- This chunk is partial for RAWLANE1 and RAWLANE3. Cross-lane analysis must merge adjacent chunks before concluding that a register family is absent or inconsistent for those lanes.
- The header lacks access semantics. Software cannot infer whether a field is read-only, write-only, write-one-to-clear, self-clearing, sticky, or firmware-owned from these macros alone.

## Test Signals

Useful validation signals for this chunk include:

- Build tests for AMDGPU display code that includes `dcn_4_1_0_sh_mask.h`, especially configurations that instantiate DCN 4.1.0 or DMUB DCN401 register tables.
- Generated-register consistency checks that compare every `REGISTER__FIELD__SHIFT` with a matching `REGISTER__FIELD_MASK`, flag missing pairs, and verify field masks match the declared shifts and widths.
- Cross-header checks that every register in this chunk has a corresponding `ixDPCSSYS_CR2_RAWLANE*` offset in the generated offset headers and that lane-to-lane field layouts remain identical where expected.
- Hardware or simulator smoke tests for DisplayPort/USB-C link bring-up, link training, hotplug/HPD handling, suspend/resume, and mode-set sequences that exercise the lane FSM, calibration, IRQ, PMA, PCS, TX, and RX fields indirectly.
- Interrupt tests that trigger RX request/rate/p-state/adaptation, lane transceiver mode, RX phase-2 calibration, loopback, DCC on-demand, and TX request/reset events, then verify status, clear, and mask behavior.
- Debug/diagnostic validation for OCLA, ATE overrides, loopback, equalization override, termination override, and FSM override paths, because those fields are high-risk and often outside normal display-mode coverage.
