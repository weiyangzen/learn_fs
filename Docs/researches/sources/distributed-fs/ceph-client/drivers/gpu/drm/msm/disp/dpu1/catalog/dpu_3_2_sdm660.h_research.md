## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_3_2_sdm660.h

### Purpose
This header defines the DPU 3.2 catalog for SDM660. It models a mid-range display block with source split, dim/idle/3D-merge capability, DP, dual DSI, and DSC.

### Important APIs, Types, And Functions
The file provides `sdm660_dpu_caps`, `sdm660_mdp`, 5 CTLs, 5 SSPPs, 4 mixers, 2 DSPPs, 4 pingpongs, 2 DSC blocks, 3 interfaces, `sdm660_perf_data`, `sdm660_mdss_ver`, and `sdm660_dpu_cfg`. Interfaces are DP0, DSI0, and DSI1, all with 21 programmable-fetch lines.

### Control Flow
DPU probe selects `sdm660_dpu_cfg` and common resource code walks each static array. There are no functions or branches in the header itself. `max_bw_high = 6600000` and `min_prefill_lines = 25` shape performance admission.

### State, Persistence, And Dependencies
The catalog is read-only static state. It depends on shared DPU structs, feature masks, DSC descriptors, and MSM DP/DSI controller definitions. Runtime resource state is created outside the header.

### Integration Points
SDM660 resource data feeds atomic plane allocation, DP/DSI encoder setup, DSC routing, and bandwidth calculations. Version 3.2 lets common DPU code distinguish this mid-range layout from MSM8998 and SDM630.

### Risks
With only 5 SSPPs and 2 DSCs, complex split/DSC modes must be rejected accurately. DP support on a mid-range target requires correct controller binding. Perf values close to MSM8998 should still reflect SDM660-specific interconnect limits.

### Test Signals
Validate DP0 and both DSI controllers, DSC on supported modes, resource exhaustion for too many planes, split display, vblank/CTL completion, and bandwidth/underrun behavior near 6.6M.
