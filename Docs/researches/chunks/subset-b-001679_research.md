# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 56534-56648

## Scope

This chunk is the final slice of AMDGPU's generated DCN 2.1.0 shift/mask header. It contains C preprocessor constants only: no functions, structs, enums, storage objects, or executable code. The exported contract is a set of `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros that describe bit positions and already-positioned masks for DCN 2.1.0 hardware registers.

The range starts in the middle of the `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` masks, then completes the remaining input endpoint 7 audio pin-control register fields through `INFOFRAME`. It ends with `MPC_OCSC_TEST_DEBUG_INDEX`, `MPC_OCSC_TEST_DEBUG_DATA`, and the header-closing `#endif`.

## Purpose

The macros provide ASIC-specific bitfield metadata for two hardware areas:

- `AZF0INPUTENDPOINT7_*`: indexed Azalia/HDA display-audio input endpoint 7 pin-control fields, covering multichannel channel routing, HBR capability and enablement, channel allocation, hot-plug audio enablement, forced unsolicited responses, default codec pin configuration, LPIB snapshots, input activity/status, and audio infoframe metadata.
- `MPC_OCSC_TEST_DEBUG_*`: memory pixel combiner output color-space conversion test/debug index and data fields, used as a small index/data debug access pair for MPC OCSC internal state.

Higher-level driver code can use logical field names while the generated header supplies the exact DCN 2.1.0 bit layout. This is especially important because the same register names recur across DCN generations and endpoint instances, while masks or register availability can still diverge by ASIC.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The important interface is the macro naming pattern:

- `*_SHIFT` is the low bit position for a field.
- `*_MASK` is the field mask already shifted into register position.
- Register-heading comments group fields by hardware register name.

The first lines finish `AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE` for channels 0-3. Each channel uses the same byte lane pattern: enable at bit 0/8/16/24, mute at bit 1/9/17/25, and a 4-bit channel ID at bits 4-7, 12-15, 20-23, or 28-31.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2` repeats the same layout for channels 4-7:

- `MULTICHANNEL4_ENABLE`, `MULTICHANNEL4_MUTE`, `MULTICHANNEL4_CHANNEL_ID`
- `MULTICHANNEL5_ENABLE`, `MULTICHANNEL5_MUTE`, `MULTICHANNEL5_CHANNEL_ID`
- `MULTICHANNEL6_ENABLE`, `MULTICHANNEL6_MUTE`, `MULTICHANNEL6_CHANNEL_ID`
- `MULTICHANNEL7_ENABLE`, `MULTICHANNEL7_MUTE`, `MULTICHANNEL7_CHANNEL_ID`

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR` exposes `HBR_CAPABLE` at bit 0 and `HBR_ENABLE` at bit 4. These fields advertise and control high-bit-rate audio behavior for the endpoint.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION` contains an 8-bit `CHANNEL_ALLOCATION` field at bits 0-7. This matches HDMI/DisplayPort audio channel layout metadata carried through the HDA codec model.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` has `CLOCK_GATING_DISABLE`, `CLOCK_ON_STATE`, and `AUDIO_ENABLED`. The high bit `AUDIO_ENABLED_MASK` (`0x80000000L`) is the most visible state/control flag in this group.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE` defines a 26-bit `UNSOLICITED_RESPONSE_PAYLOAD` field and a force bit at bit 28. This lets software force an HDA-style unsolicited response payload for endpoint event notification paths.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` packs the HDA pin default configuration fields:

- `SEQUENCE` bits 0-3
- `DEFAULT_ASSOCIATION` bits 4-7
- `MISC` bits 8-11
- `COLOR` bits 12-15
- `CONNECTION_TYPE` bits 16-19
- `DEFAULT_DEVICE` bits 20-23
- `LOCATION` bits 24-29
- `PORT_CONNECTIVITY` bits 30-31

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL`, `..._LPIB`, and `..._LPIB_TIMER_SNAPSHOT` describe link-position-in-buffer snapshot locking, an 8-bit cyclic-buffer wrap count, a 32-bit LPIB value, and a 32-bit timer snapshot value.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` exposes `INPUT_ACTIVITY`, 2-bit `CHANNEL_LAYOUT`, and two unsolicited-response enable bits for activity and channel-layout/channel-status infoframe changes.

`AZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` exposes `CHANNEL_COUNT`, `CHANNEL_ALLOCATION`, `INFOFRAME_BYTE_5`, and `INFOFRAME_VALID`. This group is the endpoint's decoded input audio infoframe summary.

The final MPC debug macros are:

- `MPC_OCSC_TEST_DEBUG_INDEX__MPC_OCSC_TEST_DEBUG_INDEX__SHIFT/MASK` for the 8-bit debug index.
- `MPC_OCSC_TEST_DEBUG_INDEX__MPC_OCSC_TEST_DEBUG_WRITE_EN__SHIFT/MASK` for the write-enable bit at bit 8.
- `MPC_OCSC_TEST_DEBUG_DATA__MPC_OCSC_TEST_DEBUG_DATA__SHIFT/MASK` for the full 32-bit data value.

## Control Flow

This header has no local control flow. Runtime behavior is created by consumers that include the DCN 2.1.0 offset and mask headers and then use AMD display register helpers to read, update, or decode fields.

A typical use pattern is:

1. DCN 2.1 code includes `dcn_2_1_0_offset.h` and this shift/mask header.
2. Register tables or helper macros paste register and field names into `_MASK` and `__SHIFT` identifiers.
3. Driver paths issue MMIO or indexed-register operations through helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, or register table initializers.
4. The helpers use these constants to isolate the intended bitfields.

For the Azalia input endpoint fields, the runtime sequencing lives in display-audio setup, hotplug, infoframe, and stream routing code. This chunk only states the bitfield layout; it does not encode whether a field is read-only, write-one-to-clear, sticky, self-clearing, clock-gated, or safe only while audio is disabled.

For the MPC OCSC debug pair, runtime code would normally select an internal debug index, set write enable when needed, and read or write the data register. The chunk does not define legal debug indices, side effects, or synchronization requirements.

## State And Persistence Behavior

The file itself stores no state and persists nothing. It describes hardware register state whose lifetime is controlled by the DCN display block, Azalia/HDA codec endpoint logic, power management, reset, and driver reprogramming.

Endpoint state represented here includes:

- Per-channel enable, mute, and channel-ID routing for multichannel input audio lanes 0-7.
- HBR capability and enable state.
- Channel allocation and infoframe-derived channel count/allocation/byte-5/valid state.
- Hot-plug and audio-enabled state for input endpoint 7.
- Forced unsolicited-response payload and force trigger state.
- HDA default pin configuration fields that describe endpoint association, device type, physical location, connection type, color, and port connectivity.
- LPIB snapshot lock, cyclic-buffer wrap count, current link position, and timer snapshot readback.
- Input activity, channel layout, and unsolicited-response enable state.

Some of these are configuration latches, some are live status readbacks, and some represent event-generation controls. Bad writes may persist until a display audio reconfiguration, hotplug cycle, suspend/resume, DCN power transition, or full GPU reset rewrites the endpoint.

The MPC OCSC debug index/data registers are debug state. Their contents may affect only diagnostic readback paths, but if write-enable is used incorrectly they can also alter an indexed internal debug register until changed or reset.

## Dependencies And Integration Points

The direct companion for this chunk is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`, which defines the matching register addresses and indexed offsets. Relevant companions include:

- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL_ENABLE2` at indexed offset `0x0037`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR` at `0x0038`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_CHANNEL_ALLOCATION` at `0x0053`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_HOT_PLUG_CONTROL` at `0x0054`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_UNSOLICITED_RESPONSE_FORCE` at `0x0055`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT` at `0x0056`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_SNAPSHOT_CONTROL` at `0x0064`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB` at `0x0065`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB_TIMER_SNAPSHOT` at `0x0066`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INPUT_STATUS_CONTROL` at `0x0067`.
- `ixAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_INFOFRAME` at `0x0068`.
- `mmMPC_OCSC_TEST_DEBUG_INDEX` and `mmMPC_OCSC_TEST_DEBUG_DATA` at MMIO offsets `0x163b` and `0x163c`, base index 2.

Visible include sites for `dcn_2_1_0_sh_mask.h` in this tree are:

- `display/dc/resource/dcn21/dcn21_resource.c`, which builds DCN 2.1 resource objects and register tables.
- `display/dc/irq/dcn21/irq_service_dcn21.c`, which uses generated masks for interrupt handling tables.
- `display/dc/gpio/dcn21/hw_factory_dcn21.c` and `display/dc/gpio/dcn21/hw_translate_dcn21.c`, which use the same generated register namespace for GPIO-related objects.
- `display/dmub/src/dmub_dcn21.c`, which includes DCN 2.1 register metadata for DMUB-facing display microcontroller support.

Direct textual references to these exact endpoint 7 macros are uncommon because AMD's display code often consumes generated headers through macro-paste register lists rather than spelling every field name directly. Cross-generation headers such as `dcn_3_0_1_sh_mask.h`, `dcn_3_5_0_sh_mask.h`, and `dcn_3_5_1_sh_mask.h` carry similar endpoint fields, which makes this range part of a broader generated-register compatibility surface.

Although the repository path sits under `sources/distributed-fs/ceph-client`, this file is AMDGPU display hardware metadata. It has no Ceph, filesystem, distributed-storage, or network protocol behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A wrong mask or shift still compiles but can write the wrong bit, truncate a field, decode status incorrectly, or leave stale bits behind during read/modify/write operations.

The multichannel fields are dense and repeated. Each channel occupies a byte lane, with a 4-bit channel ID in the high nibble. Off-by-one shifts or masks can swap enable/mute bits, route an audio channel to the wrong slot, or corrupt the neighboring channel's ID.

The HBR, channel allocation, and infoframe fields are protocol-visible. Incorrect masks can cause HDMI/DisplayPort audio to advertise the wrong channel count, channel allocation, or high-bit-rate support, leading to missing audio, wrong speaker mapping, or failures that appear only with multichannel/HBR sinks.

The hot-plug and unsolicited-response fields interact with event delivery. A bad `AUDIO_ENABLED`, unsolicited payload, or unsolicited-response enable mask can make endpoint state changes invisible to the codec model, generate unexpected events, or fail to report activity/channel-layout changes.

The LPIB snapshot fields mix locking, wrap count, position, and timer snapshot readback. Incorrect usage can produce inconsistent audio position reporting or races around snapshot capture. The header does not say whether callers must lock before reading both snapshot registers; that ordering must come from the hardware programming guide or existing audio helper code.

The MPC OCSC debug index/data pair is sensitive because indexed debug register interfaces can have side effects. The `MPC_OCSC_TEST_DEBUG_WRITE_EN` bit must not be confused with the index field; accidental writes may alter debug state rather than only reading it. The matching enums in `soc21_enum.h` and later `soc24_enum.h` define false/true values for this write-enable field, reinforcing that it is a real control bit rather than padding.

Chunk boundaries are also relevant. The first lines are only the masks for the tail of `MULTICHANNEL_ENABLE`; the matching shift macros for channels 0-3 are in the previous chunk. Whole-file reconciliation should merge this slice with the preceding endpoint 7 material before drawing conclusions about complete input endpoint coverage.

## Test Signals

Useful validation is mostly generated-header and hardware-behavior oriented:

- Build coverage for DCN 2.1 display resource, IRQ, GPIO, DMUB, and audio-related code that includes `dcn_2_1_0_sh_mask.h`.
- Generated-register consistency checks that every mask in this chunk has the expected shift and width, and that every register has a matching offset in `dcn_2_1_0_offset.h`.
- Cross-generation diffs against adjacent DCN headers for endpoint 7 and MPC OCSC debug fields, with expected differences reviewed against the ASIC register database.
- HDMI/DisplayPort audio tests for stereo, multichannel 5.1/7.1, channel allocation changes, HBR/non-PCM formats, hotplug, modeset, suspend/resume, and sink changes.
- Infoframe and input-status tests that confirm channel count, allocation, byte 5, valid bit, input activity, channel layout, and unsolicited-response behavior update as expected.
- LPIB position tests that verify snapshot lock, wrap count, LPIB, and timer snapshot values are stable and plausible during playback or capture-style endpoint activity.
- Debugfs or internal validation, where available, for MPC OCSC test-debug index/data access without unintended writes when write-enable is clear.

Regression symptoms from bad constants include no HDMI/DP audio, wrong speaker mapping, broken HBR playback, stale or missing audio hotplug events, incorrect HDA pin default reporting, inconsistent audio position reporting, stuck unsolicited responses, or MPC debug reads/writes returning impossible values.

## Cross-Chunk Notes

This is the final chunk of `dcn_2_1_0_sh_mask.h`. The previous chunk owns the beginning of input endpoint 7, including the first `MULTICHANNEL_ENABLE` shift definitions and earlier input pin-control capability/status fields. The final per-file document should treat this chunk as the tail of a generated DCN 2.1.0 register-layout contract rather than a standalone module.
