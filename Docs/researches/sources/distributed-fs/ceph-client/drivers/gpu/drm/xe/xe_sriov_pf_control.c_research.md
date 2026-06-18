<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.c

Purpose: provides device-level PF control wrappers that fan out VF operations to every GT: pause, resume, stop, reset/FLR, save migration, and restore migration.

Important APIs and control flow: pause/resume/stop loop all GTs and log success; reset triggers FLR on all GTs then waits on all GTs. `xe_sriov_pf_control_sync_flr()` performs two sync phases across all GTs. Save starts by `xe_sriov_packet_save_init()`, initializes per-GT migration save rings, then triggers save on each GT; finish-save loops finish calls. Restore trigger/finish similarly fan out per GT.

State and dependencies: depends on `xe_gt_sriov_pf_control`, `xe_gt_sriov_pf_migration`, packet save initialization, and SR-IOV printk helpers. It treats any earlier error in multi-GT pause/resume/stop as `-EUCLEAN` to indicate partial failure.

Risks and test signals: multi-GT partial failures must not be hidden. Tests should simulate one GT failing in each operation, validate save descriptor/trailer initialization happens before GT save trigger, and verify reset waits after triggering all GTs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_control.c -->
