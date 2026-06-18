# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_crtc.c

## Purpose

`vc4_mock_crtc.c` constructs dummy VC4 CRTCs for KUnit by wrapping production CRTC state management and atomic check callbacks around `__vc4_crtc_init`.

## Important APIs, Types, and Functions

- `vc4_dummy_crtc_helper_funcs`: uses production `vc4_crtc_atomic_check`.
- `vc4_dummy_crtc_funcs`: uses production state reset/duplicate/destroy functions.
- `vc4_mock_pv`: allocates `vc4_dummy_crtc` with DRM managed memory and initializes it with supplied CRTC data and primary plane.

## Control Flow

Mock topology construction creates a primary plane, then calls `vc4_mock_pv` for each pixel valve. The resulting CRTC participates in production atomic checking while avoiding hardware register setup.

## State and Persistence Behavior

The dummy CRTC is DRM-managed for the mock device lifetime. Its state is production `vc4_crtc_state`, allowing tests to inspect assigned HVS channels.

## Dependencies and Integration Points

It depends on DRM atomic helper vtables, KUnit assertions, `__vc4_crtc_init`, and production VC4 CRTC data.

## Risks and Edge Cases

If production CRTC init gains mandatory hardware resources, the mock may need new stand-ins. The helper currently supplies no enable/disable callbacks, so tests should remain check-only unless extended.

## Test Signals

PV muxing tests should create all mock CRTCs successfully and exercise `vc4_crtc_atomic_check` through `drm_atomic_check_only`.
