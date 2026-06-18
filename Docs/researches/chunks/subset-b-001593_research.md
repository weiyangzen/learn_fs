# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 29882-32307

## Chunk Scope

Work item `subset-b-001593` covers line range 29882-32307 of `dcn_1_0_sh_mask.h`. This chunk is one slice of a generated AMD DCN 1.0 register shift/mask header. It contains 2164 `#define` entries and 254 register/comment markers for Display Core Next display I/O blocks:

- the tail of `DP_AUX5_AUX_GTC_SYNC_STATUS`
- the full `dce_dc_dio_dp_aux6_dispdec` / `DP_AUX6_*` AUX block
- the full `dce_dc_dio_dig0_dispdec` / `DIG0_*` stream encoder block
- the full `dce_dc_dio_dp0_dispdec` / `DP0_*` DisplayPort stream block
- the start of `dce_dc_dio_dig1_dispdec` / `DIG1_*`, through `DIG1_AFMT_CNTL`

The file is not handwritten control logic. It is generated hardware metadata: every register field has a `__SHIFT` value and a `__MASK` value used by AMDGPU display code to construct typed register-field tables and read/modify/write DCN display registers.

## Purpose

This chunk defines bit positions and bit masks for DCN 1.0 display AUX, DIG, HDMI/AFMT, TMDS, and DP register fields. The definitions let higher-level display code describe hardware fields symbolically, for example `DP0_DP_VID_STREAM_CNTL__DP_VID_STREAM_ENABLE_MASK` instead of open-coded constants.

The practical purpose is to keep register access code independent from raw bit positions while still compiling to constant masks. Display code uses these constants through macro-generated structs such as stream encoder masks/shifts and AUX engine masks/shifts. The chunk therefore acts as an ABI-like contract between driver source and the DCN 1.0 register layout.

## Important Macro Families

### `DP_AUX5_AUX_GTC_SYNC_STATUS`

The chunk starts mid-address-block with the final `DP_AUX5` GTC sync status definitions. Fields include:

- transaction completion/request state: `AUX_GTC_SYNC_DONE`, `AUX_GTC_SYNC_REQ`
- receive error status: timeout state, timeout, overflow, HPD disconnect, partial byte, non-AUX mode, min-count violation, invalid stop/start, invalid sync, invalid receive levels
- response accounting: `AUX_GTC_SYNC_REPLY_BYTE_COUNT`
- protocol outcome: `AUX_GTC_SYNC_NACKED`, `AUX_GTC_MASTER_REQ_BY_RX`

This continuation depends on earlier `DP_AUX5` GTC sync control/status definitions from the previous chunk. It is a read/status-oriented group and likely participates in diagnostics or GTC sync handling rather than normal software AUX transactions.

### `DP_AUX6_*`

The `dce_dc_dio_dp_aux6_dispdec` address block is fully represented. It defines the sixth AUX engine register field layout:

- `DP_AUX6_AUX_CONTROL`: enable, reset, reset-done, link-service read enable, update disable, HPD-disconnect ignore, mode-detect enable, HPD select, impedance calibration request, test/deglitch/spare bits.
- `DP_AUX6_AUX_SW_CONTROL`: software AUX transaction launch and write-byte count fields.
- `DP_AUX6_AUX_ARB_CONTROL`: arbitration priority, register access status, queued transaction inhibition, SW/DMCU ownership request and done bits. Some request and pending aliases intentionally share the same shift/mask.
- `DP_AUX6_AUX_INTERRUPT_CONTROL`: SW done, LS done, GTC sync lock done, and GTC sync error interrupt/ack/mask fields.
- `DP_AUX6_AUX_SW_STATUS` and `DP_AUX6_AUX_LS_STATUS`: transaction done/request status, receive timeout/error classifications, HPD disconnect, reply byte count, CP IRQ/update bits, and arbitration status.
- `DP_AUX6_AUX_SW_DATA` and `DP_AUX6_AUX_LS_DATA`: indexed byte data windows, including data direction and auto-increment disable for software AUX.
- `DP_AUX6_AUX_DPHY_*`: TX reference selection/rate/divider, TX precharge/config, RX window/threshold timing, TX/RX state, and measured half-symbol period fields.
- `DP_AUX6_AUX_GTC_SYNC_*`: error thresholds, lock acquisition status, error ack fields, controller state, and GTC sync transaction status.

These fields mirror the earlier AUX instances (`DP_AUX0` through `DP_AUX5`) and support driver code that treats AUX engines as an indexed register array. The sixth instance matters for systems exposing enough display links or internal AUX-capable ports to require `DP_AUX6`.

### `DIG0_*`

The `dce_dc_dio_dig0_dispdec` block describes digital stream encoder 0. It includes:

- Front-end encoder control: `DIG0_DIG_FE_CNTL` fields for start, output enable, source select, stereosync, TMDS color/pixel encoding, sync gating, and HDMI/VSync muxing.
- Diagnostics/test: output CRC control/result, clock/test/random patterns, FIFO status, FIFO error ack and calibration/min/max status.
- HDMI packet/control status: `HDMI_CONTROL`, `HDMI_STATUS`, audio packet control, ACR packet control, VBI packet control, infoframe control, generic packet controls, deep color, null/ACP/GC send, AVI/audio info send, and packet generator behavior.
- AFMT audio/generic packet register windows: interrupt status, ISRC packet payload registers, MPEG infoframe words, generic packet header/body registers 0-7, audio info, IEC 60958 channel status, audio CRC, ramp/test control, AFMT status, audio packet control, VBI packet conflict/lock/index, infoframe update/source, and audio source select.
- Back-end encoder and TMDS fields: `DIG_BE_CNTL`, `DIG_BE_EN_CNTL`, lane/symbol clocks, TMDS sync/control character generation, DC balancer, CTL bit generation, pattern output, feedback-path selectors, and lane enable.
- `DIG0_AFMT_VBI_PACKET_CONTROL1`: frame/immediate update and pending bits for generic packets 0-7.

Many of these `DIG0` fields are consumed directly by DCN 1.0 stream encoder register field lists. They drive HDMI/DP packetization, audio metadata, display stream startup, and test/diagnostic features.

### `DP0_*`

The `dce_dc_dio_dp0_dispdec` block describes DisplayPort stream/link registers for DP stream encoder 0:

- Stream/link setup: link training complete/status, embedded panel mode, pixel encoding/component depth/combine, lane count, video stream enable/status/deferred-disable.
- Main Stream Attribute data: colorimetry `MISC0`, `MSA_MISC`, timing parameter registers, VBID misc, and MSA timing overrides.
- Stream timing and rate generation: `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, link framing, stream FIFO reset/overflow/interrupt/ack, TU overflow ack, M/N double buffering and generator fields.
- PHY/link training: DPHY control, training pattern selection, symbol patterns, 8b/10b control, PRBS, scramble control, HBR2 eye pattern, CRC enable/control/result, MST CRC status, fast training control/status, bit-stream/symbol swap, and HBR2 pattern control.
- Secondary data/audio: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `DP_SEC_CNTL7`, `DP_SEC_FRAMING1` through `DP_SEC_FRAMING4`, audio N/M and readbacks, timestamps, packet control, VSC SDP controls, GSP packet enables and send/line fields, and PPS/metadata packet controls.
- MST/MSE scheduling: rate control/update, slot allocation tables `DP_MSE_SAT0..2`, status readbacks, link timing, misc control, and MSO control.
- Compression/database: DSC control, secondary control extensions, and `DP_DB_CNTL`.

This block supplies the mask/shift constants that stream encoder code uses for DisplayPort main-link activation, video M/N generation, secondary packet scheduling, audio transport, MST time-slot programming, and test CRC paths.

### `DIG1_*` Start

The final part begins the `dce_dc_dio_dig1_dispdec` block and mirrors the `DIG0` layout for stream encoder instance 1. It includes the same front-end, CRC/test, HDMI/AFMT/audio/generic packet, back-end, TMDS, lane-enable, and AFMT clock definitions through `DIG1_AFMT_CNTL`. The block continues in the next chunk with `DIG1_AFMT_VBI_PACKET_CONTROL1` and then `DP1_*`.

Because the stream encoder code usually defines field masks from `DIG0_*` and applies per-instance register offsets separately, `DIG1_*` constants are still important for generated completeness and any code path that refers to instance-specific register names directly.

## APIs, Types, and Functions

This chunk exports only C preprocessor constants. There are no structs, enums, functions, or runtime-visible symbols here.

The important "API" shape is the naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register.
- Some fields intentionally alias the same bit, such as `AUX_SW_USE_AUX_REG_REQ` and `AUX_SW_PENDING_USE_AUX_REG_REQ`, because the hardware presents different semantic names for write/request and read/pending views.

Consumers build compound accessors around these names. Relevant integration examples found in this tree include:

- `drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_stream_encoder.h`, where `SE_SF(reg_name, field_name, mask_sh)` expands register/field names into `.field_name = reg_name__field_name_MASK` or `_SHIFT` initializers.
- `drivers/gpu/drm/amd/display/dc/dce/dce_aux.h`, where `AUX_SF(...)` does the same for AUX engine field tables.
- `drivers/gpu/drm/amd/display/dc/dce/dce_aux.c`, where the resulting fields are used by `REG_UPDATE`, `REG_WAIT`, `REG_READ`, `REG_GET`, and raw status-bit checks.
- `drivers/gpu/drm/amd/display/dc/dce/dce_link_encoder.c` and `drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_link_encoder.c`, where AUX HPD selection, link-service-read enable, and encoder behavior are programmed.

## Control Flow

The header has no executable control flow. The effective runtime flow is indirect:

1. ASIC-specific DCN headers provide address macros and this shift/mask header.
2. Resource, link encoder, stream encoder, AUX, and IRQ service code instantiate per-generation register tables.
3. Driver operations call register helper macros such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_GET`, and `REG_WAIT`.
4. Those helpers use the mask/shift constants from this file to isolate or update individual register fields.
5. Hardware state changes in MMIO registers drive display behavior, AUX transaction completion, HDMI/DP packet transmission, interrupts, and status polling.

For AUX specifically, the control flow around this chunk is visible in `dce_aux.c`: software requests register ownership using `AUX_ARB_CONTROL`, resets/enables `AUX_CONTROL`, waits on `AUX_SW_STATUS.AUX_SW_DONE`, reads reply count and status/error masks, and classifies timeout/HPD/protocol failures. The `DP_AUX6_*` constants are the indexed sixth-instance equivalent of that flow.

For stream encoders, `dcn10_stream_encoder.h` maps `DIG0_*` and `DP0_*` field constants into field tables. Runtime stream encoder functions then program pixel format, stream enable, secondary-data packet enables, audio packet controls, MSA timing, and HDMI infoframes through register helper macros.

## State and Persistence Behavior

All state represented by this chunk lives in DCN hardware registers, not in kernel memory managed by this header. The masks name several categories of hardware state:

- Latched/acknowledged interrupt state: AUX SW/LS/GTC interrupt bits, FIFO overflow flags, HDMI/AFMT audio enable changes, DP steer/TU overflow flags, and generic packet conflict bits.
- Pollable readiness state: AUX reset done, AUX transaction done, AUX arbitration status, DP stream status, link-training status, fast-training status, FIFO calibration, AFMT audio clock status, and GTC sync lock state.
- Runtime configuration state: stream enable bits, pixel encoding/component depth, HDMI deep color/scrambling/null/audio/ACR packet controls, AFMT packet payload selection, DP M/N/timing fields, secondary-data packet enables, MST slot allocation, and TMDS generation settings.
- Indexed payload/data windows: AUX software/link-service data bytes and AFMT generic/audio/ISRC/MPEG packet payload registers.

Persistence is hardware-scoped. Values survive as long as the display engine retains register state, but can be reset by GPU reset, display controller reset, DCN power-gating, suspend/resume, or mode-set reprogramming. The driver must reinitialize relevant fields during link training, hotplug recovery, stream creation, audio enablement, and resume paths.

## Dependencies

This chunk depends on the broader generated register-header set:

- address macros such as `mmDIG0_*`, `mmDP0_*`, and `mmDP_AUX6_*` from matching DCN/DCE `*_d.h` headers
- register helper infrastructure in AMD display code that understands masks and shifts
- naming compatibility with field-list macros in DCN/DCE code
- hardware register layout for DCN 1.0 display I/O blocks

The constants also depend on consistent instance layout. `DP_AUX6`, `DIG0`, `DP0`, and `DIG1` are instance-specific generated names; driver code often treats only instance 0 names as the canonical field layout and relies on per-instance register addresses for different encoders or AUX engines. If a later ASIC changes a field layout, it needs a separate generation-specific mask header instead of reusing these constants.

## Integration Points

Important integration points visible from this chunk:

- AUX engine access and reset: `dce_aux.h`, `dce_aux.c`, `dce_link_encoder.c`, `dcn10_link_encoder.c`, and resource files that initialize AUX reset masks.
- DCN stream encoder setup: `dcn10_stream_encoder.h` uses `DIG0_*`, `DP0_*`, HDMI, AFMT, MSA, and DP secondary-data masks to build `dcn10_stream_encoder_shift` and `dcn10_stream_encoder_mask` tables.
- IRQ/service wiring: DCN interrupt service headers include the same generated mask file and can use interrupt/ack/mask fields to describe source behavior.
- DisplayPort behavior: DP0 masks support link training status, stream enable/disable, video timing M/N, secondary data packets, MST slot scheduling, DSC/PPS packet signaling, CRC/test paths, and embedded-panel state.
- HDMI/audio behavior: DIG0/DIG1 HDMI and AFMT masks support packet generator setup, ACR/audio clocking, audio channel status, generic infoframes, ISRC/MPEG packets, and audio FIFO/CRC status.
- TMDS/back-end behavior: DIG masks support HDMI/DVI TMDS control characters, DC balancing, lane enable, back-end source/mode selection, and dual-link/TMDS lane state.

## Risks and Failure Modes

- Wrong mask/shift values can silently corrupt adjacent fields during read/modify/write operations. For display registers that pack many one-bit flags, a single bad mask can alter unrelated interrupt, ack, stream-enable, or packet-send bits.
- Status and ack fields share registers with enable/control fields. Driver writes must preserve unrelated bits and use the intended write-one-to-ack semantics where applicable.
- Alias fields in `AUX_ARB_CONTROL` make semantic errors easy: request/pending names share masks, but software must know whether it is writing a request bit or reading a pending/status bit.
- AUX status interpretation depends on raw mask checks in addition to field helpers. If the masks for timeout, HPD disconnect, invalid stop/start, or reply byte count are wrong, AUX transactions may be retried, failed, or classified incorrectly.
- `DIG0` and `DIG1` mirror each other. Any generated drift between instances can break code that assumes uniform field layouts across stream encoder instances.
- DP secondary-data and MST fields coordinate multiple packet slots and update-pending flags. Incorrect masks can lead to stale metadata, missing audio/infoframes, broken MST bandwidth allocation, or PPS/DSC signaling issues.
- Hardware generation coupling is strict. These constants are only valid for the DCN 1.0 register map; applying them to later DCN generations can work for unchanged fields but is unsafe for fields that moved, widened, or changed semantics.

## Test Signals

Useful signals for validating this chunk and its consumers include:

- compile coverage of AMDGPU display code that includes `dcn_1_0_sh_mask.h`, especially DCN 1.0 stream encoder, AUX, link encoder, and IRQ service objects
- static checks that every field referenced by `SE_SF(...)`, `AUX_SF(...)`, and link encoder field lists has both `_MASK` and `__SHIFT` definitions
- AUX transaction tests on each physical AUX instance, including hotplug/disconnect, timeout, invalid reply, and reply-byte-count paths; the `DP_AUX6` instance should be tested on hardware exposing that engine
- display mode-set tests over DP and HDMI that verify stream enable/disable, link training, M/N timing generation, packet transmission, and audio enablement
- HDMI/DP audio tests for ACR values, IEC 60958 channel-status programming, audio clock enable/status, and audio FIFO overflow ack
- MST and secondary-data tests that exercise MSE slot allocation, SDP/GSP packet enables, update-pending behavior, and DSC/PPS metadata
- suspend/resume and GPU reset tests that confirm hardware registers are reprogrammed rather than relying on retained state
- debugfs or register-dump comparisons against vendor register specifications for representative fields such as `DP0_DP_VID_STREAM_CNTL`, `DP0_DP_SEC_CNTL*`, `DIG0_HDMI_CONTROL`, `DIG0_AFMT_VBI_PACKET_CONTROL1`, and `DP_AUX6_AUX_SW_STATUS`

## Cross-Chunk Notes

- The `DP_AUX5` group is only the tail of a larger AUX5 section that starts in the prior chunk.
- The `DIG1` block is incomplete here and continues in `subset-b-001594`, which should cover `DIG1_AFMT_VBI_PACKET_CONTROL1` and the following `DP1_*` block.
- Whole-file reconciliation should merge this chunk with neighboring chunks before drawing conclusions about complete DCN 1.0 register coverage or instance counts.
