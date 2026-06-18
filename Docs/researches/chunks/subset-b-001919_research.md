# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 54347-56952

## Chunk Scope

This chunk is a generated AMD DCN 3.1.6 ASIC register shift/mask header segment. It contains preprocessor constants only: `#define` pairs for hardware bitfield offsets (`__SHIFT`) and masks (`_MASK`), plus generated comments that preserve register and address-block grouping. There are no C functions, structs, enums, global variables, or executable branches in the selected lines.

The range contains 2,606 source lines with 2,058 macro definitions: 1,062 shift constants and 996 mask constants. It spans 32 address blocks and 452 register comments. The chunk starts in the tail of the DCHVM host-VM register block and ends partway through endpoint 1 Azalia pin-control fields, so the final per-file report should merge this with neighboring chunks before making whole-file claims.

## Purpose

The purpose of this header region is to provide symbolic bit layouts for DCN 3.1.6 display, VGA compatibility, performance-monitor, and display-audio hardware registers. AMDGPU display code does not normally hand-code these bit values. Instead, register table builders and helpers such as `FD_MASK`, `FD_SHIFT`, `SF`, `SRI`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` use these generated symbols to create register-access tables and compose MMIO read/modify/write operations.

At a hardware level, this chunk covers:

- DCHVM host-VM initialization, display/DCF clock-gating controls, GPUVM retention power request controls, RIOMMU prefetch request/status, and active/done status fields.
- DC perfmon debug counter fields for eight clock-domain counters, event selectors, start/stop events, and per-clock counter-off bits.
- Legacy VGA sequencer, CRTC, graphics-controller, and attribute-controller indexed fields.
- Display Azalia F2 codec output and input converter/pin/root-function fields.
- Audio descriptor, sink-info, CRC result, and stream latency/debug fields for the display audio controller.
- Azalia F0 endpoint 0 and the beginning of endpoint 1 converter and pin fields, including stream format, channel/stream IDs, digital converter control, GTC embedding, pin capabilities, channel/speaker allocation, sink info, interrupt status, and multichannel enable fields.

## Important Macro Groups

### DCHVM Host-VM And RIOMMU Fields

The chunk begins after `DCHVM_CLK_CTRL` was introduced by the previous chunk. Visible fields include display clock and DCF clock root/gate disable bits, request/response clock-request modes, GPUVM retention power request disable/force/status fields, RIOMMU prefetch request and power status, and RIOMMU active/prefetch-done status.

These constants line up with hubbub code patterns in nearby DCN generations that initialize the host-VM block by setting `HOSTVM_INIT_REQ`, reading `RIOMMU_ACTIVE`, setting `HOSTVM_POWERSTATUS`, issuing `HOSTVM_PREFETCH_REQ`, waiting for `HOSTVM_PREFETCH_DONE`, and controlling DCHVM clock-gating and memory retention. The macros in this chunk are therefore stateful hardware-control fields even though the header itself is static.

### Perfmon Debug Fields

The `dc_perfmon_dc_perfmondebugind` block defines `PERFMON_DEBUG_ID` and `PERFMON_DEBUG01` through `PERFMON_DEBUG12`. The layout exposes low and high counter words for clock counters 0 through 7, event selector fields in the high-word registers, event start/stop bits in `PERFMON_DEBUG09`, and per-clock plus global counter-off bits in `PERFMON_DEBUG12`.

The defined fields are diagnostic infrastructure. Consumers can select a debug counter/event, start or stop collection, read low/high values, and turn individual counters off. Bugs here would usually show as broken performance/debug telemetry rather than ordinary modeset failures.

### VGA Compatibility Indexed Blocks

Four legacy VGA indexed address blocks are covered:

- `vga_vgaseqind`: `SEQ00` through `SEQ04` reset, dot clock, shift, plane map enable, font-bank, memory size, odd/even, and chain fields.
- `vga_vgacrtind`: `CRT00` through `CRT18`, plus `CRT1E`, `CRT1F`, and `CRT22`, covering horizontal/vertical total, display end, blanking, sync start/end, cursor location/shape, display start, offset, underline, CRTC mode, line compare, and graphics controller index.
- `vga_vgagrphind`: `GRA00` through `GRA08` set/reset, enable set/reset, color compare, rotate, read/write mode, odd/even, chain, memory map select, color don't-care, and bit mask fields.
- `vga_vgaattrind`: `ATTR00` through `ATTR14` palette entries, graphics/text mode controls, monochrome/logical graphics, blink, pixel panning, color select, overscan, plane enable, and pixel shift/count fields.

These fields preserve VGA register compatibility in the generated DCN register map. They are not modern display pipe programming knobs, but wrong masks can affect firmware/BIOS compatibility paths, VGA console handoff, or low-level diagnostic access.

### Azalia F2 Output Codec Fields

The `azendpoint_f2codecind` block defines display-audio codec fields with an `AZALIA_F2_CODEC_*` namespace. The converter side includes format fields (`NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, sample base divisor/multiple/rate, and stream type), channel/stream ID, digital converter channel status bits (`DIGEN`, validity/config, pre/copy/non-audio/professional/level, category code), stripe control, ramp rate, GTC embedding, audio widget capabilities, supported rates/sizes, and stream formats.

The pin side includes connection-list entry, widget output enable, unsolicited-response tag/enable, pin sense, configuration defaults, speaker/channel allocation, downmix information, ACP data, audio descriptors, multichannel enables, lipsync, HBR, sink-info index/data, codec channel-status override registers, digital output status, LPIB snapshot/counter fields, coding type, format-change status/response, wireless display identification, remote keepalive, widget capabilities, pin capabilities, and connection-list length.

These constants back endpoint discovery and programming for HDMI/DP audio. For example, resource construction comments in display core mention using `AZALIA_F0_CODEC_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT`-style registers to find valid audio pins; the F2 register family carries analogous pin default/capability information for the F2 codec namespace.

### Audio Descriptor, Sink Info, And CRC Blocks

The `azendpoint_descriptorind` block defines `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, each carrying maximum channels, supported frequencies, descriptor byte 2, and for descriptor 0 a stereo-specific supported-frequency byte. The `azendpoint_sinkinfoind` block exposes manufacturer ID, product ID, sink description length, port ID words, and sink description string words 0 through 17.

The chunk also defines input and output CRC result windows: `AZALIA_INPUT_CRC0_CHANNEL0` through `CHANNEL7`, `AZALIA_INPUT_CRC1_CHANNEL0` through `CHANNEL7`, `AZALIA_CRC0_CHANNEL0` through `CHANNEL7`, and `AZALIA_CRC1_CHANNEL0` through `CHANNEL7`. Each is a full-width CRC result field. These fields are likely used for audio validation, debug, or hardware self-test rather than normal audio enable sequencing.

### Azalia F2 Input Codec And Root Function Fields

The `azinputendpoint_f2codecind` block mirrors many output-codec patterns for input audio. It defines input converter format, channel/stream ID, digital converter status/control, audio widget capabilities, supported rates/sizes, stream formats, input pin widget/unsolicited/pin-sense/configuration fields, channel allocation, multichannel enable fields for channels 0 through 7, HBR, LPIB snapshot and timer fields, input status control, infoframe checksum/version/length/bytes, channel status low/high, input pin widget capabilities, and input pin capabilities.

The `azroot_f2codecind` block defines root/function-level metadata and controls: vendor/device ID, revision ID, subordinate node count, power state set/reset/actual/status, subsystem ID response fields, converter synchronization, reset, group type, supported size/rate and stream-format parameters, and supported power states including D0/D1/D2/D3, clock-stop, and EPSS support.

### Azalia Stream Instances 0-15

The `azf0stream*_streamind` blocks repeat the same stream-debug layout for stream instances 0 through 15. Each instance defines FIFO size control, latency counter reset, worst-case latency count, cumulative latency count, cumulative request count, and stream debug status. The FIFO control fields include FIFO allocation, FIFO size, and enable; stream debug exposes the active stream ID.

This repetition is an important integration point for display audio stream accounting. Runtime code can configure or inspect a stream instance by using generated array/register-list macros against `AZF0STREAM<n>` names while sharing one implementation body.

### Azalia F0 Endpoint 0

The `azf0endpoint0_endpointind` block is the largest complete block in this chunk. It defines endpoint 0 converter pin debug, converter widget capabilities, converter format and channel/stream ID, digital converter control, stream formats, supported size/rate fields, stripe control, ramp rate, GTC embedding, GTC offset debug, and GTC counter delta/min/max readbacks.

The pin side includes widget capabilities, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker allocation, ACP data, audio descriptors 0 through 13, two multichannel-enable register groups, lipsync, HBR, sink-info registers, hot-plug control, forced unsolicited response, default pin configuration, multichannel mode, IEC 60958 channel-status override registers 0 through 8, association information, digital output status, LPIB snapshot/data/timer fields, coding type, format-change status and response, wireless display ID, remote keepalive, audio enable status, and audio enabled/disabled/format-changed interrupt status fields.

Endpoint 0 is likely the primary display-audio endpoint used by DCN 3.1.6 audio paths. The broader display code uses `AUD_COMMON_REG_LIST(id)` and DCN resource tables to create per-audio-instance `AZF0ENDPOINT` index/data registers; the detailed endpoint fields in this chunk are the data payload layout behind those indexed accesses.

### Beginning Of Azalia F0 Endpoint 1

The final address block starts `azf0endpoint1_endpointind` and covers endpoint 1 through `AZF0ENDPOINT1_AZALIA_F0_CODEC_PIN_CONTROL_ACP_DATA__ACP_TYPE_DEPENDENT_BYTE0__SHIFT`. The visible endpoint 1 layout mirrors endpoint 0 for converter pin debug, converter widget capabilities, converter format, channel/stream ID, digital converter channel-status bits, stream formats, size/rate capabilities, stripe/ramp/GTC controls, pin widget capabilities, pin capabilities, unsolicited response, pin sense, widget output enable, channel/speaker allocation, and the first ACP data fields.

Because the chunk ends mid-register family, endpoint 1 audio descriptor and later pin-control/status fields must be read from the following chunk before synthesizing a whole-file report.

## Important APIs, Types, And Functions

This range exports no callable APIs or C types. Its interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask for the same field.
- Register comments such as `//AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER` and address-block comments such as `// addressBlock: azf0stream0_streamind` preserve generated grouping and instance identity.

The practical consumers are generated register-list tables and display register helpers. Concrete integration examples visible elsewhere in the tree include `dmub_dcn316.c`, which includes `dcn_3_1_6_offset.h` and this `dcn_3_1_6_sh_mask.h` to populate the DCN 3.1.6 DMUB register table with `FD_MASK` and `FD_SHIFT`, and `dcn316_resource.c`, which builds audio shift/mask tables for `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and endpoint data registers. The DCE audio common header maps `AZF0ENDPOINT` index/data registers into `struct dce_audio_registers`, `struct dce_audio_shift`, and `struct dce_audio_mask`.

## Control Flow

There is no runtime control flow in the chunk. Its effective flow is compile-time and table-driven:

1. DCN 3.1.6-specific source files include the matching offset and shift/mask headers.
2. Register table macros concatenate register and field names into generated symbols such as `DCHVM_RIOMMU_STAT0__HOSTVM_PREFETCH_DONE_MASK` or `AZF0ENDPOINT0_AZALIA_F0_CODEC_PIN_CONTROL_CHANNEL_SPEAKER__DOWN_MIX_INHIBIT__SHIFT`.
3. Runtime display code uses the populated register, mask, and shift tables with helpers like `REG_UPDATE`, `REG_GET`, `REG_WAIT`, indexed register access, and DMUB service register operations.
4. Sequencing lives outside this header: hubbub code drives DCHVM init/prefetch and power transitions; display audio code discovers endpoints, configures codecs, enables/disables Azalia audio, programs stream formats, reads sink capabilities, and handles status/interrupt fields.

The generated order is hardware-block order, not execution order. Most registers list all shift macros first and then the matching mask macros, and repeated instances are ordered numerically (`AZF0STREAM0` through `AZF0STREAM15`, then `AZF0ENDPOINT0`, then `AZF0ENDPOINT1`).

## State And Persistence Behavior

The header stores no software state and performs no persistence. The state represented by the macros is hardware state:

- DCHVM fields persist in MMIO registers across the relevant power domain lifetime and control initialization, power status, retention, clock gating, RIOMMU activity, and prefetch completion.
- Perfmon debug counters accumulate hardware counts until reset/disabled or reconfigured; high/low counter fields and counter-off bits are stateful diagnostics.
- VGA indexed registers represent legacy display state such as CRTC timing, cursor, display start, VGA memory access mode, palette/attribute mode, and plane selection.
- Azalia codec, stream, descriptor, sink-info, LPIB, GTC, CRC, and interrupt-status fields reflect display-audio endpoint state, stream assignments, negotiated sink capabilities, timing snapshots, and hardware event flags.

Several fields have clear write-one/ack or handshake semantics implied by their names, such as DCHVM `HOSTVM_PREFETCH_REQ`/`HOSTVM_PREFETCH_DONE`, audio enabled/disabled/format-changed interrupt flags and masks, format-change acknowledgement/response fields, LPIB snapshot lock, hot-plug control, and unsolicited response force. Incorrect bit positions in these fields can cause hangs, missed interrupts, or stale capability reads even though the header itself has no mutable storage.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.1.6 offset header for register addresses and base-index selection. It is useful only when included with code that supplies register accessors and field-table macros.

Important integration points include:

- `display/dmub/src/dmub_dcn316.c`: includes this header and the matching offset header to build the DCN 3.1.6 DMUB register, mask, and shift tables.
- HubBub/DCHVM code in nearby DCN generations: uses `DCHVM_CTRL0`, `DCHVM_MEM_CTRL`, `DCHVM_CLK_CTRL`, `DCHVM_RIOMMU_CTRL0`, and `DCHVM_RIOMMU_STAT0` fields for host-VM initialization and RIOMMU prefetch sequencing.
- `display/dc/dce/dce_audio.h`: defines common Azalia audio register/mask/shift structures and register-list macros around `AZF0ENDPOINT` index/data access.
- `display/dc/resource/dcn316/dcn316_resource.c`: populates DCN 3.1.6 display-audio shift/mask tables using the generated endpoint index/data field names.
- `display/dc/core/dc_resource.c`: constructs audio resources, probes endpoint validity, and comments on using Azalia pin configuration default registers to discover available display audio pins.
- Audio, AFMT/APG, stream encoder, and HPO DP paths: consume audio endpoint and stream state indirectly when configuring HDMI/DP audio, channel allocation, mute/control packets, audio stream IDs, and sink capability propagation.

The file also cross-relates to generated enum headers such as `soc24_enum.h`, which provide named values for some audio fields. The shift/mask header supplies layout; enum headers supply semantic values.

## Risks And Edge Cases

- Generated-header drift is the primary risk. A single stale mask or shift can silently corrupt MMIO programming and affect display audio, power management, diagnostics, or legacy VGA compatibility.
- This chunk starts and ends mid-context. DCHVM `CTRL0`/`CTRL1` and the opening of `DCHVM_CLK_CTRL` are in the previous chunk, while the rest of endpoint 1 is in the next chunk. Whole-file conclusions must reconcile adjacent chunks.
- Repeated audio instances invite copy/paste or generator bugs. `AZF0STREAM0` through `AZF0STREAM15` and endpoint 0/1 mirrored fields should remain structurally consistent except where the hardware spec intentionally differs.
- Interrupt/status fields whose names include `FLAG`, `MASK`, `TYPE`, `ACK`, or `RESPONSE` are sensitive to polarity and write semantics. The header cannot express access type; call sites must still follow hardware programming guidance.
- VGA compatibility fields are easy to dismiss as legacy, but incorrect definitions can break early console, VGA handoff, emulator paths, or firmware assumptions.
- Full-width masks such as CRC result, sink-description, LPIB, GTC delta, and descriptor data fields must remain `0xFFFFFFFFL`; narrowing them would truncate diagnostic or capability payloads.
- Audio descriptor/channel allocation fields cross software boundaries: EDID-derived audio information, ALSA/HD-audio behavior, and display link programming all depend on consistent interpretation of channel count, sample rate, bit depth, downmix, HBR, and speaker allocation fields.

## Test Signals

Useful validation signals for changes touching this range include:

- Build coverage for DCN 3.1.6 display code so all generated macro references used by `dmub_dcn316.c`, `dcn316_resource.c`, DCHVM tables, and DCE audio tables compile.
- Register-table sanity checks that compare generated offsets, masks, and shifts against the authoritative ASIC XML/spec output for DCN 3.1.6.
- Display audio smoke tests over HDMI and DisplayPort: endpoint discovery, audio device enumeration, PCM playback at common sample rates and bit depths, multichannel channel allocation, HBR/non-PCM paths, mute/disable/re-enable, and hotplug while audio is active.
- Audio capability checks against EDID: descriptor count, supported frequencies, maximum channel count, speaker allocation, sink description/manufacturer/product/port ID, and pin default configuration.
- DCHVM/host-VM tests on systems using GPUVM retention and RIOMMU prefetch: successful display bring-up, no timeout waiting for `HOSTVM_PREFETCH_DONE`, stable power-gating transitions, and no display memory fault regressions.
- Perfmon/debug validation: counters start/stop, per-clock counter-off bits behave as expected, selected event fields produce nonzero counts under known workloads, and high/low counter reads compose correctly.
- VGA fallback checks: firmware console handoff, simple framebuffer/VGA text compatibility where applicable, and no regressions in low-resolution boot or recovery modes.
- Interrupt/status testing for endpoint 0 audio enabled, disabled, and format-changed events, including mask/type decoding and acknowledgement behavior.
