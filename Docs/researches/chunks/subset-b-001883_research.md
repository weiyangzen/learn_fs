# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 44692-47145

## Scope

This chunk is a generated AMD DCN 3.1.5 register-field shift/mask header slice. It contains preprocessor constants only: `_SHIFT` macros for hardware bit positions, `_MASK` macros for raw register bit masks, register grouping comments, and address-block comments. There are no functions, structs, enums, local variables, branches, loops, allocations, software locks, or file-backed persistence in this range.

The requested range contains 2,142 `#define` lines: 1,071 shift definitions and 1,071 mask definitions. It starts in the tail of the `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` definitions, covers complete `PWRSEQ1`, `DSCC0..2`, `DSCCIF0..2`, `DSC_TOP0..2`, DSC-related `DC_PERFMON19..21`, HPO top/mapper/perfmon, `AFMT5`, `DME5`, `VPG5`, `DP_STREAM_ENC0`, and the beginning of `APG0`. It ends at `APG0_APG_AUDIO_CRC_RESULT`; the remaining APG0 status/memory/spare definitions are in the following chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display-controller hardware metadata, not Ceph filesystem code.

## Purpose

The purpose of this header range is to provide the DCN 3.1.5 bit-layout ABI used by AMDGPU Display Core and DMUB code when programming MMIO registers. Matching offset definitions in `dcn_3_1_5_offset.h` identify register addresses and base indices; this file identifies the bit fields inside those registers. Runtime code combines both sets of macros through register helpers and generated register-table initializers to pack writes, build read/modify/write masks, decode readbacks, and poll status bits.

The major hardware surfaces represented here are:

- Panel power sequencing and backlight PWM for `PWRSEQ1`, plus the end of `PWRSEQ0`.
- Display Stream Compression controller blocks `DSCC0`, `DSCC1`, and `DSCC2`, their DSCCIF interfaces, top-level DSC controls, and per-DSC performance monitors.
- High Performance Output control: HPO top clock/hardware control, DP stream mapper controls, and HPO performance monitor 22.
- HDMI/DIO stream support blocks for instance 5: AFMT audio/infoframe registers, DME dynamic metadata registers, and VPG generic packet/video packet registers.
- HPO DP stream encoder 0 and the start of APG0 audio packet generator definitions.

This chunk is data, but it is not passive in practice. A wrong mask or shift can compile successfully and then program the wrong hardware bits during panel power transitions, DSC PPS setup, HPO stream creation, audio packet generation, metadata transmission, CRC/debug capture, or performance monitoring.

## Important APIs, Types, And Macros

The exported interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for the field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in register-positioned form.
- `//<REGISTER>` comments group field macros by register.
- `// addressBlock: ...` comments identify the hardware aperture for following registers.

There are no C APIs or types defined in this slice. The important definition families are the register namespaces below.

### PWRSEQ And Backlight PWM

The chunk starts after the beginning of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`, then completes `PWRSEQ0_PANEL_PWRSEQ_REF_DIV2` and `PWRSEQ0_PWRSEQ_SPARE`. The `PWRSEQ1` block defines a complete second panel power-sequencer instance:

- `PWRSEQ1_DC_GPIO_PWRSEQ_EN`, `PWRSEQ1_DC_GPIO_PWRSEQ_CTRL`, `PWRSEQ1_DC_GPIO_PWRSEQ_MASK`, and `PWRSEQ1_DC_GPIO_PWRSEQ_A_Y` describe VARY_BL, DIGON, and BLON GPIO enable, TX/RX/pull-up/drive-strength, mask/pull-down/receiver, and A/Y state fields.
- `PWRSEQ1_PANEL_PWRSEQ_CNTL` and `PWRSEQ1_PANEL_PWRSEQ_STATE` expose panel power-sequence enable, target state, SYNCEN/DIGON/BLON signal control, override/polarity fields, current target/state readback, and done/status bits.
- `PWRSEQ1_PANEL_PWRSEQ_DELAY1`, `PWRSEQ1_PANEL_PWRSEQ_DELAY2`, `PWRSEQ1_PANEL_PWRSEQ_REF_DIV1`, and `PWRSEQ1_PANEL_PWRSEQ_REF_DIV2` define power-up/down timing, minimum power-down length, variable-backlight override, panel and PWM reference divisors, XTAL reference divisor, and microsecond time base divisor.
- `PWRSEQ1_BL_PWM_CNTL`, `PWRSEQ1_BL_PWM_CNTL2`, `PWRSEQ1_BL_PWM_PERIOD_CNTL`, and `PWRSEQ1_BL_PWM_GRP1_REG_LOCK` define active PWM count, PWM enable/fractional-enable bits, frame-start update recognition, post-frame-start update delay, debug reference-clock selection, period/bit-count, double-buffer readback, update-pending, frame-start update, master-lock bypass, and lock fields.

These definitions are paired with legal values documented in enum headers such as `soc21_enum.h` and `soc24_enum.h`, including PWM enable/fractional-enable, frame-start update, register lock, target panel state, and PWM override meanings.

### DSC, DSCC, DSCCIF, And DSC_TOP

For `DSCC0`, `DSCC1`, and `DSCC2`, this chunk repeats the same Display Stream Compression controller field layout:

- `DSCC*_DSCC_CONFIG0` covers ICH reset at end of line, slices per line, alternate ICH encoding, and vertical slice count.
- `DSCC*_DSCC_CONFIG1` carries the rate-control buffer model size.
- `DSCC*_DSCC_STATUS` exposes double-buffer register update pending.
- `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS` exposes rate-buffer overflow/underflow occurred bits for buffers 0-3, rate-control buffer model overflow bits for models 0-3, and the corresponding interrupt-enable bits.
- `DSCC*_DSCC_PPS_CONFIG0` through `DSCC*_DSCC_PPS_CONFIG22` pack DSC Picture Parameter Set fields: DSC version, PPS identifier, line buffer depth, bits per component, bits per pixel, VBR/simple/native 4:2:2/4:2:0/RGB conversion flags, chunk size, picture and slice geometry, initial transmit/decode delays, scale values and intervals, line BPG offsets, NFL/NSL/slice BPG offsets, initial/final offsets, flatness and RC model fields, edge factor, quantization increment limits, target offsets, RC buffer thresholds 0-13, and range min/max QP plus range BPG offsets 0-14.
- `DSCC*_DSCC_MEM_POWER_CONTROL` defines default low-power state, memory power force/disable/state fields, and native-422 memory power force/disable/state fields.
- `DSCC*_DSCC_R_Y/G_CB/B_CR_SQUARED_ERROR_*`, `DSCC*_DSCC_MAX_ABS_ERROR*`, `DSCC*_DSCC_RATE_BUFFER*_MAX_FULLNESS_LEVEL`, and `DSCC*_DSCC_RATE_CONTROL_BUFFER*_MAX_FULLNESS_LEVEL` expose quality/statistics/debug counters for reconstructed-channel error and rate-buffer fullness.
- `DSCC*_DSCC_TEST_DEBUG_BUS_ROTATE` selects and rotates DSCC debug bus output.

`DSCCIF0..2` provides interface-level `DSCCIF_CONFIG0` and `DSCCIF_CONFIG1` fields for DSC pixel-rate/slice-width, DSCCIF enable, status, underrun, block-prediction enable, BPP decrement, and pass-through reporting. `DSC_TOP0..2` provides the top-level DSC reset/clock-enable/disconnect state and debug display selection.

### DC_PERFMON19 Through DC_PERFMON22

The range defines four performance monitor instances:

- `DC_PERFMON19` is associated with the DSC0 address block.
- `DC_PERFMON20` is associated with DSC1.
- `DC_PERFMON21` is associated with DSC2.
- `DC_PERFMON22` is associated with HPO.

Each block follows the same pattern: `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW`. The fields cover counter enable, clear, stop modes, test debug index selection, state/version/read-window status, performance monitor enable/continuous/start modes, clear-on-read and clear-on-start behavior, manual load, windowed trigger masks, low/high current values, and interrupt/status metadata.

### HPO Top And DP Stream Mapper

`HPO_TOP_CLOCK_CONTROL` defines HPO DP stream, link, PHY, HDMI stream, and HDMI character clock gate-disable fields, plus clock-on status readbacks for DP stream/link/PHY, HDMI stream, and HDMI character clocks. `HPO_TOP_HW_CONTROL` exposes `HPO_IO_EN`.

`DP_STREAM_MAPPER_CONTROL0..3` map four stream encoders to DP stream sources through `DP_STREAM_SOURCE_SELECT0..3` fields. These fields are part of the HPO routing path and must match resource-layer stream encoder allocation.

### AFMT5 Audio And Infoframe

`AFMT5` is the audio formatter/infoframe block for stream instance 5. Important field groups include:

- `AFMT5_AFMT_VBI_PACKET_CONTROL` for null, GC, generic stream, ACP, and ISRC packet sending.
- `AFMT5_AFMT_AUDIO_PACKET_CONTROL2` for ACR packet send, layout override, HBR packet behavior, audio channel count, and HBR sample-readiness enable.
- `AFMT5_AFMT_AUDIO_INFO0` and `AFMT5_AFMT_AUDIO_INFO1` for HDMI/DP audio infoframe fields such as CC, CT, checksum offset, CXT, channel allocation, level shift value, downmix inhibit, and LFEPBL.
- `AFMT5_AFMT_60958_0`, `_1`, and `_2` for IEC 60958 channel-status fields: CS A-D, mode, category, source number, sampling frequency, clock accuracy, word length, original sampling frequency, validity bits, and channel numbers.
- `AFMT5_AFMT_AUDIO_CRC_CONTROL` and `AFMT5_AFMT_AUDIO_CRC_RESULT` for audio CRC enable/continuous/source/channel/count and result/done readback.
- `AFMT5_AFMT_RAMP_CONTROL0..3` for audio ramp test generation limits and increment/decrement values.
- `AFMT5_AFMT_STATUS`, `AFMT5_AFMT_AUDIO_PACKET_CONTROL`, `AFMT5_AFMT_INFOFRAME_CONTROL0`, `AFMT5_AFMT_AUDIO_SRC_CONTROL`, and `AFMT5_AFMT_MEM_PWR` for audio enable/HBR/FIFO overflow/change status, sample send, double-buffered sample send, FIFO reset when audio disables, test mode, overflow/change acks, 60958 update, blanking behavior, audio-info source/update, audio source select, and AFMT memory power force/disable/state.

### DME5 And VPG5

`DME5_DME_CONTROL` defines metadata requestor ID, metadata engine enable, stream type, double-buffer pending/taken/clear/disable, metadata transmission missed, and missed-clear fields. `DME5_DME_MEMORY_CONTROL` defines DME memory power force/disable/state and default low-power state.

`VPG5` defines the video packet generator instance used with the same stream family:

- `VPG5_VPG_GENERIC_PACKET_ACCESS_CTRL` and `VPG5_VPG_GENERIC_PACKET_DATA` expose indexed generic packet data bytes.
- `VPG5_VPG_GSP_FRAME_UPDATE_CTRL` provides frame-update request and pending bits for generic packets 0-14.
- `VPG5_VPG_GSP_IMMEDIATE_UPDATE_CTRL` provides immediate-update request and pending bits for generic packets 0-14.
- `VPG5_VPG_GENERIC_STATUS` exposes generic packet lock, conflict occurred, and conflict clear fields.
- `VPG5_VPG_MEM_PWR` controls VPG/GSP memory light sleep and reports memory power state.
- `VPG5_VPG_ISRC1_2_ACCESS_CTRL`, `VPG5_VPG_ISRC1_2_DATA`, `VPG5_VPG_MPEG_INFO0`, and `VPG5_VPG_MPEG_INFO1` define indexed ISRC data bytes and MPEG info checksum/metadata/update fields.

### DP_STREAM_ENC0 And APG0

`DP_STREAM_ENC0` defines the first HPO DP stream encoder's clock, mux, audio, FIFO, and spare fields:

- `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL` exposes stream encoder clock enable plus clock-on readbacks for DISPCLK, SOCCLK, DPSTREAMCLK, and SYMCLK32.
- `DP_STREAM_ENC0_DP_STREAM_ENC_INPUT_MUX_CONTROL` selects the pixel stream source.
- `DP_STREAM_ENC0_DP_STREAM_ENC_AUDIO_CONTROL` selects the audio stream source.
- `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL0` controls FIFO enable/reset, read start level, read clock source, reset done, video stream active, and FIFO error status.
- `DP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_RAMP_ADJUSTER_FIFO_STATUS_CONTROL1` controls overwrite/recalculation/recompute behavior and exposes overwrite/min/max/calibrated average level and calibrated status.

The chunk then begins `APG0`, the audio packet generator for HPO DP stream encoder 0. It covers reset/reset-done, APG enable, DP audio stream ID, ASP channel count override, debug generator enable/reset/channel/test-disable fields, ACP/audio-info source selection, audio CRC control/count/default count, and audio CRC done/clear/result readback. `APG0_APG_STATUS`, `APG0_APG_STATUS2`, `APG0_APG_MEM_PWR`, and `APG0_APG_SPARE` follow after this chunk.

## Control Flow

This header has no direct control flow. Runtime flow is supplied by AMDGPU display code:

1. DCN315 source includes `dcn_3_1_5_offset.h` and `dcn_3_1_5_sh_mask.h`.
2. Token-pasting macros such as `SF`, `SR`, `SRI`, and block-specific list macros select a register, shift, and mask by generated name.
3. DCN315 resource construction stores those offsets/shifts/masks in block-specific tables.
4. Display hardware code uses the tables through register helpers such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, wait/poll helpers, DMUB service tables, GPIO translation, IRQ service code, and stream encoder/audio/DSC abstractions.
5. Hardware latches, reports, clears, or consumes the represented fields according to the block-specific sequencing rules.

The macros do not encode access type, reset value, volatile behavior, double-buffering semantics, clear-on-write behavior, or ordering. Callers must still sequence panel power, backlight PWM updates, DSC PPS programming, DSCCIF enablement, HPO clocking, stream mapper routing, VPG/AFMT/APG packet updates, DME metadata double-buffering, FIFO reset/calibration, memory power transitions, and performance counter capture according to DCN hardware requirements.

## State And Persistence Behavior

No software state is stored by this file. It describes MMIO-backed hardware state whose lifetime is controlled by display hardware, power management, modesets, suspend/resume, resets, and firmware/driver ownership.

Persistent or latched configuration fields include panel power target/override/polarity, GPIO power sequence control, panel timing delays, PWM reference divisors/period/count/enable, DSC PPS parameters, DSCC memory power policy, DSCCIF enable/configuration, DSC top reset/clock/disconnect controls, perfmon configuration, HPO clock gate controls, stream mapper selections, AFMT packet/source/audio-info/60958 controls, DME metadata engine controls, VPG packet data/update controls, DP stream encoder mux/audio/FIFO controls, and APG enable/audio stream/debug/CRC controls.

Volatile readback or status fields include panel state/done, PWM update pending/frame-start recognition, DSCC double-buffer update pending, DSCC overflow/underflow/RC-buffer overflow occurred bits, DSCC error and fullness counters, DSCCIF status/underrun/pass-through status, DSC clock-on/current reset status, perfmon counter values and state readbacks, HPO clock-on and IO status, AFMT audio/FIFO/change status and CRC done/result, DME double-buffer taken/pending and missed-transmission status, VPG update pending/conflict/memory-power state, DP stream encoder clock-on/FIFO reset-done/active/error/calibrated status, and APG reset-done/CRC result.

Side-effecting write fields include reset bits, missed/clear bits, FIFO overflow and change acknowledgements, VPG conflict clear, DME taken/missed clears, APG CRC done clear, perfmon clear/manual load controls, DSCC interrupt enable bits, memory power force/disable fields, PWM lock/update fields, and generic packet frame/immediate update bits. Treating these fields as ordinary persistent booleans can cause lost events, stale status, or unintended hardware state changes.

## Dependencies And Integration Points

This chunk depends on the matching generated offset header at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`. For the visible field families, that header supplies offsets and base indices for registers such as `regPWRSEQ1_PANEL_PWRSEQ_CNTL`, `regDSCC0_DSCC_PPS_CONFIG0`, `regDSCC2_DSCC_INTERRUPT_CONTROL_STATUS`, `regHPO_TOP_CLOCK_CONTROL`, `regDP_STREAM_MAPPER_CONTROL0`, `regAFMT5_AFMT_AUDIO_PACKET_CONTROL`, `regDME5_DME_CONTROL`, `regVPG5_VPG_GSP_FRAME_UPDATE_CTRL`, `regDP_STREAM_ENC0_DP_STREAM_ENC_CLOCK_CONTROL`, and `regAPG0_APG_CONTROL`.

Known direct include sites for the DCN 3.1.5 generated headers are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`, which includes the offset and mask headers for DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`, which includes them for DCN315 IRQ service register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.c` and `hw_translate_dcn315.c`, which include them for GPIO register translation and factory setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`, which builds many of the runtime register/shift/mask tables.

The strongest source-tree integration points visible for this chunk are in `dcn315_resource.c`:

- `vpg_regs[]`, `vpg_shift`, and `vpg_mask` use `VPG_DCN31_REG_LIST(id)` and `DCN31_VPG_MASK_SH_LIST(...)`; this covers VPG instances including `VPG5` and HPO-related `VPG6..9`.
- `afmt_regs[]`, `afmt_shift`, and `afmt_mask` use `AFMT_DCN31_REG_LIST(id)` and `DCN31_AFMT_MASK_SH_LIST(...)`; this covers AFMT instances 0-5, including the `AFMT5` fields in this range.
- `apg_regs[]`, `apg_shift`, and `apg_mask` use `APG_DCN31_REG_LIST(id)` and `DCN31_APG_MASK_SH_LIST(...)`; this covers APG instances 0-3, including `APG0`.
- `hpo_dp_stream_enc_regs[]`, `hpo_dp_se_shift`, and `hpo_dp_se_mask` use `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST(id)` and `DCN3_1_HPO_DP_STREAM_ENC_MASK_SH_LIST(...)`; this covers `DP_STREAM_ENC0`.
- `dsc_regs[]`, `dsc_shift`, and `dsc_mask` use `DSC_REG_LIST_DCN20(id)` and `DSC_REG_LIST_SH_MASK_DCN20(...)`; this covers DSC instances 0-2.
- `hwseq_reg`, `hwseq_shift`, and `hwseq_mask` include `HPO_TOP_HW_CONTROL`, `HPO_TOP_CLOCK_CONTROL__HPO_HDMISTREAMCLK_G_GATE_DIS`, and `HPO_TOP_HW_CONTROL__HPO_IO_EN`.
- HPO DP stream encoder creation maps HPO DP stream instances to VPG and APG subblocks: `VPG[6] -> HPO_DP[0]` through `VPG[9] -> HPO_DP[3]`, and `APG[0] -> HPO_DP[0]` through `APG[3] -> HPO_DP[3]`. This is important context for the `DP_STREAM_ENC0` and `APG0` fields in this range.

Other integration is indirect through common display block implementations for DSC, VPG, AFMT, APG, HPO DP stream encoders, hardware sequencing, audio, GPIO, IRQ handling, DMUB, diagnostics, and power management. The repeated generated names also align with nearby DCN 3.1.x and later generated headers, so mechanical regeneration and cross-revision comparison are normal maintenance tools.

## Risks And Edge Cases

- Bitfield drift is the primary risk. A wrong numeric shift or mask can compile but corrupt the wrong hardware field at runtime.
- The chunk has artificial boundaries. It starts in the middle of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK` and ends before the end of `APG0`; neighboring chunks are required for full file-level conclusions about those registers.
- `PWRSEQ1` fields are timing-sensitive. Incorrect target state, override, polarity, delay, reference divider, PWM period, or lock/update-pending handling can break panel power sequencing, backlight behavior, or frame-synchronized PWM updates.
- GPIO power sequence fields are easy to confuse because VARY_BL, DIGON, and BLON fields share the same register shapes. A valid mask can still target the wrong panel signal.
- DSC PPS fields are dense and standards-driven. Mistakes in BPP, chunk size, slice geometry, RC model, thresholds, QP range, BPG offset, or native 4:2:2/4:2:0 flags can produce visual corruption, link bandwidth mismatch, sink rejection, or failures limited to compressed display modes.
- DSCC interrupt/status fields combine occurred bits and interrupt-enable bits in one namespace. Maintenance must preserve status versus enable semantics.
- DSCCIF and DSC_TOP enable/reset/underrun fields are sequencing-sensitive around modesets and stream enablement. Polling the wrong status bit can hide an underrun or release reset too early.
- Perfmon registers are diagnostic but stateful. Clear-on-read, clear-on-start, windowing, manual load, and counter selection fields can make performance data misleading if masks drift.
- HPO clock gate and stream mapper fields sit on display routing and clocking paths. Incorrect masks can leave clocks gated, route a stream to the wrong encoder, or make HPO IO unavailable.
- AFMT, VPG, DME, and APG packet/control fields are packetization and metadata surfaces. Wrong update, pending, clear, source, or data-index fields can drop HDMI/DP audio packets, generic packets, ISRC/MPEG info, dynamic metadata, or infoframe updates while leaving the display link otherwise active.
- `VPG5` has both frame-update and immediate-update request/pending fields for generic packets 0-14. Confusing request and pending bits or frame versus immediate update can produce stale packet data or update conflicts.
- DP stream encoder FIFO fields expose both control and calibrated/status values. Reset/calibration/read-level mistakes can cause underflow, FIFO error, or stream instability during clock ramping.
- Generated fields whose hardware names include `MASK` can produce names ending in `_MASK_MASK` in other chunks. Cleanup scripts should not normalize generated names by hand.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU Display Core with DCN315 enabled. Missing, malformed, or renamed macros should fail in `dcn315_resource.c`, `irq_service_dcn315.c`, `dmub_dcn315.c`, GPIO translation, or common block headers that expand the generated names.
- Mechanically compare this range against a regenerated `dcn_3_1_5_sh_mask.h` or the authoritative DCN 3.1.5 register database, checking every shift/mask pair and preserving boundary partials.
- Cross-check against adjacent DCN 3.1.x generated headers where hardware is expected to be compatible, while treating DCN315-specific instance counts and offsets as authoritative.
- Exercise panel power and backlight on DCN315 hardware: power on/off, suspend/resume, brightness changes, PWM fractional mode, frame-start PWM updates, and no stuck update-pending or incorrect GPIO signal states.
- Exercise DSC on all three instances with compressed display modes, multiple slice counts, native RGB and YCbCr formats, DSC disable/enable transitions, underrun handling, and DSC PPS readback/register dumps.
- Validate HPO DP stream creation and routing, including HPO top clock enablement, stream mapper selection, DP stream encoder clock status, pixel/audio mux selection, FIFO reset/calibration, and multi-stream configurations.
- Test HDMI/DP audio and packet paths for AFMT/VPG/APG: audio playback, HBR and channel-count modes, IEC 60958 status updates, audio infoframe updates, ACR/sample packet send, generic packet frame/immediate updates, ISRC/MPEG packet data, CRC result paths, and FIFO overflow/change acknowledgements.
- Test DME metadata updates, including double-buffer pending/taken behavior and missed-transmission clear paths during HDR/dynamic metadata changes.
- Use perfmon/debug tests to confirm DC_PERFMON19-22 counter programming, clear behavior, readback windows, and source selection remain meaningful after changes.
- Inspect runtime register dumps before and after operations. Packed writes should only affect bits covered by the intended mask and should preserve unrelated fields.

## Cross-Chunk Notes

The previous chunk owns the beginning of `PWRSEQ0_BL_PWM_GRP1_REG_LOCK`; this chunk should not be treated as the complete `PWRSEQ0` story. The next chunk owns the rest of `APG0`, starting with status, output-active, memory-power, and spare definitions. The final merged report for `dcn_3_1_5_sh_mask.h` should reconcile these artificial boundaries and avoid claiming complete PWRSEQ0 or APG0 coverage from this chunk alone.
