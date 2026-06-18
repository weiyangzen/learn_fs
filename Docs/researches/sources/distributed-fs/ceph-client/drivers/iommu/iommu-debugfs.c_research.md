<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/iommu/iommu-debugfs.c

Purpose: top-level debugfs infrastructure for IOMMU drivers.

Important APIs/types/functions: exports `struct dentry *iommu_debugfs_dir` and implements `iommu_debugfs_setup()`.

Control flow: setup lazily creates `/sys/kernel/debug/iommu` and prints a prominent boot warning that IOMMU internals are exposed. Vendor drivers can create subdirectories under `iommu_debugfs_dir` after core setup.

State and persistence: `iommu_debugfs_dir` persists for the lifetime of the kernel debugfs tree. No teardown is implemented here.

Dependencies and integration: depends on debugfs, IOMMU core init, and vendor IOMMU debugfs users.

Risks: debugfs can expose sensitive IOMMU state, which the warning explicitly calls out. Repeated setup is idempotent only through the global pointer check.

Test signals: kernel built with IOMMU debugfs, boot warning presence, `/sys/kernel/debug/iommu` creation, vendor subdirectory creation, and disabled-debugfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iommu/iommu-debugfs.c -->
