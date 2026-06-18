# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.h

## Purpose
Declares the single color pipeline initializer used when setting up DRM planes.

## APIs and integration
`intel_color_pipeline_plane_init(struct drm_plane *plane, enum pipe pipe)` attaches supported color pipeline/colorop properties to a plane. It is consumed by plane initialization code and implemented in `intel_color_pipeline.c`.

## State, dependencies, risks, and tests
The header owns no state. It depends only on `struct drm_plane` and `enum pipe` declarations. The main risk is missing initialization from plane setup, which would leave HDR color UAPI unavailable. Compile tests and plane property enumeration tests are the primary signals.
