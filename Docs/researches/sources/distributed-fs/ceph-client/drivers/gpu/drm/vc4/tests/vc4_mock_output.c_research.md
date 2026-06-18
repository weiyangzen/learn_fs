# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_mock_output.c

## Purpose

`vc4_mock_output.c` constructs dummy encoders/connectors for KUnit and provides helpers to add or remove outputs in DRM atomic state.

## Important APIs, Types, and Functions

- `vc4_dummy_output`: allocates a `vc4_dummy_output`, initializes a DRM encoder with a VC4 encoder type, initializes a DRM connector, and attaches them.
- `default_mode`: 640x480 mode used for test output enablement.
- `vc4_mock_atomic_add_output`: finds an encoder by VC4 type, gets its CRTC, attaches connector state, sets mode, and marks the CRTC active.
- `vc4_mock_atomic_del_output`: marks the CRTC inactive, clears mode, and detaches connector state.

## Control Flow

Mock device construction creates outputs. Tests allocate an atomic state, call add/del helpers for encoder combinations, then run `drm_atomic_check_only` to exercise production muxing logic.

## State and Persistence Behavior

Output objects are DRM-managed. Atomic helper calls mutate only the provided atomic state until tests call swap-state for bug-regression scenarios.

## Dependencies and Integration Points

It depends on DRM atomic/connector/encoder helpers, `vc4_find_encoder_by_type`, mock header utilities, and production VC4 encoder type values.

## Risks and Edge Cases

The helpers return `-EDEADLK` to let callers restart atomic acquisition; tests must handle backoff correctly. The default mode is simple and may not cover mode-dependent constraints.

## Test Signals

KUnit add/remove output paths for every encoder type, EDEADLK retry coverage, connector/CRTC state correctness, and muxing checks after `drm_atomic_check_only`.
