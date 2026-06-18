# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 52417-54805

## Scope

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment for the `DPCSSYS_CR2` register block. It covers 2,389 source lines and defines 2,105 preprocessor constants: 1,053 `__SHIFT` macros and 1,052 `_MASK` macros. The count mismatch is from the chunk boundaries: it starts after the first field of `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1` and ends before the final two masks of `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN`.

The content is declarative only. It contains no functions, structs, enums, branches, loops, runtime variables, allocation, locking, or file-backed persistence code. Its public surface is a large set of C preprocessor constants that describe bit positions and bit masks, mostly for 16-bit internal DPCS registers.

## Purpose

The header gives AMDGPU display code symbolic names for DPCS 4.2.2 hardware register fields. Driver code can combine these `*_SHIFT` and `*_MASK` constants with companion address macros from `dpcs_4_2_2_offset.h` and AMD register access helpers to perform read-modify-write operations without hard-coding bit locations.

This slice covers the CR2 raw common area, all CR2 raw lane 0 groups, and the beginning of CR2 raw lane 1. The common area describes MPLL state, TX calibration, SRAM initialization, OCLA/debug, supervisor analog overrides, PCS/FW IDs, always-on RTUNE values, SRAM bitline configuration, power-gating and supervisor overrides, VREF/resistor status, and reference-range/misc configuration. The lane area describes PCS/PMA crossbar overrides, finite-state-machine monitors and fast-sequence controls, IRQ status/clear/mask fields, TX/RX control fields, ATE override windows, and the start of the same PCS crossbar namespace for lane 1.

## Exported API Surface

There are no callable APIs or local types. The exported interface is the generated macro namespace. Most complete fields appear as a pair:

- `DPCSSYS_CR2_*__FIELD__SHIFT` gives the bit offset.
- `DPCSSYS_CR2_*__FIELD_MASK` gives the field mask.

Important macro families in this range:

- `DPCSSYS_CR2_RAWCMN_DIG_*`: CR2 common digital controls for MPLL state and bank selection, TX calibration code, SRAM initialization status, OCLA probe/clock controls, supervisor analog overrides, raw PCS and firmware identification, AON RTUNE RX/TX up/down values for indices 0 through 7, SRAM bitline read/write selection, AON power-gating and supervisor override inputs/outputs, VREF statistics, resistor override/readback fields, reference range override, and miscellaneous common configuration.
- `DPCSSYS_CR2_RAWLANE0_DIG_PCS_XF_*`: lane 0 PCS crossbar TX/RX override and status fields. These include TX/RX pstate, LPD, width, rate, MPLL selection and enable, master MPLL state override, reset/request override, DETRX, VBOOST/IBOOST, beacon, TX/RX acknowledge, RX adaptation request/disable/ack/FOM, RX data enable, loopback, LOS/LFPS, VCO/ref load, RX EQ and IQ delta overrides, TX/RX termination controls, lane number, reserved slots, ATE controls, TX pre/main/post direction hints, phase-2 calibration, and extended TX/RX valid/data override fields.
- `DPCSSYS_CR2_RAWLANE0_DIG_FSM_*`: lane 0 FSM override, memory-address/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration controls, fast supervisor and TX common-mode/RX detect controls, RX power-up/VCO wait/VCO calibration sequencing, common calibration status, continuous calibration/adaptation/data/phase/AFE controls, flags, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset readback.
- `DPCSSYS_CR2_RAWLANE0_DIG_IRQ_CTL_*`: lane 0 interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation request/adaptation disable, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback enable, DCC on-demand, TX reset, and TX request.
- `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_*`: lane 0 PMA crossbar fields for lane override in/out, supervisor override and PMA input, TX/RX PMA override outputs and inputs, lane RTUNE request/acknowledge, MPHY PWM/termination override inputs, MPHY output controls, and RX adaptation override output.
- `DPCSSYS_CR2_RAWLANE0_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANE0_DIG_RX_CTL_*`: lane 0 TX/RX controller controls for FSM timing, TX clock selection and enable, TX DCC continuous status, OCLA/UPCS debug enables, RX FSM enable and rate-change-in-P1 behavior, RX LOS masking, RX data-enable override counters, off-cancel/adaptation continuous status, and RX UPCS OCLA data/clock enables.
- `DPCSSYS_CR2_RAWLANE0_DIG_PCS_XF_ATE_*`: lane 0 ATE RX/TX override controls for rate, width, pstate, low-power detect, parallel/serial loopback, DETRX, VBOOST, IBOOST, TX beacon, TX async data, master MPLL loop, RX LOS/LFPS/adaptation continuous controls, VCO/ref load overrides, RX valid override, and extra TX data/async overrides.
- `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_*`, `FSM_*`, `IRQ_CTL_*`, `PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and `PCS_XF_ATE_*`: the start of the same lane register pattern for lane 1. This chunk covers lane 1 from PCS crossbar TX/RX override/status through FSM, IRQ, PMA, TX/RX control, ATE RX override, and most of ATE TX override.

## Register Areas Covered

The raw common group maps CR2-wide PHY controls and observability. The MPLL state register exposes off/force-on timing, A/B state selection, state override output enable, and bank selection. Common override registers expose calibration-disable, RTUNE request, HDMI mode, TX PWM clock selection/enable, supervisor analog override, power-gating, VREF/resistance, and reference-range control. The repeated AON RTUNE registers provide per-index RX, TX down, and TX up tuning values used by always-on common calibration logic.

The raw lane PCS crossbar groups map low-level signals between PCS-side lane logic and the surrounding PHY. TX fields cover pstate, low-power detect, width, rate, MPLL selection/enable, resets, requests, DETRX, VBOOST/IBOOST, beacon, async enable/data, TX acknowledgements, serial loopback, TX data enable, and master MPLL loop state. RX fields cover rate/width/pstate/LPD, adaptation request/disable/ack/FOM, RX data enable, loopback, LOS/LFPS thresholding, VCO/ref load, RX valid, RX EQ/IQ/phase calibration, and TX EQ direction feedback.

The raw lane FSM group describes internal sequencing and debug state. It exposes override control, micro-sequencer memory/status monitors, fast-path controls for RX startup and multiple calibration/adaptation phases, common calibration status for MPLL/RCAL, continuous RX calibration/adaptation stages, CR lock, TX DCC flags/status, OCLA debug selection, TX EQ update, and RX IQ phase offset.

The raw lane IRQ group provides per-event status, clear, and mask fields. It covers RX reset/request/rate/pstate/adaptation events, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request. The presence of separate `*_IRQ`, `*_IRQ_CLR`, and `IRQ_MASK` groups means consumers must use the hardware-defined status/clear/mask semantics rather than treating these as ordinary persistent configuration bits.

The PMA, TX_CTL, RX_CTL, and ATE groups expose lower-level bring-up, debug, and manufacturing controls. PMA crossbar fields map supervisor, TX, RX, RTUNE, and MPHY signals. TX/RX controller fields tune FSM timing, clocking, continuous DCC/adaptation/off-cancel status, LOS/data-enable counters, and OCLA capture. ATE fields provide forced values and override enables for link mode, loopback, RX detect, TX boost, beacon, async data, LOS/LFPS, adaptation continuation, VCO/ref load, and RX valid behavior.

## Control Flow And State Behavior

This file has no software control flow. Runtime behavior comes from AMDGPU display code that selects these masks and from the DPCS hardware state machines that consume or expose the underlying register bits.

The field names imply several hardware state patterns:

- Request/acknowledge handshakes: `REQ`, `RESET`, `ACK`, `TX_ACK`, `RX_ACK`, `RTUNE_REQ`, `RTUNE_ACK`, `ADAPT_REQ`, and `ADAPT_ACK` fields represent hardware state-machine transitions and their observed completion signals.
- Override gating: many fields appear as adjacent value and enable pairs such as `*_OVRD_VAL` with `*_OVRD_EN`. The value field is meaningful only when the matching override enable is asserted.
- Link mode and power transitions: `PSTATE`, `RATE`, `WIDTH`, `LPD`, `DATA_EN`, `MPLLB_SEL`, `MPLL_EN`, reset/return requests, clock selection, LOS masks, and power-gating fields encode lane bring-up, low-power entry/exit, and rate/lane-width changes.
- Calibration and adaptation: RTUNE values, VREF/resistor controls, VCO/ref load overrides, RX AFE/DFE/IQ/reference-level/phase calibration controls, CR lock, TX DCC status, TX EQ update, RX adaptation status/FOM, and RX EQ delta fields expose calibration commands and readbacks.
- Debug, validation, and manufacturing paths: OCLA, ATE, FSM memory/status monitors, IRQ masks/clears, loopback, MPHY PWM/termination, raw ID/FW ID, reserved slots, and raw PCS/PMA crossbar registers provide observability or forced settings that can bypass normal hardware sequencing.

No software state is persisted here. Hardware register contents persist only according to ASIC reset, power-domain, firmware, and display-engine sequencing. Reserved masks are explicitly present and should be preserved by read-modify-write users.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor. The semantic dependency is the DPCS 4.2.2 register database that generated this file and the companion `dpcs_4_2_2_offset.h` address map.

Within this source tree, `dpcs_4_2_2_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` together with `dpcs_4_2_2_offset.h`. The offset header maps the common CR2 raw registers around internal addresses `0x200b` onward in this slice, raw lane 0 PCS/FSM/IRQ/PMA/TX/RX/ATE groups from `0x3000` through the `0x30c*` extended fields, and lane 1 groups beginning at `0x3100`.

Integration points visible from the names include AMD DCN 3.15 display resource initialization, low-level DisplayPort/HDMI PHY programming, link training and rate/lane-width changes, TX/RX request-ack sequencing, power management and suspend/resume restore paths, RTUNE/VREF/resistor calibration, RX adaptation/equalization, TX DCC and TX EQ handling, hotplug/link recovery diagnostics, interrupt masking and clearing, OCLA debug capture, ATE/manufacturing override flows, and low-level PCS/PMA/MPHY diagnostics.

## Risks

- Generated-header drift is the main risk. A wrong shift or mask can silently target an adjacent hardware field during a register update.
- The slice starts and ends inside logical register groups. Merge/reconciliation should not treat `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1` or `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN` as fully described by this chunk alone.
- Many override value bits sit next to override-enable bits. Setting the value without the enable has no intended effect; leaving an enable asserted after debug, ATE, or recovery use can force hardware away from normal state-machine control.
- Calibration-sensitive fields such as RTUNE, VREF, resistor override, VCO/ref load, RX adaptation, RX IQ/phase calibration, TX DCC, TX EQ, and MPLL state/bank selection can destabilize link training or signal integrity if stale or misprogrammed.
- IRQ clear and mask fields are represented only as bit positions and masks; the header does not encode access semantics such as write-one-to-clear or read side effects.
- Reserved fields cover large bit ranges. Drivers should preserve reserved bits and avoid treating them as writable scratch space.
- Lane 0 and lane 1 groups are near-identical but have distinct address ranges. Copying a lane 0 register address or macro into a lane 1 path, or vice versa, can affect the wrong physical lane.
- Diagnostic, ATE, loopback, MPHY, and raw crossbar controls can interfere with normal display operation, hotplug handling, and power sequencing if used outside controlled bring-up or validation paths.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-integration oriented:

- Compile/preprocess AMDGPU DCN 3.15 code that includes `dpcs_4_2_2_sh_mask.h` through `dcn315_resource.c`.
- Static checks that every complete register group has matching `__SHIFT` and `_MASK` definitions; for this sliced chunk, expect 1,053 shifts and 1,052 masks because the selected lines cross group boundaries.
- Consistency checks against `dpcs_4_2_2_offset.h` so every complete register-family prefix in this chunk has a corresponding `ixDPCSSYS_CR2_*` address define.
- Generated-register comparison against adjacent DPCS versions such as 4.2.0 and 4.2.3 to catch accidental field-width, reserved-bit, suffix, or mask-format changes.
- Runtime display tests on hardware using DPCS 4.2.2: DisplayPort and HDMI link training, lane-count/rate changes, hotplug, suspend/resume, low-power entry/exit, TX/RX request-ack transitions, RTUNE/VREF/resistor calibration, RX adaptation/equalization, TX DCC, TX EQ, VCO/ref load behavior, interrupt status/clear/mask behavior, and link recovery.
- Debug/validation readbacks should show plausible transitions for common MPLL state, SRAM init, RTUNE values, power-gating overrides, PCS TX/RX acknowledgements, FSM status monitors, calibration flags, CR lock, TX DCC status, IRQ masks/clears, PMA RTUNE acknowledge, MPHY override outputs, TX/RX controller status, ATE override readback, and lane 0 versus lane 1 addressing.

## Chunk Notes For Merge

This document intentionally covers only lines 52417-54805 of `dpcs_4_2_2_sh_mask.h`. Earlier chunks should complete the beginning of `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1` and preceding MPLL/SSC common registers. Later chunks should complete the remaining masks for `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_ATE_TX_OVRD_IN` and continue lane 1 register families. The final merged per-file report should describe the whole file as a generated ASIC bitfield map for DPCS 4.2.2 rather than handwritten driver logic, with `dcn315_resource.c` and `dpcs_4_2_2_offset.h` as primary in-tree integration anchors.
