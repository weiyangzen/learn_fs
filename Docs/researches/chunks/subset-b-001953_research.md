# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h - subset-b-001953

## Scope

- Chunk id: `subset-b-001953`
- Source lines: 59164-61553
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`
- Observed content: 2,390 lines, 2,171 `#define` entries, 1,087 `__SHIFT` macros, 1,084 `_MASK` macros, and 219 register block comments.

This chunk is a generated AMD DCN 3.2 register field mask/shift segment for the C20 PHY CR0 lane 0 digital blocks. It does not define executable code, C types, inline functions, or storage. Its purpose is to publish the bit layout contract for register-access code that programs or reads PHY lane controls through paired `FIELD__SHIFT` and `FIELD_MASK` constants.

## Purpose

The chunk covers bit definitions for a large contiguous group of lane-0 C20 PHY digital registers. The names describe the register hierarchy:

- `C20_PHY_CR0_LANE0_DIG_ASIC_*`: ASIC-facing lane, TX, and RX input/output override registers.
- `C20_PHY_CR0_LANE0_DIG_TX_*`: TX power control, TX status counters, TX clock alignment, TX LBERT, FIFO, DCC, and analog crossover controls.
- `C20_PHY_CR0_LANE0_DIG_ANA_XF_TX_*`: digital-to-analog TX control/status/override surfaces, including analog control registers (`ANA_CREG00` through `ANA_CREG05`).
- `C20_PHY_CR0_LANE0_DIG_RX_*`: RX power control, VCO calibration, LBERT, CDR, DPLL frequency, adaptation, status counter, IQC, and analog crossover/power controls.

Every register block follows the same pattern: a `//REGISTER_NAME` marker followed by bit-position macros named `REGISTER__FIELD__SHIFT` and bit-mask macros named `REGISTER__FIELD_MASK`. Consumers combine these with the register offsets from the matching `dcn_3_2_0_offset.h` header and local MMIO helpers to construct read-modify-write operations.

## Important APIs, Types, and Macros

There are no C functions or data types in this chunk. The public API is the preprocessor namespace itself.

The most important macro families in this chunk are:

- Lane-level ASIC override and ASIC input mirrors:
  - `C20_PHY_CR0_LANE0_DIG_ASIC_LANE_OVRD_IN__*`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_LANE_ASIC_IN__*`
  - These expose serial/parallel loopback controls, lane transceiver mode selection, and an override enable bit.
- TX ASIC overrides:
  - `C20_PHY_CR0_LANE0_DIG_ASIC_TX_OVRD_IN_0` through `_IN_5`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_TX_OVRD_OUT`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_TX_ASIC_IN_0` through `_IN_3`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_TX_ASIC_OUT`
  - Fields cover `CLK_RDY`, `RESET`, polarity inversion, data enable, request/low-power detect, pstate, rate, width, MPLLB select, RX detect request, flyover enable, TX DCC controls, KR driver enable, VREG bypass, TX equalization cursor overrides, and ACK/status outputs.
- TX power-state and timing controls:
  - `C20_PHY_CR0_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0`, `_P0S`, `_P1`, `_P2`
  - `C20_PHY_CR0_LANE0_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_5`
  - `C20_PHY_CR0_LANE0_DIG_TX_PWRCTL_TX_CTL`
  - `C20_PHY_CR0_LANE0_DIG_TX_PWRCTL_TX_STATUS`
  - These describe per-state analog enable sequencing for refgen, VCM hold, clock, reset, serializer, digital clock, data enable, RX detect, VBOOST, DCC, bleeders, and word clock, plus programmable timing windows and power state machine status.
- TX calibration/statistics/clocking:
  - `C20_PHY_CR0_LANE0_DIG_TX_DCC_CTL_*`
  - `C20_PHY_CR0_LANE0_DIG_TX_STAT_*`
  - `C20_PHY_CR0_LANE0_DIG_TX_CLK_ALIGN_*`
  - `C20_PHY_CR0_LANE0_DIG_TX_LBERT_*`
  - `C20_PHY_CR0_LANE0_DIG_TX_FIFO_CTL`
  - These fields configure DCC IDAC offsets, expose DCC FSM state, load/start statistic counters, sample counts, comparator clock settings, clock alignment startup/retrigger/status, TX LBERT mode/patterns, calibration code status, and FIFO bypass/read-pointer behavior.
- TX analog crossover:
  - `C20_PHY_CR0_LANE0_DIG_ANA_XF_TX_OVRD_OUT_0` through `_3`
  - `C20_PHY_CR0_LANE0_DIG_ANA_XF_TX_TERM_CODE_*`
  - `C20_PHY_CR0_LANE0_DIG_ANA_XF_TX_ANA_DCC_*`
  - `C20_PHY_CR0_LANE0_DIG_ANA_XF_TX_STAT_*`
  - `C20_PHY_CR0_LANE0_DIG_ANA_XF_TX_ANA_CREG00` through `_CREG05`
  - These map analog TX clock, PLL, reset, serializer, data, refgen, VCM, VREG, bleeder, data-rate, RXDET, termination, DCC calibration, equalization status, ATB measurement, oscillator, VBOOST, pull-up/down, IBOOST, and analog override bits.
- RX ASIC overrides and mirrors:
  - `C20_PHY_CR0_LANE0_DIG_ASIC_RX_OVRD_IN_0` through `_IN_4`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_RX_OVRD_SIGDET_IN`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_RX_OVRD_VCO_IN`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_RX_OVRD_EQ_IN_0` through `_IN_11`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_RX_OVRD_OUT_0`
  - `C20_PHY_CR0_LANE0_DIG_ASIC_RX_ASIC_IN_*`
  - These cover RX reset/invert/data/request/LPD/pstate, DFE bypass, reference/VCO load values, div16p5 clock, CDR tracking/SSC, disable/bypass/flyover/loopback, DCC control, signal-detect thresholds, VCO config, EQ ATT/VGA/CTLE/AFE/DFE tap overrides, ACK/adapt/sigdet outputs, and ASIC-provided RX status.
- RX power, calibration, clock recovery, and adaptation:
  - `C20_PHY_CR0_LANE0_DIG_RX_PWRCTL_RX_PSTATE_P0`, `_P0S`, `_P1`, `_P2`
  - `C20_PHY_CR0_LANE0_DIG_RX_PWRCTL_RX_PWRUP_TIME_0`, `_1`, `_CTL`, `_STATUS`
  - `C20_PHY_CR0_LANE0_DIG_RX_VCOCAL_RX_VCO_CAL_*` and `_STAT_*`
  - `C20_PHY_CR0_LANE0_DIG_RX_CDR_CDR_CTL_*`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, `RX_DPLL_FREQ_BOUND_*`
  - `C20_PHY_CR0_LANE0_DIG_RX_ADPTCTL_*`
  - These define RX analog/digital pstate sequencing, power-up timing, RX control/status flags, VCO calibration knobs and status, CDR/SSC/DPLL tuning, adaptation setup thresholds, CTLE/VGA/ATT/DFE controls, DCC offset programming, fast flags, slicer/SSM controls, and final adaptation/status codes.
- RX statistics, IQC, and analog crossover:
  - `C20_PHY_CR0_LANE0_DIG_RX_STAT_*`
  - `C20_PHY_CR0_LANE0_DIG_RX_IQC_CTL_*`
  - `C20_PHY_CR0_LANE0_DIG_ANA_XF_RX_CTL_OVRD_OUT`
  - `C20_PHY_CR0_LANE0_DIG_ANA_XF_RX_PWR_OVRD_OUT_0`, `_1`
  - These map match patterns, masks, sample counters, stat counters, comparator clock, counter freeze/stop, load-value extensions, IQC reset/config/status, RX analog clock/data-rate/DFE/bypass/reset overrides, and RX analog AFE/VREG/clock/CDR/deserializer/bleeder/word-clock controls.

## Control Flow

There is no runtime control flow inside the header. Control flow is external:

1. DCN 3.2 display, GPIO, IRQ, DMUB, clock manager, resource, and amdgpu code include `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. A consumer chooses a register offset macro from the offset header and a field mask/shift pair from this header.
3. Driver helper macros/functions perform a field insert, field extract, or read-modify-write against the MMIO register.
4. Hardware then interprets the written bit pattern as PHY lane state, override state, calibration input, or status query.

Because this file is compile-time metadata, the sequencing rules are implicit in the consuming driver logic and in the hardware specification, not in this chunk. The register names still reveal intended flows: pstate programming precedes TX/RX power transitions, calibration control registers pair with status registers, statistic counters have load/start/stop/done fields, and override registers usually use value plus `*_OVRD_EN` fields to take control away from ASIC-provided defaults.

## State and Persistence Behavior

The macros themselves are stateless and are not persisted. They describe state that exists in hardware registers:

- Persistent until reset or reprogrammed: pstate definitions, power-up timing fields, DCC/IQC/CDR/VCO/adaptation configuration, analog control overrides, term codes, and FIFO/clock-alignment controls.
- Transient or status-like: `*_ACK`, `*_STATUS`, `*_FSM_STATE`, `*_DONE`, `*_IRQ`, `*_ERR`, `*_COUNT`, `*_STAT_CNT_*`, `RX_VCO_CAL_DONE`, DPLL frequency/status, LBERT error count, and adaptation final/status fields.
- Override fields are mostly paired as value and enable bits. The state hazard is that setting an override value without the matching enable bit has no effect, while leaving an enable bit set can pin hardware away from automatic PHY control.
- Reserved fields are explicitly masked. Consumers should avoid writing reserved masks except as part of a full generated field table with known reset values.

## Dependencies

This chunk depends on conventions shared by the AMDGPU/DCN register access layer:

- Matching offset definitions in `include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- Register-field helper macros that expect `REG__FIELD_MASK` and `REG__FIELD__SHIFT` naming.
- DCN 3.2 ASIC register layout generated from AMD hardware descriptions.
- Hardware side effects of C20 PHY CR0 lane 0 registers in the display PHY.

Repository search shows this header is included with the corresponding offset header by DCN 3.2 consumers such as:

- `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`

The exact C20 PHY field macros in this chunk also appear in the related DPCS 4.2.3 mask header, suggesting that some PHY register layouts are shared or mirrored across generated ASIC register namespaces.

## Integration Points

The chunk integrates with:

- DCN register access macros that use field names to build masks and shifts.
- Link PHY bring-up, power management, and link training paths that may program TX/RX pstate, rate, width, reset, data enable, and calibration controls.
- Debug, validation, and diagnostic paths that may force override values, select loopbacks, use LBERT patterns, freeze counters, read FSM states, or inspect error/status counters.
- Analog PHY calibration flows for DCC, VCO, CDR, IQC, EQ adaptation, CTLE/VGA/DFE, term code, IBOOST, VBOOST, and slicer configuration.
- Hardware-family tables that are generated per ASIC version and selected by DCN 3.2 display initialization code.

## Risks and Edge Cases

- Generated-header drift: if a mask or shift diverges from hardware, callers can silently write the wrong bit field. This is especially dangerous for PHY power, reset, PLL/CDR/VCO, and analog override fields.
- Value/enable pairing: many fields use `*_OVRD_VAL` or a value-like field plus `*_OVRD_EN`. Driver code must program both sides intentionally and clear overrides when returning to automatic control.
- Reserved-bit writes: this chunk includes many `RESERVED_*` masks. They should not be used as normal writable fields. Full-register writes need known reset/default treatment to avoid toggling reserved bits.
- Width assumptions: most masks are 16-bit lane registers, but fields span different widths. Callers must mask before shifting and must not assume all values are single-bit booleans.
- Status/control naming overlap: similarly named `OVRD_IN`, `ASIC_IN`, `OVRD_OUT`, `STAT_OUT`, and `STAT_IN` blocks can be confused. The direction is part of the hardware contract, not just naming decoration.
- Lane specificity: all names are lane 0 under CR0. Multi-lane code must not reuse these symbols for another lane unless the offset/header generation maps the intended lane.
- Calibration hazards: CDR, VCO, DCC, IQC, and adaptation fields can affect link stability. Debug writes in these fields may pass compile-time checks but break link training, hotplug, or display stream reliability.
- Counter latching: sample/stat counters expose done/freeze/stop/load behavior. Reading counters without respecting latch/done semantics can produce partial or stale diagnostics.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Build coverage: compile DCN 3.2 display code with `dcn_3_2_0_sh_mask.h` included and with warnings that catch missing/renamed macros.
- Macro-pair consistency: generated checks should ensure every non-reserved field has matching `__SHIFT` and `_MASK` definitions and that masks align with shifts and widths.
- Register access tests: unit or compile-time tests for field insert/extract helpers should verify representative fields such as TX pstate, TX DCC offset, RX DFE tap, RX VCO calibration, RX CDR gain, RX adaptation, RX statistic counter, and RX analog power override fields.
- Hardware bring-up: display link training and mode-set tests should exercise normal paths without forced overrides, then diagnostics can verify that status fields such as power-state FSM, VCO calibration done, CDR status, LBERT count, and adaptation final code remain coherent.
- Suspend/resume and hotplug: these paths are likely to expose stale override enables, incorrect pstate masks, or timing-register regressions.
- PHY diagnostic tests: LBERT pattern/error tests, stat counter load/start/stop tests, and DCC/IQC status reads can catch field layout regressions that ordinary display output might not isolate.

## Chunk Boundary Notes

The first visible line is already inside `C20_PHY_CR0_LANE0_DIG_ASIC_LANE_OVRD_IN`, so that register block began in an earlier chunk. The last visible block, `C20_PHY_CR0_LANE0_DIG_ANA_XF_RX_PWR_OVRD_OUT_1`, continues past line 61553, so its remaining mask definitions are expected in the next chunk. The merge lane should combine this report with adjacent chunks before producing the final per-file research document for `dcn_3_2_0_sh_mask.h`.
