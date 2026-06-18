# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 23896-26282

## Scope And Purpose

This chunk is part of AMD's generated DPCS 4.2.0 register shift/mask header. It contains preprocessor constants for hardware bitfields, not executable driver logic. Consumers pair these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` definitions with `dpcs_4_2_0_offset.h` register offsets and AMD display register helpers to access memory-mapped DisplayPort/PHY control registers on the relevant DCN 3.1-era ASICs.

The requested range contains 2,122 `#define` lines: 1,059 shift macros and 1,063 mask macros, plus 263 register/comment markers. The range starts inside `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT` after several earlier shift lines, and ends after the complete `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0` register. The next register, `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_1`, begins immediately after the chunk.

The substantive hardware covered here is the DPCS raw-lane control surface for CR0 and the beginning of the CR1 supervisor/lane register block:

- CR0 PCS/PMA lane cross-interface overrides, status, test/ATE controls, equalization, termination, loopback, RX/TX request/reset/data-enable, and lane-number fields.
- CR0 raw-lane FSM controls, fast-calibration/adaptation flags, lock/status monitors, on-chip logic analyzer selectors, and common-calibration status.
- CR0 raw-lane IRQ status, clear, and mask registers for RX/TX reset/request/rate/pstate/adaptation, phase calibration, transceiver mode, loopback, and DCC on-demand events.
- CR0 TX/RX control registers for lane FSM enablement, clocks, data-enable timing, loss-of-signal masking, continuous adaptation/offcan status, and UPCS observation.
- CR1 supervisor digital fields for ID code, reference clocks, MPLLA/MPLLB overrides, spread-spectrum configuration, fractional-N PLL programming, charge-pump controls, prescaler, RTUNE, power-up timing, and MPLL power-controller state.
- CR1 supervisor analog fields for bandgap, prescaler, RTUNE, MPLLA/MPLLB analog test/override/control, PMIX, voltage/reference levels, and analog status.
- The first CR1 lane0 ASIC override registers: lane loopback/enable/ACJTAG and the complete TX override input 0 surface for request, pstate, rate, width, MPLLB selection, and data enable.

## Important Constants And Register Areas

`DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_*` registers define the PCS side of the raw lane interface. The RX group covers rate, width, pstate, low-power detect, override enables, AFE/DFE adaptation enablement, RX-to-TX parallel loopback, RX data enable, reset/request overrides, loss-of-signal threshold, VCO/ref load override values, equalizer settings, adaptation acknowledgement/FOM readback, TX pre/main/post direction fields, and lane number. The range also includes ATE-specific RX/TX override registers with similar controls plus beacon, async, VBOOST, IBOOST, DETRX, master MPLL state, and loopback bits. The chunk starts with only the tail of `TX_OVRD_OUT`, so whole-register research for that register needs the previous chunk.

`DPCSSYS_CR0_RAWLANEX_DIG_FSM_*` registers expose low-level lane sequencer behavior. They include an override jump address and command/start/break controls, memory address and state monitors, fast path enables for startup, RX adaptation, AFE/DFE calibration, bypass/reference/IQ calibration, supervisor and TX common mode/RX detect, RX power-up/VCO wait/VCO calibration, continuous calibration/adaptation/data/phase/AFE paths, calibration status for MPLL/RCAL, register/memory lock bits, TX DCC flags/status, TX EQ update status, and OCLA selectors. These fields are diagnostic and sequencing-sensitive because they can alter or observe the PHY micro-sequencer directly.

`DPCSSYS_CR0_RAWLANEX_DIG_IRQ_CTL_*` registers define one-bit status, clear, and mask fields for lane events. Covered IRQs include RX reset/request/rate/pstate/adapt request/adapt disable, TX reset/request, lane transceiver mode, RX phase-2 calibration request/disable, RX-to-TX serial loopback enable, and DCC on-demand. `IRQ_MASK` and `IRQ_MASK_2` pack enable/mask bits across related RX/TX interrupt sources; corresponding `*_IRQ_CLR` fields are likely write-one-to-clear style hardware controls and should be handled through established IRQ paths.

`DPCSSYS_CR0_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` registers bridge PCS control to PMA/MPHY and lane TX/RX controllers. They include MPLLA/MPLLB lane selection, supervisor state override/readback, TX/RX request/reset/beacon/async/data-enable overrides, serial/parallel loopback, RTUNE request/acknowledge, MPHY PWM/termination/async controls, RX IQ phase adjustment mapping, TX FSM timing and clock selection, DCC continuous status, RX FSM enable/rate-change policy, LOS mask counters, RX data-enable override counters, and adaptation/offcan continuous status.

The `addressBlock: dpcssys_cr1_rdpcstxcrind` marker introduces CR1 supervisor registers. `DPCSSYS_CR1_SUP_DIG_*` covers ID code, reference clock override, MPLLA/MPLLB div/HDMI clocks, PLL enable/divider/V2I/standby/frequency/calibration/fractional-N/clock-sync overrides, multiplier and fractional-N quotient/remainder/denominator fields, spread-spectrum peak/step-size fields, CP and gear-shift CP overrides, prescaler and DCO tuning, supervisor RTUNE handshake, PHY reset/reference clock/test controls, bandgap enable, and ASIC input readback mirrors.

`DPCSSYS_CR1_SUP_ANA_*` and `DPCSSYS_CR1_SUP_DIG_ANA_*` describe analog supervisor controls and readbacks. The fields cover prescaler analog test and vreg controls, RTUNE modes and values, bandgap trims and fast-start behavior, switch/power measurement selects, MPLLA/MPLLB analog override, ATB measurement selectors, charge-pump/filter/ring/VCO/lock/SPO/DLL controls, PMIX selection/enables, analog DAC readback, RTUNE comparator and reference clock detector status, and bandgap/async reset/reference vreg override outputs.

`DPCSSYS_CR1_SUP_DIG_MPLLA_MPLL_PWR_CTL_*` and the parallel MPLLB group define MPLL power-controller override/status/timing fields. They include override select, feedback and pixel clock enables, fast power-up/lock, DTB select, div10 enable, FSM state, active lane sides, output/fbclk/cal/reset/analog enables, lock status, DAC range/output, lock/stable/gearsift/preset/PCLK enable/disable/power-down timers, calibration override, and SSC spread type. MPLLA and MPLLB layouts are intentionally parallel and should remain consistent.

The chunk ends with `DPCSSYS_CR1_LANE0_DIG_ASIC_LANE_OVRD_IN` and `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`. These fields provide lane0 ASIC-side serial/parallel loopback, enable, RX ACJTAG enable, and TX request/pstate/rate/width/MPLLB/data-enable override controls. Later lane0 TX fields continue in the next chunk.

## APIs, Types, And Functions

There are no functions, structs, enums, or inline helpers in this source range. The public interface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT` gives the bit position for packing or extracting a field.
- `REGISTER__FIELD_MASK` gives the already-positioned mask for that field.
- Register names encode the hardware block and instance, such as `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_RX_OVRD_IN`, `DPCSSYS_CR1_SUP_DIG_MPLLA_OVRD_IN_0`, or `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`.

The matching address constants live in `dpcs_4_2_0_offset.h`, for example the same CR0 raw-lane PCS/PMA/FSM/IRQ registers are listed around the `0xe000` indirect-register range and CR1 supervisor registers begin at small CR1-relative offsets. The shift/mask values are only meaningful with those matching offsets and this ASIC register database.

In-tree integration is visible in `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes `dpcs/dpcs_4_2_0_offset.h` and `dpcs/dpcs_4_2_0_sh_mask.h` before including `reg_helper.h`. Higher-level DC code generally reaches these fields through AMD register helper macros and resource tables, not through standalone functions in this header.

Semantic enum values are not defined here. Values for lane rates, widths, pstate encodings, PLL dividers, spread-spectrum modes, RTUNE modes, IRQ mask polarity, and test/ATE selections must come from hardware documentation, generated enum data, or the caller code that owns the programming sequence.

## Control Flow And Runtime Behavior

This header has no local control flow. Runtime behavior occurs when AMD display/PHY code writes or reads DPCS registers during link bring-up, lane training, PHY calibration, test/ATE flows, power management, interrupt handling, debug capture, or low-level diagnostics.

The implied CR0 lane-control flow starts with PCS/PMA request, reset, rate, width, pstate, MPLL selection, data enable, and loopback controls. RX-side setup can then configure adaptation enables, LOS thresholds, VCO/ref load values, equalization, termination, and data-enable timing. TX-side setup can select clocks, beacon/async behavior, DCC status, and TX request/reset/data-enable controls. Status and acknowledgement fields report whether hardware accepted the PCS/PMA handshakes.

The FSM and fast-calibration registers represent another control plane. They can bypass or accelerate the normal lane micro-sequencer for startup, RX adaptation, calibration, VCO wait/calibration, continuous adaptation, and supervisor/TX common-mode sequences. The `FSM_OVRD_CTL` jump/start/break fields are especially invasive because they can redirect or halt sequencer behavior.

IRQ control follows the usual status/clear/mask pattern. Hardware reports one-bit event status registers, software clears latched conditions through matching `*_IRQ_CLR` fields, and mask registers control which event sources are visible. The macros do not specify edge/level semantics or write-one-to-clear details; those are established by the interrupt service code and hardware spec.

The CR1 supervisor flow programs shared PHY resources: reference clock selection, MPLLA/MPLLB dividers and fractional-N values, spread-spectrum peak/step sizes, charge-pump settings, prescaler levels, RTUNE calibration values, bandgap and analog enablement, and MPLL power-controller timers. Status fields then expose FSM state, lock, clock enables, RTUNE results, and analog comparator/clock detector outcomes.

The lane0 fields at the end are the start of per-lane CR1 programming. They allow instance-specific ASIC-side lane override and TX state selection after the shared supervisor and MPLL resources are configured.

## State And Persistence

The file itself stores no mutable state. It defines how software reaches persistent hardware state in DPCS registers and PHY analog/digital control blocks.

Hardware state represented here includes lane RX/TX request/reset/data-enable bits, rate/width/pstate/LPD selections, loopback controls, adaptation and calibration enables, equalizer and termination settings, VCO/ref load values, IRQ latches/masks, FSM override state, OCLA capture enables, MPLLA/MPLLB configuration, spread-spectrum values, fractional-N PLL values, prescaler/RTUNE/bandgap state, analog test/measurement selects, MPLL power-controller timers, and lane0 TX override values.

Several fields are readback or status oriented rather than durable configuration: acknowledgement bits, calibration done/init bits, FSM state, command ready, ALU flags, DCC status, continuous adaptation/offcan status, RTUNE status, analog comparator and ref-clock detector results, MPLL lock, and active clock/output enables. Callers must distinguish these from writable override fields when building register update sequences.

State persistence is hardware-lifetime scoped. Register values may reset across PHY reset, GPU reset, suspend/resume, link disable, or power-gated PHY domains. PLL, RTUNE, bandgap, and analog fields are particularly sensitive to power transitions because they describe physical clocking and calibration state, not just software-visible configuration.

## Dependencies And Integration Points

This chunk depends on the matching generated register offset header `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h`. Cross-version DPCS headers such as `dpcs_4_2_2_*`, `dpcs_4_2_3_*`, or `dpcs_3_1_4_*` contain similar-looking names but must not be substituted without validating the ASIC register database and offsets.

Primary integration points are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which includes the DPCS 4.2.0 offset and shift/mask headers for DCN 3.1 resource construction.
- The AMD display register helper layer included through `reg_helper.h`, which provides the expected bitfield update/read idioms around generated mask/shift data.
- Link encoder, PHY, HPD/link training, power-management, debug, and interrupt paths that program DPCS indirect registers using the generated offset and mask namespaces.
- Neighboring DPCS generated headers for other revisions, which are useful for structural comparison but not authoritative for this ASIC revision.

The API boundary is the generated register database. Handwritten arithmetic against these constants can work mechanically, but it bypasses the normal register helper patterns and increases the chance of using the wrong base, indirect address space, or field encoding.

## Risks And Edge Cases

Generated-header drift is the main risk. A wrong mask or shift compiles cleanly but can write the wrong physical field, causing failures such as link training instability, incorrect lane width/rate/pstate selection, stuck reset/request handshakes, broken RX adaptation, invalid equalization or termination, bad PLL programming, missed or uncleared interrupts, or PHY power/clock sequencing faults.

Chunk boundaries are incomplete. The range begins in the middle of `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT`, so whole-register validation for that register requires the previous chunk. The range ends cleanly after `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`, while the next lane0 TX override register begins after line 26282.

Many fields are sequencing-sensitive. PLL fractional-N, spread-spectrum, charge-pump, power-controller timer, RTUNE, bandgap, reset, clock-enable, calibration, and FSM override fields should be written only by code that owns the PHY bring-up or diagnostic sequence. Random read-modify-write operations can disturb active links.

Interrupt clear fields are side-effecting. `*_IRQ_CLR` bits should not be treated like ordinary persistent configuration, and mask polarity must be confirmed from the IRQ code or hardware spec before changing behavior.

Repeated MPLLA/MPLLB structures are a validation signal. The A and B PLL blocks should remain parallel for most override, ASIC input, analog, and power-controller fields. Any unexpected asymmetry between the two could be a generator issue or a real hardware distinction that needs confirmation.

The `L` suffix on masks, including high-bit masks elsewhere in the generated header, means consumers should keep using the driver's unsigned register helper types and avoid signed arithmetic assumptions around raw constants.

## Test And Validation Signals

Compile coverage should include DCN 3.1 display resource construction and any link/PHY code that includes `dpcs_4_2_0_sh_mask.h`. Missing or renamed macros are usually caught at build time; incorrect numeric values require generated-data comparison or hardware validation.

Useful static checks include comparing this range against the authoritative DPCS 4.2.0 register database, verifying each complete register has non-overlapping masks whose positions match their shift values, diffing MPLLA and MPLLB repeated groups for intentional symmetry, and comparing DPCS 4.2.0 against adjacent generated revisions only as a review aid.

Runtime signals include successful display link bring-up on DCN 3.1 hardware, stable lane training across supported rates and widths, correct suspend/resume and hotplug behavior, no stuck PHY reset/request/ack handshakes, stable RX adaptation and LOS handling, valid MPLL lock and RTUNE status, reliable interrupt delivery and clearing for RX/TX lane events, and absence of link flaps or display artifacts when PLL power management and clock gating are exercised.

## Research Notes

This is source-tree-aligned chunk research only. It intentionally writes only `Docs/researches/chunks/subset-b-002298_research.md`. Whole-file research for `dpcs_4_2_0_sh_mask.h` must merge adjacent chunks to complete the leading `DPCSSYS_CR0_RAWLANEX_DIG_PCS_XF_TX_OVRD_OUT` register and continue the CR1 lane0 TX override block after `DPCSSYS_CR1_LANE0_DIG_ASIC_TX_OVRD_IN_0`.
