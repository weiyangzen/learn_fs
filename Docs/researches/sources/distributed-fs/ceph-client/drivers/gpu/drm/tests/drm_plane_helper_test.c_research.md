# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_plane_helper_test.c

## Purpose
Parameterized KUnit tests for `drm_atomic_helper_check_plane_state()`. The file validates clipping, positioning, rotation/reflection-aware source adjustment, scaling limits, and invalid plane-state rejection.

## Important APIs, Types, And Functions
The static `crtc_state` models an active 1024x768 CRTC. `struct drm_check_plane_state_test` describes input source/destination rectangles, expected clipped rectangles, rotation, scale bounds, and positioning permission. `drm_plane_helper_init()` creates mock plane/framebuffer/plane-state objects for each parameter. `check_src_eq()` and `check_crtc_eq()` compare helper-produced fixed-point source and integer destination rectangles.

## Control Flow
Valid test cases call `drm_atomic_helper_check_plane_state()` and expect zero, visible state, and exact source/destination rectangles. Cases cover simple clipping, 90-degree rotation with reflection, allowed positioning, exact 2x upscaling/downscaling, and fixed-point rounding boundaries. Invalid cases expect negative return for prohibited positioning or scale factors outside configured min/max.

## State And Persistence
State is one KUnit-allocated mock plane, framebuffer, and plane state per parameter. The framebuffer is 2048x2048. No persistent state is used.

## Dependencies And Integration Points
The suite directly exercises DRM atomic plane helper clipping/scaling logic and uses DRM rect helpers and rotation flags. It protects behavior used by many atomic KMS drivers before programming hardware plane state.

## Risks And Maintenance Notes
Expected fixed-point values are sensitive to clipping and rounding policy. Changing helper rounding, visible-state rules, or rotation handling will produce exact-value failures. The mock CRTC uses `ZERO_SIZE_PTR` for pointers because only geometry is relevant; helper changes that dereference more CRTC fields could require a richer fixture.

## Test Signals
Signals are helper return values, `plane_state->visible`, exact fixed-point source rectangle, exact destination rectangle, non-negative source coordinates, and negative errors for invalid positioning/upscale/downscale cases.
