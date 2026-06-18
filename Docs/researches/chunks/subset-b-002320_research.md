# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h lines 76243-78683

## Purpose

This chunk is a generated AMD DPCS 4.2.0 shift/mask header slice for DCN 3.1 display PHY register fields. It contains no executable C code. Its public surface is preprocessor metadata that tells AMDGPU display code where individual bitfields live inside DPCS control/status registers.

The requested range contains 2,074 `#define` entries: 1,036 `__SHIFT` constants and 1,038 `_MASK` constants. It starts inside the tail of `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`, covers the remaining CR3 raw-lane-3 PMA/TX/RX/PCS control fields, then covers repeated CR3 always-on lane calibration/status fields for lanes 0 through 3. It ends inside the beginning of `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST`, so both the first and last registers are split by chunk boundaries.

Although this file is under a local `ceph-client` source mirror, this chunk is AMDGPU display-controller register metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocations, locks, or direct MMIO operations in this range. The API contract is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask of that field within its hardware register.

The main macro families in this chunk are:

- `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_*`: PMA interface fields for lane 3, including RX/TX request, reset, data-enable and loopback override bits; PMA ack and retune request/ack bits; MPHY override controls for RX PWM clocks/data, async enable, PWM enable, clock select, and RX termination; and RX adaptation phase-map override controls.
- `DPCSSYS_CR3_RAWLANE3_DIG_TX_CTL_*`: lane-3 TX state-machine and clock controls, including MPLL-off wait time, RX-detect allowance in P states, TX clock enable/select, async beacon wait time, TX DCC continuous status, OCLA enable, and UPCS data/clock observation enables.
- `DPCSSYS_CR3_RAWLANE3_DIG_RX_CTL_*`: lane-3 RX state-machine controls and status bits, including RX control FSM enable, P1 rate-change allowance, loss-of-signal mask counter, RX data-enable override counters, off-cancel/adaptation continuous status, and RX UPCS OCLA gating.
- `DPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_ATE_*` and related PCS transfer fields: ATE/test override inputs for RX and TX rate, width, pstate, LPD, MPLL selection/enables, master MPLL override, async TX enable, TX presets, TX/RX termination, TX/RX load-value overrides, CTLE boost, and PI-related override controls.
- `DPCSSYS_CR3_RAWAONLANE0_DIG_*` through `DPCSSYS_CR3_RAWAONLANE3_DIG_*`: four repeated always-on lane blocks. Each block defines analog calibration, adaptation, status, override, signal-detect, DCC, firmware configuration, and lane transceiver-mode fields.
- `DPCSSYS_CR3_RAWAONLANEX_DIG_*`: shared or lane-X always-on field definitions beginning near the end of the chunk. The range includes AFE/DFE offset and RX phase/adaptation fields and stops before the register is complete.

The always-on lane block is the largest surface in this range. Each concrete lane instance includes masks/shifts for AFE attenuation and CTLE IDAC offsets; RX IQ adaptation and FOM; DFE summer, phase, data, bypass, and error VDAC offsets; even/odd reference levels; linear and mapped phase-adjust values; MPLLA/MPLLB coarse tune; initial power-up done; RX ATT/VGA/CTLE/DFE tap adaptation values; RX adaptation done; fast flags; slicer controls; MPLL/RCAL common-calibration status; adaptation control words; MPLL disable; TX/RX override inputs; LOS and signal-detect filters; stats; RX override output groups; signal-detect calibration/code registers; VREF generator enable; calibration code registers; RX DCC calibration code registers; TX DCC bank address/data/control; MPLL bandgap timing; firmware MM/adaptation/calibration config; lane transceiver-mode override/readback; RX signal-detect config; and TX DCC config.

## Control Flow

This header has no runtime control flow. It contributes compile-time constants to AMDGPU's register access layer:

1. `dcn31_resource.c` includes `dpcs/dpcs_4_2_0_offset.h` and this matching `dpcs/dpcs_4_2_0_sh_mask.h`.
2. Resource and link-encoder table macros use token-pasting helpers such as `REG`, `SRI`, `SRI_IX`, `LE_SF`, and related shift/mask list macros to combine register offsets from the offset header with field positions from this header.
3. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to access hardware registers.

The macros in this chunk do not decide sequencing. PHY reset, request/ack handshakes, retuning, RX adaptation, TX/RX clock selection, ATE override use, signal-detect filtering, and DCC/calibration programming are controlled by display driver code, firmware, and silicon behavior outside this generated header.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names hardware-visible state and control fields:

- Lane-3 PMA/PCS/TX/RX override and handshake state, including request/reset/data-enable overrides, loopback controls, RX/TX PMA ack, retune request/ack, RX termination overrides, async and PWM controls, TX clock controls, RX/TX state-machine controls, and test/ATE override values.
- Per-lane always-on PHY state for lane calibration and adaptation, including analog offsets, DFE references, RX phase adjustment, MPLL coarse tune, RX adaptation completion/status, fast startup flags, common calibration status, adaptation control storage, LOS/signal-detect behavior, and DCC calibration data.
- Firmware and microcode-facing configuration fields such as firmware MM/adaptation/calibration words, lane transceiver-mode override/readback, TX DCC bank access, and signal-detect tuning.

Persistence and side effects are hardware-defined. Configuration bits may survive until display modeset, PHY power gating, suspend/resume, GPU reset, or ASIC reset rewrites them. Status, ack, done, calibration, and signal-detect fields may be read-only, latched, self-clearing, or valid only while the relevant DPCS lane and always-on power island are powered and clocked. This file only supplies bit locations; it does not encode access direction or lifetime semantics.

## Dependencies And Integration Points

This generated file must stay synchronized with AMD's DPCS 4.2.0 register database and the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h` supplies the matching register offsets. For this range, lane-3 PMA/TX/RX/PCS offsets include `ixDPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_PMA_IN` through `ixDPCSSYS_CR3_RAWLANE3_DIG_PCS_XF_TX_OVRD_IN_2`, and always-on lane offsets run in repeated `0x4000`, `0x4100`, `0x4200`, and `0x4300` bands for lanes 0-3.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` directly includes this header and builds DCN 3.1 register shift/mask tables. In particular, link-encoder masks combine `LINK_ENCODER_MASK_SH_LIST_DCN31` with `DPCS_DCN31_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` and inherited DCN2/DCN3 link-encoder field-list patterns are the style of consumers that rely on DPCS register macros for link PHY programming, even when many shared field lists use canonical RDPCSTX names rather than the raw-lane names in this exact slice.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and `.c` consume DPCS/RDPCS-style offset and mask tables for high-performance DP link encoder register access.
- Adjacent generated headers for DPCS 4.2.2, DPCS 4.2.3, and DCN 4.1.0 expose closely related field names, which are useful for generator consistency comparisons but are not substitutes for this ASIC-specific file.

Behaviorally, these fields sit under display link bring-up, PHY lane power/control, link training, signal detection, runtime retuning, debug/test overrides, and calibration telemetry for DPCS CR3.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong mask or shift can compile cleanly and corrupt only one hardware bitfield at runtime.
- The file is generated. Manual edits risk divergence from the authoritative register database, `dpcs_4_2_0_offset.h`, firmware expectations, and silicon documentation.
- Chunk boundaries are not semantic. The first lines are only the ending masks for `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT`, and the final line is only the first shift definition for `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST`.
- Lane and instance repetition is copy-sensitive. The `RAWAONLANE0` through `RAWAONLANE3` blocks should be structurally aligned where hardware intends; a generator drift can affect only one physical lane or only CR3.
- Request/ack and done bits are sequencing-sensitive. Bad definitions for PMA ack, retune ack, adaptation done, power-up done, calibration status, or common-calibration state can cause timeouts, false readiness, or link bring-up hangs.
- Override-enable fields can force the PHY away from normal hardware/firmware control. Incorrect masks for RX/TX request, reset, data-enable, loopback, PLL, async, termination, or phase overrides can break link training, cause blank displays, or leave lanes stuck after suspend/resume.
- Signal-detect, LOS mask, VREF, DFE, CTLE, VGA, ATT, RX phase, and DCC fields affect analog behavior. Errors may show up only with specific lane rates, cables, sinks, boards, voltage/temperature corners, or marginal signal integrity.
- The `data`/`DATA` field spelling varies across generated ASIC headers. Consumers that token-paste exact field names must use the names from the included ASIC generation, not names from nearby DPCS/DCN versions.
- Reserved bits are widely represented. Driver code should avoid treating reserved masks as available controls unless the hardware programming guide or firmware handoff explicitly requires it.

## Test Signals

Useful validation combines generated-header consistency checks with runtime display behavior:

- Build DCN 3.1 AMDGPU display support. Missing or renamed macros should surface in `dcn31_resource.c`, DPCS link-encoder mask/shift tables, and HPO DP link encoder users.
- Mechanically compare this range against the authoritative DPCS 4.2.0 register-field database and ensure every complete register field has a consistent `__SHIFT`/`_MASK` pair, allowing the split first and last registers.
- Cross-check the shift/mask register names against `dpcs_4_2_0_offset.h` so every lane-3 PMA/TX/RX/PCS and always-on lane register has a matching offset.
- Run repetition checks across `DPCSSYS_CR3_RAWAONLANE0` through `DPCSSYS_CR3_RAWAONLANE3` to catch unintended field drift while allowing intentional lane-specific offsets.
- Compare related DPCS 4.2.2/4.2.3 and DCN 4.1.0 generated headers for expected naming, mask-width, and reserved-field differences.
- Exercise DP/HDMI link bring-up across all lanes and link rates exposed by CR3 hardware. Watch for request/ack timeouts, RX adaptation failures, retune failures, stuck data-enable/reset bits, and unstable signal detect.
- Test hotplug, modeset, blank/unblank, suspend/resume, and GPU reset paths on systems using this ASIC generation, with attention to lane power-up done, adaptation done, common-calibration status, and restoration of override controls.
- Use hardware register dumps around failed link training to verify TX/RX clock selection, PMA/PCS overrides, RX adaptation values, DFE/CTLE/VGA/ATT values, signal-detect filters, and DCC calibration fields decode as expected with these masks.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DPCSSYS_CR3_RAWLANE3_DIG_PMA_XF_RX_OVRD_OUT` and earlier CR3 raw-lane-3 PMA fields. This chunk continues through lane-3 PMA/TX/RX/PCS transfer fields and the full repeated always-on lane 0-3 blocks, then starts the shared `RAWAONLANEX` block. The next chunk should complete `DPCSSYS_CR3_RAWAONLANEX_DIG_DFE_DATA_EVEN_LOW_VDAC_OFST` and the remaining shared lane-X always-on definitions. The final per-file research document should reconcile those boundaries before making whole-register or whole-file claims.
