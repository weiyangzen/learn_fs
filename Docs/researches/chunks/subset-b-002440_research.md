# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 133879-136141

## Scope

This chunk is the final slice of the generated AMD DPCS 4.2.3 shift/mask header. It contains 1,667 `#define` constants across 588 register-field groups. In this range every emitted constant is a `__SHIFT` definition; the matching `_MASK` definitions for this tail section are outside this requested slice or absent because the file ends at line 136141.

The range starts mid-register in `C20_PHY_CR1_LANEX_DIG_ANA_XF_RX_STAT_OUT_1`, covers the remaining CR1 lane analog RX, raw-lane TX/RX PCS/PMA/FSM/IRQ/control, always-on raw-lane TX/RX calibration/adaptation, and then ends with two pipe-message-bus address blocks for `C20_PHY_LANE0_PIPE1_UPCSLANE_PIPE_LPC_PHY_*` and `C20_PHY_LANE1_PIPE1_UPCSLANE_PIPE_LPC_PHY_*`. It terminates at the file's `#endif`.

This is declarative hardware metadata only. There are no functions, structs, enums, global variables, includes, local storage, branches, locks, or allocations in this chunk. Although the local repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display-driver register metadata, not Ceph filesystem code.

## Purpose

The purpose of this slice is to publish symbolic bit positions for C20 PHY CR1 DPCS indirect registers. Display driver code combines these `__SHIFT` macros with compatible field masks and register offsets to construct read-modify-write operations, decode status fields, and poll hardware state without hard-coding bit numbers.

The represented hardware is the display PHY/DPCS lane-control surface for a C20 PHY CR1 instance. The fields describe analog RX controls, TX/RX PCS handshake and override signals, PMA/MPLL lane signals, firmware cross-interface signals, interrupt status/mask/clear bits, FSM acceleration and skip controls, TX/RX calibration banks, RX adaptation results, margining/debug controls, and vendor-defined pipe-lane controls for DisplayPort/HDMI/FRL-style link operation.

## Important Definitions

The interface exposed by this chunk is the generated macro namespace:

- `C20_PHY_CR1_<REGISTER>__<FIELD>__SHIFT`: low bit index of `FIELD` in the named hardware register.
- `RESERVED*__SHIFT`: generated layout markers for unused or reserved bit regions. These document bit placement but should not be treated as software-owned knobs.
- Address-block comments such as `addressBlock: c20_phy_lane0_pipe1_rdpcspipemsgbusind`: generator markers showing which indirect register block the following field groups belong to.

Important register families in the chunk:

- `C20_PHY_CR1_LANEX_DIG_ANA_XF_RX_*`: analog receive status, AFE override, and `RX_ANA_CREG00` through `CREG11` fields. These include RX analog sample selectors, DFE/deserializer/loopback enables, signal-detect high/low frequency enables, clock/power/word-clock overrides, DCC/AFE power controls, termination controls, VCO/VREG measurement and boost controls, ATB measurement muxing, slicer/scope settings, signal-quality controls, common-mode selections, and reserved analog control registers.
- `C20_PHY_CR1_RAWLANEX_DIG_TX_PCS_XF_*`: TX PCS lane override/input/output and context configuration. Fields cover RX-to-TX parallel loopback, TX-to-RX serial loopback, lane link number, reset/request handshakes, pstate, low-power detect, data enable, invert, clock-ready, beacon, MPLL enable, master MPLLA/MPLLB state, detection request, clock/lane deskew, recalibration force/skip, bypass encode/decode, width/rate, and firmware request/ack signals.
- `C20_PHY_CR1_RAWLANEX_DIG_TX_FW_XF_*`: firmware-facing TX override/input/output signals for reset, request, rate, pstate, termination, lane mode, training transitions, and lane number.
- `C20_PHY_CR1_RAWLANEX_DIG_TX_IRQ_CTL_*` and `TX_CTL_*`: TX interrupt mask/enable/status/clear bits and TX control/status fields for rate, reset, request, loopback enable/disable, RTUNE, termination, lane transceiver mode, FSM control, clock selection, off-channel continuous status, term code, firmware power-up done, and MPLLA/MPLLB restart calibration.
- `C20_PHY_CR1_RAWLANEX_DIG_TX_PMA_XF_*`: TX PMA lane/supervisor override and input/output fields for MPLLA/MPLLB enable, RX-to-TX loopback, PMA reset, rate, RTUNE, termination control, and lane RTUNE programming.
- `C20_PHY_CR1_RAWLANEX_DIG_RX_PCS_XF_*`: RX PCS override/input/output and context configuration. Fields include reset, request, pstate, rate, data enable, invert, MPLL state, low-power detect, signal-detect, CDR lock, clock-ready, adaptation request/stop/ack, polarity, invalid request, calibration done, calibration select, pipe width, loopback, SERDES PCLK enable, recalibration controls, deskew controls, margining starts, link number, PMA async data, CDR frequency, and phase-adjust update/status.
- `C20_PHY_CR1_RAWLANEX_DIG_RX_FW_XF_*`: RX firmware interface for reset/request/rate/pstate, adaptation controls, margining, termination, loopback, TX coefficient direction feedback, clock control, and output status.
- `C20_PHY_CR1_RAWLANEX_DIG_RX_IRQ_CTL_*` and `RX_CTL_*`: RX interrupt masks/enables/status/clears plus RX control/status fields for reset/request/rate/pstate/adaptation, margining phases, termination code, off-channel and adaptation continuous status, adaptation mode/selection, PPM drift, CDR detector status, PMA misc control, adaptation figures of merit, reference errors, IQ left/right controls, phase-adjust linear/map fields, RX margin deltas/status/errors, FSM control, rate IRQ ack, IQ code read/write, and phase-adjust update enable.
- `C20_PHY_CR1_RAWLANEX_DIG_FSM_*`: firmware/FSM override, jump-bank, control, breakpoint, monitor, scratch, lock, debug, fast-path, and skip-control fields. This group is large and controls or reports fast bring-up modes, TX DCC calibration skip/fast options, RX startup/adaptation/power/VCO acceleration, and many fine-grained RX calibration/adaptation skip knobs.
- `C20_PHY_CR1_RAWLANEAONX_DIG_TX_*`: always-on TX firmware state, SRAM recovery, continuous calibration counters, startup/continuous algorithm controls, fast flags, high-power protection, lane transceiver mode, initial power-up done, MPLLA/MPLLB DCC bank codes, calibration done flags, bank selection, and live DCC code readbacks.
- `C20_PHY_CR1_RAWLANEAONX_DIG_RX_*`: always-on RX startup calibration/adaptation algorithm controls, continuous algorithm controls, fast flags, signal-detect/VGEN/AFE/reference/DFE offset fields, DCC and IQ calibration banks, calibration done/bank select/readback fields, IQ control, adaptation limits and results, ATT/VGA/CTLE/DFE tap banks, DFE tap-1 offset banks, adaptation done, TX equalization direction polarity and thresholds, `ADPT_CTL_0` through `ADPT_CTL_28`, IQ margin range, CDR detector/recovery controls, RX override input/output, signal-detect filters, PMA override output, and RX input/output status.
- `C20_PHY_LANE[0-1]_PIPE1_UPCSLANE_PIPE_LPC_PHY_*`: pipe-message-bus lane 0 and lane 1 control blocks. These expose RX margin controls, elastic buffer controls, RX polarity/equalization/recalibration/status controls, TX deemphasis/preset/FS/LF/margin/swing controls, HDP TX controls, encode/decode bypass, vendor-defined register address/data windows, custom SERDES/HDMI/width/LFPS/debug controls, TX EQ override coefficient fields for generation 1 and generation 2, HDP EQ override coefficients, and recalibration/deskew override controls.

## Control Flow

There is no executable control flow in this header. Its effective runtime use is:

1. AMD display code includes the matching DPCS 4.2.3 offset and shift/mask generated headers for a DCN/DPCS hardware generation.
2. Register helper macros choose an indirect register offset such as a `C20_PHY_CR1_*` or `C20_PHY_LANE*_PIPE1_*` register from the offset header.
3. The caller shifts values by the `__SHIFT` constants in this file and applies the compatible mask from the generated register metadata or helper layer.
4. The driver performs MMIO or indirect CR/message-bus accesses through AMD display-core register helpers.
5. Hardware FSMs, firmware interfaces, calibration engines, and PHY analog blocks interpret the written values or expose status back to software.

Field names in this range imply sequencing requirements that are implemented elsewhere: reset/request/ack handshakes, pstate/rate changes, calibration bank programming, DCC/IQ/VCO calibration, TX/RX adaptation, margining start/finish/error handling, IRQ clear/mask handling, loopback setup, deskew/recalibration override, and vendor-defined register reads/writes.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes hardware register fields whose state is owned by the DPCS/PHY block.

State represented here includes:

- Sticky or transient TX/RX IRQ state, clear bits, mask bits, and enable flags.
- Control-plane override values and enable selectors for PCS/PMA/FW/analog paths.
- Link state inputs and outputs such as reset, request, ack, pstate, rate, width, lane number, data enable, invert, signal detect, CDR lock, MPLL state, loopback, polarity, and clock readiness.
- Firmware/FSM scratch, debug, breakpoint, jump-bank, lock, fast-mode, and calibration-skip state.
- Calibration and adaptation banks for TX MPLLA/MPLLB DCC, RX DCC, IQ, AFE, CTLE, VGA, DFE taps, reference levels, slicers, VGEN, signal detect, and CDR recovery.
- Pipe-lane protocol controls for RX margining, elastic buffer behavior, TX coefficients, vendor-defined read/write address/data windows, HDMI/custom SERDES rate selection, FRL/DP mode flags, LFPS timing, recalibration, and deskew.

Persistence duration is hardware-defined. Some fields may hold until overwritten, link reset, PHY reset, power gating, suspend/resume, or ASIC reset. Other fields may be read-only status, write-one-to-clear, self-clearing commands, sticky latch state, or banked calibration values. The header does not encode access permissions or side effects, so consumers must follow the hardware programming sequence associated with each field.

## Dependencies And Integration Points

The main dependency is the matching generated offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`

These `__SHIFT` macros are only meaningful when paired with the corresponding DPCS 4.2.3 register offsets and masks. A different DPCS version can share names while moving fields, changing widths, or changing reserved bits.

In-tree integration is through AMD display core code for DCN 3.1.6-era hardware, especially resource/register tables that include DPCS 4.2.3 generated headers. The direct known include site is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`

Runtime consumers are link encoder, PHY bring-up, DisplayPort/HDMI/FRL link training, DP alternate-mode/USB-C lane handling if present, diagnostics, hardware validation, compliance tests, and debug tooling. The pipe-message-bus lane 0/1 blocks integrate with per-lane vendor-defined PHY controls, while the `RAWLANEX` and `RAWLANEAONX` groups integrate with lane-common PCS/PMA/FSM/firmware paths.

## Risks And Edge Cases

- Shift-only chunk boundary: this requested slice contains only `__SHIFT` constants. Any code or analysis that assumes adjacent `_MASK` constants are present in the same chunk will be incomplete.
- Header/offset skew: pairing these DPCS 4.2.3 CR1/C20 shifts with a different offset header can compile while programming the wrong indirect register or wrong bit field.
- Untyped preprocessor macros: values are not range-checked. Callers must ensure values fit the intended field width before shifting and masking.
- Reserved-field writes: generated `RESERVED` shifts document layout, but whole-register writes that do not preserve reserved bits can disturb undocumented PHY behavior.
- Override-pair hazards: many fields have a value plus an `*_OVRD_EN` selector. Enabling an override with a stale or mismatched value can force bad reset, pstate, rate, loopback, signal-detect, MPLL, TX/RX data, analog, or calibration state.
- Handshake and command semantics are external. `REQ`, `ACK`, `DONE`, `START`, `CLR`, `RESET`, `CAL_*`, `MARGIN_*`, `RECAL_*`, and vendor-defined address/data fields need ordering, polling, and timeout handling in consuming code.
- Lane repetition can hide copy/paste errors. Lane 0 and lane 1 pipe blocks are intentionally parallel, and many raw-lane bank groups repeat across bank numbers; a single wrong namespace or offset can cause lane-specific failures.
- Debug/test controls can leak into production state. FSM fast/skip flags, SRAM recovery, OCLA/debug/breakpoint fields, LB/loopback controls, margining starts, DCC bank writes, VDR address/data windows, and HDP EQ overrides can destabilize normal link training if left enabled.
- Access-class ambiguity: this header does not distinguish read-only status from writeable control or write-one-to-clear fields. Register helpers and hardware-specific programming guides must provide that behavior.

## Test Signals

Useful validation for this chunk is mostly build, static generation, and hardware integration coverage:

- Build AMDGPU display code paths that include `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`, especially DCN316 resource code, to catch missing or renamed macros.
- Static generator checks that every `C20_PHY_CR1_*` and `C20_PHY_LANE[0-1]_PIPE1_*` field group in this slice has the matching register offset in `dpcs_4_2_3_offset.h`, and that reserved and non-reserved fields do not overlap within each register.
- Cross-version diffs against authoritative AMD generated DPCS 4.2.3 data and nearby DPCS 4.2.x headers, focusing on CR1/C20 lane repetition, banked calibration fields, and the lane 0/1 pipe-message-bus blocks.
- Hardware link bring-up tests across DP/HDMI/FRL rates and lane counts, including hotplug, modeset, suspend/resume, power-gating, and link recovery after errors.
- PHY diagnostics that inspect TX/RX request/ack/status, pstate/rate/width, CDR lock/detector status, MPLLA/MPLLB calibration done, TX/RX DCC banks, RX IQ/AFE/CTLE/VGA/DFE adaptation values, margining status/errors, and signal-detect calibration.
- Interrupt tests that assert mask/enable/status/clear behavior for TX reset/request/rate/loopback/RTUNE/termination/lane-mode and RX reset/request/rate/pstate/adaptation/margining/termination events.
- Regression signals include blank displays, lane-specific failures, rate-specific instability, repeated link retraining, stuck PHY IRQs, bad RX adaptation figure-of-merit, failed VCO/DCC/IQ calibration, margining errors, resume failures, or failures isolated to pipe lane 0 or lane 1 controls.

## Cross-Chunk Notes

The full-file reconciliation lane should merge this with adjacent chunks before making file-level claims. This chunk starts after the beginning of `C20_PHY_CR1_LANEX_DIG_ANA_XF_RX_STAT_OUT_1`, so the first register group is incomplete at the top boundary. It ends at `#endif`, so it is the terminal chunk for `dpcs_4_2_3_sh_mask.h`.
