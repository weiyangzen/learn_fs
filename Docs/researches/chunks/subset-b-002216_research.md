# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h lines 13312-15838

## Purpose

This chunk is a generated AMD DCN 4.2.0 register-offset header slice. It exports preprocessor constants that name MMIO register offsets and matching `_BASE_IDX` values for two DCN address spaces:

- HPO DisplayPort stream/link/DPHY register blocks use `_BASE_IDX` value `2`.
- MPC/MPCC compositor and color-management register blocks use `_BASE_IDX` value `3`.

The range contains 2,391 `#define` lines: 1,196 register-offset macros and 1,195 `_BASE_IDX` macros. It starts in the tail of the HPO DP DPHY SYM32 instance 0 block, covers HPO DP stream/link/DPHY instances 1 through 3, then transitions into the MPC block: MPCC instances 0 through 3, MPCC OGAM instances 0 through 3, MPC output CSC/denorm controls, MPC RMCM instances 0 and 1, MPC perfmon registers, and the beginning of MPCC MCM instance 0. The chunk ends in the middle of `MPCC_MCM0`, so adjacent chunks are required for whole-file conclusions about all MCM registers.

Although this source tree is under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or runtime APIs in this header chunk. The exported interface is the generated macro namespace consumed by DCN 4.2 display code:

- `reg<REGISTER>` expands to the generated register offset.
- `reg<REGISTER>_BASE_IDX` selects the base segment used by token-pasting register helpers.
- DCN 4.2 resource and DMUB code resolve final addresses as `ctx->dcn_reg_offsets[reg..._BASE_IDX] + reg...`.
- Field-level access is supplied by the sibling `dcn_4_2_0_sh_mask.h`; this offset header only names addresses.

Important register families in this slice:

- HPO DP stream encoder instances 1-3: `regDP_STREAM_ENC1_*`, `regDP_STREAM_ENC2_*`, and `regDP_STREAM_ENC3_*` provide stream clock control, input muxing, audio control, clock-ramp FIFO status/control, and spare registers.
- HPO DP APG/DME/VPG packet sub-blocks: `regAPG6-8_*`, `regDME6-8_*`, and `regVPG6-8_*` expose audio packet generator control/debug/memory power, metadata engine control/memory power, generic packet access/data, GSP frame/immediate update, generic status, memory power, and ISRC access/data registers. These APG/VPG instance numbers correspond to HPO DP stream instances rather than the legacy DIG instance numbering.
- HPO DP SYM32 stream encoders 1-3: `regDP_SYM32_ENC1-3_*` cover stream enable/control, video FIFO, MSA and pixel-format double buffering, MSA payload words, hblank handling, 15 SDP/GSP controls, audio SDP controls, metadata packet control, VBID, panel replay, video CRC control/results/status, symbol counters, ALPM sleep/wake/request/ready/hardware-mode/status/start/interrupt controls, memory power, and spare registers.
- HPO DP link encoders 1-3: `regDP_LINK_ENC1-3_*` expose clock control and spare registers.
- HPO DP DPHY SYM32 instances 1-3 plus the preceding instance-0 tail: `regDP_DPHY_SYM320-*` and `regDP_DPHY_SYM321-323_*` include DPHY control/status, stream VC rate controls, stream allocation table updates, SAT VC slots and status, eDP/ASSR configuration, ALPM sleep/wake/control, test-pattern configuration, PRBS seeds, custom pattern registers, error status, and symbol counters.
- MPCC compositor instances 0-3: `regMPCC0-3_*` define top/bottom mux selection, OPP routing, control/control2, stereo-mix control, update-lock selection, blend gains, movable color-management location control, background color channels, memory-power control, and status.
- MPCC OGAM instances 0-3: `regMPCC_OGAM0-3_*` provide output gamma control, LUT index/data/control, RAMA/RAMB piecewise-linear start/slope/base/end/offset/region registers for RGB channels, and gamut-remap coefficient format/mode/matrix coefficients for banks A and B.
- MPC output CSC/denorm: `regMPC_OUT0-3_*` exposes output mux and denormalization controls/clamps. The shared output CSC block contains coefficient format, CSC mode, and matrix coefficients for outputs 0-3, including banked A/B coefficient sets.
- MPC RMCM instances 0-1: `regMPC_RMCM0-1_*` expose shaper control, offset/scale, shaper LUT index/data/write mask, RAMA/RAMB shaper regions, 3D LUT mode/index/data/read-write/out-normalization/out-offset, gamut remap format/mode/matrix coefficients, memory power, 3D LUT fast-load select/status, control, and test/debug access.
- MPC perfmon: `regDC_PERFMON16_*` provides perfmon control, counter, test-debug index/data, and clear registers for the MPC block.
- MPCC MCM instance 0 start: `regMPCC_MCM0_*` begins a large per-MPCC movable color-management block with shaper control/offset/scale/LUT programming, shaper RAMA/RAMB region tables, 3D LUT programming, 1D LUT control/data, 1D LUT RAMA/RAMB piecewise-linear programming, and the first gamut-remap controls.

## Control Flow

This header has no executable control flow. Runtime behavior is created by consumers that include this generated metadata:

1. DCN 4.2 resource construction includes `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h`.
2. Register-list macros in `dcn42_resource.c` and `dcn42_resource.h` token-paste names such as `regDP_SYM32_ENC1_DP_SYM32_ENC_CONTROL`, `regDP_DPHY_SYM321_DP_DPHY_SYM32_STATUS`, `regMPCC0_MPCC_CONTROL`, or `regMPC_RMCM0_MPC_RMCM_3DLUT_DATA`.
3. Helpers such as `SR`, `SRI`, `SR_ARR`, and `SRI_ARR` compute final offsets from `ctx->dcn_reg_offsets[segment] + generated_offset`.
4. Constructed hardware objects use those tables through `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`.

The macros do not encode sequencing. The HPO DP code must still perform link enable/disable, lane/mode programming, stream allocation table programming, test-pattern setup, ALPM transitions, panel replay state handling, SDP/audio/metadata setup, and DPHY status polling in the correct order. The MPC/MPCC code must still acquire/update locks where required, power memories before programming LUTs, select the correct RAM bank, program PWL regions and LUT entries consistently, switch color-management modes at a safe time, and preserve pipe topology while changing muxes or blend state.

## State And Persistence Behavior

The header stores no software state. It identifies hardware registers whose state is owned by DCN 4.2 display blocks:

- HPO DP stream state includes stream encoder clock/input/audio configuration, packet generator state, generic packet memories, SDP/GSP controls, MSA and pixel-format double-buffered values, VBID/panel replay controls, video CRC state, ALPM state, memory-power state, and symbol counters.
- HPO DP link/DPHY state includes DPHY reset/enable/mode/lane state, VC rate programming, stream allocation table slots, eDP ASSR state, ALPM configuration, test-pattern and PRBS seeds, error status, and link symbol counters.
- MPCC state includes per-compositor topology selection, OPP routing, blending mode and gains, background color, update-lock selection, memory-power state, and status.
- MPCC OGAM, MPC RMCM, and MPCC MCM state includes color pipeline mode, shaper LUTs, 1D/3D LUT memories, bank selection, gamut-remap matrices, coefficient formats, fast-load status, and debug index/data state.
- MPC output state includes output mux routing, denormalization/clamp configuration, output color-space conversion matrices, and perfmon counter/control state.

Persistence is hardware-defined. Programming generally survives until a modeset, plane update, color-management update, link retrain, panel replay/ALPM transition, power-gate cycle, suspend/resume, driver reset, or ASIC reset. Status, interrupt, counter, CRC, error, perfmon, debug, and memory-power state registers may be read-only, sticky, self-clearing, write-one-to-clear, or meaningful only while the corresponding block is powered and clocked. This offset header does not describe those access semantics; consumers must rely on the shift/mask header and ASIC programming rules.

## Dependencies And Integration Points

This generated header must remain synchronized with AMD's DCN 4.2 register database and with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h`, which provides field shifts and masks for the same symbolic register names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, which includes this header and resolves offsets through `ctx->dcn_reg_offsets`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.h`, which defines DCN 4.2 register-list macros, including `DCN42_HPO_DP_STREAM_ENC_REG_LIST_RI(id)`, `DCN42_HPO_DP_LINK_ENC_REG_LIST_RI(id)`, and `VPG_DCN42_REG_LIST_RI(id)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn42/dcn42_hpo_dp_link_encoder.c`, which reads DPHY status, lane count, mode, stream allocation slots, and VC rates through the HPO DP link encoder register table.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.c`, which uses the MPC/MPCC register tables for MPCC blending, RMCM shaper/3D LUT power, PWL programming, LUT programming, gamut remap, and hardware state readback.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c`, which also includes `dcn_4_2_0_offset.h` and computes DMUB-visible register offsets via `REG_OFFSET_EXP`.

The chunk's HPO DP registers integrate with DCN 4.2 stream encoders, link encoders, DCCG HPO clocks, DMUB commands that carry HPO stream/link instance identifiers, DisplayPort 2.x link training, MST allocation, eDP ALPM/ASSR, panel replay, audio SDP, and VPG/DME/APG metadata packet paths. The MPC registers integrate with resource pool construction, plane composition, OPP routing, color management, 3D LUT and shaper programming, HDR/gamut remap paths, perfmon diagnostics, and debug-state readback.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong offset or base index can compile cleanly while directing MMIO to the wrong block or segment.
- This chunk has mixed base segments. HPO DP registers use base index `2`, while MPC/MPCC registers use base index `3`; accidental cross-segment substitution would produce plausible-looking but wrong final addresses.
- The chunk boundaries are artificial. It starts after the beginning of DPHY instance 0 and ends before the end of `MPCC_MCM0`, so complete block-level review requires adjacent chunks.
- HPO DP instance names are copy-sensitive. Stream/link/DPHY instances 1-3 are nearly identical, and APG/DME/VPG numbering uses `6`, `7`, and `8`; an instance-number mismatch can connect packets, stream encoders, link encoders, or DPHY state to the wrong HPO path.
- DPHY and SAT/VC-rate registers are central to DP 2.x operation. Misaddressing can break link enablement, lane/mode reporting, MST bandwidth allocation, throttled VCP size programming, training/test patterns, eDP ASSR, ALPM, or symbol/error diagnostics.
- Stream encoder and packet registers affect visible output metadata. Bad offsets can cause blanking, incorrect MSA or pixel format, missing audio SDP, stale HDR or ISRC packets, invalid panel replay signaling, or misleading CRC/symbol-counter reads.
- MPCC control and mux registers define pipe composition topology. Wrong values can route a plane to the wrong output, corrupt blending, break update-lock behavior, or leave the compositor in a stale state across modesets.
- MPCC OGAM, RMCM, and MCM blocks are LUT-heavy and banked. Incorrect offsets or bank selection can cause color corruption, gamma discontinuities, HDR/gamut-remap errors, hangs while programming powered-down memories, or failed fast-load transitions.
- Memory-power registers are operational, not just metadata. Programming LUT or packet memories while their memory-power state is off or transitioning may fail silently or produce transient display corruption.
- Perfmon and debug index/data registers can be misleading if the wrong block is selected, if counters are not cleared, or if reads happen while clocks/power are gated.

## Test Signals

Useful validation combines generated-header consistency with DCN 4.2 hardware behavior:

- Build AMDGPU display code with DCN 4.2 enabled. Missing or renamed macros should fail in `dcn42_resource.c`, `dcn42_resource.h`, `dcn42_mpc.c`, `dcn42_hpo_dp_link_encoder.c`, `dmub_dcn42.c`, or register-list expansion.
- Mechanically compare this range against `dcn_4_2_0_sh_mask.h` and the generated register database, checking that every consumed offset macro has a matching `_BASE_IDX` macro and that field definitions exist for all programmed fields.
- Diff equivalent HPO DP and MPC/MPCC blocks against nearby ASIC headers such as `dcn_4_0_1_offset.h`, DCN 3.6 headers, and later DCN headers to catch unintended instance swaps, base-index changes, or register omissions.
- Exercise DP 2.x and HPO paths on DCN 4.2 hardware: hotplug, cold boot, modesets, high-bandwidth modes, MST, DSC-over-DP where applicable, link retraining, test patterns, ALPM, eDP ASSR, panel replay, audio SDP, metadata packets, CRC reads, symbol counters, suspend/resume, and HPD storms.
- Exercise composition and color paths: multi-plane blending, alpha and global gain, OPP routing, update-lock changes, background color, output CSC/denorm, SDR/HDR modes, gamma/degamma updates, shaper LUTs, 1D/3D LUTs, gamut remap, fast-load paths, and repeated plane enable/disable.
- Monitor kernel logs and display diagnostics for failed `REG_WAIT` loops, DPHY status mismatches, SAT/VC allocation errors, link training failures, blank or flickering displays, missing audio or metadata, panel replay/ALPM failures, color corruption, memory-power warnings, perfmon anomalies, and resume-only regressions.

## Cross-Chunk Notes

This is a middle chunk of `dcn_4_2_0_offset.h`. The previous chunk contains the beginning of HPO DP instance 0 and likely the first stream/link/DPHY blocks. The next chunk continues `MPCC_MCM0` and the remaining generated register-offset namespace. The final per-file research document should merge adjacent chunks before making complete claims about all HPO DP instances, all VPG/APG mappings, all MPCC/MPC color-management blocks, or the full DCN 4.2 register surface.
