# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002259`: lines 1-2433, `Docs/researches/chunks/subset-b-002259_research.md`
- `subset-b-002260`: lines 2434-4853, `Docs/researches/chunks/subset-b-002260_research.md`
- `subset-b-002261`: lines 4854-7300, `Docs/researches/chunks/subset-b-002261_research.md`
- `subset-b-002262`: lines 7301-9720, `Docs/researches/chunks/subset-b-002262_research.md`
- `subset-b-002263`: lines 9721-12191, `Docs/researches/chunks/subset-b-002263_research.md`
- `subset-b-002264`: lines 12192-14650, `Docs/researches/chunks/subset-b-002264_research.md`
- `subset-b-002265`: lines 14651-17088, `Docs/researches/chunks/subset-b-002265_research.md`
- `subset-b-002266`: lines 17089-19501, `Docs/researches/chunks/subset-b-002266_research.md`
- `subset-b-002267`: lines 19502-21927, `Docs/researches/chunks/subset-b-002267_research.md`
- `subset-b-002268`: lines 21928-24369, `Docs/researches/chunks/subset-b-002268_research.md`
- `subset-b-002269`: lines 24370-26787, `Docs/researches/chunks/subset-b-002269_research.md`
- `subset-b-002270`: lines 26788-29265, `Docs/researches/chunks/subset-b-002270_research.md`
- `subset-b-002271`: lines 29266-31717, `Docs/researches/chunks/subset-b-002271_research.md`
- `subset-b-002272`: lines 31718-34157, `Docs/researches/chunks/subset-b-002272_research.md`
- `subset-b-002273`: lines 34158-36568, `Docs/researches/chunks/subset-b-002273_research.md`
- `subset-b-002274`: lines 36569-38994, `Docs/researches/chunks/subset-b-002274_research.md`
- `subset-b-002275`: lines 38995-41436, `Docs/researches/chunks/subset-b-002275_research.md`
- `subset-b-002276`: lines 41437-43854, `Docs/researches/chunks/subset-b-002276_research.md`
- `subset-b-002277`: lines 43855-46340, `Docs/researches/chunks/subset-b-002277_research.md`
- `subset-b-002278`: lines 46341-48787, `Docs/researches/chunks/subset-b-002278_research.md`
- `subset-b-002279`: lines 48788-51226, `Docs/researches/chunks/subset-b-002279_research.md`
- `subset-b-002280`: lines 51227-53595, `Docs/researches/chunks/subset-b-002280_research.md`
- `subset-b-002281`: lines 53596-55194, `Docs/researches/chunks/subset-b-002281_research.md`

## Chunk Research

### subset-b-002259: lines 1-2433

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 1-2433

## Purpose

This chunk is the opening slice of a generated AMD DPCS 3.1.4 register shift/mask header. It contains no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for DisplayPort/PHY control-system registers under the `dpcssys_cr0_rdpcstxcrind` address block.

The range starts with the MIT license and include guard, then defines 2,158 `#define` lines: 1,099 `__SHIFT` macros and 1,075 `_MASK` macros. It covers the CR0 supervisor PLL/reference-clock/control families, RTUNE and bandgap/reference timing controls, lane 0 TX/status/analog controls, and the beginning of lane 1 TX/RX controls. The chunk ends mid-register at `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, with only its first three masks included; the remaining masks continue after line 2433.

Although this file is stored under a local `ceph-client` source mirror, it is AMDGPU display hardware metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, callbacks, or direct MMIO accesses in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate, preserve, clear, or update that field.

Major register families in this chunk:

- `DPCSSYS_CR0_SUP_DIG_REFCLK_OVRD_IN`, MPLLA/MPLLB divider and HDMI-clock override registers, and `MPLLA/MPLLB_OVRD_IN_*`: reference clock selection, reference-clock range, bandgap enable, HDMI mode, MPLL enable, TX clock dividers, VCO frequency, standby, calibration, fractional-N controls, SSC peak/stepsize, fractional quotient/remainder/denominator, and charge-pump settings.
- `DPCSSYS_CR0_SUP_DIG_*_ASIC_IN*`: ASIC-driven versions of the MPLLA/MPLLB, divider, HDMI, supervisor, level, bandgap, and charge-pump control inputs. These mirror many override fields without the override-enable bits.
- `DPCSSYS_CR0_SUP_DIG_MPLLA/MPLLB_MPLL_PWR_CTL_*`: MPLL power-controller override, state/status, DAC max range, lock/stable timers, PCLK enable/disable timers, calibration override, analog DAC output, and SSC spread-type control.
- `DPCSSYS_CR0_SUP_DIG_CLK_RST_*` and `RTUNE_*`: bandgap/reference power-up timing, reference VPHUD, resistor-tuning configuration/status, RX/TX set values and status values, RTUNE timing counters, and TX calibration code.
- `DPCSSYS_CR0_SUP_DIG_ANA_*`: analog output controls and status for MPLLA/MPLLB clocks, resets, output enables, charge-pump values, RTUNE output, bandgap output, and PMIX overrides.
- `DPCSSYS_CR0_LANE0_*`: lane 0 lane-loopback controls, TX override input/output fields, ASIC TX inputs/outputs, RX status output, master-lane and digital-clock coordination fields, TX power-state P0/P0S/P1/P2 programming, TX power-up timing, DCC DAC/bank access, clock-alignment, LBERT control, RX statistic/match/counter controls, analog TX override/status, TX termination/equalization/DCC DAC controls, and reserved analog TX registers.
- `DPCSSYS_CR0_LANE1_*`: lane 1 lane-loopback controls, TX override input/output fields, RX override input/equalization fields, ASIC TX/RX inputs/outputs, RX CDR/VCO inputs, OCLA enable, TX power-state/timing/DCC/clock-align/LBERT controls, and the start of RX power-state P0.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU Display Core and hardware-sequencing code:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this shift/mask header.
2. Register-helper macros and ASIC-specific tables combine matching offsets with these field masks and shifts.
3. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to program or read hardware bitfields.
4. The constants in this chunk determine which CR0 supervisor, PLL, lane TX/RX, analog, DCC, statistic, and diagnostic bits are touched during link bring-up, training, power-state transitions, PHY tuning, and diagnostics.

The macros do not encode programming order. Consumers must still follow hardware sequencing for reference-clock and bandgap bring-up, MPLL power and lock polling, RTUNE request/ack handshakes, lane power-state changes, TX/RX reset ordering, DCC DAC programming, analog equalization updates, statistic counter sampling, and status/acknowledge reads.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware-backed DPCS state:

- Supervisor state includes reference-clock source/range, bandgap enable/state, prescaler controls, RTUNE request/ack/status, level controls, and reference/bandgap power-up timers.
- PLL state includes MPLLA/MPLLB enable, dividers, HDMI/div clocks, VCO and fractional-N settings, SSC parameters, charge-pump values, power-controller FSM state, lock status, calibration state, DAC values, and stable/lock timers.
- Lane TX state includes request/ack, data enable, P-state/rate/width, MPLL selection, main/pre/post cursor values, beacon, async drive, detect-RX request/result, clock-ready, reset, low-power disable, DC coupling, FIFO mode, MPHY mode, lane-master coordination, power-state programming, DCC DAC access, clock alignment, LBERT mode, analog TX controls, termination code, equalization pull/dir fields, DCC calibration, and analog status.
- Lane RX state in this range includes RX override/ASIC input fields for request, data enable, reset, polarity, P-state/rate/width, adaptation controls, CDR tracking/SSC, alignment, term controls, PWM and termination low-current controls, CDR/VCO load values, RX output status, and lane 1 RX P0 power-state fields at the boundary.
- Diagnostic state includes RX statistic sample/count/match controls for lane 0, DCC DAC acknowledge/address/data fields, LBERT pattern/error-trigger controls, and OCLA clock/data enables for lane 1.

Persistence is hardware-defined. Configuration fields generally survive until rewritten, reset, power-gated, suspend/resume reinitialized, or GPU reset. Status, acknowledgement, request, done, calibration, counter, and self-clearing fields may be transient, sticky, write-one-to-clear, read-only, or valid only while their clock/power domains are active. This generated header does not express those access semantics.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DPCS 3.1.4 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` provides matching `ixDPCSSYS_*` register offsets for the field-bearing registers in this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes both `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`, making this slice part of the DCN 3.1.4 display resource/register interface.
- Shared AMD display register helpers included by the resource code, especially `reg_helper.h`, consume these generated masks and shifts through register-field tables and token-pasted field names.

Behaviorally, this chunk sits at the PHY/link integration boundary for DCN 3.1.4 display output. It supports register access for reference clocks, MPLL A/B programming, HDMI/DP clocking, lane TX/RX control, analog TX/RX tuning, DCC/RTUNE calibration, link-test diagnostics, and per-lane power sequencing.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly while updating the wrong hardware bit.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the offset header, silicon documentation, and firmware or display-core assumptions.
- The chunk boundary is artificial. The final register, `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, is incomplete in this slice; the merge lane needs the following chunk before making full claims about lane 1 RX P0 power-state masks.
- Many fields are override pairs where a value bit is adjacent to an `*_OVRD_EN` bit. Confusing the two can leave hardware using ASIC defaults, force stale debug values, or unexpectedly override autonomous PHY control.
- PLL and clock fields are link-critical. Incorrect MPLL enable/divider/VCO/fractional/SSC/charge-pump masks can cause link-training failure, unstable clocks, HDMI timing errors, blank displays, or power-state hangs.
- Power-controller and timer masks affect sequencing. Bad lock/stable/PCLK/power-down timer fields can create resume-only failures, intermittent link bring-up, or calibration races.
- RTUNE and DCC calibration fields affect analog signal quality. Incorrect request/ack, set-value, DAC, range, selector, or calibration-control masks can produce poor eye margins, RX detect failures, or misleading calibration status.
- Lane TX/RX override and ASIC fields are repeated across lanes but not completely symmetric in this range. Testing only lane 0 could miss lane 1-specific RX override, CDR/VCO, OCLA, or RX power-state mistakes.
- Diagnostic fields such as statistics counters, LBERT, OCLA, and analog status are easy to treat as harmless, but bad masks can corrupt test setup or hide link-quality failures.
- Reserved-field masks are present throughout the chunk. Consumers should preserve reserved bits unless the hardware specification explicitly requires a value; this header does not describe reset values or side effects.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 3.1.4 display/link behavior:

- Build AMDGPU display support with DCN 3.1.4 enabled. Missing or renamed DPCS macros should surface in resource/register-table construction around `dcn314_resource.c`.
- Cross-check this range against `dpcs_3_1_4_offset.h` so every field-bearing `DPCSSYS_CR0_*` register in the slice has the expected matching `ixDPCSSYS_CR0_*` offset.
- Mechanically verify paired `_MASK` and `__SHIFT` definitions for all complete registers in the range, while allowing the known boundary exception at `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`.
- Diff the slice against AMD's authoritative DPCS 3.1.4 register database or a trusted generated source. Repeated MPLLA/MPLLB and lane0/lane1 register families should match expected hardware schemas.
- Exercise display link bring-up across supported DP/HDMI modes, including high-rate modes, suspend/resume, hot replug, and GPU reset. Watch for link-training failures, blanking, PLL lock timeouts, and clock instability.
- Exercise lane power-state transitions P0/P0S/P1/P2, RX detect, low-power entry/exit, and reset sequencing on all available lanes.
- Run PHY tuning and calibration paths that touch RTUNE, DCC DAC, TX main/pre/post cursor, TX termination, equalization, CDR/VCO, and analog status fields. Expected signals are stable link margins and sane calibration acknowledgements.
- Use diagnostics where available: lane statistics counters, LBERT patterns/error injection, OCLA enable, analog status readback, and DCC DAC acknowledge/address/data paths.
- Monitor kernel logs and display-debug traces for AUX/link-training failures, PLL lock or calibration timeout messages, intermittent resume issues, lane-specific failures, and connector modes that only fail under HDMI mode or high data rates.

## Cross-Chunk Notes

This chunk owns the start of `dpcs_3_1_4_sh_mask.h`: license, include guard, the `dpcssys_cr0_rdpcstxcrind` address-block comment, all early CR0 supervisor/MPLL/RTUNE definitions, complete lane 0 TX/status/analog groups in this range, and the beginning of lane 1 TX/RX groups. It ends after `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0__RESERVED_1_MASK`; the following chunk must provide the rest of that register and later lane 1 RX power/control definitions before the final per-file report summarizes complete DPCS 3.1.4 coverage.

### subset-b-002260: lines 2434-4853

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 2434-4853

## Purpose

This chunk is generated AMD DPCS 3.1.4 register field metadata. It exports C preprocessor constants only; each useful symbol is either a hardware field bit offset (`...__SHIFT`) or a pre-shifted bit mask (`..._MASK`) for DPCSSYS CR0 lane registers. Runtime AMD display code pairs these constants with `dpcs_3_1_4_offset.h` and register-helper macros to compose indexed DPCS/PHY register reads and writes without embedding numeric bit positions in the driver logic.

The requested range is a lane-oriented PHY slice. It begins inside `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`, covers the rest of lane 1 RX/analog/debug field definitions, covers lane 2 ASIC/TX/RX field definitions through RX statistic counters, and ends after `DPCSSYS_CR0_LANE2_DIG_RX_STAT_STAT_CNT_4`. The slice contains 2,158 `#define` lines: 1,075 `__SHIFT` definitions and 1,083 `_MASK` definitions. The imbalance is expected for this line-bounded chunk because the first visible register started before line 2434; the chunk includes masks for fields whose shift definitions are partly in the preceding chunk.

Although the repository path is under a `ceph-client` source tree mirror, this file is AMDGPU display-driver hardware metadata and has no distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, callbacks, or includes in this chunk. Its interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`: zero-based bit position for a field in a 16-bit-style DPCS/PHY register.
- `<REGISTER>__<FIELD>_MASK`: field mask already shifted into register position, usually with an `L` suffix.

The important register families in this range are:

- `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX p-state and power-up timing fields for analog AFE, clock/VREG, DESER, CDR, VCO frequency/calibration reset, continuous calibration, digital clock enable, and timing controls such as AFE/VREG/clock/rate/CDR/DESER enable waits.
- `DPCSSYS_CR0_LANE1_DIG_RX_VCOCAL_*`, `*_RX_CDR_*`, and `*_RX_DPLL_*`: lane 1 RX VCO calibration control/status/timing, CDR control/status, DPLL frequency, and DPLL bounds. Fields include calibration fixed counts, skip controls, startup/update/settle timing, VCO tuning/status, CDR PI update/gain controls, lock status, and frequency limits.
- `DPCSSYS_CR0_LANE1_DIG_RX_ADPTCTL_*`: lane 1 RX adaptation configuration and status for ATT, VGA, CTLE, DFE taps, VDAC offsets, slicer controls, error slicer levels, adaptation reset, DAC selector fields, and CR bank address/data.
- `DPCSSYS_CR0_LANE1_DIG_RX_STAT_*`: lane 1 statistic/match/sample/counter controls, including pattern masks, statistic/correlation source selection, counter enables, sample-done flags, calibration comparator clock controls, match controls, and stop controls.
- `DPCSSYS_CR0_LANE1_DIG_MPHY_*` and `DPCSSYS_CR0_LANE1_DIG_ANA_*`: lane 1 low-speed MPHY RX controls and digital-to-analog override/status fields for TX/RX power, termination, equalization, VCO, calibration, DAC selection, AFE/CTLE, scope, slicer, IQ/phase adjustment, signal detect, DCC DAC, and analog status readback.
- `DPCSSYS_CR0_LANE1_ANA_TX_*` and `DPCSSYS_CR0_LANE1_ANA_RX_*`: lane 1 analog register fields for TX override measurement, TX power override, alternate bus/ATB paths, DCC DAC, termination code/control, miscellaneous TX controls, RX power/squelch/calibration, and RX ATB measurements.
- `DPCSSYS_CR0_LANE2_DIG_ASIC_*`: lane 2 ASIC interface and override fields for lane loopback, enable, RX AC JTAG, TX/RX p-state and request signaling, rate/width, MPLLB selection, data enable, cursor settings, HDMI mode, clock readiness, RX detect, polarity, low-power detect, DC coupling, MPHY mode, reset, boost/equalization, signal detect, VCO/DAC controls, and status readback.
- `DPCSSYS_CR0_LANE2_DIG_TX_PWRCTL_*`, `*_TX_CLK_ALIGN_*`, and `*_TX_LBERT_*`: lane 2 TX p-state fields, TX power-up delays, TX DCC CR bank/DAC controls, clock alignment controls, and loopback/BER test controls.
- `DPCSSYS_CR0_LANE2_DIG_RX_PWRCTL_*`, `*_RX_VCOCAL_*`, `*_RX_CDR_*`, and `*_RX_DPLL_*`: lane 2 RX p-state/power timing, VCO calibration, CDR, DPLL, XAUI comma mask, and LBERT definitions, mirroring the lane 1 RX digital block with lane 2 names.
- `DPCSSYS_CR0_LANE2_DIG_RX_ADPTCTL_*` and `DPCSSYS_CR0_LANE2_DIG_RX_STAT_*`: lane 2 RX adaptation and statistics fields through `STAT_CNT_4` in this chunk. Remaining lane 2 statistic counter definitions continue after this range.

Most masks are small 16-bit hardware fields such as `0x0001L`, `0x00FFL`, `0x7FFFL`, or `0xFFFFL`, reflecting DPCS CR register layout rather than broad 32-bit display-pipe registers.

## Control Flow

This header has no direct control flow. Runtime behavior is created by consumers:

1. DCN 3.1.4 display resource code includes `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`.
2. ASIC-specific register tables and token-pasting helper macros combine register names, field names, offsets, shifts, and masks.
3. Link, PHY, power-management, diagnostics, and bring-up code uses those generated symbols through register helpers to read, write, update, or poll DPCS fields.
4. Hardware and firmware sequencing decides when lane p-state, rate, CDR/DPLL/VCO calibration, RX adaptation, TX DCC, loopback, status counter, and analog override fields are programmed.

The macros do not encode sequencing rules. They do not identify whether a field is read-only, sticky, write-one-to-clear, timing-sensitive, reset-sensitive, or safe to modify while a link is active. Those semantics must come from AMD hardware specifications and the driver code that consumes the register database.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes hardware-backed lane state:

- RX and TX power-state programming for lane 1 RX and lane 2 TX/RX p-states, including analog enables, clocks, VREG, CDR, DESER, VCO reset/calibration, and power-up timing.
- Clock-recovery state for VCO calibration, CDR control/status, DPLL frequency and bounds, lock indication, and calibration counters.
- RX equalization/adaptation state for ATT/VGA/CTLE/DFE tap settings, slicer levels, VDAC offsets, adaptation reset, and adaptation done/status bits.
- Diagnostic state for LBERT controls/errors, XAUI comma mask, statistic match/counter/sample controls, CR bank address/data access, ATB/analog measurement muxes, and OCLA-related lane 2 control.
- Analog override and status state for TX/RX termination, DCC DAC, equalization, signal detect, MPHY low-speed controls, DAC selectors, scope/slicer controls, phase/IQ adjustment, and analog status readback.

Persistence is device-local and reset/power-domain dependent. Values can survive until a modeset, link retrain, lane reset, power-gate transition, suspend/resume, or ASIC reset. Status/counter fields may change asynchronously as the physical lane trains, calibrates, enters low power, receives data, runs diagnostics, or exposes analog test paths.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which provides the indexed register addresses. Examples from the matching offset range are lane 1 RX power/control registers at `0x1140` through the lane 1 analog RX/ATB area, and lane 2 ASIC/TX/RX registers beginning at `0x1200` with lane 2 RX adaptation registers at `0x1260` through `0x127f`.

The known include point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which includes both the DCN 3.1.4 and DPCS 3.1.4 offset/mask headers before `reg_helper.h`. That makes these macros part of DCN314 resource initialization and register-table construction.

Functional integration is with the AMD display core rather than Ceph code. These fields support DisplayPort/PHY lane setup, lane-rate and p-state programming, link training, clock recovery, RX adaptation, analog trim/override, diagnostic counters, loopback/BERT paths, and manufacturing/debug access. The repeated `LANE1` and `LANE2` prefixes are part of the register-table naming contract; adjacent lane chunks should contain the corresponding lane 0/3 definitions.

## Risks And Edge Cases

- Shift/mask drift is high risk. These are untyped compile-time constants, so an incorrect bit position can compile cleanly while programming or reading the wrong PHY field.
- Offset/header mismatch can apply a correct mask to the wrong indexed register address. The mask header must stay synchronized with `dpcs_3_1_4_offset.h` and any generated register-table macros.
- Lane-instance mistakes are easy to miss. A `LANE1` versus `LANE2` table or copy error may only appear on links that use the affected physical lane.
- Override-enable fields are hazardous. `*_OVRD_EN`, power override, reset override, loopback, termination, equalization, DCC DAC, VCO, CDR, DPLL, and analog mux fields can force hardware away from normal sequencing.
- Status, counter, ack, and calibration fields may have side effects or timing requirements not represented here. Wrong masks can cause polling timeouts, lost diagnostic data, stuck calibration flows, or false link-training decisions.
- Boundary incompleteness matters for this research chunk. It starts after several `RX_PSTATE_P0` shift definitions and ends before later lane 2 statistic counter groups, so full per-register validation must include neighboring chunks.
- Constants use `L` suffixes and are often 16-bit masks; consumers should preserve expected unsigned extraction/update behavior and avoid sign or width assumptions when composing field values.

## Test Signals

Useful validation signals are a mix of generated-header consistency and hardware behavior:

- Build AMDGPU/DC with DCN314 support enabled so `dcn314_resource.c` and any register-table expansions catch missing, renamed, or malformed macros.
- Mechanically verify that every register field has a coherent `__SHIFT` and `_MASK` pair after merging adjacent chunks. For this exact line range, 1,075 shifts and 1,083 masks are expected because the start boundary is mid-register.
- Cross-check masks against `dpcs_3_1_4_offset.h` and neighboring lane definitions. Lane 1 and lane 2 repeated blocks should match where hardware layout is lane-replicated, while intentional omissions such as continuation past `STAT_CNT_4` should be handled at merge time.
- Exercise display links using the affected lanes: link training across lane counts and rates, hotplug, suspend/resume, p-state transitions, low-power entry/exit, and retraining after mode changes.
- Run PHY diagnostic paths where available: LBERT/loopback, statistic counters, CDR/DPLL/VCO calibration polling, RX adaptation status reads, DCC DAC access, and analog status/ATB measurement paths.
- Watch kernel logs and display diagnostics for lane-specific training failures, repeated retraining, stuck calibration or power-status bits, signal-detect failures, invalid counter reads, or display instability that points to an incorrect generated field definition.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR0_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`. The following chunk continues after lane 2 RX statistic counter 4 with additional lane 2 statistic and later DPCS definitions. The final per-file report should reconcile adjacent chunks before making complete claims about all registers in `dpcs_3_1_4_sh_mask.h`.

### subset-b-002261: lines 4854-7300

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h Lines 4854-7300

## Scope

This chunk is a generated AMD DPCS 3.1.4 register shift/mask header slice. It covers the end of CR0 lane 2 RX statistic and analog-control fields, a broad CR0 lane 3 lane-control and TX/RX statistic subset, CR0 raw-common PLL/retune/power-gating fields, and the start of CR0 raw lane 0 PCS/FSM/IRQ/PMA crossbar fields. The file provides C preprocessor constants only; it defines no functions, structs, storage, or executable control flow.

## Purpose

The macros provide bit positions (`__SHIFT`) and bit masks (`_MASK`) for programming or decoding 16-bit DPCS indirect registers. They are consumed together with the matching offset header, especially `dpcs_3_1_4_offset.h`, whose `ixDPCSSYS_...` constants name the register addresses. Display link code can then use local register-field helpers such as `LE_SF(register, field, mask_sh)` to populate register metadata tables from the generated mask/shift names.

Operationally, this range exposes controls for:

- RX statistic matching and sampling counters on lanes 2 and 3.
- Lane 2 analog TX/RX override outputs, term-code clocks, EQ/pre/post controls, VCO/calibration/DAC/slicer/scope status, signal-detect override, and MPHY/PWM controls.
- Lane 3 ASIC-facing TX/RX override and observation fields, TX power-state sequencing, DCC DAC programming, TX LBERT/clock alignment, RX statistic blocks, and analog TX overrides.
- Raw common PLL and always-on common controls for MPLLA/MPLLB override, bandwidth, spread-spectrum, retune values, SRAM bootload, power gating, reference range, VREF, and resource handshake.
- Raw lane 0 PCS transfer, adaptation, ATE, FSM fast-state, calibration, interrupt, clear, mask, and PMA lane override fields.

## Important Macro Families

The lane 2 section starts in the middle of `DPCSSYS_CR0_LANE2_DIG_RX_STAT_STAT_CNT_4` and continues with `STAT_CNT_5`, `STAT_CNT_6`, `RX_STAT_CAL_COMP_CLK_CTL`, `RX_STAT_MATCH_CTL2` through `MATCH_CTL5`, `STAT_CTL2`, and `STAT_STOP`. These provide statistic counter fields, sample-done bits, pattern/mask slices, delay controls, and stop controls for RX sampling hardware.

The lane 2 analog block includes `DIG_MPHY_RX_PWM_CTL`, `DIG_MPHY_RX_TERM_LS_CTL`, `DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, `DIG_ANA_TX_OVRD_OUT`, term-code override/clock registers, six TX EQ override registers, RX control/power/VCO/calibration/DAC/AFE/scope/slicer/IQ registers, `DIG_ANA_STATUS_0/1`, signal-detect override, TX DCC DAC override, and low-level `LANE2_ANA_TX_*` / `LANE2_ANA_RX_*` register masks. These fields represent direct analog PHY controls and status, including enable/reset/data-rate bits, termination codes, DCC, pre/main/post/equalization values, AFE/CTLE/slicer settings, and measurement/test-bus selectors.

The lane 3 digital ASIC-facing block begins at `DPCSSYS_CR0_LANE3_DIG_ASIC_LANE_OVRD_IN` and includes TX override inputs `0` through `5`, TX override outputs, RX override outputs, ASIC in/out mirrors, and lane loopback/master-lane controls. It also defines lane 3 TX power control P-states (`P0`, `P0S`, `P1`, `P2`), power-up timing registers, DCC bank/DAC address/data/ack fields, `TX_CLK_ALIGN_TX_CTL_0`, `TX_LBERT_CTL`, and the lane 3 RX statistic registers. These mirror lane-facing state machines and allow software or firmware to override or observe clock-ready, reset, data enable, request/ack, P-state/rate/width, loopback, beacon, HDMI mode, and cursor/equalization state.

The raw common block covers `DPCSSYS_CR0_RAWCMN_DIG_CMN_CTL`, MPLLA/MPLLB override and SSC registers, `LANE_FSM_OP_XTND`, `CMN_CTL_1`, `MPLL_STATE_CTL`, OCLA/debug control, supervisor analog override, firmware ID fields, eight repeated retune value triplets (`RTUNE_RX_VAL_n`, `RTUNE_TXDN_VAL_n`, `RTUNE_TXUP_VAL_n`), SRAM bootload configuration, common power-gate override in/out, supervisor force/ack overrides, VREF status, resource request/ack overrides, reference range override, and miscellaneous MPLL power-down timing. These fields are shared common-lane state rather than per-display-lane state.

The raw lane 0 block begins at `DPCSSYS_CR0_RAWLANE0_DIG_PCS_XF_TX_OVRD_IN` and runs through `DPCSSYS_CR0_RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT` in this chunk. It defines PCS transfer overrides and live PCS inputs/outputs for TX and RX, RX adaptation acknowledgement/FOM and TX pre/main/post direction outputs, lane number, reserved scratch fields, ATE overrides, RX EQ and phase-two calibration controls, FSM override/status/fast-state flags, calibration status flags, interrupt status/clear/mask registers, and PMA lane MPLLA/MPLLB enable override bits.

## Control Flow and State Behavior

There is no executable control flow in this header. Runtime behavior is created by driver code that combines an address macro from the offset header with these masks/shifts to read, write, poll, or compose bitfields.

The hardware state represented here is mostly volatile MMIO or indirect-register state. Some fields are command-like or handshake-oriented: `*_OVRD_EN` bits select software override paths, `*_ACK` and `*_REQ` fields expose handshakes, `*_IRQ_CLR` fields clear sticky interrupt/status bits, `*_DONE` and calibration status fields report hardware progress, and P-state/power-up timing fields configure sequenced PHY state transitions. None of that state persists in this header; persistence, reset defaults, and serialization are determined by the GPU hardware and whatever driver or firmware writes these registers.

## Dependencies and Integration Points

- Depends on consistent generated naming with `dpcs_3_1_4_offset.h`; the register stem before `__FIELD` must match an `ix...` offset macro when driver code emits real accesses.
- Integrated by AMD display/link encoder register tables through macros that expect generated `register__field_MASK` and `register__field__SHIFT` names.
- Shares register naming conventions with other generated ASIC headers such as DCN/DPCS variants, making cross-generation code reuse possible when fields are compatible.
- The constants are plain preprocessor macros, so they are globally visible after inclusion and have no type protection.

## Risks and Edge Cases

- The chunk begins mid-register at line 4854, so the first visible macro is only the `SMPL_CNT1_DONE_MASK` for `STAT_CNT_4`; the corresponding shift and count mask are in the prior chunk.
- Many fields are reserved masks. Driver writes should preserve reserved bits unless hardware documentation explicitly requires otherwise.
- Override-enable fields are high risk because setting `*_OVRD_EN` without matching value bits can disconnect normal hardware/firmware sequencing for clocks, resets, PLLs, power gating, calibration, or lane handshakes.
- Interrupt clear fields are write-sensitive. A stale mask/shift or write-one-clear misunderstanding can drop reset/request/rate/P-state/adaptation/phase-calibration notifications.
- Lane 2, lane 3, raw-common, and raw-lane0 blocks are interleaved in one header slice. Code generation or manual edits that assume a single lane context can bind a valid field name to the wrong register address family.
- Register widths in this slice are represented with 16-bit masks using `L` suffixed literals. Callers using 32-bit register helpers must still preserve the intended lower-16-bit field semantics.

## Test and Validation Signals

Useful validation for this chunk is compile-time and hardware-table oriented rather than unit-test oriented:

- Build AMDGPU display code that includes this generated header and any table macros that reference `DPCSSYS_CR0_RAWLANE0_*`, `DPCSSYS_CR0_LANE2_*`, `DPCSSYS_CR0_LANE3_*`, or `DPCSSYS_CR0_RAWCMN_*` fields.
- Check that every used `LE_SF(...)` or equivalent field helper expands to both a `_MASK` and `__SHIFT` macro.
- Diff generated `dpcs_3_1_4_sh_mask.h` against its register database source when updating ASIC headers; manual edits are especially risky.
- On hardware, monitor link bring-up, lane power-state transitions, PHY calibration completion, RX adaptation, interrupt clear/mask behavior, and DCC/retune status when fields in this range are touched.

## Research Notes

This is a source chunk report only. The later merge lane should combine it with neighboring chunks for the full `dpcs_3_1_4_sh_mask.h` file-level report, preserving that the overall file is a generated DPCS mask/shift catalog rather than handwritten control logic.

### subset-b-002262: lines 7301-9720

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 7301-9720

## Purpose

This chunk is generated AMD DPCS 3.1.4 register field metadata. It contains no executable C logic; it publishes C preprocessor constants for bit shifts and masks inside DPCSSYS CR0 raw-lane registers. Consumers pair these macros with register offsets from `dpcs_3_1_4_offset.h` and with AMD display register helpers to read, write, update, and poll lane-level PHY/PCS/FSM/IRQ state.

The requested range covers a mid-file raw-lane slice. It starts inside the tail of `DPCSSYS_CR0_RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT`, then covers the rest of lane 0 PMA/TX/RX/ATE fields, the full lane 1 PCS/FSM/IRQ/PMA/TX/RX/ATE field groups, and most of the same lane 2 groups through `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN`. The final requested line is only the marker for `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1`; that register's fields continue in the next chunk.

The range contains 2,145 `#define` lines: 1,071 `__SHIFT` definitions and 1,074 `_MASK` definitions. It is split across `RAWLANE0` tail coverage, complete `RAWLANE1` coverage for these blocks, and partial `RAWLANE2` coverage. Although this file lives under a local `ceph-client` source mirror, the content is AMDGPU display hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locking primitives, or local includes in this chunk. The interface is the generated macro namespace:

- `<register>__<field>__SHIFT`: the low bit position of a field inside a 16-bit DPCS indirect register.
- `<register>__<field>_MASK`: the bit mask for the same field.
- Register names use lane-scoped prefixes such as `DPCSSYS_CR0_RAWLANE1_DIG_PCS_XF_...`, `DPCSSYS_CR0_RAWLANE1_DIG_FSM_...`, `DPCSSYS_CR0_RAWLANE1_DIG_IRQ_CTL_...`, and `DPCSSYS_CR0_RAWLANE1_DIG_PMA_XF_...`.

Major field families in this slice:

- `PMA_XF_*`: lane-to-PMA interface override and status fields, including MPLLA/MPLLB lane enable, supervisor state override, TX/RX request and reset override, beacon and async enable override, data-enable override, TX-to-RX and RX-to-TX loopback enable override, retune request/ack, MPHY PWM/term control, RX PMA async/PWM selection, and RX IQ phase-adjust override.
- `TX_CTL_*` and `RX_CTL_*`: lane TX/RX controller controls and status, including TX wait time before MPLL off, whether RX detection is allowed in power states P0/P0s/P1/P2, TX clock enable and selection, async beacon wait time, DCC continuous status, OCLA enables, RX control FSM enable, rate changes in P1, RX loss-of-signal mask count, RX data-enable override delay/count, OFFCAN and adaptation continuous status, and UPCS OCLA data/clock enables.
- `PCS_XF_TX_*` and `PCS_XF_RX_*`: PCS transmit and receive override/status fields for lane state, rate, width, pstate, low-power detect, MPLL selection/enables, TX/RX reset and request signaling, data-valid signaling, TX and RX data enables, async data and beacon controls, serial/parallel loopback controls, RX loss-of-signal thresholding, adaptation/off-cancel controls, VCO/ref load override values, and TX pre/main/post direction outputs.
- `PCS_XF_ATE_*`: ATE-oriented override registers for manufacturing, lab, or low-level bring-up paths. These fields can override rate, width, pstate, LPD, MPLL state, async data, VBOOST, IBOOST, beaconing, RX LOS behavior, RX adaptation requests, continuous adaptation/off-cancel behavior, VCO load values, ref load values, RX valid, and lane loopback/data enable state.
- `FSM_*`: lane finite-state-machine override, monitor, calibration, adaptation, and status fields. Covered registers expose manual memory-address monitor selectors, FSM state/address/running/debug status, fast-path timers for RX startup/adaptation/AFE/DFE/bypass/reference/IQ calibration, supervisor and TX common-mode/RX-detect timing, RX power-up/VCO wait/VCO calibration, common calibration status, continuous RX calibration/adaptation/data/phase/AFE timing, aggregated fast flags, CR lock status, TX DCC flags/status, TX EQ update flags, RCAL status, and RX IQ phase offset.
- `IRQ_CTL_*`: lane interrupt request, clear, and mask fields for RX reset/request/rate/pstate/adaptation, RX phase-2 calibration, lane transceiver mode, loopback, DCC on-demand, TX reset/request, and the combined IRQ masks. Many individual IRQ and IRQ clear registers in this chunk are single-bit fields.
- `PCS_XF_TXRX_TERM_*` and `PCS_XF_RX_EQ_*`: TX/RX termination control, RX EQ delta IQ override, FFE/DCO adaptation override, VGA override, and phase-2 calibration control fields.

Reserved-field macros are generated alongside active fields. They are not API invitations to write reserved bits; they document layout and let generated code or diagnostics mask whole register widths when needed.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this `dpcs_3_1_4_sh_mask.h`.
2. Register helper macros and generated register-field tables token-paste register and field names into constants such as `DPCSSYS_CR0_RAWLANE1_DIG_PCS_XF_RX_OVRD_IN_2__VCO_LD_VAL_OVRD_MASK`.
3. The companion offset header provides `ixDPCSSYS_CR0_RAWLANE<n>_...` register indices. This mask header provides field placement within those indirect registers.
4. Link encoder, PHY bring-up, link training, diagnostics, IRQ handling, and low-level display code use `REG_SET`, `REG_UPDATE`, `REG_GET`, read-modify-write helpers, and poll/wait helpers to apply or inspect the represented fields.

The macros do not encode ordering. Consumers must still sequence PLL enablement, power-state transitions, TX/RX reset handshakes, RX detection, link training, clock gating, calibration/adaptation, retuning, IRQ clear/mask operations, loopback setup, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes MMIO or indirect-register-backed GPU state. The represented hardware state includes:

- Per-lane PCS state for TX/RX request, reset, pstate, LPD, width, rate, MPLL selection, MPLL state, async data, beaconing, loopback, data-enable, RX-valid, RX LOS, and adaptation signaling.
- Per-lane PMA interface state for lane MPLL enables, PMA supervisor state, TX/RX requests and acks, retune handshakes, PWM and termination controls, RX async selection, and IQ phase-adjust override.
- Calibration and adaptation control/status state for RX startup, AFE/DFE/reference/IQ calibration, continuous adaptation/calibration, VCO and common calibration status, DCC status, TX EQ update indication, RCAL status, and CR lock.
- Per-lane interrupt state for request, clear, and mask paths. Several fields are likely sticky, write-one-to-clear, or clear-on-read depending on the hardware register, but this generated mask header does not encode those side effects.
- Test, lab, or bring-up override state through ATE registers and OCLA observability controls.

Persistence is hardware-defined. Control fields generally retain values until the lane block is reprogrammed, power-gated, reset, or the GPU enters a suspend/resume or ASIC reset path. Status, IRQ, clear, ack, monitor, and calibration fields may be volatile or side-effect-sensitive. The generated shift/mask file deliberately does not classify fields as read-only, write-only, sticky, self-clearing, or write-one-to-clear.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 3.1.4 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which gives the `ixDPCSSYS_CR0_RAWLANE<n>_...` register indices. The offsets show the lane stride used by these masks, for example lane 0 at `0x3000`-style addresses, lane 1 at `0x3100`-style addresses, and lane 2 at `0x3200`-style addresses for these register families.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which directly includes this header together with the matching DPCS offset header and the DCN 3.1.4 register headers.
- AMD display register helper infrastructure such as `reg_helper.h` and the generated field-table macros that consume `*_MASK` and `*__SHIFT` definitions.

The broader integration point is the DCN/DPCS display link stack. These fields are lane-local primitives beneath link encoder setup, DisplayPort and HDMI PHY programming, power sequencing, training pattern handling, RX detection, AUX-related link bring-up, diagnostics, and IRQ processing. Other ASIC generations in this tree use the same naming pattern, so drift from neighboring generated headers can be detected mechanically, but the authoritative contract for this ASIC generation is the `dpcs_3_1_4_*` pair.

## Risks And Edge Cases

- Generated metadata drift is the central risk. A wrong mask or shift can compile cleanly while causing writes to the wrong bit, partial writes to a multi-bit field, broken reads, stuck status polling, or reserved-bit writes.
- The chunk is lane-repetitive and copy-sensitive. Lane 1 and lane 2 should generally preserve the same field layout for corresponding registers, while lane 0 coverage is split across neighboring chunks. A single lane-specific typo may only fail on some link-lane counts, connector mappings, link rates, or training patterns.
- Chunk boundaries are artificial. The range begins after the start of `RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT` and ends before the fields for `RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1`; adjacent chunks are required before making complete per-file claims.
- Override fields are high risk because many pairs use a value bit plus an enable bit. Setting an override value without its enable may do nothing; setting an enable with a stale value can force a lane into an unintended rate, width, pstate, reset, async, data-enable, or loopback state.
- IRQ clear and mask fields are side-effect-sensitive. Incorrect shifts can leave interrupts stuck, clear the wrong condition, mask real link faults, or produce hotplug/link-training instability that only appears under error paths.
- Calibration and adaptation fields are timing-sensitive. Bad fast-timer, continuous-adaptation, VCO, IQ, AFE, DFE, DCC, or RCAL fields can cause intermittent link failures, marginal signal integrity, or resume-only regressions.
- Reserved masks exist in the generated header, but writing reserved bits remains unsafe unless the consuming code has a hardware-specific reason.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN 3.1.4 support enabled. Missing or renamed macros should fail in `dcn314_resource.c` and any generated register-field table that references DPCS fields.
- Mechanically verify that every active field in lines 7301-9720 has exactly one `__SHIFT` and one `_MASK`, allowing for the known chunk-boundary exceptions at the beginning and end.
- Cross-check corresponding lane 1 and lane 2 registers for identical field layouts where the hardware register names match, and compare lane 0 fields by merging adjacent chunks.
- Diff this range against AMD's authoritative DPCS 3.1.4 database or nearby generated headers such as `dpcs_3_0_3_sh_mask.h`, `dpcs_4_0_0_sh_mask.h`, and `dpcs_4_2_0_sh_mask.h` where compatibility is expected.
- Exercise display paths that use different physical lanes and lane counts: 1-lane, 2-lane, and 4-lane DisplayPort where available; HDMI/FRL or TMDS modes where applicable; link-rate changes; training retries; lane remapping; and suspend/resume.
- Validate IRQ behavior by observing RX reset/request/rate/pstate/adaptation events, RX phase-2 calibration events, lane transceiver mode events, loopback events, DCC on-demand events, and TX reset/request events. Look for stuck IRQs, missed clears, and unexpected masks.
- Run signal-integrity and link-stability checks around RX detection, retune, continuous adaptation, DCC, VCO calibration, TX EQ updates, loopback modes, and high-rate modes. Kernel logs should be watched for link-training failures, AUX or DPCD errors caused by failed link bring-up, display blanking, CRC mismatch, underflow, and resume failures.

## Cross-Chunk Notes

Previous chunks are needed for the beginning of `RAWLANE0_DIG_PMA_XF_LANE_OVRD_OUT` and the earlier lane 0 PCS/FSM/IRQ fields. Later chunks are needed for `RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1` and the remaining DPCS 3.1.4 register-field namespace. The final per-file research document should merge those chunks before claiming full coverage of all raw lanes or the complete `dpcs_3_1_4_sh_mask.h` header.

### subset-b-002263: lines 9721-12191

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 9721-12191

## Scope

This chunk is part of the generated AMD DPCS 3.1.4 ASIC register shift/mask header. It contains preprocessor constants only: each hardware bitfield is represented by a `...__SHIFT` bit offset and a matching `..._MASK` bit mask. There are no C functions, structs, branches, dynamic allocations, locks, direct MMIO operations, or file-backed persistence mechanisms in this range.

The slice contains 2,111 `#define` entries: 1,056 shift definitions and 1,055 mask definitions, organized under 360 register-comment blocks. It starts in the middle of the `DPCSSYS_CR0_RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1` mask/shift family and ends in the middle of `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QDF_CODE_0`, so neighboring chunks are needed to reconstruct both boundary registers completely.

Major block coverage in this chunk:

- Tail of `RAWLANE2` PCS transfer override fields.
- Full `RAWLANE3` PCS transfer, RX/TX PCS, ATE override, equalization, FSM, IRQ, PMA transfer, TX control, and RX control field families.
- Always-on lane register families for `RAWAONLANE0` and `RAWAONLANE1`.
- Opening portion of `RAWAONLANE2`, through RX DCC calibration code register fields.

## Purpose

The purpose of this header slice is to publish exact bit positions and masks for AMD display PHY/DPCS lane registers. Runtime driver code combines these constants with companion DPCS register-address headers and AMD register-helper macros to perform masked reads, writes, updates, and polling without embedding raw bit arithmetic at call sites.

The represented hardware area is PHY/lane-oriented rather than high-level display-pipe composition. It covers per-lane PCS control, RX adaptation/calibration, TX/RX reset and request handshakes, loopback and test overrides, PMA interface state, interrupt status/mask/clear fields, and always-on calibration/status/configuration registers. The constants are compile-time metadata; the real behavior occurs when AMDGPU display code programs the matching hardware registers.

## Important Macros and Field Families

The exported API is the generated naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset within a 16-bit register image.
- `<REGISTER>__<FIELD>_MASK` gives the pre-shifted bit mask for preserving or updating that field.
- Prefixes such as `DPCSSYS_CR0_RAWLANE3_DIG_*` and `DPCSSYS_CR0_RAWAONLANE1_DIG_*` are semantically important because they bind the same logical field families to a specific DPCS instance or lane namespace.

Important register families in this chunk include:

- `RAWLANE2_DIG_PCS_XF_*`: the tail of lane 2 PCS ATE/TX/RX override metadata, including DETRX request, voltage/current boost, TX beacon, serial loopback, async data, master MPLL loop enable, RX LOS/adaptation overrides, VCO/reference lock override fields, RX-valid override, and TX data/async override fields.
- `RAWLANE3_DIG_PCS_XF_TX_*`: lane 3 TX PCS input, override input/output, PCS output, reset/request state, P-state, low-power detect, width/rate, MPLL selection/enables, master MPLL state, DETRX, TX data enable, async enable/data, beacon, and TX-to-RX serial loopback metadata.
- `RAWLANE3_DIG_PCS_XF_RX_*`: lane 3 RX PCS and override fields for reset/request, P-state, rate, MPLL selection/enables, adaptation request/disable/continue, off-cancellation continue, RX data enable, RX-to-TX serial loopback, TX pre/main/post cursor direction values, lane number, ATE override fields, RX equalization delta IQ overrides, TX/RX termination control, RX LOS threshold/valid overrides, RX adaptation FOM/ack, and phase-2 calibration fields.
- `RAWLANE3_DIG_FSM_*`: finite-state-machine control and monitor fields for override control, memory address/status monitors, fast RX startup/adaptation/calibration flags, common calibration status, continuous calibration/adaptation flags, CR lock, TX DCC flags/status, OCLA debug hooks, TX EQ update flags, RCAL status, and RX IQ phase offset.
- `RAWLANE3_DIG_IRQ_CTL_*`: interrupt request, clear, and mask fields for RX reset/request/rate/P-state/adaptation events, lane transceiver mode events, RX phase-2 calibration events, RX-to-TX serial loopback events, DCC on-demand, and TX reset/request events.
- `RAWLANE3_DIG_PMA_XF_*`: PMA interface metadata for lane, supervisor, TX, RX, MPHY, lane retune, and RX adaptation override/incoming fields. These constants describe PMA-facing reset, request, acknowledge, power, PLL, signal-detect, termination, calibration, loopback, and adaptation wires exposed through DPCS registers.
- `RAWLANE3_DIG_TX_CTL_*` and `RAWLANE3_DIG_RX_CTL_*`: lane-local TX/RX control metadata for TX FSM and clock control, TX DCC continuous status, OCLA/UPCS debug paths, RX FSM control, RX LOS mask timing, RX data enable override, and continuous off-cancellation/adaptation status.
- `RAWAONLANE0/1/2_DIG_*`: always-on per-lane calibration/status/configuration fields, including AFE/CTLE/DFE offset registers, RX adaptation IQ/FOM/ATT/VGA/CTLE/DFE tap values, DFE reference levels, phase adjust linear/map fields, MPLL coarse tune, initial power-up done, fast flags, slicer control, common calibration MPLL/RCAL status, adaptation control registers, MPLL disable, TX/RX disable override, RX LOS/signal-detect filtering, RX PMA override outputs, RX signal-detect calibration and code fields, RX VREF generator enable, RX DCC calibration code fields, TX DCC bank/configuration fields, MPLL bandgap control, signal-detect output override/input, firmware MM/adaptation/calibration configuration, lane transceiver mode override/input, RX signal-detect configuration, and TX DCC configuration. This chunk fully covers lane 0 and lane 1 instances and begins the same pattern for lane 2.

## Control Flow and Runtime Integration

There is no executable control flow in this file. Runtime behavior is indirect:

1. DPCS 3.1.4 display/PHY code includes this shift/mask header together with matching generated register-address headers.
2. Register helper macros pair an address or indirect index with the `__SHIFT` and `_MASK` constants from this file.
3. Driver code reads, writes, updates, or polls individual fields while bringing up lanes, training links, calibrating RX/TX paths, entering or leaving low-power states, servicing PHY interrupts, and collecting debug status.
4. Hardware registers hold the actual lane state; this header only describes how to isolate each field.

The represented operational flow is typically lane bring-up and maintenance: reset/request handshakes are asserted through PCS/PMA-facing fields, PLL and rate/width state are selected, RX detection and adaptation are requested, calibration FSM status and IRQs are observed or cleared, PMA override paths are used for test or bring-up modes, and always-on calibration/status registers retain lane-local tuning state across parts of the PHY power sequence.

## State and Persistence Behavior

The file itself has no mutable state. It contributes compile-time constants to the kernel build.

The hardware state represented by this chunk includes:

- PCS lane state: TX/RX reset, request, acknowledge, P-state, rate, width, low-power detect, MPLL selection/enables, DETRX, TX data/async controls, RX valid/data enable, loopback, and adaptation request/ack/FOM state.
- Calibration and adaptation state: RX adaptation IQ/FOM values, ATT/VGA/CTLE/DFE tap values, DFE reference and offset codes, phase-adjust values, RX VCO/reference lock overrides, RX LOS thresholds, signal-detect calibration/tune codes, RX DCC calibration codes, TX DCC status and banked data, common MPLL/RCAL status, and fast/continuous calibration flags.
- PMA-facing state: PMA reset/request/acknowledge wires, supervisor PMA input, lane retune controls, MPHY override state, RX adaptation override outputs, termination controls, signal-detect controls, and VREF generator controls.
- Event state: IRQ request, mask, and clear registers for lane reset/request/rate/P-state/adaptation, transceiver mode, phase-2 calibration, loopback, DCC on-demand, and TX reset/request events.
- Debug and observability state: FSM memory/status monitors, OCLA and UPCS OCLA hooks, TX/RX continuous status fields, CR lock, initial power-up done, signal-detect input/output mirrors, and firmware configuration fields.

Persistence is hardware scoped. Register values may survive some local block transitions but should be treated as volatile across GPU reset, display engine reset, DPCS/PHY reset, power gating, suspend/resume, hotplug retraining, and mode/link reconfiguration. Higher-level AMDGPU display state and firmware sequencing remain the source of truth; this header does not store policy or restore values.

## Dependencies

This chunk depends on the companion generated DPCS 3.1.4 register address/index headers. Shift and mask constants alone do not identify an MMIO address or indirect register selector.

It also depends on:

- AMDGPU/DC register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked register access.
- Silicon register database inputs used to generate the DPCS 3.1.4 headers.
- Display PHY, link encoder, DisplayPort/HDMI link-training, AUX/hotplug recovery, power-management, diagnostics, and firmware-coordination code that programs DPCS lane registers.
- Correct instance mapping between `RAWLANE2`, `RAWLANE3`, and `RAWAONLANE0/1/2` prefixes and the hardware lanes/register address spaces in companion headers.

Because this is generated silicon metadata, manual edits are high risk unless synchronized with the register database, matching offset headers, generated register tables, and all call sites using the field names.

## Integration Points

Primary integration points are macro references in AMD display code and generated register tables. A consumer that names a field such as `DPCSSYS_CR0_RAWLANE3_DIG_PCS_XF_RX_PCS_IN__RATE`, `DPCSSYS_CR0_RAWLANE3_DIG_IRQ_CTL_IRQ_MASK__RX_REQ_IRQ_MASK`, or `DPCSSYS_CR0_RAWAONLANE1_DIG_RX_ADPT_DFE_TAP1__VAL` relies on this header to provide the exact bit location and mask.

Integration surfaces include:

- Lane bring-up and reset sequencing: PCS/PMA reset, request, acknowledge, P-state, rate/width, MPLL selection, master MPLL loop state, and initial power-up done fields.
- Link training and adaptation: DETRX request/result, RX adaptation request/disable/continue, RX adaptation FOM/ack, TX pre/main/post direction controls, RX equalization delta IQ overrides, phase-2 calibration request/disable IRQs, and DFE/CTLE/VGA/ATT/tap status fields.
- Power and clock handling: MPLL enable/disable, MPLL coarse tune, common calibration MPLL status, TX clock control, low-power detect fields, lane transceiver mode, and fast/continuous calibration flags.
- Test, debug, and manufacturing modes: ATE override fields, TX/RX serial loopback, PMA/MPHY override paths, OCLA/UPCS OCLA debug registers, signal-detect overrides, firmware configuration fields, and calibration code readbacks.
- Interrupt handling: IRQ status, mask, and clear fields for RX/TX reset/request, rate/P-state changes, adaptation requests, phase-2 calibration, loopback, transceiver mode, and DCC events.
- Always-on lane state capture: `RAWAONLANE0`, `RAWAONLANE1`, and partial `RAWAONLANE2` calibration/status blocks provide lane-local observability that can be read during training diagnostics and recovery.

## Risks and Failure Modes

- Incorrect shift or mask values can corrupt neighboring fields in the same 16-bit register, leading to failed lane bring-up, incorrect PLL/rate/width selection, unstable RX adaptation, broken signal detection, or disabled TX/RX paths.
- Instance-prefix mistakes can compile successfully while targeting the wrong lane. Confusing `RAWLANE3` with `RAWAONLANE1`, for example, would mix live PCS/PMA controls with always-on calibration/status registers.
- Boundary incompleteness matters for this chunk: it begins after the register comment for `RAWLANE2_DIG_PCS_XF_ATE_TX_OVRD_IN_1` and ends before the mask/reserved fields for `RAWAONLANE2_DIG_RX_DCC_CAL_QDF_CODE_0`. The final file-level merge must reconcile both partial register families with adjacent chunk reports.
- Interrupt clear/mask fields require exact masks. A wrong IRQ clear bit can drop events, leave stale interrupts asserted, or mask real lane reset/adaptation failures.
- Override-enable fields are particularly sensitive because they can force hardware wires away from normal firmware/PHY sequencing. Bad masks in ATE, PMA, MPHY, TX/RX disable, signal-detect, or equalization override fields can cause hard-to-debug link failures.
- Calibration fields often encode signed or hardware-specific tune codes even though this header exposes only raw bit positions. Misinterpreting value width or sign in consumers can produce invalid CTLE/DFE/DCC/VREF/signal-detect tuning.
- Generated-header drift against silicon documentation or companion address headers can pass compilation but fail only on affected ASIC revisions or lane instances.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: AMDGPU display code builds without missing `DPCSSYS_CR0_RAWLANE2`, `DPCSSYS_CR0_RAWLANE3`, `DPCSSYS_CR0_RAWAONLANE0`, `DPCSSYS_CR0_RAWAONLANE1`, or `DPCSSYS_CR0_RAWAONLANE2` shift/mask symbols.
- Register-generation consistency checks: every non-boundary field has matching `__SHIFT` and `_MASK` definitions, reserved masks match the documented field widths, and instance prefixes align with companion DPCS register address headers.
- Lane/link smoke tests: hotplug, modeset, link retraining, suspend/resume, GPU reset recovery, lane-count/rate changes, and low-power transitions on hardware using DPCS 3.1.4.
- Training/adaptation diagnostics: RX adaptation request/ack/FOM transitions, DFE/CTLE/VGA/ATT value readback, phase-2 calibration IRQs, RX LOS/signal-detect behavior, TX EQ update status, and MPLL/RCAL calibration done flags.
- Interrupt validation: RX/TX reset/request IRQ assertion and clear, RX rate/P-state/adaptation IRQ mask behavior, lane transceiver mode IRQ handling, loopback IRQ handling, and DCC on-demand event reporting.
- Debug/status validation: OCLA/UPCS OCLA access, FSM status/memory monitors, TX/RX continuous calibration status, signal-detect input/output mirrors, initial power-up done, and firmware configuration fields read back as expected.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create a final per-file synthesis for `dpcs_3_1_4_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.

### subset-b-002264: lines 12192-14650

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 12192-14650

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for display PHY and link-encoder register fields. It contains no executable C logic; its public surface is a dense set of preprocessor constants that describe where fields live inside 16-bit DPCS CR registers.

The requested range contains 2,132 generated `#define` entries: 1,070 `__SHIFT` definitions and 1,062 `_MASK` definitions. It starts at the tail of `DPCSSYS_CR0_RAWAONLANE2` RX/TX calibration metadata, covers the full `RAWAONLANE3` and generic `RAWAONLANEX` always-on lane field layouts, covers generic `SUPX` PLL/supervisor/analog/tuning field layouts, and ends inside generic `LANEX` TX power-control state fields. The boundaries are artificial chunk boundaries: lane 2 begins before this range, and `LANEX` P-state fields continue after it.

Although this path is under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the same field.

The main register-field families in this chunk are:

- `DPCSSYS_CR0_RAWAONLANE2_*` tail: RX DCC calibration code fields for ICM/IDF/QCM/QDF banks, TX DCC bank address/data/control, MPLL bandgap control, signal-detect override/readback, firmware adaptation/calibration config, lane transceiver mode override/readback, and RX signal-detect filtering.
- `DPCSSYS_CR0_RAWAONLANE3_*`: lane-3 always-on lane fields for analog front-end offsets, RX adaptation values, DFE tap values, slicer controls, MPLL/RCAL status, fast-calibration skip/shortcut flags, TX/RX disable overrides, LOS and signal-detect controls, RX override outputs, RX signal-detect and VREF calibration codes, RX/TX DCC programming, firmware config, and lane transceiver mode.
- `DPCSSYS_CR0_RAWAONLANEX_*`: generic lane-X copy of the lane always-on register layout, structurally matching lane 3 for code that addresses a lane through an indexed/generic CR window rather than a fixed physical lane prefix.
- `DPCSSYS_CR0_SUPX_*`: generic supervisor/common PHY fields for refclk, MPLLA/MPLLB dividers and HDMI clocks, MPLL analog overrides, spread-spectrum peak/stepsize, charge-pump and gain settings, supervisor/prescaler/level overrides, ASIC input mirrors, bandgap and analog controls, MPLL power-control state/status/timers/calibration/DAC output, clock/reset power-up timers, RTUNE configuration/status/setpoints/counters/calibration code, and analog override/status readback.
- `DPCSSYS_CR0_LANEX_*`: generic lane-X ASIC-facing override/input/output fields for lane enable/ownership, TX driver and common-mode controls, TX/RX rate/width/P-state, RX adaptation/termination/CDR/equalizer controls, RX/TX handshakes, OCLA debug clock/data enables, and TX P-state power-control bits. This chunk ends after `TX_PWRCTL_TX_PSTATE_P0S`; later P-states are outside the range.

Many fields use a paired value/enable override pattern, for example `*_OVRD_VAL` with `*_OVRD_EN`, or hardware input/output handshake fields such as `REQ`, `ACK`, `VALID`, `DATA_EN`, and `LPD`. Reserved fields are explicitly named and masked, which lets generated tables preserve complete bit layouts without encouraging driver code to program those bits.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. `dcn314_resource.c` includes the companion `dpcs_3_1_4_offset.h` and this shift/mask header.
2. Resource setup builds link-encoder shift and mask tables with `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. Link-encoder and HPO link-encoder code use generic register helper macros such as `REG_GET`, `REG_SET`, and `REG_UPDATE` against those tables.
4. Runtime code performs the actual MMIO/indirect-CR reads and writes; this file only supplies field locations.

The macros in this chunk do not define programming order. PHY bring-up, PLL sequencing, DCC/RTUNE calibration, USB-C alt-mode handling, lane power-state changes, signal detect, CDR, equalization, and TX/RX handshakes are controlled by hardware rules and driver code outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- Per-lane RX adaptation and calibration state: ATT/VGA/CTLE/DFE tap values, IQ phase, slicer controls, VREF/signal-detect/DCC calibration codes, adaptation-done/status bits, and fast-calibration bypass flags.
- Per-lane TX/RX control state: disable overrides, TX DCC bank programming, TX driver cursor and common-mode values, TX/RX rate and width, RX termination, CDR tracking, equalizer inputs, and ASIC handshake bits.
- Common/supervisor state: reference clock selection, bandgap, MPLLA/MPLLB divider and HDMI clock setup, spread-spectrum programming, charge-pump/gain overrides, MPLL power status, calibration timers, RTUNE setpoints/status, analog override outputs, and analog status.
- Power-management state: lane and TX P-state fields such as analog refgen enable, VCM hold, analog/word/digital clock enable, analog reset, serializer enable, data enable, RX-detect allowance, and DCC compensation calibration enable.

Persistence and side effects are hardware-defined. Configuration fields generally remain until link reprogramming, power-gating transitions, suspend/resume, GPU reset, ASIC reset, or another firmware/driver path rewrites them. Status fields can be live, latched, self-clearing, or valid only while the relevant lane, PLL, clock, or PHY block is powered. This file does not encode read-only/write-only, write-one-to-clear, polling, or timing semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 3.1.4 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies matching `ixDPCSSYS_*` indirect CR offsets for the register names described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes this header and initializes DCN 3.1.4 link-encoder masks/shifts.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the DPCS register and field-list macros consumed by DCN 3.1-class resources. The fields most directly used there are RDPCS/RDPCSTX link-encoder fields outside this exact range, but the include contract is shared across the whole DPCS generated header.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` uses the resulting tables for USB-C DP alt-mode checks, DP4 lane-cap detection, transmitter enable/disable paths, and link-encoder programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and `.c` consume DPCS/RDPCSTX shift/mask metadata for HPO DP link encoder behavior on DCN 3.1-class hardware.

Behaviorally, this chunk is below the ordinary display modeset/link-training logic. It describes lower-level PHY knobs and status surfaces used for lane calibration, analog PLL control, lane power sequencing, signal detection, TX/RX handshakes, and debug/diagnostic routing.

## Risks And Edge Cases

- These are untyped preprocessor constants. An incorrect shift or mask can compile cleanly and still corrupt a hardware field at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the companion offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the tail of lane 2, and the final lines stop before the rest of the generic lane TX P-state blocks.
- Repeated lane layouts are copy-sensitive. `RAWAONLANE3` and `RAWAONLANEX` should remain structurally consistent except for their prefixes; a generator error can affect only one lane path or only generic lane-indexed access.
- Override value/enable pairs are hazardous when mismatched. Setting a value bit without the matching enable, or enabling an override with a stale value, can force a lane, PLL, signal-detect path, termination setting, or TX driver state unexpectedly.
- PLL and clock fields are sequencing-sensitive. Bad masks for MPLLA/MPLLB dividers, HDMI clock dividers, spread-spectrum values, charge-pump settings, power-control status, or calibration timers can cause link bring-up failures, unstable clocks, blank displays, or intermittent failures by link rate.
- Calibration status and fast-flag fields affect timing-dependent paths. Wrong masks can make software or firmware skip necessary calibrations, wait on the wrong completion bit, or believe calibration completed when it did not.
- RX signal-detect, LOS, CDR, termination, and equalizer masks affect link training and hotplug-like physical detection. Errors can present as absent sinks, unstable training, reduced lane counts, false loss-of-signal events, or failures only on marginal cables.
- TX P-state masks control analog/digital clocks, resets, serializer/data enable, RX-detect allowance, and DCC compensation. Incorrect values can break power transitions, suspend/resume, idle power saving, or retimer/repeater interactions.
- Reserved-bit masks are present but not a license to write reserved fields. Callers should preserve reserved bits according to the register access rules in the real programming sequence.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build AMDGPU DCN 3.1.4 display support. Missing or renamed macros should surface in `dcn314_resource.c`, DCN 3.1 link-encoder headers, HPO link-encoder headers, or register-helper table initialization.
- Mechanically compare this range with the authoritative DPCS 3.1.4 register-field database and verify every non-reserved `_MASK` has the expected paired `__SHIFT` definition.
- Cross-check field register names against `dpcs_3_1_4_offset.h`; each field group in this chunk should have a matching `ixDPCSSYS_*` register offset unless it is an intentional generated placeholder with no fields.
- Run repeated-layout checks across `RAWAONLANE3` and `RAWAONLANEX`, and across MPLLA/MPLLB supervisor blocks, allowing only intentional prefix and A/B differences.
- Exercise DP and USB-C DP-alt-mode link bring-up on all physical lanes supported by the DCN 3.1.4 ASIC. Expected signals are stable lane count/rate negotiation, no false DP4/alt-mode classification, and no link-training regressions by connector.
- Exercise suspend/resume, display idle, hotplug, rapid modeset, and link disable/enable loops to catch bad lane P-state, PLL power, clock, and reset masks.
- Validate high-rate links and lower-rate fallback paths with register dumps around PLL, RTUNE, DCC, signal-detect, CDR, equalizer, and TX driver fields. Watch for stuck calibration-done bits, false LOS/signal-detect state, or unexpected fast-calibration skips.
- Test HDMI/DP paths that use MPLL divider and HDMI clock fields, since bad common PLL masks can fail only for specific pixel clocks or link rates.
- Use hardware register traces or debugfs/reg-dump tooling, where available, to confirm `REG_GET`/`REG_UPDATE` operations preserve reserved bits and touch only the intended field masks.

## Cross-Chunk Notes

The previous chunk owns the earlier lane-2 always-on fields before the DCC calibration tail seen here. The next chunk continues generic `LANEX` TX power-control P-state definitions after `TX_PWRCTL_TX_PSTATE_P0S`. The final per-file report should reconcile adjacent chunks before making whole-file claims about all lanes, all supervisor/common PHY fields, or all TX P-state definitions in `dpcs_3_1_4_sh_mask.h`.

### subset-b-002265: lines 14651-17088

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 14651-17088

## Purpose

This chunk is generated AMD DPCS 3.1.4 register-field metadata. It contains no executable C logic; it exports preprocessor constants that encode bit shifts and masks for display PHY controller and DPCS lane registers. Driver code pairs these `__SHIFT` and `_MASK` values with the companion DPCS offset header so AMDGPU display register helpers can pack, update, and decode individual MMIO fields safely.

The requested range is a mid-file slice of `dpcs_3_1_4_sh_mask.h`. It starts inside the `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0S` register field group, covers a large CR0 lane/transceiver area, crosses an `addressBlock: dpcssys_cr1_rdpcstxcrind` marker, and ends inside the CR1 super-digital MPLLB divider override group. The chunk contains 2,438 lines, 2,143 `#define` entries, 1,068 `__SHIFT` macros, 1,098 `_MASK` macros, and 285 distinct register-comment groups. The imbalance between shift and mask counts is expected for this artificial chunk because it begins and ends inside register-field sequences.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, local includes, memory allocations, locks, or callable APIs in this range. The interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the field bit position within a 16-bit DPCS register.
- `<REGISTER>__<FIELD>_MASK`: the field mask used for read-modify-write preservation, extraction, and value packing.

Major register families in this chunk:

- `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_*`: TX p-state definitions for P0S/P1/P2, TX reference/clock/reset/serial/data enable bits, RX-detect and VBOOST permission, TX power-up timing, DCC bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT control.
- `DPCSSYS_CR0_LANEX_DIG_RX_PWRCTL_*`: RX p-state definitions for P0/P0S/P1/P2, RX AFE/clock/deserializer/CDR/VCO/digital-clock enables, RX power-up timing, and clock-delay setup.
- `DPCSSYS_CR0_LANEX_DIG_RX_VCOCAL_*`, `RX_CDR_*`, and `RX_DPLL_*`: RX VCO calibration control/status/timing fields, CDR calibration and override fields, CDR status, DPLL frequency, and upper/lower frequency bounds.
- `DPCSSYS_CR0_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration, thresholds, adaptation reset, ATT/VGA/CTLE/DFE status, even/odd DFE VDAC offsets, slicer controls, error slicer levels, DAC selector fields, and CR bank address/data.
- `DPCSSYS_CR0_LANEX_DIG_RX_STAT_*`: RX statistic/match controls, statistic counters 0-6, sample count, comparator clock control, match controls, stop controls, and data masks.
- `DPCSSYS_CR0_LANEX_DIG_MPHY_*` and `DPCSSYS_CR0_LANEX_DIG_ANA_*`: MPHY PWM/termination controls, digital-to-analog TX/RX override outputs, TX equalization and DCC override fields, RX AFE/CTLE/scope/slicer/IQ/calibration controls, analog status, RX termination, MPHY override, and signal-detect override fields.
- `DPCSSYS_CR0_LANEX_ANA_*`: low-level analog TX/RX register fields, many of which expose only reserved, no-connect, or high-byte masks in this generated slice.
- `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_*` and `PMA_XF_*`: raw-lane PCS/PMA crossbar override/input/output/status fields for TX and RX p-state, low-power detect, width, rate, MPLL selection/enables, reset/request/ack handshakes, loopback, async data, RX adaptation requests, VCO/reference load overrides, termination controls, phase-2 calibration, lane number, ATE override, and RX EQ override.
- `DPCSSYS_CR0_RAWLANEX_DIG_FSM_*`: FSM override control, memory address and status monitors, fast calibration/adaptation/power-up flags, common calibration status, CR lock, TX DCC flags/status, OCLA enables, TX EQ update flag, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR0_RAWLANEX_DIG_IRQ_CTL_*`: reset/request/rate/p-state/adaptation/phase-2-calibration/loopback/DCC/TX IRQ status bits, clear bits, and IRQ mask registers.
- `DPCSSYS_CR0_RAWLANEX_DIG_TX_CTL_*` and `RX_CTL_*`: TX/RX FSM controls, TX clock control, TX DCC continuous status, OCLA controls, RX LOS mask, RX data-enable override, and continuous adaptation/off-cancellation status.
- `DPCSSYS_CR1_SUP_DIG_*`: beginning of the next CR1 address block, including refclock override fields and MPLLA/MPLLB divider and HDMI-clock override fields.

Several register names are only comments with no field macros in this exact range, especially some analog low-level placeholders such as `DPCSSYS_CR0_LANEX_ANA_RX_CLK_1`, `ANA_RX_CLK_2`, `ANA_RX_CDR_DES`, `ANA_RX_SLC_CTRL`, `ANA_RX_PWR_CTRL2`, and `ANA_RX_CAL1`. Those comments still indicate generated register map entries, but the visible bitfields are either absent, reserved elsewhere, or outside the chunk.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display PHY and link code:

1. DPCS 3.1.4 code includes this shift/mask header together with the matching offset header.
2. Register-list macros token-paste register and field names into generated tables or inline register-helper calls.
3. Driver paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and field-specific wrappers to manipulate TX/RX power states, lane width/rate, PLL selection, calibration, adaptation, IRQ masks, and diagnostic/status fields.
4. Hardware sequencing remains in the caller: the macros only describe bit layout and do not enforce reset ordering, PLL enable timing, p-state transitions, calibration waits, IRQ acknowledgement, or suspend/resume restoration.

The implied hardware control flow in this chunk centers on lane bring-up and maintenance: configure ref clocks and MPLL selection, set TX/RX p-state power bits and timing, enable or override PCS/PMA handshakes, run VCO/CDR/DPLL and RX adaptation calibration, poll status/done bits, manage IRQ masks and clears, and optionally use LBERT/OCLA/statistic/scope registers for diagnostics.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed DPCS hardware state:

- TX lane state for analog reference generation, VCM hold, clocks, reset, serial/data enablement, RX-detect, VBOOST, DCC compensation, clock alignment, beaconing, loopback, and LBERT pattern/error injection.
- RX lane state for AFE/clock/deserializer/CDR/VCO/digital-clock enablement, p-state selection, VCO calibration, CDR/DPLL tracking, adaptation, slicer levels, DFE offsets, signal detect, LOS/LFPS, and RX data-valid overrides.
- PCS/PMA crossbar state for reset/request/ack handshakes, lane width/rate/p-state/low-power detect, master MPLL states, async data, loopback, terminations, phase-2 calibration, and ATE overrides.
- Calibration and diagnostic state for FSM status, fast-calibration flags, common calibration done bits, RX statistic counters, comparator/match controls, OCLA enables, analog status, and TX/RX DCC status.
- IRQ state for RX/TX reset and request events, rate and p-state changes, adaptation request/disable, phase-2 calibration request/disable, lane loopback events, DCC on-demand events, clear strobes, and mask bits.
- CR1 super-digital state for reference clock source/range, bandgap and HDMI mode overrides, and MPLLA/MPLLB divider and HDMI clock override fields.

Persistence is hardware-defined. Configuration fields generally retain values until link retraining, modeset, lane power transition, PHY power-gating, suspend/resume, driver reset, or ASIC reset. Status, IRQ, clear, calibration-done, lock, self-clear, and monitor fields may be read-only, sticky, write-one-to-clear, transient, or valid only while the relevant PHY clocks and power domains are active. This generated header does not encode access semantics; consuming code and the hardware register specification must supply them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DPCS 3.1.4 register database and must remain synchronized with the companion offset header for the same hardware generation:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`
- Other chunks of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h`

The expected integration points are AMDGPU display PHY, link encoder, DPCS, DCN resource, and DMUB or link-service code that programs DPCS registers through generated register tables. The CR0 `LANEX` and `RAWLANEX` names indicate per-lane transceiver fields, while the CR1 `SUP_DIG` fields indicate shared/supervisor clock and PLL controls. Consumers must use these field constants with the corresponding register offsets, base indices, and silicon-specific sequencing tables.

This chunk is tightly coupled to display link behavior. Field mistakes can affect DisplayPort or HDMI link training, lane power state transitions, high-speed rate/width changes, PLL/MPLL selection, RX adaptation, low-power modes, loopback/ATE diagnostics, PHY interrupts, and suspend/resume restoration.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while touching the wrong hardware bit, preserving the wrong reserved bits, or corrupting an adjacent field during read-modify-write.
- The file is generated metadata. Manual edits risk divergence from AMD's register database, the matching offset header, firmware expectations, and silicon documentation.
- The chunk boundary is artificial. The first lines are only the tail of `DPCSSYS_CR0_LANEX_DIG_TX_PWRCTL_TX_PSTATE_P0S`, and the final lines stop inside the CR1 supervisor PLL override area; adjacent chunks are required before making whole-register or whole-file claims.
- TX/RX power and p-state fields are sequencing-sensitive. Incorrect masks around analog clocks, reset, serial/data enablement, VBOOST, RX detect, VCO/CDR enables, or digital clocks can produce link-training failures, intermittent display loss, or power-state bugs that only appear during modeset, hotplug, low power, or resume.
- Calibration fields are side-effect-sensitive. VCO, CDR, DPLL, RX adaptation, DCC, RCAL, phase adjustment, and phase-2 calibration fields may involve start/done/ack semantics; confusing status with control bits can cause stuck calibration or invalid analog settings.
- IRQ clear and mask registers are easy to misuse. A wrong clear or mask field can create missed PHY events, stuck interrupts, interrupt storms, or stale rate/p-state/adaptation notifications.
- Repeated override and ATE patterns are copy-sensitive. Fields such as `*_OVRD_VAL`, `*_OVRD_EN`, PCS/PMA input/output, raw-lane and ATE variants look similar but have different direction and side effects.
- Reserved and no-connect fields are numerous in this range. Consumers should preserve reserved bits unless the hardware specification explicitly says otherwise; writing visible reserved masks as data can be harmful.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support for ASICs that consume DPCS 3.1.4. Missing or renamed macros should fail in generated register-table construction or field-helper use.
- Mechanically verify that fields in lines 14651-17088 have matching `__SHIFT` and `_MASK` definitions where both sides are inside the range, while allowing boundary exceptions at the start of `TX_PSTATE_P0S` and the end of the CR1 supervisor PLL groups.
- Diff this range against AMD's authoritative DPCS 3.1.4 register database and nearby DPCS versions where the PHY layout is expected to remain compatible.
- Exercise DisplayPort and HDMI link bring-up across lane counts, link rates, hotplug, unplug/replug, modeset, link retraining, low-power entry/exit, and suspend/resume.
- Validate PHY calibration and adaptation by checking VCO/CDR/DPLL lock and done statuses, RX adaptation status fields, DCC/RCAL status, and absence of repeated retraining or timeout logs.
- Exercise IRQ paths for RX/TX reset/request, rate changes, p-state changes, adaptation request/disable, phase-2 calibration, loopback, and DCC events; verify clear bits do not leave stuck status.
- Use diagnostics where available: LBERT, OCLA, RX statistic counters, analog status/scope, loopback, and ATE override paths can reveal bitfield drift that normal display modes do not cover.
- Watch kernel logs and display diagnostics for AUX/link-training failures, blank displays, CRC or error-counter growth, hotplug storms, PHY timeout messages, stuck interrupts, audio/video loss after resume, and failures limited to specific rates or lane widths.

## Cross-Chunk Notes

Previous chunks own the opening portions of `dpcs_3_1_4_sh_mask.h`, including the beginning of the CR0 DPCS register namespace and the start of the `TX_PSTATE_P0S` field group. Later chunks continue the CR1 supervisor register block after `DPCSSYS_CR1_SUP_DIG_MPLLB_DIV_CLK_OVRD_IN` and cover the remaining DPCS 3.1.4 register-field namespace. The final per-file research document should merge all chunks before making complete claims about all DPCS 3.1.4 registers, all CR0/CR1 address blocks, or all lane and supervisor PHY controls.

### subset-b-002266: lines 17089-19501

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 17089-19501

## Scope

This chunk is a mid-file slice of the generated AMD DPCS 3.1.4 register shift/mask header. It contains compile-time preprocessor metadata only: hardware bitfields are exposed as `...__SHIFT` bit offsets and matching `..._MASK` constants. There are no C functions, structs, executable branches, locks, allocations, direct register accesses, or software persistence mechanisms in this range.

The slice contains 2,185 `#define` entries: 1,100 shift macros and 1,085 mask macros across 244 register-comment blocks. The imbalance is a chunk-boundary artifact. The first two lines are masks for the preceding `DPCSSYS_CR1_SUP_DIG_MPLLB_DIV_CLK_OVRD_IN` register, and the range ends after the first shift for `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P2`, before the rest of that register's fields.

Although the repository path is under `ceph-client`, this file is AMDGPU display PHY metadata. The covered namespace is `DPCSSYS_CR1`, the DPCS control/register instance used by DCN 3.1.4 display code.

## Purpose

The purpose of this chunk is to publish exact bit positions and masks for DCN 3.1.4 DPCS CR1 supervisor, PLL, analog, and lane-control registers. Runtime AMD display code combines these constants with companion indirect-register offsets from `dpcs_3_1_4_offset.h` and register-helper macros to isolate fields while programming the DisplayPort/HDMI PHY-side hardware.

Major covered areas:

- CR1 supervisor digital PLL and clock controls for MPLLA/MPLLB, including HDMI/divider clocks, PLL enable/divider/VCO/standby/calibration controls, fractional-N quotient/remainder/denominator fields, spread-spectrum peak/stepsize fields, charge-pump controls, and clock-sync override bits.
- Supervisor override, ASIC-input, analog-input, power-control, clock/reset, RTUNE, bandgap, PMIX, and status fields that describe or force PHY supervisor state.
- Lane 0 ASIC-facing lane/TX/RX override and mirror fields, TX power-state programming, TX power-up timing, TX DCC DAC access, TX clock alignment, TX LBERT, RX statistic counters and pattern-match controls, and TX analog override/status fields.
- Lane 1 ASIC-facing lane/TX/RX override and mirror fields, TX power-state/timing/DCC/LBERT controls, and the beginning of RX power-state programming.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit offset inside the register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by masked register read/update/write helpers.
- Register comments such as `//DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0` identify the register block whose field macros follow.
- Instance and lane prefixes are part of the ABI. `DPCSSYS_CR1_SUP_*` refers to the CR1 supervisor block, while `DPCSSYS_CR1_LANE0_*` and `DPCSSYS_CR1_LANE1_*` refer to lane-specific PHY registers.

Important register families in this chunk include:

- `DPCSSYS_CR1_SUP_DIG_MPLLA_*` and `DPCSSYS_CR1_SUP_DIG_MPLLB_*`: PLL override inputs, PLL multipliers, TX clock dividers, VCO frequency, standby/calibration controls, fractional-N programming, SSC enable/up-spread/peak/stepsize, PMIX/word-divide controls, charge-pump proportional/integral settings, gear-shift charge-pump overrides, HDMI clock divider fields, and PLL power-control status/timers/calibration/analog-DAC outputs.
- `DPCSSYS_CR1_SUP_DIG_SUP_OVRD_IN`, `PRESCALER_OVRD_IN`, `SUP_OVRD_OUT`, and `LVL_OVRD_IN`: supervisor-level overrides for prescaler, RTUNE, TX calibration codes, PHY reset, reference clock, HDMI mode, bandgap, PLL enable/calibration, TX/RX power states, and level-based digital behavior.
- `DPCSSYS_CR1_SUP_DIG_*_ASIC_IN`: hardware input mirrors for MPLL A/B, divider clocks, HDMI clocks, general supervisor state, level controls, bandgap, and charge-pump settings. These pair with the override input/output blocks to distinguish programmed override values from ASIC-provided live values.
- `DPCSSYS_CR1_SUP_ANA_*`: analog supervisor controls for prescaler, RTUNE, bandgap configuration, and switch-power measurement.
- `DPCSSYS_CR1_SUP_DIG_CLK_RST_*` and `RTUNE_*`: bandgap/reference-clock power-up timers, VPH under-drive timing, RTUNE configuration/status, RX/TX down/up set values and observed status, counter configuration, and TX calibration code reporting.
- `DPCSSYS_CR1_SUP_DIG_ANA_*_OVRD_OUT`, `ANA_STAT`, and PMIX override outputs: observable analog override outputs and status mirrors for MPLL, RTUNE, bandgap, and PMIX state.
- `DPCSSYS_CR1_LANE0_DIG_ASIC_*` and `DPCSSYS_CR1_LANE1_DIG_ASIC_*`: per-lane request, reset, pstate, rate, width, enable, clock-ready, TX swing/pre/post cursor, de-emphasis, HDMI mode, RX detect, RX/TX inversion, RX equalizer/CDR/VCO/low-power control, and override output fields.
- `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_*` and `DPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_*`: TX P0/P0S/P1/P2 state bitmaps for analog reference generation, VCM hold, clocks, reset, serial/data enable, RX-detect allowance, vboost allowance, and DCC compensation calibration; plus power-up timer fields and DCC calibration/DAC address/data/range/acknowledge controls.
- `DPCSSYS_CR1_LANE0_DIG_RX_STAT_*`: RX statistic load values, data masks, match controls, statistic control, sample counts, seven statistic counters, calibration comparator clock control, extended match controls, and statistic stop controls.
- `DPCSSYS_CR1_LANE0_DIG_ANA_*` and `DPCSSYS_CR1_LANE0_ANA_TX_*`: TX analog override outputs and raw analog TX controls for term codes, equalization, DCC DACs, power override, alternate/ATB buses, clocks, misc controls, and reserved analog fields.
- `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0/P0S/P1`: RX AFE, clock regulator, clock, deserializer, CDR, VCO reset/calibration, continuous calibration, and digital-clock enable fields. `RX_PSTATE_P2` begins at the final line and is completed in the next chunk.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. DCN 3.1.4 resource/display code includes `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`.
2. Register descriptors or helper macros pair an indirect DPCS register offset such as `ixDPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0` or `ixDPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0` with this file's shift/mask constants.
3. AMD display register helpers perform masked reads, writes, updates, and polling against the DPCS CR1 indirect register interface.
4. Hardware state changes occur in the PHY, PLL, supervisor, TX, RX, analog, and diagnostic registers. This file only supplies the bitfield metadata needed to avoid hard-coded bit arithmetic.

The represented hardware flow is typically: configure or observe supervisor reference/PLL state, program MPLL A/B clocks and spread-spectrum behavior, handle RTUNE and calibration state, program per-lane TX/RX override inputs or observe ASIC-provided inputs, sequence lane TX/RX power states and timers, access DCC calibration controls, and read diagnostics such as RX counters, LBERT controls, and analog status mirrors.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros resides in DPCS hardware registers.

Hardware state represented by this chunk includes:

- PLL and clock state: MPLLA/MPLLB enable, divider, multiplier, VCO frequency, standby, calibration, fractional-N fields, SSC fields, HDMI clock division, charge-pump tuning, PLL power-control timers/status, and PMIX controls.
- Supervisor state: PHY reset, reference-clock and bandgap control, prescaler/RTUNE overrides, TX calibration code, level controls, and ASIC input/output mirrors.
- Lane state: lane reset, pstate/rate/width requests, TX/RX enable and clock-ready state, TX swing/equalization/pre/post-cursor settings, HDMI mode, RX detection, RX equalizer/CDR/VCO controls, and lane OCLA hook for lane 1.
- TX/RX power sequencing state: TX P0/P0S/P1/P2 power bitmaps, TX power-up timers, RX P0/P0S/P1 power bitmaps, and the start of RX P2.
- Diagnostics and calibration state: DCC CR bank and DAC access, LBERT mode/error injection fields, RX pattern-match/statistic counters, analog override outputs, analog TX DCC/term/equalization fields, RTUNE status, and PLL analog DAC output fields.

Persistence is limited to the lifetime of hardware register programming. Values may be lost or require reprogramming after GPU reset, display engine reset, PHY reset, power gating, suspend/resume, hotplug retraining, mode set, link-rate changes, or lane-count changes. Higher-level AMD display state and BIOS/firmware policy remain the source of truth for reprogramming these registers.

## Dependencies

This chunk depends on the matching generated DPCS 3.1.4 offset header. Shift and mask constants alone do not identify the indirect register address; for example, the offset header maps the CR1 supervisor block at offsets such as `0x0007` for `ixDPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0` and lane 1 TX/RX blocks at offsets such as `0x1120` for `ixDPCSSYS_CR1_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0` and `0x1140` for `ixDPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P0`.

It also depends on:

- AMD display register-helper infrastructure, especially masked read/write/update and polling helpers that consume generated `__SHIFT` and `_MASK` symbols.
- DCN 3.1.4 resource code, which includes the generated DPCS offset and shift/mask headers alongside the DCN 3.1.4 display register headers.
- The silicon register database or generator that produced the DPCS 3.1.4 headers.
- Display link, PHY, clock, PLL, HPD/link-training, HDMI/DP, power-management, and diagnostic code that programs these fields during mode set, retraining, suspend/resume, reset recovery, and validation.

Because this is generated silicon metadata, manual edits are risky unless synchronized with the register database, companion offset header, and any generated register tables that reference these names.

## Integration Points

The primary integration point is the macro-name ABI between generated headers and AMD display code. A consumer naming `DPCSSYS_CR1_LANE0_DIG_TX_PWRCTL_DCC_DAC_SEL__REQ_MASK` or `DPCSSYS_CR1_SUP_DIG_MPLLB_OVRD_IN_0__MPLLB_EN_MASK` relies on this header for the exact bit position and mask.

Integration surfaces include:

- DCN 3.1.4 resource initialization: `dcn314_resource.c` includes `dpcs/dpcs_3_1_4_offset.h` and `dpcs/dpcs_3_1_4_sh_mask.h` so generated register definitions are available to display-resource construction and lower-level hardware blocks.
- DPCS indirect register access: CR1 `ixDPCSSYS_*` offsets from the companion header select the register, while this header selects or updates the field within that register.
- PHY clock and PLL programming: MPLLA/MPLLB override, divider, HDMI clock, SSC, charge-pump, fractional-N, power-control timer/status, and calibration fields feed display clock and link PHY setup.
- Lane power and link bring-up: lane ASIC override/input fields and TX/RX pstate/timing fields are used when enabling lanes, changing link rates, powering down idle lanes, handling RX detect, and coordinating TX/RX analog/digital clocks.
- Calibration and analog tuning: RTUNE, TX calibration code, DCC DAC, analog override outputs, term code, equalization, vboost, and DCC compensation fields integrate with PHY calibration and board/silicon tuning paths.
- Diagnostics and debug: RX statistic counters, match controls, LBERT fields, analog status, MPLL status, OCLA, and switch-power measurement provide validation and debug signals.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent hardware fields in the same 16-bit register, leading to bad PLL programming, failed link training, unstable clocks, blank displays, or audio/video link instability.
- Instance-prefix mistakes can compile cleanly while programming CR0/CR1 or lane 0/lane 1 incorrectly. The lane offset pattern differs by `0x100` blocks, so a wrong macro family can target a different physical lane.
- PLL, SSC, and fractional-N fields are timing-sensitive. Bad masks can produce incorrect link clocks, excessive spread, failed lock, or intermittent display failures that only appear at certain link rates or HDMI/DP modes.
- Power-state and timer fields control sequencing of analog reference generation, VCM hold, clocks, reset, serial/data enable, RX detect, VCO reset/calibration, CDR, deserializer, and digital clocks. Misprogramming can cause hangs, missed detects, or incomplete power transitions.
- Status and clear/update fields must be handled with exact masks. RTUNE, DCC DAC request/acknowledge, statistic stop/counter fields, LBERT trigger, and analog status fields can otherwise lose events or report stale state.
- Reserved bits are explicitly represented. Writes that fail to preserve reserved fields may violate silicon programming requirements.
- This chunk starts and ends mid-register context. The merge lane must combine adjacent chunks before making whole-file claims about the complete `MPLLB_DIV_CLK_OVRD_IN` and `LANE1 RX_PSTATE_P2` definitions.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DCN 3.1.4 AMD display code builds without missing `DPCSSYS_CR1_SUP_*`, `DPCSSYS_CR1_LANE0_*`, or `DPCSSYS_CR1_LANE1_*` shift/mask symbols.
- Generated-header consistency: every field in this slice pairs with the matching `ixDPCSSYS_CR1_*` offset in `dpcs_3_1_4_offset.h`, and regenerated output has stable shift/mask values.
- Mode-set smoke tests: DP and HDMI displays light up across common resolutions, refresh rates, color depths, link rates, and lane counts.
- Link training and retraining: hotplug, unplug/replug, GPU reset recovery, suspend/resume, link-rate changes, lane-count changes, and RX-detect paths succeed without PHY lock or clock instability.
- PLL and clock validation: MPLL lock/status, HDMI/divider clock behavior, SSC enable/disable, fractional-N programming, and PLL power-control timer/status fields read back as expected.
- Lane power sequencing: TX/RX P0/P0S/P1/P2 programming, power-up timers, RX VCO/CDR/deserializer enables, and low-power transitions behave across active and idle lanes.
- Calibration and debug: RTUNE status, TX calibration code, DCC DAC request/acknowledge, analog override/status fields, RX statistic counters, and LBERT controls produce expected values during hardware diagnostics.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_3_1_4_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.

### subset-b-002267: lines 19502-21927

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 19502-21927

## Scope

This chunk is part of the generated AMD DPCS 3.1.4 ASIC register shift/mask header. It contains preprocessor constants only: each register field is represented by a `...__SHIFT` bit offset and usually a matching `..._MASK` bit mask. There are no C functions, structs, branches, allocations, locks, direct MMIO operations, or persistence mechanisms in this range.

The slice covers 2,426 source lines, 2,155 `#define` entries, and 271 register-comment blocks. It begins inside `DPCSSYS_CR1_LANE1_DIG_RX_PWRCTL_RX_PSTATE_P2`, after the first `RX_P2_ANA_AFE_EN__SHIFT` definition, and ends inside `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, before that register's mask definitions. Neighboring chunks are needed to reconstruct those two boundary registers completely.

## Purpose

The purpose of this chunk is to publish exact bitfield metadata for DPCS CR1 lane 1 and lane 2 PHY control/status registers. Runtime AMDGPU display/link code combines these generated shift and mask names with companion register-address headers and register helper macros to program or inspect per-lane DisplayPort/PHY hardware without open-coded bit arithmetic.

Major covered areas:

- Tail of lane 1 RX power-state P2 controls, RX power-up timing, VCO calibration controls/status, CDR controls/status, DPLL frequency fields, receiver adaptation controls/status, pattern/statistics counters, MPHY low-speed controls, and analog TX/RX override/status fields.
- Lane 1 analog register aliases for TX override measurement, TX power/term/DCC/misc fields, RX clock/CDR/slicer/power/calibration/test-bus fields.
- Lane 2 ASIC-facing lane/TX/RX override and real input/output fields, including equalization, CDR/VCO, OCLA, lane mapping, transmit drive, receive detection, and calibration handoff fields.
- Lane 2 TX power-state/timing/DCC controls and loopback error-rate test control.
- Lane 2 RX power-state/timing, VCO calibration, CDR/DPLL, adaptation, statistics, MPHY PWM/termination/stable-clock fields.

## Important Macros and Field Families

The exported API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's bit position inside a 16-bit DPCS register.
- `<REGISTER>__<FIELD>_MASK` gives the field mask used by register-helper update paths.
- Instance prefixes such as `DPCSSYS_CR1_LANE1_` and `DPCSSYS_CR1_LANE2_` are part of the ABI between generated headers and display/PHY register tables. They distinguish two physical lanes with otherwise repeated field layouts.

Important register families in this chunk include:

- Lane 1 RX power and calibration: `DIG_RX_PWRCTL_RX_PSTATE_P2`, `RX_PWRUP_TIME_1/2/3`, `DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0/1/2`, `RX_VCO_CAL_TIME_0/1`, and `RX_VCO_STAT_0/1/2` define AFE, voltage-regulator, clock, CDR, deserializer, VCO reset/calibration, continuous calibration, startup/update/settle timing, calibration-done, VCO counter, too-fast, correct, and up status fields.
- Lane 1 CDR/DPLL and link-test fields: `RX_ALIGN_XAUI_COMM_MASK`, `RX_LBERT_CTL`, `RX_LBERT_ERR`, `RX_CDR_CDR_CTL_0..4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_0/1` define comma-mask, LBERT mode/sync/error count, phase detector, SSC counters, lock counts, filter settings, edge/status bits, frequency, and bound fields.
- Lane 1 RX adaptation and statistics: `RX_ADPTCTL_ADPT_CFG_0..9`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP*_STATUS`, slicer/DFE DAC offset controls, CR bank address/data, `RX_STAT_*` match/control/counter registers, and statistic stop fields define equalization/adaptation behavior, loaded values, pattern masks, source selection, sample counts, counter enables, pause/clock/valid-loss controls, and comparator clock timing.
- Lane 1 MPHY and analog overrides: `DIG_MPHY_RX_PWM_CTL`, `TERM_LS_CTL`, `ANA_PWM_CLK_STABLE_CNT`, `DIG_ANA_TX_*`, `DIG_ANA_RX_*`, `DIG_ANA_STATUS_*`, `ANA_TX_*`, and `ANA_RX_*` expose low-speed polarity/termination/stability fields plus digital override outputs for analog TX/RX clocks, data enables, DCC, termination, equalization, AFE/CTLE/VGA/slicer, calibration DACs, phase adjust, signal detect, and test-bus measurements.
- Lane 2 ASIC interface and override fields: `DIG_ASIC_LANE_OVRD_IN`, `DIG_ASIC_TX_OVRD_IN_0..5`, `DIG_ASIC_RX_OVRD_IN_0..6`, `DIG_ASIC_RX_OVRD_EQ_IN_*`, `DIG_ASIC_*_ASIC_IN/OUT`, `DIG_ASIC_RX_CDR_VCO_ASIC_IN_*`, and `DIG_ASIC_OCLA` define the lane's override inputs, hardware-owned ASIC inputs, and observed outputs for power enables, reset lines, DCC, transmit/receive analog enables, CDR/VCO controls, equalization, and observation/logic-analyzer selection.
- Lane 2 TX power and diagnostic controls: `DIG_TX_PWRCTL_TX_PSTATE_P0/P0S/P1/P2`, `TX_PWRUP_TIME_0..5`, `DCC_CR_BANK_*`, `DCC_DAC_*`, `TX_CLK_ALIGN_TX_CTL_0`, and `TX_LBERT_CTL` describe per-power-state transmit enable/reset bits, timing delays, DCC DAC access/range/ack/address, clock alignment, and TX LBERT pattern control.
- Lane 2 RX repeated families: `DIG_RX_PWRCTL_*`, `DIG_RX_VCOCAL_*`, `DIG_RX_CDR_*`, `DIG_RX_DPLL_*`, `DIG_RX_ADPTCTL_*`, `DIG_RX_STAT_*`, and `DIG_MPHY_RX_*` repeat the lane 1 receiver control/status model for lane 2.

## Control Flow and Runtime Integration

This header has no executable control flow. Runtime behavior is indirect:

1. AMDGPU display or PHY code includes this generated shift/mask header with the matching DPCS 3.1.4 register offset/address header.
2. Register descriptor tables pair the DPCS register address with the field constants from this file.
3. Masked read/modify/write helpers use the `_MASK` and `__SHIFT` constants to update individual fields or decode status fields.
4. The actual state transition occurs in DPCS hardware: lane power sequencing, VCO/CDR calibration, link training diagnostics, adaptation, DCC, analog override, or statistics collection.

The represented hardware flow is typically: select ASIC-owned or software-override controls, sequence TX/RX power states and power-up timings, bring up RX AFE/clock/CDR/deserializer and TX analog paths, run VCO/CDR/DCC/adaptation calibration, optionally drive LBERT or statistics collection, and poll status/counter fields to validate lane readiness and signal quality.

## State and Persistence Behavior

The file itself has no mutable state. All state described by these macros lives in hardware registers.

The hardware state represented by this chunk includes:

- Lane power state: TX/RX P0, P0S, P1, and P2 enable/reset fields, power-up delay fields, low-speed MPHY polarity/termination/stable-clock settings, and analog clock/data/refgen/termination enables.
- Calibration state: RX VCO startup/update/settle timing, calibration reset/continuous-calibration bits, VCO FSM state, calibration done, VCO counter result, DCC DAC bank/data/range/ack/address, RX calibration DAC controls, and CDR/DPLL frequency and lock controls.
- Equalization/adaptation state: ATT, VGA, CTLE, DFE tap status, slicer levels, DAC control selection, adaptation configuration, reset configuration, CR bank access, and DFE data/error offset fields.
- Diagnostics and observability: LBERT mode/sync/error count, statistic match patterns and masks, statistic counters, sample-count done bits, valid-loss clear/control, OCLA selection, ASIC input/output mirrors, and analog test-bus measurement fields.
- Override state: digital and ASIC override inputs/outputs for TX, RX, equalization, signal detect, DCC, CDR/VCO, MPHY, phase adjustment, and analog status.

Persistence is limited to hardware register lifetime. Values can be lost or need reprogramming after GPU reset, DPCS or lane reset, display engine reset, power gating, suspend/resume, hotplug-driven retraining, or mode/link reconfiguration. Higher-level driver link state and board/silicon configuration remain the durable source of truth.

## Dependencies

This chunk depends on matching generated DPCS 3.1.4 register-address headers. Shift and mask constants alone do not identify where a register is located.

It also depends on:

- AMD display and PHY register-helper infrastructure that consumes generated `__SHIFT` and `_MASK` names for masked reads, writes, updates, and polling.
- The silicon register database used to generate this header and the companion register offset headers.
- DisplayPort/link encoder, PHY bring-up, power-management, diagnostics, and validation code that programs DPCS CR1 lane registers.
- Correct lane-instance mapping between `LANE1`/`LANE2` macro prefixes and the corresponding hardware lane addresses in generated tables.

Because this is generated silicon metadata, manual edits are risky unless synchronized with the register database, companion offset headers, and every generated register table that references these names.

## Integration Points

Primary integration points are the macro names consumed by AMDGPU register tables and masked register helpers. A consumer naming a field such as `DPCSSYS_CR1_LANE2_DIG_TX_PWRCTL_TX_PSTATE_P0__TX_P0_ANA_CLK_EN` or `DPCSSYS_CR1_LANE1_DIG_RX_ADPTCTL_CTLE_STATUS__CTLE_STATUS` relies on this header for the correct bit position and mask.

Integration surfaces include:

- Link/lane power sequencing: TX/RX P-state registers, power-up timers, MPHY low-speed controls, RX AFE/clock/CDR/deserializer enables, and TX analog clock/data/reference/termination enables.
- PHY calibration: RX VCO calibration controls/status, CDR controls/status, DPLL frequency/bounds, DCC DAC bank/data/range/ack/address fields, and RX analog calibration DAC fields.
- Link training and signal integrity: adaptation configuration, VGA/CTLE/DFE/slicer controls and status, signal-detect overrides, equalization ASIC handoff fields, and phase-adjust fields.
- Diagnostics: LBERT controls and error counters, statistic pattern matchers/counters/sample status, OCLA selection, ASIC input/output mirrors, analog status, and test-bus measurement registers.
- Multi-lane mapping: lane 1 and lane 2 have repeated receiver families but different address namespaces, so generated names must stay aligned with the companion address definitions.

## Risks and Failure Modes

- Incorrect shifts or masks can corrupt adjacent fields in a 16-bit lane register, causing failed power sequencing, CDR/VCO calibration failures, bad DPLL settings, broken DCC calibration, or unstable link training.
- Lane-prefix mistakes can compile cleanly while programming the wrong physical lane, producing asymmetric failures that only appear on particular lane-count or lane-mapping configurations.
- Override fields are especially sensitive. Writing the wrong mask can force software ownership of ASIC-controlled TX/RX/AFE/CDR/equalization signals or prevent hardware from taking control after calibration.
- Status and clear fields can have side effects. Misidentifying statistic done bits, valid-loss clear, DCC ack, calibration done, or LBERT error overflow fields can hide real failures or leave stale status latched.
- Power-state and timing fields are order and delay sensitive. Bad masks in `PSTATE` or `PWRUP_TIME` registers can leave analog supplies, clocks, deserializers, or CDR/VCO blocks enabled too early, too late, or not at all.
- Adaptation and equalization masks affect signal margin. Small field errors in CTLE, VGA, DFE, slicer, or DAC selection can present as intermittent DP training failures rather than deterministic build failures.
- This chunk starts and ends mid-register, so any final per-file report must reconcile the missing first lane 1 `RX_P2_ANA_AFE_EN__SHIFT` line and the lane 2 `PWM_CLK_STABLE_CNT` mask lines from neighboring chunks.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Compile-time coverage: DPCS 3.1.4 display/PHY code builds without missing `DPCSSYS_CR1_LANE1_*` or `DPCSSYS_CR1_LANE2_*` shift/mask symbols.
- Generated-table sanity: lane 1 and lane 2 fields are paired with the correct companion DPCS register addresses and retain matching repeated-family layouts where expected.
- DP/link smoke tests: hotplug, modeset, lane-count and lane-rate changes, link retraining, suspend/resume, GPU reset, and power-gating recovery across displays that exercise CR1 lanes 1 and 2.
- PHY bring-up checks: TX/RX P-state transitions, RX AFE/clock/CDR/deserializer enable sequencing, VCO calibration done, DPLL frequency status, DCC DAC ack/status, and calibration timeout behavior.
- Signal-integrity checks: adaptation convergence, ATT/VGA/CTLE/DFE status readback, slicer offset behavior, signal detect, and CDR lock status under varying link rates and cable/sink conditions.
- Diagnostic checks: LBERT mode/error counts, statistic sample counters and match patterns, OCLA/ASIC mirror fields, analog status/readback, and MPHY PWM/termination/stable-clock fields.

## Chunk Notes

This is a source-tree-aligned chunk report only. It intentionally does not create the final per-file synthesis for `dpcs_3_1_4_sh_mask.h`; that merge is left for the reconciliation lane after all chunks for this generated header are available.

### subset-b-002268: lines 21928-24369

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 21928-24369

## Scope

This chunk is part of AMD's generated DPCS 3.1.4 register shift/mask header. It contains only preprocessor constants for DisplayPort/PHY control-system bitfields: every field is represented by a `...__SHIFT` bit position and a matching `..._MASK` value. There are no functions, structs, enums, variables, includes, branches, locks, allocations, or direct MMIO operations in this range.

The requested slice contains 2,144 `#define` lines: 1,072 shift macros and 1,072 mask macros across 292 distinct register-name prefixes. It starts at an artificial boundary with two trailing masks for `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT`, covers lane-2 analog control tail, the lane-3 ASIC/TX/RX-stat/analog subset, CR1 raw common PLL/AON controls, and the beginning of rawlane0 PCS/FSM/IRQ/PMA interfaces. It ends inside `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`, after the first two RX PMA override shift fields.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement distributed filesystem behavior.

## Purpose

The purpose of this range is to publish exact bitfield metadata for DPCS CR1 lane and raw PHY registers used by AMD display link/PHY code. Runtime code pairs these field constants with matching register offsets from `dpcs_3_1_4_offset.h` and AMD display register helpers to perform masked reads, writes, updates, polls, and status extraction without hard-coded bit arithmetic.

Important covered surfaces:

- Lane-2 analog TX/RX controls: TX analog override outputs, termination code override, equalization/pre/post cursor fields, DCC DAC override, TX power/ATB/misc controls, RX analog power/control overrides, CDR/VCO tuning, calibration DAC controls, AFE attenuation/VGA/CTLE, slicer/scope controls, IQ phase/sense controls, signal-detect overrides, and analog status mirrors.
- Lane-3 digital ASIC and analog TX controls: lane override inputs, TX override inputs and ASIC input mirrors, RX override output/status mirrors, lane-3 TX power-state programming, TX power-up timing, DCC controls, clock alignment, LBERT, RX statistic match/counter controls, and analog TX override/direct analog fields.
- CR1 raw common controls: common enable bits, MPLLA/MPLLB override and spread-spectrum controls, lane FSM extension, CMN control, MPLL state, TX calibration code, SRAM init status, OCLA, supervisor analog overrides, PCS/FW ID words, AON RTUNE RX/TXDN/TXUP values, AON SRAM/power-gate/supervisor/resource overrides, VREF status, reference range, and miscellaneous common configuration.
- Rawlane0 PCS transfer controls: TX/RX PCS override inputs, live PCS input/output mirrors, RX adaptation acknowledge/FOM and TX pre/main/post direction fields, lane number/reserved fields, ATE override, RX equalization override, TX/RX termination controls, and phase-2 calibration controls.
- Rawlane0 FSM/IRQ/PMA controls: FSM override/status and fast-state monitors, TX DCC flags/status, calibration status, RX IQ phase offset, RX/TX request/rate/pstate/adaptation/loopback/DCC interrupt status and clear fields, IRQ masks, PMA lane/supervisor override inputs/outputs, TX PMA override output, TX PMA acknowledge, and the beginning of RX PMA override output.

## Important APIs, Types, And Macros

There are no typed C APIs in this chunk. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's starting bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used by register helpers to preserve unrelated fields during read-modify-write.
- Register comments such as `//DPCSSYS_CR1_RAWCMN_DIG_MPLLA_OVRD_IN` delimit generated register blocks and match `ixDPCSSYS_...` names in the offset header.

Major macro families include:

- `DPCSSYS_CR1_LANE2_DIG_ANA_*` and `DPCSSYS_CR1_LANE2_ANA_*` for lane-2 analog TX/RX override, direct analog, DCC, termination, equalization, calibration, and status fields.
- `DPCSSYS_CR1_LANE3_DIG_ASIC_*`, `DPCSSYS_CR1_LANE3_DIG_TX_PWRCTL_*`, `DPCSSYS_CR1_LANE3_DIG_RX_STAT_*`, and `DPCSSYS_CR1_LANE3_DIG_ANA_*` for lane-3 ASIC-facing signal handoff, power control, RX statistics, and analog TX controls.
- `DPCSSYS_CR1_RAWCMN_DIG_*` and `DPCSSYS_CR1_RAWCMN_DIG_AON_CMN_*` for common raw DPCS PLL, spread-spectrum, SRAM, firmware identity, OCLA, supervisor, RTUNE, VREF, power-good, reset, isolation, resource-request, reference-range, and REXT fields.
- `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_*` for rawlane0 PCS-side TX/RX override, PCS input/output mirrors, adaptation feedback, term-control, ATE, equalization, and phase-2 calibration fields.
- `DPCSSYS_CR1_RAWLANE0_DIG_FSM_*` for rawlane0 FSM override, memory address/status monitoring, fast calibration/adaptation state flags, TX DCC flags/status, TX EQ update flag, CMN calibration status, and RX IQ phase offset.
- `DPCSSYS_CR1_RAWLANE0_DIG_IRQ_CTL_*` for lane IRQ status, clear, and mask bits covering RX reset/request/rate/pstate/adaptation, lane transceiver mode, phase-2 calibration, RX-to-TX serial loopback, DCC on-demand, TX reset, and TX request events.
- `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_*` for PMA-side lane/MPLL supervisor handshakes, TX PMA request/reset/beacon/async/data-enable overrides, TX acknowledge, and the start of RX request override metadata.

The instance prefixes are semantically significant. Lane-2 and lane-3 fields describe different physical lanes, `RAWCMN` describes shared common PHY resources, and `RAWLANE0` describes the first raw lane interface. The same-looking bit layouts must remain paired with their matching offsets and resource instances.

## Control Flow

This header has no executable control flow. Runtime flow is created by consumers that include this file with the matching offset header and expand register/field names into register tables.

Typical use is:

1. DPCS 3.1.4-aware AMD display code includes `dpcs_3_1_4_offset.h` for `ixDPCSSYS_*` register addresses and `dpcs_3_1_4_sh_mask.h` for field positions and masks.
2. Register-list macros or block-specific tables token-paste register and field names into descriptors.
3. Runtime paths call AMD register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, or polling/wait helpers.
4. Link, PHY, diagnostics, and power-management code uses the generated constants while programming DisplayPort lanes, PLLs, analog tuning, calibration, statistics, interrupts, and PMA/PCS handshakes.

The hardware programming order is not encoded here. Consumers must still sequence resets, power states, reference clocks, MPLLA/MPLLB selection, analog overrides, calibration, RX adaptation, statistic sampling, IRQ clearing, and PMA/PCS handshakes according to the DPCS hardware model.

## State And Persistence Behavior

The file itself stores no mutable or persistent software state. All represented state lives in hardware registers.

Hardware-backed state described by this chunk includes:

- Lane-2 analog TX/RX override and status state: clocks, data enable, reference generator, VCM hold, PLL clock enables, resets, serial enable, data rate, RX detect, termination, equalization leg pull controls, pre/post cursor controls, DCC DAC values, power controls, CDR/VCO settings, calibration modes, AFE/CTLE settings, slicer/scope controls, signal-detect settings, and ATB measurement selections.
- Lane-3 lane/ASIC and TX/RX state: TX request/reset/pstate/rate/width, MPLL selects/enables, low-power disable, beacon/async controls, VBOOST/IBOOST, RX detect/valid/signal-detect, TX power-state and timing controls, RX statistic counters and match controls, and analog TX override/direct state.
- Raw common state: common enables, MPLLA/MPLLB overrides and acknowledgements, spread-spectrum control, firmware/PCS IDs, SRAM init, supervisor analog overrides, RTUNE values for RX and TX termination, AON power-good/reset/isolation overrides, VREF status, resource request/ack, reference range, and miscellaneous common configuration.
- Rawlane0 PCS/FSM/IRQ/PMA state: PCS TX/RX request/rate/width/pstate and override state, adaptation feedback and FOM, termination controls, phase-2 calibration, FSM fast-state flags, TX DCC status, CMN calibration status, IRQ status/clear/mask bits, PMA lane/supervisor state, TX PMA overrides, TX acknowledge, and the first RX PMA override fields.

Persistence is hardware-defined. Configuration and override fields generally remain programmed until another link-training, modeset, diagnostics, suspend/resume, power-gating, display-engine reset, GPU reset, or ASIC reset path rewrites them. Status, ack, done, pending, interrupt, clear, and calibration fields may be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the relevant common/lane clocks and power domains are active. This generated header does not encode those access semantics.

## Dependencies And Integration Points

Direct dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies the matching `ixDPCSSYS_*` register offsets, including lane-2 analog registers around `0x12a0`, lane-3 registers around `0x1300`, raw common registers around `0x2000`, and rawlane0 PCS/FSM/IRQ/PMA registers starting around `0x3000`.
- AMD display register-helper infrastructure supplies the masked register access macros that consume `__SHIFT` and `_MASK` symbols.
- AMD's DPCS 3.1.4 register database is the authoritative source for the generated names and bit positions.

Important integration points:

- DisplayPort link and PHY programming paths use the lane and rawlane fields for lane enablement, rate/width selection, TX/RX requests, reset handshakes, power-state transitions, PLL selection, and PMA/PCS signal handoff.
- PHY analog tuning and calibration paths use termination, DCC DAC, equalization, AFE, CTLE, CDR/VCO, slicer, phase, VREF, RTUNE, and calibration-status fields.
- Diagnostics, bring-up, and factory/test flows use RX statistic counters, pattern match controls, LBERT, OCLA, ATB controls, ATE overrides, DCC status, TX EQ update flags, and raw FSM monitors.
- Interrupt and event handling paths use the rawlane0 IRQ status, clear, and mask fields for RX/TX requests, resets, pstate/rate changes, adaptation requests/disables, phase-2 calibration events, lane transceiver mode events, loopback events, and DCC on-demand events.
- Low-power, suspend/resume, hotplug, and reset flows depend on correct power-good, isolation, reset, resource request/ack, SRAM init, MPLL, and PMA/PCS supervisor fields.

## Risks And Failure Modes

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while corrupting an adjacent hardware field in the same register.
- Chunk boundaries are not semantic. This range begins with masks whose shifts are in the previous chunk and ends before the masks for `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`; final per-file reconciliation must merge neighboring chunks.
- Lane instance alignment is critical. Accidentally pairing `LANE2`, `LANE3`, `RAWCMN`, or `RAWLANE0` field constants with the wrong offset can program a different physical lane or a shared common resource.
- Override-enable fields are high risk. Leaving TX/RX analog, PCS, PMA, PLL, power, or supervisor overrides asserted after test or training can force stale state and break later hotplug, retraining, suspend/resume, or modeset paths.
- PLL, reference-clock, power-good, isolation, and reset fields are sequencing-sensitive. Writes while the target block is off or unstable can be ignored, produce stuck waits, or create transient hardware states not represented in this header.
- Analog tuning fields are hardware-sensitive. Bad termination, DCC DAC, equalization, AFE/CTLE, CDR/VCO, VREF, RTUNE, slicer, or phase masks can cause link training failures, high-rate signal integrity problems, or lane-specific display instability.
- Status, clear, and IRQ fields need correct access semantics in callers. Misusing write-one-to-clear, self-clearing, sticky, or read-only fields can lose events or leave stale interrupts asserted.
- RX statistic and diagnostic fields can produce false validation if counters, stop bits, match masks, or sample status are read while clocks are gated or while the lane is not in the expected state.

## Test Signals

Useful validation signals include:

- Build AMDGPU display support with DPCS 3.1.4 headers enabled. Missing or renamed macros should fail in register-table, link, PHY, diagnostics, or interrupt code that references these DPCSSYS fields.
- Mechanically verify shift/mask pairing for lines 21928-24369, allowing the known boundary cases at `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT` and `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`.
- Diff this range against AMD's authoritative DPCS 3.1.4 register database and the matching `dpcs_3_1_4_offset.h` so every field name maps to the intended register offset and instance.
- Exercise DisplayPort link training/retraining across lane counts that include lanes 2 and 3, multiple rates, hotplug, HPD IRQ, suspend/resume, display-engine reset, GPU reset, and low-power transitions.
- Validate analog and calibration paths by monitoring DCC, termination, EQ, AFE/CTLE, CDR/VCO, signal-detect, VREF, RTUNE, CMN calibration, and phase-2 calibration status on real hardware.
- Exercise rawlane0 PCS/PMA handshakes and IRQ flows: RX/TX request/reset, rate and pstate changes, adaptation request/disable, phase-2 calibration request/disable, lane transceiver mode, RX-to-TX loopback, DCC on-demand, IRQ mask/unmask, and clear behavior.
- Use diagnostics such as RX statistic counters, match controls, LBERT, OCLA, ATB, TX DCC status, TX EQ update flag, and FSM fast-state monitors. Expected signals are no stuck waits, no unexpected IRQ storms, stable link training, correct lane power state, and no failures isolated to lane 2, lane 3, or rawlane0.

## Cross-Chunk Notes

This is a source-tree-aligned chunk report only. The previous chunk is needed for the complete `DPCSSYS_CR1_LANE2_DIG_MPHY_RX_ANA_PWM_CLK_STABLE_CNT` register, and the next chunk is needed for the rest of `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT` and later rawlane0 PMA/TX/RX control fields. The final per-file report should merge adjacent chunks before making complete claims about the full `dpcs_3_1_4_sh_mask.h` namespace.

### subset-b-002269: lines 24370-26787

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 24370-26787

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for DCN 3.1.4 display PHY/link hardware. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks for indexed DPCS CR registers under `DPCSSYS_CR1_RAWLANE*`.

The requested range contains 2,145 `#define` entries: 1,073 `__SHIFT` macros and 1,072 `_MASK` macros. The line boundary is artificial. The chunk starts in the middle of `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`, after the `RX_REQ_*` shifts but before their masks, and ends inside `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`, before that register's masks.

Although this file lives under a local `ceph-client` source mirror, this is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The public surface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or updating that field.

The chunk covers DPCS CR1 raw-lane register fields for portions of lanes 0, 1, and 2:

- `DPCSSYS_CR1_RAWLANE0_*`: tail fields for lane 0, mostly PMA receive override/acknowledge, lane retune, MPHY override, RX adaptation override, TX/RX control, and ATE PCS override registers.
- `DPCSSYS_CR1_RAWLANE1_*`: a complete raw-lane 1 block, including PCS TX/RX override and PCS-facing state, RX adaptation status/FOM and TX equalization direction fields, lane number/reserved registers, ATE override fields, FSM monitor/fast-sequence status, IRQ status/clear/mask fields, PMA override/status registers, and TX/RX control registers.
- `DPCSSYS_CR1_RAWLANE2_*`: the beginning and most of raw-lane 2, with the same PCS, FSM, IRQ, PMA, TX control, RX control, and ATE override structure as lane 1, stopping midway through `ATE_RX_OVRD_IN_2`.

Important field families include:

- PCS TX controls: `PSTATE`, `LPD`, lane `WIDTH`, link `RATE`, `MPLLB_SEL`, `MPLL_EN`, `OVRD_EN`, master MPLL state overrides, `DETRX_REQ`, `VBOOST_EN`, `IBOOST_LVL`, beacon enable, serial loopback enable, TX data enable, and TX async data overrides.
- PCS RX controls and status: RX request/reset/rate/pstate/width/low-power/valid/data-enable inputs, loss-of-signal LFPS and threshold overrides, adaptation request/continuous flags, offset-cancel continuous flags, VCO/reference load overrides, RX adaptation acknowledge, figure-of-merit readback, and RX-to-TX equalization direction fields for pre/main/post cursor.
- PMA controls and handshakes: lane/PMA/supervisor override inputs and outputs, TX/RX PMA acknowledge fields, TX/RX PMA data-enable overrides, RX reset/request overrides, lane retune request and acknowledge, MPHY PWM/async/termination override fields, and RX IQ phase adjustment map override.
- FSM status and debug fields: override controls, memory-address monitor, current FSM state and substate, fast RX startup/adaptation/calibration stage bits, common calibration MPLL/RCAL status, TX DCC flags/status, OCLA control/status, TX EQ update flag, RX IQ phase offset, CR lock flags, and broad fast-state flag readbacks.
- IRQ fields: RX reset/request/rate/pstate/adaptation request/adaptation disable IRQ status and clear registers; lane transceiver mode IRQ; RX phase-2 calibration request/disable IRQs; lane RX-to-TX serial loopback IRQ; DCC on-demand IRQ; TX reset/request IRQs; and `IRQ_MASK`/`IRQ_MASK_2` enable masks.
- TX/RX control registers: TX FSM timing and RX detect permissions across power states, TX clock enable/source/beacon wait fields, TX DCC continuous status, RX control FSM enable and rate-change-in-P1 control, RX LOS mask count, RX data-enable override timing, and continuous offset-cancel/adaptation status.

Most registers in this slice are 16-bit indirect CR register layouts, visible from masks such as `0xFFFFL`, `0xFFFEL`, and field masks within bits 0-15.

## Control Flow

This header has no runtime control flow. Its role is compile-time metadata for AMDGPU display register helpers:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this shift/mask header.
2. Link encoder resource tables use token-pasting macros such as `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` to populate shift and mask structures.
3. Runtime link encoder code calls AMD display register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. The helpers combine register offsets, shifts, and masks to update DPCS fields without disturbing adjacent hardware bits.

The macros in this chunk do not encode sequencing. PHY reset, lane power state changes, MPLL selection, TX/RX request/ack handshakes, RX adaptation, calibration, IRQ acknowledgement, retuning, and loopback/test overrides are ordered by driver code and hardware specifications outside this generated file.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes hardware-visible lane state:

- Per-lane TX state for link rate/width, power state, low-power detect, MPLL enable/source, beaconing, voltage/current boost, TX data enable, async data, loopback, and reset/request handshakes.
- Per-lane RX state for request/reset/rate/pstate/width, RX valid/data enable, low-power detect, loss-of-signal threshold and LFPS behavior, adaptation request/continuous operation, offset-cancel continuous operation, RX IQ phase adjustment, and VCO/reference load override values.
- Calibration and monitor state for FSM fast-sequence progress, RX AFE/DFE/IQ/reference-level/VCO calibration, RX continuous adaptation/data/phase/AFE calibration, common MPLL/RCAL status, TX DCC state, CR lock, OCLA, and TX equalization update flags.
- Interrupt state for RX/TX request/reset/rate/pstate/adaptation/phase-calibration/loopback/DCC events, including separate clear and mask registers.
- PMA/MPHY handshakes, retune request/acknowledge state, and supervisor/PMA override paths.

Persistence and side effects are hardware-defined. Configuration fields usually remain until the lane is reprogrammed, the link is disabled, suspend/resume restores state, power gating removes state, or a GPU/ASIC reset occurs. Status, IRQ, clear, acknowledge, and monitor fields can be read-only, sticky, write-one-to-clear, self-clearing, or valid only while the DPCS block and relevant PHY clocks are powered. The generated masks do not carry access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 3.1.4 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` provides matching indirect register identifiers such as `ixDPCSSYS_CR1_RAWLANE1_DIG_*` and `ixDPCSSYS_CR1_RAWLANE2_DIG_*`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` directly includes both DPCS 3.1.4 generated headers and initializes link encoder shift/mask tables with `DPCS_DCN31_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines the DCN 3.1 DPCS register and field-list macros consumed by DCN 3.1.4 resources. Those public lists mostly expose the higher-level `RDPCSTX*` DPCS fields used by link encoder code; this chunk provides lower-level CR raw-lane fields that must remain name-compatible with generated indirect CR offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` and related DCN 3.1 link encoder paths consume the register tables for DP/HDMI PHY setup, transmitter enable/disable, DP Alt Mode checks, clocking, lane state, and DPCS interrupt control.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.*` uses related RDPCS/DPCS register metadata for high-performance DisplayPort link encoder behavior.

Behaviorally, this slice sits under display link bring-up and diagnostics: DP/HDMI PHY lane programming, receiver detection, link-rate and lane-width selection, MPLL state, lane calibration/adaptation, equalization, retuning, interrupt handling, test/ATE override paths, and debug/status readback.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while updating the wrong indirect CR bit.
- The file is generated. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first register has masks for fields whose shifts are in the previous chunk, while the final register has shifts whose masks are in the next chunk.
- Lane layouts are highly repetitive. A generator error can affect only raw lane 1 or raw lane 2, so one working lane does not prove the others are correct.
- Register names mix normal control, override, status, clear, mask, ATE, and reserved fields. Using a status/clear/mask field with the wrong access convention can leave IRQs stuck, miss lane events, or acknowledge the wrong condition.
- TX/RX power-state, rate, width, MPLL, and request/reset fields are sequencing-sensitive. Incorrect masks can cause failed link training, blank displays, unstable DP Alt Mode, bad HDMI/DP PHY enable, or resume-only failures.
- Calibration/adaptation fields are timing-sensitive. Bad masks around RX AFE/DFE/IQ/VCO/reference-level calibration or continuous adaptation can produce marginal links, intermittent bit errors, or failures only at high link rates.
- PMA and MPHY override fields can bypass normal hardware control. Accidentally enabling override bits or writing wrong override values can force lanes into loopback, reset, disabled data paths, invalid termination, or unsupported async/PWM modes.
- IRQ mask and clear fields are per-event and per-lane. Cross-lane copy mistakes can cause interrupt storms, lost RX/TX request transitions, or misleading diagnostics when only one connector path is active.
- Reserved field masks occupy large portions of many 16-bit registers. Read-modify-write paths must preserve reserved bits according to hardware guidance rather than assuming all visible bits are safe to modify.

## Test Signals

Useful validation combines generated-header consistency checks with hardware behavior:

- Build AMDGPU display support with DCN 3.1.4 enabled. Missing or renamed macros should surface in `dcn314_resource.c`, `dcn31_dio_link_encoder.h`, and related DPCS register-table construction.
- Mechanically compare lines 24370-26787 against AMD's authoritative DPCS 3.1.4 register database, including the boundary cases where fields are split across adjacent chunks.
- Cross-check every register prefix in this range against `dpcs_3_1_4_offset.h` to ensure corresponding `ixDPCSSYS_CR1_RAWLANE*` offsets exist.
- Run static checks that every complete field in this chunk has a paired `__SHIFT` and `_MASK`, allowing the known artificial boundary exceptions at `RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT` and `RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`.
- Compare repeated lane 1 and lane 2 layouts for expected structural identity, while accounting for the fact that lane 2 is truncated by this chunk boundary.
- Exercise DP and HDMI link bring-up, link training, disable/re-enable, hotplug, suspend/resume, and GPU reset on DCN 3.1.4 hardware. Expected signals are stable modesets, correct lane count/rate behavior, no stuck TX/RX request or reset handshakes, and no DPCS interrupt storms.
- Test high-rate DisplayPort modes, DP Alt Mode, MST where available, and reduced link-rate fallback to catch lane width/rate/MPLL/equalization mask issues.
- Capture DPCS/PHY register dumps during successful and failing link training to verify RX adaptation, calibration status, TX DCC status, CR lock, and IRQ bits decode consistently with the shift/mask definitions.
- Exercise diagnostic or manufacturing-style paths only in controlled environments: loopback, ATE overrides, PMA/MPHY overrides, OCLA, retune, and forced adaptation/offset-cancel controls.

## Cross-Chunk Notes

The previous chunk owns the beginning of raw lane 0 and the first two `RX_REQ_*` shifts for `DPCSSYS_CR1_RAWLANE0_DIG_PMA_XF_RX_OVRD_OUT`. This chunk then finishes the lane 0 tail and covers raw lane 1 fully. The next chunk must finish `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`, continue lane 2, and likely cover later lane 2/lane 3 definitions. The final per-file research document should reconcile those boundaries before making whole-file claims about all DPCS CR1 raw lanes.

### subset-b-002270: lines 26788-29265

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 26788-29265

## Purpose

This chunk is generated AMD DPCS 3.1.4 register-field metadata for the display PHY/controller side of AMDGPU. It contains no executable C logic; it exports preprocessor constants that describe bit shifts and bit masks for fields inside DPCS indexed registers. Consumers pair these macros with matching `ixDPCSSYS_*` offsets from `dpcs_3_1_4_offset.h` and AMD display register helpers to read, write, and update individual hardware fields.

The requested range contains 2,107 `#define` lines and 371 register-group comment markers. It starts inside the tail of `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`, then covers the rest of the raw lane 2 PCS tail. Most of the chunk covers raw lane 3 digital PCS, FSM, IRQ, PMA, TX control, RX control, and ATE override fields. The final section covers the start of CR1 always-on lane metadata for `RAWAONLANE0`, `RAWAONLANE1`, and `RAWAONLANE2`, ending at the beginning of `DPCSSYS_CR1_RAWAONLANE2_DIG_LANE_XCVR_MODE_OVRD_IN`.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, callbacks, or direct MMIO operations in this range. The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for encoding or decoding a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, preserving, clearing, or updating that field.

Major register groups in this chunk:

- `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_*` tail: ATE RX VCO/reference-load override fields, RX valid override output, and TX serial-loopback/data/async-data override fields for raw lane 2.
- `DPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_*`: raw lane 3 PCS transmit and receive control surfaces. These include TX/RX pstate, low-power detect, width, rate, MPLL selection/enables, master MPLL state overrides, reset/request handshakes, detection request/result bits, vboost/iboost, TX beacon, ACK/status outputs, RX loss-of-signal thresholds, RX adaptation request/continuous/off-candidate control, VCO/reference-load status, RX equalization and DFE coefficients, TX pre/main/post cursor direction fields, lane-number reporting, termination controls, phase-2 calibration, ATE overrides, loopback, and async data gating.
- `DPCSSYS_CR1_RAWLANE3_DIG_FSM_*`: raw lane 3 micro/FSM monitor, override, status, fast-sequence, calibration, adaptation, continuous-calibration, flag, CR-lock, TX DCC, OCLA, TX EQ update, CMN calibration, and RX IQ phase-offset fields.
- `DPCSSYS_CR1_RAWLANE3_DIG_IRQ_CTL_*`: IRQ status, clear, mask, and return-request fields for RX reset/request/rate/pstate/adaptation events, lane transceiver mode changes, RX phase-2 calibration request/disable, lane RX-to-TX serial loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR1_RAWLANE3_DIG_PMA_XF_*`: PMA lane/supervisor/TX/RX override and PMA input/output bridge fields, lane RTUNE control, MPHY override, and RX adaptation override output.
- `DPCSSYS_CR1_RAWLANE3_DIG_TX_CTL_*` and `RX_CTL_*`: lane-local TX/RX FSM control, TX clock control, TX DCC continuous status, RX LOS mask count, RX data-enable override, off-candidate/adaptation continuous status, and OCLA/debug fields.
- `DPCSSYS_CR1_RAWAONLANE0_DIG_*`, `RAWAONLANE1_DIG_*`, and beginning of `RAWAONLANE2_DIG_*`: always-on lane calibration/status/configuration metadata. These blocks repeat per lane and cover AFE/CTLE/DFE offset readbacks, RX IQ/adaptation/FOM, RX phase adjustment, coarse MPLL tuning, initial power-up status, RX adaptation tap results, slicer controls, common calibration statuses, adaptation-control registers, MPLL disable, TX/RX overrides, LOS and signal-detect filter controls, PMA squelch/termination/sigdet/vrefgen overrides, signal-detect calibration codes, RX DCC calibration codes, TX DCC bank address/data/continuous-enable, MPLL background delay control, firmware adaptation/calibration config, and lane transceiver mode override/input fields.

The companion offset header maps representative register names in this range to indexed addresses: lane 3 PCS begins at `ixDPCSSYS_CR1_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` `0x3300`; lane 3 IRQ mask fields sit around `0x334d` and `0x334e`; lane 3 PMA bridge fields begin at `0x3360`; lane 3 TX/RX control blocks begin at `0x3380` and `0x33a0`; ATE PCS fields resume at `0x33c0`; always-on lane 0, 1, and 2 blocks begin at `0x4000`, `0x4100`, and `0x4200`.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code and the hardware programming model:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`.
2. AMD display register-list macros token-paste register and field names into register, shift, and mask tables.
3. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and indexed-register variants to access DPCS registers through those tables.
4. The numeric values in this chunk determine which bits are touched when the display stack controls PHY lane state, link rate/width, lane power/reset/request handshakes, adaptation/calibration, IRQ masks and clears, PMA overrides, DCC, signal-detect, LOS, and diagnostics.

The macros do not define ordering rules. Consumers must still follow hardware sequencing for lane reset, request/ack handshakes, MPLL state changes, rate/width updates, RX adaptation, calibration start/done checks, interrupt acknowledgement, PMA override enable/disable, power gating, and display link training.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk. It describes hardware-backed state:

- Lane 2 and lane 3 PCS override state for TX/RX data enables, async data, serial/parallel loopback, reset/request controls, rate/width/pstate, MPLL selection, vboost/iboost, TX beacon, LOS thresholds, adaptation requests, and RX equalization controls.
- Lane 3 status and monitor state for TX/RX ACK, detection results, RX valid, adaptation ACK, FOM, TX pre/main/post direction, FSM state, calibration status, fast flags, CR lock, TX DCC status, TX EQ updates, CMN calibration, RX IQ phase offset, and OCLA/debug readbacks.
- Lane 3 IRQ status/mask/clear state for RX/TX request/reset, rate/pstate changes, adaptation, phase-2 calibration, lane mode changes, loopback, and DCC events.
- Always-on lane calibration and adaptation state for lanes 0 and 1 completely and lane 2 partially: AFE/DFE/CTLE offsets, tap values, slicer controls, RX signal-detect calibration codes, RX DCC calibration values, TX DCC bank address/data, MPLL background controls, firmware adaptation/calibration controls, and lane transceiver mode.

Persistence is hardware-defined. Configuration fields generally last until modeset, link retraining, PHY reset, suspend/resume, display block power gating, GPU reset, or driver reinitialization. Status, IRQ, calibration, adaptation, LOS, signal-detect, and DCC fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while relevant lane clocks and power domains are active. This generated header does not encode access type, reset value, volatility, write-one-to-clear semantics, or required polling delays.

## Dependencies And Integration Points

This generated header must stay synchronized with AMD's DPCS 3.1.4 register database and related display code:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies matching `ixDPCSSYS_*` offsets for every register family described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` includes both `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`, making this metadata part of DCN 3.1.4 display resource construction.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/reg_helper.h` and related AMD display register-helper infrastructure combine offsets, shifts, and masks for MMIO or indexed-register access.
- Adjacent generated ASIC headers such as `dcn_3_1_4_sh_mask.h` and later DPCS/DCN versions provide comparable field layouts for other display blocks and ASIC revisions; many lane and DPCS field names are shared across revisions.
- Runtime integration is with display link PHY bring-up, DisplayPort/HDMI link training, lane power/reset sequencing, PLL/MPLL control, RX adaptation and equalization, signal detection, DCC calibration, IRQ handling, diagnostics, and suspend/resume restore paths.

The practical API contract is compile-time: code that names a register field through AMD's register macros requires the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` definitions to exist and match the silicon layout.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while reading or modifying the wrong hardware bits.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the companion offset header, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first line is inside `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`; the earlier VCO fields are in the previous chunk. The final lines stop inside `DPCSSYS_CR1_RAWAONLANE2_DIG_LANE_XCVR_MODE_OVRD_IN`; the remaining lane 2 transceiver mode and later always-on lane 2/3 fields continue in the next chunk.
- Repeated lane blocks are copy-sensitive. Lane 0, lane 1, lane 2, and lane 3 layouts are structurally similar but independently named; an instance-specific generation error may affect only one physical lane and may be missed by testing that exercises fewer lanes or lower link widths.
- Override-enable pairs are hazardous. Many fields use a value bit plus an override-enable bit; setting only the value, setting only the enable, or using a mask from the wrong lane can leave hardware under autonomous control or force an unintended PHY state.
- Reset/request/ACK, adaptation, calibration, and IRQ clear fields are sequencing-sensitive. Incorrect masks can cause link bring-up timeouts, stuck adaptation, missed calibration completion, repeated interrupts, or premature progression while the PHY is not ready.
- Rate, width, pstate, MPLL, vboost, iboost, termination, RTUNE, DFE, CTLE, VREF, signal-detect, and LOS fields directly affect electrical behavior. Bad masks can manifest as link-training failures, intermittent high-rate failures, degraded margins, black screens, or resume-only failures.
- Status and debug fields can be invalid while a lane is powered down, clock-gated, reset, or assigned to another mode. Diagnostics that ignore power/lane ownership can misinterpret stale hardware state.
- Always-on DCC and calibration bank fields use address/data-style registers. Wrong masks or ordering can corrupt calibration read/write access instead of just producing a bad readback.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display link behavior:

- Build AMDGPU DCN 3.1.4 display support. Missing or renamed DPCS macros should fail in resource/register-table construction paths that include `dpcs_3_1_4_sh_mask.h`.
- Mechanically verify that every field in this chunk has the expected `__SHIFT` and `_MASK` pair, while allowing boundary exceptions where a pair is split across adjacent chunks.
- Cross-check every register group in this slice against `dpcs_3_1_4_offset.h` so register names in the shift/mask header have matching `ixDPCSSYS_*` addresses.
- Diff this chunk against AMD's authoritative DPCS 3.1.4 register database and against compatible generated DPCS/DCN headers where identical lane layouts are expected.
- Exercise DisplayPort and HDMI link bring-up across lane counts and link rates that use lane 3 and the always-on lane blocks: hotplug, modeset, link retraining, low-power transitions, suspend/resume, GPU reset recovery, and high-bandwidth modes.
- Monitor link-training status, PHY lane ready/ACK bits, RX adaptation done/FOM, LOS/signal-detect status, DCC/calibration status, IRQ counters, and kernel logs for stuck bits, repeated IRQs, missed completions, or lane-specific failures.
- Test loopback, ATE/diagnostic, and OCLA/debug access only where supported by hardware/lab tooling; these fields can force non-normal PHY states and should not be exercised blindly on production paths.
- Compare register dumps before and after modeset, retrain, suspend/resume, and reset to confirm that pstate/rate/width, MPLL, override-enable, IRQ mask/clear, signal-detect, and calibration fields are restored coherently.

## Cross-Chunk Notes

The previous chunk owns the beginning of raw lane 2 PCS/ATE RX override metadata and the earlier fields of `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_ATE_RX_OVRD_IN_2`. This chunk owns the raw lane 2 tail, the complete raw lane 3 PCS/FSM/IRQ/PMA/TX/RX-control/ATE surface, complete always-on lane 0 and lane 1 metadata, and most of always-on lane 2 through the start of `LANE_XCVR_MODE_OVRD_IN`. The next chunk should complete always-on lane 2 and cover the remaining generated DPCS fields. The final per-file research document should reconcile these artificial boundaries before making whole-file claims about all DPCS 3.1.4 lane metadata.

### subset-b-002271: lines 29266-31717

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 29266-31717

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for `DPCSSYS_CR1` PHY control-register fields. It contains preprocessor constants that describe bit positions and masks for a large run of 16-bit CR registers covering:

- the tail of RAW always-on lane 2 receiver/transceiver controls;
- the complete RAW always-on lane 3 receiver adaptation, DFE, slicer, MPLL, signal-detect, DCC, firmware, and transceiver-mode field set;
- the generic `RAWAONLANEX` version of the same lane field layout at the lane-X address window;
- the CR1 supervisor (`SUPX`) PLL, reference-clock, bandgap, rtune, analog override/status, and power-timer controls;
- the beginning of the `LANEX` ASIC-lane and transmit power-control register layout, ending at `TX_PWRCTL_TX_PWRUP_TIME_0`.

The header has no executable logic. Its purpose is to let DCN 3.1.4 display/link encoder code build register field tables and perform CR/MMIO read-modify-write operations with stable generated names instead of open-coded bit constants. Although this repository path is under `ceph-client`, the file is AMDGPU display hardware metadata, not distributed filesystem code.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, globals, locks, allocations, callbacks, or inline helpers in this range. The exported API is entirely macro based:

- `DPCSSYS_CR1_*__*__SHIFT` gives the bit offset for a hardware field.
- `DPCSSYS_CR1_*__*_MASK` gives the mask for preserving, extracting, clearing, or updating that field.

The main register families in this chunk are:

- `DPCSSYS_CR1_RAWAONLANE2_DIG_*`: finishes the lane 2 `LANE_XCVR_MODE_OVRD_IN`, `LANE_XCVR_MODE_IN`, and `RX_SIGDET_CONFIG` definitions. The first line is a continuation from the previous chunk, so the complete `LANE_XCVR_MODE_OVRD_IN` field set must be reconciled across chunk boundaries.
- `DPCSSYS_CR1_RAWAONLANE3_DIG_*`: per-lane receiver/PHY metadata for lane 3. Fields include RX adaptation values (`IQ`, `ATT`, `VGA`, `CTLE`, `DFE_TAP1` through `DFE_TAP5`), DFE offset/reference-level registers, phase adjust registers, slicer controls, common calibration status, adaptation control words `ADPT_CTL_0` through `ADPT_CTL_7`, MPLL disable/control fields, fast-mode flags, TX/RX override inputs, loss-of-signal and signal-detect controls, statistics/status bits, RX override outputs, RX signal-detect calibration/code registers, VREF/calibration-code registers, RX DCC calibration code banks, TX DCC bank address/data/control fields, MPLL bandgap controls, firmware adaptation/calibration words, lane transceiver mode override/input fields, and RX signal-detect filter counters.
- `DPCSSYS_CR1_RAWAONLANEX_DIG_*`: the same RAW always-on lane pattern generalized to a lane-X window. The field names mirror the lane 3 fields and are paired with a separate address window in `dpcs_3_1_4_offset.h`, allowing code or diagnostics to address the generic lane instance instead of a fixed lane number.
- `DPCSSYS_CR1_SUPX_DIG_*` and `DPCSSYS_CR1_SUPX_ANA_*`: supervisor-level PLL/reference/analog controls. These define ID-code fields, reference-clock override, MPLLA/MPLLB divided and HDMI clock override/input fields, MPLLA/MPLLB override words, SSC peak/step-size fields, charge-pump override/status fields, prescaler, support-level override/status, ASIC input mirrors, bandgap input/status/override, analog prescaler/rtune/bandgap controls, MPLL power-control override/status/timer/calibration/DAC fields, SSC spread type, clock/reset power-up timers, reference VPHUD timing, rtune configuration/status/set-value/stat fields, TX calibration code, and analog override/status outputs.
- `DPCSSYS_CR1_LANEX_DIG_*`: lane-X ASIC-facing lane/TX/RX override and status fields plus the start of TX power-control p-state timing. This chunk includes lane override input, TX override inputs 0-5, TX override outputs, RX override inputs/outputs and EQ/CDR/ASIC input mirrors, OCLA enable bits, and TX p-state controls for `P0`, `P0S`, `P1`, and `P2`.

Most masks in this slice are 16-bit values using the generated `0x....L` convention. Several logical values span split fields across adjacent registers, such as MPLL SSC peak/step-size words, MPLL fractional-N values, VCM hold timers, VBOOST disable timers, and pstate/timer fields. Some register comments intentionally have no following field macros in this chunk, for example reserved or empty generated placeholders such as `DIG_TX_DCC_CONFIG` and `FW_MM_CONFIG`.

## Control Flow

This chunk has no runtime control flow. It participates in driver control paths indirectly:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this shift/mask header.
2. Register-list macros and field-list macros token-paste generated register names with `_BASE_IDX`, address, `__SHIFT`, and `_MASK` suffixes.
3. Link encoder and HPO DP link encoder objects receive register offsets and field masks through static tables in `dcn314_resource.c`.
4. Runtime display/link code uses those tables through register helper paths to program DP/HDMI PHY state, PLL state, lane p-states, lane overrides, training-related controls, and status reads.

The generated constants do not encode sequencing. Consumers still need to follow PHY bring-up, link training, clock/PLL programming, and suspend/resume ordering: select PLL/reference clocks, wait for lock/stable indications, program per-lane rates and widths, manage p-states, apply overrides only when safe, and clear or restore diagnostic/firmware control bits after use.

## State And Persistence Behavior

The header itself stores no state and persists nothing. The underlying registers represent live PHY and analog state:

- RAWAON lane fields hold receiver adaptation results, calibration codes, signal-detect thresholds, transceiver mode bits, DFE and slicer settings, and lane-local override/status state.
- `FAST_FLAGS` and `FAST_FLAGS_2` fields can alter or skip calibration/adaptation waits. If enabled in live hardware, they persist until reset or driver/firmware reprogramming and can shorten training at the cost of relying on previous calibration state.
- Supervisor fields persist PLL, reference-clock, bandgap, prescaler, rtune, SSC, charge-pump, timer, DAC, and analog override state while the DPCS block remains powered.
- LANEX override and p-state fields persist transmit/receive lane override state and p-state enable/reset/data/clock/serial settings. These are hardware control bits, not software cache variables.
- Status-like fields such as common-calibration done, rtune status, ASIC input mirrors, analog status, and override output mirrors are observations of hardware state. This header does not identify read-only, write-one-to-clear, sticky, self-clearing, or firmware-owned semantics.

The driver must treat these masks as an ABI to the ASIC register database. Reset values, access permissions, side effects, and power-domain persistence are defined by the hardware spec and driver sequencing, not by this header.

## Dependencies And Integration Points

The immediate companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which defines the matching CR register addresses. In the corresponding offset range, lane 3 registers occupy `0x4300` through `0x4351`, generic `RAWAONLANEX` registers occupy `0x7000` through `0x7051`, supervisor registers start at `0x8000`, and LANEX ASIC/TX power-control registers start at `0x9000`.

The exact DPCS 3.1.4 headers are included directly by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`. That file uses:

- `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)` to populate `struct dcn10_link_enc_shift` and `struct dcn10_link_enc_mask` tables.
- `DCN3_1_RDPCSTX_REG_LIST(...)` to populate HPO DP link encoder register tables.
- register helper infrastructure from `reg_helper.h` to map generated register metadata into runtime register access.

The specific macros in this chunk are lower-level DPCS CR field definitions than the public link encoder tables usually expose. They can still be consumed by indirect CR address/data paths, diagnostics, bring-up scripts, firmware flows, or future link encoder changes that need detailed PHY calibration, analog, or override fields. The repeated lane 3 and lane-X layouts are an important consistency contract with the offset header and with adjacent generated DPCS versions such as 4.2.x.

## Risks And Edge Cases

- A wrong shift or mask compiles cleanly but can program the wrong PHY bits, leading to link-training failures, unstable high-bit-rate links, lost signal detect, bad PLL lock behavior, or intermittent display/audio link faults.
- This chunk starts mid-register for `DPCSSYS_CR1_RAWAONLANE2_DIG_LANE_XCVR_MODE_OVRD_IN`; completeness checks for that register require the previous chunk.
- This chunk ends at `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_0`; the rest of the TX power-up timing and later LANEX power-control fields are in the next chunk.
- Many fields are hardware or firmware override enables paired with override values. Setting an override-enable bit without a valid value, or leaving overrides asserted after diagnostic use, can block normal firmware/hardware control.
- Reserved masks are present throughout. Whole-register writes that do not preserve reserved bits risk toggling undocumented behavior or diverging from firmware-owned state.
- Split fields require coordinated programming across multiple registers. Examples include SSC peak/step-size, MPLL timers, VCM hold timing, VBOOST disable timing, and multi-bank DCC/calibration values.
- Calibration skip/fast flags can reduce required waits only under valid preconditions. Misuse may make problems appear data-rate, temperature, or resume dependent.
- Status fields and output mirror fields are not necessarily writable. Treating them as ordinary RMW targets can be harmless on one ASIC revision and harmful on another.
- Generated DPCS 3.1.4 naming overlaps with generated DCN 4.1.0 and DPCS 4.2.x headers. Consumers must include the ASIC-matched offset and mask headers together; mixing versions can silently produce valid C with wrong hardware layout.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN 3.1.4 enabled. Missing or renamed macros should surface where `dcn314_resource.c` initializes link encoder and HPO DP link encoder register/field tables.
- Mechanically compare each complete register in this chunk against `dpcs_3_1_4_offset.h` and the generated AMD register database. Every non-placeholder field should have a matching `__SHIFT` and `_MASK` pair.
- Cross-check lane 3 and `RAWAONLANEX` field layouts for parity where the hardware intends the generic lane window to mirror fixed lane registers.
- Exercise DP and HDMI link bring-up on DCN 3.1.4 hardware across lane counts, link rates, voltage swing/pre-emphasis levels, hotplug cycles, and suspend/resume.
- Stress PHY power transitions and p-state changes, especially `P0`, `P0S`, `P1`, `P2`, clock/data/serial enable bits, reset bits, RX-detect allowance, and VBOOST/DCC calibration behavior.
- Use debug or hardware-trace paths to read PLL lock/stable status, signal-detect status, rtune status, calibration-done status, and lane statistics after link training and resume.
- Compare register dumps before and after link training or suspend/resume to ensure override bits, reserved bits, and fast-calibration flags are restored or preserved as expected.

## Cross-Chunk Notes

This slice contains 2,452 lines, 316 register-comment markers, and 2,136 `#define` lines. It is the middle of a much larger generated DPCS 3.1.4 mask header, so final per-file research should reconcile:

- the preceding chunk for the start of lane 2 `LANE_XCVR_MODE_OVRD_IN`;
- this chunk for full lane 3, lane-X, supervisor, and early LANEX TX power-control coverage;
- the following chunk for the remainder of LANEX TX power-up timing, DCC, clock-align, LBERT, RX power-control, and later fields.

### subset-b-002272: lines 31718-34157

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 31718-34157

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for display PHY/controller register fields. It contains no executable C logic; its public surface is a set of preprocessor constants that encode bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCS register fields.

The requested range contains 2,142 `#define` entries over 2,440 lines. It starts inside the `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_0` field pair, covers a large CR1 per-lane TX/RX/PCS/PMA/FSM/IRQ register-field section, then crosses into the `addressBlock: dpcssys_cr2_rdpcstxcrind` supervisor/common PLL block. The range ends inside `DPCSSYS_CR2_SUP_DIG_MPLLA_SSC_PEAK_2`, before that register's mask definitions.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct MMIO accesses in this range. The exported interface is the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the hardware register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.

The main register-field families in this chunk are:

- TX lane power and timing fields: `TX_PWRUP_TIME_0-5`, DCC control-bank address/data, DCC DAC control/range/select/ack/address, TX clock alignment, and TX LBERT pattern/error-injection controls.
- RX lane power state and bring-up fields: `RX_PSTATE_P0`, `P0S`, `P1`, `P2`, RX power-up timers, analog AFE/clock/deserializer/CDR enable bits, VCO reset/calibration bits, and digital clock enable bits.
- RX VCO and CDR fields: VCO calibration control, start values, calibration steps, result/status readbacks, CDR SSC on/off counters, loop gain override fields, DPLL frequency, and frequency-bound enable/range fields.
- RX adaptation and equalization fields: adaptation configuration registers, reset controls, attenuation/VGA/CTLE/DFE tap status, DFE data/error DAC offsets, slicer controls, DAC control selectors, and indirect CR bank address/data.
- RX status/statistics fields: load-value, data mask, match controls, statistic controls, sample counts, statistic counters, calibration-comparison clock control, and statistic stop fields.
- MPHY and analog lane fields: MPHY PWM/termination/stable-count fields, analog TX/RX override outputs, TX equalization override fields, RX DAC/AFE/CTLE/scope/slicer/IQ/calibration controls, analog status, termination-code overrides, signal-detect overrides, TX DCC DAC overrides, and raw analog TX/RX control/readback registers.
- Raw lane PCS/PMA transfer fields: TX/RX override input/output, PCS input/output, ACK handshakes, pstate and MPLL select/enable fields, serial/parallel loopback controls, lane number, RX adaptation ACK/FOM, directed TX pre/main/post cursor fields, ATE override surfaces, RX EQ override fields, PMA lane/supervisor override and status fields, MPHY override fields, and RX adaptation override output.
- Raw lane FSM and IRQ fields: FSM override, memory/status monitors, fast RX startup/adaptation/calibration/power-up/VCO wait/VCO cal controls, common calibration status, fast flags, CR lock, TX DCC flags/status, OCLA debug fields, TX EQ update flag, RX IQ phase offset, RX/TX reset/request/rate/pstate/adaptation IRQs, clear registers, IRQ masks, lane transceiver-mode IRQs, loopback IRQs, PH2 calibration IRQs, and DCC on-demand/TX IRQ fields.
- Raw lane TX/RX control fields: TX FSM/clock controls, TX DCC continuous status, OCLA/UPCS OCLA fields, RX FSM/LOS mask/data-enable override controls, off-cancel/continuous-adaptation status, and RX UPCS OCLA.
- CR2 supervisor/common PLL fields: ID code placeholders, reference-clock override fields, MPLLA/MPLLB divider and HDMI clock override fields, MPLLA enable/divider/VCO/calibration/frac-N/SSC fields, MPLLA multiplier, and the beginning of MPLLA SSC peak programming.

Most masks in this range are 16-bit style values ending in `L`, matching the DPCS indirect-register field width used by these lane and supervisor blocks.

## Control Flow

This header has no runtime control flow. It participates in compile-time register-table construction:

1. DCN 3.1.4 resource code includes `dpcs_3_1_4_offset.h` and this matching `dpcs_3_1_4_sh_mask.h`.
2. Register-list and shift/mask-list macros token-paste DPCS register and field names into typed tables for the display resource pool and PHY/link encoder plumbing.
3. Runtime display code uses AMD register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` with those offset/shift/mask tables.
4. The actual sequencing for power-up, PLL programming, lane training, calibration, interrupt handling, and debug readback is implemented in DC/link/PHY code and hardware state machines outside this generated header.

The macros in this chunk describe where bits live; they do not encode which fields are read-only, write-one-to-clear, self-clearing, latched, or sequencing-sensitive.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible state in DPCS CR1 per-lane and CR2 supervisor/common registers:

- TX and RX power-state configuration, including analog enable, clock enable, reset, data enable, receive-detect, common-mode, Vboost, DCC compensation, and programmed bring-up delays.
- Calibration and adaptation state for RX VCO, CDR/DPLL, AFE, VGA, CTLE, DFE taps, slicer offsets, IQ phase, and continuous adaptation controls.
- Test and diagnostic state for LBERT, OCLA, alternate buses, analog test bus measurement, statistic counters, match controls, debug selectors, and raw status/readback fields.
- PCS/PMA handshake state for pstate, MPLL selection and enablement, lane override enables, ACK bits, lane numbering, RX valid override, TX/RX serial or parallel loopback, and RX/TX directed coefficient controls.
- Interrupt state for RX/TX reset and request events, rate and pstate changes, adaptation request/disable events, PH2 calibration request/disable events, lane mode changes, loopback enable changes, and DCC on-demand events.
- Supervisor PLL/reference-clock state for reference clock source/range, bandgap, HDMI mode, MPLLA/MPLLB divider/HDMI clock overrides, MPLLA enable, standby, VCO frequency, calibration force, fractional-N, SSC enable/update, and SSC peak programming.

Persistence is hardware-defined. Configuration fields generally remain until link reprogramming, modeset, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, ACK, IRQ, and statistics fields may be latched, clear-on-write, sampled, self-clearing, or valid only while the lane/common PLL power and clock domains are active. This generated header does not record those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 3.1.4 register database and its companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies matching `ixDPCSSYS_*` register offsets for the fields described here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` directly includes both DPCS 3.1.4 generated headers and initializes DCN 3.1.4 resource tables.
- The same resource file uses `DPCS_DCN31_MASK_SH_LIST(__SHIFT)`, `DPCS_DCN31_MASK_SH_LIST(_MASK)`, and `DCN3_1_RDPCSTX_REG_LIST(...)` around the DPCS include site, so field names in this header are consumed through DCN 3.1-era DPCS table macros.
- Display link encoder, PHY, AUX/link-training, clock-source, and hardware-sequencing code consume those initialized tables indirectly when programming display PHY lanes and shared MPLL/reference-clock state.

Behaviorally, this range sits under display link bring-up and maintenance. It describes the low-level bit layout used when the driver enables or powers down TX/RX lanes, selects MPLLs, configures reference/HDMI clocks, runs receiver calibration/adaptation, handles lane-level interrupts, or reads debug/status counters.

## Risks And Edge Cases

- These constants are untyped preprocessor values. An incorrect shift or mask can compile cleanly while writing the wrong DPCS field, corrupting an adjacent reserved bit, or misreading status.
- The file is generated metadata. Manual edits risk divergence from the authoritative AMD register database, the matching offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are artificial. Line 31718 starts with the two masks for `TX_PWRUP_TIME_0`; the corresponding shifts are just before this range. Line 34157 stops after `MPLLA_SSC_PEAK_2` shifts; its masks are in the next chunk.
- Power and calibration fields are sequencing-sensitive. Bad masks for RX/TX pstate enables, VCO reset/calibration, DPLL bounds, CDR SSC gains, DCC DAC handshakes, or MPLL enable/divider fields can cause link-training failures, blank displays, unstable clocks, high error rates, or resume-only failures.
- ACK, IRQ, and clear fields are side-effect-sensitive. Confusing IRQ status, clear, and mask bits can cause missed lane events, stuck interrupts, repeated IRQs, or failure to observe adaptation/pstate/rate changes.
- The raw PCS/PMA override and ATE fields can bypass normal state-machine control. Incorrect override masks may force loopback, pstate, MPLL, RX-valid, or TX/RX data-enable behavior that is hard to diagnose from higher-level display state.
- Repeated lane-style register groups are copy-sensitive. A generator error can affect one lane path or one sub-block while nearby groups still appear correct.
- Debug/statistic counter fields are not functional programming knobs, but wrong masks can hide useful failure evidence during link bring-up, PHY characterization, or manufacturing diagnostics.
- CR2 supervisor fields affect shared clock resources. Bad reference clock, MPLLA/MPLLB divider, HDMI clock, fractional-N, or SSC masks can break multiple links or modes that share the same common PLL resource.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU display support with DCN 3.1.4 enabled. Missing or renamed macros should fail where `dcn314_resource.c` initializes DPCS register, shift, and mask tables.
- Mechanically verify that each field in this range has the expected `__SHIFT`/`_MASK` pair, while allowing the known chunk-boundary exceptions for `TX_PWRUP_TIME_0` and `MPLLA_SSC_PEAK_2`.
- Cross-check this slice against `dpcs_3_1_4_offset.h` so every complete register group in the chunk has a corresponding `ixDPCSSYS_*` offset.
- Diff against AMD's authoritative DPCS 3.1.4 register database and nearby generated variants such as `dpcs_3_0_3_sh_mask.h`, `dpcs_4_0_0_sh_mask.h`, or `dpcs_4_2_0_sh_mask.h` where register layouts are expected to be compatible.
- Exercise DisplayPort/HDMI link bring-up across all available PHY lanes and rates. Expected signals are stable link training, correct lane power transitions, no false lane IRQs, and no stuck ACK/status bits.
- Exercise hotplug, modeset, stream disable/enable, suspend/resume, and GPU reset paths to catch persistence or reinitialization mistakes in power, pstate, PLL, and calibration fields.
- Validate high-bandwidth and clock-sensitive modes that stress MPLL divider, HDMI clock, fractional-N, and SSC programming. Watch for blank displays, link retraining loops, PHY lock failures, or display corruption.
- Use register dumps or PHY debug traces during failing links to confirm RX adaptation, VCO/CDR status, statistic counters, DCC status, and FSM status fields decode correctly.
- Exercise diagnostic paths where available: LBERT, OCLA, statistic match/count controls, analog test bus/readback fields, loopback controls, and ATE overrides.

## Cross-Chunk Notes

The previous chunk owns most of TX power-state programming and the shifts for `DPCSSYS_CR1_LANEX_DIG_TX_PWRCTL_TX_PWRUP_TIME_0`; this chunk starts with that register's masks. The next chunk should begin with the missing masks for `DPCSSYS_CR2_SUP_DIG_MPLLA_SSC_PEAK_2` and continue MPLLA SSC step-size and later CR2 supervisor/common PLL fields. The final per-file research document should reconcile those boundaries before making whole-file claims about all DPCS 3.1.4 lane and supervisor fields.

### subset-b-002273: lines 34158-36568

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 34158-36568

## Scope

This chunk is a generated AMD DPCS 3.1.4 shift/mask header segment for the `DPCSSYS_CR2` register address block. It covers lines 34158 through 36568 and contains only preprocessor constants: 2,169 `#define` entries, with 1,086 `__SHIFT` definitions and 1,083 `_MASK` definitions across 243 register groups. The mismatch is expected for this chunk boundary: the range starts in the middle of `DPCSSYS_CR2_SUP_DIG_MPLLA_SSC_PEAK_2` after its shift definitions, and ends in the middle of `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0` before its remaining shifts and all masks.

The content is declarative register metadata. It defines no C functions, types, storage, structs, enums, executable statements, or local control flow. Runtime behavior appears only in consumers that include this generated header and use the constants to compose read-modify-write operations against DPCS/RDPCS hardware registers.

## Purpose

The purpose of this chunk is to expose symbolic bitfield locations for the DPCS CR2 supervisor and lane-control hardware. Each macro follows the generated AMD register naming convention:

- `<register>__<field>__SHIFT` gives the bit offset used to place or extract a field.
- `<register>__<field>_MASK` gives the already-shifted bit mask used to preserve, clear, or test the field.

The register areas covered here describe CR2 supervisor PLL programming, spread-spectrum clocking, analog override/status reporting, bandgap/reference-clock/RTUNE timing, lane 0 transmitter and receiver statistic controls, lane 0 analog TX override/status fields, lane 1 transmitter and receiver ASIC override inputs/outputs, lane 1 TX power-state sequencing, lane 1 RX power-state sequencing, and the beginning of lane 1 RX VCO calibration control.

## Exported API Surface

There are no callable APIs. The exported surface is the macro namespace itself, intended for AMDGPU display code that already knows the matching register addresses from companion generated headers.

Important macro families in this chunk include:

- `DPCSSYS_CR2_SUP_DIG_MPLLA_*` and `DPCSSYS_CR2_SUP_DIG_MPLLB_*`: MPLL A/B override, ASIC input, fractional-N divider, spread-spectrum peak/step, charge-pump, power-control, timer, calibration, status, and analog override-out fields.
- `DPCSSYS_CR2_SUP_DIG_SUP_*`, `PRESCALER_*`, `LVL_*`, `BANDGAP_*`, `CLK_RST_*`, and `RTUNE_*`: supervisor-level control, analog calibration, reference-clock selection/detection, bandgap power sequencing, level override, resistor tuning request/status/set-value, and related timing counters.
- `DPCSSYS_CR2_SUP_ANA_*`: narrow analog-supervisor fields for prescaler, RTUNE, bandgap, and switch power-measurement control.
- `DPCSSYS_CR2_LANE0_DIG_ASIC_*`: lane 0 lane/TX/RX override inputs and ASIC input/output mirrors.
- `DPCSSYS_CR2_LANE0_DIG_TX_PWRCTL_*`: lane 0 TX power states, TX power-up timing, DCC CR-bank/DAC selection, TX clock alignment, and LBERT pattern/test controls.
- `DPCSSYS_CR2_LANE0_DIG_RX_STAT_*`: lane 0 RX statistics match/control/counter registers, including masks, sample counters, comparator clocking, and statistic-stop control.
- `DPCSSYS_CR2_LANE0_DIG_ANA_*` and `DPCSSYS_CR2_LANE0_ANA_TX_*`: lane 0 digital-to-analog TX override/status definitions and direct analog TX measurement/power/ATB/DCC/termination/misc fields.
- `DPCSSYS_CR2_LANE1_DIG_ASIC_*`: lane 1 lane/TX/RX override inputs, equalizer override inputs, ASIC input mirrors, output mirrors, CDR/VCO ASIC inputs, and OCLA selection bits.
- `DPCSSYS_CR2_LANE1_DIG_TX_PWRCTL_*`: lane 1 TX power states, TX power-up timing, DCC DAC control, TX clock alignment, and LBERT controls.
- `DPCSSYS_CR2_LANE1_DIG_RX_PWRCTL_*`: lane 1 RX P0/P0S/P1/P2 power-state bitmaps and RX power-up timing.
- `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`: the beginning of lane 1 RX VCO calibration control fields; only the first five shift definitions are inside this chunk.

## Register Areas Covered

The supervisor MPLL sections define field positions for both MPLLA and MPLLB. The fields include enable, div5 clock enable, TX clock divider, override enable, V2I, standby, VCO frequency selection, calibration force, fractional-N enable, clock-sync override, multiplier, SSC enable/up-spread, PMIX enable, word-div2 enable, fractional configuration update, SSC peak, SSC step size, fractional quotient/remainder/denominator, charge-pump proportional/integral settings, and gear-shift charge-pump overrides. The corresponding ASIC input groups mirror many of the same semantic fields without the explicit override-enable pattern.

The supervisor power and analog sections expose state-machine controls and status for MPLL power control. The `MPLL_PWR_CTL_MPLL_OVRD` fields carry request-style controls such as `MPLL_EN`, `MPLL_STANDBY`, `MPLL_DIV5_CLK_EN`, `MPLL_DAC_RANGE`, `MPLL_WAIT_LOCK`, and `MPLL_DONE_ACK`. The `MPLL_PWR_CTL_STAT` fields expose observed state such as lock, calibration done, calibration fail, range, DAC outputs, clock-stable state, FSM state, VCO frequency status, clock-off status, and divider state. Timer/calibration groups define lock timers, generic MPLL timers, PCLK stable timers, DAC max range, calibration control, and analog DAC output fields.

The clock/reset and RTUNE sections provide field locations for bandgap power-up timing, reference-clock power-up timing, VPH/UD reference controls, RTUNE request/continuous/acknowledge behavior, RTUNE FSM status, set values and measured status for RX/TXDN/TXUP legs, RTUNE retry/interval counters, and TX calibration code. These fields are coordination points between digital control logic and analog calibration hardware.

The supervisor analog override-output sections define fields that report or drive analog-facing outputs for MPLLA/MPLLB, RTUNE, bandgap, PMIX, and analog status. They include fields for analog enable/standby/divider states, SSC/fractional settings, VCO/CP settings, RTUNE acknowledge, PLL state, bandgap lane/supervisor state, reference-clock acknowledgement, PMIX enables, and analog status bits such as PLL lock and calibration completion.

Lane 0 coverage is primarily TX and RX-stat oriented. Its ASIC override and ASIC input/output groups define TX driver controls, common-mode controls, FIR/equalization controls, main/pre/post cursor settings, termination, polarity, scrambling-related controls, RTUNE code fields, pattern data, and TX request/ack state. The lane 0 TX power-control groups define P0/P0S/P1/P2 state bitmaps and power-up/down delay fields for serial AFE, predrivers, data path, boost, DCC, and rate changes. The DCC groups expose a small indirect DAC/CR-bank command surface with address/data, range/control, select/request/update, and acknowledge fields.

Lane 0 RX-stat groups define programmable match and sampling machinery rather than RX bring-up. They include data-mask/load values, data-rate and clear controls, load/lock gating, pattern selection, counter increment policy, error/running/done/fail/valid state bits, state counters 0 through 6, comparator clock control, auxiliary match-control registers, and statistic stop control.

Lane 0 analog TX groups define the digital override-out fields for analog TX, including power state, AFE enable, predriver enable, driver enable, impedance enable, termination, DCC, boost, rate, inversion, common-mode controls, feed-forward equalization controls, DCC DAC overrides, and analog status. The direct `LANE0_ANA_TX_*` groups are narrow analog register bitfields for override measurement, power override, alternate bus, ATB selection, DCC DAC/control, termination code/control, override clock, miscellaneous analog fields, and reserved analog fields.

Lane 1 coverage repeats most lane 0 TX concepts and adds more RX bring-up material. Its ASIC override input groups include lane and TX controls plus RX analog controls: AFE/VREG/clock/deserializer/CDR enables, VCO reset/calibration/continuous calibration, channel rate/width, DETRX controls, adaptation mode, DFE enable, squelch detect, VCO mux, load/update fields, VGA and peaking controls, VCO buffer settings, CDR reference/VCO controls, EQ pre/post/current settings, and additional RX override register groups. Lane 1 ASIC input mirrors expose the same classes of fields as direct hardware inputs rather than override inputs.

Lane 1 TX power-control groups mirror lane 0 TX P-state and timing fields. Lane 1 RX power-control groups define RX P0/P0S/P1/P2 bitmaps for AFE, clock VREG, analog clock, deserializer, CDR, VCO frequency reset, VCO calibration reset, continuous calibration, and digital clock enable. RX timing groups define AFE/VREG/clock enable timing, fast enable bits, fast-start time, rate-change time, CDR enable time, deserializer enable time, and deserializer disable time. The final in-range register starts RX VCO calibration control by defining shift positions for fixed-count calibration, fixed-count enable, calibration-count shift, bounce count, and disabling bin hold.

## Control Flow And State Behavior

This header has no branches or local execution. It is a register-field map for hardware state machines. The field names nevertheless reveal the control surfaces that consumers must sequence carefully:

- MPLL programming is staged through override/ASIC input fields, fractional-N quotient/remainder/denominator fields, SSC peak/step fields, charge-pump fields, PMIX controls, timer fields, and power-control status fields.
- Supervisor bring-up coordinates bandgap, reference clock, prescaler, level, RTUNE, and PLL status. Request/acknowledge pairs such as `RTUNE_REQ`/`RTUNE_ACK`, state fields such as `MPLLA_STATE`, and lock/calibration status fields are intended for ordered writes followed by polling or readback.
- Lane TX bring-up is represented by P-state bitmaps and power-up timers. Consumers are expected to program timing/control values before requesting link/lane state changes.
- DCC DAC and CR-bank controls expose request/update/ack bits and address/data fields, implying an indirect register transaction protocol.
- RX-stat registers implement a small hardware measurement pipeline: program mask/match/control fields, clear or start the statistic engine, poll running/done/fail/valid bits, and read count registers.
- RX power-control and VCO calibration fields gate analog AFE/CDR/deserializer/VCO blocks and calibration behavior. Incorrect sequencing can produce link-training failures or unstable CDR lock.

No software persistence exists here. Register values persist only according to the GPU hardware power and reset domains. Some fields named `SPARE`, `RESERVED`, or full-width data/address fields may hold hardware- or firmware-defined values, but this chunk does not document a software storage contract.

## Dependencies And Integration Points

This header depends only on the C preprocessor and the include guard defined at the top of `dpcs_3_1_4_sh_mask.h`. It is normally consumed together with generated register-address headers for the same ASIC generation, plus AMD display helper macros that combine a register address, field mask, and shift.

Likely integration points are:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS/PHY code that programs DisplayPort and HDMI transmitter PLLs and lanes.
- Generated DPCS 3.1.4 address headers that define the actual CR2 register offsets corresponding to the field masks here.
- Link training and display clock programming paths that configure MPLLA/MPLLB, SSC, fractional-N dividers, PMIX, P-states, and TX/RX lane rate/width fields.
- Power-management and suspend/resume flows that toggle bandgap/reference-clock/MPLL/lane power states and then poll lock, stable, calibration, request/ack, or done fields.
- Diagnostics and validation paths that use lane RX-stat counters, LBERT controls, DCC DAC controls, analog status bits, and OCLA selection.
- Firmware or hardware ownership boundaries for analog/ASIC input and override-output surfaces. The `OVRD`, `ASIC_IN`, `ASIC_OUT`, and `ANA_*` names indicate that some fields are direct hardware inputs/outputs while others are software override controls.

## Risks

- Generated mask drift is the primary risk. A single incorrect shift or mask can silently write an adjacent analog/PLL/lane bit during read-modify-write operations.
- This chunk has partial boundary registers. Automated per-chunk analysis must not treat the missing `MPLLA_SSC_PEAK_2` shifts or the missing `RX_VCO_CAL_CTRL_0` masks as file-level defects; they are outside the requested line range.
- Many registers pair command and status semantics in nearby bits. Examples include request/ack, enable/state, calibration force/done/fail, timer programming/status, statistic clear/running/done/fail, and DCC request/ack. Consumer code must know which bits are writable, read-only, write-one-to-clear, or latched by hardware.
- PLL and analog override fields are high-impact. Bad values in fractional-N, SSC, charge-pump, VCO, PMIX, DCC, termination, common-mode, or EQ fields can break display link training or cause marginal signal integrity.
- Repeated lane and PLL macro families are vulnerable to copy-generation errors. MPLLA/MPLLB, lane 0/lane 1, override/ASIC input, and status/output groups use similar field names with different prefixes; consumers should avoid mixing prefixes when composing register writes.
- Reserved fields are explicitly named and masked in many registers. Using broad writes instead of mask-scoped writes risks modifying reserved bits with undocumented hardware behavior.
- Full-width or nearly full-width address/data fields, such as DCC CR-bank address/data and SSC/fractional payload fields, require caller-side range validation because the header only supplies bit placement.

## Test Signals

Useful validation for this chunk is mostly build-time, generated-header consistency, and hardware integration testing:

- C preprocessing and compilation of AMDGPU display code that includes `dpcs_3_1_4_sh_mask.h`.
- Generated-register validation against the authoritative DPCS 3.1.4 register database, including checks that matching `__SHIFT` and `_MASK` pairs exist across whole-register boundaries outside this chunk.
- Static checks that consumer code uses the CR2 lane and supervisor prefixes consistently, especially for MPLLA versus MPLLB and lane 0 versus lane 1 register families.
- Hardware smoke tests for DisplayPort and HDMI modes on ASICs using DPCS 3.1.4: hotplug, link training at multiple rates, spread-spectrum enable/disable, display mode changes, suspend/resume, and multi-lane configurations.
- Register readback tests around MPLL lock/calibration, RTUNE acknowledge/status, bandgap/reference-clock power-up, lane TX/RX P-state transitions, DCC request/ack, RX-stat done/fail/valid status, and RX VCO calibration behavior.
- Signal-integrity or compliance tests when changing any consumer of TX analog, EQ, DCC, termination, SSC, charge-pump, PMIX, or fractional-N fields.

## Chunk Notes For Merge

The merged per-file report should describe this file as a generated DPCS 3.1.4 bitfield map, not handwritten driver logic. This chunk is centered on CR2 supervisor and lane-control masks. It starts after the `MPLLA_SSC_PEAK_2` shift definitions and ends before the complete `LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0` register definition, so adjacent chunks are needed to reconstruct complete field-pair accounting for those two boundary registers.

### subset-b-002274: lines 36569-38994

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 36569-38994

## Purpose

This chunk is generated AMD DPCS 3.1.4 register-field metadata. It contains no executable C logic; it publishes preprocessor constants that encode bit positions and masks for fields in DPCS/DisplayPort PHY control and status registers. Driver code pairs these `__SHIFT` and `_MASK` constants with register offsets from `dpcs_3_1_4_offset.h` so AMDGPU DCN 3.1.4 link-encoder and HPO DP link code can update or read individual MMIO fields through the display register helpers.

The requested range covers 2,426 lines in the middle of a 55,194-line generated header. It starts inside `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`, covers the remainder of the lane 1 RX VCO/CDR/adaptation/statistics/analog-control block, then covers lane 2 ASIC override, TX power, RX power, RX VCO/CDR/adaptation/statistics, MPHY RX, and the beginning of lane 2 analog TX override/equalization fields. The chunk ends at the first shift for `DPCSSYS_CR2_LANE2_DIG_ANA_TX_EQ_OVRD_OUT_1`; its companion mask entries are in the next chunk.

Although the repository path is under `sources/distributed-fs/ceph-client`, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, includes, or locks in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position used to pack or unpack a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to preserve, isolate, or modify the field in a register read-modify-write operation.

The main field families in this chunk are:

- Lane 1 RX VCO calibration: `RX_VCO_CAL_CTRL_[0-2]`, `RX_VCO_CAL_TIME_[0-1]`, and `RX_VCO_STAT_[0-2]` expose gain-calibration counters, fixed-count enables, hold/skip controls, VCO reset and continuous-calibration enables, frequency tuning start/step values, wait timers, FSM state, calibration-done status, final counter values, and too-fast/correct/up indicators.
- Lane 1 RX CDR and DPLL: `RX_CDR_CDR_CTL_[0-4]`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and `RX_DPLL_FREQ_BOUND_[0-1]` describe phase-detector enable/edge/polarity, SSC on/off counters, phase/frequency update gains, override gain values, DPLL frequency readback, and upper/lower frequency bounds.
- Lane 1 adaptation control and readback: `RX_ADPTCTL_ADPT_CFG_[0-9]`, `RST_ADPT_CFG`, `ATT_STATUS`, `VGA_STATUS`, `CTLE_STATUS`, `DFE_TAP[1-2]_STATUS`, DFE/slicer VDAC offset registers, slicer controls, error slicer levels, reset, DAC selector registers, and CR bank address/data.
- Lane 1 RX statistics and pattern matching: `RX_STAT_LD_VAL_1`, `DATA_MSK`, `MATCH_CTL[0-5]`, `STAT_CTL[0-2]`, `SMPL_CNT1`, `STAT_CNT_[0-6]`, `CAL_COMP_CLK_CTL`, and `STAT_STOP` define match patterns/masks, statistic source selection, scope controls, counter enables, done bits, sample/counter readback, comparator clock timing, and stop control.
- Lane 1 analog and MPHY override/status: MPHY PWM/termination/stable-count controls; TX override, TX termination/equalization, RX control/power/VCO/calibration/DAC/AFE/CTLE/scope/slicer/IQ controls; analog status; RX termination; MPHY; signal detect; TX DCC DAC; and low-level `LANE1_ANA_*` TX/RX analog register bitfields.
- Lane 2 digital ASIC boundary: `DIG_ASIC_*_OVRD_IN`, `*_OVRD_OUT`, `*_ASIC_IN`, and `*_ASIC_OUT` fields model lane-level, TX, RX, RX EQ, and RX CDR/VCO override paths between digital logic and PHY analog interfaces.
- Lane 2 power and training setup: TX P-state registers, TX power-up timing, DCC DAC CR bank and acknowledgement fields, TX clock alignment, TX LBERT controls, RX P-state registers, and RX power-up timing.
- Lane 2 RX calibration/statistics: lane 2 repeats the VCO calibration, CDR/DPLL, adaptation, and statistics families seen for lane 1, with the same field purposes but lane-specific register names.
- Lane 2 MPHY and TX analog override start: MPHY RX PWM/termination/stable-count fields and the start of TX analog override, termination-code override, termination-clock override, and TX equalization override fields.

Most fields in this chunk are 16-bit register fields, with masks such as `0xFFFFL`, `0x8000L`, or lower-width subfields. Some ASIC override and power-control registers are wider, especially lane 2 `DIG_ASIC_*` fields and power-state macros using 32-bit masks.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. `dcn314_resource.c` includes `dpcs_3_1_4_offset.h` and this `dpcs_3_1_4_sh_mask.h`.
2. DCN 3.1/3.1.4 link-encoder macro lists, including `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`, collect selected field shifts and masks into `dcn10_link_enc_shift` and `dcn10_link_enc_mask` tables.
3. HPO DP link encoder register construction in the same resource file pulls DPCS/RDPCSTX register lists into per-link register tables.
4. Later display link code uses AMD register helper macros such as `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`, and poll/wait wrappers with those offsets, shifts, and masks to sequence link PHY reset, power, calibration, training, and status handling.

The macros themselves do not encode ordering. Safe sequencing still belongs to the consumers: clocks and power rails must be enabled before calibration; reset, P-state, DPLL/CDR, adaptation, and analog override writes must be ordered around hardware handshakes; and status fields must be polled or cleared according to the register specification.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU PHY state.

The represented hardware state includes:

- RX VCO and DPLL calibration state: reset bits, continuous calibration, skip controls, timers, FSM state, calibration done, frequency tune values, and counter readbacks.
- Clock/data recovery and adaptation state: phase-detector controls, SSC gain timing, phase/frequency update gains, adaptation machine configuration, attenuator/VGA/CTLE/DFE status, slicer offsets, and DAC selections.
- Statistics and diagnostics state: pattern match values/masks, statistic counter enables, sample counters, statistic counters, done bits, LBERT error count/overflow, and OCLA-related capture fields.
- Power and P-state state: lane 2 TX/RX P0/P0S/P1/P2 controls, power-up timers, analog enable/disable fields, DCC controls, and stable/acknowledge fields.
- Analog override state: TX and RX analog enables, rates, resets, serializer/deserializer controls, equalization pre/post/leg-pull settings, term-code overrides, signal-detect overrides, DCC DAC controls, calibration codes, and measurement/status fields.

Persistence is hardware-defined. Some configuration fields retain values until modeset, link retraining, power gating, suspend/resume, or ASIC reset. Status and counter fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while a lane is powered. This generated header does not express access type or side effects; the register spec and consumer code must supply that knowledge.

## Dependencies And Integration Points

This chunk depends on the matching DPCS 3.1.4 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`

The offset header maps the same symbolic registers to indirect DPCS addresses. For example, generic lane-X offsets identify the same register families represented here, including `ixDPCSSYS_CR2_LANEX_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`, `ixDPCSSYS_CR2_LANEX_DIG_RX_CDR_CDR_CTL_0`, `ixDPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_ADPT_CFG_0`, `ixDPCSSYS_CR2_LANEX_DIG_RX_STAT_STAT_CTL0`, and `ixDPCSSYS_CR2_LANEX_DIG_ANA_TX_OVRD_OUT`.

The direct include site found in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`

At that integration point, this header feeds:

- link encoder shift/mask tables through `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`;
- HPO DP link encoder register tables through `DCN3_1_RDPCSTX_REG_LIST(...)` and related DPCS register-list macros;
- the common AMD display register helper pattern that expects each register field to have a matching shift and mask macro.

The chunk also aligns with generated DPCS headers for nearby ASIC versions. Similar register names appear in later `dpcs_4_2_0_*` and `dcn_4_1_0_sh_mask.h` metadata, which is useful for consistency checks but is not a substitute for the 3.1.4 register database.

## Risks And Edge Cases

- Generated metadata can fail silently. A wrong shift or mask usually compiles, but it can program the wrong bits in a PHY register and produce link failures, unstable training, intermittent blank displays, or analog-margin problems.
- This chunk has artificial boundaries. It begins after the first fields of lane 1 `RX_VCO_CAL_CTRL_0` and ends before the masks for lane 2 `ANA_TX_EQ_OVRD_OUT_1`; adjacent chunks are required before making complete per-register claims.
- Lane repetition is copy-sensitive. Lane 1 and lane 2 fields are structurally similar, but a lane-specific typo can affect only one physical lane, making failures depend on lane count, connector routing, link rate, or whether the failing lane is active.
- PHY calibration fields are timing- and power-state-sensitive. Misusing VCO calibration, DPLL frequency, CDR gains, or adaptation controls can cause lock failures, high bit error rates, or training instability that may only appear at high bandwidth or after resume.
- Override fields are high risk. `*_OVRD_EN` bits bypass normal hardware sequencing. Leaving an override asserted across modeset, hotplug, retraining, or suspend/resume can pin analog enables, data rates, resets, termination, or equalization values unexpectedly.
- Status and counter fields may have side effects or validity windows. LBERT errors, statistic counters, calibration done bits, ACK fields, and analog status bits may require specific read/clear/poll ordering not represented in this header.
- Reserved masks are present throughout the chunk. Consumers must preserve reserved bits during read-modify-write operations; writing raw constants instead of using field helpers risks changing undocumented hardware behavior.
- Some fields are wider 32-bit lane-interface controls while many PHY fields are 16-bit. Mixing register width assumptions can corrupt neighboring fields or drop high-order control bits.

## Test Signals

Useful validation combines generated-header consistency with hardware-facing display tests:

- Build AMDGPU/DC with DCN 3.1.4 support enabled. Missing or renamed DPCS shift/mask macros should fail at resource and link-encoder table construction.
- Mechanically verify that every complete field in this range has the expected `__SHIFT`/`_MASK` pair, while accounting for the chunk-edge exceptions at line 36569 and line 38994.
- Compare this range against AMD's authoritative DPCS 3.1.4 register database and against neighboring generated headers where register layout is expected to match.
- Exercise DP and HDMI link bring-up on DCN 3.1.4 hardware across lane counts and link rates, especially cases using physical lanes 1 and 2.
- Run modeset, hotplug, link retraining, MST if supported by the platform, high-bandwidth modes, suspend/resume, runtime power management, and repeated connector unplug/replug cycles.
- Watch kernel logs and display diagnostics for AUX/link-training failures, CDR/VCO calibration timeouts, stuck ACK/done bits, blank screens, intermittent flicker, CRC mismatches, audio/video instability, and resume regressions.
- If debug tooling is available, sample DPLL/CDR/VCO status, adaptation status, statistic counters, LBERT counters, and analog status before and after training to confirm fields decode plausibly.

## Cross-Chunk Notes

Previous chunks own the beginning of lane 1 RX power and `DPCSSYS_CR2_LANE1_DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0`. Later chunks continue lane 2 TX equalization override, lane 2 RX analog controls/status, and the rest of the DPCS 3.1.4 shift/mask namespace. The final per-file research document should merge those chunks before making whole-file claims about all lanes, all DPCS CR blocks, or complete DPCS PHY programming coverage.

### subset-b-002275: lines 38995-41436

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 38995-41436

## Scope

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice. It contains preprocessor constants only: no callable functions, structs, enums, storage objects, allocation, or executable control flow. Its exported contract is the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` namespace, where each macro describes one 16-bit DPCS/PHY register field position or already-shifted mask.

The range starts in the middle of the `DPCSSYS_CR2_LANE2` analog TX equalization override block, covers the rest of lane 2 RX/TX analog override and status fields, then covers most of `DPCSSYS_CR2_LANE3` digital ASIC, TX power-control, RX statistics, and TX analog fields. It then moves to `DPCSSYS_CR2_RAWCMN` common PHY registers, `RAWLANE0` PCS/FSM/IRQ fields, and the start of `RAWLANE0` PMA transfer/override fields. The chunk ends inside `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT`; adjacent chunks own the beginning of the lane 2 TX-EQ context and the remainder of raw-lane0 PMA/TX control metadata.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMD display/link PHY register metadata. It has no Ceph, filesystem, distributed-storage, network protocol, or persistent-disk behavior.

## Purpose

The purpose of this header range is to provide ASIC-specific bit geometry for DCN 3.1.4 DPCS CR2 lane, common, PCS, FSM, IRQ, and PMA registers. Runtime display code includes this header with the matching `dpcs_3_1_4_offset.h` file so register tables can map logical link-encoder fields onto the exact CR-indirect DPCS hardware layout.

The covered hardware areas are:

- Lane 2 analog TX/RX controls: TX equalization leg-pull enable/direction, pre/post controls, RX control and power overrides, RX CDR/VCO overrides, RX calibration DAC and slicer controls, AFE attenuation/gain/CTLE, scope/IQ phase controls, RX term-code controls, MPHY and signal-detect overrides, TX DCC DAC overrides, and analog TX readback/test registers.
- Lane 3 digital ASIC boundary controls: per-lane override inputs/outputs for TX rate/width/power state, MPLL selection, TX data/reset/async/ack signaling, RX request/rate/power/adaptation/loopback signaling, and ASIC input/output mirror registers.
- Lane 3 TX power and diagnostics: P-state tables for `P0`, `P0S`, `P1`, and `P2`; TX power-up timing registers; DCC CR bank address/data and DCC DAC programming; TX clock alignment and LBERT control; RX stat pattern/match/count controls; calibration comparator clocking; and statistic stop controls.
- Lane 3 analog TX controls: TX term-code, TX-EQ, TX DCC DAC, TX override/status, and analog TX miscellaneous/reserved registers.
- CR2 raw-common PHY controls: common functional reset, `MPLLA`/`MPLLB` word-divider, TX clock divider, bandwidth and spread-spectrum overrides, lane FSM extension, MPLL state control, TX calibration code, SRAM init done, OCLA/debug, supervisor analog overrides, PCS/FW ID codes, AON retune values for RX/TXDN/TXUP across entries 0-7, AON SRAM block config, power-gate/supervisor/resistance/reference range overrides, VREF stats, and miscellaneous common configuration.
- CR2 raw-lane0 PCS/FSM/IRQ/PMA metadata: PCS TX/RX override and PCS mirror registers, RX adaptation ACK/FOM and TX EQ direction hints, lane number and ATE overrides, RX EQ/phase/term controls, FSM override/status/fast-path timing controls, continuous calibration/adaptation flags, CR lock and DCC status, IRQ status/clear/mask registers, PMA lane/supervisor/TX/RX handshakes, rtune request/ack, and the start of MPHY PMA override input/output controls.

## Important APIs, Types, And Macros

There are no C APIs or concrete types in this chunk. The important interface is the generated macro pattern:

- `*_SHIFT` gives a field's least-significant bit position.
- `*_MASK` gives the field mask in its final register position.
- Register names encode the DPCS CR instance and block, such as `DPCSSYS_CR2_LANE3_DIG_ASIC_TX_OVRD_IN_0`, `DPCSSYS_CR2_RAWCMN_DIG_MPLLA_OVRD_IN`, `DPCSSYS_CR2_RAWLANE0_DIG_PCS_XF_RX_OVRD_IN`, and `DPCSSYS_CR2_RAWLANE0_DIG_IRQ_CTL_IRQ_MASK`.

The lane analog fields are dominated by override-enable/value pairs. Examples include `TX_EQ_OVRD_EN`, `TX_ANA_LOAD_CLK`, `TX_ANA_CTRL_PRE`, `TX_ANA_CTRL_POST`, `RX_CTL_OVRD_EN`, `RX_PWR_OVRD_EN`, `RX_VCO_CDR_OVRD_EN`, `RX_CDR_FREQ_TUNE_OVRD_EN`, `RX_CAL_DAC_CTRL_OVRD`, `RX_AFE_OVRD_EN`, `RX_ANA_SLICER_CTRL_OVRD_EN`, signal-detect override enables, and DCC DAC override enables. These fields let low-level driver or firmware code force link PHY state for calibration, bring-up, debug, or controlled mode transitions.

The lane 3 ASIC-facing fields describe handshakes between digital link logic and the physical lane. TX-side fields include `TX_WIDTH`, `TX_RATE`, `TX_PSTATE`, `TX_REQ`, `TX_RESET`, `TX_ACK`, `TX_BEACON_EN`, `TX_FIFO_CLK_EN`, `TX_DATA_EN`, `TX_DCC_CALDONE`, MPLL enable/select state, async data controls, polarity/inversion, and serial loopback. RX-side fields include `RX_RATE`, `RX_PSTATE`, `RX_REQ`, `RX_RESET`, `RX_ACK`, `RX_VALID`, `RX_ADAPT_REQ`, `RX_ADAPT_ACK`, adaptation disable/continuous control, rate-change ACK, power-up/down controls, parallel/serial loopback, and RX data-enable state.

The TX power-control fields are packed state descriptors. `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` carry per-state TX power-up/down, VBOOST, iboost, rate, main/pre/post equalization, term control, and state-selection information. `TX_PWRCTL_TX_PWRUP_TIME_*` splits timing and enable bits across several registers. `DCC_CR_BANK_ADDR`, `DCC_CR_BANK_DATA`, `DCC_DAC_CTRL`, `DCC_DAC_RANGE`, `DCC_DAC_SEL`, `DCC_DAC_ACK`, and `DCC_DAC_ADDR` define an indexed DCC programming path.

The raw-common `MPLLA`/`MPLLB` fields expose parallel A/B PLL controls. Each PLL has word-divide, TX clock divisor, div8/div10 enable, bandwidth override, and spread-spectrum override fields. Common support fields include `PHY_FUNC_RST`, lane FSM extension operation, MPLL state wait/min/max counters, TX calibration code, SRAM init done, OCLA/debug bits, supervisor analog override, ID-code readbacks, AON retune values, SRAM block configuration, power-gate controls, VREF stats, resistance override/input-output values, and reference-range override.

The raw-lane0 PCS transfer fields define override paths between PCS, ASIC, and PMA. `PCS_XF_TX_*` and `PCS_XF_RX_*` groups contain override values/enables and PCS mirror values for TX request/reset/async/data/loopback, RX request/reset/rate/pstate/adaptation/term/valid/data/PWM controls, and link-training support values such as `RX_ADAPT_FOM`, `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, and `RX_TXPOST_DIR`. ATE-specific fields expose testing overrides for VBOOST, IBOOST, beacon, loopback, TX async data, and loss/adaptation controls.

The raw-lane0 FSM and IRQ groups define status and event plumbing. FSM registers expose override control, memory/status monitors, fast-path cycle counters for RX startup/adaptation/calibration/power/VCO/SUP/TX paths, continuous calibration and adaptation counters, fast flags, CR lock, TX DCC flags/status, OCLA, TX EQ update flag, RCAL status, and RX IQ phase offset. IRQ registers expose individual status and clear bits for reset/request/rate/pstate/adaptation, PH2 calibration, serial loopback, DCC on-demand, TX reset/request, plus two mask registers.

The PMA transfer fields at the end define lane/supervisor/TX/RX handshake overrides and readbacks. They include `LANE_MPLLA_EN`, `LANE_MPLLB_EN`, `SUP_STATE_OVRD_EN`, TX/RX request and reset override value/enable bits, PMA data-enable overrides, loopback controls, TX/RX `ACK` readbacks, lane rtune request/ack, and MPHY/PMA PWM, term, async, and clock-selection controls.

## Control Flow

This header range has no local control flow. Runtime behavior is created by consumers that include `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`, construct register/field tables, and then use AMD display register helpers to perform MMIO or CR-indirect reads and writes.

A typical DCN 3.1.4 path is:

1. `display/dc/resource/dcn314/dcn314_resource.c` includes the DCN and DPCS 3.1.4 offset/shift-mask headers.
2. Resource construction macros build link-encoder register tables with generated register offsets and matching field masks/shifts. In this file, `le_shift` and `le_mask` expand `DPCS_DCN31_MASK_SH_LIST(__SHIFT)` and `DPCS_DCN31_MASK_SH_LIST(_MASK)`.
3. Link-encoder, HPO DP, GPIO, IRQ, and clock/resource code access those table entries through helper macros such as `REG_GET`, `REG_UPDATE`, `REG_UPDATE_2`, and related `reg_helper.h` operations.
4. Higher-level display/link code sequences PHY reset, PLL setup, TX/RX lane enable, DisplayPort alternate-mode handshakes, power-state changes, training/equalization, calibration, and debug/status polling.

The header itself does not encode ordering, delays, polling loops, lane ownership, or policy. Those rules live in the display link encoder, HPO DP link encoder, clock manager, GPIO, IRQ, hardware-sequencer, and firmware-facing code that consumes the generated register tables.

## State And Persistence Behavior

The file itself stores no runtime state and persists nothing. It describes hardware register state whose lifetime is controlled by DPCS/PHY programming, link training, modesets, hotplug, DP alt-mode transitions, suspend/resume, runtime power management, and GPU reset.

State represented by this chunk includes:

- Lane analog state for TX equalization, termination, DCC DACs, signal-detect behavior, RX AFE/CTLE/slicer/calibration, CDR/VCO controls, and IQ phase controls.
- Lane 3 digital state for TX/RX width, rate, power state, reset/request/ack handshakes, data enable, loopback, async signaling, adaptation request/ack, and ASIC mirror values.
- TX power-control state for each P-state and associated timing, DCC bank/DAC programming, clock alignment, LBERT controls, and RX-stat capture counters.
- Common PHY state for resets, PLL dividers, spread-spectrum controls, MPLL state waits, calibration codes, SRAM init status, retune values, power-gate/supervisor/resistance/reference overrides, and ID/readback registers.
- Raw-lane0 PCS/FSM/IRQ/PMA state for TX/RX PCS overrides, adaptation FOM and equalization directions, ATE overrides, RX phase/term calibration, FSM fast counters and flags, IRQ status/masks/clears, PMA supervisor/TX/RX handshakes, rtune, and MPHY PWM/term/async controls.

Many fields are status-like readbacks, including ACK bits, calibration done/status bits, FOM values, statistics counters, IRQ status bits, FSM status monitors, CR lock, SRAM init done, ID codes, retune values, VREF stats, power/status mirrors, and PMA input mirrors. Other fields are writable controls that can immediately change live PHY behavior or arm self-clearing pulses. Fields named `*_SELF_CLEAR_DISABLE`, `*_CLK`, `*_REQ`, `*_CLR`, or `*_UPDATE_FLAG` are especially sequencing-sensitive because they often represent pulses, clear-on-write paths, or control strobes rather than passive configuration.

Bad values can persist until the lane, common PHY, DPCS block, display link, or whole GPU is reset or reprogrammed. Some link state is reconstructed during modeset, hotplug handling, link training, and suspend/resume, but this generated header has no restore logic; it only defines the bit layout that those paths rely on.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which provides the matching generated offsets. These masks are only correct when paired with the DPCS 3.1.4 offset header and the DCN314 resource layout.

Visible integration points include:

- `display/dc/resource/dcn314/dcn314_resource.c`, the only direct include of `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h` in this tree. It builds DCN314 link encoder shift/mask tables using `DPCS_DCN31_MASK_SH_LIST`.
- `display/dc/dio/dcn10/dcn10_link_encoder.h` and generation-specific link encoder headers, which define the logical DPCS field lists used by resource files. These lists include DPCS PHY TX data/pstate/MPLL, SRAM, FIFO, reset/request/ack, reference clock, PLL, TX-EQ, DP alt-mode, and debug fields.
- `display/dc/dio/dcn21/dcn21_link_encoder.*` and related DIO link encoder code, which show how DPCS field tables are consumed by `REG_GET`/`REG_UPDATE` calls for DP alt-mode, reference-clock, TX lane, and PHY control behavior.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.*`, which uses RDPCSTX/DPCS metadata for high-performance DisplayPort link encoder paths, including `RDPCS_PHY_DPALT_DISABLE`.
- GPIO, IRQ, clock-manager, and resource files for nearby generations, which include DPCS generated headers and use the same register-table expansion pattern.

The generated namespace is cross-generation but not interchangeable. Nearby headers such as `dpcs_3_0_0_sh_mask.h`, `dpcs_4_0_0_sh_mask.h`, `dpcs_4_2_2_sh_mask.h`, and `dpcs_4_2_3_sh_mask.h` contain similar register names, but field availability, offsets, and exact masks may differ. Consumers must bind the correct offset and mask pair for the target ASIC.

## Risks And Edge Cases

The main risk is silent PHY misprogramming. Shift and mask constants compile cleanly even when wrong, but a bad constant can update a neighboring field, truncate a multi-bit value, miss a control pulse, decode a status bit incorrectly, or force the wrong lane/PLL state.

Chunk-boundary risk is present. The first lines are already inside the lane 2 TX-EQ override group, and the final lines stop before the remainder of `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT` and later PMA/TX controls. The final per-file report should merge adjacent chunks before making whole-block claims about lane 2 TX-EQ or raw-lane0 PMA coverage.

Lane and instance pairing are critical. This chunk mixes CR2 lane 2, CR2 lane 3, CR2 raw-common, and CR2 raw-lane0 names. A field copied into the wrong lane instance or paired with a mismatched offset can create failures that look like timing or link-training bugs.

PLL and clock fields are high risk. `MPLLA`/`MPLLB` dividers, bandwidth overrides, spread-spectrum controls, word-divide bits, TX clock dividers, and MPLL state timing affect symbol clocks and link stability. Wrong masks can cause no-link, intermittent training failure, jitter, or mode-specific display loss.

Analog override fields are calibration-sensitive. TX equalization, termination, VBOOST/IBOOST, DCC DAC, RX AFE/CTLE/slicer, CDR/VCO, signal detect, and IQ phase controls can produce subtle signal-integrity problems, particularly at higher DP rates, with certain cables, docks, alt-mode paths, or board designs.

Power-state and handshake fields are sequencing-sensitive. TX/RX request/reset/ack, data-enable, pstate, rate, loopback, adaptation, PMA ACK, rtune, and PMA/PWM controls must be changed in hardware-defined order. The masks do not express waits, dependencies, or whether a field is read-only, write-one-to-clear, pulse, or latched.

IRQ and status fields can mislead diagnostics. Incorrect IRQ mask, status, or clear constants may hide lane events, leave interrupts stuck, or clear the wrong event. RX statistic and LBERT fields can return plausible but wrong debug data if match controls or counter masks are wrong.

Reserved fields appear frequently. Generic register updates must preserve reserved bits unless the hardware database explicitly allows otherwise. Full-register writes using these masks can unintentionally disturb reserved or test-only state.

## Test Signals

Useful validation is mostly generated-header, build, and hardware-behavior oriented:

- Compile coverage for DCN314 resource construction, link encoder, HPO DP link encoder, GPIO, IRQ, and clock/resource users that include generated DPCS headers.
- Generated-register consistency checks that every field has a matching offset/header pair, each `*_MASK` matches its `*_SHIFT` width, and no logical field list references a missing generated macro.
- Cross-generation diffs against AMD's authoritative DPCS 3.1.4 register database and nearby DPCS 3.0.x/4.x headers, with expected differences explicitly reviewed.
- Link bring-up tests across DP rates, lane counts, MST/HPO paths, USB-C/DP alt-mode, dock paths, hotplug/unplug, suspend/resume, runtime PM, and GPU reset.
- PLL and clock tests that exercise MPLLA/MPLLB selection, dividers, spread-spectrum, reference clock enable/range, symbol clock gating, and clock-ready/status readbacks.
- TX/RX lane tests for request/reset/ack handshakes, pstate/rate transitions, data-enable, polarity/inversion, loopback, adaptation request/ack, RX valid, and PMA ACK/rtune behavior.
- Signal-integrity tests for TX EQ pre/main/post, term codes, VBOOST/IBOOST, DCC DAC programming, RX AFE/CTLE/slicer, CDR/VCO controls, signal detect, and IQ phase calibration at high link rates.
- IRQ/debug tests that trigger reset/request/rate/pstate/adaptation/PH2 calibration/TX events, verify mask behavior, confirm clear bits, and read RX-stat/LBERT/FSM counters.
- Recovery tests that verify bad or interrupted link-training sequences are cleaned up by modeset, hotplug recovery, suspend/resume, or GPU reset.

Regression symptoms from bad constants include blank display output, intermittent DP link training failures, reduced maximum link rate, hotplug or alt-mode failures, unstable docks, flicker at high rates, stuck reset/request/ack bits, failed suspend/resume recovery, misleading PHY debug counters, missing or storming interrupts, and failures isolated to DCN 3.1.4 ASICs.

## Cross-Chunk Notes

This is not a standalone source module. It is a generated register-layout slice inside `dpcs_3_1_4_sh_mask.h`. The preceding chunk owns the beginning of the lane 2 analog TX-EQ override context before line 38995. The following chunk owns the remainder of the raw-lane0 PMA MPHY override output register and subsequent DPCS register blocks after line 41436. The merge/reconciliation lane should treat this document as the CR2 lane 2 tail, lane 3, raw-common, and raw-lane0 PCS/FSM/IRQ/PMA opening portion of the full DPCS 3.1.4 shift/mask contract.

### subset-b-002276: lines 41437-43854

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 41437-43854

## Scope

This chunk is a middle slice of the generated AMD DPCS 3.1.4 register shift/mask header. It covers lines 41437 through 43854 inside the `dpcssys_cr2_rdpcstxcrind` address block. The range contains 2,145 `#define` constants across 273 register comment blocks: 1,070 `__SHIFT` definitions and 1,075 `_MASK` definitions. The five extra masks are the tail of `DPCSSYS_CR2_RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT`, whose matching shifts and first masks are immediately before the chunk. The final line is the comment for `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_1`; that register's fields begin after the chunk.

The content is declarative only. It has no functions, structs, storage, branches, or local side effects. Its API surface is preprocessor constants used by AMDGPU display code to compose and decode 16-bit DPCS/PHY control-register fields.

## Purpose

The header gives display-driver code symbolic bitfield locations for DPCS CR2 raw-lane digital PCS, PMA, FSM, interrupt, TX control, and RX control registers. This chunk mainly completes raw lane 0 control definitions, then provides large repeated raw lane 1 and raw lane 2 field maps, and starts raw lane 3 PCS TX override coverage.

The fields describe low-level Display PHY behavior: lane reset/request handshakes, link rate and lane width, power state, low-power detect, PLL and master PLL selection, TX/RX data enables, loopback enables, receiver adaptation/calibration state, DFE/AFE/IQ calibration controls, interrupt status and clear bits, termination and equalization overrides, PMA/PWM/MPHY controls, and OCLA/UPCS observation controls.

## Exported API Surface

There are no C-callable APIs or types. The exported interface is macro naming of this form:

- `DPCSSYS_CR2_RAWLANE<N>_<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `DPCSSYS_CR2_RAWLANE<N>_<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Important register families in this chunk:

- `DPCSSYS_CR2_RAWLANE0_DIG_*`: tail coverage for lane 0 PMA MPHY output masks, RX adaptation override output, TX/RX control, ATE RX/TX overrides, master MPLL loop enables, RX validity override, and TX data/async-data override fields.
- `DPCSSYS_CR2_RAWLANE1_DIG_PCS_XF_*` and `DPCSSYS_CR2_RAWLANE2_DIG_PCS_XF_*`: parallel PCS transfer interface definitions for TX override/input/output status, RX override/input/output status, RX adaptation acknowledgement and figure-of-merit fields, directed TX pre/main/post cursor values, lane numbering, ATE override, RX equalization and delta-IQ controls, termination controls, phase-2 calibration, and secondary RX/TX override registers.
- `DPCSSYS_CR2_RAWLANE1_DIG_FSM_*` and `DPCSSYS_CR2_RAWLANE2_DIG_FSM_*`: FSM override, status, monitor, fast-state, calibration/adaptation, lock, DCC, OCLA, TX EQ update, RCAL status, and RX IQ phase offset fields.
- `DPCSSYS_CR2_RAWLANE1_DIG_IRQ_CTL_*` and `DPCSSYS_CR2_RAWLANE2_DIG_IRQ_CTL_*`: lane-local interrupt status, clear, and mask fields for RX/TX reset and request events, RX rate and pstate changes, adaptation request/disable, lane transceiver mode, phase-2 calibration, loopback, DCC on-demand, and TX request events.
- `DPCSSYS_CR2_RAWLANE1_DIG_PMA_XF_*` and `DPCSSYS_CR2_RAWLANE2_DIG_PMA_XF_*`: PMA lane/supervisor/TX/RX override and input fields, RTUNE controls, MPHY controls, and RX adaptation override output fields.
- `DPCSSYS_CR2_RAWLANE1_DIG_TX_CTL_*`, `DPCSSYS_CR2_RAWLANE2_DIG_TX_CTL_*`, `DPCSSYS_CR2_RAWLANE1_DIG_RX_CTL_*`, and `DPCSSYS_CR2_RAWLANE2_DIG_RX_CTL_*`: lane TX/RX control FSM, clock, loss-of-signal mask, data-enable override counters, continuous DCC/off-cancellation/adaptation status, and OCLA/UPCS observation fields.
- `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN`: first lane 3 PCS TX override register, covering pstate, low-power detect, width, rate, MPLLB selection, MPLL enable, override enable, master MPLL states, and TX async enable override.

The lane 1 and lane 2 blocks are intentionally near-identical. Their shifts and masks encode the same per-lane hardware semantics with only the `RAWLANE1` versus `RAWLANE2` instance prefix changed.

## Register Areas Covered

PCS transfer-interface registers define the interface between lane PCS control logic and PHY-facing TX/RX signals. TX-side fields include pstate, low-power detect, width, rate, reset/request, DETRX request, VBOOST, IBOOST, TX beacon, async enable/data, loopback, TX data enable, and MPLL state/selection. RX-side fields include reset/request, rate, width, pstate, loss-of-signal threshold and LFPS handling, adaptation requests, continuous adaptation/off-cancellation, RX validity, RX data enable, RX2TX loopback, and several RX status/input mirrors.

RX adaptation and equalization registers expose training/control details: RX adaptation acknowledgement bits, adaptation done status, figure of merit, directed transmitter pre/main/post cursor values, RX EQ delta-IQ override values, coefficient override enables, AFE/DFE/IQ calibration entry points, VCO/reference load override values, and phase-2 calibration controls.

FSM registers expose micro-state controls and monitors for startup calibration, RX adaptation, AFE/DFE/bypass/reference-level/IQ calibration, supervisor and TX common-mode flows, RX detect, power-up, VCO wait/calibration, continuous calibration/adaptation, CR lock, TX DCC flags/status, OCLA, TX EQ update flags, RCAL status, and RX IQ phase offset. These are not executable state machines in this header; the macros describe the register fields used to observe or override hardware FSM behavior.

Interrupt-control registers define both status and write-clear/mask fields. Covered events include RX reset, RX request, RX rate, RX pstate, RX adaptation request/disable, lane transceiver mode, RX phase-2 calibration request/disable, lane RX2TX serial loopback, DCC on-demand, TX reset, and TX request. The `_CLR` and `_MASK` registers share similar event names but have different runtime semantics in consumers.

PMA transfer-interface registers define lane/PMA-side override and input/status bits: TX/RX data enable, resets, request/ack, pstate, rates and widths, PLL/MPLL enable and state, DETRX, VBOOST/IBOOST, termination control, TX common-mode, LFPS and loss-of-signal status, RTUNE request/ack, MPHY PWM controls, RX PWM/async controls, and RX PMA IQ phase adjustment override.

TX/RX control registers define lane-local controller behavior: TX wait time for MPLL off, which power states allow RX detection, TX clock enable/select and async beacon wait timing, DCC continuous status, OCLA FSM/data/clock enables, RX control FSM enable and rate-change behavior, RX loss-of-signal mask counters, RX data-enable override/reference tracking counters, and continuous off-cancellation/adaptation enable status.

## Control Flow And State Behavior

This chunk has no software control flow. Runtime control flow is in consumer code that includes this header and uses these constants with register read/modify/write helpers.

The bitfields nevertheless model several hardware control paths:

- Link and lane bring-up: reset/request/ack, pstate, rate, width, low-power detect, TX/RX data enable, and clock enable fields must be sequenced by the display link-management code.
- PLL and clocking: MPLLA/MPLLB state, MPLLB selection, MPLL enable, master MPLL override, TX clock selection, and VCO/reference load override fields participate in link-rate and PHY-clock configuration.
- RX training and adaptation: adaptation request/ack, continuous adaptation, off-cancellation, AFE/DFE/IQ calibration, phase-2 calibration, EQ override, and figure-of-merit fields expose training state and manual override hooks.
- Interrupt handling: status, clear, and mask registers require consumers to distinguish readable event state from write-one-to-clear and interrupt-mask semantics.
- Debug and observation: FSM monitors, fast-state registers, OCLA/UPCS enable bits, CR lock, DCC status, and IQ phase offset fields are intended for diagnostics, hardware validation, or tightly controlled bring-up flows.

No persistence is implemented in software. Register values persist only according to ASIC register reset and power domains. Some fields are status-only mirrors, some are writable controls, and some are override-enable/value pairs; the header itself does not encode access permissions.

## Dependencies And Integration Points

This file depends only on the C preprocessor, but it is meant to be included with companion generated DPCS 3.1.4 register address headers. Address headers select the register offset; this shift/mask header supplies field encodings.

Integration points include:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially display core and PHY/link-training paths that program DPCS CR registers.
- Common AMD register helper macros that combine masks and shifts for read/modify/write operations.
- DisplayPort/USB-C alternate-mode and HDMI-related PHY programming paths, inferred from field names such as `RATE`, `WIDTH`, `PSTATE`, `MPLL`, `DETRX`, `VBOOST`, `IBOOST`, `LFPS`, and lane loopback controls.
- Hardware diagnostics, bring-up, and validation tooling that reads FSM, interrupt, OCLA, DCC, calibration, and adaptation status fields.

## Risks

- Generated-header drift is the primary risk. A wrong shift or mask can corrupt adjacent hardware fields during read/modify/write, particularly because most registers are dense 16-bit bitfields.
- Chunk boundaries split register definitions. This range starts after the shifts for `RAWLANE0_DIG_PMA_XF_MPHY_OVRD_OUT` and ends at the comment before `RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_1`; merge tooling must reconcile adjacent chunks to avoid treating these as complete per-register summaries.
- Lane copy/paste errors are high impact. Raw lane 1 and raw lane 2 should remain parallel; a mismatched lane prefix or field mask can route programming to the wrong lane or decode status incorrectly.
- Status, clear, and mask registers share event vocabulary. Consumers must not treat `_IRQ`, `_IRQ_CLR`, and `IRQ_MASK` fields as interchangeable.
- Override value and override enable fields are paired throughout the chunk. Setting an override value without its enable, or leaving an enable asserted after training, can produce confusing PHY state.
- Reserved fields are explicitly named and masked. Driver code should preserve reserved bits unless the hardware specification for this ASIC explicitly requires otherwise.
- Several fields influence PHY calibration, PLL state, RX adaptation, and termination. Incorrect values can cause link-training failures, unstable display output, hotplug regressions, or suspend/resume issues that only reproduce on specific ASIC/display combinations.

## Test Signals

Useful validation signals for this chunk are mostly generated-header, build, and hardware-integration checks:

- Compile AMDGPU display code that includes `dpcs_3_1_4_sh_mask.h`.
- Compare this header against the authoritative DPCS 3.1.4 register database for exact field names, shifts, masks, and lane-instance repetition.
- Static checks that every complete register field in the chunk has matching `__SHIFT` and `_MASK` constants, while accounting for the deliberate boundary imbalance at lines 41437-41441.
- Grep/build checks for `DPCSSYS_CR2_RAWLANE1`, `DPCSSYS_CR2_RAWLANE2`, and `DPCSSYS_CR2_RAWLANE3` consumers after any rename or regeneration.
- Runtime display validation on ASICs using DPCS 3.1.4: DP link training at multiple rates and lane widths, HDMI mode if routed through these PHY blocks, hotplug, suspend/resume, display clock changes, lane disable/reenable, and error recovery.
- Register readback during bring-up to verify reset/request/ack, rate/width/pstate, MPLL state, TX/RX data enable, RX adaptation done/ack, calibration/FSM status, IRQ clear/mask behavior, and OCLA/debug status transitions.

## Chunk Notes For Merge

This chunk belongs to the CR2 raw-lane section of `dpcs_3_1_4_sh_mask.h`. Earlier chunks define the beginning of the CR2 block and the first part of lane 0; later chunks continue lane 3 and the rest of the file. The final per-file research document should describe the whole file as a generated ASIC bitfield map, not handwritten driver logic, and should merge the repeated lane 0-3 patterns rather than treating each lane as independent code.

### subset-b-002277: lines 43855-46340

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 43855-46340

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice. It exports preprocessor constants that describe bit positions and masks for CR2 display PHY/DPCS registers, mainly the `DPCSSYS_CR2_RAWLANE3` digital PCS/PMA lane-control block and the beginning of the repeated `DPCSSYS_CR2_RAWAONLANE*` always-on lane diagnostic and calibration blocks.

The source tree path is under a `ceph-client` mirror, but this file is AMDGPU DRM display hardware metadata. It does not implement filesystem behavior. Its purpose is to give display-driver code symbolic field definitions for safe read-modify-write access to memory-mapped or indexed DPCS registers when setting link rate, lane width, power state, resets, loopback, RX adaptation, PMA controls, interrupts, and lane calibration fields.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, variables, includes, locks, callbacks, allocation paths, or direct MMIO operations in this range. The exported interface is the generated register-field macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used to encode or decode a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate, clear, preserve, or update that field.

The chunk contains 2,101 `#define` lines: 1,051 `__SHIFT` macros and 1,050 `_MASK` macros. The one-count mismatch is a chunk-boundary artifact: line 46340 defines `DPCSSYS_CR2_RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST__RESERVED_15_8__SHIFT`, and its matching mask is outside this work-item range. The chunk also starts without the preceding register comment for `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_1`, though it contains that register's complete fields.

Major macro families in this slice:

- `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_*`: PCS transfer interface fields for TX/RX overrides, PCS inputs and outputs, RX adaptation acknowledgements, figure-of-merit reporting, TX pre/main/post direction controls, lane number, ATE overrides, RX equalization overrides, termination controls, and phase-2 calibration.
- `DPCSSYS_CR2_RAWLANE3_DIG_FSM_*`: lane FSM override, status, fast-state observability, RX startup/adaptation/calibration states, common calibration status, CR lock, TX DCC flags/status, OCLA debug selection, TX EQ update flags, RCAL status, and RX IQ phase offset.
- `DPCSSYS_CR2_RAWLANE3_DIG_IRQ_CTL_*`: per-event interrupt status, clear, and mask fields for RX reset/request/rate/pstate/adaptation, lane transceiver mode, phase-2 calibration, loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR2_RAWLANE3_DIG_PMA_XF_*`: PMA transfer and MPHY override/status fields covering lane reset, test powerdown, beacon/receiver-detect controls, transmit and receive PMA enable/idle/signaling controls, VCO/reference load values, RTUNE state, SRAM bypass/load/init status, and RX adaptation outputs.
- `DPCSSYS_CR2_RAWLANE3_DIG_TX_CTL_*` and `DPCSSYS_CR2_RAWLANE3_DIG_RX_CTL_*`: TX/RX local FSM control, clock control, DCC/continuous adaptation status, loss-of-signal masking, RX data-enable override, and OCLA observability.
- `DPCSSYS_CR2_RAWAONLANE0_DIG_*`, `RAWAONLANE1_DIG_*`, and `RAWAONLANE2_DIG_*`: repeated always-on lane fields for RX adaptation values, fast flags, DFE taps, slicer control, common calibration status, RX signal-detect filtering/calibration, DCC calibration codes, TX DCC bank access, MPLL background controls, firmware configuration, and lane transceiver mode.
- `DPCSSYS_CR2_RAWAONLANE3_DIG_*`: the beginning of the lane 3 always-on block, through the first DFE bypass offset shift at the chunk boundary.

## Control Flow

This header has no runtime control flow. It contributes constants to control paths elsewhere:

1. AMDGPU display code includes `dpcs_3_1_4_offset.h` for register addresses and `dpcs_3_1_4_sh_mask.h` for fields.
2. Register helper macros token-paste a register and field name into offset, mask, and shift constants.
3. Runtime code composes values, performs read-modify-write updates, polls status, or writes interrupt clear bits through ASIC-specific register accessors.
4. Hardware state machines consume or expose these fields for PHY bring-up, link training, lane reset, clocking, adaptation, calibration, loopback, ATE/test modes, interrupt delivery, and debug capture.

The constants do not encode required sequencing. Consumer code must still follow the hardware rules for reset ordering, power-state changes, MPLL selection, TX/RX request and acknowledge handshakes, adaptation request/acknowledge handling, DCC calibration, signal-detect tuning, and interrupt clear/mask ordering.

## State And Persistence Behavior

The header stores no software state and persists nothing. The underlying registers are live hardware state:

- TX and RX PCS override fields persist programmed values such as reset/request overrides, link rate, lane width, pstate, low-power detect, MPLL selection/enables, async data controls, beacon enable, loopback, RX data enable, adaptation controls, VCO/reference load overrides, and equalization override values until hardware reset, power-domain reset, or later driver writes.
- PCS/PMA output and status fields expose transient or sticky hardware observations such as ACK bits, DETRX result, RX adaptation acknowledgement, TX/RX PMA enables, idle/valid state, VCO/ref load values, RTUNE done, SRAM load/init state, MPHY override output, RX adaptation outputs, and lane transceiver mode.
- FSM fields expose current and historical state-machine details, including fast-state flags, calibration phase state, TX DCC flags/status, CR lock, TX EQ update, common calibration status, and OCLA debug selection.
- IRQ status, clear, and mask fields represent interrupt state. Some fields are likely status-only, some are mask/configuration bits, and clear registers are write-triggered. The header does not state which bits are write-one-to-clear, read-only, self-clearing, or sticky.
- RAWAON lane fields hold or expose calibration/adaptation data for RX AFE/DFE, DCC, signal detection, firmware configuration, and transceiver mode. These values can survive longer than the active lane datapath depending on the always-on power domain, but the header itself gives no reset-value or retention contract.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, which defines matching `ix...` register addresses. In that file, this chunk maps `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_*` from the `0x3300` range, `DPCSSYS_CR2_RAWLANE3_DIG_FSM_*` from `0x3320`, IRQ control from `0x3340`, PMA transfer from `0x3360`, TX/RX local control from `0x3380` and `0x33a0`, ATE-related PCS registers from `0x33c0`, and RAWAON lane registers beginning at `0x4000`.

The practical integration points are AMDGPU display and PHY code that configures DisplayPort/HDMI/USB-C physical lanes for ASICs using DPCS 3.1.4. The generated names are intended for common AMD register helper idioms such as `REG_SET`, `REG_UPDATE`, `REG_GET`, or indexed-register wrappers. The repeated register shapes across `RAWLANE3` and `RAWAONLANE0/1/2/3` are an ABI contract: generic lane-management code can select an instance while relying on consistent field names, shifts, and masks.

This slice also integrates with firmware/test/debug surfaces:

- ATE override registers let manufacturing or validation code force TX/RX values independent of normal PCS/PMA control.
- OCLA and UPCS OCLA fields expose internal observability selections for debug capture.
- Firmware configuration and calibration fields under `FW_*`, `FAST_FLAGS`, `ADPT_CTL_*`, and calibration-code registers reflect coordination with firmware or microcontroller-managed lane adaptation.
- Interrupt status/clear/mask fields connect low-level lane events to DRM hotplug/link-management recovery paths.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong shift or mask compiles cleanly but programs or reads the wrong silicon bits, which can manifest as link-training failures, unstable displays, calibration timeouts, or unhandled lane interrupts.
- This work item starts and ends on register boundaries only partially. The previous chunk owns the `PCS_XF_TX_OVRD_IN_1` register comment context, and the next chunk owns the matching mask for the final `RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST` shift.
- The register names mix command, override-enable, override-value, status, clear, mask, and reserved fields. Treating all fields as normal writable configuration can lose interrupts, write reserved bits, or fight hardware-owned state machines.
- PCS/PMA reset, request/ack, data-enable, MPLL, pstate, width, and rate fields are sequencing-sensitive. Updating them while the lane is active can disrupt link training or data transmission.
- ATE, loopback, MPHY override, RX/TX PMA override, and signal-detect override fields can bypass normal hardware control. Leaving these set after diagnostics can break normal PHY operation.
- RAWAON lanes 0, 1, and 2 are large parallel blocks. Copy/paste or generation errors between lane instances are especially hard to notice because the field layouts are intentionally similar.
- Several registers expose mostly `RESERVED_*` fields. Driver code should not infer those are safe storage bits; reserved masks mainly describe bits to preserve during field updates.
- Status fields for adaptation, calibration, DCC, signal detect, and common calibration depend on analog hardware behavior. Software-only tests cannot prove their semantics without hardware readback.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU display code for ASICs using DPCS 3.1.4; missing or renamed generated macros should become compile failures in register-table or PHY programming code.
- Mechanical consistency checks against AMD's generated register database and `dpcs_3_1_4_offset.h`, especially that every complete field has one `__SHIFT` and one matching `_MASK`.
- Cross-lane comparison of the repeated RAWAON blocks for lanes 0, 1, and 2, plus reconciliation with the next chunk for the rest of lane 3.
- Runtime display validation on relevant hardware: link bring-up, hotplug, suspend/resume, mode changes, link-rate changes, lane-count changes, DP Alt Mode transitions, and HDMI/DP PHY power cycling.
- Instrumented register readback during PHY bring-up to confirm reset, request/ack, pstate, width/rate, MPLL enable/state, RTUNE, SRAM load/init, DCC, adaptation, and signal-detect fields move through expected states.
- Interrupt-path tests that trigger or observe RX reset/request/rate/pstate/adaptation events, phase-2 calibration events, loopback events, DCC on-demand, and TX reset/request interrupts; stale IRQs or repeated clears indicate mask/clear-field errors.
- Diagnostic/validation tests for ATE, OCLA, loopback, RX equalization, signal-detect calibration, DFE tap reporting, and firmware calibration fields, with cleanup checks that override enable bits return to normal values.

## Cross-Chunk Notes

The previous chunk should be consulted for the beginning of the `DPCSSYS_CR2_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN` area and the register comment context immediately before line 43855. The next chunk should be consulted for the rest of `DPCSSYS_CR2_RAWAONLANE3_DIG_*`, including the mask paired with the final shift in this range. The final merged per-file report should describe this header as generated DPCS 3.1.4 register ABI metadata, not handwritten driver logic.

### subset-b-002278: lines 46341-48787

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 46341-48787

## Scope

This chunk is a generated AMD DPCS 3.1.4 shift/mask header segment. It covers lines 46341-48787 of `dpcs_3_1_4_sh_mask.h`, defining bit positions and masks for DPCS CR2 raw always-on lane registers, generic lane mirrors, supervisor PLL/control registers, and the beginning of the generic lane ASIC/TX power-control register block.

The chunk is declarative only. It contains no C functions, types, storage, or executable control flow. The exported surface is preprocessor constants named as:

- `DPCSSYS_CR2_*__FIELD__SHIFT`
- `DPCSSYS_CR2_*__FIELD_MASK`

Within the exact line range, the slice contains 1,077 `__SHIFT` definitions and 1,076 `_MASK` definitions. The imbalance is from chunk boundaries: line 46341 is the trailing mask for `DPCSSYS_CR2_RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST`, whose shift is above this range, and line 48787 is only the next register comment for `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_DCC_DAC_ACK`, whose shift/mask definitions continue after this chunk.

## Purpose

The header gives DCN 3.1.4 display driver code symbolic bitfield metadata for DPCS hardware registers. These constants are intended to be paired with register offset constants from `dpcs_3_1_4_offset.h` and consumed by AMD display register helper macros that perform read/modify/write, field extraction, and field composition without embedding raw bit positions in handwritten code.

This chunk focuses on DPCSSYS CR2:

- The tail of concrete `RAWAONLANE3` receive/adaptation/calibration fields.
- A complete generic `RAWAONLANEX` mirror of the same raw always-on lane register surface.
- The `SUPX` supervisor register surface for reference clocks, MPLLA/MPLLB override/ASIC-in status, spread-spectrum control, RTUNE, bandgap, and MPLL power control.
- The start of the `LANEX` generic lane register surface for ASIC override/status paths and TX power-control timing/DCC programming.

The repeated `LANE3` and `LANEX` naming is important: `LANE3` maps to a concrete lane address range, while `LANEX` maps to a generic lane/indirect access range. Their field semantics are largely parallel but their offsets differ in the companion offset header.

## Exported API Surface

There are no callable APIs or structs. The exported API is a set of macros usable anywhere this generated header is included. The header is included by DCN 3.1.4 resource code alongside `dpcs_3_1_4_offset.h`, for example in `drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`.

Important macro families in this chunk:

- `DPCSSYS_CR2_RAWAONLANE3_DIG_*`: concrete lane 3 fields for RX adaptation, DFE/DCC calibration, signal detect, fast calibration bypass flags, firmware configuration bits, lane mode selection, and TX DCC config.
- `DPCSSYS_CR2_RAWAONLANEX_DIG_*`: generic lane mirror fields for the same RX/DFE/adaptation/calibration/signal-detect surfaces, including additional early fields such as AFE offsets, RX IQ adaptation, RX adaptation figure-of-merit, DFE data/ref-level offsets, phase-adjust linear/map fields, and then the same later controls as lane 3.
- `DPCSSYS_CR2_SUPX_DIG_*` and `DPCSSYS_CR2_SUPX_ANA_*`: supervisor clock, PLL, bandgap, RTUNE, analog status, override output, ASIC input, and MPLL power-control fields.
- `DPCSSYS_CR2_LANEX_DIG_ASIC_*`: generic lane ASIC interface fields for TX/RX override inputs, ASIC input/status mirrors, CDR/VCO values, EQ controls, request/ack handshakes, and override output/status.
- `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_*`: TX power-state bitfields, TX power-up timing fields, and the first TX DCC control-bank/DAC-selection fields.

All field values in this range are low-level numeric constants. Most masks are 16-bit-style values with an `L` suffix, matching the CR register width exposed by this block. Some fields are full 16-bit data payloads such as `ADDR`, `DATA`, or `VAL`.

## Register Areas Covered

### RAWAONLANE3 Lane Tail

The `RAWAONLANE3` portion begins mid-register at line 46341, with the reserved mask for `DPCSSYS_CR2_RAWAONLANE3_DIG_DFE_BYPASS_EVEN_VDAC_OFST`. It then covers the rest of the concrete lane 3 raw always-on digital block.

Key lane 3 register categories:

- DFE and phase/calibration remnants: bypass/error VDAC offsets, RX IQ phase adjust, MPLLA/MPLLB coarse tune, and initial power-up done.
- RX adaptation readouts: attenuation, VGA, CTLE boost/pole, DFE taps 1-5, slicer controls, and `ADPT_CTL_0` through `ADPT_CTL_7` full-width control words.
- Calibration/status bits: lane common MPLL/RCAL init and done bits, MPLL disable, RX adaptation done, stats, DCC code fields for ICM/IDF/QCM/QDF, IOFF/ICONST/VREFGEN calibration codes, and RX VREFGEN enable.
- Fast-mode flags: `FAST_FLAGS` exposes bypass/fast paths for startup, adaptation, AFE/DFE/bypass/reference/IQ calibration, TX common mode, TX RX detection, RX power-up, VCO wait, and VCO calibration. `FAST_FLAGS_2` extends this to continuous calibration/adaptation paths, DCC/VPHUD/VREF/sigdet shortcuts, and `SKIP_TX_RTUNE_CAL`.
- RX/TX override and signal-detect controls: TX/RX override input, RX loss-of-signal mask, signal-detect filter control, RX override outputs, signal-detect calibration and HF/LF codes, signal-detect output override/input, and RX signal-detect configuration.
- Firmware hooks: firmware MM, adaptation, and calibration config registers.
- Lane mode and DCC setup: lane transceiver mode override/input and TX DCC bank/address/data/config controls.

These fields model values that are typically set or observed during link bring-up, receiver adaptation, signal detection, calibration, and PHY debugging.

### RAWAONLANEX Generic Lane Mirror

The `RAWAONLANEX` block repeats the lane register map in generic form. It starts earlier than the visible `RAWAONLANE3` tail, so this chunk includes the full generic sequence from AFE offset/adaptation fields through TX DCC configuration.

Additional generic-lane fields visible here include:

- AFE/CTLE IDAC offsets.
- RX IQ adaptation values and RX adaptation figure-of-merit.
- DFE summer, phase, data, bypass, error, even/odd reference-level, and phase-adjust mapping fields.

After those early generic fields, `RAWAONLANEX` mirrors the same adaptation, calibration, fast flag, signal-detect, firmware, lane mode, and TX DCC families present for `RAWAONLANE3`. This symmetry is a useful generated-header consistency signal: if a driver can address a lane through a generic lane path, it can use the same field semantics without hard-coding lane 3-specific names.

### SUPX Supervisor And PLL Control

The `SUPX` portion exposes shared CR2 supervisor state rather than per-lane raw adaptation state.

Covered supervisor areas include:

- ID code placeholders: `DPCSSYS_CR2_SUPX_DIG_IDCODE_LO` and `_HI` appear as comments only in this slice, indicating register names with no field macros in the chunk.
- Reference clock override: enable, override-enable, pad selection, clock range, bandgap enable, HDMI mode enable, and pre-high-power override controls.
- MPLLA/MPLLB divider and HDMI clock overrides: divider clock enable, divider multipliers, pixel-clock divider, HDMI divider, and override enables.
- MPLLA/MPLLB analog override inputs: enable, div5, TX clock divider, V2I, standby, VCO frequency, calibration force, FRACN, clock sync, multiplier, calibration comparator settings, multiplier thresholds, integer/fractional fields, SSC peak/step settings, accumulator control, gear-shift fields, charge-pump controls, and VREG/VCM/PMIX related settings.
- Supervisor override/input/status: general supervisor override bits, prescaler override, supervisor override outputs, level override, MPLLA/MPLLB ASIC input mirrors, divider/HDMI ASIC input mirrors, bandgap ASIC input, charge-pump ASIC input, and analog status/override output.
- Analog controls: prescaler control, RTUNE control, bandgap registers, and switch power measurement.
- MPLL power-control sub-blocks for MPLLA and MPLLB: MPLL power override, status, DAC max range, lock/pixel-clock stable timers, calibration controls, analog DAC output, and SSC spread type.
- Clock/reset timing and RTUNE: bandgap/reference power-up timers, reference VPHUD timing, RTUNE config/status, RX/TXDN/TXUP set and status values, RTUNE counters, and TX calibration code.

This block is the shared PLL/reference/termination layer that per-lane link programming depends on. It contains many request/status pairs and override/override-enable pairs, so consumers need to treat field direction carefully.

### LANEX ASIC And TX Power-Control Start

The `LANEX` portion begins the generic lane digital block. It covers interface wiring between the ASIC/display controller and the PHY lane, plus the start of TX power management.

Covered `LANEX_DIG_ASIC_*` areas include:

- Lane override input fields for lane power state, RX/TX state, lane mode, and MPLL selection.
- TX override inputs for analog power, clocking, reset, serial/data enable, boost, common-mode, voltage mode, main/pre/post cursor levels, TX muxing, DCC compensation, clock loopback, AC JTAG, and additional TX fast-start style controls.
- RX override inputs for signal-detect calibration, squelch controls, PWM controls, reference generator, clock/data enable, reset, equalization/VCO controls, DCC, VPHUD, VREF, adaptation, and DFE/slicer settings.
- ASIC input mirrors for lane, TX, RX, RX EQ, RX CDR/VCO, and ASIC output/status fields.
- Override outputs for TX/RX controls, repeater enable, digital clock state, shift/ack handshakes, and OCLA clock/data enables.

The TX power-control sub-block covers:

- P-state definitions for `P0`, `P0S`, `P1`, and `P2`, including TX analog reference generator, VCM hold, analog clock/word clock, reset, serial enable, digital clock, data enable, RX detection allowance, VBOOST allowance for P2, and DCC compensation calibration enable.
- Power-up timing registers for reference generator enable time, clock enable time, VCM hold time, VBOOST disable time, ground-sense VCM hold pulse timing, RX-detect time, reset time, serial-enable time, and fast/skip controls.
- DCC control-bank and DAC programming registers: CR bank address/data, DAC control, DAC range, and DAC selection request/update bits. The next `DCC_DAC_ACK` register is only introduced by comment at the final line of this chunk; its actual fields are in the following chunk.

## Control Flow And State Behavior

This file has no software control flow. Runtime sequencing is imposed by the hardware state machines that consume these fields and by driver code that writes or polls them through register helpers.

The fields imply several important state-machine surfaces:

- RX adaptation and calibration: adapted ATT/VGA/CTLE/DFE values, adaptation done, DCC code readouts, calibration config fields, continuous calibration fast flags, slicer controls, and VREFGEN fields expose the state of receiver tuning.
- Power-up and power-state transitions: initial power-up done, TX P-state bitfields, TX power-up timers, reference generator timing, VCM hold timing, VBOOST timing, reset/serial/data enables, and clock-enable fields must be programmed in hardware-defined order.
- PLL and clock control: MPLLA/MPLLB override inputs, divider/HDMI clock overrides, SSC configuration, MPLL power-control timers, calibration controls, lock/status fields, and supervisor reference-clock controls define shared clock state used by lanes.
- Request/ack and override handshakes: many fields pair a requested value with an override-enable bit or a status/ack bit. Examples include supervisor override paths, ASIC TX/RX overrides, signal-detect output override/input, RTUNE status, shift output/ack, DAC selection request, and lane common calibration init/done status.
- Signal detection and link presence: loss-of-signal masks, signal-detect filter, signal-detect calibration/HF/LF codes, squelch/PWM controls, and RX signal-detect configuration feed hotplug/link-detect behavior and low-power entry/exit decisions.
- TX DCC programming: bank address/data and DAC selection/update fields form an indirect programming path into DCC calibration state. The sliced boundary before `DCC_DAC_ACK` means the request side is visible here but the acknowledgement macro definitions are outside this work item.

No state is persisted by this header. Persistence belongs to hardware registers and their power/reset domains. Full-width `VAL`, `ADDR`, `DATA`, timer, scratch-like, and calibration code masks merely expose writable/readable register storage; this chunk does not define software ownership or retention policy for those values.

## Dependencies And Integration Points

The header depends only on the C preprocessor, but it is meaningful only in combination with generated register address definitions and AMD display register access helpers.

Key dependencies and integration points:

- `dpcs_3_1_4_offset.h`: provides `ixDPCSSYS_CR2_*` offsets for the register names whose fields are defined here. For example, `RAWAONLANE3` registers in this area map around offsets `0x430f` through `0x4351`, generic `RAWAONLANEX` starts at `0x7000`, and `LANEX_DIG_TX_PWRCTL_DCC_DAC_SEL` maps to `0x902e`.
- DCN 3.1.4 resource code includes both `dpcs_3_1_4_offset.h` and this shift/mask header, making these constants available to display resource construction and lower-level register programming.
- AMD display register helper code such as `reg_helper.h` expects separate register, field, mask, and shift definitions. These macros fit that convention.
- Hardware/firmware coordination paths: names such as `FW_MM_CONFIG`, `FW_ADPT_CONFIG`, `FW_CALIB_CONFIG`, supervisor override outputs, ASIC input mirrors, and generic lane override paths show integration with firmware-managed or hardware-managed PHY state.
- Display PHY link-management paths: receiver adaptation, signal detect, DFE/DCC calibration, MPLL programming, RTUNE, TX P-state sequencing, and DCC DAC programming all affect DisplayPort/HDMI/PHY bring-up and recovery.

There are no local includes or compile-time conditionals in this slice; include guards and licensing are outside the chunk.

## Risks

- Generated-header drift is the primary risk. Any wrong shift or mask can corrupt adjacent hardware fields in read-modify-write operations. This is especially risky in dense 16-bit CR registers where many one-bit enable/status fields are packed together.
- The `RAWAONLANE3` and `RAWAONLANEX` blocks are highly parallel. A copy/generation mismatch between concrete lane and generic lane fields would be hard to detect at compile time but could cause lane-specific and generic access paths to behave differently.
- Many fields expose override values next to override-enable bits. Driver code that writes a value without coordinating the corresponding `_OVRD_EN` field may appear to update a value while hardware continues using the non-overridden path, or may unexpectedly seize control from firmware/hardware state machines.
- Request/status ordering matters. Fields such as calibration init/done, RTUNE status, DAC selection request/update, shift/ack, clock enable/status, and MPLL power-control status should not be treated as plain configuration bits.
- Fast/skip flags can bypass calibrations or timing waits. Incorrect values in `FAST_FLAGS`, `FAST_FLAGS_2`, `SKIP_TX_RTUNE_CAL`, `FAST_TX_RXDET`, or timer skip bits can produce marginal links, unstable training, or failures that only appear on specific boards, cables, link rates, or power states.
- Reserved fields are explicitly named and masked in many registers. Code should preserve reserved bits unless the hardware programming guide says otherwise; writing raw full-register values with these masks risks toggling undocumented controls.
- The line-range boundaries split complete register definitions. The opening line is only a trailing mask for a previous field, and the final `DCC_DAC_ACK` register is only a comment in this chunk. Any automated per-chunk validation must account for boundary carry-over rather than assuming every comment in the chunk has a complete field set.
- Cross-generation comparison shows similarly named DPCS versions may differ in width or added fields. Consumers must not mix masks from `dpcs_3_1_4_sh_mask.h` with offsets or field expectations from later `dpcs_4_*` or `dcn_4_*` generated headers.

## Test Signals

Useful validation signals for this chunk are mostly compile-time, generation-time, and hardware-integration oriented:

- AMDGPU/DCN 3.1.4 build coverage that preprocesses `dcn314_resource.c` and any downstream files including `dpcs_3_1_4_sh_mask.h`.
- Generated-register consistency checks comparing this header against the authoritative DPCS 3.1.4 register database, especially for paired `RAWAONLANE3` and `RAWAONLANEX` fields.
- Static checks that field masks align with shifts and expected widths, while allowing this chunk's two boundary exceptions.
- Cross-header checks that every register field in this shift/mask chunk has a corresponding register offset in `dpcs_3_1_4_offset.h`.
- Runtime link bring-up tests on DCN 3.1.4 ASICs: DisplayPort and HDMI hotplug, link training across rates, suspend/resume, display mode changes, low-power transitions, and error recovery.
- PHY diagnostics/readback during bring-up: RX adaptation done/readouts, DFE tap values, signal-detect status, MPLL lock/power-control status, RTUNE status, TX P-state transitions, TX DCC DAC request/ack, and calibration code readbacks.
- Stress tests for paths implied by fast/skip controls: repeated hotplug, short/long cable combinations, cold boot, warm resume, high link rates, and continuous calibration/adaptation behavior.

## Chunk Notes For Merge

This chunk should merge into the per-file report as one middle section of a much larger generated register-map header. It is not handwritten driver logic. The merged document should describe this file as an ASIC-specific bitfield map and should preserve the distinction between concrete CR2 lane 3 fields, generic `LANEX`/`RAWAONLANEX` fields, and shared `SUPX` supervisor fields. The following chunk is needed to complete `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_DCC_DAC_ACK` and subsequent `LANEX` TX clock/lane controls.

### subset-b-002279: lines 48788-51226

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 48788-51226

## Scope And Purpose

This chunk is a generated AMD DC/DPCS register field mask header segment. It contains no executable C logic, functions, structs, or enum declarations. Its role is to publish preprocessor constants for bit shifts and masks used by AMDGPU display code when composing or decoding register values for the DPCS 3.1.4 block, especially CR2 per-lane PHY control/status registers and the following `dpcssys_dcio_dcio_dispdec` address block.

Every field follows the same contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask value.
- Most CR2 lane registers in this chunk are 16-bit fields with masks ending in `L`; the DCIO/UNIPHY display decode block at the end uses 32-bit masks for wider display registers.

The chunk starts mid-register with `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_DCC_DAC_ACK` fields, then covers many complete register-comment blocks through `DCIO_SOFT_RESET`.

## Register Families Covered

The CR2 lane digital TX/RX control region defines constants for DCC DAC acknowledge/addressing, TX clock alignment, LBERT test pattern generation, RX power-state definitions, RX power-up timing, VCO/CDR calibration, RX adaptive equalization, statistics/counters, MPHY/PWM support, analog override/status fields, PCS/PMA cross-interface fields, FSM controls, IRQ flags/masks, and TX/RX control state. These names are all prefixed primarily with `DPCSSYS_CR2_LANEX_*` or `DPCSSYS_CR2_RAWLANEX_*`.

The `dpcssys_dcio_dcio_dispdec` address block begins at line 51050 and switches to display/DCIO naming. It includes `DC_GENERICA`, `DC_GENERICB`, `DCIO_CLOCK_CNTL`, `DC_REF_CLK_CNTL`, UNIPHY channel inversion/crossbar registers for UNIPHYA through UNIPHYE, `DC_PINSTRAPS`, `INTERCEPT_STATE`, backlight PWM frame-start selection, genlock/swaplock pad controls, and `DCIO_SOFT_RESET`.

## Important Macro Interfaces

RX power-state macros define the bit layouts for `DPCSSYS_CR2_LANEX_DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, and `P2`. Each p-state block exposes the same operational signals: AFE enable, clock regulator enable, analog clock enable, deserializer enable, CDR enable, VCO frequency reset, VCO calibration reset, continuous VCO calibration enable, and digital clock enable. These masks are used by callers to program different receiver power/performance states without hardcoding the bit positions.

RX power-up timing is represented by `RX_PWRUP_TIME_1`, `RX_PWRUP_TIME_2`, and `RX_PWRUP_TIME_3`. The fields cover AFE/VREG/clock enable delays, fast-start enable bits, RX rate timing, CDR enable timing, deserializer enable timing, and deserializer disable timing. These constants matter when software sequences a lane into active operation or fast-start modes.

RX VCO/CDR calibration is represented by `RX_VCO_CAL_CTRL_0` through `_2`, `RX_VCO_CAL_TIME_0` and `_1`, `RX_VCO_STAT_0` through `_2`, `RX_CDR_CDR_CTL_0` through `_4`, `RX_CDR_STAT`, `RX_DPLL_FREQ`, and DPLL frequency bounds. The fields expose fixed-count controls, calibration step count, skip-calibration bits, VCO startup/update/settle timing, calibration done flags, final counter values, VCO correctness/up indicators, CDR phase detector controls, spread-spectrum counters, DPLL gain override fields, and upper/lower frequency bounds.

RX adaptive equalization is represented by `RX_ADPTCTL_ADPT_CFG_0` through `_9`, reset controls, status fields for ATT/VGA/CTLE/DFE taps, slicer and VDAC offset fields, DAC control selects, and CR bank address/data fields. Important knobs include adaptation timing and clock division, CTLE/VGA/ATT/DFE enable masks, threshold fields, adaptation step-size fields, initial error slicer levels, adaptation reset bits, and final adaptation code/status fields.

RX statistic and match/counter macros define `RX_STAT_*` registers. These include pattern masks and pattern values, statistic source/shift/clock selection, sample-count start/stop/pause bits, seven statistic counter enable bits and counter values, valid-loss clear/control bits, and calibration comparison clock controls. These macros are likely used by diagnostic or bring-up flows to measure link behavior and pattern matches.

Analog override macros map software-accessible controls for TX/RX analog behavior. TX coverage includes data/clock/reference/reset/serial enable, data rate, RX detect, termination code override, TX equalization leg pull enables/directions, pre/post controls, DCC calibration controls, fast start, loopback clock enable, and AC JTAG enable. RX coverage includes data rate, word/div4 clocks, DFE/adaptation enable, power overrides, VCO/frequency tuning overrides, calibration muxes/modes, DAC control selection, AFE ATT/VGA/CTLE/slicer/scope controls, IQ phase adjustment, signal-change enables, analog status, termination override, MPHY PWM/squelch controls, and signal-detect calibration thresholds.

The raw lane PCS/PMA cross-interface macros define override/input/output handshakes between PCS and PMA. PCS fields include TX/RX `REQ`, `RESET`, `PSTATE`, `RATE`, `WIDTH`, low-power detect, MPLL selection/enables, adaptation request/continuous/offcan signals, loopback enable overrides, async data enables, RX EQ fields, phase-2 calibration request/ack bits, lane number, ATE overrides, termination controls, and TX pre/main/post direction hints. PMA fields include lane MPLL enables, supervisor states, TX/RX request/reset/data enable overrides, beacon/async/loopback controls, lane retune request/ack, MPHY PWM and termination overrides, and IQ phase map override.

FSM and IRQ macros expose the lane micro-sequencer and interrupt model. `FSM_FSM_OVRD_CTL` can select jump address, start commands, enable override, or break execution; monitor registers expose memory address, state, command-ready, ALU flags, wait counter, and read/write-mask disabled flags. The many `FAST_RX_*`, `FAST_TX_*`, and `FAST_FLAGS` registers provide one-bit fast-path calibration/power/adaptation bypass or status controls. IRQ fields expose RX/TX reset/request/rate/pstate/adaptation/phase-2-calibration/loopback/DCC interrupts, matching clear registers, and aggregate mask registers.

The DCIO/UNIPHY macros at the end are wider display fabric controls. `DC_GENERICA` and `DC_GENERICB` select generic outputs and UNIPHY clock sources. UNIPHY link/crossbar controls expose channel inversion and channel source mapping. `INTERCEPT_STATE` exposes PWRSEQ and DPCS intercept state bits. `DCIO_SOFT_RESET` publishes per-UNIPHY and per-DSYNC soft-reset bits.

## Control Flow And State Behavior

There is no direct control flow in this header chunk. Runtime behavior emerges in code that includes this header and performs register read/modify/write operations using these masks and shifts. Typical consumers combine field values as `(value << SHIFT) & MASK`, OR several fields together, or extract a register field by masking then shifting.

The represented hardware state is persistent only in device registers. Writes to control, override, reset, IRQ-clear, and calibration fields can change PHY/display hardware state until hardware, firmware, driver, or reset code changes the register again. Status macros name readback-only or status-like fields such as `ACK`, `*_DONE`, `*_STATUS`, `*_STAT`, `RX_VALID`, VCO counter values, interrupt latches, and calibration results. The header itself stores no state and has no initialization.

Several macro groups imply hardware sequencing dependencies even though this file does not implement them: power p-state bits must be coherent with RX/TX timing fields; VCO/CDR resets and continuous calibration enables must match calibration timing; adaptation enable/reset/status fields must be sequenced around receiver training; IRQ clear registers pair with IRQ status and mask registers; PCS/PMA override enable bits must be set consistently with override value bits; and DCIO soft-reset bits must be used with care because they target shared UNIPHY/DSYNC blocks.

## Dependencies And Integration Points

This header depends only on the C preprocessor. It is intended to be included by AMDGPU display and DC register access layers along with corresponding register address headers for the same ASIC block. The naming indicates integration with the Linux AMD DRM display stack under `drivers/gpu/drm/amd`, especially low-level display core code that programs DPCS/DCIO/UNIPHY lanes.

The macro names are part of a generated register ABI. Other code can reference them directly, so renaming or regenerating with changed names has broad build impact. The address constants are not in this chunk; callers must pair these `_SHIFT` and `_MASK` definitions with the corresponding register offset definitions from sibling ASIC register headers.

The chunk also bridges multiple hardware conceptual layers: analog PHY lane controls, digital PCS/PMA interfaces, FSM/IRQ management, and display fabric/DCIO controls. That makes it an integration point between normal display link bring-up, factory/ATE test paths, diagnostics, and low-level debug tooling.

## Risks And Maintenance Notes

Incorrect mask or shift values can silently corrupt hardware programming. The highest-risk fields are reset, override-enable, power-state, VCO/CDR calibration, adaptation, and soft-reset bits because a wrong value can disable a lane, stall link training, mask interrupts, or reset a shared display block.

Reserved fields are explicitly named and masked throughout the chunk. Driver code should avoid writing arbitrary values to reserved masks unless the hardware programming guide or generated sequence requires it. A broad register write that fails to preserve reserved bits can introduce ASIC-specific regressions.

Many fields have paired `*_OVRD_VAL` and `*_OVRD_EN` bits. Setting the value without the enable bit, or leaving enable set after a debug/test path, can produce misleading behavior. IRQ fields also have status, clear, and mask variants with similar names; accidentally using a clear mask where a status or mask field is expected would be a hard-to-debug interrupt issue.

The DCIO/UNIPHY section uses 32-bit masks while most earlier CR2 lane macros use 16-bit masks. Callers and code generators should preserve the target register width and not assume all masks in this file are 16-bit.

Because this is generated source, hand edits are risky. The reliable maintenance path is regeneration from the authoritative register database, followed by build and hardware-focused validation.

## Test Signals

Useful build-time signals are successful compilation of AMDGPU display code that includes this header and absence of duplicate or missing macro-name errors after regeneration. Static checks can verify that every field has a matching `_SHIFT`/`_MASK` pair, masks align with shifts, masks do not overlap unexpectedly within a register, and 16-bit versus 32-bit register widths are preserved.

Runtime validation requires hardware or simulation. Relevant signals include successful display link bring-up across rates and power states, stable RX/TX training and adaptation, correct VCO/CDR calibration done/status readbacks, expected IRQ masking/clearing behavior, successful loopback/LBERT/ATE diagnostics where supported, correct UNIPHY channel routing/inversion, and safe behavior of DCIO soft resets.

For this specific chunk, regression tests should emphasize RX p-state transitions, fast-start timing, DPLL/VCO calibration bounds and statuses, adaptation status counters, PCS/PMA override handshakes, IRQ clear/mask behavior, and DCIO/UNIPHY channel crossbar programming.

### subset-b-002280: lines 51227-53595

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 51227-53595

## Purpose

This chunk is a generated AMD DPCS 3.1.4 shift/mask header slice for display PHY, GPIO, DDC/I2C, HPD, AUX-pad, and RDPCSTX link-transmitter register fields. It contains no executable C code. Its public surface is a set of preprocessor constants that describe field bit positions and masks for DCN 3.1.4 display hardware.

The requested range contains 2,164 `#define` entries: 1,077 `__SHIFT` constants and 1,087 `_MASK` constants. It starts inside the tail of `DCIO_SOFT_RESET`, covers the `dpcssys_dcio_dcio_chip_dispdec` GPIO/DDC/AUX register block, covers the first two RDPCSTX transmitter instances, and ends inside `RDPCSTX1_RDPCSTX_PHY_CNTL16`. The boundaries are artificial chunk boundaries: the soft-reset register begins before this range, and the RDPCSTX1 PHY generic-bus fields continue after it.

Although this file lives under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this range. The API contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the field's least-significant bit position inside the register.
- `<REGISTER>__<FIELD>_MASK`: the field's bit mask inside the register.

The main register-field families in this chunk are:

- `DCIO_SOFT_RESET` tail: reset controls for UNIPHY A-G, DSYNC A-G, and power sequencer blocks 0 and 1. The chunk starts after several soft-reset shift definitions, so the full register is split with the previous chunk.
- `DC_GPIO_GENERIC_*`: generic GPIO A-G mask, pull-down disable, receiver mode, output value (`A`), output enable (`EN`), and input/readback (`Y`) fields, plus a generic strength selector.
- `DC_GPIO_DDC1` through `DC_GPIO_DDC5` and `DC_GPIO_DDCVGA`: DDC clock/data mask, pull-down, receive, AUX-pad mode, AUX polarity, hardware pull-down allowance, drive-strength, output value, output enable, and readback fields. These are the low-level pins used for DDC/I2C and AUX pad selection.
- `DC_GPIO_GENLK_*`: genlock/swaplock GPIO mask, pull-down, receive, output, enable, and readback fields for clock/sync/swaplock pins.
- `DC_GPIO_HPD_*`: HPD1-HPD6 mask, pull-down, receive, output, enable, and readback fields, plus HPD disconnect output-enable controls in `DC_GPIO_HPD_EN`.
- `DC_GPIO_PWRSEQ0_EN` and `DC_GPIO_PWRSEQ1_EN`: backlight, panel power, panel reset, Vary-BL, BLON, and OTG-vsync selection/enabling fields for display panel power sequencing.
- `DC_GPIO_PAD_STRENGTH_1` and `DC_GPIO_PAD_STRENGTH_2`: drive-strength selectors for generic, DDC, genlock, swaplock, HPD, and power-sequencer pads.
- `PHY_AUX_CNTL`, `DC_GPIO_AUX_CTRL_0` through `DC_GPIO_AUX_CTRL_5`, `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, and `AUXI2C_PAD_ALL_PWR_OK`: AUX/DDC/HPD pad wake, receiver select, slew, spike filter, bias/resistance tuning, HPD electrical tuning, receiver enable, pull-up enable, AUX polarity/termination/hysteresis, AUX VOD tuning, DDC I2C mode, DDC 1.2 V supply, pad I2C control, and per-AUX/I2C PHY power-good fields.
- `RDPCSTX0_*` and `RDPCSTX1_*`: two repeated RDPCS transmitter instances. Each exposes TX control, clocks, interrupt/error control, PLL update data, CR address/data windows, SRAM power controls, scratch/spare registers, PHY encoding and timing controls, DP-alt-mode handshakes, PHY resets, lane disable/request/ack/data-enable/status fields, MPLLB controls, lane equalization fuse fields, RX load-value readback, DMCU-reserved DP-alt controls, driver-access gating, regulator/capacitor bypass fields, REXT controls, and PHY generic bus fields.
- `DPCSSYS_CR0_DPCSSYS_CR_ADDR` and `DPCSSYS_CR0_DPCSSYS_CR_DATA`: system-level CR address/data field definitions that mirror the RDPCS TX CR access window.
- `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED57`: reserved 32-bit UNIPHY1 macro-control words, each exposed as a full-width reserved field.

The RDPCSTX0 and RDPCSTX1 blocks are intentionally similar. Instance 0 is the canonical name most shared link-encoder field-list macros use for shifts and masks, while per-instance register offsets select the actual transmitter instance.

## Control Flow

This header has no runtime control flow. It participates in compile-time register table construction:

1. `dcn314_resource.c` includes `dpcs_3_1_4_offset.h` and this matching `dpcs_3_1_4_sh_mask.h`.
2. Resource setup and hardware-object headers use token-pasting macros such as `REG`, `REGI`, `SRI`, `LE_SF`, `SF_DDC`, and `SF_HPD` to combine generated offset, shift, and mask names into typed register tables.
3. GPIO, DDC, HPD, AUX, and link-encoder objects receive those tables during DCN 3.1.4 resource construction.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use the stored offsets, shifts, and masks to manipulate MMIO bitfields.

The macros in this chunk do not define sequencing. Reset ordering, DDC/AUX pin mode transitions, HPD polling/interrupt behavior, panel power sequencing, DP/HDMI PHY programming, PLL updates, DP-alt-mode handshakes, and FIFO startup are controlled by driver code and hardware rules outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state fields:

- DCIO reset state for UNIPHY, DSYNC, and power sequencer blocks.
- GPIO state for generic pins, DDC clock/data pins, VGA DDC pins, genlock/swaplock pins, HPD pins, power-sequencer pins, receiver enables, pull-ups, output values, output enables, input readback, pull-down controls, and pad strengths.
- AUX/DDC/HPD electrical state for pad wake, AUX receiver routing, slew/spike filters, compensation/bias/resistance controls, termination, polarity swap, hysteresis, VOD tuning, I2C-mode selection, pad supply enable, and per-pad power-good reporting.
- RDPCSTX transmitter state for soft resets, TX FIFO enables/start/read delay, lane bit/byte order, DP-alt block status, clock enables and clock-on readback, interrupt/error flags and masks, CR access state, SRAM power state, PHY reset/status, HDMI mode, reference range, RTUNE request/ack, SRAM init/load status, lane disable/request/ack/data-enable/clock-ready handshakes, MPLLB fractional/SSC/divider/state controls, transmitter equalization/fuse values, DCO tuning, VSWING, VREF, REXT, and generic debug/control busses.
- Driver-access arbitration fields for DP-alt-mode control blocks, including allow-driver-access and blocked status.

Persistence and side effects are hardware-defined. Many fields are configuration bits that retain values until modeset, power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, interrupt, pending, clear, request/ack, and power-good fields can be latched, self-clearing, write-one-to-clear, read-only, or valid only while the relevant display block is powered and clocked. This generated file only supplies bit locations; it does not encode access semantics.

## Dependencies And Integration Points

This generated file must remain synchronized with AMD's DPCS 3.1.4 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h` supplies the matching register offsets and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c` directly includes this header and constructs DCN 3.1.4 resource tables for link encoders, HPD, DDC, AUX, and related display hardware.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` consumes `RDPCSTX0_*` shift/mask names for link-encoder fields including TX FIFO enables, RDPCS clocks, PHY lane disable/request/ack/reset controls, PHY reset/reference/SRAM status, interrupt masks, CR address/data, MPLLB controls, and DP TX equalization/fuse fields. The DCN 3.1.4 resource file pairs those common masks with per-instance RDPCSTX offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` consumes `DC_GPIO_DDC1_*`, `PHY_AUX_CNTL__AUX*_PAD_RXSEL`, and `DC_GPIO_AUX_CTRL_5__DDC_PAD*_I2CMODE` fields for DDC/I2C pin tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hpd_regs.h` consumes `DC_GPIO_HPD_*` fields for HPD GPIO tables and combines them with HPD interrupt/toggle-filter registers outside this chunk.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/hw_ddc.c` uses DDC mask fields and AUX-pad mode fields to switch pads between I2C/DDC behavior and AUX behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c` and related translator implementations map DDC and HPD register/mask pairs to GPIO pin identities; these are the style of consumers that rely on the generated `DC_GPIO_DDC*` and `DC_GPIO_HPD*` constants being consistent across ASIC generations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmware.h` documents firmware transmitter-adjustment fields that map to RDPCSTX PHY fuse/equalization and VBOOST/VSWING controls represented in this chunk.

Behaviorally, this chunk sits under connector bring-up and link operation: connector GPIO detection, EDID/DDC access, AUX pad routing, HPD sensing, panel power/backlight sequencing, and physical link transmitter programming for DP/HDMI/DP-alt-mode paths.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while only corrupting one hardware field at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, the offset header, firmware assumptions, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the tail of `DCIO_SOFT_RESET`, and the final lines stop inside `RDPCSTX1_RDPCSTX_PHY_CNTL16`. Adjacent chunk reports must be merged before making whole-register or whole-file claims.
- DDC and AUX share pads. Incorrect `AUX_PAD*_MODE`, `AUX*_PAD_RXSEL`, `DDC_PAD*_I2CMODE`, pull-down, pull-up, polarity, or termination masks can break EDID reads, DPCD/AUX traffic, link training, or connector detection only on selected ports.
- HPD fields are connector-visible and often noisy. Wrong mask/readback/enable definitions can cause missed hotplug events, repeated connect/disconnect flapping, or incorrect sense reporting.
- Power-sequencer GPIO fields are panel-sensitive. Incorrect Vary-BL, BLON, panel-power, panel-reset, or OTG-vsync selection masks can affect eDP panel power-up/down timing, backlight behavior, or suspend/resume.
- Pad-strength and AUX electrical tuning fields affect signal integrity. Bad values or bit definitions can produce marginal failures that depend on cable, sink, voltage rail, board routing, temperature, or link rate.
- RDPCSTX reset, clock, FIFO, request/ack, and lane-enable fields are sequencing-sensitive. Incorrect masks can create hangs waiting for clock-on or ack bits, TX FIFO underflow/overflow, blank displays, or lane-count-specific failures.
- RDPCSTX interrupt-control names include status, clear, and mask fields in one register. Confusing `*_MASK` field names with generated `_MASK` suffixes or writing the wrong clear bit can hide FIFO/reg errors or leave errors latched.
- RDPCSTX PHY fuse/equalization fields map to firmware transmitter settings. Wrong masks for `EQ_MAIN`, `EQ_PRE`, `EQ_POST`, MPLLB tuning, DCO range/fine tune, VSWING, VREF, or REXT can cause link-training failures or intermittent high-rate DP/HDMI issues.
- Instance repetition is copy-sensitive. RDPCSTX0 and RDPCSTX1 should be structurally aligned where hardware intends; an instance-specific generator error can affect only one physical transmitter.
- The reserved UNIPHY1 macro-control fields expose full-width registers. Treating reserved fields as safe software controls would be risky unless explicitly required by silicon documentation or firmware handoff rules.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build DCN 3.1.4 AMDGPU display support. Missing or renamed macros should surface in `dcn314_resource.c`, `dcn31_dio_link_encoder.h`, `ddc_regs.h`, `hpd_regs.h`, and GPIO translator users.
- Mechanically compare this range against the authoritative DPCS 3.1.4 register-field database and ensure every expected `_MASK` has a paired `__SHIFT`, allowing fields split by chunk boundaries.
- Cross-check this shift/mask range against `dpcs_3_1_4_offset.h` so every register family in the chunk has matching offsets/base indices.
- Run static repetition checks across `DC_GPIO_DDC1-5`, `DC_GPIO_DDCVGA`, `DC_GPIO_HPD1-6`, `AUX1-6` pad fields, and `RDPCSTX0/1` to catch unintended instance drift while allowing intentional per-instance or VGA differences.
- Exercise EDID reads and DDC transactions on every connector. Watch for stuck pull-downs, wrong pad mode, bad DDC clock/data direction, failed I2C-mode selection, or port-specific failures.
- Exercise DP AUX/DPCD reads and link training on every AUX-capable connector, including unplugged and timeout paths. Expected signals are correct AUX pad routing, stable power-good status, and no cross-connector aliasing.
- Exercise HPD connect/disconnect and HPD sense/readback across all exposed connectors. Expected signals are stable sense bits, correct GPIO mapping, and no repeated interrupts from bad mask/readback definitions.
- Validate panel power and backlight sequencing on internal-panel platforms, including boot, modeset, blank/unblank, suspend/resume, and fast display switching.
- Exercise DP/HDMI link bring-up across lane counts and link rates. Watch for TX FIFO errors, stuck clock-on/status bits, request/ack timeout, lane-disable mistakes, and link-training regressions.
- Compare RDPCSTX PHY/equalization programming against AtomBIOS/firmware transmitter settings and hardware register dumps, especially for high-rate DP, HDMI FRL/TMDS-adjacent paths when applicable, and marginal cables/sinks.
- Test DP-alt-mode or USB-C display paths where present, focusing on `DPALT_DISABLE`, `DPALT_DP4`, driver-access gating, and DMCU-reserved DP-alt handshake fields.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DCIO_SOFT_RESET`, including shift definitions before `DSYNCG_SOFT_RESET`. This chunk covers the corresponding soft-reset masks and then the DCIO GPIO/pad and RDPCSTX0/1 register groups. The next chunk should continue `RDPCSTX1_RDPCSTX_PHY_CNTL16` and the remaining DPCS register metadata. The final per-file research document should reconcile these boundaries before describing all DPCS 3.1.4 GPIO, AUX, HPD, UNIPHY, or RDPCSTX behavior.

### subset-b-002281: lines 53596-55194

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h lines 53596-55194

## Scope

This chunk is the final segment of the generated AMD DPCS 3.1.4 shift/mask header. It covers line 53596 through the closing `#endif` at line 55194 and defines 1,313 preprocessor constants: 655 `__SHIFT` macros and 658 `_MASK` macros. The uneven count is expected for this chunk boundary because the range starts in the middle of `RDPCSTX1_RDPCSTX_PHY_CNTL16`, where three mask definitions are present but the matching shifts were defined before line 53596.

The content is declarative only. It exports bitfield locations for memory-mapped DPCS/RDPCS, UNIPHY, CR, and panel power sequencer registers; it contains no C functions, structs, runtime storage, or branching logic.

## Purpose

The header provides symbolic field positions for AMDGPU display driver code that programs ASIC display PHY and panel-power hardware. Each register field is represented by a bit shift and mask so consumer code can compose read-modify-write operations without embedding raw bit constants. In this range, the exported constants cover:

- The tail of RDPCS transmitter instance 1 generic bus, byte-order, and PLL override fields.
- CR bridge address/data fields for RDPCS transmitter instances 1 and 2.
- RDPCSPIPE0/1 DP Alt Mode PHY disable/status bits.
- UNIPHY2, UNIPHY3, and UNIPHY4 reserved macro-control windows.
- A full RDPCSTX2 transmitter/PHY register surface, including clocking, FIFO, interrupt, SRAM, DP Alt Mode, PLL, fuse, and per-lane PHY controls.
- PWRSEQ0 and PWRSEQ1 GPIO, panel power sequencing, backlight PWM, timing divider, lock, and spare-register fields.

## Exported API Surface

There are no callable APIs or local types. The public interface is the macro set consumed by AMD display code after including this generated ASIC register header.

Important macro families:

- `RDPCSTX1_RDPCSTX_PHY_CNTL16`, `RDPCSTX1_RDPCSTX_PHY_CNTL17`, `RDPCSTX1_RDPCS_CNTL3`, and `RDPCSTX1_RDPCS_TX_PLL_UPDATE_*_OVRRD`: tail fields for transmitter instance 1 generic PHY buses, per-lane byte order changes, and PLL update override address/data.
- `DPCSSYS_CR1_DPCSSYS_CR_ADDR` / `DATA` and `DPCSSYS_CR2_DPCSSYS_CR_ADDR` / `DATA`: 16-bit CR access fields used to address and transfer RDPCS transmitter CR data.
- `RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` and `RDPCSPIPE1_RDPCSPIPE_PHY_CNTL6`: DPALT DP4 mode, disable request, and disable acknowledgement fields for pipe-level PHY control.
- `DCIO_UNIPHY{2,3,4}_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`: full-width reserved control registers, each exposing a 32-bit reserved field.
- `RDPCSTX2_RDPCSTX_*` and `RDPCSTX2_RDPCS_*`: the main instance-2 RDPCS transmitter and PHY mask surface.
- `PWRSEQ0_*` and `PWRSEQ1_*`: parallel panel power sequencer and backlight PWM fields for two sequencer instances.

## Register Areas Covered

The `RDPCSTX2` control block defines transmitter reset, common-mode override, per-lane bit and byte ordering, interrupt mask, PLL update request/pending, request/ack enforcement, FIFO enables, FIFO start/delay controls, register-block gating, DPALT block status, clock enables/status, SRAM clocking, OCLACLK clocking, FIFO and DPALT interrupt status/clear/mask bits, SRAM memory power controls, full-width scratch/spare registers, CR convert FIFO status, and beacon/data-enable timing delays.

The `RDPCSTX2` PHY block defines reset and APB reset controls, test powerdown, HDMI mode, reference-range selection, RTUNE request/ack, CR muxing, reference-clock detection, SRAM init/load status, PCS/PMA/analog power-gating and stable status, lane loopback controls, per-lane DP TX reset/disable/clock-ready/data-enable/request/ack fields, termination/inversion/EQ bypass/high-performance protection, lane low-power detect/rate/width/DETRX fields, lane power states, MPLL enables, DPALT DP4/disable/ack, DP reference clock enable/request, MPLLB fractional/SSC/divider programming fields, fuse-derived EQ and PLL calibration fields, RX reference/VCO load values, generic PHY input/output bus fields, and byte-order controls.

The `RDPCSTX2` DP Alt Mode and DMCU-facing fields define `ALLOW_DRIVER_ACCESS`, `DRIVER_ACCESS_BLOCKED`, DPALT control spares, DMCU disable/block controls, forced TX clock disable, and DMCU-reserved mirrors of selected PHY lane request/ack and power-state fields. These names show the register surface is shared between normal driver control and firmware/Type-C DP Alt Mode coordination.

The `PWRSEQ0` and `PWRSEQ1` blocks are structurally identical. They define GPIO enable/control/mask/A-Y fields for `VARY_BL`, `DIGON`, and `BLON`; panel sequencer enable, target state, override, polarity, and state readback fields; power-up/power-down delay fields; reference dividers for panel sequencing and backlight PWM; PWM active count, fractional enable, period, bit count, frame-start update behavior, double-buffer lock/update/readback controls, and full-width spare registers.

## Control Flow And State Behavior

This header has no local control flow. Runtime behavior emerges when AMDGPU display code uses the masks with register read/write helpers.

The field names imply several hardware state machines and handshakes:

- RDPCS reset/bring-up: soft reset, PHY reset, SRAM reset, clock enable, clock-on status, SRAM init/load status, and power-gate stable fields must be sequenced by consumers during link initialization and resume.
- Link and lane activation: per-lane FIFO enables, aggregate FIFO start, data enable, lane request/ack, clock-ready, DETRX, lane rate/width, and byte/bit ordering fields define the programmable transmit datapath.
- PLL programming: PLL update request/pending, CR address/data, override address/data, MPLLB fractional numerator/denominator/remainder, SSC, divider, and force/calibration fields support staged link-rate configuration.
- Interrupt/error handling: FIFO overflow, DPALT toggles, per-lane FIFO errors, disabled-FIFO status, clear bits, and interrupt masks provide status and recovery points.
- DP Alt Mode ownership: pipe-level DPALT disable/ack, RDPCS DPALT block status, driver access gates, DMCU reserved mirrors, and forced clock-disable fields model coordination between the host driver, display firmware, and Type-C/DPALT control paths.
- Panel sequencing: PWRSEQ target state, DONE/state readback, DIGON/SYNCEN/BLON outputs, delay fields, GPIO polarity/drive controls, and PWM frame-start locking support ordered panel power and backlight transitions.

No software persistence is implemented in this file. Hardware register contents persist according to ASIC reset and power domains. The `SCRATCH`, `SPARE`, `PWRSEQ_SPARE`, UNIPHY reserved, and PWM lock/update fields expose storage or latch semantics, but this chunk does not define any higher-level policy for their contents.

## Dependencies And Integration Points

The only syntactic dependency is the C preprocessor. The masks are intended to be included with companion generated DPCS 3.1.4 address headers and used by AMDGPU/DC register helper macros that take a register, field shift, and field mask.

Integration points visible from the naming:

- AMDGPU DRM display code under `drivers/gpu/drm/amd`, especially DC/DPCS link encoder, PHY, clock, and panel-power code.
- DPCS 3.1.4 generated register address headers that provide offsets for the field masks in this file.
- DisplayPort, HDMI, USB-C/DP Alt Mode, and DMCU firmware paths, reflected by `DPALT`, `DMCU`, `HDMIMODE`, `MPLLB`, and per-lane DP TX fields.
- Panel/backlight control paths that program power-sequence timings, GPIO output enables, BL PWM period/duty, and frame-start synchronized updates.
- Interrupt handlers and diagnostic paths that inspect FIFO, DPALT, register FIFO, and lane error/status fields.

## Risks

- Generated-header drift is the primary risk. An incorrect shift or mask can silently update adjacent hardware bits during read-modify-write operations.
- The chunk contains many parallel per-lane and per-instance definitions. Copy-generation mistakes in lane offsets, masks, or instance prefixes can affect only one lane or one sequencer and be hard to catch in build tests.
- Some fields are status/readback-only while adjacent fields are writable controls, such as request/pending, enable/clock-on, request/ack, stable status, interrupt status/clear/mask, and panel state/DONE bits. Consumers must preserve access semantics from the hardware spec.
- DPALT and DMCU-reserved fields indicate shared ownership. Writing them without checking access/block status can conflict with firmware or Type-C state transitions.
- Full-width reserved, scratch, spare, and PLL update-data masks allow broad writes. Consumer code needs hardware-specific value validation and should avoid treating reserved windows as general storage.
- This range closes the header with `#endif`; malformed edits here can break all users of the generated file.

## Test Signals

Useful validation signals are build-time and hardware-integration oriented:

- Compile/preprocess AMDGPU display code that includes `dpcs_3_1_4_sh_mask.h`.
- Static checks that complete register groups have matching `__SHIFT` and `_MASK` definitions; for this chunk as sliced, the expected count is 655 shifts and 658 masks because of the partial `RDPCSTX1_RDPCSTX_PHY_CNTL16` boundary.
- Generated-register consistency checks comparing this header against the DPCS 3.1.4 register database.
- Grep/compile checks for consumers of `RDPCSTX2`, `PWRSEQ0`, `PWRSEQ1`, `DCIO_UNIPHY2`, `DCIO_UNIPHY3`, and `DCIO_UNIPHY4` macros to catch missing or renamed fields.
- Runtime display tests on ASICs using DPCS 3.1.4: DP and HDMI link training, hotplug, USB-C DP Alt Mode attach/detach, suspend/resume, panel power on/off, backlight PWM changes, and interrupt/error recovery.
- Register readback during bring-up to confirm reset, clock-on, FIFO, PLL pending, lane ack, DPALT blocked/ack, power-gate stable, panel DONE/state, and PWM update-pending transitions.

## Chunk Notes For Merge

This chunk is source-tree aligned and intentionally documents only lines 53596-55194 of `dpcs_3_1_4_sh_mask.h`. Earlier chunks should cover the beginning of `RDPCSTX1_RDPCSTX_PHY_CNTL16` and lower-numbered register blocks. The later per-file merge should describe the whole file as a generated ASIC register bitfield map, not handwritten driver logic, and should preserve the repeated instance pattern across RDPCSTX, UNIPHY, RDPCSPIPE, CR, and PWRSEQ blocks.
