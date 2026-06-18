# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 44550-46976

## Scope And Purpose

This chunk is generated AMD DCN 2.0 register field metadata. It contains no executable C logic. Its purpose is to publish compile-time bit shifts and masks for DCN 2.0 digital display encoder (`DIG`) and DisplayPort (`DP`) MMIO registers so AMDGPU display code can compose, update, and decode register fields without hard-coded bit positions.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The covered range is a DIO/display-decoder slice:

- Tail of `DIG3`: TMDS control/generation fields, DIG lane/audio-clock controls, AFMT generic packet update state, HDMI generic immediate-send state, and force-disable.
- Full `DP3`: DisplayPort link, video, DPHY, secondary-data/audio, MST/MSE, MSO, DSC, metadata, double-buffer, VBID, and ALPM field definitions.
- Full `DIG4`: stream encoder/front-end fields, HDMI metadata/generic/audio/infoframe/ACR/GC fields, AFMT audio and generic infoframe payload fields, back-end and TMDS fields, lane/audio controls, and force-disable.
- Full `DP4`: another repeated DisplayPort instance with the same field surface as `DP3`.
- Beginning of `DIG5`: only the first `DIG5_DIG_FE_CNTL` shifts/masks for source selection, stereo sync, start, bypass/input pixel selection, Dolby Vision state, symbol clock, and TMDS pixel/color format. The rest of `DIG5` continues in the next chunk.

Every register field appears as a pair of preprocessor definitions: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position of a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Instance-qualified register prefixes (`DIG3`, `DP3`, `DIG4`, `DP4`, and partial `DIG5`) let common stream/link encoder code bind the same generic field names to one hardware encoder instance.

Important macro families in this chunk:

- `DIG3_TMDS_*` and `DIG4_TMDS_*`: HDMI/DVI TMDS synchronization, control characters, feedback selection/delay, stereo sync selection, sync character patterns, per-control-bit output selection/delay/invert/modulation, DC balancer controls, and 2-bit counter enable.
- `DIG3_DIG_VERSION`, `DIG3_DIG_LANE_ENABLE`, `DIG4_DIG_VERSION`, and `DIG4_DIG_LANE_ENABLE`: DIG type, lane enables, and DIG clock-enable bits used by link encoder setup and enable/disable logic.
- `DIG3_AFMT_CNTL`, `DIG4_AFMT_CNTL`, `DIG3_AFMT_VBI_PACKET_CONTROL1`, and `DIG4_AFMT_VBI_PACKET_CONTROL1`: audio formatter clock enable/status plus per-generic-packet frame/immediate update and pending bits for generic packet slots 0-7.
- `DIG3_HDMI_GENERIC_PACKET_CONTROL5` and `DIG4_HDMI_GENERIC_PACKET_CONTROL5`: immediate-send and pending bits for HDMI generic packet slots 0-7.
- `DIG4_DIG_FE_CNTL` and partial `DIG5_DIG_FE_CNTL`: stream source select, stereo sync select/gating, DIG start, bypass/input pixel selection, Dolby Vision enable/missed metadata, front-end symbol-clock status, and TMDS pixel encoding/color format.
- `DIG4_DIG_OUTPUT_CRC_*`, `DIG4_DIG_CLOCK_PATTERN`, `DIG4_DIG_TEST_PATTERN`, `DIG4_DIG_RANDOM_PATTERN_SEED`, and `DIG4_DIG_FIFO_STATUS`: output CRC, clock/test pattern, pseudo-random seed, and FIFO diagnostic fields.
- `DIG4_HDMI_*`: HDMI metadata packet line/reference/enable fields, generic packet line/send/continue controls, HDMI enable/status/deep-color/packing/scrambler settings, audio sample layout and HBR packet controls, ACR select/enable/CTS/N, VBI packet enables, AVI/audio/MPEG infoframe update controls, GC fields, and double-buffer status/clear/lock fields.
- `DIG4_AFMT_*`: audio packet/channel layout controls, ISRC fields, MPEG/HDR/generic packet header/body bytes, IEC 60958 channel status fields, ramp controls, AFMT audio CRC controls/results, AFMT status flags, generic packet control/index/conflict bits, and audio source selection.
- `DIG4_DIG_BE_CNTL` and `DIG4_DIG_BE_EN_CNTL`: back-end dual-link/swap/RB switch, front-end source selection, DIG mode, HPD select, enable, and back-end symbol-clock status.
- `DP3_*` and `DP4_*`: repeated DisplayPort instance fields covering link-training completion/status, embedded panel mode, pixel format/depth/combine, MSA colorimetry/misc/VBID/timing parameters, lane count, stream enable, steer FIFO, video timing N/M, link framing, HBR2 eye pattern, interrupts, DPHY training/test/scrambler/CRC/FEC-related diagnostics, fast training, secondary-data packet controls, audio M/N/readback/timestamp, MST/MSE rate and slot allocation, MSO, DSC mode/slice width/bytes per pixel, generic secondary packet send/line scheduling, double-buffer lock/taken/pending state, metadata transmission, and ALPM sleep/standby scheduling.

## Control Flow

This chunk has no runtime control flow. It is declarative metadata consumed by register-table construction and register helper macros such as `SRI`, `SE_SF`, `LE_SF`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT`.

Representative runtime flows in local consumers:

1. DCN20 resource construction includes `dcn_2_0_0_sh_mask.h` and binds these shifts/masks into stream encoder, link encoder, clock, GPIO, IRQ, and DMUB resource tables.
2. DCE/DCN stream encoder code maps `DIG{id}` AFMT/HDMI/DIG front-end registers and `DP{id}` secondary-data registers through `SE_DCN2_REG_LIST(id)` and `SE_COMMON_MASK_SH_LIST_DCN20(mask_sh)`. `enc2_stream_encoder_update_hdmi_info_packets()` writes HDMI generic packet fields, while DSC, dynamic metadata, Dolby Vision, audio clock, GSP/PPS, and DP secondary-data helpers use the DP/DIG fields defined here.
3. Link encoder code maps back-end and DP link fields through `LINK_ENCODER_MASK_SH_LIST_DCN10(mask_sh)` and DCN20 extensions. It uses these masks for DIG enable, HPD select, DIG mode, front-end selection, TMDS clock/control bits, DPHY training/test/scrambler fields, link framing, DP stream enable, lane count, MST slot allocation, and hotplug/AUX-related setup.
4. Audio formatter and HDMI/DP audio code programs AFMT audio source, channel layout, IEC 60958 channel-status fields, DP audio secondary packets, ACR N/CTS, HBR packet enables, and audio CRC/status fields.
5. Diagnostic paths use output CRC, DPHY CRC, FIFO status, MSE status, fast-training status, double-buffer status, missed metadata, and deadline-missed/pending fields to validate or debug link and stream behavior.

Because the header only supplies constants, it does not enforce sequencing. Consumers must order operations around link training, DIG front-end/back-end routing, HDMI/DP packet memory conflicts, AFMT clock enable, DP secondary packet scheduling, DSC enablement, MST slot updates, double-buffer locks, ALPM requests, and reset/power/clock transitions.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe hardware MMIO state.

The represented hardware state includes:

- Stream routing and front-end state: source select, stereo sync, DIG start, bypass/input pixel select, Dolby Vision enable/missed-metadata flag, symbol-clock state, and TMDS encoding/color-format state.
- Link/back-end state: DIG enable, HPD select, DIG mode, front-end source binding, lane enables, lane count, link-training completion/status, embedded-panel mode, and DP stream enable.
- HDMI/TMDS state: HDMI enable, deep color, packing phase, scrambler/clock ratio, generic packet line/send/continue/immediate flags, metadata packet scheduling, VBI/infoframe update bits, ACR parameters, audio sample/HBR controls, guard band/control period settings, and TMDS control/DC-balance/test settings.
- AFMT/audio state: audio clock enable/status, audio source/channel enables, IEC 60958 channel-status values, ISRC/MPEG/HDR/generic packet payload bytes, ramp controls, audio CRC, and audio FIFO/status flags.
- DisplayPort transport state: pixel encoding/depth/combine, MSA/VBID/timing fields, video timing N/M, link framing, DPHY training/test/scrambler/CRC/fast-training state, secondary-data packet enables and scheduling, audio M/N/timestamp/readbacks, MST MSE rates and slot allocation tables, MSO controls, DSC mode/slice/bytes-per-pixel, metadata packet line scheduling, double-buffer state, and ALPM sleep/standby requests.

Persistence is hardware-specific and not encoded here. Some fields are durable programming knobs that remain until modeset, reset, suspend/resume, link retraining, power-gating transition, or an explicit rewrite. Other fields are read-only status, sticky flags, pending bits, deadline-missed indicators, self-clearing send/update requests, write-one-to-clear controls, double-buffered latches, or line-scheduled packet triggers. Names such as `*_STATUS`, `*_PENDING`, `*_CLR`, `*_LOCK`, `*_TAKEN`, `*_DEADLINE_MISSED`, `*_READBACK`, `*_SEND`, and `*_UPDATE` hint at side effects, but access type and reset values require the hardware register specification and the matching generated offset/enum headers.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract for DCN 2.0. It is meaningful together with:

- `dcn_2_0_0_offset.h` for the matching MMIO register offsets and base indices.
- DCN 2.0 enum/value headers for symbolic field values.
- AMD display register helper macros and per-block register/mask/shift tables in `drivers/gpu/drm/amd/display/dc`.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

Practical integration surfaces are HDMI and DisplayPort stream encoder programming, link encoder enable/link-training/MST programming, DSC PPS and bytes-per-pixel setup, Dolby Vision and dynamic metadata packet scheduling, HDMI and DP infoframe/generic packet emission, HDMI/DP audio packet and IEC 60958 programming, hotplug/routing association through DIG back-end fields, DP ALPM, and stream/link diagnostics through CRC/status/readback fields.

## Risks And Edge Cases

- Masks and shifts are hardware ABI. A one-bit error can compile cleanly but update the wrong field, causing link-training failures, black screens, bad HDMI/DP packets, corrupted audio metadata, incorrect DSC configuration, or unstable hotplug/routing behavior.
- The range is generated and highly repetitive. `DP3`/`DP4` and `DIG3`/`DIG4` instance families are easy to skew by hand; regeneration from the authoritative register database is safer than manual edits.
- The chunk boundary is not semantic. It starts after earlier `DIG3_DIG_BE_EN_CNTL` shift definitions and ends after only the first `DIG5_DIG_FE_CNTL` fields, so complete per-instance analysis requires adjacent chunks.
- Stream and link roles overlap. `DIG` front-end fields route pixel streams and metadata, while `DIG` back-end and `DP` fields drive physical/link transport. Mismatched instance IDs can bind one stream to the wrong back-end or DP link.
- Packet-control fields have pending, conflict, lock, immediate, frame-update, and line-number semantics. Updating AFMT/HDMI/DP packet memory without respecting these flags can drop HDR/Dolby/AVI/audio infoframes or race hardware packet reads.
- DP secondary-data scheduling is timing-sensitive. Wrong line references, line numbers, GSP send flags, PPS flags, or metadata packet enables can miss packet deadlines or place packets on invalid lines.
- DSC fields are display-mode critical. Wrong DSC mode, slice width, or bytes-per-pixel fields can produce blank output or decompression artifacts on DSC-capable sinks.
- MST/MSE and MSO fields are allocation-critical. Incorrect slot counts, source IDs, rate updates, link timing, or MSO segment settings can break multi-stream or multi-segment DisplayPort output.
- ALPM and DPHY training/test fields can affect link stability. Misprogramming sleep/standby requests, training patterns, scrambler state, PRBS, CRC, or HBR2 pattern fields can lead to failed training, flicker, or resume failures.
- Status, clear, reset-like, and pending bits often have side effects that are invisible in this header. Consumers must not infer access type from the mask alone.

## Test Signals

Useful validation is compile-time plus hardware/display behavior:

- Build AMDGPU/DC with DCN20 support; generated macro drift should fail in DCN20 resource construction, stream encoder, link encoder, audio, IRQ, GPIO, DMUB, or clock-manager paths.
- Compare this chunk against `dcn_2_0_0_offset.h` and adjacent DCN-family mask headers to catch instance drift, missing `DP3`/`DP4` symmetry, and unintended `DIG4`/`DIG5` field differences.
- Exercise HDMI and DP modesets on DCN20 hardware across multiple encoder instances, including hotplug, blank/unblank, suspend/resume, link retraining, and routing between front-end and back-end encoders.
- Validate HDMI infoframes and generic packets: AVI, vendor/HF-VSIF, HDR static metadata, VTEM, metadata packet line scheduling, double-buffer behavior, and packet stop/start transitions.
- Validate DisplayPort stream behavior: link training, stream enable/disable, enhanced framing, MSA/VBID values, MST slot allocation where available, MSO paths, DSC PPS/bytes-per-pixel programming, and secondary-data packet scheduling.
- Validate audio paths: HDMI ACR, DP audio M/N and timestamp packets, AFMT audio clock, channel layout, IEC 60958 channel status, HBR audio, and audio CRC/status behavior.
- Validate diagnostics and negative signals: output CRC/DPHY CRC, FIFO status, DPHY fast-training status, MSE status, metadata deadline-missed flags, AFMT generic conflict flags, kernel underflow/link-training messages, black screens, flicker, color/format mismatches, missing HDR/Dolby metadata, silent HDMI/DP audio, and resume/hotplug regressions.
