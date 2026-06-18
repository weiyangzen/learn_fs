# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 91078-93479

## Purpose

This chunk is a generated AMD DCN 4.1.0 shift/mask register-field slice. It contains no executable C logic; it publishes preprocessor constants that tell AMDGPU display register helpers where individual hardware fields live inside DPCS/DPCSSYS registers. Driver code combines these macros with the matching offset definitions, register tables, and helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`.

The range sits deep inside a 145,870-line header and covers DisplayPort/PHY control-system (`DPCSSYS_CR1`) field definitions. It starts in the middle of the lane-2 RX statistics block, covers lane-2 analog TX/RX control and status fields, covers lane-3 ASIC interface, TX power-control, RX statistics, and analog TX fields, then enters raw common PLL/AON control fields and stops inside the first rawlane0 PCS transmit override register. The requested slice has 2,176 `#define` lines: 1,097 `__SHIFT` macros and 1,087 `_MASK` macros. The mismatch is expected for this artificial chunk boundary because the first lines are masks for a register whose shifts are just before the slice, and the final `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN` masks continue after the slice.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, memory allocations, or software APIs in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate the field during read-modify-write operations.

Major register families in this slice:

- `DPCSSYS_CR1_LANE2_DIG_RX_STAT_*`: lane-2 sample/statistic counters, match-pattern controls, counter enables, clock/sample delay controls, valid-loss clear, and statistic stop bits. The chunk begins after `STAT_CTL1` shifts, so only its masks are visible here.
- `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_*`: lane-2 MPHY RX PWM polarity, RX termination low-speed count, and analog PWM clock-stability count fields.
- `DPCSSYS_CR1_LANE2_DIG_ANA_TX_*`: digital overrides for lane-2 analog TX clocks, data enable, reference generator, VCM hold, PLL clock enables, reset, serial enable, data rate, RX detect, override enable, termination code, driver source, equalization leg pull enables/directions, pre/post cursor controls, DCC DAC controls, and TX override extensions.
- `DPCSSYS_CR1_LANE2_DIG_ANA_RX_*` and `DPCSSYS_CR1_LANE2_ANA_RX_*`: lane-2 RX analog override and direct analog fields for rate/width, reset/power, termination, squelch/signal-detect, VCO/phase settings, calibration, DAC, AFE attenuation/VGA/CTLE, scope/slicer controls, IQ phase/sense, clock phase adjust, status, CDR, voltage regulator, and ATB measurement controls.
- `DPCSSYS_CR1_LANE2_ANA_TX_*`: lane-2 direct analog TX controls for override measurements, power, alternate bus, ATB selection, DCC DAC, termination code, override clocking, miscellaneous analog tuning, mux select, voltage regulator, and reserved hardware fields.
- `DPCSSYS_CR1_LANE3_DIG_ASIC_*`: lane-3 ASIC-facing override and observed signal fields for lane ownership, TX reset/request/pstate/rate/width/power/PLL/VBOOST/IBOOST/beacon/async behavior, RX detect/valid/signal-detect, and raw ASIC in/out status.
- `DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_*`: lane-3 TX power-state programming for P0/P0S/P1/P2, power-up timing, DCC CR-bank address/data, DCC DAC control/range/select/ack/address, clock alignment, and LBERT control.
- `DPCSSYS_CR1_LANE3_DIG_RX_STAT_*`: lane-3 pattern match, data masks, LD values, sample and statistic counters 0-6, statistic clock/control fields, and statistic stop.
- `DPCSSYS_CR1_LANE3_DIG_ANA_TX_*` and `DPCSSYS_CR1_LANE3_ANA_TX_*`: lane-3 analog TX override and direct analog fields equivalent to the lane-2 TX subset, including termination, equalization, status, DCC DAC, power, ATB, misc, mux, VREG, and reserved fields.
- `DPCSSYS_CR1_RAWCMN_DIG_*`: common raw DPCS controls for CMN enable, MPLLA/MPLLB overrides, bandwidth and spread-spectrum controls, lane FSM extension, common control fields, MPLL state, TX calibration code, SRAM init status, OCLA, supervisor analog overrides, raw PCS/FW ID codes, and repeated AON RTUNE RX/TXDN/TXUP values 0-7.
- `DPCSSYS_CR1_RAWCMN_DIG_AON_CMN_*`: always-on common controls for SRAM boot-loader/power-gate behavior, PMA/PCS power-good overrides, power/reset/isolation overrides, MPLL/refclock force/ack overrides, VREF calibration status, resource request/ack overrides, reference range override, MPLL power-down timing, and REXT override.
- `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`: the beginning of rawlane0 PCS TX override fields for pstate, low-power disable, width, rate, MPLL selection/enables, master MPLL state overrides, and TX async enable override. Only shifts and the first two masks are inside this chunk.

## Control Flow

This header has no runtime control flow. Runtime behavior comes from AMDGPU display and link code:

1. DCN 4.1.0 register-list code includes this shift/mask header with the matching register-offset header.
2. Block-specific table macros token-paste register and field names into shift/mask table initializers.
3. Link, PHY, DMUB, diagnostics, and display resource code stores the generated constants in per-ASIC register tables.
4. Runtime paths use register helpers to read, update, poll, and clear DPCS/DPCSSYS fields while programming DisplayPort PHY lanes, power states, PLLs, calibration, link bring-up, test modes, and diagnostics.

The macros do not encode ordering. Consumers must still sequence resets, reference clocks, MPLL selection, lane power state changes, TX/RX analog overrides, RX statistic sampling, calibration, and power-gating transitions according to hardware requirements.

## State And Persistence Behavior

This chunk stores no software state and persists nothing by itself. It describes MMIO-backed hardware state for DPCS/PHY control:

- Per-lane RX statistic state: sample counters, statistic counters, match masks/patterns, clock enables, sample done bits, valid-loss control, and stop/pause controls.
- Per-lane TX and RX analog state: override enables and values for clocks, resets, PLL use, rate/width, equalization, termination, power, DCC DAC, signal detect, CDR/VCO, AFE, slicers, calibration, DAC, and VREG tuning.
- Per-lane ASIC interface state: observed and overridden lane/PHY request, acknowledgement, pstate, rate, width, PLL, async, beacon, valid, and detect signals.
- Common PHY state: MPLLA/MPLLB force/ack and SSC controls, lane FSM behavior, SRAM initialization, supervisor analog controls, calibration codes, AON RTUNE values, power-good/reset/isolation overrides, reference range, VREF status, and resource handshake bits.

Persistence is hardware-defined. Configuration and override fields can remain active until another modeset/link-training path reprograms them, the lane/common block is power-gated, the display core suspends, or the ASIC resets. Status, done, ack, and calibration fields may be read-only, sticky, self-clearing, or valid only while the relevant PHY clocks and power domains are on. The generated header does not identify access side effects; consuming code and the hardware register specification must supply that semantic layer.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 4.1.0 register database and the matching offset header for the same register names. The field macros are only meaningful when paired with the correct `DPCSSYS_CR1_*` register offsets and the SOC/DCN base-address tables used by AMDGPU.

Integration points include:

- AMD display register access helpers that use generated shift/mask tables for field-level read-modify-write.
- DCN link and PHY programming paths that configure DisplayPort DPCS lanes, lane power state, TX/RX training behavior, PLLs, analog front-end tuning, signal detect, termination, and calibration.
- Diagnostics, bring-up, and factory/test flows using RX statistics, pattern matchers, LBERT, OCLA, ATB measurement, DCC DAC controls, and raw override registers.
- Low-power, suspend/resume, and hotplug/link-retraining paths that depend on correct PMA/PCS power-good, isolation, reset, MPLL, reference-clock, SRAM, and resource handshake fields.

The macro names are highly instance-specific. Lane-2, lane-3, raw common, and rawlane0 fields in this slice are not interchangeable with fields for other lanes or DPCS instances even when their bit layouts look mechanically repeated.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly but update an adjacent PHY control bit, leaving a lane stuck in reset, misprogramming rate/width, disabling a PLL, or corrupting analog tuning.
- The file is generated metadata. Manual edits can diverge from the authoritative register database, matching offset header, firmware expectations, and silicon documentation.
- The register families are repetitive across lanes. A generator or copy error can affect only lane 2 or lane 3, so successful single-lane or low-lane-count testing does not prove all lane instances are correct.
- The chunk boundaries are artificial. The first visible `STAT_CTL1` definitions are masks without their shifts in this slice, and the final `RAWLANE0_DIG_PCS_XF_TX_OVRD_IN` register is incomplete because most masks continue in the next chunk.
- Override-enable fields are high risk. Leaving override enables asserted after diagnostics or training can force stale analog, PLL, or power-state values and break subsequent link training, hotplug, or resume.
- Power and PLL fields are sequencing-sensitive. Writes while the common block, lane block, reference clock, or MPLL is off may be ignored or may produce unstable intermediate hardware state.
- Analog tuning and calibration masks are hardware-sensitive. Incorrect DCC DAC, termination, equalization, AFE, CDR, VCO, VREF, REXT, or RTUNE fields can cause link training failures, marginal signal integrity, or failures only at high link rates.
- Status and statistic fields may be side-effect-sensitive. Misinterpreting done/valid/ack/status bits can produce false diagnostics, stuck waits, missed calibration completion, or invalid link-health reporting.

## Test Signals

Useful validation combines generated-header checks with hardware exercise:

- Build AMDGPU display support for DCN 4.1.0. Missing or renamed field macros should fail where DCN 4.1.0 register tables reference these DPCSSYS fields.
- Mechanically verify shift/mask pairing in lines 91078-93479, allowing the known boundary exceptions at the beginning of `DPCSSYS_CR1_LANE2_DIG_RX_STAT_STAT_CTL1` masks and the end of `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN`.
- Diff this range against AMD's authoritative DCN 4.1.0 register database and adjacent generated headers where DPCS lane/common layouts are expected to be compatible.
- Exercise DisplayPort link training and retraining on DCN 4.1 hardware across lane counts that include lanes 2 and 3, multiple link rates, hotplug, HPD IRQ, MST if supported, suspend/resume, and low-power transitions.
- Validate diagnostic paths for RX statistic counters, match controls, LBERT/OCLA, ATB measurement, DCC DAC programming, and calibration done/status reporting.
- Stress power and PLL transitions: enter/exit lane power states, switch MPLLA/MPLLB selection, power-gate/ungate PMA and PCS domains, and verify resource request/ack and SRAM/VREF/RTUNE status.
- Watch kernel logs and hardware diagnostics for AUX/link-training timeouts, CR/EQ failures, stuck waits on done/ack/status bits, display blanking after resume, high-link-rate instability, repeated retraining, incorrect lane power state, and failures isolated to lane 2 or lane 3.

## Cross-Chunk Notes

Previous chunks contain the beginning of the lane-2 RX statistic control block and earlier DPCSSYS_CR1 lane-2 definitions. Later chunks continue the rawlane0 PCS transmit override register and then cover subsequent rawlane0/rawlane/common DPCS fields. The final per-file research document should merge adjacent chunks before making complete claims about all lanes, all rawlane registers, or the full `dcn_4_1_0_sh_mask.h` namespace.
