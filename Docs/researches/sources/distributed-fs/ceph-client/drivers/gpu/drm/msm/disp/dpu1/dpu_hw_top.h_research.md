# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_hw_top.h

## Purpose
Declares the MDP TOP wrapper, configuration structures, and ops used for shared top-level display hardware programming.

## Important APIs, types, and functions
- `struct traffic_shaper_cfg`, although declared, is not wired by the current implementation.
- `struct split_pipe_cfg` models dual-pipe enable, interface mode, controlling interface, and split flush.
- `struct dpu_danger_safe_status` holds decoded MDP and SSPP status.
- `struct dpu_vsync_source_cfg` carries pingpong list, frame rate, and vsync source.
- `enum dpu_dp_phy_sel` and `struct dpu_hw_mdp_ops` expose top-level control operations.
- `dpu_hw_mdptop_init()` constructs the wrapper.

## Control flow
No significant control flow exists in the header. Ops are optional by hardware generation and must be checked before use.

## State and persistence
`struct dpu_hw_mdp` stores register map, catalog caps, and ops. Persistent state is written into MDP TOP registers by implementation callbacks.

## Dependencies and integration points
Includes catalog, MDSS, and utility headers. KMS, encoder, debugfs, and VBIF/plane QoS paths use top-level clock and status services.

## Risks
The API exposes `setup_traffic_shaper` but the current implementation never assigns it, so callers must treat it as optional. `ppnumber[PINGPONG_MAX]` assumes pingpong enum bounds from `dpu_hw_mdss.h`.

## Test signals
Compile coverage and runtime checks through split-pipe setup, vsync source programming, danger/safe debugfs files, and DP PHY selection validate this header’s contracts.
