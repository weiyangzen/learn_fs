# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_plane.c

## Purpose

`vc4_mock_plane.c` creates dummy primary planes for VC4 KUnit mock devices.

## Important APIs, Types, and Functions

- `vc4_dummy_plane`: asserts the requested plane type is primary and delegates to `drm_kunit_helper_create_primary_plane`.

## Control Flow

Mock pipe construction calls this before creating the dummy CRTC. The returned DRM plane is attached to the CRTC by `vc4_mock_pv`.

## State and Persistence Behavior

The plane is KUnit/DRM-helper managed for the test lifetime. No file-local state exists.

## Dependencies and Integration Points

It depends on DRM KUnit helpers and the mock header. It intentionally only supports `DRM_PLANE_TYPE_PRIMARY` because the muxing tests do not need overlay/cursor planes.

## Risks and Edge Cases

Tests requesting non-primary planes will assert. Production code changes that require plane formats/modifiers in atomic checks may need richer mock plane setup.

## Test Signals

Build KUnit mocks and create every mock VC4/VC5 pipe; failures here surface as mock-device construction assertions.
