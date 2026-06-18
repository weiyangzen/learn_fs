# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 68056-70486

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice for display PHY register fields. It contains no executable C logic; its public surface is a large set of preprocessor constants that encode bit positions (`__SHIFT`) and field masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,146 `#define` entries across 2,431 lines and 285 register-comment groups. It starts in the middle of `DPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT`: the first five shift definitions and the register comment are immediately before line 68056, while this chunk continues with the remaining shifts and all masks for that register. It then covers CR3 lane3 digital/analog TX override and status fields, CR3 raw common/MPLL/AON common fields, all visible CR3 rawlane0 PCS/FSM/IRQ/PMA/TX/RX/ATE fields, and the beginning of CR3 rawlane1 PCS/FSM/IRQ fields. The range ends inside `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_LANE_XCVR_MODE_IRQ`: only the shift definitions are in this chunk, with its masks in the next chunk.

Although this repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The exported interface follows the generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, compose, or update the field.

The main register-field families in this chunk are:

- CR3 lane3 digital analog TX controls: `DPCSSYS_CR3_LANE3_DIG_ANA_TX_*` covers TX analog clock/data/reference/VCM/reset/serial/data-rate override outputs, termination-code override and clocking, TX equalization override banks, DCC DAC override controls, fast-start, clock-loopback, AC JTAG, and lane3 analog TX status readbacks such as receive-detect, loopback, calibration, and EQ mux status.
- CR3 lane3 raw analog TX registers: `DPCSSYS_CR3_LANE3_ANA_TX_*` exposes measurement overrides, TX power override, alternate/test bus selection, ATB measurement enables, DCC DAC and DCC control values, termination-code programming, override clocking, slew/drive/source/vreg-style miscellaneous fields, and reserved analog registers.
- CR3 raw common controls: `DPCSSYS_CR3_RAWCMN_DIG_*` includes common control, MPLLA/MPLLB override inputs, PLL bandwidth and SSC override words, lane FSM operation extension, common control extension, MPLL state control, TX calibration code, SRAM init status, OCLA enablement, supervisor analog override, PCS/FW ID code words, and common RTUNE readback/programming values.
- CR3 always-on common controls: `DPCSSYS_CR3_RAWCMN_DIG_AON_CMN_*` describes per-index RTUNE RX/TXDN/TXUP values, SRAM bitline configuration, common power-gate override input/output, supervisor override input, VREF statistics, resistor override input and ASIC in/out readback, reference range override, and miscellaneous common configuration.
- CR3 rawlane0 PCS transfer fields: `DPCSSYS_CR3_RAWLANE0_DIG_PCS_XF_*` covers TX/RX override inputs, TX/RX PCS input and output handshakes, RX adaptation acknowledgement and figure of merit, directed TX pre/main/post cursor feedback, lane numbering, reserved words, ATE override inputs, RX EQ delta/IQ controls, TX/RX termination control override/input, PH2 calibration, master MPLL loop control, and extended ATE/RX/TX override banks.
- CR3 rawlane0 FSM and fast-flow controls: `DPCSSYS_CR3_RAWLANE0_DIG_FSM_*` covers FSM override, memory/status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration flags, continuous calibration/adaptation controls, fast supervisor/TX common-mode/RX detect/RX power-up/VCO wait/VCO calibration paths, common MPLL/RCAL status, CR locking, TX DCC flags/status, OCLA selection, TX EQ update flag, and RX IQ phase offset.
- CR3 rawlane0 IRQ controls: `DPCSSYS_CR3_RAWLANE0_DIG_IRQ_CTL_*` defines reset-return requests, RX/TX reset and request IRQ status and clear fields, RX rate/pstate/adaptation IRQ status and clears, PH2 calibration request/disable IRQ status and clears, lane transceiver-mode and RX-to-TX serial-loopback IRQs, DCC on-demand IRQ status, and IRQ mask banks.
- CR3 rawlane0 PMA/TX/RX controls: `DPCSSYS_CR3_RAWLANE0_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` describe PMA lane/supervisor override and input/output handshakes, TX/RX PMA signals, lane RTUNE controls, MPHY override paths, RX adaptation override output, TX FSM/clock controls, TX DCC continuous status, OCLA and UPCS OCLA selectors, RX FSM controls, loss-of-signal masking, data-enable override timing, off-cancel continuous status, and adaptation continuous status.
- CR3 rawlane1 beginning: `DPCSSYS_CR3_RAWLANE1_DIG_PCS_XF_*`, `FSM_*`, and early `IRQ_CTL_*` repeat the same PCS/FSM/IRQ layout for rawlane1 through the `LANE_XCVR_MODE_IRQ` shift definitions. The remainder of rawlane1 IRQ and later rawlane1 PMA/TX/RX fields continue after this chunk.

Most field masks are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these lane, raw common, raw lane, PCS/PMA, FSM, IRQ, and analog blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. AMD display code for the matching DCN/DPCS generation includes the DPCS 4.2.3 offset header and this shift/mask header.
2. Version-specific resource code, including `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, uses these generated constants through register, shift, and mask tables.
3. Runtime display driver paths use helper macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables.
4. The real sequencing for TX analog override, MPLL/common programming, RTUNE, power-gating, PCS/PMA handshakes, RX adaptation, fast calibration, IRQ handling, diagnostic readback, and ATE/test operation lives outside this generated header.

The macros only describe bit layout. They do not encode access type, ordering constraints, reset values, read-only/write-only status, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, power-domain validity, or hardware errata.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 lane3, raw common, rawlane0, and early rawlane1 DPCS registers:

- Lane3 TX analog state includes enable/clock/reset/serial/data-rate overrides, MPLLA/MPLLB clock enables, RX detect enable, termination code, driver source, EQ leg pull controls, pre/post cursor controls, DCC calibration range/control/select/compensation controls, fast-start, loopback, AC JTAG, analog measurement/test-bus selection, ATB routing, power override, DCC DAC values, termination clocking, and miscellaneous analog drive or reserved latches.
- Raw common state includes common controls, MPLLA/MPLLB enable/divider/SSC/bandwidth override inputs, MPLL state control, lane FSM operation extension, SRAM init completion, OCLA enables, supervisor analog override bits, ID-code and firmware-code readback, common TX calibration code, common RTUNE values for RX and TX up/down paths, common power-gate overrides, VREF statistics, resistor override/readback, and reference range selection.
- Rawlane0 PCS and PMA state includes TX/RX pstate, rate, width, MPLL selection, resets, requests, data-enable, loopback, beacon, async signals, RX adaptation request/disable/ACK/FOM, directed TX coefficient feedback, termination control overrides, PH2 calibration, ATE override signals, lane number, PMA supervisor/lane handshakes, RTUNE controls, MPHY PWM/termination override paths, and RX adaptation override output.
- Rawlane0 FSM and IRQ state includes state-machine override and status monitors, fast one-shot and continuous calibration/adaptation flags, RX VCO and common calibration status, CR register/memory lock, TX DCC flags/status, TX EQ update flag, RX IQ phase offset, RX/TX reset/request/rate/pstate/adaptation/PH2/lane-mode/loopback/DCC IRQ status, clear, and mask fields.
- Rawlane0 TX/RX control state includes TX FSM controls, TX clock and DCC continuous controls, TX/RX OCLA probe selectors, RX FSM controls, LOS mask timing, RX data-enable override timing, off-cancel continuous status, and adaptation continuous status.
- Rawlane1 state begins repeating the rawlane0 PCS/FSM/IRQ model, but this chunk stops before the full rawlane1 IRQ set and before rawlane1 PMA/TX/RX controls are complete.

Persistence is hardware-defined. Configuration fields usually remain until modeset/link reprogramming, PHY power gating, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization rewrites them. Status, ACK, IRQ, statistic, calibration, and handshake fields may be latched, sampled, clear-on-write, self-clearing, or valid only while the relevant common/lane clock and power domains are active. This generated header does not define those semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.3 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h` supplies matching `ixDPCSSYS_*` offsets. For this range, representative offsets include `0x13a0` for `ixDPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT`, `0x2000` for `ixDPCSSYS_CR3_RAWCMN_DIG_CMN_CTL`, `0x3000` for `ixDPCSSYS_CR3_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`, and `0x314f` for `ixDPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_LANE_XCVR_MODE_IRQ`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes `dpcs/dpcs_4_2_3_sh_mask.h`, tying these generated bit definitions to the DCN 3.1.6 display resource configuration.
- AMD display DCN/DPCS resource code consumes these constants through version-specific register, shift, and mask tables rather than by open-coding bit values.
- Link training, PHY bring-up, clock-source programming, display mode set, hotplug, suspend/resume, diagnostics, and interrupt code interact with the hardware fields described here through register helpers and generated tables.
- Firmware and hardware state machines also interact with the same fields, especially for MPLL/common control, RTUNE, power gating, RX adaptation, fast calibration/adaptation flows, PMA/PCS handshakes, DCC calibration, ATE paths, OCLA/debug routing, and IRQ latching.

Behaviorally, this range is below the user-facing display stack. It defines bit layout used when the driver or firmware configures CR3 lane3 TX analog behavior, manages common PLL and always-on common state, controls rawlane0 link/PHY operations, and begins the same rawlane model for rawlane1.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are artificial. The first register in this range, `DPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT`, is split because its register comment and first five shifts are before line 68056. The last register, `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_LANE_XCVR_MODE_IRQ`, is also split because only its shift definitions are in this chunk.
- Repeated rawlane0/rawlane1 patterns are copy-sensitive. A generator or merge error can affect only one lane while adjacent lane definitions still look correct.
- Analog TX fields can affect electrical behavior. Wrong masks for TX clock enables, resets, data rate, termination, EQ, DCC, power override, ATB/test-bus, loopback, VCM hold, or analog miscellaneous controls may produce blank displays, unstable links, compliance failures, or misleading debug traces.
- Common MPLL and AON common fields are clock and power sensitive. Bad masks for MPLLA/MPLLB override inputs, SSC controls, MPLL state, SRAM init, RTUNE values, power-gate overrides, resistor overrides, or reference range selection can cause clock instability, link retraining loops, power-transition failures, or mode-specific regressions.
- Raw PCS/PMA override and ATE fields can bypass normal hardware state machines. Misprogramming reset/request/data-enable/loopback/MPLL/termination/RTUNE/PH2/ATE fields can leave a lane in a state that higher-level display code cannot easily reason about.
- FSM fast-flow bits are sequencing-sensitive. Incorrect masks around fast startup, RX adaptation, DFE/AFE/ref-level/IQ calibration, VCO wait/calibration, continuous adaptation, CR lock, or TX DCC flags can cause stuck polling loops, incomplete calibration, or degraded link margin.
- IRQ status, clear, and mask registers are easy to confuse because many field names repeat across status, clear, and mask groups. Wrong masks can drop events, leave stale status latched, or cause repeated interrupts.
- Reserved fields are numerous. Consumers must preserve reserved bits according to hardware requirements; this header only gives masks and does not explain whether reserved fields must be written as zero, preserved, or avoided.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.3. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that every complete field in this range has the expected `__SHIFT` and `_MASK` pair, allowing the known boundary exceptions for `DPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT` at the start and `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_LANE_XCVR_MODE_IRQ` at the end.
- Cross-check every complete register group in this chunk against `dpcs_4_2_3_offset.h`, including lane3 offsets around `0x13a0`, raw common offsets around `0x2000`, rawlane0 offsets around `0x3000`, and rawlane1 offsets through the early IRQ region around `0x314f`.
- Diff this generated header against AMD's source register database and nearby generated variants such as DPCS 4.2.2 or other DPCS 4.2.x headers where hardware layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, power states, and PHY lanes. Expected signals are stable link training, correct MPLL selection, successful calibration/adaptation, no stuck ACK/status bits, and no unexpected lane IRQs.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in common PLL, AON common, lane analog, PMA/PCS, FSM, and IRQ fields.
- Validate high-bandwidth and clock-sensitive modes that stress MPLLA/MPLLB, SSC, reference range, common RTUNE, TX data-rate, TX termination/EQ, DCC calibration, and PMA/PCS handshake fields. Watch for black screens, PHY lock failures, retraining loops, display corruption, audio/video timing instability, or rate-specific failures.
- Use register dumps or PHY debug traces during failing links to confirm lane3 TX analog controls, common MPLL/AON fields, rawlane0 PCS/PMA handshakes, RX adaptation/FOM, DCC status, FSM fast flags, CR lock, IRQ clear/mask bits, and rawlane1 early PCS/FSM/IRQ fields decode correctly.
- Exercise diagnostic paths where available: OCLA, analog test bus/readback fields, directed TX coefficient feedback, PH2 calibration, loopback controls, ATE overrides, MPHY low-speed controls, and raw common firmware/ID-code readbacks.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT` and earlier CR3 lane3 RX statistic fields. This chunk continues that split register, covers the rest of lane3 TX analog controls, the CR3 raw common area, all visible CR3 rawlane0 PCS/FSM/IRQ/PMA/TX/RX/ATE definitions, and the start of CR3 rawlane1 PCS/FSM/IRQ definitions. The next chunk should finish `DPCSSYS_CR3_RAWLANE1_DIG_IRQ_CTL_LANE_XCVR_MODE_IRQ` masks and continue the remaining rawlane1 IRQ/PMA/TX/RX definitions. The final per-file research document should reconcile these boundary splits before making whole-file claims about all DPCS 4.2.3 register groups.
