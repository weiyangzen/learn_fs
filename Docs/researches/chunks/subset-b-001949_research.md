# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 49650-52098

## Purpose

This chunk is a generated AMDGPU DCN 3.2.0 register shift/mask header slice. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for Azalia/HD-audio codec and stream/endpoint register fields. Consumers combine these constants with the matching DCN 3.2.0 offset header and AMD display register helpers to compose, update, or decode MMIO register fields without hard-coded bit literals.

The range starts in the tail of an `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT_4` definition, covers F2 input-pin/root/function codec fields, defines repeated Azalia F0 stream latency blocks for streams 0 through 15, then defines endpoint codec converter and pin-control blocks for endpoints 0 through 3. The chunk ends partway through endpoint 3 audio descriptor fields. It defines 2,032 preprocessor constants: 1,017 shift constants and 1,015 mask constants across 21 generated `addressBlock` comments.

Although this source tree is under `ceph-client`, this file is AMDGPU display/audio hardware metadata, not distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocation paths, includes, or direct register accesses in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the low bit index of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or updating that field.
- `// addressBlock: ...`: generated grouping comments for indexed Azalia root, stream, and endpoint register banks.

The covered register groups are:

- F2 input-pin controls: channel allocation, multichannel 0 through 7 enable/mute/channel IDs, HBR capability/enable, LPIB snapshot/value/timer fields, input activity/status, channel layout, input infoframe, and channel-status low/high words.
- F2 input-pin and function parameters: audio widget capabilities, pin capabilities, root vendor/device ID, revision ID, subordinate node count, function power state, subsystem ID bytes, converter synchronization, codec reset, supported size/rate fields, stream formats, and power-state capability bits including `CLKSTOP` and `EPSS`.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated stream-indexed FIFO size and latency counter blocks. Each stream exposes minimum/maximum FIFO size, maximum latency support, latency counter reset, worst-case latency count, cumulative latency count, and cumulative request count.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT2`: complete endpoint-indexed F0 codec converter and pin-control blocks.
- `AZF0ENDPOINT3`: endpoint converter and pin capability/control fields through the beginning of `AUDIO_DESCRIPTOR8`; the rest of endpoint 3 continues in the next chunk.

Important endpoint field families include:

- Converter capabilities and format programming: audio widget capabilities, `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base divisor/multiple/rate, stream type, channel ID, stream ID, supported stream formats, and supported size/rate masks.
- Digital converter control: `DIGEN`, validity/configuration bits, pre-emphasis, copyright, non-audio/professional mode, category code, and keepalive.
- Stripe/ramp/GTC controls: stripe control/capability, ramp rate, presentation-time embedding enable/group, offset-changed indication, and GTC counter delta/current/min/max registers.
- Pin capabilities and state: HDMI/DP capability, VREF, EAPD, output enable, unsolicited response tag/enable, pin sense impedance, digital output active status, and coding type.
- Speaker, audio descriptor, and multichannel routing fields: speaker allocation, channel allocation, HDMI/DP connection flags, LFE playback level, level shift, downmix inhibit, descriptors 0 through 13 for endpoints 0 through 2, multichannel pair enables/mutes/channel IDs, odd-channel multichannel controls, and multichannel mode.
- Sink and default-configuration fields: manufacturer/product IDs, sink description length, port IDs, packed description bytes, sequence/default association/misc/color/connection type/default device/location/port connectivity.
- Event/status fields: hot-plug clock/audio fields, forced unsolicited response payload, format-changed flag/ack/reason/response, wireless display identification, remote keepalive, audio enable status, and audio enabled/disabled/format-changed interrupt flags, masks, and type bits.
- IEC 60958 channel-status overrides: mode/source number, clock accuracy, word length, sampling frequency, original sampling frequency, coefficient/MPEG surround/CGMS-A, and per-channel channel-number overrides.
- Audio position observation: LPIB snapshot lock, cyclic buffer wrap count, full 32-bit LPIB value, and full 32-bit LPIB timer snapshot.

## Control Flow

This header chunk has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, builds register tables, then uses AMD register read/write/update helpers to manipulate hardware fields.

The effective hardware flow represented by these fields is external to the header:

1. DCN 3.2 display/audio code selects an Azalia root, stream, or endpoint indexed register bank.
2. The matching offset macro supplies the register address or index/data selector.
3. A shift/mask macro from this header isolates, encodes, or updates the target field.
4. Higher-level audio code sequences codec reset/power state, converter format and stream IDs, digital converter state, pin/sink metadata, multichannel/HBR settings, unsolicited-response controls, LPIB snapshots, and interrupt/status handling.

The constants do not encode access type, ordering, volatility, polling delays, or side effects. Callers must still follow the hardware programming sequence for modeset, stream start/stop, hotplug, audio format changes, power gating, suspend/resume, and reset.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to memory, disk, or firmware. It describes MMIO-backed GPU state in DCN 3.2.0 Azalia audio hardware.

The represented hardware state includes:

- Advertised codec/root/function/pin/converter capabilities.
- Programmed audio stream state: sample format, channel count, stream type, stream ID, channel ID, digital converter flags, supported rates/formats, multichannel routing, HBR, and channel-status overrides.
- Sink and connector metadata: speaker/channel allocation, audio descriptors, sink manufacturer/product IDs, port IDs, textual sink description bytes, default pin configuration, HDMI/DP connection flags, and wireless display identification.
- Event and interrupt state: unsolicited response enable/force/tag, hot-plug audio enablement, audio enabled/disabled/format-changed flags, interrupt masks/types, format-change reason/response, and remote keepalive.
- Runtime counters and observations: per-stream latency counters, FIFO size capabilities, LPIB snapshot locks, cyclic-buffer wrap counts, LPIB values, LPIB timer snapshots, GTC counter deltas, and digital output activity.

Persistence is hardware-defined. Programmed configuration generally lasts until reprogramming, power gating, suspend/resume, modeset, or ASIC reset. Status and event fields may be read-only, sticky, latched, self-clearing, write-one-to-clear, or side-effectful depending on the actual register definition outside this generated mask file.

## Dependencies And Integration Points

This header depends only on the C preprocessor, but it must remain synchronized with the DCN 3.2.0 generated register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies matching register offsets and indexed-base metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c` includes this header to build DCN32 DMUB register mask/shift tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c` includes it while constructing DCN32 resource/register tables, including display/audio-related objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`, `display/dc/gpio/dcn32/hw_translate_dcn32.c`, `display/dc/gpio/dcn32/hw_factory_dcn32.c`, and `display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c` include the same offset/mask pair for DCN32 IRQ, GPIO, and clock-manager register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c` also includes the DCN 3.2.0 offset/mask pair for GPU memory-controller/display-adjacent register definitions.

Runtime audio integration is with the shared AMD display audio path under `display/dc/dce/dce_audio.c` and related headers. That code programs Azalia codec endpoint registers, hot-plug audio control, supported rates/formats, HBR/multichannel state, speaker/channel allocation, sink information, and audio descriptors through generic register tables rather than necessarily spelling every generated macro name directly.

The stream and endpoint numbering is significant. `AZF0STREAM0` through `AZF0STREAM15` are stream-indexed latency/FIFO resources. `AZF0ENDPOINT0` through `AZF0ENDPOINT3` are endpoint-indexed codec/pin resources, with endpoints 0 through 2 complete in this chunk and endpoint 3 split at the chunk boundary.

## Risks And Edge Cases

- Field drift is the main risk. These macros are untyped constants, so an incorrect bit position or mask can compile cleanly while programming or decoding the wrong hardware bits.
- The chunk starts mid-register and ends mid-endpoint. Adjacent chunks are required before making complete claims about `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT_4` or `AZF0ENDPOINT3`.
- Repeated stream and endpoint blocks are instance-specific. Copying an endpoint 0 macro into endpoint 1/2/3 code, or a stream 0 macro into another stream, can silently route programming or diagnostics to the wrong hardware instance.
- The stream latency counters and LPIB/GTC fields are timing-sensitive. Misusing snapshot locks, wrap counts, timer snapshots, or counter reset bits can produce wrong audio position accounting or race-prone diagnostics while a stream is active.
- Audio format and routing fields are user-visible. Bad masks for sample size/rate, stream type, channel count, stream ID, channel ID, channel allocation, multichannel routing, HBR, or speaker allocation can cause silence, distorted audio, channel swaps, or failures only in multichannel/HBR modes.
- Digital converter and IEC 60958 channel-status fields carry sink-visible metadata. Incorrect validity, non-audio/professional/copyright, category code, word length, sampling frequency, or channel-number bits can make sinks misinterpret the stream.
- Hotplug, unsolicited response, and audio enable/disable/format-change interrupt fields are event-sensitive. Incorrect masks can cause missed notifications, interrupt storms, stuck status, or resume-only audio failures.
- Side-effect fields such as reset, force unsolicited response, snapshot lock, interrupt flags, and clear/ack-style status bits should not be touched by broad read-modify-write code unless the caller intentionally masks them.

## Test Signals

Useful validation should combine generated-header checks with real display/audio behavior:

- Build AMDGPU with DCN32 enabled. Include or token-paste mismatches should surface in `dmub_dcn32.c`, `dcn32_resource.c`, IRQ/GPIO/clock-manager code, or shared register-table helpers.
- Mechanically verify that each register field in the repeated stream and endpoint schemas has the expected `__SHIFT`/`_MASK` pair, allowing for this chunk's partial first and last registers.
- Diff the repeated `AZF0STREAM0` through `AZF0STREAM15` layouts and `AZF0ENDPOINT0` through `AZF0ENDPOINT3` layouts against AMD's authoritative generated register database or neighboring DCN generations where compatibility is expected.
- Exercise HDMI/DP audio on DCN32 hardware across stereo PCM, multichannel PCM, multiple sample rates and bit depths, HBR-capable formats, stream start/stop, plug/unplug, blanking, modeset, suspend, and resume.
- Watch for no-sound-on-one-endpoint bugs, endpoint-specific channel swaps, incorrect ELD/sink description data, invalid speaker/channel allocation, hotplug notification storms, stuck audio enabled/disabled/format-change flags, missed unsolicited responses, and bad resume behavior.
- Use register traces or debug reads to confirm correct stream/endpoint instance selection, FIFO/latency counter behavior, LPIB snapshot stability, and GTC delta min/max tracking.

## Cross-Chunk Notes

This is chunk-level research for `dcn_3_2_0_sh_mask.h`. The final per-file report should merge this with the previous chunk for the beginning of the F2 input-pin configuration-default register and with the next chunk for the rest of `AZF0ENDPOINT3`, especially the remaining audio descriptors and subsequent endpoint-3 pin-control fields.
