<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fu.h

Purpose: Declares common i.MX8 DC fetchunit constants, structures, operations, and helper APIs.

Important APIs/types/functions: Defines per-fraction register offset stride, fetchunit control bitfield macros, `enum dc_fu_frac`, fetchunit ids, `struct dc_fu_ops`, and `struct dc_fu`. Declares common ops and helper functions.

Control flow: Header only.

State and persistence behavior: `struct dc_fu` stores register maps, per-fraction register offsets, ids, link id, operation table, and associated layerblend pointer.

Dependencies: Linux bitfield/bits/regmap/types, DRM fourcc, and DC pixel-engine link enums.

Integration points: Used by `dc-fl.c`, `dc-fw.c`, `dc-fu.c`, `dc-plane.c`, and pixel-engine aggregation.

Risks: Register offset arrays must be populated by each concrete fetchunit before common ops run. API changes affect both fetchlayer and fetchwarp drivers.

Test signals: Build coverage and primary-plane atomic update using concrete fetchunit ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-fu.h -->
