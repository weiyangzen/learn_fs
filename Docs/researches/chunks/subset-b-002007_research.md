# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 190431-192839

## Scope

This chunk is a generated AMD DCN 3.2.0 register shift/mask header slice. It contains preprocessor constants only: register grouping comments, `_SHIFT` macros for field bit positions, and `_MASK` macros for register-positioned field masks. There are no C functions, structs, enums, branches, loops, allocations, locks, syscalls, or direct file-backed persistence in this range.

The requested range covers 2,409 source lines, 2,164 `#define` lines, and 245 register-group comments. It starts in the middle of `C20_PHY_CR4_SUP_DIG_MPLLA_MPLL_PWR_CTL_STAT`: the register comment and `FSM_STATE__SHIFT` line are immediately before the requested start, while the requested first line is `MPLL_TOOSLOW__SHIFT`. It ends in the middle of `C20_PHY_CR4_LANE0_DIG_ANA_XF_TX_OVRD_OUT_3`: the requested final line is `TX_ANA_MISC_EN_OVRD_EN_MASK`, and the remaining masks for async reset and reserved bits are in the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU Display Core hardware metadata for DCN/DPCS PHY programming, not Ceph filesystem logic.

## Purpose

The purpose of this header range is to describe the bit layout for C20 PHY CR4 supervisor/common and lane0 TX registers used by AMD display driver code for DCN 3.2.0-era hardware. The companion offset header provides the register addresses; this file provides the field positions and masks used by generated register-helper infrastructure to pack MMIO writes, extract status readbacks, and preserve unrelated bits during read/modify/write operations.

The major hardware surfaces represented here are:

- CR4 supervisor digital MPLLA/MPLLB power, calibration, timing, spread-spectrum, status, and analog override/readback fields.
- CR4 raw common digital control, ATE/ALU diagnostics, firmware status/configuration, context-restore configuration, always-on SRAM, tune/calibration banks, power-gate override, firmware metadata/version, RTUNE readbacks, and APB/supervisor status fields.
- CR4 lane0 ASIC lane/TX override and normal ASIC input/output fields.
- CR4 lane0 TX power-control, DCC/statistics, clock-alignment, loopback BERT, TX FIFO, TX level calculation, and analog transfer override fields.

These constants are generated data rather than executable logic, but they are still a hardware ABI between driver code, generated register tables, firmware-facing helpers, and the display PHY. A wrong shift or mask can compile cleanly while causing software to write the wrong hardware bits or decode the wrong status, with failures showing up as PLL bring-up failures, spread-spectrum problems, lost firmware handshakes, broken context restore, unstable TX clocks, link training failures, or unusable PHY diagnostics.

## Important APIs, Types, And Macros

This range exports the standard generated AMD register-field naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group the following definitions by register.

There are no callable APIs or C types in this chunk. Runtime code consumes these macros indirectly through AMD display register-list and mask/shift-list infrastructure, typically paired with register offsets from `dcn_3_2_0_offset.h`. The header itself is protected by `_dcn_3_2_0_SH_MASK_HEADER`.

Important definition families in this chunk are:

- `C20_PHY_CR4_SUP_DIG_MPLLA_MPLL_PWR_CTL_*`, `C20_PHY_CR4_SUP_DIG_MPLLA_SSC_*`, `C20_PHY_CR4_SUP_DIG_MPLLB_UPLL_PWR_CTL_*`, and `C20_PHY_CR4_SUP_DIG_MPLLB_SSC_*`.
- `C20_PHY_CR4_SUP_DIG_ANA_XF_*`, including supervisor, MPLLA, MPLLB, PMIX, RTUNE, and CREG override/readback groups.
- `C20_PHY_CR4_RAWCMN_DIG_*`, including common control, firmware status, context restore, always-on SRAM/tune/calibration/RTUNE, APB, and metadata groups.
- `C20_PHY_CR4_LANE0_DIG_ASIC_*`, `C20_PHY_CR4_LANE0_DIG_TX_PWRCTL_*`, `C20_PHY_CR4_LANE0_DIG_TX_DCC_CTL_*`, `C20_PHY_CR4_LANE0_DIG_TX_STAT_*`, `C20_PHY_CR4_LANE0_DIG_TX_CLK_ALIGN_*`, `C20_PHY_CR4_LANE0_DIG_TX_LBERT_*`, `C20_PHY_CR4_LANE0_DIG_TX_FIFO_CTL`, and `C20_PHY_CR4_LANE0_DIG_ANA_XF_TX_OVRD_OUT_*`.

## Supervisor MPLL, SSC, And Analog Transfer Fields

The first major section covers CR4 supervisor digital control around MPLLA and MPLLB. The chunk begins with the body of `MPLLA_MPLL_PWR_CTL_STAT`, which reports the MPLLA power finite-state-machine state and flags such as too-slow, frequency-check done, calibration ready, lane side enables, PCLK/output/FBCLK enables, calibration, reset, analog enable, and analog-regulator speedup.

MPLLA power timing and tune groups then define fields for:

- VCO stabilization, calibration-update, VCO clock stabilization, PCLK enable/disable, VCO power-down, regulator speedup, analog power-up, feedback digital-clock enable, feedback-clock enable, VCO gearshift, and output delay timing.
- Coarse/fine tune value readback or override, skip-calibration coarse/fine tune values, restart tune-code override enable, and skip-calibration override enable.
- Power FSM coarse-start and coarse-limit fields across four FSM configuration registers.
- Spread-spectrum fractional output and ramp override values, plus SSC configuration fields for bypassing MPLL logic and selecting the fractional clock.

The MPLLB/UPLL section mirrors much of the MPLLA material but is not a byte-for-byte duplicate. It includes calibration override, PCLK/FBDIGCLK controls, fast power/lock controls, DTB select, power status, VCO/PCLK timing, analog DAC status, SSC fractional/ramp/configuration, and reserved upper fields. Status fields include MPLL lock, reset, analog enable, output enable, feedback clock enable, and lane sync bits.

The `C20_PHY_CR4_SUP_DIG_ANA_XF_*` groups bridge supervisor digital state to analog controls and status:

- `STAT_IN`, `STAT_OUT`, `MPLLA_STAT_OUT`, and `MPLLB_STAT_OUT` expose supervisor, MPLLA, and MPLLB analog-facing readbacks such as calibration completion, lock, VCO frequency, fractional output, ramp, range, tune codes, and reserved status bits.
- `BG_OVRD_OUT` and `REF_OVRD_OUT` provide value/enable pairs for bandgap, lane bandgap, reference regulator, reference clock detector, reference clock divider, pad selection, clock range, and alternate low-power clock selection.
- `SUP_VREF_CTL` carries supervisor reference voltage controls.
- `MPLLA_OVRD_OUT_*`, `MPLLB_OVRD_OUT_*`, and PMIX override groups expose value/enable pairs for MPLL reset, calibration, analog enable, output enable, feedback/PCLK enables, regulator speedup, lane selection, input-clock selection, tune/range controls, fractional/ramp overrides, and PMIX-specific knobs.
- `RTUNE_OVRD_OUT`, `SUP_OVRD_OUT`, `MPLLA_TUNE_OVRD_OUT_0`, supervisor CREG groups, MPLLA CREG groups, MPLLB CREG groups, and full-word override placeholders define low-level analog test/configuration fields and reserved alignment registers.

These supervisor and analog-transfer fields are sequencing-sensitive. The macros expose the bit positions, but they do not encode legal ordering, wait times, self-clearing behavior, calibration ownership, or which status bits are volatile. Those rules must come from driver/firmware logic and the hardware programming guide.

## Raw Common Digital And Always-On Fields

The `C20_PHY_CR4_RAWCMN_DIG_*` section describes the raw common PHY digital block. It includes:

- Common control and clock-gate fields: `CMN_CTL`, `CMN_CLK_GATE_CTL`, `CMN_CTL_1`, and `MPLL_CONFIG`.
- ATE/ALU diagnostic access: `ATE_ALU_CTRL`, `ATE_ALU_ADDR`, `ATE_ALU_DATA`, `ATE_ALU_FLAGS`, and `ATE_ALU_ACCUM`.
- MPLL and firmware handshake/status: `MPLL_IN`, `FW_PWRUP_DONE`, `STATIC_CONFIG_STATUS`, `FW_CONFIG_STATUS`, `CMN_STATUS_1`, `MPLL_CLK_ASYNC_OVRD`, `MPLL_RECAL_BANK_OVRD`, `MPLLA_FRAC_UPDATE`, `MPLLB_FRAC_UPDATE`, and `CONFIG_MASTER_VERSION`.
- CTLE offset configuration and control-register access: `CTLE_OFST_CFG_0` through `CTLE_OFST_CFG_3` and `CREG_ACCESS_CTL`.
- Context restore and context selection: `CNTX_RSTR_REQ_CTRL`, `CNTX_SEL_OVRD_IN_0` through `_2`, `SUP_CNTX_CFG_0` through `_3`, `MPLLA_CNTX_CFG_0` through `_9`, and `MPLLB_CNTX_CFG_0` through `_10`.

The always-on portion provides fields for SRAM power gating, MPLLA/MPLLB tune-bank control, calibration-bank selection, tune completion, power-gate/supervisor override input and output, PMA recalibration bank selection, common-calibration status, RTUNE status, per-lane RTUNE RX/TXDN/TXAVG values for lanes 0 through 7, SRAM override/input/output, firmware version/raw version, RTUNE-in-recalibration, SRAM end/beginning-of-code addresses, supervisor control/status, APB configuration, MPLL context-restore control, metadata location, and SRAM record-address override/readback.

This part of the chunk represents persistent hardware state in the sense of live MMIO register state, always-on SRAM configuration, firmware metadata, and context-restore records. The C header itself persists nothing; it only names fields that software may use to restore PHY context after power transitions or firmware-managed sequencing.

## Lane0 ASIC TX Interface And Power Control

The chunk then transitions into lane0-specific TX digital registers. `C20_PHY_CR4_LANE0_DIG_ASIC_LANE_OVRD_IN` defines lane-level override bits for TX-to-RX serial loopback, RX-to-TX parallel loopback, transceiver mode, and lane override enable. `TX_OVRD_IN_0` through `TX_OVRD_IN_5` provide value/enable pairs for the TX ASIC input path:

- Clock-ready, reset, invert, data-enable, request, low-power-disable, and power-state controls.
- TX rate, width, wide-transfer alignment enable, MPLLB selection, detect-RX request, flyover enable, and override enables.
- NYQUIST data, TX disable, beacon enable, IBOOST level, VBOOST enable, and TX override enable.
- TX post/main/pre cursor fields, EQ override, DCC bypass, EQ-calculation bypass, DCC range controls, async FIFO, lane-to-lane deskew, KR driver enable, TX clock deskew, regulator bypass, DCC update enable, and corresponding override enables.

`TX_OVRD_OUT` provides overrideable TX output/status readbacks such as acknowledgement, detect-RX result, calibration status, and override enables. The non-override `LANE_ASIC_IN`, `TX_ASIC_IN_0` through `_3`, and `TX_ASIC_OUT` groups expose the normal hardware/ASIC interface for the same lane and TX signals without the diagnostic override-enable pattern. `TX_OVRD_MISC` is a generic miscellaneous override payload with an override-enable bit.

The TX power-control section defines per-power-state register layouts and timing:

- `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` encode per-state analog TX controls such as MPLLA/MPLLB clock enables, TX clock/data/serial/reset, reference generation, VCM hold, regulator behavior, RX detect, data rate, VBOOST, and word-clock related controls.
- `TX_PWRUP_TIME_0` through `TX_PWRUP_TIME_5` provide power-up/down timing windows for the TX analog path.
- `TX_CTL` and `TX_STATUS` expose TX power-control command/readback state.

These definitions separate three related views: software-forced override inputs, normal ASIC inputs/outputs, and power-state-driven sequencer values. Driver code must avoid conflating them; leaving an override enable asserted can mask the normal ASIC state machine, while changing a PSTATE value affects later sequencer behavior rather than just the immediate live signal.

## Lane0 TX DCC, Statistics, Clock Alignment, LBERT, FIFO, And Analog Overrides

The remaining lane0 TX groups cover diagnostics and analog transfer fields:

- `TX_DCC_CTL_TX_DCC_DIFF_IDAC_OFST`, `TX_DCC_CTL_TX_DCC_CM_IDAC_OFST`, and `TX_DCC_CTL_STAT` define DCC differential/common-mode offset controls and DCC status.
- `TX_STAT_LD_VAL_1`, `TX_STAT_STAT_CTL0`, `TX_STAT_SMPL_CNT1`, `TX_STAT_STAT_CNT_0`, `TX_STAT_CAL_COMP_CLK_CTL`, and `TX_STAT_STAT_STOP` define statistic load/sample/count/control fields and calibration compare-clock controls.
- `TX_CLK_ALIGN_TX_CTL_0`, `TX_CTL_1`, and `CLK_ALIGN_STATUS` define clock-alignment startup delay, UI shift counts for multiple data-width modes, retrigger/sticky-late controls, shift count, FSM state, and TX clock state.
- `TX_LBERT_CTL` and `TX_LBERT_PAT1_0` through `_3` define loopback BERT mode, forced-error trigger, and pattern payload fields.
- `TX_LVL_CALC_STAT` exposes TX calibration code readback, and `TX_FIFO_CTL` exposes TX FIFO read-pointer start and bypass fields.
- `TX_OVRD_OUT_0` through the visible part of `TX_OVRD_OUT_3` define analog transfer override outputs for MPLLA/MPLLB/TX clocks, clock divider, clock shift, reset, serial/data enable, reference generator, VCM hold, regulator bypass/fast-start/bleeder, data rate, clock loopback, RX detect, reference selection, VBOOST, word clock, miscellaneous TX analog controls, and async reset.

This part is diagnostic-heavy. It exposes fields that can force clocks, resets, training patterns, FIFO behavior, calibration paths, and analog enables. Such fields are useful for bring-up and validation but carry high risk if used in normal display paths without restoring the hardware-owned state.

## Control Flow And Data Flow

There is no executable control flow in this chunk. The effective runtime flow is imposed by the code that includes the header:

1. DCN 3.2.0 modules include `dcn_3_2_0_offset.h` for addresses and `dcn_3_2_0_sh_mask.h` for field metadata.
2. Register helper macros combine a register offset with a field's `_SHIFT` and `_MASK`.
3. Driver or firmware-support code builds a packed register value, performs read/modify/write, or extracts field values from MMIO reads.
4. The hardware block consumes writes or returns volatile status according to PHY sequencing rules outside this generated header.

The data flow is therefore from generated constants into register-helper tables and finally into MMIO register access. No user data, filesystem data, network data, or Ceph client state flows through this header.

## State And Persistence Behavior

The header creates no runtime state and has no persistence behavior on its own. It defines constants compiled into the AMDGPU display driver.

The hardware fields named here do represent stateful PHY surfaces:

- MPLL calibration, lock, tune, spread-spectrum, power FSM, and regulator state.
- Firmware completion/configuration/version and always-on SRAM metadata.
- Context-restore requests and saved supervisor/MPLLA/MPLLB context fields.
- Per-lane TX power-state sequencer values, calibration results, DCC offsets, statistic counters, BERT patterns, FIFO controls, and clock alignment status.
- Override-enable bits that can redirect hardware from normal ASIC-controlled state to software-forced values.

Most of this state is volatile MMIO/device state and can change asynchronously due to hardware FSMs, firmware, link training, power management, or diagnostic activity. Context and always-on SRAM fields are named here because the hardware/firmware can preserve or restore PHY context across lower-power transitions, but the persistence mechanism is outside the C preprocessor header.

## Dependencies And Integration Points

Direct dependencies visible in this source slice are limited to the C preprocessor and the generated naming contract. Integration depends on adjacent generated register headers and AMD display helpers:

- `dcn_3_2_0_offset.h` supplies matching register offsets such as the C20 PHY CR4 address space.
- `dcn_3_2_0_sh_mask.h` is included by DCN 3.2 display modules including `dmub_dcn32.c`, `irq_service_dcn32.c`, `dcn32_resource.c`, `dcn32_clk_mgr.c`, and DCN 3.2 GPIO factory/translate code.
- AMD display register helpers such as `FN(reg, field)`, `FD(reg__field)`, and mask/shift list macros consume the generated `_SHIFT` and `_MASK` names.
- Hardware integration is with DCN/DPCS PHY CR4 supervisor, raw common, always-on, and lane0 TX sub-blocks.

A local reference search found these exact sample field names primarily in the generated header itself, with corresponding C20 PHY CR4 addresses in the offset header. That suggests many fields in this chunk are generated hardware coverage used by tables, diagnostics, firmware support, or future register access paths rather than hand-written direct references in display C files.

## Risks And Maintenance Notes

- Chunk boundary risk: the requested range starts after the first field in `MPLLA_MPLL_PWR_CTL_STAT` and ends before the final masks for `TX_OVRD_OUT_3`. The later merge step must combine adjacent chunks to avoid treating those registers as incomplete in the final per-file report.
- Generated ABI risk: manual edits to shifts or masks can silently corrupt register programming while still compiling.
- Reserved-field risk: many registers contain `RESERVED_*` masks. Driver writes should preserve reserved bits unless the hardware database or firmware contract explicitly says otherwise.
- Override-pair risk: many fields follow a value plus `_OVRD_EN` pattern. Setting the value without its enable may do nothing; leaving the enable asserted may force diagnostic state and bypass normal hardware control.
- Sequencing risk: power, calibration, lock, tune, context restore, clock alignment, and DCC fields have ordering and wait requirements not represented in this header.
- Volatile-status risk: fields named `STAT`, `STATUS`, `DONE`, `LOCK`, `CAL`, `FSM_STATE`, counters, and firmware completion flags may change under hardware/firmware control and should not be treated as stable cached software state.
- Lane/common confusion risk: CR4 supervisor/raw-common fields apply to the common PHY block, while `LANE0` fields apply to one lane. Similar names in other chunks for other lanes or CR instances must not be substituted casually.

## Test Signals

There are no unit-testable functions in this chunk. Useful validation signals are build-time and hardware/integration oriented:

- Compile coverage for DCN 3.2 display code including files that include `dcn_3_2_0_sh_mask.h`.
- Generated-header consistency checks that every `_SHIFT` has the expected matching `_MASK`, field masks align with shifts and bit widths, no field names collide unexpectedly, and register comments match offset-header register names.
- Static checks that register helper invocations resolve both offset and mask/shift symbols.
- Driver bring-up tests on DCN 3.2 hardware covering display link training, PLL lock, clock programming, power-state transitions, suspend/resume or context restore, and hotplug/display modes that exercise CR4 PHY lanes.
- Diagnostic or lab tests for MPLL calibration/SSC, firmware power-up completion, RTUNE/tune-bank status, TX DCC calibration, TX BERT, clock alignment, FIFO bypass, and analog override cleanup.
- Regression checks that diagnostic override paths clear `_OVRD_EN` bits and restore normal ASIC-controlled TX/PHY behavior before leaving validation code paths.
