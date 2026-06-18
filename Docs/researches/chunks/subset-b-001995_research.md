# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h - subset-b-001995

## Scope

- Chunk id: `subset-b-001995`
- Source lines: 161218-163593
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`
- Observed content: 2,376 lines, 2,182 `#define` entries, 1,092 `__SHIFT` macros, 1,090 `_MASK` macros, and 194 register block comments.

This chunk is a generated AMD DCN 3.2 register field mask/shift segment for C20 PHY CR3 lane 0 RX tail blocks and CR3 lane 1 TX/RX bring-up blocks. It contains no executable C code, no functions, and no C types. Its value is the compile-time register-field contract used by AMDGPU/DCN code when it inserts or extracts bit fields from memory-mapped display PHY registers.

## Purpose

The chunk publishes bit positions and masks for register fields under the `C20_PHY_CR3_*` namespace. The visible register range has two major parts:

- The end of `C20_PHY_CR3_LANE0_DIG_*`, focused on RX statistic, IQC, analog RX crossover, AFE, signal detect, VCO override, DAC, slicer, loopback, RX status, and analog control-register fields.
- The beginning and most of `C20_PHY_CR3_LANE1_DIG_*`, covering lane-level ASIC override inputs, TX override/mirror outputs, TX power sequencing, TX DCC/statistics/clock alignment/LBERT/FIFO fields, TX analog crossover controls, RX ASIC overrides and mirrors, RX pstate/power sequencing, RX VCO calibration, RX LBERT, and early RX CDR controls.

Each register block follows the generated pattern:

- A `//REGISTER_NAME` marker.
- One or more `REGISTER__FIELD__SHIFT` constants giving the field's least significant bit.
- Matching `REGISTER__FIELD_MASK` constants giving the bit mask to apply within the register.

Consumers combine these macros with register offsets from the matching offset header and with DCN register helper macros to perform read-modify-write, field extraction, diagnostics, and hardware bring-up programming.

## Important APIs, Types, and Macros

There are no C APIs or types in this chunk. The public interface is the macro namespace itself.

Important macro groups include:

- RX statistics and IQC for CR3 lane 0:
  - `C20_PHY_CR3_LANE0_DIG_RX_STAT_STAT_CNT_N_SHD`
  - `C20_PHY_CR3_LANE0_DIG_RX_STAT_SMPL_CNT2`
  - `C20_PHY_CR3_LANE0_DIG_RX_STAT_LD_VAL_EXT_1`
  - `C20_PHY_CR3_LANE0_DIG_RX_STAT_LD_VAL_EXT_2`
  - `C20_PHY_CR3_LANE0_DIG_RX_IQC_CTL_RESET_ADJUST`
  - `C20_PHY_CR3_LANE0_DIG_RX_IQC_CTL_CONFIG`
  - `C20_PHY_CR3_LANE0_DIG_RX_IQC_CTL_STAT`
  - These expose sampled statistic counts, sample completion bits, extended load values, IQC bypass/data adjustments, step size, jump divisors, bypass/data enables, DFE bypass selection, and IQC FSM state.
- CR3 lane 0 RX analog crossover and power overrides:
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_CTL_OVRD_OUT`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_PWR_OVRD_OUT_0`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_PWR_OVRD_OUT_1`
  - These define digital-to-analog override outputs for RX data rate, clocks, DFE enable/taps, bypass slicer, async reset, AFE enable, fast VREG start, clock VREG/DCC/clock enable, CDR, deserializer, bleeder, misc bits, clock bypass, and word clock enable. Many fields are paired with `*_OVRD_EN` bits.
- CR3 lane 0 RX signal-detect, VCO, calibration, DAC, and AFE controls:
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_SIGDET_CAL_EN`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_SIGDET_HF_CAL`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_SIGDET_LF_CAL`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_VCO_OVRD_OUT_0` through `_2`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_CAL_0`, `_1`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_VDAC_RANGE_SEL`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_DAC_CTRL*`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_AFE_OVRD_IN_0` through `_2`
  - These fields control or report RX signal-detect calibration, CDR/VCO enable/startup/counter/frequency tune overrides, calibration DAC values, VDAC range, DAC bypass and selections, and AFE/analog RX override inputs.
- CR3 lane 0 RX sampler, loopback, term-code, status, and analog CREG blocks:
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_SCOPE`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_SLICER_CTRL`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_ANA_IQ`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_ANA_IQC_*`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_ANA_LOOPBACK_CTRL`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_TERM_CODE_*`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_STAT_OUT_0`, `_1`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_STAT_IN_0`
  - `C20_PHY_CR3_LANE0_DIG_ANA_XF_RX_ANA_CREG00` through `_CREG11`
  - These map RX scope selection, slicer selection, IQ/phase controls, IQC bypass/data override clocks, analog calibration DAC enable, loopback data and clock options, termination code overrides, analog status outputs, analog status inputs, and vendor-specific RX analog control registers.
- CR3 lane 1 ASIC lane/TX override and mirror fields:
  - `C20_PHY_CR3_LANE1_DIG_ASIC_LANE_OVRD_IN`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_TX_OVRD_IN_0` through `_IN_5`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_TX_OVRD_OUT`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_LANE_ASIC_IN`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_TX_ASIC_IN_0` through `_IN_3`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_TX_ASIC_OUT`
  - These fields describe lane loopback/transceiver mode, TX clock-ready/reset/invert/data-enable/request/low-power/pstate/rate/width/MPLLB/RX-detect/flyover/DCC/VREG/equalization overrides, and the corresponding ASIC-facing input/output mirrors.
- CR3 lane 1 TX power, DCC, statistics, clock alignment, LBERT, FIFO, and analog crossover:
  - `C20_PHY_CR3_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0`, `_P0S`, `_P1`, `_P2`
  - `C20_PHY_CR3_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_5`
  - `C20_PHY_CR3_LANE1_DIG_TX_PWRCTL_TX_CTL`, `_STATUS`
  - `C20_PHY_CR3_LANE1_DIG_TX_DCC_CTL_*`
  - `C20_PHY_CR3_LANE1_DIG_TX_STAT_*`
  - `C20_PHY_CR3_LANE1_DIG_TX_CLK_ALIGN_*`
  - `C20_PHY_CR3_LANE1_DIG_TX_LBERT_*`
  - `C20_PHY_CR3_LANE1_DIG_TX_FIFO_CTL`
  - `C20_PHY_CR3_LANE1_DIG_ANA_XF_TX_*`
  - These describe TX pstate enable sequencing, power-up timing, TX control/status, DCC offset and status, statistic load/sample/stop controls, clock alignment state, built-in test pattern generation, FIFO bypass/read-pointer controls, TX analog override outputs, termination code overrides, DCC calibration controls, TX EQ status/override, analog status, and TX analog CREG fields.
- CR3 lane 1 RX ASIC override, power, calibration, LBERT, and CDR fields:
  - `C20_PHY_CR3_LANE1_DIG_ASIC_RX_OVRD_IN_0` through `_IN_4`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_RX_OVRD_SIGDET_IN`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_RX_OVRD_VCO_IN`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_RX_OVRD_EQ_IN_0` through `_IN_11`
  - `C20_PHY_CR3_LANE1_DIG_ASIC_RX_ASIC_IN_*`, `RX_ASIC_OUT_0`, `RX_CDR_VCO_ASIC_IN`, and `RX_EQ_ASIC_IN_*`
  - `C20_PHY_CR3_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, `_P0S`, `_P1`, `_P2`
  - `C20_PHY_CR3_LANE1_DIG_RX_PWRCTL_RX_PWRUP_TIME_0`, `_1`, `_CTL`, `_STATUS`
  - `C20_PHY_CR3_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_*`
  - `C20_PHY_CR3_LANE1_DIG_RX_LBERT_*`
  - `C20_PHY_CR3_LANE1_DIG_RX_CDR_CDR_CTL_0` through `_4`
  - These fields drive RX reset/invert/data/pstate/rate/width/flyover/DCC/sigdet/VCO/EQ override programming, ASIC mirrors, RX analog/digital pstate sequencing, RX power timing and status, VCO calibration controls and status, RX LBERT mode/error counters, and CDR/SSC gain programming.

## Control Flow

The header has no runtime control flow. Runtime sequencing is imposed by the code that includes it and by the hardware state machines behind the registers:

1. DCN 3.2 display, DMUB, clock-manager, IRQ, GPIO, resource, or amdgpu code includes `dcn_3_2_0_sh_mask.h` with the corresponding offset header.
2. The caller selects a register offset and one or more field macros from this header.
3. Register helper macros/functions mask and shift a value into the correct bit positions, usually through a read-modify-write of an MMIO register.
4. The PHY hardware observes the programmed bits and advances power, calibration, clock recovery, statistic, or diagnostic state machines.
5. Status paths read fields such as `*_FSM_STATE`, `*_DONE`, `*_IRQ`, `*_ERR`, `*_STAT*`, `*_ACK`, and analog status outputs back through the same mask/shift contract.

The names imply several external flows: TX/RX pstate fields are configured before power transitions; calibration control registers pair with calibration status registers; statistic counters have load/sample/done behavior; CDR and VCO controls pair with frequency and lock-like status; and override value fields require matching enable bits before hardware will honor them.

## State and Persistence Behavior

The macros are compile-time constants and do not persist state themselves. They describe hardware register state with different lifetimes:

- Persistent until reset or reprogrammed: pstate definitions, TX/RX power-up timing, analog CREG values, term-code overrides, VCO/CDR/IQC/DCC calibration controls, LBERT mode/pattern configuration, FIFO mode, and analog override enables.
- Transient or sampled status: statistic counts, sample-done bits, DCC/IQC/VCO FSM states, CDR gain/status values, LBERT error counters, TX/RX ACK bits, adaptation/status mirrors, RX/TX analog status outputs, and power-state machine status.
- Override state: many registers have a value bit or field next to an `*_OVRD_EN` bit. The enable bit controls whether the programmed value replaces automatic ASIC/PHY behavior. Leaving these enables asserted can pin clocks, resets, VCO/CDR controls, EQ taps, DFE controls, pstate inputs, or analog calibration paths away from normal link training behavior.
- Reserved fields: this chunk contains 268 reserved-field macro definitions. They document occupied bit ranges but should generally not be treated as writable fields by normal driver logic.

## Dependencies

This chunk depends on AMDGPU/DCN register-generation conventions:

- The matching register address definitions in `drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- Register access helper macros that expect `REG__FIELD__SHIFT` and `REG__FIELD_MASK` names.
- The generated DCN 3.2 ASIC register layout for C20 PHY CR3 lanes.
- Hardware-side semantics for PHY pstate, clocking, calibration, adaptation, LBERT, CDR, VCO, IQC, DCC, and analog crossover registers.

Repository include sites for `dcn_3_2_0_sh_mask.h` include:

- `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`

## Integration Points

This chunk integrates with:

- DCN register-field helpers that build field insert/extract operations from generated mask/shift names.
- Display link bring-up and training paths that need TX/RX reset, pstate, rate, width, data enable, DCC, VCO, CDR, and EQ controls.
- Power-management paths that program pstate tables, power-up timing, and analog/digital enable sequencing for lane 1 TX/RX blocks.
- Debug and validation paths that force ASIC overrides, loopback, LBERT patterns, statistic counters, clock alignment, VCO calibration, CDR gains, IQC, DAC selections, termination codes, and analog CREG values.
- Hardware diagnostics that read status outputs, FSM states, sample counters, error counters, calibration-done bits, power-state status, and analog status mirrors.

## Risks and Edge Cases

- Generated-header drift: a wrong mask or shift silently targets the wrong hardware bit. In this chunk that can affect reset, data enable, pstate, CDR/VCO, DCC/IQC, analog power, and EQ/DFE control.
- Value/enable pairing: override fields must be programmed together with their enable bits. A value without enable may be ignored, while a stale enable may block automatic PHY control.
- Reserved-bit writes: reserved fields are numerous and should not be used as ordinary writable fields. Full-register writes should preserve reserved bits unless the hardware programming guide says otherwise.
- Lane specificity: all symbols are CR3-specific and either lane 0 or lane 1-specific. Multi-lane code must select the matching offset/macro set rather than reusing a similar field name from another lane or CR block.
- Direction ambiguity: similarly named `OVRD_IN`, `OVRD_OUT`, `ASIC_IN`, `ASIC_OUT`, `STAT_IN`, and `STAT_OUT` blocks represent different hardware directions. Confusing them can produce valid C that manipulates the wrong side of the PHY interface.
- Calibration instability: VCO, CDR, IQC, DCC, DAC, AFE, slicer, signal-detect, and EQ/DFE fields can destabilize link training and display output if written during active links or without proper sequencing.
- Counter latching: statistic and LBERT counters include load, sample, done, count, and overflow-like fields. Diagnostic reads need to respect the counter lifecycle to avoid stale or partial readings.
- Chunk-boundary partials: this slice starts with the last mask from `C20_PHY_CR3_LANE0_DIG_RX_STAT_MATCH_CTL6` and ends immediately before the following `C20_PHY_CR3_LANE1_DIG_RX_DPLL_FREQ` block. Adjacent chunk reports are required for a complete per-file view.

## Test Signals

Useful validation signals for code consuming this chunk:

- Build coverage for all DCN 3.2 include sites so renamed or missing generated macros fail at compile time.
- Generated consistency checks that each non-reserved field has an aligned mask/shift pair and that masks do not exceed the expected register width.
- Register helper tests using representative fields from this chunk, such as RX IQC config/status, RX analog power override, lane 1 TX pstate, lane 1 TX DCC, TX LBERT pattern, RX EQ override, RX pstate, RX VCO calibration, and RX CDR gain fields.
- Hardware link-training and modeset tests that exercise normal automatic PHY control with override enables cleared.
- Suspend/resume and hotplug tests to catch stale override enables, incorrect pstate masks, or bad power-up timing definitions.
- PHY diagnostics that read statistic counters, LBERT error counters, VCO calibration status, CDR status, DCC/IQC FSM state, and analog status outputs after controlled test operations.
- Negative/debug validation on lab hardware for override paths, ensuring forced loopback, signal-detect, VCO/CDR, DCC/IQC, and EQ/DFE settings are cleared before returning to normal display operation.

## Chunk Boundary Notes

Line 161218 is already inside the `C20_PHY_CR3_LANE0_DIG_RX_STAT_MATCH_CTL6` block; only that block's final reserved mask is visible here. The last visible block, `C20_PHY_CR3_LANE1_DIG_RX_CDR_STAT`, is complete by line 163593, and the next block `C20_PHY_CR3_LANE1_DIG_RX_DPLL_FREQ` begins after this chunk. The merge/reconciliation lane should combine this report with adjacent chunks before producing the final source-file research document.
