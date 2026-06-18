# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 76244-78674

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY registers. It contains no executable C logic; its exported surface is preprocessor metadata that names bit positions and masks for DPCS indirect hardware fields.

The requested range contains 2,080 `#define` entries across 2,431 lines and 351 register-comment groups. It is in the CR3 DPCS register namespace. The first part finishes the CR3 raw lane 3 digital IRQ/PMA/TX/RX/ATE control window. The larger second part starts the CR3 raw always-on lane window and covers raw AON lanes 0, 1, 2, and the beginning of lane 3. The chunk starts mid-register in `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR`, where only masks are present in this range, and it ends mid-register in `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL`, where only shifts are present in this range.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field inside its hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- CR3 raw lane 3 IRQ control: `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_*` provides clear, status, and mask fields for RX pstate/rate/adaptation events, RX reset/request, lane transceiver-mode changes, PH2 calibration request/disable events, RX-to-TX serial loopback, DCC on-demand events, and TX reset/request events. The aggregate mask registers split RX/lane events in `IRQ_MASK` and TX events in `IRQ_MASK_2`.
- CR3 raw lane 3 PMA transfer and override fields: `PMA_XF_LANE_OVRD_IN/OUT`, `SUP_OVRD_IN`, `SUP_PMA_IN`, `TX_OVRD_OUT`, `TX_PMA_IN`, `RX_OVRD_OUT`, `RX_PMA_IN`, `LANE_RTUNE_CTL`, `SUP_PMA_IN_1`, `MPHY_OVRD_IN/OUT`, and `RX_ADAPT_OVRD_OUT` describe lane MPLL enables, supervisor MPLL state, TX request/reset/beacon/async/data-enable overrides, RX request/reset/AFE/DFE/data/path overrides, RTUNE handshakes, MPHY PWM/termination override paths, and RX adaptation acknowledge or command overrides.
- CR3 raw lane 3 local TX/RX controls: `TX_CTL_*` and `RX_CTL_*` cover TX FSM and clock controls, TX DCC continuous status, OCLA/UPCS OCLA probe enables, RX FSM enable/rate-change behavior, RX loss-of-signal mask timing, RX data-enable override timing, and off-cancel/adaptation continuous status.
- CR3 raw lane 3 late PCS/ATE controls: `PCS_XF_ATE_RX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN`, `PCS_XF_ATE_TX_OVRD_IN_1`, `PCS_XF_MASTER_MPLL_LOOP`, `PCS_XF_ATE_RX_OVRD_IN_1/2/3`, `PCS_XF_RX_OVRD_OUT_2`, and `PCS_XF_TX_OVRD_IN_2` expose manufacturing/test override values and enables for RX rate/width/pstate/LPD/loopback, TX pstate/rate/width/MPLL selection, boost/beacon/async/serial-loopback/data controls, master MPLL loop enables, RX LOS/adaptation/continuous controls, VCO/reference load overrides, RX valid override, and additional TX data/async data overrides.
- CR3 raw AON lane 0 through lane 2 complete windows: each `DPCSSYS_CR3_RAWAONLANE{0,1,2}_DIG_*` group repeats the same always-on lane schema. It includes AFE/CTLE IDAC offsets, RX IQ/adaptation figure-of-merit, DFE summer/phase/data/bypass/error offsets, even/odd reference levels, RX phase-adjust linear/map values, MPLLA/MPLLB coarse tune, power-up done bits, RX adaptation values for ATT/VGA/CTLE/DFE taps 1-5, adaptation done status, fast calibration flags, slicer controls, common calibration MPLL/RCAL status, eight generic adaptation control words, MPLL disable bits, continuous fast flags, TX/RX disable overrides, RX LOS mask control, signal-detect filter control, RX PMA stats, RX PMA squelch/termination/sigdet overrides, RX sigdet calibration and code fields, VREF generator enable, calibration code registers, RX DCC calibration code words, TX DCC bank address/data/control, MPLL background control, sigdet output override/input mirrors, firmware MM/adaptation/calibration config words, lane transceiver-mode override/input mirrors, RX sigdet config, and TX DCC config.
- CR3 raw AON lane 3 partial window: the range begins the lane 3 AON schema at `AFE_ATT_IDAC_OFST` and continues through adaptation, DFE, fast flags, common calibration, TX/RX disable, LOS/sigdet/stat fields, and RX PMA override groups. It stops after the shift half of `RX_SIGDET_CAL`; the masks and later lane 3 AON groups are outside this chunk.

Most fields are 16-bit DPCS register fields with an `L`-suffixed mask. Many status/control fields are single-bit, while calibration and adaptation values often occupy 5, 6, 7, 8, 10, 12, 13, or full 16-bit field widths. A repeated pattern in override registers is `<signal>_OVRD_VAL` paired with `<signal>_OVRD_EN`, where the enable bit decides whether the override value bypasses normal hardware or firmware sequencing.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes this shift/mask header with the companion DPCS 4.2.2 offset header.
2. Generated register tables, macros, and helper code pair these `__SHIFT` and `_MASK` values with `ixDPCSSYS_*` register offsets.
3. Runtime driver paths use those tables through register helpers to read, compose, update, poll, clear, or mask hardware fields during PHY bring-up, link training, modeset, hotplug handling, diagnostics, low-power transitions, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual PHY sequencing; this chunk only names the bit layout consumed by those paths.

The macros do not encode access type, reset value, write-one-to-clear behavior, self-clearing behavior, polling order, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 raw lane and raw always-on lane registers:

- IRQ state includes latched lane events, clear bits, and interrupt mask bits for RX request/reset/rate/pstate/adaptation events, PH2 calibration events, loopback events, lane transceiver-mode changes, DCC on-demand signals, and TX reset/request signals.
- Raw lane PMA/PCS state includes reset/request handshakes, rate/width/pstate/LPD controls, data-enable and async paths, serial and parallel loopback controls, MPLL selection and loop controls, RTUNE controls, MPHY override paths, TX/RX PMA handshakes, RX LOS/adaptation controls, and ATE overrides.
- TX/RX control state includes local FSM enables, TX clock controls, DCC continuous status, OCLA probe selection, RX LOS masking, RX data-enable override timing, and continuous off-cancel/adaptation status.
- Raw AON lane state includes analog-adjacent tuning and telemetry for AFE/CTLE/DFE/IQ/phase adjustment, adaptation values and completion, common calibration completion, fast and continuous calibration selectors, DCC calibration code storage, signal-detect filtering and calibration, VREF/squelch/termination controls, firmware configuration words, and lane transceiver-mode overrides.

Persistence is hardware-defined. Override and configuration fields generally remain until another link-training or modeset sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, IRQ, calibration, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only while the corresponding lane, always-on domain, and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching `ixDPCSSYS_*` offsets for CR3 raw lane and raw AON lane registers.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware and hardware state machines share ownership of many fields in this chunk, especially IRQ clear/mask fields, reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane transceiver-mode controls, signal-detect calibration, and ATE/debug overrides.
- The raw AON lane groups are repeated for lanes 0, 1, 2, and 3. Correct integration depends on each lane's mask names pairing with the same lane's offsets and not with neighboring raw lane or AON lane windows.
- The chunk is source-tree-aligned with the generated AMD header, not with any Ceph subsystem. Consumers should treat it as GPU display register metadata even though it lives inside the mirrored source tree under `sources/distributed-fs/ceph-client`.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure, observe, and debug CR3 PHY lane behavior during display link operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong hardware field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts mid-register. `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` shift definitions are immediately before the requested range; this range only contains its two masks.
- The chunk ends mid-register. `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL` masks are immediately after the requested range; this range only contains its shift definitions.
- Status, clear, and mask registers use similar field names. Mixing IRQ status masks with clear or interrupt-mask masks can leave stale events latched, drop events, or create repeated interrupts.
- Override registers can bypass normal hardware sequencing. Bad masks around TX/RX reset, request, data enable, async, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, signal detect, or ATE controls can leave a display PHY lane in a state that higher-level code cannot reason about.
- The raw AON groups are copy-sensitive. A generator issue in one lane can be hard to notice because adjacent lanes have nearly identical names and masks.
- Calibration fields are sequencing-sensitive. Incorrect masks for fast calibration flags, DCC codes, VREF/sigdet calibration, DFE/CTLE/IQ adaptation, common MPLL/RCAL status, or TX DCC bank controls can cause link training failure, unstable links, blank displays, rate-specific failures, compliance failures, or misleading debug traces.
- Reserved masks are emitted alongside real fields. Consumers should not treat reserved fields as software-owned configuration unless hardware documentation explicitly allows it.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify complete register groups in this range have matching `__SHIFT` and `_MASK` pairs, allowing the known boundary exceptions for `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` at the start and `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL` at the end.
- Cross-check the complete CR3 raw lane 3 and raw AON lane 0-2 groups against `dpcs_4_2_2_offset.h` and against nearby generated DPCS variants where repeated lane layouts should match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, and power states. Expected signals are stable link training, completed RX adaptation, no stuck reset/request handshakes, no unexpected lane IRQs, and plausible AON lane calibration/status readings.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in IRQ, PMA, TX_CTL, RX_CTL, ATE, and AON calibration fields.
- Use register dumps or PHY debug traces during failing links to confirm that IRQ clear/mask bits, RX adaptation ACK/FOM, DCC status and codes, common calibration done bits, RTUNE handshakes, PH2 calibration, signal-detect calibration, OCLA probes, lane transceiver-mode mirrors, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: OCLA and UPCS OCLA, serial or parallel loopback, RX statistic/adaptation debug, PH2 calibration, DCC on-demand IRQs, signal-detect/VREF calibration, TX DCC bank access, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the `__SHIFT` half of `DPCSSYS_CR3_RAWLANE3_DIG_IRQ_CTL_RX_PSTATE_IRQ_CLR` and earlier CR3 raw lane 3 IRQ state. This chunk continues CR3 raw lane 3 through its IRQ/PMA/TX/RX/ATE tail, fully covers raw AON lanes 0 through 2, and starts raw AON lane 3. The next chunk should finish `DPCSSYS_CR3_RAWAONLANE3_DIG_RX_SIGDET_CAL` masks and continue the remaining raw AON lane 3 signal-detect, VREF, calibration-code, DCC, firmware-config, and lane-mode fields. The final per-file research document should reconcile these artificial line boundaries before making whole-file claims about all DPCS 4.2.2 CR3 lane registers.
