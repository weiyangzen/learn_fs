# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 61490-61940

## Purpose

This chunk is the final slice of the generated AMD DCN 3.6.0 register shift/mask header. It contains C preprocessor constants for Azalia/HDA input endpoint register fields, specifically the tail of `AZF0INPUTENDPOINT6_*` and the complete `azf0inputendpoint7_inputendpointind` address block. The macros let AMDGPU display/audio code pack and unpack individual bitfields in indexed Azalia input endpoint registers without embedding raw bit positions in runtime code.

The requested range contains 403 `#define` entries: 200 `__SHIFT` macros, 203 `_MASK` macros, 43 register/address comments, and the closing `#endif` for the whole header. The start boundary is artificial: it begins in the middle of `AZF0INPUTENDPOINT6_AZALIA_F0_CODEC_INPUT_CONVERTER_CONTROL_DIGITAL_CONVERTER`, so the earlier `DIGEN`, `V`, `VCFG`, `PRE`, `COPY`, `NON_AUDIO`, and `PRO` fields for endpoint 6 are defined in the previous chunk. The end boundary is semantic for the file: it completes endpoint 7 input status/infoframe fields and closes the include guard.

Although the path is inside a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata, not Ceph or distributed filesystem logic.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct MMIO operations in this range. The interface is entirely generated macros following the standard AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for isolating, inserting, or preserving that field during read/modify/write.

The chunk covers these register groups:

- Endpoint 6 tail fields:
  - Input converter digital converter masks for `L`, `CC`, and `KEEPALIVE`.
  - Input converter stream format and supported size/rate capabilities.
  - Input pin audio widget capabilities and pin capabilities.
  - Unsolicited response tag/enable fields, input pin sense, widget input enable, multichannel enable/mute/channel-id banks for channels 0-7, HBR capability/enable, channel allocation, hot-plug audio enable/clock control, forced unsolicited response payload, default pin configuration, LPIB snapshot/LPIB/timer snapshot, input status, and captured infoframe fields.
- Endpoint 7 complete indexed input endpoint block:
  - Converter audio widget capabilities, converter format, channel/stream ID, digital converter control, stream formats, and supported size/rate capabilities.
  - Input pin audio widget capabilities and pin capabilities.
  - The same control/status groups as endpoint 6: unsolicited response, input pin sense, widget control, multichannel enable banks, HBR, channel allocation, hot-plug control, forced unsolicited response, default configuration, LPIB snapshot, LPIB value, timer snapshot, input status control, and infoframe decode.

The companion offset header defines the register addresses and indexed register numbers that match these masks:

- `regAZF0INPUTENDPOINT6_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` / `DATA` and `regAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` / `DATA` are the indexed access ports.
- `ixAZF0INPUTENDPOINT6_*` and `ixAZF0INPUTENDPOINT7_*` provide the indirect register indices, including converter parameter/control indices `0x0001` through `0x0006`, pin control indices `0x0020` through `0x0038`, and status/infoframe indices `0x0053` through `0x0068`.

## Control Flow

This header has no runtime control flow. Its control-flow role is indirect:

1. DCN 3.6 display/audio code includes `dcn_3_6_0_offset.h` and `dcn_3_6_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into typed tables for display resources, audio blocks, interrupt service setup, and DMUB support.
3. Runtime helpers use those tables with register access macros such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`.
4. For Azalia indexed registers, software writes an endpoint index register, reads or writes the endpoint data register, then applies these shifts and masks to interpret or update the selected field.

The macros do not enforce sequencing. Consumers still need to follow HDA/Azalia rules for converter programming, stream ID assignment, channel allocation, HBR setup, unsolicited response enablement, LPIB snapshot locking, hot-plug/audio-enable state, and infoframe/status sampling.

## State And Persistence Behavior

This chunk stores no software state and persists nothing directly. It describes hardware-visible state in DCN 3.6 Azalia input endpoint registers:

- Audio capability state: widget capabilities, pin capabilities, supported stream formats, sample-rate capabilities, bit-depth capabilities, HDMI/DP capability bits, power-control capability, and HBR support.
- Stream programming state: number of channels, bits per sample, sample base rate/divisor/multiple, stream type, channel ID, stream ID, digital converter status/control flags, channel allocation, and multichannel enable/mute/channel IDs.
- Hot-plug and notification state: unsolicited response tag/enable, forced unsolicited response payload, input activity unsolicited-response enable, channel-layout/channel-status infoframe change enable, and hot-plug audio enable/clock bits.
- Status and sampling state: pin sense, LPIB snapshot lock, cyclic buffer wrap count, LPIB value, LPIB timer snapshot, input activity, channel layout, decoded infoframe channel count/allocation/byte 5, and infoframe-valid flag.
- Default pin configuration state: sequence, association, misc, color, connection type, default device, location, and port connectivity fields.

Persistence is hardware-defined. Capability registers are typically read-only descriptions. Control fields generally persist until rewritten by a modeset/audio reconfiguration, hot-plug handling, suspend/resume, GPU reset, or ASIC reset. Status, snapshot, force, unsolicited response, and infoframe-valid fields may be read-only, sticky, self-clearing, write-one-to-clear, sampled only after a lock bit, or valid only while the audio endpoint and related display engine are powered and clocked. This generated header does not encode access semantics, side effects, or valid programming order.

## Dependencies And Integration Points

The immediate dependency is synchronization with AMD's generated DCN 3.6.0 register database and the matching offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h` supplies the corresponding direct `reg*` indexed access ports and indirect `ix*` register numbers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` includes the generated offset and shift/mask headers, defines audio register tables with `AUD_COMMON_REG_LIST_RI(id)`, and creates DCE audio objects through `dce_audio_create()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c` includes the same generated DCN 3.6 headers for DMUB register programming support.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn36/irq_service_dcn36.c` includes the same generated headers for DCN 3.6 interrupt setup.
- Shared DCE/DCN audio code in `dce_audio.h` and related implementation files consumes audio register/shift/mask tables rather than spelling most endpoint-specific field names at each call site.

One notable integration detail is that `dcn36_resource.c` allocates `audio_regs[7]` and initializes entries 0 through 6, while `res_cap_dcn36` reports `num_audio = 5`. This chunk includes endpoint 7 generated definitions because the register database contains that block, but normal DCN 3.6 resource construction may not expose every generated endpoint as a runtime audio object.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while causing reads or writes to target the wrong bitfield.
- The file is generated. Manual edits risk diverging from the authoritative register database, the companion offset header, firmware assumptions, and hardware documentation.
- The chunk starts mid-register for endpoint 6, so any completeness check must combine this range with the previous chunk before deciding whether all digital converter fields have paired shifts and masks.
- Endpoint 6 and endpoint 7 groups are mechanically similar. Generator drift or copy errors can affect only one endpoint while adjacent endpoint smoke tests still pass.
- Indexed-register access is sensitive to pairing the correct endpoint index/data ports with the correct `ix*` register numbers. A mismatch can read or program a different endpoint than the masks imply.
- Stream format and channel layout fields are interoperability-sensitive. Incorrect masks can produce silent audio, wrong channel mapping, invalid HBR behavior, or bad HDMI/DP audio infoframes.
- Hot-plug, unsolicited response, input activity, and infoframe-change fields can affect interrupt behavior. Confusing enable, force, status, and payload fields can cause missed notifications, repeated notifications, or stale status.
- LPIB snapshot fields can be timing-sensitive. Reading LPIB/timer snapshots without honoring lock and wrap-count behavior can produce inconsistent position reporting.
- Capability masks for HDMI, DP, HBR, supported rates, supported bit depths, and pin capabilities influence feature advertisement. Wrong values may expose unsupported formats or hide valid display-audio modes.

## Test Signals

Useful validation is mostly build, generator-consistency, and hardware audio behavior:

- Build AMDGPU display support with DCN 3.6 enabled. Missing or renamed constants should fail where DCN36 resource, DMUB, IRQ, or audio register tables are constructed.
- Mechanically compare this range against AMD's authoritative DCN 3.6.0 register source and `dcn_3_6_0_offset.h`, including the artificial endpoint 6 boundary at line 61490.
- Check that complete register groups have both `__SHIFT` and `_MASK` definitions when adjacent chunks are considered together.
- Exercise HDMI/DP display audio on DCN 3.6 hardware across hot-plug, modeset, suspend/resume, and GPU reset.
- Validate PCM format negotiation across sample rates, bit depths, channel counts, channel allocation maps, and HBR-capable streams.
- Monitor unsolicited responses, input activity, infoframe-change events, and hot-plug audio enable behavior for missed or repeated notifications.
- Read back LPIB, LPIB timer snapshot, cyclic buffer wrap count, input status, and infoframe fields while audio is active to catch stale or incorrectly masked status bits.
