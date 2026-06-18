# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_sriov_pf.c

## Purpose
Coordinates per-GT SR-IOV Physical Function setup, hardware enablement, restart work, VF scratch sanitization, and readiness waits.

## Important APIs and Functions
- Public PF lifecycle: `xe_gt_sriov_pf_init_early`, `xe_gt_sriov_pf_init`, `xe_gt_sriov_pf_init_hw`, `xe_gt_sriov_pf_stop_prepare`, `xe_gt_sriov_pf_restart`, and `xe_gt_sriov_pf_wait_ready`.
- VF resource/hardware helpers: `xe_gt_sriov_pf_sanitize_hw` and `xe_gt_sriov_pf_sched_groups_enabled`.
- Internal worker flow: `pf_init_workers`, `pf_queue_restart`, `pf_worker_restart_func`, `pf_restart`, `pf_flush_restart`, and cancellation/fini helpers.

## Control Flow
- Early init allocates PF/VF metadata, initializes service and control layers, and prepares restart work.
- Late init initializes config, policy, migration, and devm cleanup.
- Hardware init enables guest GGTT updates on selected platforms and refreshes PF service state.
- GT restart queues a worker on `xe->sriov.wq`; the worker repushes PF config/control state and releases a runtime PM reference taken at queue time.
- Stop prepare cancels pending restart work to avoid racing GT teardown.

## State and Persistence
`gt->sriov.pf.vfs` is a flexible array indexed with PF at 0 and VFs at 1..n. Restart work is persistent per GT and protected by runtime PM references while queued.

## Dependencies and Integration Points
Integrates PF config/control/service/policy/migration modules, GuC submission stopped state, GGTT guest update register programming, runtime PM, and GT reset/restart.

## Risks and Test Signals
- Restart work must not leak runtime PM references when already queued or canceled.
- `xe_gt_sriov_pf_wait_ready` returns `-EBUSY` if GuC is stopped, so callers should distinguish reset-in-progress from permanent failure.
- PF init ordering is important: config push requires GuC CT and resource managers to be available.
