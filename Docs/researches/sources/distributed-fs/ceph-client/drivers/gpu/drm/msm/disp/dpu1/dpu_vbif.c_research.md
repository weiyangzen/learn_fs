# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/disp/dpu1/dpu_vbif.c

Purpose: configures the DPU VBIF bus interface for outstanding transaction limits, QoS remapping, error clearing, memory types, and debugfs exposure.

Important APIs and functions: `dpu_vbif_set_ot_limit()` calculates and programs read/write OT limits; `dpu_vbif_set_qos_remap()` applies real-time or non-real-time QoS priority tables; `dpu_vbif_clear_errors()` clears pending/source error registers; `dpu_vbif_init_memtypes()` programs catalog memory types; `dpu_debugfs_vbif_init()` exposes static catalog parameters in debugfs. Internal `_dpu_vbif_wait_for_xin_halt()` waits for halt acknowledgement, `_dpu_vbif_get_ot_limit()` selects limits, and `_dpu_vbif_apply_dynamic_ot_limit()` adjusts WFD limits based on pixels per second.

Control flow: OT programming optionally enables write-gather, skips no-op writes, traces the chosen limit, writes limit configuration, asserts halt, waits with timeout, traces failure, then deasserts halt. QoS remap loops over catalog priority levels.

State and persistence: state is hardware register state in VBIF; no software persistence beyond catalog pointers. Debugfs files expose read-only or restricted values.

Dependencies and integration: integrates with `struct dpu_kms`, `dpu_hw_vbif` ops, catalog VBIF tables, debugfs, and DPU performance/plane paths that compute client parameters.

Risks: halt wait blocks up to catalog timeout and can delay atomic work. Bad catalog defaults can skip needed programming or overconstrain bus traffic. Dynamic OT only applies to WFD paths. Missing ops cause silent no-op behavior except debug logs.

Test signals: validate display and writeback stability under high bandwidth, confirm VBIF tracepoints show expected OT changes, force timeout paths with faulty hardware simulation, and inspect debugfs values against catalog.
