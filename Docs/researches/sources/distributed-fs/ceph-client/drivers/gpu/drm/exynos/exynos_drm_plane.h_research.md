# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_plane.h

## Purpose
This header exposes the common Exynos plane initialization API to Exynos display controller drivers. It is intentionally small: controller-specific files include it when they need to instantiate `struct exynos_drm_plane` objects with a static `struct exynos_drm_plane_config`.

## Important APIs, Types, and Functions
The only declaration is `int exynos_plane_init(struct drm_device *dev, struct exynos_drm_plane *exynos_plane, unsigned int index, const struct exynos_drm_plane_config *config);`. The referenced structures are defined in the Exynos DRM private headers, so this header acts as a cross-module contract rather than defining types itself.

## Control Flow
There is no executable control flow. At runtime, callers in mixer, VIDI, FIMD, DECON, and related Exynos display drivers call `exynos_plane_init()` during component bind or CRTC setup. The implementation then registers the DRM plane and attaches atomic helper callbacks.

## State and Persistence Behavior
The header stores no state. Its API transfers ownership expectations to the implementation: the caller must provide storage for `struct exynos_drm_plane`, a stable plane index, and a static or otherwise long-lived config describing supported formats, plane type, zpos, and capabilities.

## Dependencies and Integration Points
This header depends on prior declarations of `struct drm_device`, `struct exynos_drm_plane`, and `struct exynos_drm_plane_config` from the including source's header chain. It integrates the shared plane helper into all Exynos display blocks that expose DRM universal planes.

## Risks
Because the header has no include guard-local type declarations beyond the prototype, include order matters unless the including file already pulled in the Exynos DRM definitions. Passing a config with temporary lifetime is unsafe because `exynos_plane_init()` stores the pointer in the plane object. Incorrect indexes or capabilities propagate to hardware-specific update paths.

## Test Signals
Build coverage is the main signal for this header. Runtime signals come from every controller that calls `exynos_plane_init()`: successful plane enumeration, correct plane properties in modetest, and working atomic updates across all Exynos display backends.
