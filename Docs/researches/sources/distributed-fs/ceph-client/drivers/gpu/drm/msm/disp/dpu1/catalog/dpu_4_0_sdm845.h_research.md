## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_0_sdm845.h

### Purpose
This file defines the SDM845 DPU 4.0 catalog, a major shared baseline for later Qualcomm DPU descriptions. It supports source split, dim layer, idle PC, 3D merge capability, DSC, DP, dual DSI, and DP MST pairing.

### Important APIs, Types, And Functions
The header exports `sdm845_dpu_caps`, `sdm845_mdp`, 5 CTLs, 8 SSPPs, 4 mixers, 4 DSPPs, 4 pingpongs, 4 DSC blocks, 4 interfaces, `sdm845_perf_data`, `sdm845_mdss_ver`, and `sdm845_dpu_cfg`. Interfaces are DP0, DSI0, DSI1, and a paired DP0 MST interface with 24 programmable-fetch lines.

### Control Flow
No functions execute here. Probe and resource-manager code consume the static `dpu_mdss_cfg`, map block arrays, and use counts to expose DRM resources. Perf data sets `max_bw_high = 6800000` and `min_prefill_lines = 24`.

### State, Persistence, And Dependencies
Catalog data is static read-only state. Dependencies include shared DPU structs, SDM845 sub-block descriptors, feature masks, DPU IRQ macros, DSC data, and MSM DP/DSI controller IDs.

### Integration Points
Many later headers reuse SDM845 arrays, masks, or perf data, so this file is both a hardware catalog and a baseline dependency for related targets. It integrates with atomic resource assignment, DSC, DP MST, DSI encoders, and bandwidth voting.

### Risks
Because other catalogs reuse `sdm845_*` data, changes here can affect multiple SoCs. The paired DP MST interface must be interpreted correctly. Four DSC blocks must align with pingpong and mixer topology for split/compressed modes.

### Test Signals
Validate SDM845 probe counts, DP0 and DP MST, dual DSI, DSC modes, high-plane atomic tests, bandwidth near 6.8M, CTL/pingpong interrupts, and regression tests for any SoC reusing SDM845 arrays.
