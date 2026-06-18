# sources/distributed-fs/ceph-client/drivers/gpu/drm/vkms/vkms_colorop.c

## Purpose

`vkms_colorop.c` creates the optional per-plane DRM color pipeline used by VKMS when the plane pipeline feature is enabled. It models a fixed chain of color operations that the composer later evaluates for each pixel.

## Important APIs and functions

`vkms_initialize_colorops()` creates and attaches a `COLOR_PIPELINE` property to a DRM plane. Internally, `vkms_initialize_color_pipeline()` allocates four `struct drm_colorop` objects: a 1D curve supporting sRGB EOTF and inverse EOTF, two 3x4 CTM operations, and a final 1D curve with the same supported transfer functions. Each operation allows bypass, and `drm_colorop_set_next_property()` links them in order. `vkms_colorop_funcs.destroy` delegates cleanup to DRM core.

## Control flow and state

The function allocates colorops, initializes each through DRM colorop helpers, records the first op id/name in a single enum list entry, then creates the plane property. On error it cleans already initialized ops and frees their memory. The persistent state lives in DRM plane/colorop objects and their property graph.

## Dependencies and integration

This file depends on DRM colorop, plane, property, and print helpers. It integrates with plane initialization and `vkms_composer.c`, where `pre_blend_color_transform()` traverses `plane_state->color_pipeline`, checks bypass state, and applies the corresponding LUT or matrix operation.

## Risks and test signals

Risks include partial allocation cleanup, leaked dynamically allocated pipeline names, mismatch between declared pipeline order and compositor evaluation, and unsupported colorop types. KUnit color tests cover the math helpers but not DRM property creation; integration tests should exercise plane initialization with `enable_plane_pipeline=1` and atomic commits that toggle colorop bypass/data.
