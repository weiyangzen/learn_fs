# sources/distributed-fs/ceph-client/drivers/infiniband/Makefile

Purpose: Top-level kbuild dispatcher for InfiniBand/RDMA subdirectories.

Important APIs/types/functions: Adds `core/`, `hw/`, `ulp/`, and `sw/` when `CONFIG_INFINIBAND` is enabled.

Control flow: build-system only.

State and persistence: none beyond build configuration.

Dependencies/integration: aligns with top-level InfiniBand Kconfig and subordinate Makefiles.

Risks: any subdirectory omitted here cannot build even if its Kconfig is enabled.

Test signals: enabling `CONFIG_INFINIBAND` should descend into all four subtrees.
