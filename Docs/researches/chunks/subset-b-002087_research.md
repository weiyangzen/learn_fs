# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 1-2215

## Purpose

This chunk is generated AMD DCN 3.5.1 register field metadata. It contains no executable driver logic; it exposes C preprocessor constants that describe bit shifts and masks for hardware register fields. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with matching register offsets from `dcn_3_5_1_offset.h` and AMD display register helpers to read, write, update, and preserve fields in DCN 3.5.1 MMIO registers.

The requested range covers the beginning of `dcn_3_5_1_sh_mask.h`: license/header guard, Azalia controller command/response DMA ring fields, immediate command/response fields, DMA position buffer fields, top-level sink identity/description fields, Azalia input/output CRC fields, Azalia stream latency/FIFO counters for streams 0-15, complete Azalia F0 endpoint field layouts for endpoints 0-2, and the start of endpoint 3 through `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`.

Although this source tree is under a local `ceph-client` mirror, this file is AMD GPU display/audio hardware metadata. It has no Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, callbacks, locks, allocation paths, or direct I/O operations in this chunk. Its only exported interface is a generated macro namespace:

- `REGISTER__FIELD__SHIFT`: bit offset of `FIELD` inside `REGISTER`.
- `REGISTER__FIELD_MASK`: bit mask for the same field.

Major macro families in lines 1-2215:

- `AZCONTROLLER0_*`: HDA/Azalia controller CORB and RIRB queue fields, response interrupt count/control/status fields, immediate command output/input/status fields, and DMA position buffer base-address fields.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: sink manufacturer/product IDs, sink description length, two 32-bit port IDs, and byte-sized sink description storage.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*`: full 32-bit CRC fields for channels 0-7 across CRC groups 0 and 1.
- `AZF0STREAM0` through `AZF0STREAM15`: per-stream FIFO sizing fields (`MIN_FIFO_SIZE`, `MAX_FIFO_SIZE`, `MAX_LATENCY_SUPPORT`) and latency instrumentation (`AZALIA_LATENCY_COUNTER_RESET`, worst-case latency, cumulative latency, cumulative request count).
- `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, and `AZF0ENDPOINT2`: repeated endpoint converter and pin-control field layouts, including widget capabilities, converter format, channel/stream ID, digital converter control, supported formats/rates, stripe/ramp/GTC embedding controls, pin capabilities, unsolicited response controls, speaker/channel allocation, audio descriptors 0-13, multichannel enables, lipsync/HBR responses, sink info registers, hot-plug/audio enable control, configuration default response, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change status, remote keepalive, and audio enabled/disabled/format-changed interrupt status.
- `AZF0ENDPOINT3`: same repeated endpoint layout begins at line 1814 but this chunk ends in the middle of the channel-status override group, at `CODEC_CS_OVERRIDE_4`.

The macro names are intentionally long because they encode the hardware block, instance, register, field, and generated constant kind. They are usually consumed through token-pasting helpers rather than typed directly in ordinary C code.

## Control Flow

This header has no runtime control flow. The operational flow is supplied by the AMD display and audio code that includes this generated metadata:

1. A DCN 3.5.1 source file includes `dcn_3_5_1_offset.h` and `dcn_3_5_1_sh_mask.h`.
2. Register-list macros token-paste register and field names into offset, shift, and mask tables. For example, DCN 3.5.1 DMUB initialization uses `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)` after including this header.
3. Runtime paths call helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_2`, `REG_READ`, `AZ_REG_READ`, and `AZ_REG_WRITE`. Those helpers use the generated shift/mask constants to isolate a field and preserve unrelated bits.
4. Sequencing rules are entirely in the consumers. This chunk only defines where a field lives; it does not encode whether a field is read-only, write-one-to-clear, self-clearing, sticky, interrupt-status, or safe to touch while the audio/display block is clock-gated.

For Azalia endpoint access specifically, the audio code writes an endpoint register index and then reads or writes the indexed endpoint data register. The endpoint fields in this chunk define the bit layouts of the indexed endpoint data values.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes MMIO-backed GPU display/audio state.

Represented hardware state includes HDA CORB/RIRB queue pointers and enables, immediate codec command status, DMA position-buffer addresses, monitor/sink identity bytes, audio CRC observations, stream latency counters, converter sample/channel configuration, digital audio status bits, HDMI/DP speaker allocation, supported audio descriptors, hot-plug/audio enable state, lipsync/HBR response state, IEC 60958 channel-status overrides, LPIB snapshots, format-change status, and endpoint audio interrupt flags.

Persistence is hardware-defined. Configuration fields generally last until driver reprogramming, display/audio disable, block reset, power gating, suspend/resume, or ASIC reset. Counter/status fields may be read-only, clear-on-write, sticky, or self-clearing depending on the underlying register. Since the generated macros are untyped constants, the consuming driver must know ordering constraints for enabling audio, updating sink info, programming descriptors, toggling hot-plug/audio enable, clearing interrupt flags, and reading latency/CRC diagnostics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the corresponding register offsets and base-index selectors.

Representative integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which includes this header and builds DCN 3.5.1 shift/mask tables with `FD_MASK` and `FD_SHIFT`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes this header while constructing the DCN 3.5.1 resource pool and hardware block register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes this header for generated interrupt register metadata used by the DCN 3.5.1 IRQ service.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h`, whose `AUD_COMMON_REG_LIST` uses `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)` to bind endpoint instances to audio objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.c`, which programs endpoint-indexed Azalia fields for HBR capability, lipsync, hot-plug/audio enable, speaker/channel allocation, audio descriptors, sink info, configuration defaults, and supported stream formats.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These macros are untyped constants, so a wrong bit position can compile cleanly while silently writing the wrong hardware field.
- The Azalia controller fields drive command and response DMA rings. Incorrect CORB/RIRB pointer, reset, DMA enable, size, or interrupt masks can break codec command submission, lose responses, or cause audio initialization timeouts.
- Immediate command fields have busy/result-valid semantics. Wrong masks can make polling loops believe a command is complete too early or never complete.
- Sink metadata and audio descriptor fields feed HDMI/DP audio capability exposure. Incorrect masks can advertise wrong manufacturer/product data, speaker layout, supported rates, channel counts, HBR capability, or ELD-like sink description data to the audio stack.
- Repeated endpoint blocks are copy-sensitive. Endpoints 0-3 have nearly identical field layouts; an instance-specific typo may only affect one display/audio output.
- Stream latency and CRC fields are diagnostic. Bad masks may not break basic audio playback but can hide FIFO sizing, latency, CRC, or underrun-style problems.
- Hot-plug, unsolicited response, audio enable, audio disable, and format-change interrupt/status fields are ordering-sensitive. Incorrect masks can cause missed audio events, stale status, interrupt storms, or lost format-change acknowledgements.
- The chunk boundary is artificial. It ends inside endpoint 3 channel-status override fields, so later chunk research is required before making complete file-level claims about all endpoint 3 fields or endpoints 4-7.

## Test Signals

Useful validation signals combine generated-header consistency checks with hardware/audio behavior:

- Build AMDGPU/DC with DCN 3.5.1 enabled; missing or renamed macros should fail in DCN 3.5.1 DMUB, IRQ, resource, and audio register-table construction.
- Mechanically verify that every field in lines 1-2215 has the expected `__SHIFT` and `_MASK` pair, and that each mask aligns with its shift and apparent field width.
- Diff this chunk against AMD's authoritative DCN 3.5.1 register database and neighboring generated headers where identical Azalia layouts are expected.
- Exercise HDMI and DisplayPort audio bring-up across multiple connectors/endpoints, including hotplug, modeset, audio enable/disable, suspend/resume, and display power-gating transitions.
- Validate codec command paths that use CORB/RIRB and immediate commands by checking for command timeouts, invalid responses, or stuck busy/result-valid bits.
- Test EDID/ELD-driven audio configuration: supported rates, bit depths, channel counts, speaker allocation, HBR exposure, sink description bytes, manufacturer/product IDs, and port IDs.
- Exercise format changes while audio is active and watch audio enabled/disabled/format-changed interrupt status, unsolicited response behavior, and kernel logs for missed or repeated events.
- Read diagnostics for CRC, latency counter reset, worst-case latency, cumulative latency, and cumulative request counts across multiple streams.
- Listen for user-visible failures: no HDMI/DP audio device, wrong channel mapping, missing multichannel formats, HBR failures, audio dropouts, lipsync anomalies, stuck hotplug/audio enable state, or regressions limited to a single endpoint.

## Cross-Chunk Notes

This is the first chunk of `dcn_3_5_1_sh_mask.h`. Later chunks continue endpoint 3 after `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_4`, then cover the rest of the generated DCN 3.5.1 register field map. The final per-file document should merge adjacent chunks before making complete claims about all Azalia endpoints, all audio interrupt fields, or the full DCN 3.5.1 mask/shift surface.
