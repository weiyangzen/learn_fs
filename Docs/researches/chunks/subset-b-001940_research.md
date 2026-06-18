# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 27728-30147

## Scope And Purpose

This chunk is part of AMDGPU Display Core Next 3.2.0 generated register field metadata. It contains preprocessor constants only: `__SHIFT` and `_MASK` definitions for memory-mapped display I/O registers. There are no C functions, structs, enums, storage objects, locks, or executable branches in this range.

The path lives under a local `ceph-client` source mirror, but the source slice is AMD GPU display-driver hardware metadata. It does not implement Ceph filesystem behavior, distributed storage behavior, or persistent filesystem state.

The covered hardware surface spans the display I/O path:

- The tail of `HPD0` and complete `HPD1` through `HPD4` hot-plug-detect register fields.
- Full `DP0` DisplayPort stream encoder and main-link field definitions.
- Full `DIG0` digital front-end/back-end, HDMI packet, AFMT, and TMDS field definitions.
- The beginning and most of `DP1` DisplayPort stream encoder definitions, ending in the middle of `DP1_DP_SEC_METADATA_TRANSMISSION`.

The chunk starts after the first two `HPD0_DC_HPD_INT_STATUS` shifts and ends before the remaining `DP1_DP_SEC_METADATA_TRANSMISSION` masks plus later `DP1` ALPM/GSP/AUX-less ALPM fields. Final per-file reconciliation must merge adjacent chunks before treating `HPD0` and `DP1` as complete.

## Important API Surface

The exported interface is the generated field naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned mask for that field.
- Names ending in `MASK_MASK` are expected when the hardware field itself is named `MASK` and the generated suffix denotes the mask constant.

The companion offset header, `dcn_3_2_0_offset.h`, supplies the matching `reg...` offsets and `reg..._BASE_IDX` values. Runtime code combines offsets, shifts, and masks through AMD Display Core helper macros such as `SRI`, `SE_SF`, `LE_SF`, `IRQ_REG_ENTRY`, `REG_READ`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `generic_reg_update_ex`.

Major macro families in this chunk:

- `HPD[0-4]_DC_HPD_INT_STATUS`: HPD interrupt status, current and delayed sense, RX interrupt status, and connect/disconnect debounce timer readback fields.
- `HPD[0-4]_DC_HPD_INT_CONTROL`: HPD and HPD-RX interrupt acknowledge, polarity, and enable fields.
- `HPD[0-4]_DC_HPD_CONTROL`, `FAST_TRAIN_CNTL`, and `TOGGLE_FILT_CNTL`: HPD enable, connection/RX timers, connect-time AUX/fast-training delays, and connect/disconnect filter delays.
- `DP0_*` and `DP1_*` link/video fields: link-training-complete, link status, embedded-panel mode, pixel encoding/depth, lane count, video stream enable/status/deferred disable, FIFO reset/overflow/TU size, MSA colorimetry/misc, M/N timing, link framing, VBID, stream-disable interrupt, and DPHY training/scrambler/CRC/test-pattern controls.
- `DP*_DP_DPHY_*`: FEC enable/readback, scrambler selection, bypass/skew bypass, training pattern selection, PRBS, 8b10b state, CRC enable/control/result, MST CRC slot and phase status, and fast-training control/status.
- `DP*_DP_SEC_*`: DP secondary-data packet stream enable, ASP/ATP/AIP/ACM enables, generic stream packet enables, GSP send/pending/deadline/any-line state, line-number programming, audio M/N values, timestamp mode, packet coding/version/channel-count override, and framing/collision/audio-mute controls.
- `DP*_DP_MSE_*`: MST rate programming, slot-allocation table entries/status for sources 0-5, update controls, link timing, and MST encoder behavior.
- `DP*_DP_MSO_*`, `DP*_DP_DSC_CNTL`, `DP*_DP_MSA_VBID_MISC`, and `DP*_DP_SEC_METADATA_TRANSMISSION`: multi-stream operation secondary packet enables, DSC mode, VBID override and VBID6 line scheduling, and metadata packet scheduling.
- `DP*_DP_ALPM_CNTL`, `DP*_DP_GSP8_CNTL` through `GSP11_CNTL`, `DP*_DP_GSP_EN_DB_STATUS`, and `DP*_DP_AUXLESS_ALPM_CNTL[1-5]`: ALPM sleep/standby/wakeup controls, higher-numbered GSP send/enable/line fields, double-buffer pending status, and AUX-less ALPM timing/interrupt fields. This chunk fully covers these for `DP0`; for `DP1`, only the start of `DP_SEC_METADATA_TRANSMISSION` is present and later ALPM/GSP/AUX-less fields fall in the next chunk.
- `DIG0_DIG_FE_CNTL`, `DIG0_DIG_BE_CNTL`, and `DIG0_DIG_BE_EN_CNTL`: source selection, stereosync, digital bypass, Dolby Vision enable/status, front-end and back-end symbol-clock state, TMDS pixel/color format, dual-link/swap/RB switch, DIG mode, HPD selection, and DIG enable state.
- `DIG0_DIG_OUTPUT_CRC_*`, `DIG0_DIG_CLOCK_PATTERN`, `DIG0_DIG_TEST_PATTERN`, `DIG0_DIG_RANDOM_PATTERN_SEED`, and `DIG0_DIG_FIFO_CTRL[0-1]`: output CRC, clock/test/random pattern generation, FIFO enable/reset/read-start level/output mode, reset-done/error status, and FIFO calibration levels.
- `DIG0_HDMI_*`: HDMI metadata, control/status, audio packet delay, ACR packet control and CTS/N values, VBI packets, audio/MPEG infoframes, generic packet controls for packets 0-14, generic packet line numbers, generic-packet enable double-buffer status, HDMI double-buffer control, and AVMUTE/general-control fields.
- `DIG0_AFMT_CNTL` and `DIG0_TMDS_*`: AFMT audio clock control and TMDS control characters, sync patterns, control-bit generation, DC balancer, feedback, stereosync selection, and version/force-disable fields.

## Control Flow

This header chunk has no runtime control flow. Its behavior is indirect: consumers expand the generated macro names into register tables and then use those tables during display link setup, stream programming, interrupt handling, and diagnostics.

Observed consumer patterns in this tree include:

1. DCN32 include sites pull in `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register-list macros such as `SE_COMMON_MASK_SH_LIST_DCN32` in `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h` paste field names from this chunk into stream-encoder shift/mask tables.
3. Runtime stream-encoder methods call `REG_UPDATE`, `REG_GET`, and related helpers. For example, `dcn32_dio_stream_encoder.c` updates `DP_DSC_CNTL.DP_DSC_MODE`, reads `DP_GSP11_CNTL.DP_SEC_GSP11_*`, reads `DP_MSA_VBID_MISC.DP_VBID6_*`, and updates `DP_VID_STREAM_CNTL.DP_VID_STREAM_ENABLE`.
4. IRQ service code in `display/dc/irq/dcn32/irq_service_dcn32.c` builds HPD and HPD-RX IRQ entries using `DC_HPD_INT_CONTROL` enable/ack fields and `DC_HPD_INT_STATUS` status registers.
5. Link encoder code inherited from DCN10 accesses HPD fields through per-instance `hpd_regs`; `dcn10_link_encoder_enable_hpd()` and `dcn10_link_encoder_disable_hpd()` update `DC_HPD_CONTROL.DC_HPD_EN`, and HPD filter programming routes through GPIO/IRQ helpers that depend on the HPD filter fields.
6. HDMI/DP audio and packet paths use the DIG/DP/AFMT field tables to program audio packet timing, generic packets, metadata packets, MSA/VBID, secondary packets, and stream audio clocks.

Ordering rules are not encoded here. Callers must sequence HPD acknowledgment, AUX/DDC access, DP link training, FEC/scrambler/test pattern changes, stream enable/disable, FIFO reset, DSC PPS/GSP scheduling, MSA/VBID updates, metadata packet scheduling, HDMI packet double-buffer updates, and audio clock/packet programming according to hardware requirements.

## State And Persistence Behavior

The header stores no software state. It describes hardware state in DCN 3.2 display I/O blocks.

Hardware state represented here includes:

- HPD connection state, delayed sense state, interrupt latch/ack state, RX interrupt state, debounce timers, HPD enable state, and connect/disconnect filter delay configuration.
- DP stream state: link status, stream enable/status, pixel format, lane configuration, M/N generator state, MSA/VBID placement, TU/steer FIFO state, stream-disable interrupts, DPHY link-training/scrambler/FEC/CRC/test-pattern state, and fast-training state.
- DP secondary packet state: stream/global packet enables, GSP send requests and pending/active/deadline status, audio M/N programming and readbacks, packet framing/collision/audio mute status, metadata scheduling, DSC mode, VBID6 scheduling, MST rate and slot allocation, MSO enables, and ALPM/AUX-less ALPM sleep/wakeup state.
- DIG/HDMI/TMDS state: digital front-end source and mode selection, back-end HPD association, symbol-clock readbacks, FIFO reset/enable/calibration, output CRC/test pattern state, HDMI scrambling/deep-color/keepout/error status, ACR CTS/N values, audio/VBI/infoframe/generic-packet scheduling, double-buffer state, AFMT audio clock state, and TMDS control pattern/DC-balancer configuration.

Persistence is hardware-defined. Programming fields generally persist while the display block remains powered and until modeset/link reconfiguration, stream disable, power gating, suspend/resume, GPU reset, or driver teardown rewrites them. Status, pending, active, error, interrupt, ack, clear, and result fields can be live readback, sticky state, write-one-to-clear, or self-clearing controls depending on the register; this header only encodes bit positions and masks.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.2 register ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h` for matching register addresses.
- DCN32 component register-list macros that reference these symbols by exact generated names.
- Display Core register helpers that combine register offsets with shift/mask tables.
- Hardware-specific base offsets in `ctx->dcn_reg_offsets[]`.

Observed direct include and integration points for this header include:

- `display/dc/irq/dcn32/irq_service_dcn32.c` for HPD/HPD-RX interrupt routing, enable, ack, and status.
- `display/dc/gpio/dcn32/hw_factory_dcn32.c` and `display/dc/gpio/dcn32/hw_translate_dcn32.c` for DCN32 GPIO/HPD translation and pin setup.
- `display/dc/dio/dcn32/dcn32_dio_stream_encoder.h` and `.c` for DP/HDMI stream encoder register tables and runtime programming.
- `display/dc/dio/dcn32/dcn32_dio_link_encoder.c` plus inherited DCN10 link-encoder helpers for DIG/HPD/AUX interaction and link output control.
- `display/dc/resource/dcn321/dcn321_resource.c` and related DCN32-family resource files that instantiate stream encoders and pass register/shift/mask tables.
- Higher display paths for DP link training, MST, DSC, metadata, HDMI packet generation, audio/AFMT programming, hotplug handling, and diagnostic hardware-state logging.

## Risks And Edge Cases

- Wrong masks or shifts compile cleanly but can program the wrong hardware bits. High-risk fields include HPD interrupt ack/enable, `DP_VID_STREAM_ENABLE`, DPHY FEC/scrambler/training controls, FIFO reset/enable, DSC mode, GSP/PPS scheduling, metadata packet line scheduling, HDMI double-buffer controls, and audio/ACR fields.
- Chunk boundaries split related register families. `HPD0_DC_HPD_INT_STATUS` is incomplete at the start, and `DP1_DP_SEC_METADATA_TRANSMISSION` is incomplete at the end. A per-file report must not infer complete HPD0 or DP1 coverage from this chunk alone.
- Repeated `DP0` and `DP1` blocks look nearly identical. Instance-prefix mistakes can affect only one stream encoder and may only reproduce on specific connectors or pipes.
- HPD status and ack fields share interrupt-control/status flows. A stale or wrong mask can lose hotplug events, generate interrupt storms, or break HPD-RX/AUX interrupt handling.
- DP secondary packet fields mix send triggers, enable bits, pending/active readbacks, deadline-missed status, line-number programming, and double-buffer disables. Generic read-modify-write code can accidentally trigger sends, miss deadlines, or leave stale packets enabled.
- Metadata, DSC PPS, VBID6, and GSP line-number fields are timing-sensitive. Incorrect values can produce intermittent sink failures, missing HDR/Adaptive-Sync/DSC metadata, or mode-specific blanking.
- HDMI generic packet and double-buffer fields cover packets 0-14 with dense bit packing. Off-by-one field use can send the wrong infoframe or update it on the wrong frame.
- Fields such as `*_ACK`, `*_CLEAR`, `*_PENDING`, `*_STATUS`, `*_RESULT_VALID`, `*_ERROR`, and `*_INT` may have side effects or latch semantics not visible in the generated header.
- Full-width and high-bit masks use `L` suffix constants. Ad hoc consumers must keep the existing 32-bit register-helper conventions to avoid signedness or width surprises.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for DCN32/DCN321 display, IRQ, GPIO, stream-encoder, and link-encoder sources that include `dcn_3_2_0_sh_mask.h`.
- Generated-header consistency checks that every intended field has both `__SHIFT` and `_MASK`, masks align with shifts and field widths, and repeated `DP0`/`DP1` and `HPD0`-`HPD4` families match the hardware database where required.
- Diff checks against the authoritative DCN 3.2 register database and against `dcn_3_2_0_offset.h`, especially around the `HPD0` and `DP1_DP_SEC_METADATA_TRANSMISSION` chunk boundaries.
- Hardware hotplug tests on all HPD pins, including HPD-RX/AUX interrupt traffic, debounce/filter delay behavior, rapid connect/disconnect, suspend/resume, and interrupt ack/mask behavior.
- DP modeset and link-training tests covering lane-count changes, FEC, scrambler control, training/test patterns, stream enable/disable, FIFO reset, CRC readback, fast training, and embedded-panel modes.
- MST tests that exercise MSE rate programming, SAT update/status fields, slot counts, link timing, and source selection.
- DSC tests that enable/disable `DP_DSC_MODE`, verify PPS/GSP11 scheduling, and validate VBID6 line programming/readback.
- HDMI tests covering scrambling, deep color, ACR CTS/N programming for 32/44/48 kHz families, AVMUTE, audio packets, VBI packets, infoframes, generic packets 0-14, metadata packets, and double-buffer update status.
- Metadata and variable-refresh/HDR tests that verify DP metadata packet scheduling and HDMI metadata packet line/reference behavior across modeset, vblank updates, and stream disable.
- Diagnostic logging checks from stream-encoder state reads, including DSC mode, GSP11 PPS line/enable, VBID6 line/reference, and secondary stream enable state.
