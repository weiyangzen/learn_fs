# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 95565-97960

## Scope

This chunk is a generated AMD DCN 3.2.0 register-field shift/mask header slice for the C20 PHY CR1 lane 1 digital/analog register namespace. It contains C preprocessor constants only: `_SHIFT` macros for bit positions, `_MASK` macros for register-positioned masks, and `//<REGISTER>` comments that group fields by hardware register. There are no C functions, structs, enums, local variables, branches, loops, allocations, locks, or software persistence in this range.

The requested range contains 2,167 `#define` entries: 1,080 shift definitions and 1,087 mask definitions across roughly 230 register names. It starts in the middle of `C20_PHY_CR1_LANE1_DIG_ASIC_TX_ASIC_IN_0`, where only the tail mask definitions are visible, then covers complete TX, RX, adaptation, status, calibration, and analog-transfer register groups for lane 1. It ends at the beginning of `C20_PHY_CR1_LANE1_DIG_ANA_XF_RX_ANA_IQ`, after only `SENSE_EN__SHIFT` and `SENSE_SEL__SHIFT`; the remaining shifts and masks for that register continue in the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph filesystem code.

## Purpose

The purpose of this header range is to describe the bit layout for C20 PHY lane 1 registers used by DCN/DPCS display link hardware. The generated constants are the mask/shift half of a hardware ABI: matching offset headers provide register addresses, while this file provides the field packing needed by MMIO register helpers and generated register tables.

The covered lane-1 hardware surface includes:

- ASIC-facing TX control and status, including clock ready, reset, inversion, data enable, request, low-power state, pstate, link rate, width, MPLL selection, RX detect request/result, beacon, boost, main/pre/post cursor, and calibration status fields.
- TX power state and power-up sequencing, including P0, P0S, P1, and P2 enable/reset/data/DCC/word-clock controls plus timing registers for refgen, clock, VCM hold, serial, data, DCC, TX ack, and VBoost sequencing.
- TX diagnostics and calibration, including TX DCC IDAC offsets, DCC status, statistic/load/sample/count controls, clock alignment status, loopback BERT controls, FIFO controls, and analog-transfer TX override/status/equalization fields.
- RX ASIC override/input/output fields, including reset, enable, pstate, rate/width, DFE/VGA/CTLE/AFE controls, signal detect, CDR/VCO, equalization, misc overrides, and status outputs.
- RX power, VCO calibration, CDR, DPLL, adaptation, statistic, IQ calibration, and analog-transfer fields, including RX P0/P0S/P1/P2 controls, VCO calibration timings/status, LBERT error count, CDR lock/rate/frequency controls, DPLL frequency bounds, adaptation configuration and reset controls, ATT/VGA/CTLE/DFE status, DFE tap/VDAC/slicer fields, DCC offsets, fast flags, SSM controls, match/stat counters, and IQC reset/config/status fields.
- RX analog-transfer controls for power, signal detect calibration, VCO overrides, calibration mux/DAC/rtrim controls, AFE overrides, scope selection, slicer control, and the start of RX analog IQ controls.

This is generated data rather than executable logic, but it is security- and stability-relevant for display bring-up. A bad bit mask can compile cleanly while causing link training failures, stuck PHY power transitions, bad equalization, incorrect calibration, lost RX detect, or destructive analog override programming.

## Important APIs, Types, And Macros

There are no callable APIs or C types in this chunk. The exported interface is the generated AMD register-field naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw mask with the field already positioned inside the register.
- `//<REGISTER>` comments identify the register whose field constants follow.

Important register families in this chunk are:

- `C20_PHY_CR1_LANE1_DIG_ASIC_TX_ASIC_IN_0..3`, `OUT`, and `OVRD_MISC` for the ASIC-visible TX lane interface, RX-detect handshake, transmit equalization, beacon/boost, DCC range, and miscellaneous override values.
- `C20_PHY_CR1_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` for per-power-state TX analog/digital enable recipes. Each pstate exposes fields such as `ANA_REFGEN_EN`, `ANA_VCM_HOLD`, `ANA_CLK_EN`, `ANA_RESET`, `ANA_SERIAL_EN`, `DIG_CLK_EN`, `DATA_EN`, `ALLOW_RXDET`, `ALLOW_VBOOST`, `ANA_DCC_EN`, VREG bleeders, and `ANA_WORD_CLK_EN`.
- `C20_PHY_CR1_LANE1_DIG_TX_PWRCTL_TX_PWRUP_TIME_0..5`, `TX_CTL`, and `TX_STATUS` for TX power-up delays, fast timing selectors, TX pstate request, manual power control, active pstate, request state, ACK timeout, and busy flags.
- `C20_PHY_CR1_LANE1_DIG_TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL` for TX DCC calibration, stat sampling/counting, clock alignment, LBERT patterns, calibration levels, and FIFO pointer/load behavior.
- `C20_PHY_CR1_LANE1_DIG_ANA_XF_TX_*` for analog-transfer TX overrides and readback, including TX power/control overrides, term-code overrides, DCC enable/config/calibration, equalization override/status, and TX analog CREG registers.
- `C20_PHY_CR1_LANE1_DIG_ASIC_RX_OVRD_*`, `RX_ASIC_IN_*`, `RX_CDR_VCO_ASIC_IN`, `RX_EQ_ASIC_IN_*`, `RX_ASIC_OUT_0`, `RX_OVRD_MISC`, and additional `RX_OVRD_EQ_IN_5..11` registers for RX-side override, ASIC input, equalizer, CDR/VCO, signal-detect, and status interfaces.
- `C20_PHY_CR1_LANE1_DIG_RX_PWRCTL_*` for RX P0/P0S/P1/P2 state recipes, RX power-up timing, RX pstate request/control, active pstate, request state, ACK timeout, and busy state.
- `C20_PHY_CR1_LANE1_DIG_RX_VCOCAL_*`, `RX_CDR_*`, `RX_DPLL_*`, and `RX_LBERT_*` for receiver VCO calibration, CDR tuning/status, DPLL frequency programming/bounds, and RX loopback BERT error reporting.
- `C20_PHY_CR1_LANE1_DIG_RX_ADPTCTL_*` for adaptation control and readback, including DFE, VGA, CTLE, attenuation, slicer thresholds, DCC offsets, fast flags, adaptation resets, and SSM final-code status.
- `C20_PHY_CR1_LANE1_DIG_RX_STAT_*` for match masks, match controls, stat controls, sample counts, stat counters, load values, counter shadowing, and stat-stop control.
- `C20_PHY_CR1_LANE1_DIG_RX_IQC_CTL_*` and `C20_PHY_CR1_LANE1_DIG_ANA_XF_RX_*` for RX IQ calibration and RX analog-transfer control, including power overrides, signal-detect high/low-frequency calibration, CDR VCO override, calibration mux/DAC/rtrim controls, AFE/CTLE/VGA overrides, scope controls, slicer controls, and the first two RX analog IQ shift definitions.

## Control Flow

This header has no local control flow. Runtime flow is created by AMDGPU display code that includes generated offset and shift/mask headers, then uses token-pasting register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SRI`, `SRI_IX`, `SRI_ARR`, `LE_SF`, and `SE_SF` patterns.

Typical runtime usage is:

1. Link encoder, DPCS/PHY, DMUB, GPIO, IRQ, or hardware sequencing code selects a link encoder, PHY lane, or related MMIO block instance.
2. Generated register lists bind a register address from an offset header with field masks/shifts from this header or a matching DPCS generation header.
3. Register helpers pack values into the field using the `__SHIFT` and `_MASK` pair, issue an MMIO read/modify/write, poll status, or decode readback values.
4. Hardware applies the lane operation: transmitter power sequencing, RX-detect handshake, link-rate/width selection, equalization, DCC/VCO/CDR calibration, adaptation, loopback BERT, stat capture, or analog override/readback.

The sequencing rules are intentionally not represented here. For example, this chunk names fields for pstate requests, ACK timeouts, calibration enables, adaptation resets, self-clearing controls, override enables, status counters, and analog CREG controls, but the header does not encode which fields are safe to write together, which require delays, which are write-one-to-clear, or which are volatile readback. Those constraints live in hardware specifications and in the display/link encoder code that consumes the generated definitions.

## State And Persistence Behavior

The file itself stores no software state. It describes MMIO-backed hardware state whose lifetime is controlled by display hardware, link training, modesets, hotplug, suspend/resume, runtime power management, firmware interactions, and hardware reset.

Configuration-like or latched hardware state represented here includes TX/RX pstate recipes, TX/RX power-up timings, TX/RX pstate requests, link rate/width fields, MPLL selection, TX cursor/pre/post settings, VBoost and beacon control, analog override values/enables, DCC calibration ranges and offsets, VCO/CDR/DPLL tuning fields, RX adaptation configuration, RX slicer/VDAC settings, scope selection, and calibration mux/DAC/rtrim controls.

Volatile readback or diagnostic state includes TX/RX ACK/result/status fields, TX/RX busy and active-pstate fields, DCC and VCO calibration status, CDR status, LBERT error counts, clock-alignment status, statistic counters, sample counters, DFE tap status, ATT/VGA/CTLE status, SSM final codes, RX fast flags, IQC status, and analog status/readback fields.

Side-effecting or sequencing-sensitive fields include reset bits, pstate requests, power-control modes, calibration start/enables, DCC update enables, adaptation resets, statistic load/stop controls, ACK/timeout controls, override enables, and self-clearing or clocked adjustment controls. Treating these as ordinary persistent booleans can leave a PHY lane in the wrong power state, clear/overwrite a latched diagnostic, retrigger calibration unexpectedly, or wedge link training.

## Dependencies And Integration Points

This chunk depends on generated register-address metadata from matching ASIC register offset headers. The same C20 PHY CR1 lane naming pattern appears in DPCS register databases as well as this DCN 3.2.0 mask header, so the shift/mask definitions must remain synchronized with the corresponding offset source for the specific ASIC family.

Relevant integration points visible in the source tree include:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, `dc/gpio/dcn32/*`, `dc/irq/dcn32/irq_service_dcn32.c`, and `dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, which include `dcn/dcn_3_2_0_offset.h` and `dcn/dcn_3_2_0_sh_mask.h` for DCN 3.2 generated register access.
- DPCS/link encoder register-list infrastructure in `drivers/gpu/drm/amd/display/dc/dio/*_link_encoder.h` and resource construction in `drivers/gpu/drm/amd/display/dc/resource/*`, which uses generated mask/shift macros to build link encoder and PHY register tables.
- Link encoder and HPO DP link encoder code that programs PHY/lane status and control fields through `REG_GET` and `REG_UPDATE` helpers.
- Hardware sequencing and link training paths that depend on TX/RX power, MPLL, rate/width, equalization, DCC/VCO/CDR calibration, RX adaptation, and diagnostic status fields to bring up DisplayPort/HDMI/USB-C PHY lanes.
- Validation/debug flows that rely on LBERT, stat counters, DCC/VCO/CDR status, adaptation status, and analog scope/readback fields to diagnose PHY and link failures.

Because this range is generated, the usual consumer code generally does not hand-code every symbol in this chunk. Instead, it consumes logical register lists and field lists that expand into these constants. Missing names fail at build time; wrong numeric values, swapped lane prefixes, or partial-register boundary mistakes often compile and surface only as hardware behavior regressions.

## Risks And Edge Cases

- Boundary incompleteness matters for chunk-level interpretation. The chunk starts with only the tail masks for `TX_ASIC_IN_0` and ends with only the first two shifts for `RX_ANA_IQ`; neighboring chunks are needed for complete per-register coverage.
- Lane and instance repetition is error-prone. C20 PHY definitions repeat across CRs, lanes, pipes, TX/RX sides, and ASIC/DIG/ANA transfer namespaces. A lane-0/lane-1 or TX/RX prefix mix-up can compile but program the wrong lane or wrong direction.
- Pstate fields are sequencing-sensitive. Incorrect masks for `TX_P*_` or `RX_P*_` recipes, pstate requests, ACK timeout, active pstate, or busy fields can break power-up/down, hotplug, resume, or link retraining.
- Equalization and analog fields have protocol-visible effects. Incorrect `TX_MAIN_CURSOR`, `TX_PRE_CURSOR`, `TX_POST_CURSOR`, RX VGA/CTLE/DFE/AFE, VDAC, slicer, or signal-detect masks can cause marginal links, intermittent monitor failures, or failures only at high link rates.
- Calibration controls are high-risk. DCC, VCO, CDR, IQC, rtrim, and DAC calibration fields often interact with internal analog state machines. Wrong masks may trigger calibration at the wrong time, leave override mode enabled, or hide calibration failure status.
- Status, counter, and statistic fields are not interchangeable with controls. Bad masks in stat/load/sample/count, LBERT, CDR status, VCO status, or adaptation status can mislead diagnostics even if the display appears functional.
- Reserved-field masks must not be used as writable payloads. Many registers expose explicit `RESERVED_*` masks. Runtime code should preserve reserved bits with read/modify/write patterns unless hardware documentation says otherwise.
- Partial generated-header drift is hard to detect. If this mask header and the corresponding offset header come from different register databases, all macros can still compile while MMIO writes target valid addresses with invalid bit layout.

## Test Signals

Useful validation signals are mostly build, hardware, and integration oriented:

- Build coverage: DCN 3.2 and DPCS/link encoder code compiles with no missing `__SHIFT` or `_MASK` symbols in generated register lists.
- Display link smoke tests: monitors light up on links that use the C20 PHY path, including hotplug, modeset, suspend/resume, and runtime power-management cycles.
- Link-training coverage: DisplayPort lane count, rate selection, width programming, MPLL selection, TX EQ cursors, RX detect, and training retries behave correctly across supported rates.
- Power sequencing coverage: TX/RX pstate transitions complete, active-pstate and busy/status fields settle, and ACK timeout fields do not indicate stuck state during hotplug, blanking, or resume.
- Calibration coverage: DCC, VCO, CDR, IQC, signal detect, and RX adaptation status fields indicate completion/sane values, with no unexpected calibration loops or override leakage.
- Diagnostic coverage: LBERT, stat counters, clock alignment, CDR/DPLL status, DFE/VGA/CTLE status, SSM final code, and analog scope/readback fields can be read without wedging the lane.
- Negative-path coverage: invalid or marginal cables/panels surface expected RX detect, CDR, LBERT, adaptation, or timeout diagnostics rather than hangs or silent success.
- Regression comparison: generated masks should match the authoritative register database and neighboring DPCS/DCN generation headers for equivalent C20 PHY lane-1 fields where the hardware block is shared.
