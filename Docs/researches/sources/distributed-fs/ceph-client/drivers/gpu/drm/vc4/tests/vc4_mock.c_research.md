# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock.c

## Purpose

`vc4_mock.c` builds synthetic VC4 and VC5 DRM devices for KUnit tests. It creates mock CRTCs, primary planes, encoders, connectors, HVS state, runs VC4 KMS load, registers the DRM device, and returns a ready `struct vc4_dev`.

## Important APIs, Types, and Functions

- Mock descriptors: `vc4_mock_output_desc`, `vc4_mock_pipe_desc`, and `vc4_mock_desc` describe pixel valves and their outputs.
- Static mock topologies: `vc4_mock` and `vc5_mock` model VC4/VC5 CRTC-output combinations.
- `__build_one_pipe` and `__build_mock`: create dummy primary plane, CRTC, and outputs for each pipe.
- `__mock_device`: allocates KUnit device/DRM device, sets generation, allocates HVS, builds topology, loads KMS, registers DRM, and registers cleanup action.
- Public helpers: `vc4_mock_device` and `vc5_mock_device`.

## Control Flow

Tests call a mock-device helper. The helper allocates managed test resources, constructs the topology from the generation-specific descriptor, invokes production `vc4_kms_load`, registers the device so atomic helpers behave normally, and arranges `drm_dev_unregister` as a KUnit cleanup action.

## State and Persistence Behavior

All state is test-scoped and mostly DRM-managed or KUnit-managed. The returned `vc4_dev` contains mock KMS objects, HVS state, generation marker, and a registered DRM device until test teardown.

## Dependencies and Integration Points

It depends on DRM KUnit helpers, VC4 production data objects (`bcm2835_*`, `bcm2711_*`), mock CRTC/output/plane helpers, `__vc4_hvs_alloc`, and `vc4_kms_load`.

## Risks and Edge Cases

- Mock descriptors must reflect production hardware mux constraints; stale topology reduces test value.
- Registering a DRM device inside KUnit requires reliable cleanup to avoid leakage across tests.
- Production KMS load may gain dependencies not modeled by the mock device.

## Test Signals

The PV muxing KUnit suites are the primary consumers. Build and run both VC4 and VC5 mock-device paths, verify all expected encoders/connectors exist, and ensure KUnit cleanup unregisters devices.
