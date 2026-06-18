## sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_dp.c

### Purpose

`mtk_dp.c` is the MediaTek DisplayPort/eDP bridge driver for MT8188 and MT8195 families. It owns DP register access, AUX transfers, HPD handling, link capability parsing, PHY calibration and configuration, link training, video timing setup, bridge atomic format negotiation, audio packet programming, HDMI-codec registration, eDP panel linking, and suspend/resume power sequencing.

### Important APIs, types, and functions

Core state is `struct mtk_dp`, containing enable/HPD state, RX DPCD caps, calibration data, bridge/connector/AUX objects, train info, video/audio info, PHY/regmap devices, debounce timer, HDMI-codec callback state, and platform data. `struct mtk_dp_data` selects connector type, secure monitor command, efuse layout, audio support, audio packet placement, and audio divider bits.

Major function groups are register helpers (`mtk_dp_read/write/update_bits()`), video setup (`mtk_dp_set_msa()`, `mtk_dp_set_color_format()`, `mtk_dp_setup_encoder()`, `mtk_dp_video_config()`), AUX (`mtk_dp_aux_do_transfer()`, `mtk_dp_aux_transfer()`), IRQ/HPD (`mtk_dp_hpd_event()`, `mtk_dp_hpd_event_thread()`), calibration/PHY (`mtk_dp_get_calibration_data()`, `mtk_dp_phy_configure()`), link training (`mtk_dp_training()`, `mtk_dp_train_cr()`, `mtk_dp_train_eq()`), bridge ops, and HDMI-codec ops.

### Control flow

Probe allocates a DRM bridge, parses MMIO/data-lanes/max-linkrate, requests threaded HPD IRQ for external DP, initializes `drm_dp_aux`, optionally registers HDMI-codec audio, registers a child DP PHY platform device, configures bridge type, and either populates the eDP AUX bus and panel bridge or registers a hotpluggable DP bridge. Runtime PM is enabled and held active.

Bridge attach registers AUX, powers on DP, attaches a downstream bridge, and enables IRQs for external DP. Atomic check records input bus format as RGB or YUV422 and converts adjusted mode to `videomode`. Atomic enable powers eDP AUX/panel if needed, performs eDP training, programs MSA/color, unmutes video, configures audio if EDID SADs/audio are present, updates plugged status, and marks eDP enabled. Atomic disable marks eDP disabled, powers eDP panel off, updates audio plug status, mutes video/audio, resets SDP path, and waits for sink mute.

External DP HPD IRQs are split into a hard IRQ that clears hardware/software IRQ state and records cable/event bits under a spinlock, and a threaded handler that debounces, emits DRM HPD events, powers AUX, parses capabilities, runs link training on connect, or disables audio/AUX and starts debounce on disconnect.

### State and persistence behavior

Persistent software state includes `enabled`, `need_debounce`, `train_info`, RX caps, calibration data, current video format/timing, current audio capabilities, and HDMI-codec callback pointers. Hardware state persists across register blocks: PHY power, AUX engine, HPD thresholds, MSA, pattern generator, video/audio mute, SDP packets, lane count, swing/pre-emphasis, FEC/scrambler, and PLL/lane PHY configuration. Suspend powers down DP and disables IRQs; resume reinitializes port settings and power.

### Dependencies

The driver depends on DRM bridge, atomic, DP helper, AUX bus, EDID, panel, and probe helper APIs; Linux regmap, PHY, NVMEM, OF graph, IRQ, PM, timer, and ARM SMCCC APIs; HDMI codec audio; and `mtk_dp_reg.h`. It relies on secure monitor calls for video mute/unmute and on the `mediatek-dp-phy` child driver for PHY programming.

### Integration points

It registers as a DRM bridge with detect/EDID/HPD ops for external DP and as an eDP bridge only after a panel is found. AUX is used for EDID, DPCD, link training, and eDP panel power. The MediaTek DPI/DP-INTF path negotiates input bus formats with this bridge, allowing YUV422 when RGB888 bandwidth is too high but YUV422 fits. HDMI-codec callbacks expose DP audio to ALSA.

### Risks

AUX transactions are timing-sensitive and return NACK on unsupported requests, timeouts, or PHY hang; failures can break EDID and training. Link training downshifts link rate and lane count, but repeated failures end in `-ETIMEDOUT` or `-EIO`. eDP capability caching assumes fixed panel capabilities during a boot. Video mute uses secure monitor commands, so firmware behavior is part of display correctness. Audio capability parsing only tracks SAD count and monitor-audio detection, with FIXME comments around newer EDID handling. Probe holds runtime PM active, so power-management changes need care.

### Test signals

Validate external DP hotplug/unplug, HPD IRQ events, EDID reads through AUX, DPCD capability parsing, link training at 1/2/4 lanes and multiple link rates, fallback after CR/EQ failure, eDP AUX-bus panel discovery, suspend/resume, YUV422 bus-format fallback for bandwidth-limited modes, audio ELD and HDMI-codec playback, secure mute/unmute, and nvmem calibration fallback/default paths.
