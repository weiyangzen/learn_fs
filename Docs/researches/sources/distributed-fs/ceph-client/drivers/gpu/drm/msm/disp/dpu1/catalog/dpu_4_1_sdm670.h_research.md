## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_4_1_sdm670.h

### Purpose
`dpu_4_1_sdm670.h` defines the SDM670 DPU 4.1 catalog as a derivative of SDM845. It supplies SDM670-specific MDP, SSPP, mixer, DSPP, and DSC arrays while reusing SDM845 caps, CTLs, pingpongs, interfaces, and performance data.

### Important APIs, Types, And Functions
The file defines `sdm670_mdp`, `sdm670_sspp`, `sdm670_lm`, `sdm670_dspp`, `sdm670_dsc`, `sdm670_mdss_ver`, and `sdm670_dpu_cfg`. `sdm670_dpu_cfg` references `sdm845_dpu_caps`, `sdm845_ctl`, `sdm845_pp`, `sdm845_intf`, and `sdm845_perf_data`; local counts are 5 SSPPs, 4 mixers, 2 DSPPs, and 2 DSC blocks, with inherited 5 CTLs, 4 pingpongs, and 4 interfaces.

### Control Flow
The catalog is static data only. Probe uses the mixed local/inherited table pointers to instantiate SDM670 resources. Output interfaces and CTL/pingpong arrays follow the SDM845 layout even though plane/DSPP/DSC capacity is reduced.

### State, Persistence, And Dependencies
No mutable state exists. This header directly depends on symbols from the SDM845 catalog being visible in the same inclusion context, plus the shared DPU catalog structs and sub-block descriptors.

### Integration Points
The derivative catalog integrates SDM670 without duplicating unchanged SDM845 resources. This saves maintenance but ties SDM670 behavior to SDM845 definitions for caps, CTLs, pingpongs, output interfaces, and perf limits.

### Risks
The main risk is hidden coupling: SDM845 changes can alter SDM670. Reusing SDM845 interface data may over-advertise outputs if SDM670 routing differs. Resource-manager paths must handle inherited counts and local reduced DSC/DSPP counts consistently.

### Test Signals
Compile-order coverage is important because this file references SDM845 symbols. Runtime validation should check actual SDM670 output exposure, reduced plane/DSPP/DSC capacity, inherited DP/DSI/MST behavior, and bandwidth behavior from reused SDM845 perf data.
