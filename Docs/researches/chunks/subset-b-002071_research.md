# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_sh_mask.h lines 33218-35435

## Purpose

This chunk is a generated AMD DCN 3.5.0 shift/mask register-field slice. It has no executable C logic; it exports preprocessor constants that describe bit positions and bit masks for MMIO register fields in display, audio, DisplayPort, HDMI/TMDS, metadata, GPIO, AUX/DDC, HPD, UNIPHY, and DCIO blocks. AMDGPU display code combines these constants with matching offsets from `dcn_3_5_0_offset.h` so register-helper macros can pack, update, or extract individual hardware fields without hard-coding numeric bit layouts in handwritten driver code.

The requested range contains 2,218 `#define` lines: 1,117 `__SHIFT` macros and 1,101 `_MASK` macros. The count mismatch is caused by chunk boundaries, not by a complete in-range field mismatch. The range starts after three `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` shifts, so their masks are present here but their shifts are in the previous chunk. It ends after `DC_GPIO_AUX_CTRL_1` shifts and before the corresponding masks for 19 AUX/I2C/DDCVGA fields, which continue in the next chunk.

Although the repository root is a `ceph-client` source tree mirror, this file belongs to the AMDGPU display driver. It is hardware metadata for AMD display silicon, not distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocation paths, or direct register accesses in this chunk. The public interface is the generated macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the field mask used by AMD display helpers such as `FD_SHIFT`, `FD_MASK`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and macro-generated register-table initializers.

The major macro families in this range are:

- `AFMT4_*`: audio formatter instance 4 fields for audio infoframes, IEC 60958 channel status, audio CRC, test ramps, FIFO overflow/status ack bits, audio sample send, channel swap, channel enablement, DP audio stream ID, HBR override, audio source select, and AFMT memory power control.
- `DME4_*`: display metadata engine instance 4 controls for HUBP requestor ID, metadata engine enable, stream type, double-buffer pending/taken state, clear bits, DB disable, transmission-missed status, and DME memory power controls.
- `DIG4_*`: digital frontend/backend, HDMI, AFMT clock, and TMDS fields for source selection, stereosync, FIFO/output CRC/test pattern support, HDMI control, VBI/audio/infoframe/metadata packet control, generic packet send modes, immediate-send pending state, generic packet line numbers, HDMI double-buffer status/locking, HDMI ACR CTS/N values, DIG backend mapping, TMDS control characters, sync patterns, DC balancer controls, and control-bit generation.
- `DP4_*`: DisplayPort instance 4 fields for link status, pixel format, MSA colorimetry/timing, stream enable/defer/status, steer FIFO, video timing, VBID/MSA misc values, vid M/N, DPHY controls, training patterns, PRBS/scrambler/CRC, secondary data packet controls, audio M/N, timestamping, MST/MSE allocation tables, MSO routing, DSC mode, GSP packet controls, DP double-buffering, metadata packet transmission, and ALPM/AUX-less ALPM controls.
- `UNIPHYA_*` through `UNIPHYE_*`: link and channel crossbar controls for UNIPHY output routing. A/B/C include `LINK_CNTL` and `CHANNEL_XBAR_CNTL`; D/E in this range include channel crossbar controls.
- `DCIO_*`, `DC_PINSTRAPS`, and `INTERCEPT_STATE`: clock source selection, write-command delay, spare fields, pinstrap status, intercept status for PWRSEQ/DPCS units, pattern generator enable/data, backlight PWM frame-start display selection, genlock/swaplock GSL pad controls, and soft-reset fields for UNIPHY, DSYNC, and PWRSEQ blocks.
- `DC_GPIO_*` and `PHY_AUX_CNTL`: generic GPIO, genlock, DDC1-5, DDCVGA, HPD, PWRSEQ, pad-strength, TX12, AUX pad wake/RX select, and AUX control fields for display connector sideband, hotplug, backlight, generic pins, and AUX/I2C electrical behavior.

Several layouts are mechanically repeated. HDMI generic packet controls cover packet slots 0-14 with send/continuous/line-reference/update-lock and immediate-send/pending bits. DP secondary-data controls cover ASP, ATP, AIP, ACM, GSP0-11, MPG, ISRC, audio mute, line scheduling, DB gating, active/idle status, and deadline-missed flags. GPIO DDC registers repeat the same mask/A/EN/Y shape for DDC1 through DDC5 and DDCVGA.

## Control Flow

This header has no runtime control flow. Runtime behavior is created by consumers that include the generated offsets and shifts/masks:

1. DCN 3.5 modules include `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`.
2. Register-list macros token-paste register and field names into offset, shift, and mask tables. For example, `dmub_dcn35.c` initializes `regs->mask.reg__field` with `FD_MASK(reg, field)` and `regs->shift.reg__field` with `FD_SHIFT(reg, field)`.
3. Display block constructors hand those tables to register helpers for DMUB, link encoders, GPIO/DDC, IRQ, audio/stream encoder, and other DCN components.
4. Runtime code calls helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`. These helpers use the numeric masks and shifts from this header to preserve unrelated bits during read-modify-write operations and to decode status fields.

The sequencing rules are not encoded here. The handwritten display driver remains responsible for correct ordering around HDMI/DP stream enablement, link training, infoframe or secondary packet updates, double-buffer commit/taken waits, FIFO resets, CRC capture, audio setup, DDC/AUX routing, HPD handling, soft reset assertion/deassertion, power gating, and suspend/resume restore.

## State And Persistence Behavior

The chunk persists no software state by itself. It describes mutable hardware state in DCN 3.5 registers:

- AFMT state includes audio infoframe payload fields, IEC 60958 channel-status values, audio packet send/override controls, FIFO overflow/acknowledgement flags, audio enable and HBR status, test ramp controls, CRC start/result state, selected audio source, and AFMT memory power state.
- DME state includes metadata engine enablement, stream type, DB pending/taken/disable/clear bits, missed-transmission status/clear bits, and low-power memory state.
- DIG and HDMI/TMDS state includes selected frontend/backend routing, FIFO and test-pattern controls, HDMI deep-color/pixel-repetition/packet mode fields, metadata and generic-packet scheduling, ACR N/CTS values, HDMI/vertical-update DB state, AFMT audio clock gating, TMDS sync/control/DC-balance generation, and encoder type.
- DP state includes link-training completion/status, lane count, pixel encoding/depth, stream enable/status/deferred disable, video timing, DPHY training/scrambling/CRC, MSA timing values, secondary packet framing and GSP scheduling, audio M/N values, MST/MSE slot allocations, MSO secondary-stream packet enables, DSC mode, metadata packet line scheduling, and ALPM/AUX-less ALPM counters and enables.
- DCIO, UNIPHY, and GPIO state includes output lane/link routing, channel crossbar mapping, resets, pinstrap-observed configuration, intercept status, pattern generation, PWM frame-start association, genlock/swaplock pad selections, generic GPIO drive/read/enable/mask state, DDC/AUX mode and pull-down behavior, HPD enable/sample/read state, pad strength, and AUX/I2C comparator or bias configuration.

Persistence semantics are hardware-defined. Some fields are latched configuration until the next modeset, power transition, driver reset, or ASIC reset. Some are read-only status, write-one-to-clear acknowledgement bits, self-clearing update bits, sticky fault bits, or double-buffer handshakes. This generated header does not mark access semantics, clock-domain requirements, reset defaults, or side effects.

## Dependencies And Integration Points

This chunk must stay synchronized with AMD's generated DCN 3.5.0 register database and with the companion offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h` supplies matching MMIO offsets and base-index macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.c` directly includes this header and uses `FD_MASK`/`FD_SHIFT` to populate DCN35 DMUB register tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn35/irq_service_dcn35.c` includes this header for DCN35 interrupt register definitions.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/ddc_regs.h` shows the `SF_DDC(...)` pattern that consumes `DC_GPIO_DDC1_MASK` fields such as DDC data/clock pull-down and AUX pad mode.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h` and related link-encoder headers show the `LE_SF(...)` pattern that consumes fields such as `DCIO_SOFT_RESET__UNIPHYA_SOFT_RESET`.

The main behavioral integration points from this exact slice are display link and connector operation. AFMT/DIG/DP fields affect HDMI/DP audio and packet transmission. DP DPHY and stream fields affect link training and video transport. DME and DP metadata fields affect HDR or other metadata packet delivery. DCIO/UNIPHY fields affect physical routing and reset. GPIO/DDC/AUX/HPD fields affect monitor discovery, EDID reads, DisplayPort AUX transactions, hotplug detection, panel/backlight signaling, and sideband electrical configuration.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile successfully while writing the wrong MMIO bit or preserving the wrong adjacent field.
- The file is generated. Manual edits can diverge from the authoritative AMD register database, firmware expectations, silicon documentation, and the matching `dcn_3_5_0_offset.h` layout.
- Repeated HDMI generic packet, DP GSP/MSE/MSO, DDC, HPD, and UNIPHY families are vulnerable to instance-specific generator or copy errors. One connector, packet slot, or stream working does not prove the repeated siblings are correct.
- This chunk starts and ends mid-family. The first three `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` shifts are outside this chunk, and the `DC_GPIO_AUX_CTRL_1` masks for 19 fields are outside this chunk. Whole-register conclusions need adjacent chunks.
- Double-buffer and pending/taken fields are sequencing-sensitive. Confusing pending, taken, clear, lock, disable, or update-lock fields can cause stale packets, lost metadata, delayed updates, or waits that never complete.
- Audio fields are interoperability-sensitive. Incorrect AFMT channel enablement, IEC 60958 status, audio packet layout, HBR override, ACR N/CTS, or DP secondary audio M/N fields can cause silent HDMI/DP audio, wrong sample-rate reporting, channel mapping failures, or receiver-specific behavior.
- DisplayPort transport fields are timing-sensitive. Incorrect MSA timing, VBID, DPHY training, scrambling, CRC, MSE slot allocation, MSO enablement, DSC mode, or ALPM control can produce link training failures, blank screens, MST bandwidth errors, or resume-only failures.
- GPIO, DDC, AUX, and HPD fields can affect physical pins. Wrong masks for pull-down, drive enable, pad mode, polarity, slew, strength, comparator, bias, or RX selection can break EDID/AUX communication, hotplug detection, backlight control, or board-specific connector routing.
- Reset and power fields can have broad blast radius. Incorrect `DCIO_SOFT_RESET`, AFMT/DME memory power, or clock-control bits can leave PHYs, DSYNC, PWRSEQ, audio, or packet engines inaccessible until a larger display reset.

## Test Signals

Useful validation combines build-time generated-header checks with hardware tests:

- Build AMDGPU display support with DCN 3.5 enabled. Missing or renamed macros should fail in DCN35 DMUB, IRQ, link encoder, GPIO/DDC, or stream/audio register-table initialization.
- Mechanically verify in this line range that all in-range complete fields have matching `__SHIFT` and `_MASK` values, while accounting for the three `AFMT4_AFMT_AUDIO_PACKET_CONTROL2` masks whose shifts are just before line 33218 and the 19 `DC_GPIO_AUX_CTRL_1` shifts whose masks are just after line 35435.
- Diff the range against AMD's authoritative generated DCN 3.5.0 register database and nearby generated headers, especially DCN 3.2 or DCN 3.5.1 variants where the same AFMT4, DIG4, DP4, DCIO, UNIPHY, and GPIO register layouts are expected to match.
- Exercise HDMI and DisplayPort audio on DCN 3.5 hardware across modesets, plug/unplug, suspend/resume, sample-rate changes, multichannel LPCM, HBR/compressed formats, and audio sink changes. Watch for silent audio, wrong channel allocation, FIFO overflow, ACR instability, and packet-update failures.
- Exercise DisplayPort link training, MST, DSC, MSO, ALPM, metadata packets, and secondary data packet scheduling. Watch for training timeouts, CRC errors, missing HDR metadata, blank screens, underruns, MST slot-allocation mismatches, and ALPM wake failures.
- Exercise DDC/AUX/HPD paths across all exposed connectors. Validate EDID reads, DP AUX transactions, HPD IRQ/level detection, connector wake, panel backlight/PWRSEQ behavior, and resume after display power gating.
- Use register readback or debugfs traces where available to confirm DB pending/taken transitions, CRC done/result fields, DP MSA timing readbacks, DPHY training status, AFMT/DIG packet enables, and GPIO Y/A/EN state changes match the intended programming sequence.

## Cross-Chunk Notes

This chunk continues the AFMT4 audio packet-control/register family from the previous range and stops mid-`DC_GPIO_AUX_CTRL_1`. Adjacent chunks are required before making whole-file claims about all AFMT4 audio packet fields or all AUX control masks. The final merged per-file research should treat this as one slice of the broader DCN 3.5.0 generated shift/mask namespace rather than as an independent handwritten module.
