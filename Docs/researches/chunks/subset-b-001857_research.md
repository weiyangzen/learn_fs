# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 58976-61482

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it publishes preprocessor constants for field shifts and bit masks used to pack and unpack 32-bit MMIO register fields in the display controller.

The requested range covers 2,118 `#define` lines, split evenly between 1,059 `__SHIFT` constants and 1,059 `_MASK` constants. It starts inside the MPC RMU0 shaper RAM A region table, covers the rest of RMU0 shaper RAM A and RAM B metadata, complete RMU0/RMU1 3D LUT and shaper metadata, DC performance monitor blocks 22 and 23, HPO HDMI/DP packet and stream-mapper blocks, and most of ABM instances 0 through 3. The final line stops inside `ABM3_DC_ABM1_ACE_OFFSET_SLOPE_3`, so later chunks are needed for the rest of ABM3.

Although this file lives under a local `ceph-client` source mirror, this is AMDGPU display-driver hardware metadata, not Ceph or distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. Its interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major register families in this slice:

- `MPC_RMU0_*` and `MPC_RMU1_*`: gamut/remap unit shaper LUT controls, RAM A/RAM B piecewise curve region descriptors, channel start/end controls, 3D LUT mode/index/data/read-write controls, output normalization, and per-channel output offsets.
- `DC_PERFMON22_*` and `DC_PERFMON23_*`: display performance counter select, clear, start, stop, state, mode, counter value, and threshold/mask fields.
- `AFMT5_*`: HDMI/audio formatter fields for VBI/audio packet controls, channel status words, audio infoframes, audio CRC, audio ramp generation, status, source select, infoframe update, and AFMT memory power.
- `VPG9_*`: video packet generator fields for generic packet indexed access, 15 frame-update bits, 15 immediate-update bits, conflict status/clear, memory power, ISRC data, and MPEG info.
- `DME9_*`: Display Micro Engine control and memory-control fields.
- `HPO_TOP_*`: high-performance output clock-gating/test-clock and HPO IO enable fields.
- `DP_STREAM_MAPPER_CONTROL0` through `CONTROL3`: DP stream-to-link target fields.
- `ABM0_*`, `ABM1_*`, `ABM2_*`, and partial `ABM3_*`: adaptive backlight/PWM registers, ABM enable and bypass, IPCSC coefficient select, ACE slope/offset and threshold fields, HGLS read-progress and lock fields, histogram/luma-stat controls and results, sample-rate controls, and master-lock fields.

Several patterns repeat with fixed field widths. RMU shaper region registers pack two regions per 32-bit register: low-region LUT offset at shift `0x0`, low-region segment count at `0xc`, high-region LUT offset at `0x10`, and high-region segment count at `0x1c`. ABM PWM level registers expose 17-bit duty/level values. Many result/data registers are full-width `0xFFFFFFFF` payload fields.

## Control Flow

This header has no runtime control flow. The runtime path is supplied by DCN register helper code:

1. DCN 3.1.4 resource, IRQ, and DMUB files include `dcn_3_1_4_offset.h` together with this `dcn_3_1_4_sh_mask.h`.
2. Resource construction builds register address tables from the offset header and field tables from this mask header. For example, `dcn314_resource.c` defines `SR`, `SRI`, `SRII`, and `SRII_MPC_RMU` token-pasting helpers, then fills MPC RMU register tables with `MPC_RMU_REG_LIST_DCN3AG(0)` and `(1)`.
3. Block-specific headers map these generated constants into typed shift/mask structs using macros such as `SF`, `SE_SF`, `HWS_SF`, and `ABM_SF`.
4. Driver code later uses `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET_*`, `REG_GET`, and polling helpers. Those helpers combine the register address, field shift, and field mask from the generated tables.

The chunk itself does not encode sequencing. Consumers must still handle ordering around display clocking, memory power, double-buffered updates, vblank/frame boundaries, link state, histogram-read timing, ABM firmware interaction, and performance-counter start/clear/read ordering.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes MMIO-backed GPU state.

The represented hardware state includes:

- RMU shaper and 3D LUT programming for color pipeline remap, including RAM bank selection, LUT write enable masks, mode/current-mode fields, and per-region curve descriptors.
- Display performance monitor configuration and counters, including selected event IDs, counter state, clear/start/stop controls, overflow/threshold status, and high/low counter value registers.
- HDMI/DP secondary-data packet generation state through AFMT and VPG fields, including audio infoframes, channel-status words, generic packets, ISRC/MPEG packets, conflict status, and packet update timing.
- HPO output control, stream mapper selection, clock-gating control, and DME/VPG/AFMT memory-power state.
- ABM/PWM state for ambient/user/current/target/final/minimum backlight levels, ABM enable/bypass flags, histogram and luma-stat sampling, ACE curve parameters, result registers, and register-lock/update-pending bits.

Persistence is hardware-defined. Configuration registers generally retain values until modeset, power gating, suspend/resume, or ASIC reset. Status/counter/result/clear fields may be read-only, sticky, self-clearing, write-one-to-clear, or updated by hardware at frame/sample cadence. This generated header does not mark those side effects; the consuming block code and hardware programming guides determine safe access sequences.

## Dependencies And Integration Points

This chunk must match the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`

Direct include sites for the DCN 3.1.4 generated headers in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`

Important consumer modules and contracts:

- `display/dc/mpc/dcn30/dcn30_mpc.c` uses the RMU shaper and 3D LUT fields while programming transfer functions, region descriptors, RAM A/B selection, LUT index/data ports, and read/write control.
- `display/dc/mpc/dcn30/dcn30_mpc.h` defines the MPC RMU register, shift, and mask field lists that consume `MPC_RMU*_...` macros from this chunk.
- `display/dc/dce/dce_abm.c` and `display/dc/dce/dmub_abm_lcd.c` write ABM sample-rate, histogram/luma-stat, IPCSC, PWM level, and read-progress fields; DMUB command paths also use ABM state for firmware-mediated backlight control.
- `display/dc/dce/dce_abm.h` maps ABM fields into register lists and shift/mask structs with `ABM_SF`.
- `display/dc/dcn31/dcn31_afmt.h` and `.c` consume AFMT audio/packet/memory-power fields.
- `display/dc/dcn31/dcn31_vpg.h` and `.c` consume VPG generic-packet, update, status, and memory-power fields.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and `.c` consume `DP_STREAM_MAPPER_CONTROL*` fields to route DP streams to HPO links.
- `dcn314_resource.c` includes HPO clock and IO fields in `HWSEQ_DCN31_MASK_SH_LIST`, tying `HPO_TOP_CLOCK_CONTROL` and `HPO_TOP_HW_CONTROL` into hardware sequencing.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These constants are untyped preprocessor values, so an incorrect mask can compile cleanly while corrupting adjacent MMIO fields.
- Generated namespaces are copy-sensitive. RMU0/RMU1, ABM0-ABM3, and performance monitor 22/23 are structurally similar but instance-specific; a wrong instance prefix may only fail on a particular pipe, link, or panel.
- The chunk boundaries are artificial. The first visible line is the tail of `MPC_RMU0_SHAPER_RAMA_REGION_12_13`, and the final lines stop inside ABM3 ACE offset/slope registers.
- RMU shaper/3D LUT programming is stateful. Wrong RAM bank selection, write-enable mask, LUT index/data field, or region descriptor can produce color corruption, failed color management, or a transient glitch during modeset.
- ABM fields have frame/sample cadence and firmware interactions. Incorrect sample-rate, read-progress clear, lock, or PWM fields can cause stale histogram/luma data, missed-frame flags, brightness jumps, or conflicts with DMUB-controlled ABM updates.
- AFMT/VPG packet update fields are timing-sensitive. Incorrect update masks or memory-power fields can cause missing HDMI/DP infoframes, audio loss, metadata corruption, or packet conflicts.
- HPO and stream-mapper fields affect link routing and clocks. Bad masks can route a DP stream to the wrong link target or leave HPO IO/stream clocks disabled.
- Perfmon fields mix control, state, counters, and clear bits. Incorrect masks can silently invalidate diagnostics or leave counters stuck/overflowing.

## Test Signals

Useful validation combines generated-header consistency, compile coverage, and hardware behavior:

- Build AMDGPU display code with DCN 3.1.4 enabled; resource, IRQ, DMUB, MPC, ABM, AFMT, VPG, and HPO consumers should compile without missing or renamed shift/mask symbols.
- Mechanically verify that every field in lines 58976-61482 has exactly one `__SHIFT` and one `_MASK` define, and that field names match the companion `dcn_3_1_4_offset.h` register names.
- Diff the chunk against AMD's authoritative DCN 3.1.4 register database or adjacent generated DCN 3.x headers where register compatibility is expected.
- Exercise color-management paths that program RMU shaper and 3D LUT state, including modesets, gamma/degamma changes, HDR/color transforms, suspend/resume, and multi-plane composition.
- Exercise ABM/backlight paths on panels that support adaptive backlight: enable/disable ABM, change user brightness, read current/target levels, verify histogram/luma-stat updates, and test suspend/resume.
- Exercise HDMI/DP audio and metadata paths: audio playback, infoframes, generic packets, ISRC/MPEG metadata, packet update timing, and memory power transitions.
- Exercise HPO DP stream mapping with multiple links/streams, link training, hotplug, MST or high-bandwidth modes when available.
- Use perfmon/debug tools to confirm counters can be selected, cleared, started, stopped, and read without stuck state or bogus overflow/threshold status.
- Watch kernel logs and display diagnostics for blank displays, color corruption, audio dropouts, packet conflicts, ABM missed-frame flags, brightness jumps, link-routing failures, stuck interrupts, and resume regressions.

## Cross-Chunk Notes

Previous chunks own the beginning of RMU0 shaper RAM A, including regions before the visible `REGION_12_13` tail. Later chunks finish ABM3 and continue the remaining DCN 3.1.4 shift/mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all MPC RMU fields, all ABM3 registers, or the complete `dcn_3_1_4_sh_mask.h` hardware map.
