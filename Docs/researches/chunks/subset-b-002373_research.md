# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 85818-88178

## Purpose

This chunk is a generated AMD DPCS 4.2.2 shift/mask header slice for low-level display PHY/DPCS register fields. It contains no executable C code; its public surface is preprocessor constants that identify bit positions and bit masks for fields in DPCSSYS CR4 lane registers.

The requested range contains 2,136 `#define` lines and 225 register-comment markers. It starts inside `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`, covers the remainder of CR4 lane0 RX statistics and lane0 TX analog-control metadata, then covers a large CR4 lane1 span from ASIC override/status fields through TX/RX power, calibration, adaptation, statistics, MPHY, analog RX/TX override, signal-detect, DCC DAC, ATB, and TX term-code fields. The final line stops inside `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`, so both the first and last register groups are artificial chunk boundaries.

Although this file lives under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the same field.

The main register-field families in this chunk are:

- CR4 lane0 RX statistics tail: statistic counter enables, sample count, statistic counters 0 through 6, comparator clock controls, pattern-match controls, statistic stop, valid-loss clear/control, and sample-count disabling.
- CR4 lane0 digital/analog TX controls: TX analog override outputs, TX termination-code overrides, term-code load clock control, equalization override outputs 0 through 5, analog status, TX DCC DAC overrides, fast-start/loopback/AC-JTAG controls, ATB measurement selectors, power override, alternate bus, DCC DAC, term-code, override clock, misc, and reserved TX fields.
- CR4 lane1 ASIC-facing override/input/output fields: lane loopback and AC-JTAG controls; TX request, P-state, rate, width, MPLL selection, data enable, main/pre/post cursor, HDMI mode, detect-RX request, invert, low-power-detect, DC coupling, MPHY mode, FIFO, raw ASIC inputs, and OCLA fields; RX status/override paths for CDR, DPLL, equalization, adaptation, DAC control, and VCO.
- CR4 lane1 TX power/control fields: TX P-state values for P0/P0S/P1/P2, power-up timing registers, DCC CR bank address/data, DCC DAC control/range/selection/ack/address, TX clock alignment, and TX LBERT pattern/error injection control.
- CR4 lane1 RX power/calibration/adaptation fields: RX P-state and power-up timing, RX VCO calibration controls/timers/status, XAUI alignment mask, RX LBERT control/error, CDR control/status, DPLL frequency/bounds, adaptation configuration and reset, ATT/VGA/CTLE/DFE status, DFE offset readbacks, slicer controls, error-slicer level, DAC control selects, and adaptation CR bank access.
- CR4 lane1 RX statistics and MPHY fields: statistic load value, data mask, match controls, statistic control/count/stop, calibration-comparator clock control, MPHY PWM control, low-speed termination, and PWM-clock stable-count fields.
- CR4 lane1 analog RX/TX controls: TX analog override and equalization outputs, RX analog control/power/VCO overrides, RX calibration and DAC controls, AFE ATT/VGA/CTLE, scope/slicer/IQ controls, analog signal-change enable, status readbacks, RX term-code override/clock controls, MPHY override, signal-detect thresholds/calibration controls, TX DCC DAC overrides, TX fast-start/clock-loopback/AC-JTAG, ATB measurement selectors, TX power and alternate-bus overrides, DCC DAC, and TX term-code low bits.

Many fields follow an `*_OVRD_EN` or `ovrd_*` pattern. Those macros describe manual override enable bits paired with override values or hardware-state readbacks, which makes this range especially sensitive to debug, bring-up, PHY tuning, and link-training flows.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.5 resource code includes `dpcs_4_2_2_offset.h` and this matching `dpcs_4_2_2_sh_mask.h`.
2. Register-list and mask/shift-list macros in `dcn315_resource.c` bind generated offsets, shifts, and masks into link-encoder and DPCS register tables.
3. Display link encoder code uses those tables through shared AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. Runtime control flow for link enable, lane power sequencing, DP/HDMI PHY setup, training, test patterns, clock recovery, equalization, diagnostics, suspend/resume, and reset lives outside this generated header.

The macros in this chunk do not define programming order, timing, reset requirements, or read/write side effects. They only provide the bitfield positions used by code that performs those operations.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields for two CR4 lanes:

- Lane power, P-state, rate, width, PLL selection, data enable, clock readiness, reset, serial enable, loopback, MPHY, and AC-JTAG controls.
- TX electrical tuning state, including main/pre/post cursor values, equalization leg pull/push controls, termination-code override and update/reset controls, DCC DAC controls, VREG/VCM/refgen/clock/data/serial enables, and fast-start settings.
- RX clock/data recovery and adaptation state, including CDR controls, DPLL frequency bounds, VCO calibration results, ATT/VGA/CTLE/DFE status, DAC control selectors, slicer thresholds, scope controls, and RX term-code/signaldetect controls.
- Diagnostic and production-test state, including LBERT controls/errors, OCLA selectors, alternate-bus and ATB measurement selectors, CR bank address/data windows, statistic counters, pattern matchers, sample counters, valid-loss clear/control, and analog status readbacks.

Persistence and side effects are hardware-defined. Configuration fields generally remain until rewritten by modeset, link training, PHY reconfiguration, suspend/resume, power gating, GPU reset, or ASIC reset. Status, counter, acknowledge, self-clear, and calibration fields may be latched, sticky, clear-on-write, self-clearing, or valid only while the relevant DPCS lane is powered and clocked. This generated file does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.2 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h` supplies matching `ixDPCSSYS_CR4_*` register offsets, including the lane0 range around `0x1085-0x10ef` and the lane1 range around `0x1100-0x11e8` covered here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both DPCS 4.2.2 generated headers, defines `DPCS_BASE__INST0_SEG*`, and expands DPCS register and mask/shift lists for DCN 3.1.5 resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` also constructs HPO DP and DIO link encoder resources that depend on the generated register metadata for DPCS-backed link paths.
- Link management code under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/` exercises the resulting encoder operations for DP link enable/disable, DP PHY setup, link training, power management, and HPD/link-state transitions.
- Neighboring generated DPCS versions (`dpcs_4_2_0_*` and `dpcs_4_2_3_*`) provide useful generated-header comparison points. The 4.2.3 shift/mask header keeps many equivalent fields but uses shorter 16-bit-looking mask literals and some upper-case field spellings, so consumers must include the ASIC-specific header rather than mix versions.

Behaviorally, this range is part of the display link PHY layer. A bad field macro here can surface as connector bring-up failure, unstable DP training, broken HDMI electrical programming, incorrect lane power sequencing, unreliable calibration, misleading diagnostics, or failures limited to CR4 lane0/lane1 depending on routing.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift compiles cleanly and may corrupt only one hardware field at runtime.
- The file is generated. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the tail of `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0`, and the final lines stop after only three shift definitions in `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL`; adjacent chunks are required for complete register descriptions at both ends.
- Lane instance repetition is copy-sensitive. Lane1 largely mirrors lane0 families with address and prefix changes, but this chunk includes only the tail of lane0 and a broad lane1 span, so whole-lane equivalence claims need reconciliation with neighboring chunks.
- Override enable bits are hazardous. Misprogramming `*_OVRD_EN`, `ovrd_*`, and corresponding value fields can force PHY states that hardware training or power sequencing expects to control automatically.
- TX cursor, equalization, termination, DCC, VREG, and VCM masks are electrically sensitive. Incorrect field definitions can cause link-training failures, eye-margin degradation, intermittent high-rate errors, or visible display corruption.
- RX CDR, DPLL, VCO calibration, adaptation, DFE, CTLE, VGA, and slicer fields influence clock recovery and equalization. Wrong masks may look like sink/cable instability while the real issue is local PHY programming.
- Statistic, LBERT, OCLA, ATB, and CR-bank fields are diagnostic surfaces. Bad definitions may not affect normal display output but can hide training defects, produce misleading debug data, or break manufacturing/bring-up tests.
- Power and P-state fields require sequencing outside this header. Incorrect use of these masks can interact badly with suspend/resume, fast link retraining, power gating, and lane disable/enable transitions.
- CR4 lane-specific errors may be topology-dependent. Bugs can appear only on connectors or modes routed through the affected DPCS lane, especially when alternate routing or HPO DP paths are in use.

## Test Signals

Useful validation combines generated-header consistency checks with real display-link behavior:

- Build DCN 3.1.5 AMDGPU display support. Missing or renamed macros should surface in `dcn315_resource.c` and downstream link encoder register-table construction.
- Mechanically compare every field in this range against the authoritative DPCS 4.2.2 register-field database, ensuring each `_MASK` has the intended paired `__SHIFT` definition.
- Cross-check this shift/mask range against `dpcs_4_2_2_offset.h`, confirming every register comment in the chunk has a corresponding `ixDPCSSYS_CR4_*` offset.
- Run generated-header diff checks against `dpcs_4_2_0_*` and `dpcs_4_2_3_*` to catch accidental version mixing while allowing intentional spelling and literal-format differences.
- Exercise DP and HDMI link bring-up on connectors routed through CR4 lane0 and CR4 lane1. Expected signals are successful modesets, stable hotplug/link state, and no unexpected training fallback at normal link rates.
- Exercise DP link training across multiple rates and lane counts, including retraining after unplug/replug and suspend/resume. Watch for CDR/DPLL/VCO/adaptation failures, repeated equalization retries, or lane-specific instability.
- Validate TX electrical programming using high-bandwidth modes and, where available, register dumps or lab margining for main/pre/post cursor, EQ override, termination, DCC DAC, and fast-start fields.
- Exercise diagnostic paths that rely on this metadata: LBERT pattern/error control, statistic counters, pattern-match controls, OCLA, ATB measurement selection, CR bank address/data access, and analog status readbacks.
- Test power-management transitions with active and inactive links, including link disable/enable, display blank/unblank, runtime power gating, and system suspend/resume. Expected signals are no stuck P-state/power-up/calibration bits and no lane that requires a full GPU reset to recover.

## Cross-Chunk Notes

The previous chunk owns earlier CR4 lane0 ASIC, TX power, TX clock-align/LBERT, RX statistic load/match/control0, and likely other lane0 register groups. This chunk begins after `DPCSSYS_CR4_LANE0_DIG_RX_STAT_STAT_CTL0__STAT_RXCLK_SEL__SHIFT` and finishes the rest of that register's masks before moving forward.

The next chunk continues `DPCSSYS_CR4_LANE1_ANA_TX_TERM_CODE_CTRL` with the remaining shift and mask definitions, then should cover later CR4 lane1 analog RX fields and subsequent DPCS register groups. The final per-file research document should reconcile these partial boundaries before making complete statements about `dpcs_4_2_2_sh_mask.h` or all DPCS 4.2.2 lane metadata.
