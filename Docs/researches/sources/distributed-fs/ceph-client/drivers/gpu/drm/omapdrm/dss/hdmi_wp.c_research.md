# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi_wp.c

Purpose: Implements the HDMI wrapper register helper layer for IRQs, PHY/PLL power commands, video start/stop, timing/interface programming, audio DMA/FIFO programming, and DMA address discovery.

Important APIs/functions: IRQ helpers get/ack/enable/disable wrapper IRQ status. `hdmi_wp_set_phy_pwr()` and `hdmi_wp_set_pll_pwr()` issue power commands and poll status fields with timeout. `hdmi_wp_video_config_format()`, `hdmi_wp_video_config_interface()`, `hdmi_wp_video_config_timing()`, and `hdmi_wp_init_vid_fmt_timings()` translate `videomode`/`hdmi_config` into wrapper registers, including interlace and double-clock adjustments. `hdmi_wp_video_start()` enables video, while `hdmi_wp_video_stop()` waits for frame done. Audio helpers configure format, DMA block/transfer size, threshold, DMA mode, and audio/core request enable bits. `hdmi_wp_init()` maps the `wp` resource and stores physical base/version.

Control flow: HDMI full enable clears IRQs, powers PLL/PHY, configures core and wrapper, then starts video. Full disable clears IRQs, stops wrapper video, disables manager and PHY/PLL. Audio config/start paths program wrapper DMA and toggle audio enable bits.

State and persistence: `struct hdmi_wp_data` stores mapped base, physical base, and version. Register state persists only while the hardware is powered. Top-level drivers cache idlemode and audio state.

Dependencies/integration: Shared by HDMI4 and HDMI5. Uses common HDMI register helpers, DSS logging, wrapper register definitions from `hdmi.h`, and top-level IRQ/audio/video paths.

Risks and test signals: Power command polling failures return `-ETIMEDOUT`; video stop logs if FRAMEDONE never arrives after up to about one second. OMAP4 and OMAP5 differ in HSW programming. Test enable/disable cycles, frame-done on stop, PLL/PHY timeout injection, interlaced/double-clock timing, IRQ ack flushing, and audio DMA address correctness.
