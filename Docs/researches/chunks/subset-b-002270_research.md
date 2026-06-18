# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 26788-29265

## Purpose

This chunk is generated AMD DPCS 3.1.4 register-field metadata for the display PHY/controller side of AMDGPU. It contains no executable C logic; it exports preprocessor constants that describe bit shifts and bit masks for fields inside DPCS indexed registers. Consumers pair these macros with matching `ixDPCSSYS_*` offsets from `dpcs_3_1_4_offset.h` and AMD display register helpers to read, write, and update individual hardware fields.

The requested range contains 2,107 `#define` lines and 371 register-group comment markers. It starts inside the tail of `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`, then covers the rest of the raw lane 2 PCS tail. Most of the chunk covers raw lane 3 digital PCS, FSM, IRQ, PMA, TX control, RX control, and ATE override fields. The final section covers the start of CR1 always-on lane metadata for `RAWAONLANE0`, `RAWAONLANE1`, and `RAWAONLANE2`, ending at the beginning of `DPCSSYS_CR1_RAWAONLANE2_DIG_LANE_XCVR_MODE_OVRD_IN`.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, clearing, or updating that field.

Major register groups in this chunk:

- `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_*` tail: ATE RX VCO/reference-load override fields, RX valid override output, and TX serial-loopback/data/async-data override fields for raw lane 2.
- `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*`: raw lane 3 PCS transmit and receive control surfaces. These include TX/RX pstate, low-power detect, width, rate, MPLL selection/enables, master MPLL state overrides, reset/request handshakes, detection request/result bits, vboost/iboost, TX beacon, ACK/status outputs, RX loss-of-signal thresholds, RX adaptation request/continuous/off-candidate control, VCO/reference-load status, RX equalization and DFE coefficients, TX pre/main/post cursor direction fields, lane-number reporting, termination controls, phase-2 calibration, ATE overrides, loopback, and async data gating.
- `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*`: raw lane 3 micro/FSM monitor, override, status, fast-sequence, calibration, adaptation, continuous-calibration, flag, CR-lock, TX DCC, OCLA, TX EQ update, CMN calibration, and RX IQ phase-offset fields.
- `DPCSSYS_CR1_RAWLANE3_DIG_IRQ_CTL_*`: IRQ status, clear, mask, and return-request fields for RX reset/request/rate/pstate/adaptation events, lane transceiver mode changes, RX phase-2 calibration request/disable, lane RX-to-TX serial loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR1_RAWLANE3_DIG_PMA_XF_*`: PMA lane/supervisor/TX/RX override and PMA input/output bridge fields, lane RTUNE control, MPHY override, and RX adaptation override output.
- `DPCSSYS_CR1_RAWLANE3_DIG_TX_CTL_*` and `RX_CTL_*`: lane-local TX/RX FSM control, TX clock control, TX DCC continuous status, RX LOS mask count, RX data-enable override, off-candidate/adaptation continuous status, and OCLA/debug fields.
- `DPCSSYS_CR1_RAWAONLANE0_DIG_*`, `RAWAONLANE1_DIG_*`, and beginning of `RAWAONLANE2_DIG_*`: always-on lane calibration/status/configuration metadata. These blocks repeat per lane and cover AFE/CTLE/DFE offset readbacks, RX IQ/adaptation/FOM, RX phase adjustment, coarse MPLL tuning, initial power-up status, RX adaptation tap results, slicer controls, common calibration statuses, adaptation-control registers, MPLL disable, TX/RX overrides, LOS and signal-detect filter controls, PMA squelch/termination/sigdet/vrefgen overrides, signal-detect calibration codes, RX DCC calibration codes, TX DCC bank address/data/continuous-enable, MPLL background delay control, firmware adaptation/calibration config, and lane transceiver mode override/input fields.

The companion offset header maps representative register names in this range to indexed addresses: lane 3 PCS begins at `ixDPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` `0x3300`; lane 3 IRQ mask fields sit around `0x334d` and `0x334e`; lane 3 PMA bridge fields begin at `0x3360`; lane 3 TX/RX control blocks begin at `0x3380` and `0x33a0`; ATE PCS fields resume at `0x33c0`; always-on lane 0, 1, and 2 blocks begin at `0x4000`, `0x4100`, and `0x4200`.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code and the hardware programming model:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`.
2. AMD display register-list macros token-paste register and field names into register, shift, and mask tables.
3. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed-register variants to access DPCS registers through those tables.
4. The numeric values in this chunk determine which bits are touched when the display stack controls PHY lane state, link rate/width, lane power/reset/request handshakes, adaptation/calibration, IRQ masks and clears, PMA overrides, DCC, signal-detect, LOS, and diagnostics.

The macros do not define ordering rules. Consumers must still follow hardware sequencing for lane reset, request/ack handshakes, MPLL state changes, rate/width updates, RX adaptation, calibration start/done checks, interrupt acknowledgement, PMA override enable/disable, power gating, and display link training.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed state:

- Lane 2 and lane 3 PCS override state for TX/RX data enables, async data, serial/parallel loopback, reset/request controls, rate/width/pstate, MPLL selection, vboost/iboost, TX beacon, LOS thresholds, adaptation requests, and RX equalization controls.
- Lane 3 status and monitor state for TX/RX ACK, detection results, RX valid, adaptation ACK, FOM, TX pre/main/post direction, FSM state, calibration status, fast flags, CR lock, TX DCC status, TX EQ updates, CMN calibration, RX IQ phase offset, and OCLA/debug readbacks.
- Lane 3 IRQ status/mask/clear state for RX/TX request/reset, rate/pstate changes, adaptation, phase-2 calibration, lane mode changes, loopback, and DCC events.
- Always-on lane calibration and adaptation state for lanes 0 and 1 completely and lane 2 partially: AFE/DFE/CTLE offsets, tap values, slicer controls, RX signal-detect calibration codes, RX DCC calibration values, TX DCC bank address/data, MPLL background controls, firmware adaptation/calibration controls, and lane transceiver mode.

Persistence is hardware-defined. Configuration fields generally last until modeset, link retraining, PHY reset, suspend/resume, display block power gating, GPU reset, or driver reinitialization. Status, IRQ, calibration, adaptation, LOS, signal-detect, and DCC fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while relevant lane clocks and power domains are active. This generated header does not encode access type, reset value, volatility, write-one-to-clear semantics, or required polling delays.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DPCS 3.1.4 register database and related display code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies matching `ixDPCSSYS_*` offsets for every register family described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes both `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`, making this metadata part of DCN 3.1.4 display resource construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/reg_helper.h` and related AMD display register-helper infrastructure combine offsets, shifts, and masks for MMIO or indexed-register access.
- Adjacent generated ASIC headers such as `dcn_3_1_4_sh_mask.h` and later DPCS/DCN versions provide comparable field layouts for other display blocks and ASIC revisions; many lane and DPCS field names are shared across revisions.
- Runtime integration is with display link PHY bring-up, DisplayPort/HDMI link training, lane power/reset sequencing, PLL/MPLL control, RX adaptation and equalization, signal detection, DCC calibration, IRQ handling, diagnostics, and suspend/resume restore paths.

The practical API contract is compile-time: code that names a register field through AMD's register macros requires the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` definitions to exist and match the silicon layout.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while reading or modifying the wrong hardware bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first line is inside `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`; the earlier VCO fields are in the previous chunk. The final lines stop inside `DPCSSYS_CR1_RAWAONLANE2_DIG_LANE_XCVR_MODE_OVRD_IN`; the remaining lane 2 transceiver mode and later always-on lane 2/3 fields continue in the next chunk.
- Repeated lane blocks are copy-sensitive. Lane 0, lane 1, lane 2, and lane 3 layouts are structurally similar but independently named; an instance-specific generation error may affect only one physical lane and may be missed by testing that exercises fewer lanes or lower link widths.
- Override-enable pairs are hazardous. Many fields use a value bit plus an override-enable bit; setting only the value, setting only the enable, or using a mask from the wrong lane can leave hardware under autonomous control or force an unintended PHY state.
- Reset/request/ACK, adaptation, calibration, and IRQ clear fields are sequencing-sensitive. Incorrect masks can cause link bring-up timeouts, stuck adaptation, missed calibration completion, repeated interrupts, or premature progression while the PHY is not ready.
- Rate, width, pstate, MPLL, vboost, iboost, termination, RTUNE, DFE, CTLE, VREF, signal-detect, and LOS fields directly affect electrical behavior. Bad masks can manifest as link-training failures, intermittent high-rate failures, degraded margins, black screens, or resume-only failures.
- Status and debug fields can be invalid while a lane is powered down, clock-gated, reset, or assigned to another mode. Diagnostics that ignore power/lane ownership can misinterpret stale hardware state.
- Always-on DCC and calibration bank fields use address/data-style registers. Wrong masks or ordering can corrupt calibration read/write access instead of just producing a bad readback.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display link behavior:

- Build AMDGPU DCN 3.1.4 display support. Missing or renamed DPCS macros should fail in resource/register-table construction paths that include `dpcs_3_1_4_sh_mask.h`.
- Mechanically verify that every field in this chunk has the expected `__SHIFT` and `_MASK` pair, while allowing boundary exceptions where a pair is split across adjacent chunks.
- Cross-check every register group in this slice against `dpcs_3_1_4_offset.h` so register names in the shift/mask header have matching `ixDPCSSYS_*` addresses.
- Diff this chunk against AMD's authoritative DPCS 3.1.4 register database and against compatible generated DPCS/DCN headers where identical lane layouts are expected.
- Exercise DisplayPort and HDMI link bring-up across lane counts and link rates that use lane 3 and the always-on lane blocks: hotplug, modeset, link retraining, low-power transitions, suspend/resume, GPU reset recovery, and high-bandwidth modes.
- Monitor link-training status, PHY lane ready/ACK bits, RX adaptation done/FOM, LOS/signal-detect status, DCC/calibration status, IRQ counters, and kernel logs for stuck bits, repeated IRQs, missed completions, or lane-specific failures.
- Test loopback, ATE/diagnostic, and OCLA/debug access only where supported by hardware/lab tooling; these fields can force non-normal PHY states and should not be exercised blindly on production paths.
- Compare register dumps before and after modeset, retrain, suspend/resume, and reset to confirm that pstate/rate/width, MPLL, override-enable, IRQ mask/clear, signal-detect, and calibration fields are restored coherently.

## Cross-Chunk Notes

The previous chunk owns the beginning of raw lane 2 PCS/ATE RX override metadata and the earlier fields of `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`. This chunk owns the raw lane 2 tail, the complete raw lane 3 PCS/FSM/IRQ/PMA/TX/RX-control/ATE surface, complete always-on lane 0 and lane 1 metadata, and most of always-on lane 2 through the start of `LANE_XCVR_MODE_OVRD_IN`. The next chunk should complete always-on lane 2 and cover the remaining generated DPCS fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 3.1.4 lane metadata.
