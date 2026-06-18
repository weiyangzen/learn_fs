<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.h -->
# sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.h

Purpose: header for Intel DMAR latency statistics, providing enums, the statistic structure, and real or stub implementations depending on `CONFIG_DMAR_PERF`.

Important APIs/types/functions: `enum latency_type` names IOTLB, devTLB, and IEC invalidation latency classes; `enum latency_count` defines histogram buckets plus min/max/sum; `struct latency_statistic` holds enable state, counters, and sample count. Public helpers are declared or stubbed.

Control flow: callers can unconditionally call latency helpers; when disabled, enable returns `-EINVAL`, enabled returns false, and update/snapshot become no-ops.

State and persistence: no state in the header itself; it defines the shape allocated per IOMMU by `perf.c`.

Dependencies and integration: included by Intel IOMMU code that wants optional latency accounting without ifdefs at call sites.

Risks: enum/list drift with `perf.c` can produce mislabeled output or out-of-bounds clears. Stubs must match signatures to preserve compile behavior across configs.

Test signals: builds with and without `CONFIG_DMAR_PERF`, callers using every helper, and snapshot consumers tolerating empty strings when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/intel/perf.h -->
