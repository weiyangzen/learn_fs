# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 34941-37351

## Purpose

This chunk is a generated AMD DCN 3.2.0 shift/mask header segment. It contains no executable C logic; it publishes preprocessor constants that describe hardware register bit positions (`__SHIFT`) and bit masks (`_MASK`) for parts of the display I/O pipeline. Consumers combine these constants with `dcn_3_2_0_offset.h` and AMD display register helper macros to read, compose, update, and decode MMIO fields.

The range starts in the middle of the `DIG4_HDMI_CONTROL` definition, then covers the rest of the DIG4 HDMI/TMDS display encoder fields, complete AFMT audio formatter blocks for DIG0 through DIG4, complete DME metadata-engine and VPG video-packet-generator blocks for DIG0 through DIG4, and ends at the first few shift fields for `DP_AUX0_AUX_CONTROL`. The chunk defines 2,164 generated constants: 1,083 shift constants and 1,081 mask constants. The slight mismatch is because the range starts and ends mid-register.

Although the repository path is under `ceph-client`, this file is AMDGPU display hardware metadata, not distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocations, includes, or direct register accesses in this chunk. The public surface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: low bit index of a field inside a hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating or updating that field.
- `// addressBlock: ...`: generated grouping comments that map repeated register blocks to DCN display I/O instances.

Covered register groups include:

- DIG4 HDMI and TMDS encoder controls: `HDMI_STATUS`, `HDMI_AUDIO_PACKET_CONTROL`, ACR packet controls and status, VBI/infoframe/generic-packet controls for generic packets 0 through 14, HDMI double-buffer control, general-control packet AVMUTE/packing fields, AFMT clock enable/status, DIG back-end enable/source/mode/HPD selection, TMDS sync/control-character fields, DC balancer fields, CTL generator fields, `DIG_VERSION`, and `FORCE_DIG_DISABLE`.
- AFMT0 through AFMT4 audio formatter blocks: HDMI audio packet-per-line controls, audio layout/channel/DP stream ID/HBR overrides, audio infoframe payload fields, IEC 60958 channel-status fields, audio CRC control/result fields, ramp/test pattern controls, formatter status, audio sample send/double-buffer/reset/test/overflow/channel-swap/update/blanking controls, audio infoframe source/update, audio source select, and AFMT memory power state.
- DME0 through DME4 metadata-engine blocks: `DME_CONTROL` fields for HUBP requester selection, engine enable, stream type, metadata double-buffer pending/taken/clear/disable, and missed-transmission status/clear; plus `DME_MEMORY_CONTROL` fields for memory power force/disable/state/default low-power state.
- VPG0 through VPG4 video packet generator blocks: generic packet data index and byte lanes, frame-update and immediate-update triggers plus pending bits for generic packets 0 through 14, generic lock/conflict status and conflict clear, GSP memory light-sleep/power state, ISRC 1/2 indexed data access, and MPEG infoframe payload/update fields.
- Start of DP AUX0: only the first `DP_AUX0_AUX_CONTROL` shift fields through `AUX_IGNORE_HPD_DISCON` are inside this chunk; the remaining AUX shifts and masks are in the following chunk.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by AMD display code that includes the generated offset and shift/mask headers, builds register tables with token-pasting macros, and then calls helpers such as `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, and `REG_WAIT`.

Typical use outside the header is:

1. DCN 3.2 display resource code selects an encoder, AFMT, DME, VPG, or AUX instance.
2. The matching offset macro supplies the MMIO register address or indexed base.
3. The shift/mask macro from this header isolates or updates a field.
4. Higher-level code sequences HDMI/DP bring-up, audio formatter programming, secondary-data-packet transmission, dynamic metadata updates, memory power state transitions, or AUX reset/enable handling.

For example, `dcn32_dio_stream_encoder.c` updates HDMI scrambling, VBI packets, audio infoframe send/line fields, and AVMUTE through generic register helpers. AFMT and VPG object constructors use the repeated instance register and mask/shift tables defined in shared DCN3 headers, where the instance-0 field names from this generated file seed per-instance tables.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk, memory, or firmware. It describes MMIO-backed GPU state in DCN 3.2.0 hardware.

The represented hardware state includes:

- HDMI/DIG/TMDS encoder state for packet generation, scrambling, deep color, null/general-control/audio/ACR/infoframe/generic-packet send modes, line scheduling, pending updates, AVMUTE, back-end enable, source selection, output mode, HPD routing, TMDS control symbols, and test/feedback fields.
- AFMT state for audio packet layout, channel enable masks, DP audio stream ID, HBR/60958 overrides, HDMI audio infoframe payload, IEC 60958 channel status, audio CRC/test/ramp behavior, audio FIFO overflow and audio-enable change acknowledgement, audio source selection, and formatter memory power.
- DME state for dynamic metadata transport, including metadata stream type, double-buffering handshake, missed-transmission status, and memory power management.
- VPG state for generic secondary data packet payload bytes, frame/immediate update requests, update-pending bits, conflict status, ISRC payload bytes, MPEG infoframe payload/update, and VPG memory power state.
- The beginning of DP AUX0 control state for enable/reset, reset done, light-sleep read/update behavior, and ignoring HPD disconnect.

Persistence is hardware-defined. Programmed values normally survive until reprogramming, modeset, stream disable, power gating, suspend/resume, or ASIC reset. Status, pending, clear, done, and acknowledgement fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive depending on the underlying register definition; this generated header does not encode those access semantics.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the DCN 3.2.0 generated register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies matching register offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` directly includes this header and initializes DMUB DCN32 register masks/shifts with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c` also directly includes this header for DCN32 clock-manager mask/shift tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.c` is a runtime consumer of the same HDMI/DIG field names via stream-encoder register tables and register helper macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_vpg.h` define AFMT and VPG register/mask/shift table layouts that rely on generated `AFMT0_*` and `VPG0_*` field names.

Integration is mostly indirect through resource construction for DCN display blocks. The generated constants are not a standalone API; they are schema inputs for per-ASIC register tables used by stream encoders, audio formatter objects, VPG packet programming, DMUB service code, and AUX/link-management code.

## Risks And Edge Cases

- Field drift is the main risk. These are untyped preprocessor constants, so an incorrect shift or mask can compile cleanly while programming the wrong hardware bits.
- The chunk starts mid-register at `DIG4_HDMI_CONTROL`, so adjacent chunk `subset-b-001942` is needed to fully analyze that register. It also ends mid-register at `DP_AUX0_AUX_CONTROL`, so the next chunk is needed for complete AUX0 coverage.
- DIG4-specific HDMI/TMDS errors may appear only on one physical/logical encoder. A bad DIG4 packet-control, source-select, mode, HPD, or TMDS field can be connector-specific and difficult to reproduce on systems that do not route through DIG4.
- HDMI packet and generic-packet controls are update-sensitive. Wrong send/continuous/immediate/pending/line-reference masks can cause missing audio infoframes, stale metadata, incorrect AVMUTE behavior, packet timing errors, or double-buffer updates that never take effect.
- AFMT fields are user-visible through audio behavior. Bad masks for channel enable, stream ID, HBR, 60958 channel status, audio sample send, FIFO overflow ACK, or audio-info update can produce silence, wrong channel mapping, HBR-only failures, malformed audio infoframes, or resume-only audio regressions.
- DME double-buffer and missed-transmission fields affect dynamic metadata delivery. Incorrect masks can lose HDR/vendor metadata updates, report false missed transmissions, or leave metadata buffers stuck pending/taken.
- VPG generic packet update and pending fields are highly repetitive across packets 0 through 14 and instances 0 through 4. A generation error in one lane can affect only a subset of secondary data packets or a subset of display paths.
- Memory power fields for AFMT, DME, and VPG interact with low-power states. Bad masks can leave blocks powered when idle, power them down while still in use, or misread power state during suspend/resume sequences.
- The partial AUX0 coverage at the end should not be treated as a complete AUX control definition; mask definitions begin after this chunk.

## Test Signals

Useful validation should combine generated-header consistency checks with hardware-facing display tests:

- Build AMDGPU display code with DCN32 enabled. Include or token-paste mismatches should surface in `dmub_dcn32.c`, `dcn32_clk_mgr.c`, stream encoder code, AFMT/VPG resource tables, or register-helper initializers.
- Mechanically verify that generated fields in this range have expected `__SHIFT`/`_MASK` pairs where the range contains both sides, and account for the intentional partial pairs at the start and end of the chunk.
- Diff repeated AFMT0-4, DME0-4, and VPG0-4 layouts against each other and against AMD's authoritative DCN 3.2 register database where identical instance geometry is expected.
- Exercise HDMI on a DCN32 system using DIG4 when possible: modesets, deep color, scrambling, AVMUTE, audio infoframes, generic packets, and plug/unplug.
- Exercise DP/HDMI audio across stereo, multichannel PCM, multiple sample rates/depths, HBR-capable formats, audio mute/unmute, stream start/stop, suspend/resume, and modeset transitions.
- Exercise metadata and packet paths: HDR/vendor metadata updates through DME/VPG, ISRC/MPEG/generic packet payload updates, immediate and frame-synchronized updates, and repeated updates while a stream is active.
- Watch for connector-specific no-audio, stale/missing infoframes, wrong channel allocation, packet conflict status, generic update pending bits that never clear, metadata missed-transmission indications, AUX reset/enable failures in the following chunk, and power-state regressions around AFMT/DME/VPG memory controls.

## Cross-Chunk Notes

This is a middle chunk of the very large `dcn_3_2_0_sh_mask.h` generated header. It should be merged with adjacent chunks before making complete claims about `DIG4_HDMI_CONTROL` or `DP_AUX0_AUX_CONTROL`. The final per-file report should also reconcile this segment with later chunks that continue VPG instances beyond VPG4 and complete the DP AUX register block family.
