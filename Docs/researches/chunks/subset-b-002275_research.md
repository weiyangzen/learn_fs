# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 38995-41436

## Scope

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, allocation, or executable control flow. Its exported contract is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each macro describes one 16-bit DPCS/PHY register field position or already-shifted mask.

The range starts in the middle of the `DPCSSYS_CR2_LANE2` analog TX equalization override block, covers the rest of lane 2 RX/TX analog override and status fields, then covers most of `DPCSSYS_CR2_LANE3` digital ASIC, TX power-control, RX statistics, and TX analog fields. It then moves to `DPCSSYS_CR2_RAWCMN` common PHY registers, `RAWLANE0` PCS/FSM/IRQ fields, and the start of `RAWLANE0` PMA transfer/override fields. The chunk ends inside `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT`; adjacent chunks own the beginning of the lane 2 TX-EQ context and the remainder of raw-lane0 PMA/TX control metadata.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display/link PHY register metadata. It has no Ceph, filesystem, distributed-storage, network protocol, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide ASIC-specific bit geometry for DCN 3.1.4 DPCS CR2 lane, common, PCS, FSM, IRQ, and PMA registers. Runtime display code includes this header with the matching `dpcs_3_1_4_offset.h` file so register tables can map logical link-encoder fields onto the exact CR-indirect DPCS hardware layout.

The covered hardware areas are:

- Lane 2 analog TX/RX controls: TX equalization leg-pull enable/direction, pre/post controls, RX control and power overrides, RX CDR/VCO overrides, RX calibration DAC and slicer controls, AFE attenuation/gain/CTLE, scope/IQ phase controls, RX term-code controls, MPHY and signal-detect overrides, TX DCC DAC overrides, and analog TX readback/test registers.
- Lane 3 digital ASIC boundary controls: per-lane override inputs/outputs for TX rate/width/power state, MPLL selection, TX data/reset/async/ack signaling, RX request/rate/power/adaptation/loopback signaling, and ASIC input/output mirror registers.
- Lane 3 TX power and diagnostics: P-state tables for `P0`, `P0S`, `P1`, and `P2`; TX power-up timing registers; DCC CR bank address/data and DCC DAC programming; TX clock alignment and LBERT control; RX stat pattern/match/count controls; calibration comparator clocking; and statistic stop controls.
- Lane 3 analog TX controls: TX term-code, TX-EQ, TX DCC DAC, TX override/status, and analog TX miscellaneous/reserved registers.
- CR2 raw-common PHY controls: common functional reset, `MPLLA`/`MPLLB` word-divider, TX clock divider, bandwidth and spread-spectrum overrides, lane FSM extension, MPLL state control, TX calibration code, SRAM init done, OCLA/debug, supervisor analog overrides, PCS/FW ID codes, AON retune values for RX/TXDN/TXUP across entries 0-7, AON SRAM block config, power-gate/supervisor/resistance/reference range overrides, VREF stats, and miscellaneous common configuration.
- CR2 raw-lane0 PCS/FSM/IRQ/PMA metadata: PCS TX/RX override and PCS mirror registers, RX adaptation ACK/FOM and TX EQ direction hints, lane number and ATE overrides, RX EQ/phase/term controls, FSM override/status/fast-path timing controls, continuous calibration/adaptation flags, CR lock and DCC status, IRQ status/clear/mask registers, PMA lane/supervisor/TX/RX handshakes, rtune request/ack, and the start of MPHY PMA override input/output controls.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the field mask in its final register position.
- Register names encode the DPCS CR instance and block, such as `DPCSSYS_CR2_LANE3_DIG_ASIC_TX_OVRD_IN_0`, `DPCSSYS_CR2_RAWCMN_DIG_MPLLA_OVRD_IN`, `DPCSSYS_CR2_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN`, and `DPCSSYS_CR2_RAWLANE0_DIG_IRQ_CTL_IRQ_MASK`.

The lane analog fields are dominated by override-enable/value pairs. Examples include `TX_EQ_OVRD_EN`, `TX_ANA_LOAD_CLK`, `TX_ANA_CTRL_PRE`, `TX_ANA_CTRL_POST`, `RX_CTL_OVRD_EN`, `RX_PWR_OVRD_EN`, `RX_VCO_CDR_OVRD_EN`, `RX_CDR_FREQ_TUNE_OVRD_EN`, `RX_CAL_DAC_CTRL_OVRD`, `RX_AFE_OVRD_EN`, `RX_ANA_SLICER_CTRL_OVRD_EN`, signal-detect override enables, and DCC DAC override enables. These fields let low-level driver or firmware code force link PHY state for calibration, bring-up, debug, or controlled mode transitions.

The lane 3 ASIC-facing fields describe handshakes between digital link logic and the physical lane. TX-side fields include `TX_WIDTH`, `TX_RATE`, `TX_PSTATE`, `TX_REQ`, `TX_RESET`, `TX_ACK`, `TX_BEACON_EN`, `TX_FIFO_CLK_EN`, `TX_DATA_EN`, `TX_DCC_CALDONE`, MPLL enable/select state, async data controls, polarity/inversion, and serial loopback. RX-side fields include `RX_RATE`, `RX_PSTATE`, `RX_REQ`, `RX_RESET`, `RX_ACK`, `RX_VALID`, `RX_ADAPT_REQ`, `RX_ADAPT_ACK`, adaptation disable/continuous control, rate-change ACK, power-up/down controls, parallel/serial loopback, and RX data-enable state.

The TX power-control fields are packed state descriptors. `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` carry per-state TX power-up/down, VBOOST, iboost, rate, main/pre/post equalization, term control, and state-selection information. `TX_PWRCTL_TX_PWRUP_TIME_*` splits timing and enable bits across several registers. `DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR` define an indexed DCC programming path.

The raw-common `MPLLA`/`MPLLB` fields expose parallel A/B PLL controls. Each PLL has word-divide, TX clock divisor, div8/div10 enable, bandwidth override, and spread-spectrum override fields. Common support fields include `PHY_FUNC_RST`, lane FSM extension operation, MPLL state wait/min/max counters, TX calibration code, SRAM init done, OCLA/debug bits, supervisor analog override, ID-code readbacks, AON retune values, SRAM block configuration, power-gate controls, VREF stats, resistance override/input-output values, and reference-range override.

The raw-lane0 PCS transfer fields define override paths between PCS, ASIC, and PMA. `PCS_XF_TX_*` and `PCS_XF_RX_*` groups contain override values/enables and PCS mirror values for TX request/reset/async/data/loopback, RX request/reset/rate/pstate/adaptation/term/valid/data/PWM controls, and link-training support values such as `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, and `RX_TXPOST_DIR`. ATE-specific fields expose testing overrides for VBOOST, IBOOST, beacon, loopback, TX async data, and loss/adaptation controls.

The raw-lane0 FSM and IRQ groups define status and event plumbing. FSM registers expose override control, memory/status monitors, fast-path cycle counters for RX startup/adaptation/calibration/power/VCO/SUP/TX paths, continuous calibration and adaptation counters, fast flags, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset. IRQ registers expose individual status and clear bits for reset/request/rate/pstate/adaptation, PH2 calibration, serial loopback, DCC on-demand, TX reset/request, plus two mask registers.

The PMA transfer fields at the end define lane/supervisor/TX/RX handshake overrides and readbacks. They include `LANE_MPLLA_EN`, `LANE_MPLLB_EN`, `SUP_STATE_OVRD_EN`, TX/RX request and reset override value/enable bits, PMA data-enable overrides, loopback controls, TX/RX `ACK` readbacks, lane rtune request/ack, and MPHY/PMA PWM, term, async, and clock-selection controls.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`, construct register/field tables, and then use AMD display register helpers to perform MMIO or CR-indirect reads and writes.

A typical DCN 3.1.4 path is:

1. `display/dc/resource/dcn314/dcn314_resource.c` includes the DCN and DPCS 3.1.4 offset/shift-mask headers.
2. Resource construction macros build link-encoder register tables with generated register offsets and matching field masks/shifts. In this file, `le_shift` and `le_mask` expand `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. Link-encoder, HPO DP, GPIO, IRQ, and clock/resource code access those table entries through helper macros such as `REG_GET`, `REG_UPDATE`, `REG_UPDATE_2`, and related `reg_helper.h` operations.
4. Higher-level display/link code sequences PHY reset, PLL setup, TX/RX lane enable, DisplayPort alternate-mode handshakes, power-state changes, training/equalization, calibration, and debug/status polling.

The header itself does not encode ordering, delays, polling loops, lane ownership, or policy. Those rules live in the display link encoder, HPO DP link encoder, clock manager, GPIO, IRQ, hardware-sequencer, and firmware-facing code that consumes the generated register tables.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by DPCS/PHY programming, link training, modesets, hotplug, DP alt-mode transitions, suspend/resume, runtime power management, and GPU reset.

State represented by this chunk includes:

- Lane analog state for TX equalization, termination, DCC DACs, signal-detect behavior, RX AFE/CTLE/slicer/calibration, CDR/VCO controls, and IQ phase controls.
- Lane 3 digital state for TX/RX width, rate, power state, reset/request/ack handshakes, data enable, loopback, async signaling, adaptation request/ack, and ASIC mirror values.
- TX power-control state for each P-state and associated timing, DCC bank/DAC programming, clock alignment, LBERT controls, and RX-stat capture counters.
- Common PHY state for resets, PLL dividers, spread-spectrum controls, MPLL state waits, calibration codes, SRAM init status, retune values, power-gate/supervisor/resistance/reference overrides, and ID/readback registers.
- Raw-lane0 PCS/FSM/IRQ/PMA state for TX/RX PCS overrides, adaptation FOM and equalization directions, ATE overrides, RX phase/term calibration, FSM fast counters and flags, IRQ status/masks/clears, PMA supervisor/TX/RX handshakes, rtune, and MPHY PWM/term/async controls.

Many fields are status-like readbacks, including ACK bits, calibration done/status bits, FOM values, statistics counters, IRQ status bits, FSM status monitors, CR lock, SRAM init done, ID codes, retune values, VREF stats, power/status mirrors, and PMA input mirrors. Other fields are writable controls that can immediately change live PHY behavior or arm self-clearing pulses. Fields named `*_SELF_CLEAR_DISABLE`, `*_CLK`, `*_REQ`, `*_CLR`, or `*_UPDATE_FLAG` are especially sequencing-sensitive because they often represent pulses, clear-on-write paths, or control strobes rather than passive configuration.

Bad values can persist until the lane, common PHY, DPCS block, display link, or whole GPU is reset or reprogrammed. Some link state is reconstructed during modeset, hotplug handling, link training, and suspend/resume, but this generated header has no restore logic; it only defines the bit layout that those paths rely on.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which provides the matching generated offsets. These masks are only correct when paired with the DPCS 3.1.4 offset header and the DCN314 resource layout.

Visible integration points include:

- `display/dc/resource/dcn314/dcn314_resource.c`, the only direct include of `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h` in this tree. It builds DCN314 link encoder shift/mask tables using `DPCS_DCN31_MASK_SH_LIST`.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and generation-specific link encoder headers, which define the logical DPCS field lists used by resource files. These lists include DPCS PHY TX data/pstate/MPLL, SRAM, FIFO, reset/request/ack, reference clock, PLL, TX-EQ, DP alt-mode, and debug fields.
- `display/dc/dio/dcn21/dcn21_link_encoder.*` and related DIO link encoder code, which show how DPCS field tables are consumed by `REG_GET`/`REG_UPDATE` calls for DP alt-mode, reference-clock, TX lane, and PHY control behavior.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.*`, which uses RDPCSTX/DPCS metadata for high-performance DisplayPort link encoder paths, including `RDPCS_PHY_DPALT_DISABLE`.
- GPIO, IRQ, clock-manager, and resource files for nearby generations, which include DPCS generated headers and use the same register-table expansion pattern.

The generated namespace is cross-generation but not interchangeable. Nearby headers such as `dpcs_3_0_0_sh_mask.h`, `dpcs_4_0_0_sh_mask.h`, `dpcs_4_2_2_sh_mask.h`, and `dpcs_4_2_3_sh_mask.h` contain similar register names, but field availability, offsets, and exact masks may differ. Consumers must bind the correct offset and mask pair for the target ASIC.

## Risks And Edge Cases

The main risk is silent PHY misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad constant can update a neighboring field, truncate a multi-bit value, miss a control pulse, decode a status bit incorrectly, or force the wrong lane/PLL state.

Chunk-boundary risk is present. The first lines are already inside the lane 2 TX-EQ override group, and the final lines stop before the remainder of `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT` and later PMA/TX controls. The final per-file report should merge adjacent chunks before making whole-block claims about lane 2 TX-EQ or raw-lane0 PMA coverage.

Lane and instance pairing are critical. This chunk mixes CR2 lane 2, CR2 lane 3, CR2 raw-common, and CR2 raw-lane0 names. A field copied into the wrong lane instance or paired with a mismatched offset can create failures that look like timing or link-training bugs.

PLL and clock fields are high risk. `MPLLA`/`MPLLB` dividers, bandwidth overrides, spread-spectrum controls, word-divide bits, TX clock dividers, and MPLL state timing affect symbol clocks and link stability. Wrong masks can cause no-link, intermittent training failure, jitter, or mode-specific display loss.

Analog override fields are calibration-sensitive. TX equalization, termination, VBOOST/IBOOST, DCC DAC, RX AFE/CTLE/slicer, CDR/VCO, signal detect, and IQ phase controls can produce subtle signal-integrity problems, particularly at higher DP rates, with certain cables, docks, alt-mode paths, or board designs.

Power-state and handshake fields are sequencing-sensitive. TX/RX request/reset/ack, data-enable, pstate, rate, loopback, adaptation, PMA ACK, rtune, and PMA/PWM controls must be changed in hardware-defined order. The masks do not express waits, dependencies, or whether a field is read-only, write-one-to-clear, pulse, or latched.

IRQ and status fields can mislead diagnostics. Incorrect IRQ mask, status, or clear constants may hide lane events, leave interrupts stuck, or clear the wrong event. RX statistic and LBERT fields can return plausible but wrong debug data if match controls or counter masks are wrong.

Reserved fields appear frequently. Generic register updates must preserve reserved bits unless the hardware database explicitly allows otherwise. Full-register writes using these masks can unintentionally disturb reserved or test-only state.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN314 resource construction, link encoder, HPO DP link encoder, GPIO, IRQ, and clock/resource users that include generated DPCS headers.
- Generated-register consistency checks that every field has a matching offset/header pair, each `*_MASK` matches its `*_SHIFT` width, and no logical field list references a missing generated macro.
- Cross-generation diffs against AMD's authoritative DPCS 3.1.4 register database and nearby DPCS 3.0.x/4.x headers, with expected differences explicitly reviewed.
- Link bring-up tests across DP rates, lane counts, MST/HPO paths, USB-C/DP alt-mode, dock paths, hotplug/unplug, suspend/resume, runtime PM, and GPU reset.
- PLL and clock tests that exercise MPLLA/MPLLB selection, dividers, spread-spectrum, reference clock enable/range, symbol clock gating, and clock-ready/status readbacks.
- TX/RX lane tests for request/reset/ack handshakes, pstate/rate transitions, data-enable, polarity/inversion, loopback, adaptation request/ack, RX valid, and PMA ACK/rtune behavior.
- Signal-integrity tests for TX EQ pre/main/post, term codes, VBOOST/IBOOST, DCC DAC programming, RX AFE/CTLE/slicer, CDR/VCO controls, signal detect, and IQ phase calibration at high link rates.
- IRQ/debug tests that trigger reset/request/rate/pstate/adaptation/PH2 calibration/TX events, verify mask behavior, confirm clear bits, and read RX-stat/LBERT/FSM counters.
- Recovery tests that verify bad or interrupted link-training sequences are cleaned up by modeset, hotplug recovery, suspend/resume, or GPU reset.

Regression symptoms from bad constants include blank display output, intermittent DP link training failures, reduced maximum link rate, hotplug or alt-mode failures, unstable docks, flicker at high rates, stuck reset/request/ack bits, failed suspend/resume recovery, misleading PHY debug counters, missing or storming interrupts, and failures isolated to DCN 3.1.4 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dpcs_3_1_4_sh_mask.h`. The preceding chunk owns the beginning of the lane 2 analog TX-EQ override context before line 38995. The following chunk owns the remainder of the raw-lane0 PMA MPHY override output register and subsequent DPCS register blocks after line 41436. The merge/reconciliation lane should treat this document as the CR2 lane 2 tail, lane 3, raw-common, and raw-lane0 PCS/FSM/IRQ/PMA opening portion of the full DPCS 3.1.4 shift/mask contract.
