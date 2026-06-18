# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 95286-97717

## Scope

This chunk covers lines 95286-97717 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h`. It is a generated AMD DPCS 4.2.0 register bitfield header slice, not executable logic. The range contains 2,078 `#define` macros: 1,039 `__SHIFT` definitions and 1,039 matching `_MASK` definitions. Register blocks are separated by `//DPCSSYS_...` comments; 354 block comments appear in this range.

## Purpose

The chunk provides C preprocessor constants used by AMD GPU display/PHY driver code to compose, mask, and decode 16-bit DPCS CR4 register fields. The constants map hardware register field names to bit positions and masks for:

- `DPCSSYS_CR4_RAWLANE3_DIG_*`: raw lane 3 digital PCS, FSM, IRQ, PMA, TX, and RX control/status fields.
- `DPCSSYS_CR4_RAWAONLANE0_DIG_*`, `RAWAONLANE1`, and `RAWAONLANE2`: repeated always-on lane register fields for analog adaptation, DFE, signal-detect, DCC, MPLL, firmware config, and transceiver mode.
- The chunk ends at the comment for `DPCSSYS_CR4_RAWAONLANE3_DIG_AFE_ATT_IDAC_OFST`; the actual lane 3 always-on field macros are outside this chunk.

The header lets other code avoid hard-coded bit positions when programming DPCS hardware through MMIO/register-access helpers. It preserves the hardware register naming scheme, so integration code can use generated symbolic masks while still matching the ASIC register specification.

## Important Macros and Register Areas

There are no functions, structs, enums, or types in this slice. The API surface is the macro namespace itself:

- `...__FIELD__SHIFT` macros define the least-significant bit position of a field.
- `...__FIELD_MASK` macros define the field mask in the 16-bit register word, generally with an `L` suffix.
- `...__RESERVED_*` macros document reserved bit positions and masks. These are useful for validation and generated completeness, but driver writes should avoid setting reserved bits unless required by hardware documentation.

Key raw lane 3 groups:

- PCS transfer/control fields: `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, `LANE_NUMBER`, reserved registers, ATE override input, RX equalization overrides, termination control, RX phase-2 calibration, and lane data/clock override fields.
- FSM fields: override controls such as `FSM_JMP_ADDR`, `FSM_JMP_EN`, `FSM_CMD_START`, `FSM_OVRD_EN`, `FSM_BREAK`; monitor fields such as `MEM_ADDR`, `STATE`, `CMD_RDY`, `ALU_OVFLW`, `WAIT_CNT_EQ0`; fast calibration/adaptation flags including startup, AFE/DFE, bypass, reference-level, IQ, supervisor, TX common-mode, RX detect, VCO wait/calibration, continuous calibration/adaptation, DCC, VPHUD, and VREF status.
- IRQ fields: reset/request/rate/pstate/adaptation IRQ status and clear bits, `IRQ_MASK` and `IRQ_MASK_2`, lane transceiver mode IRQs, RX phase-2 calibration request/disable IRQs, loopback enable IRQs, DCC on-demand IRQ, and TX reset/request IRQs.
- PMA/PCS bridge fields: lane MPLL enable/state overrides, TX/RX request/reset/data-enable overrides, serial and parallel loopback overrides, RTUNE request/ack, MPHY PWM/async/termination controls, and RX adapt phase-adjust map override.
- TX/RX control fields: TX FSM wait and RX detection permissions by power state, TX clock enable/source and beacon wait, TX/RX OCLA fields, RX control FSM enable/rate-change behavior, LOS mask count, RX data-enable override counters, and continuous off-cancellation/adaptation status.
- ATE PCS override fields: RX rate/width/pstate/LPD and loopback overrides, TX pstate/LPD/width/rate/MPLL/async controls, detector RX request, vboost, iboost, beacon, serial loopback, master MPLL loop, and RX/TX override outputs.

Key always-on lane groups for lanes 0-2:

- Adaptation readback/calibration: `AFE_ATT_IDAC_OFST`, `AFE_CTLE_IDAC_OFST`, `RX_ADPT_IQ`, `RX_ADAPT_FOM`, DFE summer/phase/ref-level/data/bypass/error offsets, `RX_IQ_PHASE_ADJUST`, `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, and DFE taps 1-5.
- Lane calibration/status: MPLLA/MPLLB coarse tune, init power-up done, RX adaptation done, fast flags, common calibration MPLL/RCAL status, and MPLL disable bits.
- Signal-detect and analog RX controls: LOS mask control, signal-detect filter control, stats, RX override outputs for SQ threshold/response/weakkeep/polarity/enable, vrefgen, SQ output, term ACDC/term enable, LF/HF signal-detect enables, signal-detect calibration thresholds, HF/LF tune codes, and VREF pull-up.
- DCC and firmware configuration: RX DCC calibration ICM/IDF/QCM/QDF code registers for two banks, TX DCC bank address/data/control, MPLL background control, firmware MM/adaptation/calibration config, lane transceiver mode override/input, RX signal-detect config, and TX DCC config.

## Control Flow

This chunk has no runtime control flow. Control behavior is indirect: compiled driver code includes this header, selects a register from the companion offset header, then uses these masks/shifts to read-modify-write hardware fields or decode hardware status.

Typical use is expected to be:

1. Read a 16-bit or wider DPCS register through the AMD display register access layer.
2. Isolate a field with `value & FIELD_MASK`.
3. Shift it down with `FIELD__SHIFT` for interpretation, or shift a new value up and combine it with `FIELD_MASK` for writes.
4. Preserve unrelated and reserved bits during read-modify-write operations.

The raw lane 3 definitions expose active controls that affect link training, PMA handshakes, resets, clocks, calibration, loopback, IRQ masking/clearing, and override paths. The always-on lane definitions expose mostly analog calibration, readback, and static control fields replicated per lane.

## State and Persistence Behavior

The macros are compile-time constants and maintain no software state. The state they describe lives in hardware registers:

- Status/readback fields represent volatile hardware state, such as FSM state, IRQ status, calibration done/init flags, ACK bits, signal-detect outputs, DCC codes, and adaptation results.
- Control/override fields persist in hardware register state until changed by the driver, reset by hardware, or affected by power/domain reset behavior.
- Many fields are paired as override value plus override enable bits. Safe use requires programming both consistently; setting an override value without its enable bit, or leaving enable asserted after testing, can hold the PHY in a forced state.
- IRQ clear fields are likely write-one or write-trigger style integration points; callers must use the matching clear mask rather than treating clear registers as ordinary persistent storage.

Because this is a register-mask header, persistence semantics depend on the underlying ASIC register block, not on C storage in this file.

## Dependencies and Integration Points

This header depends only on the C preprocessor. Practical integration depends on surrounding AMDGPU display code:

- Companion generated register offset/address headers for DPCS 4.2.0 provide the actual register addresses. This file provides only shifts and masks.
- AMD display register helpers and macros consume `_MASK`/`__SHIFT` pairs when forming field writes and reads.
- DisplayPort/PHY/link-training paths may use lane PCS/PMA fields for reset sequencing, RX/TX request handshakes, adaptation, equalization, termination, rate/width/pstate selection, loopback, signal detect, and DCC calibration.
- Debug, bring-up, and manufacturing/ATE paths may use the numerous `ATE_*`, `OVRD_*`, `OCLA`, and FSM override fields.

The naming convention is the main contract. Any generated-name drift would break call sites that reference exact macro names.

## Risks and Edge Cases

- Reserved bit handling: the chunk defines reserved masks, but callers should not write reserved fields unless an ASIC sequence explicitly requires it. Read-modify-write helpers should preserve reserved bits.
- Field width correctness is critical. Examples include multi-bit fields for rates, widths, pstate, DFE/adaptation values, DCC calibration codes, RX signal-detect counters, and TX clock select. Incorrect masks can silently corrupt adjacent controls.
- Override controls can destabilize the PHY if left enabled after diagnostics or ATE paths. Value/enable bit pairs are common and should be reviewed together.
- IRQ status and clear definitions are easy to mix up because names differ only by `_CLR` or `_MSK`. Using a clear mask in a status read or masking the wrong interrupt could hide link events.
- This chunk starts mid-register (`RX_ADAPT_FOM`) and ends at the next lane's first comment. Whole-file research/merge must account for adjacent chunks to reconstruct complete lane coverage.
- Lane replication creates copy/paste risk. Lanes 0-2 always-on blocks are structurally parallel; differences should be treated as generated hardware-spec differences, not manually normalized without checking the source generator/spec.

## Test and Validation Signals

Useful validation for this chunk is mostly static and integration-oriented:

- Build coverage: any malformed macro or duplicate conflicting definition should surface through kernel/driver compilation units that include this header.
- Generated-pair checks: every `__SHIFT` in this range has a matching `_MASK` definition count-wise; this chunk has 1,039 of each.
- Mask/shift consistency checks: for non-reserved fields, verify masks line up with the declared shift and expected field width from the ASIC spec.
- Register smoke tests on supported hardware: link training, lane power transitions, RX/TX reset/request handshakes, interrupt status/clear behavior, calibration completion, and DCC/signal-detect readbacks should work when code uses these constants.
- Debugfs or tracing that reads DPCS fields can confirm that decoded values remain plausible for lane number, FSM state, IRQ status, adaptation done flags, and calibration codes.

## Chunk Notes for Merge Lane

This is a partial view of `dpcs_4_2_0_sh_mask.h`. The later merge lane should combine this with neighboring chunks to describe the full generated header. For this chunk specifically, the major source-tree-aligned signal is that it documents DPCS CR4 lane 3 raw digital control/status fields and most of always-on lane 0-2 digital analog/calibration field masks.
