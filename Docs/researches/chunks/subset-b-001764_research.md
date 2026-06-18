# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 32315-34689

## Purpose

This chunk is generated AMDGPU DCN 3.0.2 display-controller register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and bit masks inside DCN 3.0.2 MMIO registers. Consumers pair these constants with register offsets from `dcn_3_0_2_offset.h` and then use AMD display register helpers to read, update, poll, and write display hardware state.

The range is a mid-file slice. It starts at the final mask entry for `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`, covers the remaining `DP_AUX1` DPHY/GTC/wake fields, then covers complete `DP_AUX2`, `DP_AUX3`, and `DP_AUX4` AUX blocks. It then covers the instance-0 stream-output families: `VPG0`, `AFMT0`, `DME0`, `DIG0`, and the beginning of `DP0`, ending with the complete `DP0_DP_DPHY_FAST_TRAINING_STATUS` register fields just before `DP0_DP_SEC_CNTL`.

Although this repository path is under a local `ceph-client` source tree, this file is AMD display-driver hardware metadata. It has no distributed filesystem protocol behavior and no Ceph persistence semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this chunk. The API surface is the generated macro namespace:

- `REGISTER__FIELD__SHIFT`: the least-significant-bit position for a field.
- `REGISTER__FIELD_MASK`: the already-positioned bit mask for that field.

The macros are consumed through higher-level register-description macros such as `SF`, `SE_SF`, `AUX_SF`, `LE_SF`, and driver helpers including `REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_SET`, `REG_GET`, and `REG_WAIT`. The generated constants are therefore an ABI-like contract between the ASIC register database and the DCN 3.0.2 display code.

Major field families in this range:

- `DP_AUX1` tail: DPHY TX/RX timing and status, GTC sync control/error/status, and AUX PHY wake handshaking.
- `DP_AUX2`, `DP_AUX3`, `DP_AUX4`: AUX enable/reset, low-speed read control, HPD selection, mode detection, impedance calibration request, arbitration, interrupt masking/ack/status, software AUX status and data, low-speed AUX status and data, DPHY TX/RX controls, GTC sync controls and errors, and PHY wake fields.
- `VPG0`: generic packet access/data bytes, conflict status/clear, generic-stream-packet frame-update and immediate-update bits for packet slots 0-14, generic packet memory power, ISRC access/data, and MPEG info packet fields.
- `AFMT0`: VBI and audio packet controls, audio channel enable/layout/oversampling overrides, HDMI/DP audio info bytes, IEC 60958 channel-status words, audio CRC controls/results, ramp controls, audio source selection, infoframe update, status, and AFMT memory power.
- `DME0`: DME enable/reset/ready, indirect index/data controls, register read/write controls, and DME memory power state.
- `DIG0`: stream encoder front-end and back-end fields, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, generic packet line/send/continuous flags, gamut/control packet fields, TMDS control characters/sync/DC-balancer generation, FIFO status, CRC/test/random pattern controls, lane enablement, and forced DIG disable.
- `DP0`: DisplayPort link training completion, pixel format, MSA colorimetry/misc/timing/VBID, stream enable/status/deferred disable, steer FIFO overflow/ack bits, video `M/N`, link framing, HBR2 eye pattern, video interrupt clear/mask, DPHY FEC/bypass/training-pattern/symbol/8b10b/PRBS/scrambler/CRC/MST CRC/fast-training fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. `dcn302_resource.c` includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h` file.
2. Resource construction macros paste register and field names into constants, for example `SRI(AUX_CONTROL, DP_AUX, id)` for addresses and `DCN_AUX_MASK_SH_LIST(__SHIFT)` or `DCN_AUX_MASK_SH_LIST(_MASK)` for AUX field tables.
3. VPG, AFMT, stream encoder, link encoder, and AUX objects receive per-block register addresses plus shift/mask tables.
4. Operational code uses those tables to perform read-modify-write updates, waits, status decoding, and error checks while programming connectors, AUX transactions, info packets, audio, HDMI/TMDS output, DisplayPort streams, and link training.

The macros do not encode safe ordering. Consumers must still handle reset sequencing, HPD/AUX arbitration, AUX transaction timeout handling, stream enable/disable waits, HDMI/DP packet update timing, AFMT memory power, link training, FEC state, CRC capture, and interrupt acknowledge behavior.

## State And Persistence Behavior

The chunk stores no software state and persists nothing on its own. It describes packed fields in GPU MMIO registers. The represented hardware state includes:

- AUX channel configuration, reset status, HPD routing, transaction status, reply/error bits, software and low-speed data bytes, DPHY timing/status, GTC sync lock/error state, and wake handshakes.
- VPG packet RAM access state, generic packet payload bytes, packet update triggers, conflict status, memory power state, ISRC data, and MPEG infoframe data.
- AFMT audio and infoframe state, including audio source, channel mapping, packet send/mute controls, IEC 60958 channel status, CRC test state, and memory power controls.
- DIG/HDMI/TMDS stream-encoder state for front-end source selection, start/stop, back-end enable, audio/video packet generation, ACR values and status, generic packet scheduling, test patterns, FIFO status, lane enable, TMDS symbol generation, and forced disable.
- DP0 link and stream state for link-training completion, stream enable/status, timing/colorimetry payloads, DPHY training/test generation, FEC status, PRBS/scrambler controls, CRC results, MST CRC phase status, and fast-training completion/ack bits.

Persistence is hardware-defined. Configuration fields typically retain values until a modeset, link reconfiguration, power-gating event, suspend/resume path, firmware action, or ASIC reset changes them. Status, interrupt, clear, ack, timeout, CRC, conflict, wake, and reset-done fields can be sticky, self-clearing, read-only, write-one-to-clear, or sequencing-sensitive. This generated header only defines bit layout; access semantics come from hardware documentation and the consuming AMD display code.

## Dependencies And Integration Points

The direct dependency is the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_offset.h`

The direct include point found in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn302/dcn302_resource.c`

Important consumer-side integration points include:

- `dcn302_resource.c`: builds DCN 3.0.2 resource tables, including AUX engines, link encoders, stream encoders, VPG, AFMT, and related display blocks.
- `dce/dce_aux.h` and `dce/dce_aux.c`: define AUX register and field lists, then use AUX status/error fields such as `AUX_SW_DONE`, `AUX_SW_REPLY_BYTE_COUNT`, timeout, invalid-stop, no-detect, HPD-disconnect, and NACK fields to drive DPCD/EDID AUX transactions.
- `dce/dce_link_encoder.h`, `dce/dce_link_encoder.c`, and `dio/dcn10/dcn10_link_encoder.h`: consume AUX, DP link, DP fast-training, and link-encoder fields for HPD routing, low-speed AUX reads, link training completion, stream disable, and fast training.
- `dce/dce_stream_encoder.h` and `dce/dce_stream_encoder.c`: consume `DIG0` and `DP0` stream fields for HDMI generic packets, DP stream enable/status waits, TMDS pixel/color format, DIG source selection, stereosync, and info packet scheduling.
- `dcn30/dcn30_vpg.h` and `dcn30/dcn30_vpg.c`: consume `VPG0` fields for generic packet data writes, conflict polling/clearing, and per-packet frame or immediate updates.
- `dcn30/dcn30_afmt.h` and `dcn30/dcn30_afmt.c`: consume `AFMT0` fields for audio source selection, channel enablement, IEC 60958 channel status, audio sample send/mute, audio-info update, and AFMT power behavior.

The generated file also depends on naming stability across AMD's register-generation pipeline. The consumer macros assume instance-0 field names such as `DP_AUX0_AUX_CONTROL__AUX_RESET_MASK`, `VPG0_VPG_GENERIC_PACKET_DATA__VPG_GENERIC_DATA_BYTE0_MASK`, `AFMT0_AFMT_AUDIO_PACKET_CONTROL__AFMT_AUDIO_SAMPLE_SEND_MASK`, `DIG0_DIG_FE_CNTL__DIG_START_MASK`, and `DP0_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK` exist and have compatible field positions for all repeated hardware instances described by the register tables.

## Risks And Edge Cases

- Wrong shifts or masks compile cleanly but cause silent hardware misprogramming. A bad mask can corrupt neighboring fields in packed MMIO registers, while a bad shift can decode status incorrectly or write an intended value into the wrong bit lane.
- Chunk boundaries are artificial. The first line is only the last mask of `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`; its matching shifts and earlier masks are in the previous chunk. The next chunk starts with `DP0_DP_SEC_CNTL`. File-level conclusions must merge adjacent chunks.
- AUX fields are side-effect-sensitive. Incorrect reset, HPD selection, timeout, reply-byte-count, NACK, invalid-start/stop, overflow, arbitration, interrupt ack, or wake fields can break EDID reads, DPCD access, hotplug, link training, panel wake, or low-power resume.
- Repeated AUX instances are copy-sensitive. This chunk covers full `DP_AUX2` through `DP_AUX4`, and DCN 3.0.2 resources expose five AUX engines. A field drift in one repeated block may only appear on particular connectors or board routings.
- VPG packet update fields are timing-sensitive. Incorrect immediate/frame update masks, conflict clear/status bits, data index fields, or payload byte masks can corrupt HDMI/DP infoframes and metadata without necessarily causing a modeset failure.
- AFMT audio fields can fail as audio-only regressions. Bad IEC 60958 channel-number fields, audio source selection, sample-send, channel-enable, layout override, or memory power masks can cause silence, wrong channel mapping, or intermittent audio while video remains functional.
- DIG/HDMI/TMDS fields are broad and packed. Generic packet controls, ACR values, TMDS symbol generation, FIFO status, lane enable, source selection, and forced-disable fields affect HDMI display bring-up, color format, stereo sync, packet scheduling, and test modes.
- DP0 stream and DPHY fields interact with link state outside this header. Bad masks for `DP_LINK_TRAINING_COMPLETE`, stream enable/status, FEC, scrambler, PRBS, CRC, or fast-training status can produce blank displays, link retraining loops, CRC false positives, or failures limited to specific link rates, lane counts, MST paths, or panels.
- Some generated fields contain `MASK` as part of the field name, for example `DPHY_FAST_TRAINING_COMPLETE_MASK`. Consumers and validation scripts must distinguish the field name from the `_MASK` suffix when checking shift/mask pairs.

## Test Signals

Useful validation combines generated-header consistency with display hardware behavior:

- Build the AMDGPU display driver with DCN 3.0.2 support enabled. Missing or renamed macros should fail where `dcn302_resource.c`, AUX, link-encoder, stream-encoder, VPG, and AFMT tables are initialized.
- Mechanically verify that every field in lines 32315-34689 has the expected shift/mask pair after accounting for the artificial chunk start at the tail of `DP_AUX1_AUX_DPHY_TX_REF_CONTROL`.
- Diff the chunk against AMD's authoritative DCN 3.0.2 register database and nearby compatible generated headers, especially `dcn_3_0_0_sh_mask.h` and later DCN 3.x headers where unchanged hardware blocks are expected.
- Exercise all exposed AUX engines on DCN 3.0.2 hardware: HPD detection, EDID reads, DPCD reads/writes, AUX retry paths, timeout and disconnect handling, suspend/resume, and low-power wake.
- Test connector diversity and instance coverage: use systems or boards that route displays through high-numbered AUX/link/stream instances, not only instance 0.
- Validate HDMI output with audio and metadata: modeset, color format changes, generic packets, infoframes, ACR behavior, audio channel layout, mute/unmute, IEC 60958 status, and suspend/resume.
- Validate DP output: link training, fast training, link-rate and lane-count changes, stream enable/disable, MST where supported, FEC where supported, CRC capture, scrambler/PRBS test paths, and hotplug under load.
- Watch kernel logs and display diagnostics for AUX timeout/NACK/HPD-disconnect errors, link training failures, stuck `DP_VID_STREAM_STATUS`, packet conflicts, audio dropouts, FIFO/CRC errors, and resume regressions.

## Cross-Chunk Notes

Previous chunks own the beginning of the `DP_AUX1` block and the earlier DCN 3.0.2 field namespace. This chunk begins in the middle of `DP_AUX1_AUX_DPHY_TX_REF_CONTROL` and then covers `DP_AUX2` through `DP_AUX4` plus the first instance-0 stream/link blocks. The following chunk continues the `DP0` secondary-data packet and later DisplayPort fields. The final per-file research document should merge adjacent chunks before making complete claims about all AUX channels, all stream encoder instances, or the full DCN 3.0.2 link register surface.
