# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.h

Purpose: declares the DPU resource manager interface and the topology/requirement structures used by DPU atomic modeset and plane code.

Important APIs and types: `struct dpu_rm` stores arrays of hardware block handles for pingpong, LM, CTL, INTF, WB, CWB, DSPP, merge3d, DSC, SSPP, and CDM. `struct dpu_rm_sspp_requirements` expresses pipe features (`yuv`, `scale`, `rot90`). `struct msm_display_topology` describes requested LM/INTF/DSPP/DSC/CDM counts and CWB enablement. Public functions cover init, reserve, release, SSPP reserve/release, assigned-resource lookup, and state printing. Inline accessors expose INTF/WB/SSPP handles by enum index.

Control flow and integration: callers create `dpu_rm` during KMS init, pass display topologies during atomic reservation, and query assigned blocks while configuring encoders and CRTCs. The header deliberately separates fixed catalog handles in `dpu_rm` from dynamic mappings in `dpu_global_state`.

State and persistence: only declares in-memory objects. Reservation state persists for an atomic global state lifetime, not across driver unload or reboot.

Dependencies: relies on DRM types, `msm_kms.h`, and DPU hardware enum definitions from `dpu_hw_top.h`.

Risks: inline accessors do no bounds checking, so callers must pass valid enum values. The arrays are sized from enum ranges, making catalog enum changes a compatibility point.

Test signals: compile coverage catches signature drift. Runtime tests should verify each accessor returns catalog-created blocks and invalid topologies fail without corrupting `dpu_global_state`.
