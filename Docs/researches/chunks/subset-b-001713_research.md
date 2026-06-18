# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 64243-66684

## Purpose

This chunk is a generated DCN 3.0.0 register shift/mask header slice for AMDGPU display audio hardware. It contains no executable C logic; its public interface is preprocessor constants of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. These constants pair with the generated offset header so AMD display register helpers can compose field values for Azalia/HDA codec function, stream, and endpoint-indirect registers.

The range begins at the tail of the Azalia codec function parameter fields, then covers all 16 `azf0stream*_streamind` stream latency/FIFO blocks and endpoint-indirect field definitions for `AZF0ENDPOINT0`, `AZF0ENDPOINT1`, `AZF0ENDPOINT2`, and the first part of `AZF0ENDPOINT3`. There are 2,035 `#define` entries in this slice. The path sits under a `ceph-client` source mirror, but this code is AMD GPU display/audio metadata, not Ceph filesystem logic.

## Important APIs, Types, And Constants

There are no functions, structs, enums, variables, or runtime data structures. The important API surface is the generated macro namespace consumed by register-table and field-access macros:

- `AZALIA_F2_CODEC_FUNCTION_PARAMETER_*`: codec function group type, supported sample sizes/rates, stream-format capability, and power-state capability fields, including `CLKSTOP` and `EPSS`.
- `AZF0STREAM0` through `AZF0STREAM15`: repeated stream-indirect field groups for `AZALIA_FIFO_SIZE_CONTROL`, `AZALIA_LATENCY_COUNTER_CONTROL`, `AZALIA_WORSTCASE_LATENCY_COUNT`, `AZALIA_CUMULATIVE_LATENCY_COUNT`, and `AZALIA_CUMULATIVE_REQUEST_COUNT`.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT3`: endpoint-indirect converter and pin-widget fields. Endpoint 0, 1, and 2 are complete in this chunk; endpoint 3 is partial and ends in `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1`.
- Converter widget fields: audio-widget capabilities, converter stream format, channel/stream ID, digital converter status/control bits, supported stream formats, supported size/rate capabilities, stripe control, ramp rate, GTC embedding, and GTC counter delta/min/max readbacks.
- Pin widget fields: pin audio-widget capabilities, HDMI/DP pin capability bits, unsolicited response controls, pin sense, output widget enable, channel/speaker allocation, 14 audio descriptors, multichannel enable/mute/channel maps, lipsync response, HBR capability, sink info and description bytes, hotplug/audio-enable control, forced unsolicited response payload, configuration default, IEC 60958 channel-status overrides, LPIB snapshots, coding type, format-change state, wireless display identification, remote keepalive, and audio enable/disable/format-change interrupt status fields.

The generated convention is regular: most registers list all shift constants first and all mask constants second. Full-width status/counter fields use `0xFFFFFFFFL`; narrow HDA fields use masks such as 4-bit channel IDs, 7-bit speaker allocations, 8-bit frequency/descriptor bytes, 16-bit product IDs, and high-bit control/status flags.

## Control Flow

This chunk has no local runtime control flow. Its practical use is compile-time expansion:

1. DCN 3.0 display/audio code includes this mask header with `dcn_3_0_0_offset.h`.
2. Register tables or helpers concatenate register and field names through macros such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `AZ_REG_READ`, and `AZ_REG_WRITE`.
3. Consumer code performs the actual MMIO or Azalia endpoint-indirect index/data accesses.

The stream blocks and endpoint blocks are declarative replicas. Any sequencing rules for HDA stream reset/run transitions, latency counter reset, endpoint index selection, converter programming, pin unsolicited responses, LPIB snapshot locking, interrupt acknowledgement, or hotplug audio enablement live in the AMD display audio driver and the hardware specification, not in this header.

## State And Persistence Behavior

The header stores no software state and persists no data. It describes hardware state held by the DCN 3.0 Azalia/HDA audio path:

- Codec function parameters advertise static or firmware-programmed capabilities: supported rates, bit depths, stream formats, group type, and power states.
- Stream-indirect registers expose FIFO sizing and latency telemetry for 16 Azalia streams. `AZALIA_LATENCY_COUNTER_RESET` is a control bit; worst-case, cumulative latency, and request counts are hardware counters/readbacks.
- Converter fields configure or report audio stream format, stream/channel routing, digital converter enable/status, IEC 60958-style channel status, HDMI/DP keepalive, striping, ramping, and GTC presentation-time embedding.
- Pin fields describe sink-facing state: HDMI/DP capability, speaker/channel allocation, ELD-like sink manufacturer/product/description bytes, hotplug audio enablement, HBR and multichannel capability, lipsync response values, unsolicited response payloads, default configuration, and remote keepalive.
- LPIB snapshot fields and timer snapshots expose stream position state. The snapshot lock and cyclic-buffer wrap count are synchronization-sensitive and should be handled by consumer code as hardware state with side effects.
- Audio enabled/disabled/format-changed interrupt status fields expose flag, mask, and type bits for endpoint state transitions.

Persistence is hardware-dependent. Some fields remain programmed until modeset, audio route change, suspend/resume, codec reset, or ASIC reset. Others are counters, snapshots, sticky flags, interrupt state, or write-sensitive controls.

## Dependencies And Integration Points

This chunk depends on generated-name compatibility with the DCN 3.0 offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`

The offset header supplies matching `ixAZF0STREAM*_*` and `ixAZF0ENDPOINT*_*` indirect register indexes, while this chunk supplies the field positions and masks for those registers. The two headers are normally consumed together by AMD display code that builds ASIC-specific register descriptors.

Important integration points in the surrounding driver are the display audio and resource paths that program HDMI/DP audio over the GPU's HDA/Azalia controller. Typical consumers include DCN resource setup, audio endpoint programming, IRQ handling, DMUB/DCN register table construction, and HDA/DP/HDMI hotplug or ELD update flows. The endpoint-indirect nature matters: callers must select the correct endpoint/index register before using the paired data register; these macros do not distinguish safe direct MMIO fields from indirect codec fields by type.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting HDA/Azalia register programming, causing no audio, wrong channel layout, incorrect sample-rate reporting, bad ELD/sink data, broken HBR, or hotplug/audio-enable regressions.
- The repeated `AZF0STREAM0` through `AZF0STREAM15` and `AZF0ENDPOINT0` through `AZF0ENDPOINT3` patterns create copy/paste drift risk. A single instance-specific mismatch can affect only one stream or display audio endpoint.
- `mm`/`ix` access classes must not be confused. These stream and endpoint names correspond to indirect Azalia register spaces, so direct MMIO access without the proper index/data sequence is unsafe.
- Status, mask, and control fields are mixed in adjacent registers. Names such as `*_INT_STATUS`, `*_FORMAT_CHANGED`, `*_UNSOLICITED_RESPONSE_FORCE`, `*_HOT_PLUG_CONTROL`, and `*_LPIB_SNAPSHOT_CONTROL` should be treated as side-effect-sensitive until the consumer path proves its access semantics.
- Full-width counter and payload fields use `0xFFFFFFFFL` or large payload masks; callers need width-safe reads and writes, especially on code paths that combine values with shifts.
- Audio descriptor and sink-info bytes encode externally visible capabilities. Incorrect masks can make userspace or audio middleware see unsupported formats, wrong maximum channels, or stale monitor identity.
- The chunk ends mid-endpoint for `AZF0ENDPOINT3`; later chunks must complete the endpoint 3 channel-status override and remaining pin/audio status fields before whole-file conclusions are drawn.

## Test Signals

Useful validation signals are mostly build-time and hardware-integration oriented:

- Build AMDGPU/DC with DCN 3.0 and DCN 3.02 support so missing or renamed `AZALIA`, `AZF0STREAM`, and `AZF0ENDPOINT` field macros are caught by register table initializers and audio code.
- Diff this generated range against the authoritative AMD register database or adjacent DCN-generation headers, with special attention to repeated stream/endpoint instance drift.
- Exercise HDMI and DisplayPort audio on DCN 3.0 hardware: hotplug, modeset, DPMS, suspend/resume, audio enable/disable transitions, ELD/sink-info updates, and stream format changes.
- Test multichannel and HBR audio formats, including channel allocation, speaker allocation, IEC 60958 channel-status override fields, and endpoint `MULTICHANNEL_ENABLE`/`MULTICHANNEL_ENABLE2` mappings.
- Validate latency and position telemetry by reading stream FIFO sizing, worst-case/cumulative latency counters, request counters, LPIB snapshots, and timer snapshots while audio is active.
- Check interrupt behavior for audio enabled, audio disabled, format changed, and unsolicited response paths; monitor for missed events, repeated events, or interrupt storms.
- Inspect kernel logs and audio userspace state for HDA command timeouts, wrong monitor audio capability reporting, silent endpoints, channel swaps, bad sample-rate negotiation, and resume-only failures.

## Cross-Chunk Notes

The range starts after earlier Azalia function parameter definitions, so the `AZALIA_F2_CODEC_FUNCTION_PARAMETER_GROUP_TYPE` comment and any preceding fields are outside this chunk. It ends at line 66684 in the middle of `AZF0ENDPOINT3_AZALIA_F0_PIN_CONTROL_CODEC_CS_OVERRIDE_1`; the remainder of endpoint 3 and additional endpoints, if present later in the file, must be merged from subsequent chunks.
