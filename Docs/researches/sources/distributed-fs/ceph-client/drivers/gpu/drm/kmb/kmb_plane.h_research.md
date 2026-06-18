<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.h

## Purpose
Declares Keem Bay plane constants, layer IDs, sub-plane IDs, plane/private status structures, and plane creation/destruction APIs.

## Important APIs, types, and functions
Defines interrupt masks for VL0, VL1, GL0, GL1, combined DMA errors, `POSSIBLE_CRTCS`, `KMB_MAX_PLANES`, `enum layer_id`, `enum sub_plane_id`, `struct kmb_plane`, `struct layer_status`, `struct disp_cfg`, `kmb_plane_init()`, and `kmb_plane_destroy()`.

## Control flow
There is no executable control flow. The declarations shape the plane loops and IRQ handling in the C files.

## State and persistence
`struct layer_status` persists deferred disable state and related LCD control bits. `struct disp_cfg` persists first-use width, height, and format constraints for each plane.

## Dependencies and integration points
Includes DRM fourcc and plane definitions and relies on layer interrupt bits from `kmb_regs.h` through inclusion order in users.

## Risks
`POSSIBLE_CRTCS` is defined twice and `KMB_MAX_PLANES` is 2 despite four enumerated layer IDs. Any change here affects plane creation loops, IRQ array indexing, and underflow recovery behavior.

## Test signals
Build coverage and runtime creation of the expected number of planes are the main signals. Plane disable and DMA error recovery validate the status structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_plane.h -->
