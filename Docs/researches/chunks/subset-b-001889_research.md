# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 60080-62071

## Purpose

This chunk is the tail of AMD DCN 3.1.5 generated register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe hardware bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN 3.1.5 display-controller MMIO registers. Consumers combine these constants with the matching `dcn_3_1_5_offset.h` register offsets and AMD display register-helper macros to read, write, set, update, or decode individual fields.

The requested range starts in the middle of the `AZF0INPUTENDPOINT1` Azalia F0 codec input endpoint block, fully covers `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7`, then ends the header with DSCC, DSCCIF, and DSC_TOP debug-register shift definitions plus the include guard terminator. It defines 1,707 macros in this slice: 897 `__SHIFT` constants and 810 `_MASK` constants.

Although the repository path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct MMIO operations in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask used to isolate or update that field.
- `// addressBlock: ...` comments: generated grouping markers for indexed hardware blocks.

Major register families in this range:

- `AZF0INPUTENDPOINT1` tail: remaining input converter and input pin field masks/shifts for converter format, channel/stream ID, digital converter control, supported formats/rates, pin capabilities, unsolicited responses, pin sense, widget enable, multichannel routing, HBR, channel allocation, hotplug/audio enable, forced unsolicited response payloads, configuration default, LPIB snapshots, input activity, and infoframe data.
- `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7`: six complete repeated Azalia F0 codec input endpoint blocks. Each endpoint exposes the same converter, pin-parameter, pin-control, stream-format, multichannel, hotplug, LPIB, status, and infoframe field layout.
- `DSCC_DEBUG_ID` and `DSCC_DEBUG_0` through `DSCC_DEBUG_76`: debug register selectors and status fields for the DSCC compressor/debug block. Most are single full-register fields at shift 0; `DSCC_DEBUG_8` exposes four individual `DSCC_RATE_BUFFER*_INITIAL_XMIT_DELAY_REACHED` bits.
- `DSCCIF_DEBUG_ID` and `DSCCIF_DEBUG_0` through `DSCCIF_DEBUG_4`: debug selector/data fields for the DSC client interface debug block.
- `DSC_TOP_DEBUG_ID` and `DSC_TOP_DEBUG_0` through `DSC_TOP_DEBUG_4`: top-level DSC debug selector/data fields.
- Final `#endif`: closes `_dcn_3_1_5_SH_MASK_HEADER`, confirming this chunk reaches end-of-file.

Representative Azalia endpoint fields include:

- Audio widget capability fields: channel capability, input/output amplifier presence, format override, stripe, processing widget, unsolicited response capability, connection list, digital, power control, LR swap, delay, and type.
- Converter controls: channel count, bits per sample, sample base divisor/multiple/rate, stream type, channel ID, stream ID, digital enable, validity/configuration/copyright/non-audio/pro bits, category code, and keepalive.
- Pin controls: impedance/presence detect, input enable, multichannel enables/mutes/channel IDs for channels 0 through 7, HBR capable/enable, channel allocation, clock gating, clock-on state, audio enabled, and configuration default fields.
- Runtime/status fields: forced unsolicited response payloads, LPIB lock and wrap count, LPIB value, LPIB timer snapshot, input activity, channel layout, unsolicited-response enables, infoframe channel count/allocation/byte 5, and infoframe-valid.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1.5 translation units include `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Register-list macros paste symbolic register and field names into offset, mask, and shift macro names.
3. Helper macros such as `FD_MASK`, `FD_SHIFT`, block-specific field-list macros, and `REG_*` helpers materialize per-ASIC register tables.
4. Driver code later uses those tables to program or inspect audio endpoints, codec pin/converter state, hotplug/audio enable state, infoframes, LPIB snapshots, and DSC debug state.

The generated constants do not encode access ordering. Consumers must still handle hardware sequencing for display audio stream setup, pin/control updates, unsolicited responses, HBR/multichannel enablement, hotplug/audio enable transitions, LPIB snapshot locking, DSC debug selection, interrupt/status clearing, power gating, suspend/resume, and reset.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in memory or files. It describes MMIO-backed GPU state. The represented hardware state includes:

- Azalia input converter capabilities and active audio stream format/channel/stream controls for endpoints 1 through 7.
- Digital converter flags that describe whether an endpoint is enabled, valid, non-audio, professional, copyright-marked, category-coded, or using keepalive behavior.
- Input pin capabilities and controls for jack/presence sense, input enablement, multichannel routing/mute/channel IDs, HBR, channel allocation, audio enablement, and default configuration metadata.
- LPIB and timer snapshots used to observe audio buffer position and wrap count.
- Input activity, channel layout, infoframe change signaling, and infoframe payload status.
- DSCC, DSCCIF, and DSC_TOP debug selector/data state for display stream compression diagnostics.

Persistence is hardware-defined. Configuration fields usually retain programmed values until modeset, stream reconfiguration, power gating, suspend/resume, or ASIC reset. Status, sense, interrupt, unsolicited-response, LPIB, debug, and counter-like fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only supplies field geometry; it does not distinguish access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.5 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which supplies matching MMIO offsets.
- DCN base-address definitions used with the offset header to address the correct register segment.
- Common AMD display register helpers that derive masks and shifts by token pasting generated names.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`

Important integration areas:

- Display audio and Azalia/HDA-codec paths use the endpoint fields to advertise and control stream format, sample rate/size, digital converter state, pin capabilities, channel allocation, HBR, multichannel routing, infoframes, and hotplug/audio enable state.
- IRQ or status paths can use unsolicited-response, input activity, infoframe-change, and hotplug-related fields to report audio endpoint changes.
- Firmware-facing DMUB register tables depend on the same masks/shifts when exposing DCN 3.1.5 register fields to firmware service code.
- DSC diagnostics use the DSCC, DSCCIF, and DSC_TOP debug shift constants to select and read display stream compression debug signals.

## Risks And Edge Cases

- Field drift is the central risk. These are untyped preprocessor constants, so a wrong shift or mask can compile cleanly while targeting the wrong MMIO bits.
- The chunk boundary is artificial. The first line begins mid-block in `AZF0INPUTENDPOINT1`, so adjacent chunks are required for complete endpoint-1 coverage and whole-file conclusions.
- Repeated endpoint families are copy-sensitive. `AZF0INPUTENDPOINT2` through `AZF0INPUTENDPOINT7` are structurally similar but not interchangeable; an instance-specific typo may only fail on one physical/logical audio endpoint.
- Audio format and channel fields are user-visible. Incorrect sample size/rate/channel count, stream ID, channel allocation, HBR, or multichannel masks can cause silence, channel swaps, distorted audio, or failures limited to specific HDMI/DP audio formats.
- Digital converter control fields include validity, non-audio, professional, copyright, category-code, and keepalive bits. Misprogramming can affect sink negotiation, audio compliance behavior, or keepalive during blanking/idle periods.
- Hotplug, unsolicited response, input activity, and infoframe-change fields are event-sensitive. Bad masks can cause missed audio endpoint events, spurious notifications, stuck status bits, or resume-only audio failures.
- LPIB snapshot fields are timing-sensitive. Incorrect lock/wrap-count/value interpretation can produce wrong audio position reporting or races when snapshotting active streams.
- DSC debug registers are mostly shift-only in this chunk. Consumers must pair them with offsets and access semantics from other generated files and hardware documentation; these macros do not tell whether the debug data is stable, latched, or selector-dependent.
- The final `#endif` means any accidental edit near this chunk can break the entire header's include guard, affecting all DCN315 display builds.

## Test Signals

Useful validation combines generated-header consistency checks and display/audio behavior:

- Build AMDGPU/DC with DCN 3.1.5 support enabled. Missing or renamed masks/shifts should fail in `dcn315_resource.c`, `irq_service_dcn315.c`, `dmub_dcn315.c`, `hw_factory_dcn315.c`, `hw_translate_dcn315.c`, or shared display-register-table users.
- Mechanically verify that Azalia endpoint fields in lines 60080-62071 have expected `__SHIFT` and `_MASK` pairs where the generated schema defines both, and that shift-only debug fields are intentionally shift-only.
- Diff this slice against AMD's authoritative DCN 3.1.5 register database and neighboring DCN generated headers where compatibility is expected.
- Exercise HDMI/DP audio across endpoints: stereo and multichannel PCM, different sample rates and bit depths, HBR-capable formats, plug/unplug, stream start/stop, blanking, suspend/resume, and rapid display modesets.
- Validate channel allocation, infoframe-valid, input activity, unsolicited response, and hotplug/audio-enable behavior through sink-side audio tests and kernel logs.
- Monitor for audio dropouts, wrong channel mapping, no-sound-on-one-connector bugs, hotplug storms, missed audio endpoint changes, stuck interrupts/status bits, LPIB position anomalies, and resume-only failures.
- For DSC debug fields, enable DSC-capable display modes and confirm debug selectors/data paths remain readable and plausible when investigating compression issues.

## Cross-Chunk Notes

Previous chunks own the beginning of the Azalia F0 codec input endpoint section, including the start of `AZF0INPUTENDPOINT1`. This chunk completes the file after endpoint 7 and the DSCC/DSCCIF/DSC_TOP debug blocks. The final per-file report should merge adjacent chunks before making complete claims about all Azalia endpoint macros, all DSC debug macros, or the full `dcn_3_1_5_sh_mask.h` generated namespace.
