# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats_types.h

Purpose: defines GT statistics IDs and the per-CPU counter storage structure.

Important types: `enum xe_gt_stats_id` covers SVM page faults, TLB invalidations, page-fault sizes/timings, migration/copy metrics, hardware engine group queue metrics, and page reclaim list metrics. `struct xe_gt_stats` stores a cacheline-aligned `u64 counters[__XE_GT_STATS_NUM_IDS]`.

Control flow: enum values index both counter arrays and the description array in `xe_gt_stats.c`.

State and persistence: per-CPU instances are allocated at GT stats init and freed at teardown.

Dependencies and integration: includes Linux types; included by `xe_gt_types.h` and stats API.

Risks: enum insertions require updating `stat_description` to avoid NULL names or mismatched output. Cacheline alignment helps but per-CPU allocation still consumes memory proportional to stat count and CPU count.

Test signals: build-time and debugfs output validation for every enum id, plus instrumentation tests for newly added counters.
