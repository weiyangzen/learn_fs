# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 72910-75405

## Chunk Scope

This chunk is a generated AMD DPCS 4.2.3 register field header slice. It contains C preprocessor constants for bit shifts and bit masks, not executable code. The source header is guarded by `_dpcs_4_2_3_SH_MASK_HEADER` and is intended to be included by AMDGPU display code that programs or decodes DPCS/PCS PHY control-register fields.

The range covers 2,101 `#define` entries and 395 register-comment groups. It starts mid-register for `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_RX_FSM_CTL`, continues through CR3 raw lane 3 RX/PCS override fields, then defines complete always-on lane register field sets for `RAWAONLANE0`, `RAWAONLANE1`, `RAWAONLANE2`, and `RAWAONLANE3`. It then begins the generic `DPCSSYS_CR3_RAWAONLANEX` pattern and ends partway through `DPCSSYS_CR3_RAWAONLANEX_DIG_RX_OVRD_OUT_2` at the `RX_SQ_OUT_OVRD_VAL_MASK` definition.

## Purpose

The constants in this chunk let driver code construct, mask, shift, and inspect 16-bit DPCS CR3 PHY register values without embedding numeric bit positions in C logic. The covered registers describe:

- CR3 raw lane 3 receiver control and PCS test/override paths.
- Per-lane always-on analog front-end, DFE, receiver adaptation, PLL, calibration, signal detect, and TX/RX disable controls for lanes 0 through 3.
- A generic `RAWAONLANEX` definition set used for lane-parametric code or generated tables where the lane index is abstracted outside the field macro name.

## Important APIs, Types, and Constants

This chunk exports macros only. The naming convention is the API:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask in the register value.
- Register group comments such as `//DPCSSYS_CR3_RAWAONLANE0_DIG_RX_ADPT_CTLE` delimit field groups but do not compile into code.

The CR3 raw lane 3 PCS/control definitions include:

- `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_RX_LOS_MASK_CTL`: `RX_LOS_MASK_CNT` controls receiver loss-of-signal mask timing.
- `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_RX_DATA_EN_OVRD_CTL`: `RX_DATA_EN_OVRD_CNT` and `INT_REF_TRCK_CNT` timing fields.
- `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_OFFCAN_CONT_STATUS` and `...ADAPT_CONT_STATUS`: single-bit `ENABLE` status/control masks.
- `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_UPCS_OCLA`: `DATA_EN` and `CLK_EN` observability/control bits.
- `DPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_ATE_RX_OVRD_IN`: override value/enable pairs for RX `RATE`, `WIDTH`, `PSTATE`, low-power detect, and RX-to-TX parallel loopback.
- `DPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_ATE_TX_OVRD_IN` and `_1`: TX-side P-state, LPD, width, rate, MPLL selection/enable, master MPLL state override, async enable/data, beacon, VBOOST, IBOOST, DETRX request, and TX-to-RX serial loopback fields.
- `DPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_MASTER_MPLL_LOOP`: `MPLLA`/`MPLLB` loop enable bits.
- `DPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_ATE_RX_OVRD_IN_1` through `_3`: RX LOS LFPS, LOS threshold, adaptation/offcan continuous request controls, VCO load/low-frequency override, and reference load override.
- `DPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_RX_OVRD_OUT_2` and `...TX_OVRD_IN_2`: RX valid override and TX data/async/loopback override fields.

The per-lane `DPCSSYS_CR3_RAWAONLANE{0,1,2,3}` blocks are structurally identical and expose 82 register groups per lane. Important groups include:

- Analog/DFE calibration storage: `DIG_AFE_ATT_IDAC_OFST`, `DIG_AFE_CTLE_IDAC_OFST`, `DIG_DFE_*_VDAC_OFST`, `DIG_DFE_*_REF_LVL`, `DIG_RX_PHSADJ_LIN`, `DIG_RX_PHSADJ_MAP`, and `DIG_RX_IQ_PHASE_ADJUST`, mostly exposing `DATA` fields plus reserved high bits.
- Receiver adaptation results: `DIG_RX_ADPT_IQ`, `DIG_RX_ADAPT_FOM`, `DIG_RX_ADPT_ATT`, `DIG_RX_ADPT_VGA`, `DIG_RX_ADPT_CTLE`, and `DIG_RX_ADPT_DFE_TAP1` through `TAP5`.
- Adaptation completion and acceleration control: `DIG_RX_ADAPT_DONE`, `DIG_FAST_FLAGS`, `DIG_FAST_FLAGS_2`, and `DIG_ADPT_CTL_0` through `DIG_ADPT_CTL_7`.
- PLL and common calibration: `DIG_MPLLA_COARSE_TUNE`, `DIG_MPLLB_COARSE_TUNE`, `DIG_LANE_CMNCAL_MPLL_STATUS`, `DIG_LANE_CMNCAL_RCAL_STATUS`, `DIG_MPLL_DISABLE`, and `DIG_MPLL_BG_CTL`.
- Power and transceiver mode state: `DIG_INIT_PWRUP_DONE`, `DIG_TXRX_OVRD_IN`, `DIG_LANE_XCVR_MODE_OVRD_IN`, and `DIG_LANE_XCVR_MODE_IN`.
- Signal detect and RX PMA overrides: `DIG_RX_LOS_MASK_CTL`, `DIG_RX_SIGDET_FILT_CTRL`, `DIG_STATS`, `DIG_RX_OVRD_OUT_1`, `DIG_RX_OVRD_OUT_2`, `DIG_RX_OVRD_OUT_3`, `DIG_RX_SIGDET_CAL`, `DIG_RX_SIGDET_HF_CODE`, `DIG_RX_SIGDET_LF_CODE`, `DIG_RX_VREFGEN_EN`, `DIG_SIGDET_OUT_OVRD`, `DIG_SIGDET_OUT_IN`, and `DIG_RX_SIGDET_CONFIG`.
- Calibration code and TX DCC controls: `DIG_CAL_IOFF_CODE`, `DIG_CAL_ICONST_CODE`, `DIG_CAL_VREFGEN_CODE`, `DIG_RX_DCC_CAL_{ICM,IDF,QCM,QDF}_CODE_{0,1}`, `DIG_TX_DCC_BANK_ADDR`, `DIG_TX_DCC_BANK_DATA`, `DIG_TX_DCC_CONT`, and `DIG_TX_DCC_CONFIG`.
- Firmware knobs: `DIG_FW_MM_CONFIG`, `DIG_FW_ADPT_CONFIG`, and `DIG_FW_CALIB_CONFIG`.

The generic `DPCSSYS_CR3_RAWAONLANEX` block repeats the same field layout through `DIG_RX_OVRD_OUT_2` but is truncated by this chunk. Within the visible range it covers the same AFE/DFE, RX adaptation, fast flags, PLL status/disable, TX/RX override, LOS, signal-detect filter, status, RX override out 1, and the first part of RX override out 2 definitions.

## Control Flow

There is no runtime control flow in this chunk. Runtime behavior is created by consumers that combine these constants with register read/modify/write helpers elsewhere in the AMDGPU display stack. A typical use pattern is:

1. Read a DPCS CR3 register value through the DPCS indirect-address/data mechanism or a generated register accessor.
2. Clear a field with `value &= ~FIELD_MASK`.
3. Insert a new field value with `(field_value << FIELD__SHIFT) & FIELD_MASK`.
4. Write the register back or test status bits with `value & FIELD_MASK`.

The visible field layout implies several hardware state-machine flows that consumers may drive:

- RX adaptation sequencing reads completion/result fields, optionally enables `FAST_FLAGS`/`FAST_FLAGS_2`, and may force override values through `RX_OVRD_OUT_*`.
- TX/RX power sequencing may inspect `INIT_PWRUP_DONE`, then force `TXRX_OVRD_IN`, `MPLL_DISABLE`, or `LANE_XCVR_MODE_OVRD_IN`.
- PLL and calibration paths poll `LANE_CMNCAL_MPLL_STATUS` or `LANE_CMNCAL_RCAL_STATUS` and program calibration-code registers.
- Signal-detect tuning uses `RX_SIGDET_*`, `SIGDET_OUT_*`, and RX PMA override fields.

## State and Persistence Behavior

The macros themselves hold no state. They encode hardware register layout, so the persistent state lives in the display PHY registers and any cached register images maintained by driver code outside this header.

Most fields in this chunk are 16-bit lane-local hardware fields. Important state categories are:

- Latched calibration/adaptation values: DFE offsets, CTLE/VGA/ATT/IQ adaptation results, DCC calibration codes, and signal-detect tune codes.
- Control overrides: fields with `*_OVRD_VAL` plus `*_OVRD_EN` pairs can force hardware behavior until cleared.
- Status bits: `*_DONE`, `*_INIT`, `RX_PMA_SQ_OUT`, `RX_VREFGEN_MASTER`, `PH2_PWRUP_DONE`, and related fields expose hardware progress or analog state.
- Reserved fields: many registers reserve upper bits; consumers should preserve reserved bits during read/modify/write unless hardware documentation says otherwise.

Because lanes 0 through 3 use identical field layouts, persistence is lane-scoped: writing a `RAWAONLANE1` override should not affect the corresponding `RAWAONLANE0`/`2`/`3` register unless the underlying hardware aliases are misaddressed by consumer code.

## Dependencies and Integration Points

This header depends only on the C preprocessor. It integrates with:

- AMDGPU DC/DPCS register programming code that includes ASIC register headers for DPCS 4.2.3.
- Companion offset/address headers for the same ASIC block, which provide register addresses while this file provides field masks and shifts.
- Register helper macros commonly used in AMD display code, such as field prepare/get helpers or generated `REG_SET`, `REG_UPDATE`, and `REG_GET` style wrappers, which need the `__SHIFT` and `_MASK` naming scheme.
- Hardware sequencing code for DisplayPort/USB-C PHY lane bring-up, receiver adaptation, TX/RX disable/enable, PLL calibration, and signal detect.

The `DPCSSYS_CR3_*` prefix ties this chunk to controller/register block CR3. The repeated lane-specific macro groups are integration points for per-lane initialization loops, while `RAWAONLANEX` supports consumers that generate the lane address separately but use a shared field layout.

## Risks and Edge Cases

- This chunk starts after the first two `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_RX_FSM_CTL` shift definitions; only `RATE_CHG_IN_P1_MASK` and `RESERVED_15_2_MASK` are visible here. A full-file merge must include the preceding chunk to capture `EN_RX_CTL_FSM__SHIFT`, `RATE_CHG_IN_P1__SHIFT`, and `EN_RX_CTL_FSM_MASK`.
- This chunk ends in the middle of `DPCSSYS_CR3_RAWAONLANEX_DIG_RX_OVRD_OUT_2`. Lines 75403-75405 include masks through `RX_SQ_OUT_OVRD_VAL_MASK`; the rest of that register's masks and subsequent generic lane-X signal-detect definitions are in the next chunk.
- Generated macros are sensitive to naming drift. A typo in any field name breaks consumers at compile time; a wrong shift or mask compiles cleanly but can program unsafe PHY state.
- Override fields are hazardous if used without paired enable-bit discipline. Setting an override value without its enable bit may have no effect; leaving enable bits set can pin calibration, RX/TX data, loopback, or signal-detect behavior beyond the intended sequence.
- Reserved masks occupy high bits in many 16-bit registers. Full-width writes that ignore reserved masks may alter undocumented hardware state.
- The per-lane blocks are almost identical, so copy/paste or generated offset mismatches in consumers can silently program the wrong lane while still using valid field macros.
- Several fields expose analog calibration values (`DCC`, `DFE`, `CTLE`, `VGA`, `IQ`, VREF, signal detect). Invalid values may cause link training failures, unstable receive detection, or PHY bring-up regressions rather than obvious software errors.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware-integration oriented:

- Compile coverage from AMDGPU display code that includes `dpcs_4_2_3_sh_mask.h`; missing or renamed macros should fail compilation in register programming paths.
- Static checks that every `__SHIFT`/`_MASK` pair for a register field agrees with expected bit widths and that lane 0, 1, 2, 3, and X definitions remain layout-identical where intended.
- Generated-header consistency checks against the corresponding DPCS register-offset header and the source register database used by AMD.
- Hardware or simulator tests for CR3 lane bring-up, DisplayPort link training, lane adaptation, PLL calibration, RX signal-detect behavior, TX/RX disable override, and loopback/ATE paths.
- Readback tests that write a field through a driver helper and confirm only the documented mask bits change, especially for `OVRD_VAL`/`OVRD_EN` pairs and reserved high-bit regions.

## Cross-Chunk Notes

The merge lane should reconcile this report with adjacent chunk reports because the first and last register groups are partial. The preceding chunk owns the complete beginning of `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_RX_FSM_CTL`; the following chunk owns the remainder of `DPCSSYS_CR3_RAWAONLANEX_DIG_RX_OVRD_OUT_2` and subsequent `RAWAONLANEX` groups.
