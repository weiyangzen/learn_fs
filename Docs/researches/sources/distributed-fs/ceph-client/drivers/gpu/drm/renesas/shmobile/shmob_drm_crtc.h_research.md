# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_crtc.h

## Purpose

`shmob_drm_crtc.h` declares the legacy SH Mobile CRTC, connector wrapper, and CRTC/encoder/connector constructors.

## Important APIs, Types, and Functions

`struct shmob_drm_crtc` embeds `drm_crtc` and stores pending page-flip event/wait queue. `struct shmob_drm_connector` embeds `drm_connector`, stores a preferred encoder, and points to a fixed `videomode`. The header declares CRTC creation, page-flip completion, encoder creation, and connector creation.

## Control Flow

Driver modeset init calls the constructors, and IRQ handling calls `shmob_drm_crtc_finish_page_flip()` on vblank.

## State and Persistence Behavior

The CRTC persists in `shmob_drm_device`. Connector wrappers are dynamically allocated for platform-data mode and destroyed through connector funcs.

## Dependencies and Integration Points

It depends on DRM CRTC/connector/encoder headers and video mode definitions.

## Risks and Edge Cases

Event fields require DRM `event_lock` synchronization. The connector wrapper is only valid for platform-data fixed-panel mode.

## Test Signals

Compile coverage and page-flip event lifecycle tests validate the header contracts.
