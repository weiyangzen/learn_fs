# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 37381-39778

## Purpose

This chunk is a generated AMD DCN 3.6 register shift/mask header segment. It contains only preprocessor constants; there are no executable functions, C types, or local algorithms. The API surface is the generated naming contract where `REGISTER__FIELD__SHIFT` gives a field bit position and `REGISTER__FIELD_MASK` gives the packed register mask. Driver code combines these constants with matching register addresses from `dcn_3_6_0_offset.h` and AMD display register helpers such as `FD_SHIFT`, `FD_MASK`, `SE_SF`, `SRI`, `REG_UPDATE`, `REG_SET`, and `REG_GET`.

The requested range covers 2,168 `#define` constants across 218 register comment groups. It starts in the middle of `DIG3_DIG_FIFO_CTRL1`, then covers most of DIO digital encoder instance 3 HDMI/TMDS fields, the complete displayed DisplayPort instance 4 (`DP4`) field set in this range, digital encoder instance 4 (`DIG4`) front-end/FIFO/HDMI/TMDS fields, all AFMT instance 0 fields present for the chunk, and the beginning of AFMT instance 1 through the audio CRC control area at the line boundary.

## Important API Surface

There are no callable APIs. The important interfaces are the generated field macros consumed by register-list headers and resource construction:

- `DIG3_*` fields describe the tail of digital encoder 3 FIFO calibration plus HDMI packet generation, HDMI control/status, audio clock regeneration, generic packets, deep-color packet control, AFMT routing, digital backend clock/control/enable, TMDS control characters, DC balancing, sync character patterns, and the `DIG_VERSION` readout.
- `DP4_*` fields describe DisplayPort stream/link programming for DIO DisplayPort instance 4. The group includes link control, pixel format, MSA colorimetry and timing, stream enable/status, steer FIFO, DPHY internal/training/8b10b/PRBS/scrambler/CRC/fast-training controls, secondary packet and audio timing fields, MST/MSE rate and slot allocation, DSC, metadata transmission, ALPM and auxless ALPM controls, GSP8-GSP11 packet controls, and stream/link symbol-count diagnostics.
- `DIG4_*` repeats the digital encoder programming surface for instance 4: FE clock/enable/source selection, output CRC, clock/test/random patterns, FIFO controls, HDMI metadata/control/status/audio/ACR/VBI/infoframe/generic-packet fields, deep-color DB control, AFMT routing, backend control, TMDS encoding and DC-balancing fields, debug, and version.
- `AFMT0_*` covers audio format instance 0. The fields include ACP packet bytes, VBI packet source and HDMI audio-packet pacing, audio layout/channel enable/DP stream ID/HBR and IEC-60958 overrides, HDMI audio infoframe payload fields, IEC-60958 channel-status words, audio CRC controls/results, ramp test pattern controls, AFMT status, sample-send and acknowledge bits, audio infoframe update/source, audio source select, and memory power controls.
- `AFMT1_*` begins the same AFMT layout for instance 1 and reaches the audio CRC control/ramp-control boundary. It includes ACP, VBI packet control, packet-control2, audio infoframes, IEC-60958 words 0 and 1, and audio CRC field definitions within this range.

Representative high-risk field families include `HDMI_GENERIC*_SEND/CONT/LINE`, `HDMI_ACR_*_CTS/N`, `DP_MSA_*`, `DP_DPHY_*`, `DP_SEC_*`, `DP_MSE_*`, `DP_ALPM_*`, `AFMT_AUDIO_CHANNEL_ENABLE`, `AFMT_DP_AUDIO_STREAM_ID`, `AFMT_60958_*`, `AFMT_AUDIO_SAMPLE_SEND`, and `AFMT_MEM_PWR_*`. Many are packed next to status or pending bits, so field-level access helpers are expected rather than ad hoc whole-register writes.

## Control Flow and Usage Model

This header has no runtime control flow. Its compile-time data flow is:

1. DCN 3.6 source includes `dcn_3_6_0_offset.h` and this shift/mask header.
2. Resource and block constructors expand register-list macros such as `SRI`/`SRI_ARR` to bind instance-specific offsets, and `SE_SF`/`FD_MASK`/`FD_SHIFT` to copy field masks and shifts into block-local register structures.
3. Runtime display code programs or reads MMIO registers using those structures, so call sites can name logical fields instead of open-coding bit positions.

The direct include points found for this ASIC header are `display/dmub/src/dmub_dcn36.c`, `display/dc/irq/dcn36/irq_service_dcn36.c`, and `display/dc/resource/dcn36/dcn36_resource.c`. The DIO and AFMT fields in this chunk are mainly used through shared DCN30/DCN31/DCN35/DIO stream encoder and AFMT patterns rather than through functions in this header. For example, AFMT register tables use `AFMT0_AFMT_AUDIO_PACKET_CONTROL2`, `AFMT0_AFMT_AUDIO_PACKET_CONTROL`, `AFMT0_AFMT_60958_*`, and `AFMT0_AFMT_MEM_PWR` masks to drive audio layout, channel status, sample send, and AFMT memory power. DIO stream encoder tables in nearby generations use the same families for HDMI metadata/generic packets, HDMI ACR, TMDS pixel encoding/color format, DP MSA timing, DP secondary packets, and DIG FIFO/FE controls.

## State and Persistence Behavior

The macros themselves are stateless. The state they describe is hardware-resident MMIO state that persists until reprogrammed, reset, power-gated, or overwritten during modeset/resume:

- HDMI packet controls determine whether metadata, infoframes, generic packets, audio packets, ACR packets, null/GC/ACP/ISRC packets, and Dolby Vision metadata are emitted, whether they are continuous or one-shot, and which display line is used.
- HDMI/TMDS fields hold sink-facing link encoding state: scrambling, clock-channel rate, deep color, pixel encoding, color format, keepout behavior, control characters, DC balancing, sync patterns, and backend enable/clock controls.
- DP4 link and stream fields hold active DisplayPort state: lane/link framing, pixel format, MSA timing/colorimetry, VBID, training pattern, scrambler/PRBS/CRC, secondary packet scheduling, MST slot allocation/rate updates, DSC enablement, ALPM timing, and symbol-count diagnostics.
- AFMT fields hold audio packet and channel-status state, including HDMI/DP audio stream selection, channel enable mask, layout/HBR/IEC-60958 overrides, audio infoframe payload, audio CRC/test-ramp configuration, sample-send enable, status/acknowledge bits, and AFMT memory power state.
- Status and readback fields such as missed packet flags, pending packet sends, ACR status, CRC done/results/status, fast-training status, stream/link symbol counters, `AFMT_STATUS`, and memory-power state are hardware-observed state and should not be treated as ordinary software-owned configuration.

## Dependencies and Integration Points

- Requires the matching `dcn_3_6_0_offset.h`; this header provides bit layouts but not register addresses or base indices.
- Depends on AMD display register macro infrastructure in `reg_helper.h` and block headers that build `shift` and `mask` structures from generated `*_SHIFT`/`*_MASK` names.
- Integrates with DCN 3.6 resource construction in `dcn36_resource.c`, which includes the generated headers and defines `SRI`, `SRI_ARR`, and related macros for instance-aware register address setup.
- Integrates with DMUB register initialization in `dmub_dcn36.c`; that path copies selected generated fields into DMUB register tables. This chunk's DIO/AFMT fields are not the main DMUB scratch/mailbox surface, but they share the same generated-header dependency.
- Integrates with IRQ service compilation for DCN 3.6 through the same include pair, although this chunk is mostly stream/audio/link field definitions rather than interrupt routing logic.
- Uses shared block layouts from prior DCN generations. AFMT register-list headers from DCN30/DCN31 consume `AFMT0_*` masks with `SE_SF`; DIO stream encoder headers from later/nearby generations consume matching `DIG0_*` and `DP0_*` field families. Instance number changes (`DIG3`, `DIG4`, `DP4`, `AFMT0`, `AFMT1`) are resolved by register-table construction rather than by unique code paths for every instance.

## Risks and Edge Cases

- Boundary truncation: this chunk starts after the first `DIG3_DIG_FIFO_CTRL1` shift definitions and ends before the full `AFMT1` block is complete. The final per-file merge must reconcile adjacent chunks before declaring either group complete.
- Offset/mask drift: generated offset and shift/mask headers must match the same hardware register database. A correct-looking field mask paired with a stale offset can write a valid bit pattern into the wrong register.
- Repeated-instance mistakes: `DIG3` and `DIG4` are structurally similar, and `AFMT0`/`AFMT1` repeat the AFMT layout. A wrong instance table can create failures isolated to one connector, stream encoder, or audio formatter.
- Packed-field corruption: line numbers, packet-send bits, pending/missed flags, control bits, and status bits often share a register. Whole-register writes can unintentionally clear diagnostics, retrigger packets, or change timing.
- HDMI timing sensitivity: generic-packet line numbers, metadata packet enables, ACR CTS/N values, deep-color controls, scrambling, and TMDS color-format fields may fail only with specific HDMI sinks, HDR/Dolby Vision metadata, high pixel clocks, deep color, or audio sample-rate transitions.
- DP link-training and MST sensitivity: DPHY training/scrambler/PRBS fields, MSE slot/rate updates, DSC controls, ALPM/auxless ALPM fields, and secondary packet scheduling can produce sink-specific black screens, link drops, audio loss, or power-state regressions when programmed out of sequence.
- Status-versus-control confusion: fields named `*_STATUS`, `*_READBACK`, `*_DONE`, `*_PENDING`, `*_MISSED`, `*_RESULT`, and symbol-count status fields are diagnostic or hardware-owned in normal operation.
- Width validation: packed values include 4-bit channel numbers, 5-bit packet counts, 6-bit HDMI line fields, 8-bit infoframe and audio source/channel fields, 16-bit MSA/ACR/symbol-count fields, 24-bit CRC/ramp fields, and full 32-bit timestamp/symbol-count values. Callers must clamp before shifting.
- Power sequencing: `DIG*_DIG_BE_CLK_CNTL`, `DIG*_DIG_BE_EN_CNTL`, `DIG*_DIG_FE_CLK_CNTL`, `DIG*_DIG_FE_EN_CNTL`, `AFMT*_AFMT_MEM_PWR`, and DP ALPM fields interact with runtime power management. Forcing a block off or into low power while packets or audio are active can cause hangs or silent output loss.

## Test Signals

- Build with DCN 3.6 enabled to catch missing generated names in resource, IRQ, DMUB, DIO stream encoder, and AFMT register-table expansion.
- Static checks should verify every field in the chunk has coherent shift/mask geometry, no overlap within expected packed fields, and repeated layouts align where `DIG3`/`DIG4` or `AFMT0`/`AFMT1` are intended to mirror.
- HDMI runtime coverage should include modesets across 8bpc/deep-color, scrambling on/off, TMDS pixel encoding and color-format changes, HDR/Dolby Vision metadata, generic packet sends, infoframes, ACR updates for 32/44.1/48 kHz families, suspend/resume, and hotplug.
- DP4 coverage should exercise link training patterns, scrambler/PRBS/CRC diagnostics, MSA timing/colorimetry, SST and MST/MSE slot allocation, DSC, secondary audio/data packets, metadata transmission, ALPM/auxless ALPM, and stream/link symbol counters.
- Audio coverage should validate HDMI and DP audio enumeration, AFMT channel enable/layout, DP audio stream ID selection, IEC-60958 channel-status programming, HBR override behavior, audio sample send, audio CRC diagnostics, and audio disable/re-enable transitions.
- Power-management coverage should watch DIG FE/BE clock gating, AFMT memory power state, ALPM state, resume/retrain paths, and packet/audio recovery after display core reset.
- Register-dump diagnostics should inspect `DIG3_HDMI_*`, `DIG4_HDMI_*`, `DP4_DP_*`, `AFMT0_AFMT_*`, and `AFMT1_AFMT_*` fields when debugging sink-specific packet timing, link training, audio dropouts, color-format mismatches, or power regressions.
