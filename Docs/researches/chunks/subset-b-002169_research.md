# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 44859-47301

## Purpose

This chunk is a generated AMD DCN 4.1.0 register field encoding slice. It contains preprocessor `#define` constants only: field shifts and bit masks for display-engine hardware registers. There are no C functions, local structs, enums, runtime branches, allocations, or persistent software data structures in this range.

The covered hardware area starts at the tail of HPD0 hot-plug detect filtering, then defines HPD1-HPD3 hot-plug status/control fields, HPO top-level clock and I/O control fields, HPO DP stream-mapper fields, HDMI link/FRL/stream/AFMT/TB encoder fields, HPO DP stream encoder 0 fields, DP SYM32 stream encoder 0 fields, HPO DP stream encoder 1 fields, APG1 audio packet generator fields, DME6 metadata-engine fields, and the first VPG6 generic-packet fields. Although the repository path is under `distributed-fs/ceph-client`, this file is AMDGPU Display Core hardware metadata and has no Ceph, filesystem, distributed storage, or network protocol behavior.

This chunk is part of the companion pair for DCN 4.1.0 direct register programming:

- `dcn_4_1_0_offset.h` supplies register addresses or offsets.
- `dcn_4_1_0_sh_mask.h` supplies the field extraction/insertion metadata used by register helper macros.

## Important APIs, Types, And Macros

The exported API surface is generated macro names of the form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

These names are consumed by AMD Display Core register helpers and register-list macros such as `SE_SF(...)`, `REG_GET(...)`, `REG_UPDATE(...)`, and `REG_UPDATE_N(...)`. The macros are not standalone APIs; they are the field metadata that lets typed display code update individual bitfields without hard-coding shift and mask literals.

Visible address blocks and register families in this chunk include:

- `dcn_dcec_dcoh_hpd1_dispdec`, `hpd2`, and `hpd3`: `HPD*_DC_HPD_INT_STATUS`, `INT_CONTROL`, `CONTROL`, `FAST_TRAIN_CNTL`, and `TOGGLE_FILT_CNTL`. These define hot-plug interrupt status, sense state, delayed sense, RX interrupt status, ACK/enable/polarity, debounce/timer, fast-train, and connect/disconnect interrupt delay fields. The first visible line is the final `HPD0_DC_HPD_TOGGLE_FILT_CNTL__DC_HPD_DISCONNECT_INT_DELAY_MASK` from the previous HPD0 block.
- `dcn_dcec_hpo_hpo_top_dispdec`: `HPO_TOP_CLOCK_CONTROL` and `HPO_TOP_HW_CONTROL`. These expose clock gate-disable bits for DISPCLK, SOCCLK, HDMI stream/char clocks, DP stream clock, SYMCLK32 SE/LE, an FGCG reporting disable bit, test clock selection, and HPO I/O enable.
- `dcn_dcec_hpo_dp_stream_mapper_dispdec`: `DP_STREAM_MAPPER_CONTROL0..5`, each with `DP_STREAM_LINK_TARGET`. These map stream encoder instances to link encoder targets.
- `dcn_dcec_hpo_hdmi_link_enc0_dispdec`: `HDMI_LINK_ENC_CONTROL` and `HDMI_LINK_ENC_CLK_CTRL`, covering enable, soft reset, clock enable, and HDMI character clock selection.
- `dcn_dcec_hpo_hdmi_frl_enc0_dispdec`: `HDMI_FRL_ENC_CONFIG`, `CONFIG2`, `METER_BUFFER_STATUS`, and `MEM_CTRL`, covering FRL lane count/training/scrambler fields, lane training patterns, jitter metering, meter-buffer overflow/status reset, and memory power control.
- `dcn_dcec_hpo_hdmi_stream_enc0_dispdec`: HDMI stream encoder clock, input mux, and clock-ramp FIFO fields, including FIFO enable/reset/status, pixel encoding indicators, min/max/calibrated levels, read-start level, and read-clock source.
- `dcn_dcec_hpo_hdmi_stream_enc0_afmt_afmt_dispdec`: `AFMT4_*` HDMI audio formatter fields for ACP, VBI packet control, audio packet control, HDMI/DP audio infoframes, IEC 60958 channel status words, audio CRC, debug ramp, status, source control, DTO debug, and AFMT memory power.
- `dcn_dcec_hpo_hdmi_stream_enc0_dme_dme_dispdec`: `DME4_DME_CONTROL` and memory control for metadata engine enable, stream type, double-buffer pending/taken/clear/disable, transmission missed/clear, HUBP requestor ID, and DME memory power state.
- `dcn_dcec_hpo_hdmi_stream_enc0_vpg_vpg_dispdec`: `VPG4_*` fields for generic packet data indexing/data bytes, generic-packet frame and immediate update bits for slots 0-14, pending bits, generic lock/conflict status, memory power, ISRC data access, and MPEG info fields.
- `dcn_dcec_hpo_hdmi_tb_enc0_dispdec`: HDMI transmission block fields for core control, pixel format, packet and ACR packet control, VBI packets, guard-band/control-period behavior, generic packet send/pending controls for 15 generic slots, generic packet line/EMP placement, double-buffer pending/disable, ACR CTS/N values for 32/44/48 kHz families and live status, buffer prefill override, memory power, metadata packet control, active/blank dimensions, CRC control/results, mode, and input FIFO error.
- `dcn_dcec_hpo_dp_stream_enc0_dispdec` and `dp_stream_enc1`: per-instance DP stream encoder clock, pixel/audio mux, clock-ramp FIFO status, and spare fields.
- `dcn_dcec_hpo_dp_stream_enc0_apg_apg_dispdec` and `apg1`: APG audio packet generator reset, enable, DP audio stream ID, channel-count override, debug generator, packet source selection, ACP/audio info/debug 60958 words, audio CRC, debug ramp, audio/HBR/FIFO-overflow status, DTO debug, memory power, and spare fields.
- `dcn_dcec_hpo_dp_stream_enc0_dme_dme_dispdec` and `dme6`: DME metadata engine control and DME memory power fields. In this chunk `DME5_*` belongs to DP stream encoder 0 and `DME6_*` begins the DP stream encoder 1 DME block.
- `dcn_dcec_hpo_dp_stream_enc0_vpg_vpg_dispdec` and the opening of `vpg6`: VPG packet, update, status, memory power, ISRC, and MPEG fields for stream encoder packet generation. The chunk ends after `VPG6_VPG_GENERIC_PACKET_DATA__VPG_GENERIC_DATA_BYTE1__SHIFT`, so the VPG6 block is incomplete and must be merged with the next chunk for the full VPG6 field set.
- `dcn_dcec_hpo_dp_sym32_enc0_dispdec`: DP SYM32 encoder 0 field definitions for stream enable/reset, pixel-to-symbol FIFO, double-buffered MSA/pixel format, video pixel format, MSA words, hblank symbol width, SDP generic packet controls 0-14, SDP stream/audio/metadata/framing/ATP controls, idle pattern, MSA/VBID/video stream controls, panel replay optimization, video CRC, symbol count, ALPM sleep/wake/request/status/interrupt fields, memory power, and spare.

There are no C types in the chunk. The "types" implied by these definitions are hardware bitfields packed into 32-bit MMIO registers.

## Control Flow And Usage Model

This header has no local control flow. Runtime control flow appears in the display driver code that includes this generated metadata and then programs the hardware through register abstraction macros.

A typical use path is:

1. DCN 4.1.0 or related Display Core resource setup includes the matching offset and mask headers.
2. Block-specific register-list macros bind register offsets, field masks, and field shifts into per-block register structures.
3. Runtime display code calls helpers such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_4`, `REG_GET`, or `REG_GET_3`.
4. The helper uses the generated mask and shift macros to read, clear, insert, or extract exactly one field in a 32-bit register.

The HPO DP stream encoder code is a direct integration example. Its register-list header defines `SE_SF(DP_STREAM_MAPPER_CONTROL0, DP_STREAM_LINK_TARGET, mask_sh)` and similar entries for `DP_STREAM_ENC0_*` and `DP_SYM32_ENC0_*` fields. Its implementation maps stream encoders to link encoders with `REG_UPDATE(DP_STREAM_MAPPER_CONTROL*, DP_STREAM_LINK_TARGET, link_enc_inst)`, configures audio source muxes with `DP_STREAM_ENC_INPUT_MUX_AUDIO_STREAM_SOURCE_SEL`, enables audio SDP packets with `ASP_ENABLE`, `ATP_ENABLE`, and `AIP_ENABLE`, controls `SDP_STREAM_ENABLE`, and reads back encoder state with fields such as `DP_SYM32_ENC_ENABLE`, `VID_STREAM_ENABLE`, `PIXEL_ENCODING_TYPE`, `UNCOMPRESSED_PIXEL_ENCODING`, and `DP_STREAM_LINK_TARGET`.

The APG fields in this chunk are similarly consumed through APG register/mask lists. APG setup, enable/disable, debug generation, channel status, CRC, and FIFO overflow handling depend on the `APG0_*` and `APG1_*` field definitions staying aligned with the actual hardware generation.

The HPD fields are part of the display connector interrupt path. They expose sense, delayed sense, interrupt status, RX interrupt status, polarity, ACK, enable, and debounce/toggle timers for hotplug and DisplayPort AUX/HPD event handling.

## State And Persistence Behavior

The macros themselves are immutable compile-time constants and persist no state. The state they describe is hardware state in display engine registers.

State represented in this chunk includes:

- Connector hot-plug state: HPD sense, delayed sense, interrupt status, interrupt polarity, ACK bits, RX interrupt status, HPD enable, and connection/RX/toggle filter timers.
- Clock and power state: HPO clock gate-disable bits, HDMI/DP stream encoder clocks, HDMI FRL/TB/AFMT/APG/VPG/DME/SYM32 memory power force/disable/state fields, and HPO I/O enable.
- Stream routing state: DP stream mapper link target fields and HDMI/DP stream input mux selectors.
- Packet/audio state: AFMT and APG audio infoframe/channel-status/ACP/CRC/debug fields, HDMI TB generic packet controls, VPG generic/ISRC/MPEG packet fields, and DP SYM32 SDP generic/audio/metadata packet controls.
- Video stream state: DP SYM32 enable/reset, FIFO reset/done/overflow, MSA data and double-buffering, pixel format, video stream enable/status, VBID compressed-stream flags, panel replay optimization, CRC, symbol count, and hblank minimum symbol width.
- Metadata state: DME metadata engine enable, stream type, DB pending/taken/clear/disable, missed transmission status/clear, metadata packet line/enable fields, and memory power state.
- Diagnostic/status state: FIFO calibration and error fields, CRC valid/result fields, generic packet lock/conflict status, APG audio FIFO overflow, FRL jitter/meter-buffer status, HDMI input FIFO errors, ALPM status/pending/interrupt state, and hardware current-frame state.

Hardware register state persists only for the lifetime of the relevant hardware block configuration. It can be reset or rewritten by mode sets, hotplug handling, audio stream setup, link retraining, display power gating, runtime suspend/resume, GPU reset, DCN block reset, or firmware/display-manager reinitialization. No filesystem persistence is involved.

## Dependencies And Integration Points

- Companion register offsets are in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`. Correct behavior depends on using offset and sh/mask files generated for the same ASIC register version.
- Display Core register helper infrastructure consumes these names through generated per-block register, shift, and mask tables. Relevant consumers include HPO DP stream encoder code, APG code, VPG code, DME metadata packet code, HDMI stream/link/TB encoder code, HPD/IRQ handling, and resource construction for DCN 4.1-era display blocks.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h` demonstrates the pattern with `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST`, register storage members, and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST`. While that file is named for DCN 3.1, the field families and helper contract are shared by later generated register headers when the block layout is compatible.
- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.c` demonstrates runtime reads and updates for fields in this chunk: stream-to-link mapping, audio stream source selection, APG clock enable when available, SDP audio packet enable/disable, SDP stream enable, and state readback.
- `display/dc/dcn31/dcn31_apg.h` binds APG field names such as `APG_RESET`, `APG_RESET_DONE`, `APG_ENABLE`, `APG_DP_AUDIO_STREAM_ID`, `APG_DBG_AUDIO_CHANNEL_ENABLE`, and `APG_MEM_PWR_FORCE` to the generated masks and shifts.
- HDMI-related field definitions in this chunk integrate with HDMI link/FRL/TB stream setup, infoframe/generic packet programming, ACR/N/CTS audio timing, CRC diagnostics, memory power management, and metadata packet handling.
- HPD fields integrate with IRQ service and connector-detection paths that need to program interrupt polarity, ACK/enable bits, debounce timers, and read delayed sense.

## Risks And Edge Cases

- Header-generation pairing is critical. If `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` are mismatched, code can compile while programming the wrong bits in valid-looking registers.
- The chunk starts and ends mid-context. It begins with the final HPD0 toggle-filter mask from the previous block and ends inside `VPG6_VPG_GENERIC_PACKET_DATA`. Whole-file reconciliation must preserve chunk ordering so HPD0 and VPG6 are not treated as complete from this chunk alone.
- Repeated block instances hide copy/paste or generation drift. HPD1-HPD3, APG0/APG1, DME4/DME5/DME6, VPG4/VPG5/VPG6, and DP stream encoder 0/1 blocks have similar layouts. A single incorrect suffix, shift, or mask can affect only one connector or stream instance and may not be caught by tests using instance 0 only.
- Some mapper fields expose more logical targets than a specific implementation may support. For example, this chunk defines `DP_STREAM_MAPPER_CONTROL0..5`, while nearby HPO stream encoder code asserts a smaller stream/link range in one generation. Resource construction must keep instance counts aligned with the target ASIC.
- Status, clear, and control fields are adjacent. Fields such as `*_CLEAR`, `*_ACK`, `*_PENDING`, `*_MISSED`, `*_OVERFLOW_STATUS_CLEAR`, and `*_RESET` must be treated according to hardware semantics; using a generic read-modify-write flow on write-one-to-clear or transient status fields can lose events.
- Power and clock fields are sensitive. Incorrect HPO clock gating, APG/VPG/DME/FRL/TB/SYM32 memory power, or clock-enable programming can cause intermittent blanking, audio dropout, packet loss, or power-management regressions.
- Packet timing fields are mode-dependent. Generic packet line numbers, EMP flags, metadata packet line references, MSA transmission line numbers, hblank symbol width, ALPM sleep/wake line numbers, and ACR CTS/N fields can fail only on specific display modes, refresh rates, DSC/panel replay states, or HDMI/DP sink combinations.
- Audio field mistakes are sink-dependent. AFMT/APG channel layout, HBR, IEC 60958 channel status, AIP/ATP/ASP enable, stream ID, audio infoframe, and CRC fields may pass basic video tests but fail with multichannel PCM, HBR, specific sample rates, or hotplug/suspend audio reconfiguration.
- DP SYM32 generic packet controls 0-14 are highly repetitive and dense. The update, pending, continuous transmission, one-shot, payload-size, SOF-reference, and line-number fields must remain slot-aligned with VPG/DME packet producers.

## Test Signals

- Build AMDGPU Display Core with DCN 4.1.0 support enabled. Compile-time failures in register-list expansion, `SE_SF(...)`, `REG_GET(...)`, or `REG_UPDATE(...)` indicate missing or renamed generated symbols.
- Static generated-header validation should verify that every `__SHIFT` field has the expected matching `_MASK`, that masks match shifts and widths, and that repeated instances such as HPD1-HPD3, APG0/APG1, DP stream encoders 0/1, and VPG4/VPG5/VPG6 remain intentionally aligned.
- Register dump comparison against the DCN 4.1.0 hardware register specification is the strongest validation for this chunk, especially for dense HDMI TB generic packet controls, DP SYM32 SDP controls, and the partial VPG6 tail.
- Hotplug testing should exercise HPD1, HPD2, and HPD3 connectors, including connect/disconnect debounce, delayed sense, RX interrupts, interrupt ACK/polarity, suspend/resume, and rapid plug/unplug sequences.
- HPO DP testing should cover stream-to-link mapping, stream enable/disable, pixel mux selection, DP audio enable/disable, SDP stream enable, generic packet transmission, metadata packet enable, MSA updates, CRC readback, symbol count, ALPM sleep/wake, panel replay, and stream state readback.
- HDMI testing should cover FRL link training, scrambler behavior, jitter/meter-buffer status, HDMI TB packet generation, VBI/audio/ACP/infoframe programming, ACR CTS/N for 32/44/48 kHz families, metadata packets, CRC, FIFO status, and multiple pixel formats.
- Audio testing should cover DP and HDMI sinks with stereo, multichannel, HBR, multiple sample rates, stream-ID changes, hotplug, mode set, runtime power management, suspend/resume, and FIFO overflow/CRC diagnostics.
- Power-management tests should toggle display idle, memory low-power, clock gating, runtime suspend/resume, and GPU reset paths while validating that APG/VPG/DME/FRL/TB/SYM32 blocks reinitialize correctly and do not leave stale pending, reset, or memory-power status bits.
