# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 15509-15686

## Purpose

This chunk is the closing section of AMD's generated DCN 3.1.6 register offset header. It contains no executable C logic; it publishes preprocessor constants for Azalia function 0 input-endpoint indexed registers. The values are the indirect register offsets selected through each endpoint's `AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` register before reading or writing the matching `AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA` window.

The requested range contains 178 source lines, 151 `#define` entries, six generated `addressBlock` comments for complete input endpoints 2 through 7, and the final `#endif` for the header guard. It starts inside the tail of `azf0inputendpoint1_inputendpointind`, then covers complete indexed-offset maps for `azf0inputendpoint2_inputendpointind` through `azf0inputendpoint7_inputendpointind`.

Although this path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, allocation paths, locks, or direct register accesses in this chunk. The exported interface is a generated macro namespace:

- `ixAZF0INPUTENDPOINT<N>_AZALIA_F0_CODEC_INPUT_*`: indirect Azalia codec input-endpoint register offsets for endpoint instances 1 through 7.
- `// addressBlock: azf0inputendpoint<N>_inputendpointind`: generated grouping comments for indexed register blocks. In this chunk, endpoint 1 is only the inherited tail from the previous block; endpoint 2 through endpoint 7 have visible block comments.
- The closing `#endif` terminates `_dcn_3_1_6_OFFSET_HEADER`.

Endpoint 1 coverage starts after the converter and early pin registers and includes the tail pin-control indexed offsets:

- `..._WIDGET_CONTROL` at `0x0024`.
- Multichannel, HBR, channel-allocation, hot-plug, unsolicited-response-force, default-configuration, LPIB snapshot/readback, input-status, and infoframe offsets from `0x0036` through `0x0068`.

Endpoints 2 through 7 repeat the same complete 23-offset input-endpoint map:

- Converter parameter/control offsets: audio widget capabilities `0x0001`, converter format `0x0002`, channel/stream ID `0x0003`, digital converter `0x0004`, stream formats `0x0005`, and supported size/rates `0x0006`.
- Input pin parameter/control offsets: audio widget capabilities `0x0020`, pin capabilities `0x0021`, unsolicited response `0x0022`, input pin sense `0x0023`, and widget control `0x0024`.
- Multichannel and high-bit-rate audio offsets: multichannel enable `0x0036`, multichannel enable2 `0x0037`, and HBR response `0x0038`.
- Audio metadata and event offsets: channel allocation `0x0053`, hot-plug control `0x0054`, unsolicited-response-force `0x0055`, and response default configuration `0x0056`.
- Runtime position/status offsets: LPIB snapshot control `0x0064`, LPIB `0x0065`, LPIB timer snapshot `0x0066`, input status control `0x0067`, and infoframe `0x0068`.

The bit-level meanings for these indexed registers live in the companion `dcn_3_1_6_sh_mask.h` file under the matching `AZF0INPUTENDPOINT<N>_...` register names. This offset chunk only says which indexed register number to select.

## Control Flow

This header has no runtime control flow. The intended runtime sequence is supplied by AMDGPU display/audio code and the generic register helpers:

1. DCN 3.1.6 translation units include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. Direct MMIO offset macros elsewhere in this same header identify each input endpoint's index/data pair, for example `regAZF0INPUTENDPOINT2_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` at `0x0442` and `regAZF0INPUTENDPOINT2_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA` at `0x0443`, both with base index `2`.
3. A consumer selects an `ixAZF0INPUTENDPOINT<N>_...` value by writing the endpoint index window, then reads or writes the endpoint data window.
4. Field masks and shifts from `dcn_3_1_6_sh_mask.h` are applied to pack or extract individual HDA/Azalia fields.

The macros do not encode any sequencing rule. Consumers must still order codec probing, stream-format selection, audio enablement, infoframe handling, hotplug/unsolicited-response processing, LPIB snapshots, and status reads according to hardware requirements.

## State And Persistence Behavior

The macros store no software state and persist nothing in memory or files. They describe MMIO-backed GPU display-audio state reachable through indexed endpoint windows.

The hardware state represented by the indexed offsets includes:

- Input converter capability and format state: channel count, sample width/rate encoding, stream ID, channel ID, stream format support, and supported size/rate reporting.
- Input digital-converter state for audio-valid/status-channel attributes and keepalive behavior.
- Input pin capabilities and controls, including unsolicited response configuration, pin sense, widget enablement, and multichannel lane enable/mute/channel-ID state.
- HBR capability/enablement, channel allocation, hotplug/audio-enable control, forced unsolicited-response payloads, and HDA default pin configuration.
- LPIB position and timer snapshot state, cyclic-buffer wrap count, input activity, channel layout, infoframe-change unsolicited-response enables, and decoded audio infoframe fields.

Persistence and side effects are hardware-defined. Some fields are configuration values that remain until reprogrammed, reset, power-gated, or restored after suspend/resume. Others are live status, latched status, snapshot, self-clearing, or event-generation controls. This offset header does not identify access type, reset value, or write side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.6 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h`, which provides the matching field masks and shifts for the same `AZF0INPUTENDPOINT<N>` logical registers.
- The direct index/data register offsets earlier in this file, including `regAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` through `regAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`.
- DCN base-address definitions used by DCN 3.1.6 code, such as the `DCN_BASE__INST0_SEG*` constants in `display/dmub/src/dmub_dcn316.c`.
- AMD display register helpers and table-building macros that combine generated offsets with masks/shifts.

Direct include sites for the generated DCN 3.1.6 offset/mask pair in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`

The main display-audio integration point is DCN316 resource construction. `dcn316_resource.c` builds audio register tables with `audio_regs(...)`, creates audio objects through `dce_audio_create(...)`, and constructs stream encoders, VPG, AFMT, and APG blocks used for HDMI/DP audio programming. The visible audio table in `dcn316_resource.c` references output endpoint index/data masks, while this chunk supplies the generated input-endpoint indexed-offset side of the same Azalia function 0 register map for hardware paths or diagnostics that need input endpoint access.

## Risks And Edge Cases

- Generated offset drift is the main risk. These constants are untyped numeric macros, so an incorrect `ix...` value can compile cleanly while selecting the wrong indexed endpoint register at runtime.
- The range starts mid-block. Endpoint 1's converter offsets and early pin offsets are in the previous chunk; only endpoint 2 through endpoint 7 are complete here.
- The range ends at the file-level `#endif`. There is no later chunk for this file after endpoint 7, so merge/reconciliation should treat this as the final offset-header slice.
- Input endpoint instances are repetitive but not interchangeable. Using endpoint 5 offsets through endpoint 4's index/data window, or using an input endpoint offset with an output endpoint window, can silently program or read the wrong HDA node.
- Offset and mask headers must match. Combining `dcn_3_1_6_offset.h` with a different ASIC's `*_sh_mask.h` can produce correct-looking names with wrong hardware semantics.
- Indexed access is sequencing-sensitive. A stale index selection, concurrent access to the same index/data window, or a missing readback/snapshot step can return data for the wrong logical register.
- Audio status and event fields can be live or latched. Misprogramming unsolicited response, hotplug, input activity, HBR, or infoframe offsets can cause missed audio events, spurious notifications, incorrect channel layout reporting, or broken HDMI/DP audio detection.
- LPIB and timer snapshot offsets describe position-related state. Reading them without the expected snapshot/lock protocol can produce inconsistent position data.

## Test Signals

Useful validation signals are mostly build-time, generated-header consistency, and hardware audio behavior:

- Build AMDGPU display code with DCN 3.1.6 enabled to catch missing or renamed generated macros in include paths used by `dcn316_resource.c` and `dmub_dcn316.c`.
- Mechanically verify that every `ixAZF0INPUTENDPOINT<N>_...` offset in this range has a matching logical register family in `dcn_3_1_6_sh_mask.h`.
- Check parity across endpoint 2 through endpoint 7: each complete endpoint should expose the same 23 indexed offsets with identical numeric values.
- Verify that the direct index/data windows earlier in `dcn_3_1_6_offset.h` exist for every input endpoint 0 through 7 and use the expected base index.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database or nearby compatible DCN headers where endpoint layouts are expected to match.
- Exercise HDMI/DP audio paths on DCN316 hardware: stream setup, sample-rate/bit-depth changes, multichannel layouts, HBR audio, hotplug, unplug/replug, suspend/resume, and rapid modesets.
- Monitor kernel logs and audio behavior for missed hotplug/unsolicited-response events, wrong channel allocation, invalid infoframe reporting, LPIB position anomalies, audio silence, or spurious audio-enable/disable transitions.

## Cross-Chunk Notes

The previous chunk must be merged to complete `AZF0INPUTENDPOINT1` because this range starts at `ixAZF0INPUTENDPOINT1_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_WIDGET_CONTROL`. This chunk completes the file by covering all visible indexed offsets for input endpoints 2 through 7 and the closing header guard.
