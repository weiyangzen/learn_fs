# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 47071-49649

## Purpose

This chunk is part of the generated AMD DCN 3.2.0 register shift/mask header. It contains no executable logic; it exposes preprocessor constants that describe bit positions (`__SHIFT`) and masks (`_MASK`) for DCN 3.2 DisplayPort, HDA/Azalia audio, legacy VGA, and related indexed register blocks. Consumers combine these constants with the matching DCN 3.2.0 offset header and AMD display register helpers to compose, update, or decode MMIO fields.

The range starts in the middle of `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7`, covers the tail of the third 32-symbol DisplayPort encoder block, both HPO DP link encoder/DPHY instances 0 and 1, RDPCS DPALT controls for pipes 0 through 4, the HDA/Azalia controller and output stream descriptor blocks, legacy VGA indexed blocks, Azalia F2 codec output endpoint metadata, audio descriptor and sink info blocks, Azalia CRC result blocks, and the beginning of the Azalia F2 codec input endpoint block. It defines 2,073 macros in this slice: 1,033 shift constants and 1,040 mask constants.

Although this source tree is rooted under `ceph-client`, this file is AMDGPU display hardware metadata, not distributed-filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, locks, allocation paths, includes, or direct register accesses in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit of a register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for isolating or setting that field.
- `// addressBlock:` comments: generated grouping metadata for hardware address blocks such as `dcn_dc_hpo_dp_dphy_sym320_dispdec`, `dcn_dc_hda_azcontroller_azdec`, and `azendpoint_f2codecind`.

Major register groups covered here are:

- `DP_SYM32_ENC3_*`: SDP generic packet controls 7 through 14, SDP stream/audio/metadata controls, video MSA/VBID/stream/panel-replay controls, video CRC controls/results/status, memory power controls, and spare bits for the third HPO DP symbol encoder.
- `DP_LINK_ENC0_*` and `DP_LINK_ENC1_*`: HPO DisplayPort link encoder clock enable and `SYMCLK32` clock-on status fields.
- `DP_DPHY_SYM320_*` and `DP_DPHY_SYM321_*`: two repeated 32-symbol DisplayPort PHY instances with enable/reset/mode/lane controls, status, stream virtual-channel rate programming, slot allocation table updates/status, training-pattern generation, PRBS seeds, custom symbols, error status, symbol override, and PHY CRC configuration/status/count fields.
- `RDPCSPIPE0_*` through `RDPCSPIPE4_*`: DPALT lane-mode and disable/ack fields in `RDPCSPIPE_PHY_CNTL6`.
- HDA/Azalia controller registers: CORB/RIRB pointers, DMA enable/status/size bits, immediate command and response interfaces, DMA position buffer base, and wall-clock counter alias.
- HDA/Azalia endpoint/root immediate-command index/data registers.
- `AZSTREAM0_*` through `AZSTREAM7_*`: output stream descriptor control/status, link position in current buffer, cyclic buffer length, last valid index, FIFO size, stream format, BDL base address, and link-position alias fields.
- VGA indexed blocks: sequencer (`SEQ00`-`SEQ04`), CRTC (`CRT00`-`CRT1F`, `CRT22`), graphics controller (`GRA00`-`GRA08`), and attribute controller (`ATTR00`-`ATTR14`) field geometry.
- `AZALIA_F2_CODEC_*`: output converter and pin-control fields for audio format, stream/channel IDs, digital converter status, stripe/ramp/GTC embedding, widget capabilities, speaker/channel allocation, downmix, audio descriptors, multichannel enables, HBR, sink-info index/data, codec status overrides, LPIB snapshot, coding-type/format-change, wireless display identification, remote keepalive, and pin capabilities.
- `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13` and `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`: indexed EDID/audio sink metadata payload fields.
- `AZALIA_INPUT_CRC*` and `AZALIA_CRC*`: full-width per-channel CRC result registers.
- `AZALIA_F2_CODEC_INPUT_*`: the start of the input endpoint converter and pin-control metadata, including format, channel/stream ID, digital converter fields, capabilities, supported rates/formats, input enable, unsolicited response, pin sense, and configuration-default fields.

## Control Flow

This header chunk has no runtime control flow. Runtime sequencing is supplied by AMDGPU display and audio code that includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`, then uses register-helper macros and token-pasted field names to read, write, or poll hardware fields.

Expected runtime use follows the same generated-register pattern throughout the AMD display stack:

1. A DCN 3.2 subsystem selects a symbolic register, for example an HPO DP DPHY control register, an Azalia stream descriptor, or a VGA indexed register.
2. The matching offset macro identifies the MMIO register or indexed-register aperture.
3. The shift/mask macros in this header isolate, encode, or update the requested field.
4. Higher-level code handles the hardware ordering: clock enablement, reset sequencing, DisplayPort link training, MST virtual-channel slot allocation, SDP/audio/infoframe programming, stream descriptor setup, command ring DMA, interrupt handling, and suspend/resume state restoration.

The generated constants do not encode access width, read/write permissions, polling requirements, sticky status semantics, self-clearing bits, or ordering barriers. Those behaviors must come from the hardware programming model and the driver code using the constants.

## State And Persistence Behavior

This chunk stores no software state and persists nothing to disk, memory, firmware, or driver-owned data structures. It describes MMIO-backed GPU state in DCN 3.2 hardware.

The represented hardware state includes:

- DisplayPort symbol encoder state for SDP generic packets, audio packet enablement/mute status, metadata packet double-buffering, video stream enable/defer/status, panel replay tunneling optimization, CRC capture, and encoder memory power state.
- HPO DP link/DPHY state for clock enablement, PHY enable/reset, current mode, lane count, rate-update and slot-allocation-update pending flags, stream rate numerators/denominators, slot allocation table programming, training/test pattern generation, error reporting, symbol override, and PHY CRC capture.
- RDPCS PHY state for DP alternate mode lane configuration and disable acknowledgement.
- HDA/Azalia controller state for CORB/RIRB DMA rings, response interrupts and overruns, immediate command issue/response, DMA position buffer base, and wall-clock timing.
- HDA output stream state for reset/run bits, interrupt enables/status, stream number, FIFO readiness/errors, cyclic buffer length, BDL address, format, and link position reporting.
- Legacy VGA indexed register state for sequencer, CRT controller, graphics controller, and attribute controller compatibility paths.
- Azalia codec endpoint state for output and input converter formats, digital converter metadata, pin sense/configuration, speaker and channel allocation, multichannel/HBR controls, sink descriptors, LPIB snapshots, remote keepalive, and CRC diagnostics.

Persistence is hardware-defined. Programmed configuration generally lasts until driver reprogramming, modeset, stream teardown, power gating, suspend/resume, GPU reset, or ASIC reset. Status, CRC, ring pointers, link-position, immediate-command, interrupt, and unsolicited-response bits may be volatile, latched, sticky, write-one-to-clear, or self-clearing depending on the register definition outside this generated mask file.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the DCN 3.2.0 generated register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` supplies matching register offsets and indexed-register addresses.
- DCN 3.2 display code consumes these names through generated register tables and helper macros.
- HDA/Azalia and DisplayPort hardware definitions outside this header define legal values, access direction, and programming order.

Observed include sites for `dcn_3_2_0_sh_mask.h` in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c`

Runtime integration is mainly with the DCN 3.2 resource, IRQ, DMUB, clock, GPIO, DisplayPort link/PHY, and shared display-audio paths. The Azalia fields are consumed by audio endpoint code that programs HDA stream descriptors, codec verbs, speaker/channel allocation, sink information, high-bit-rate audio, and link-position reporting. The HPO DP fields feed DisplayPort link enablement, 128b/132b or 32-symbol PHY operation, MST virtual-channel scheduling, CRC/test pattern diagnostics, and panel replay/metadata packet behavior.

## Risks And Edge Cases

- Field drift is the primary risk. These macros are untyped constants, so a wrong mask or shift compiles but can silently program the wrong hardware bit.
- The chunk starts mid-register at `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7` and ends mid-register group at `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT_4`. Adjacent chunks are required for complete per-register analysis at both boundaries.
- The HPO DP DPHY blocks are repeated for instances 0 and 1. A generation or copy error may affect only one physical link, making failures connector-specific.
- Slot allocation, rate counter, and stream-source fields are sensitive in MST and high-bandwidth DP modes. Incorrect masks can produce link training failures, underflow, blanking, payload allocation errors, or stream corruption.
- Training pattern, PRBS, custom symbol, symbol override, and CRC fields are diagnostic/test paths. Incorrect use can leave a link in a non-normal pattern mode or make hardware validation results misleading.
- SDP, audio packet, metadata, VBID, MSA, panel replay, and stream enable fields are timing-sensitive. Misprogramming can cause missing infoframes, muted audio, metadata not taking effect, panel replay issues, CRC mismatches, or stream disable races.
- HDA CORB/RIRB and output stream descriptor fields control DMA-visible ring buffers and BDL addresses. Bad masks or ordering can cause lost codec responses, response overruns, FIFO/descriptor errors, wrong audio position reporting, or DMA to incorrect addresses.
- Legacy VGA indexed fields are compatibility-sensitive and may be used during early display, console, or fallback paths; accidental drift can create obscure boot/display regressions.
- Azalia sink, speaker allocation, multichannel, HBR, LPIB, and CRC fields are user-visible through HDMI/DP audio behavior. Bugs may appear only with specific sample rates, channel layouts, compressed/HBR formats, displays, or suspend/resume cycles.

## Test Signals

Useful validation should combine generated-header checks with hardware-level display/audio coverage:

- Build AMDGPU with DCN 3.2 enabled. Include or token-paste mismatches should surface in the DCN32 resource, DMUB, IRQ, clock, GPIO, or GMC users of `dcn_3_2_0_sh_mask.h`.
- Mechanically verify each generated register field in this range has the expected `__SHIFT` and `_MASK` pair, except where the generated schema intentionally provides only one side or full-register fields.
- Diff repeated blocks for `DP_DPHY_SYM320` vs. `DP_DPHY_SYM321`, `DP_LINK_ENC0` vs. `DP_LINK_ENC1`, `RDPCSPIPE0` through `RDPCSPIPE4`, and `AZSTREAM0` through `AZSTREAM7` to catch instance-local drift.
- Exercise DisplayPort HPO links across link training, MST payload allocation, stream enable/disable, audio packet transmission, metadata/infoframe updates, panel replay, CRC capture, test pattern/PRBS diagnostics, hotplug, suspend, and resume.
- Exercise HDMI/DP audio over HDA/Azalia with stereo, multichannel PCM, high-bit-rate/compressed formats, multiple sample rates and bit depths, stream start/stop, sink changes, plug/unplug, and resume.
- Watch for no display or blanking on a single connector, MST payload allocation errors, bad CRC/status diagnostics, stuck update-pending bits, audio silence or channel mapping errors, codec command timeouts, RIRB overruns, FIFO/descriptor errors, bad LPIB positions, and regressions limited to legacy VGA or boot display paths.

## Cross-Chunk Notes

This is a chunk-level document for `subset-b-001948` only. The final per-file report for `dcn_3_2_0_sh_mask.h` should merge this with adjacent chunks before making complete claims about `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL7` or `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_RESPONSE_CONFIGURATION_DEFAULT_4`.
