# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rcar-du/rcar_du_kms.h

## Purpose

`rcar_du_kms.h` declares the KMS-facing format descriptor and core KMS helper APIs for mode-set initialization, dumb-buffer creation, and PRIME SG-table import.

## Important APIs, Types, and Functions

- `struct rcar_du_format_info` stores DRM fourcc, V4L2 format, bits per pixel, plane count, horizontal subsampling, and DU register fields.
- `rcar_du_format_info()` returns a format descriptor for a DRM fourcc.
- `rcar_du_modeset_init()` initializes all KMS objects for a DU device.
- `rcar_du_dumb_create()` and `rcar_du_gem_prime_import_sg_table()` are exported to DRM driver operations.

## Control Flow

The header is used by the platform driver to wire DRM callbacks and start KMS initialization, and by plane/CRTC code to retrieve format programming data.

## State and Persistence Behavior

No state is stored here. Format descriptors are immutable data in `rcar_du_kms.c`.

## Dependencies and Integration Points

- Forward declares DRM/GEM/DMA-buf types and `struct rcar_du_device`.
- Used by driver, CRTC, plane, and KMS implementation files.

## Risks and Edge Cases

- `pnmr` and `edf` fields are register-level details; consumers must apply generation-specific restrictions before programming them.

## Test Signals

- Format lookup tests should ensure every format exposed by direct-DU planes has a descriptor and unsupported formats return NULL.
