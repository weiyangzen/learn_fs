# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.c

## Purpose

`xen_drm_front_cfg.c` reads the XenStore display configuration supplied by the backend/domain config.

## Important APIs, Types, And Functions

The public function is `xen_drm_front_cfg_card()`. The internal helper `cfg_connector()` reads a connector path and parses its `resolution` field into width and height.

## Control Flow

Configuration starts by checking whether backend allocation is advertised through `XENDISPL_FIELD_BE_ALLOC`. It scans connector indices from 0 through `XEN_DRM_FRONT_MAX_CRTCS - 1`, stopping at the first missing or malformed connector resolution. At least one connector must be present or the call returns `-ENODEV`.

## State And Persistence Behavior

It fills `struct xen_drm_front_cfg`: `front_info`, `be_alloc`, `num_connectors`, per-connector dimensions, and devm-allocated XenStore connector paths. This state persists through event-channel creation and KMS initialization.

## Dependencies And Integration Points

It depends on XenBus reads, Xen display protocol field names, DRM logging, and `xen_drm_front_cfg.h`. The core file calls it during backend `InitWait`.

## Risks And Test Signals

Risks include accepting only contiguous connector indices, rejecting malformed resolution strings, and trusting backend-provided dimensions. Test by varying XenStore resolution entries, missing connector 0, backend allocation flag, and maximum connector count.
