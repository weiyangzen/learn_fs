# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 20000-22091

## Scope

This chunk is the final slice of AMDGPU's generated DCN 2.0.1 register shift/mask header. It contains preprocessor constants only: no functions, structs, enums, storage objects, or executable control flow. The exported surface is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros used by register helper code to insert or extract fields from DCN 2.0.1 MMIO and indexed Azalia/HDA display-audio registers.

The range has 2,092 source lines, including 921 shift macros, 929 mask macros, and 232 register or address-block comments. It starts at the tail of `DC_GPIO_HPD_MASK`, covers DC GPIO HPD/AUX pad controls, then describes Azalia function-0 output endpoint blocks 0 and 1, a partial endpoint2 audio-descriptor mirror, input endpoint blocks 0 and 1, and ends with the file's closing `#endif`.

## Purpose

The chunk provides exact bit positions and already-positioned masks for DCN 2.0.1 display connector GPIO and display-audio hardware fields. Higher-level AMD display code can name logical fields while this generated header supplies ASIC-specific layout details.

Major hardware areas covered here are:

- `DC_GPIO_HPD_MASK`, `DC_GPIO_HPD_A`, `DC_GPIO_HPD_EN`, and `DC_GPIO_HPD_Y`: hot-plug detect mask, pad disable, receive mode, active value, enable, Schmitt/slew, selection, and output/readback fields for HPD pins.
- `DC_GPIO_PAD_STRENGTH_1`, `PHY_AUX_CNTL`, and `DC_GPIO_AUX_CTRL_1` through `_5`: connector pad drive strength, AUX/DDC pad wake/enable/pulldown, comparator/bias/resistor selection, spike rejection, slew, DP/DN swap, termination, hysteresis, AUX control, and voltage-output tuning fields.
- `AUXI2C_PAD_ALL_PWR_OK`: global AUX/I2C pad power-good and bypass controls.
- `AZF0ENDPOINT0_*` and `AZF0ENDPOINT1_*`: repeated HDMI/DisplayPort output audio codec endpoint metadata, converter controls, pin controls, sink/ELD-derived information, multichannel routing, HBR, channel-status overrides, LPIB snapshots, format-change tracking, keepalive, and audio enable/disable/format-change interrupt status.
- `AZF0ENDPOINT2_*`: only the channel-speaker and audio-descriptor portions appear in this chunk, apparently as an input-endpoint-adjacent generated alias or continuation.
- `AZF0INPUTENDPOINT0_*` and `AZF0INPUTENDPOINT1_*`: input converter and input pin controls, including input format/stream routing, digital converter state, input pin capabilities, unsolicited response, input pin sense, multichannel enable/mute/channel IDs, HBR, channel allocation, hot-plug audio enable, forced unsolicited response, configuration default, LPIB snapshots, input activity/status interrupts, and input infoframe fields.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The API contract is macro naming and the pairing of every field shift with its mask:

- `*_SHIFT` constants hold the low bit position of a field.
- `*_MASK` constants hold the field mask already shifted into register position.
- Register-heading comments such as `//AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_HOT_PLUG_CONTROL` group the field macros by generated hardware register.
- Address-block comments such as `// addressBlock: azf0endpoint0_endpointind` and `// addressBlock: azf0inputendpoint1_inputendpointind` mark indexed codec endpoint register windows.

The GPIO/PHY macros are consumed by GPIO, HPD, DDC/AUX, and link-detection paths. Representative fields include `DC_GPIO_HPD_A__DC_GPIO_HPD1_A_MASK`, `DC_GPIO_HPD_EN__DC_GPIO_HPD1_EN_MASK`, `DC_GPIO_PAD_STRENGTH_1__RX_HPD_STRENGTH_SN_MASK`, `PHY_AUX_CNTL__AUX_PAD_WAKE_MASK`, `DC_GPIO_AUX_CTRL_1__DC_GPIO_AUX1_COMPSEL_MASK`, `DC_GPIO_AUX_CTRL_2__DC_GPIO_HPD12_SPIKERCEN_MASK`, `DC_GPIO_AUX_CTRL_3__AUX1_DP_DN_SWAP_MASK`, and `AUXI2C_PAD_ALL_PWR_OK__AUXI2C_PAD_ALL_PWR_OK_MASK`.

The output endpoint macros repeat a dense HDA codec endpoint model. Important groups include:

- `AZF0ENDPOINTn_AZALIA_F0_CODEC_CONVERTER_PARAMETER_AUDIO_WIDGET_CAPABILITIES` for converter widget capability flags, delay, and type.
- `...CONVERTER_CONTROL_CONVERTER_FORMAT` for channel count, bits per sample, sample divisor/multiple/base rate, and stream type.
- `...CONVERTER_CONTROL_CHANNEL_STREAM_ID` for channel and stream IDs.
- `...CONVERTER_CONTROL_DIGITAL_CONVERTER` for digital enable, validity, pre-emphasis, copyright, non-audio, professional, category code, generation level, and keepalive fields.
- `...PARAMETER_STREAM_FORMATS`, `...PARAMETER_SUPPORTED_SIZE_RATES`, `...STRIPE_CONTROL`, `...RAMP_RATE`, `...GTC_EMBEDDING`, and `...GTC_COUNTER_DELTA*` for capability advertisement and stream synchronization.
- `...CODEC_PIN_PARAMETER_*` and `...CODEC_PIN_CONTROL_*` for pin capabilities, unsolicited response tags, pin sense, output enable, channel/speaker mapping, audio descriptors 0-13, multichannel routing, lipsync, HBR, sink info, hot-plug audio enable, forced unsolicited responses, configuration default, LPIB, coding type, format changed, wireless display identification, and remote keepalive.
- `...PIN_CONTROL_CODEC_CS_OVERRIDE_0` through `_8` for IEC 60958 channel-status override fields.
- `...AUDIO_ENABLE_STATUS`, `...AUDIO_ENABLED_INT_STATUS`, `...AUDIO_DISABLED_INT_STATUS`, and `...AUDIO_FORMAT_CHANGED_INT_STATUS` for output endpoint state and interrupt metadata.

The input endpoint macros mirror much of the converter/pin model but use `CODEC_INPUT_CONVERTER_*` and `CODEC_INPUT_PIN_*` names. Input-specific groups include `...INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` for input activity, channel layout, and unsolicited-response enables, plus `...INPUT_PIN_CONTROL_INFOFRAME` for channel count, channel allocation, infoframe byte 5, and valid state.

## Control Flow

This header has no local control flow. Runtime behavior occurs in consumers that include `dcn_2_0_1_offset.h` and this shift/mask header, then build register tables or issue MMIO/indexed-register accesses through helper macros.

A typical use pattern is:

1. DCN 2.0.1 resource, IRQ, clock, GPIO, DDC/AUX, or audio code includes the generated offset and shift/mask headers.
2. Register tables are assembled with macro expansion helpers such as `SF`, `SRI`, `FD_MASK`, `FD_SHIFT`, and generation-specific mask-list macros.
3. Driver code calls helper operations such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, or indexed Azalia endpoint accessors.
4. The helpers use these masks and shifts to read, update, acknowledge, or decode hardware fields.

Control-sensitive flows represented by this chunk include HPD interrupt/presence handling, AUX/DDC pad bring-up, connector detection, HDMI/DP audio endpoint setup, stream-to-endpoint binding, audio format/rate/channel programming, sink descriptor propagation, hot-plug audio enablement, HBR enablement, channel-status override programming, LPIB position snapshots, and audio enable/disable/format-change interrupt reporting.

The macros do not encode ordering, volatility, access permissions, or write-one-to-clear behavior. Callers must still know when a field is read-only status, sticky status, self-clearing, safe only during link/audio disable, or shared with firmware/hardware state machines.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. It describes hardware register state that persists according to DCN/Azalia register semantics until changed by software, hardware, reset, or power management.

State represented in this range includes:

- HPD and GPIO state: pin masks, active values, enable bits, pull/power-disable controls, receiver selection, Schmitt/slew configuration, and pad output/readback values.
- AUX/DDC electrical state: pad wake, RX selection, pad mode, data/clock enable and power-disable bits, bias/resistor/comparator controls, spike rejection, termination, DP/DN swap, hysteresis, control nibbles, and voltage-output tuning.
- Audio converter state: stream format, channel count, sample size/rate encoding, channel/stream ID binding, digital converter status bits, keepalive controls, stripe/ramp/GTC embedding, and GTC delta/min/max readbacks.
- Output pin state: pin capabilities, pin sense, output enable, channel/speaker allocation, descriptor payloads, multichannel enable/mute/channel IDs, lipsync/HBR, sink info, hot-plug audio enable, forced unsolicited response payloads, default configuration, channel-status overrides, LPIB snapshots, coding type, format-change response, wireless display identity, remote keepalive, and audio interrupt state.
- Input endpoint state: input converter and pin capability/control values, input pin sense, multichannel routing, HBR, channel allocation, hot-plug audio enable, configuration default, LPIB snapshots, input activity/channel-layout status, unsolicited-response enables, and input infoframe state.

Some fields are configuration latches, some are live status readbacks, some are capability values exposed to the HDA codec model, and some are interrupt status/ack/mask/type fields. Incorrect software use can persist until a modeset, audio reconfiguration, connector hotplug, suspend/resume cycle, power reset, or full GPU reset reprograms the block.

## Dependencies And Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h`, which provides matching register addresses and indexed-register offsets. This chunk provides the bit layout within those registers. The constants also depend on AMD display helper conventions that paste register and field names into `_MASK` and `__SHIFT` identifiers.

Direct include sites visible in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`, which includes the DCN 2.0.1 offset and mask headers while building Cyan Skillfish/DCN201 resources, including display audio, link, GPIO, DDC/AUX, and IRQ objects.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`, which includes this header and expands generated masks into interrupt register entries for HPD, HPDRX, vblank, vline, vupdate, and page-flip sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`, which includes the header for DCN201 clock-manager register/field tables.

Shared GPIO translation code also relies on the HPD mask constants from this generated namespace. For example, `display/dc/gpio/dce80/hw_translate_dce80.c`, `display/dc/gpio/dce120/hw_translate_dce120.c`, and later DCN GPIO translators map `DC_GPIO_HPD_A__DC_GPIO_HPDn_A_MASK` values to software GPIO IDs.

Display audio integration flows through common DCE/DCN audio code and generation-specific resource tables that expose Azalia endpoint index/data windows to HDMI/DP audio setup. The endpoint and input-endpoint fields in this chunk are tightly coupled to matching `AZF0ENDPOINT*` and `AZF0INPUTENDPOINT*` offsets in the generated offset header.

Although the repository path is under `sources/distributed-fs/ceph-client`, this source is AMDGPU display hardware metadata. It has no Ceph filesystem, distributed storage, network protocol, or persistence-layer behavior.

## Risks And Edge Cases

The dominant risk is silent hardware misprogramming. A wrong shift or mask can compile cleanly but cause register helpers to alter the wrong bit, truncate a value, miss a sticky status bit, or acknowledge the wrong interrupt.

GPIO and AUX/HPD fields are connector-critical. Bad constants in `DC_GPIO_HPD_*`, `PHY_AUX_CNTL`, or `DC_GPIO_AUX_CTRL_*` can break hotplug detection, HPD IRQ delivery, DDC/AUX communication, DisplayPort link training, receiver selection, pad power state, or electrical tuning. Some failures may appear only on specific boards, connectors, cables, or suspend/resume paths.

Display audio fields are protocol-visible. Incorrect converter format, stream ID, digital converter, pin capability, audio descriptor, sink info, HBR, multichannel, channel allocation, or channel-status masks can produce missing HDMI/DP audio, wrong sample rate/channel advertisement, incorrect non-audio/professional/copyright metadata, broken HBR streams, or bad audio routing after hotplug.

Interrupt and status fields are especially sensitive. Audio enable/disable/format-change status groups and unsolicited-response controls mix status, mask, type, ack/clear, enable, and payload fields. A read/modify/write using the wrong mask can drop an interrupt, fail to clear a sticky bit, or report an event on the wrong endpoint.

The repeated endpoint layouts create copy/generation hazards. `AZF0ENDPOINT0` and `AZF0ENDPOINT1` should be structurally aligned, and `AZF0INPUTENDPOINT0` and `AZF0INPUTENDPOINT1` mostly mirror each other. Any one-off field-width or shift difference should be treated as suspicious unless the ASIC register database explicitly requires it.

Chunk boundaries matter. The range starts in the middle of `DC_GPIO_HPD_MASK`, so earlier shift definitions for that register live in the previous chunk. It also contains a duplicated `addressBlock: azf0inputendpoint0_inputendpointind` comment and a partial `AZF0ENDPOINT2_*` descriptor sequence amid input-endpoint material; the final merge lane should verify whether this is intentional generated aliasing or a source-generation irregularity before drawing whole-file conclusions.

## Test Signals

Useful validation signals are primarily generated-header checks plus DCN201 display, connector, and audio behavior:

- Build coverage for DCN201 resource, IRQ, clock manager, GPIO, DDC/AUX, and DCE/DCN audio code that includes `dcn_2_0_1_sh_mask.h`.
- Generated-register validation that every field has a matching address/register definition in `dcn_2_0_1_offset.h`, that masks match their shifts and widths, and that repeated endpoint/input-endpoint instances stay structurally consistent.
- Hotplug tests across HPD1/HPD2 and HPDRX paths, including plug/unplug storms, suspend/resume, runtime power transitions, and connector detection after display off/on.
- AUX/DDC validation through EDID reads, DisplayPort link training, HPD IRQ sideband handling, and failure-injection around pad power/wake paths.
- HDMI/DisplayPort audio tests for stream binding, PCM and non-PCM formats, sample-rate changes, multichannel layouts, HBR enablement, channel allocation, sink descriptor updates, and audio behavior across hotplug and modeset.
- Interrupt tests that confirm audio enabled, audio disabled, audio format changed, HPD, HPDRX, vblank, vline, vupdate, and page-flip interrupt masks/status/ack paths still report and clear expected events.
- LPIB and infoframe sanity checks that confirm snapshot locks, wrap counters, timer snapshots, input activity, channel layout, and infoframe-valid fields move plausibly during playback or capture-style input endpoint activity.

Regression symptoms from bad constants include missing hotplug events, failed EDID/AUX transactions, black screen after connector changes, no HDMI/DP audio, wrong audio channel layout or rate, stuck audio interrupts, format-change events not delivered, broken HBR audio, or endpoint-specific failures that only affect one generated instance.

## Cross-Chunk Notes

This is a generated constants-only chunk and the final chunk of `dcn_2_0_1_sh_mask.h`. The previous chunk owns the beginning of `DC_GPIO_HPD_MASK` and likely earlier DCIO/Azalia register families. The final per-file document should merge this slice with adjacent chunks to present the full DCN 2.0.1 register layout contract rather than treating this artificial line range as a standalone module.
