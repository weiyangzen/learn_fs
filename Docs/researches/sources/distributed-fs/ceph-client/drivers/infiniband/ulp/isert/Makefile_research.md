# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Makefile

Purpose: Provides the Kbuild rule for the iSER target module.

Important APIs/types/functions: Binds `obj-$(CONFIG_INFINIBAND_ISERT)` to `ib_isert.o`.

Control flow: Kbuild compiles and links `ib_isert.c` into the `ib_isert` object when `CONFIG_INFINIBAND_ISERT` is enabled.

State and persistence: Build metadata only.

Dependencies and integration: Integrates directly with the Kconfig symbol from the same directory and relies on headers from RDMA core, target-core, and iscsi target through the source file includes.

Risks: If additional source files are added later, this object list must be updated or code will be omitted. Test signals include module build and modpost unresolved-symbol checks.
