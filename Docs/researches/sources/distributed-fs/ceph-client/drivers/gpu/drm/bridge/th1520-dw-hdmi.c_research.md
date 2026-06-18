# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/th1520-dw-hdmi.c

Purpose: provides the T-Head TH1520 platform wrapper for the Synopsys DesignWare HDMI bridge. The file supplies TH1520-specific PHY programming tables, a mode-valid limit, clock/reset acquisition, and `dw_hdmi_probe()` / `dw_hdmi_remove()` integration for the SoC HDMI encoder.

Important APIs/types/functions: `struct th1520_hdmi_phy_params` stores max pixel clock and six PHY register values. `th1520_hdmi_phy_params[]` maps clock ceilings up to 594 MHz to PHY opmode, PLL current, divider, clock-symbol, voltage, and termination settings. `struct th1520_hdmi` stores `dw_hdmi_plat_data`, `dw_hdmi` handle, pixel clock, and main/APB resets. `th1520_hdmi_mode_valid()` rejects modes above 594 MHz. `th1520_hdmi_phy_set_params()` writes the PHY I2C registers through DesignWare helper APIs. `th1520_hdmi_phy_configure()` selects the first table row whose max clock covers the requested pixel clock.

Control flow: probe allocates the wrapper, enables the `pix` clock, obtains and deasserts `main` and `apb` resets, fills `dw_hdmi_plat_data` with output port 1, mode-valid callback, PHY configuration callback, and private data, calls `dw_hdmi_probe()`, and stores driver data. Remove retrieves driver data and calls `dw_hdmi_remove()`.

State and persistence: persistent state is minimal: the enabled clock and deasserted reset controls are devm-managed, and the `dw_hdmi` pointer represents the registered DesignWare HDMI instance. PHY register values persist in hardware until reconfigured or reset. No mode or connector state is stored by this wrapper.

Dependencies and integration points: depends on the DRM `dw_hdmi` bridge library, platform devices, managed clocks, reset controls, OF compatible `thead,th1520-dw-hdmi`, and the DesignWare PHY I2C write API. Most HDMI protocol, connector, EDID, and atomic behavior is delegated to the shared DesignWare HDMI implementation.

Risks: the probe error check after `dw_hdmi_probe()` tests `IS_ERR(hdmi)` instead of the returned `hdmi->dw_hdmi`, which can miss a failed DesignWare probe and store an error pointer. Remove retrieves driver data as `struct dw_hdmi *`, but probe stores `struct th1520_hdmi *`, so `dw_hdmi_remove()` may receive the wrong pointer type. PHY table selection is ceiling-based and must remain sorted by `mpixelclock`. Clocks below the first table entry use the 35.5 MHz row; clocks above 594 MHz are rejected by mode validation and by PHY configure fallback.

Test signals: platform probe/remove on TH1520 DT; failure injection for `pix` clock, `main` reset, `apb` reset, and `dw_hdmi_probe()`; 594 MHz mode acceptance and higher-clock rejection; PHY register writes for common CEA modes; and runtime remove/unbind to catch driver-data pointer type issues.
