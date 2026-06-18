# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 73854-76243

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY control/status registers. It contains no executable logic; its exported interface is a set of preprocessor constants that describe bit positions and masks for indirect DPCS hardware registers.

The requested range contains 2,103 `#define` entries across 2,390 lines. It is within the CR3 raw-lane register space and spans the tail of raw lane 1, all raw lane 2, and the early/middle portion of raw lane 3. The range starts inside `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL`, continues through raw lane 1 FSM/IRQ/PMA/TX/RX/ATE fields, covers the complete raw lane 2 PCS/FSM/IRQ/PMA/TX/RX/ATE layout, then covers raw lane 3 PCS and FSM fields plus IRQ status/clear fields through the shift definitions for `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR`.

Although the repository path is under a local `ceph-client` source tree, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, direct MMIO accesses, or callbacks in this range. The API surface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position in a DPCS indirect register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- Raw lane 1 FSM tail: `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL` starts just before the chunk and is completed here, followed by fast RX DFE/bypass/reference-level/IQ calibration, AFE/DFE adaptation, fast supervisor/TX common-mode/TX RX-detect/RX power-up/RX VCO wait/RX VCO calibration controls, common MPLL and RCAL status, continuous RX calibration/adaptation/data/phase/AFE controls, `FAST_FLAGS`, CR register/memory lock bits, TX DCC flags/status, OCLA selection, TX EQ update flag, and RX IQ phase offset.
- Raw lane 1 IRQ controls: `RESET_RTN_REQ`, RX reset/request/rate/pstate/adaptation request/adaptation disable IRQ status bits, matching clear registers, `IRQ_MASK`, `IRQ_MASK_2`, lane transceiver-mode IRQs, PH2 calibration request/disable IRQs, serial loopback IRQs, DCC on-demand IRQ, and TX reset/request IRQ status and clear bits.
- Raw lane 1 PMA/TX/RX/ATE tail: PMA transfer fields for lane/supervisor/TX/RX override paths, RTUNE, MPHY override in/out, RX adaptation override out, TX FSM/clock/DCC/OCLA controls, RX FSM/LOS/data-enable/off-cancel/adaptation/UPCS OCLA controls, and late PCS ATE override registers for RX/TX manufacturing/test paths and master MPLL loop controls.
- Complete raw lane 2 PCS window: `DPCSSYS_CR3_RAWLANE2_DIG_PCS_XF_*` covers TX override inputs, TX PCS input/output mirrors, RX override inputs, RX PCS inputs/outputs, RX adaptation ACK/FOM, directed TX pre/main/post coefficient feedback, lane number and reserved words, ATE overrides, RX EQ delta/IQ override, TX/RX termination controls, RX clock output, RX EQ override controls, and PH2 calibration request/acknowledge.
- Complete raw lane 2 FSM/IRQ/PMA/TX/RX/ATE window: lane 2 repeats the same FSM, IRQ, PMA transfer, TX control, RX control, and late ATE/PCS register schema described for lane 1, with `RAWLANE2` names and offsets in the `0x3200` lane window.
- Raw lane 3 partial window: lane 3 starts at `PCS_XF_TX_OVRD_IN` and continues through PCS TX/RX override/input/output, RX adaptation, lane number, ATE/EQ/termination/PH2, FSM controls/status/calibration flags, CR lock, DCC/OCLA/EQ-update/RCAL/IQ fields, and IRQ status/clear registers through `RX_PSTATE_IRQ_CLR` shift definitions. The masks for that final register and the rest of lane 3 IRQ/PMA/TX/RX/ATE tail are outside this chunk.

Most fields are 16-bit DPCS register fields and use hexadecimal masks with an `L` suffix. Many control, status, clear, and mask registers are single-bit fields with a `RESERVED_15_1` mask; wider fields include full 16-bit words, packed override-value/override-enable pairs, state monitor bits, multi-bit IRQ mask words, and packed calibration/debug flags.

## Control Flow

This header has no runtime control flow. It participates in compile-time hardware-register description:

1. AMD display code for the DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Generated register tables or register-helper macros pair `ixDPCSSYS_*` offsets with the `__SHIFT` and `_MASK` constants from this file.
3. Runtime driver paths use those constants when reading, writing, updating, masking, clearing, or decoding raw-lane PHY registers during link bring-up, training, modeset, reset recovery, diagnostics, and interrupt handling.
4. The actual sequencing is performed by driver code, firmware, and hardware state machines; this chunk only names bit layouts.

The macros do not encode access permissions, reset values, polling order, self-clearing behavior, write-one-to-clear behavior, clock-domain restrictions, power-domain validity, or reserved-bit ownership.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 raw-lane registers:

- PCS state: TX/RX reset and request override paths, pstate/rate/width/MPLL selection fields, beacon/loopback/data-enable controls, PCS input/output mirrors, RX adaptation request/disable/ACK/FOM, directed TX coefficient feedback, lane-number fields, ATE overrides, RX equalization overrides, termination controls, RX clock output, and PH2 calibration handshakes.
- FSM state: manual FSM override controls, state and command readiness monitors, memory address monitor, fast startup/adaptation/calibration selectors, common MPLL and RCAL completion status, continuous calibration/adaptation selectors, CR locks, TX DCC flags/status, TX EQ update flag, OCLA probe selection, and RX IQ phase offset.
- IRQ state: latched RX/TX reset/request events, RX rate and pstate events, RX adaptation request/disable events, lane transceiver-mode events, PH2 calibration events, serial loopback events, DCC on-demand events, reset-return request bits, clear registers, and mask registers.
- PMA transfer state: lane and supervisor override inputs/outputs, TX/RX PMA handshake fields, RTUNE control, MPHY PWM/termination override in/out paths, and RX adaptation override outputs.
- TX/RX local control state: TX FSM and clock controls, TX DCC continuous status, OCLA/UPCS OCLA probe selection, RX FSM control, LOS masking, RX data-enable override timing, off-cancel continuous status, and adaptation continuous status.
- ATE/debug state: manufacturing/test override enables and values for RX/TX control paths, RX calibration/equalization fields, TX data/data-valid paths, master MPLL loop controls, and extra RX/TX override outputs.

Persistence is hardware-defined. Configuration and override fields generally remain until driver/firmware reprogramming, modeset/link-training changes, PHY power transitions, suspend/resume, GPU reset, ASIC reset, or display-engine reinitialization. Status, ACK, IRQ, calibration, handshake, and clear fields may be latched, sampled, self-clearing, write-one-to-clear, or valid only while the relevant lane power and clocks are active. This generated header does not specify those semantics.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_CR3_RAWLANE*` offsets for the registers described here.
- Raw lane 1 coverage starts mid-FSM at offsets around `0x3125`, continues through IRQ registers at `0x3140`-`0x315b`, PMA transfer at `0x3160`-`0x316c`, TX control at `0x3180`-`0x3184`, RX control at `0x31a0`-`0x31a5`, and late PCS/ATE fields at `0x31c0`-`0x31c8`.
- Raw lane 2 is the complete lane-local layout: PCS at `0x3200`-`0x321f`, FSM at `0x3220`-`0x323f`, IRQ at `0x3240`-`0x325b`, PMA at `0x3260`-`0x326c`, TX control at `0x3280`-`0x3284`, RX control at `0x32a0`-`0x32a5`, and late PCS/ATE at `0x32c0`-`0x32c8`.
- Raw lane 3 coverage starts with PCS at `0x3300`, covers FSM through `0x333f`, and reaches IRQ clear state around `0x334a`; later lane 3 IRQ masks, PMA, TX control, RX control, and late PCS/ATE fields continue after this range.
- AMD display link encoder, PHY, link-training, hotplug, modeset, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware and hardware state machines share ownership of many fields, especially reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane IRQs, and ATE/test overrides.

Behaviorally, this chunk sits below user-facing display code. It defines the bit layout needed to configure, observe, and debug CR3 raw lanes during display PHY operation.

## Risks And Edge Cases

- The constants are untyped preprocessor macros. A wrong shift or mask can compile cleanly while updating the wrong bit, corrupting reserved bits, or decoding status incorrectly.
- This is generated hardware metadata. Manual edits risk divergence from AMD's source register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL__FAST_RX_AFE_CAL__SHIFT` is in the previous chunk, while this chunk contains the reserved shift and masks.
- The chunk ends mid-register. `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` masks continue after line 76243.
- Repeated lane layouts are copy-sensitive. Lane 1, lane 2, and lane 3 names must stay paired with their matching offset windows; an off-by-one lane or `CR` instance mismatch can target a different physical lane.
- Status, clear, and interrupt-mask registers have similar names. Mixing status masks with clear or mask-register fields can lose events, leave stale events latched, or create repeated interrupts.
- PCS and PMA override fields can bypass normal hardware sequencing. Bad masks around reset, request, data-enable, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, or ATE controls can leave a lane in an unexpected electrical or protocol state.
- FSM fast-flow and calibration bits are sequencing-sensitive. Incorrect masks for fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO/common calibration or continuous calibration flags can cause link training failure, unstable links, stuck polling loops, or misleading debug dumps.
- Reserved masks are emitted alongside real fields. Consumers should not treat reserved bits as software-owned unless the hardware database or documentation explicitly allows it.

## Test Signals

Useful validation combines generated-header checks with hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated tables are initialized.
- Mechanically verify that every complete register group in this range has matching `__SHIFT` and `_MASK` entries, allowing the known start boundary in `RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL` and the end boundary in `RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR`.
- Cross-check all complete register names against `dpcs_4_2_2_offset.h`, especially lane-local spacing around `0x3100`, `0x3200`, and `0x3300`.
- Diff this generated slice against AMD's authoritative register database and nearby DPCS variants where the raw-lane schema is expected to match.
- Exercise DisplayPort and HDMI link bring-up across supported rates, widths, lane counts, and power states. Expected signals include stable link training, completed RX adaptation, no stuck reset/request handshakes, and no unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in PCS, FSM, IRQ, PMA, TX control, RX control, and ATE fields.
- Use register dumps or PHY debug traces during failures to confirm that RX adaptation ACK/FOM, directed TX coefficient feedback, DCC status, FSM state, CR lock, IRQ clear/mask bits, RTUNE handshakes, PH2 calibration, OCLA probes, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: OCLA and UPCS OCLA, serial loopback, RX adaptation debug, PH2 calibration, DCC on-demand IRQs, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_AFE_CAL` and the earlier raw lane 1 PCS/FSM fields. This chunk completes the lane 1 tail, fully covers raw lane 2, and starts raw lane 3 through the early IRQ clear registers. The next chunk should complete `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` and continue through the remaining lane 3 IRQ masks, PMA transfer, TX control, RX control, and late PCS/ATE fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR3 raw-lane registers.
