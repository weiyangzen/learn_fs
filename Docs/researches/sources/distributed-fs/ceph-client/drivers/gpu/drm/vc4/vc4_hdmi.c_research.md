# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.c

## Purpose

`vc4_hdmi.c` is the main HDMI controller driver for Broadcom VC4/VC5/VC6 Raspberry Pi display hardware. It binds the platform HDMI component into DRM, exposes an HDMI connector and TMDS encoder, programs video timing/CSC/infoframe/packet RAM state, handles hotplug and SCDC scrambling, provides HDMI audio through ASoC and the DRM HDMI audio helper, optionally registers CEC, manages runtime PM and clocks, and selects SoC-specific behavior through `struct vc4_hdmi_variant`.

## Important APIs, Types, and Functions

- Connector entry points: `vc4_hdmi_connector_detect_ctx()`, `vc4_hdmi_connector_get_modes()`, `vc4_hdmi_connector_atomic_check()`, `vc4_hdmi_connector_reset()`, and `vc4_hdmi_connector_init()` integrate with DRM connector, HDMI state helper, EDID/DDC, TV margins, colorspace, broadcast RGB, audio, and mode validation.
- HDMI infoframe support is implemented through `vc4_hdmi_clear_infoframe()`, `vc4_hdmi_write_infoframe()`, and typed wrappers for AVI, vendor HDMI, audio, HDR DRM, and SPD frames. `vc4_hdmi_hdmi_connector_funcs` wires these into the DRM HDMI connector helper.
- Encoder operations are split across the VC4 encoder staging hooks: `vc4_hdmi_encoder_pre_crtc_configure()` powers the block and configures clocks/PHY/timings, `vc4_hdmi_encoder_pre_crtc_enable()` applies CSC and FIFO mode, `vc4_hdmi_encoder_post_crtc_enable()` enables video, packet RAM, infoframes, FIFO recentering, and scrambling, while `vc4_hdmi_encoder_post_crtc_disable()` and `vc4_hdmi_encoder_post_crtc_powerdown()` blank/disable video, scrambling, PHY, clocks, and runtime PM.
- Clock, timing, and format helpers include `vc4_hdmi_mode_needs_scrambling()`, `vc4_hdmi_connector_clock_valid()`, `vc4_hdmi_encoder_atomic_check()`, `vc4_hdmi_encoder_mode_valid()`, `vc4_hdmi_set_timings()`, `vc5_hdmi_set_timings()`, `vc4_hdmi_csc_setup()`, and `vc5_hdmi_csc_setup()`.
- Audio support is implemented through `vc4_hdmi_audio_startup()`, `vc4_hdmi_audio_prepare()`, `vc4_hdmi_audio_shutdown()`, `vc4_hdmi_audio_init()`, `vc4_hdmi_audio_set_mai_clock()`, `vc4_hdmi_set_n_cts()`, `sample_rate_to_mai_fmt()`, channel-map helpers, ASoC DAI/card setup, and DRM HDMI audio callbacks.
- Optional CEC support under `CONFIG_DRM_VC4_HDMI_CEC` includes threaded IRQ handlers, message packing/unpacking, `vc4_hdmi_cec_enable()`, `vc4_hdmi_cec_disable()`, `vc4_hdmi_cec_adap_log_addr()`, `vc4_hdmi_cec_adap_transmit()`, `vc4_hdmi_cec_init()`, and `vc4_hdmi_cec_register()`.
- Resource/probe paths include `vc4_hdmi_init_resources()` for BCM2835-style register maps, `vc5_hdmi_init_resources()` for named VC5/VC6 register regions, `vc4_hdmi_runtime_suspend()`, `vc4_hdmi_runtime_resume()`, `vc4_hdmi_bind()`, `vc4_hdmi_dev_probe()`, `vc4_hdmi_dev_remove()`, and the exported `vc4_hdmi_driver`.
- Variant records for BCM2835, BCM2711 HDMI0/HDMI1, and BCM2712 HDMI0/HDMI1 provide register tables, max pixel clocks, lane mapping, PHY functions, reset/timing/CSC callbacks, odd horizontal timing restrictions, HPD path, HDR support, audio card names, and IRQ-controller topology.

## Control Flow

Component bind allocates `struct vc4_hdmi`, initializes locks and delayed scrambling work, resolves resources through the variant, acquires DDC and optional HPD GPIO, enables runtime PM, initializes encoder and connector objects, registers hotplug IRQs, CEC, and audio. Runtime resume enables HSM/audio clocks, verifies HSM is nonzero to avoid CPU stalls on uninitialized firmware clock state, resets the hardware, and initializes CEC divider/masks.

Hotplug detection resumes runtime PM, reads GPIO or hardware HPD, calls `drm_atomic_helper_connector_hdmi_hotplug()`, and, when connected, may call `vc4_hdmi_reset_link()`. The link reset path locks connection and CRTC state, checks whether the current active mode needs SCDC scrambling, compares sink SCDC status, and requests a full CRTC reset if the sink and source are out of sync.

The modeset enable path saves adjusted mode and HDMI output format in `atomic_mode_set`, then `pre_crtc_configure` raises runtime PM, sets HSM/pixel/BVB clocks, updates the CEC divider, initializes the PHY, enables manual scheduler format mode, and writes timing registers. `pre_crtc_enable` configures CSC and FIFO master/slave. `post_crtc_enable` enables video output, switches HDMI/DVI scheduler mode, enables packet RAM for HDMI sinks, updates infoframes, recenters the FIFO, and enables SCDC scrambling for HDMI 2.0 rates.

Disable runs in the reverse direction: packet RAM is marked disabled, video is blanked and optionally disabled, SCDC scrambling is disabled, PHY is disabled, pixel clocks are turned off, and runtime PM is released. Audio and CEC have their own enable/disable paths but share the same HDMI state and MMIO lock discipline.

## State and Persistence

Persistent driver state is in `struct vc4_hdmi`: connector/encoder objects, DDC adapter, MMIO bases, clocks, reset line, debugfs regsets, hotplug GPIO, CEC message/IRQ state, audio card state, delayed scrambling work, `saved_adjusted_mode`, packet RAM and SCDC state, output bpc/format, and the ALSA jack. State is not persisted to disk; it is live kernel device state reconstructed at bind/probe and runtime resume.

Concurrency is split between `mutex`, protecting cross-framework HDMI state used by KMS/ALSA/CEC, and `hw_lock`, a spinlock protecting register writes and many read-modify-write sequences. Most MMIO access is guarded by `drm_dev_enter()` and runtime PM; CEC interrupt paths explicitly rely on IRQ lifetime being tied to the platform device rather than the DRM device.

## Dependencies and Integration Points

This file depends heavily on DRM atomic helpers, DRM HDMI connector/audio/CEC helpers, EDID/DDC, SCDC, debugfs regsets, Linux component framework, runtime PM, clocks, resets, GPIO descriptors, OF device tree, ASoC, DMAEngine PCM, and local VC4 helpers in `vc4_drv.h`, `vc4_hdmi.h`, `vc4_hdmi_regs.h`, and `vc4_regs.h`. It integrates with `vc4_hdmi_phy.c` through variant PHY callbacks, with HVS/KMS through encoder hooks and mode validation, and with platform matching through `of_device_id`.

## Risks and Edge Cases

- Incorrect runtime PM or clock sequencing can stall the CPU, especially when firmware leaves HSM clock rate at zero.
- SCDC scrambling is stateful across source and sink; stale sink state is handled by forcing a full modeset, but races with hotplug and commits are delicate.
- Packet RAM writes require packet RAM enabled and packet idle polling; infoframe length or stale bytes can trigger analyzer checksum failures.
- Audio registration intentionally uses devm ASoC lifetimes while relying on DRM-managed `vc4_hdmi` lifetime plus `drm_dev_enter()` to avoid removed-device MMIO.
- CEC message packing reads/writes groups of four bytes; malformed lengths over 16 are rejected, but short messages rely on `cec_msg` storage being safe for grouped access.
- BCM2712 has a TODO around disabling `VID_CTL_ENABLE` after blanking because it can lock up.
- Odd horizontal timings, WiFi coexistence clock adjustment, HDMI 2.0 core-clock enable flags, and 4096x2160 limits are hardware/platform policy embedded in atomic validation.

## Test Signals

Useful signals include DRM/KUnit tests for PV muxing and mock KMS paths elsewhere in the vc4 tree, debugfs register dumps from `*_regs`, `hvs_underrun` interactions for display stability, EDID/mode probing with HDMI 1.4 vs HDMI 2.0 clocks, hotplug/CEC IRQ exercise, ALSA playback through HDMI with 2/8-channel PCM and HBR status, SCDC scrambling status at >340 MHz TMDS, and suspend/resume/remove races verified by lack of `drm_dev_enter()` failures or PM warnings.
