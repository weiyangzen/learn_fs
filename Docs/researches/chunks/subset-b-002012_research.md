# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 202390-204787

## Scope

This chunk is a generated AMD DCN 3.2 register field mask header segment. It covers 2,398 source lines containing 2,161 `#define` entries: 1,080 `__SHIFT` constants, 1,081 `_MASK` constants, and comment delimiters for 238 distinct register groups. The covered block is limited to C20 PHY CR4 lane/register definitions, mainly lane 3 RX and analog receive controls plus raw lane 0 TX/RX PCS/PMA cross-interface controls.

The file does not define executable functions or C types. Its API surface is the macro namespace used by register access helpers elsewhere in the AMD display and GPU driver stack.

## Purpose

The purpose of this chunk is to provide compile-time bitfield metadata for programming and decoding DCN 3.2 PHY registers. Each register field is represented by:

- `<REGISTER>__<FIELD>__SHIFT`, the low-bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for the field in the hardware register.

These constants let low-level register helpers build read-modify-write operations without open-coded bit arithmetic. The specific hardware covered here is concentrated around C20 PHY CR4:

- `C20_PHY_CR4_LANE3_DIG_ASIC_RX_*`: lane 3 ASIC-side RX input/output and RX equalization override registers.
- `C20_PHY_CR4_LANE3_DIG_RX_PWRCTL_*`: lane 3 RX power-state configuration, power-up timing, control, and status.
- `C20_PHY_CR4_LANE3_DIG_RX_VCOCAL_*`, `*_CDR_*`, and `*_DPLL_*`: VCO calibration, clock/data recovery, DPLL frequency, and boundary fields.
- `C20_PHY_CR4_LANE3_DIG_RX_ADPTCTL_*`: RX adaptation, CTLE/VGA/DFE status, DCC offsets, slicer/search-state-machine configuration, and adaptation reset fields.
- `C20_PHY_CR4_LANE3_DIG_RX_STAT_*` and `*_IQC_CTL_*`: pattern/statistical counters, sample counts, match controls, stop controls, and IQ calibration control/status.
- `C20_PHY_CR4_LANE3_DIG_ANA_XF_RX_*`: digital-to-analog RX cross-interface controls, calibration knobs, analog override/status registers, and analog configuration registers.
- `C20_PHY_CR4_RAWLANE0_DIG_TX_*` and `C20_PHY_CR4_RAWLANE0_DIG_RX_*`: raw lane 0 TX/RX PCS, firmware, IRQ, control, PMA, and RX PCS context register field definitions.

## Important APIs and Data Shapes

The important API is the macro naming contract. Callers are expected to combine a register address macro from the matching address header with these field masks and shifts through AMDGPU/DC register helper macros such as field-update, field-get, or register-write wrappers.

The field definitions are almost entirely 16-bit register fields. Many masks are `0xFFFFL`-bounded, and reserved fields explicitly occupy the unused high bits. The chunk uses recurring field patterns:

- Override pairs: a value field plus an enable bit, for example `*_OVRD_EN`, `*_OVRD`, `*_OVRD_IN_*`, and `*_OVRD_OUT_*`.
- Handshake pairs: `REQ`, `ACK`, `VALID`, `RESET`, `RESET_OVRD_EN`, and `ACK_OVRD_EN`.
- Power-state controls: `PSTATE`, `LPD`, `DATA_EN`, `CLK_RDY`, `MPLL_EN`, `CDR_SSC_EN`, `ADAPT_REQ`, and `ADAPT_IN_PROG`.
- Analog/RX tuning values: `EQ_ATT_LVL`, `EQ_VGA_GAIN`, `EQ_CTLE_BOOST`, `EQ_CTLE_POLE`, `EQ_CTLE_ZERO`, `EQ_AFE_RATE`, `EQ_AFE_BIAS`, `EQ_AFE_BIAS_TIA`, `EQ_AFE_VCM_ADJ`, and `EQ_DFE_TAP1`.
- Calibration and status values: `VCO_CAL_CODE`, `VCO_CAL_DONE`, `VCO_CAL_FAIL`, `CDR_FREQ_CODE`, `DFE_TAP*_ADPT_CODE`, `ASM1_DONE`, `SSM_DONE`, `FSM_STATE`, statistic counters, and scope/match controls.
- Reserved masks: numerous `RESERVED_*` fields document the silicon bit layout and should not be treated as writable semantic state.

There are no structs, enums, functions, or inline helpers in this chunk. The macros are effectively a generated schema for the hardware register layout.

## Control Flow and Behavior

This file has no runtime control flow. Runtime behavior arises when other driver code includes `dcn_3_2_0_sh_mask.h` and uses these constants to program display PHY state. The header is included by DCN 3.2 display paths such as `dmub_dcn32.c`, `irq_service_dcn32.c`, GPIO translation/factory code, the DCN 3.2 clock manager, resource construction, and one amdgpu GMC source file.

The implied hardware flows represented by this slice are:

- RX power sequencing: `RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2` select analog bleeder, AFE, clock regulator, deserializer, CDR, VCO reset/calibration, DFE, and bypass-slicer enablement for each power state. Power-up timing registers supply settle times for these transitions.
- RX clock recovery and calibration: VCO calibration control/time/status, CDR control/status, DPLL frequency, and DPLL frequency bounds define how the PHY locks to incoming serial data.
- RX adaptation and equalization: adaptation configuration, CTLE/VGA/DFE status, DFE offset registers, slicer controls, DCC offset overrides, and SSM configuration expose tuning loops used to train the receive path.
- Analog cross-interface control: `ANA_XF_RX_*` fields bridge digital control into analog RX blocks for power, signal detect, VCO, DAC, termination, AFE, scope, IQ correction, loopback, and analog configuration registers.
- Raw-lane TX/RX interface control: `RAWLANE0_DIG_TX_*` and `RAWLANE0_DIG_RX_*` define PCS/PMA/FW request/acknowledge handshakes, lane loopback, link number, rate/width/context configuration, IRQ flags/clears, RTUNE request/acknowledge, and RX margin/recalibration controls.

## State and Persistence

These macros do not allocate memory and do not persist state in software. The persistent state is hardware register state in the GPU/display PHY after a caller writes fields described here.

Important state classes represented in the chunk:

- Latched hardware configuration: power-state register fields, context configuration fields, analog configuration registers, rate/width selections, EQ/DFE/CTLE tuning values, and termination codes.
- Transient handshake state: `REQ`, `ACK`, `VALID`, `RESET`, `RTUNE_REQ`, `RTUNE_ACK`, IRQ status, and IRQ clear fields.
- Status/readback state: CDR/VCO status, adaptation status, statistic counters, IQC status, analog status outputs, and final SSM codes.
- Self-clearing or side-effect-prone controls: IRQ clear fields, reset controls, start bits such as `START_SSM`, and clock/self-clear fields such as RX termination clock controls need hardware-specific ordering.

Because the macros encode only positions and masks, they do not enforce correct sequencing, valid enumerated values, or read/write permissions. Those requirements must be handled by the calling register programming code and by the hardware programming guide.

## Dependencies and Integration Points

This chunk depends on the larger generated DCN 3.2 register header set:

- Address headers provide register offsets.
- This `*_sh_mask.h` header provides field masks and shifts.
- Driver register helper macros combine both into read/modify/write operations.

Direct `rg` checks in this tree found includes of `dcn/dcn_3_2_0_sh_mask.h` from DCN 3.2 display, GPIO, IRQ, clock, resource, DMUB, and GMC code, but no direct references to the sampled CR4 C20 PHY field names outside this generated header. That suggests these exact fields are either unused in this source snapshot, reached through generated macro expansion patterns not visible by simple field-name search, or reserved for silicon support paths not present in the checked slice.

Integration-sensitive boundaries include:

- Display link bring-up and training, where PHY lane power, CDR, DFE, CTLE, and margining state affect link stability.
- DMUB/display firmware interactions, especially for fields named `FW_XF`, request/acknowledge, and lane-number/context controls.
- IRQ service integration for raw-lane TX interrupt mask, enable, status, and clear registers.
- Debug, diagnostics, and manufacturing/test flows that may use loopback, RTUNE, scope, statistic counters, analog test bus, and margining fields.

## Risks

- Generated-header drift: any mismatch between this header and the silicon register specification can silently program the wrong bits. Since callers trust the macros, mistakes usually surface as PHY bring-up failures, link instability, or hardware hangs rather than compiler errors.
- Reserved-bit writes: the chunk exposes many `RESERVED_*` masks. Callers should avoid writing reserved fields except as required by authoritative programming sequences.
- Override-enable hazards: many registers pair an override value with an override enable bit. Setting the value without enabling the override has no effect; enabling an override with stale or invalid value bits can force bad PHY behavior.
- Handshake ordering hazards: `REQ`/`ACK`, `RESET`, `VALID`, `RTUNE_REQ`/`RTUNE_ACK`, IRQ clear, and SSM start/done bits likely require ordered polling and timeout handling in consumers.
- Power-state and analog sequencing: fields that enable AFE, CDR, VCO, deserializer, DFE, clocks, and regulators can be unsafe if toggled out of order or while traffic is active.
- Width and signedness assumptions: masks are `L` constants and mostly 16-bit values. Callers should use unsigned register-width types and central field macros rather than ad hoc shifts to avoid sign/width mistakes.
- Lane naming: this chunk mixes `LANE3` and `RAWLANE0` groups. Code mapping logical display lanes to physical/raw lanes must not infer lane identity from only the textual prefix.
- Incomplete direct-use evidence: the exact field names in this chunk are not directly referenced elsewhere in the searched tree. Changes here may compile cleanly even if they break firmware-facing or future paths.

## Test Signals

Useful validation signals for code using this chunk include:

- Build coverage for all DCN 3.2 display objects that include `dcn_3_2_0_sh_mask.h`.
- Static checks that paired field masks and shifts are internally consistent, especially for generated changes: `(mask >> shift)` should match the expected field width and paired `_OVRD_EN` fields should not overlap their value fields.
- Register readback tests after programming power states, lane contexts, rate/width, and analog/EQ settings.
- Display link training across supported link rates, lane counts, and power transitions.
- Hotplug, suspend/resume, and runtime power-management tests that exercise RX power-state and clock recovery fields.
- IRQ tests for raw-lane TX status and clear fields, including timeout handling for request/acknowledge and RTUNE flows.
- Diagnostic tests for loopback, margining, CDR/VCO calibration, DFE/CTLE adaptation, statistic counters, and IQ calibration readbacks.
- Hardware fault logs or debugfs traces showing stuck `ACK`, incomplete `VCO_CAL_DONE`, failed `CDR_LOCK`, aborted SSM final status, or nonzero margin/adaptation errors.

## Research Notes

This is source-tree-aligned chunk research only. The final per-file synthesis should reconcile this with adjacent chunks because the CR4 C20 PHY register family begins before line 202390 and continues after line 204787. Adjacent chunks are needed to determine whether the `LANE3` and `RAWLANE0` naming transition is part of a repeated generated lane block or a distinct register-address block boundary.
