<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.c

## Purpose

`xe_sriov_vf_ccs.c` manages VF-side compression metadata (CCS) save/restore support for migration. It creates special migration execution queues/LRCAs, allocates batch-buffer pools, registers save/restore contexts with GuC, and attaches per-BO CCS copy commands.

## Important APIs, Types, and Functions

`xe_sriov_vf_ccs_init()` is the main setup path. `xe_sriov_vf_ccs_register_context()` re-registers save and restore contexts after runtime suspend. `xe_sriov_vf_ccs_rebase()` rewrites LRC rings after GGTT rebasing. `xe_sriov_vf_ccs_attach_bo()` and `xe_sriov_vf_ccs_detach_bo()` insert or clear CCS copy commands for BOs. `xe_sriov_vf_ccs_rw_update_bb_addr()` patches the batch-buffer address in the LRC. `xe_sriov_vf_ccs_print()` dumps pool state. Internal helpers compute pool size, allocate `xe_mem_pool`, reset LRC head/tail, and map context IDs to GuC compression save/restore types.

## Control Flow

Initialization runs only for VFs with migration enabled, integrated devices using flat CCS, and GuC ABI at least 1.23. For each read/write CCS context it creates a permanent kernel migrate queue, allocates and zeroes a BB pool sized from system memory and CCS ratio, writes an LRC ring pointing at the pool, registers the queue with GuC, and registers devm cleanup. BO attach loops over read/write contexts and calls `xe_migrate_ccs_rw_copy()`. Detach clears copy commands for valid CCS BBs.

## State and Persistence Behavior

Persistent VF CCS state is `xe->sriov.vf.ccs.contexts[]`, each holding context ID, migration queue, and CCS BB pool. `initialized` marks readiness. Cleanup sets ring tail to head before dropping the queue so GuC does not submit stale work after unbind.

## Dependencies and Integration Points

This file depends on MI/GPU command definitions, LRC ring helpers, exec queue creation and GuC registration, migration copy helpers, memory pools, runtime PM, VF migration gating, and BO `bb_ccs` bookkeeping. It is used by VF init, runtime resume, BO binding/unbinding, GGTT rebasing, and debugfs.

## Risks and Test Signals

The code has a documented workaround requiring LRC head zero for repeated migrations. Risks include oversized BB-pool memory use, partial initialization when one context succeeds and the other fails, stale BB addresses after GGTT movement, and attach continuing after an earlier context error. Tests should cover GuC version gating, non-flat-CCS no-op, successful read/write context registration, rebase ring contents, BO attach/detach idempotence, cleanup with GuC pause, and repeated migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_sriov_vf_ccs.c -->
