<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fl.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fl.c

Purpose: Implements the FetchLayer fetchunit instance used by the i.MX8 DC primary-plane display path.

Important APIs/types/functions: Defines a `struct dc_fl` wrapper around `struct dc_fu`, specialized `dc_fl_set_fmt()`, `dc_fl_set_framedimensions()`, `dc_fl_init()`, and platform driver `dc_fl_driver`.

Control flow: Bind maps the `cfg` register space, initializes a fetchunit regmap, identifies the instance, fills all per-fraction register offsets, assigns link id `LINK_ID_FETCHLAYER0`, installs operations derived from `dc_fu_common_ops`, and stores the fetchunit in `dc_drm->fu_disp[]`.

State and persistence behavior: Fetchunit state is mostly hardware register state and the `dc_fu` structure. Init applies common defaults and sticky shadow-load requests across all fractions.

Dependencies: Shared fetchunit helpers, DRM fourcc format info, component/platform/regmap frameworks, and DC link IDs.

Integration points: `dc_plane_init()` picks fetchunit instances from the pixel engine. Plane atomic update uses its ops to set stride, dimensions, format, base address, frame dimensions, and enable source buffers.

Risks: Only XRGB8888 is currently exposed by the plane path, and `dc_fl_set_fmt()` assumes format lookup succeeds. Hard-coded register layout and instance address must match SoC hardware.

Test signals: Primary-plane scanout using FetchLayer0, format programming inspection, runtime PM reinit through pixel engine, and invalid/missing fetchlayer device tree tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fl.c -->
