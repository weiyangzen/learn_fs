<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.c

Purpose: lightweight Intel DMAR latency histogram support for invalidation and PRQ-related operations when `CONFIG_DMAR_PERF` is enabled.

Important APIs/types/functions: `dmar_latency_enable()`, `dmar_latency_disable()`, `dmar_latency_enabled()`, `dmar_latency_update()`, and `dmar_latency_snapshot()` operate on `struct latency_statistic` arrays indexed by `enum latency_type`.

Control flow: enabling lazily allocates `iommu->perf_statistic`, marks a latency bucket enabled, and initializes minimum to `UINT_MAX`. Updates bucket nanosecond latency into fixed ranges, maintains min/max/sum/sample count, and snapshots a formatted table with min/max/average converted to microseconds.

State and persistence: per-IOMMU statistics persist in `iommu->perf_statistic` until disabled or the IOMMU is freed. A single global spinlock serializes all stat updates and snapshots.

Dependencies and integration: included by Intel IOMMU invalidation/PRQ code and debugfs/reporting paths that request latency snapshots. It depends on `perf.h` enum ordering matching the snapshot name arrays.

Risks: `dmar_latency_disable()` clears `sizeof(*lstat) * DMAR_LATENCY_NUM` from `&lstat[type]`, which can overrun for nonzero `type` in this snapshot. Snapshot name arrays include `svm_prq` while `DMAR_LATENCY_NUM` currently covers three enum entries, another drift signal.

Test signals: enable/disable each latency type, update boundary values around each bucket, snapshot formatting with empty and populated samples, lockdep coverage under IRQ context, and KASAN/UBSAN for disable bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.c -->
