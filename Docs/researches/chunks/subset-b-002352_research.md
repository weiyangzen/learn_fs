# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 35751-38153

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header segment. It contains register-field metadata for AMDGPU display PHY hardware, not executable driver logic. The public surface is a large set of C preprocessor constants that give each hardware register field a bit position (`__SHIFT`) and a bit mask (`_MASK`) for use by AMD display register helpers.

The requested range covers 2,403 lines with 2,094 `#define` entries: 1,046 shift macros, 1,084 mask macros, and 309 register-comment markers. It starts in the middle of `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`: the initial `TX_FAST_DCC_CAL` and `RX_FAST_DCC_CAL` shift definitions are in the previous chunk, while this chunk begins with `RX_FAST_VPHUD_CAL`. It then covers the tail of CR1 raw lane 2 FSM, IRQ, PMA, TX/RX control, and ATE fields; a broad CR1 raw lane 3 PCS/FSM/IRQ/PMA/TX/RX/ATE block; a full CR1 raw always-on lane 0 block; and the beginning of CR1 raw always-on lane 1 through `RX_ADPT_DFE_TAP5`. The final line is only the comment for `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN`, so that register's field definitions belong to the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, runtime variables, includes, locks, allocations, or direct MMIO calls in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` defines the least-significant bit for a field in a DPCS indirect register.
- `<REGISTER>__<FIELD>_MASK` defines the field mask used when extracting, composing, or updating that field.

Important register families in this chunk are:

- CR1 raw lane 2 FSM tail: `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `OCLA`, `TX_EQ_UPDATE_FLAG`, `CMNCAL_RCAL_STATUS`, and `RX_IQ_PHASE_OFFSET` expose fast calibration/adaptation flags, CR register/memory lock state, TX duty-cycle-correction flags and status, on-chip logic analyzer selection, TX equalization update state, common RCAL status, and RX IQ phase offset.
- CR1 raw lane 2 IRQ controls: `DPCSSYS_CR1_RAWLANE2_DIG_IRQ_CTL_*` defines reset-return request, RX/TX reset and request IRQs, RX rate/pstate/adaptation IRQs, clear registers, IRQ masks, lane transceiver-mode IRQs, phase-2 calibration IRQs, serial loopback IRQs, and DCC on-demand IRQ state.
- CR1 raw lane 2 PMA/PCS and controller controls: `PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and late `PCS_XF_ATE_*` groups describe PMA lane/supervisor/TX/RX override and status paths, MPHY override paths, RTUNE control, RX adaptation override output, TX FSM and clock control, DCC continuous status, RX LOS and data-enable override timing, OFFCAN/adaptation continuous status, OCLA probes, ATE RX/TX override inputs, master MPLL loop, and secondary RX/TX override banks.
- CR1 raw lane 3 PCS crossbar: `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*` covers TX and RX override inputs/outputs, PCS input/output status, rate/width/pstate/low-power detect fields, MPLL selection and enablement, data enable and async TX controls, loopback/beacon/DETRX controls, RX adaptation acknowledgement and figure-of-merit, directed TX pre/main/post cursor feedback, lane number, ATE overrides, RX EQ delta/IQ controls, TX/RX termination controls, RX EQ override controls, and phase-2 calibration request/acknowledge fields.
- CR1 raw lane 3 FSM and IRQ controls: `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*` and `IRQ_CTL_*` repeat the raw-lane state-machine, calibration, OCLA, DCC, IQ phase, event, clear, and mask model for lane 3.
- CR1 raw lane 3 PMA and TX/RX controller controls: `PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` expose lane/supply/TX/RX/MPHY handshakes, RTUNE controls, RX adaptation override output, TX FSM/clock/DCC status, RX FSM/LOS/data-enable controls, continuous calibration/adaptation status, and UPCS/OCLA observability.
- CR1 raw lane 3 ATE and secondary override banks: `PCS_XF_ATE_RX_OVRD_IN`, `ATE_TX_OVRD_IN`, `ATE_TX_OVRD_IN_1`, `ATE_RX_OVRD_IN_1`, `ATE_RX_OVRD_IN_2`, `ATE_RX_OVRD_IN_3`, `RX_OVRD_OUT_2`, and `TX_OVRD_IN_2` define manufacturing or deep debug override surfaces for RX/TX lane state.
- CR1 raw always-on lane 0: `DPCSSYS_CR1_RAWAONLANE0_DIG_*` includes AFE IDAC offsets, RX adaptation IQ/FOM/ATT/VGA/CTLE/DFE tap values, DFE even/odd VDAC and reference-level offsets, RX phase adjust values, MPLLA/MPLLB coarse tuning, initial power-up done bits, fast flags, slicer controls, common MPLL/RCAL status, adaptation control words, MPLL disable, fast flags 2, TX/RX overrides, LOS mask and signal-detect filtering, statistics, RX override readbacks, signal-detect calibration and codes, VREF generator enable, calibration codes, RX DCC calibration I/Q code banks, TX DCC bank address/data/continuous control, MPLL bandgap control, signal-detect output override/input, firmware mode/adaptation/calibration config, lane transceiver-mode override/input, RX signal-detect config, and TX DCC config.
- CR1 raw always-on lane 1 start: `DPCSSYS_CR1_RAWAONLANE1_DIG_*` begins the same always-on lane pattern from AFE offsets through RX adaptation DFE taps 2-5, but the slicer-control fields and later lane 1 always-on registers continue in the next chunk.

Most masks are 16-bit-style constants with an `L` suffix, matching the DPCS indirect register width used by these PHY control and status blocks. Several multi-field masks cover reserved bit ranges; consumers must preserve these according to the register access semantics implemented outside this header.

## Control Flow

This header has no runtime control flow. It is compile-time data used by the display driver:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this shift/mask header.
2. Version-specific register, shift, and mask tables are built with generated names and token-pasting helper macros.
3. Runtime display code uses register helpers such as read, write, get, set, and update operations with those tables.
4. Actual sequencing for lane bring-up, PLL and MPLL selection, link training, RX adaptation, DCC calibration, interrupt handling, ATE/debug override use, power management, and diagnostics lives in AMDGPU display code and hardware/firmware state machines.

The macros here only describe bit layout. They do not encode access type, reset value, read-only/write-only behavior, write-one-to-clear behavior, self-clearing bits, polling order, timeout requirements, or clock and power domain validity.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR1 DPCS registers:

- Raw lane 2 and lane 3 FSM state includes fast startup/adaptation/calibration flags, common MPLL/RCAL status, continuous calibration/adaptation state, CR lock state, TX DCC state, OCLA selection, TX EQ update state, and RX IQ phase offset.
- Raw lane 2 and lane 3 IRQ state includes RX and TX reset/request events, RX rate and pstate events, adaptation request/disable events, phase-2 calibration request/disable events, lane transceiver-mode changes, serial loopback enable events, DCC on-demand events, matching clear fields, and mask fields.
- Raw lane 2 and lane 3 PMA/PCS state includes TX/RX reset, request, pstate, rate, width, low-power detect, MPLL select and enable, master MPLL state, receive-detect controls, loopback and beacon controls, data-enable and async data paths, adaptation acknowledgements, FOM readback, directed TX coefficient feedback, termination controls, RTUNE control, MPHY control, supply power state, and PMA-facing ACK/data/valid/readback paths.
- Raw lane 2 and lane 3 TX/RX controller state includes TX FSM control, TX clock control, DCC continuous status, RX FSM control, LOS mask timing, RX data-enable override timing, OFFCAN continuous state, adaptation continuous state, and OCLA/UPCS debug observability.
- Raw always-on lane 0 and lane 1 state includes adaptation results and tuning values for AFE, CTLE, VGA, DFE taps, slicers, phase adjust, FOM, ATT, common calibration status, MPLL coarse tuning, initial power-up, signal-detect, VREF, DCC calibration code banks, TX DCC bank access, firmware configuration, and lane transceiver mode.

Persistence is determined by hardware. Configuration fields generally remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver initialization rewrites them. Status, ACK, IRQ, statistic, calibration, and handshake fields may be sampled, latched, clear-on-write, self-clearing, or valid only while the relevant DPCS lane, always-on lane, common clock, and power domains are active. This generated header does not specify those semantics.

## Dependencies And Integration Points

The direct compile-time dependency is the C preprocessor. The semantic dependency is AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_*` addresses. For the CR1 instance covered here, this chunk aligns with offsets such as `0x3238` for `RAWLANE2_DIG_FSM_FAST_FLAGS`, `0x324d` and `0x324e` for raw lane 2 IRQ mask registers, `0x3300` and later for raw lane 3 PCS transfer registers, `0x4000` and later for raw always-on lane 0, and `0x4100` and later for raw always-on lane 1.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`, tying this generated register contract to DCN 3.1.5 resource initialization.
- AMD display link encoder, PHY, clock-source, link-training, power-management, interrupt, diagnostics, and manufacturing/test code consume the generated constants indirectly through register tables and helper macros rather than open-coded bit numbers.
- Firmware and hardware state machines interact with the same fields, especially for PMA/PCS handshakes, RX adaptation, signal detect, DCC calibration, RTUNE, MPLL status, fast calibration flows, and low-level lane IRQ latching.

Behaviorally, this range sits below user-facing display policy. It defines bit positions and masks needed when the driver or firmware configures CR1 raw lanes 2 and 3, observes low-level lane state, handles lane interrupts, and reads or overrides raw always-on lane calibration and adaptation state.

## Risks And Edge Cases

- These are untyped preprocessor constants. Incorrect shifts or masks can compile cleanly while writing adjacent fields, preserving the wrong reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register source, the companion offset header, firmware expectations, and silicon behavior.
- The chunk starts and ends inside logical groups. `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` is missing its first two shift definitions in this slice, and `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` is only a trailing comment with its field definitions in the next slice.
- The range mixes raw lane 2 tail definitions, full raw lane 3 definitions, raw always-on lane 0 definitions, and the start of raw always-on lane 1. Consumers must pair each macro with the correct CR1 offset and lane/register table.
- Lane 2 and lane 3 register names are highly repetitive. A generator, merge, or manual-copy error can affect only one lane while adjacent lane definitions appear valid, causing asymmetric link-training or lane-count failures.
- IRQ status, clear, and mask fields have similar names. Confusing status, clear, and mask registers can drop events, leave latched IRQ bits uncleared, or produce repeated low-level interrupts.
- Override registers often contain both override-enable bits and override-value bits. Setting values without enables, or leaving enables asserted after ATE/debug use, can force the PHY away from normal state-machine control.
- PMA/PCS, termination, RTUNE, MPHY, DCC, MPLL, signal-detect, VREF, slicer, and DFE fields affect electrical link behavior. Wrong masks can surface as blank displays, unstable links, compliance failures, retraining loops, or misleading hardware debug traces.
- Reserved masks are explicit but not safe scratch space. Register update code must use the correct helper semantics so reserved bits are not corrupted.

## Test Signals

Useful validation combines generated-header checks with hardware-oriented display testing:

- Build AMDGPU display support for DCN 3.1.5 code that includes `dpcs_4_2_2_sh_mask.h` through `dcn315_resource.c`. Missing, renamed, or malformed macros should fail in generated register/shift/mask table initialization.
- Statically verify that complete register groups in this chunk have matching `__SHIFT` and `_MASK` definitions, while allowing the known boundary exceptions for `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` at the start and `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` at the end.
- Cross-check every complete register group in the slice against `dpcs_4_2_2_offset.h`, especially the CR1 raw lane 2 tail, raw lane 3 repeated window, raw always-on lane 0 window, and raw always-on lane 1 start.
- Diff generated DPCS 4.2.2 fields against adjacent hardware versions or sibling lanes where layouts are expected to match. Repeated lane 2/lane 3 and always-on lane 0/lane 1 patterns are strong signals for generator drift.
- Exercise DisplayPort and HDMI link bring-up across lane counts, rates, power states, and hotplug sequences. Watch for stable link training, correct RX adaptation completion, correct PMA/PCS acknowledgements, no stuck DCC or calibration status, and no unexpected raw lane IRQs.
- Run modeset, stream disable/enable, suspend/resume, and GPU reset flows to catch persistence and reinitialization issues around FSM, IRQ, PMA/PCS, signal-detect, DCC, MPLL, and always-on lane calibration state.
- Use register dumps or PHY debug traces on failures to confirm that IRQ status/clear/mask bits, RX adaptation FOM/tap values, DFE offsets, slicer controls, signal-detect calibration, VREF generator state, DCC code banks, RTUNE fields, and MPLL status decode with the expected masks.
- Exercise diagnostic or manufacturing paths where available: OCLA, UPCS_OCLA, ATE RX/TX override banks, MPHY override paths, loopback, directed TX coefficient feedback, phase-2 calibration, signal-detect output override, firmware config registers, and TX DCC bank access.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` and earlier raw lane 2 PCS/FSM fields. This chunk finishes that raw lane 2 tail, covers raw lane 3 and raw always-on lane 0, and begins raw always-on lane 1. The next chunk should start with the field definitions for `DPCSSYS_CR1_RAWAONLANE1_DIG_RX_SLICER_CTRL_EVEN` and continue the rest of CR1 raw always-on lane 1. The later merge/reconciliation lane should combine these boundaries before making whole-file claims about the complete DPCS 4.2.2 register map.
