# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h lines 17563-19999

## Purpose

This chunk is part of AMDGPU Display Core's generated DCN 2.0.1 register shift/mask header. It contains no executable C logic; it publishes preprocessor constants that describe bit positions and already-positioned masks for fields inside DCN display, link, PHY, DCIO, DDC, and HPD registers.

The covered range is the DIO/link-encoder tail of display instance 0, a full DP0 block, most of DIG1/DP1, and the beginning of DCIO GPIO/pinstrap metadata:

- The chunk starts in the middle of `DIG0_TMDS_CTL2_3_GEN_CNTL`, then completes `DIG0` version, lane-enable, AFMT audio-clock, AFMT VBI generic-packet update, and HDMI generic immediate-send fields.
- It defines the `DP0` DisplayPort link/stream block, including link status, pixel format, MSA metadata and timing, video stream enable/status, FIFO overflow reporting, DPHY training/test/CRC/scrambler controls, secondary-data and audio packet controls, MST/MSE allocation/status, DSC controls, metadata packet transmission, VBID misc fields, and data-bypass controls.
- It defines the `DIG1` digital encoder block, including front-end/back-end controls, output CRC, HDMI packet scheduling, HDMI audio/status/control, AFMT audio/infoframe/generic/ISRC/MPEG fields, TMDS control-symbol generation, lane enable, AFMT clock control, and generic-packet update/send controls.
- It defines the matching `DP1` DisplayPort block with the same broad register families as `DP0`, including DSC and metadata transmission fields.
- It begins DCIO-level register definitions for `DC_GENERICA`, `UNIPHYA`, `UNIPHYB`, `DC_PINSTRAPS`, `DCIO_CLOCK_CNTL`, DDC1/DDC2 GPIO registers, and the start of `DC_GPIO_HPD_MASK`.

Each hardware field appears through paired macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's low bit.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register position.

Driver code combines these constants with register-address macros from `dcn_2_0_1_offset.h` and with Display Core register helper macros such as `FN`, `FD`, `HWS_SF`, `SE_SF`, and `REG_UPDATE`-style helpers.

Although this source tree is under a `ceph-client` mirror path, this chunk is AMD GPU display hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, networking, or storage persistence.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or storage objects in this chunk. The API surface is the macro namespace consumed by DCN201 resource tables and common display hardware blocks.

Important `DIG0` groups in this range are:

- `DIG0_TMDS_CTL2_3_GEN_CNTL`: control-symbol data selection, delay, inversion, modulation, feedback path, feedback sync, and pattern output for TMDS control lanes 2 and 3. The chunk begins after the first lines of this register, so adjacent chunk context is needed for the complete register.
- `DIG0_DIG_VERSION` and `DIG0_DIG_LANE_ENABLE`: digital encoder type and lane/clock enable bits.
- `DIG0_AFMT_CNTL`: AFMT audio clock enable/status.
- `DIG0_AFMT_VBI_PACKET_CONTROL1`: frame and immediate update controls plus pending bits for AFMT generic packets 0 through 7.
- `DIG0_HDMI_GENERIC_PACKET_CONTROL5`: immediate-send and pending bits for HDMI generic packets 0 through 7.

The `DP0_*` and `DP1_*` register families describe DisplayPort stream encoders for two hardware instances. Major groups include:

- Link and stream control: `DP_LINK_CNTL`, `DP_CONFIG`, `DP_VID_STREAM_CNTL`, `DP_STEER_FIFO`, `DP_LINK_FRAMING_CNTL`, and `DP_VID_INTERRUPT_CNTL`.
- Pixel and main-stream attributes: `DP_PIXEL_FORMAT`, `DP_MSA_COLORIMETRY`, `DP_MSA_MISC`, `DP_VID_TIMING`, `DP_VID_N`, `DP_VID_M`, `DP_VID_MSA_VBID`, `DP_MSA_TIMING_PARAM1` through `PARAM4`, and `DP_MSA_VBID_MISC`.
- DPHY training and diagnostics: `DP_DPHY_CNTL`, `DP_DPHY_TRAINING_PATTERN_SEL`, `DP_DPHY_SYM0` through `SYM2`, `DP_DPHY_8B10B_CNTL`, `DP_DPHY_PRBS_CNTL`, `DP_DPHY_SCRAM_CNTL`, CRC enable/control/result/MST status, fast-training controls/status, bit/serializer swap controls, HBR2 eye/pattern controls, and test-pattern fields.
- Secondary-data and audio packet controls: `DP_SEC_CNTL`, `DP_SEC_CNTL1` through `CNTL7`, `DP_SEC_FRAMING1` through `FRAMING4`, `DP_SEC_AUD_N/M` programming and readback, `DP_SEC_TIMESTAMP`, `DP_SEC_PACKET_CNTL`, and `DP_SEC_METADATA_TRANSMISSION`.
- MST/MSE programming: `DP_MSE_RATE_CNTL`, `DP_CP_MSE_STATUS`, `DP_MSE_RATE_UPDATE`, `DP_MSE_SAT0` through `SAT2`, `DP_MSE_SAT_UPDATE`, `DP_MSE_LINK_TIMING`, `DP_MSE_MISC_CNTL`, and `DP_MSE_SAT*_STATUS`.
- Compression and bypass: `DP_DSC_CNTL`, `DP_DSC_BYTES_PER_PIXEL`, and `DP_DB_CNTL`.

The `DIG1_*` groups describe the second digital/HDMI/TMDS stream encoder instance. They include front-end fields such as source select, pixel encoding, color format, stereosync, Dolby Vision, CRC/test patterns, FIFO status, HDMI metadata/generic/infoframe/audio/ACR controls, AFMT audio and IEC 60958 status fields, audio CRC/ramp/status fields, back-end enable/control fields, TMDS control character and DC-balancer fields, and AFMT/HDMI generic packet scheduling.

The DCIO groups at the end of the chunk include:

- `DC_GENERICA`: generic DCIO scratch/control payload fields.
- `UNIPHYA_LINK_CNTL` and `UNIPHYB_LINK_CNTL`: pixel-valid reset, minimum low duration, channel inversion, lane stagger, HPD mask, and pixel-frequency-change fields for the two UNIPHY links.
- `UNIPHYA_CHANNEL_XBAR_CNTL` and `UNIPHYB_CHANNEL_XBAR_CNTL`: lane crossbar source selections and link enable bits.
- `DC_PINSTRAPS`: hardware strap fields for SMS enable, audio availability, clock-controller bypass, and display connectivity.
- `DCIO_CLOCK_CNTL`: DCIO display-clock gate disable.
- `DC_GPIO_DDC1_*` and `DC_GPIO_DDC2_*`: DDC clock/data mask, pull-down, receive, AUX pad mode/polarity, hardware pull-down enable, drive-strength, output value, output enable, and input readback fields.
- `DC_GPIO_HPD_MASK`: HPD1-HPD6 mask, pull-disable, receive, and RX HPD selection fields. The chunk ends before `DC_GPIO_HPD_MASK` is complete.

Generated names that end in `MASK_MASK`, such as `DC_GPIO_DDC1_MASK__DC_GPIO_DDC1CLK_MASK_MASK`, are expected. The first `MASK` belongs to the hardware register/field name; the final `_MASK` is the generated mask-constant suffix.

## Control Flow

This header range has no runtime control flow. It is compile-time register metadata. Runtime behavior is created by code that chooses an instance, combines the offset and shift/mask tables, and performs MMIO reads or writes through Display Core helpers.

A typical DCN201 flow is:

1. `dcn201_resource.c`, `dcn201_clk_mgr.c`, or `irq_service_dcn201.c` includes `dcn/dcn_2_0_1_offset.h` and this shift/mask header.
2. Register-list macros instantiate per-block register tables for stream encoders, link encoders, audio engines, AUX/I2C/HPD, DIO, clock manager, and IRQ services.
3. Constructors such as `dcn20_stream_encoder_construct()`, `dcn201_link_encoder_construct()`, `dce_audio_create()`, `dcn10_dio_construct()`, and `dcn2_i2c_hw_construct()` receive address tables plus shift/mask tables.
4. Higher-level Display Core code performs modeset, link training, packet programming, audio setup, HPD/AUX/DDC handling, DSC setup, MST allocation, and clock/strap reads.
5. Hardware helpers encode or decode fields using these constants and issue register reads or writes.

Control-sensitive hardware actions represented by this chunk include enabling/disabling DIG lanes and clocks, scheduling AFMT/HDMI generic packets, enabling DP video streams, deferring DP stream disable, polling stream/link status, acknowledging DP FIFO overflows, programming MSA timing and VBID fields, selecting DP training and test patterns, enabling/disabling scrambling or CRC capture, programming secondary-data/audio packets, updating MST allocation tables, enabling DSC, selecting DDC/AUX pad behavior, reading HPD/DDC inputs, and changing UNIPHY lane routing/link state.

The macros do not encode legal values, access type, reset values, lock timing, or sequencing. Consumers must know when fields are writable, read-only, sticky, write-one-to-clear, self-clearing, double-buffered, or safe to change only during blanking/link-training windows.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes state held in DCN 2.0.1 display hardware registers.

Hardware state represented by this chunk includes:

- Digital encoder state: lane enables, DIG type, TMDS control-symbol generation, feedback and DC-balance behavior, FIFO status, output CRC/test-pattern state, front-end source/color/stereo state, and back-end enable state.
- HDMI/AFMT state: HDMI control/status, audio-packet and ACR controls, AVI/VBI/generic/infoframe scheduling, metadata packet control, AFMT audio clock, ISRC/MPEG/audio-infoframe payloads, IEC 60958 fields, audio CRC, ramp controls, packet update pending bits, and immediate-send pending bits.
- DisplayPort link and stream state: link-training complete/status, embedded-panel mode, lane count, pixel encoding/depth/combine, stream enable/status, MSA metadata/timing, video `M/N`, VBID, interrupt controls, framing, FIFO overflow flags, DPHY training/test/scrambler/PRBS/CRC status, secondary-data packet enable/update state, audio `N/M` values and readbacks, timestamp mode, metadata packet state, DSC mode/slice width/bytes-per-pixel, data-bypass disable, and MST/MSE allocation/status registers.
- DCIO/PHY state: UNIPHY channel inversion, lane stagger, crossbar lane mapping, link enable, pixel-valid reset, clock-gate override, generic DCIO scratch/control fields, and display strap readbacks.
- Connector GPIO state: DDC1/DDC2 clock/data output enables, output values, input readbacks, pad pull-downs, AUX pad mode/polarity, drive strength, hardware pull-down control, and HPD mask/pull-disable/receive status for HPD1-HPD6.

Persistence is hardware-specific. Programmed control fields generally persist until rewritten, display block reset, power gating, suspend/resume, or ASIC reset. Status fields reflect live hardware. Pending and immediate-send bits can be transient or self-clearing. FIFO overflow, CRC, interrupt, and status/ack fields may be sticky until explicitly cleared or acknowledged. Strap and fuse-like fields are usually read as board/ASIC configuration and should not be treated as mutable software state.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0.1 register-header contract:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_offset.h` supplies the matching `mm...` register addresses and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_1_sh_mask.h` supplies the field layouts, including this chunk.
- Display Core `reg_helper.h` and common register macros fold offset/shift/mask constants into typed resource tables.

Observed local include points for this mask header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn201/dcn201_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn201/irq_service_dcn201.c`

`dcn201_resource.c` is the main integration point for this range. It includes the offset and mask headers, defines stream encoder, link encoder, audio, AUX, HPD, I2C, DIO, and hardware-sequencer register tables, and creates DCN201 resources. The code also reads `DC_PINSTRAPS__DC_PINSTRAPS_AUDIO` through `generic_reg_get()` when populating resource straps.

The chunk's `DIG0`/`DIG1`, HDMI, AFMT, DP, DSC, and metadata fields integrate with stream encoder construction via `dcn20_stream_encoder_construct()`. The `UNIPHYA`/`UNIPHYB`, HPD, and AUX-related fields integrate with link encoder construction via `dcn201_link_encoder_construct()`. The `DC_GPIO_DDC*` fields integrate with hardware I2C/DDC creation through `dcn2_i2c_hw_construct()`. HPD fields also connect to IRQ source mapping and HPD acknowledgement logic in the DCN201 IRQ service.

The `DP0` and `DP1` register families are user-visible through display features: DP/eDP link training, MST, DSC, HDR/metadata secondary packets, audio, DP color format selection, stream enable/disable, and diagnostics. HDMI/TMDS and AFMT families are user-visible through HDMI video mode set, infoframes, generic packets, audio, ACR/N/CTS programming, and output CRC/test behavior.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. A bad shift or mask compiles successfully but can update the wrong bit, fail to update the intended field, corrupt adjacent fields during read-modify-write, or decode status incorrectly.

High-risk areas in this chunk include:

- Repeated instance layout. `DIG0`/`DP0` and `DIG1`/`DP1` use similar field families, and many consumers build tables by macro expansion. A prefix, instance, or lane mismatch can affect only one physical stream encoder or connector path and may be hard to reproduce.
- Chunk boundaries. The range starts in the middle of `DIG0_TMDS_CTL2_3_GEN_CNTL` and ends in the middle of `DC_GPIO_HPD_MASK`. Whole-file conclusions must merge adjacent chunks before treating either register as complete.
- Packet scheduling and pending bits. AFMT, HDMI generic, DP secondary-data, metadata, and VBI controls include frame-update, immediate-update, send, and pending fields. Incorrect handling can drop HDR metadata, AVI/audio/infoframe packets, ISRC/MPEG payloads, or generic packets.
- DP link and stream sequencing. `DP_VID_STREAM_ENABLE`, deferred disable, link-training status, MSA/VBID, `M/N`, DPHY training pattern, scrambler, PRBS, CRC, and FIFO overflow fields are timing-sensitive. Wrong constants can cause blank displays, failed link training, compliance-test failures, flicker, or incorrect diagnostics.
- MST/MSE state. SAT table fields, rate updates, link timing, and MSE status must align with stream allocation logic. Bad masks can misallocate MST bandwidth or report the wrong slot status.
- DSC fields. `DP_DSC_CNTL` and `DP_DSC_BYTES_PER_PIXEL` influence compressed stream transport. Incorrect field values can break high-bandwidth modes or produce sink-side decode failure.
- Audio fields. AFMT clocks, HDMI/DP audio packet controls, ACR programming, and audio `N/M` fields are sensitive to pixel clock and link configuration. Bad constants can produce missing audio, rate mismatch, or unstable audio after modeset/resume.
- GPIO/DDC/HPD side effects. DDC output enables, pull-downs, AUX pad modes, HPD masks, and receive fields are connector-facing. Incorrect writes can break EDID reads, AUX transactions, hotplug detection, or HPD RX handling.
- Status and clear semantics. Fields named `ACK`, `CLEAR`, `PENDING`, `STATUS`, `READBACK`, and `RESULT` should not be blindly read-modify-written without knowing whether they are sticky, self-clearing, or write-one-to-clear.
- Full-width and high-bit masks. Several fields use broad masks, including high bits such as HPD receive fields and packet-control bitmaps. Consumers should use unsigned 32-bit register helpers to avoid signedness or width surprises.

Reserved or generic fields such as `DC_GENERICA` should remain conservative unless backed by ASIC documentation or existing driver behavior. The generated header does not distinguish reserved, read-only, write-only, or firmware-owned fields.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Kernel/driver build coverage for DCN201 paths that include `dcn_2_0_1_sh_mask.h`, especially resource, clock-manager, IRQ, stream encoder, link encoder, audio, DIO, I2C, AUX, and HPD code.
- Generated-header checks that every field has matching `__SHIFT` and `_MASK` definitions, masks align to shifts, and repeated instance families are consistent across `DIG0`/`DIG1` and `DP0`/`DP1`.
- Diff validation against AMD's authoritative DCN 2.0.1 register database and the companion `dcn_2_0_1_offset.h`.
- HDMI/TMDS modeset tests that exercise lane enable, TMDS control-character generation, HDMI infoframes/generic packets, metadata packets, AFMT audio clocking, ACR/N/CTS, audio packet controls, and output CRC/test paths.
- DisplayPort/eDP tests for link training, video stream enable/disable, pixel encoding/depth/combine, MSA timing, VBID, `M/N`, scrambler, PRBS, training patterns, HBR2/TPS patterns, and link/status readback.
- MST tests that verify MSE rate programming, SAT0/SAT1/SAT2 allocation, update sequencing, link timing, and SAT status readback across multiple streams.
- DSC tests for compressed DP modes, including slice width, bytes-per-pixel programming, and interaction with metadata/secondary packets.
- HDR/metadata and infoframe tests that confirm DP secondary metadata and HDMI metadata/generic packets are sent on the expected lines and remain stable across modeset, fast update, and resume.
- Audio tests for HDMI and DP that verify AFMT clock state, packet generation, ACR status, and DP audio `N/M` programming/readback.
- AUX/DDC/HPD tests that cover EDID reads on DDC1/DDC2, AUX pad mode/polarity, hotplug mask/receive behavior, HPD IRQ acknowledgement, HPD RX interrupt paths, and suspend/resume reconnect behavior.
- Stress tests around hotplug, link retraining, runtime power management, suspend/resume, MST topology changes, DSC enable/disable, and repeated modesets, watching for blank displays, flicker, missing audio, bad EDID reads, incorrect HPD events, and stuck pending/status bits.

## Cross-Chunk Notes

This source slice is artificially bounded. Earlier chunks contain the beginning of `DIG0_TMDS_CTL2_3_GEN_CNTL` and preceding `DIG0` HDMI/TMDS fields. Later chunks complete `DC_GPIO_HPD_MASK` and continue with HPD output/enable/readback fields and the rest of the DCN 2.0.1 register-mask header. The final per-file report should merge this chunk with neighboring chunks before summarizing complete DIG0, HPD, GPIO, and DCIO behavior.
