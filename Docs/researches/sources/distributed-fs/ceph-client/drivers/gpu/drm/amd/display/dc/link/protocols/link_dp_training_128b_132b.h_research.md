# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.h

## Purpose
`link_dp_training_128b_132b.h` declares the DP2 128b/132b training entry points used by generic DP training code.

## Important APIs
- `dp_perform_128b_132b_link_training()` executes the DP2 training sequence for prepared `link_training_settings`.
- `decide_128b_132b_training_settings()` initializes DP2 training policy, patterns, timings, and LTTPR mode.
- `dp_decide_128b_132b_lttpr_mode()` chooses LTTPR mode for 128b/132b links.

## Control Flow And Integration
The header includes `link_dp_training.h` and is included by the generic training orchestrator. It keeps the DP2-specific implementation behind three functions while reusing shared training structures and helpers.

## State, Risks, And Test Signals
The APIs mutate training settings, DPCD training state, hardware pattern/lane state, and read `dc_link` DP2/LTTPR capability state. Tests should compile generic training with DP2 support and run UHBR training success/failure, LTTPR, and debug legacy fallback paths.
