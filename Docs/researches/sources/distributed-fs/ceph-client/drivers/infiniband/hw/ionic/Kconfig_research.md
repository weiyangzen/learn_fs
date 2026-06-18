# sources/distributed-fs/ceph-client/drivers/infiniband/hw/ionic/Kconfig

## Purpose
`Kconfig` adds the build-time configuration symbol for the AMD Pensando DSC RDMA/RoCE provider.

## Important APIs, Types, And Functions
The only symbol is `CONFIG_INFINIBAND_IONIC`, a tristate named "AMD Pensando DSC RDMA/RoCE Support". It depends on `NETDEVICES`, `ETHERNET`, `PCI`, `INET`, and the Pensando Ethernet driver symbol `IONIC`.

## Control Flow
Kconfig selection controls whether the `ionic_rdma` provider is built in, built as a module, or omitted. The help text describes DSC RoCE support and the module name.

## State And Persistence
This file has no runtime state. It influences kernel configuration state and therefore which objects are compiled.

## Dependencies And Integration Points
The dependency on `IONIC` ties the RDMA driver to the Ethernet/LIF infrastructure that supplies PCI, lif configuration, doorbell, interrupt, and device-command services. The symbol is consumed by the Ionic RDMA `Makefile`.

## Risks
Missing dependencies on RDMA core symbols may be covered by menu placement outside this file; if moved, the symbol could become visible without the expected InfiniBand core context. The strict `IONIC` dependency prevents building the RDMA provider without the net driver, which is correct for shared lif resources but affects modular packaging.

## Test Signals
Test `allyesconfig`, `allmodconfig`, and minimal configs with `IONIC=n/m/y`, verify `ionic_rdma` module visibility only when dependencies are met, and confirm module naming matches the help text.
