# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/Makefile

## Purpose
`Makefile` declares the RXE module object composition.

## Important APIs, types, and functions
`obj-$(CONFIG_RDMA_RXE) += rdma_rxe.o` builds the driver. `rdma_rxe-y` links core RXE files for device setup, requester/completer/responder/receiver paths, pools, queues, verbs, address vectors, SRQ/QP/CQ/MR/MW, opcode tables, mmap, ICRC, multicast, tasks, net, hardware counters, and namespaces. `rdma_rxe-$(CONFIG_INFINIBAND_ON_DEMAND_PAGING) += rxe_odp.o` conditionally includes ODP support.

## Control flow
No runtime flow. The build system uses the object list to produce the `rdma_rxe` module or built-in object.

## State and persistence
Build state is determined by Kconfig and object dependencies. Runtime state is owned by the linked files.

## Dependencies and integration points
The file integrates RXE with the kernel kbuild system and optional ODP compilation. Object order matters for module linkage but not high-level behavior.

## Risks
Omitting a file from `rdma_rxe-y` creates unresolved symbols or missing feature paths. Adding new source files requires updating this list. ODP declarations in `rxe_loc.h` must stay compatible with the conditional `rxe_odp.o` inclusion.

## Test signals
Run kernel builds with `CONFIG_RDMA_RXE=m`, built-in, and with/without `CONFIG_INFINIBAND_ON_DEMAND_PAGING` to catch object-list and symbol regressions.
