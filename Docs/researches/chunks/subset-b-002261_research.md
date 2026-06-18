# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h Lines 4854-7300

## Scope

This chunk is a generated AMD DPCS 3.1.4 register shift/mask header slice. It covers the end of CR0 lane 2 RX statistic and analog-control fields, a broad CR0 lane 3 lane-control and TX/RX statistic subset, CR0 raw-common PLL/retune/power-gating fields, and the start of CR0 raw lane 0 PCS/FSM/IRQ/PMA crossbar fields. The file provides C preprocessor constants only; it defines no functions, structs, storage, or executable control flow.

## Purpose

The macros provide bit positions (`__SHIFT`) and bit masks (`_MASK`) for programming or decoding 16-bit DPCS indirect registers. They are consumed together with the matching offset header, especially `dpcs_3_1_4_offset.h`, whose `ixDPCSSYS_...` constants name the register addresses. Display link code can then use local register-field helpers such as `LE_SF(register, field, mask_sh)` to populate register metadata tables from the generated mask/shift names.

Operationally, this range exposes controls for:

- RX statistic matching and sampling counters on lanes 2 and 3.
- Lane 2 analog TX/RX override outputs, term-code clocks, EQ/pre/post controls, VCO/calibration/DAC/slicer/scope status, signal-detect override, and MPHY/PWM controls.
- Lane 3 ASIC-facing TX/RX override and observation fields, TX power-state sequencing, DCC DAC programming, TX LBERT/clock alignment, RX statistic blocks, and analog TX overrides.
- Raw common PLL and always-on common controls for MPLLA/MPLLB override, bandwidth, spread-spectrum, retune values, SRAM bootload, power gating, reference range, VREF, and resource handshake.
- Raw lane 0 PCS transfer, adaptation, ATE, FSM fast-state, calibration, interrupt, clear, mask, and PMA lane override fields.

## Important Macro Families

The lane 2 section starts in the middle of `DPCSSYS_CR0_LANE2_DIG_RX_STAT_STAT_CNT_4` and continues with `STAT_CNT_5`, `STAT_CNT_6`, `RX_STAT_CAL_COMP_CLK_CTL`, `RX_STAT_MATCH_CTL2` through `MATCH_CTL5`, `STAT_CTL2`, and `STAT_STOP`. These provide statistic counter fields, sample-done bits, pattern/mask slices, delay controls, and stop controls for RX sampling hardware.

The lane 2 analog block includes `DIG_MPHY_RX_PWM_CTL`, `DIG_MPHY_RX_TERM_LS_CTL`, `DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, `DIG_ANA_TX_OVRD_OUT`, term-code override/clock registers, six TX EQ override registers, RX control/power/VCO/calibration/DAC/AFE/scope/slicer/IQ registers, `DIG_ANA_STATUS_0/1`, signal-detect override, TX DCC DAC override, and low-level `LANE2_ANA_TX_*` / `LANE2_ANA_RX_*` register masks. These fields represent direct analog PHY controls and status, including enable/reset/data-rate bits, termination codes, DCC, pre/main/post/equalization values, AFE/CTLE/slicer settings, and measurement/test-bus selectors.

The lane 3 digital ASIC-facing block begins at `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` and includes TX override inputs `0` through `5`, TX override outputs, RX override outputs, ASIC in/out mirrors, and lane loopback/master-lane controls. It also defines lane 3 TX power control P-states (`P0`, `P0S`, `P1`, `P2`), power-up timing registers, DCC bank/DAC address/data/ack fields, `TX_CLK_ALIGN_TX_CTL_0`, `TX_LBERT_CTL`, and the lane 3 RX statistic registers. These mirror lane-facing state machines and allow software or firmware to override or observe clock-ready, reset, data enable, request/ack, P-state/rate/width, loopback, beacon, HDMI mode, and cursor/equalization state.

The raw common block covers `DPCSSYS_CR0_RAWCMN_DIG_CMN_CTL`, MPLLA/MPLLB override and SSC registers, `LANE_FSM_OP_XTND`, `CMN_CTL_1`, `MPLL_STATE_CTL`, OCLA/debug control, supervisor analog override, firmware ID fields, eight repeated retune value triplets (`RTUNE_RX_VAL_n`, `RTUNE_TXDN_VAL_n`, `RTUNE_TXUP_VAL_n`), SRAM bootload configuration, common power-gate override in/out, supervisor force/ack overrides, VREF status, resource request/ack overrides, reference range override, and miscellaneous MPLL power-down timing. These fields are shared common-lane state rather than per-display-lane state.

The raw lane 0 block begins at `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN` and runs through `DPCSSYS_CR0_RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT` in this chunk. It defines PCS transfer overrides and live PCS inputs/outputs for TX and RX, RX adaptation acknowledgement/FOM and TX pre/main/post direction outputs, lane number, reserved scratch fields, ATE overrides, RX EQ and phase-two calibration controls, FSM override/status/fast-state flags, calibration status flags, interrupt status/clear/mask registers, and PMA lane MPLLA/MPLLB enable override bits.

## Control Flow and State Behavior

There is no executable control flow in this header. Runtime behavior is created by driver code that combines an address macro from the offset header with these masks/shifts to read, write, poll, or compose bitfields.

The hardware state represented here is mostly volatile MMIO or indirect-register state. Some fields are command-like or handshake-oriented: `*_OVRD_EN` bits select software override paths, `*_ACK` and `*_REQ` fields expose handshakes, `*_IRQ_CLR` fields clear sticky interrupt/status bits, `*_DONE` and calibration status fields report hardware progress, and P-state/power-up timing fields configure sequenced PHY state transitions. None of that state persists in this header; persistence, reset defaults, and serialization are determined by the GPU hardware and whatever driver or firmware writes these registers.

## Dependencies and Integration Points

- Depends on consistent generated naming with `dpcs_3_1_4_offset.h`; the register stem before `__FIELD` must match an `ix...` offset macro when driver code emits real accesses.
- Integrated by AMD display/link encoder register tables through macros that expect generated `register__field_MASK` and `register__field__SHIFT` names.
- Shares register naming conventions with other generated ASIC headers such as DCN/DPCS variants, making cross-generation code reuse possible when fields are compatible.
- The constants are plain preprocessor macros, so they are globally visible after inclusion and have no type protection.

## Risks and Edge Cases

- The chunk begins mid-register at line 4854, so the first visible macro is only the `SMPL_CNT1_DONE_MASK` for `STAT_CNT_4`; the corresponding shift and count mask are in the prior chunk.
- Many fields are reserved masks. Driver writes should preserve reserved bits unless hardware documentation explicitly requires otherwise.
- Override-enable fields are high risk because setting `*_OVRD_EN` without matching value bits can disconnect normal hardware/firmware sequencing for clocks, resets, PLLs, power gating, calibration, or lane handshakes.
- Interrupt clear fields are write-sensitive. A stale mask/shift or write-one-clear misunderstanding can drop reset/request/rate/P-state/adaptation/phase-calibration notifications.
- Lane 2, lane 3, raw-common, and raw-lane0 blocks are interleaved in one header slice. Code generation or manual edits that assume a single lane context can bind a valid field name to the wrong register address family.
- Register widths in this slice are represented with 16-bit masks using `L` suffixed literals. Callers using 32-bit register helpers must still preserve the intended lower-16-bit field semantics.

## Test and Validation Signals

Useful validation for this chunk is compile-time and hardware-table oriented rather than unit-test oriented:

- Build AMDGPU display code that includes this generated header and any table macros that reference `DPCSSYS_CR0_RAWLANE0_*`, `DPCSSYS_CR0_LANE2_*`, `DPCSSYS_CR0_LANE3_*`, or `DPCSSYS_CR0_RAWCMN_*` fields.
- Check that every used `LE_SF(...)` or equivalent field helper expands to both a `_MASK` and `__SHIFT` macro.
- Diff generated `dpcs_3_1_4_sh_mask.h` against its register database source when updating ASIC headers; manual edits are especially risky.
- On hardware, monitor link bring-up, lane power-state transitions, PHY calibration completion, RX adaptation, interrupt clear/mask behavior, and DCC/retune status when fields in this range are touched.

## Research Notes

This is a source chunk report only. The later merge lane should combine it with neighboring chunks for the full `dpcs_3_1_4_sh_mask.h` file-level report, preserving that the overall file is a generated DPCS mask/shift catalog rather than handwritten control logic.
