# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 122527-124924

## Scope

This chunk is a generated AMD DCN 4.1.0 register field mask/shift section. It contains C preprocessor constants only: every register field is represented by a `__SHIFT` macro and a matching `__MASK` macro. The covered range starts inside the `DPCSSYS_CR2_LANEX_DIG_ASIC_TX_ASIC_IN_0` block and continues through CR2 lane digital/analog TX and RX controls, raw lane PCS controls, and raw lane FSM fast-calibration flags, ending at `DPCSSYS_CR2_RAWLANEX_DIG_FSM_FAST_RX_DFE_ADAPT`.

The header itself has no executable functions, no structs, and no runtime storage. Its purpose is to give typed driver code stable symbolic bit positions for MMIO register programming elsewhere in the AMD display stack.

## Purpose And Register Families

This chunk describes the bit layout for a CR2 lane (`CR2_LANEX`) and raw lane (`CR2_RAWLANEX`) block. The macros are used with register offsets from sibling offset headers, such as `dpcs_4_2_2_offset.h`, and with AMD display register helpers that combine a register address, field mask, and shift for reads and writes.

Important register families in this chunk:

- `DPCSSYS_CR2_LANEX_DIG_ASIC_*`: digital ASIC-facing TX/RX lane inputs, outputs, handshakes, and overrides. These cover TX clock-ready/reset/invert/data-enable/request/low-power/pstate/rate/width/MPLL selection/RX-detect disable fields, RX reset/data-enable/request/rate/width/adaptation/CDR tracking fields, TX/RX acknowledge/status fields, and lane/clock synchronization overrides.
- `DPCSSYS_CR2_LANEX_DIG_TX_PWRCTL_*`: TX power-state presets and sequencing delays. P-states `P0`, `P0S`, `P1`, and `P2` define analog clock, reference, reset, serializer, data-enable, VCM, RX-detect, div4, and MPLL clock enables. Power-up timing registers define TX clock, reference, VCM, reset, serializer, RX detect, MPLL clock, and fast-path timing fields.
- `DPCSSYS_CR2_LANEX_DIG_RX_PWRCTL_*`: RX power-state presets and RX power-up timing fields. P-states `P0`, `P0S`, `P1`, and `P2` include AFE, clock regulator, analog clock, deserializer, CDR, VCO reset/calibration, continuous calibration, and digital clock enables. Timing registers define AFE/VREG/clock/rate/CDR/deserializer delay and fast-start controls.
- `DPCSSYS_CR2_LANEX_DIG_RX_VCOCAL_*` and `DPCSSYS_CR2_LANEX_DIG_RX_CDR_*`: RX VCO calibration and CDR/DPLL controls/status. These include calibration counters, override selectors, skip-calibration bits, startup/update/settle timing, FSM state, calibration done, VCO counter results, frequency tune, CDR phase/frequency update gains, SSC counts, and DPLL bounds.
- `DPCSSYS_CR2_LANEX_DIG_RX_ADPTCTL_*`: RX adaptation configuration and status. These fields control adaptation configuration bits, resets, attenuation/VGA/CTLE/DFE status, slicer offsets, DAC control selection, and adaptation CR bank address/data access.
- `DPCSSYS_CR2_LANEX_DIG_RX_STAT_*`: RX statistics and pattern matching controls. These include load/start/stop, data masks, CR1A/CR1B pattern/mask fields, stat source/counter enables, sample counters, stat counters `0` through `6`, valid-loss clear/control, clock enable, and comparator clock controls.
- `DPCSSYS_CR2_LANEX_DIG_ANA_*` and `DPCSSYS_CR2_LANEX_ANA_*`: digital-to-analog override outputs and analog register fields for TX/RX lane bring-up, equalization, term code, DAC controls, VCO/CDR tuning, calibration, ATB measurement, voltage regulators, slicers, signal detect, MPHY, and power controls.
- `DPCSSYS_CR2_RAWLANEX_DIG_PCS_XF_*`: raw lane PCS transfer controls for TX/RX override inputs, PCS inputs/outputs, RX adaptation feedback, training direction fields, lane number, ATE overrides, term control, equalization overrides, and phase-2 calibration.
- `DPCSSYS_CR2_RAWLANEX_DIG_FSM_*`: raw lane FSM override, monitor, and fast RX calibration/adaptation enable fields. These expose jump address, jump enable, command start, override enable, break control, current FSM memory/status monitor bits, and one-bit fast calibration/adaptation flags.

## Important APIs, Types, And Macros

There are no functions or C types in this chunk. The important public surface is the macro naming contract:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit.
- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.
- Register comments such as `//DPCSSYS_CR2_LANEX_DIG_RX_VCOCAL_RX_VCO_STAT_1` group the subsequent field macros until the next register comment.
- The register name portion aligns with offset macros named `ixREGISTER` in generated offset headers. For example, sibling DPCS offset headers define offsets for names such as `ixDPCSSYS_CR2_LANEX_DIG_ASIC_TX_ASIC_IN_0`, `ixDPCSSYS_CR2_LANEX_DIG_RX_VCOCAL_RX_VCO_STAT_1`, `ixDPCSSYS_CR2_LANEX_ANA_RX_CLK_2`, and `ixDPCSSYS_CR2_RAWLANEX_DIG_FSM_FSM_OVRD_CTL`.

The mask width in this DCN 4.1.0 chunk is mostly 16-bit (`0xFFFFL`, `0x8000L`, etc.), matching lane-local 16-bit register fields. Related generated DPCS 4.2.x headers often use 32-bit-padded masks for the same logical fields, so code should not assume textual mask width is portable across ASIC register header families.

## Control Flow

This header contributes no direct control flow. Control flow is in the display driver code that includes this file, constructs register field descriptors, and uses the masks/shifts to update hardware registers.

The implicit hardware-control flow represented by the fields is:

1. TX/RX ASIC input registers request lane actions through `REQ`, `RESET`, `DATA_EN`, `PSTATE`, `RATE`, `WIDTH`, and low-power/disable fields.
2. Output/status registers report acknowledgements and hardware results, such as `TX_ACK`, `DETRX_RESULT`, RX `ACK`, `VALID`, adaptation status, VCO calibration done/status, CDR status, and stat-counter done flags.
3. Power-control registers establish desired per-state enable patterns and the hardware FSM/timing registers sequence those enables.
4. Calibration and adaptation blocks run VCO, CDR, AFE, DFE, reference-level, IQ, and RX adaptation operations; status and counter registers expose progress and outcomes.
5. Override registers can bypass normal FSM or analog-control paths for bring-up, diagnostics, ATE, or low-level tuning.
6. Raw lane PCS and FSM registers expose lower-level transfer, lane training, test, and fast-start controls beneath the higher-level CR2 lane abstraction.

## State And Persistence

The macros are compile-time constants and do not persist state. The state they describe lives in GPU hardware MMIO/register space. Writes to fields such as P-state enables, timing values, override enables, calibration skip bits, and FSM controls persist in the register block until the hardware resets, the driver reprograms them, or firmware/another control path changes them.

Important state classes:

- Programmed configuration: P-state values, power-up timing fields, CDR/DPLL gains and bounds, adaptation configuration, stat/pattern setup, analog calibration/override values.
- Ephemeral handshake/status: `ACK`, `VALID`, `*_DONE`, FSM state, counter done flags, calibration status bits, sampled statistics.
- Debug/test overrides: ATE override enable/value fields, raw-lane FSM jump/break controls, ATB measurement selections, OCLA selection, loopback, test pattern, and LBERT fields.

Because these are shared hardware registers, correctness depends on preserving reserved bits and using read-modify-write helpers when updating individual fields.

## Dependencies And Integration Points

This chunk depends on generated AMD ASIC register conventions rather than on normal C dependencies. It is protected by the file-level include guard `_dcn_4_1_0_SH_MASK_HEADER`.

Integration points observed from the tree:

- `drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes `dcn/dcn_4_1_0_sh_mask.h`, making these masks available to DCN 4.0.1/4.1-generation DMUB display code.
- Offset headers under `include/asic_reg/dpcs/`, such as `dpcs_4_2_2_offset.h`, define `ixDPCSSYS_CR2_*` register offsets for many of the same register names. Driver register tables typically combine these offset macros with the masks/shifts in this header.
- Similar generated mask files exist for DPCS 3.1.4, 4.2.0, and 4.2.2. This chunk is therefore part of a multi-ASIC generated register ABI, and field names must remain synchronized with the offset files and any register-table macros that paste field names.

## Risks And Edge Cases

- Field drift across ASIC revisions is the main risk. A field name reused with a different mask/shift in another generated header can silently program the wrong bits if the wrong ASIC header is included.
- Reserved and `NC*` fields are exposed as masks. Driver code should avoid writing reserved/non-connected bits unless hardware documentation or generated init tables require it.
- Some override fields are safety-sensitive: FSM jump/break, power override, term code override, VCO/CDR frequency tune, DPLL gain override, and ATE override controls can disrupt link training or display output if set outside controlled bring-up/debug flows.
- The chunk mixes digital lane, analog lane, PCS, and FSM registers. Code that assumes all `DPCSSYS_CR2_LANEX_*` fields are in one access domain may miss that `RAWLANEX` and analog register blocks can have different addressing or access restrictions.
- Several control/status pairs imply handshakes (`REQ`/`ACK`, calibration start/done, stat sample start/done). Polling code must use the matching status mask and respect hardware timeouts; this header only provides bit positions, not sequencing rules.
- DCN 4.1.0 uses mostly 16-bit masks in this lane section. Automated comparison or table generation should normalize numeric values rather than string width when comparing to related 32-bit-padded DPCS headers.

## Test Signals

Useful verification signals for this chunk are mostly compile-time and hardware/integration oriented:

- Build coverage for AMD display code that includes `dcn_4_1_0_sh_mask.h`, especially DMUB/DCN401 paths, catches missing or renamed macros.
- Register-table compile tests should verify that every used `REGISTER__FIELD__SHIFT` has a matching `REGISTER__FIELD_MASK`.
- Static generated-header validation can check that each field mask contains the shifted field width at the declared shift and that masks within a register do not overlap except where hardware intentionally aliases fields.
- Cross-header validation should compare this DCN 4.1.0 mask chunk against same-name DPCS 4.2.x and 3.1.4 definitions to catch unintended field drift while allowing known ASIC differences.
- Hardware smoke tests for affected blocks include link training, DisplayPort/USB-C lane bring-up, RX detect, low-power transitions, VCO/CDR calibration, adaptation, loopback/LBERT diagnostics, and recovery from display hotplug or suspend/resume.
- Debugfs or register-dump tests can confirm that read-modify-write helpers preserve reserved bits while updating fields such as `PSTATE`, `RATE`, `WIDTH`, power timing, calibration control, and override enables.

## Chunk Boundaries And Unresolved References

The chunk starts one line after the `//DPCSSYS_CR2_LANEX_DIG_ASIC_TX_ASIC_IN_0` register comment, so the first register group comment is just outside the requested range at line 122526. The first macros in scope are still part of that register group.

The chunk ends after the `DPCSSYS_CR2_RAWLANEX_DIG_FSM_FAST_RX_DFE_ADAPT` masks. Any subsequent raw-lane FSM fields, and earlier CR2 lane fields before TX ASIC input 0, are outside this chunk and should be reconciled by adjacent chunk reports during the final per-file merge.
