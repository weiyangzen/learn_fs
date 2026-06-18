# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.c

Purpose: implements per-GT debug statistics counters using per-CPU storage to avoid hot-path atomics.

Important APIs and functions: `xe_gt_stats_init` allocates per-CPU `struct xe_gt_stats` and registers cleanup; `xe_gt_stats_incr` increments a counter on the current CPU; `xe_gt_stats_print_info` sums all CPUs and prints descriptions; `xe_gt_stats_clear` zeroes all per-CPU counters.

Control flow: init attaches cleanup to the DRM device lifetime. Producers call `xe_gt_stats_incr` with an enum id. Debugfs print iterates every stat and every possible CPU to produce totals.

State and persistence: `gt->stats` points to per-CPU counters. State is volatile, cleared by explicit debugfs clear or freed on GT teardown. Clear is documented as unsafe under concurrent updates.

Dependencies and integration: depends on DRM managed cleanup and printer, `xe_device`, and the enum/type header. Counters are used by SVM page fault/migration, TLB invalidation, page-table reclaim, and hardware engine group paths; debugfs exposes print/clear.

Risks: `xe_gt_stats_incr` silently ignores invalid ids, but assumes `gt->stats` is initialized when CONFIG_DEBUG_FS is enabled. Concurrent clear can produce unpredictable totals. Description array must stay aligned with enum order.

Test signals: debugfs stats read/clear, hot-path increments from SVM/TLB/page reclaim, CPU hotplug/per-CPU summing, and enum/description build consistency.
