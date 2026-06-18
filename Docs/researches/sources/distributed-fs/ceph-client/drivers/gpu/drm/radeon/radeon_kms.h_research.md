<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.h

## Purpose

`radeon_kms.h` is a small private KMS header that declares the Radeon KMS vblank callback functions implemented in `radeon_kms.c`. It lets DRM driver setup and IRQ/vblank code refer to the KMS-specific vblank counter and enable/disable hooks without exposing the broader Radeon mode header.

## Important APIs, Types, and Functions

- `u32 radeon_get_vblank_counter_kms(struct drm_crtc *crtc)`: returns a DRM-adjusted frame counter for a CRTC.
- `int radeon_enable_vblank_kms(struct drm_crtc *crtc)`: enables vblank interrupt delivery for a CRTC.
- `void radeon_disable_vblank_kms(struct drm_crtc *crtc)`: disables vblank interrupt delivery for a CRTC.
- Include guard `__RADEON_KMS_H__` prevents duplicate declaration.

## Control Flow

The header has no runtime control flow. It establishes compile-time linkage from DRM driver tables or IRQ setup code to the KMS vblank implementations. Callers pass `struct drm_crtc *`; the implementation maps that CRTC to a Radeon pipe and IRQ state.

## State and Persistence Behavior

No state is stored here. The declared functions operate on persistent DRM CRTC objects and `rdev->irq` state in the implementation.

## Dependencies and Integration Points

It assumes users already have DRM CRTC type visibility through surrounding includes. The declared functions integrate with DRM core vblank callbacks and Radeon IRQ state in `radeon_irq_kms.c`/`radeon_kms.c`.

## Risks and Edge Cases

The header is intentionally narrow. Signature drift between this header and `radeon_kms.c` would break driver callback wiring at build time. Adding broader declarations here would increase coupling with unrelated KMS internals.

## Test Signals

Build coverage is the primary test signal. Runtime validation comes from DRM vblank tests that exercise the declared functions through driver callback tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_kms.h -->
