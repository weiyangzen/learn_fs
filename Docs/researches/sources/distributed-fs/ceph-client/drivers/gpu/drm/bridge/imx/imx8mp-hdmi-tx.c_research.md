# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-tx.c

# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-tx.c

## Purpose

This driver adapts the generic Synopsys DW HDMI bridge to the i.MX8MP HDMI TX block. It provides mode validation, PHY ops, optional component binding for the audio PAI block, and probe/remove glue.

## Important APIs, Types, And Functions

`struct imx8mp_hdmi` stores DW HDMI platform data, returned `dw_hdmi`, and pixel clock. Important functions are `imx8mp_hdmi_mode_valid()`, `im8mp_hdmi_phy_setup_hpd()`, `imx8mp_dw_hdmi_probe/remove()`, `imx8mp_dw_hdmi_bind/unbind()`, and system resume.

## Control Flow

Probe gets the pixel clock, fills DW HDMI platform data, and checks graph port 2 for the optional PAI component. Without PAI it probes DW HDMI immediately; with PAI it registers as component master and probes DW HDMI after child components bind. Mode validation rejects below 13.5 MHz, above 297 MHz, pixel clocks the generator cannot round within 0.5 percent, double-clocked modes, and interlaced modes. PHY setup releases PHY reset and delegates HPD handling to DW HDMI helpers.

## State And Persistence Behavior

State is in the private struct and DW HDMI core object. No hardware mode state is cached here; DW HDMI and PHY drivers manage detailed registers. Resume calls `dw_hdmi_resume()`.

## Dependencies And Integration Points

It depends on common clocks, component framework, DW HDMI bridge library, OF graph, and the Samsung HDMI PHY via forced vendor PHY ops. PAI integration is optional through graph port 2.

## Risks And Test Signals

Risks include mode rejection due to strict pixel-clock rounding, duplicate graph lookup in remove, no suspend work beyond resume, and dependency on component ordering for audio. Test signals are DW HDMI probe success, HPD detection, mode validation for common CEA/VESA modes, resume after system sleep, and HDMI audio when PAI is present.
