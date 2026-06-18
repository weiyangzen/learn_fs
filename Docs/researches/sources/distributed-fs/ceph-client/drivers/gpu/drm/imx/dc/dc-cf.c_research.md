<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-cf.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-cf.c

Purpose: Implements i.MX8 DC ConstFrame subdevices, which generate constant-color frame sources for content and safety display streams.

Important APIs/types/functions: Exports `dc_cf_get_link_id()`, `dc_cf_framedimensions()`, `dc_cf_constantcolor_black()`, `dc_cf_constantcolor_blue()`, and `dc_cf_init()`. The platform driver is `dc_cf_driver`.

Control flow: Component bind allocates `struct dc_cf`, maps the `cfg` register region, creates a regmap, identifies the instance from the register start address, assigns the hardware link id, and stores it in either `dc_drm->cf_cont[]` or `dc_drm->cf_safe[]`. Runtime helpers write frame size, color, and shadow-enable state.

State and persistence behavior: Per-instance state is a regmap plus link id. Register state includes shadow-enable, frame dimensions, and constant color, and is reinitialized by pixel-engine runtime resume.

Dependencies: Uses component framework, platform resources, regmap-mmio, and shared DC link IDs from `dc-pe.h`.

Integration points: CRTCs use content constframes for black background and safety constframes for blue safety stream. Planes use constframe link ids as layerblend primary inputs and extdst fallback sources.

Risks: Instance identification is hard-coded to physical resource starts. Unsupported device-tree address changes will break binding. Wrong link id assignment misroutes the display pipeline.

Test signals: Probe with all four constframe nodes, CRTC enable with no plane showing black content/blue safety streams, register write tracing, and runtime resume restoring `SHDEN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-cf.c -->
