<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.h

## Purpose

`sun4i_layer.h` declares the DE1 layer plane structures and conversion helpers shared by the backend layer implementation and related pipeline code.

## Important APIs, Types, And Functions

`struct sun4i_layer` embeds a `drm_plane`, backend pointer, driver pointer, and hardware layer id. `struct sun4i_layer_state` extends `drm_plane_state` with `pipe` and `uses_frontend`; `uses_frontend` records whether the frontend was part of the committed plane path. Inline helpers `plane_to_sun4i_layer()` and `state_to_sun4i_layer_state()` implement container conversions. `sun4i_layers_init()` is the exported initializer.

## Control Flow

The header has no executable flow. Its inline conversions are used by DRM plane callbacks to recover driver-private state from generic DRM objects.

## State And Persistence Behavior

The structures persist as DRM plane objects and atomic plane states. `uses_frontend` is copied during duplicate-state and read during disable/update to decide whether frontend teardown is required. `pipe` is present as private state but is not manipulated in the researched implementation.

## Dependencies And Integration Points

It forward-declares `struct sunxi_engine` and relies on DRM plane types through consumers. It is included by `sun4i_layer.c` and any code that needs DE1 plane-private state.

## Risks And Test Signals

Risks are mostly ABI drift within the driver: changing struct layout or state fields requires matching reset/duplicate/destroy callbacks. Test by building all sun4i DRM code and exercising atomic plane duplication/destruction with KMS plane updates that enter and leave frontend usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun4i_layer.h -->
