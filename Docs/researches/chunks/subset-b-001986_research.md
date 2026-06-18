# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 139180-141615

## Scope And Purpose

This chunk is a generated register field shift/mask slice from AMD DCN 3.2 C20 PHY control-register metadata. It covers the tail of raw lane 0 RX calibration skip/status fields, almost all visible `C20_PHY_CR2_RAWLANE1` digital TX/RX PCS, firmware, PMA, IRQ, control, and FSM fields, and the beginning of the corresponding `C20_PHY_CR2_RAWLANE2` definitions through the start of `RAWLANE2_DIG_RX_FW_XF_OVRD_IN_1`.

The file does not define executable C functions or runtime state machines. Its purpose is to provide preprocessor constants that encode bit positions and bit masks for 16-bit PHY control/status registers. Driver code elsewhere can include this header and build register read-modify-write operations without hard-coding numeric fields. The repeated pattern is:

- A register comment such as `//C20_PHY_CR2_RAWLANE1_DIG_TX_PCS_XF_OVRD_IN_1`.
- One `__SHIFT` macro per named field in that register.
- One `_MASK` macro per named field, including reserved ranges, using hexadecimal constants with an `L` suffix.

The chunk contains 311 register comment groups and 2,125 `#define` lines. Most fields are lane-local copies of a common PHY schema; raw lane 2 starts with the same TX/RX PCS, firmware, PMA, IRQ, and control layout as raw lane 1.

## Register Areas Covered

### Raw Lane 0 Tail

The first visible lines complete the previous raw lane 0 block with RX calibration and margining controls:

- `DIG_FSM_SKIP_RX_CTLE_STARTUP_CAL`
- `DIG_FSM_SKIP_RX_ATT_STARTUP_CAL`
- `DIG_FSM_SKIP_RX_MARGINING`
- `DIG_FSM_RX_CAL_STATUS`

These single-bit fields expose skip switches for startup CTLE/attenuation/margining stages and a reset-calibration-done status bit. They are continuation context for an earlier raw lane 0 chunk.

### Raw Lane 1 TX PCS/Firmware Interface

`C20_PHY_CR2_RAWLANE1_DIG_TX_PCS_XF_*` describes the PCS-facing TX transfer interface:

- Lane override/input registers carry RX-to-TX parallel loopback, TX-to-RX serial loopback, lane link number, reset, request, pstate, low-power detect, data enable, polarity invert, clock-ready, beacon, MPLL enable, master MPLLA/MPLLB state, receiver-detect request, clock/lane deskew, recalibration force/skip, and context-select fields.
- Output registers expose ACK and DETRX result signals, with override-enable companions where the register is an override path.
- `CNTX_CFG_0..2` encode lane TX operating context: rate, width, wide-transfer alignment, MPLLB selection, VREG/VBOOST/IBOOST, KR driver enable, off-cannon continuous mode, DCC control range, DCC bypass, termination control, misc byte, and TX unique ID.

`C20_PHY_CR2_RAWLANE1_DIG_TX_FW_XF_*` is the firmware-facing version of the TX transfer interface. It has reset/request handshakes, pstate/rate/MPLLB/MPLL override fields, master PLL state, TX clock enable, deskew controls, lane number, and ACK status.

### Raw Lane 1 TX IRQ And Control

The TX interrupt group exposes mask, enable, status, and clear fields for:

- TX rate changes, TX request, TX reset.
- RX-to-TX parallel loopback enable/disable.
- RTUNE, termination control, and lane transceiver mode events.
- Optional block-ACK behavior for TX request IRQs.

The TX control group includes FSM policy and calibration/status fields:

- `DIG_TX_CTL_FSM_CTL` enables RX detect in power states P2/P1/P0s/P0 and enables internal IRQ sources for lane rate, width, MPLLB select, misc, termination, DCC control/bypass, and calibration done.
- Clock select, off-cannon continuous status, rate IRQ acknowledge, 10-bit termination code, firmware power-up done, and MPLLA/MPLLB restore-calibration enable fields.

### Raw Lane 1 TX PMA Interface

`C20_PHY_CR2_RAWLANE1_DIG_TX_PMA_XF_*` bridges TX digital control to PMA/supervisor state. It includes:

- Lane MPLLA/MPLLB enable input/output override values and enables.
- RX-to-TX loopback override controls.
- Supervisor MPLLA/MPLLB state override/input fields.
- TX request/reset override output fields and ACK input.
- RTUNE request/ACK controls.

These constants are used when the driver or firmware needs to coordinate lane power, PLL selection, PMA handshakes, and tuning across digital and analog PHY boundaries.

### Raw Lane 1 RX PCS/Firmware Interface

`C20_PHY_CR2_RAWLANE1_DIG_RX_PCS_XF_*` mirrors the transfer-interface style for the RX side:

- Override/input fields cover reset, request, pstate, low-power detect, data enable, polarity invert, CDR SSC enable, adaptation request/in-progress, margin IQ, margin VDAC, margin-in-progress, margin error clear, recalibration bank select, loopback select, and context select.
- Output/ACK registers expose handshake completion.
- `CNTX_CFG_0..8` describe RX equalization and CDR context: attenuation, VGA gain, CTLE offset/boost/pole/zero, AFE rate and bias controls, DFE tap 1, DFE bypass, adaptation select/mode, misc nibble/byte, delta IQ, CDR VCO config, DCC control range, rate, reference load, DIV16P5 clock enable, CDR PPM max, width, VCO load value, signal-detect LF/HF thresholds, LFPS filter enable, termination, DCC/VREG bypass, continuous adaptation/off-cannon modes, and unique ID.

`C20_PHY_CR2_RAWLANE1_DIG_RX_FW_XF_*` exposes firmware-facing RX controls and status: reset/request, pstate/low-power/rate/width/DFE-bypass override fields, adaptation request, delta IQ, ACK, RX-valid override, adaptation ACK/FOM, TX pre/main/post direction hints, RX clock control, and ACK output.

### Raw Lane 1 RX IRQ And Control

The RX IRQ group provides mask, enable, status, and clear fields for:

- RX request, rate, pstate, adaptation request/disable, reset, and termination-control events.
- Margining events: global, IQ start, VDAC start, error clear, init, and finish.
- Optional request block-ACK behavior.

The RX control group contains lane observable and programmable state:

- Termination code, off-cannon/adaptation continuous status, adaptation mode/select, PPM drift plus valid bit, CDR detect status, PMA misc control, adaptation mode override/enable, adaptation FOM values, reference errors, IQ left/right measurements, phase-adjust linear/map values and update values, margin IQ/VDAC deltas, margin status/error, FSM IRQ enables, rate IRQ ACK, IQ code read/write registers, and phase-adjust update enable.

These macros are central for code that tracks RX link health, calibration quality, and eye-margining status.

### Raw Lane 1 FSM And Calibration Controls

The raw lane 1 FSM block exposes debug/control hooks and many calibration shortcuts:

- `DIG_FSM_FSM_OVRD_CTL`, `FSM_JMP_BANK`, `FSM_CTL_0`, memory breakpoints, memory address monitor, and status monitor fields allow firmware/debug code to override or observe the PHY finite-state machine.
- `FW_CFG_STAGE` and `FW_SCRATCH_0..11` provide firmware configuration-stage bits and 16-bit scratch storage.
- `CR_LOCK` locks register or memory access. `FAST_SUP`, `FAST_TX_*`, and `FAST_RX_*` enable fast supervisor, TX, RX, VCO, power-up, startup-calibration, and continuous-adaptation paths.
- Many `SKIP_*` registers let firmware skip selected TX/RX calibration stages: TX DCC rate/startup/continuous/range, RX AFE/DFE/DFE-ext/IQ/phase/DCC/signal-detect/VGEN/VGA/CTLE/ATT/margining, continuous phase/AFE/reference-level/VGA adaptation, half/full-rate startup, bypass/error/buffer/slicer startup, DCC data/bypass/phase startup, adaptation reload, DFE coarse/fine adaptation, and RX DCC range rate/startup calibration.
- `DIG_FSM_RX_CAL_STATUS` exposes reset-calibration done for the lane.

These definitions are high-risk because they can bypass analog calibration and directly alter PHY bring-up sequencing if used incorrectly.

### Raw Lane 2 Beginning

The chunk then starts the same register pattern for `C20_PHY_CR2_RAWLANE2`:

- TX PCS lane override/input/output, context config, and firmware interface groups.
- TX IRQ mask/enable/status/clear groups and TX control/PMA groups.
- RX PCS override/input/output and context config groups through `CNTX_CFG_8`.
- RX firmware override group `RX_FW_XF_OVRD_IN_0` and the start of `RX_FW_XF_OVRD_IN_1`.

The range ends at line 141615 after `C20_PHY_CR2_RAWLANE2_DIG_RX_FW_XF_OVRD_IN_1__PSTATE_MASK`; the remaining masks for that register and subsequent raw lane 2 RX firmware/IRQ/control/FSM fields continue in the next chunk.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or exported runtime APIs in this chunk. The important interface is the macro naming contract:

- Register base: `C20_PHY_CR2_RAWLANE<N>_DIG_<BLOCK>_<REGISTER>`
- Field shift: `<REGISTER>__<FIELD>__SHIFT`
- Field mask: `<REGISTER>__<FIELD>_MASK`
- Reserved masks: `<REGISTER>__RESERVED_<high>_<low>_MASK`

Consumer code typically combines these constants through AMDGPU register helpers such as field get/set macros or read-modify-write helpers from adjacent AMD display driver code. The header itself is dependency-free C preprocessor data; it relies on consumers to pair these shifts/masks with the corresponding address definitions from the matching DCN 3.2 register offset header.

## Control Flow And State Behavior

No control flow executes in this file. The control-flow meaning is encoded in hardware state fields:

- Handshake fields (`REQ`, `ACK`, `RESET`, `RX_VALID`, `DETRX_RESULT`) represent PHY micro-protocols between PCS, firmware, PMA, and lane supervisors.
- Override-enable companions (`*_OVRD_EN`) are a recurring two-part state model: one field supplies the forced value and another field authorizes using it instead of natural hardware/firmware control.
- IRQ mask/enable/status/clear groups model event flow: an event source is enabled, possibly masked, latched in a status register, and cleared through a matching clear bit.
- Context configuration groups persist lane operating parameters such as rate, width, PLL choice, equalization, CDR, DCC, termination, and unique IDs until rewritten or reset by the hardware/FSM.
- FSM scratch, lock, jump, breakpoint, and monitor registers expose persistent debug/firmware state inside the PHY FSM.

Because these are MMIO-backed hardware fields, persistence is hardware-lifetime persistence rather than file or software persistence. Values survive in the PHY register block until reset, power transition, firmware rewrite, or explicit driver write. Reserved bits must be preserved by read-modify-write code.

## Dependencies And Integration Points

This chunk integrates with the AMDGPU display stack as generated register metadata:

- It belongs under `drivers/gpu/drm/amd/include/asic_reg/dcn`, tying it to DCN 3.2 display hardware.
- It should be used alongside generated register address headers for the same ASIC/IP revision; masks alone are insufficient to access hardware.
- DisplayPort/PHY bring-up, link training, clock/power management, firmware handoff, diagnostics, and interrupt handling code may reference these constants indirectly through register abstraction macros.
- The lane-numbered duplication means multi-lane code can select raw lane 0, 1, 2, and later lanes by using the corresponding macro family rather than one generic indexed definition.

The file has no includes in this slice and no direct dependency on Linux kernel APIs. Its practical dependencies are the hardware register specification, the generator that produced it, and AMD display driver helper macros that know how to apply shifts and masks.

## Risks And Edge Cases

- Register drift risk: these constants must match the ASIC register specification exactly. A wrong shift or mask can corrupt neighboring control bits, including reserved bits or calibration controls.
- Reserved-bit preservation risk: many registers include large `RESERVED_*` masks. Driver writes that compose full values instead of read-modify-write preserving reserved fields can trigger undefined PHY behavior.
- Override misuse risk: fields with `*_OVRD_EN` can force reset, request, PLL, rate, width, data-enable, margining, adaptation, and PMA handshake behavior. Debug or workaround code using these in production paths can break link bring-up or recovery.
- Calibration skip risk: the FSM skip/fast fields can bypass DCC, AFE, DFE, CTLE, VGA, phase, IQ, signal-detect, and margining stages. These are useful for firmware workarounds and test modes but can reduce signal integrity if enabled unintentionally.
- IRQ polarity/clear risk: status and clear registers are separate macro families. Using a status mask against a clear register with a slightly different field name, or clearing by writing a full register value, can lose events.
- Chunk-boundary risk: line 141615 cuts through `RAWLANE2_DIG_RX_FW_XF_OVRD_IN_1`; the complete raw lane 2 RX firmware/control analysis needs the following chunk.
- Generated-duplication risk: raw lane 1 and raw lane 2 definitions are highly repetitive. Manual edits or partial regeneration can create lane-to-lane inconsistencies that compile cleanly but misprogram one physical lane.

## Test Signals

There are no unit tests local to this header. Useful validation signals are compile-time, generated-header, and hardware/integration oriented:

- Kernel build coverage catches missing macros, duplicate names, syntax errors, or consumers referring to renamed fields.
- Generator regression tests or diffs against the ASIC register database should verify every `__SHIFT` and `_MASK` pair, including reserved ranges, across raw lane copies.
- Static checks can verify masks agree with shifts and field widths, for example single-bit fields use `1 << shift`, multi-bit masks are contiguous, and reserved masks do not overlap named fields.
- Hardware smoke tests should cover display link bring-up across affected lanes, link training, hotplug/retrain, low-power transitions, firmware power-up done, RX/TX IRQ handling, and recovery after reset.
- PHY diagnostics should exercise RX margining/adaptation, TX/RX loopback, RTUNE, DCC, PLL select, rate/width changes, and calibration skip/fast paths only under controlled test conditions.

## Unresolved Cross-Chunk References

This chunk starts after raw lane 0 FSM definitions have already begun and ends before raw lane 2 RX firmware/control/FSM definitions complete. The merge lane should combine this with adjacent chunks before drawing whole-file conclusions about the complete C20 PHY register surface.
