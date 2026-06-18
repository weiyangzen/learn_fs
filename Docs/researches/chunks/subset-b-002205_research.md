# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 132119-134519

## Scope And Purpose

This chunk is part of AMD's generated DCN 4.1.0 register field header. It defines `*_SHIFT` and `*_MASK` constants for a contiguous slice of DisplayPort/USB-C PHY-related `DPCSSYS_CR3_*` registers. The source contains no executable C functions or data objects; it is an ABI-style map from symbolic register fields to their bit positions and masks. Driver code includes this header together with the matching `dcn_4_1_0_offset.h` file so register helper macros can compose MMIO addresses and field encodings at compile time.

The range starts in the middle of the CR3 lane 2 analog transmit override/measurement block and continues through lane 2 analog RX fields, lane 3 digital/analog PHY control and status fields, common raw PHY/MPLL fields, raw lane 0 PCS transfer fields, and the beginning of raw lane 0 FSM fast-calibration/lock fields. In this 2,401-line slice, there are 2,174 `#define` entries covering 228 register names and 1,458 unique field names. Most registers are 16-bit field maps with explicit `RESERVED_*` masks to preserve the generated hardware register layout.

This chunk is source-tree-aligned with `drivers/gpu/drm/amd/include/asic_reg/dcn/`. It should be merged later with adjacent chunks for the same header rather than treated as a standalone final file report.

## Major Register Areas

The first portion completes `DPCSSYS_CR3_LANE2_*` definitions. It covers lane 2 analog TX override and measurement controls such as `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1`, `ANA_TX_ATB2`, DCC DAC controls, termination code controls, clock override controls, miscellaneous TX controls, selector mux controls, voltage-regulator controls, and reserved vendor/test registers. It then covers lane 2 analog RX controls for RX clocks, CDR/deserializer controls, slicer control, RX power controls, signal detect/squelch, calibration controls, analog test bus measurements, VDAC range, CDR VREG, and RX VREG control.

The middle portion covers `DPCSSYS_CR3_LANE3_*` digital and analog lane controls. Digital ASIC override/input/output registers describe override enables and values for TX/RX lane state, power state, rate/divider selection, MPLL selection, equalization coefficients, DCC calibration, RX detection, VCO calibration, and adaptation/status handshakes. The TX power-control group defines lane 3 power states `P0`, `P0S`, `P1`, and `P2`, power-up timing registers, and DCC DAC bank/selector/ack/address fields. RX statistic registers define match masks, match values, statistic modes, sample counts, stop controls, and status counters. Digital-to-analog output registers expose computed/overridden analog TX fields such as term codes, EQ main/pre/post cursor values, boost controls, DCC DAC overrides, and fast-start/loopback bits.

The later lane 3 analog section mirrors the lane 2 analog TX control shape for `DPCSSYS_CR3_LANE3_ANA_TX_*`: measurement override, power override, alternate bus routing, ATB measurement selection, DCC DAC and DCC control, termination code control, clock override, misc boost/inversion fields, mux selection, VREG control, and reserved registers.

The common raw PHY section begins at `DPCSSYS_CR3_RAWCMN_DIG_*`. It includes common control, MPLLA/MPLLB override and spread-spectrum controls, lane FSM operation extension, common MPLL state control, TX calibration code, SRAM init status, OCLA, supervisory analog overrides, PCS/FW ID codes, always-on RTUNE values for RX/TX pull-down/pull-up lanes 0 through 7, common SRAM bitline config, power-gating override/status, supervisory override, VREF stats, reset override/status, reference-range override, and miscellaneous common configuration inputs.

The final section covers `DPCSSYS_CR3_RAWLANE0_DIG_*` raw lane 0 PCS and FSM fields. PCS transfer registers describe TX override inputs, TX PCS inputs/outputs, RX override inputs, RX PCS inputs/outputs, RX adaptation acknowledgement, figure-of-merit, directional TX pre/main/post cursor requests, lane number, ATE override inputs, RX equalization overrides, TX/RX termination override inputs, and RX phase-2 calibration. FSM registers then define manual FSM override control, memory-address/status monitor fields, fast RX startup/adaptation/calibration flags, fast TX common-mode and RX-detect flags, common-calibration MPLL status, continuous fast-calibration/adaptation controls, aggregate fast flags, and the opening `CR_LOCK` fields.

## Important APIs, Types, And Macros

This header exports preprocessor constants only. There are no C functions, structs, enums, or runtime storage in the chunk. The key naming contract is:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field bit mask in the register value.
- Register comments such as `//DPCSSYS_CR3_LANE3_DIG_TX_PWRCTL_TX_PSTATE_P0` identify the register block for the following field constants.

Downstream register helper layers consume these definitions through token-pasting macros. In display core code, `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h` defines `FN(reg_name, field)` as `FD(reg_name##__##field)`, and `REG_SET`, `REG_UPDATE`, and `REG_GET` pass those field tuples to generic field accessors. In DMUB code, `drivers/gpu/drm/amd/display/dmub/src/dmub_reg.h` defines `FD_SHIFT(reg_name, field)` and `FD_MASK(reg_name, field)` as token-pasted references to these generated constants, and uses `REG_SET`, `REG_UPDATE`, and `REG_GET` wrappers around DMUB register accessors.

This means the macro names themselves are the API. A rename, spelling difference, mask-width change, or shift mismatch is equivalent to changing a hardware register contract. The matching register offset names live in `dcn_4_1_0_offset.h`, while comparable DPCS-generation headers such as `dpcs_4_2_0_offset.h` and `dpcs_4_2_0_sh_mask.h` show the same register naming scheme for related IP blocks.

## Control Flow

There is no runtime control flow inside this chunk. The effective flow is compile-time and call-site driven:

1. A DCN 4.1 implementation file includes `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`.
2. A local register table or register helper macro names a register and field.
3. Token-pasting resolves the register address macro from the offset header and the field shift/mask macros from this header.
4. Generic helpers read, write, set, update, or extract field values using the resolved address, shift, and mask.
5. Hardware side effects occur only when those helpers touch MMIO registers; this header only supplies bit layout metadata.

The chunk is therefore a dependency of many potential control paths even when no C source references these exact CR3 symbols directly. If a caller later adds a lane-training, PHY diagnostic, PLL, RX adaptation, or DCC calibration path using these field names, the helper macros depend on these constants resolving correctly at compile time.

## State And Persistence Behavior

The header itself has no mutable state and persists nothing. All state described by the constants is hardware state in DCN/DPCS registers. Writes through helper macros can persist until the hardware block is reset, power-gated, retrained, or overwritten by firmware/driver code. Reads reflect current PHY, PLL, PCS, calibration, status-monitor, or test/override state.

Several fields in this chunk are especially stateful at the hardware level:

- Override enable/value pairs such as `*_OVRD_EN`, `*_OVRD_VAL`, `*_OVRD_IN`, and `*_OVRD_OUT` can redirect normal PHY control away from firmware or autonomous logic.
- Power-state fields such as lane 3 `TX_PSTATE_P0`, `P0S`, `P1`, and `P2` encode lane behavior for different power states.
- Calibration and adaptation fields such as DCC DAC selectors, RX EQ overrides, PH2 calibration, fast RX calibration flags, continuous calibration flags, and MPLL calibration status coordinate with hardware state machines.
- Status and monitor fields such as RX statistic counters, FSM status, memory-address monitors, OCLA controls, VREF stats, RTUNE values, and common power-gating status expose transient hardware state.
- Lock fields at the end of the chunk, beginning with `DPCSSYS_CR3_RAWLANE0_DIG_FSM_CR_LOCK__CR_REG_LOCK`, suggest hardware-level protection for control registers and memory.

Because reserved masks are explicitly generated, read-modify-write users should preserve reserved bits unless hardware documentation requires a specific value. Incorrect masks can clear sticky status bits, set reserved bits, or corrupt adjacent fields during field updates.

## Dependencies And Integration Points

The immediate dependency is the paired DCN 4.1.0 offset header. Offset macros provide register addresses; this file provides field layout. Both are guarded by `_dcn_4_1_0_SH_MASK_HEADER` and are included by DCN 4.0.1/4.1 display paths such as `display/dmub/src/dmub_dcn401.c` and `display/dc/irq/dcn401/irq_service_dcn401.c`.

The generated constants integrate with:

- Display Core register helpers in `display/dc/inc/reg_helper.h`, including `REG_READ`, `REG_WRITE`, `REG_SET*`, `REG_UPDATE*`, and `REG_GET*`.
- DMUB register helpers in `display/dmub/src/dmub_reg.h`, where shift/mask constants are stored in generated register tables and passed to `dmub_reg_set`, `dmub_reg_update`, and `dmub_reg_get`.
- DCN 4.1 register table construction, which uses field macros to populate offset, shift, and mask arrays for hardware services.
- Hardware link/PHY bring-up, diagnostics, validation, and firmware interaction paths that may use the CR3 lane/common/raw-lane register fields.
- ASIC register generation tooling outside this source slice; the regularity and large volume strongly indicate the file is generated from hardware register specifications.

The chunk also has cross-family alignment implications. Similar `DPCSSYS_CR3_*` field names appear in DPCS 4.2 generated headers. Differences between DCN 4.1 and DPCS 4.2 may be intentional IP-version changes, but accidental divergence can break shared code or ported register sequences.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These constants often compile even when values are wrong, and failures appear later as display link training instability, PHY calibration failures, missing hotplug/link events, bad equalization, clocking problems, or hard-to-reproduce power-state bugs.

Important risk categories include:

- Field-width errors: masks such as `0x0001L`, `0x001CL`, `0x03FFL`, `0x1F00L`, and `0xFFFFL` encode different widths. A one-bit width error can truncate a programmed value or spill into a neighboring field.
- Shift/mask mismatch: helper code generally trusts the pair. If `SHIFT` and `MASK` no longer describe the same field, register updates can appear to succeed while programming the wrong bits.
- Reserved-bit handling: many registers include `RESERVED_15_*` masks. Field update helpers must not use these as normal programmable fields unless explicitly intended for generated table completeness.
- Override hazards: enabling analog or digital overrides such as TX power overrides, RX EQ overrides, MPLL overrides, FSM overrides, ATE overrides, or DCC DAC overrides can bypass autonomous hardware/firmware sequencing.
- Lane indexing: this chunk transitions from lane 2 to lane 3 and then to `RAWLANE0`. Copying symbols between lanes is easy to get wrong because many field names are identical except for the lane number.
- Boundary continuity: the chunk starts after earlier lane 2 digital analog output definitions and ends at the beginning of the `RAWLANE0_DIG_FSM_CR_LOCK` block. Adjacent chunks are required to understand the full register run.
- Generated-file drift: manual edits to generated headers can be overwritten by regeneration or can desynchronize from offset headers and hardware specs.

## Test Signals

The most basic signal is compilation of DCN 4.1 display code that includes both `dcn_4_1_0_offset.h` and this header. Token-pasted references must resolve, and generated register tables must have matching shift/mask members. Warnings about redefinitions, missing macros, or invalid constants are strong indicators of generation or integration drift.

Useful static checks include verifying each field has a matching `SHIFT` and `MASK`, verifying masks are contiguous when interpreted at their shift, verifying reserved fields do not overlap non-reserved fields within a register, and comparing register names against the paired offset header. This chunk's register count and regular lane/common/raw-lane grouping make it suitable for automated consistency checks rather than manual review alone.

Runtime signals require AMD hardware or emulation that exercises the affected PHY paths. Relevant scenarios include DisplayPort/USB-C link bring-up, lane training at multiple rates, power-state transitions, hotplug/resume, link retraining after suspend, MST or high-bandwidth display modes, diagnostics that read RX statistics or OCLA/ATE state, and firmware interactions that read or write common MPLL and lane calibration status.

Failure signatures to watch for include display link failure, intermittent blanking, reduced link rate/lane count, repeated training fallback, bad RX EQ/adaptation status, DCC calibration timeout, unexpected PLL state, firmware/DMUB register access errors, and read-modify-write traces that modify reserved bits or adjacent fields. Because this file has no unit-testable algorithm, the strongest test value comes from register-map validation plus hardware smoke and stress coverage of display link paths.
