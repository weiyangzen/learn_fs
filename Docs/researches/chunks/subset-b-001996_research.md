# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 163594-165984

## Purpose

This chunk is a generated AMD DCN 3.2.0 shift/mask header slice. It exports preprocessor constants for hardware register bitfields: `__SHIFT` macros give field low-bit positions and `_MASK` macros give the matching raw bit masks. The `//<REGISTER>` comments group each set of field definitions by register. There are no functions, structs, enums, allocations, locks, branches, or direct MMIO operations in this range.

The range covers C20 PHY CR3 lane metadata. It begins in the mask tail of `C20_PHY_CR3_LANE1_DIG_RX_CDR_STAT`, then covers lane 1 RX DPLL, adaptation, statistics, IQ correction, and analog-RX crossbar/register-control fields. It then transitions to lane 2 ASIC TX override/input/output fields, lane 2 TX power/control/status/statistics/clock-alignment/LBERT/equalization metadata, lane 2 analog-TX crossbar and analog control registers, and the first lane 2 RX ASIC override fields. The source tree path is under a local `ceph-client` mirror, but this file is AMDGPU display hardware metadata, not distributed filesystem logic.

The chunk is boundary-partial at both ends. Line 163594 starts after the `C20_PHY_CR3_LANE1_DIG_RX_CDR_STAT` comment and shift definitions from the prior chunk; line 165984 is the comment for `C20_PHY_CR3_LANE2_DIG_ASIC_RX_OVRD_VCO_IN`, while that register's shift and mask definitions continue in the following chunk.

## Important APIs, Types, And Macros

The only exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` for bitfield shifts.
- `<REGISTER>__<FIELD>_MASK` for bitfield masks.
- Register grouping comments such as `//C20_PHY_CR3_LANE1_DIG_RX_ADPTCTL_ADPT_CFG_0`.

Within the assigned lines there are 2,169 `#define` lines: 1,084 shift macros, 1,086 mask macros, and 222 register-comment boundaries. The shift/mask count is uneven because the slice starts in one register's mask tail and ends before the final commented register's definitions.

Major register groups in this chunk include:

- `C20_PHY_CR3_LANE1_DIG_RX_CDR_*` and `DPLL_*`: receive CDR status and DPLL frequency/bounds fields, including `PHUG_VALUE`, `FRUG_VALUE`, frequency value, and upper/lower frequency bounds.
- `C20_PHY_CR3_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration, reset, status, slicer, DFE offset, DCC offset, fast-flag, SSM, final-code, and adaptation-state fields.
- `C20_PHY_CR3_LANE1_DIG_RX_STAT_*`: pattern-match, load-value, sample-counter, statistic-counter, comparator-clock, stop, shadow-counter, and extended-load-value definitions.
- `C20_PHY_CR3_LANE1_DIG_RX_IQC_CTL_*`: IQ correction reset-adjust, configuration, and FSM state fields.
- `C20_PHY_CR3_LANE1_DIG_ANA_XF_RX_*`: analog RX crossbar override, power override, signal-detect calibration, VCO override, calibration mux/range/DAC controls, AFE overrides, scope/slicer controls, IQ/loopback/update/sample controls, termination override/status, and analog CREG00-CREG11/override fields.
- `C20_PHY_CR3_LANE2_DIG_ASIC_LANE_*` and `C20_PHY_CR3_LANE2_DIG_ASIC_TX_*`: lane 2 ASIC lane loopback/transceiver-mode inputs, TX override inputs for reset/invert/data/request/pstate/rate/width/PLL/equalization/DCC/drive controls, TX output ACK/detect/calibration status, real ASIC input mirrors, and miscellaneous TX override values.
- `C20_PHY_CR3_LANE2_DIG_TX_PWRCTL_*`: lane 2 TX pstate P0/P0S/P1/P2 analog and digital enable/reset/data/DCC/bleeder/word-clock fields, power-up timing registers, TX control, and TX status.
- `C20_PHY_CR3_LANE2_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL`: TX DCC offsets/status, statistics counters, calibration comparator clock, clock-alignment status, local BERT control/patterns, level-calculation status, and FIFO control.
- `C20_PHY_CR3_LANE2_DIG_ANA_XF_TX_*`: analog TX crossbar override outputs, termination override outputs, DCC enable/config/calibration controls, equalization override/status outputs, analog status inputs, analog CREG00-CREG05, and CREG override fields.
- `C20_PHY_CR3_LANE2_DIG_ASIC_RX_OVRD_*`: beginning of lane 2 RX override input fields for reset/invert/data/request/LPD/pstate/DFE bypass, reference and VCO load values, rate/width, DIV16P5 clock, CDR tracking/SSC/disable, VREG clock bypass, flyover, loopback, RX DCC, and signal-detect threshold/filter overrides.

Most definitions describe 16-bit register layouts. Reserved masks such as `RESERVED_15_6`, `RESERVED_15_13`, and `RESERVED_15_0` are part of the generated ABI and are important for preserving undefined or hardware-owned bits during masked writes.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by consumers that include the DCN 3.2.0 offset and shift/mask headers and pass these constants to AMDGPU register helpers.

The typical flow is:

1. DCN32 code includes `dcn_3_2_0_offset.h` for register addresses and this `dcn_3_2_0_sh_mask.h` file for fields.
2. Register-table macros and field-list macros expand the generated constants into block-specific register descriptors or firmware-facing definitions.
3. MMIO helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and generated field helpers combine offsets, masks, and shifts to read or write hardware fields.
4. Real sequencing remains in display PHY/link-training code and hardware/firmware state machines.

The macros do not encode ordering. Consumers still have to sequence RX CDR/DPLL programming, adaptation resets and starts, SSM/final-code observation, RX statistics setup and reads, IQ correction, analog calibration/override enables, TX pstate transitions, TX DCC calibration, TX detect/ACK handshakes, clock alignment, LBERT patterns, and RX override setup according to the ASIC programming model.

## State And Persistence Behavior

There is no software state or persistence in this generated header. The state described by this chunk lives in MMIO-backed PHY registers:

- Lane 1 RX CDR/DPLL state for frequency values and bounds.
- Lane 1 RX adaptation state for ATT/VGA/CTLE/DFE enablement, thresholds, mu values, adaptation reset bits, status/done fields, slicer offsets, DFE tap/status fields, RX DCC offsets, fast flags, SSM control, and final-code output.
- Lane 1 RX statistics state for pattern matching, sample counters, statistic counters, calibration-comparator clocks, stop/freeze controls, and extended load values.
- Lane 1 RX IQ correction and analog state for bypass/data adjust, analog power/clock/CDR/deserializer enables, signal-detect calibration, VCO controls, calibration muxes, DAC controls, AFE trims, scope/slicer settings, loopback, termination, analog measurements, regulator/bias controls, and CREG override latches.
- Lane 2 TX state for ASIC override inputs, live ASIC input/output mirrors, pstate control words, power-up timers, TX status, DCC offsets, statistics, clock alignment, LBERT, FIFO state, analog override outputs, DCC calibration, equalization status, and analog TX control registers.
- Lane 2 RX override state at the end of the chunk for reset/request/data/rate/width/pstate/DFE bypass, reference/VCO load values, CDR tracking and SSC, loopback, RX DCC, and signal-detect threshold/filter fields.

Persistence and side effects are hardware-defined. Some fields are stable configuration bits; others are read-only status, sticky status, write-one-to-clear, self-clearing triggers, firmware-owned state, calibration outputs, or override enables that persist only until link retrain, modeset, suspend/resume, power gating, or ASIC reset. Access type, reset values, and side-effect semantics are not represented in this header and must come from the register specification and the driver code that uses these macros.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`; offsets and shift/mask definitions are a single generated register ABI. A mismatch can compile cleanly while causing masked reads or writes to decode or update the wrong bitfields.

Direct include sites for the DCN 3.2.0 offset and shift/mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

Functional integration points include:

- DCN32 resource and block construction that binds generated masks/shifts into display register tables.
- DMUB/DCN32 initialization paths that expose register and field definitions to firmware-facing display logic.
- Link bring-up, retraining, hotplug, and power-management paths that need lane pstate, request/ACK, rate, width, PLL, CDR, DCC, and calibration controls.
- PHY diagnostic paths that inspect adaptation status, DFE/CTLE/VGA/ATT codes, RX/TX statistics, clock-alignment status, LBERT counters/patterns, equalization state, analog status, and calibration readbacks.
- Debug/override paths where forcing TX or RX reset/request/pstate/rate/width, loopback, DFE bypass, CDR tracking, signal-detect thresholds, analog enables, or DCC controls can temporarily bypass normal firmware/hardware ownership.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can silently corrupt PHY programming even when the code builds.
- The chunk is not a standalone logical module. It starts inside a lane 1 CDR status register and ends on the comment for the next lane 2 RX VCO override register.
- Lane identity is easy to mix up. `C20_PHY_CR3_LANE1_*` and `C20_PHY_CR3_LANE2_*` fields are valid-looking but target different lane register banks.
- RX adaptation fields mix configuration, reset, status, slicer offsets, DFE coefficients, DCC offsets, SSM state, and final-code readbacks. Treating status fields as writable controls or resetting only part of the adaptation state can leave hardware in inconsistent training state.
- Statistics and sample-counter fields have done/freeze/stop controls. Reading counters without respecting done bits, freeze selection, or clock enable state can produce misleading diagnostics.
- Override fields can supersede firmware or hardware-owned control. Forcing reset, pstate, rate, width, CDR tracking, DFE bypass, analog enables, TX drive/equalization, or DCC update bits can break link training or power transitions.
- TX pstate definitions encode many analog and digital enables per power state. One-bit mistakes can cause lane bring-up failures, excessive power, missing RX detect, missing data enable, or invalid DCC/word-clock behavior.
- DCC, VCO, IQ, signal-detect, and analog calibration fields are sensitive to link rate, temperature, voltage, and board characteristics. Bad masks can cause failures that appear only under certain rates or after suspend/resume/retrain.
- Reserved fields are explicitly emitted and should be preserved unless the hardware specification requires otherwise.
- Access type is not encoded. Clear, trigger, sticky, self-clearing, read-only, and firmware-owned fields all look like ordinary masks in this header.

## Test Signals

Useful validation for changes touching this range includes:

- Build AMDGPU Display Core with DCN32 support enabled; malformed macro names or duplicate definitions should surface in DCN32 resource, DMUB, IRQ, clock, GPIO, and low-level register users.
- Mechanically compare this range against the authoritative AMD register database or a regenerated `dcn_3_2_0_sh_mask.h`.
- Cross-check matching registers in `dcn_3_2_0_offset.h` so the `C20_PHY_CR3_LANE1_*` and `C20_PHY_CR3_LANE2_*` offsets align with these field layouts.
- On DCN32 hardware, exercise DisplayPort/PHY bring-up and retraining across lane counts, link rates, pstate transitions, hotplug, suspend/resume, and DFE-bypass/adaptation scenarios.
- Inspect lane 1 RX adaptation diagnostics: ATT/VGA/CTLE/DFE done bits, DFE tap codes, slicer offsets, RX DCC offsets, SSM state, final code, and fast flags should decode consistently.
- Validate RX/TX statistic and sample-counter behavior by checking pattern-match controls, sample-done bits, counter freeze/stop behavior, comparator-clock enable, and shadow-counter reads.
- Validate lane 2 TX state transitions through P0/P0S/P1/P2 and power-up timing; status fields should reflect expected analog/digital enable, reset, data, DCC, word-clock, and RX-detect behavior.
- Run PHY diagnostics for TX DCC, clock alignment, LBERT, equalization, analog-TX status, analog-RX calibration, signal detect, VCO, and loopback paths.
- Compare register dumps before and after calibration, link retrain, power transitions, and debug override use; masked writes should affect only intended fields and reserved bits should remain stable.

## Cross-Chunk Notes

The final per-file report should merge this artifact with the previous chunk for the complete `C20_PHY_CR3_LANE1_DIG_RX_CDR_STAT` definitions and with the following chunk for `C20_PHY_CR3_LANE2_DIG_ASIC_RX_OVRD_VCO_IN` and later lane 2 RX fields. This document is intentionally limited to lines 163594-165984 and is the source-tree-aligned chunk artifact for `subset-b-001996`.
