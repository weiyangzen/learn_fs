# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/dp.h

## Purpose
`dp.h` declares the Tegra-local DisplayPort link abstraction used by `dp.c` and hardware-specific DP/SOR code. It stores sink capabilities, selected link configuration, eDP supported rates, training state, and source-side operation callbacks.

## Important APIs, Types, and Definitions
`struct drm_dp_link_caps` records enhanced framing, TPS3, fast training, ANSI 8b/10b channel coding, and eDP alternate scrambler reset support. `struct drm_dp_link_ops` provides source-specific hooks for applying training parameters and configuring source hardware. `struct drm_dp_link_train_set` carries per-lane voltage swing, pre-emphasis, and post-cursor levels. `struct drm_dp_link_train` carries requested and sink-adjusted settings plus current pattern and success flags. `struct drm_dp_link` ties all of that to DPCD/eDP revisions, max/current rate and lanes, AUX read intervals, optional eDP rates, operation hooks, AUX channel, and training state.

Macros such as `DP_TRAIN_VOLTAGE_SWING_LEVEL()`, `DP_TRAIN_PRE_EMPHASIS_LEVEL()`, and `DP_LANE_POST_CURSOR()` encode DPCD training fields.

## Control Flow Role
The header is passive but defines how DP code is sequenced: callers probe into `drm_dp_link`, optionally choose a mode-specific configuration, configure DPCD/source hardware, and train through `drm_dp_link_train()`. Source drivers must fill `ops` and `aux` before training if hardware register programming is required.

## State and Persistence
The key persistent runtime state is the `struct drm_dp_link` instance owned by an output driver. It tracks probed capabilities and currently selected rate/lane count across link setup. Training state is embedded and updated during link training only.

## Dependencies and Integration Points
The header includes Linux types and forward-declares DRM display/AUX types. It depends on DP helper constants such as `DP_MAX_SUPPORTED_RATES` being visible to consumers through included DRM DP helper headers in implementation files. It integrates with `dpaux.c` through `struct drm_dp_aux` and with source drivers through `drm_dp_link_ops`.

## Risks
Because this is a local helper abstraction named with `drm_dp_*`, it can be confused with upstream DRM core helpers. Consumers must initialize `aux` and `ops` correctly or `drm_dp_link_apply_training()` can dereference missing hooks. The fixed array sizes assume DP helper constants and four-lane DP semantics.

## Test Signals
Build tests should verify all consumers see the same struct layout and prototypes. Runtime tests should verify that a link object survives probe, configure, choose, and train sequences, and that source-specific hooks receive the requested per-lane training values.
