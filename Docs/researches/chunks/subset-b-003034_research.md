# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 71177-73847

## Scope

This chunk covers generated AMD NBIO 6.1 shift and mask macros for the `DWC_E12MP_PHY_X4_NS_X4_1` PCIe/PHY register namespace. The range starts inside the `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_1` register, where only the trailing mask definitions are included, and then covers the remainder of the lane-3 digital/analog RX and analog TX/RX mask section. It then transitions into raw common digital memory windows for common-memory banks.

The chunk contains 766 register comment blocks and 1,905 `#define` lines: 951 `__SHIFT` macros and 954 `_MASK` macros. The shift/mask imbalance is caused by the line-range boundary: lines 71177-71179 contain only masks for a register whose shift definitions are in the preceding chunk. The last line in this range is the comment marker for `DWC_E12MP_PHY_X4_NS_X4_1_RAWCMN_DIG_MEM_CMN4_B6_R21`; its `DATA` shift and mask definitions begin on the next line outside this chunk.

Major covered groups are:

- `LANE3_DIG_ANA_RX_*` control, calibration, AFE, slicer, scope, phase-adjust, and status bitfields.
- `LANE3_ANA_TX_*` analog transmit override, power, alternate-bus, ATB, vboost, termination, iboost, clock, and miscellaneous bitfields.
- `LANE3_ANA_RX_*` analog receive ATB, DCC, power, CDR/AFE, calibration mux, termination, slicer, and voltage-reference bitfields.
- `RAWCMN_DIG_MEM_CMN2_B0..B7_R0..R31` and `RAWCMN_DIG_MEM_CMN3_B0..B7_R0..R31`, each as full 256-register raw memory windows with a 16-bit `DATA` field.
- `RAWCMN_DIG_MEM_CMN4_B0..B5_R0..R31` and `RAWCMN_DIG_MEM_CMN4_B6_R0..R20` definitions, plus the boundary comment for `CMN4_B6_R21`.

This file section is a generated hardware register bitfield map. It has no C functions, structs, variables, persistent in-memory state, or executable control flow.

## Purpose

The purpose of this header chunk is to provide compile-time bitfield constants for AMDGPU code that needs to read, compose, or update NBIO 6.1 PCIe PHY registers. Each complete field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset.
- `<REGISTER>__<FIELD>_MASK`, the field mask after shifting.

The lane-3 PHY definitions describe how driver or firmware-support code can manipulate per-lane receiver and transmitter analog controls. The raw common-memory definitions expose uniform 16-bit data fields for indirect/common memory locations within the DesignWare PCIe PHY namespace.

## Important APIs, Types, and Macros

There are no callable APIs or types in this chunk. The important interface is the generated macro naming contract consumed by AMD register helpers:

- `REG_SET_FIELD(value, REGISTER, FIELD, field_value)` and related field-packing helpers expect the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` spellings used here.
- `REG_GET_FIELD(value, REGISTER, FIELD)` relies on the same constants to extract hardware fields from register values.
- `RREG32*` and `WREG32*` style accessors perform the actual MMIO/SMN reads and writes; this header only tells those accessors which bits are meaningful.
- Companion NBIO 6.1 headers provide the rest of the register contract: `nbio_6_1_offset.h` for register offsets, `nbio_6_1_default.h` for reset/default values, and `nbio_6_1_smn.h` for SMN-addressed registers.

Important bitfield families in this chunk include:

- RX digital analog calibration: `RX_ANA_CAL_MUXA_SEL`, `RX_ANA_CAL_MUXB_SEL`, `RX_ANA_CAL_LPFBYP_EN`, `RX_ANA_CAL_SHORT_EN`, `RX_ANA_SLICER_CAL_EN`, `RX_ANA_CAL_MODE`, and `RX_ANA_CAL_COMP_EN`.
- RX AFE and slicer tuning: attenuation/VGA gain, CTLE pole/boost, slicer even/odd controls, IQ phase adjust, IQ sense enable, DAC control, and self-clear-disable bits for update strobes.
- RX/TX status and measurement: `TX_ANA_CLK_SHIFT_ACK`, RX detect results, loopback status, loss-of-signal, calibration result, scope data, and VCO counter fields.
- TX analog overrides: loopback, reference generator, clock-divider, data/clock/serial enable, vboost, termination up/down codes, iboost, clock shift, alternate-bus source, and ATB measurement selection.
- RX analog overrides: DCC/AFE enable, loopback clock, LOS/LFPS enable, MPLL enable, CDR/AFE, power controls, calibration muxes, termination, slicer controls, and ATB/VREG measurement or override fields.
- Raw common memory: every `RAWCMN_DIG_MEM_*` register in this chunk uses `DATA__SHIFT 0x0` and `DATA_MASK 0xFFFFL`, indicating a full 16-bit payload window rather than named subfields.

## Control Flow

This chunk has no runtime control flow. The runtime sequence is imposed by callers that include this header:

1. Select a NBIO/PHY register address from the companion offset/SMN header.
2. Read or initialize a 16-bit or 32-bit register value using AMDGPU MMIO/SMN helpers.
3. Use this header's `__SHIFT` and `_MASK` constants, often through `REG_SET_FIELD` or `REG_GET_FIELD`, to compose or decode fields.
4. Write the resulting value back if the flow is configuring hardware, or inspect/poll decoded fields if the flow is measuring hardware state.

The bitfields themselves imply hardware sequencing constraints even though no sequence is implemented here. For example, calibration enable bits, DAC control enable bits, AFE update enable bits, phase-adjust clock bits, and override-enable bits are command/configuration strobes whose safe order must come from the PHY programming sequence, firmware tables, or ASIC-specific initialization code. Status fields such as `RX_ANA_CAL_RESULT`, `RX_ANA_LOS`, and `TX_ANA_CLK_SHIFT_ACK` are likely used for poll/verify phases after such writes.

## State and Persistence Behavior

No software state is stored by this header. The persistent state is in hardware registers:

- Configuration and override bits persist in the NBIO/PCIe PHY register file until reset, power transition, firmware reprogramming, or another driver write changes them.
- Self-clear or strobe-like fields may not retain the written value; examples include update-enable and phase-adjust clock controls with adjacent `*_SELF_CLEAR_DISABLE` bits.
- Status fields represent live hardware observations rather than driver-owned storage.
- Raw common memory windows expose 16-bit hardware memory/register payloads. Writes to these windows can persist in PHY common-memory state and may affect link training, calibration, or PHY behavior depending on the addressed bank/register.

The line range is lane-instance-specific: all named lane controls here are for `X4_1_LANE3`, not for other lanes or PHY instances. The same header contains analogous namespaces for other `X4_*` instances elsewhere, so callers must use the matching offset and mask namespace together.

## Dependencies and Integration Points

This header depends on the generated AMD register-header ecosystem rather than on ordinary C libraries. Its practical dependencies are:

- Include ordering with `nbio_6_1_offset.h`, `nbio_6_1_default.h`, or `nbio_6_1_smn.h` when code needs addresses or defaults as well as masks.
- AMDGPU register helper macros in the surrounding driver tree that know the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming convention.
- ASIC-specific NBIO/PCIe/PHY initialization, link-management, diagnostics, and firmware-loading code that decides which fields are legal to touch.
- Hardware documentation or generated register databases that define semantics for reserved bits and lane/common-memory programming order.

Repository search in the AMD driver subtree found these exact lane-3 and raw-memory macros defined in this header but no direct C consumer in the checked source. That suggests this region is part of a broad generated register surface where only a subset is used by open driver code, while the remaining masks are available for bring-up, debug, firmware-adjacent flows, or downstream code.

## Risks and Edge Cases

- Boundary risk: this chunk starts with masks for `LANE3_DIG_ANA_RX_VCO_OVRD_OUT_1` but not the corresponding shifts, and ends with only the comment for `RAWCMN_DIG_MEM_CMN4_B6_R21`. Any automated merger must reconcile neighboring chunks before treating register blocks as complete.
- Reserved-bit risk: many lane control registers include `RESERVED_15_*` masks. Driver writes should preserve reserved bits unless hardware documentation explicitly requires a value.
- Width risk: most lane PHY registers in this range are 16-bit-shaped masks. Using a 32-bit field helper is normal in AMDGPU, but values must still be constrained to the documented mask.
- Lane-instance risk: `X4_1_LANE3` masks are not interchangeable with `X4_0`, `X4_2`, `X4_3`, or other lane namespaces even when field names look identical.
- Hardware sequencing risk: changing RX CDR, AFE, DFE, slicer, LOS, clock, power, termination, vboost, or calibration override bits at the wrong point in link training or power management can destabilize PCIe links.
- Raw-memory risk: `RAWCMN_DIG_MEM_*` registers are opaque 16-bit data windows. They lack semantic field names, so writes without a generated table or hardware procedure are especially risky.
- Generated-header drift risk: hand-editing masks or shifts would break the generated register ABI and could silently misprogram hardware. Updates should come from the authoritative register-generation source.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Build coverage: any code including `nbio_6_1_sh_mask.h` should compile without macro redefinition or missing-field errors after regeneration or merge.
- Macro-pair integrity: each complete field should have matching `__SHIFT` and `_MASK` definitions, with known exceptions at chunk boundaries.
- Offset/mask consistency: fields used with `nbio_6_1_offset.h` or `nbio_6_1_smn.h` should share the same register prefix and ASIC version.
- Read/modify/write preservation: tests or code review should verify that writes preserve reserved bits and unrelated fields.
- Hardware smoke tests: PCIe link training, link speed/width reporting, reset/resume, runtime power management, and GPU discovery are the practical signals that PHY lane programming has not been damaged.
- Diagnostic tests: if these fields are exercised by bring-up or debug code, polling of calibration/status bits such as `RX_ANA_CAL_RESULT`, `RX_ANA_LOS`, `TX_ANA_CLK_SHIFT_ACK`, and VCO counter status should converge as expected.
