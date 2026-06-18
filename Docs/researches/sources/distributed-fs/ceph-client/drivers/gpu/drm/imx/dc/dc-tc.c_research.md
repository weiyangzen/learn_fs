<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-tc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-tc.c

Purpose: Implements the i.MX8 DC Timing Controller subdevice, setting bypass/default control and pixel map bits for output format mapping.

Important APIs/types/functions: Exports `dc_tc_init()` and platform driver `dc_tc_driver`.

Control flow: Bind maps registers, creates regmap, identifies the display instance by MMIO base, and stores it in `dc_drm->tc[]`. Init resets `TCON_CTRL` to the power-on default and bulk-writes MAPBIT registers so internal 30-bit BGR pixels are presented as 30-bit RGB.

State and persistence behavior: `struct dc_tc` stores device and regmap. Register state is restored on display-engine runtime resume.

Dependencies: Component/platform/regmap frameworks and DC display-engine declarations.

Integration points: Display-engine post-bind attaches timing controllers to `dc_de`; runtime resume calls `dc_tc_init()`. KMS bridge lookup uses the tcon device-tree node for each CRTC output.

Risks: MAPBIT values are hardware-format ABI. Wrong mapping causes color channel or bit-order errors. Base-address id mapping is SoC-specific.

Test signals: Probe of both tcon instances, color-channel visual tests, bridge output modeset, and runtime resume register checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-tc.c -->
