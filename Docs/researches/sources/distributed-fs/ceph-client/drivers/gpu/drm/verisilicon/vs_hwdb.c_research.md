<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.c

## Purpose
`vs_hwdb.c` maps VeriSilicon DC model/revision/customer identity registers to driver capabilities, currently display count and supported DRM framebuffer formats.

## Important APIs, Types, and Functions
The public function is `vs_fill_chip_identity(struct regmap *regs, struct vs_chip_identity *ident)`. Static data includes RGB format arrays with and without YUV444 capability placeholders, `struct vs_formats` instances, and `vs_chip_identities[]` for DC8200 revisions/customer IDs.

## Control Flow
The function reads model, revision, and customer ID from top registers, linearly searches the identity table, matches either exact customer ID or wildcard `~0U`, copies the identity into the caller, overwrites the customer ID with the actual hardware value, and returns 0. No match returns `-EINVAL`.

## State and Persistence Behavior
The table is static read-only driver data. The selected `vs_chip_identity` persists in `struct vs_dc` and feeds output count, pixel-clock lookup count, and plane format list.

## Dependencies and Integration Points
The file depends on regmap reads, DRM fourcc constants, top-register definitions, and `vs_hwdb.h`. `vs_dc_probe()` uses it before creating CRTCs and planes.

## Risks
Wildcard entries can shadow more specific entries if ordered incorrectly. The `with_yuv444` and `no_yuv444` arrays are currently identical aside from TODO comments, so advertised capabilities may not yet reflect hardware YUV support. Unsupported revisions fail probe entirely.

## Test Signals
Mock regmap tests should cover exact match, wildcard match, unknown identity, table ordering, actual customer ID preservation, and format-list selection used by primary-plane init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.c -->
