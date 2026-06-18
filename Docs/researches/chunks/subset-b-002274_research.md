# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 36569-38994

## Purpose

This chunk is generated AMD DPCS 3.1.4 register-field metadata. It contains no executable C logic; it publishes preprocessor constants that encode bit positions and masks for fields in DPCS/DisplayPort PHY control and status registers. Driver code pairs these `__SHIFT` and `_MASK` constants with register offsets from `dpcs_3_1_4_offset.h` so AMDGPU DCN 3.1.4 link-encoder and HPO DP link code can update or read individual MMIO fields through the display register helpers.

The requested range covers 2,426 lines in the middle of a 55,194-line generated header. It starts inside `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`, covers the remainder of the lane 1 RX VCO/CDR/adaptation/statistics/analog-control block, then covers lane 2 ASIC override, TX power, RX power, RX VCO/CDR/adaptation/statistics, MPHY RX, and the beginning of lane 2 analog TX override/equalization fields. The chunk ends at the first shift for `DPCSSYS_CR2_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_1`; its companion mask entries are in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, includes, or locks in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to preserve, isolate, or modify the field in a register read-modify-write operation.

The main field families in this chunk are:

- Lane 1 RX VCO calibration: `RX_VCO_CAL_CTRL_[0-2]`, `RX_VCO_CAL_TIME_[0-1]`, and `RX_VCO_STAT_[0-2]` expose gain-calibration counters, fixed-count enables, hold/skip controls, VCO reset and continuous-calibration enables, frequency tuning start/step values, wait timers, FSM state, calibration-done status, final counter values, and too-fast/correct/up indicators.
- Lane 1 RX CDR and DPLL: `RX_CDR_CDR_CTL_[0-4]`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_[0-1]` describe phase-detector enable/edge/polarity, SSC on/off counters, phase/frequency update gains, override gain values, DPLL frequency readback, and upper/lower frequency bounds.
- Lane 1 adaptation control and readback: `RX_ADPTCTL_ADPT_CFG_[0-9]`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP[1-2]_STATUS`, DFE/slicer VDAC offset registers, slicer controls, error slicer levels, reset, DAC selector registers, and CR bank address/data.
- Lane 1 RX statistics and pattern matching: `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL[0-5]`, `STAT_CTL[0-2]`, `SMPL_CNT1`, `STAT_CNT_[0-6]`, `CAL_COMP_CLK_CTL`, and `STAT_STOP` define match patterns/masks, statistic source selection, scope controls, counter enables, done bits, sample/counter readback, comparator clock timing, and stop control.
- Lane 1 analog and MPHY override/status: MPHY PWM/termination/stable-count controls; TX override, TX termination/equalization, RX control/power/VCO/calibration/DAC/AFE/CTLE/scope/slicer/IQ controls; analog status; RX termination; MPHY; signal detect; TX DCC DAC; and low-level `LANE1_ANA_*` TX/RX analog register bitfields.
- Lane 2 digital ASIC boundary: `DIG_ASIC_*_OVRD_IN`, `*_OVRD_OUT`, `*_ASIC_IN`, and `*_ASIC_OUT` fields model lane-level, TX, RX, RX EQ, and RX CDR/VCO override paths between digital logic and PHY analog interfaces.
- Lane 2 power and training setup: TX P-state registers, TX power-up timing, DCC DAC CR bank and acknowledgement fields, TX clock alignment, TX LBERT controls, RX P-state registers, and RX power-up timing.
- Lane 2 RX calibration/statistics: lane 2 repeats the VCO calibration, CDR/DPLL, adaptation, and statistics families seen for lane 1, with the same field purposes but lane-specific register names.
- Lane 2 MPHY and TX analog override start: MPHY RX PWM/termination/stable-count fields and the start of TX analog override, termination-code override, termination-clock override, and TX equalization override fields.

Most fields in this chunk are 16-bit register fields, with masks such as `0xFFFFL`, `0x8000L`, or lower-width subfields. Some ASIC override and power-control registers are wider, especially lane 2 `DIG_ASIC_*` fields and power-state macros using 32-bit masks.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. `dcn314_resource.c` includes `dpcs_3_1_4_offset.h` and this `dpcs_3_1_4_sh_mask.h`.
2. DCN 3.1/3.1.4 link-encoder macro lists, including `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`, collect selected field shifts and masks into `dcn10_link_enc_shift` and `dcn10_link_enc_mask` tables.
3. HPO DP link encoder register construction in the same resource file pulls DPCS/RDPCSTX register lists into per-link register tables.
4. Later display link code uses AMD register helper macros such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, and poll/wait wrappers with those offsets, shifts, and masks to sequence link PHY reset, power, calibration, training, and status handling.

The macros themselves do not encode ordering. Safe sequencing still belongs to the consumers: clocks and power rails must be enabled before calibration; reset, P-state, DPLL/CDR, adaptation, and analog override writes must be ordered around hardware handshakes; and status fields must be polled or cleared according to the register specification.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU PHY state.

The represented hardware state includes:

- RX VCO and DPLL calibration state: reset bits, continuous calibration, skip controls, timers, FSM state, calibration done, frequency tune values, and counter readbacks.
- Clock/data recovery and adaptation state: phase-detector controls, SSC gain timing, phase/frequency update gains, adaptation machine configuration, attenuator/VGA/CTLE/DFE status, slicer offsets, and DAC selections.
- Statistics and diagnostics state: pattern match values/masks, statistic counter enables, sample counters, statistic counters, done bits, LBERT error count/overflow, and OCLA-related capture fields.
- Power and P-state state: lane 2 TX/RX P0/P0S/P1/P2 controls, power-up timers, analog enable/disable fields, DCC controls, and stable/acknowledge fields.
- Analog override state: TX and RX analog enables, rates, resets, serializer/deserializer controls, equalization pre/post/leg-pull settings, term-code overrides, signal-detect overrides, DCC DAC controls, calibration codes, and measurement/status fields.

Persistence is hardware-defined. Some configuration fields retain values until modeset, link retraining, power gating, suspend/resume, or ASIC reset. Status and counter fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while a lane is powered. This generated header does not express access type or side effects; the register spec and consumer code must supply that knowledge.

## Dependencies And Integration Points

This chunk depends on the matching DPCS 3.1.4 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`

The offset header maps the same symbolic registers to indirect DPCS addresses. For example, generic lane-X offsets identify the same register families represented here, including `ixDPCSSYS_CR2_LANEX_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`, `ixDPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_0`, `ixDPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0`, `ixDPCSSYS_CR2_LANEX_DIG_RX_STAT_STAT_CTL0`, and `ixDPCSSYS_CR2_LANEX_DIG_ANA_TX_OVRD_OUT`.

The direct include site found in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`

At that integration point, this header feeds:

- link encoder shift/mask tables through `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`;
- HPO DP link encoder register tables through `DCN3_1_RDPCSTX_REG_LIST(...)` and related DPCS register-list macros;
- the common AMD display register helper pattern that expects each register field to have a matching shift and mask macro.

The chunk also aligns with generated DPCS headers for nearby ASIC versions. Similar register names appear in later `dpcs_4_2_0_*` and `dcn_4_1_0_sh_mask.h` metadata, which is useful for consistency checks but is not a substitute for the 3.1.4 register database.

## Risks And Edge Cases

- Generated metadata can fail silently. A wrong shift or mask usually compiles, but it can program the wrong bits in a PHY register and produce link failures, unstable training, intermittent blank displays, or analog-margin problems.
- This chunk has artificial boundaries. It begins after the first fields of lane 1 `RX_VCO_CAL_CTRL_0` and ends before the masks for lane 2 `ANA_TX_EQ_OVRD_OUT_1`; adjacent chunks are required before making complete per-register claims.
- Lane repetition is copy-sensitive. Lane 1 and lane 2 fields are structurally similar, but a lane-specific typo can affect only one physical lane, making failures depend on lane count, connector routing, link rate, or whether the failing lane is active.
- PHY calibration fields are timing- and power-state-sensitive. Misusing VCO calibration, DPLL frequency, CDR gains, or adaptation controls can cause lock failures, high bit error rates, or training instability that may only appear at high bandwidth or after resume.
- Override fields are high risk. `*_OVRD_EN` bits bypass normal hardware sequencing. Leaving an override asserted across modeset, hotplug, retraining, or suspend/resume can pin analog enables, data rates, resets, termination, or equalization values unexpectedly.
- Status and counter fields may have side effects or validity windows. LBERT errors, statistic counters, calibration done bits, ACK fields, and analog status bits may require specific read/clear/poll ordering not represented in this header.
- Reserved masks are present throughout the chunk. Consumers must preserve reserved bits during read-modify-write operations; writing raw constants instead of using field helpers risks changing undocumented hardware behavior.
- Some fields are wider 32-bit lane-interface controls while many PHY fields are 16-bit. Mixing register width assumptions can corrupt neighboring fields or drop high-order control bits.

## Test Signals

Useful validation combines generated-header consistency with hardware-facing display tests:

- Build AMDGPU/DC with DCN 3.1.4 support enabled. Missing or renamed DPCS shift/mask macros should fail at resource and link-encoder table construction.
- Mechanically verify that every complete field in this range has the expected `__SHIFT`/`_MASK` pair, while accounting for the chunk-edge exceptions at line 36569 and line 38994.
- Compare this range against AMD's authoritative DPCS 3.1.4 register database and against neighboring generated headers where register layout is expected to match.
- Exercise DP and HDMI link bring-up on DCN 3.1.4 hardware across lane counts and link rates, especially cases using physical lanes 1 and 2.
- Run modeset, hotplug, link retraining, MST if supported by the platform, high-bandwidth modes, suspend/resume, runtime power management, and repeated connector unplug/replug cycles.
- Watch kernel logs and display diagnostics for AUX/link-training failures, CDR/VCO calibration timeouts, stuck ACK/done bits, blank screens, intermittent flicker, CRC mismatches, audio/video instability, and resume regressions.
- If debug tooling is available, sample DPLL/CDR/VCO status, adaptation status, statistic counters, LBERT counters, and analog status before and after training to confirm fields decode plausibly.

## Cross-Chunk Notes

Previous chunks own the beginning of lane 1 RX power and `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`. Later chunks continue lane 2 TX equalization override, lane 2 RX analog controls/status, and the rest of the DPCS 3.1.4 shift/mask namespace. The final per-file research document should merge those chunks before making whole-file claims about all lanes, all DPCS CR blocks, or complete DPCS PHY programming coverage.
