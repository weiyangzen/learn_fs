# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 51931-54346

## Scope

This chunk is a generated AMDGPU DCN 3.1.6 register shift/mask header slice. It contains only C preprocessor constants: no functions, structs, enums, storage definitions, or executable control flow. The macros describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for HPO DisplayPort stream encoders, audio packet generators, metadata/video packet generators, Symbol32 encoders, DPHY Symbol32 blocks, link encoder spares, and the beginning of DCHVM host-VM controls.

The slice starts in the tail of `DP_SYM32_ENC1` SDP generic stream packet controls and then defines complete repeated register groups for stream encoders 2 and 3. It ends at `DCHVM_CLK_CTRL`, where only the first clock-gating and request-clock fields are present in this chunk.

## Purpose

The header gives the display driver symbolic bitfield names for MMIO register programming. Driver code can compose or decode register values without hard-coded literals by combining these masks and shifts with AMD register access helpers. The chunk covers several hardware responsibilities:

- `DP_STREAM_ENC2` and `DP_STREAM_ENC3`: clock enables, stream/audio input mux selection, and clock-ramp-adjuster FIFO status/control.
- `APG2` and `APG3`: DisplayPort audio packet generator reset, enable, debug audio generation, packet source selection, audio CRC, active/overflow status, memory power, and spare fields.
- `DME8` and `DME9`: metadata engine source selection, enable, stream type, double-buffer pending/taken state, clear bits, missed-transmission state, and memory power.
- `VPG8` and `VPG9`: generic packet byte access, generic packet frame/immediate update requests for slots 0-14 and their pending bits, generic conflict status/clear, memory power, ISRC packet data, and MPEG info packet fields.
- `DP_SYM32_ENC1/2/3`: Symbol32 video stream encoding, MSA payload registers, pixel format, HBLANK symbol width, 15 generic secondary data packet controls, audio SDP controls, metadata packet scheduling, VBID/MSA timing, stream enable/status, panel replay tunneling, video CRC, memory power, and spare registers.
- `DP_LINK_ENC0` and `DP_LINK_ENC1`: clock-control/spare field definitions for link encoder instances, though the visible clock-control fields in this chunk are minimal.
- `DP_DPHY_SYM320` and `DP_DPHY_SYM321`: physical Symbol32 link control/status, stream allocation table update, virtual-channel rate controls, SAT VC and SAT VC status fields, test-pattern configuration and seeds, error status, symbol override, and CRC configuration/status/count.
- `DCHVM`: initial host virtual memory request and display/HVM clock gating fields at the chunk boundary.

## Important Macro Groups

The naming pattern is consistent:

- Register field shift: `<REGISTER>__<FIELD>__SHIFT`
- Register field mask: `<REGISTER>__<FIELD>_MASK`

There are no helper APIs in this file, but these macro names become the API surface consumed by driver register programming macros elsewhere in the AMD DC stack.

### Symbol32 stream encoders

`DP_SYM32_ENC1` tail fields cover `SDP_GSP_CONTROL12` through `SDP_GSP_CONTROL14`, followed by common stream fields. `DP_SYM32_ENC2` and `DP_SYM32_ENC3` are fully represented in this chunk.

Key controls include:

- core enable/reset/status: `DP_SYM32_ENC{2,3}_DP_SYM32_ENC_CONTROL__DP_SYM32_ENC_ENABLE`, `...RESET`, `...RESET_DONE`;
- pixel-to-symbol FIFO setup: `VID_FIFO_CONTROL__PIXEL_TO_SYMBOL_FIFO_ENABLE`, `...RESET_DONE`, `...OVERFLOW_STATUS`;
- double-buffering: `VID_MSA_DOUBLE_BUFFER_CONTROL`, `VID_PIXEL_FORMAT_DOUBLE_BUFFER_CONTROL`, generic SDP `GSP_DOUBLE_BUFFER_ENABLE`, `GSP_DOUBLE_BUFFER_PENDING`, metadata packet double-buffer fields;
- pixel format: `VID_PIXEL_FORMAT__PIXEL_ENCODING_TYPE`, `UNCOMPRESSED_PIXEL_ENCODING`, and `UNCOMPRESSED_COMPONENT_DEPTH`;
- MSA payload words: `VID_MSA0` through `VID_MSA8`, each exposing a full 32-bit `MSA_DATA` field;
- secondary data packet enable/scheduling: `SDP_CONTROL`, `SDP_GSP_CONTROL0` through `SDP_GSP_CONTROL14`, `SDP_AUDIO_CONTROL0/1`, and `SDP_METADATA_PACKET_CONTROL`;
- stream timing/status: `VID_MSA_CONTROL`, `VID_VBID_CONTROL`, `VID_STREAM_CONTROL`, `VID_PANEL_REPLAY_CONTROL`;
- diagnostics: `VID_CRC_CONTROL`, `VID_CRC_RESULT0/1`, `VID_CRC_STATUS`;
- memory/spare: `MEM_POWER_CONTROL` and `SPARE`.

Each GSP control register repeats the same field layout: continuous transmission during video/idle, one-shot trigger and trigger position, double buffering, payload size, SOF reference, deadline missed, trigger pending, double-buffer pending, and a high 16-bit transmission line number.

### HPO DP stream encoder wrappers

`DP_STREAM_ENC2` and `DP_STREAM_ENC3` define clocks and muxes around the Symbol32 encoder path. Their clock-control fields identify whether the stream encoder clock is enabled and sourced/observed on `DISPCLK`, `SOCCLK`, `DPSTREAMCLK`, and `SYMCLK32`. The input mux fields select the pixel stream source and audio stream source. FIFO status/control registers expose enable/reset, read-start level, read clock source, reset-done, video-stream-active, FIFO error, forced recalculation, overwrite/min/max/calculated FIFO levels, and calibration status.

### Audio packet generators

`APG2` and `APG3` are repeated APG register blocks. They expose reset/reset-done, enable, DP audio stream ID, channel-count override, debug generator enable/reset, debug channel enables, packet source selection, audio CRC enable/continuous/channel/count, CRC result/done/clear, audio/HBR status, audio FIFO overflow status/clear, output-active status, memory power controls, and spare fields.

### Metadata and video packet generators

`DME8` and `DME9` hold metadata engine state: HUBP requestor ID, engine enable, stream type, double-buffer pending/taken state, clear/disable bits, transmission-missed status/clear, and DME memory power fields.

`VPG8` and `VPG9` define byte-indexed generic packet data access, 15 generic packet frame update request bits plus 15 pending bits, 15 generic packet immediate update request bits plus 15 pending bits, lock/conflict status and conflict clear, GSP memory light-sleep controls, ISRC data access, and MPEG info packet checksum/byte/format/update fields.

### DPHY Symbol32 blocks

`DP_DPHY_SYM320` and `DP_DPHY_SYM321` are repeated physical/link Symbol32 register blocks. They include:

- control/status: `SYM32_ENABLE`, `SYM32_RESET`, `SYM32_RESET_DONE`, `SYM32_READY`, `PHY_SYMCLK_FE_ON`, `PHY_SYMCLK_FE_OFF`;
- stream allocation/rate: `SAT_UPDATE`, four `VC_RATE_CNTL` registers, four `SAT_VC` configs, and four `SAT_VC_STATUS` views;
- test patterns: lane/select and PRBS selection in `TP_CONFIG`, per-lane PRBS seeds, square pulse width, and `TP_CUSTOM0` through `TP_CUSTOM10`;
- error reporting: total slot count, rate, duplicate VC stream source, missing ACT, unexpected mode transition, illegal stream symbol, rate counter saturation, counter overflow, and cipher errors;
- stream symbol override: four stream override enable/type/symbol slots packed across the register;
- CRC diagnostics: `CRC_CONFIG0`, `CRC_CONFIG1`, `CRC_STATUS`, and `CRC_COUNT`.

## Control Flow

There is no local control flow. The effective hardware programming sequence is external and inferred from the fields:

1. Enable clocks and choose stream/audio sources through `DP_STREAM_ENC*_CLOCK_CONTROL`, `INPUT_MUX_CONTROL`, and `AUDIO_CONTROL`.
2. Reset and enable APG/DME/VPG/Symbol32/DPHY blocks using their reset, reset-done, and enable fields.
3. Program stream metadata: MSA words, pixel format, VBID/MSA scheduling, generic SDP payload control, metadata packet timing, APG audio packets, and VPG generic/ISRC/MPEG packet bytes.
4. Use double-buffer enable/pending or frame/immediate update request/pending bits to commit packet and format updates at a frame boundary or immediately.
5. Monitor status, overflow, missed-transmission, CRC, FIFO, DPHY readiness, and DPHY error bits.
6. Apply memory power settings once blocks are idle or during low-power transitions.

Any actual ordering, polling, locking, and delay behavior must come from AMD DC source files that consume these macros, not from this header.

## State And Persistence

The macros themselves have no runtime state. They describe persistent hardware state stored in display engine registers. Notable state categories exposed by this chunk are:

- latched/clearable status: APG FIFO overflow, APG CRC done, DME metadata double-buffer taken, DME transmission missed, VPG generic conflict, DPHY error status, CRC done, FIFO errors;
- pending state: generic SDP trigger pending, generic SDP double-buffer pending, metadata packet double-buffer pending, VPG frame/immediate update pending, MSA/pixel-format double-buffer pending;
- enable/configuration state: stream encoder clocks, audio/video/metadata packet enables, stream enable, DPHY/Symbol32 enable, virtual-channel allocation, test patterns, memory power mode;
- diagnostic counters/results: video CRC result words, APG audio CRC, DPHY CRC value/count, FIFO calculated levels.

Because these are MMIO bit definitions, writes can have side effects such as clears, resets, hardware commits, and power-state changes. The `_CLR`, `_RESET`, `_UPDATE`, and one-shot trigger fields should be treated as side-effectful by consumers.

## Dependencies And Integration Points

This header depends only on the C preprocessor. Its integration points are generated AMD register address headers and AMD DC register helper macros that expect matching register and field names. The likely consumers are Display Core modules handling HPO DisplayPort stream/link encoders, audio packet generation, metadata packet handling, DisplayPort MST/SST allocation, Panel Replay, CRC diagnostics, and power management.

The register groups are tightly coupled by instance numbering:

- stream encoder 2 uses `APG2`, `DME8`, `VPG8`, and `DP_SYM32_ENC2`;
- stream encoder 3 uses `APG3`, `DME9`, `VPG9`, and `DP_SYM32_ENC3`;
- DPHY Symbol32 blocks `DP_DPHY_SYM320` and `DP_DPHY_SYM321` pair with link encoder instances 0 and 1;
- the `DP_SYM32_ENC1` tail is a continuation from the previous chunk and should be merged with earlier chunk research for the full encoder-1 view.

The masks use `L`-suffixed constants and are suitable for 32-bit register fields. Consumers should avoid assuming signed arithmetic semantics and should use the existing AMD register update/read helpers.

## Risks

- Generated header drift is the main risk: a wrong shift/mask silently programs the wrong hardware bits.
- Repeated blocks are highly similar but instance-specific. Copying an `ENC2`/`VPG8` macro into `ENC3`/`VPG9` code, or mixing DPHY 0/1 macros, can route state to the wrong hardware instance.
- Side-effect bits such as clear, reset, update, one-shot send, and force recalculation fields should not be written through broad read-modify-write sequences unless the caller masks them deliberately.
- Pending/status fields share register layouts with control bits in several groups. Polling code must distinguish writable controls from hardware-owned state.
- Line-number and payload fields are multi-bit packed fields; callers must shift values before masking or use helper macros that do this consistently.
- The chunk boundary splits `DP_SYM32_ENC1` and `DCHVM`, so whole-file research must reconcile adjacent chunks before making file-wide completeness claims.

## Test Signals

Useful validation signals for code using this chunk include:

- compile coverage for all generated macro names referenced by DCN 3.1.6 display code;
- register read/write traces showing correct instance selection for stream encoders 2/3, APG2/3, DME8/9, VPG8/9, DPHY0/1, and link encoder 0/1;
- DisplayPort bring-up tests that verify clock enable, FIFO reset-done, Symbol32 reset-done, DPHY ready, and stream status transitions;
- audio playback and HBR audio tests that check APG enable/status, FIFO overflow, audio mute, ASP/ATP/AIP/ACM/ISRC packet enables, and APG CRC;
- generic SDP, metadata, ISRC, MPEG infoframe, Panel Replay, and one-shot packet tests that watch pending bits clear and expected packets appear on the link;
- CRC diagnostics that compare video CRC, APG audio CRC, and DPHY CRC status/count values against expected test patterns;
- error-injection or compliance tests for DPHY slot count, rate, duplicate VC source, missing ACT, illegal symbol, overflow, cipher, and unexpected mode transition bits;
- low-power tests that exercise APG, DME, VPG, Symbol32 encoder, and DCHVM clock/memory power fields without losing stream state.

## Cross-Chunk Notes

This chunk is partial-file research for `dcn_3_1_6_sh_mask.h`. It should be merged with neighboring chunks to recover full address-block continuity. The previous chunk is needed for the beginning of `DP_SYM32_ENC1` and earlier HPO stream/link blocks. The next chunk is needed for the rest of `DCHVM_CLK_CTRL` and any subsequent DCHVM fields.
