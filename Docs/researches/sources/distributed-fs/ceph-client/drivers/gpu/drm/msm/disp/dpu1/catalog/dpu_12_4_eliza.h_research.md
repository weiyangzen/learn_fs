## sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/catalog/dpu_12_4_eliza.h

### Purpose
`dpu_12_4_eliza.h` defines a smaller DPU 12.4 catalog for Eliza-class hardware. It keeps the modern DPU features of source split, dim layer, idle PC, 3D merge, DSC, WB, and CWB, but with fewer pipes and a lower bandwidth ceiling than SM8750/Glymur.

### Important APIs, Types, And Functions
The header exports `eliza_dpu_caps`, `eliza_mdp`, `eliza_ctl`, `eliza_sspp`, `eliza_lm`, `eliza_dspp`, `eliza_pp`, `eliza_merge_3d`, `eliza_dsc`, `eliza_wb`, `eliza_cwb`, `eliza_intf`, `eliza_perf_data`, `eliza_mdss_ver`, and `eliza_dpu_cfg`. Counts are 4 CTLs, 6 SSPPs, 4 mixers, 3 DSPPs, 8 pingpongs, 4 merge-3D blocks, 3 DSC blocks, 1 WB, 4 CWB entries, and 4 interfaces.

### Control Flow
The DPU core consumes the static `dpu_mdss_cfg` and walks each array to publish resources. The interface list is DP0, DSI0, DSI1, and a paired DP0 MST interface with 24 programmable-fetch lines. The CTL interrupt starts use TOP0_INTR2 bits 9-12.

### State, Persistence, And Dependencies
There is no mutable state in this header. It depends on shared DPU catalog structures, sub-block descriptors, and controller IDs. The constants are copied or referenced by runtime DPU resource objects created during probe.

### Integration Points
Version 12.4 and `max_bw_high = 14200000` place this catalog in the modern DPU programming family while reflecting a reduced resource/bandwidth envelope. WB/CWB and DSC entries integrate with writeback and compressed display paths, and the DP/DSI interfaces feed encoder creation.

### Risks
The asymmetric DSC count of 3 relative to 4 mixers and 8 pingpongs makes resource allocation edge cases likely for split DSC modes. CWB entries must not advertise impossible concurrent capture routes. Lower bandwidth means perf-data mistakes can produce visible underruns or unnecessarily reject modes.

### Test Signals
Probe should expose the expected reduced counts. Exercise single and dual DSI, DP MST pairing, DSC resource exhaustion cases, writeback/CWB, high-resolution modes near the 14.2M bandwidth ceiling, and CTL/pingpong interrupt paths.
