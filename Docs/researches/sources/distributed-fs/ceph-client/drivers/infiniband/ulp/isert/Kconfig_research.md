# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/isert/Kconfig

Purpose: Declares the build configuration option for the iSER target transport.

Important APIs/types/functions: Defines `CONFIG_INFINIBAND_ISERT` as a tristate option labelled "iSCSI Extensions for RDMA (iSER) target support".

Control flow: When enabled as built-in or module, Kbuild compiles the adjacent `ib_isert.o` target transport. The option is only visible when its dependency stack is satisfied.

State and persistence: Build-time configuration only; no runtime state.

Dependencies and integration: Requires `INET`, `INFINIBAND_ADDR_TRANS`, `TARGET_CORE`, and `ISCSI_TARGET`, expressing that the module bridges RDMA address translation with the kernel target-core iSCSI target.

Risks: Missing dependencies can break builds or expose the option without target/RDMA infrastructure. Test signals include `allmodconfig`/`allyesconfig`, dependency-disabled configs, and module load with target-core/iSCSI target enabled.
