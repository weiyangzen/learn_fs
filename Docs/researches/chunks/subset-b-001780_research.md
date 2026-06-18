# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 7903-8471

## Scope

This chunk is the closing segment of the generated AMD DCN 3.0.3 register-offset header. It contains preprocessor constants only: symbolic indirect-register indices for Azalia/HD-audio codec endpoint windows. The assigned range spans 569 source lines, with 519 `#define` entries, 335 output-endpoint index definitions, 184 input-endpoint index definitions, 12 visible `addressBlock` comments, and the file's final `#endif`.

The chunk starts inside the `azf0endpoint3_endpointind` output endpoint block, at `AUDIO_DESCRIPTOR2`; the beginning of endpoint3, plus endpoint0 through endpoint2, are in prior chunks. The range then covers full output endpoint blocks 4 through 7, full input endpoint blocks 0 through 7, and closes the include guard.

## Purpose

The purpose of this header segment is to expose hardware-defined Azalia codec endpoint register indices for the DCN 3.0.3 AMDGPU display path. These `ix...` constants are the values written to each endpoint's `AZALIA_F0_CODEC_ENDPOINT_INDEX` or `AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` register before reading or writing the paired endpoint data register.

The covered surface is display-audio related rather than filesystem logic despite the repository path prefix. It describes HDMI/DP audio codec widgets associated with display outputs and input/audio-capture style endpoint windows. The constants let shared DCE/DCN audio helpers address codec verb-like endpoint registers without embedding raw numeric index values in runtime code.

## Address Blocks And Register Surface

Visible output endpoint blocks:

- Tail of `azf0endpoint3_endpointind`: output endpoint 3 pin-control descriptors, sink info, hot-plug/audio enable, LPIB, coding/format status, and interrupt status indices.
- `azf0endpoint4_endpointind` through `azf0endpoint7_endpointind`: complete output endpoint blocks, each with converter parameter/control indices from `0x0001` through `0x000e` and pin-control/status indices from `0x0020` through `0x006e`.

Visible input endpoint blocks:

- `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`: complete input endpoint blocks. Each block has input converter indices `0x0001` through `0x0006`, input pin capability/sense/widget indices `0x0020` through `0x0024`, multichannel/HBR indices `0x0036` through `0x0038`, channel allocation and hot-plug/configuration indices `0x0053` through `0x0056`, LPIB snapshot/readback indices `0x0064` through `0x0066`, and input status/infoframe indices `0x0067` and `0x0068`.

Companion direct MMIO addresses for these indirect windows are defined earlier in the same header. For example, output endpoint 3 through 7 endpoint-index registers are `mmAZF0ENDPOINT3_AZALIA_F0_CODEC_ENDPOINT_INDEX` through `mmAZF0ENDPOINT7_AZALIA_F0_CODEC_ENDPOINT_INDEX`, while input endpoint 0 through 7 endpoint-index registers are `mmAZF0INPUTENDPOINT0_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` through `mmAZF0INPUTENDPOINT7_AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX`.

## Important Macros And Register Families

The `ixAZF0ENDPOINT[3-7]_AZALIA_F0_CODEC_CONVERTER_*` constants describe output converter widgets. They include audio widget capabilities, converter format, channel/stream ID, digital converter control, supported stream formats, supported sample sizes/rates, stripe control, ramp rate, GTC embedding, and GTC counter delta/min/max indices. These are per-endpoint offsets within an indirect Azalia endpoint address space, not absolute MMIO addresses.

The `ixAZF0ENDPOINT[3-7]_AZALIA_F0_CODEC_PIN_*` and `...PIN_CONTROL_*` constants describe output pin widgets. The visible families cover pin capabilities and sense, widget control, channel/speaker allocation, audio descriptors 0-13, multichannel enable/mode, lip-sync response, HBR response, sink info 0-8, hot-plug control, unsolicited response force, response configuration default, channel-status override registers 0-8, association info, digital output status, LPIB snapshot/readback, coding type, format-changed status, wireless display identification, remote keepalive, audio-enable status, and audio enabled/disabled/format-changed interrupt status.

The `ixAZF0INPUTENDPOINT[0-7]_AZALIA_F0_CODEC_INPUT_CONVERTER_*` constants mirror the converter capability and stream-format surface for input endpoints, but the input converter block is smaller: it does not include the output-only stripe, ramp, or GTC delta indices present in the output endpoint blocks.

The `ixAZF0INPUTENDPOINT[0-7]_AZALIA_F0_CODEC_INPUT_PIN_*` constants describe input pin widgets. These include input pin capabilities and sense, widget control, multichannel enables, HBR response, channel allocation, hot-plug control, unsolicited response force, response configuration default, LPIB snapshot/readback, input activity/status control, and audio infoframe readback.

The repeated numeric layout is a key property. Output endpoints use the same indirect index values across endpoint instances, and input endpoints likewise repeat a smaller common layout across input instances. This lets higher-level code combine an endpoint instance's MMIO index/data pair with a common indirect register number.

## Control Flow And Runtime Behavior

There is no executable C control flow in this chunk. Runtime behavior is indirect through register helpers that consume these constants.

The relevant flow in the AMD display code is:

1. DCN 3.0.3 resource construction includes `dcn/dcn_3_0_3_offset.h` and `dcn/dcn_3_0_3_sh_mask.h`.
2. `dcn303_resource.c` builds `audio_regs[]` using `AUD_COMMON_REG_LIST(id)`, which expands through `SRI(AZALIA_F0_CODEC_ENDPOINT_INDEX, AZF0ENDPOINT, id)` and `SRI(AZALIA_F0_CODEC_ENDPOINT_DATA, AZF0ENDPOINT, id)` from `dce_audio.h`.
3. `dcn303_create_audio()` passes the selected register pair plus shift/mask tables into `dce_audio_create()`.
4. `dce_audio.c` performs indirect Azalia access by writing a register index to `AZALIA_F0_CODEC_ENDPOINT_INDEX` and then reading or writing `AZALIA_F0_CODEC_ENDPOINT_DATA`.

The output endpoint `ix...` constants in this chunk are the values that can be written in step 4 for the matching endpoint window. Although the DCN303 resource file creates `audio_regs[]` entries for instances 0 through 6, `res_cap_dcn303.num_audio` is 2, so only the active resource count is normally instantiated by the DC resource pool. The extra endpoint macros still remain part of the generated hardware namespace and may be needed for ASIC variants, diagnostics, or shared generated-header consistency.

Input endpoint constants are not wired by the same `dce_audio` helper path visible in `dcn303_resource.c`, which uses output `AZF0ENDPOINT` windows. They expose the hardware's input endpoint indirect register map for consumers that need capture/status/infoframe surfaces, even if no local DCN303 resource constructor in the inspected code instantiates them directly.

## State And Persistence

The macros themselves hold no state and allocate no storage. They name persistent hardware registers inside indirect endpoint address spaces. When driver code writes through an endpoint index/data pair, the target state persists in the audio codec/display hardware until changed by another write, reset, power transition, suspend/resume reinitialization, or mode-set/audio reprogramming.

Important state classes represented by this chunk:

- Audio format and stream state: converter format, stream ID, digital converter, supported formats/rates, coding type, and format-changed status control how the endpoint advertises and tracks the active audio stream.
- Sink capability state: audio descriptor registers, sink info registers, speaker/channel allocation, HBR capability, lip-sync response, and response configuration default represent EDID/ELD-derived or hardware-exposed capabilities that userspace and the audio stack depend on.
- Hot-plug and unsolicited response state: hot-plug control, pin sense, unsolicited response, and forced unsolicited response indices participate in connector/audio-jack change reporting.
- Runtime position state: LPIB snapshot control, LPIB, and LPIB timer snapshot expose link-position and timing state. Snapshot lock and timer semantics are defined by companion shift/mask registers and hardware documentation, not by this offset file alone.
- Interrupt/status state: audio enabled, disabled, and format-changed interrupt status indices expose latched events for output endpoints; input status control and infoframe indices expose activity and channel-layout changes for input endpoints.
- Channel-status override state: output endpoint channel-status override indices 0-8 are persistent hardware registers that can affect the channel-status bits sent with digital audio.

## Dependencies And Integration Points

This chunk depends on the rest of `dcn_3_0_3_offset.h` for the direct MMIO addresses of the endpoint index/data windows, and on `dcn_3_0_3_sh_mask.h` for the bitfields inside both the direct index/data registers and the indirect endpoint registers. It is included by at least the DCN303 resource, IRQ, and DMUB source files, although the audio endpoint constants are most directly relevant to the resource/audio path.

Primary integration points:

- `display/dc/resource/dcn303/dcn303_resource.c`: includes the generated DCN 3.0.3 headers, declares `res_cap_dcn303.num_audio = 2`, constructs `audio_regs[]`, and creates DCE audio objects through `dce_audio_create()`.
- `display/dc/dce/dce_audio.h`: defines `AUD_COMMON_REG_LIST(id)` and the shift/mask table layout used for endpoint index/data access.
- `display/dc/dce/dce_audio.c`: implements indirect Azalia register access by writing `AZALIA_ENDPOINT_REG_INDEX` and then reading/writing `AZALIA_ENDPOINT_REG_DATA`.
- `display/dc/irq/dcn303/irq_service_dcn303.c` and `display/dmub/src/dmub_dcn303.c`: include the same generated offset/mask headers for DCN303 register table construction, though this particular chunk has no obvious IRQ or DMUB-specific endpoint consumer in the inspected source.
- Companion generated enum headers such as `soc21_enum.h`, `soc24_enum.h`, `navi10_enum.h`, and `vega10_enum.h` define symbolic enum values for related Azalia input endpoint fields.

Because this is a generated public include inside AMDGPU, compile-time consumers depend on exact macro spelling. A missing or renamed `ix...` definition can break register-table builds; an incorrect value can silently redirect an indirect read/write to the wrong Azalia endpoint register.

## Risks And Edge Cases

- Generated-header drift is the main risk. If an `ix` value is wrong, audio code can program the wrong indirect endpoint register while all C code still compiles.
- The assigned range starts mid-block. Endpoint3 converter, capability, pin sense, widget control, channel speaker, and descriptor0/descriptor1 definitions are above line 7903. The final per-file report must merge adjacent chunks before treating endpoint3 as complete.
- The range ends at `#endif`. There is no following chunk for this source file's include guard, but there may be adjacent chunks that complete the earlier endpoint blocks.
- Output and input endpoint families look similar but are not identical. Input endpoints omit several output-only converter controls and audio descriptor/sink-info/channel-status override families. Scripts that assume a single common endpoint layout across both families may produce invalid accesses.
- Numeric index reuse is intentional across endpoint instances. A deduplication tool must preserve the endpoint instance prefix (`AZF0ENDPOINT4`, `AZF0INPUTENDPOINT4`, etc.) because the same index value targets different hardware windows depending on which direct MMIO index/data pair is used.
- DCN303 exposes more generated endpoint definitions than the resource pool normally instantiates (`num_audio = 2`). Reviewers should distinguish generated hardware addressability from runtime resource count.
- Indirect register programming is sequencing-sensitive. The offset header does not encode whether a target register is read-only, write-one-to-clear, self-clearing, sticky, or safe only while audio is disabled.
- Status and interrupt registers can interact with hot-plug, audio enable/disable, and format-change handling. Incorrect polling or acknowledgement behavior may cause missed audio state changes or repeated interrupts even when the index constants are correct.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage for the DCN303 display resource path, especially `dcn303_resource.c`, `dce_audio.h`, and `dce_audio.c`, to catch missing endpoint index/data register macros and shift/mask names.
- Generated-header consistency checks verifying that endpoint blocks 4-7 have identical output indirect index layouts, input endpoint blocks 0-7 have identical input layouts, index values remain within the expected `0x0001`-`0x006e` range, and every indirect register with bitfields has corresponding entries in `dcn_3_0_3_sh_mask.h`.
- HDMI/DP audio mode-set tests that exercise audio enable, stream format programming, channel/speaker allocation, audio descriptors, HBR support, lip-sync fields, and hot-plug audio state.
- ELD/sink-capability tests that compare descriptor and sink-info programming/readback against monitor EDID/ELD expectations.
- Suspend/resume and GPU reset tests that verify audio endpoint state is restored and stale format-change or enable/disable status does not survive incorrectly.
- Interrupt/status tests for audio enabled, disabled, and format-changed events, plus unsolicited response and pin-sense behavior across display hot-plug.
- Diagnostic readback tests for LPIB snapshot/timer values and input endpoint activity/infoframe fields if input endpoint surfaces are used on the target ASIC.

## Open Questions For Merge Lane

- Merge the previous chunk to recover the start of `azf0endpoint3_endpointind` and confirm endpoint3 has the same full output layout as endpoints 4-7.
- Confirm whether endpoint7 output and input blocks represent usable DCN303 hardware on all supported ASICs or are generated superset definitions beyond the normal `num_audio = 2` resource count.
- Identify any non-DC resource or firmware diagnostic path that uses the `AZF0INPUTENDPOINT[0-7]` indirect indices, since the inspected `dce_audio` path is output-endpoint oriented.
