# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 195230-197621

## Scope

- Chunk id: `subset-b-002009`
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h`
- Source lines: 195230-197621
- Observed content: 2,392 lines, 2,170 `#define` entries, 1,083 `__SHIFT` macros, 1,087 `_MASK` macros, and 222 register block comments.

This chunk is generated AMD DCN 3.2.0 register field metadata for the C20 PHY CR4 lane 1 digital register block. It contains preprocessor constants only. There are no C functions, structs, enums, executable branches, memory allocations, locks, direct MMIO operations, or persistent software data structures in this range.

The range starts inside `C20_PHY_CR4_LANE1_DIG_ASIC_TX_OVRD_IN_1`, covers most of the lane 1 TX digital, TX analog crossover, RX override, RX power/calibration/adaptation/statistics, IQC, and RX analog crossover definitions, and ends inside `C20_PHY_CR4_LANE1_DIG_ANA_XF_RX_VCO_OVRD_OUT_1`. Adjacent chunks are needed for the leading fields of the first register and the remaining fields of the final VCO override register.

## Purpose

The purpose of this header slice is to publish bit positions and bit masks for C20 PHY CR4 lane 1 registers used by DCN 3.2 display/link code. The matching offset header identifies register addresses; this file provides the field layout used by register helpers to pack writes and unpack reads.

The covered hardware surface is lane-oriented PHY control rather than high-level display policy:

- ASIC-facing TX and RX control mirrors and override registers.
- TX power-state sequencing, power-up timing, DCC, statistics, clock alignment, LBERT, FIFO, equalization, termination, and analog control fields.
- RX power-state sequencing, VCO calibration, LBERT, CDR/DPLL, adaptation, DFE/CTLE/VGA/ATT controls, slicer state, status counters, IQC, signal detect calibration, and analog power/VCO override fields.
- Value-plus-enable override pairs that let debug, bring-up, or validation paths force PHY state away from automatic ASIC-provided control.

## Important APIs, Types, and Macros

There are no C APIs or types in this chunk. The public interface is the generated macro namespace:

- `C20_PHY_CR4_LANE1_DIG_*__FIELD__SHIFT` gives the least-significant bit number for a field.
- `C20_PHY_CR4_LANE1_DIG_*__FIELD_MASK` gives the unshifted mask for that field.
- `//C20_PHY_CR4_LANE1_DIG_*` comments group field definitions by hardware register.

Important macro families in this chunk:

- `C20_PHY_CR4_LANE1_DIG_ASIC_TX_OVRD_IN_1` through `_IN_5`, `TX_OVRD_OUT`, `TX_ASIC_IN_0` through `_IN_3`, `TX_ASIC_OUT`, and `TX_OVRD_MISC`: TX-facing override and mirror fields for rate, width, wide-transfer alignment, MPLLB select, RX detect request, flyover enable, disable/beacon/VBOOST/IBOOST, equalization cursors, DCC bypass/update/range, lane/clock deskew, KR driver enable, VREG bypass, TX ACK, RX detect result, and calibration status.
- `C20_PHY_CR4_LANE1_DIG_ASIC_LANE_ASIC_IN`: lane loopback and transceiver mode mirror fields, including serial TX-to-RX loopback, parallel RX-to-TX loopback, and lane XCVR mode.
- `C20_PHY_CR4_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0`, `_P0S`, `_P1`, and `_P2`: per-state TX analog/digital sequencing bits for refgen, VCM hold, clock, reset, serializer, digital clock, data enable, RX detect allowance, VBOOST, DCC, VREG bleeders, and word clock.
- `C20_PHY_CR4_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` through `_5`, `TX_CTL`, and `TX_STATUS`: TX timing windows, transition controls, bypass/fsm controls, ACK bypass, and TX power state status.
- `C20_PHY_CR4_LANE1_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL`: TX DCC IDAC offsets and FSM state, statistic load/sample/count controls, comparator clock configuration, clock alignment retrigger/status, TX LBERT enable/mode/pattern, level calculation code, and FIFO bypass/read-pointer control.
- `C20_PHY_CR4_LANE1_DIG_ANA_XF_TX_OVRD_OUT_0` through `_3`: digital-to-analog TX override outputs for analog clock, MPLL, reset, serializer, data, refgen, VCM, DCC, VREG, data rate, RXDET, VBOOST, VPTX, LFPS, and related override enables.
- `C20_PHY_CR4_LANE1_DIG_ANA_XF_TX_TERM_CODE_*`, `TX_ANA_DCC_*`, `TX_STAT_*`, and `TX_ANA_CREG00` through `_CREG05`: TX analog termination, DCC calibration, equalization status, analog status mirrors, and analog configuration registers for pull-up/down, oscillator, IBOOST, VBOOST, measurement, MPLL clock enables, ring control, bias, and charge-pump/VREG behavior.
- `C20_PHY_CR4_LANE1_DIG_ASIC_RX_OVRD_IN_0` through `_IN_4`, `RX_OVRD_SIGDET_IN`, `RX_OVRD_VCO_IN`, and `RX_OVRD_EQ_IN_0` through `_IN_11`: RX override fields for reset, invert, data enable, request, low-power detect, pstate, DFE bypass, reference/VCO load values, rate/width, div16p5 clock, CDR tracking/SSC, disable, clock VREG bypass, flyover, loopback, DCC controls, signal-detect thresholds, CDR VCO config, CTLE/VGA/ATT/AFE controls, DFE taps, and even/odd high/low DFE tap offsets.
- `C20_PHY_CR4_LANE1_DIG_ASIC_RX_ASIC_IN_*`, `RX_CDR_VCO_ASIC_IN`, `RX_EQ_ASIC_IN_*`, and `RX_ASIC_OUT_0`: ASIC-provided RX mirrors for reset/data/request/pstate/rate/width, signal detect, DCC range, VCO load/config, equalization levels, ACK, valid, and adaptation status.
- `C20_PHY_CR4_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, `_P0S`, `_P1`, `_P2`, `RX_PWRUP_TIME_*`, `RX_CTL`, and `RX_STATUS`: RX analog/digital power-state sequencing, programmable timing, power-control mode, and FSM/status outputs.
- `C20_PHY_CR4_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_*` and `RX_VCO_STAT_*`: RX VCO calibration control, timing, load/start/override parameters, done/status signals, lock counters, FSM state, and final codes.
- `C20_PHY_CR4_LANE1_DIG_RX_CDR_*`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*`: CDR PI gain/offset controls, fractional frequency and SSC controls, tracking status, DPLL frequency readback, and min/max bounds.
- `C20_PHY_CR4_LANE1_DIG_RX_ADPTCTL_*`: RX adaptation configuration and reset controls, ATT/VGA/CTLE/DFE status, DFE VDAC offsets, slicer controls, DCC offset programming, fast flags, SSM configuration, and SSM final status codes.
- `C20_PHY_CR4_LANE1_DIG_RX_STAT_*`: RX statistic pattern/load/match controls, sample counters, statistic counters, comparator clock controls, counter stop/freeze controls, shadowed counts, and extended load values.
- `C20_PHY_CR4_LANE1_DIG_RX_IQC_CTL_*` and `C20_PHY_CR4_LANE1_DIG_ANA_XF_RX_*`: IQC reset/config/status, RX analog control overrides, RX analog power overrides, signal-detect calibration/tuning, and CDR VCO override output fields.

## Control Flow

This chunk has no runtime control flow. Control flow is supplied by consumers that include `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, select a register offset and a field mask/shift pair, then use AMDGPU Display Core register helpers to read, update, wait on, or write MMIO fields.

Typical external flow for definitions in this chunk:

1. DCN 3.2 initialization selects generated register, shift, and mask tables for the ASIC.
2. Link/PHY setup programs TX and RX pstate fields, power-up timing fields, lane rate/width, clocking, reset, data enable, and CDR/VCO/adaptation controls.
3. Training, diagnostics, or validation code may enable loopback, LBERT, DCC/IQC calibration, statistics counters, clock alignment, or forced override values.
4. Status paths read ACK, valid, FSM, done, counter, calibration, DPLL, adaptation, EQ, and error fields to determine whether the PHY lane reached the requested state.
5. Cleanup or normal operation should clear debug override enables so automatic ASIC control can resume.

The naming reveals several implicit sequencing contracts even though the sequencing code is outside this header: pstate definitions precede power transitions, `*_OVRD_VAL` or value-like fields are effective only with matching `*_OVRD_EN` bits, calibration starts pair with done/status fields, statistic loads pair with sample/count done fields, and reset/bypass fields can block normal link behavior if left asserted.

## State and Persistence Behavior

The macros themselves are stateless compile-time constants. They describe hardware register state with several different lifetimes:

- Programmed state that persists until reset, power gating, suspend/resume, hotplug reconfiguration, modeset reprogramming, or a later register write: pstate definitions, power-up timing, TX/RX DCC controls, CDR/DPLL tuning, VCO calibration parameters, adaptation thresholds, analog CREG values, termination codes, FIFO controls, and override enable bits.
- Volatile status and readback state: TX/RX ACK, DETRX result, calibration status, TX/RX power FSM status, DCC FSM state, clock alignment status, LBERT error count, VCO calibration done/status/final codes, CDR status, DPLL frequency, adaptation status, SSM final code, statistic counters, IQC FSM state, and analog status mirrors.
- Side-effecting or control-like fields: reset, data enable, request, pstate, start/load/freeze/stop controls, calibration enables, counter controls, FIFO bypass, clock alignment retrigger, LBERT enable, override enables, and bypass bits. Incorrect use can change PHY behavior immediately.

There is no disk persistence or driver-owned durable storage in this chunk. Any persistence is hardware register persistence and is bounded by the display hardware power/reset lifecycle.

## Dependencies

This chunk depends on the generated AMDGPU/DCN register ecosystem:

- Matching register offsets in `include/asic_reg/dcn/dcn_3_2_0_offset.h`.
- Register helper conventions that expect paired `__SHIFT` and `_MASK` symbols.
- DCN 3.2 ASIC register tables generated from AMD hardware descriptions.
- Hardware interpretation of C20 PHY CR4 lane 1 registers.

Repository include points for `dcn_3_2_0_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`

The concrete lane fields in this chunk are also coupled to nearby generated C20 PHY lane blocks in the same header. CR/lane prefixes are part of the ABI: using `CR4_LANE1` masks with a register table for another CR or lane can compile if the surrounding table is wrong, but it would address the wrong hardware lane semantics at runtime.

## Integration Points

The definitions integrate with:

- DCN32 resource and register-table initialization, which wires generated offsets, masks, and shifts into display engine structures.
- Display link encoder and PHY bring-up paths that program rate, width, reset, data enable, request, pstate, clocking, DCC, VCO, CDR, and adaptation controls.
- Link training and recovery code that relies on RX signal detect, CDR, VCO, equalization, DFE/CTLE/VGA/ATT, and status readbacks.
- Power management and suspend/resume paths that need coherent TX/RX pstate sequencing, power-up timing, ACK/FSM status, and analog power controls.
- Diagnostics and validation flows that use loopbacks, LBERT patterns/error counts, statistic counters, clock alignment, IQC/DCC/VCO calibration, and analog override/readback fields.
- Hardware debug interfaces that may intentionally force `*_OVRD_EN` controls for narrow experiments and then release them.

## Risks and Edge Cases

- Numeric drift in a generated mask or shift can compile cleanly and still program the wrong PHY bit. High-risk areas include reset, power state, clock enable, CDR/VCO, DCC, adaptation, and analog override fields.
- Override fields usually require both a value and an enable bit. Setting only a value has no effect; leaving an enable bit set can pin the lane away from automatic control and cause later link training, hotplug, or power transitions to fail.
- Many registers contain `RESERVED_*` masks. Normal consumers should not treat reserved masks as writable feature fields, and full-register writes need authoritative reset/default handling.
- Directional names matter. `OVRD_IN`, `OVRD_OUT`, `ASIC_IN`, `ASIC_OUT`, `STAT_IN`, and `STAT_OUT` indicate different hardware directions; mixing them can lead to reads of write-only intent fields or writes to status/override outputs.
- The chunk is lane-specific. `C20_PHY_CR4_LANE1` fields must not be reused for another C20 PHY lane or CR instance unless the generated register table explicitly maps that same hardware layout.
- Calibration and adaptation fields are timing-sensitive. CDR, VCO, DCC, IQC, DFE, CTLE, VGA, slicer, and SSM controls may fail only at specific link rates, voltage conditions, cable/display combinations, or after suspend/resume.
- Status counter and LBERT fields have latch/load/done semantics. Reading counters without respecting sample completion, freeze, or shadow rules can produce stale or partial diagnostics.
- The chunk boundaries cut through register groups. The first visible macros are the tail of `TX_OVRD_IN_1`, and the final visible register `RX_VCO_OVRD_OUT_1` is incomplete because its reserved mask is outside this line range.

## Test Signals

Useful validation signals for code that consumes this chunk:

- Build DCN 3.2 display code and ensure all generated `C20_PHY_CR4_LANE1_DIG_*` field names resolve through the selected offset/mask/shift tables.
- Run generated-header consistency checks: paired `__SHIFT` and `_MASK` definitions where expected, masks aligned with shifts, no unintended overlapping fields within a register, masks within the 16-bit lane-register width commonly used in this block, and no accidental reuse of CR4 lane 1 symbols in another lane table.
- Exercise display link bring-up across rate and width changes, pstate transitions, reset/data-enable/request sequencing, and normal operation without forced overrides.
- Test suspend/resume, hotplug, link retraining, and display blank/unblank to catch stale override enables, bad pstate masks, and power FSM or ACK regressions.
- Use PHY diagnostics for TX/RX LBERT patterns and error counts, clock alignment status, TX/RX statistic counters, DCC/IQC status, VCO calibration done/final codes, DPLL frequency bounds, CDR status, and adaptation/SSM final codes.
- Validate RX equalization and adaptation behavior across marginal links or compliance setups, watching ATT/VGA/CTLE/DFE status fields, slicer offsets, fast flags, and signal-detect threshold behavior.
- For analog override debug flows, verify that forced analog clock, VREG, CDR, deserializer, VCO, signal detect, DCC, termination, and TX/RX power fields are cleared or restored before returning to normal automatic control.

## Chunk-Specific Summary

Lines 195230-197621 define generated shift/mask constants for the C20 PHY CR4 lane 1 digital TX/RX register surface in DCN 3.2.0. The content is register ABI metadata, not executable logic. Correctness depends on exact numeric field definitions, preserving the CR4 lane 1 namespace, treating value/enable override pairs carefully, avoiding reserved-bit writes, and validating consumers with build checks plus real PHY link, calibration, adaptation, diagnostics, hotplug, and power-management tests.
