<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4.c

## Purpose
`hdmi4.c` is the OMAP4 HDMI display driver. It binds the HDMI wrapper, PLL, PHY, and HDMI4 core layers into a DRM bridge and OMAP DSS output, handles hotplug/core IRQs, powers the HDMI pipeline, reads EDID, manages CEC physical address updates, registers HDMI audio callbacks, and participates in the DSS component framework.

## Important APIs, types, and functions
Runtime power helpers are `hdmi_runtime_get()` and `hdmi_runtime_put()`. Display power sequencing is split between `hdmi_power_on_core()`, `hdmi_power_off_core()`, `hdmi_power_on_full()`, and `hdmi_power_off_full()`. DRM bridge callbacks are `hdmi4_bridge_attach()`, `hdmi4_bridge_mode_set()`, `hdmi4_bridge_enable()`, `hdmi4_bridge_disable()`, `hdmi4_bridge_hpd_notify()`, and `hdmi4_bridge_edid_read()`. Component lifecycle is `hdmi4_bind()` and `hdmi4_unbind()`, and platform lifecycle is `hdmi4_probe()` and `hdmi4_remove()`. Audio callbacks are exposed through `struct omap_hdmi_audio_ops`.

## Control flow
Probe allocates the bridge-embedded `struct omap_hdmi`, parses lanes, initializes wrapper, PHY, and core blocks, requests the IRQ, gets the `vdda` regulator, enables runtime PM, registers the DSS output, and adds the component. Bind obtains the parent DSS device, initializes the HDMI PLL, initializes optional CEC, registers the HDMI audio platform device, and installs debugfs.

Bridge mode set stores adjusted timings and updates DISPC TV pixel clock. Bridge enable derives HDMI or DVI mode from connector info, builds AVI infoframe data for HDMI sinks, powers the full path, restores cached audio configuration if present, and restarts audio if it was already playing. Full power-on enables the core regulator/runtime PM, selects HDMI clock routing in DSS, computes and programs the HDMI PLL, configures PHY, powers the PHY to LDO, configures wrapper/core video, enables the DSS manager, starts wrapper video, and enables link connect/disconnect IRQs.

IRQ handling acknowledges wrapper IRQs, handles simultaneous connect/disconnect by resetting PHY state, moves PHY to TXON or LDOON for hotplug transitions, and dispatches HDMI core CEC interrupt bit 3 through `hdmi4_cec_irq()`.

## State and persistence
The driver persists current video config in `hdmi->cfg`, core reference count in `core.core_pwr_cnt`, display enable state, cached audio configuration, audio playback state, debugfs handle, audio platform device, and regulator/runtime state. Hardware state spans DSS clock routing, HDMI PLL dividers, PHY power/configuration, wrapper timing and video enable, HDMI core video/audio registers, CEC registers, and IRQ masks.

## Dependencies and integration points
The file depends on DRM atomic bridge state, EDID helpers, OMAP DSS output/manager helpers, DISPC TV clock programming, common HDMI wrapper/PLL/PHY helpers, HDMI4 core helpers, optional CEC helpers, OMAP HDMI audio platform data, regulators, runtime PM, component framework, OF graph lane parsing, and debugfs.

## Risks
Power ordering is sensitive: core power, PLL, PHY, wrapper, DSS manager, video start, and IRQ enables must unwind correctly on errors. EDID reading temporarily enables the core if needed and uses `BUG_ON()` after runtime get, so unexpected PM failure is harsh. Audio callbacks use a spinlock for playback/display flags while configuration uses the mutex; lock use must avoid sleeping under spinlock. Hotplug IRQ handling changes PHY state directly and must keep CEC physical address invalidation in sync with connector state.

## Test signals
Signals include successful probe/bind, debugfs HDMI register dumps, hotplug connect/disconnect IRQs, EDID read and connector update, HDMI and DVI mode display, mode-set PLL/PHY programming, bridge enable/disable without leaks, audio startup/config/start/stop across display on/off transitions, CEC physical address updates, and suspend/resume or repeated hotplug stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi4.c -->
