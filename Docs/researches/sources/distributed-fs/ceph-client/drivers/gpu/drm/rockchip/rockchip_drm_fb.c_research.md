# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_drm_fb.c

## Purpose

`rockchip_drm_fb.c` installs Rockchip-specific DRM mode configuration and framebuffer creation. Its main addition over generic GEM framebuffer helpers is allocation of `struct drm_afbc_framebuffer` and initialization of AFBC metadata when the framebuffer modifier is AFBC.

## Important APIs, Types, and Functions

- `rockchip_drm_fb_funcs` uses generic GEM framebuffer destruction, GEM handle creation, and atomic dirtyfb handling.
- `rockchip_mode_config_helpers` selects `drm_atomic_helper_commit_tail_rpm`.
- `rockchip_fb_create()` allocates a `drm_afbc_framebuffer`, initializes the base GEM framebuffer, then calls `drm_gem_fb_afbc_init` for AFBC modifiers.
- `rockchip_drm_mode_config_init()` sets mode-config bounds, installs funcs/helpers, and enables normalized z-position.

## Control Flow

Driver setup calls `rockchip_drm_mode_config_init`. Userspace framebuffer creation enters `rockchip_fb_create`, which allocates the AFBC-capable wrapper, initializes GEM planes and format metadata, validates AFBC layout only when needed, and returns the base framebuffer. Error paths distinguish direct wrapper free from registered framebuffer put.

## State and Persistence Behavior

The mode-config callbacks persist for the DRM device lifetime. Each framebuffer owns GEM references through `drm_gem_fb_init_with_funcs`; AFBC metadata persists in the wrapper until `drm_gem_fb_destroy`. Normalized zpos makes atomic state carry explicit plane ordering for VOP/VOP2.

## Dependencies and Integration Points

The file depends on DRM framebuffer, GEM framebuffer, AFBC, damage, probe, and atomic helpers. It integrates with Rockchip GEM objects through included declarations and with VOP/VOP2 through framebuffer modifiers and z-position normalization.

## Risks and Edge Cases

AFBC state is assumed to be represented by modifier plane 0. The default 4096x4096 bounds may later be narrowed by VOP2 bind. AFBC allocation error paths must keep `kfree` and `drm_framebuffer_put` ownership distinct.

## Test Signals

Useful tests include linear and AFBC `ADDFB2` creation, malformed AFBC metadata rejection, GEM handle creation, dirtyfb dispatch, zpos normalization, and atomic commits under runtime PM suspend/resume.
