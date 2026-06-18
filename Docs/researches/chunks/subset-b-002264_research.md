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
