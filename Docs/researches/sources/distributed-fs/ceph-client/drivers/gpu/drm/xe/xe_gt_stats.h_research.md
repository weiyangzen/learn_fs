# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_stats.h

Purpose: declares GT stats APIs and provides no-op/time helper behavior when debugfs stats are disabled.

Important APIs: under `CONFIG_DEBUG_FS`, declares init/print/clear/incr. Without debugfs, init returns 0 and increment is a no-op. Inline time helpers return `ktime_get`/delta only when debugfs is enabled, otherwise zero.

Control flow: instrumentation can call stats and timing helpers unconditionally; compile-time config removes overhead for non-debugfs builds.

State and persistence: state is `gt->stats` from the implementation and `struct xe_gt_stats`.

Dependencies and integration: includes `linux/ktime.h` and `xe_gt_stats_types.h`; used by SVM, TLB invalidation, page reclaim, and engine group code.

Risks: timing helpers returning zero when disabled means callers must only use them for stats, not functional timing. Print/clear declarations are absent in non-debugfs builds.

Test signals: compile with and without CONFIG_DEBUG_FS and verify instrumentation has no missing symbols.
