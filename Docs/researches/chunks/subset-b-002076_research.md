# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 44309-46526

## Purpose

This chunk is a generated AMD DCN 3.5.0 shift/mask register-field slice. It has no executable C logic; it publishes preprocessor constants that describe bit positions and masks for fields inside DCN display, audio, video-packet, performance-counter, and adaptive-backlight MMIO registers. Driver code combines this header with the matching `dcn_3_5_0_offset.h` register offsets and AMD display register-helper macros to pack, extract, and update individual hardware fields.

The requested range starts in the middle of the `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25` field group and ends at only the `__SHIFT` half of `DPIA_MU_RBBMIF_TIMEOUT_CTRL__RBBMIF_TIMEOUT_DELAY`. Within the exact range there are 2,218 `#define` lines: 1,108 `__SHIFT` macros and 1,110 `_MASK` macros. The uneven count is caused by chunk boundaries: the first three lines are masks whose shifts live before line 44309, while the final `DPIA_MU_RBBMIF_TIMEOUT_CTRL` mask and its sibling fields continue after line 46526.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this range. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating, preserving, or clearing that field during MMIO read-modify-write operations.

Major register families in this chunk:

- `MPCC_OGAM3_*`: tail of MPCC 3 output gamma and gamut-remap metadata. It covers RAM-B exponential-region LUT offsets and segment counts for regions 24-33, output-gamma gamut-remap coefficient format/mode fields, and A/B banks of `C11` through `C34` matrix coefficients.
- `MPC_*`: display pipe composition and output processing fields. Covered groups include MPC clock control, global/per-component soft reset bits, CRC control/selection/result fields, perfmon event enable, bypass background color, host-read rate control, DPP/config/surface pending status, frame/update-lock sets, DWB muxing, output muxes 0-3, output denorm controls and clamps, and output CSC format/mode/coefficient fields for outputs 0-3.
- `DC_PERFMON22_*` and `DC_PERFMON23_*`: performance monitor and performance counter selection, trigger, enable, clear, state, current value, high, and low fields for two monitor instances.
- `AFMT5_*`: audio formatter instance 5 fields for VBI packet control, audio packet control, audio info words, IEC 60958 channel-status words, audio CRC control/result, ramp controls, formatter status, infoframe control, audio source control, and AFMT memory power state.
- `VPG9_*`: video packet generator instance 9 fields for generic packet access/data, generic stream packet frame and immediate update controls, update-pending bits, generic status/conflict state, VPG memory power, ISRC data access, and MPEG info payload/update fields.
- `DME9_*`: Display Micro Engine metadata requestor and memory low-power control fields.
- `HPO_TOP_*` and `DP_STREAM_MAPPER_CONTROL[0-3]`: HPO top-level display-clock gating, high-performance-output hardware enable, and DP stream mapper link-target selection fields.
- `ABM0_*` through `ABM3_*`: four repeated adaptive backlight management/PWM instances. Each instance contains ambient/user/target/current/final/minimum duty level fields; ABM PWM control and backlight update sample-rate fields; double-buffer lock/update control; ABM enable/bypass; IPS color-space-conversion coefficient selectors; ACE slope/offset and threshold fields; histogram/luminance-statistics controls, results, sample rates, shift flags, and register-read progress; plus backlight master lock.
- `DPIA_MU_RBBMIF_TIMEOUT_CTRL`: only the first timeout-delay shift appears at the final line; the corresponding hold field and masks are outside this chunk.

Several repeated layouts are significant. `MPC_OUT0` through `MPC_OUT3` share mux, denorm, and output CSC geometry; `ABM0` through `ABM3` are almost mechanically identical, with the same field layout per adaptive-backlight instance; `DC_PERFMON22` and `DC_PERFMON23` repeat the same monitor/counter model.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from the AMDGPU display driver:

1. DCN 3.5 code includes `dcn_3_5_0_offset.h` and this shift/mask header.
2. Register-list macros token-paste symbolic register and field names into per-block register tables.
3. Resource, DMUB, MPC, output pixel processor, audio formatter, video packet generator, performance monitor, HPO/DP mapping, and ABM code stores those tables in DCN 3.5-specific structures.
4. Runtime paths call register helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and wait/poll variants; those helpers use the numeric shift/mask constants to read or modify only the targeted field bits.

The macros do not encode ordering rules. Consumers still have to sequence clock gating, reset, pipe composition, output muxing, color pipeline programming, CRC capture, packet double-buffer updates, audio packet setup, performance-counter start/stop, ABM double-buffer locks, frame-start update timing, and power-gated block access correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing to disk. It describes MMIO-backed DCN 3.5 hardware state:

- MPCC output gamma/gamut-remap state, including piecewise RAM-B region layout and 3x4-style gamut-remap coefficient banks.
- MPC global state for clock gating, soft resets, CRC source/result capture, DPP pending status, composition output muxing, denormalization, bypass background color, and output CSC programming.
- Video/audio packet state for `AFMT5` and `VPG9`, including audio infoframes, IEC 60958 channel status, packet update requests, pending bits, CRC, ramp controls, ISRC/MPEG payload bytes, and memory power controls.
- Performance monitor state for two counter instances: selected events, trigger modes, clear/enable flags, current values, high/low counter reads, and state-machine/status fields.
- HPO/DP stream-mapper state that routes DP stream targets and gates/enables top-level HPO hardware.
- ABM/PWM state for four instances: requested and measured backlight levels, duty-cycle limits, ambient light input, adaptive contrast enhancement slope/threshold tables, histogram and luma statistics, sampling intervals, update locks/pending bits, missed-frame indicators, and master locks.
- The beginning of DPIA RBBM interface timeout-control state.

Persistence is hardware-defined. Configuration fields generally last until modeset, pipe/link reconfiguration, ABM disable, display-block power gating, suspend/resume, GPU reset, or driver reinitialization. Status, pending, conflict, missed-frame, clear, CRC, histogram, performance-counter, and power-state fields may be read-only, sticky, self-clearing, write-one-to-clear, or valid only while the relevant display clocks and power domains are active. This generated header does not express those access semantics; consuming code and the register specification must provide them.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.0 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h`, which provides matching MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c`, which directly includes `dcn_3_5_0_sh_mask.h` and the offset header for DCN 3.5 DMUB register table construction.
- DCN 3.5 resource and block headers that build register lists for MPC, AFMT, VPG, DME, HPO, DP stream mapping, performance monitoring, and ABM through token-pasted `reg`, `shift`, and `mask` names.
- Generic AMD display register helpers that combine offsets, base indexes, shifts, and masks for MMIO read/write/update operations.

The most direct behavioral integration points are display composition/color management, HDMI/DP audio packet formatting, secondary-data packet generation, HPO/DP stream routing, display performance diagnostics, CRC/debug capture, and panel power/backlight adaptation. The `ABM0`-`ABM3` fields integrate with firmware or driver backlight policy, while `AFMT5`/`VPG9` integrate with stream encoder paths for high-numbered display instances.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while modifying the wrong MMIO bits, corrupting adjacent fields, or silently breaking a specific display/audio/backlight path.
- The file is generated metadata. Manual edits risk divergence from AMD's authoritative register database, the matching offset header, firmware assumptions, and silicon documentation.
- The chunk begins and ends inside field groups. Line 44309 lacks the earlier shifts for `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25`, and line 46526 lacks the rest of `DPIA_MU_RBBMIF_TIMEOUT_CTRL`; reconciliation with adjacent chunks is required before making complete per-register claims.
- Repeated instances are copy-sensitive. `MPC_OUT0`-`MPC_OUT3`, `ABM0`-`ABM3`, and the perfmon instances have similar layouts, so a generator error may affect only one pipe, one output, one backlight block, or one high-numbered stream.
- Lock, update-pending, readback-double-buffer, frame-start-select, missed-frame, and clear bits are sequencing-sensitive. Using the wrong mask can leave stale ABM/ACE/PWM state, miss frame-boundary updates, or clear a diagnostic bit unintentionally.
- Audio/video packet fields are receiver-sensitive. Bad AFMT/VPG masks can cause invalid infoframes, wrong IEC 60958 channel status, broken audio CRC/ramp behavior, missing ISRC/MPEG packets, or update-pending bits that never clear.
- Color pipeline fields are visually high impact. Wrong OGAM/gamut-remap/CSC/denorm masks can produce color shifts, clipping, black output, or failures limited to HDR, color-managed, or multi-plane modes.
- Clock, reset, memory-power, timeout, and HPO enable fields are high risk because writes may be ignored or harmful when the block is power-gated, clock-disabled, reset, firmware-owned, or not present on a given ASIC stepping.

## Test Signals

Useful validation combines generated-header consistency checks with DCN 3.5 hardware behavior:

- Build AMDGPU display support with DCN 3.5 enabled. Missing or renamed macros should fail at compile time in DMUB/resource/block register-table construction.
- Mechanically verify field pairing in this range while allowing the two boundary exceptions: the first `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25` masks pair with shifts before line 44309, and `DPIA_MU_RBBMIF_TIMEOUT_CTRL__RBBMIF_TIMEOUT_DELAY__SHIFT` pairs with masks after line 46526.
- Diff this slice against AMD's authoritative DCN 3.5.0 register database and nearby generated headers where layout compatibility is expected.
- Exercise MPC composition and output color paths across plane enable/disable, multiple outputs, DWB use if supported, CRC capture, CSC/denorm changes, HDR/color-management transitions, and suspend/resume.
- Validate HDMI/DP audio and packet generation on high-numbered instances that can use `AFMT5` and `VPG9`: audio playback, IEC 60958 channel status, infoframes, generic packets, ISRC/MPEG metadata, CRC reporting, packet update timing, hotplug, modeset, and stream disable/enable.
- Test ABM/PWM behavior for all represented instances: brightness transitions, ambient/user/target levels, duty-cycle bounds, frame-start updates, double-buffer locks, ACE threshold/slope updates, histogram/luma readback, missed-frame clear behavior, and resume from low-power states.
- Exercise HPO/DP stream mapping and DME paths where supported, including link bring-up, stream assignment, display-clock gating transitions, metadata memory power states, and error recovery.
- Watch kernel logs, display diagnostics, and hardware counters for stuck update-pending bits, missed-frame flags, CRC mismatches, audio dropouts, color corruption, backlight jumps, perfmon counter anomalies, RBBMIF timeout reports, and resume-only failures.

## Cross-Chunk Notes

The previous chunk owns the start of `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_24_25`, including the missing shift macros for region 24/25 fields. The next chunk owns the rest of `DPIA_MU_RBBMIF_TIMEOUT_CTRL`, follow-on DPIA RBBMIF status fields, and then additional generated register families. The final per-file research document should merge adjacent chunks before making whole-file claims about all MPCC OGAM regions, all DPIA timeout/status fields, or the complete DCN 3.5.0 shift/mask namespace.
