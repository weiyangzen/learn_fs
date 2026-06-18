# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 71474-73853

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for display PHY register fields. It contains no executable C logic. Its exported surface is a set of preprocessor constants that encode field bit positions (`__SHIFT`) and field masks (`_MASK`) for DPCS indirect hardware registers.

The requested range contains 2,119 `#define` entries across 2,380 lines. It is entirely in the CR3 DPCS namespace and spans several adjacent hardware register regions: the lane 3 RX statistic and TX analog tail, the CR3 raw-common digital block, the complete CR3 raw lane 0 register window, and the beginning of CR3 raw lane 1 through `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL`. The companion offset header maps these groups around lane 3 offsets `0x1384` through `0x13ef`, raw-common offsets `0x2000` through `0x2040`, raw lane 0 offsets `0x3000` through `0x30c8`, and raw lane 1 offsets starting at `0x3100`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The interface is generated macro data:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, compose, or update that field.

The main register-field families are:

- Lane 3 RX statistic controls: `DPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_CTL0/1/2`, `SMPL_CNT1`, `STAT_CNT_0` through `STAT_CNT_6`, `CAL_COMP_CLK_CTL`, `MATCH_CTL2` through `MATCH_CTL5`, and `STAT_STOP`. These fields configure correlation/statistic source selection, statistic counter enables, sample/count completion bits, data delay/scope delay controls, calibration comparator clock counters, pattern/mask words, and the statistic counter stop bit.
- Lane 3 digital TX analog override outputs: `DPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT`, `TX_TERM_CODE_OVRD_OUT`, `TX_TERM_CODE_CLK_OVRD_OUT`, `TX_EQ_OVRD_OUT_0` through `_5`, `ANA_STATUS_0`, `TX_DCC_DAC_OVRD_OUT`, `TX_DCC_DAC_OVRD_OUT_2`, and `TX_OVRD_OUT_2`. These macros name software-visible override, status, equalization, termination, DCC DAC, data-rate, clock, reset, serial-enable, RX-detect, and transmit-coefficient fields.
- Lane 3 analog TX registers: `DPCSSYS_CR3_LANE3_ANA_TX_OVRD_MEAS`, `TX_PWR_OVRD`, `TX_ALT_BUS`, `TX_ATB1/2`, `TX_DCC_DAC`, `TX_DCC_CTRL1`, `TX_TERM_CODE`, `TX_TERM_CODE_CTRL`, `TX_OVRD_CLK`, `TX_MISC1/2/3`, and reserved words. These are analog-adjacent fields for measurement override, power override, alternate test buses, DCC, termination, clock override, and miscellaneous analog TX controls.
- CR3 raw-common digital controls: `DPCSSYS_CR3_RAWCMN_DIG_CMN_CTL`, MPLLA/MPLLB override and bandwidth/SSC registers, lane FSM extension, `CMN_CTL_1`, `MPLL_STATE_CTL`, `TX_CAL_CODE`, `SRAM_INIT_DONE`, `OCLA`, `SUP_ANA_OVRD`, PCS/FW ID codes, and the always-on common RTUNE, SRAM, power-gating, supervisor, VREF, resistor, reference-range, and miscellaneous controls. These fields describe common PLL, supervisor, calibration, debug, firmware identity, and always-on common resources shared by lanes.
- Raw lane 0 PCS transfer and adaptation fields: `DPCSSYS_CR3_RAWLANE0_DIG_PCS_XF_*` covers TX and RX override inputs/outputs, PCS input/output mirrors, RX adaptation ACK/FOM, directed TX pre/main/post cursor feedback, lane number and reserved words, ATE overrides, RX equalization delta/IQ, termination override and input mirrors, RX clock output, RX EQ overrides, and PH2 calibration request/acknowledge fields.
- Raw lane 0 FSM controls: `DPCSSYS_CR3_RAWLANE0_DIG_FSM_*` covers manual FSM override/jump/command control, memory address and status monitors, fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO flows, common MPLL/RCAL status, continuous calibration/adaptation controls, fast flags, CR lock, TX DCC flags/status, OCLA selection, TX EQ update flag, and RX IQ phase offset.
- Raw lane 0 IRQ controls: `DPCSSYS_CR3_RAWLANE0_DIG_IRQ_CTL_*` includes reset-return request, RX reset/request/rate/pstate/adaptation IRQ status, matching clear registers, IRQ masks, lane transceiver-mode IRQs, PH2 calibration IRQs, serial loopback IRQs, DCC on-demand IRQ, and TX reset/request IRQ status and clear fields.
- Raw lane 0 PMA, TX_CTL, RX_CTL, and ATE/debug fields: `PMA_XF_*`, `TX_CTL_*`, `RX_CTL_*`, and late `PCS_XF_*` registers describe PMA/PCS handshakes, lane and supervisor override paths, TX/RX PMA input/output mirrors, RTUNE and MPHY controls, TX FSM/clock/DCC status, RX FSM/LOS/data-enable/off-cancel/adaptation status, OCLA probes, manufacturing/test overrides, master MPLL loop controls, and additional RX/TX override outputs.
- Raw lane 1 beginning: the chunk repeats the CR3 raw-lane schema for `DPCSSYS_CR3_RAWLANE1_*` from PCS TX/RX transfer registers through early FSM fast RX calibration selectors. It ends after `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL`; the later raw lane 1 FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE/debug fields continue in the next chunk.

Most masks in this slice are 16-bit-style values with an `L` suffix, matching the DPCS indirect register width used by these blocks. Several fields occupy full 16-bit words, while many hardware-control fields are single-bit enables, status bits, clear bits, or override-value/override-enable pairs.

## Control Flow

This header has no runtime control flow. It participates in compile-time register access setup:

1. AMD display code for the matching DPCS/DCN generation includes the DPCS 4.2.2 offset header and this shift/mask header.
2. Version-specific register, shift, and mask tables use generated names from this header and companion `ixDPCSSYS_*` offsets.
3. Runtime driver code uses register helpers and those tables to read, write, set, clear, or update hardware fields during PHY bring-up, link training, modeset, diagnostics, interrupt handling, suspend/resume, and reset recovery.
4. Hardware and firmware state machines perform the actual lane/common sequencing; this header only names bit positions and masks.

The macros do not encode access type, reset value, polling order, write-one-to-clear behavior, self-clearing behavior, clock-domain restrictions, power-domain validity, or whether a field is read-only, write-only, or reserved.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in CR3 lane, common, and raw-lane registers:

- Lane 3 RX statistic state includes statistic/correlation selector configuration, counter enables, sample/count completion indicators, pattern matching words, data masks, calibration comparator timing, validity-loss clear/control, and statistic stop state.
- Lane 3 analog TX state includes override values and enables for TX clocks, data enable, reference generation, VCM hold, MPLL clocks, reset, serial enable, data rate, divide-by-4, RX detect, termination codes, driver source, equalization taps, DCC DAC controls, power override, test buses, and miscellaneous analog controls.
- Raw-common state includes common control bits, MPLLA/MPLLB override and SSC configuration, lane FSM extension controls, MPLL state control, TX calibration code, SRAM initialization status, OCLA selection, supervisor analog override state, PCS/firmware ID code words, always-on common RTUNE values for RX/TX down/up paths, SRAM block configuration, power-gating overrides, VREF stats, resistor overrides, reference range, and miscellaneous configuration.
- Raw lane 0 state includes PCS TX/RX reset/request/width/rate/pstate/MPLL/loopback/data-enable handshakes, RX adaptation ACK/FOM and directed TX coefficient feedback, ATE override paths, equalization and termination controls, PH2 calibration, FSM status and fast-flow selectors, lane IRQ latches/masks/clears, PMA handshakes, TX/RX local controls, and late ATE/debug output controls.
- Raw lane 1 state in this chunk is partial: PCS TX/RX transfer, RX adaptation, equalization/termination/PH2, ATE overrides, and early FSM fast RX calibration/adaptation fields are covered, but the rest of lane 1's FSM and downstream blocks are outside the requested line range.

Persistence is hardware-defined. Configuration and override fields generally last until another modeset/link-training sequence, PHY power transition, suspend/resume, GPU reset, ASIC reset, or firmware/driver reinitialization changes them. Status, ACK, IRQ, calibration, clear, and handshake fields may be latched, sampled, write-one-to-clear, self-clearing, or valid only when the corresponding common/lane power and clocks are active. This generated header does not specify those behaviors.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies the matching CR3 offsets.
- Lane 3 RX statistic registers in this chunk map from `ixDPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_CTL0` at `0x1384` through `ixDPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_STOP` at `0x1394`; their earlier load/data/match setup registers are just before this chunk.
- Lane 3 digital and analog TX registers covered here map through `ixDPCSSYS_CR3_LANE3_DIG_ANA_TX_OVRD_OUT` at `0x13a0`, digital analog TX fields through `0x13c4`, and analog TX controls from `0x13e0` through `0x13ef`.
- CR3 raw-common fields map from `ixDPCSSYS_CR3_RAWCMN_DIG_CMN_CTL` at `0x2000` through `ixDPCSSYS_CR3_RAWCMN_DIG_AON_CMN_MISC_CONF_IN_1` at `0x2040`.
- CR3 raw lane 0 uses the full lane window: PCS at `0x3000` through `0x301f`, FSM at `0x3020` through `0x303f`, IRQ at `0x3040` through `0x305b`, PMA at `0x3060` through `0x306c`, TX_CTL at `0x3080` through `0x3084`, RX_CTL at `0x30a0` through `0x30a5`, and late ATE/PCS fields at `0x30c0` through `0x30c8`.
- CR3 raw lane 1 begins at `0x3100`; this chunk reaches `ixDPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL` at `0x3126`.
- AMD display link encoder, PHY sequencing, link-training, mode-setting, hotplug, low-power, debug, and interrupt paths consume these constants indirectly through generated register tables and register helper macros.
- Firmware and hardware state machines share ownership of many fields, especially PLL/SSC controls, reset/request handshakes, RX adaptation, DCC and RTUNE calibration, PH2 calibration, PMA/PCS handshakes, lane IRQs, and ATE/test overrides.

Behaviorally, this chunk sits below user-facing display code. It describes the bit layout needed to configure and observe CR3 lane 3, CR3 common resources, and CR3 raw lanes during display PHY operation.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong field, corrupting reserved bits, or decoding status incorrectly.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- The chunk starts immediately after `DPCSSYS_CR3_LANE3_DIG_RX_STAT_MATCH_CTL1`; the preceding RX statistic load, data mask, and first pattern-match controls are in the previous chunk.
- The chunk ends immediately before `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_BYPASS_CAL`; raw lane 1's remaining FSM, IRQ, PMA, TX_CTL, RX_CTL, and late ATE/PCS registers are in the next chunk.
- Repeated lane layouts are copy-sensitive. A generator issue can affect one lane while neighboring lanes appear correct; CR3 lane 3, raw lane 0, and raw lane 1 names must pair with their matching offsets and tables.
- Status, clear, and mask registers use similar field names. Mixing IRQ status masks with clear or interrupt-mask masks can drop events, leave stale events latched, or create repeated interrupts.
- PCS, PMA, and analog override fields can bypass normal hardware sequencing. Bad masks around reset, request, data-enable, loopback, MPLL selection, termination, RTUNE, RX adaptation, PH2 calibration, ATE, TX DCC, or TX equalization controls can leave a lane in a state higher-level display code cannot reason about.
- Common PLL, SSC, SRAM, power-gating, VREF, resistor, and RTUNE fields are shared resources. Wrong masks here can affect multiple lanes rather than only the local lane being debugged.
- FSM fast-flow and calibration bits are sequencing-sensitive. Incorrect masks for fast RX startup/adapt/AFE/DFE/bypass/reference/IQ/VCO/common calibration or continuous calibration flags can cause link training failure, poor equalization, unstable links, or stuck polling loops.
- Reserved masks are still emitted. Consumers should not treat reserved fields as safe software-owned configuration fields unless hardware documentation explicitly says so.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support for the DCN/DPCS generation that includes DPCS 4.2.2. Missing, renamed, or malformed macros should fail where generated register, shift, and mask tables are initialized.
- Mechanically verify that complete registers in this range have consistent `__SHIFT` and `_MASK` pairs, allowing the known cross-chunk boundaries before `DPCSSYS_CR3_LANE3_DIG_RX_STAT_STAT_CTL0` and after `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_DFE_CAL`.
- Cross-check every complete register group against `dpcs_4_2_2_offset.h`, especially lane/common address windows: lane 3 around `0x1384` to `0x13ef`, raw common around `0x2000`, raw lane 0 around `0x3000`, and raw lane 1 around `0x3100`.
- Diff against AMD's source register database and nearby DPCS generated variants where lane layouts are expected to match.
- Exercise DisplayPort and HDMI link bring-up across available rates, widths, lanes, and power states. Expected signals are stable link training, completed RX adaptation, no stuck reset/request handshakes, no unexpected lane IRQs, and valid common PLL/RTUNE/SRAM status.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in RX statistic, analog TX, raw-common, PCS, FSM, IRQ, PMA, TX_CTL, RX_CTL, and ATE fields.
- Use register dumps or PHY debug traces during failing links to confirm that RX statistic counters, lane 3 TX analog overrides, MPLL/SSC state, RTUNE values, RX adaptation ACK/FOM, directed TX coefficient feedback, DCC status, FSM state, CR lock, IRQ clear/mask bits, PH2 calibration, OCLA probes, and ATE overrides decode correctly.
- Exercise diagnostic paths where available: RX statistic sampling, OCLA and UPCS OCLA, serial loopback, RX adaptation debug, PH2 calibration, DCC on-demand IRQs, common calibration, and manufacturing/test override flows.

## Cross-Chunk Notes

The previous chunk owns the beginning of the CR3 lane 3 RX statistic sequence, including load value, data mask, and `MATCH_CTL0/1`. This chunk starts at `STAT_CTL0`, finishes lane 3 RX statistic and TX analog fields, covers the CR3 raw-common block and all CR3 raw lane 0, then starts raw lane 1 through early FSM fast RX calibration selectors. The next chunk should continue raw lane 1 at `DPCSSYS_CR3_RAWLANE1_DIG_FSM_FAST_RX_BYPASS_CAL` and reconcile the rest of lane 1's raw-lane window. The final per-file research document should merge these artificial boundaries before making whole-file claims about all DPCS 4.2.2 CR3 registers.
