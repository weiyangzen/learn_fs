# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Kconfig

## Purpose
`Kconfig` defines the `RDMA_RXE` soft-RoCE driver option and its kernel configuration dependencies.

## Important APIs, types, and functions
The option is `config RDMA_RXE`, a tristate named "Software RDMA over Ethernet (RoCE) driver". It depends on `INET`, `PCI`, `INFINIBAND`, `64BIT`, and `INFINIBAND_VIRT_DMA`, and selects `NET_UDP_TUNNEL` and `CRC32`.

## Control flow
No runtime flow. Kconfig controls whether `rdma_rxe.o` is built into the kernel, built as a module, or omitted.

## State and persistence
Configuration state persists in the kernel `.config`. It determines module availability and optional build integration.

## Dependencies and integration points
The help text documents RXE as a software RDMA transport over the Linux network stack, interoperable with RoCE adapters or other RXE systems, and points users to rdma-core RXE configuration documentation. The selected symbols match runtime use of UDP tunnel networking and CRC32 ICRC support.

## Risks
Dependency changes can allow unsupported architectures or missing network/RDMA features to build RXE. The `64BIT` dependency matters because the uverbs ABI note in `rxe.h` distinguishes 32-bit layouts.

## Test signals
Kconfig tests should verify `RDMA_RXE=m/y` builds only when dependencies are met, that selecting RXE pulls required CRC and UDP tunnel support, and that module load works with rdma-core tooling.
