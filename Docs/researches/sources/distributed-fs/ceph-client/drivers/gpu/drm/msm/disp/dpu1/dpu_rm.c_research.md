# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_rm.c

Purpose: implements the DPU hardware resource manager. It builds runtime objects for catalog-described blocks and reserves per-CRTC display resources across layer mixers, pingpongs, CTLs, DSPPs, DSCs, CDM, CWB muxes, and SSPPs.

Important APIs and functions: `dpu_rm_init()` instantiates hardware wrappers from `dpu_mdss_cfg`; `dpu_rm_reserve()` drives reservation; `dpu_rm_release()` clears mappings; `dpu_rm_reserve_sspp()` assigns a source pipe by feature need; `dpu_rm_get_assigned_resources()` returns reserved blocks; `dpu_rm_print_state()` dumps mapping state. Internal helpers enforce LM peer selection, PP/DSC parity, legacy CTL split-display requirements, and CWB odd/even mux matching.

Control flow: init walks catalog arrays and stores block pointers in index-by-hardware-id arrays. Reserve first selects LM/PP/DSPP sets, optionally CWB muxes and CWB pingpongs, then CTLs, DSC blocks, and CDM. SSPP reservation is separate and prefers DMA, then RGB, then VIG depending on scale/YUV/rotation requirements.

State and persistence: durable state for commits lives in `struct dpu_global_state` maps from block index to DRM CRTC id. `dpu_rm` itself is a device lifetime catalog cache of block objects. There is no disk persistence.

Dependencies and integration: depends on DPU catalog data, DPU hardware block init helpers, DRM CRTC ids, and DPU atomic global state. Encoders and CRTCs consume assigned resources through `dpu_rm_get_assigned_resources()`. Tracepoints in `dpu_trace.h` expose RM reservation activity.

Risks: partial failure inside `_dpu_rm_make_reservation()` can leave earlier resource map writes unless caller rolls global state back via atomic state abort. Index math assumes catalog ids match array bases. CWB support currently requires dedicated CWB pingpongs. DSC pairing is topology-sensitive and can reject otherwise free blocks because of strict parity.

Test signals: exercise concurrent CRTCs, split display, DSC merge mode, writeback/CWB, YUV CDM, and SSPP feature fallbacks. Debugfs/DRM state should show expected CRTC ids in RM maps, and tracepoints should show LM/CTL reservations.
