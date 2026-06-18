# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h lines 50048-52416

## Purpose

This chunk is part of AMDGPU Display Core's generated DPCS 4.2.2 shift/mask header. It defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DPCSSYS CR2 PHY registers. The register addresses live in the companion `dpcs_4_2_2_offset.h`; this file supplies the field layout needed by register helper macros to extract or update individual hardware fields.

The line range starts in the middle of `DPCSSYS_CR2_LANE2_DIG_RX_VCOCAL_RX_VCO_STAT_1` and ends after only the first field of `DPCSSYS_CR2_RAWCMN_DIG_CMN_CTL_1`, so the chunk is a partial slice of a larger generated header. Within the slice, the dominant coverage is CR2 lane 2 RX/analog controls, CR2 lane 3 digital/analog TX controls, and CR2 raw-common MPLL controls.

## Register Groups Covered

- Lane 2 RX calibration and clock recovery: VCO status, XAUI comma mask, LBERT control/error counters, CDR controls and status, DPLL frequency and frequency bounds.
- Lane 2 adaptive receiver tuning: `ADPTCTL_ADPT_CFG_0` through `_9`, reset configuration, ATT/VGA/CTLE/DFE tap status, slicer levels, DAC selector registers, CR bank address/data, and RX statistic/match/counter registers.
- Lane 2 MPHY and analog bridge controls: MPHY RX PWM/termination, digital-to-analog TX/RX override outputs, RX VCO override outputs, RX AFE/CTLE/scope/slicer controls, analog status, signal-detect overrides, TX DCC DAC overrides, and direct lane 2 analog TX/RX registers.
- Lane 3 ASIC lane and TX controls: lane override input, ASIC TX override inputs/outputs, ASIC TX/RX status outputs, TX power states `P0`, `P0S`, `P1`, `P2`, power-up timing, DCC DAC control, TX clock alignment, and TX LBERT.
- Lane 3 RX statistic monitor and analog TX controls: RX match/statistic counters plus digital analog TX override/status registers and direct lane 3 analog TX registers.
- CR2 raw common controls: `PHY_FUNC_RST`, MPLLA/MPLLB clock divider and bandwidth override inputs, MPLLA/MPLLB SSC override controls, lane FSM extension bit, MPLLA/MPLLB fractional-N SSC controls, and the first `MPLLA_INIT_CAL_DISABLE_OVRD_VAL` field of `RAWCMN_DIG_CMN_CTL_1`.

## Important APIs, Types, and Macros

There are no functions, structs, or runtime data structures in this chunk. Its API surface is the generated macro namespace:

- `DPCSSYS_CR2_<register>__<field>__SHIFT` gives the low bit index of a hardware field.
- `DPCSSYS_CR2_<register>__<field>_MASK` gives the already-shifted mask for that field.
- Fields are generally 16-bit CR register layouts, with many masks expressed as `0x0000....L`. Some adjacent ASIC register headers use shorter 16-bit spellings for equivalent masks; this 4.2.2 header consistently emits widened 32-bit constants for this area.
- Companion address macros such as `ixDPCSSYS_CR2_LANE2_DIG_RX_CDR_CDR_CTL_0` and `ixDPCSSYS_CR2_RAWCMN_DIG_MPLLA_OVRD_IN` are in `dpcs_4_2_2_offset.h`. The shift/mask macros are meaningful only when paired with the corresponding offset macro.

Notable fields include receiver adaptation enables (`CTLE_EN`, `VGA_EN`, `ATT_EN`, `DFE_EN`, `TGG_EN`), calibration completion/status (`RX_VCO_CAL_DONE`, `VCOCLK_TOO_FAST`, `RX_VCO_CORRECT`, `RX_VCO_UP`), TX power-state enables/resets/data enables, analog override enable/value pairs, MPLL divider/SSC/frac-N override enable/value pairs, and RX statistics comparator configuration (`PTTRN_*`, `DATA_MSK_*`, `STAT_CNT_*`).

## Control Flow

The header has no executable control flow. Control flow is indirect:

1. DCN resource code includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` for DCN 3.1.5 resource construction.
2. Display Core register tables and helper macros bind register offsets, shifts, and masks into encoder/resource structures.
3. Runtime link encoder and PHY code writes or reads hardware registers through those tables; the macros from this file determine which bits are touched.

The direct include point found for this ASIC revision is `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which includes both DPCS 4.2.2 offset and shift/mask headers. More generic DPCS field lists are declared in `dcn20_link_encoder.h` and `dcn201_link_encoder.h`, but this chunk mostly covers lower-level PHY CR fields that are not referenced by their full generated names in ordinary C code.

## State and Persistence

The macros themselves are compile-time constants and do not persist state. The state they describe lives in GPU display PHY hardware registers:

- Status fields expose current hardware state, such as VCO calibration results, CDR gain values, RX adaptation tap values, analog status bits, TX calibration status, and RX statistic counters.
- Control and override fields can persist in hardware until reset, power-gate transitions, driver reprogramming, or firmware/BIOS ownership changes.
- Many fields are paired as override value plus override enable. Programming the value without the enable bit, or leaving an enable bit asserted after a diagnostic operation, can leave hardware in a forced state instead of autonomous PHY control.
- The CR2 raw-common MPLL fields affect shared PLL behavior for the CR2 DPCS instance, so their state can influence multiple lanes rather than a single lane-local datapath.

## Dependencies and Integration Points

- Depends on the generated DPCS register offset header for the matching ASIC revision: `dpcs_4_2_2_offset.h`.
- Integrated into AMDGPU Display Core through DCN 3.1.5 resource setup, where DPCS base addresses and DPCS shift/mask definitions are selected for the ASIC.
- Consumed by AMD display register helper macros that combine offset, mask, and shift definitions. A field rename or mask change can break build-time macro expansion even if no direct textual reference to a full generated macro name exists.
- Mirrors similar DPCS headers for nearby revisions (`dpcs_4_2_0`, `dpcs_4_2_3`, `dpcs_3_1_4`) and DCN aggregate headers. These are useful comparison points when validating generated register database changes, but revision-specific differences must not be manually normalized without hardware confirmation.

## Risks

- Bitfield drift is high impact: an incorrect shift or mask can silently write the wrong hardware bit, affecting link training, PLL setup, RX adaptation, signal detect, or lane power sequencing.
- Partial-register writes must preserve reserved bits. This chunk contains many `RESERVED_*` masks, which signal fields that should generally be left untouched by driver code.
- Lane and instance naming is easy to confuse. This slice mixes CR2 lane 2, CR2 lane 3, and CR2 raw-common registers; copying a field between lanes or CR instances can target the wrong PHY path.
- Override enable/value pairs are risky during diagnostics and bring-up. Incorrectly asserting override enables for MPLL, TX, RX, DCC, VCO, or signal-detect controls can mask firmware defaults or hardware state machines.
- The chunk boundary is incomplete. Research or regeneration work using only this slice must not conclude that `RAWCMN_DIG_CMN_CTL_1` has only one field; its remaining fields appear after the requested end line.

## Test Signals

- Build coverage: compile AMDGPU Display Core for the DCN 3.1.5 configuration that includes `dpcs_4_2_2_sh_mask.h`; macro spelling and field-list mismatches should surface as compiler errors.
- Register database validation: compare this header against its matching offset header and generated source database to ensure every field belongs to the intended register and every mask matches the declared shift/width.
- Link training and display smoke tests: DisplayPort/HDMI bring-up across all CR2 lanes, including lane 2 and lane 3, is the main behavioral signal for bad TX power, PLL, RX, or analog field definitions.
- Hardware diagnostics: readback of VCO calibration status, CDR status, RX adaptation status, RX statistic counters, MPLL override/status, and SRAM/init/common reset fields can indicate whether the masks decode expected values.
- Regression comparison: when updating generated headers, diff against neighboring ASIC revisions only as a sanity check; identical names with changed mask spellings may be expected, while changed bit positions require hardware-register-source confirmation.
