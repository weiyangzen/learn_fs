# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4.c

## Purpose

This file implements the OMAP4 HDMI DSS output driver. It binds the HDMI wrapper, PLL, PHY, and HDMI4 core helpers into an `omap_dss_device`, handles full/core-only power transitions, EDID reads, HDMI/DVI infoframe mode, hotplug IRQ PHY state, runtime PM, and an `omap-hdmi-audio` child device. The complete 812-line source was read.

## Important APIs, Types, and Functions

State is the single static `struct omap_hdmi hdmi` declared in `hdmi.h`. Important functions include `hdmi_runtime_get()/put()`, `hdmi_irq_handler()`, `hdmi_init_regulator()`, `hdmi_power_on_core()`, `hdmi_power_off_core()`, `hdmi_power_on_full()`, `hdmi_power_off_full()`, display timing callbacks, `hdmi_display_enable()/disable()`, `hdmi_core_enable()/disable()`, `hdmi_connect()/disconnect()`, `hdmi_read_edid()`, `hdmi_set_infoframe()`, `hdmi_set_hdmi_mode()`, `hdmi_probe_of()`, HDMI audio callbacks, `hdmi_audio_register()`, `hdmi4_bind()/unbind()`, runtime PM callbacks, and platform driver init/uninit.

The registered `omapdss_hdmi_ops` supplies connect, disconnect, enable, disable, timing check/set/get, EDID read, infoframe set, and HDMI mode set. Audio registration supplies `omap_hdmi_audio_ops` for startup, shutdown, start, stop, and config.

## Control Flow

Component bind initializes the global state, parses optional DT lane data, initializes wrapper/PLL/PHY/core blocks, requests the HDMI IRQ, enables runtime PM, registers the HDMI output, registers the audio child platform device, and creates debugfs. Connect lazily initializes the VDDA regulator, connects the DIGIT overlay manager, and links the downstream display.

Full display enable locks `hdmi.lock`, verifies a manager, powers core resources, clears/disables IRQs, computes HDMI PLL settings from the configured pixel clock, enables/configures the PLL, configures PHY, powers PHY to LDO, configures HDMI4 core/wrapper, disables TV gamma, sets manager timings, starts wrapper video, enables the manager, and enables connect/disconnect IRQs. Disable stops audio, clears IRQs, disables the manager, stops video, powers PHY off, disables PLL, drops runtime PM, and disables VDDA.

EDID reads use core-only power if full display power is not already active. The IRQ handler acknowledges wrapper IRQs and moves PHY power among off, LDO, and TX states for connect/disconnect, with a special restart sequence when both bits are set. Audio callbacks require HDMI mode with display enabled, cache audio config, start/stop wrapper/core audio under a spinlock, and abort cached audio if display re-enable cannot restore it.

## State and Persistence Behavior

State is volatile and global for one HDMI4 instance: current timings/infoframe/mode, regulator pointer, `core_enabled`, display/audio enabled flags, cached audio config, audio callback pointer, output registration, child audio platform device, and wrapper idle mode. Hardware state includes PLL/PHY/core/wrapper registers, DISPC TV pixel clock, DSS HDMI/VENC source mux, manager timing/enable, IRQ masks, and regulator/runtime PM state. There is no file persistence.

## Dependencies and Integration Points

The file depends on HDMI4 core helpers, HDMI wrapper/PLL/PHY/common helpers, DSS clock muxing, DISPC runtime and TV pixel clock, OMAP DSS manager/output APIs, Linux regulators, IRQs, runtime PM, OF graph, component framework, and OMAP HDMI audio platform data. It integrates with panels/connectors through `omapdss_hdmi_ops`, with sound through the `omap-hdmi-audio` platform child, and with debugfs via `dss_debugfs_create_file()`.

## Risks and Edge Cases

The global `hdmi` object implies one HDMI4 instance. `read_edid()` uses `BUG_ON()` if runtime PM resume fails. `hdmi_power_on_full()` returns `-EIO` for several distinct lower-level failures, losing detailed error codes. Audio shutdown writes `audio_playing` under the mutex rather than the audio spinlock used elsewhere, so lock ordering and races should be reviewed carefully. IRQ hotplug handling assumes wrapper IRQ semantics and PHY power commands succeed in interrupt context. Runtime PM for HDMI proxies DISPC PM, so imbalance affects both blocks.

## Test Signals

Test probe/bind/unbind, regulator deferral, DT lane parsing, connect/disconnect to HDMI displays, EDID reads before and during display enable, HDMI and DVI modes, common CEA/VESA timings, PLL/PHY failure injection, hotplug connect/disconnect IRQs including simultaneous bits, runtime suspend/resume, audio startup/config/start/stop/shutdown, display disable while audio is playing, and debugfs HDMI dumps.
