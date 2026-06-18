# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 121324-123730

## Scope

This chunk is a generated AMDGPU NBIO 6.1 register bitfield header segment for the DesignWare E12MP x4 PCIe PHY namespace `DWC_E12MP_PHY_X4_NS_X4_3`. It contains only C preprocessor constants: `__SHIFT` and `_MASK` definitions for 16-bit PHY register fields. There are no functions, structs, enums, executable branches, allocation paths, locks, or runtime storage in this range.

The chunk begins in the middle of `RAWLANE1_DIG_AON_RX_ADPT_VGA`: the `VGA_ADPT_VAL` and reserved masks are present here, while the matching shift definitions are in the previous chunk. It ends in the middle of `SUPX_DIG_MPLLB_MPLL_PWR_CTL_PCLK_EN_AND_VCO_CLK_STABILIZATION_TIME_THRESHOLD`: only the two shift constants are in this chunk, while the masks begin in the next chunk. Any merged per-file research should treat those two boundary registers as split across adjacent chunks.

## Purpose

The purpose of this header range is to publish compile-time bit layout metadata for NBIO 6.1 PHY registers. Driver code that reads or writes a register can use the companion offset/SMN headers to locate the register and these macros to isolate, test, or compose individual fields. The macro naming pattern is:

- `REGISTER__FIELD__SHIFT` for the least significant bit position of a field.
- `REGISTER__FIELD_MASK` for the field mask before shifting/extraction.

The selected range is mostly PHY-facing rather than high-level NBIO doorbell/mailbox logic. It describes receiver adaptation outputs, fast calibration flags, lane IRQ bits, PMA/PCS crossing override state, TX/RX finite-state-machine controls, and shared SUPX PLL/refclk override and status fields. These definitions are part of the register ABI between the AMDGPU driver and the NBIO/PCIe PHY hardware.

## Important Macro Groups

### Raw lane 1 AON receiver adaptation

The first part of the chunk completes and continues `RAWLANE1_DIG_AON` field metadata:

- `RAWLANE1_DIG_AON_RX_ADPT_VGA` exposes the `VGA_ADPT_VAL` 10-bit mask and reserved upper bits.
- `RAWLANE1_DIG_AON_RX_ADPT_CTLE` exposes CTLE boost and pole adaptation values.
- `RAWLANE1_DIG_AON_RX_ADPT_DFE_TAP1` through `DFE_TAP5` expose DFE tap adaptation values, with tap 1 using a 13-bit value and taps 2-5 using 12-bit values.
- `RAWLANE1_DIG_AON_RX_ADAPT_DONE` exposes the single-bit adaptation completion flag.
- `RAWLANE1_DIG_AON_FAST_FLAGS` exposes individual fast-path/calibration flags such as `FAST_RX_STARTUP_CAL`, `FAST_RX_ADAPT`, `FAST_RX_AFE_CAL`, `FAST_RX_DFE_CAL`, `FAST_RX_BYPASS_CAL`, `FAST_RX_REFLVL_CAL`, `FAST_RX_IQ_CAL`, `FAST_RX_AFE_ADAPT`, `FAST_RX_DFE_ADAPT`, `FAST_SUP`, `FAST_TX_CMN_MODE`, `FAST_TX_RXDET`, `FAST_RX_PWRUP`, `FAST_RX_VCO_WAIT`, and `FAST_RX_VCO_CAL`.
- `RAWLANE1_DIG_AON_RX_SLICER_CTRL_EVEN` and `_ODD` expose 4-bit analog slicer controls.
- `RAWLANE1_DIG_AON_LANE_CMNCAL_STATUS` exposes common-calibration init/done status.
- `RAWLANE1_DIG_AON_ADPT_CTL_0` through `_7` define full-width `VAL` masks for opaque/adaptation control words.

These fields are state/diagnostic metadata for per-lane receiver calibration. Most reset defaults in the companion default header are zero, except several related lane defaults elsewhere in the same register family (for example DFE tap and slicer values), so consumers must respect the exact field widths rather than assuming all lane calibration values are boolean.

### Raw lane 1 IRQ control and PMA/TX/RX control

The lane 1 IRQ block defines one-bit request/status/clear registers and a packed IRQ mask register:

- `RESET_RTN_REQ` has a one-bit reset-return request.
- `RX_RESET_IRQ`, `RX_REQ_IRQ`, `RX_RATE_IRQ`, `RX_PSTATE_IRQ`, `RX_ADAPT_REQ_IRQ`, and `RX_ADAPT_DIS_IRQ` expose individual IRQ status bits.
- Matching `_IRQ_CLR` registers expose one-bit clear fields for the same events.
- `IRQ_MASK` packs masks for RX request, rate, pstate, adaptation request/disable, and reset IRQs.

The PMA and lane crossing macros describe override and PMA input/output signal bits:

- `PMA_XF_LANE_OVRD_IN` and `PMA_XF_LANE_OVRD_OUT` contain lane power, reset, and AFE ready override fields.
- `PMA_XF_SUP_OVRD_IN` and `PMA_XF_SUP_PMA_IN` contain PLL/clock/readiness signals shared between lane and SUP/PMA logic.
- `PMA_XF_TX_OVRD_OUT`, `PMA_XF_TX_PMA_IN`, `PMA_XF_RX_OVRD_OUT`, and `PMA_XF_RX_PMA_IN` expose TX/RX electrical idle, request, acknowledgment, detection, power, rate, and valid/status style fields.
- `PMA_XF_LANE_RTUNE_CTL` exposes lane RTUNE control/status bits.

The TX/RX control registers then expose FSM and override controls:

- `TX_CTL_TX_FSM_CTL` includes TX common-mode, RX detect, electrical idle, AFE enable, and related override/control fields.
- `TX_CTL_TX_CLK_CTL` exposes TX clock ready/enable style controls.
- `RX_CTL_RX_FSM_CTL`, `RX_CTL_RX_LOS_MASK_CTL`, and `RX_CTL_RX_DATA_EN_OVRD_CTL` expose RX FSM reset/powerup/calibration, loss-of-signal masking, and data-enable override controls.
- `RX_CTL_OFFCAN_CONT_STATUS` and `RX_CTL_ADAPT_CONT_STATUS` expose continuation/status bits for offset cancellation and adaptation.

### Raw lanes 2 and 3 PCS/FSM/AON/IRQ/PMA/TX/RX

The middle of the chunk repeats the same generated pattern for `RAWLANE2` and `RAWLANE3`, while also including their PCS and FSM blocks. Important groups include:

- `DIG_PCS_XF_TX_OVRD_IN`, `_TX_OVRD_IN_1`, `_TX_PCS_IN`, `_TX_OVRD_OUT`, and `_TX_PCS_OUT` for TX-side PCS crossing signals. Field names include reset, power, rate, de-emphasis, margin, swing, polarity, electrical-idle, and beacon-related controls.
- `DIG_PCS_XF_RX_OVRD_IN`, `_RX_OVRD_IN_1`, `_RX_OVRD_IN_2`, `_RX_OVRD_IN_3`, `_RX_PCS_IN`, `_RX_PCS_IN_1` through `_4`, `_RX_OVRD_OUT`, and `_RX_PCS_OUT` for RX-side PCS crossing signals. Field names cover reset, power, rate, equalization, adaptation request/ack, figure of merit, polarity, termination, data enable, and status.
- `DIG_PCS_XF_RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, `RX_TXPOST_DIR`, and `LANE_NUMBER` for adaptation handshake/status and lane identification.
- `DIG_FSM_FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, `FAST_RX_*`, `FAST_SUP`, `FAST_TX_*`, and `CMNCAL_STATUS` for per-lane FSM override, monitor, and accelerated calibration status/control fields.
- `DIG_AON_AFE_*_IDAC_OFST`, `DIG_AON_DFE_*_VDAC_OFST`, `RX_PHSADJ_*`, `RX_IQ_PHASE_ADJUST`, PLL coarse tune, RTUNE values, `INIT_PWRUP_DONE`, receiver adaptation values, slicer controls, common calibration status, and eight full-width adaptation control words.
- The same one-bit IRQ status/clear/mask pattern and PMA/TX/RX control pattern described for lane 1.

These repeated lane blocks are valuable for generated-header validation because the field names, shifts, and masks should remain lane-isomorphic except where the register database intentionally differs. Lane 2 and lane 3 default values in `nbio_6_1_default.h` also show the same reset/default pattern for PCS override words, AON offsets, DFE taps, slicers, IRQ registers, PMA crossing state, and TX/RX control words.

### SUPX shared PLL/refclk/override block

The last part of the range moves from per-lane macros to `SUPX_DIG`, the shared PHY/supply/PLL block for the same `X4_3` instance:

- `SUPX_DIG_IDCODE_LO` and `_HI` define full-width ID code value fields.
- `SUPX_DIG_REFCLK_OVRD_IN` contains refclk select, enable, spread-spectrum clocking, and SSC mode fields.
- `SUPX_DIG_MPLLA_B_DIV_CLK_OVRD_IN` contains divided-clock enables and multipliers for MPLLA/MPLLB.
- `SUPX_DIG_MPLLA_OVRD_IN_0/1/2` and `MPLLB_OVRD_IN_0/1/2` expose PLL override inputs, including multiplier, SSC enable/range/clock select, reference clock selection, MPLL enable, power-down, reset, and calibration/feedback controls.
- `SUPX_DIG_SUP_OVRD_IN`, `_OUT`, and `LVL_OVRD_IN` expose supply-level override/ready/reset/control fields.
- `SUPX_DIG_MPLLA_ASIC_IN_*`, `MPLLB_ASIC_IN_*`, `MPLLA_B_DIV_CLK_ASIC_IN`, `ASIC_IN`, and `LVL_ASIC_IN` mirror ASIC-provided input fields for the same clock/PLL/control paths.
- `SUPX_DIG_ANA_MPLLA_OVRD_OUT`, `ANA_MPLLB_OVRD_OUT`, `ANA_RTUNE_OVRD_OUT`, `ANA_RX_TERM_OVRD_OUT`, and `ANA_STAT` expose analog override outputs and status bits.
- `SUPX_DIG_MPLLA_MPLL_PWR_CTL_*` and the beginning of `SUPX_DIG_MPLLB_MPLL_PWR_CTL_*` define calibration, override, status, timing threshold, coarse-tune, skip-calibration, and spread-spectrum fields for the MPLL power-control logic.

The `MPLLA` and `MPLLB` power-control definitions are symmetric in this chunk up to the split boundary. Status fields such as `FSM_STATE`, `MPLL_TOOSLOW`, `CHKFRQ_DONE`, `MPLL_CAL_RDY`, lane selection, PCLK/output/feedback clock enables, calibration, reset, and analog enable provide test/debug visibility into PLL bring-up.

## APIs, Types, and Functions

This chunk defines no callable APIs, C types, or functions. Its public interface is the macro namespace consumed by register access helpers elsewhere in AMDGPU. Typical consumers combine these masks/shifts with:

- address macros from `nbio_6_1_offset.h` or SMN aliases from `nbio_6_1_smn.h`;
- reset/default values from `nbio_6_1_default.h`;
- AMDGPU register helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, `REG_GET_FIELD`, and `WREG32_FIELD15`.

Direct include users in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and the Vega powerplay include aggregators `vega10_inc.h` and `vega12_inc.h`. The nearby in-tree runtime code mostly uses other NBIO 6.1 fields for doorbells, HDP flush, mailbox, interrupt, clock-gating, and PCIe configuration, but the include relationship means this generated PHY block is compiled into the same register namespace.

## Control Flow

There is no control flow in this chunk. Runtime control flow exists in the code that includes the header:

1. Driver code selects a register address from the companion offset/SMN header.
2. It reads the current register value or prepares a new value.
3. It applies a field mask and shift directly or via `REG_SET_FIELD`/`REG_GET_FIELD`.
4. It writes the composed value back, or compares/polls masked status bits.

For these PHY fields, common runtime patterns would include polling `*_DONE`, `*_ACK`, `*_RDY`, or `*_STATUS` bits; clearing IRQs through one-bit `_CLR` fields; enabling overrides only when explicitly requested; and preserving reserved bits on read-modify-write paths.

## State and Persistence

The macros are stateless compile-time constants. Hardware state lives in the NBIO/PCIe PHY registers. Persistence behavior is therefore hardware-defined:

- Many fields represent latched or live PHY state such as adaptation values, calibration done flags, PLL status, IRQ bits, and analog status.
- Control/override fields may persist in the register block until reset, power transition, firmware action, or a later driver write changes them.
- Clear fields such as `RX_RESET_IRQ_CLR` are likely write-to-clear style controls, so consumers must not treat them as persistent configuration bits.
- Reserved masks identify bits that should generally be preserved or left at reset/default values when composing writes.

The companion `nbio_6_1_default.h` publishes reset/default values for the same register names. In this range, defaults show many control/status fields reset to zero, DFE tap 2-5 defaults commonly at `0x800`, slicer controls at `0x7`, lane reset-return request defaults at `1`, PMA lane override defaults at `3`, TX FSM defaults around `0xde`, RX LOS/data-enable defaults, SUPX ID code values, refclk/PLL override defaults, and MPLL timing/spread-spectrum defaults. Those defaults are useful test or initialization signals but should not replace hardware-state reads for live calibration/status checks.

## Dependencies and Integration Points

Primary dependencies:

- `nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide register addresses corresponding to these field names.
- `nbio_6_1_default.h` provides default register values that must stay aligned with the same generated register database.
- AMDGPU SOC15/NBIO register access helpers provide the actual MMIO/SMN read-write mechanics.
- `nbio_v6_1.c` includes this header with the offset/default/SMN headers and uses the NBIO 6.1 register namespace for NBIO setup, HDP flush mapping, interrupt control, doorbell aperture programming, ASPM/LTR, and clock/power behavior.
- `mxgpu_ai.c` includes the same NBIO 6.1 mask header for SR-IOV mailbox register packing/extraction.
- `vega10_inc.h` and `vega12_inc.h` aggregate these register headers for power-management code paths.

The chunk also depends on generated-file ordering. Since this range covers pieces of raw lane 1, complete lane 2, complete lane 3, and the beginning of SUPX, it must remain synchronized with adjacent chunks and companion generated headers during reconciliation.

## Risks

- Generated-header skew is the dominant risk. If a mask/shift name drifts from the offset/default/SMN header for the same register database, code can compile while targeting the wrong field or interpreting hardware state incorrectly.
- Boundary-split registers can be misdocumented if chunks are merged mechanically. `RAWLANE1_DIG_AON_RX_ADPT_VGA` is missing its shifts in this chunk, and `SUPX_DIG_MPLLB_MPLL_PWR_CTL_PCLK_EN_AND_VCO_CLK_STABILIZATION_TIME_THRESHOLD` is missing its masks.
- Reserved fields are explicitly named and masked. Runtime code that writes whole register values without preserving reserved bits can alter undocumented PHY behavior.
- Full-width `VAL` fields and opaque override words are easy to misuse because the macro names do not encode higher-level semantics. Values should come from hardware documentation, generated defaults, or known-good initialization sequences.
- IRQ clear/status registers are one-bit fields with similar names. Confusing `_IRQ`, `_IRQ_CLR`, and `_IRQ_MSK` forms can either leave interrupts uncleared or mask events unexpectedly.
- PLL and refclk override fields can affect link bring-up and stability. Incorrect MPLL multipliers, SSC controls, PCLK/VCO timing thresholds, or reset/enable overrides could cause PCIe link training failures or intermittent clocking issues.
- Lane-isomorphic blocks invite copy/paste mistakes. A lane 2 register mask used with a lane 3 address may compile because the field names are structurally similar, but it would be semantically wrong if register names are passed to helper macros inconsistently.

## Test Signals

Useful validation signals for this chunk are mostly static and hardware/driver integration oriented:

- Regenerate `nbio_6_1_sh_mask.h`, `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h` from the same AMD register database and diff this range for exact macro names, shifts, masks, and ordering.
- Check that every non-boundary register in this chunk has matching `__SHIFT` and `_MASK` definitions for each field, and that masks correspond to the declared shift/width.
- Compare repeated `RAWLANE2` and `RAWLANE3` field layouts for intended lane-isomorphism, especially PCS crossing, FSM fast flags, AON adaptation, IRQ, PMA, TX, and RX control groups.
- Validate boundary handoff with adjacent chunks: previous chunk should contain the `RAWLANE1_DIG_AON_RX_ADPT_VGA` shifts, and next chunk should contain the `SUPX_DIG_MPLLB_MPLL_PWR_CTL_PCLK_EN_AND_VCO_CLK_STABILIZATION_TIME_THRESHOLD` masks.
- Build-test AMDGPU users that include `nbio_6_1_sh_mask.h`, especially `nbio_v6_1.c`, `mxgpu_ai.c`, and Vega powerplay include paths, to catch macro rename/removal regressions.
- On hardware or emulation, smoke-test NBIO/PCIe link bring-up, SR-IOV mailbox paths, interrupt delivery/clear behavior, clock-gating state, and suspend/resume or reset sequences. For this specific PHY range, additional diagnostics would include reading adaptation done flags, DFE/CTLE/VGA adaptation fields, lane common-calibration status, IRQ status/mask/clear behavior, and MPLL ready/calibration/status bits.
