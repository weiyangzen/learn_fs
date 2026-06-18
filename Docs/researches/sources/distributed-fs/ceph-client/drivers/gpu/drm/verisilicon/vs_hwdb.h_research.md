<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.h

## Purpose
`vs_hwdb.h` declares the hardware database structures for VeriSilicon DC capability selection.

## Important APIs, Types, and Functions
It defines `struct vs_formats`, `struct vs_chip_identity`, and `vs_fill_chip_identity()`. `struct vs_chip_identity` carries model, revision, customer ID, display count, and a pointer to supported DRM formats.

## Control Flow
Probe code fills a `vs_chip_identity` through `vs_fill_chip_identity()` and later CRTC/plane code consults its display count and format array.

## State and Persistence Behavior
The populated identity persists in `struct vs_dc`. Format arrays are static data owned by the implementation.

## Dependencies and Integration Points
The header depends on regmap and fixed-width types. It integrates DC probe with plane format advertisement and output creation.

## Risks
Consumers trust `formats` to be non-NULL and `display_count` to fit `VSDC_MAX_OUTPUTS`. Future capability fields must preserve initialization for existing entries.

## Test Signals
Compile tests plus hardware identity probing and plane creation with the selected format list validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_hwdb.h -->
