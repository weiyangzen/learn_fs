# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_cfg.h

## Purpose

`xen_drm_front_cfg.h` defines the frontend's parsed XenStore display configuration.

## Important APIs, Types, And Functions

It defines `XEN_DRM_FRONT_MAX_CRTCS` as 4, `struct xen_drm_front_cfg_connector` with width, height, and XenStore path, `struct xen_drm_front_cfg` with connector array and `be_alloc`, and declares `xen_drm_front_cfg_card()`.

## Control Flow

No runtime control flow exists in the header.

## State And Persistence Behavior

The config struct is stored inside `struct xen_drm_front_info` and persists across channel publishing and DRM/KMS setup.

## Dependencies And Integration Points

It depends on Linux types and is shared by the core, config reader, and KMS pipeline initialization.

## Risks And Test Signals

Risks are fixed connector capacity and assumptions that dimensions are valid for DRM mode creation. Build coverage and XenStore-driven multi-connector tests are the main signals.
