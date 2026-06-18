# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 79053-81495

## Scope And Purpose

This chunk is part of AMDGPU Display Core Next 4.1.0 generated register metadata. It contains C preprocessor constants for bit shifts and masks, not executable functions. The covered area defines 2,142 `#define` entries for 301 register comment blocks in the `DPCSSYS_CR0` DisplayPort PHY/clock subsystem. The chunk starts inside the `DPCSSYS_CR0_RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0` record and ends after `DPCSSYS_CR0_SUPX_DIG_RTUNE_STAT`; the following RTUNE set/stat/config counter records begin after this chunk.

The main purpose is to give DCN401 display code stable symbolic names for extracting or composing fields in 16-bit PHY register values. These masks pair with ASIC offset headers, for example `ixDPCSSYS_CR0_RAWAONLANE3_DIG_ADPT_CTL_0`, and with the display register helper macros that combine a register offset, field mask, and field shift. The file is included directly by DCN401 components such as DMUB support, IRQ service, resource setup, and clock manager code.

## Register Areas Covered

The slice contains four source-tree-aligned register groups:

- Tail of `DPCSSYS_CR0_RAWAONLANE2_DIG_*`: the final lane-2 always-on PHY fields, mostly DCC calibration code readouts, TX DCC bank programming, MPLL background control, signal-detect overrides/status, firmware configuration windows, lane transceiver mode override/status, RX signal-detect filtering, and TX/RX DCC bypass controls.
- Full `DPCSSYS_CR0_RAWAONLANE3_DIG_*`: lane-3 equivalents for receiver adaptation, DFE/slicer tuning, phase adjustment, MPLL coarse tune/status, calibration status, adaptation control words, signal-detect state, DCC calibration, firmware windows, lane mode, and DCC bypass.
- Full `DPCSSYS_CR0_RAWAONLANEX_DIG_*`: generic lane-X aliases with the same field layout as lane 3. These are likely used by code or generated tables that operate on an indexed lane rather than a specific physical lane.
- Beginning of `DPCSSYS_CR0_SUPX_*`: supervisor/common PHY fields for ID code, reference clock overrides, MPLLA/MPLLB divider and HDMI clock override inputs, PLL override words, spread-spectrum peak/stepsize controls, CP/GS controls, supervisor and prescaler overrides, ASIC input/status mirror registers, PMA version, analog prescaler/RTUNE/bandgap/vref/MPLL control, MPLLA/MPLLB power-control finite-state-machine registers, clock/reset power-up timers, reference regulator control, and RTUNE configuration/status.

## Important APIs, Types, And Constants

There are no C APIs, structs, or functions in this chunk. The effective interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the least significant bit for a field.
- `REGISTER__FIELD_MASK` gives the bit mask for the same field.
- `REGISTER` names in comments correspond to hardware registers whose offsets live in matching generated offset headers.
- `RESERVED_*` masks describe bits callers should preserve during read-modify-write sequences.

The register field families are hardware-facing and important:

- Receiver adaptation and equalization: `RX_ADPT_ATT`, `RX_ADPT_VGA`, `RX_ADPT_CTLE`, `RX_ADPT_DFE_TAP1` through `TAP5`, `RX_ADAPT_DONE`, `RX_ADAPT_FOM`, `ADPT_CTL_0` through `ADPT_CTL_7`, and multiple DFE VDAC/IDAC offset registers.
- Signal detection and loss-of-signal: `RX_SIGDET_CAL`, `RX_SIGDET_HF_CODE`, `RX_SIGDET_LF_CODE`, `SIGDET_OUT_OVRD`, `SIGDET_OUT_IN`, `RX_SIGDET_CONFIG`, `RX_SIGDET_FILT_CTRL`, and `RX_LOS_MASK_CTL`.
- DCC and calibration: `RX_DCC_CAL_*`, `TX_DCC_BANK_ADDR`, `TX_DCC_BANK_DATA`, `TX_DCC_CONT`, `TX_DCC_CONFIG`, `TX_RX_DCC`, and `TX_RX_DCC_BYP_AC_CAP_IN`.
- PLL and clocking: lane-level `MPLLA_COARSE_TUNE`, `MPLLB_COARSE_TUNE`, `MPLL_DISABLE`, lane `LANE_CMNCAL_MPLL_STATUS`, supervisor `MPLLA_*`, `MPLLB_*`, spread-spectrum controls, divider/HDMI clocks, and MPLL power-control state/timers.
- Analog common controls: supervisor `ANA_*` fields for prescaler, RTUNE, bandgap, vref generation, charge pump, output clocks, lock controls, and PMIX-related MPLL controls.

## Control Flow And Data Flow

This header has no runtime control flow. At compile time it expands symbolic field metadata into constants that the display driver can use in register programming helpers. Runtime data flow is external:

1. DCN401 display code includes this header and the matching offset header.
2. Driver code reads a MMIO or indirect PHY register value, or prepares a new value.
3. Field helper macros use `*_MASK` and `*_SHIFT` to isolate, validate, set, or preserve individual fields.
4. The composed value is written back to the ASIC register, often as part of link bring-up, clock selection, power sequencing, signal-detect calibration, or PHY debug/override paths.

The lane-specific and lane-X groups provide the same field shape at different register names. That matters for table-driven code: a caller can use the generic layout when it already computed a lane base, while direct lane-specific code can use `RAWAONLANE3` names.

## State And Persistence Behavior

The macros themselves do not persist state. They describe state stored in GPU hardware registers. Most fields affect transient hardware state such as adaptation status, calibration codes, PLL lock/power states, signal-detect readings, and override enables. Some writes can have persistent effects for the duration of the display link or until the display engine resets the PHY block, such as MPLL override selection, clock divider choices, spread-spectrum settings, DCC bank data, RTUNE controls, and bandgap/reference power-up timing.

Reserved masks are part of the state contract. Any write path that updates one field should preserve reserved bits and unrelated live fields, usually through read-modify-write helpers. Blind writes to registers in this area risk disturbing analog calibration, PLL lock, or lane adaptation state.

## Dependencies And Integration Points

This chunk depends on the generated ASIC register ecosystem rather than normal C linkage:

- Matching DCN/DPCS offset headers supply `ix...` register addresses for the names documented here.
- AMD display register access helpers supply the logic that combines offset, mask, and shift constants for `REG_GET`, `REG_SET`, `REG_UPDATE`, and related patterns.
- DCN401 display modules include this exact header: `display/dmub/src/dmub_dcn401.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/resource/dcn401/dcn401_resource.c`, and `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`.
- Hardware integration is with the DisplayPort PHY/clock subsystem, especially link lane bring-up, lane adaptation, signal detection, PLL selection, spread-spectrum clocking, power sequencing, and debug/firmware override interfaces.

The file also mirrors nearby generated DPCS variants, with the same register concepts appearing in `dpcs_*_sh_mask.h` and `dpcs_*_offset.h`. That duplication is expected for ASIC-family register snapshots, but it means manual edits in one generated header can silently diverge from sibling ASIC definitions.

## Risks And Edge Cases

- Chunk boundaries split register records. The first `RAWAONLANE2_DIG_RX_DCC_CAL_QCM_CODE_0` field is incomplete in this chunk, and the RTUNE family continues after `RTUNE_STAT`; downstream reconciliation should merge with adjacent chunks before treating this as a complete per-file view.
- These macros encode hardware ABI. A wrong shift or mask can corrupt unrelated fields, especially in shared 16-bit analog/PHY registers with reserved high bits.
- Override-enable fields are common in this area. Setting an override value without its enable bit, or leaving an enable bit asserted after debug/calibration code, can make link training and power management nondeterministic.
- `RAWAONLANE3` and `RAWAONLANEX` have intentionally parallel layouts. Copy/paste or generator drift between them would break lane-indexed register logic even if direct lane-3 access still builds.
- Many status fields are read-only or hardware-updated in practice despite being represented only as masks here. Driver code should avoid writing status/mirror registers unless the hardware programming guide marks them writable.
- Reserved masks such as `0xFFF0L`, `0xFC00L`, and `0xF000L` dominate many records. Any helper that writes full-register literals must be audited against these reserved regions.

## Test Signals

Because this is generated metadata, useful validation is mostly structural and integration-based:

- Compile DCN401 AMDGPU display code with `dcn_4_1_0_sh_mask.h` included; missing or renamed masks should fail at build time in register helper users.
- Cross-check every `REGISTER__FIELD_MASK` against `REGISTER__FIELD__SHIFT` widths and ensure fields do not overlap except reserved coverage.
- Diff the lane-3 and lane-X register layouts to confirm matching field names, shifts, and masks where the generic lane alias is expected to mirror a physical lane.
- Cross-check `dcn_4_1_0_sh_mask.h` against the matching offset header and sibling DPCS generated files for register presence and obvious width changes.
- Runtime display smoke tests should include DP link training, hotplug, suspend/resume, modesets at multiple link rates, and MST or multi-lane configurations, because failures in these fields are most likely to appear as link instability, PLL lock failures, signal-detect errors, or PHY calibration regressions.
