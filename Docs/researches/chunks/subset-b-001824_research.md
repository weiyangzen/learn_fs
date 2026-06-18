# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 54475-56841

## Purpose

This chunk is generated AMD DCN 3.1.2 register field metadata. It contains no executable C logic; it publishes C preprocessor constants for field shifts and bit masks used to read, write, and update MMIO-backed Azalia/HD-audio endpoint registers on DCN 3.1.2 hardware.

The requested range is a mid-file slice of `dcn_3_1_2_sh_mask.h`. It covers 2,367 lines with 2,051 `#define` entries: 1,026 `__SHIFT` macros and 1,025 `_MASK` macros. The range starts in the middle of `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_PARAMETER_AUDIO_WIDGET_CAPABILITIES`, continues through the rest of endpoint 0 pin/status fields, covers complete endpoint 1 through endpoint 3 Azalia converter and pin field blocks, and ends partway through endpoint 4 at `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE`.

Although the path is under a local `ceph-client` source mirror, this header is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locking primitives in this range. The public interface is the generated macro namespace:

- `AZF0ENDPOINT<n>_<register>__<field>__SHIFT`: bit position for a named field.
- `AZF0ENDPOINT<n>_<register>__<field>_MASK`: bit mask for the same field.

These macros are intended to be consumed with the matching DCN 3.1.2 offset header and helper macros such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and DMUB register-table construction. The shift and mask constants are not useful by themselves unless the caller also addresses the correct endpoint register through `dcn_3_1_2_offset.h`.

Major field families in this slice:

- Endpoint 0 pin fields: tail of audio-widget capabilities, pin capabilities, unsolicited response control, pin sense, widget output enable, channel/speaker allocation, audio descriptor 0 through 13, multichannel enable maps, lipsync/HBR response, sink information, hot-plug controls, default configuration, channel-status overrides, association/status/LPIB fields, coding and format-change status, wireless-display identification, remote keepalive, and audio enable/disable/format interrupt status.
- Endpoints 1 through 3 complete blocks: converter audio-widget capabilities, converter stream format, channel/stream ID, digital converter control, supported formats and rates, stripe/ramp/GTC controls, GTC counter deltas, then the same pin-control, sink-info, multichannel, channel-status override, LPIB, coding, format-change, wireless-display, keepalive, and audio interrupt/status families as endpoint 0.
- Endpoint 4 partial block: converter and pin capability/control fields from audio-widget capabilities through audio descriptor 13 and the beginning of `MULTICHANNEL_ENABLE`.

Representative fields include audio channel count, amplifier presence, converter type, stream/channel IDs, digital converter enable/V/VCFG/DIGEN bits, supported stream formats and sample rates, GTC embedding and timing deltas, impedance sense, output enable, HDMI/DP connection flags, speaker/channel allocation, ELD-like sink manufacturer/product/port-description fields, hot-plug capability/enables, unsolicited-response tag/enable/force controls, multichannel pair enable/mute/channel-ID fields for 0/1 through 6/7 channels, IEC 60958 channel-status override bytes, LPIB snapshot/timer fields, coding type, format-change flags, keepalive enable/status, and per-audio-event interrupt masks/acks/status bits.

## Control Flow

This header has no runtime control flow. Runtime code supplies the sequencing:

1. DCN 3.1.2 display and DMUB code includes `dcn_3_1_2_offset.h` and `dcn_3_1_2_sh_mask.h`.
2. Register lists and helper macros paste register and field names into generated tokens such as `AZF0ENDPOINT2_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER__CHANNEL_ALLOCATION_MASK`.
3. `FD_MASK` and `FD_SHIFT`-style macros place those constants into field tables or use them directly in register access helpers.
4. Driver or firmware-service code programs the addressed Azalia endpoint registers during audio-capability exposure, HDMI/DP audio setup, stream-format updates, hotplug/unsolicited-response handling, and status/interrupt processing.

The macros do not encode ordering requirements. Consumers must still sequence audio endpoint enablement, display-link setup, ELD/sink updates, converter stream assignment, channel-status programming, hotplug notification, interrupt clear/ack, and suspend/resume restoration correctly.

## State And Persistence Behavior

This chunk stores no software state and persists nothing. It describes fields within hardware registers. The represented hardware state includes:

- Converter state for stream format, stream/channel identity, supported formats/rates, digital converter bits, striping, ramp control, GTC embedding, and GTC timing-delta reporting.
- Pin state for widget capability reporting, pin capability reporting, output enable, pin sense, HDMI/DP connection indication, speaker/channel allocation, supported audio descriptors, multichannel routing and mute controls, and lipsync/HBR response.
- Sink metadata state for manufacturer/product IDs, description length/content fragments, and DP/HDMI port identifiers.
- Notification and status state for unsolicited responses, forced responses, hotplug presence/capability/enables, digital-output status, LPIB snapshot/timer values, coding type, format-change bits, wireless-display identification, remote keepalive, and audio enable/disable/format-change interrupts.

Persistence is hardware-defined. Configuration-like fields normally retain values until modeset, endpoint reprogramming, display/audio reset, power gating, suspend/resume, or ASIC reset. Status, interrupt, hotplug, LPIB, format-change, keepalive, and force/ack fields may be read-only, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. The generated mask header only provides bit layout; it does not declare access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.2 register database and must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h` for the corresponding register offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/yellow_carp/yellow_carp_offset.h` and DCN base-address definitions for Yellow Carp/DCN 3.1 register addressing.
- Field helper macros such as `FD_MASK` and `FD_SHIFT` in the AMD display/DMUB register access layer.

The direct include site found in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`, which builds `dmub_srv_dcn31_regs` by combining DCN 3.1 offset constants with DCN 3.1.2 field masks and shifts. Broader integration is through AMDGPU display audio and DMUB service code that uses generated register tables and field macros for HDMI/DisplayPort audio endpoint programming.

This range is closely coupled to the adjacent offset and mask chunks. The line range begins after the start of endpoint 0 and ends before endpoint 4 is complete, so final file-level analysis must merge neighboring chunks before making complete claims about all Azalia endpoints.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These are untyped constants, so a wrong mask or bit position can compile cleanly while corrupting unrelated hardware fields.
- Endpoint repetition is copy-sensitive. Endpoint 1 through endpoint 3 are complete and structurally similar, while endpoint 0 and endpoint 4 are partial in this chunk; a merge or generator error can affect only a specific display/audio endpoint.
- Some fields are side-effect-sensitive. Interrupt status/ack/mask bits, format-change flags, unsolicited-response force bits, hotplug controls, LPIB snapshot controls, and keepalive state may not tolerate blind read-modify-write patterns.
- Audio capability fields are externally visible through HDMI/DP audio behavior. Incorrect descriptor, supported-rate, channel allocation, or HBR fields can produce missing formats, wrong channel maps, audio dropouts, or broken receiver compatibility.
- Sink information and port ID fields must line up with link and ELD/EDID handling. Stale or incorrectly masked values can confuse audio device enumeration after hotplug, MST changes, or resume.
- Multichannel routing fields pack enable, mute, and channel IDs into repeated bit groups. Misprogramming one group can leave stereo working while 5.1/7.1 or HBR audio fails.
- This header does not identify access permissions. Callers must know which fields are read-only, write-only, W1C, sticky, or self-clearing from the hardware specification and surrounding driver logic.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU/DC and DMUB code paths that include `dcn_3_1_2_sh_mask.h`; missing or renamed macros should fail during register-table and field-table construction.
- Mechanically verify that every complete register field in lines 54475-56841 has a consistent `__SHIFT`/`_MASK` pair, accounting for the artificial chunk boundaries at endpoint 0 and endpoint 4.
- Diff this range against AMD's authoritative DCN 3.1.2 register database and neighboring generated DCN headers where endpoint field layouts are expected to match.
- Exercise HDMI and DisplayPort audio on hardware that uses DCN 3.1.2/Yellow Carp paths: hotplug, modeset, suspend/resume, audio enable/disable, stream-format changes, stereo, multichannel, and HBR formats.
- Validate audio descriptors and channel allocation with receivers that report different ELD/EDID capabilities, including 2-channel-only sinks, 5.1/7.1 sinks, high sample-rate modes, and DP versus HDMI connections.
- Check unsolicited response and hotplug behavior through audio-device enumeration after monitor unplug/replug, MST topology changes, and resume.
- Watch kernel logs and user-visible audio diagnostics for missing HDMI/DP audio devices, format-change storms, stuck interrupts, channel-map errors, LPIB/timestamp anomalies, audio dropouts, or failures limited to one connector/endpoint.

## Cross-Chunk Notes

Previous chunks own the beginning of endpoint 0, including earlier converter and audio-widget capability fields. Later chunks continue endpoint 4 after `AZF0ENDPOINT4_AZALIA_F0_CODEC_PIN_CONTROL_MULTICHANNEL_ENABLE` and should cover the rest of endpoint 4 plus any later endpoints. The final per-file research document should reconcile these boundaries before summarizing the complete `dcn_3_1_2_sh_mask.h` Azalia endpoint field map.
