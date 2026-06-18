# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 66320-68712

## Scope

This chunk is a generated DCN 3.2.0 register-field shift/mask slice. It contains preprocessor constants only: register comments, `<REGISTER>__<FIELD>__SHIFT` definitions, and `<REGISTER>__<FIELD>_MASK` definitions. There are no C functions, types, branches, loops, allocation paths, locks, direct MMIO calls, or persistence structures in this range.

The slice covers 2,393 lines with 2,169 `#define` entries, grouped by 224 register comments. It starts in the tail of `C20_PHY_CR0_LANE2_DIG_ASIC_RX_ASIC_IN_2`, covers a large set of lane-2 RX control/status/analog-transfer fields and the beginning of lane-3 TX fields, and ends after the shift definitions for `C20_PHY_CR0_LANE3_DIG_ANA_XF_TX_TERM_CODE_CLK_OVRD_OUT`; the masks for that final register are outside this chunk. Neighboring chunks must be merged for complete register-family coverage.

## Purpose And Hardware Surface

`dcn_3_2_0_sh_mask.h` is part of AMDGPU's generated DCN 3.2.0 register ABI. Companion offset headers name register addresses; this header supplies bit positions and masks used by AMD Display Core register helpers to pack values into hardware MMIO registers and decode fields read back from hardware. The visible range is centered on C20 PHY lane register definitions, mostly 16-bit PHY register layouts encoded as C macros.

Major hardware surfaces represented here:

- Lane 2 RX ASIC input and status: reference-load, VCO-load, CDR VCO configuration, RX equalizer inputs, ASIC output ACK/VALID/adaptation status, and RX miscellaneous override fields.
- Lane 2 RX override controls: DFE tap offset override families for even/odd, data/error/bypass high/low paths; IQ, AFE bias, CTLE zero, CTLE offset, and miscellaneous override enable/value fields.
- Lane 2 RX power-state controls: `RX_PSTATE_P0`, `P0S`, `P1`, and `P2` fields for analog bleeder, AFE, clock regulators, dividers, DCC clock, deserializer, CDR, VCO reset/calibration, continuous calibration, digital clock, DFE, and bypass/SLC behavior.
- Lane 2 RX power sequencing and status: power-up timers, request/ack protocol, PLL lock selection, RX request selection, current request/status fields, and power control FSM state.
- Lane 2 RX VCO calibration and CDR: calibration control, bin/boost/init values, max/min code, frequency/reset controls, calibration timers, stat bins/codes, CDR frequency/phase/gain controls, lock thresholds, lock indicators, and DPLL frequency bounds.
- Lane 2 RX adaptation: adaptation configuration, resets, thresholds, timers, adaptive equalization and DFE controls, ATT/VGA/CTLE/DFE status, DFE VDAC offsets, slicer controls, DCC IDAC offsets, fast flags, and SSM final-code/status fields.
- Lane 2 RX statistics and IQC: statistical match/control/sample/count windows, calibration comparison clock controls, stop bits, shadow count, extended load values, IQC reset/config/status.
- Lane 2 analog transfer (`ANA_XF`) RX interface: RX control and power override outputs, signal-detect calibration, VCO override controls, calibration controls, VDAC/DAC controls, AFE override inputs, scope/slicer/IQ controls, IQC adjust clocks/data override, loopback, AFE update, sampler selection, termination-code override, RX status outputs, status inputs, and many analog CREG control registers plus override toggles.
- Lane 3 TX ASIC and power-control surface: lane override input, TX override inputs/outputs, lane ASIC input, TX ASIC input/output fields, TX miscellaneous override, `TX_PSTATE_P0/P0S/P1/P2`, TX power-up timers, TX request/status FSM fields, DCC offset/stat fields, TX statistics, TX clock alignment, LBERT pattern generation, TX FIFO, and analog-transfer TX override fields.

## Important Definitions

The generated naming scheme is the important API surface:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted bit mask for that same field.
- `//<REGISTER>` comments group all following field macros until the next register comment.
- Repeated prefixes encode PHY topology: `C20_PHY_CR0_LANE2_DIG_RX_*` for lane-2 receive-side digital/analog controls and `C20_PHY_CR0_LANE3_DIG_TX_*` for lane-3 transmit-side controls.

Important macro families in this chunk:

- `C20_PHY_CR0_LANE2_DIG_ASIC_RX_*` defines the ASIC-visible lane-2 RX input/output fields for equalization, reference/VCO load values, CDR VCO setup, adaptation status, and overrideable miscellaneous RX controls.
- `C20_PHY_CR0_LANE2_DIG_RX_PWRCTL_*` defines lane-2 RX power-state templates, sequencing timers, request control, status readback, PLL lock selection, and power-state FSM fields.
- `C20_PHY_CR0_LANE2_DIG_RX_VCOCAL_*` defines VCO calibration setup, calibration code constraints, boost/init/bin selections, timer fields, and calibration status readback.
- `C20_PHY_CR0_LANE2_DIG_RX_CDR_*`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_*` define RX clock-data recovery and DPLL configuration/status fields, including frequency/phase integral gain, lock thresholds, and lock status.
- `C20_PHY_CR0_LANE2_DIG_RX_ADPTCTL_*` defines the receiver adaptation controller: adaptation enable/disable/reset flags, thresholds, DFE/tap status, slicer levels, DCC offset values, fast flags, and SSM control/final-code fields.
- `C20_PHY_CR0_LANE2_DIG_RX_STAT_*` defines lane-2 RX statistic collection: load values, data masks, match controls, statistic controls, sample counts, statistic counters, calibration comparison clocking, stop bits, and shadow count.
- `C20_PHY_CR0_LANE2_DIG_RX_IQC_CTL_*` defines IQ calibration reset, configuration, adjustment-clock control, calibration counters, and status fields.
- `C20_PHY_CR0_LANE2_DIG_ANA_XF_RX_*` defines the digital-to-analog transfer register interface for lane-2 RX, including override outputs, calibration enables, VCO/AFE/DAC/IQ/slicer/sampler/termination controls, loopback, status outputs/inputs, and `ANA_CREG00` through `ANA_CREG11` bitfields.
- `C20_PHY_CR0_LANE3_DIG_ASIC_*` defines the first lane-3 TX ASIC interface fields in this chunk: TX power/drive/pre-emphasis/swing override inputs, TX ASIC inputs, TX output ACK/VALID status, and TX miscellaneous override.
- `C20_PHY_CR0_LANE3_DIG_TX_PWRCTL_*` defines lane-3 TX power-state templates, timers, request control/status, and p-state FSM fields.
- `C20_PHY_CR0_LANE3_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL` define lane-3 TX DCC calibration/status, statistic collection, clock alignment, link BERT test-pattern generation, calibration-code readback, and FIFO behavior.
- `C20_PHY_CR0_LANE3_DIG_ANA_XF_TX_OVRD_OUT_*` and `TX_TERM_CODE_*` define lane-3 analog TX override outputs for clocks, resets, serializers, data enable, reference generation, VCM hold, regulators/bleeders, data rate, loopback, RX detection, reference select, voltage boost, word clock, miscellaneous analog control, async reset, and termination-code override.

## Control Flow And State Behavior

There is no executable control flow in this header. Runtime behavior is created by code that combines these constants with matching register offsets and AMDGPU/DCN register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `FD`, `FN`, or generated register tables.

Typical runtime use:

1. DCN 3.2 initialization code includes this header with the matching offset header and builds per-block register descriptor tables.
2. PHY/display link bring-up code programs lane RX/TX power-state templates, request bits, calibration controls, EQ/adaptation controls, CDR/DPLL controls, and analog override fields as a link transitions through training, enable, low-power, and reset states.
3. Status and diagnostics paths read ACK/VALID bits, adaptation state, PLL/CDR/VCO calibration status, DFE/equalizer status, statistic counters, signal-detect status, CREG/status outputs, TX status, clock-alignment state, and LBERT/statistic fields.
4. Test and debug flows may set explicit override values and override-enable bits to bypass automatic analog/PHY control, force termination/data-rate/clock behavior, inject LBERT patterns, or observe calibration/statistical outputs.

The state represented here is hardware register state:

- Programmed state includes RX/TX p-state templates, power-up delays, request selections, VCO/CDR/DPLL calibration parameters, equalization/adaptation thresholds, DFE/slicer/DCC offsets, IQC configuration, signal-detect calibration, analog override values/enables, TX drive/swing/pre-emphasis settings, TX clock alignment setup, LBERT pattern registers, FIFO setup, and termination-code override fields.
- Volatile readback includes RX/TX ACK and VALID bits, adaptation state/status, power-control FSM status, VCO calibration codes/bins, CDR lock status, DPLL frequency readback, DFE/equalizer status, statistic counters, IQC status, analog status outputs/inputs, TX statistic counters, clock alignment status, and TX calibration-code readback.
- Side-effecting fields include reset bits, request bits, calibration enable/reset fields, statistic stop/control bits, override-enable bits, LBERT trigger-error control, status/ACK handshakes, and self-clearing termination-clock control. Incorrect masks for these fields can change hardware state even when the caller intends a narrow update.

## Dependencies And Integration Points

This chunk depends on exact generated-name consistency with the rest of the DCN 3.2.0 register header family. Direct includes of `dcn/dcn_3_2_0_sh_mask.h` in this tree include DCN 3.2 DMUB, IRQ service, GPIO factory/translation, clock manager, resource construction, and one GMC source. The same field names also appear in the generated DPCS 4.2.3 shift/mask header, indicating that this PHY register surface is shared or mirrored across generated register namespaces.

Integration points to consider during merge-level research:

- Display Core register helper infrastructure consumes `_SHIFT` and `_MASK` names to compose register field operations. A missing macro usually fails compilation; a wrong numeric value can compile and only fail on hardware.
- DCN 3.2 resource, GPIO, IRQ, DMUB, and clock-manager code includes this header directly, so generated symbol drift can affect display initialization, interrupt decoding, firmware-facing register programming, and board/connector control.
- PHY/link encoder/link training paths are the likely semantic consumers for the C20 PHY lane RX/TX families, even if many references are generated or table-driven rather than literal `C20_PHY_CR0_LANE*` symbols in handwritten code.
- Neighboring generated headers provide register addresses and related instances. These shift/mask definitions are not useful alone; they must match offsets for `C20_PHY_CR0_LANE2` and `C20_PHY_CR0_LANE3` registers exactly.
- The lane-2 RX and lane-3 TX split is topologically important. Mistakenly copying a lane-2 RX field into lane-3 TX programming, or vice versa, would not necessarily be caught by type checking because all exports are integer-like macros.

## Risks And Maintenance Notes

- Numeric drift is the primary risk. A one-bit mask or shift error can corrupt PHY calibration, lane power sequencing, equalizer/adaptation behavior, signal detection, TX drive, termination, or status decoding.
- The range contains many repeated structures with small variations: p-states `P0/P0S/P1/P2`, DFE high/low and even/odd offsets, statistic windows, DCC offset families, CREG registers, TX override groups, and status/control pairs. Generator or copy errors can produce valid C symbols with subtly wrong field positions.
- Override fields are high-risk because they can bypass automatic PHY behavior. Incorrect `*_OVRD_EN` masks can force analog controls during normal operation or fail to apply a diagnostic override.
- Power/reset/calibration fields are sequencing-sensitive. Bad masks may produce intermittent link bring-up failures, failed resume, CDR/VCO unlock, unstable signal detection, or failures that only appear at certain link rates.
- Status fields are used for diagnostics and link-training decisions. Incorrect masks can make the driver believe calibration, adaptation, CDR lock, or TX clock alignment succeeded when hardware is not ready.
- Addressing by lane prefix must be preserved. This chunk transitions from lane-2 RX to lane-3 TX at `C20_PHY_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN`, so merge or parser tooling should not group the whole chunk as one logical lane.
- The first and last register groups are partial. Lines 66320-66323 complete `C20_PHY_CR0_LANE2_DIG_ASIC_RX_ASIC_IN_2`, whose earlier shift definitions are outside this chunk, and lines 68709-68712 begin `C20_PHY_CR0_LANE3_DIG_ANA_XF_TX_TERM_CODE_CLK_OVRD_OUT` without its masks.

## Test Signals

Useful validation combines generated-header consistency checks, build coverage, and hardware/link behavior:

- Build AMDGPU with DCN 3.2 display support enabled and ensure all direct includers of `dcn_3_2_0_sh_mask.h` compile with the matching offset headers.
- Run a generated-register consistency pass over this range: each complete field should have matching `_SHIFT` and `_MASK` entries, masks should fit the intended 16-bit/32-bit register width, fields within a register should not overlap unexpectedly, and repeated p-state/lane families should match the authoritative register specification.
- Compare this range against the DCN 3.2.0/C20 PHY source specification, focusing on reset, request, override-enable, calibration, CDR/DPLL lock, statistic stop/control, LBERT trigger, and termination-clock self-clear fields.
- Exercise display link bring-up at multiple link rates and lane counts, including cold boot, hotplug, modeset, suspend/resume, link retraining, and low-power entry/exit while watching for CDR/VCO lock failures, training retries, blank displays, flicker, or PHY timeout logs.
- Stress RX adaptation and equalization by testing marginal cables/monitors or compliance patterns where DFE, CTLE, VGA, slicer, DCC, and IQC fields affect stability.
- Exercise TX behavior with link BERT/test-pattern modes if available, checking TX LBERT patterns, FIFO behavior, clock alignment, DCC status, drive/swing/pre-emphasis programming, and termination-code override.
- Use debugfs/register dumps or driver tracepoints to confirm status decoding for ACK/VALID, adaptation status, power FSM state, VCO calibration status, CDR lock, statistic counters, signal-detect calibration, analog status outputs, TX status, and clock alignment status.

## Chunk-Specific Summary

Lines 66320-68712 define DCN 3.2.0 C20 PHY register shifts and masks for the tail of lane-2 RX ASIC input, lane-2 RX equalization/adaptation/power/VCO/CDR/statistics/IQC/analog-transfer controls, and the start of lane-3 TX ASIC/power/DCC/statistics/clock-align/LBERT/FIFO/analog-transfer controls. The content is generated register ABI rather than executable logic. Correctness depends on exact bit positions, complete pairing with matching register offsets and neighboring chunks, preserving lane-specific prefixes, and validating high-risk power, reset, calibration, override, status, and link-training behavior on hardware.
