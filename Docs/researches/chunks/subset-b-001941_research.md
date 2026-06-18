# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 30148-32542

## Purpose

This chunk is a generated DCN 3.2.0 register field shift/mask header for display I/O encoder blocks. It defines C preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for DP1 tail registers, the complete DIG1/DIG2 HDMI/TMDS register groups, the complete DP2 DisplayPort link/stream/secondary-data group, and the beginning of the DP3 DisplayPort group. The definitions are data rather than executable logic, but they are part of the ABI between AMDGPU display driver code and DCN 3.2.0 hardware MMIO registers.

The range contains 2,171 `#define` entries across 212 register comment sections. It starts after `DP1_DP_SEC_METADATA_TRANSMISSION` masks, continues through DP1 ALPM/GSP support, covers `addressBlock: dcn_dc_dio_dig1_dispdec`, `addressBlock: dcn_dc_dio_dp2_dispdec`, `addressBlock: dcn_dc_dio_dig2_dispdec`, and ends in `addressBlock: dcn_dc_dio_dp3_dispdec` after the DP3 link framing fields.

## Important APIs, Types, and Register Groups

There are no functions or C types in this chunk. The important API surface is the naming contract used by `REG_*`, `SE_SF`, `LE_SF`, and `SRI_ARR` macros elsewhere in the display driver:

- Field names use `<register>__<field>__SHIFT` and `<register>__<field>_MASK`.
- Instance-specific register names such as `DP2_DP_LINK_CNTL` and `DIG2_HDMI_GENERIC_PACKET_CONTROL0` pair with instance-address macros from the matching offset header.
- Driver code generally consumes these definitions through generated shift/mask tables, not by spelling the raw constants at call sites.

Major groups in this range:

- `DP1_DP_ALPM_CNTL` and `DP1_DP_AUXLESS_ALPM_CNTL1..5`: DisplayPort active link power-management sequencing, wakeup, LFPS symbol timing, hardware mode, lock periods, line/frame numbers, and wakeup interrupt state.
- `DP1_DP_GSP8_CNTL..DP1_DP_GSP11_CNTL` and `DP1_DP_GSP_EN_DB_STATUS`: secondary generic stream packet enable, send timing, pending/active/deadline status, and double-buffer pending bits.
- `DIG1_*` and `DIG2_*`: display encoder front-end/back-end controls, output CRC, test/random patterns, FIFO control, HDMI metadata/audio/ACR/VBI/infoframe/generic packet controls, HDMI guard-band/control/status, AFMT, TMDS control characters, TMDS sync/DC-balancer/pattern generation, version, and forced-disable state.
- `DP2_*`: the full non-HPO DisplayPort encoder register field set for link status, pixel format, MSA colorimetry/misc/timing, video stream enable/status, steer FIFO/TU overflow, DPHY control/training/symbol/PRBS/scrambler/CRC/fast-training, secondary audio and packet controls, MST MSE rate and slot allocation tables, MSO, DSC, metadata, ALPM, GSP, and DB control.
- `DP3_*` beginning: link status, pixel format, MSA fields, stream control, FIFO, DPHY internal control, video timing M/N, link framing, HBR2 eye pattern, video interrupt, and start of DPHY control.

Representative field semantics:

- Enable/state fields are one-bit controls such as `DP_VID_STREAM_ENABLE`, `DPHY_FEC_EN`, `HDMI_STREAM_ENABLE`, `DIG_FE_ENABLE`, `FORCE_DIG_DISABLE`, and `DP_SEC_METADATA_PACKET_ENABLE`.
- Timing and line fields use multi-bit ranges such as `DP_SEC_METADATA_PACKET_LINE`, `DP_ALPM_WAKEUP_LINE_NUM`, `DP_VID_N`, `DP_VID_M`, `HDMI_GENERIC*_LINE`, and MSA timing parameters.
- Packet controls expose continuous/send/update/pending bits for HDMI generic packets, DP secondary packets, GSP packets, and MST allocation updates.
- Diagnostic fields expose CRC results, overflow flags/acks, fast-training status, PRBS selection/seeds, TMDS feedback, and output CRC selection.

## Control Flow

This header has no local control flow. Runtime control flow is created where driver code uses these shift/mask entries to read or update MMIO fields:

- DCN 3.2 stream encoder setup builds register and field tables with `SRI_ARR(...)` and `SE_SF(...)` in `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h` and `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h`.
- Stream encoder functions then call `REG_UPDATE`, `REG_SET`, and `REG_GET` against logical registers such as `HDMI_GENERIC_PACKET_CONTROL0`, `DP_SEC_METADATA_TRANSMISSION`, and `DP_GSP11_CNTL`.
- Link encoder initialization in `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.c` uses the DIG/TMDS fields through link shift/mask tables; for example hardware init writes `TMDS_CTL_BITS.TMDS_CTL0` as a legacy setting before AUX initialization.
- DP/HDMI enable, metadata packet programming, audio infoframe setup, MST allocation, DSC/MSO configuration, FEC readiness, and training-pattern setup are all higher-level flows whose register writes depend on this header matching the hardware layout.

## State and Persistence Behavior

The file itself has no stored state. Its constants define how driver writes alter persistent hardware register state until reset, power gating, mode change reprogramming, or another MMIO write changes it.

Important state domains represented here include:

- Link state: `DP_LINK_TRAINING_COMPLETE`, `DP_LINK_STATUS`, lane count, enhanced framing, VBID behavior, DPHY FEC state, scrambler/training state, and stream enable/status.
- Packet state: HDMI generic/infoframe/audio/ACR packets, DP secondary packets, metadata packets, GSP packets, and double-buffer pending/taken bits.
- Power-management state: ALPM sleep/standby send/pending bits, AUX-less wakeup scheduling, hardware ALPM mode, FEC immediate enable, and wakeup interrupts.
- Diagnostic state: CRC enable/result fields, FIFO and TU overflow flags/acks, fast-training status, and TMDS/DC-balancer feedback.

Because many fields are status, ack, pending, or clear-on-write style controls, stale or incorrect masks can leave hardware in a partially updated state even when the C code compiles.

## Dependencies and Integration Points

This header depends on the matching DCN 3.2.0 offset header for register addresses and base indices. The shift/mask names integrate with AMD display helper macros in the DCE/DCN stream and link encoder layers.

Concrete consumers found in the tree:

- `drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.h` maps DIG and DP instance registers with `SRI_ARR(HDMI_GENERIC_PACKET_CONTROL0..10, DIG, id)`, `SRI_ARR(DP_SEC_METADATA_TRANSMISSION, DP, id)`, `SRI_ARR(DP_GSP11_CNTL, DP, id)`, and `SRI_ARR(TMDS_CTL_BITS, DIG, id)`.
- `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.h` maps fields such as `DP_SEC_GSP11_ENABLE`, `DP_SEC_GSP11_LINE_NUM`, HDMI generic packet continuous/send/line fields, and DP metadata-packet enable/line fields.
- `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_stream_encoder.c` reads `DP_GSP11_CNTL` fields for PPS/GSP state reporting.
- `drivers/gpu/drm/amd/display/dc/dio/dcn32/dcn32_dio_link_encoder.c` updates `TMDS_CTL_BITS.TMDS_CTL0` during hardware initialization.
- Earlier-generation stream encoder code such as `dcn20_stream_encoder.c`, `dcn30_dio_stream_encoder.c`, and DCE helpers show the same logical register families used for HDMI generic packets and DP metadata, indicating this generated header is part of a cross-generation register-table pattern.

## Risks

- Bit-position drift is the main risk. A wrong `__SHIFT` or `_MASK` silently targets the wrong hardware field, causing blank display, failed link training, broken FEC/DSC/MSO, incorrect audio or metadata packets, or power-management hangs.
- Instance mismatch is risky because this range repeats similar DIG and DP blocks for different encoder instances. Copy/paste or generation errors between `DP2`, `DP3`, `DIG1`, and `DIG2` can compile cleanly while programming the wrong instance.
- Pending/ack/clear fields require exact masks. Incorrect masks around `DP_DB_CNTL`, `DP_GSP_EN_DB_STATUS`, FIFO overflow ack bits, or packet send-pending bits can make update sequencing appear stuck.
- Timing fields carry protocol-visible behavior. Bad line numbers, M/N fields, MSA timing, ACR values, or metadata-packet timing can produce intermittent monitor compatibility failures rather than deterministic driver crashes.
- ALPM and AUX-less ALPM fields interact with link power states and wakeup timing. Incorrect masks can cause resume/wakeup regressions, especially on eDP or USB-C DisplayPort paths.

## Test Signals

Useful validation signals are mostly hardware and integration oriented:

- Build coverage: AMDGPU/DC display must compile with DCN 3.2.0 resources and no missing field names in `SE_SF`, `LE_SF`, or `SRI_ARR` tables.
- Display smoke tests: DP and HDMI monitors light up on DIG/DP instances covered by this chunk, including DP2/DIG2 and DP3 paths where available.
- Link-training tests: DP link training completes, lane count/rate programming works, FEC can be enabled and reports active, and training-pattern/PRBS diagnostics behave as expected.
- Mode-set tests: pixel encoding/depth, MSA timing/colorimetry, video stream enable/disable, VBID, and TU/FIFO overflow status remain sane across hotplug and mode changes.
- Metadata/audio tests: HDMI infoframes/generic packets, DP secondary metadata packets, audio ACR/N/M programming, and GSP/PPS reads for DSC paths are correct.
- MST/MSO/DSC tests: MSE slot allocation updates, MSO split control, and DSC enable state work on capable panels.
- Power tests: ALPM/AUX-less ALPM sleep and wakeup paths do not hang or lose link after idle, suspend/resume, or panel self-refresh transitions.
- Debug/diagnostic tests: output CRC, DPHY CRC, fast-training status, and overflow ack fields can be read or cleared without wedging the encoder.
