# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/Kconfig

Purpose: Adds the kernel configuration switch for the Hisilicon Hip08 family RoCE driver. `CONFIG_INFINIBAND_HNS_HIP08` is a tristate option that builds the HNS RoCE hardware v2 module.

Important APIs/types/functions: This is Kconfig metadata rather than C code. The key symbol is `INFINIBAND_HNS_HIP08`, presented as "Hisilicon Hip08 Family RoCE support"; its module name is documented as `hns-roce-hw-v2`.

Control flow: Kernel configuration exposes the option only when architecture and bus prerequisites are met. Enabling it selects compilation through the adjacent Makefile.

State and persistence: Build-time state only. No runtime state is stored here, but the choice determines whether the driver is absent, built-in, or loadable as a module.

Dependencies and integration: Requires `ARM64` or `(COMPILE_TEST && 64BIT)`, plus `PCI` and `HNS3`. The explicit `HNS3` dependency ties the RDMA driver to the Hisilicon Ethernet stack used for RoCE netdev and hardware-service integration.

Risks: Incorrect dependency constraints could allow builds on unsupported platforms or hide valid compile-test coverage. Test signals include `allyesconfig`/`allmodconfig` on ARM64 and 64-bit compile-test targets, module name verification, and ensuring HNS3 symbols are available whenever this driver is selected.
