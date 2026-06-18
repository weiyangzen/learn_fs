# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_kms.h

## Purpose

`rzg2l_du_kms.h` declares KMS-level format metadata and entry points for RZ/G2L DU mode setting and dumb-buffer creation.

## Important APIs, Types, and Functions

`struct rzg2l_du_format_info` maps DRM fourcc to V4L2 format, plane count, and horizontal subsampling. The public functions are `rzg2l_du_format_info()`, `rzg2l_du_modeset_init()`, `rzg2l_du_dumb_create()`, and a declared GEM prime SG import helper.

## Control Flow

Driver probe calls `rzg2l_du_modeset_init()`. Framebuffer creation and VSP plane setup call `rzg2l_du_format_info()`. DRM dumb-buffer ioctl handling uses `rzg2l_du_dumb_create()`.

## State and Persistence Behavior

No state is owned here; it defines static format metadata interfaces.

## Dependencies and Integration Points

It forward-declares DRM and DMA-buf types and is included by CRTC/VSP/KMS implementation files.

## Risks and Edge Cases

The declared `rzg2l_du_gem_prime_import_sg_table()` is not implemented in this subset, so link coverage should confirm no stale reference exists or an implementation is elsewhere.

## Test Signals

Compile/link tests and format lookup coverage for every advertised VSP format.
