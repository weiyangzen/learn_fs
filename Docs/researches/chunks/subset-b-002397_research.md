# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 26725-29133

## Purpose

This chunk is part of the generated AMD DPCS 4.2.3 shift/mask register header. It does not define executable logic; it defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for fields inside DPCS CR1 lane registers. The covered slice starts inside `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_3` and ends inside `DPCSSYS_CR1_LANE2_DIG_RX_DPLL_FREQ`.

The constants are consumed with companion register-address definitions from `dpcs_4_2_3_offset.h` and AMDGPU register access helpers. Together, the offset and mask headers let driver code construct read-modify-write values for DisplayPort/USB-C PHY lane control without embedding numeric bit layouts in C code.

## Register Families Covered

- `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_*`: remaining lane 1 TX power sequencing and DCC DAC control masks. This includes VCM hold time, VBOOST disable timing, RX detect timing, reset/serial-enable timing, DCC CR bank address/data, DCC DAC selection/request/update/ack, DAC address, and TX clock alignment/LBERT controls.
- `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX P-state and power-up timing masks for P0, P0S, P1, and P2. Fields control analog AFE, clock regulator, clock enable, DESER/CDR enable, VCO resets, continuous calibration, and digital clock enable behavior.
- `DPCSSYS_CR1_LANE1_DIG_RX_VCOCAL_*`: lane 1 RX VCO calibration control, timing, and status fields. These expose fixed-count calibration knobs, reset/continuous-calibration controls, skip bits, startup/update/counter timing, final counter values, FSM state, calibration-done, VCO-correct, and VCO-up status.
- `DPCSSYS_CR1_LANE1_DIG_RX_CDR_*` and `DPCSSYS_CR1_LANE1_DIG_RX_DPLL_*`: lane 1 CDR/DPLL fields for phase detector enable/edge/polarity, spread-spectrum clocking on/off counters and gain values, override gain controls, CDR status, DPLL frequency, and upper/lower frequency bounds.
- `DPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration/status masks. This includes adaptation state-machine timing, CTLE/VGA/ATT/DFE/eye/TGG enables, reset configuration, ATT/VGA/CTLE/DFE status, VDAC offsets, slicer controls, error slicer level, DAC control selects, and adaptation CR bank access.
- `DPCSSYS_CR1_LANE1_DIG_RX_STAT_*`: lane 1 statistic/matcher/counter controls for loading values, data masks, match controls, statistic controls, sample counts, statistic counters, calibration comparison clock control, and statistic stop.
- `DPCSSYS_CR1_LANE1_DIG_MPHY_*`, `DPCSSYS_CR1_LANE1_DIG_ANA_*`, and `DPCSSYS_CR1_LANE1_ANA_*`: lane 1 MPHY, digital-to-analog override, analog calibration/status, TX analog, and RX analog masks. These expose override outputs for TX/RX power, EQ, term code, DAC, signal detect, RX VCO/calibration, slicer, IQ phase, analog status, and low-level analog TX/RX measurement/control registers.
- `DPCSSYS_CR1_LANE2_DIG_ASIC_*`: beginning of lane 2 ASIC-facing override/input/output masks for lane, TX, RX, RX equalization, RX CDR/VCO, and OCLA plumbing.
- `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX P-state, power sequencing, DCC DAC, clock alignment, and TX LBERT masks. These mirror the lane 1 TX power-control structures for the second lane.
- `DPCSSYS_CR1_LANE2_DIG_RX_PWRCTL_*`, `DPCSSYS_CR1_LANE2_DIG_RX_VCOCAL_*`, `DPCSSYS_CR1_LANE2_DIG_RX_CDR_*`: lane 2 RX P-state/power timing, VCO calibration, RX alignment/LBERT, and CDR masks through the start of `DPCSSYS_CR1_LANE2_DIG_RX_DPLL_FREQ`.

## Important APIs, Types, And Constants

The only API surface here is macro constants. Each register field is represented by two related defines:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit index for the field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the field in the register's native width.

Most lane-local PHY registers in this slice are 16-bit CR-space fields with masks such as `0xFFFFL`, `0x8000L`, or narrower subfields. The generated suffix still uses `L`, so call sites should treat values as integer constants and combine them through existing AMDGPU helpers rather than relying on implicit C type width. The chunk contains 2,170 `#define` lines and 239 register-comment headings in the assigned range.

Representative fields include:

- TX sequencing: `TX_VCM_HOLD_TIME_*`, `TX_VBOOST_DIS_TIME_*`, `TX_RXDET_TIME`, `FAST_TX_RXDET`, `TX_RESET_TIME`, and `TX_SERIAL_EN_TIME`.
- TX state enables: `TX_P*_ANA_REFGEN_EN`, `TX_P*_ANA_CLK_EN`, `TX_P*_ANA_SERIAL_EN`, `TX_P*_DATA_EN`, `TX_P*_ALLOW_RXDET`, `TX_P*_ALLOW_VBOOST`, and `TX_P*_ANA_DCC_COMP_CAL_EN`.
- RX state enables: `RX_P*_ANA_AFE_EN`, `RX_P*_ANA_CLK_VREG_EN`, `RX_P*_ANA_CLK_EN`, `RX_P*_ANA_DESER_EN`, `RX_P*_ANA_CDR_EN`, `RX_P*_VCO_FREQ_RST`, `RX_P*_VCO_CAL_RST`, `RX_P*_VCO_CONTCAL_EN`, and `RX_P*_DIG_CLK_EN`.
- Calibration/status: `RX_VCO_CAL_DONE`, `RX_VCO_FSM_STATE`, `VCO_CNTR_FINAL`, `VCOCLK_TOO_FAST`, `RX_VCO_CORRECT`, `RX_VCO_UP`, `PHUG_VALUE`, and `FRUG_VALUE`.
- Adaptation/equalization: `CTLE_EN`, `VGA_EN`, `ATT_EN`, `DFE_EN`, `EYEHE_EN`, `EYEHO_EN`, `TGG_EN`, `DFE_TAP*_STATUS`, VDAC offset fields, slicer control fields, and adaptation reset/status fields.

No structs, enums, functions, inline helpers, or storage objects are declared in this slice.

## Control Flow And State

There is no runtime control flow in the header. Control flow is implicit in the hardware sequences that driver code can program with these masks:

1. Select a DPCS CR1 lane register address from the companion offset header.
2. Read or construct a register value.
3. Shift field values by the matching `__SHIFT` and mask with `_MASK`.
4. Write the resulting value through the AMD display register access path.
5. Poll status fields such as DAC `ACK`, VCO calibration done/up/correct bits, CDR values, adaptation status, statistic counters, or DPLL frequency state when hardware sequencing requires confirmation.

The state affected by these definitions is persistent only in hardware registers. This file stores no software state and has no initialization, locking, allocation, or teardown behavior. Persistence across suspend/resume, hotplug, link training, USB-C alt-mode transitions, or GPU reset depends on higher-level display/PHY code that programs these registers.

## Dependencies And Integration Points

- Paired offsets are in `drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h`; for example `ixDPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_4` maps to CR address `0x1128`, and lane 2 RX adaptation registers continue around `0x1260` in that file.
- The header guard `_dpcs_4_2_3_SH_MASK_HEADER` and generated naming convention align it with other AMD ASIC register headers. Consumers normally include this through ASIC-specific DC/DPCS register include stacks rather than including a chunk directly.
- The covered fields integrate with AMDGPU Display Core PHY, link encoder, link training, DP/USB-C alternate-mode, and diagnostic paths that need per-lane TX/RX power, equalization, DPLL/CDR, VCO calibration, and test-pattern/statistics access.
- Lane 1 and lane 2 masks mirror each other for many PHY blocks. Callers that compute per-lane behavior must pair the correct lane-specific offset with the same lane's masks; cross-lane reuse of masks is only safe when bit layouts are known to match.

## Risks And Review Notes

- This file is generated hardware ABI data. Manual edits risk silently corrupting register programming. A one-bit shift or mask error can break link training, PHY power sequencing, RX CDR lock, calibration, or low-power state transitions.
- The assigned chunk starts mid-register at line 26725 and ends mid-register at line 29133. Merge/reconciliation should preserve boundary context from adjacent chunks so partial register descriptions are not interpreted as complete standalone register families.
- Many fields are marked `RESERVED_*`. Driver writes should preserve reserved bits by read-modify-write unless hardware documentation explicitly says otherwise.
- Some masks have repeated field names with lane-specific prefixes. Search/replace across `LANE1` and `LANE2` is risky because offsets and register boundaries differ even where field layouts match.
- Status and control fields coexist in adjacent groups. Polling code must distinguish read-only status fields such as `*_STAT_*` from writable control/reset/mask fields.
- Calibration and adaptation knobs are analog-sensitive. Incorrect defaults can produce failures that look like intermittent display link instability rather than deterministic software bugs.

## Test Signals

- Build coverage: compile the AMDGPU driver or any translation unit that includes the DPCS 4.2.3 headers with warnings enabled to catch malformed macros or missing include guards.
- Header consistency: compare each register comment in this slice with a matching `ix...` offset in `dpcs_4_2_3_offset.h`; lane 1 values around `0x1128` and lane 2 values around `0x1220`/`0x1240`/`0x1260` are expected for this chunk.
- Macro shape checks: ensure every field has both `__SHIFT` and `_MASK` defines where the generated pattern requires it, and that masks remain within the register width used by the corresponding CR-space register.
- Runtime display signals: DP link training success, stable hotplug detection, lane count/rate negotiation, USB-C DP alt-mode entry/exit, suspend/resume display restore, and absence of RX/TX FIFO or PHY calibration errors are the practical integration signals.
- Diagnostic signals: lane LBERT error counters, VCO calibration done/up/correct status, CDR `PHUG`/`FRUG` values, DPLL frequency/bounds status, adaptation status registers, and RX statistic counters are useful when validating changes to consumers of these masks.
