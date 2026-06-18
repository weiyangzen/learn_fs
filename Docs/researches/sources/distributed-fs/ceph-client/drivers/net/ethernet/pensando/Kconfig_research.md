# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/Kconfig

Purpose: Adds the Pensando vendor menu and the `CONFIG_IONIC` option for the Pensando/AMD Ionic Ethernet driver.

Important APIs/types/functions: `NET_VENDOR_PENSANDO` gates the vendor submenu. `IONIC` is a tristate depending on `64BIT`, `PCI`, and optional PTP clock support; it selects `NET_DEVLINK`, `DIMLIB`, `PAGE_POOL`, and `AUXILIARY_BUS`.

Control flow: Kernel configuration first enables the vendor bucket, then offers the Ionic NIC driver. When built as a module, the module name is `ionic`.

State and dependencies: No runtime state. The Kconfig selections directly determine whether devlink, adaptive interrupt moderation, page-pool RX allocation, auxiliary RDMA device registration, and optional PTP code are available to the compiled driver.

Risks and test signals: Build matrix should cover built-in, module, and disabled `IONIC`, plus `CONFIG_PTP_1588_CLOCK` on/off. Dependency drift is important: removing `AUXILIARY_BUS`, `PAGE_POOL`, or `NET_DEVLINK` selections would break source files in this subset.
