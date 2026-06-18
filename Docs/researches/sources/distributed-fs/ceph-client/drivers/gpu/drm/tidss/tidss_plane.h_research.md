# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_plane.h

## Purpose

`tidss_plane.h` defines the TIDSS plane wrapper and plane creation/error APIs shared between KMS setup, DISPC programming, and IRQ handling.

## Important APIs, Types, and Functions

- `to_tidss_plane()` converts `struct drm_plane *` to `struct tidss_plane *`.
- `struct tidss_plane` embeds a DRM plane and stores the hardware plane ID.
- `tidss_plane_create()` creates a primary or overlay plane with the supplied CRTC mask and format list.
- `tidss_plane_error_irq()` reports hardware underflow for a plane.

## Control Flow

`tidss_kms.c` creates planes through this header. `tidss_irq.c` converts stored plane pointers through `to_tidss_plane()` to match IRQ bits and logs errors through `tidss_plane_error_irq()`. Plane helper callbacks use the hardware ID to call DISPC plane APIs.

## State and Persistence Behavior

The hardware plane ID is persistent and immutable after creation. DRM plane state is managed by the DRM core.

## Dependencies and Integration Points

It includes DRM plane definitions and forward declares `struct tidss_device`. It is consumed by KMS, IRQ, and plane implementation files.

## Risks and Edge Cases

- The hardware ID is a raw `u32`; caller-supplied feature-table ordering must be correct.
- `to_tidss_plane()` assumes the pointer really belongs to a TIDSS plane.

## Test Signals

Build coverage should catch API changes. Runtime coverage should verify plane IDs match DISPC registers and IRQ underflow bits for each feature-table `vid_order`.
