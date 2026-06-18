# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color_pipeline.c

## Purpose
Exposes DRM plane color pipeline objects for HDR-capable i915 planes. It builds a chain of DRM colorops representing pre-CSC 1D LUT, 3x4 CSC, optional 3D LUT, and post-CSC 1D LUT blocks.

## Important APIs and functions
`intel_color_pipeline_plane_init()` is the exported initializer. Internal helpers include `plane_has_3dlut()`, `_intel_color_pipeline_plane_init()`, and `intel_color_pipeline_plane_add_colorop()`. Static pipeline arrays define the HDR plane chain and the Xe3/PLPD primary-plane chain with 3D LUT. The file uses `intel_colorop_create()` and `intel_colorop_destroy()` for object lifetime and DRM helpers such as `drm_plane_colorop_curve_1d_lut_init()`, `drm_plane_colorop_ctm_3x4_init()`, `drm_plane_colorop_3dlut_init()`, and `drm_plane_create_color_pipeline_property()`.

## Control flow
Initialization skips non-HDR planes. For HDR planes it selects a pipeline based on display version, pipe 3D LUT capability, and primary-plane type, allocates each colorop in order, links adjacent colorops through the `next` property, creates a named pipeline enum entry, then publishes the plane color pipeline property. On failure it walks back and destroys already-created colorops.

## State and integration
The persistent state is DRM object state attached to the plane: colorop objects, their next links, and the color pipeline property. It integrates new DRM color pipeline UAPI with hardware programming in `intel_color_plane_program_pipeline()`.

## Risks and test signals
Risks include exposing unsupported 3D LUT sharing, leaking allocated pipeline names or colorops on partial failure, and mismatches between exposed pipeline order and actual hardware programming. Tests should cover property enumeration on HDR/non-HDR planes, primary vs non-primary Xe3 pipelines, object cleanup, and atomic commits using each colorop.
