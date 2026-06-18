# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/mdp5/mdp5_ctl.c

Purpose: implements the MDP5 CTL pool manager and CTL programming layer. CTLs describe and flush display pipelines shared by interfaces.

Important APIs and functions: `mdp5_ctlm_init()` creates the CTL pool from hardware config; `mdp5_ctlm_request()` allocates a CTL, preferring booked CTLs for DSI interface numbers 1/2; `mdp5_ctlm_hw_reset()` clears CTL ops. CTL APIs set pipeline/interface selection, encoder state, cursor routing, layer blending, flush masks, commit/start, commit status, and CTL id.

Control flow: `mdp5_ctl_set_pipeline()` programs display interface selection and CTL op bits for command mode, writeback line mode, and 3D packing/source split. `mdp5_ctl_blend()` resets layer registers, builds left/right mixer layer and extension masks from stage arrays, preserves cursor output, writes layer regs, and records pending CTL trigger bits. `mdp5_ctl_commit()` adds CTL flush when pending trigger bits overlap, applies software flush fixes for targets without dedicated bits, filters by hardware mask, accumulates if `start` is false, otherwise writes flush register and sends START when needed.

State and persistence: each `mdp5_ctl` tracks id, busy/booked status, encoder enabled, accumulated flush mask, hw lock, register offset, pending trigger bits, and cursor state. Pool state is protected by `pool_lock`.

Dependencies and integration: used by MDP5 CRTC and encoder paths; depends on MDP5 config flush masks, interface structs, pipeline structs, and MDP5 register helpers.

Risks: allocated CTLs are marked busy but this file does not show a release API, so lifecycle is controlled elsewhere or persistent per encoder. Flush mask filtering can hide missing config bits if tables are wrong. `stage_cnt` loop relies on initialized stage arrays.

Test signals: CTL allocation exhaustion, DSI command START, writeback START, cursor enable/disable flush, source split blending, deferred start modesets, and targets with shared cursor/LM flush bits.
