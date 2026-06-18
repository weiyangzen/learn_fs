# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/Makefile

## Purpose
The Makefile defines the object composition for the mlx4 InfiniBand/RDMA driver.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MLX4_INFINIBAND) += mlx4_ib.o` builds the driver when configured. `mlx4_ib-y` includes address handles, CQs, doorbells, MAD, main, MR, QP, SRQ, multicast groups, CM paravirtualization, alias GUID, and sysfs objects.

## Control Flow
There is no runtime flow. Kbuild links the listed translation units into one mlx4_ib driver.

## State And Persistence
No runtime state exists in this file.

## Dependencies And Integration Points
The object list maps to the RDMA ops and mlx4-specific services declared in `mlx4_ib.h`; subset files here depend on additional objects such as `main.o`, `qp.o`, `srq.o`, and `mad.o`.

## Risks
Object-list drift causes unresolved symbols or missing runtime services, especially for cross-file helpers like AH creation, CQ polling, CM multiplexing, and alias GUID service.

## Test Signals
Run module and built-in builds; verify all listed objects compile and link under `CONFIG_MLX4_INFINIBAND`.
