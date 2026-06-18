# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi_common.c

## Purpose
`hdmi_common.c` provides shared helpers used by OMAP4 and OMAP5 HDMI drivers: DT lane parsing and HDMI audio clock regeneration N/CTS calculation.

## Important APIs, types, and functions
The exported helpers are `hdmi_parse_lanes_of` and `hdmi_compute_acr`. `hdmi_parse_lanes_of` reads an endpoint `lanes` property of eight `u32` values or falls back to identity lane order, then delegates validation and mapping to `hdmi_phy_parse_lanes`. `hdmi_compute_acr` maps sample frequencies to HDMI N values and derives CTS from pixel clock, N, and deep-color percentage.

## Control Flow
Lane parsing checks property length, reads the array, and reports DT parse errors through the platform device. With no property, it uses lanes `{0..7}` and treats validation failure as unexpected. ACR computation validates output pointers, sets deep color to the currently hard-coded 100 percent path, chooses standard N values for 32, 44.1, 48, 88.2, 96, 176.4, and 192 kHz, and computes CTS with integer arithmetic.

## State and Persistence
No global state is held. Lane parsing writes into the caller-owned `struct hdmi_phy_data`. ACR values are returned through caller-provided `u32` pointers and later persisted in HDMI core registers by HDMI4/5 audio code.

## Dependencies and Integration Points
The file depends on OF property APIs, `hdmi.h`, `omapfb_dss.h`, and the HDMI PHY parser. `hdmi4_core.c` and `hdmi5_core.c` both use `hdmi_compute_acr`; `hdmi5.c` uses the lane parser during DT probe.

## Risks
The lane property must contain exactly eight cells. Deep-color handling is stubbed to 100 percent, so future 30/36-bit modes need this calculation revisited. CTS calculation uses integer division and assumes `pclk` in Hz and supported sample frequencies only.

## Test Signals
DT tests with missing, valid, and malformed lane arrays; PHY lane/polarity outcomes; ACR N/CTS comparisons against HDMI spec tables; invalid sample frequency handling; and audio playback at all supported rates are the main signals.
