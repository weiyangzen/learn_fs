<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-pe.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-pe.h

Purpose: Declares i.MX8 DC pixel-engine link IDs, common shadow/clock bits, subblock structures, and public pixel-engine helper APIs.

Important APIs/types/functions: Defines `enum dc_link_id`, `enum dc_lb_mode`, `enum dc_pec_clken`, `struct dc_cf`, `struct dc_ed`, `struct dc_lb`, and `struct dc_pe`. Declares constframe, extdst, and layerblend functions.

Control flow: Header only.

State and persistence behavior: Structures represent hardware subblocks and runtime aggregation pointers; link IDs encode hardware routing identifiers.

Dependencies: Linux clk/device/regmap and `dc-de.h` for display count.

Integration points: Used by constframe, extdst, layerblend, fetchunit, plane, CRTC, pixel-engine, and aggregate driver code.

Risks: Link IDs are hardware ABI constants. Any incorrect value misroutes the pixel pipeline. Array counts constrain how many fetchunits/layerblends the driver can address.

Test signals: Visual scanout through constframe/fetchunit/layerblend/extdst paths and build coverage across all DC pixel-engine files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-pe.h -->
