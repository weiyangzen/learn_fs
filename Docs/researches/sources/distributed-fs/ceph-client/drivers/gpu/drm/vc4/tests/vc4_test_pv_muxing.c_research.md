# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/tests/vc4_test_pv_muxing.c

## Purpose

`vc4_test_pv_muxing.c` is a KUnit test suite for VC4/VC5 HVS FIFO and pixel-valve muxing. It validates legal encoder-to-channel assignments, rejects illegal output combinations, and captures regressions around active FIFO stability and unnecessary CRTC state acquisition.

## Important APIs, Types, and Functions

- `check_fifo_conflict`: verifies no HVS FIFO channel is assigned twice in global state.
- Encoder constraint tables: `vc4_encoder_constraints` and `vc5_encoder_constraints`.
- `check_channel_for_encoder`: confirms an encoder's assigned channel is enabled and allowed by the generation-specific constraints.
- Parameter arrays: valid and invalid VC4/VC5 output combinations.
- Test bodies: `drm_vc4_test_pv_muxing`, `drm_vc4_test_pv_muxing_invalid`, and VC5 bug regression tests for subsequent CRTC enable, stable FIFO, and avoiding too many CRTC states.
- `kunit_test_suites`: registers VC4 valid/invalid, VC5 valid/invalid, and VC5 bug suites.

## Control Flow

Each parameterized test builds a mock VC4 or VC5 device, allocates a DRM atomic state with deadlock retry handling, enables or disables requested mock outputs, runs `drm_atomic_check_only`, and inspects VC4 global HVS/CRTC state. Valid cases expect success, no FIFO conflicts, and allowed channel assignments. Invalid cases expect atomic check failure. Bug tests perform staged atomic commits/checks to ensure enabling a second HDMI uses a different FIFO, disabling one output does not move the other active output, and enabling HDMI1 does not pull in HDMI0 CRTC state.

## State and Persistence Behavior

Most tests inspect transient atomic state. Bug regressions use `drm_atomic_helper_swap_state` to persist a first checked state before testing a subsequent transition. Test-private state stores the mock device pointer in `struct pv_muxing_priv`.

## Dependencies and Integration Points

The suite depends on mock device helpers, DRM KUnit/atomic helpers, production VC4 KMS/HVS state, `vc4_find_encoder_by_type`, `vc4_hvs_get_new_global_state`, and production muxing logic in VC4 atomic checks.

## Risks and Edge Cases

- The exhaustive-looking parameter lists are hand-maintained; new encoder types or muxing rules require updates.
- Some VC5 valid cases are duplicated, which increases runtime without adding coverage.
- Tests are check-focused and do not exercise hardware programming paths.
- Deadlock retry handling must clear atomic state correctly to avoid false failures.

## Test Signals

Run `vc4-pv-muxing-combinations`, `vc5-pv-muxing-combinations`, and `vc5-pv-muxing-bugs` through KUnit. Failures indicate regressions in HVS channel assignment, constraint enforcement, state reuse, or active FIFO stability.
