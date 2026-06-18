# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r600_hdmi.c

## Purpose

`r600_hdmi.c` programs HDMI audio support for R600-era display engines. It reads the hardware audio pin status, updates HDMI audio infoframes and ACR values, configures audio packets, DTO clocks, AVI/VBI packets, mute state, HDMI stream routing, and AFMT IRQ enablement for digital encoders.

## Important APIs, Types, and Functions

- `enum r600_hdmi_color_format` and `enum r600_hdmi_iec_status_bits`: local symbolic values for HDMI color mode and IEC60958 channel-status bits.
- `r600_audio_status`: samples `R600_AUDIO_RATE_BPS_CHANNEL` and `R600_AUDIO_STATUS_BITS` into `struct r600_audio_pin` fields: channels, bits per sample, rate, status bits, and category code.
- `r600_audio_update_hdmi`: workqueue callback that detects audio-status changes and refreshes all digital HDMI-capable encoders when audio state or buffer fill status changes.
- `r600_audio_enable` and `r600_audio_get_pin`: enable audio pins through `AZ_HOT_PLUG_CONTROL`; R6xx-NI exposes one pin.
- `r600_hdmi_update_acr`: writes ACR CTS/N values for 32, 44.1, and 48 kHz families, using a DCE3-specific control register when needed.
- `r600_set_avi_packet`, `r600_hdmi_update_audio_infoframe`, `r600_set_vbi_packet`, and `r600_set_audio_packet`: program HDMI infoframe and packet-control registers.
- `r600_hdmi_buffer_status_changed`, `r600_hdmi_audio_set_dto`, `r600_set_mute`, `r600_hdmi_update_audio_settings`, and `r600_hdmi_enable`: manage audio buffer state, audio DTO selection, AVMUTE, infoframe refresh, HDMI routing, and AFMT IRQs.

## Control Flow

Audio polling begins in `r600_audio_update_hdmi`, which reads current audio hardware status and compares it with cached `rdev->audio.pin[0]`. If changed, it updates the cache. It then walks the DRM encoder list, skips non-digital encoders, and calls `r600_hdmi_update_audio_settings` when global audio fields changed or the per-encoder HDMI audio buffer fill status toggled.

HDMI audio settings update checks that the encoder has an enabled AFMT block, reads current audio status, initializes and packs a standard `hdmi_audio_infoframe`, disables HDMI audio test mode if set, acknowledges HDMI errors, selects software audio infoframe source, writes audio infoframe payload registers, and enables continuous audio infoframe update.

Enabling HDMI first validates `dig` and `dig->afmt`. On pre-DCE3 hardware it manually sets HDMI enable/routing bits based on the encoder object id for TMDSA, LVTMA, DDIA, or DVOA and writes `HDMI0_CONTROL`. If IRQs are installed, it enables or disables AFMT IRQs. Finally it records `dig->afmt->enabled`.

Packet setup helpers write fixed control bits for null/general-control packets, audio sample packets, audio infoframe line, generic packet disablement, and IEC60958 channel numbers. DTO setup chooses DTO0 or DTO1 based on `dig_encoder` and derives module from the pixel clock.

## State and Persistence Behavior

Cached audio state persists in `rdev->audio.pin[0]`. Per-encoder AFMT state includes `enabled` and `last_buffer_filled_status`. Hardware register state persists in HDMI, audio, DTO, hotplug, and encoder routing registers. No dynamic memory is allocated here; infoframe buffers are stack-local.

## Dependencies and Integration Points

This file depends on Linux HDMI infoframe helpers, DRM encoder/mode lists, Radeon encoder/private structures, Radeon audio state, AFMT IRQ helpers, DCE version macros, Atom encoder ids, and R600/DCE register definitions from `r600.h`/`r600d.h`. It integrates with the display mode-setting path, Radeon audio workqueue, hotplug/audio enable handling, and interrupt management.

## Risks and Edge Cases

- `r600_set_avi_packet` and `r600_hdmi_update_audio_infoframe` assume caller-provided buffers are large enough for the fixed byte offsets.
- Audio-rate decoding supports only the hardware register encoding this generation exposes; unknown sample-size encodings fall back to 16 bits with an error.
- `r600_hdmi_update_audio_settings` reads fresh hardware status instead of the cached pin, so workqueue ordering with audio changes matters.
- Manual pre-DCE3 routing depends on encoder ids; new or unusual encoder mappings can log an error and leave routing incomplete.
- AFMT IRQ enablement is conditional on IRQ installation, so polling/buffer-status behavior must remain correct without IRQs.
- DTO math multiplies by 100 and assumes clocks fit expected ranges.

## Test Signals

Signals include HDMI audio playback at 44.1/48 kHz families, channel-count changes, hotplug enable/disable, suspend/resume, mute toggling, AFMT interrupt delivery, buffer status changes, pre-DCE3 encoder routing across TMDS/LVTMA/DDI/DVO outputs, and infoframe validation with HDMI analyzers or receiver diagnostics. Regression tests should include no-IRQ fallback and disabled-encoder paths.
