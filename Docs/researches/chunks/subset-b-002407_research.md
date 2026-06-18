# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h chunk subset-b-002407

Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h` lines 51028-53443.

## Purpose

This chunk is part of AMDGPU's generated DPCS 4.2.3 register shift/mask header. It defines preprocessor constants for fields inside `DPCSSYS_CR2` raw-lane digital control registers. The constants describe the bit positions (`__SHIFT`) and bit masks (`_MASK`) used by C code that programs or decodes DisplayPort/PHY lane control registers through AMD display hardware access helpers.

The chunk starts inside raw lane 0's transmit-control OCLA and receive-control sections, contains the full repeated field map for raw lanes 1 and 2, and ends inside raw lane 3's `DIG_PCS_XF_TX_PCS_IN` definition. It is therefore a chunk-level partial view of a generated, larger per-ASIC register contract rather than a self-contained subsystem.

## Important APIs, Types, and Defines

There are no C functions, structs, enums, storage objects, or callable APIs in this chunk. Its public surface is a large set of `#define` macros. The dominant pattern is:

- `DPCSSYS_CR2_RAWLANE*_...__FIELD__SHIFT`: zero-based bit offset for a register field.
- `DPCSSYS_CR2_RAWLANE*_...__FIELD_MASK`: mask value for the same field, usually 16-bit wide and suffixed with `L`.
- Comment lines such as `//DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_TX_OVRD_IN`: register names that group the following field definitions.

Within the requested line range there are 2148 `#define` entries: 1079 shift definitions and 1069 mask definitions. Lane coverage is partial at the boundaries and complete in the middle: `RAWLANE0` contributes the tail of its register map, `RAWLANE1` and `RAWLANE2` contribute the full repeated maps in this chunk, and `RAWLANE3` begins at the end.

Major register families visible in the chunk:

- `DIG_PCS_XF_*`: PCS crossbar/interface fields for TX/RX request, reset, power state, low-power detect, width, rate, MPLL selection/enables, detect-RX request, acknowledgements, data-enable overrides, loopback enables, equalization values, lane number, training direction values, RX phase calibration, and ATE override paths.
- `DIG_FSM_*`: lane FSM override, status, memory-address monitor, fast calibration/adaptation flags, common calibration status, CR register/memory locks, TX DCC flags/status, and OCLA enables.
- `DIG_IRQ_CTL_*`: per-lane interrupt status, clear, and mask bits for RX/TX reset/request, rate, pstate, adaptation request/disable, lane transceiver mode, phase-calibration request/disable, serial loopback, and DCC on-demand events.
- `DIG_PMA_XF_*`: PCS-to-PMA interface and override fields for lane MPLL state, supervisor state, TX/RX requests/resets, beacon/async/data enables, loopback, retune, MPHY PWM/termination/asynchronous controls, and RX adaptation IQ phase map override.
- `DIG_TX_CTL_*` and `DIG_RX_CTL_*`: TX/RX control FSM timing, clock selection, DCC continuous status, OCLA hooks, LOS masking, data-enable override timing, and continuous adaptation/off-cancellation status.

Representative field groups include `PSTATE`, `LPD`, `WIDTH`, `RATE`, `MPLLB_SEL`, `MPLL_EN`, `RESET`, `REQ`, `ACK`, `OVRD_EN`, `*_OVRD_VAL`, `*_OVRD_EN`, `ADAPT_AFE_EN`, `ADAPT_DFE_EN`, `VCO_LD_VAL`, `REF_LD_VAL`, `RX_LOS_THRSHLD`, `IBOOST_LVL`, and reserved bit ranges.

## Control Flow

The header itself has no executable control flow. It supplies compile-time constants consumed by driver code elsewhere. Runtime control flow is indirect:

1. Display or PHY management code selects a DPCS register address using companion register-offset headers and the target raw lane.
2. That code uses these `__SHIFT` and `_MASK` macros to compose, update, or decode bitfields.
3. Hardware register writes affect lane FSM behavior, PCS/PMA handshakes, RX/TX override paths, calibration requests, interrupt masks/clears, or debug capture enables.
4. Hardware register reads are decoded with the same masks to inspect acknowledgements, FSM status, interrupt status, calibration status, equalization state, and similar hardware state.

The repeated lane layout is the main control-flow signal: higher-level code can apply the same register programming sequence across lanes by selecting the lane-specific macro namespace. The incomplete lane 0 and lane 3 regions mean any whole-file analysis must reconcile this chunk with adjacent chunks before inferring complete per-lane coverage.

## State and Persistence Behavior

This chunk declares no software state and persists nothing by itself. The state represented by the macros lives in GPU display hardware registers. The defined fields can influence persistent-in-hardware behavior until changed by the driver, reset by hardware, or lost through power/reset events.

Important hardware-state categories exposed by this chunk:

- Override state: many `*_OVRD_VAL` plus `*_OVRD_EN` pairs can force request, reset, rate, width, power, equalization, loopback, async, data-enable, or PMA interface values.
- Handshake state: `REQ`, `ACK`, `RESET`, `DETRX_REQ`, `DETRX_RESULT`, `RX_ADAPT_ACK`, and PMA in/out fields encode lane bring-up and cross-block coordination.
- Calibration and adaptation state: fast RX calibration/adaptation bits, phase calibration, common MPLL/RCAL status, DCC flags, RX IQ phase offset, FOM, EQ, VCO, and reference load fields.
- Interrupt state: IRQ status and clear registers are expected to be write/read side-effectful in hardware, while mask registers control which events propagate.
- Debug/observability state: OCLA fields, FSM monitors, memory-address monitor, and CR locks expose diagnostic or low-level control behavior.

Reserved fields are explicitly masked in the generated header. Driver code should preserve or avoid touching reserved bits unless hardware programming guides require a specific value.

## Dependencies and Integration Points

This file depends only on the C preprocessor and the include guard established at the top of the full header. It is normally paired with register offset/address headers from the same `asic_reg/dpcs` generated family. The masks are meaningful only with the matching DPCS 4.2.3 register addresses and hardware generation.

Integration points include:

- AMDGPU display core and DCN/PHY code that performs read-modify-write operations against DPCS registers.
- Register helper macros that conventionally combine `_MASK` and `__SHIFT` values for field insertion or extraction.
- ASIC-specific include selection paths that ensure DPCS 4.2.3 masks are used only for compatible hardware.
- Debug, validation, and bring-up code that may force ATE, OCLA, loopback, calibration, interrupt, or FSM override paths.

The macro names encode both the block (`DPCSSYS_CR2`) and lane (`RAWLANE0` through `RAWLANE3`). Code using these macros must not mix them with offsets from a different CR instance, lane namespace, or ASIC revision.

## Risks and Edge Cases

- Generated-header drift: if the matching address header or hardware spec changes without regenerating this file, code may write the correct-looking field into the wrong bit position.
- Boundary incompleteness: this chunk starts after lane 0 TX-control definitions and ends before lane 3 is complete. Chunk consumers must not treat this report as full-file or full-lane coverage.
- Reserved-bit writes: masks such as `RESERVED_15_*_MASK` identify bits that should generally be preserved. Clearing or setting full registers without read-modify-write can corrupt reserved state.
- Override enable/value pairing: many fields use separate value and enable bits. Setting an override value without the corresponding enable, or leaving an enable asserted after test/bring-up flows, can produce subtle lane failures.
- Interrupt clear semantics: `*_IRQ_CLR` fields are likely write-one-to-clear style hardware controls. Generic bitfield writes could accidentally acknowledge events.
- Lane copy/paste hazards: lane 1 and lane 2 definitions are highly repetitive. Driver code that manually selects macro names can silently target the wrong lane namespace.
- Width assumptions: most masks in this region are 16-bit, but the full header also contains wider fields. Helper code must use the declared mask width rather than assuming every DPCS register is identically sized.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Build coverage for all AMDGPU configurations that include DPCS 4.2.3 headers; undefined macro failures catch namespace or generation mismatches.
- Static checks that each non-reserved field has a matching `__SHIFT` and `_MASK` definition and that masks align with shifts.
- Register access tests or hardware bring-up logs showing lane 1 and lane 2 TX/RX PCS/PMA sequences complete with expected `ACK`, `RX_ADAPT_ACK`, calibration done, and no unexpected IRQ bits.
- Runtime traces around link training, lane power transitions, DCC/calibration, retune, and loopback paths to confirm override enables are asserted and cleared in expected order.
- Debugfs or tracepoint reads of DPCS registers, decoded using these masks, compared against hardware documentation for DPCS 4.2.3.
- Negative tests for interrupt-mask/clear paths where individual RX/TX request, reset, pstate, adaptation, and phase-calibration IRQ bits are masked, generated, cleared, and re-read.

## Chunk Notes

The source is generated-style register metadata. Research conclusions should be merged with neighboring chunks before producing the final per-file report, especially for the incomplete `RAWLANE0` and `RAWLANE3` sections and for address-block context outside this line range.
