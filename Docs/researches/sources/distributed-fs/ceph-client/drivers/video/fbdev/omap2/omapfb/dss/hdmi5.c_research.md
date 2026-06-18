# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi5.c

## Purpose
`hdmi5.c` is the fbdev OMAP DSS platform/component driver for OMAP5/DRA7 HDMI. It binds wrapper, PLL, PHY, and HDMI5 core helpers into an `omap_dss_device` output, handles runtime PM and regulators, services link connect/disconnect IRQs, exposes EDID/timing/infoframe operations, and registers the `omap-hdmi-audio` child platform device.

## Important APIs, types, and functions
The file uses the global `static struct omap_hdmi hdmi`. Key functions are `hdmi_power_on_core`, `hdmi_power_on_full`, `hdmi_power_off_full`, timing operations, `read_edid`, display enable/disable, core enable/disable, connect/disconnect, HDMI ops, audio callbacks, `hdmi5_bind`, `hdmi5_unbind`, runtime PM callbacks, and platform driver init/uninit. It integrates `hdmi_wp_init`, `hdmi_pll_init`, `hdmi_phy_init`, `hdmi5_core_init`, `dss_pll_*`, and `dss_mgr_*`.

## Control Flow
Component bind initializes locks, parses DT lane mapping, maps wrapper/PLL/PHY/core resources, requests the IRQ, enables runtime PM, registers the output, registers HDMI audio, and creates debugfs. Display enable locks the HDMI singleton, powers the core and regulator, computes and enables the PLL, configures PHY and link power, calls `hdmi5_configure`, programs DISPC manager timings, starts wrapper video, enables the manager, and unmasks link IRQs. Disable reverses manager, video, PHY, PLL, runtime PM, and regulator state. EDID can temporarily core-enable the hardware. Audio startup/config/start/stop are allowed only in HDMI mode with display enabled.

## State and Persistence
Runtime state is in the global `hdmi`: current `hdmi_config`, output object, `core_enabled`, `display_enabled`, audio configuration/playback flags, saved wrapper idle mode, regulator pointer, component resources, and mapped register blocks. Hardware state persists in wrapper, PLL, PHY, core, and DISPC registers while powered.

## Dependencies and Integration Points
Dependencies include component framework, runtime PM, regulator and clock APIs, OF graph lane parsing, DSS manager/output APIs, DISPC runtime, debugfs, HDMI wrapper/PLL/PHY/core libraries, and the OMAP HDMI audio platform interface.

## Risks
The global singleton model assumes one HDMI5 instance. Error unwinding partly shares a generic `err` path and must keep PLL registration, output registration, runtime PM, and audio child lifetime consistent. The IRQ handler manipulates PHY power and pad force bits from interrupt context. Audio callbacks depend on spinlock/mutex ordering and display state.

## Test Signals
Test with OMAP5 and DRA7 DT compatibles, lane remapping, EDID reads before and after enable, HDMI/DVI mode toggles, hotplug connect/disconnect and simultaneous IRQ cases, display enable error injection at PLL/PHY/video/manager stages, suspend/resume, audio startup/config/play/stop across display off/on, and debugfs HDMI dumps.
