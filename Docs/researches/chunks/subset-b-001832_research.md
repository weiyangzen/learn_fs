# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h lines 12982-15245

## Purpose

This chunk is generated AMD DCN 3.1.4 register-offset metadata. It contains no executable C logic; it publishes preprocessor constants that map symbolic display-controller register names to numeric MMIO offsets plus companion base-index selectors. DCN314 display code combines each `reg...` offset with its matching `reg..._BASE_IDX` through helper macros such as `BASE(reg..._BASE_IDX) + reg...`.

The requested range is the final large slice of `dcn_3_1_4_offset.h`. It starts in the tail of HPO DP Sym32 stream encoder 2, then covers HPO DP stream encoder 3, MPC/MPCC composition and color-management blocks, HPO HDMI stream encoder 0 packet/audio blocks, HPO top/mapper/perfmon blocks, ABM instances 0 through 3, DPIA MU status/timeout registers, and the second HDA/Azalia controller/endpoint aliases. The chunk has 2,136 `#define` lines: 1,068 register-offset macros and 1,068 matching `_BASE_IDX` macros.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, or direct includes in this range. Its public surface is the generated register macro namespace:

- `reg<block>_<register>`: a DCN314 MMIO register offset.
- `reg<block>_<register>_BASE_IDX`: the DCN base segment selector used by resource and hardware helper macros.

Every non-`_BASE_IDX` register macro in this chunk has a matching `_BASE_IDX`. The first HPO DP stream-encoder families use base index `2`; the MPC, HPO top/HDMI, ABM, DPIA, and HDA/AZ families in this slice use base index `3`. The base index is part of the address contract, so the numeric offset alone is not sufficient for safe register access.

Major macro families in this slice:

- Tail of `DP_SYM32_ENC2`: video MSA tail registers, HBLANK control, generic SDP/GSP controls 0-14, SDP audio/metadata controls, stream/VBID/panel replay/CRC controls, memory power, and spare register.
- `DP_STREAM_ENC3`, `APG3`, `DME8`, `VPG8`, and `DP_SYM32_ENC3`: HPO DP stream encoder 3 clock/input/audio controls, APG audio packet generator controls and CRC/status, DME memory/control, VPG generic packet/ISRC/MPEG registers, and Sym32 video/SDP/MSA/CRC/memory-power controls.
- `MPCC0` through `MPCC3`: compositor pipe controls for top/bottom selection, OPP routing, blending/control fields, update-lock selection, gains, background color, memory power, and status.
- `MPCC_OGAM0` through `MPCC_OGAM3`: per-MPCC output gamma controls, indexed LUT access/data, RAM A/B piecewise-region programming, offsets, start/end/slope/base controls, and gamut-remap coefficient registers.
- `MPC` configuration: clock control, mutex/arbiter controls, output MUXes, output CDE controls, DWB muxing, CRC controls/results, 1 mux, MMHUBBUB read-urgent select, shared memory-power control, and debug-select/data registers.
- `MPC_OUT0` through `MPC_OUT3` OCSC: output muxes, output CSC control and 3x4 coefficient registers for output color-space conversion.
- `MPC_RMU`: RMU control, memory power, MPCC muxing, shared control, shaper LUT programming, RAM A/B regions, 3D LUT indexed access/data/read-write control, normalization factor, and output offsets for two RMU pipelines.
- `DC_PERFMON22` and `DC_PERFMON23`: MPC and HPO perf counter control/state/current-value/high/low registers.
- `AFMT5`, `VPG9`, and `DME9`: HPO HDMI stream encoder 0 audio formatter packet/channel/status/CRC/audio source/memory-power controls, VPG generic packet registers, and DME control/memory-control.
- `HPO_TOP` and `DP_STREAM_MAPPER`: HPO top clock/hardware controls and stream-mapper controls 0-3.
- `ABM0` through `ABM3`: ambient/user/target/current/final PWM levels, minimum duty cycle, ABM/PWM update/lock controls, ACE offset/slope and threshold controls, luma statistics, sample rates, histogram bin shift/index controls, histogram results 1-24, and backlight master lock.
- `DPIA_MU`: RBBM interface timeout controls and status.
- `AZCONTROLLER1`, `AZENDPOINT1`, and `AZINPUTENDPOINT1`: HDA/Azalia CORB/RIRB pointers/control/status/size, immediate command/response interfaces, DMA position base addresses, and endpoint immediate command aliases.

## Control Flow

This header has no runtime control flow. The runtime sequencing is supplied by AMDGPU display code:

1. DCN314 resource, IRQ, DIO, DMUB, clock, HPO, ABM, VPG, AFMT, MPC, and related code includes `dcn_3_1_4_offset.h` together with `dcn_3_1_4_sh_mask.h`.
2. Register-list macros paste instance IDs into generated names such as `regMPCC0_MPCC_STATUS`, `regMPCC_OGAM3_MPCC_OGAM_LUT_DATA`, `regMPC_RMU1_3DLUT_DATA`, `regVPG9_VPG_GENERIC_PACKET_DATA`, or `regABM2_DC_ABM1_HG_RESULT_24`.
3. Resource helpers in `dcn314_resource.c` define address builders such as `SR(reg_name)` and `SRI(reg_name, block, id)` that expand the offset plus its `BASE_IDX` segment.
4. Hardware blocks later use the populated register tables through `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, wait/poll helpers, and DMUB register access paths.

The macros do not encode ordering or side effects. Consumers still must sequence clocks, power gating, memory power, stream setup, audio/infoframe packet updates, double-buffer commits, color LUT programming, ABM/backlight updates, perf counter sampling, HDA command rings, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files. It describes MMIO-backed GPU display state. The represented hardware state includes:

- HPO DP/HDMI stream-encoder state for input routing, clocks, audio controls, video MSA/MSA double-buffering, SDP/GSP packet controls, metadata packets, panel replay, CRC capture, memory power, and spare/debug controls.
- APG, VPG, AFMT, and DME state for audio/infoframe/generic packet generation, ISRC/MPEG metadata, audio CRC/status, packet update timing, memory control, and memory-power state.
- MPC/MPCC blending and routing state for plane composition, OPP/output selection, background color, gains, update locks, memory power, status, mutex arbitration, debug buses, CRC capture, and DWB routing.
- Output color-management state for MPCC output gamma LUTs, shaper LUTs, output CSC matrices, gamut-remap coefficients, 3D LUT access/data, normalization factors, and RMU pipeline routing.
- ABM/backlight state for user and ambient light inputs, ABM target/current levels, PWM duty-cycle output, ACE parameters, luma statistics, histogram bins/results, sample rates, register locks, and master backlight lock.
- DPIA MU RBBM interface status and timeout configuration.
- HDA/Azalia command-ring and immediate command state for the second controller and endpoint aliases.

Persistence is hardware-defined. Configuration registers normally retain values until modeset, block reprogramming, power gating, suspend/resume, or ASIC reset. Status, interrupt, lock, indexed data, CRC, histogram, perf counter, clear/ack, and command-interface registers can be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive. This offset header does not define those semantics; the matching mask header and block-specific driver code do.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN314 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h` for field shifts and masks.
- DCN base-address definitions in `dcn314_resource.c`, especially `DCN_BASE__INST0_SEG2` and `DCN_BASE__INST0_SEG3`, which are selected through `_BASE_IDX` values.
- Register helper macros from `reg_helper.h` and local resource macros such as `SR`, `SRI`, `SRI2`, and `SRIR`.

Direct include sites for `dcn_3_1_4_offset.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

Important consumers around these register families include DCN314 resource-pool construction, DIO stream encoder setup, HPO DP stream/link encoders, `dcn31_vpg`, `dcn31_afmt`, ABM/DMUB backlight control, MPC/MPCC color and composition code, IRQ service setup, perf counter/debug paths, and HDA/Azalia display-audio initialization.

## Risks And Edge Cases

- Offset or base-index drift is the main risk. These are untyped preprocessor constants, so a bad offset or `_BASE_IDX` can compile cleanly while reading or writing the wrong MMIO register.
- The chunk begins inside `DP_SYM32_ENC2`; earlier macros for that block are owned by the previous chunk. File-level conclusions about encoder 2 require reconciliation with adjacent chunks.
- Repeated instance families are copy-sensitive. `MPCC0`-`MPCC3`, `MPCC_OGAM0`-`MPCC_OGAM3`, `ABM0`-`ABM3`, and HPO DP/HDMI packet blocks are structurally similar but not interchangeable.
- Indexed LUT/data pairs are sequencing-sensitive. Wrong `LUT_INDEX`, `LUT_DATA`, shaper, 3D LUT, or gamut-remap offsets can silently corrupt color programming and may only show on HDR, gamma, color-management, or multi-plane paths.
- Packet and audio controls are timing-sensitive. Bad VPG/AFMT/APG/DME/HPO offsets can cause missing or stale infoframes, audio dropouts, CRC failures, metadata corruption, or issues limited to DP/HDMI HPO paths.
- ABM and PWM registers affect visible backlight behavior. Incorrect offsets or lock handling can cause wrong brightness, flicker, unexpected dimming, failed ambient-light compensation, or resume-time backlight regressions.
- Perfmon, CRC, histogram, status, and command-ring registers may be read/clear or counter-like. Treating them as ordinary persistent configuration can lose diagnostics or create misleading telemetry.
- HDA/AZ aliases intentionally share some offsets, for example CORB and RIRB subfields mapped at the same register address. Mechanical duplicate-address checks must account for packed register fields and endpoint aliases.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC with DCN314 support enabled; missing or renamed macros should fail in DCN314 resource, IRQ, DMUB, DIO, HPO, VPG, AFMT, ABM, MPC, and related register-table construction.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 12982-15245 has exactly one matching `_BASE_IDX` macro, and that base-index values remain `2` for HPO DP stream-encoder register blocks and `3` for the later MPC/HPO/ABM/DPIA/HDA register blocks.
- Diff this chunk against AMD's authoritative DCN314 register database and adjacent generated headers where compatible register maps are expected, such as DCN 3.1.x and DCN 4.x offset headers.
- Exercise HPO DP and HPO HDMI outputs: modesets, link enable/disable, audio playback, packet/infoframe updates, metadata packets, panel replay paths where available, CRC capture, suspend/resume, and hotplug.
- Exercise composition and color-management paths: multi-plane blending, OPP routing, MPC CRCs, output CSC, gamut remap, output gamma, shaper LUTs, 3D LUT programming, and DWB routing.
- Validate ABM/backlight behavior across all exposed ABM instances: brightness updates, ambient-light input, ABM level changes, histogram/luma statistics, PWM duty cycle, register locking, and suspend/resume restoration.
- Watch kernel logs and display diagnostics for MMIO access faults, underflow, link-training failures, packet conflicts, audio loss, color corruption, backlight anomalies, stuck interrupts, perf counter anomalies, HDA command timeouts, and DPIA MU RBBM timeout/status errors.

## Cross-Chunk Notes

Earlier chunks own the beginning of `dce_dc_hpo_dp_sym32_enc2_dispdec`, including the control, FIFO, pixel-format, and first MSA registers. This chunk owns the encoder-2 tail and the final DCN314 offset-header blocks through `#endif`. The merge lane should reconcile this document with neighboring chunks before making complete claims about the full `dcn_3_1_4_offset.h` register map.
