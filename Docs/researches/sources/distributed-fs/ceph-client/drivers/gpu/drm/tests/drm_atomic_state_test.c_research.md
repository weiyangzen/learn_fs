# sources/distributed-fs/ceph-client/drivers/gpu/drm/tests/drm_atomic_state_test.c

## Purpose

`drm_atomic_state_test.c` provides KUnit tests for DRM atomic helper modeset and clone-mode behavior. It verifies that connector changes trigger encoder modeset callbacks and that clone-mode helper checks accept only valid encoder clone combinations.

## Important APIs, Types, and Functions

- `struct drm_atomic_test_priv` embeds a test DRM device, primary plane, CRTC, three encoders, and two connectors.
- `drm_atomic_test_init_drm_components()` creates a minimal atomic modeset device with configurable connectors, encoder clone masks, helper callbacks, and mode-config reset.
- `set_up_atomic_state()` allocates an atomic state, optionally attaches a connector to the CRTC, sets a fixed 1024x768 mode, enables/activates the CRTC, and commits or seeds a connector mask.
- `drm_test_check_connector_changed_modeset()` asserts that moving an active CRTC from one connector to another increments `modeset_counter`.
- `drm_test_check_in_clone_mode()` tests `drm_crtc_in_clone_mode()` against one-encoder and two-encoder masks.
- `drm_test_check_valid_clones()` tests `drm_atomic_helper_check_modeset()` with valid and invalid `possible_clones` combinations.

## Control Flow

Each test constructs DRM objects with KUnit helpers, initializes mode config, and uses `drm_modeset_acquire_ctx` retry loops for `-EDEADLK`. The connector-change test performs an initial commit to enable one connector, creates a second atomic state, detaches the old connector, attaches a new one, commits, and checks that `atomic_mode_set` ran once more. Clone tests parameterize encoder masks and either call the helper directly or force a modeset check on a dummy CRTC state.

## State and Persistence Behavior

All DRM objects are KUnit-managed and test-local. `modeset_counter` is file-static and incremented by `drm_test_encoder_mode_set()`, so tests depending on its delta record the initial count. Atomic state objects are managed by KUnit helper cleanup and DRM managed resources.

## Dependencies and Integration Points

The tests depend on DRM atomic, atomic helper, atomic UAPI, probe helper, and DRM KUnit helper APIs. They target behavior in `drm_atomic_helper_check_modeset()`, `drm_crtc_in_clone_mode()`, connector/encoder atomic commit handling, and possible-clone validation.

## Risks and Edge Cases

- The global `modeset_counter` is not reset per test, so tests must continue using deltas if more cases are added.
- Clone validation is synthetic: it manipulates `encoder_mask` directly and does not cover full connector/encoder routing.
- The no-connector setup seeds `connector_mask` manually, which is enough for helper testing but not a full userspace-equivalent atomic state.

## Test Signals

KUnit suites `drm_validate_modeset` and `drm_validate_clone_mode` should pass. Signals include mode-set count increasing on connector replacement, `drm_crtc_in_clone_mode()` returning true only for multi-encoder masks, and invalid clone masks returning `-EINVAL` from modeset check.
