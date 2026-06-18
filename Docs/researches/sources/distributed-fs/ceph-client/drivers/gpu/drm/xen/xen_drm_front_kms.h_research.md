# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front_kms.h

## Purpose

`xen_drm_front_kms.h` declares the simple-KMS interface for the Xen PV display frontend.

## Important APIs, Types, And Functions

It declares `xen_drm_front_kms_init()`, `xen_drm_front_kms_fini()`, and `xen_drm_front_kms_on_frame_done()` with forward declarations for frontend DRM info and pipeline types.

## Control Flow

The header has no runtime control flow.

## State And Persistence Behavior

No state is owned here; the declarations operate on state defined in `xen_drm_front.h`.

## Dependencies And Integration Points

It connects core DRM creation and event-channel frame-done dispatch to KMS implementation.

## Risks And Test Signals

Risk is signature drift. Build coverage and frame-done dispatch linkage validate it.
