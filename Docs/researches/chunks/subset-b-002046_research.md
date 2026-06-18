# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 47066-49630

## Scope

This chunk is a generated AMD DCN 3.2.1 register shift/mask slice. It contains preprocessor constants only: `_SHIFT` macros define field least-significant bit positions and `_MASK` macros define field masks already positioned within the register. `//<REGISTER>` comments group the constants by hardware register, and `// addressBlock:` comments identify the indexed or MMIO register block being described.

There are no C functions, structs, enums, loops, branches, allocation paths, locking primitives, direct MMIO calls, or persistent data structures in this range. Runtime behavior comes from AMDGPU Display Core code that includes this header together with matching offset headers and uses the constants through register helper macros.

The range starts in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6`; the shifts and early masks for that register are in the preceding chunk. It ends on the comment for `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL4_ENABLE`; that register's field definitions begin in the next chunk. The final per-file reconciliation should merge adjacent chunks before treating either boundary register as complete.

## Purpose And Hardware Surface

The file is the `sh_mask` companion for DCN 3.2.1 display hardware register definitions. The macros let display and audio code compose writes and decode reads without hardcoding bit positions. This chunk spans two major surfaces:

- High-performance DisplayPort output pieces: the tail of DP Sym32 encoder 3 secondary-data-packet control, HPO DP link encoder 0/1 clock/spare controls, and DP DPHY Sym32 instances 0/1.
- Display audio and legacy display compatibility pieces: the HDA/Azalia controller, HDA endpoints, output stream descriptors 0-7, legacy VGA indexed sequencer/CRT/graphics/attribute registers, HDMI/DP codec endpoint controls, audio descriptors, sink info storage, audio CRC result blocks, and the start of the Azalia input codec endpoint.

The chunk defines 2,074 `#define` lines and 435 comment/group lines. Its address blocks are:

- `dce_dc_hpo_dp_link_enc0_dispdec` and `dce_dc_hpo_dp_link_enc1_dispdec` for HPO DP link encoder clock control.
- `dce_dc_hpo_dp_dphy_sym320_dispdec` and `dce_dc_hpo_dp_dphy_sym321_dispdec` for DP 32-symbol physical/link scheduling, test pattern, error, symbol override, and CRC fields.
- `dce_dc_hda_azcontroller_azdec`, `azendpoint`, `azinputendpoint`, `azroot`, and `azstream0` through `azstream7` for HD Audio command rings, response rings, immediate command interfaces, DMA position buffers, wall clock, endpoints, and stream descriptors.
- `vga_vgaseqind`, `vga_vgacrtind`, `vga_vgagrphind`, and `vga_vgaattrind` for legacy VGA indexed register bit layouts.
- `azendpoint_f2codecind`, `azendpoint_descriptorind`, and `azendpoint_sinkinfoind` for display codec converter, pin widget, audio descriptor, and sink metadata controls.
- `azf0controller_azinputcrc0resultind`, `azinputcrc1resultind`, `azcrc0resultind`, and `azcrc1resultind` for per-channel audio CRC readback.
- `azinputendpoint_f2codecind` for the beginning of input codec converter and input pin controls.

## Important Definitions

The generated API pattern is consistent throughout this chunk:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the corresponding mask in register position.
- Full-width fields use masks such as `0xFFFFFFFFL`; one-bit controls and statuses use single-bit masks.

Important DisplayPort definitions include:

- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL6` through `GSP_CONTROL14` define Generic SDP enable, idle/video continuous transmission, one-shot trigger, double-buffer, payload size, start-of-frame reference, pending/deadline status, and line-number fields. `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_CONTROL` adds SDP stream enable, GSP0 priority, and CRC16 enable.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_AUDIO_CONTROL0/1` cover audio secondary packet enables for ASP/ATP/AIP/ACM/ISRC, ASP priority, ATP version, audio mute/status, and ASP concatenation sample-count limits.
- `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_METADATA_PACKET_CONTROL`, `VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, `VID_PANEL_REPLAY_CONTROL`, and `VID_CRC_*` define metadata packet double buffering, MSA/VBID line timing, video stream enable/defer/status, panel replay tunneling optimization, video CRC enable/continuous mode/results/valid, memory power control, and spare fields.
- `DP_LINK_ENC0/1_DP_LINK_ENC_CLOCK_CONTROL` provide HPO link encoder clock enable and `SYMCLK32` clock-on fields.
- `DP_DPHY_SYM320/321_DP_DPHY_SYM32_*` define DPHY enable/reset/precoder/mode/lane-count, status and update-pending bits, virtual-channel rate controls, scheduler allocation table stream-source/slot-count fields, test pattern selection/PRBS seed/custom-symbol registers, error status bits, per-stream symbol override, and DPHY CRC configuration/status/count.

Important HDA/Azalia controller definitions include:

- `CORB_*` and `RIRB_*` fields describe command output ring and response input ring write/read pointers, resets, DMA enables, memory/overrun/response interrupt controls and statuses, ring base addresses, response interrupt count, and supported ring sizes.
- `IMMEDIATE_COMMAND_OUTPUT_INTERFACE`, `IMMEDIATE_RESPONSE_INPUT_INTERFACE`, and `IMMEDIATE_COMMAND_STATUS` define immediate verb/response data paths, index fields, busy state, immediate response status, and unsolicited-response flags.
- `DMA_POSITION_LOWER/UPPER_BASE_ADDRESS` and `WALL_CLOCK_COUNTER_ALIAS` expose DMA position-buffer base and wall-clock counter fields.
- Endpoint, input-endpoint, and root immediate-command registers repeat data/index fields for scoped HDA access.
- `AZSTREAM0` through `AZSTREAM7_OUTPUT_STREAM_DESCRIPTOR_*` repeat a stream descriptor layout covering traffic priority, stripe control, descriptor error/FIFO completion/status/interrupt enables, stream reset/run bits, link position in current buffer, cyclic buffer length, last valid index, FIFO size, stream format, BDL pointer lower/upper base address, and link-position aliases.

Important legacy VGA definitions include:

- Sequencer registers `SEQ00` through `SEQ04` define synchronous/asynchronous reset, clocking mode, plane write mask, character-map select, and memory mode fields.
- CRT controller registers `CRT00` through `CRT22` include horizontal/vertical timing totals, display end, blanking and retrace starts/ends, cursor start/end/location, start address, offset, underline location, mode control, line compare, readback data, and memory mapping fields.
- Graphics controller registers `GRA00` through `GRA08` define set/reset, enable set/reset, color compare, rotate/function select, read map, mode, miscellaneous, color-dont-care, and bit mask fields.
- Attribute controller registers `ATTR00` through `ATTR14` define palette entries, mode control, overscan color, color plane enable, horizontal pixel panning, color select, and reserved fields.

Important codec endpoint definitions include:

- `AZALIA_F2_CODEC_CONVERTER_*` defines converter format, channel/stream ID, digital converter flags, stripe control, ramp rate, GTC embedding, audio widget capabilities, supported size/rate masks, and stream formats.
- `AZALIA_F2_CODEC_PIN_CONTROL_*` covers connection list entry, widget output enable, unsolicited response tag/enable, pin sense impedance/presence, default configuration fields, speaker/channel allocation, downmix and audio descriptor access, multichannel enable/mute/channel ID pairs, lipsync, high bit rate capability, audio sink info index/data, channel status override words, pin association, digital output status, LPIB snapshot/LPIB/timer snapshot, coding type, format-changed status, wireless display identification, remote keepalive, and pin capability parameters.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` provide per-descriptor sample-rate/bit-depth/channel fields and descriptor enable bits.
- `AZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0/1`, and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17` define sink metadata storage.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*` channel registers are full-width CRC result fields for channels 0-7 across input and output CRC result banks.
- `AZALIA_F2_CODEC_INPUT_*` begins the input converter and input pin controls for converter format, channel/stream ID, digital converter flags, input widget capabilities, supported sizes/rates, stream formats, input enable, unsolicited response, pin sense, configuration default fields, channel allocation, and multichannel 0/2 enable/mute/channel ID fields.

## Control Flow And State Behavior

This chunk has no executable control flow. The effective control flow is in callers that combine these constants with generated register offsets and AMDGPU register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, or lower-level MMIO/indexed-register accessors.

Typical runtime flows enabled by these definitions are:

1. DisplayPort stream setup programs SDP, audio packet, metadata, MSA/VBID, video stream, panel replay, and CRC fields on DP Sym32 encoder 3.
2. HPO link bring-up enables link encoder clocks and configures DPHY mode, lane count, scheduler allocation table state, virtual-channel rates, test pattern generation, symbol overrides, and CRC diagnostics for DPHY instances 0 and 1.
3. Link diagnostics poll DPHY status, rate/SAT update pending bits, error status, CRC done/value/count fields, and video CRC result/valid fields.
4. HDA controller initialization configures CORB/RIRB base addresses, pointers, ring sizes, DMA enables, interrupt controls, immediate command paths, DMA position buffer, and wall-clock reads.
5. Audio playback streams configure stream descriptor control/status, cyclic buffer length, last valid index, FIFO size, stream format, BDL base address, and current link position for stream descriptors 0-7.
6. Codec verb handling reads or writes converter format, stream ID, pin widget control, unsolicited response, pin sense, default configuration, channel/speaker allocation, audio descriptors, sink info, and remote keepalive state.
7. Input audio paths use the input codec converter and pin controls to configure input stream format, digital converter metadata, input enable, presence sense, and multichannel input routing.
8. Legacy VGA compatibility paths can use the indexed VGA definitions to preserve or decode sequencer, CRTC, graphics, and attribute register state during modeset, resume, or VGA handoff.

The state represented here is hardware register state:

- Programmed state includes DP SDP/audio/metadata/video enables, DPHY enable/reset/mode/lane count, VC rates, SAT slot assignments, test patterns, symbol override controls, HDA ring base addresses and DMA enables, stream descriptor formats and BDL pointers, codec converter and pin controls, audio descriptor data, sink metadata, and VGA indexed-register fields.
- Volatile readback includes SDP/GSP pending/deadline bits, video stream status, CRC valid/results, DPHY current mode/update-pending/error/CRC status, CORB/RIRB and immediate-command status, stream FIFO/status/link position, pin presence sense, digital output status, LPIB snapshots, format-changed status, keepalive state, and per-channel CRC values.
- Sequencing-sensitive fields include one-shot SDP triggers, double-buffer pending bits, stream enable/defer controls, DPHY reset and SAT update, CRC reset/start/end event selection, CORB/RIRB pointer resets, stream reset/run bits, interrupt status/clear-style fields, unsolicited-response enable, and LPIB snapshot controls.

## Dependencies And Integration Points

The definitions depend on exact consistency with the DCN 3.2.1 hardware register specification and matching generated offset headers. Compilation can catch missing macro names, but wrong numeric shifts or masks may still compile and only fail on hardware.

Key integration points are:

- AMDGPU Display Core DisplayPort and HPO link code that configures DP Sym32 encoders, link encoder clocks, DPHY mode/lane scheduling, SDP packets, video timing metadata, panel replay, and CRC diagnostics.
- Display audio code and the Linux HDA/DRM audio integration that configure Azalia controller rings, immediate commands, stream descriptors, codec widgets, channel allocation, sink info, and audio descriptors.
- Hotplug, modeset, suspend/resume, link retrain, and audio stream start/stop paths that need stable register programming across resets and power transitions.
- Firmware or diagnostic tooling that dumps DPHY errors/CRC values, video CRC, audio CRC banks, HDA ring state, stream positions, pin sense, sink metadata, and VGA compatibility state.
- Register dump and hardware validation scripts that expect generated `*_SHIFT` and `*_MASK` names to align with the DCN 3.2.1 offset namespace.

## Risks And Maintenance Notes

- Numeric drift is the main risk. A single incorrect shift or mask can route writes to the wrong hardware field, corrupting link setup, packet scheduling, HDA DMA, stream descriptor programming, codec verb responses, or legacy VGA restore.
- Repetition increases copy/paste risk. The DPHY 0/1 blocks, stream descriptor 0-7 blocks, audio descriptor 0-13 blocks, sink description 0-17 blocks, and CRC channel 0-7 blocks are intentionally patterned; one mismatched instance can affect only a specific link, stream, descriptor, or channel.
- Several fields are one-bit strobes or reset-like controls. SDP one-shot triggers, DPHY reset/CRC reset, SAT update, CORB/RIRB pointer resets, stream reset/run, interrupt status/control bits, and LPIB snapshot controls are sensitive to ordering and write semantics in callers.
- Reserved and full-width fields should be preserved unless the hardware specification says otherwise. This header documents bit packing; it does not make reserved bits safe to write.
- The HDA stream descriptor and ring fields describe DMA-facing state. Wrong base address, pointer, length, or enable masks can cause stream underruns, missing audio interrupts, stale position reporting, or DMA faults.
- Boundary completeness matters for this chunk. `GSP_CONTROL6` and `MULTICHANNEL4_ENABLE` are split across chunk boundaries and should be documented as complete only in the merged per-file report.

## Test Signals

Useful validation signals for changes touching these macros are mostly build-time and hardware-facing:

- Build coverage for AMDGPU Display Core and display audio code that includes `dcn_3_2_1_sh_mask.h` and references DP Sym32, HPO DPHY, HDA/Azalia, VGA, or codec endpoint fields.
- Static comparison against generated register collateral or the DCN 3.2.1 hardware specification for every `_SHIFT`/`_MASK` pair in the affected register families.
- DisplayPort bring-up, hotplug, retrain, suspend/resume, panel replay, MST or multi-stream scheduling, SDP/audio packet, and CRC diagnostic testing on DCN 3.2.1 hardware.
- Audio playback tests across HDA streams 0-7, including stream start/stop, format changes, channel allocation, HBR paths, LPIB position reporting, DMA position buffer reads, and unsolicited response handling.
- Codec and sink-info validation that checks pin sense, EDID-derived audio descriptors, speaker/channel allocation, sink description/manufacturer/product/port IDs, remote keepalive, and format-changed status.
- Register dump comparisons before and after modeset/audio start/resume to verify intended fields change, volatile status behaves as expected, and reserved bits remain stable.
