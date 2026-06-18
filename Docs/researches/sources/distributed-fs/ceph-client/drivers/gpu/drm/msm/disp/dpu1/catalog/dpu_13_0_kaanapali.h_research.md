## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_13_0_kaanapali.h

### Purpose
This header defines the Kaanapali DPU 13.0 catalog. It is a newer flagship-style display configuration with 8192-line support, source split, dim layer, idle PC, 3D merge, DSC, WB, CWB, and DP/DSI/MST interfaces.

### Important APIs, Types, And Functions
Static exports include `kaanapali_dpu_caps`, `kaanapali_mdp`, resource arrays for CTL/SSPP/LM/DSPP/pingpong/merge3d/DSC/WB/CWB/interface blocks, `kaanapali_perf_data`, `kaanapali_mdss_ver`, and `kaanapali_dpu_cfg`. The topology has 6 CTLs, 10 SSPPs, 8 mixers, 4 DSPPs, 12 pingpongs, 6 merge-3D blocks, 8 DSC blocks, 1 WB, 4 CWB entries, and 4 interfaces.

### Control Flow
No functions execute here. Probe selects `kaanapali_dpu_cfg`, then the DPU catalog/resource code maps each block by array order, base, length, ID, pair links, and IRQ start. Interfaces are DP0, DSI0, DSI1, and paired DP0 MST, all with 24 programmable-fetch lines.

### State, Persistence, And Dependencies
The file contributes immutable catalog data. It depends on shared DPU feature masks, sub-block descriptors, IRQ macros, and controller enums. Runtime resources persist in DPU driver structures initialized from the constants.

### Integration Points
`core_major_ver = 13` identifies the newest programming family in this subset. `max_bw_high = 30200000` and `min_prefill_lines = 35` feed DPU bandwidth and prefill calculations. The resource tables integrate with atomic plane allocation, DSC compression, CWB/WB, and DP/DSI encoder setup.

### Risks
As a high-resource catalog, errors in mixer-pingpong-merge3d-DSC relationships can break only complex modes and be missed by basic boot tests. The very high bandwidth ceiling must match interconnect capabilities. Version 13.0 paths need compile/runtime coverage in the DPU core.

### Test Signals
Validate resource counts at probe, high-bandwidth 8192-line display modes, DP MST on the paired interface, dual DSI, DSC across eight encoders, CWB and WB capture, interrupt delivery across all CTLs, and suspend/resume with idle power collapse.
