# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 2474-4859

## Scope

This chunk is part of the generated AMD DPCS 4.2.0 register offset header. It contains preprocessor constants only: `ix...` register-index aliases mapped to hexadecimal offsets inside the DPCS client register aperture. There are no C functions, structs, branches, allocations, locks, direct MMIO accesses, or persistence mechanisms in this source range.

The slice covers 2,386 source lines and 2,382 `#define` entries. It starts inside the CR0 RAWAON lane 0 always-on receiver register list at `ixDPCSSYS_CR0_RAWAONLANE0_DIG_RX_PHSADJ_LIN` (`0x4009`) and ends inside the CR1 RAWAON lane 2 list at `ixDPCSSYS_CR1_RAWAONLANE2_DIG_RX_SIGDET_CONFIG` (`0x4250`). Neighboring chunks are needed to reconstruct the full CR0 RAWAON lane 0 prologue and the CR1 RAWAON lane 2 tail.

## Purpose

The purpose of this chunk is to publish the DPCS 4.2.0 offset namespace used by AMDGPU display and PHY code to address DisplayPort/PHY control/status registers. The values are not field masks; they are register offsets or indirect register indices that are paired with companion shift/mask headers and the driver's register access helpers.

Major covered areas:

- CR0 always-on lane receiver/DFE/adaptation aliases for RAWAON lanes 0 through 3 plus a generic `RAWAONLANEX` block.
- CR0 support/supervisor aliases covering ID code, level and reference-clock overrides, MPLLA/MPLLB ASIC inputs, PLL override inputs, SSC, bandgap/reference power timing, rtune, and analog status/override outputs.
- CR0 lane-generic aliases for ASIC handoff/mirror registers, TX/RX P-state and power-up timing, TX DCC, RX VCO/CDR/DPLL/adaptation/statistics, MPHY low-speed controls, and analog TX/RX override/status registers.
- CR0 raw memory and raw lane aliases for PCS, FSM, IRQ, PMA, TX/RX control, loopback/test, and lane state observation.
- CR1 support/supervisor aliases with the same PLL, clock/reset, rtune, bandgap, and analog status model as CR0, but reset to a CR1-local offset namespace beginning at `0x0000`.
- CR1 per-lane aliases for lanes 0 through 3, where lanes 1 and 2 include the full TX/RX PHY register families while lanes 0 and 3 in this chunk expose the smaller TX/ASIC subset present in this range.
- CR1 raw common and raw lane aliases for common control/status, PCS/FSM/IRQ/PMA cross-fabric state, and lane controller observability.
- CR1 RAWAON lane 0, lane 1, and most of lane 2 always-on receiver/DFE/adaptation aliases.

## Important Macros and Register Families

The exported API is the generated macro naming contract:

- `ixDPCSSYS_CR<n>_<BLOCK>_<REGISTER>` names an indexed DPCS register for client router instance `CR<n>`.
- The hexadecimal value is the register's DPCS internal offset or index. For repeated lane blocks the low byte commonly identifies the register inside the lane, while the high nibble/byte selects lane or sub-block.
- Generic `LANEX`, `RAWLANEX`, and `RAWAONLANEX` entries describe per-lane templates; numbered `LANE0..3`, `RAWLANE0..3`, and `RAWAONLANE0..3` entries bind the same register families to concrete lanes.
- These offset constants must be used with companion generated shift/mask headers such as `dpcs_4_2_0_sh_mask.h` when code needs to update individual fields.

Important covered families include:

- Always-on receiver calibration and adaptation: `RAWAONLANE*` and `RAWAONLANEX` entries for AFE ATT/CTLE IDAC offsets, RX IQ/phase adjustment, DFE phase/data/bypass/error offsets, DFE even/odd reference levels, RX adaptation ATT/VGA/CTLE/DFE tap status, adaptation done, fast flags, slicer controls, common calibration status, and calibration code readbacks.
- Always-on signal detect and DCC controls: RAWAON aliases for RX LOS mask/filtering, signal-detect calibration/high-frequency/low-frequency code, VREF generator enable, TX DCC bank address/data/control/config, MPLL background control, signal-detect override/input, firmware MM/adaptation/calibration configuration, lane transceiver mode override/input, and RX signal-detect configuration.
- Supervisor and common PLL controls: `SUP` and `SUPX` entries for ID code, reference clock and level overrides, MPLLA/MPLLB ASIC inputs, charge-pump/divider/HDMI-clock overrides, SSC peak/step/spread type, PLL power/control/timers/status/calibration/DAC outputs, bandgap and reference power timing, rtune configuration/status/set values, and analog override/status mirrors.
- ASIC lane handoff registers: `LANE*` and `LANEX` `DIG_ASIC_*` entries for lane override inputs, TX/RX override inputs/outputs, ASIC-owned TX/RX inputs and outputs, RX equalization and CDR/VCO ASIC inputs, OCLA selection, and lane control observability.
- TX power, DCC, and diagnostics: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, DCC CR bank access, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- RX power, VCO, CDR, DPLL, adaptation, and statistics: RX P-state and power-up timing, VCO calibration controls/timers/status, XAUI comma mask, RX LBERT control/error count, CDR control/status, DPLL frequency and bounds, adaptation config/reset/status, slicer and DAC-control selection, statistic match/mask/control/counter/sample registers, and statistic stop/calibration-comparator clock controls.
- Analog and MPHY integration registers: `DIG_ANA_*`, `ANA_TX_*`, `ANA_RX_*`, and `DIG_MPHY_*` entries for analog TX/RX override outputs, termination codes, equalization, DCC DAC, RX AFE/CTLE/VGA/slicer/calibration DAC controls, signal detect, analog test-bus measurement, MPHY PWM, low-speed termination, and PWM clock stability.
- Raw lane controller and interrupt registers: `RAWLANE*` and `RAWLANEX` entries for PCS transmit/receive overrides and PCS I/O mirrors, FSM fast-state monitors for RX startup/adaptation/calibration/power-up/VCO and TX common mode/RX detect, IRQ request/clear/mask entries for RX/TX reset/request/rate/P-state/adaptation/phase calibration/loopback/DCC, and PMA cross-fabric override/status registers.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. AMDGPU display or PHY code includes this generated DPCS 4.2.0 offset header with the matching 4.2.0 shift/mask header.
2. Register tables, macro accessors, or generated init paths select an `ix...` offset for the appropriate CR instance and lane namespace.
3. Register helpers use that offset to address the DPCS register, optionally applying companion field shift/mask constants for read/modify/write operations.
4. The hardware performs the actual state transition: PLL power-up, reference clock/bandgap sequencing, lane TX/RX P-state changes, DCC/VCO/CDR/adaptation calibration, signal-detect setup, statistics collection, interrupt status updates, or PCS/PMA handoff.

The represented hardware flow is typically: configure supervisor PLL/reference/rtune resources, select ASIC-owned or software-override lane controls, sequence TX/RX power states and delay timers, perform DCC/VCO/CDR/adaptation calibration, expose or consume PCS/PMA/ASIC handoff signals, and read status/diagnostic offsets to validate link readiness.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros lives in DPCS hardware registers.

The hardware state represented by this chunk includes:

- Supervisor state: MPLLA/MPLLB power, calibration, spread-spectrum, timer, charge-pump, divider, HDMI-clock, rtune, bandgap, reference-clock, and analog status/override registers.
- Lane power state: TX and RX P0/P0S/P1/P2 controls, TX/RX power-up timers, MPHY PWM/termination/stable-clock controls, and analog clock/data/refgen/termination enables.
- Calibration state: RX VCO and CDR/DPLL controls/status, RX DCC calibration code readbacks, TX DCC DAC/bank controls, AFE/CTLE/VGA/DFE/slicer offsets, phase/IQ adjustment, common calibration status, and firmware calibration/adaptation configuration.
- Handoff and override state: ASIC, PCS, PMA, raw lane, and always-on lane override inputs/outputs for TX, RX, equalization, CDR/VCO, signal detect, transceiver mode, DCC, and lane mapping.
- Diagnostics and observability: LBERT controls/errors, RX statistics match/counter/sample registers, FSM fast-state/status monitors, IRQ status/clear/mask registers, OCLA selections, analog status, and test-bus measurement registers.

Persistence is limited to the hardware register lifetime. Values can be lost or require reprogramming after GPU reset, DPCS client router reset, lane reset, power gating, display engine reset, suspend/resume, hotplug-triggered retraining, or link mode/rate/lane-count changes. Higher-level driver state and silicon tables remain the durable source of truth.

## Dependencies

This chunk depends on:

- Companion generated DPCS 4.2.0 field metadata headers, especially the matching shift/mask header, because offsets alone do not describe bit layout.
- AMDGPU display register access infrastructure that understands DPCS indexed registers and the `ixDPCSSYS_*` naming convention.
- The silicon register database that generated this file; manual edits must remain synchronized with other generated headers and register tables.
- DisplayPort/link encoder, PHY bring-up, power-management, diagnostics, and validation code that selects CR0/CR1 and lane-specific DPCS offsets.
- Correct mapping between generic `LANEX`/`RAWLANEX`/`RAWAONLANEX` templates and concrete lane instances when generated tables or helper macros expand per-lane access.

The offsets in CR0 and CR1 intentionally use different base namespaces in this range. CR0 contains higher CR0 template/raw/supervisor ranges such as `0x7000`, `0x8000`, `0x9000`, `0xa000`, and `0xe000`, while CR1 restarts supervisor offsets at `0x0000`, lane offsets at `0x1000..0x1300`, raw/common offsets at `0x2000..0x3300`, and RAWAON offsets at `0x4000..0x4250` in this chunk.

## Integration Points

Primary integration points are the macro names consumed by AMDGPU register tables and register helpers. A consumer naming an offset such as `ixDPCSSYS_CR1_LANE2_DIG_RX_CDR_CDR_CTL_0` or `ixDPCSSYS_CR0_RAWAONLANEX_DIG_RX_ADPT_DFE_TAP3` relies on this header for the exact DPCS 4.2.0 register index.

Integration surfaces include:

- Link and lane power sequencing through TX/RX P-state and power-up-time offsets.
- PHY calibration through supervisor PLL, TX DCC, RX VCO/CDR/DPLL, common calibration, and raw/always-on calibration status offsets.
- Link training and signal integrity through adaptation, AFE/CTLE/VGA/DFE/slicer, signal-detect, phase/IQ, and equalization handoff offsets.
- Display engine and PHY ownership handoff through ASIC, PCS, PMA, and raw lane override/input/output offsets.
- Diagnostics through LBERT, RX statistic counters/matchers, FSM monitors, IRQ status/clear/mask, OCLA selection, and analog test-bus/status offsets.
- Multi-lane access through repeated lane families, where a wrong concrete lane prefix can program a valid but incorrect lane.

## Risks and Failure Modes

- Incorrect offset values can program the wrong hardware register even when the field shift/mask is correct, causing link training, power sequencing, or calibration failures that compile cleanly.
- CR0/CR1 namespace confusion is high risk because similar register families recur under different offset bases. A valid CR0 offset used in a CR1 path, or the reverse, can silently target unrelated hardware.
- Lane prefix mistakes can produce asymmetric failures that appear only for particular lane counts, lane mappings, rates, connectors, or hotplug sequences.
- Generic `LANEX`/`RAWLANEX`/`RAWAONLANEX` template offsets must stay aligned with numbered lane instances. Divergence can break generated table expansion or lane-generic helper code.
- Override and handoff offsets are sensitive. Writing an ASIC/PCS/PMA override register instead of an observed input/output mirror can force software ownership of signals that hardware sequencing expects to control.
- Power and timing offsets are order-sensitive. Bad P-state or power-up timer addresses can leave analog supplies, clocks, deserializers, or CDR/VCO resources enabled too early, too late, or not at all.
- Calibration and status aliases can have side effects or stale-read hazards depending on hardware semantics. Misaddressed DCC ack, VCO status, adaptation done, IRQ clear, or statistic stop registers can hide real failures.
- This chunk starts and ends mid-family, so final per-file synthesis must reconcile partial boundary coverage with neighboring chunks before claiming complete RAWAON lane coverage.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DPCS 4.2.0 display/PHY code builds without missing `ixDPCSSYS_CR0_*` or `ixDPCSSYS_CR1_*` offset symbols.
- Generated-header consistency: every offset consumed by register tables has a matching shift/mask register name in companion generated headers where field access is required.
- Register-table sanity: CR0 and CR1 instances use the correct namespace bases, and repeated lane/register families preserve expected spacing across lane instances.
- DP/link smoke tests: hotplug, modeset, link retraining, lane-count changes, link-rate changes, suspend/resume, GPU reset, and power-gating recovery on displays that exercise CR0 and CR1 paths.
- PHY bring-up checks: supervisor PLL readiness, rtune/bandgap/reference-clock setup, TX/RX P-state transitions, VCO/CDR/DPLL lock, DCC acknowledgement, adaptation done, and signal-detect readback.
- Signal-integrity checks: AFE/CTLE/VGA/DFE/slicer convergence, phase/IQ adjustment, RX statistics counters, LBERT error counts, and stable behavior across cable/sink/link-rate combinations.
- Interrupt and observability checks: raw lane IRQ request/clear/mask behavior, FSM fast-state monitors, OCLA selections, PCS/PMA/ASIC input/output mirrors, and analog status/test-bus readbacks.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_4_2_0_offset.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.
