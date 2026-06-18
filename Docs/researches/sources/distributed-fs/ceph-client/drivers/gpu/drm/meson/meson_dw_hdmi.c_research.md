# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_dw_hdmi.c

Purpose: Implements the platform glue driver for Amlogic Meson Synopsys DesignWare HDMI TX. It owns HDMI TOP register access, DesignWare controller register access, PHY setup, HPD interrupt handling, component bind/unbind, runtime state for reset/clock resources, and suspend/resume restoration.

Important APIs, types, and functions: `struct meson_dw_hdmi_data` abstracts SoC-specific TOP/DWC register access and PHY init values. `struct meson_dw_hdmi` stores DRM-private state, MMIO base, reset controls, `dw_hdmi` handle, bridge pointer, and last IRQ status. Register access helpers include legacy indirect `dw_hdmi_top_read/write()` and `dw_hdmi_dwc_read/write()` plus direct G12A variants. DRM/bridge entry points are `meson_dw_hdmi_bind()`, `meson_dw_hdmi_unbind()`, and platform `probe/remove`. PHY callbacks are exported through `meson_dw_hdmi_phy_ops`.

Control flow: probe only registers the component. During bind the driver resolves match data, enables optional HDMI regulator, gets reset lines and clocks, maps HDMITX MMIO, creates a regmap for the DW core, requests the shared threaded IRQ, runs `meson_dw_hdmi_init()`, then calls `dw_hdmi_probe()`. PHY init selects 4:2:0 mode when required by sink or bus format, programs TOP TMDS clock patterns, configures HHI PHY registers from pixel clock thresholds, resets PHY three times, briefly disables ENCI/ENCP video, restores HDMI write clock bits, and routes ENCI or ENCP into HDMI-TX.

State and persistence: mutable state is hardware-centric: HHI register programming, TOP interrupt masks/status, reset lines, enabled clocks, `irq_stat`, bridge references, and `priv->venc.hdmi_use_enci`. Suspend asserts TOP reset; resume reruns initialization and calls `dw_hdmi_resume()`. Clock resources are devm-managed with action cleanup.

Dependencies and integration points: depends on Linux component framework, reset/clock/regulator APIs, `regmap`, DRM bridge helpers, `dw_hdmi`, EDID/SCDC helpers, Meson DRM private `hhi` and `io_base`, and register definitions from `meson_dw_hdmi.h` and `meson_registers.h`. It integrates with the HDMI encoder bridge, which supplies VENC/VCLK setup and bus format decisions.

Risks: register access is protected by one global spinlock, but G12A direct accesses bypass it. PHY constants are SoC-specific magic values with limited validation. HPD interrupt top-half returns `IRQ_NONE` when only core interrupt bit is set, relying on DW core behavior. `of_drm_find_and_get_bridge()` result is stored after `dw_hdmi_probe()` and must be released on unbind. PLL/PHY/4:2:0 interactions are timing-sensitive and hardware-revision dependent.

Test signals: boot/probe on GXBB/GXL/GXM/G12A DT compatibles, HDMI HPD connect/disconnect events, EDID reads, 480i/576i ENCI modes, progressive ENCP modes, 4:2:0-only sinks, suspend/resume with display attached, and DRM debug traces for selected TMDS division and VENC source.
