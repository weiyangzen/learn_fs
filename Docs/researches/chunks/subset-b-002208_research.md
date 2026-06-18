# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 139391-141853

## Purpose

This chunk is generated AMD DCN 4.1.0 register-field metadata for the DPCS/PHY side of the display stack. It contains no executable C logic; it exports `#define` constants that describe bit shifts and masks for 16-bit DPCSSYS CR3 RAWAON lane registers and CR3 SUPX support/PLL registers. Driver code pairs these constants with generated register offsets and AMD display register helpers when it needs to pack, extract, or update individual hardware fields.

The requested range contains 2,128 macro definitions: 1,066 `__SHIFT` entries and 1,062 `_MASK` entries across 336 register names. It starts immediately after the comment for `DPCSSYS_CR3_RAWAONLANE1_DIG_FW_CALIB_CONFIG`, so the first register comment is just outside the chunk. It ends in the middle of `DPCSSYS_CR3_SUPX_ANA_MPLLAB_CTR_OUTCLK`; four `MPLLB_*` masks for that register continue on lines 141854-141857.

Although this file lives under a local `ceph-client` source mirror, the content here is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, callbacks, locks, allocations, includes, or direct MMIO operations in this range. The public contract is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or preserving that field.

The major register groups are:

- `DPCSSYS_CR3_RAWAONLANE1_DIG_*` tail: firmware calibration, lane transceiver mode override/readback, RX signal-detect filter configuration, TX DCC configuration, and TX/RX DCC bypass-capacitor override/readback fields.
- `DPCSSYS_CR3_RAWAONLANE2_DIG_*`, `DPCSSYS_CR3_RAWAONLANE3_DIG_*`, and `DPCSSYS_CR3_RAWAONLANEX_DIG_*`: three repeated lane layouts, each with 84 register blocks. These cover AFE/CTLE offsets, RX adaptation readbacks, DFE offsets and tap values, RX phase/slicer controls, MPLL coarse tuning/status, startup/adaptation done flags, adaptation control words, MPLL disable/background controls, TX/RX overrides, LOS and signal-detect filtering/status, calibration code registers, DCC calibration code banks, TX DCC bank address/data/control, firmware MM/adaptation/calibration configuration, and lane transceiver mode fields.
- `DPCSSYS_CR3_SUPX_DIG_*`: 61 support digital registers for reference-clock and MPLLA/MPLLB override inputs, spread-spectrum peak and step-size values, charge-pump override fields, supervisor and level overrides, ASIC input readbacks, bandgap/CP ASIC inputs, clock ASIC inputs, and PMA version identification.
- `DPCSSYS_CR3_SUPX_ANA_*`: 16 support analog registers for prescaler, RTUNE, bandgap, measurement switch, pre-regulator and VREF generator controls, MPLLA/MPLLB miscellaneous controls, PLL enable/cal/reset overrides, analog test-bus selection, VREG controls, and the start of MPLLAB output-clock controls.

Common field themes in this chunk are `OVRD`/`OVERRIDE` enable-value pairs, `RESERVED_*` or `NC*` holes, PLL and clock controls, RX adaptation/DFE calibration data, signal-detect/LOS filtering, TX/RX DCC calibration, and firmware handoff/configuration fields. Most masks are 16-bit values ending in `L`, consistent with this DPCS register window.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMD display code and hardware sequencing:

1. DCN401 display files include `dcn_4_1_0_sh_mask.h` together with the matching offset header.
2. Register table macros and AMD display helpers combine register offsets, shifts, and masks into block-specific access tables.
3. Runtime paths use helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` to access selected fields.
4. If these DPCSSYS CR3 fields are used, higher-level PHY, link, clock, or firmware-control code decides the programming order; this generated header only supplies bit positions.

Current-tree search shows the header is included by DCN401 resource, clock-manager, GPIO, IRQ, and DMUB code, but the exact `DPCSSYS_CR3_RAWAONLANE*` and `DPCSSYS_CR3_SUPX_*` names in this slice are not directly referenced outside generated ASIC headers in this source tree. That makes this slice primarily a hardware-description surface for future or indirect table consumers.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It names hardware-backed DPCS PHY state:

- Per-lane RX adaptation and calibration state, including ATT/VGA/CTLE values, DFE tap values, IQ/phase adjustment, slicer controls, figure-of-merit, adaptation done flags, and fast calibration flags.
- Per-lane signal-detect and LOS state, including HF/LF signal-detect outputs, filter counters, calibration codes, masks, and override outputs.
- Per-lane TX/RX DCC and DFE calibration state, including calibration code registers, DCC bank address/data/control, bypass capacitor controls, and related override/readback bits.
- Per-lane MPLL state, including coarse tune, disable, common calibration status, RCAL status, and background-control waits/delays.
- SUPX shared PLL/support state for reference clocks, MPLLA/MPLLB enables, dividers, HDMI/div clocks, spread-spectrum controls, charge pump settings, supervisor controls, level controls, bandgap, VREF, VREG, test-bus selection, and output clocks.

Persistence and side effects are hardware-defined. Configuration fields generally remain until link reprogramming, PHY reset, display block power gating, suspend/resume, GPU reset, ASIC reset, firmware reinitialization, or another driver path rewrites them. Status and calibration fields can be read-only, sticky, self-clearing, volatile while clocks are gated, or valid only after firmware/hardware calibration has completed. This generated header does not encode those access semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DCN 4.1.0 register database and companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` provides matching register offsets and base indexes for DCN 4.1.0 register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h`, `dpcs_4_2_2_sh_mask.h`, and `dpcs_4_2_3_sh_mask.h` contain closely related DPCS-generated field layouts for other DPCS versions; the same example names appear there with compatible offsets in the matching DPCS offset headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, `display/dc/gpio/dcn401/*`, `display/dc/irq/dcn401/irq_service_dcn401.c`, and `display/dmub/src/dmub_dcn401.c` include this generated header as part of the DCN401 hardware-description set.
- Generic AMD display register-helper infrastructure depends on the shift/mask naming scheme being exact; token-pasted field names must match the generated register database.
- Behaviorally, these fields sit below display link training, PHY bring-up, AUX/HPD routing, clock/PLL programming, firmware-assisted PHY calibration, and diagnostics that inspect signal-detect or adaptation state.

The `RAWAONLANEX` register family is a notable integration point: it appears to provide a lane-generic namespace parallel to concrete lane 2 and lane 3 copies. Consumers must choose the correct offset/register namespace rather than assuming `LANEX` aliases a particular physical lane.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly and only surface as corrupted PHY programming or misleading status reads.
- The file is generated. Manual edits risk divergence from AMD's authoritative register database, matching offset headers, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first register comment for `FW_CALIB_CONFIG` is just before this range, and the final `MPLLAB_CTR_OUTCLK` register is incomplete because four masks continue immediately after line 141853.
- Many fields are override enable/value pairs. Setting a value bit without the matching enable bit, or using the wrong mask for an enable bit, can leave hardware-controlled behavior unexpectedly active or force an invalid PHY state.
- `RESERVED_*` and `NC*` fields are numerous. Accidentally writing masks that include reserved bits can create silicon-version-specific failures.
- The repeated lane 2, lane 3, and `LANEX` blocks are copy-sensitive. A generator or merge error may affect only one physical lane and only connectors routed through that lane.
- RX adaptation, DFE, CTLE, VGA, ATT, and slicer fields are calibration-sensitive. Wrong masks can produce marginal links, high error rates, blank displays, or failures only at high data rates.
- Signal-detect and LOS masks affect link presence and recovery decisions. Bad fields can look like sink disconnects, false link-loss events, or stuck link training.
- MPLL, spread-spectrum, charge-pump, VREG, bandgap, and output-clock fields are sequencing-sensitive and can be invalid while the PHY is powered down or reset.
- Firmware MM/adaptation/calibration configuration fields imply coordination with firmware or hardware microcontrollers; using stale masks can break firmware handoff assumptions even if host-side code builds.

## Test Signals

Useful validation combines generated-header checks with hardware display-link coverage:

- Build AMDGPU display support with DCN401 enabled. Missing or renamed macros should surface in DCN401 register-table construction or consumers that token-paste generated names.
- Mechanically verify that every register in this slice has paired shift/mask fields, allowing the expected boundary exception where `DPCSSYS_CR3_SUPX_ANA_MPLLAB_CTR_OUTCLK` has its final four masks after this chunk.
- Diff this slice against AMD's authoritative DCN 4.1.0 register database and against related DPCS 4.2.x generated headers where layout compatibility is expected.
- Cross-check each register name against `dcn_4_1_0_offset.h` or the matching DPCS offset headers so fields are not orphaned from register addresses.
- Exercise DisplayPort and HDMI link bring-up across connectors mapped to different physical lanes, especially lane 2 and lane 3, at multiple link rates and spread-spectrum settings.
- Run link training, hotplug, suspend/resume, display power-gating, GPU reset, and rapid modeset cycles while watching for false LOS/signal-detect events, PLL lock failures, stuck calibration done bits, or firmware calibration timeouts.
- Capture register dumps before and after PHY calibration to confirm adaptation readbacks, DFE tap values, DCC calibration codes, MPLL status, and signal-detect state use the expected bit positions.
- Test high-bandwidth modes that stress PHY margins. Useful external signals include stable modesets, no repeated link retraining, no unexpected HPD disconnects, clean display output, and absence of PHY/link errors in kernel logs.
- If direct tests for these exact macros are unavailable, static generated-header consistency checks are the main guard because the current source tree appears not to reference these exact DPCSSYS CR3 names outside generated headers.

## Cross-Chunk Notes

The previous chunk owns the comment and nearby context for `DPCSSYS_CR3_RAWAONLANE1_DIG_FW_CALIB_CONFIG` and earlier lane 1 firmware/adaptation fields. This chunk owns the lane 1 tail, complete lane 2/lane 3/`LANEX` DPCS PHY field groups, most SUPX digital fields, and SUPX analog fields through the first half of `MPLLAB_CTR_OUTCLK` masks. The next chunk begins with the remaining `MPLLAB_CTR_OUTCLK` masks and then continues into `MPLLAB_CTR_LOCK` and later SUPX analog controls. The final per-file research document should reconcile those boundaries before making whole-file claims about all CR3 DPCS PHY and SUPX PLL metadata in `dcn_4_1_0_sh_mask.h`.
