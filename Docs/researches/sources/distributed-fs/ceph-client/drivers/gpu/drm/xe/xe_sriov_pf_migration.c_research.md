<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.c

Purpose: implements device-level PF migration state, support gating, per-VF locks/waitqueues, save-data consumption, restore-data production, debugfs read/write streaming, and total migration-size reporting.

Important APIs and control flow: `xe_sriov_pf_migration_init()` disables migration if memory-based IRQ support is missing, initializes per-VF mutexes/waitqueues, and registers cleanup for pending/descriptor/trailer packets. `xe_sriov_pf_migration_save_consume()` loops over GT migration queues, waiting on the per-VF waitqueue while data is pending but not yet ready. `xe_sriov_pf_migration_restore_produce()` handles descriptor/trailer packets at device level and dispatches other packet types to the target GT. `xe_sriov_pf_migration_read()` and `_write()` hold the per-VF lock and stream packets until the user buffer is consumed or data ends.

State and dependencies: `xe->sriov.pf.migration.disabled` gates support; each VF has `struct xe_sriov_migration_state` with waitqueue, lock, pending, descriptor, and trailer packets. Depends on per-GT control/migration APIs, packet helpers, runtime PM via debugfs callers, and SR-IOV logging.

Risks and test signals: save consumption can block interruptibly, restore must reject invalid tile/GT/type metadata, and trailer handling marks restore data done on all GTs. Tests should cover missing memirq gating, debug override behavior, wait interruption, empty save stream, descriptor/trailer validation, multi-GT size aggregation, and locked streaming partial transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_pf_migration.c -->
