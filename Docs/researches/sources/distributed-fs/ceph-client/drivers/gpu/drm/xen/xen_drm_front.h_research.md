# sources/distributed-fs/ceph-client/drivers/gpu/drm/xen/xen_drm_front.h

## Purpose

`xen_drm_front.h` defines shared state and protocol-facing APIs for the Xen PV DRM frontend.

## Important APIs, Types, And Functions

It documents buffer allocation modes and driver limitations, defines `XEN_DRM_FRONT_WAIT_BACK_MS`, and declares `struct xen_drm_front_info`, `struct xen_drm_front_drm_pipeline`, and `struct xen_drm_front_drm_info`. Inline cookie helpers convert framebuffer and GEM pointers to backend cookies. Function declarations cover mode set, display-buffer create, framebuffer attach/detach, page flip, frame-done notification, and GEM object free.

## Control Flow

No direct control flow. It defines the call graph used by KMS, GEM, event-channel, and core files.

## State And Persistence Behavior

The structs persist for the lifetime of the XenBus frontend and DRM device. `xen_drm_front_info` owns channels, config, and display-buffer list; per-pipeline state owns connector/pipe metadata, pending vblank event, delayed flip timeout work, and connection status.

## Dependencies And Integration Points

It depends on DRM connector/simple-KMS types, scatterlist support, and `xen_drm_front_cfg.h`. It is the shared contract across all Xen frontend source files.

## Risks And Test Signals

Risks include fixed limits (`XEN_DRM_FRONT_MAX_CRTCS`), pointer-as-cookie assumptions, and documented feature limitations such as primary-plane-only and fixed 60 Hz virtual modes. Compile coverage and multi-connector runtime tests validate struct and API alignment.
