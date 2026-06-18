# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_offset.h lines 12824-14596

## Purpose

This chunk is the final slice of the generated AMD DCN 3.2.1 register-offset header. It contains C preprocessor constants that map display, audio, VGA, and Azalia indexed register names to numeric offsets or indirect indexes used by the AMDGPU display driver. The range is not executable code; it is a hardware ABI description consumed together with `dcn_3_2_1_sh_mask.h` by DCN 3.2.1 resource, stream encoder, link encoder, and audio register-table code.

The chunk contains 1,522 `#define` entries: 453 `reg*` macros for direct MMIO-style register offsets and their `_BASE_IDX` selectors, plus 1,069 `ix*` macros for indexed VGA/Azalia/codec register spaces. It starts in the tail of HPO DP stream encoder 3 VPG definitions, covers HPO DP `SYM32` stream encoder 3, HPO DP link/DPHY symbol blocks 0 and 1, and then switches to HDA/Azalia controller, output streams, VGA indexed registers, Azalia codec verb indexes, audio descriptors, CRC result indexes, stream latency counters, endpoint indexes, and input endpoint indexes. The file ends at line 14596 with the `#endif`, so this work item closes the header.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver register metadata. It has no distributed-filesystem logic.

## Important APIs, Types, And Register Groups

There are no functions, structs, enums, variables, includes, locks, allocations, or callbacks in this chunk. Its public interface is the macro namespace:

- `reg<block>_<register>`: a direct register offset value.
- `reg<block>_<register>_BASE_IDX`: a register-base selector, mostly `2` for DCN display register apertures in this slice, `0` for HDA controller/stream registers, and `1` for selected alias offsets.
- `ix<register>`: an indexed-register address used through an index/data register pair or legacy indexed IO-style interface.

Major register blocks in the exact line range:

- `dce_dc_hpo_dp_sym32_enc3_dispdec` at base `0x1b664`: HPO DP symbol stream encoder 3 registers. It defines video FIFO control, MSA double-buffering, pixel format, `VID_MSA0` through `VID_MSA8`, horizontal blank control, secondary data packet controls, audio SDP controls, metadata packet control, VBID/stream/panel replay controls, CRC control/result/status, memory power, and spare registers.
- `dce_dc_hpo_dp_link_enc0_dispdec` and `dce_dc_hpo_dp_link_enc1_dispdec`: HPO DP link encoder clock-control and spare registers for link encoder instances 0 and 1.
- `dce_dc_hpo_dp_dphy_sym320_dispdec` and `dce_dc_hpo_dp_dphy_sym321_dispdec`: HPO DP DPHY/SYM32 transport registers for two instances. Each defines control/status, SAT update, virtual-channel rate controls, SAT VC slots/status, test-pattern configuration, PRBS seeds, square pulse, custom test-pattern payloads, error status, symbol override, and CRC config/status/count.
- `dce_dc_hda_azcontroller_azdec`: core HDA/Azalia controller register offsets for CORB/RIRB pointers, controls, statuses, sizes, immediate command/response interfaces, DMA position base addresses, and a wall-clock alias.
- `dce_dc_hda_azendpoint_azdec`, `dce_dc_hda_azinputendpoint_azdec`, and `dce_dc_hda_azroot_azdec`: immediate command data/index register aliases for endpoint, input endpoint, and root nodes.
- `dce_dc_hda_azstream0_azdec` through `dce_dc_hda_azstream7_azdec`: output stream descriptor offsets. Each stream repeats control/status, link position in current buffer, cyclic buffer length, last valid index, FIFO size/format, BDL pointer lower/upper base, and an alias for link position.
- `vga_vgaseqind`, `vga_vgacrtind`, `vga_vgagrphind`, and `vga_vgaattrind`: legacy VGA sequencer, CRT controller, graphics controller, and attribute-controller indexed register numbers.
- `azendpoint_f2codecind`: Azalia F2 output codec converter and pin-control verb indexes, including converter format, stream/channel ID, digital converter controls, size/rate/stream-format parameters, pin sense/configuration defaults, speaker/channel allocation, audio descriptors, multichannel enables, lipsync/HBR, sink information, channel-status overrides, LPIB snapshots, format-change/wireless-display/keepalive status, and pin capabilities.
- `azendpoint_descriptorind` and `azendpoint_sinkinfoind`: audio descriptor entries and sink description/port-ID indexed registers.
- `azf0controller_azinputcrc0resultind`, `azinputcrc1resultind`, `azcrc0resultind`, and `azcrc1resultind`: per-channel CRC result indexes for input and output audio paths.
- `azinputendpoint_f2codecind` and `azroot_f2codecind`: F2 input converter/pin controls and root/function parameter/control verb indexes.
- `azf0stream0_streamind` through `azf0stream15_streamind`: per-stream FIFO size and latency counter control/result indexes.
- `azf0endpoint0_endpointind` through `azf0endpoint7_endpointind`: repeated F0 output endpoint indexed registers for converter capabilities/control, pin capabilities/control, audio descriptors, multichannel modes, sink info, hotplug/unsolicited response forcing, channel-status overrides, LPIB snapshots, format-change/wireless-display/remote-keepalive state, and audio enable/disable/format-change interrupt status.
- `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`: repeated F0 input endpoint indexed registers for input converter capabilities/control, pin capabilities/control, multichannel/HBR/channel allocation, hotplug/unsolicited response, LPIB snapshots, input status, and infoframe data.

## Control Flow

This header has no runtime control flow. The effective control flow is created by AMDGPU display code that includes this header and uses its constants in register helper macros:

1. DCN 3.2.1 resource code includes `dcn/dcn_3_2_1_offset.h` and `dcn/dcn_3_2_1_sh_mask.h`.
2. Resource macros such as `SR`, `SRI`, `SRI_ARR`, and `SF` expand these offsets and field masks into register tables for a specific ASIC generation.
3. HPO DP stream/link encoder code uses the `DP_SYM32_ENC*` and `DP_DPHY_SYM32*` register table entries through `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` style helpers to program stream MSA, secondary data packets, DPHY mode, test patterns, SAT/VC allocation, CRC, and link state.
4. Audio code uses Azalia controller/endpoint index/data register definitions to expose HDMI/DP audio capabilities, configure converter stream formats, maintain channel and speaker allocation data, service hotplug/unsolicited response status, and report buffer/latency counters.

The chunk itself does not enforce sequencing. Ordering requirements such as DP stream blanking, MSA double buffering, SAT update polling, DPHY reset/enable transitions, HDA CORB/RIRB setup, immediate command handshakes, BDL programming, and indexed endpoint reads/writes live in the consuming driver code and hardware specifications.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It defines addresses for hardware state:

- HPO DP stream state: video timing metadata, pixel format, stream enable, VBID, panel replay, secondary data packets, audio packets, metadata packets, CRC result/status, and memory-power controls.
- HPO DP link/DPHY state: clock control, DPHY enable/reset/mode/lane configuration, SAT/VC allocation, VC rate programming, link test-pattern payloads, PRBS seeds, error status, symbol override, and CRC counters.
- HDA/Azalia controller state: CORB/RIRB ring pointers and controls, immediate command/response state, DMA position buffer addresses, wall-clock state, output stream descriptors, BDL pointers, FIFO/format state, and stream position aliases.
- Indexed VGA state: legacy sequencer/CRT/graphics/attribute registers exposed as indexes rather than normal `reg*` offsets.
- Azalia codec state: root/function parameters, converter format and stream IDs, pin sense/default configuration, audio descriptors, channel/speaker allocation, multichannel and HBR flags, sink info, channel status overrides, LPIB snapshots, format-change status, keepalive state, CRC result channels, FIFO size, latency counters, and endpoint interrupt/status indexes.

Persistence is hardware-defined. Some programmed values survive until another register write, stream reset, link reconfiguration, audio engine reset, suspend/resume, power-gating transition, or ASIC reset. Status and interrupt-style values may be read-only, sticky, self-clearing, or write-to-clear depending on the target register. The header only supplies numeric offsets/indexes and base selectors, so side effects must be understood by the register access path that uses them.

## Dependencies And Integration Points

Key dependencies and consumers visible in this source tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c` includes both `dcn_3_2_1_offset.h` and `dcn_3_2_1_sh_mask.h`. Its register-table macros include Azalia endpoint index/data fields and audio DTO/controller clock-gating fields, making this header part of the DCN 3.2.1 resource object layout.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` and related HPO stream encoder code use the same `DP_SYM32_ENC` naming pattern defined here to instantiate per-instance stream encoder register lists.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn32/dcn32_hpo_dp_link_encoder.h` declares `DP_DPHY_SYM320` field lists that pair with the `DP_DPHY_SYM320` offsets in this chunk. The corresponding implementation programs DPHY control, test-pattern, SAT, and VC-rate fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_audio.h` models Azalia endpoint index/data access, while generation resource files map `AZF0ENDPOINT0_AZALIA_F0_CODEC_ENDPOINT_INDEX` and `_DATA` fields through `SF(...)`.
- The generated shift/mask companion `dcn_3_2_1_sh_mask.h` must agree with every `reg*` entry that is accessed through field helpers. Offset-only `ix*` entries depend on the correct index/data access convention rather than normal MMIO field extraction.
- Similar VGA/Azalia endpoint index definitions appear across older `dce_*_offset.h` and `dcn_*_offset.h` headers, indicating this chunk preserves a cross-generation hardware interface that audio and display code expect to remain structurally stable.

## Risks And Edge Cases

- Generated offset drift is the main risk. A wrong numeric offset can compile cleanly while directing a register helper at the wrong MMIO word or indexed codec verb.
- `_BASE_IDX` mistakes are high impact because the same offset value can refer to a different aperture or alias depending on the selected base. This chunk mixes base index `2` display registers, base index `0` HDA registers, and base index `1` aliases.
- The chunk crosses unrelated hardware domains. HPO DP, HDA/Azalia, VGA, codec endpoint, CRC, and latency-counter definitions sit next to each other; bulk regeneration or manual edits can accidentally move, rename, or duplicate macros across domains.
- Indexed-register definitions are easy to misuse. `ix*` values are not normal MMIO offsets; consumers must write the correct index register and then read/write the paired data register, often with endpoint/node context already selected.
- Repeated endpoint and stream blocks invite copy/paste or generator-template errors. Output endpoints 0-7, input endpoints 0-7, streams 0-15, and CRC channel 0-7 definitions should remain identical except for instance prefixes and expected base/index offsets.
- Audio stream descriptor aliases share names and addresses with primary descriptor state. Incorrect alias handling could break position reporting, latency accounting, or interrupt/debug reads.
- DP DPHY SAT/VC and test-pattern registers affect link bring-up and compliance testing. Wrong offsets can manifest as training failures, bad MST payload allocation, failed PRBS/custom pattern tests, or incorrect CRC/error reporting.
- Legacy VGA indexes are retained for compatibility. Accidentally treating them as DCN MMIO registers would target invalid or unrelated hardware state.

## Test Signals

Useful validation signals are mostly build, generated-header consistency, and hardware integration signals:

- Build coverage: DCN 3.2.1 display code compiles with no missing `reg*`, `ix*`, `_BASE_IDX`, or shift/mask companion macros.
- Register-table sanity: `dcn321_resource.c` can instantiate its audio, stream encoder, link encoder, and hub/resource register tables using the generated offsets from this file.
- HPO DP behavior: displays using DP 2.x/HPO paths train reliably, program MSA and secondary data packets correctly, update SAT/VC allocation without timeout, and pass test-pattern/CRC diagnostics.
- Audio behavior: HDMI/DP audio endpoints enumerate expected capabilities, program stream formats and channel allocation, maintain correct LPIB/position reporting, and handle hotplug/format-change/enable-disable status.
- Indexed access behavior: Azalia endpoint/root/input endpoint reads return expected codec parameters through index/data registers rather than invalid MMIO reads.
- Suspend/resume and power transitions: audio streams, DP link encoders, DPHY state, aliases, and memory-power controls recover after suspend, display blank/unblank, GPU reset, and hotplug.
- Cross-generation regression checks: repeated stream, endpoint, input endpoint, VGA, and codec indexes remain consistent with adjacent DCN/DCE generated headers unless hardware-specific deltas are intentional.
- Static generation checks: every direct `reg*` macro that should have a `_BASE_IDX` companion has one, repeated instance blocks preserve expected address spacing, and the header terminates cleanly with the final `#endif`.
