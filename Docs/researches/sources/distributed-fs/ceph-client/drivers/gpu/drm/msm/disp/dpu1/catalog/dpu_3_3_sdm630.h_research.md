## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_3_sdm630.h

### Purpose
`dpu_3_3_sdm630.h` describes the smaller SDM630 DPU 3.3 catalog. It supports source split, dim layer, idle PC, 3D merge capability, one DP output, one DSI output, and a reduced two-mixer topology.

### Important APIs, Types, And Functions
The header defines `sdm630_dpu_caps`, `sdm630_mdp`, 5 CTLs, 4 SSPPs, 2 mixers, 1 DSPP, 2 pingpongs, 2 interfaces, performance data, version data, and `sdm630_dpu_cfg`. Interfaces are DP0 and DSI0 with 21 programmable-fetch lines.

### Control Flow
The file is declarative. The DPU core reads `sdm630_dpu_cfg` during probe and constructs the matching resource pools. `max_bw_high = 4100000` and `min_prefill_lines = 25` limit atomic bandwidth decisions.

### State, Persistence, And Dependencies
All state is immutable catalog data. It depends on DPU catalog structs, sub-block descriptors, DPU IRQ constants, and MSM DP/DSI controller IDs.

### Integration Points
The catalog drives DRM plane allocation for a reduced SDM630 hardware block and exposes exactly DP0 and DSI0 output resources. It shares common DPU v3 code paths with SDM660/MSM8998 while reducing block counts.

### Risks
Resource-manager code must handle the mismatch between the advertised `has_3d_merge` capability and the absence of a local merge3d array in this file. Low bandwidth requires accurate mode rejection. Single DSI and DP routes must not be confused with SDM660's dual DSI topology.

### Test Signals
Probe resource counts, DP0 and DSI0 modes, rejection of unsupported DSI1/extra-plane paths, split-display constraints, bandwidth tests near 4.1M, and underrun/vblank interrupt behavior.
