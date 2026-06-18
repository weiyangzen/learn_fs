# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/head.h

## Purpose
Declares NVIF display head objects and vblank event construction.

## Important APIs, Types, And Functions
Defines `struct nvif_head`, `nvif_head_ctor/dtor`, `nvif_head_id`, and `nvif_head_vblank_event_ctor`.

## Control Flow
Display enumeration constructs head objects by id. Vblank event construction attaches event callbacks with optional wait behavior.

## State And Persistence
Head object state is the embedded NVIF object/handle and persists while the DRM CRTC/head exists.

## Dependencies And Integration Points
Depends on `nvif/object.h`, `nvif/event.h`, and `nvif_disp`; integrated with DRM CRTC and vblank handling.

## Risks
Incorrect head id mapping breaks CRTC-to-hardware routing or vblank delivery.

## Test Signals
CRTC enumeration, vblank IRQ delivery, modesets, and event teardown validate behavior.
