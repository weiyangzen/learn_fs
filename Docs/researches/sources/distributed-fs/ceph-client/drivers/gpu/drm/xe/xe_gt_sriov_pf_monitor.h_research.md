# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf_monitor.h

Purpose: declares PF adverse-event monitor APIs for FLR cleanup, GuC event dispatch, and debug printing.

Important APIs: `xe_gt_sriov_pf_monitor_flr`, `xe_gt_sriov_pf_monitor_print_events`, and conditional `xe_gt_sriov_pf_monitor_process_guc2pf`; the latter returns `-EPROTO` when PCI IOV is disabled.

Control flow: PF control calls FLR cleanup after VF reset data cleanup; GuC event dispatch calls `process_guc2pf`; debugfs calls print.

State and persistence: no state in the header; state is defined by `xe_gt_sriov_pf_monitor_types.h`.

Dependencies and integration: forward-declares `struct xe_gt` and `struct drm_printer`.

Risks: callers must treat the no-IOV stub as unsupported rather than a transient parse failure.

Test signals: build both PCI IOV configurations and route adverse event messages through the PF GuC event multiplexer.
