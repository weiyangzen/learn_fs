# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 165985-168379

## Chunk Scope

This chunk is a generated AMD DCN 3.2.0 register shift/mask header segment. It contains C preprocessor constants only: `#define` entries for hardware bitfield low-bit positions (`__SHIFT`) and raw bit masks (`_MASK`), plus generated `//REGISTER_NAME` comments that group fields by hardware register. It has no executable functions, structs, enums, branches, locks, allocations, or direct MMIO operations.

The requested range contains 2,395 source lines, 2,168 macro definitions, and 227 register-group comments. It starts in the tail of `C20_PHY_CR3_LANE2_DIG_ASIC_RX_OVRD_VCO_IN`, covers a large part of the CR3 lane2 RX PHY register layout, crosses into CR3 lane3 ASIC/TX layout, and ends after the two shift definitions for `C20_PHY_CR3_LANE3_DIG_TX_FIFO_CTL`. The source tree path is under a local `ceph-client` mirror, but this content is AMDGPU display/DCN hardware metadata rather than distributed filesystem logic.

## Purpose

The purpose of this header region is to publish symbolic bit layouts for C20 PHY CR3 lane2 receive and lane3 transmit registers in the DCN 3.2 ASIC register namespace. AMD display code pairs these constants with register offsets from `dcn_3_2_0_offset.h` and token-pasting register helpers to build field-aware MMIO or indirect-register reads and writes.

At the hardware level, this chunk describes:

- Lane2 RX ASIC-facing override/input/output fields for CDR VCO configuration, equalization values, adaptation status, reset/request/low-power/rate/width controls, signal-detect thresholds, DFE bypass, and RX DCC range.
- Lane2 RX power-control, VCO calibration, CDR/DPLL, adaptation, statistics, IQ calibration, analog crossover, slicer, loopback, CREG, and status/readback fields.
- Lane3 ASIC-facing TX override and input/status fields for lane enable/reset, TX pstate/source, TX reset, USB/alternate-mode symbols, idle/low-power/loopback, reference selection, SSC, CDR/regulator, muxing, pattern, and power-source controls.
- Lane3 TX power-state, power-up timing, DCC offset/status, statistics, clock-alignment, LBERT pattern/test, level-calculation, and FIFO-control fields.

The macros do not encode register addresses, reset values, access types, or legal sequencing. They only provide field positions and masks used by generated register access layers and by low-level display PHY code.

## Important APIs, Types, And Macros

This range exports no callable APIs or C types. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the in-register mask for that field.
- `//<REGISTER>` comments preserve the generated grouping and register identity.

Major macro groups in this chunk include:

- `C20_PHY_CR3_LANE2_DIG_ASIC_RX_*`: RX ASIC interface and override registers. These include EQ override fields such as `EQ_ATT_LVL`, `EQ_VGA_GAIN`, `EQ_CTLE_BOOST`, `EQ_CTLE_POLE`, DFE tap overrides, IQ and AFE bias/zero/offset overrides, `ACK`, `VALID`, `ADAPT_STS`, `RESET`, `INVERT`, `DATA_EN`, `REQ`, `LPD`, `PSTATE`, `RATE`, `WIDTH`, CDR tracking/SSC, signal-detect threshold, VCO load/config, and RX DCC range fields.
- `C20_PHY_CR3_LANE2_DIG_RX_PWRCTL_*`: lane2 RX pstate and power timing fields. P0/P0S/P1/P2 layouts control AFE, clock/regulator, deserializer, CDR, VCO frequency/reset/calibration, continuous calibration, digital clocks, DFE, bypass slicer, VCO power, and DCC. Timing/control/status registers define RX power-up wait fields, reset/request state, current pstate, and requested pstate.
- `C20_PHY_CR3_LANE2_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: VCO calibration controls, completion/status, calibration counters, CDR divide/config/frequency lock, CDR enable/update behavior, DPLL frequency and frequency-bound fields.
- `C20_PHY_CR3_LANE2_DIG_RX_ADPTCTL_*`: adaptation configuration and telemetry. These fields cover adaptation disable/request/ACK behavior, continuous/standalone enablement, timer/wait controls, ATT/VGA/CTLE/DFE update enables, adaptation status, DFE tap1-5 status, even/odd/high/low VDAC offsets, slicer controls, DCC IDAC offsets, fast flags, SSM configuration/final code, adaptation reset, and additional adaptation configuration words.
- `C20_PHY_CR3_LANE2_DIG_RX_STAT_*` and `RX_IQC_CTL_*`: RX statistics, match masks, sample counters, statistic counters, shadowed counter selection, comparator-clock controls, statistic stop, IQ reset/adjustment configuration, and IQ calibration status.
- `C20_PHY_CR3_LANE2_DIG_ANA_XF_RX_*`: digital-to-analog RX crossover metadata. This includes analog override outputs for reset/clock/data/refgen/VCO paths, signal-detect calibration, VCO override outputs, DAC and DCC calibration controls, AFE override inputs, scope/slicer/IQ controls, IQC bypass/data controls, loopback, update/sample selection, termination-code overrides, analog status in/out, and raw analog CREG payload/override fields.
- `C20_PHY_CR3_LANE3_DIG_ASIC_*`: lane3 TX ASIC-facing override and non-overridden input/status registers. These define value plus override-enable pairs for lane enable, reset, pstate, power source, TX reset, USB/PCS symbols, idle and low-power controls, raw data/status selects, LBERT, pattern mode, mux select, alternate PCS grant, data-bus enable, voltage boost, loopback, RX detect, reference selection, SSC, CDR/regulator clocks, PLL/power-source selection, and TX output handshake/status.
- `C20_PHY_CR3_LANE3_DIG_TX_PWRCTL_*`, `TX_DCC_CTL_*`, `TX_STAT_*`, `TX_CLK_ALIGN_*`, `TX_LBERT_*`, `TX_LVL_CALC_STAT`, and `TX_FIFO_CTL`: lane3 TX pstate and power-up timing fields, DCC differential/common-mode IDAC offsets and FSM status, statistic load/control/sample/counter fields, clock-alignment startup/retrigger/status fields, LBERT mode/error/pattern fields, TX calibration code status, and the beginning of TX FIFO read-pointer/bypass controls.

Most visible registers are 16-bit layouts. Many include explicit `RESERVED_*` fields; those masks are part of the generated contract because read/modify/write helpers must preserve reserved bits unless hardware documentation says otherwise.

## Control Flow

There is no runtime control flow in this header. Its effective flow is compile-time and table-driven:

1. DCN 3.2 display code includes the generated offset header and this shift/mask header.
2. Register-list and field-list macros concatenate register and field names into symbols from this file.
3. Helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` use the constants when manipulating hardware registers.
4. The actual ordering is implemented by display, DMUB, PHY, and link-training code, plus hardware/firmware state machines.

The source order is generated register order, not an execution sequence. Consumers must still sequence RX reset/request/ACK flows, pstate/rate/width programming, CDR/VCO/DPLL setup, adaptation requests, statistics capture, analog overrides, TX pstate transitions, DCC calibration, clock alignment, LBERT test programming, and FIFO changes according to the hardware programming model.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state:

- Lane2 RX control state for reset, invert, data enable, request, low-power detect, pstate, rate, width, DFE bypass, CDR tracking/SSC, signal detect, VCO/DPLL/CDR configuration, DCC range, and RX misc overrides.
- Lane2 RX equalization/adaptation state for ATT/VGA/CTLE/DFE taps, IQ, AFE bias and zero, per-slicer VDAC offsets, DFE tap1 offset banks, update enables, adaptation reset, SSM settings, adaptation status, and fast flags.
- Lane2 RX calibration/status state for VCO calibration, CDR lock, statistics counters, match controls, IQ calibration, analog signal-detect calibration, DAC/DCC calibration, slicer controls, analog CREG payloads, loopback, termination-code overrides, and analog status in/out.
- Lane3 TX ASIC and power state for lane and TX resets, pstate/source selection, USB/PCS/pattern/mux controls, reference and SSC selection, voltage boost, loopback/RX detect, PLL/power-source selection, TX pstate contents, power-up timing, DCC offsets, statistic counters, clock alignment, LBERT pattern words, calibration code, and FIFO controls.

Persistence and side effects are hardware-defined. Some fields are stable configuration bits that may persist until reprogramming, link retraining, power gating, suspend/resume, firmware restore, or ASIC reset. Others are status, sticky event, self-clearing trigger, write-one-to-clear, read-only telemetry, firmware-owned scratch/status, or hardware-owned calibration state. This generated header does not distinguish those access types.

## Dependencies And Integration Points

This chunk must stay synchronized with `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`, which supplies the matching register addresses or indices. A correct field mask applied to the wrong register offset is as dangerous as an incorrect mask.

Direct include sites for the DCN 3.2.0 generated offset and shift/mask headers in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`

Functional integration points include DCN32 resource construction, DMUB register access, display IRQ setup, low-level PHY/link bring-up, link training and retraining, pstate/rate changes, suspend/resume restore, power gating, PHY diagnostics, LBERT tests, margin/adaptation diagnostics, register dumps, and hardware debug flows that inspect calibration or adaptation state.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A wrong shift or mask can compile cleanly while corrupting RX adaptation, CDR/VCO/DPLL setup, analog crossover programming, TX pstate behavior, DCC calibration, clock alignment, or diagnostic readback.
- This range is boundary-partial. It starts after the register comment for `C20_PHY_CR3_LANE2_DIG_ASIC_RX_OVRD_VCO_IN` and ends before the masks for `C20_PHY_CR3_LANE3_DIG_TX_FIFO_CTL`; adjacent chunks are needed for complete register-family descriptions.
- Lane/register repetition is easy to misindex. `LANE2` RX fields and `LANE3` TX fields are structurally similar to other C20 PHY lanes, but the names target distinct lane instances.
- Value and `*_OVRD_EN` pairs must be updated carefully. Setting a value without its override-enable bit may have no effect, while setting override-enable bits unintentionally can bypass hardware or firmware ownership during link training and calibration.
- Status, clear, trigger, request, done, lock, and calibration fields can have side effects not visible in this header. Generic read/modify/write code must preserve unrelated bits and honor access-type rules from the hardware specification.
- Reserved masks are explicit and should not be treated as writable payload. Accidental writes to reserved bits may have undefined behavior on real hardware.
- Power, reset, and clock fields are sensitive. Incorrect pstate, reset, regulator, VCO, CDR, DCC, clock-alignment, or FIFO programming can cause intermittent link failures that depend on link rate, lane count, power state, temperature, voltage, or suspend/resume timing.
- Diagnostic fields such as statistics counters, LBERT patterns, adaptation status, and analog CREG/status readbacks can produce valid-looking values even when decoded with the wrong lane or field mask.

## Test Signals

Useful validation signals for changes touching this range include:

- Build AMDGPU Display Core with DCN32 support enabled so token-pasted register and field symbols resolve across resource, DMUB, IRQ, clock, GPIO, and GMC users.
- Mechanically compare the 2,168 macro definitions in this chunk against the authoritative AMD register database or a known-good regenerated `dcn_3_2_0_sh_mask.h`.
- Cross-check the companion `dcn_3_2_0_offset.h` for matching `C20_PHY_CR3_LANE2_*` and `C20_PHY_CR3_LANE3_*` register names and address/index alignment.
- Run display link bring-up and retraining on DCN32 hardware across lane counts, link rates, hotplug, mode changes, suspend/resume, and power-gating transitions.
- Exercise lane2 RX paths that depend on signal-detect thresholds, CDR lock, VCO calibration, DPLL bounds, adaptation request/status, EQ/DFE coefficients, DCC/IQ calibration, and statistics counters.
- Exercise lane3 TX paths that depend on pstate transitions, reset/request behavior, power-up timings, DCC calibration, clock alignment, FIFO bypass/read-pointer settings, and LBERT pattern/error controls.
- Inspect register dumps before and after link training, retraining, calibration, diagnostic test modes, and suspend/resume. Masked writes should affect only intended fields, reserved bits should remain stable, and lane2/lane3 fields should not be accidentally swapped.
- Use PHY diagnostics, where available, to validate adaptation telemetry, slicer/VDAC/IDAC offsets, signal-detect calibration, CDR/VCO status, TX calibration code, clock-alignment state, and LBERT pattern handling.

## Cross-Chunk Notes

The final per-file report should merge this document with the preceding chunk for the complete `C20_PHY_CR3_LANE2_DIG_ASIC_RX_OVRD_VCO_IN` register and with the following chunk for the rest of `C20_PHY_CR3_LANE3_DIG_TX_FIFO_CTL` plus subsequent lane3 analog TX definitions. This document is intentionally limited to the assigned source range and serves as the source-tree-aligned chunk artifact for `subset-b-001997`.
