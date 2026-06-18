# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 4767-7226

## Scope

This chunk is part of the generated AMD DPCS 4.2.0 ASIC register shift/mask header. It contains preprocessor constants only: each register field is represented by a `...__SHIFT` bit offset and usually a matching `..._MASK` value. There are no C functions, structs, branches, allocations, locks, direct MMIO operations, or file-backed persistence mechanisms in this range.

The slice covers 2,460 source lines, 2,089 `#define` entries, and 362 register-comment blocks. It begins inside the `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED*` run at reserved register 6, covers the full `DCIO_UNIPHY3` and `DCIO_UNIPHY4` reserved macro-control ranges, then enters the `dpcssys_cr0_rdpcstxcrind` indirect CR0 transmitter/PHY register namespace. It ends at the complete `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CTL2` register, immediately before `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_STOP`.

## Purpose

The purpose of this chunk is to publish exact bitfield metadata for DPCS 4.2.0 display PHY, UNIPHY, supervisor, PLL, lane-0 TX, and lane-0 RX-statistics registers. Runtime AMDGPU display/link code combines these generated shift and mask names with companion register-address headers and register helper macros to program or inspect hardware without open-coded bit arithmetic.

Major covered areas:

- UNIPHY macro-control reserved windows for `DCIO_UNIPHY2` tail registers and all `DCIO_UNIPHY3`/`DCIO_UNIPHY4` reserved registers 0 through 57, each exposing a full 32-bit `UNIPHY_MACRO_CNTL_RESERVED` field.
- CR0 supervisor digital controls for ID code readback, reference clock overrides, MPLLA/MPLLB divider and HDMI clock overrides, PLL enable/divider/fractional-N/SSC/charge-pump controls, prescaler and level overrides, ASIC input mirrors, bandgap, RTUNE, and analog status/override output paths.
- CR0 supervisor analog controls for prescaler, RTUNE comparator, bandgap, MPLLA/MPLLB analog miscellaneous bits, override gates, analog test bus selectors, PLL control words, DLL/divider bypasses, and reserved analog control fields.
- MPLLA/MPLLB power-control and calibration fields, including power FSM status, DAC max-range, lock/stable/power-down timers, calibration override, analog DAC output, and SSC spread-type override.
- Lane 0 ASIC/TX interface fields for lane loopback, software override inputs, ASIC-owned input mirrors, TX request/ack handshakes, rate/width/P-state, reset, inversion, detect-RX, data enable, async drive, HDMI mode, MPLL selection, repeated-lane/master-lane clock-shift handoff, and TX output mirror fields.
- Lane 0 TX power-control fields for P0/P0S/P1/P2 per-state analog enables, resets, low-power detection, electrical-idle, reference-generation, termination, RX detection, async termination, power-up timing, DCC CR-bank/DAC access, clock alignment, and TX LBERT control.
- Lane 0 RX statistic fields for load/start values, data and pattern masks, A/B pattern match controls, statistic source/shift/timer/clock controls, sample counter completion, seven statistic counters, comparator clock timing, extended pattern masks, and sample-count disable/scope-delay controls.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position inside the target DPCS register.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask consumed by register-helper read/modify/write and decode paths.
- Prefixes such as `DCIO_UNIPHY3_`, `DPCSSYS_CR0_SUP_DIG_`, `DPCSSYS_CR0_SUP_ANA_`, and `DPCSSYS_CR0_LANE0_` are part of the generated ABI between register metadata and display/PHY tables.

Important families in this chunk include:

- UNIPHY reserved windows: `DCIO_UNIPHY2_UNIPHY_MACRO_CNTL_RESERVED6..57`, `DCIO_UNIPHY3_UNIPHY_MACRO_CNTL_RESERVED0..57`, and `DCIO_UNIPHY4_UNIPHY_MACRO_CNTL_RESERVED0..57` define full-register reserved masks. They preserve generated address/field coverage for silicon registers that are not given public semantic field names in this header.
- Supervisor PLL digital overrides: `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN`, `MPLLA/MPLLB_DIV_CLK_OVRD_IN`, `MPLLA/MPLLB_HDMI_CLK_OVRD_IN`, `MPLLA/MPLLB_OVRD_IN_0..5`, `MPLLA/MPLLB_SSC_PEAK_*`, `MPLLA/MPLLB_SSC_STEPSIZE_*`, and charge-pump override registers define refclock source/range, PLL enable, divider, VCO/fractional-N, SSC, HDMI clocking, and CP settings.
- Supervisor handoff and status: `SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, `LVL_OVRD_IN`, `MPLLA/MPLLB_ASIC_IN_*`, clock ASIC input mirrors, `ASIC_IN`, level/bandgap/CP ASIC inputs, `ANA_STAT`, and `ANA_*_OVRD_OUT` fields describe the boundary between ASIC-owned PHY control and software override/readback paths.
- Supervisor analog tuning: `SUP_ANA_PRESCALER_CTRL`, `SUP_ANA_RTUNE_CTRL`, `SUP_ANA_BG1..3`, `SUP_ANA_MPLLA/MPLLB_MISC*`, `SUP_ANA_MPLLA/MPLLB_OVRD`, `SUP_ANA_MPLLA/MPLLB_ATB*`, `SUP_ANA_MPLLA/MPLLB_CTR*`, and reserved analog control registers expose bandgap/reference, RTUNE, PLL analog bias/filter/test, reset/calibration override, and test-bus measurement fields.
- MPLL power and calibration: `SUP_DIG_MPLLA/MPLLB_MPLL_PWR_CTL_*`, `MPLL_DAC_MAXRANGE`, `MPLL_TIMERS*`, `MPLL_CAL`, `MPLL_ANA_DAC_OUT`, and `SSC_GEN_SPREAD_TYPE` define PLL power FSM controls/status, lock and stable timing, calibration forcing, DAC readback, and spread-spectrum type override.
- Lane 0 ASIC/TX override and mirror fields: `LANE_OVRD_IN`, `TX_OVRD_IN_0..5`, `TX_OVRD_OUT`, `RX_OVRD_OUT_0`, `LANE_ASIC_IN`, `TX_ASIC_IN_0..2`, `TX_ASIC_OUT`, `RX_ASIC_OUT_0`, and `TX_OVRD_OUT_1` define software-forced and hardware-observed signals around TX lane control, RX detect, clock shifting, lane-master selection, and low-level handshakes.
- Lane 0 TX power/diagnostic fields: `TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, `DCC_CR_BANK_*`, `DCC_DAC_*`, `TX_CLK_ALIGN_TX_CTL_0`, and `TX_LBERT_CTL` define analog TX enable/reset sequencing, timing delays, DCC DAC access, clock alignment, and loopback error-rate test pattern control.
- Lane 0 RX statistic fields: `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL0..5`, `STAT_CTL0..2`, `SMPL_CNT1`, `STAT_CNT_0..6`, and `CAL_COMP_CLK_CTL` define pattern-match setup, sample timing, statistic source selection, counter enables/readback, valid-loss control, and comparator timing.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. AMDGPU display/PHY code includes this generated shift/mask header with the matching DPCS 4.2.0 register offset/address header.
2. Register descriptor tables or register helper macros pair the address constants with the shift and mask constants from this file.
3. Masked read/modify/write helpers use the `_MASK` and `__SHIFT` definitions to update individual fields or decode status fields.
4. The actual control flow occurs in hardware: supervisor clock/PLL power-up, analog calibration, RTUNE, lane-0 TX power sequencing, DCC access, LBERT diagnostics, and RX-statistic collection.

The represented hardware flow is typically: choose ASIC-owned or software-override controls, configure refclock/MPLL/prescaler/level/bandgap settings, wait for PLL power/calibration/status signals, program lane TX P-state and power-up timing, optionally access DCC or enable LBERT, and poll RX statistic counters or ASIC mirror outputs to validate signal behavior.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros lives in GPU/display PHY hardware registers.

The hardware state represented by this chunk includes:

- UNIPHY reserved register contents for instances 2, 3, and 4.
- Supervisor clock and PLL state: refclock enable/source/range, MPLLA/MPLLB enable/divider/VCO/fractional-N/SSC/CP settings, HDMI/div clocks, power FSM state, lock state, calibration state, DAC output, and spread-spectrum mode.
- Analog support state: prescaler, RTUNE comparator/configuration/results, bandgap/reference settings, PLL analog bias/filter/test controls, test-bus selectors, PMIX outputs, and analog override enables.
- Lane 0 TX state: request/ack, P-state, rate/width, reset, data enable, detect-RX, inversion, low-power detect, HDMI mode, async drive, MPLL selection, main/pre/post cursor values, per-P-state analog enables/resets, power-up delays, DCC DAC access, and lane-master clock-shift handoff.
- Lane 0 diagnostic/statistic state: LBERT mode/pattern/error injection, RX pattern masks, match selectors, statistic source and clock controls, sample-count completion, seven statistic counters, valid-loss control, and comparator clock timing.

Persistence is limited to hardware register lifetime. Values may need reprogramming after GPU reset, display engine reset, DPCS/PHY reset, power gating, suspend/resume, hotplug retraining, link-rate changes, or modeset-driven PHY reconfiguration. Driver policy and board/silicon tables remain the durable source of truth.

## Dependencies

This chunk depends on matching generated DPCS 4.2.0 register-address headers. Shift and mask constants alone do not identify where a register is located.

It also depends on:

- AMD display and PHY register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked reads, writes, updates, and polling.
- The silicon register database or generator that emits this header and the companion offset headers.
- Link encoder, PHY bring-up, clock, power-management, diagnostics, and validation code that programs CR0 supervisor and lane-0 DPCS registers.
- Correct instance mapping between `DCIO_UNIPHY2/3/4`, `DPCSSYS_CR0_SUP_*`, and `DPCSSYS_CR0_LANE0_*` macro prefixes and their corresponding hardware address blocks.

Because this is generated silicon metadata, manual edits are risky unless synchronized with the register database, address headers, generated register tables, and all consumers that reference these exact names.

## Integration Points

Primary integration points are the macro names consumed by AMDGPU register tables and masked register helpers. A consumer naming a field such as `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN__REF_CLK_EN`, `DPCSSYS_CR0_SUP_DIG_MPLLA_OVRD_IN_0__MPLLA_EN`, `DPCSSYS_CR0_LANE0_DIG_TX_PWRCTL_TX_PSTATE_P0__TX_P0_ANA_CLK_EN`, or `DPCSSYS_CR0_LANE0_DIG_RX_STAT_STAT_CNT_0__STAT_CNT_0` relies on this header for the correct bit position and mask.

Integration surfaces include:

- Clock/PLL bring-up: refclock, MPLLA/MPLLB dividers, HDMI clock division, fractional-N, SSC, power FSM, lock timing, DAC, and calibration fields.
- Analog support and calibration: prescaler, bandgap, RTUNE, PLL analog controls, analog override outputs, PMIX fields, and test-bus measurement selectors.
- ASIC/software ownership handoff: `*_OVRD_IN`, `*_OVRD_OUT`, and `*_ASIC_IN/OUT` fields that let software override, observe, or debug hardware-owned PHY signals.
- Lane 0 transmit path: TX request/ack, rate/width/P-state, reset, detect-RX, HDMI mode, main/pre/post cursor, per-power-state analog enables, power-up timers, DCC DAC access, and clock alignment.
- Diagnostics and validation: TX LBERT controls, RX statistic pattern matchers, sample counters, statistic counters, valid-loss handling, comparator timing, and ASIC mirror registers.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent fields in compact 16-bit DPCS registers, causing PLL bring-up, calibration, TX power sequencing, or statistic collection failures.
- Reserved UNIPHY full-register masks are broad by design. If used carelessly, they can enable writes to undocumented hardware state that should remain generator- or firmware-controlled.
- Override fields are sensitive. A wrong mask can force software ownership of ASIC-controlled refclock, MPLL, bandgap, TX, RX, or lane-master signals and prevent hardware from completing normal training or calibration.
- PLL and timing fields are order and delay sensitive. Bad masks in MPLL power, lock, stable, power-down, or TX power-up timing registers can produce intermittent display bring-up failures rather than deterministic compile failures.
- Lane-prefix or address-block mistakes can compile cleanly while targeting the wrong UNIPHY instance or lane-0 register block, creating failures that only appear on certain connector, lane-count, or link-rate configurations.
- Status and clear fields can have side effects. Misdecoding RTUNE status, MPLL lock/calibration bits, DCC ack, RX statistic done bits, valid-loss clear/control, or LBERT trigger fields can hide real hardware failures or leave stale status latched.
- The chunk starts mid-family and ends at a boundary before the next RX statistic register. Per-file synthesis should reconcile the earlier `DCIO_UNIPHY2` reserved registers and the following `RX_STAT_STAT_STOP` fields from neighboring chunks.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DPCS 4.2.0 display/PHY code builds without missing `DCIO_UNIPHY*`, `DPCSSYS_CR0_SUP_*`, or `DPCSSYS_CR0_LANE0_*` shift/mask symbols.
- Generated-table sanity: each field is paired with the correct companion DPCS address constant and retains the expected repeated layout across MPLLA/MPLLB and UNIPHY instances.
- Display/link smoke tests: hotplug, modeset, lane-rate changes, link retraining, suspend/resume, GPU reset, and power-gating recovery on displays that exercise CR0 and lane-0 PHY paths.
- PHY bring-up checks: reference clock acknowledgement, MPLLA/MPLLB power FSM and lock status, calibration completion, RTUNE comparator/status readback, bandgap/reference state, and TX request/ack transitions.
- Lane TX checks: P0/P0S/P1/P2 sequencing, analog clock/data/refgen/termination enables, power-up timers, detect-RX, electrical-idle, DCC DAC ack/range/address behavior, and clock-alignment settings.
- Diagnostic checks: LBERT mode/error injection behavior, RX statistic match patterns, sample-count done bits, counter readbacks, valid-loss clear/control, comparator-clock timing, and ASIC input/output mirror consistency.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_4_2_0_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
