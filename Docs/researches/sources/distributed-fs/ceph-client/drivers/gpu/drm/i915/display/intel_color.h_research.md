# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_color.h

## Purpose
Declares the i915 display color management interface used by CRTC, atomic commit, modeset, and plane update code. The header hides generation-specific details behind stable entry points implemented in `intel_color.c`.

## Important APIs and types
It forward-declares display, CRTC, atomic, DSB, plane-state, property-blob, and pipe types. APIs cover lifecycle (`intel_color_init_hooks()`, `intel_color_init()`, `intel_color_crtc_init()`), atomic validation (`intel_color_check()`), commit sequencing (`prepare`, `cleanup`, `wait`, `commit_noarm`, `commit_arm`, `post_update`, `modeset`, `load_luts`), state readout/equality (`get_config`, `lut_equal`, `assert_luts`), and plane color programming (`intel_color_plane_program_pipeline()`, `intel_color_plane_commit_arm()`, `intel_color_crtc_has_3dlut()`).

## Control flow and integration
Callers first initialize display hooks and per-CRTC color properties, then use the check and commit helpers during atomic modesets and fast updates. Plane color code queries `intel_color_crtc_has_3dlut()` before binding 3D LUT state.

## State, dependencies, risks, and tests
The header owns no state, but its functions mutate `intel_crtc_state`, `intel_plane_state`, display hook tables, and hardware registers through implementation code. Risks are API-ordering mistakes: callers must pair prepare/wait/cleanup and respect no-arm/arm split. Tests should compile all display paths and exercise atomic color updates with and without DSB.
