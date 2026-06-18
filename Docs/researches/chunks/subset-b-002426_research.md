# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 97292-99808

## Purpose

This chunk is a generated AMD DPCS 4.2.3 shift/mask header slice. It contains C preprocessor constants for register-field bit positions and masks; it has no executable driver logic. AMDGPU display code combines these constants with companion DPCS offset/index headers and register helpers to program or decode low-level Display Core PHY, PCS/PMA, PLL, clock, power, calibration, interrupt, and debug fields without open-coded bit numbers.

The requested range contains 2,517 lines, 2,130 `#define` statements, 1,622 `__SHIFT` macros, 528 `_MASK` macros, and 385 generated register/address-block comments. It starts at the complete `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED2` mask line set, proceeds through CR4 lane analog RX and raw-lane PCS/PMA/FSM/IRQ/control definitions, then enters the `c20_phy_cr0_rdpcspipecrind` address block with CR0 supervisor and raw-common PHY definitions. It ends after `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0__FW_CLK_ACK__SHIFT`, with the following `RESERVED_15_6` shift and subsequent AON supervisor output fields left to the next chunk.

Although this path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, memory allocations, locks, direct MMIO operations, or exported symbols in this range. The interface is entirely the generated macro convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit index for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the field when the generator emits one.
- `//DPCSSYS_*` and `//C20_PHY_*` comments: generated register boundaries that correspond to offset/index definitions in companion DPCS 4.2.3 headers.
- `// addressBlock: c20_phy_cr0_rdpcspipecrind`: boundary where the chunk moves from CR4 DPCS/raw-lane definitions into C20 PHY CR0 indirect pipe/common register definitions.

The main macro families in this chunk are:

- `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED*` and `DPCSSYS_CR4_LANEX_ANA_RX_*`: reserved/NC TX fields plus analog RX clock/CDR/deserializer, slicer, power, squelch, calibration mux, analog-test-bus measurement/force, and reserved fields for CR4 lane X.
- `DPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_*`: raw-lane PCS crossing override/input/output/status fields for TX/RX pstate, low-power detect, rate, width, MPLL selection/enables, reset/request/detect-RX, TX beacon, vboost/iboost, async enable, RX data-enable, adaptation requests/acks, RX equalization, termination control, loopback, ATE, PH2 calibration, lane number, and debug/status mirrors.
- `DPCSSYS_CR4_RAWLANEX_DIG_FSM_*`: finite-state-machine override, memory/status monitor, fast RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration controls, supervisor/TX common-mode/RX-detect/RX power-up/VCO wait/VCO calibration controls, common calibration status, continuous calibration/adaptation controls, CR lock, DCC flags/status, OCLA, TX EQ update, RCAL status, and RX IQ phase offset fields.
- `DPCSSYS_CR4_RAWLANEX_DIG_IRQ_CTL_*`: lane interrupt status, clear, and mask fields for reset, request, rate, pstate, adaptation request/disable, lane transceiver mode, PH2 calibration request/disable, RX-to-TX serial loopback, DCC on-demand, and TX reset/request events.
- `DPCSSYS_CR4_RAWLANEX_DIG_PMA_XF_*`: PMA crossing override/input/output fields for lane and supervisor handshakes, TX/RX PMA control and status, RTUNE, MPHY overrides, and RX adaptation outputs.
- `DPCSSYS_CR4_RAWLANEX_DIG_TX_CTL_*` and `DPCSSYS_CR4_RAWLANEX_DIG_RX_CTL_*`: TX/RX FSM and clock controls, DCC continuous status, loss-of-signal masking, RX data-enable override, offset-cancel/adaptation continuous status, OCLA, and UPCS OCLA fields.
- `C20_PHY_CR0_SUP_DIG_*`: CR0 supervisor digital definitions for ID code, reference-clock overrides, MPLLA/MPLLB divider/HDMI and PLL overrides, SSC parameters, supervisor input/output override paths, ASIC input/output mirrors, RTUNE debug/config/status/set/stat values, BG/ref power-up timing, MPLLA/MPLLB power-control calibration/status/timers, SSC configuration, analog-crossing status/override outputs, and supervisor/MPLL analog CREG fields.
- `C20_PHY_CR0_RAWCMN_DIG_*`: raw-common digital control, clock gating, MPLL configuration/input, firmware/static status, async/recal/frac-update controls, config-master version, CTLE offset context, CREG access, context restore/select, debug, supervisor context configuration, MPLLA/MPLLB context configuration, AON SRAM power-gate/firmware-stop controls, MPLLA/MPLLB tune banks/status/recal, AON power-gate overrides, and AON supervisor input overrides.

Common field-name patterns encode the intended hardware semantics: `OVRD`, `OVRD_EN`, `OVRD_VAL`, `ASIC_IN`, `PMA_IN`, `PCS_IN`, `PCS_OUT`, `PMA_OUT`, `REQ`, `ACK`, `IRQ`, `IRQ_CLR`, `MASK`, `PSTATE`, `RATE`, `WIDTH`, `RESET`, `DATA_EN`, `CAL`, `ADAPT`, `DFE`, `AFE`, `CDR`, `PH2`, `MPLL`, `MPLLA`, `MPLLB`, `SSC`, `RTUNE`, `OCLA`, `ATB`, `LB`, `TERM`, `CREG`, `CNTX`, `AON`, `TUNE`, `PG`, and `RESERVED`/`NC`.

## Control Flow

This header has no runtime control flow. It affects driver behavior only after inclusion and macro expansion:

1. A consumer selects a DPCS 4.2.3 register offset or indirect CR index from a matching generated offset header.
2. The consumer uses the shift/mask macro pair, or a shift-only field when that is the generated form, to insert, clear, read, or test specific register bits.
3. AMDGPU register helpers perform the MMIO or indexed DPCS CR read/modify/write, poll, dump, or decode operation.
4. Hardware and firmware state machines perform the actual lane/PHY sequencing.

The sequencing implied by the fields is external to this file. Examples include releasing or forcing TX/RX lane overrides, initiating or observing reset/request/adaptation handshakes, clearing or masking lane IRQs, programming MPLLA/MPLLB and SSC context values, waiting for PLL tune/calibration completion, updating fractional PLL settings, reading RTUNE/termination status, and preserving ownership between firmware, hardware state machines, and driver override paths.

## State And Persistence Behavior

The macros are stateless compile-time constants. They describe hardware-visible state but do not store it. Register values live in DPCS/PHY hardware and may be volatile, latched, read-only, write-one-to-clear, self-clearing, retained across selected low-power states, or reset by power/clock domains depending on the register.

Hardware state named by this chunk includes:

- CR4 analog lane RX/TX reserved state, clock/CDR/deserializer controls, RX slicer and power controls, squelch, RX calibration muxes, ATB measurement controls, and forced analog-test values.
- CR4 raw-lane PCS/PMA state for TX/RX request/reset/rate/width/pstate/data-enable, TX beacon/boost, RX adaptation, RX EQ, PH2 calibration, lane mode, loopback, ATE, termination, and PCS/PMA mirror paths.
- CR4 raw-lane FSM/debug/interrupt state for fast startup/calibration/adaptation stages, continuous calibration/adaptation, CR lock, DCC, OCLA, TX EQ update, RCAL, IQ phase offset, lane IRQ status/clear/mask, and TX/RX event reporting.
- CR0 supervisor digital state for reference clocks, MPLLA/MPLLB clock/divider/HDMI/SSC/charge-pump/frac settings, supervisor overrides, ASIC mirrors, RTUNE state, BG/ref timing, MPLL power-control timers/status, and analog-crossing override outputs.
- CR0 raw-common state for clock gating, firmware/static configuration status, MPLL async/recal bank controls, fractional update triggers, context restore/selection, CTLE offset contexts, CREG access, MPLLA/MPLLB context configuration, AON tune banks, AON recal/tune status, SRAM power-gate behavior, power-gate overrides, and AON supervisor input signals.

Persistence is hardware-defined. Values may be reset or rewritten during modeset, link retraining, hotplug recovery, suspend/resume, GPU reset, display-engine reset, PHY power-gating, firmware ownership transitions, or state-machine recalibration. This header does not define reset values, legal enumerations, access widths, polling timeouts, ordering rules, lock ownership, or firmware arbitration.

## Dependencies And Integration Points

This generated header must stay synchronized with the DPCS 4.2.3 register database, the matching DPCS 4.2.3 offset header, and AMDGPU Display Core code that token-pastes register, field, mask, and shift identifiers.

Integration points include:

- Companion generated headers under `drivers/gpu/drm/amd/include/asic_reg/dpcs/`, especially `dpcs_4_2_3_offset.h` and adjacent chunks of this same shift/mask file.
- Similar generated headers for neighboring DPCS/DCN generations, which expose repeated register families but may differ in naming, casing, emitted masks, or field layout.
- AMDGPU display link, PHY, encoder, and resource code that programs DisplayPort/HDMI lane operation, link training, PHY power sequencing, PLL setup, spread-spectrum clocks, RTUNE, and ASIC-specific register tables.
- DPCS CR access helpers that perform indirect indexed CR operations and read/modify/write using these field layouts.
- Hardware/firmware lane and supervisor state machines that own PCS/PMA handshakes, calibration/adaptation, MPLLA/MPLLB operation, AON power/tune state, RTUNE, bandgap/reference power, and interrupt/status reporting.
- Diagnostic and validation paths for ATE, OCLA, ATB measurement, raw-lane dumps, RX adaptation/PH2 status, DCC status, IRQ observation, PLL/SSC/tune readback, and CREG/context debug.

The range crosses major generated domains: CR4 lane analog/register-crossing definitions first, then CR0 C20 PHY supervisor/raw-common definitions after the address-block marker. A merged per-file report should preserve that boundary rather than flattening everything into one lane block.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while silently programming the wrong PHY bit.
- The file is generated. Manual edits risk divergence from AMD's source register database, silicon documentation, firmware expectations, and companion offset headers.
- The requested first line is inside the `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED2` register group, after the register comment and shift definitions. The preceding chunk is needed for the full start-of-register context.
- The requested last line is inside `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0`. The following `RESERVED_15_6` shift and subsequent AON supervisor output groups are outside this work item.
- Many fields in this DPCS 4.2.3 slice have `__SHIFT` definitions without corresponding `_MASK` definitions in the same range, while reserved/NC and some wider fields do have masks. Consumers should follow established AMDGPU helper conventions and not assume every shift has a nearby explicit mask.
- Override-enable and override-value fields are easy to confuse. Misprogramming them can force clocks, resets, pstate/rate/width, data-enable, loopback, adaptation, PH2 calibration, termination, PLL, SSC, RTUNE, AON, or analog controls away from hardware/firmware ownership.
- IRQ, clear, mask, request, ack, done, status, tune, recal, and context-update fields are sequencing-sensitive. Bad definitions can cause missed interrupts, false readiness, stuck clears, repeated IRQs, link-training timeouts, or failures during hotplug and suspend/resume recovery.
- PLL, SSC, charge-pump, bandgap, RTUNE, DCC, termination, RX equalization, slicer, squelch, CREG, CTLE offset, and analog-test fields are silicon- and board-sensitive. Defects may only reproduce at specific link rates, voltage/temperature corners, cable/sink combinations, or after repeated retraining.
- Reserved and `NC` fields occur throughout the chunk. Driver code should preserve them or leave them untouched unless authoritative programming documentation for the target ASIC stepping says otherwise.
- Repetitive names across lanes, CR instances, and DPCS generations can hide copy/paste mistakes. Mixing a CR4 raw-lane macro with a CR0 supervisor offset, or pairing a DPCS 4.2.3 field macro with a neighboring generation's offset, may compile but target the wrong hardware semantics.

## Test Signals

Useful validation for this generated header and its consumers includes:

- Build AMDGPU display configurations that include DPCS 4.2.3 support; missing or renamed macros should break generated register-table compilation.
- Mechanically compare this range against the authoritative DPCS 4.2.3 register database, checking that complete field layouts have expected shifts/masks within the intended register width.
- Cross-check complete register groups against the matching DPCS 4.2.3 offset header, especially around `DPCSSYS_CR4_RAWLANEX_DIG_*`, `C20_PHY_CR0_SUP_DIG_*`, and `C20_PHY_CR0_RAWCMN_DIG_*`.
- Diff repeated PCS/PMA/FSM/IRQ, MPLLA/MPLLB, RTUNE, AON, and analog-control families against neighboring DPCS/DCN generation headers to catch generator drift while allowing intentional generation differences.
- Exercise DisplayPort/HDMI boot display, hotplug, modeset, link-rate changes, lane-count changes, blank/unblank, suspend/resume, GPU reset, and repeated link retraining on hardware using this DPCS generation.
- Monitor logs and register dumps for link-training failures, request/ack timeouts, stuck reset/data-enable/clock overrides, repeated or missing lane IRQs, RX adaptation/PH2 calibration failures, DCC status anomalies, PLL tune/lock failures, SSC misconfiguration, RTUNE failures, unstable signal detect, and analog calibration drift.
- Decode known-good register dumps with these macros and compare against hardware documentation or reference tools for raw-lane PCS/PMA status, IRQ state, fast calibration/adaptation controls, MPLLA/MPLLB context and power-control fields, RTUNE values, AON tune/recal state, CREG context values, and analog ATB/bandgap/termination fields.
- Treat ATE, OCLA, ATB, forced analog, PLL override, CREG, context, and raw-lane debug paths as controlled diagnostics. They can bypass normal PHY ownership and should be validated with hardware-aware procedures.

## Cross-Chunk Notes

The previous chunk owns the start of `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED2`, including its register comment and shift definitions. This chunk resumes with `DPCSSYS_CR4_LANEX_ANA_TX_RESERVED2__NC7_0_MASK`, completes CR4 analog RX and raw-lane PCS/PMA/FSM/IRQ/control definitions, and then covers the beginning of the CR0 C20 PHY indirect pipe/common address block.

This chunk stops inside `C20_PHY_CR0_RAWCMN_DIG_AON_SUP_IN_0`, after the `FW_CLK_ACK` shift at line 99808. The next chunk should continue with that register's reserved field and then AON supervisor output/status definitions.
