<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge_regs.h

## Purpose
`vs_bridge_regs.h` maps VeriSilicon DC output-panel, DPI, DP, start, and commit registers used by `vs_bridge.c`.

## Important APIs, Types, and Functions
Important macros include `VSDC_DISP_PANEL_CONFIG(n)`, polarity and enable bits for DE/data/clock/running/YUV, `VSDC_DISP_DPI_CONFIG(n)` format fields, `VSDC_DISP_PANEL_START`, `VSDC_DISP_DP_CONFIG(n)` RGB/YUV format fields, and `VSDC_DISP_PANEL_CONFIG_EX(n)` commit bit.

## Control Flow
The bridge code writes these macros during atomic enable/disable. DPI mode clears DP enable and writes DPI format; DP mode writes DP format and YUV state; both paths start the panel and set commit.

## State and Persistence Behavior
These macros describe persistent MMIO state in the display controller. No software state lives here.

## Dependencies and Integration Points
The header depends on Linux bit macros and is included by the bridge implementation. It must match the DC register map and the regmap max range in `vs_dc.c`.

## Risks
Incorrect bit positions can invert polarity, disable outputs, or select a wrong bus format. Format constants are shared with the DP media-bus mapping and must stay synchronized.

## Test Signals
Register-write trace tests for DPI/DP enable and disable, plus hardware validation for RGB/YUV bus formats and polarity flags, validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge_regs.h -->
