# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h lines 15421-16662

## Purpose

This chunk is a generated AMD DCN 4.1.0 register-offset slice. It contains preprocessor constants only: no C functions, structs, enums, storage, or executable control flow. The exported surface is `ix*` indirect-register index macros for display timing-generator debug windows and Azalia/HDA display-audio codec, stream, endpoint, CRC, descriptor, and sink-info windows.

The range starts with five continuation macros from the previous `mpcc_mcm3_mpcc_mcmdebugind` block (`ixMPCC_MCM3_ID8...ID12`), then covers OTG debug indirect registers for OTG0-OTG3, and then a large Azalia Function 0 audio register map. It ends at the file's closing `#endif`, so this is the tail chunk of `dcn_4_1_0_offset.h`. Although the repository root path includes `distributed-fs/ceph-client`, this header is AMDGPU Display Core hardware metadata and has no Ceph, filesystem, network, or persistent-storage behavior.

## Important APIs, Types, And Macros

The only API is generated macro constants:

- `ix*` names define indirect register indices inside a block-specific indexed register space.
- Address-block comments name the hardware index aperture, for example `otg0_otgdebugind`, `azendpoint_f2codecind`, `azf0stream0_streamind`, and `azf0endpoint7_endpointind`.
- Every visible address block in this chunk declares `base address: 0x0`; consumers combine these indices with the appropriate indirect access mechanism or register table rather than adding `reg*_BASE_IDX` segment bases as done for direct `reg*` MMIO offsets.

The chunk contains 1,061 `#define` lines. The visible block inventory is:

- `mpcc_mcm3_mpcc_mcmdebugind` continuation: five MCM debug entries for 3DLUT float conversion and gamut remap IDs.
- `otg0_otgdebugind`, `otg1_otgdebugind`, `otg2_otgdebugind`, `otg3_otgdebugind`: OTG debug data registers `OTG_DBG_DATA1..10`, scaler/output interface debug selectors, and, for OTG2, a small `DCIO_DEBUG*` group.
- `azendpoint_f2codecind`: Function 2 codec converter and pin-control verbs/parameters, including converter format, stream/channel ID, digital converter controls, pin sense, default configuration, speaker/channel allocation, HBR, lipsync, LPIB snapshot registers, coding/format-change status, wireless-display identification, and remote keepalive.
- `azendpoint_descriptorind` and `azendpoint_sinkinfoind`: audio descriptor slots, manufacturer/product IDs, sink description length, port IDs, and sink description words.
- `azf0controller_azinputcrc0resultind`, `azf0controller_azinputcrc1resultind`, `azf0controller_azcrc0resultind`, `azf0controller_azcrc1resultind`: eight-channel CRC result windows for input and output/controller audio CRC diagnostics.
- `azinputendpoint_f2codecind` and `azroot_f2codecind`: Function 2 input endpoint and root codec verb/parameter indices, including converter capabilities, stream formats, supported rates, pin capabilities, unsolicited response, input pin sense, HBR, and root node/function group metadata.
- `azf0stream0_streamind` through `azf0stream15_streamind`: sixteen repeated stream indirect blocks, each with stream descriptor control, status, link position-in-buffer, cyclic-buffer length, and stream FIFO size.
- `azf0endpoint0_endpointind` through `azf0endpoint7_endpointind`: eight repeated display-audio output endpoint blocks, each with converter controls, pin controls, speaker/channel allocation, ELD/sink-info access, ACP index/data, audio descriptors, infoframe/status registers, LPIB snapshot, coding/format-change, wireless-display, and endpoint fine-grain clock-gating reporting disable.
- `azf0inputendpoint0_inputendpointind` through `azf0inputendpoint7_inputendpointind`: eight repeated input endpoint blocks with input converter format/stream/digital controls, supported rates/formats, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel/HBR/channel allocation, hot-plug control, LPIB snapshot, input status, and infoframe indices.

There are no local C types. Runtime code normally reaches these constants through AMD Display Core register-list and indirect-access helpers, paired with the matching `dcn_4_1_0_sh_mask.h` field encodings where field-level access is needed.

## Control Flow And Usage Model

This header has no local control flow. It contributes compile-time constants to code that builds hardware register tables and then performs MMIO or indirect register operations at runtime.

A typical DCN 4.1.0 flow in this tree is:

1. DCN401 source files include `dcn/dcn_4_1_0_offset.h` and `dcn/dcn_4_1_0_sh_mask.h`.
2. Register-list macros in resource, DMUB, IRQ, clock, GPIO, audio, and block-specific code expand generated names into concrete offsets, masks, and shifts.
3. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `AZ_REG_READ`, `AZ_REG_WRITE`, or indexed debug/audio helpers use those generated constants to access the selected hardware register.

Direct local include anchors for this generation are `display/dmub/src/dmub_dcn401.c`, `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/irq/dcn401/irq_service_dcn401.c`, `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, `display/dc/gpio/dcn401/hw_factory_dcn401.c`, and `display/dc/gpio/dcn401/hw_translate_dcn401.c`. The audio-specific `ixAZALIA*`, `ixAZF0STREAM*`, `ixAZF0ENDPOINT*`, and `ixAZF0INPUTENDPOINT*` names align with common DCE/DC audio code that programs Azalia/HDA display-audio endpoints through endpoint register tables rather than hard-coded numeric indices.

## State And Persistence Behavior

The macros are immutable compile-time constants and persist nothing. The state they describe lives in hardware registers:

- OTG debug data/interface registers expose live timing-generator and display-output diagnostic state.
- Azalia codec converter, stream, pin-control, descriptor, sink-info, and endpoint registers hold display-audio configuration and status across a mode/audio configuration lifetime until the display engine, codec function, power-management path, or GPU reset reinitializes them.
- Stream LPIB, cyclic-buffer, FIFO, and CRC registers are runtime diagnostic/status surfaces tied to active audio streams.
- Endpoint and input-endpoint hotplug, unsolicited response, pin sense, infoframe, HBR, multichannel, and format-change registers are hardware-owned or software-programmed state used during connector audio setup, sink updates, and stream reconfiguration.

Persistence is hardware lifetime persistence, not filesystem persistence. Suspend/resume, runtime power gating, display IP reset, GPU reset, or audio re-enumeration can clear or rewrite the described register state.

## Dependencies And Integration Points

- The companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h`, which provides field shifts and masks for these register names when field-level access is required.
- DCN401 register-table code includes this header in DMUB service setup, resource construction, IRQ service construction, clock manager setup, and GPIO factory/translation paths. `dmub_dcn401.c` demonstrates the direct-offset pattern with `REG_OFFSET_EXP()`, while indexed audio/debug constants are consumed by block-specific indirect access paths.
- Common display-audio code under `display/dc/dce/` uses generated audio register tables and `struct dce_audio`-style register/shift/mask mappings to configure Azalia endpoints, ELD/sink data, audio info support, stream format/channel selection, and endpoint pin-control state.
- The repeated endpoint and stream namespaces are hardware instance contracts. Resource construction must keep audio endpoint counts, stream counts, and generated table entries aligned with the ASIC's exposed blocks.
- Similar constants appear across older `dce_*_offset.h` and `dcn_*_offset.h` generations, which is useful for drift comparison but also means a wrong-generation include can compile if names overlap while still targeting the wrong hardware layout.

## Risks And Edge Cases

- Offset/header pairing is critical. `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` must come from the same hardware generation; stale offsets with valid masks can silently misprogram audio or debug registers.
- Repetition hides instance-specific mistakes. Sixteen stream blocks, eight output endpoints, and eight input endpoints share near-identical layouts. A copied numeric value or table entry that targets the wrong endpoint may only fail on one connector/audio instance.
- Indirect indices are not direct MMIO addresses. Treating `ix*` values as direct `reg*` offsets would access the wrong register path.
- The chunk starts mid-block and ends the file. Whole-file reconciliation must merge the preceding chunk for complete `MPCC_MCM3` debug context, and accidental edits near the closing `#endif` can break all consumers of this generated header.
- Audio register effects are hardware- and sink-dependent. Wrong `CHANNEL_STREAM_ID`, converter format, HBR, multichannel enable, speaker/channel allocation, ELD/sink-info, or pin-sense indices can produce failures only with particular HDMI/DP sinks, sample rates, channel layouts, or hotplug sequences.
- Status and control names are adjacent. `LPIB`, CRC result, input status, pin sense, format-changed, hot-plug, unsolicited-response, and keepalive registers should not be treated as ordinary persistent configuration words.
- Clock-gating reporting disable fields are power/diagnostic sensitive. Incorrect endpoint `FGCG_REP_DIS` indices can mask clock-gating telemetry or interfere with power-debug signals.

## Test Signals

- Build AMDGPU DC with DCN401 enabled so all include sites compile against `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h`; missing or renamed generated symbols should fail at compile time in register-list expansion.
- Static consistency checks should compare repeated `azf0stream0..15`, `azf0endpoint0..7`, and `azf0inputendpoint0..7` index layouts and flag unintended divergence.
- HDMI/DP audio testing should cover hotplug, mode set, suspend/resume, runtime power management, sample-rate/format changes, HBR, multichannel layouts, ELD/sink-info updates, and endpoint counts high enough to exercise endpoints beyond instance 0.
- Diagnostic testing should read OTG debug windows and Azalia CRC/LPIB/status registers during active display and audio playback to verify that indirect indices reach the expected hardware windows.
- Register-dump comparison against the DCN 4.1.0 ASIC register specification is the most direct validation for this generated tail chunk, especially around the repeated endpoint blocks and the file-ending `#endif`.
