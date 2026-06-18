# sources/distributed-fs/ceph-client/include/media/rcar-fcp.h

## Purpose
Declares the Renesas R-Car Frame Compression Processor helper API used by display/video drivers.

## Important APIs, Types, and Functions
The header forward-declares `struct rcar_fcp_device` and exposes `rcar_fcp_get()`, `rcar_fcp_put()`, `rcar_fcp_get_device()`, `rcar_fcp_enable()`, `rcar_fcp_disable()`, and `rcar_fcp_soft_reset()`. Stubs return `ERR_PTR(-ENOENT)`, `NULL`, or success/no-op when `CONFIG_VIDEO_RENESAS_FCP` is disabled.

## Control Flow
Client drivers obtain the FCP from a device-tree node, enable it before using dependent processing/display hardware, optionally soft-reset it, disable it afterward, and release the reference during teardown.

## State and Persistence Behavior
FCP device state is owned by the implementation and persists with platform device/runtime PM lifetime. The header is a client contract.

## Dependencies and Integration Points
Integrates Renesas VSP/display/media drivers with a shared FCP block.

## Risks
Enable/disable imbalance can break power management or shared hardware access. Clients must handle `-ENOENT` and `NULL` stub behavior gracefully when FCP support is absent.

## Test Signals
Probe with and without FCP, runtime PM transitions, repeated enable/disable, soft reset behavior, stream/display start-stop, and remove cleanup.
