## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_2_glymur.h

### Purpose
This file describes the Glymur DPU 12.2 catalog, a high-end multi-output display topology. It extends the DPU 12 family with 8 CTLs, 8 DSPPs, many DP interfaces, DSC, CWB, and 8192-line capability.

### Important APIs, Types, And Functions
The exported catalog pieces are `glymur_dpu_caps`, `glymur_mdp`, arrays for CTL, SSPP, LM, DSPP, pingpong, merge3d, DSC, WB, CWB, and interfaces, plus `glymur_perf_data`, `glymur_mdss_ver`, and `glymur_dpu_cfg`. Counts are 8 CTLs, 10 SSPPs, 8 LMs, 8 DSPPs, 10 pingpongs, 4 merge-3D blocks, 8 DSC blocks, 1 WB, 4 CWB entries, and 9 interfaces.

### Control Flow
The common DPU catalog code indexes this static topology to instantiate resources. Interface entries include DP0, DSI0, DSI1, paired DP0 MST, DP1, DP3, DP2, paired DP2 MST, and paired DP1 MST, each with 24 worst-case programmable-fetch lines. CTL interrupt starts cover TOP0_INTR2 bits 9 through 15 plus 23.

### State, Persistence, And Dependencies
All fields are static constants. Dependencies are the DPU catalog ABI, shared sub-block descriptors, DPU IRQ macros, and MSM display controller IDs. The data persists in `.rodata`; mutable display state is allocated elsewhere from these tables.

### Integration Points
`glymur_dpu_cfg` feeds resource allocation for multi-display systems, including many DP controller routes and concurrent DSC pipelines. `max_bw_high = 28500000` and `min_prefill_lines = 35` integrate with bandwidth and latency admission, while version 12.2 gates hardware-version-specific paths.

### Risks
The 9-interface topology is the main risk: controller IDs and MST pairing comments must match the physical output routing. Any mismatch between 8 DSPPs and mixer/display paths can break color processing assignment. The four merge-3D entries with eight DSC blocks require careful resource-manager validation for split/compressed modes.

### Test Signals
Validate probe counts, simultaneous DP/DSI enumeration, DP1/DP2/DP3 routing, MST on paired DP entries, DSC allocation across eight blocks, CWB/WB availability, CTL interrupt delivery for all 8 CTLs, and high-bandwidth atomic tests near the configured limits.
