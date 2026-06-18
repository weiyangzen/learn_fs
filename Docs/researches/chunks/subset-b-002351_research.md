# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 33364-35750

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is a large set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,105 `#define` entries across 2,387 lines. It is entirely within the `dpcssys_cr1_rdpcstxcrind` address block and covers CR1 raw-lane register fields. The chunk starts in the mask half of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN`, then continues through the rest of raw lane 0 PCS/FSM/IRQ/PMA/TX/RX/ATE control fields, all corresponding raw lane 1 fields, and the beginning of raw lane 2 fields through the first masks of `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`. The companion offset header maps these raw lane windows around `0x3000` for lane 0, `0x3100` for lane 1, and `0x3200` for lane 2.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- Lane 0 PCS tail: `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` masks for ATE overrides of RX/TX reset, RX/TX request, RX AFE/DFE adaptation enable, and RX/TX data enable. The shifts for this register begin before the chunk boundary.
- Lane 0 PCS equalization and termination: `RX_EQ_DELTA_IQ_OVRD_IN`, `TXRX_TERM_CTRL_OVRD_IN`, `TXRX_TERM_CTRL_IN`, `RX_OVRD_OUT_1`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, and `RX_PH2_CAL` describe RX equalization delta/IQ overrides, RX/TX termination control overrides, RX clock enable output, AFE gain, attenuation level, DFE tap1, CTLE boost, and phase-2 calibration request/acknowledge bits.
- Lane 0 FSM controls and monitors: `FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, `FAST_RX_*`, `FAST_SUP`, `FAST_TX_*`, `CMNCAL_*_STATUS`, `FAST_RX_CONT_*`, `FAST_FLAGS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `OCLA`, `TX_EQ_UPDATE_FLAG`, and `RX_IQ_PHASE_OFFSET` expose state-machine override, command readiness, memory address monitor, fast calibration/adaptation enables, common MPLL/RCAL status, continuous-calibration controls, DCC and EQ update flags, OCLA selection, and RX IQ phase offset.
- Lane 0 IRQ controls: `RESET_RTN_REQ`, individual RX IRQ status registers, matching RX IRQ clear registers, `IRQ_MASK`, `IRQ_MASK_2`, lane transceiver-mode IRQs, PH2 calibration IRQs, serial loopback IRQs, DCC on-demand IRQ, and TX reset/request IRQ status and clear fields. These names repeat across status, clear, and mask registers but have different hardware semantics.
- Lane 0 PMA transfer fields: `PMA_XF_LANE_OVRD_IN/OUT`, `SUP_OVRD_IN`, `SUP_PMA_IN`, `TX_OVRD_OUT`, `TX_PMA_IN`, `RX_OVRD_OUT`, `RX_PMA_IN`, `LANE_RTUNE_CTL`, `SUP_PMA_IN_1`, `MPHY_OVRD_IN/OUT`, and `RX_ADAPT_OVRD_OUT` define lane/supervisor/PMA handshakes, TX and RX override outputs, lane RTUNE control, MPHY PWM/termination override paths, and RX adaptation override outputs.
- Lane 0 TX/RX control and late ATE fields: `TX_CTL_*`, `RX_CTL_*`, `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1/2/3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2` describe TX FSM/clock controls, TX DCC continuous status, OCLA probes, RX FSM controls, LOS mask timing, RX data-enable override timing, off-cancel/adaptation continuous status, manufacturing/test overrides, master MPLL loop selection, and additional RX/TX override outputs.
- Lane 1 complete raw-lane window: the chunk repeats the same CR1 raw-lane schema for `DPCSSYS_CR1_RAWLANE1_*`, starting at `PCS_XF_TX_OVRD_IN` and continuing through PCS TX/RX overrides, PCS inputs/outputs, RX adaptation ACK/FOM and directed TX coefficient feedback, lane number and reserved words, ATE overrides, EQ/termination/PH2 fields, FSM, IRQ, PMA, TX_CTL, RX_CTL, and late ATE registers.
- Lane 2 partial raw-lane window: the chunk begins `DPCSSYS_CR1_RAWLANE2_*` at `PCS_XF_TX_OVRD_IN` and continues through PCS TX/RX, RX adaptation, ATE, EQ/termination/PH2, and early FSM controls. It ends inside `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS`; the remaining masks and the lane 2 IRQ/PMA/TX_CTL/RX_CTL/ATE tail are in the next chunk.

Most field masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these raw-lane blocks. Several fields occupy full 16-bit words, while many control/status fields are single-bit enables, status bits, clear bits, or override-value/override-enable pairs.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables use generated names from this header and companion `ixDPCSSYS_*` offsets.
3. Runtime driver code uses register helpers and those tables to read, write, set, clear, or update hardware fields during PHY bring-up, link training, modeset, diagnostics, interrupt handling, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual lane sequencing; this header only names bit positions and masks.

The macros do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR1 raw-lane registers:

- PCS state includes TX/RX reset and request overrides, pstate/rate/width/MPLL select paths, beacon/loopback/data-enable style controls, PCS input/output mirrors, RX adaptation request/disable/ACK/FOM, directed TX pre/main/post cursor feedback, lane number, ATE override bits, RX equalization overrides, termination controls, RX clock output, and PH2 calibration handshakes.
- FSM state includes manual FSM override controls, jump address and command start bits, state/status monitor bits, fast calibration/adaptation selectors, common MPLL/RCAL completion status, continuous calibration/adaptation selectors, CR lock, TX DCC flags and status, TX EQ update flags, OCLA selection, and RX IQ phase offset.
- IRQ state includes latched RX/TX reset and request events, RX rate and pstate events, RX adaptation request/disable events, lane transceiver-mode events, PH2 calibration events, serial loopback events, DCC on-demand events, clear registers, reset-return request bits, and mask registers.
- PMA transfer state includes lane and supervisor override inputs/outputs, TX/RX PMA handshakes, RTUNE control, MPHY override in/out fields, and RX adaptation override output.
- TX/RX local control state includes TX FSM and clock controls, TX DCC continuous status, RX FSM control, RX LOS masking, RX data-enable override timing, off-cancel/adaptation continuous status, and OCLA/UPCS OCLA probes.
- ATE and debug state includes manufacturing/test override values and enables for RX/TX controls, RX calibration and equalization fields, TX data and data-valid controls, master MPLL loop controls, and additional RX/TX override outputs.

Persistence is hardware-defined. Configuration and override fields generally last until another modeset/link-training sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, IRQ, calibration, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only when the corresponding lane power and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching CR1 raw-lane offsets. In that file, the relevant address block is `dpcssys_cr1_rdpcstxcrind`.
- Lane 0 registers covered here map from `ixDPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` at `0x3018` through PCS EQ/termination/PH2, FSM at `0x3020` through `0x303f`, IRQ at `0x3040` through `0x305b`, PMA at `0x3060` through `0x306c`, TX_CTL at `0x3080` through `0x3084`, RX_CTL at `0x30a0` through `0x30a5`, and late ATE/PCS fields at `0x30c0` through `0x30c8`.
- Lane 1 uses the same layout offset by `0x100`, with PCS starting at `0x3100`, FSM at `0x3120`, IRQ at `0x3140`, PMA at `0x3160`, TX_CTL at `0x3180`, RX_CTL at `0x31a0`, and late ATE/PCS fields at `0x31c0`.
- Lane 2 begins at `0x3200`; this chunk reaches `ixDPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` at `0x3238` but does not include the rest of lane 2's raw-lane window.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware/hardware state machines share ownership of many of these fields, especially reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane IRQs, and test overrides.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure and observe CR1 raw lanes during display PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` shift definitions are in the previous chunk; only the later shifts and masks are visible here.
- The chunk ends mid-register. `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` masks continue after line 35750 in the next chunk.
- Repeated lane layouts are copy-sensitive. A generator issue can affect one lane while neighboring lanes appear correct; lane 0, lane 1, and lane 2 names must pair with their matching offsets and tables.
- Status, clear, and mask registers use similar field names. Mixing IRQ status masks with clear or interrupt-mask masks can drop events, leave stale events latched, or create repeated interrupts.
- PCS and PMA override fields can bypass normal hardware sequencing. Bad masks around reset, request, data-enable, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, or ATE controls can leave a lane in a state that higher-level display code cannot reason about.
- FSM fast-flow and calibration bits are sequencing-sensitive. Incorrect masks for fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO/common calibration or continuous calibration flags can cause link training failure, poor equalization, unstable links, or stuck polling loops.
- TX/RX analog-adjacent control fields affect electrical behavior through PMA/PCS handshakes and calibration paths. Wrong DCC, termination, EQ, IQ phase, or adaptation fields may produce blank displays, rate-specific failures, compliance failures, or misleading debug traces.
- Reserved masks are still emitted. Consumers should not treat reserved fields as safe software-owned configuration fields unless hardware documentation explicitly says so.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete fields in this range have consistent `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions for `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` at the start and `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` at the end.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h`, especially lane-local offset spacing: lane 0 around `0x3000`, lane 1 around `0x3100`, and lane 2 around `0x3200`.
- Diff against AMD's source register database and nearby DPCS generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, and power states. Expected signals are stable link training, completed RX adaptation, no stuck reset/request handshakes, and no unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in PCS, FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE fields.
- Use register dumps or PHY debug traces during failing links to confirm that RX adaptation ACK/FOM, directed TX coefficient feedback, DCC status, FSM state, CR lock, IRQ clear/mask bits, RTUNE handshakes, PH2 calibration, OCLA probes, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: OCLA and UPCS OCLA, serial loopback, RX statistic/adaptation debug, PH2 calibration, DCC on-demand IRQs, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_ATE_OVRD_IN` and earlier lane 0 PCS fields such as lane number and reserved PCS words. This chunk continues lane 0, fully covers lane 1, and starts lane 2. The next chunk should finish `DPCSSYS_CR1_RAWLANE2_DIG_FSM_FAST_FLAGS` and continue lane 2's IRQ, PMA, TX_CTL, RX_CTL, and late ATE/PCS fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR1 raw-lane registers.
