# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_1_sh_mask.h lines 27726-30144

## Scope

This chunk is a generated AMD DCN 3.2.1 register field shift/mask header slice. It covers the tail of HPD0, HPD1-HPD4 hot-plug-detect blocks, all visible DP0 DisplayPort and DIG0 digital encoder field definitions, and the beginning of DP1 DisplayPort field definitions through `DP1_DP_ALPM_CNTL__DP_LINK_TRAINING_SWITCH_BETWEEN_VIDEO_MASK`. It defines C preprocessor constants only; there are no functions, structs, storage objects, or executable control flow in this chunk.

## Purpose

The constants provide the bit positions and bit masks used by AMD display driver register helpers to read, write, and compose DCN 3.2.1 hardware registers. Each hardware field appears as a pair of macros:

- `<REGISTER>__<FIELD>__SHIFT`, giving the least significant bit index.
- `<REGISTER>__<FIELD>_MASK`, giving the already-positioned register bit mask.

These macros are consumed indirectly by DCN 3.2.1 resource and hardware object constructors, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn321/dcn321_resource.c`, which includes both `dcn_3_2_1_offset.h` and this `dcn_3_2_1_sh_mask.h`. The resource code expands register-list macros into per-block register address tables plus shift/mask tables, then passes those tables into link encoder, stream encoder, VPG, AFMT, audio, and related constructors.

## Important Macro Families

- HPD registers: `HPD0_DC_HPD_CONTROL`, `HPD0_DC_HPD_FAST_TRAIN_CNTL`, `HPD0_DC_HPD_TOGGLE_FILT_CNTL`, and full `HPD1` through `HPD4` sets. The full HPD instances include interrupt status, interrupt control, connection/RX timers, enable bits, fast-training connect delays, AUX transmit enable, and toggle filter delays. These support connector hotplug sense, delayed sense, RX interrupt acknowledgment, HPD interrupt polarity, and filtering/debounce behavior.
- DP0 link core: `DP0_DP_LINK_CNTL`, `DP0_DP_PIXEL_FORMAT`, `DP0_DP_CONFIG`, `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_STEER_FIFO`, `DP0_DP_VID_TIMING`, `DP0_DP_VID_N`, `DP0_DP_VID_M`, `DP0_DP_LINK_FRAMING_CNTL`, and `DP0_DP_VID_INTERRUPT_CNTL`. These describe link training completion/status, lane count, video-stream enable/defer/status bits, transfer-unit and FIFO overflow reporting, video M/N generation, VBID/enhanced framing, and stream-disable interrupt control.
- DP0 DPHY and training: `DP0_DP_DPHY_CNTL`, `DP0_DP_DPHY_TRAINING_PATTERN_SEL`, `DP0_DP_DPHY_SYM0..2`, `DP0_DP_DPHY_8B10B_CNTL`, `DP0_DP_DPHY_PRBS_CNTL`, `DP0_DP_DPHY_SCRAM_CNTL`, CRC control/result/MST status registers, `DP0_DP_DPHY_FAST_TRAINING`, `DP0_DP_DPHY_FAST_TRAINING_STATUS`, `DP0_DP_DPHY_BS_SR_SWAP_CNTL`, and `DP0_DP_DPHY_HBR2_PATTERN_CONTROL`. These are the low-level DP PHY fields for FEC, scrambler, training patterns, test symbols, PRBS, CRC capture, MST CRC slot selection, fast-training state and completion interrupt/ack paths.
- DP0 secondary data packet and audio: `DP0_DP_SEC_CNTL`, `DP0_DP_SEC_CNTL1..7`, framing registers, audio `N`/`M` and readback registers, timestamp mode, packet control, metadata transmission, and GSP enable/send/active/deadline fields. These define the sideband/secondary packet machinery for audio stream packets, audio timestamping, generic secondary packets, ISRC, metadata/PPS-like packet sends, double-buffer disable bits, and send-active/send-in-idle status.
- DP0 MST/MSO: `DP0_DP_MSE_RATE_CNTL`, `DP0_DP_MSE_RATE_UPDATE`, `DP0_DP_MSE_SAT0..2`, `DP0_DP_MSE_SAT*_STATUS`, `DP0_DP_MSE_SAT_UPDATE`, `DP0_DP_MSE_LINK_TIMING`, `DP0_DP_MSE_MISC_CNTL`, `DP0_DP_MSO_CNTL`, and `DP0_DP_MSO_CNTL1`. These fields drive Multi-Stream Transport allocation, source IDs, encryption flags, slot counts, rate X/Y, SAT update pending/status, MSO secondary packet enables, and link timing fields.
- DP0 panel power behavior: `DP0_DP_ALPM_CNTL` and `DP0_DP_AUXLESS_ALPM_CNTL1..5` describe link PHY sleep/standby sends, pending bits, line/pattern counts, AUX-less ALPM enable/control, detected-sleep/standby states, IRQ mask/status/clear fields, and frame/line coordinates for wake events.
- DIG0 digital encoder: `DIG0_DIG_FE_CNTL`, output CRC control/result, test and random pattern registers, FIFO controls, metadata packet control, HDMI control/status/audio/ACR/VBI/infoframe/generic packet controls, HDMI double-buffer controls, AFMT, back-end enable/control, TMDS control-character/sync/DC-balance/generator controls, DIG version, and forced disable. These fields back HDMI/TMDS/DVI-style output setup, CRC/test-pattern diagnostics, packet generator scheduling, deep color/scrambling, AVMUTE/status/error handling, generic packet immediate sends, and digital front-end/back-end routing.
- DP1 beginning: the DP1 register set mirrors DP0 for link, video, DPHY, secondary packets, MST/MSO, double-buffering, metadata, and ALPM until the chunk ends at the early masks for `DP1_DP_ALPM_CNTL`. The visible DP1 definitions are structurally aligned with DP0 and are instance-specific for the second DIO DP block.

## Control Flow and Data Flow

This header has no runtime branches or calls. Its behavior is compile-time token substitution into AMD display register-helper call sites. The data flow is:

1. `dcn321_resource.c` includes this shift/mask header and the matching offset header.
2. Register-list initialization macros in resource and hardware-object code concatenate register and field names into constants such as `DP0_DP_DPHY_CNTL__DPHY_FEC_EN_MASK` or `DIG0_HDMI_CONTROL__HDMI_DEEP_COLOR_DEPTH__SHIFT`.
3. Constructors populate hardware-object tables, for example `link_enc_hpd_regs`, `link_enc_regs`, `stream_enc_regs`, `vpg_regs`, `afmt_regs`, and their shift/mask companions.
4. Runtime helpers such as `REG_GET`, `REG_SET`, `REG_SET_2`, `generic_reg_get`, and related AMD display macros use the precomputed shift/mask values to preserve unrelated bits while extracting or updating a field in memory-mapped DCN registers.

Important integration examples visible from nearby code include `dcn321_link_encoder_construct`, which receives link, AUX, HPD, shift, and mask tables; `dcn321_stream_encoder_create`, which passes stream encoder registers plus VPG/AFMT instances into `dcn32_dio_stream_encoder_construct`; and HPD setup paths that use the HPD masks through the link encoder function table for enable, disable, state read, and filter programming.

## State and Persistence Behavior

The file itself has no mutable state and persists no data. It encodes hardware state layout: using a macro against a live register may change or observe persistent hardware state in the GPU display engine. Relevant state surfaces in this chunk include HPD interrupt latch/ack bits, DP stream enable/status, FIFO and TU overflow flags, DPHY CRC result-valid/result bytes, fast-training complete/ack bits, MST allocation table status, secondary packet send-pending/deadline-missed flags, double-buffer pending/taken/lock/disable bits, HDMI packet/status/error bits, and ALPM sleep/standby pending/status/interrupt bits.

Because many fields are status or acknowledge fields, read/write semantics come from the hardware register specification and caller code, not from this header. A mask typo can therefore cause durable hardware misprogramming even though the header is syntactically passive.

## Dependencies and Integration Points

- Depends on the matching DCN 3.2.1 offset header for register addresses; the shift/mask macros are meaningful only when paired with the same-generation register offsets.
- Depends on AMD display register helper conventions in `reg_helper.h` and hardware object code that expects field names to be available through token concatenation.
- Integrates with DCN 3.2.1 resource construction in `display/dc/resource/dcn321/dcn321_resource.c`, which includes this header and constructs resource-specific register/shift/mask tables.
- Integrates with DIO link encoder code, including HPD operations, DP output enable, MST allocation, FEC control, DIO PHY mux, and DP fast-training support through `dcn321_dio_link_encoder.c` and inherited `dcn10/dcn20/dcn31/dcn32` helpers.
- Integrates with stream encoder, AFMT, VPG, audio, HDMI packet generation, secondary data packets, and TMDS output programming because DIG0/DP0/DP1 masks feed the corresponding constructor tables.
- Generated constants are intentionally duplicated by instance (`DP0`, `DP1`, `DIG0`, `HPD1` etc.) rather than parameterized at runtime. This matches the hardware-register naming model and allows the macro layer to build static per-instance tables.

## Risks

- Offset/header mismatch: using this `dcn_3_2_1_sh_mask.h` with another ASIC generation's offset header can silently write the wrong fields.
- Bitfield drift: generated values for fields such as `DPHY_FEC_EN`, `DP_SEC_GSP*_SEND`, `HDMI_DEEP_COLOR_DEPTH`, `DP_MSE_SAT_SLOT_COUNT*`, or HPD ack/status bits are hardware ABI. One incorrect shift or mask can break link training, hotplug detection, MST bandwidth allocation, HDMI packet scheduling, or ALPM wake behavior.
- Acknowledge and status fields are easy to misuse because names like `_ACK`, `_CLEAR`, `_PENDING`, and `_STATUS` appear side by side. The header does not encode write-one-to-clear or read-only semantics.
- Repeated instance blocks invite copy/paste or generator errors. DP1 mostly mirrors DP0, and HPD1-HPD4 mirror one another; a single instance-specific anomaly must be intentional and checked against hardware source data.
- The chunk begins in the middle of HPD0 definitions and ends in the middle of `DP1_DP_ALPM_CNTL`, so final per-file reconciliation must combine adjacent chunks before making whole-file claims about completeness.

## Test Signals

- Compile coverage is the first signal: any renamed/missing field macro breaks builds in DCN 3.2.1 resource or DIO object initialization because token concatenation cannot resolve the constants.
- Register-table construction review: ensure `dcn321_resource.c` still compiles when it includes `dcn_3_2_1_offset.h` and this header, and that HPD, link encoder, stream encoder, AFMT, VPG, and audio constructor tables receive the expected shift/mask structures.
- Runtime display smoke tests should include HPD plug/unplug detection, DP link training, DP MST stream allocation, HDMI output with deep color/scrambling as applicable, audio/secondary packet transmission, panel self-refresh or fast-training paths, and ALPM entry/exit on supported panels.
- Diagnostic tests can exercise output CRC and DPHY CRC fields, FIFO/TU overflow flags, HDMI packet error status, generic packet send-pending bits, and fast-training completion/ack fields to catch field-position mistakes.
- Cross-generation diffing against adjacent generated headers such as DCN 3.2.0/3.5.1 is useful for detecting accidental generator regressions, but differences must be validated against DCN 3.2.1 register specifications rather than assumed wrong.

## Chunk Boundaries

This report is intentionally limited to lines 27726-30144. It does not summarize the entire source file. The merge/reconciliation lane should combine this with neighboring chunk reports for the final per-file research document.
