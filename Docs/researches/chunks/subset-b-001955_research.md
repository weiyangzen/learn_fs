# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 63932-66319

## Purpose

This chunk is generated AMD DCN 3.2.0 register bitfield metadata for a C20 PHY CR0 lane slice. It contains only C preprocessor constants, following the standard generated naming contract `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`. The constants describe bit positions and masks for 16-bit PHY control/status registers; they do not implement logic by themselves.

The range begins at the tail of lane 1 RX adaptation control and status fields, covers lane 1 RX statistic/IQC/analog transfer control fields, then crosses into lane 2 ASIC-facing lane, TX, power, DCC, statistic, clock-align, LBERT, analog TX, and early RX override fields. Line 66319 stops inside `C20_PHY_CR0_LANE2_DIG_ASIC_RX_ASIC_IN_2`, so the full lane 2 RX ASIC input family continues in the next chunk.

## Major Register Areas

The first section completes `C20_PHY_CR0_LANE1_DIG_RX_ADPTCTL_*` definitions. It includes reset controls for individual adaptation loops (`RST_ADPT_ATT`, `RST_ADPT_VGA`, CTLE boost/pole, DFE taps, RX DCC, AFE rate/VCM/bias/zero/TIA), adaptation result status for attenuator, VGA, CTLE, and DFE taps 1-5, slicer and VDAC offset fields for even/odd data/error/bypass paths, error slicer levels, `RESET_ASM1`, DCC phase/data/bypass IDAC offsets, fast flags, extra adaptation config, SSM state-machine configuration, and final SSM codes. These fields expose and override low-level RX equalization and adaptation state for lane 1.

The next lane 1 block is `C20_PHY_CR0_LANE1_DIG_RX_STAT_*`. It defines statistic engine load values, masks, match controls, statistic controls, sample counters, statistic counters, calibration compare clock controls, stop control, shadowed counter count, and extended load values. The field names indicate a hardware counter/matcher path used to sample RX data or calibration state, with controls for mask/compare behavior, capture scope, clear/load behavior, and stop-on-match behavior.

`C20_PHY_CR0_LANE1_DIG_RX_IQC_CTL_*` supplies IQ calibration reset-adjust, config, and status fields. It covers IQC enable/adjust paths, bypass/override style controls, calibration-done or status reporting, and related reset behavior. It sits between the digital statistic block and the analog transfer controls, suggesting it bridges RX data-quality calibration with analog front-end state.

The largest lane 1 section is `C20_PHY_CR0_LANE1_DIG_ANA_XF_RX_*`. It defines analog RX transfer override outputs, power overrides, signal-detect calibration, CDR/VCO overrides, calibration mux/DAC controls, analog trim, AFE overrides, scope/slicer/IQ controls, IQC bypass/data adjustment clocks, loopback, AFE update, DFE/bypass/phase sample selection, termination-code overrides, analog status inputs/outputs, and a bank of analog control registers `ANA_CREG00` through `ANA_CREG11` plus reserved override registers. The fields cover RX power sequencing, clock enables, CDR/VCO tuning, DCC/calibration DAC setup, signal detect thresholds, loopback, termination, VDAC and slicer behavior, ATB measurement muxing, regulator settings, bias/trim controls, and reserved control-register surfaces.

The chunk then switches to lane 2. `C20_PHY_CR0_LANE2_DIG_ASIC_LANE_*` exposes lane-level ASIC and override fields for TX-to-RX serial loopback, RX-to-TX parallel loopback, enable, and transceiver mode. `C20_PHY_CR0_LANE2_DIG_ASIC_TX_OVRD_*` provides overrideable TX inputs for clock-ready, reset, invert, data enable, request, low-power detect, pstate, rate, width, wide-transfer alignment, PLL select, detect-RX request, flyover, nyquist data, disable, beacon, boost, vboost, TX enable, post/main/pre cursor settings, TX EQ override enable, DCC bypass, EQ-calculation bypass, DCC control range/update, asynchronous FIFO, lane/clock deskew, KR driver enable, and VREG bypass. `C20_PHY_CR0_LANE2_DIG_ASIC_TX_ASIC_*` mirrors many of those values as direct ASIC input/output status fields.

Lane 2 TX power and diagnostics follow under `C20_PHY_CR0_LANE2_DIG_TX_*`. The `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` registers describe per-power-state enable/reset/serial/data/DCC/word-clock/bleeder behavior; `TX_PWRUP_TIME_0` through `_5` describe timing fields for bring-up sequencing. `TX_CTL` and `TX_STATUS` expose general TX control/status. `TX_DCC_CTL_*` provides TX DCC differential/common-mode IDAC offsets and status. `TX_STAT_*` exposes a compact TX statistic block. `TX_CLK_ALIGN_*` exposes clock-align controls and status. `TX_LBERT_*` exposes link BERT enable/control and pattern registers. `TX_LVL_CALC_STAT` and `TX_FIFO_CTL` cover TX level calculation and FIFO behavior.

The lane 2 analog TX block is `C20_PHY_CR0_LANE2_DIG_ANA_XF_TX_*`. It contains analog TX override outputs for power, clocks, reset, serial/data/driver/PLL paths, equalization and DCC; termination-code overrides; analog DCC enable/config/calibration controls; analog DCC calibration data; TX status EQ override and status output registers; analog TX status input; and analog control registers `ANA_CREG00` through `ANA_CREG05` plus reserved CREG override fields. This block maps the digital control plane onto TX analog front-end state.

The final section starts lane 2 RX ASIC controls. `C20_PHY_CR0_LANE2_DIG_ASIC_RX_OVRD_IN_0` through `_4` and related SIGDET/VCO/EQ override registers define overrideable RX reset, invert, data-enable, request, low-power, pstate, DFE bypass, rate, width, divider clocks, CDR tracking/SSC, disable, VREG bypass, flyover, loopback selection, DCC control range/update/bypass, signal-detect thresholds/filter enable, CDR VCO config, and equalizer settings for ATT, VGA, CTLE, AFE rate/bias/VCM, and DFE taps 1-5. `RX_OVRD_OUT_0` exposes ack/adaptation/valid override output fields. The chunk ends after the start of direct RX ASIC input registers `RX_ASIC_IN_0`, `RX_ASIC_IN_1`, and the first two fields of `RX_ASIC_IN_2`.

## APIs, Types, and Functions

This chunk defines no functions, structs, enums, or runtime APIs. Its public interface is the generated macro namespace. The important contract is:

- `*_SHIFT` values are the least-significant bit positions used when packing or extracting a field.
- `*_MASK` values are the field masks in register position, almost always within a 16-bit `0x0000L` to `0xFFFFL` layout in this PHY slice.
- Register names encode instance and hierarchy: `C20_PHY_CR0`, `LANE1` or `LANE2`, digital sub-block (`DIG_RX_ADPTCTL`, `DIG_ANA_XF_RX`, `DIG_ASIC_TX`, `DIG_TX_PWRCTL`, `DIG_ANA_XF_TX`, `DIG_ASIC_RX`), register name, and field.
- Many fields are paired override value/override enable bits, for example `*_OVRD_VAL` with `*_OVRD_EN` or a named control with a matching `*_OVRD_EN`.
- Reserved fields are explicitly defined and must still be masked correctly during read-modify-write operations, even though software should generally avoid depending on their values.

The companion address definitions live in `dcn_3_2_0_offset.h`, where corresponding `ixC20_PHY_CR0_LANE*_*` register addresses are defined. Driver-side register helpers conventionally combine an address macro from the offset header with these shift/mask macros.

## Control Flow

There is no executable control flow in the header. Runtime control flow appears in consumers that use the masks for MMIO register programming, status polling, and debug reads.

The control-flow-sensitive behaviors represented by this chunk include RX adaptation sequences, where software or firmware can reset specific adaptation loops, wait for `ASM1_DONE`/status bits, inspect DFE/CTLE/VGA/ATT codes, and potentially override slicer, VDAC, DCC, and equalizer values. TX bring-up is represented by lane 2 TX ASIC and power-state fields: clock-ready/reset/data-enable/request/pstate/rate/width values feed power-state and link-training sequencing, while `TX_PWRUP_TIME_*` fields affect timing between analog enable, reset release, serial enable, data enable, word clock, DCC, and related transitions.

Diagnostic and calibration control flow is also implied. RX/TX statistic registers define sample/count/match/start-stop behavior; IQC and DCC fields expose calibration control/status; LBERT pattern fields enable link bit-error test flows; clock-align status fields support polling or validation after alignment control writes; and analog status fields expose readback points for CDR, signal detect, calibration, termination, equalization, and loopback state.

## State and Persistence

All state described here is device register state, not kernel-owned persistent data. Writes through these masks persist in the GPU PHY register file until changed by software, firmware, reset, power-gating, link retraining, or hardware side effects. Status and counter fields may be read-only, latched, shadowed, clear-on-write, sticky, or dynamically updated by hardware; this `_sh_mask` header does not encode access type or reset value, so users must rely on the register specification, generated offset/default headers where available, and existing driver access patterns.

The chunk contains many override-enable bits. Those fields are especially stateful: enabling an override can force analog or ASIC-facing behavior away from normal hardware/firmware control. Incorrect persistence across modesets, suspend/resume, or link retraining could leave a lane stuck in forced reset, wrong power state, bad equalization, DCC bypass, loopback, disabled CDR tracking, or an unintended TX/RX rate/width.

Statistic, calibration, and status registers are also stateful. Sample counters, statistic counters, calibration-done/status fields, and shadow registers represent sampled hardware state at a point in time and can be stale or cleared depending on the surrounding control bits.

## Dependencies and Integration Points

The header itself depends only on the C preprocessor and the generated include guard for the full file. Practically, it is coupled to the matching DCN 3.2.0 register address header and to AMDGPU display register-access helpers that expect the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` naming scheme.

The full `dcn_3_2_0_sh_mask.h` header is included by DCN32 display components including DMUB support, IRQ service, GPIO factory/translation, resource construction, and clock management. Local source search did not find direct C references to the exact C20 lane macros in this chunk outside generated register headers; these fields appear to be a generated low-level PHY surface available to DCN32/DCIO code, firmware-facing diagnostics, or future/manual debug paths rather than actively referenced by high-level display logic in this tree.

Integration points represented by the field names include DisplayPort/PHY link training, lane power sequencing, CDR/VCO configuration, RX equalization/adaptation, TX equalization and cursor programming, DCC calibration, signal detect thresholds, analog front-end trim and calibration, loopback, link BERT diagnostics, statistic/counter capture, clock alignment, and ASIC-to-PHY handshake signals such as ack, request, valid, adaptation status, and calibration status.

The same macro families also appear in adjacent generated hardware-generation headers such as `dpcs_4_2_3_sh_mask.h`, which is useful for cross-generation comparison but dangerous as a source for copy/paste assumptions because generated layouts can diverge by block version or lane family.

## Risks

The primary risk is silent PHY misprogramming if a shift or mask does not match the silicon register layout. These registers control link bring-up, analog power, CDR, equalization, calibration, DCC, clocking, and loopback; a one-bit error can force the wrong override, corrupt an adjacent field, misread a status bit, or leave a lane unable to train.

Override pairs are particularly hazardous. Setting an override value without its enable bit has no intended effect; setting an enable bit with a stale or wrong value can force bad hardware state. Because many registers pack multiple override value/enable pairs in one 16-bit word, read-modify-write code must preserve unrelated fields and reserved bits correctly.

Repeated lane and register families increase generator and maintenance risk. Lane 1 RX analog definitions and lane 2 TX/RX definitions share naming patterns with lane 0/1/2/3 elsewhere, but not every field width or bit position is guaranteed to be identical. The chunk also crosses a lane boundary and ends mid-register family, so any final file-level analysis must merge adjacent chunks before making complete statements about lane 2 RX ASIC input coverage.

Reserved fields are explicit masks in this generated header. Treating reserved bits as scratch space, clearing them blindly, or assuming readback values are stable can break across stepping, firmware, or reset domains.

There is also a diagnostic risk: many fields look useful for debug, but this header does not say whether a register is safe to write during an active link, whether writes require a quiesced lane, or whether firmware owns the field. Consumers need the hardware programming sequence, not just the mask.

## Test Signals

Validation for code that depends on these masks should include compile coverage of DCN 3.2 paths so macro spelling or generated-name drift fails early. Runtime validation requires DCN 3.2-class hardware or a register-level emulator/trace environment because these fields describe MMIO state.

Useful hardware signals include successful DP/HDMI link bring-up across lane rates and widths, hotplug and retraining stability, clean suspend/resume and power-gating restoration, absence of unexpected PHY calibration failures, and stable modesets after link disable/enable cycles. RX-specific checks should inspect adaptation completion/status, DFE/CTLE/VGA/ATT codes, signal-detect behavior, CDR tracking/SSC behavior, DCC status, and error/statistic counters. TX-specific checks should verify pstate sequencing, clock-ready/ack handshakes, DCC offsets/status, cursor/EQ programming, FIFO and clock-align status, and LBERT pattern operation where supported.

For generated-header integrity, compare this chunk against the vendor register specification and the matching `dcn_3_2_0_offset.h` addresses for the same `C20_PHY_CR0_LANE1` and `LANE2` registers. Cross-checking analogous lane/register families in adjacent chunks can catch lane-index copy errors, but final validation should prefer the DCN 3.2 register source over neighboring generation headers.
