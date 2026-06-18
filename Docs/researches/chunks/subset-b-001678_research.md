# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 54267-56533

## Purpose

This chunk is part of AMD's generated DCN 2.1 ASIC register field mask header. It does not define functions or runtime logic; it defines `#define` constants for bit shifts and masks used when reading or programming Azalia/HD-audio codec registers through the display controller register access layer.

The covered lines span the tail of the `azf0endpoint7` output pin-control block and most of the repeated `azf0inputendpointN_inputendpointind` input endpoint blocks for endpoints 0 through 7. The constants describe HDMI/DisplayPort audio capabilities, audio stream format fields, channel mapping, hot-plug/audio-enable status, unsolicited response signaling, LPIB snapshots, IEC 60958 channel-status overrides, and input audio infoframe/status fields.

## Important Definitions

- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR7..13__*`: remaining audio descriptor fields for output endpoint 7. The repeated layout exposes `MAX_CHANNELS`, `SUPPORTED_FREQUENCIES`, and `DESCRIPTOR_BYTE_2` masks/shifts used to advertise supported sink audio formats.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE*__*`: output endpoint 7 channel-pair enable, mute, and channel-id fields. The first register groups channel pairs `01`, `23`, `45`, and `67`; `MULTICHANNEL_ENABLE2` exposes odd channel controls; `MULTICHANNEL_MODE` selects the multi-channel mode.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_*`: output pin response fields for lipsync, high bit rate audio (`HBR_CAPABLE`, `HBR_ENABLE`), default configuration, sink information, and unsolicited response forcing.
- `AZF0ENDPOINT7_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_0..8__*`: IEC 60958 channel-status override fields for mode, source number, clock accuracy, word length, sampling frequency, original sampling frequency, channel numbers, CGMS-A, MPEG surround, and validity/override-enable bits.
- `AZF0ENDPOINT7_AZALIA_F0_CODEC_PIN_CONTROL_LPIB*__*`: link position in buffer snapshot, raw LPIB value, timer snapshot, and cyclic buffer wrap count fields.
- `AZF0ENDPOINT7_AZALIA_F0_AUDIO_*_INT_STATUS__*`: output endpoint 7 interrupt status/mask/type fields for audio enabled, disabled, and format changed events.
- `AZF0INPUTENDPOINT0..7_AZALIA_F0_CODEC_INPUT_CONVERTER_*__*`: repeated input converter fields for audio widget capabilities, converter format, channel/stream id, digital converter control, stream format capabilities, and supported size/rate capabilities.
- `AZF0INPUTENDPOINT0..7_AZALIA_F0_CODEC_INPUT_PIN_*__*`: repeated input pin fields for widget capabilities, pin capabilities, unsolicited response enable/tag, input pin sense, widget input enable, channel allocation, hot-plug/audio enable, default configuration, LPIB snapshots, input status, and HDMI/DP audio infoframe data.

Each named field has a paired `__SHIFT` and `_MASK` definition. The conventional consumer pattern is to combine these constants with register read/modify/write helpers so callers can isolate a field using the mask and position a new value using the shift.

## Control Flow

There is no executable control flow in this chunk. The practical control flow appears in including C files that select DCN 2.1 register lists and then use generated offset/mask headers with AMD display register macros. In this repository, `dcn_2_1_0_sh_mask.h` is included by DCN 2.1 display modules such as `display/dmub/src/dmub_dcn21.c`, `display/dc/irq/dcn21/irq_service_dcn21.c`, `display/dc/gpio/dcn21/hw_factory_dcn21.c`, `display/dc/gpio/dcn21/hw_translate_dcn21.c`, and `display/dc/resource/dcn21/dcn21_resource.c`.

For this specific chunk, the runtime flow is indirect:

1. A DCN 2.1 module includes `dcn_2_1_0_offset.h` and `dcn_2_1_0_sh_mask.h`.
2. Register access tables bind symbolic register offsets to masks/shifts.
3. Display/audio setup, interrupt, GPIO, or DMUB code reads or writes hardware registers through AMD's register helper macros.
4. These constants define which bits correspond to a requested Azalia endpoint field.

The repeated input endpoint sections imply table-driven or macro-generated use. Endpoints 0 through 6 are complete in this chunk; endpoint 7 begins and continues beyond line 56533.

## State And Persistence Behavior

The header itself has no memory, persistence, initialization, or teardown behavior. The state represented by the constants lives in hardware registers:

- Capability registers report persistent hardware/firmware-advertised properties such as widget capabilities, supported stream formats, supported sample rates, HDMI/DP pin support, HBR capability, and sink identity fields.
- Control registers hold mutable device state such as converter format, digital converter enable, channel/stream id, channel enable/mute/channel id, unsolicited response configuration, hot-plug audio enable, input widget enable, and remote keepalive.
- Snapshot/status registers expose transient hardware state such as LPIB position, timer snapshots, wrap counts, input activity, infoframe validity, audio enable status, and interrupt flags.

Persistence is therefore owned by the display/audio hardware and any driver paths that program it. Misprogramming a mask or shift affects live MMIO/register state, not a software-owned data structure in this file.

## Dependencies And Integration Points

- Paired offset headers such as `dcn_2_1_0_offset.h` provide the register addresses; this file provides field layout. A mask without the matching offset does not identify a hardware location.
- AMD display register helper macros in the DC driver consume `*_MASK` and `*__SHIFT` constants to generate field reads/writes.
- The constants align with HD Audio/Azalia codec concepts: converter format, stream id, digital converter control, pin widget capabilities, unsolicited responses, pin sense, infoframe fields, channel allocation, and IEC 60958 channel status.
- The repeated `AZF0INPUTENDPOINTN_` naming binds each logical input endpoint to the same register shape. Any table or macro that assumes uniform endpoint layout depends on all endpoint blocks staying consistent.
- The output endpoint 7 definitions integrate with HDMI/DP audio output handling, audio format-change reporting, HBR support, sink information, and channel-status override programming.

## Risks

- Because this file is generated hardware contract data, a one-bit error in a mask or shift can silently corrupt unrelated register fields during read/modify/write operations.
- Repeated endpoint blocks are easy to miscompare by eye. A copy-generation mismatch for one `AZF0INPUTENDPOINTN_` block would affect only that endpoint and may surface as port-specific audio failures.
- The chunk starts mid-register (`AUDIO_DESCRIPTOR7`) and ends mid-endpoint (`AZF0INPUTENDPOINT7`), so whole-file review must reconcile this chunk with adjacent chunks before making conclusions about the complete endpoint 7 input block.
- Several fields affect interrupt behavior (`*_UR_ENABLE`, `AUDIO_*_INT_STATUS__*_MASK`) and live audio routing (`DIGEN`, channel IDs, stream IDs, mute bits). Incorrect definitions can produce missing notifications, stuck interrupts, wrong channel layout, or silent audio.
- The constants use long integer hexadecimal literals. Consumers should avoid assumptions about signedness or field width beyond the masks provided here.

## Test Signals

- Build coverage: any syntax or name collision issue should appear when compiling DCN 2.1 display code that includes `dcn_2_1_0_sh_mask.h`.
- Register table coverage: tests or static checks that instantiate DCN 2.1 register/mask tables should catch missing macro names referenced by C sources.
- Hardware/display validation: HDMI/DP audio enumeration, hot-plug audio enable, HBR playback, multi-channel output, input endpoint reporting, and audio format-change interrupts are the meaningful runtime signals for this region.
- Regression checks should compare this generated header against AMD's authoritative register database or adjacent ASIC-generation headers for endpoint layout consistency.
- For chunk reconciliation, confirm that the final merged research accounts for the preceding output endpoint 7 definitions before line 54267 and the continuation of input endpoint 7 after line 56533.
