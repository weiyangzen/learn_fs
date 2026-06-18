# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.h

## Purpose

`vc4_mock.h` declares the VC4 KUnit mock helpers and small wrapper structs used by mock CRTC/output construction and atomic-state manipulation.

## Important APIs, Types, and Functions

- `vc4_find_crtc_for_encoder`: inline helper that asserts a single possible CRTC and returns it.
- `struct vc4_dummy_crtc` and `struct vc4_dummy_output`: test wrappers around production `vc4_crtc`, `vc4_encoder`, and DRM connector.
- Constructors: `vc4_dummy_plane`, `vc4_mock_pv`, `vc4_dummy_output`, `vc4_mock_device`, and `vc5_mock_device`.
- Atomic helpers: `vc4_mock_atomic_add_output` and `vc4_mock_atomic_del_output`.

## Control Flow

KUnit tests include this header to build a mock device and manipulate outputs in atomic states without depending on physical hardware.

## State and Persistence Behavior

No state is stored in the header, but it defines test object layouts used for DRM-managed allocations and container conversions.

## Dependencies and Integration Points

It includes `vc4_drv.h` and is shared by all VC4 KUnit mock/test files.

## Risks and Edge Cases

The inline CRTC lookup asserts exactly one possible CRTC; tests for shared encoders would need a different helper. Wrapper layout must stay compatible with production `vc4_encoder` and `vc4_crtc` expectations.

## Test Signals

Compile all KUnit mock files, run PV muxing suites, and add coverage when production encoder/CRTC structures change.
