# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 54800-57195

## Scope

This chunk is part of the generated AMD DPCS 4.2.0 register shift/mask header. It contains 2,100 `#define` entries for bit positions and bit masks, covering the end of `DPCSSYS_CR2_RAWLANE2`, the full matching `DPCSSYS_CR2_RAWLANE3` digital lane block, and the beginning of `DPCSSYS_CR2_RAWAONLANE0`. The file is declarative: it exports preprocessor constants only and has no C functions, structs, runtime branches, allocation, or persistent software data.

## Purpose

The constants describe 16-bit register fields used by AMD display PHY/DPCS programming code for lane-level DisplayPort/PHY control. Each register field has a `__SHIFT` constant for positioning and a `_MASK` constant for read-modify-write operations. The chunk is mostly lane-scoped control and status metadata:

- `RAWLANE2` tail: PCS/PMA crossbar override inputs and outputs, RX/TX request/ack fields, ATE overrides, FSM monitor and fast-calibration fields, IRQ status/clear/mask fields, lane TX/RX controller flags, OCLA debug hooks, and late PCS TX override bits.
- `RAWLANE3`: the same PCS, FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE register groups repeated for lane 3.
- `RAWAONLANE0` start: always-on lane calibration/readback definitions for AFE/DFE offsets, adapted equalizer values, phase adjustment, MPLL coarse tune and disable, power-up done status, calibration fast flags, common calibration status, and TX/RX disable overrides.

## Important API Surface

The exported API is the macro namespace. Important families in this chunk include:

- PCS TX/RX interface macros such as `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN__PSTATE_MASK`, `...__RATE_MASK`, `...__MPLL_EN_MASK`, `...__RESET_OVRD_EN_MASK`, `...__REQ_OVRD_EN_MASK`, and the corresponding RX fields for `ADAPT_AFE_EN`, `ADAPT_DFE_EN`, `RX_DATA_EN_OVRD_*`, CDR VCO/ref load values, EQ gains, and acknowledge bits.
- ATE and loopback/test macros such as `DPCSSYS_CR2_RAWLANE{2,3}_DIG_PCS_XF_ATE_OVRD_IN`, `ATE_RX_OVRD_IN*`, `ATE_TX_OVRD_IN*`, `MASTER_MPLL_LOOP`, serial loopback enable overrides, TX data/asynchronous data overrides, and RX EQ delta IQ controls.
- FSM/fast-calibration macros such as `DPCSSYS_CR2_RAWLANE{2,3}_DIG_FSM_FAST_RX_STARTUP_CAL`, `FAST_RX_ADAPT`, `FAST_RX_AFE_CAL`, `FAST_RX_DFE_CAL`, `FAST_RX_CONT_*`, `FAST_FLAGS`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `CMNCAL_MPLL_STATUS`, `CMNCAL_RCAL_STATUS`, `CR_LOCK`, and `OCLA`.
- Interrupt macros for per-lane RX/TX request, reset, rate, pstate, adaptation, phase-2 calibration, lane mode, loopback, and DCC-on-demand events, including individual IRQ status bits, clear bits, and `IRQ_MASK` / `IRQ_MASK_2` fields.
- PMA interface macros for lane/supervisor override routing, TX/RX PMA fields, MPHY fields, RTUNE controls, and RX adaptation override values.
- `RAWAONLANE0` calibration/status macros for AFE and DFE IDAC/VDAC offsets, even/odd ref levels, adapted ATT/VGA/CTLE/DFE tap values, RX slicer controls, `FAST_FLAGS`, `FAST_FLAGS_2`, MPLL coarse tune/disable, common calibration done/init status, and generic `ADPT_CTL_0` through `ADPT_CTL_7` full-word fields.

The paired offset definitions live in `dpcs_4_2_0_offset.h`; this header supplies only bit layout. Consumers normally combine an `ix...` offset macro with a `...__FIELD_MASK` and `...__FIELD__SHIFT` macro through AMD display register helper code.

## Control Flow

There is no executable control flow in this chunk. The implied hardware flow is encoded by register naming:

1. Software selects a lane and register offset from the DPCS offset header.
2. It reads or writes hardware register words through AMD display register helpers.
3. Field values are shifted by `__SHIFT` and masked by `_MASK`.
4. Override enable bits, request bits, reset bits, and IRQ clear bits affect hardware state machines in the PCS/PMA/lane-controller blocks.
5. Status and acknowledge fields report the hardware result, for example request `ACK`, RX adaptation acknowledge/FOM, calibration done bits, CR lock, TX DCC status, and OCLA monitor fields.

For `RAWLANE2` and `RAWLANE3`, the chunk preserves a regular repeated lane layout, which lets higher-level code use lane-indexed offset tables while the field definitions stay lane-specific. The `RAWAONLANE0` section is not a repeat of the raw lane PCS block; it starts the always-on calibration/status register set that can be shared by or adjacent to PHY lane bring-up logic.

## State And Persistence

The header itself has no software state and persists nothing. Its constants address hardware-backed state:

- Override registers can force TX/RX power, reset, request, rate, width, pstate, MPLL selection, PLL state, data enable, loopback, PMA signal-detect, and calibration paths.
- Status registers expose transient PHY state, including acknowledgements, signal/adaptation figure-of-merit, calibration phases, common calibration completion, clock/data recovery indicators, and debug monitor values.
- IRQ clear masks are write-sensitive hardware controls; using a wrong mask can clear the wrong event or fail to clear an asserted one.
- Reserved masks document unused or reserved bit ranges. Callers should preserve these bits on read-modify-write unless the hardware programming guide explicitly says otherwise.

Any durable effect comes from writes to the display PHY registers during link setup, training, test mode, power management, or recovery, not from this header.

## Dependencies And Integration Points

This header depends only on C preprocessing and its include guard. In this tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes both `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h`, wiring these constants into the DCN 3.1 resource implementation alongside DCN, NBIO, and MMHUB register headers.

Integration points are expected to include AMD display register helper macros from `reg_helper.h` and resource/link encoder initialization code that builds register tables. The constants are ASIC-version-specific: DPCS 4.2.0 bit layouts must remain synchronized with the matching offset header and the generated DCN/DPCS register tables used for Yellow Carp/DCN31-era display resources.

## Risks

- Bit drift between `dpcs_4_2_0_offset.h`, this shift/mask header, and silicon documentation can silently misprogram PHY registers.
- The lane 2 and lane 3 blocks are highly repetitive; copy-generation mistakes can leave one lane with a shifted mask or a missing override that is hard to spot in review.
- Many controls are low-level PHY override or calibration knobs. Incorrect writes can break link training, leave lanes stuck in reset, disable data, mask interrupts, bypass required calibrations, or force test/ATE behavior in normal operation.
- Reserved masks are numerous in this range. Code that writes full register literals instead of read-modify-write field updates risks changing reserved bits.
- `RAWAONLANE0` contains always-on calibration and MPLL controls; errors here can affect broader PHY bring-up behavior beyond a single high-level display connector flow.

## Test Signals

Useful validation signals are compile-time and hardware-facing:

- Kernel/display build coverage should include `dcn31_resource.c` so these macro names compile with the matching offset header and register helper usage.
- Static checks can verify each register field has coherent shift/mask pairs and that masks do not overlap except for documented reserved ranges.
- Generated-header regression checks should compare lane 2 and lane 3 repeated register groups for expected structural equivalence while allowing lane-number-specific prefixes.
- Hardware or emulator tests should exercise DisplayPort link bring-up, link retraining, power state changes, lane reset/request handshakes, RX adaptation, DCC/RTUNE calibration, interrupt clear/mask handling, and debug/OCLA monitor reads.
- Failure signatures include link training timeouts, missing RX/TX request acknowledgements, stuck calibration-done bits, unexpected IRQ storms or lost IRQs, and lane-specific failures that reproduce only on raw lane 2 or raw lane 3.
