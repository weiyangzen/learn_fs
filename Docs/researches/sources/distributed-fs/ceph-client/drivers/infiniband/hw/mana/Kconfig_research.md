# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/Kconfig

## Purpose
This Kconfig entry exposes `CONFIG_MANA_INFINIBAND`, the RDMA/InfiniBand verbs driver for Microsoft Azure Network Adapter hardware.

## Important APIs, Types, And Functions
`MANA_INFINIBAND` is a tristate option labeled "Microsoft Azure Network Adapter support". It depends on `NETDEVICES`, `ETHERNET`, `PCI`, and `MICROSOFT_MANA`, ensuring the Ethernet/GDMA MANA core is available before the RDMA auxiliary driver can be built.

## Control Flow
There is no runtime flow. The option controls whether the `mana_ib` module is built into the kernel, built as a module, or omitted.

## State And Persistence
The only state is build configuration. No runtime state is created by this file.

## Dependencies And Integration Points
The entry integrates the MANA RDMA driver into the kernel RDMA hardware-driver menu and ties it to the Microsoft MANA network driver stack.

## Risks
Missing dependency coverage would surface as unresolved symbols against MANA core, PCI, Ethernet, or RDMA infrastructure. The help text describes user-mode RDMA workloads such as DPDK and MPI, so packaging should make the dependency on the base MANA net driver clear.

## Test Signals
Validate `allyesconfig`, module build, disabled `MICROSOFT_MANA`, and `MANA_INFINIBAND=m` combinations; confirm `drivers/infiniband/hw/mana/Makefile` produces `mana_ib.o` only when this config is enabled.
