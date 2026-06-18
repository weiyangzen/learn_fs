# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 129729-132118

## Purpose

This chunk is generated AMD DCN 4.1.0 register-field metadata for `DPCSSYS_CR3` lane hardware. It contains preprocessor constants only: each field is represented by a `...__SHIFT` bit offset and a matching `..._MASK` value for use by AMDGPU display register helpers. There are no executable functions, structs, branches, allocation paths, locks, or direct MMIO accesses in this range.

The range covers the tail of `DPCSSYS_CR3_LANE1` analog/digital PHY definitions, then the beginning and most of the `DPCSSYS_CR3_LANE2` lane block. It starts inside `DPCSSYS_CR3_LANE1_DIG_ANA_STATUS_0`: the first three status shifts are immediately before the chunk, while the remaining shifts and all masks for that register are included here. It ends inside `DPCSSYS_CR3_LANE2_ANA_TX_OVRD_MEAS`: only the first seven shifts are included, and the rest of that register continues in the following chunk.

Although the repository path is under a local `ceph-client` source mirror, this header belongs to AMDGPU display hardware support, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for extracting or encoding a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, clearing, or preserving that field.

This chunk has 2,180 `#define` lines: 1,092 shift macros and 1,088 mask macros across 211 register names. The shift/mask imbalance is due to the chunk boundaries starting and ending inside register definitions.

Major covered register families:

- `DPCSSYS_CR3_LANE1_DIG_ANA_*` and `DPCSSYS_CR3_LANE1_ANA_*`: lane 1 analog status, RX termination/PWM/signal-detect overrides, TX DCC DAC and fast-start/loopback controls, TX measurement and power overrides, alternate bus/ATB controls, TX termination/DCC/clock/misc/mux/regulator fields, and RX clock, CDR/deserializer, slicer, power, squelch, calibration, ATB measurement, VDAC range, and regulator controls.
- `DPCSSYS_CR3_LANE2_DIG_ASIC_*`: lane 2 digital ASIC override inputs/outputs and live ASIC mirrors for TX/RX request, pstate, rate, width, data enable, clock ready, detect-RX, inversion, low-power detect, PMA FIFO, M-PHY mode, reset, boost settings, transceiver mode, CDR, VCO, equalizer, loopback, and acknowledgement/status paths.
- `DPCSSYS_CR3_LANE2_DIG_TX_PWRCTL_*` and `DPCSSYS_CR3_LANE2_DIG_RX_PWRCTL_*`: TX/RX pstate definitions and power-up timing fields for analog clock/data/serial/deserializer, DCC, VCO, AFE, CDR, and digital-clock sequencing, plus DCC DAC bank, range, selector, acknowledgement, and address fields.
- `DPCSSYS_CR3_LANE2_DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, and `DIG_RX_ADPTCTL_*`: VCO calibration controls/status, CDR/DPLL tuning, DPLL frequency bounds, receiver adaptation configuration, attenuation/VGA/CTLE/DFE status, slicer controls, reset controls, and DAC selector fields.
- `DPCSSYS_CR3_LANE2_DIG_RX_STAT_*`: receiver statistic load values, data masks, match controls, counter/sample controls, statistic counters, calibration compare clock controls, and statistic stop fields.
- `DPCSSYS_CR3_LANE2_DIG_MPHY_RX_*`, `DPCSSYS_CR3_LANE2_DIG_ANA_*`, and the beginning of `DPCSSYS_CR3_LANE2_ANA_TX_OVRD_MEAS`: M-PHY RX PWM/termination timing, digital analog override outputs, TX equalization override outputs, RX power/VCO/calibration/DAC/AFE/scope/slicer controls, analog status, RX termination/signal-detect overrides, TX DCC overrides, and initial analog TX measurement override fields.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this header with the matching DCN 4.1.0 offset header, builds register-field tables from the symbolic names, and then calls register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, and wait/poll variants.

The hardware flow represented by the fields is roughly:

1. Select a CR3 lane and register instance through the consuming register table.
2. Program or clear override fields for request, pstate, rate, width, data enable, TX cursors, RX CDR/VCO, equalizer, clocking, inversion, loopback, or reset.
3. Program TX/RX power-state and timing fields before lane bring-up or low-power entry.
4. Start or update calibration/adaptation operations such as DCC, VCO calibration, CDR tuning, DPLL bounds, CTLE/VGA/DFE adaptation, slicer adjustment, or statistic sampling.
5. Poll or read status fields such as acknowledgement, done, sync, calibration result, VCO counters, error status, statistic counters, and analog measurement outputs.

The macros themselves do not enforce sequencing, access type, or write semantics. Those rules live in the display/link/PHY code and the DCN 4.1.0 hardware programming specification.

## State And Persistence Behavior

The file stores no mutable software state and persists nothing to disk. It describes hardware-backed state in CR3 lane registers.

State represented by this chunk includes:

- Override state: value fields paired with `*_OVRD_EN` bits can force lane request, pstate, rate, width, clock readiness, data enable, cursor/equalization settings, reset, transceiver mode, M-PHY mode, termination, signal detect, PWM, RX power, VCO, calibration, DCC, and loopback controls.
- Power state: TX and RX `PSTATE_P0`, `P0S`, `P1`, and `P2` register fields describe per-state enables and resets for analog and digital lane blocks.
- Calibration and adaptation state: VCO, CDR, DPLL, DCC, CTLE, VGA, attenuation, DFE, slicer, VDAC, ATB, and calibration compare fields contain configuration, counters, done bits, error indicators, mux selectors, and measurement readbacks.
- Diagnostic and test state: LBERT, loopback, OCLA, RX statistics, match masks, sample counters, ATB routing, scope data, and analog status fields expose lane validation and debug information.

Persistence is limited to hardware register lifetime. Values may be reset by GPU reset, display engine reset, lane reset, PHY reinitialization, link retraining, modeset, suspend/resume, or display/audio/PHY power gating. Status fields may be read-only, sticky, self-clearing, write-one-to-clear, or invalid when the relevant clock/power domains are off; this generated header does not encode those semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 4.1.0 register database and must remain synchronized with the matching address/base-index definitions in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`.

Integration points include:

- AMD display register-helper infrastructure that token-pastes register and field names into offset, shift, and mask lookups.
- DCN 4.1.0/4.0.1 display resource, link encoder, PHY, clock, DMUB, and diagnostic code that accesses DPCS/DPCSSYS lane registers.
- DisplayPort, HDMI, and USB-C/PHY programming paths that need lane power sequencing, link training, transmitter cursor/equalization programming, receiver CDR/DPLL/VCO calibration, and low-power transitions.
- Debug and validation tooling that reads LBERT, OCLA, ATB, RX statistics, scope, VCO counters, CDR status, adaptation status, and analog measurement fields.

The critical ABI is the macro name itself. Consumers that refer to a field like `DPCSSYS_CR3_LANE2_DIG_RX_ADPTCTL_CTLE_STATUS__ASM1_DONE` rely on this header for the exact bit location and mask, while the paired offset header supplies the register address.

## Risks And Edge Cases

- These are untyped preprocessor constants. An incorrect shift or mask can compile cleanly while modifying adjacent PHY bits in the same 16-bit register.
- This file is generated metadata. Manual edits risk divergence from AMD's register database, the paired offset header, firmware expectations, and silicon documentation.
- Lane instances are highly repetitive. A lane-prefix or copy error may affect only CR3 lane 1 or lane 2 and can be missed by tests that use different CR/lane routing.
- Override-enable fields are high risk. Leaving `*_OVRD_EN` asserted can pin hardware state and defeat normal link training, power management, calibration, or reset sequencing.
- Analog fields such as termination, DCC DAC, regulator trim, VCO/CDR controls, slicer/VDAC, CTLE/VGA/DFE, ATB, and signal-detect thresholds are silicon-sensitive and may fail only for certain boards, cables, link rates, temperatures, or sinks.
- Status, acknowledge, reset, self-clear-disable, load, update, and statistic-stop fields can have specialized write semantics not visible in the macro names. Using the correct mask with the wrong access pattern can wedge calibration or lose events.
- The chunk boundaries split two register definitions: full reasoning about `LANE1_DIG_ANA_STATUS_0` requires the immediately preceding lines, and full reasoning about `LANE2_ANA_TX_OVRD_MEAS` requires the following chunk.
- High-bit masks such as `0x8000L` should be handled with unsigned-safe register math by consumers.

## Test Signals

Useful validation for changes affecting this chunk includes:

- Build AMDGPU display support with DCN 4.1.0 enabled. Missing or renamed field macros should fail in register-table construction or link/PHY code.
- Mechanically check that each complete register field in the range has one `__SHIFT` and one `_MASK`, allowing the expected boundary exceptions for `LANE1_DIG_ANA_STATUS_0` and `LANE2_ANA_TX_OVRD_MEAS`.
- Diff this slice against AMD's authoritative DCN 4.1.0 register database and adjacent generated ASIC headers where lane layout compatibility is expected.
- Exercise DP/HDMI link bring-up on CR3-backed routes across lane counts, rates, bit depths, hotplug, modeset, suspend/resume, and GPU reset.
- Inspect link-training diagnostics for CDR lock, DPLL frequency bounds, VCO calibration done/correct/up status, CTLE/VGA/DFE adaptation done bits, slicer/VDAC values, and RX statistic counters.
- Exercise power-state transitions through P0/P0S/P1/P2, TX/RX power-up timings, DCC DAC request/ack paths, low-power entry/exit, fast-start, and lane reset.
- Validate debug paths such as TX/RX loopback, LBERT error count and overflow, OCLA, ATB measurement routing, RX scope data, pattern matching, and statistic stop/sample behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_LANE1_DIG_ANA_STATUS_0`, including `TX_ANA_CLK_SHIFT_ACK`, `TX_ANA_RXDETP_RESULT`, and `TX_ANA_RXDETM_RESULT` shift definitions. This chunk owns the rest of the lane 1 analog tail and most of the lane 2 digital/analog metadata through the first part of `DPCSSYS_CR3_LANE2_ANA_TX_OVRD_MEAS`. The next chunk owns the remaining `LANE2_ANA_TX_OVRD_MEAS` shifts and masks plus subsequent lane 2 analog TX/RX register families. The final per-file report should reconcile these boundaries before making complete claims about all `DPCSSYS_CR3` lane definitions.
